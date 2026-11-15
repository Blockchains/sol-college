/**
 * adoption <slug> <candidateSha> <inputs.json>
 * Retrieves real GitHub evidence, verifies baseline ancestry and builds the exact manifest.
 * inputs.json: { contributions: Contribution[], narrative: Narrative, testConclusions: string[], version: number }
 */
import { readFileSync } from "node:fs";
import { join } from "node:path";
import { loadConfig, getProject, getPolicy } from "../config/project.ts";
import { githubFromEnv, type GhCompare, type GhRepo, type GhWorkflow } from "../github/api.ts";
import { PUBLIC_RECORDS_DIR } from "../lib/paths.ts";
import { evaluateCandidate, fetchValidationEvidence } from "../validation/evidence.ts";
import { buildManifest, existingPackageFor, storeManifest, type Contribution, type Narrative } from "./package.ts";

const [slug, sha, inputsPath] = process.argv.slice(2);
if (!slug || !sha || !inputsPath) throw new Error("usage: adoption <slug> <sha> <inputs.json>");
const inputs = JSON.parse(readFileSync(inputsPath, "utf8")) as { contributions: Contribution[]; narrative: Narrative; testConclusions: string[]; version: number };
const cfg = loadConfig();
const p = getProject(cfg, slug);
const pol = getPolicy(cfg, p);
const dir = join(PUBLIC_RECORDS_DIR, "adoption");
const dup = existingPackageFor(dir, slug, sha);
if (dup && !process.env["SC_NEW_VERSION"]) {
  console.log(JSON.stringify({ outcome: "exists", file: dup, note: "duplicate request: no new package created" }));
  process.exit(0);
}
const gh = githubFromEnv();
const candidate = { project: slug, repo: p.lab.repo, sha };
const evidence = await fetchValidationEvidence(gh, { workflowRepo: p.validation.workflowRepo, workflowPath: p.validation.workflowPath, titlePrefix: pol.validation.runTitlePrefix, candidate, requiredJobs: pol.validation.requiredJobs });
const repo = await gh.get<GhRepo & { default_branch: string }>(`/repos/${p.validation.workflowRepo}`);
const wf = await gh.get<GhWorkflow>(`/repos/${p.validation.workflowRepo}/actions/workflows/${p.validation.workflowPath.split("/").pop()}`);
const verdict = evaluateCandidate(evidence, candidate, { repositoryId: repo.id, workflowId: wf.id, workflowPath: p.validation.workflowPath, defaultBranch: repo.default_branch, requiredJobs: pol.validation.requiredJobs });
const upstreamHead = (await gh.get<{ commit: { sha: string } }>(`/repos/${p.upstream.repo}/branches/${encodeURIComponent(p.upstream.branch)}`)).commit.sha;
const cmp = await gh.get<GhCompare>(`/repos/${p.lab.repo}/compare/${upstreamHead}...${sha}`);
const ancestry = cmp.status === "ahead" || cmp.status === "identical" ? "upstream-baseline-is-ancestor-of-candidate" : `not-ancestor:${cmp.status}`;
const commit = await gh.get<{ tree: { sha: string } }>(`/repos/${p.lab.repo}/git/commits/${sha}`);
const manifest = buildManifest({ project: p, verdict, sourceDigest: `git-tree:${commit.tree.sha}`, baseline: { sha: upstreamHead, ancestry }, contributions: inputs.contributions, narrative: inputs.narrative, testConclusions: inputs.testConclusions, version: inputs.version, createdAt: new Date().toISOString() });
const stored = storeManifest(dir, manifest);
console.log(JSON.stringify({ outcome: stored.created ? "created" : "exists", packageId: manifest.packageId, sha256: stored.sha256, path: stored.path.replace(PUBLIC_RECORDS_DIR, "records/public"), decidingRun: verdict.decidingRun?.htmlUrl, acceptCommand: `/sc-accept package=${manifest.packageId} sha256=${stored.sha256} candidate=${sha}` }, null, 2));
