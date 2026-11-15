import { join } from "node:path";
import type { GhIssueComment } from "../github/api.ts";
import type { Policy, ProjectConfig } from "../config/types.ts";
import { writeImmutableCanonical } from "../lib/store.ts";
import { sha256Hex, canonicalBytes } from "../lib/canonical.ts";
import type { AdoptionManifest } from "../adoption/package.ts";
import type { CandidateVerdict } from "../validation/evidence.ts";

export interface AcceptanceCommand {
  packageId: string;
  manifestSha256: string;
  candidateSha: string;
}

const CMD_RE = /^\/sc-accept\s+package=([a-z0-9-]+)\s+sha256=([0-9a-f]{64})\s+candidate=([0-9a-f]{40})\s*$/m;

export function parseAcceptanceComment(body: string, command = "/sc-accept"): AcceptanceCommand | undefined {
  if (command !== "/sc-accept") throw new Error("unsupported acceptance command");
  const m = CMD_RE.exec(body);
  if (!m) return undefined;
  return { packageId: m[1]!, manifestSha256: m[2]!, candidateSha: m[3]! };
}

export interface AcceptanceContext {
  project: ProjectConfig;
  policy: Policy;
  comment: GhIssueComment; // fetched from the GitHub API by id, not from the event payload alone
  commentRepo: string;
  manifest: AdoptionManifest;
  storedManifestSha256: string; // hash of the exact stored bytes, recomputed now
  currentUpstreamHead: string; // trusted current head
  currentVerdict: CandidateVerdict; // re-evaluated now from GitHub
}

export interface AcceptanceRecord {
  schema: "sc-acceptance/1";
  acceptanceId: string;
  decision: "adoption-acceptance";
  project: { projectId: string; slug: string };
  packageId: string;
  manifestSha256: string;
  candidateSha: string;
  upstreamBaseline: string;
  reviewer: { login: string; id: number; authorAssociation: string };
  decidedAt: string;
  evidence: { commentUrl: string; commentId: number; repo: string };
  notProductionDeployment: true;
}

export class AcceptanceDenied extends Error {
  constructor(message: string) {
    super(message);
    this.name = "AcceptanceDenied";
  }
}

/** Verify an acceptance decision against current state. Throws AcceptanceDenied; records nothing on failure. */
export function verifyAcceptance(ctx: AcceptanceContext): AcceptanceRecord {
  const cmd = parseAcceptanceComment(ctx.comment.body, ctx.policy.acceptance.command);
  if (!cmd) throw new AcceptanceDenied("comment is not a well-formed acceptance command");
  const login = ctx.comment.user.login;
  const agents = new Set(ctx.policy.agentIdentities.map((a) => a.toLowerCase()));
  if (ctx.comment.user.type !== "User" || agents.has(login.toLowerCase()) || login.endsWith("[bot]")) throw new AcceptanceDenied("agents and bots cannot accept");
  const reviewer = ctx.project.reviewers.find((r) => r.githubId === ctx.comment.user.id && r.github.toLowerCase() === login.toLowerCase());
  if (!reviewer || !reviewer.roles.includes(ctx.policy.acceptance.requiredRole)) throw new AcceptanceDenied(`${login} is not an authorised ${ctx.policy.acceptance.requiredRole} reviewer for ${ctx.project.slug}`);
  if (!ctx.policy.acceptance.allowedAuthorAssociations.includes(ctx.comment.author_association)) throw new AcceptanceDenied(`author association ${ctx.comment.author_association} not allowed`);
  if (ctx.comment.updated_at !== ctx.comment.created_at) throw new AcceptanceDenied("edited comments are not accepted; post a new decision");
  if (cmd.packageId !== ctx.manifest.packageId) throw new AcceptanceDenied("package id mismatch");
  if (cmd.manifestSha256 !== ctx.storedManifestSha256) throw new AcceptanceDenied("stale approval: manifest hash does not match stored bytes");
  if (cmd.candidateSha !== ctx.manifest.candidate.sha) throw new AcceptanceDenied("candidate SHA mismatch");
  if (ctx.manifest.project.slug !== ctx.project.slug) throw new AcceptanceDenied("package belongs to another project");
  if (ctx.manifest.baseline.sha !== ctx.currentUpstreamHead) throw new AcceptanceDenied("stale approval: upstream head changed since the package was built; re-validate and repackage");
  if (!ctx.currentVerdict.passed || ctx.currentVerdict.candidate.sha !== cmd.candidateSha) throw new AcceptanceDenied(`stale approval: current validation verdict is not passing (${ctx.currentVerdict.reasons.join("; ")})`);
  if (ctx.currentVerdict.decidingRun && ctx.currentVerdict.decidingRun.runId !== ctx.manifest.evidence.runId) throw new AcceptanceDenied("stale approval: a newer validation run exists; repackage");
  if (Date.parse(ctx.comment.created_at) < Date.parse(ctx.manifest.createdAt)) throw new AcceptanceDenied("decision predates the package");
  const base = { packageId: cmd.packageId, manifestSha256: cmd.manifestSha256, candidateSha: cmd.candidateSha, reviewer: ctx.comment.user.id };
  return {
    schema: "sc-acceptance/1",
    acceptanceId: `acc-${sha256Hex(canonicalBytes(base)).slice(0, 16)}`,
    decision: "adoption-acceptance",
    project: { projectId: ctx.project.projectId, slug: ctx.project.slug },
    packageId: cmd.packageId,
    manifestSha256: cmd.manifestSha256,
    candidateSha: cmd.candidateSha,
    upstreamBaseline: ctx.manifest.baseline.sha,
    reviewer: { login, id: ctx.comment.user.id, authorAssociation: ctx.comment.author_association },
    decidedAt: ctx.comment.created_at,
    evidence: { commentUrl: ctx.comment.html_url, commentId: ctx.comment.id, repo: ctx.commentRepo },
    notProductionDeployment: true,
  };
}

/** Persist once (duplicate requests return the existing record; different content is refused). */
export function storeAcceptance(dir: string, rec: AcceptanceRecord): { path: string; created: boolean } {
  const path = join(dir, rec.project.slug, `${rec.packageId}.json`);
  const { created } = writeImmutableCanonical(path, rec);
  return { path, created };
}
