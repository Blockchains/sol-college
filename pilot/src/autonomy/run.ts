/**
 * CTO autonomy loop (one pass). Runs in the protected `cto-autonomy` workflow (environment `minds`) on a schedule.
 * Per project: reconcile pending Mind tasks and act on validated results, track upstream, discover lab PR heads,
 * dispatch candidate validation, draft and build adoption packages, ask for research plans and Lab Reporter status.
 * Everything a Mind proposes passes deterministic checks before anything is written. Mind lifecycle, Circles,
 * pausing and acceptance are never touched here. Private state lives in SC_PRIVATE_RECORDS_DIR (control repo).
 */
import { existsSync, mkdirSync, readFileSync, writeFileSync } from "node:fs";
import { join } from "node:path";
import { loadConfig, getProject, type LoadedConfig } from "../config/project.ts";
import type { ProjectConfig } from "../config/types.ts";
import type { GitHubApi } from "../github/api.ts";
import { sha256Hex } from "../lib/canonical.ts";
import { PUBLIC_RECORDS_DIR, REPO_ROOT } from "../lib/paths.ts";
import { findSecretLeaks } from "../lib/secrets.ts";
import type { FileStore } from "../lib/store.ts";
import type { MindMapping, Approval } from "../minds/authority.ts";
import { resolveProjectMind } from "../minds/authority.ts";
import type { MindsPort } from "../minds/port.ts";
import { dispatchTask, normaliseReplyText, reconcileTask, MAX_REVIEW_ATTEMPTS, type TaskRecord, type TaskResponse, type TaskSpec, type SourceRef } from "../minds/task.ts";
import { candidateVerdict, createAdoptionPackage } from "../adoption/create.ts";
import { existingPackageFor } from "../adoption/package.ts";
import { githubCompare, reconcileUpstream, type ExperimentRef } from "../upstream/reconcile.ts";
import { FileStore as Store } from "../lib/store.ts";
import { checkPatch, patchPolicyFor } from "../lab/patch.ts";
import { checkTransferRequest, loadTreasury } from "../treasury/treasury.ts";
import { opsSnapshot } from "../minds/ops.ts";

export interface AutonomyConfig {
  schema: "sc-autonomy/1";
  standingApproval: { approvedBy: string; ref: string; at: string; covers: string[]; excludes: string[] };
  projects: string[];
  limits: { maxNewTasksPerProjectPerRun: number; maxIssuesPerProjectPerRun: number; researchPlanIntervalHours: number; reportIntervalHours: number; taskWaitMs: number };
}

type Kind = TaskSpec["kind"];
interface TaskMeta { kind: Kind; createdAt: string; sha?: string; prUrl?: string; handled?: string }
export interface AutonomyState {
  project: string;
  upstreamHead?: string;
  lastResearchPlanAt?: string;
  lastReportAt?: string;
  lastReportRequestedAt?: string;
  tasks: Record<string, TaskMeta>;
  prHeads: Record<string, string>;
  validations: Record<string, { dispatchedAt: string; prUrl: string }>;
  packages: Record<string, string>;
  proposalHashes: string[];
  issuesOpened: Array<{ url: string; at: string; taskId: string }>;
  /** research-question issue url -> experiment-patch taskId */
  patchRequests?: Record<string, string>;
  /** taskId -> outcome of the Mind's requested actions (patch / devnet-transfer) */
  actionsHandled?: Record<string, string[]>;
  lastOpsAt?: string;
  lastRunAt?: string;
}

export interface PublicStatus {
  schema: "sc-cto-status/1";
  project: string;
  updatedAt: string;
  runUrl: string | null;
  report: { summary: string; at: string; taskId: string } | null;
  activity: Array<{ at: string; text: string; url?: string }>;
  pendingTasks: number;
  operatorReview: number;
  upstreamHead: string | null;
  openLabPullRequests: number;
}

export interface RunDeps {
  minds: MindsPort;
  gh: GitHubApi;
  store: FileStore;
  cfg: LoadedConfig;
  mapping: MindMapping;
  auto: AutonomyConfig;
  now: () => Date;
  runUrl: string | null;
  dryRun?: boolean;
}

const hours = (a: string | undefined, now: Date) => (a ? (now.getTime() - Date.parse(a)) / 3_600_000 : Infinity);
const stamp = (d: Date) => d.toISOString().replace(/[-:T]/g, "").slice(0, 10); // yyyymmddhh
const EXCLUDED_TOPICS = /\b(mainnet|private key|seed phrase|mnemonic|faucet|airdrop farming)\b/i;
const EMAIL = /[\w.+-]+@[\w-]+\.[a-z]{2,}/i;

