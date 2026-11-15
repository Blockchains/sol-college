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
  /** "manual-comment" (a reviewer's /sc-accept) or "auto-owner-policy" (no human reviewed it). Absent on older records = manual. */
  method?: "manual-comment" | "auto-owner-policy";
  autoPolicy?: { label: typeof AUTO_ACCEPT_LABEL; ref: string; humanReviewed: false; checks: string[]; validationRunUrl: string };
}

export const AUTO_ACCEPT_LABEL = "auto-accepted by owner policy (2026-11-15, user instruction)" as const;
export const AUTO_ACCEPT_REF = "owner-instruction-2026-11-15T18:29Z (t690u)";

export interface AutoAcceptanceContext {
  project: ProjectConfig;
  manifest: AdoptionManifest;
  storedBytes: Buffer;
  storedManifestSha256: string;
  agentIdentities?: string[];
  currentVerdict: CandidateVerdict;
  now: string;
}

/**
 * Owner policy t690u: accept without a human comment when ALL hold: candidate-validation passed on the exact
 * candidate commit, the adoption package exists, its sha256 matches the recomputed hash, and the candidate
 * commit matches. The record says plainly that no human reviewed it.
 */
export function verifyAutoAcceptance(ctx: AutoAcceptanceContext): AcceptanceRecord {
  const m = ctx.manifest;
  if (m.project.slug !== ctx.project.slug) throw new AcceptanceDenied("package belongs to another project");
  // No self-acceptance: work authored by an agent or bot identity (e.g. a Mind's lab patch pushed by Actions) is never
  // auto-accepted or certified; it needs a human contributor of record.
  const agents = new Set(["github-actions[bot]", "sol-college-cto[bot]", ...(ctx.agentIdentities ?? [])].map((a) => a.toLowerCase()));
  const botAuthors = m.contributions.map((c) => c.author).filter((a) => a.toLowerCase().endsWith("[bot]") || agents.has(a.toLowerCase()));
  if (botAuthors.length) throw new AcceptanceDenied(`agent-authored work cannot be auto-accepted (no self-acceptance): ${botAuthors.join(", ")}`);
  const recomputed = sha256Hex(canonicalBytes(m));
  if (recomputed !== ctx.storedManifestSha256 || sha256Hex(ctx.storedBytes) !== ctx.storedManifestSha256) throw new AcceptanceDenied("package sha256 does not match the recomputed canonical hash");
  if (sha256Hex(canonicalBytes(m.evidence)) !== m.evidenceDigest) throw new AcceptanceDenied("package evidence digest does not match its evidence");
  const v = ctx.currentVerdict;
  if (!v.passed || !v.decidingRun) throw new AcceptanceDenied(`candidate-validation has not passed on the exact candidate (${v.reasons.join("; ")})`);
  if (v.candidate.sha !== m.candidate.sha) throw new AcceptanceDenied("candidate commit mismatch");
  if (v.decidingRun.runId !== m.evidence.runId) throw new AcceptanceDenied("a newer validation run exists for this candidate; repackage");
  const base = { packageId: m.packageId, manifestSha256: recomputed, candidateSha: m.candidate.sha, reviewer: 0, method: "auto-owner-policy" };
  return {
    schema: "sc-acceptance/1",
    acceptanceId: `acc-${sha256Hex(canonicalBytes(base)).slice(0, 16)}`,
    decision: "adoption-acceptance",
    project: { projectId: ctx.project.projectId, slug: ctx.project.slug },
    packageId: m.packageId,
    manifestSha256: recomputed,
    candidateSha: m.candidate.sha,
    upstreamBaseline: m.baseline.sha,
    reviewer: { login: AUTO_ACCEPT_LABEL, id: 0, authorAssociation: "NONE (automated; no human reviewer)" },
    decidedAt: ctx.now,
    evidence: { commentUrl: v.decidingRun.htmlUrl, commentId: 0, repo: ctx.project.validation.workflowRepo },
    notProductionDeployment: true,
    method: "auto-owner-policy",
    autoPolicy: { label: AUTO_ACCEPT_LABEL, ref: AUTO_ACCEPT_REF, humanReviewed: false, checks: ["candidate-validation passed on the exact candidate commit", "adoption package exists", "package sha256 matches the recomputed canonical hash", "candidate commit matches the package"], validationRunUrl: v.decidingRun.htmlUrl },
  };
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
    method: "manual-comment",
  };
}

/** Persist once (duplicate requests return the existing record; different content is refused). */
export function storeAcceptance(dir: string, rec: AcceptanceRecord): { path: string; created: boolean } {
  const path = join(dir, rec.project.slug, `${rec.packageId}.json`);
  const { created } = writeImmutableCanonical(path, rec);
  return { path, created };
}
