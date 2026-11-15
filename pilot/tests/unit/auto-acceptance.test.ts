import { test } from "node:test";
import assert from "node:assert/strict";
import { join } from "node:path";
import { loadConfig } from "../../src/config/project.ts";
import { PUBLIC_RECORDS_DIR } from "../../src/lib/paths.ts";
import { readManifestBytes } from "../../src/adoption/package.ts";
import { verifyAutoAcceptance, AcceptanceDenied, AUTO_ACCEPT_LABEL } from "../../src/acceptance/accept.ts";
import { issueCredential } from "../../src/certification/certificate.ts";

const cfg = loadConfig();
const project = cfg.projects.find((p) => p.slug === "gifter-escrow")!;
const pkg = readManifestBytes(join(PUBLIC_RECORDS_DIR, "adoption", "gifter-escrow", "gifter-escrow-5628bfc9439f-v1.json"));
const passing = { candidate: { project: "gifter-escrow", repo: project.lab.repo, sha: pkg.manifest.candidate.sha }, passed: true, decidingRun: { runId: pkg.manifest.evidence.runId, htmlUrl: pkg.manifest.evidence.runUrl } as never, reasons: [], consideredRuns: [] };
const ctx = { project, manifest: pkg.manifest, storedBytes: pkg.bytes, storedManifestSha256: pkg.sha256, currentVerdict: passing, now: "2026-11-15T18:40:00Z" };

test("Auto-acceptance (owner policy t690u): accepted when validation passed on the exact candidate and the package hash matches; labelled as no human review", () => {
  const rec = verifyAutoAcceptance(ctx);
  assert.equal(rec.method, "auto-owner-policy");
  assert.equal(rec.reviewer.login, AUTO_ACCEPT_LABEL);
  assert.equal(rec.autoPolicy?.humanReviewed, false);
  assert.equal(rec.manifestSha256, pkg.sha256);
  const cred = issueCredential({ acceptance: rec, acceptanceVerified: true, manifest: pkg.manifest, manifestSha256: pkg.sha256, subject: pkg.manifest.contributions[0]!.author, issuedAt: "2026-11-15T18:41:00Z", verifyBaseUrl: "https://sol.college/campus/" });
  assert.equal(cred.acceptanceEvidence.humanReviewed, false);
  assert.match(cred.disclaimers[0]!, /no human reviewed/);
});

test("Auto-acceptance is refused when any condition fails", () => {
  assert.throws(() => verifyAutoAcceptance({ ...ctx, currentVerdict: { ...passing, passed: false, reasons: ["failed"] } }), AcceptanceDenied);
  assert.throws(() => verifyAutoAcceptance({ ...ctx, currentVerdict: { ...passing, candidate: { ...passing.candidate, sha: "0".repeat(40) } } }), /candidate commit mismatch/);
  assert.throws(() => verifyAutoAcceptance({ ...ctx, storedManifestSha256: "0".repeat(64) }), /sha256/);
  assert.throws(() => verifyAutoAcceptance({ ...ctx, storedBytes: Buffer.concat([pkg.bytes, Buffer.from(" ")]) }), /sha256/);
  assert.throws(() => verifyAutoAcceptance({ ...ctx, currentVerdict: { ...passing, decidingRun: { runId: 1, htmlUrl: "x" } as never } }), /newer validation run/);
});