export function loadAutonomy(): AutonomyConfig {
  return JSON.parse(readFileSync(join(REPO_ROOT, "config", "autonomy.json"), "utf8")) as AutonomyConfig;
}

/** Deterministic gate for any Mind-authored text that will become public. */
export function publicTextCheck(text: string, max: number): { ok: boolean; text: string; reasons: string[] } {
  const t = normaliseReplyText(text).replace(/<[^>]+>/g, "").replace(/\s+/g, " ").trim();
  // Negated boundary disclaimers ("no mainnet keys", "devnet only, not mainnet") restate the rules, they do not raise the topic.
  const topical = t.replace(/\b(no|not|never|without|excluding|excludes|nothing on|avoid(?:s|ing)?)\s+(?:any\s+|the\s+)?(?:use\s+of\s+)?(?:mainnet|faucet)(?:[\s-]+(?:keys?|funds|deployments?|claims?|automation|access))?(?:\s*(?:,|or|and|nor)\s*(?:mainnet|faucet)(?:[\s-]+(?:keys?|funds|deployments?|claims?|automation|access))?)*\b/gi, " ");
  const reasons: string[] = [];
  if (t.length < 20) reasons.push("too short");
  if (t.length > max) reasons.push(`longer than ${max} characters`);
  if (EMAIL.test(t)) reasons.push("contains an email address");
  if (findSecretLeaks(t).length) reasons.push("contains secret-shaped text");
  if (EXCLUDED_TOPICS.test(topical)) reasons.push("mentions an excluded topic");
  if (/https?:\/\/(?!github\.com\/|sol\.college\/)/i.test(t)) reasons.push("links outside github.com or sol.college");
  return { ok: reasons.length === 0, text: t, reasons };
}

/** Choose the first Mind proposal that may become a research-question issue. */
export function pickProposal(resp: TaskResponse, seen: string[]): { title: string; detail: string; hash: string } | null {
  for (const p of resp.proposals) {
    // Minds sometimes repeat the issue prefix ("[research] <project>: ..."); it is added again when the issue is opened.
    const title = publicTextCheck(p.title.replace(/^(\s*\[[a-z -]+\]\s*[\w.-]*\s*:\s*)+/i, ""), 120);
    const detail = publicTextCheck(p.detail, 4000);
    if (!title.ok || !detail.ok || title.text.length < 12 || detail.text.length < 40) continue;
    const hash = sha256Hex(Buffer.from(title.text.toLowerCase().replace(/[^a-z0-9]+/g, " ").trim(), "utf8")).slice(0, 16);
    if (seen.includes(hash)) continue;
    return { title: title.text, detail: detail.text, hash };
  }
  return null;
}

function emptyState(project: string): AutonomyState {
  return { project, tasks: {}, prHeads: {}, validations: {}, packages: {}, proposalHashes: [], issuesOpened: [] };
}

interface LabPr { url: string; number: number; repo: string; headSha: string; title: string }

async function openLabPullRequests(gh: GitHubApi, p: ProjectConfig): Promise<LabPr[]> {
  type Pr = { html_url: string; number: number; title: string; head: { sha: string; repo: { full_name: string } | null }; base: { repo: { full_name: string } } };
  const up = await gh.get<Pr[]>(`/repos/${p.upstream.repo}/pulls?state=open&per_page=50`);
  const lab = await gh.get<Pr[]>(`/repos/${p.lab.repo}/pulls?state=open&per_page=50`);
  const out: LabPr[] = [];
  for (const pr of up) if (pr.head.repo?.full_name === p.lab.repo) out.push({ url: pr.html_url, number: pr.number, repo: p.upstream.repo, headSha: pr.head.sha, title: pr.title });
  for (const pr of lab) if (pr.base.repo.full_name === p.lab.repo && pr.head.repo?.full_name === p.lab.repo) out.push({ url: pr.html_url, number: pr.number, repo: p.lab.repo, headSha: pr.head.sha, title: pr.title });
  return out;
}

async function existingQuestions(gh: GitHubApi, p: ProjectConfig): Promise<string[]> {
  type I = { title: string; html_url: string; state: string };
  const all = await gh.get<I[]>(`/repos/${p.validation.workflowRepo}/issues?labels=research-question&state=all&per_page=100`);
  return all.filter((i) => i.title.includes(p.slug)).map((i) => `${i.title} (${i.state})`).slice(0, 20);
}

