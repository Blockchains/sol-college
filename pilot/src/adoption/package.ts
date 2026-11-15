import { existsSync, readFileSync, readdirSync } from "node:fs";
import { join } from "node:path";
import { canonicalBytes, sha256Hex } from "../lib/canonical.ts";
import { writeImmutableCanonical } from "../lib/store.ts";
import type { CandidateVerdict, RunEvidence } from "../validation/evidence.ts";
import type { ProjectConfig } from "../config/types.ts";

export const MANIFEST_SCHEMA = "sc-adoption-package/1";

export interface Contribution {
  title: string;
  author: string; // GitHub login
  prUrl: string;
  commits: string[];
}

export interface Narrative {
  source: "operator" | "mind-draft";
  problem: string;
  alternatives: string[];
  risks: string[];
  limitations: string[];
  integration: string;
  rollback: string;
}

export interface AdoptionManifest {
  schema: typeof MANIFEST_SCHEMA;
  packageId: string;
  version: number;
  project: { projectId: string; slug: string; ownership: string; demonstrationNotice: string | null };
  candidate: { repo: string; sha: string; sourceDigest: string; workflowVersionSha: string; toolchain: { anchor: string; solana: string } };
  baseline: { upstreamRepo: string; branch: string; sha: string; ancestry: string };
  policy: { version: string; scope: string[]; exclusions: string[] };
  contributions: Contribution[];
  evidence: { runId: number; runAttempt: number; runUrl: string; workflowPath: string; workflowId: number; repositoryId: number; conclusion: string | null; jobs: Array<{ name: string; conclusion: string | null }>; artifacts: Array<{ id: number; name: string; digest: string | null }> };
  testConclusions: string[];
  evidenceDigest: string;
  narrative: Narrative;
  attribution: string[];
  requestedDecision: string;
  createdAt: string;
}

export function packageIdFor(slug: string, candidateSha: string, version: number): string {
  return `${slug}-${candidateSha.slice(0, 12)}-v${version}`;
}

export interface BuildInput {
  project: ProjectConfig;
  verdict: CandidateVerdict;
  sourceDigest: string; // e.g. git tree SHA of the candidate commit (from GitHub)
  baseline: { sha: string; ancestry: string };
  contributions: Contribution[];
  narrative: Narrative;
  testConclusions: string[];
  version: number;
  createdAt: string;
}

/** Programmatic assembly of authoritative fields. Fails closed unless the exact candidate passed. */
export function buildManifest(i: BuildInput): AdoptionManifest {
  if (!i.verdict.passed || !i.verdict.decidingRun) throw new Error(`candidate ${i.verdict.candidate.sha} has not passed validation: ${i.verdict.reasons.join("; ")}`);
  if (i.baseline.ancestry !== "upstream-baseline-is-ancestor-of-candidate") throw new Error("baseline ancestry not verified");
  if (i.contributions.length === 0) throw new Error("at least one contribution is required");
  const run: RunEvidence = i.verdict.decidingRun;
  const evidence = {
    runId: run.runId,
    runAttempt: run.runAttempt,
    runUrl: run.htmlUrl,
    workflowPath: run.workflowPath,
    workflowId: run.workflowId,
    repositoryId: run.repositoryId,
    conclusion: run.conclusion,
    jobs: run.jobs.map((j) => ({ name: j.name, conclusion: j.conclusion })),
    artifacts: run.artifacts.map((a) => ({ id: a.id, name: a.name, digest: a.digest })),
  };
  return {
    schema: MANIFEST_SCHEMA,
    packageId: packageIdFor(i.project.slug, i.verdict.candidate.sha, i.version),
    version: i.version,
    project: { projectId: i.project.projectId, slug: i.project.slug, ownership: i.project.ownership, demonstrationNotice: i.project.demonstrationNotice ?? null },
    candidate: { repo: i.verdict.candidate.repo, sha: i.verdict.candidate.sha, sourceDigest: i.sourceDigest, workflowVersionSha: run.workflowVersionSha, toolchain: { anchor: i.project.validation.anchorVersion, solana: i.project.validation.solanaVersion } },
    baseline: { upstreamRepo: i.project.upstream.repo, branch: i.project.upstream.branch, sha: i.baseline.sha, ancestry: i.baseline.ancestry },
    policy: { version: i.project.policyVersion, scope: i.project.research.scope, exclusions: i.project.research.exclusions },
    contributions: i.contributions,
    evidence,
    testConclusions: i.testConclusions,
    evidenceDigest: sha256Hex(canonicalBytes(evidence)),
    narrative: i.narrative,
    attribution: i.contributions.map((c) => `${c.author}: ${c.title}`),
    requestedDecision: `Accept package ${packageIdFor(i.project.slug, i.verdict.candidate.sha, i.version)} (candidate ${i.verdict.candidate.sha}) as a project-accepted contribution. This is not a production deployment decision.`,
    createdAt: i.createdAt,
  };
}

export interface StoredPackage {
  path: string;
  sha256: string;
  created: boolean;
}

/** Write the exact canonical bytes once; the hash is over the stored bytes. Never overwrites. */
export function storeManifest(dir: string, m: AdoptionManifest): StoredPackage {
  const path = join(dir, m.project.slug, `${m.packageId}.json`);
  const { bytes, created } = writeImmutableCanonical(path, m);
  return { path, sha256: sha256Hex(bytes), created };
}

/** Find an existing package for the same candidate (duplicate requests must not create another). */
export function existingPackageFor(dir: string, slug: string, candidateSha: string): string | undefined {
  const d = join(dir, slug);
  if (!existsSync(d)) return undefined;
  return readdirSync(d).find((f) => f.startsWith(`${slug}-${candidateSha.slice(0, 12)}-v`));
}

export function readManifestBytes(path: string): { bytes: Buffer; sha256: string; manifest: AdoptionManifest } {
  const bytes = readFileSync(path);
  return { bytes, sha256: sha256Hex(bytes), manifest: JSON.parse(bytes.toString("utf8")) as AdoptionManifest };
}
