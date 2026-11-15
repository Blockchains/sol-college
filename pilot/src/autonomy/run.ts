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
import { dispatchTask, normaliseReplyText, reconcileTask, type TaskRecord, type TaskResponse, type TaskSpec, type SourceRef } from "../minds/task.ts";
import { candidateVerdict, createAdoptionPackage } from "../adoption/create.ts";
import { existingPackageFor } from "../adoption/package.ts";
import { githubCompare, reconcileUpstream, type ExperimentRef } from "../upstream/reconcile.ts";
import { FileStore as Store } from "../lib/store.ts";

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
  const reasons: string[] = [];
  if (t.length < 20) reasons.push("too short");
  if (t.length > max) reasons.push(`longer than ${max} characters`);
  if (EMAIL.test(t)) reasons.push("contains an email address");
  if (findSecretLeaks(t).length) reasons.push("contains secret-shaped text");
  if (EXCLUDED_TOPICS.test(t)) reasons.push("mentions an excluded topic");
  if (/https?:\/\/(?!github\.com\/|sol\.college\/)/i.test(t)) reasons.push("links outside github.com or sol.college");
  return { ok: reasons.length === 0, text: t, reasons };
}

/** Choose the first Mind proposal that may become a research-question issue. */
export function pickProposal(resp: TaskResponse, seen: string[]): { title: string; detail: string; hash: string } | null {
  for (const p of resp.proposals) {
    const title = publicTextCheck(p.title, 120);
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
    const verb: Record<Kind, string> = { "research-plan": "Drafting the next research question", "upstream-impact": "Assessing an upstream change", "pr-triage": "Triaging a lab pull request", "adoption-draft": "Drafting an adoption package", "progress-report": "Writing the Lab Reporter status", "smoke-test": "Running a smoke test" };
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
    if (meta.handled) continue;
    const stored = d.store.read<TaskRecord>(`tasks/${slug}/${taskId}`);
    if (!stored) { meta.handled = "missing-record"; continue; }
    let rec = stored.data;
    if (["uncertain", "dispatched", "dispatch-intent"].includes(rec.state) && !d.dryRun) rec = await reconcileTask({ minds: d.minds, store: d.store }, rec.spec);
    if (rec.state === "operator-review") { meta.handled = "operator-review"; log(`${taskId}: operator review (${rec.errors.join("; ")})`); continue; }
    if (rec.state !== "completed" || !rec.response) {
      if (hours(meta.createdAt, now) > 48) { meta.handled = "expired-no-reply"; log(`${taskId}: no reply after 48h; closed without resend`); }
      continue;
    }
    const resp = rec.response;
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
  for (const pr of prs) {
    if (st.prHeads[pr.url] === pr.headSha) continue;
    if (!st.validations[pr.headSha]) {
      const existing = await candidateVerdict(d.gh, d.cfg, slug, pr.headSha);
      if (existing.decidingRun) { st.validations[pr.headSha] = { dispatchedAt: existing.decidingRun.createdAt, prUrl: pr.url }; log(`existing validation evidence for ${pr.headSha.slice(0, 7)}; not re-dispatched`); }
    }
    if (!st.validations[pr.headSha] && !d.dryRun) {
      await d.gh.send("POST", `/repos/${p.validation.workflowRepo}/actions/workflows/${p.validation.workflowPath.split("/").pop()}/dispatches`, { ref: "main", inputs: { project: slug, lab_repo: p.lab.repo, candidate_sha: pr.headSha } });
      st.validations[pr.headSha] = { dispatchedAt: nowIso, prUrl: pr.url };
      activity.push({ at: nowIso, text: `Requested validation of ${pr.repo}#${pr.number} at ${pr.headSha.slice(0, 7)}`, url: pr.url });
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