export async function runProject(d: RunDeps, slug: string, log: (s: string) => void): Promise<{ state: AutonomyState; status: PublicStatus }> {
  const now = d.now();
  const nowIso = now.toISOString();
  const p = getProject(d.cfg, slug);
  const approval: Approval = { approvedBy: d.auto.standingApproval.approvedBy, ref: d.auto.standingApproval.ref, action: "message", projectSlug: slug };
  const r = await resolveProjectMind({ cfg: d.cfg, mapping: d.mapping, slug, operation: "message", approval, minds: d.minds });
  const mindName = (await d.minds.getMind(r.mindId)).name ?? `SolCollege CTO (${slug})`;
  const key = `autonomy/${slug}`;
  const cur = d.store.read<AutonomyState>(key);
  const st: AutonomyState = cur?.data ?? emptyState(slug);
  const activity: PublicStatus["activity"] = [];
  const prefix = p.mind.conversationPrefix ?? `sc-${slug}`;
  const deps = { minds: d.minds, store: d.store, mindId: r.mindId, aliasPrefix: prefix, timeoutMs: d.auto.limits.taskWaitMs };
  let newTasks = 0;
  let issues = 0;
  const pending = (kind: Kind, match?: (m: TaskMeta) => boolean) => Object.values(st.tasks).some((m) => m.kind === kind && !m.handled && (!match || match(m)));

  const dispatch = async (spec: TaskSpec, meta: Omit<TaskMeta, "createdAt" | "kind">): Promise<TaskRecord | null> => {
    if (newTasks >= d.auto.limits.maxNewTasksPerProjectPerRun || st.tasks[spec.taskId]) return null;
    newTasks++;
    st.tasks[spec.taskId] = { kind: spec.kind, createdAt: nowIso, ...meta };
    if (d.dryRun) { log(`[dry-run] would dispatch ${spec.taskId}`); return null; }
    const rec = await dispatchTask(deps, spec);
    log(`dispatched ${spec.taskId}: ${rec.state}`);
    const verb: Record<Kind, string> = { "research-plan": "Drafting the next research question", "upstream-impact": "Assessing an upstream change", "pr-triage": "Triaging a lab pull request", "adoption-draft": "Drafting an adoption package", "progress-report": "Writing the Lab Reporter status", "smoke-test": "Running a smoke test", "experiment-patch": "Writing a patch for a research question" };
    activity.push({ at: nowIso, text: `${verb[spec.kind]}${meta.prUrl ? ` (${meta.prUrl.replace("https://github.com/", "")})` : ""}` });
    return rec;
  };

  const sources: SourceRef[] = [
    { id: "upstream", url: `https://github.com/${p.upstream.repo}` },
    { id: "lab", url: `https://github.com/${p.lab.repo}` },
    { id: "research", url: p.research.authorisationRef },
  ];

  // 1) Reconcile pending tasks and act on validated results.
  for (const [taskId, meta] of Object.entries(st.tasks)) {
    // A plan whose proposals were all filtered may be re-checked (no Mind call) while it is still the current plan,
    // e.g. after the public-text gate is corrected; issue creation is still deduplicated by proposal hash.
    const recheck = meta.handled === "no-eligible-proposal" && hours(meta.createdAt, now) < d.auto.limits.researchPlanIntervalHours;
    // Operator-review tasks get a bounded re-evaluation of replies already in history (reviewTask stops after MAX_REVIEW_ATTEMPTS).
    const reviewable = meta.handled === "operator-review" && (d.store.read<TaskRecord>(`tasks/${slug}/${taskId}`)?.data.reviewAttempts ?? 0) < MAX_REVIEW_ATTEMPTS;
    if (meta.handled && !recheck && !reviewable) continue;
    const stored = d.store.read<TaskRecord>(`tasks/${slug}/${taskId}`);
    if (!stored) { meta.handled = "missing-record"; continue; }
    let rec = stored.data;
    if (["uncertain", "dispatched", "dispatch-intent", "operator-review"].includes(rec.state) && !d.dryRun) rec = await reconcileTask({ minds: d.minds, store: d.store }, rec.spec);
    if (rec.state === "operator-review" && (rec.reviewAttempts ?? 0) < MAX_REVIEW_ATTEMPTS && !rec.history.some((h) => h.note.startsWith("sent message not found"))) { log(`${taskId}: operator review pending re-evaluation (${rec.errors.join("; ")})`); continue; }
    if (rec.state === "operator-review") { meta.handled = "operator-review"; log(`${taskId}: operator review (${rec.errors.join("; ")})`); continue; }
    if (rec.state !== "completed" || !rec.response) {
      if (hours(meta.createdAt, now) > 48) { meta.handled = "expired-no-reply"; log(`${taskId}: no reply after 48h; closed without resend`); }
      continue;
    }
    const resp = rec.response;
    if (resp.actions?.length && !(st.actionsHandled ??= {})[taskId]) {
      st.actionsHandled![taskId] = d.dryRun ? ["dry-run"] : await handleActions(d, p, slug, taskId, resp, mindName, activity, log, nowIso);
    }
    if (meta.kind === "experiment-patch") {
      meta.handled = resp.actions?.some((a) => a.type === "patch") ? "patch-handled" : "no-patch";
      continue;
    }
    if (meta.kind === "research-plan") {
      const pick = issues < d.auto.limits.maxIssuesPerProjectPerRun ? pickProposal(resp, st.proposalHashes) : null;
      if (pick && !d.dryRun) {
        const factLines = resp.facts.slice(0, 8).map((f) => `- ${publicTextCheck(f.statement, 400).text} (sources: ${f.sourceRefs.map((s) => rec.spec.sources.find((x) => x.id === s)?.url ?? s).join(", ")})`);
        const hypLines = resp.hypotheses.slice(0, 5).map((h) => `- ${publicTextCheck(h.statement, 400).text}\n  - How to test: ${publicTextCheck(h.howToTest, 400).text}`);
        const body = [`### Project\n\n${slug}`, `### Question\n\n${pick.detail}`, `### Facts (cited)\n\n${factLines.join("\n") || "- none"}`, `### Hypotheses and how to test them\n\n${hypLines.join("\n") || "- none"}`,
          `### Boundaries\n\n- [x] Devnet / local validator only; no mainnet keys.\n- [x] No security findings in public; those go to the private channel.`,
          `---\nProposed by the Sol.College CTO agent for ${p.displayName} (task \`${taskId}\`), opened automatically after deterministic checks (length, no secrets or emails, no excluded topics, links limited to github.com/sol.college, not a duplicate). ${p.demonstrationNotice ?? ""}\n<!-- sc-proposal:${pick.hash} -->`].join("\n\n");
        const issue = await d.gh.send<{ html_url: string }>("POST", `/repos/${p.validation.workflowRepo}/issues`, { title: `[research] ${slug}: ${pick.title}`.slice(0, 200), body, labels: ["research-question", "mind-proposed"] });
        if (issue) { st.issuesOpened.push({ url: issue.html_url, at: nowIso, taskId }); activity.push({ at: nowIso, text: `Opened research question: ${pick.title}`, url: issue.html_url }); issues++; log(`opened ${issue.html_url}`); }
        st.proposalHashes.push(pick.hash);
      }
      meta.handled = pick ? "issue-opened" : "no-eligible-proposal";
    } else if (meta.kind === "progress-report") {
      const chk = publicTextCheck(resp.summary, 900);
      if (chk.ok) { st.lastReportAt = nowIso; meta.handled = "published"; writeReport(slug, { summary: chk.text, at: nowIso, taskId }); }
      else meta.handled = `report-rejected:${chk.reasons.join(",")}`;
    } else if (meta.kind === "adoption-draft" && meta.sha) {
      if (!existingPackageFor(join(PUBLIC_RECORDS_DIR, "adoption"), slug, meta.sha) && !d.dryRun) {
        const prNum = meta.prUrl ? Number(meta.prUrl.split("/").pop()) : NaN;
        const prRepo = meta.prUrl ? meta.prUrl.replace("https://github.com/", "").split("/pull/")[0] : p.lab.repo;
        type C = { sha: string; author: { login: string } | null };
        const commits = Number.isFinite(prNum) ? await d.gh.get<C[]>(`/repos/${prRepo}/pulls/${prNum}/commits?per_page=100`) : [];
        const integration = resp.proposals.find((x) => /integrat|merge|deploy/i.test(x.title));
        const rollback = resp.proposals.find((x) => /rollback|revert/i.test(x.title));
        const res = await createAdoptionPackage(d.gh, d.cfg, slug, meta.sha, {
          version: 1,
          contributions: [{ title: publicTextCheck(resp.summary, 300).text.slice(0, 300), author: commits[0]?.author?.login ?? "unknown", prUrl: meta.prUrl ?? `https://github.com/${p.lab.repo}`, commits: commits.map((c) => c.sha) }],
          narrative: {
            source: "mind-draft",
            problem: publicTextCheck(resp.summary, 2000).text,
            alternatives: resp.hypotheses.map((h) => publicTextCheck(h.statement, 400).text).slice(0, 5),
            risks: resp.uncertainties.map((u) => publicTextCheck(u, 400).text).slice(0, 8),
            limitations: [`Validation fixture: ${p.validation.fixture}.`, "Narrative drafted by the Sol.College CTO agent; authoritative fields (commits, evidence, hashes) are assembled by code."],
            integration: integration ? publicTextCheck(integration.detail, 800).text : "Merge the pull request commits onto the upstream branch and redeploy to devnet.",
            rollback: rollback ? publicTextCheck(rollback.detail, 800).text : "Revert the pull request commits and redeploy the previous program binary.",
          },
          testConclusions: [`Newest genuine candidate-validation run for ${meta.sha.slice(0, 12)} passed (fixture: ${p.validation.fixture}).`],
        });
        if (res.outcome === "created" && "packageId" in res && res.packageId) { st.packages[meta.sha] = res.packageId; activity.push({ at: nowIso, text: `Built adoption package ${res.packageId} (awaiting the project reviewer)`, url: `https://github.com/${p.validation.workflowRepo}/blob/main/${res.path}` }); log(`package ${res.packageId}`); }
      }
      meta.handled = "package-built";
    } else {
      meta.handled = "recorded-private"; // pr-triage, upstream-impact: private record; public line only
      activity.push({ at: nowIso, text: meta.kind === "pr-triage" ? `Triaged ${meta.prUrl?.replace("https://github.com/", "") ?? "a pull request"}` : "Assessed upstream impact" });
    }
  }

  // 2) Upstream.
  const head = (await d.gh.get<{ commit: { sha: string } }>(`/repos/${p.upstream.repo}/branches/${encodeURIComponent(p.upstream.branch)}`)).commit.sha;
  if (st.upstreamHead !== head) {
    const expFile = join(PUBLIC_RECORDS_DIR, "experiments", `${slug}.json`);
    const experiments: ExperimentRef[] = existsSync(expFile) ? (JSON.parse(readFileSync(expFile, "utf8")) as { experiments: ExperimentRef[] }).experiments : [];
    const res = d.dryRun ? null : await reconcileUpstream({ store: new Store(join(PUBLIC_RECORDS_DIR, "upstream")), project: slug, upstreamRepo: p.upstream.repo, branch: p.upstream.branch, observedHead: head, compare: githubCompare(d.gh, p.upstream.repo), experiments });
    if (st.upstreamHead && res && res.outcome !== "unchanged" && !pending("upstream-impact")) {
      await dispatch({ taskId: `impact-${slug}-${head.slice(0, 7)}`, project: slug, kind: "upstream-impact", instructions: "Follow Sol.College operating instructions v1. The upstream head changed. Assess which experiments need rebase or retest and what changed that matters for this project.", sources: [...sources, { id: "previous", url: `https://github.com/${p.upstream.repo}/commit/${st.upstreamHead}`, sha: st.upstreamHead }, { id: "current", url: `https://github.com/${p.upstream.repo}/commit/${head}`, sha: head }], evidence: [], context: { impacts: res.impacts, outcome: res.outcome } }, {});
    }
    st.upstreamHead = head;
  }

  // 3) Lab pull requests: validation + triage.
  const prs = await openLabPullRequests(d.gh, p);
  // Mind-authored lab branches (sc-lab/<slug>/...) are candidates even before a PR exists.
  type Br = { name: string; commit: { sha: string } };
  const branches = await d.gh.get<Br[]>(`/repos/${p.lab.repo}/branches?per_page=100`).catch(() => [] as Br[]);
  const candidates: LabPr[] = [...prs];
  for (const b of branches) if (b.name.startsWith(`sc-lab/${slug}/`) && !prs.some((x) => x.headSha === b.commit.sha)) candidates.push({ url: `https://github.com/${p.lab.repo}/tree/${b.name}`, number: 0, repo: p.lab.repo, headSha: b.commit.sha, title: b.name });
  for (const pr of candidates) {
    if (st.prHeads[pr.url] === pr.headSha) continue;
    if (!st.validations[pr.headSha]) {
      const existing = await candidateVerdict(d.gh, d.cfg, slug, pr.headSha);
      if (existing.decidingRun) { st.validations[pr.headSha] = { dispatchedAt: existing.decidingRun.createdAt, prUrl: pr.url }; log(`existing validation evidence for ${pr.headSha.slice(0, 7)}; not re-dispatched`); }
    }
    if (!st.validations[pr.headSha] && !d.dryRun) {
      await d.gh.send("POST", `/repos/${p.validation.workflowRepo}/actions/workflows/${p.validation.workflowPath.split("/").pop()}/dispatches`, { ref: "main", inputs: { project: slug, lab_repo: p.lab.repo, candidate_sha: pr.headSha } });
      st.validations[pr.headSha] = { dispatchedAt: nowIso, prUrl: pr.url };
      activity.push({ at: nowIso, text: `Requested validation of ${pr.number ? `${pr.repo}#${pr.number}` : pr.title} at ${pr.headSha.slice(0, 7)}`, url: pr.url });
      log(`validation dispatched for ${pr.url}@${pr.headSha.slice(0, 7)}`);
    }
    const t = await dispatch({ taskId: `triage-${slug}-${pr.headSha.slice(0, 7)}`, project: slug, kind: "pr-triage", instructions: "Follow Sol.College operating instructions v1. Triage this lab pull request: what it changes, risk, and what the validation fixture does and does not exercise. Do not state that validation passed.", sources: [...sources, { id: "pr", url: pr.url }, { id: "candidate", url: `https://github.com/${p.lab.repo}/commit/${pr.headSha}`, sha: pr.headSha }], evidence: [], context: { title: pr.title, fixture: p.validation.fixture } }, { sha: pr.headSha, prUrl: pr.url });
    if (t !== null || st.tasks[`triage-${slug}-${pr.headSha.slice(0, 7)}`]) st.prHeads[pr.url] = pr.headSha;
  }

  // 4) Passing candidates without a package: ask for an adoption draft (package is built when it returns).
  for (const [sha, v] of Object.entries(st.validations)) {
    if (st.packages[sha] || existingPackageFor(join(PUBLIC_RECORDS_DIR, "adoption"), slug, sha) || pending("adoption-draft", (m) => m.sha === sha) || st.tasks[`adopt-${slug}-${sha.slice(0, 7)}`]) continue;
    const verdict = await candidateVerdict(d.gh, d.cfg, slug, sha);
    if (!verdict.passed || !verdict.decidingRun) continue;
    await dispatch({ taskId: `adopt-${slug}-${sha.slice(0, 7)}`, project: slug, kind: "adoption-draft", instructions: "Follow Sol.College operating instructions v1. Draft the adoption narrative for this validated candidate: summary = the problem solved; hypotheses = alternatives considered; proposals should include one titled 'Integration' and one titled 'Rollback'; uncertainties = risks. Do not claim acceptance.", sources: [...sources, { id: "pr", url: v.prUrl }, { id: "candidate", url: `https://github.com/${p.lab.repo}/commit/${sha}`, sha }], evidence: [{ id: "validation-run", url: verdict.decidingRun.htmlUrl }], context: { fixture: p.validation.fixture } }, { sha, prUrl: v.prUrl });
  }

  // 4b) Coding: ask the Mind for a patch for the oldest open research question that has none yet.
  st.patchRequests ??= {};
  if (!pending("experiment-patch")) {
    type I = { title: string; html_url: string; body: string | null; number: number };
    const open = (await d.gh.get<I[]>(`/repos/${p.validation.workflowRepo}/issues?labels=research-question&state=open&per_page=50&sort=created&direction=asc`)).filter((i) => i.title.startsWith(`[research] ${slug}:`) && !st.patchRequests![i.html_url]);
    const q = open[0];
    if (q) {
      const labHead = (await d.gh.get<{ commit: { sha: string } }>(`/repos/${p.lab.repo}/branches/${encodeURIComponent(p.lab.branch)}`)).commit.sha;
      const files = await referencedFiles(d.gh, p.lab.repo, labHead, q.body ?? "");
      const taskId = `patch-${q.number}-${stamp(now)}`;
      const t = await dispatch({ taskId, project: slug, kind: "experiment-patch", instructions: "Follow Sol.College operating instructions v1. Write the smallest correct code change that answers this research question as an experiment on the lab fork. Return it as one action {type:'patch',title,rationale,patch} where patch is a git unified diff (diff --git a/<path> b/<path>, ---/+++ headers, @@ hunks with exact context) against labHead, touching only program source or tests under the allowed paths. Do not edit .github, workflows, Anchor.toml, package manifests, lockfiles or toolchain files; no keys, no mainnet. Keep it under 400 changed lines. Code applies it to a branch sc-lab/<project>/<task> and the secret-free candidate-validation workflow builds it; you cannot mark it as passing. If the change needs devnet SOL for a test wallet, you may add {type:'devnet-transfer',recipient,lamports,reason}.", sources: [...sources, { id: "question", url: q.html_url }, { id: "lab-head", url: `https://github.com/${p.lab.repo}/commit/${labHead}`, sha: labHead }], evidence: [], context: { question: { title: q.title, body: (q.body ?? "").slice(0, 6000) }, labHead, allowedPathPrefixes: patchPolicyFor(p.validation.programDir ?? "contract").allowedPrefixes, files } }, {});
      if (t !== null || d.dryRun) st.patchRequests[q.html_url] = taskId;
    }
  }

  // 4c) HelloMinds operations snapshot (cognition, usage by tool, equipped skills/apps, conversations), every 2 h.
  if (hours(st.lastOpsAt, now) >= 1.9 && !d.dryRun) {
    try {
      const ops = await opsSnapshot(d.minds, r.mindId, prefix);
      mkdirSync(join(PUBLIC_RECORDS_DIR, "minds"), { recursive: true });
      writeFileSync(join(PUBLIC_RECORDS_DIR, "minds", `${slug}.json`), JSON.stringify({ schema: "sc-mind-ops/1", project: slug, mind: mindName, at: nowIso, ...ops }, null, 2) + "\n");
      st.lastOpsAt = nowIso;
    } catch (e) { log(`ops snapshot failed: ${(e as Error).message}`); }
  }

  // 5) Research plan (periodic) and Lab Reporter status.
  if (hours(st.lastResearchPlanAt, now) >= d.auto.limits.researchPlanIntervalHours && !pending("research-plan")) {
    const t = await dispatch({ taskId: `plan-${slug}-${stamp(now)}`, project: slug, kind: "research-plan", instructions: "Follow Sol.College operating instructions v1. Propose the next research question for this project's lab, within the authorised scope and excluding the exclusions. Each proposal: a short title and a detail paragraph framed as a testable question. Cite facts only by the source ids given. Avoid duplicating the existing questions listed in context.", sources, evidence: [], context: { scope: p.research.scope, exclusions: p.research.exclusions, openAssignments: p.publicListing.assignments.filter((a) => a.status === "open").map((a) => a.title), existingQuestions: await existingQuestions(d.gh, p) } }, {});
    if (t !== null || d.dryRun) st.lastResearchPlanAt = nowIso;
  }
  if (hours(st.lastReportRequestedAt, now) >= d.auto.limits.reportIntervalHours && !pending("progress-report")) {
    const t = await dispatch({ taskId: `report-${slug}-${stamp(now)}`, project: slug, kind: "progress-report", instructions: "Follow Sol.College operating instructions v1. Write the public Lab Reporter status for this project in the summary field: at most 100 words, plain text, no private details, no links except github.com or sol.college, and no claim that anything passed validation or was accepted unless the evidence ids say so.", sources, evidence: [], context: { openLabPullRequests: prs.length, packages: Object.keys(st.packages).length, validationsRequested: Object.keys(st.validations).length } }, {});
    if (t !== null || d.dryRun) st.lastReportRequestedAt = nowIso;
  }

  st.lastRunAt = nowIso;
  if (!d.dryRun) d.store.write(key, st, cur?.version ?? 0);
  const status = writeStatus(slug, { runUrl: d.runUrl, activity, st, prs: prs.length, now: nowIso, dryRun: d.dryRun ?? false });
  return { state: st, status };
}

const statusPath = (slug: string) => join(PUBLIC_RECORDS_DIR, "status", `${slug}.json`);
function readStatus(slug: string): PublicStatus | null {
  return existsSync(statusPath(slug)) ? (JSON.parse(readFileSync(statusPath(slug), "utf8")) as PublicStatus) : null;
}
function writeReport(slug: string, report: NonNullable<PublicStatus["report"]>): void {
  const prev = readStatus(slug);
  if (!prev) { pendingReports.set(slug, report); return; }
  persistStatus({ ...prev, report });
}
const pendingReports = new Map<string, NonNullable<PublicStatus["report"]>>();
function persistStatus(s: PublicStatus): void {
  mkdirSync(join(PUBLIC_RECORDS_DIR, "status"), { recursive: true });
  writeFileSync(statusPath(s.project), JSON.stringify(s, null, 2) + "\n");
}
function writeStatus(slug: string, o: { runUrl: string | null; activity: PublicStatus["activity"]; st: AutonomyState; prs: number; now: string; dryRun: boolean }): PublicStatus {
  const prev = readStatus(slug);
  const tasks = Object.values(o.st.tasks);
  const s: PublicStatus = {
    schema: "sc-cto-status/1",
    project: slug,
    updatedAt: o.now,
    runUrl: o.runUrl,
    report: pendingReports.get(slug) ?? prev?.report ?? null,
    activity: [...o.activity, ...(prev?.activity ?? [])].slice(0, 12),
    pendingTasks: tasks.filter((t) => !t.handled).length,
    operatorReview: tasks.filter((t) => t.handled === "operator-review").length,
    upstreamHead: o.st.upstreamHead ?? null,
    openLabPullRequests: o.prs,
  };
  if (!o.dryRun) persistStatus(s);
  return s;
}

/** Fetch up to 6 files the question links to (github.com/<lab>/blob/<sha>/<path>), at the lab head, for patch context. */
async function referencedFiles(gh: GitHubApi, labRepo: string, sha: string, body: string): Promise<Array<{ path: string; content: string }>> {
  const re = new RegExp(`https://github\\.com/${labRepo.replace(/[.]/g, "\\.")}/blob/[0-9a-f]{7,40}/([^\\s#)]+)`, "g");
  const paths = [...new Set([...body.matchAll(re)].map((m) => m[1]!))].slice(0, 6);
  const out: Array<{ path: string; content: string }> = [];
  for (const path of paths) {
    try {
      const f = await gh.get<{ content?: string; encoding?: string; type?: string }>(`/repos/${labRepo}/contents/${path}?ref=${sha}`);
      if (f.type === "file" && f.content) out.push({ path, content: Buffer.from(f.content, "base64").toString("utf8").slice(0, 20000) });
    } catch { /* missing file: skip */ }
  }
  return out;
}

/** Deterministically check and dispatch a Mind's requested actions. Returns one outcome line per action. */
async function handleActions(d: RunDeps, p: ProjectConfig, slug: string, taskId: string, resp: TaskResponse, mindName: string, activity: PublicStatus["activity"], log: (s: string) => void, nowIso: string): Promise<string[]> {
  const out: string[] = [];
  let patches = 0;
  for (const a of resp.actions ?? []) {
    if (a.type === "patch") {
      if (patches++ >= 1) { out.push("patch: skipped (one patch per task)"); continue; }
      const chk = checkPatch(a.patch, patchPolicyFor(p.validation.programDir ?? "contract"));
      const title = publicTextCheck(a.title, 120);
      if (!chk.ok || !title.ok) { out.push(`patch rejected: ${[...chk.reasons, ...title.reasons].join(", ")}`); log(`${taskId}: patch rejected (${chk.reasons.join(", ")})`); continue; }
      const dir = join(d.store.root, "lab-patches", slug);
      mkdirSync(dir, { recursive: true });
      writeFileSync(join(dir, `${taskId}.diff`), a.patch.replace(/\r\n/g, "\n"));
      writeFileSync(join(dir, `${taskId}.json`), JSON.stringify({ taskId, project: slug, title: title.text, rationale: publicTextCheck(a.rationale, 2000).text, sha256: chk.sha256, files: chk.files, added: chk.added, removed: chk.removed, mind: mindName, at: nowIso }, null, 2));
      // The private record must be pushed before lab-patch reads it: the workflow pushes the control repo first, then dispatches.
      pendingDispatches.push({ workflow: "lab-patch.yml", inputs: { project: slug, task_id: taskId, patch_sha256: chk.sha256 } });
      out.push(`patch queued ${chk.sha256.slice(0, 12)} (${chk.files.length} files, +${chk.added}/-${chk.removed})`);
      activity.push({ at: nowIso, text: `Wrote a patch (${chk.files.length} file${chk.files.length === 1 ? "" : "s"}, +${chk.added}/-${chk.removed}); applying it to a lab branch` });
    } else if (a.type === "devnet-transfer") {
      const t = loadTreasury();
      const req = { project: slug, recipient: a.recipient, lamports: a.lamports, reason: publicTextCheck(a.reason, 300).text, taskId, requestedBy: mindName };
      const errs = checkTransferRequest(req, t.address);
      if (errs.length) { out.push(`transfer rejected: ${errs.join(", ")}`); continue; }
      pendingDispatches.push({ workflow: "devnet-treasury.yml", inputs: { project: slug, recipient: req.recipient, lamports: String(req.lamports), reason: req.reason, task_id: taskId, requested_by: mindName } });
      out.push(`devnet transfer queued: ${req.lamports} lamports`);
      activity.push({ at: nowIso, text: `Requested a devnet treasury transfer (${req.lamports / 1e9} SOL)` });
    }
  }
  return out;
}

/** Workflow dispatches requested by Mind actions; written by the CLI for the workflow to send after private records are pushed. */
export const pendingDispatches: Array<{ workflow: string; inputs: Record<string, string> }> = [];
