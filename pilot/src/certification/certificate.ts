import { existsSync, readFileSync } from "node:fs";
import { join } from "node:path";
import { canonicalBytes, canonicalJson, sha256Hex } from "../lib/canonical.ts";
import { writeImmutableCanonical } from "../lib/store.ts";
import { mkdirSync, writeFileSync } from "node:fs";
import type { AcceptanceRecord } from "../acceptance/accept.ts";
import type { AdoptionManifest } from "../adoption/package.ts";

export type CredentialStatus = "active" | "revoked" | "superseded";

export interface Credential {
  schema: "sc-contribution-credential/1";
  credentialId: string;
  subject: { github: string };
  project: { projectId: string; slug: string; ownership: string; demonstrationNotice: string | null };
  acceptedWork: string;
  prUrl: string;
  packageId: string;
  manifestSha256: string;
  acceptedCommit: string;
  acceptanceEvidence: { acceptanceId: string; reviewer: string; commentUrl: string; decidedAt: string; method: "manual-comment" | "auto-owner-policy"; humanReviewed: boolean; note?: string };
  issuer: "Sol.College";
  issuedAt: string;
  verification: { type: "platform-published-verification-record"; url: string; notes: string };
  disclaimers: string[];
}

export interface StatusEntry {
  credentialId: string;
  status: CredentialStatus;
  changedAt: string;
  reason?: string;
  supersededBy?: string;
}

export interface Registry {
  schema: "sc-credential-registry/1";
  credentials: Array<{ credentialId: string; subject: string; project: string; packageId: string; path: string; status: CredentialStatus; statusHistory: StatusEntry[] }>;
}

export class CertificationRefused extends Error {
  constructor(message: string) {
    super(message);
    this.name = "CertificationRefused";
  }
}

/** Draft view when no verified acceptance exists: no active certificate, no recognition badge. */
export function draftStatus(packageId: string): { status: "draft"; packageId: string; notice: string } {
  return { status: "draft", packageId, notice: "Draft only. No certificate is issued until an authorised project reviewer accepts this exact package." };
}

/**
 * Issue a narrow contribution credential. Fails closed unless a verified acceptance record exists
 * that binds the same package, manifest hash and candidate. A lab merge alone is insufficient.
 */
export function issueCredential(args: { acceptance: AcceptanceRecord | undefined; acceptanceVerified: boolean; manifest: AdoptionManifest; manifestSha256: string; subject: string; issuedAt: string; verifyBaseUrl: string; labMergeOnly?: boolean }): Credential {
  if (args.labMergeOnly) throw new CertificationRefused("a lab merge is not project acceptance");
  const a = args.acceptance;
  if (!a || !args.acceptanceVerified) throw new CertificationRefused("no verified project acceptance");
  if (a.packageId !== args.manifest.packageId || a.manifestSha256 !== args.manifestSha256 || a.candidateSha !== args.manifest.candidate.sha) throw new CertificationRefused("acceptance does not bind this exact package");
  const contribution = args.manifest.contributions.find((c) => c.author.toLowerCase() === args.subject.toLowerCase());
  if (!contribution) throw new CertificationRefused(`${args.subject} is not an attributed contributor in the package`);
  const id = `scc-${sha256Hex(canonicalBytes({ subject: args.subject.toLowerCase(), packageId: a.packageId, manifest: a.manifestSha256 })).slice(0, 20)}`;
  return {
    schema: "sc-contribution-credential/1",
    credentialId: id,
    subject: { github: args.subject },
    project: { ...args.manifest.project },
    acceptedWork: contribution.title,
    prUrl: contribution.prUrl,
    packageId: a.packageId,
    manifestSha256: a.manifestSha256,
    acceptedCommit: a.candidateSha,
    acceptanceEvidence: { acceptanceId: a.acceptanceId, reviewer: a.reviewer.login, commentUrl: a.evidence.commentUrl, decidedAt: a.decidedAt, method: a.method ?? "manual-comment", humanReviewed: a.method !== "auto-owner-policy", ...(a.method === "auto-owner-policy" ? { note: "Auto-accepted by owner policy (2026-11-15, user instruction): no human reviewed this contribution. Accepted because the exact candidate passed candidate-validation and the adoption package hash and candidate matched. The link is the validation run, not a review." } : {}) },
    issuer: "Sol.College",
    issuedAt: args.issuedAt,
    verification: { type: "platform-published-verification-record", url: `${args.verifyBaseUrl}?id=${id}`, notes: "Verification is the record published by Sol.College; it is not a cryptographic signature." },
    disclaimers: [...(a.method === "auto-owner-policy" ? ["Auto-accepted by owner policy (2026-11-15, user instruction); no human reviewed it."] : []), "Documents one accepted contribution only.", "Not an accreditation or assessment of general expertise.", "Not issued on-chain.", "Not cryptographically signed."],
  };
}

function loadRegistry(dir: string): Registry {
  const p = join(dir, "registry.json");
  return existsSync(p) ? (JSON.parse(readFileSync(p, "utf8")) as Registry) : { schema: "sc-credential-registry/1", credentials: [] };
}

function saveRegistry(dir: string, r: Registry): void {
  mkdirSync(dir, { recursive: true });
  writeFileSync(join(dir, "registry.json"), canonicalJson(r));
}

/** Publish: credential file is immutable; duplicate issuance returns the existing entry. */
export function publishCredential(dir: string, c: Credential): { created: boolean; path: string } {
  const rel = `${c.project.slug}/${c.credentialId}.json`;
  const { created } = writeImmutableCanonical(join(dir, rel), c);
  const reg = loadRegistry(dir);
  if (!reg.credentials.some((x) => x.credentialId === c.credentialId)) {
    reg.credentials.push({ credentialId: c.credentialId, subject: c.subject.github, project: c.project.slug, packageId: c.packageId, path: rel, status: "active", statusHistory: [{ credentialId: c.credentialId, status: "active", changedAt: c.issuedAt }] });
    saveRegistry(dir, reg);
  }
  return { created, path: rel };
}

/** Revocation/supersession is appended to the public registry, so it stays visible. */
export function changeCredentialStatus(dir: string, credentialId: string, status: "revoked" | "superseded", reason: string, at: string, supersededBy?: string): Registry {
  const reg = loadRegistry(dir);
  const e = reg.credentials.find((x) => x.credentialId === credentialId);
  if (!e) throw new Error(`unknown credential ${credentialId}`);
  if (e.status !== "active") throw new Error(`credential is already ${e.status}`);
  e.status = status;
  e.statusHistory.push({ credentialId, status, changedAt: at, reason, ...(supersededBy ? { supersededBy } : {}) });
  saveRegistry(dir, reg);
  return reg;
}
