import type { GitHubApi, GhArtifact, GhJob, GhRepo, GhRun, GhWorkflow } from "../github/api.ts";

const SHA_RE = /^[0-9a-f]{40}$/;

export interface CandidateRef {
  project: string;
  repo: string; // lab repository
  sha: string; // exact 40-char commit
}

export interface RunEvidence {
  repository: string;
  repositoryId: number;
  workflowId: number;
  workflowPath: string;
  runId: number;
  runAttempt: number;
  workflowVersionSha: string;
  headBranch: string;
  event: string;
  status: string;
  conclusion: string | null;
  createdAt: string;
  htmlUrl: string;
  candidate: CandidateRef;
  jobs: Array<{ name: string; conclusion: string | null; runAttempt: number }>;
  artifacts: Array<{ id: number; name: string; digest: string | null; expired: boolean }>;
}

export interface EvidenceQuery {
  workflowRepo: string;
  workflowPath: string;
  titlePrefix: string;
  candidate: CandidateRef;
  requiredJobs: string[];
}

export function runTitle(prefix: string, c: CandidateRef): string {
  return `${prefix} ${c.project} ${c.repo}@${c.sha}`;
}

/**
 * Retrieve validation evidence from GitHub itself (never from caller claims). A run is only
 * considered if it comes from the expected repository id, the expected workflow id AND path,
 * a workflow_dispatch on the protected default branch, and its title names the exact candidate.
 */
export async function fetchValidationEvidence(gh: GitHubApi, q: EvidenceQuery): Promise<RunEvidence[]> {
  if (!SHA_RE.test(q.candidate.sha)) throw new Error("exact 40-character candidate SHA required");
  const repo = await gh.get<GhRepo>(`/repos/${q.workflowRepo}`);
  const file = q.workflowPath.split("/").pop()!;
  const wf = await gh.get<GhWorkflow>(`/repos/${q.workflowRepo}/actions/workflows/${file}`);
  if (wf.path !== q.workflowPath) throw new Error(`workflow path mismatch: ${wf.path}`);
  const runs = await gh.get<{ workflow_runs: GhRun[] }>(`/repos/${q.workflowRepo}/actions/workflows/${wf.id}/runs?per_page=100&event=workflow_dispatch`);
  const title = runTitle(q.titlePrefix, q.candidate);
  const out: RunEvidence[] = [];
  for (const run of runs.workflow_runs) {
    if (run.display_title !== title) continue;
    const jobs = await gh.get<{ jobs: GhJob[] }>(`/repos/${q.workflowRepo}/actions/runs/${run.id}/jobs?filter=latest`);
    const arts = await gh.get<{ artifacts: GhArtifact[] }>(`/repos/${q.workflowRepo}/actions/runs/${run.id}/artifacts`);
    out.push({
      repository: run.repository.full_name,
      repositoryId: run.repository.id,
      workflowId: run.workflow_id,
      workflowPath: run.path.split("@")[0]!,
      runId: run.id,
      runAttempt: run.run_attempt,
      workflowVersionSha: run.head_sha,
      headBranch: run.head_branch,
      event: run.event,
      status: run.status,
      conclusion: run.conclusion,
      createdAt: run.created_at,
      htmlUrl: run.html_url,
      candidate: q.candidate,
      jobs: jobs.jobs.map((j) => ({ name: j.name, conclusion: j.conclusion, runAttempt: j.run_attempt })),
      artifacts: arts.artifacts.map((a) => ({ id: a.id, name: a.name, digest: a.digest ?? null, expired: a.expired })),
    });
  }
  if (out.some((e) => e.repositoryId !== repo.id)) throw new Error("run repository id does not match the workflow repository");
  return out;
}

export interface CandidateVerdict {
  candidate: CandidateRef;
  passed: boolean;
  decidingRun?: RunEvidence;
  reasons: string[];
  consideredRuns: number[];
}

export interface Expected {
  repositoryId: number;
  workflowId: number;
  workflowPath: string;
  defaultBranch: string;
  requiredJobs: string[];
}

/**
 * Rerun policy: the newest run (highest run id) for the exact candidate decides, at its latest
 * attempt. An older pass never hides a newer failure. Spoofed runs (wrong repo id, workflow id or
 * path, branch or event) are discarded before the newest run is chosen.
 */
export function evaluateCandidate(evidence: RunEvidence[], candidate: CandidateRef, expected: Expected): CandidateVerdict {
  const reasons: string[] = [];
  if (!SHA_RE.test(candidate.sha)) return { candidate, passed: false, reasons: ["exact 40-character candidate SHA required"], consideredRuns: [] };
  const genuine = evidence.filter((e) => {
    const bad: string[] = [];
    if (e.repositoryId !== expected.repositoryId) bad.push("repository id");
    if (e.workflowId !== expected.workflowId) bad.push("workflow id");
    if (e.workflowPath !== expected.workflowPath) bad.push("workflow path");
    if (e.headBranch !== expected.defaultBranch) bad.push("branch");
    if (e.event !== "workflow_dispatch") bad.push("event");
    if (e.candidate.sha !== candidate.sha || e.candidate.repo !== candidate.repo || e.candidate.project !== candidate.project) bad.push("candidate");
    if (bad.length) reasons.push(`run ${e.runId} ignored: ${bad.join(", ")} mismatch`);
    return bad.length === 0;
  });
  if (genuine.length === 0) return { candidate, passed: false, reasons: [...reasons, "no genuine validation run for this exact candidate"], consideredRuns: [] };
  const newest = [...genuine].sort((a, b) => b.runId - a.runId)[0]!;
  const consideredRuns = genuine.map((e) => e.runId);
  if (newest.status !== "completed") return { candidate, passed: false, decidingRun: newest, reasons: [...reasons, `newest run ${newest.runId} is ${newest.status}`], consideredRuns };
  if (newest.conclusion !== "success") return { candidate, passed: false, decidingRun: newest, reasons: [...reasons, `newest run ${newest.runId} concluded ${newest.conclusion}`], consideredRuns };
  for (const j of expected.requiredJobs) {
    const job = newest.jobs.find((x) => x.name === j || x.name.startsWith(`${j} `));
    if (!job) reasons.push(`required job ${j} missing`);
    else if (job.conclusion !== "success") reasons.push(`required job ${j} concluded ${job.conclusion}`);
  }
  const attest = newest.jobs.find((x) => x.name.startsWith("attest"));
  if (attest && !attest.name.includes(candidate.sha)) reasons.push("attest job does not name the exact candidate SHA");
  const failed = reasons.some((r) => r.startsWith("required job") || r.startsWith("attest"));
  return { candidate, passed: !failed, decidingRun: newest, reasons, consideredRuns };
}
