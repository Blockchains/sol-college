/** Shared adoption-package creation (CLI and autonomy). Evidence is always fetched from GitHub. */
import { join } from "node:path";
import type { LoadedConfig } from "../config/project.ts";
import { getPolicy, getProject } from "../config/project.ts";
import type { GhCompare, GhRepo, GhWorkflow, GitHubApi } from "../github/api.ts";
import { PUBLIC_RECORDS_DIR } from "../lib/paths.ts";
import { evaluateCandidate, fetchValidationEvidence, type CandidateVerdict } from "../validation/evidence.ts";
import { buildManifest, existingPackageFor, storeManifest, type Contribution, type Narrative } from "./package.ts";

export interface PackageInputs { contributions: Contribution[]; narrative: Narrative; testConclusions: string[]; version: number }

export async function candidateVerdict(gh: GitHubApi, cfg: LoadedConfig, slug: string, sha: string): Promise<CandidateVerdict> {
  const p = getProject(cfg, slug);
  const pol = getPolicy(cfg, p);
  const candidate = { project: slug, repo: p.lab.repo, sha };
  const evidence = await fetchValidationEvidence(gh, { workflowRepo: p.validation.workflowRepo, workflowPath: p.validation.workflowPath, titlePrefix: pol.validation.runTitlePrefix, candidate, requiredJobs: pol.validation.requiredJobs });
  const repo = await gh.get<GhRepo & { default_branch: string }>(`/repos/${p.validation.workflowRepo}`);
  const wf = await gh.get<GhWorkflow>(`/repos/${p.validation.workflowRepo}/actions/workflows/${p.validation.workflowPath.split("/").pop()}`);
  return evaluateCandidate(evidence, candidate, { repositoryId: repo.id, workflowId: wf.id, workflowPath: p.validation.workflowPath, defaultBranch: repo.default_branch, requiredJobs: pol.validation.requiredJobs });
}

export async function createAdoptionPackage(gh: GitHubApi, cfg: LoadedConfig, slug: string, sha: string, inputs: PackageInputs, opts: { allowNewVersion?: boolean } = {}) {
  const p = getProject(cfg, slug);
  const dir = join(PUBLIC_RECORDS_DIR, "adoption");
  const dup = existingPackageFor(dir, slug, sha);
  if (dup && !opts.allowNewVersion) return { outcome: "exists" as const, file: dup };
  const verdict = await candidateVerdict(gh, cfg, slug, sha);
  const upstreamHead = (await gh.get<{ commit: { sha: string } }>(`/repos/${p.upstream.repo}/branches/${encodeURIComponent(p.upstream.branch)}`)).commit.sha;
  const cmp = await gh.get<GhCompare>(`/repos/${p.lab.repo}/compare/${upstreamHead}...${sha}`);
  const ancestry = cmp.status === "ahead" || cmp.status === "identical" ? "upstream-baseline-is-ancestor-of-candidate" : `not-ancestor:${cmp.status}`;
  const commit = await gh.get<{ tree: { sha: string } }>(`/repos/${p.lab.repo}/git/commits/${sha}`);
  const manifest = buildManifest({ project: p, verdict, sourceDigest: `git-tree:${commit.tree.sha}`, baseline: { sha: upstreamHead, ancestry }, contributions: inputs.contributions, narrative: inputs.narrative, testConclusions: inputs.testConclusions, version: inputs.version, createdAt: new Date().toISOString() });
  const stored = storeManifest(dir, manifest);
  return { outcome: stored.created ? ("created" as const) : ("exists" as const), packageId: manifest.packageId, sha256: stored.sha256, path: stored.path.replace(PUBLIC_RECORDS_DIR, "records/public"), decidingRun: verdict.decidingRun?.htmlUrl, acceptCommand: `/sc-accept package=${manifest.packageId} sha256=${stored.sha256} candidate=${sha}` };
}
