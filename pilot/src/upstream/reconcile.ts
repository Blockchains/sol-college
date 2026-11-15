import type { GitHubApi, GhCompare } from "../github/api.ts";
import type { FileStore } from "../lib/store.ts";

export interface UpstreamState {
  project: string;
  upstreamRepo: string;
  branch: string;
  head: string;
  previousHead: string | null;
  observedAt: string;
  sequence: number;
  divergedAt?: string;
}

export interface ExperimentRef {
  id: string;
  baseline: string; // upstream commit the experiment was based on
  candidateSha?: string;
  status: "idea" | "approved-experiment" | "tested-candidate" | "project-accepted" | "superseded";
}

export interface Impact {
  experiment: string;
  action: "current" | "rebase-and-retest" | "retest" | "superseded" | "baseline-not-ancestor";
  detail: string;
}

export interface ReconcileResult {
  outcome: "initialised" | "unchanged" | "advanced" | "stale-ignored" | "diverged-operator-review";
  state: UpstreamState;
  impacts: Impact[];
}

export type CompareFn = (base: string, head: string) => Promise<GhCompare["status"]>;

export function githubCompare(gh: GitHubApi, repo: string): CompareFn {
  return async (base, head) => (await gh.get<GhCompare>(`/repos/${repo}/compare/${base}...${head}`)).status;
}

/**
 * Trusted current-head reconciliation with a conditional (versioned) update. An observation
 * whose head is an ancestor of the recorded head (out-of-order/stale run) never rewinds state.
 * Ancestry is verified with GitHub compare, not inferred from stored fields.
 */
export async function reconcileUpstream(args: {
  store: FileStore;
  project: string;
  upstreamRepo: string;
  branch: string;
  observedHead: string;
  compare: CompareFn;
  experiments: ExperimentRef[];
  observedAt?: string;
}): Promise<ReconcileResult> {
  const k = `upstream/${args.project}`;
  const cur = args.store.read<UpstreamState>(k);
  const at = args.observedAt ?? new Date().toISOString();
  if (!cur) {
    const state: UpstreamState = { project: args.project, upstreamRepo: args.upstreamRepo, branch: args.branch, head: args.observedHead, previousHead: null, observedAt: at, sequence: 1 };
    args.store.write(k, state, 0);
    return { outcome: "initialised", state, impacts: await impacts(args.compare, args.observedHead, args.experiments) };
  }
  const prev = cur.data;
  if (prev.head === args.observedHead) return { outcome: "unchanged", state: prev, impacts: await impacts(args.compare, prev.head, args.experiments) };
  const rel = await args.compare(prev.head, args.observedHead);
  if (rel === "behind") return { outcome: "stale-ignored", state: prev, impacts: [] };
  const state: UpstreamState = { ...prev, previousHead: prev.head, head: args.observedHead, observedAt: at, sequence: prev.sequence + 1, ...(rel === "diverged" ? { divergedAt: at } : {}) };
  args.store.write(k, state, cur.version); // throws ConflictError if another run updated first
  return { outcome: rel === "diverged" ? "diverged-operator-review" : "advanced", state, impacts: await impacts(args.compare, args.observedHead, args.experiments) };
}

async function impacts(compare: CompareFn, head: string, exps: ExperimentRef[]): Promise<Impact[]> {
  const out: Impact[] = [];
  for (const e of exps) {
    if (e.status === "superseded") {
      out.push({ experiment: e.id, action: "superseded", detail: "marked superseded" });
      continue;
    }
    if (e.baseline === head) {
      out.push({ experiment: e.id, action: "current", detail: "baseline equals upstream head" });
      continue;
    }
    const rel = await compare(e.baseline, head);
    if (rel === "ahead") out.push({ experiment: e.id, action: e.candidateSha ? "rebase-and-retest" : "retest", detail: "upstream moved past the experiment baseline" });
    else out.push({ experiment: e.id, action: "baseline-not-ancestor", detail: `baseline is ${rel} relative to upstream head; verify history` });
  }
  return out;
}
