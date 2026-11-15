import { mkdtempSync } from "node:fs";
import { tmpdir } from "node:os";
import { join } from "node:path";
import { FileStore } from "../../src/lib/store.ts";
import { loadConfig } from "../../src/config/project.ts";
import type { ProjectConfig } from "../../src/config/types.ts";
import type { RunEvidence } from "../../src/validation/evidence.ts";

export const tmp = (p = "sc-") => mkdtempSync(join(tmpdir(), p));
export const store = () => new FileStore(tmp("sc-store-"));
export const cfg = () => loadConfig();
export const gifter = (): ProjectConfig => structuredClone(cfg().projects.find((p) => p.slug === "gifter-escrow")!);

export const GOOD = "fb2bbfd2e101c9e2600f6f6558c3335f691d5384";
export const BAD = "a9c3a417d2d78294f58975b1461859ffb20df05a";
export const EXPECTED = { repositoryId: 1000, workflowId: 2000, workflowPath: ".github/workflows/candidate-validation.yml", defaultBranch: "main", requiredJobs: ["untrusted-validate", "attest"] };

export function run(over: Partial<RunEvidence> & { runId: number }, sha = GOOD, conclusion: string | null = "success"): RunEvidence {
  return {
    repository: "Blockchains/sol-college",
    repositoryId: 1000,
    workflowId: 2000,
    workflowPath: ".github/workflows/candidate-validation.yml",
    runAttempt: 1,
    workflowVersionSha: "c".repeat(40),
    headBranch: "main",
    event: "workflow_dispatch",
    status: "completed",
    conclusion,
    createdAt: "2026-11-15T15:00:00Z",
    htmlUrl: `https://github.com/Blockchains/sol-college/actions/runs/${over.runId}`,
    candidate: { project: "gifter-escrow", repo: "Blockchains/gifter-escrow", sha },
    jobs: [
      { name: "check-request", conclusion: "success", runAttempt: 1 },
      { name: "untrusted-validate", conclusion, runAttempt: 1 },
      { name: `attest Blockchains/gifter-escrow@${sha}`, conclusion, runAttempt: 1 },
    ],
    artifacts: [{ id: 1, name: "attestation", digest: "sha256:abc", expired: false }],
    ...over,
  };
}
