/**
 * acceptance <owner/repo> <commentId>   verify a /sc-accept comment fetched from GitHub; record it once (optional manual path)
 * acceptance auto <packageId>          owner policy t690u: accept without a comment when the exact candidate passed
 *                                       validation and the package bytes/hash/candidate match; recorded as auto-accepted
 */
import { readdirSync, existsSync, mkdirSync, appendFileSync } from "node:fs";
import { join } from "node:path";
import { loadConfig, getPolicy } from "../config/project.ts";
import { githubFromEnv, type GhIssueComment, type GhRepo, type GhWorkflow, type GitHubApi } from "../github/api.ts";
import { PUBLIC_RECORDS_DIR } from "../lib/paths.ts";
import { readManifestBytes } from "../adoption/package.ts";
import { evaluateCandidate, fetchValidationEvidence } from "../validation/evidence.ts";
import type { ProjectConfig, Policy } from "../config/types.ts";
import type { AdoptionManifest } from "../adoption/package.ts";
import { parseAcceptanceComment, storeAcceptance, verifyAcceptance, verifyAutoAcceptance, AcceptanceDenied } from "./accept.ts";

const gh = githubFromEnv();
const cfg = loadConfig();

function loadPackage(packageId: string): { project: ProjectConfig; policy: Policy; manifest: AdoptionManifest; sha256: string; bytes: Buffer } {
  const project = cfg.projects.find((p) => packageId.startsWith(`${p.slug}-`));
  if (!project) throw new AcceptanceDenied("package does not belong to a live project");
  const dir = join(PUBLIC_RECORDS_DIR, "adoption", project.slug);
  const file = existsSync(dir) ? readdirSync(dir).find((f) => f === `${packageId}.json`) : undefined;
  if (!file) throw new AcceptanceDenied(`package ${packageId} not found`);
  const { manifest, sha256, bytes } = readManifestBytes(join(dir, file));
  return { project, policy: getPolicy(cfg, project), manifest, sha256, bytes };
}

async function verdictFor(g: GitHubApi, project: ProjectConfig, policy: Policy, sha: string) {
  const candidate = { project: project.slug, repo: project.lab.repo, sha };
  const ev = await fetchValidationEvidence(g, { workflowRepo: project.validation.workflowRepo, workflowPath: project.validation.workflowPath, titlePrefix: policy.validation.runTitlePrefix, candidate, requiredJobs: policy.validation.requiredJobs });
  const repo = await g.get<GhRepo & { default_branch: string }>(`/repos/${project.validation.workflowRepo}`);
  const wf = await g.get<GhWorkflow>(`/repos/${project.validation.workflowRepo}/actions/workflows/${project.validation.workflowPath.split("/").pop()}`);
  return evaluateCandidate(ev, candidate, { repositoryId: repo.id, workflowId: wf.id, workflowPath: project.validation.workflowPath, defaultBranch: repo.default_branch, requiredJobs: policy.validation.requiredJobs });
}

const [a0, a1] = process.argv.slice(2);
if (a0 === "auto") {
  if (!a1) throw new Error("usage: acceptance auto <packageId>");
  const { project, policy, manifest, sha256, bytes } = loadPackage(a1);
  const verdict = await verdictFor(gh, project, policy, manifest.candidate.sha);
  const rec = verifyAutoAcceptance({ project, manifest, storedBytes: bytes, storedManifestSha256: sha256, currentVerdict: verdict, now: new Date().toISOString() });
  const stored = storeAcceptance(join(PUBLIC_RECORDS_DIR, "acceptance"), rec);
  const priv = process.env["SC_PRIVATE_RECORDS_DIR"];
  if (priv && stored.created) { mkdirSync(join(priv, "acceptance"), { recursive: true }); appendFileSync(join(priv, "acceptance", "log.jsonl"), JSON.stringify({ ...rec, runUrl: process.env["GITHUB_RUN_ID"] ? `https://github.com/${process.env["GITHUB_REPOSITORY"]}/actions/runs/${process.env["GITHUB_RUN_ID"]}` : null }) + "\n"); }
  console.log(JSON.stringify({ outcome: stored.created ? "recorded" : "exists", method: rec.method, label: rec.reviewer.login, acceptanceId: rec.acceptanceId, packageId: rec.packageId, subjectCandidates: manifest.contributions.map((c) => c.author) }));
} else {
  const [commentRepo, commentId] = [a0, a1];
  if (!commentRepo || !commentId) throw new Error("usage: acceptance <owner/repo> <commentId> | acceptance auto <packageId>");
  const comment = await gh.get<GhIssueComment>(`/repos/${commentRepo}/issues/comments/${commentId}`);
  const cmd = parseAcceptanceComment(comment.body);
  if (!cmd) {
    console.log(JSON.stringify({ outcome: "ignored", reason: "not an acceptance command" }));
    process.exit(0);
  }
  const { project, policy, manifest, sha256 } = loadPackage(cmd.packageId);
  const head = (await gh.get<{ commit: { sha: string } }>(`/repos/${project.upstream.repo}/branches/${encodeURIComponent(project.upstream.branch)}`)).commit.sha;
  const verdict = await verdictFor(gh, project, policy, manifest.candidate.sha);
  const rec = verifyAcceptance({ project, policy, comment, commentRepo, manifest, storedManifestSha256: sha256, currentUpstreamHead: head, currentVerdict: verdict });
  const stored = storeAcceptance(join(PUBLIC_RECORDS_DIR, "acceptance"), rec);
  console.log(JSON.stringify({ outcome: stored.created ? "recorded" : "exists", method: rec.method, acceptanceId: rec.acceptanceId, packageId: rec.packageId, subjectCandidates: manifest.contributions.map((c) => c.author) }));
}
