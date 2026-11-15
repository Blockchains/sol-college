/** acceptance <owner/repo> <commentId>: verify an acceptance comment fetched from GitHub; record it once. */
import { readdirSync, existsSync } from "node:fs";
import { join } from "node:path";
import { loadConfig, getPolicy } from "../config/project.ts";
import { githubFromEnv, type GhIssueComment, type GhRepo, type GhWorkflow } from "../github/api.ts";
import { PUBLIC_RECORDS_DIR } from "../lib/paths.ts";
import { readManifestBytes } from "../adoption/package.ts";
import { evaluateCandidate, fetchValidationEvidence } from "../validation/evidence.ts";
import { parseAcceptanceComment, storeAcceptance, verifyAcceptance, AcceptanceDenied } from "./accept.ts";

const [commentRepo, commentId] = process.argv.slice(2);
if (!commentRepo || !commentId) throw new Error("usage: acceptance <owner/repo> <commentId>");
const gh = githubFromEnv();
const comment = await gh.get<GhIssueComment>(`/repos/${commentRepo}/issues/comments/${commentId}`);
const cmd = parseAcceptanceComment(comment.body);
if (!cmd) {
  console.log(JSON.stringify({ outcome: "ignored", reason: "not an acceptance command" }));
  process.exit(0);
}
const cfg = loadConfig();
const project = cfg.projects.find((p) => cmd.packageId.startsWith(`${p.slug}-`));
if (!project) throw new AcceptanceDenied("package does not belong to a live project");
const dir = join(PUBLIC_RECORDS_DIR, "adoption", project.slug);
const file = existsSync(dir) ? readdirSync(dir).find((f) => f === `${cmd.packageId}.json`) : undefined;
if (!file) throw new AcceptanceDenied(`package ${cmd.packageId} not found`);
const { manifest, sha256 } = readManifestBytes(join(dir, file));
const policy = getPolicy(cfg, project);
const head = (await gh.get<{ commit: { sha: string } }>(`/repos/${project.upstream.repo}/branches/${encodeURIComponent(project.upstream.branch)}`)).commit.sha;
const candidate = { project: project.slug, repo: project.lab.repo, sha: manifest.candidate.sha };
const ev = await fetchValidationEvidence(gh, { workflowRepo: project.validation.workflowRepo, workflowPath: project.validation.workflowPath, titlePrefix: policy.validation.runTitlePrefix, candidate, requiredJobs: policy.validation.requiredJobs });
const repo = await gh.get<GhRepo & { default_branch: string }>(`/repos/${project.validation.workflowRepo}`);
const wf = await gh.get<GhWorkflow>(`/repos/${project.validation.workflowRepo}/actions/workflows/${project.validation.workflowPath.split("/").pop()}`);
const verdict = evaluateCandidate(ev, candidate, { repositoryId: repo.id, workflowId: wf.id, workflowPath: project.validation.workflowPath, defaultBranch: repo.default_branch, requiredJobs: policy.validation.requiredJobs });
const rec = verifyAcceptance({ project, policy, comment, commentRepo, manifest, storedManifestSha256: sha256, currentUpstreamHead: head, currentVerdict: verdict });
const stored = storeAcceptance(join(PUBLIC_RECORDS_DIR, "acceptance"), rec);
console.log(JSON.stringify({ outcome: stored.created ? "recorded" : "exists", acceptanceId: rec.acceptanceId, packageId: rec.packageId, subjectCandidates: manifest.contributions.map((c) => c.author) }));
