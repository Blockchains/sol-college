// [mock/contract] Governance, validation, adoption, acceptance, certification, attendance.
import { test } from "node:test";
import assert from "node:assert/strict";
import { join } from "node:path";
import { readFileSync } from "node:fs";
import { cfg, gifter, run, tmp, GOOD, BAD, EXPECTED } from "../fixtures/helpers.ts";
import { validateProject, isPlaceholder, loadPolicies, loadConfig } from "../../src/config/project.ts";
import { evaluateCandidate } from "../../src/validation/evidence.ts";
import { buildManifest, storeManifest, readManifestBytes, existingPackageFor, type BuildInput } from "../../src/adoption/package.ts";
import { verifyAcceptance, AcceptanceDenied, storeAcceptance } from "../../src/acceptance/accept.ts";
import { issueCredential, publishCredential, changeCredentialStatus, CertificationRefused, draftStatus } from "../../src/certification/certificate.ts";
import { submitAttendance, attendanceLabel, manualReview, entitlementLabel } from "../../src/attendance/attendance.ts";
import { canonicalJson } from "../../src/lib/canonical.ts";
import type { GhIssueComment } from "../../src/github/api.ts";

const policies = loadPolicies();
const policy = policies.get("pilot-policy-v1")!;
const cand = { project: "gifter-escrow", repo: "Blockchains/gifter-escrow", sha: GOOD };

test("Governance: placeholder config is excluded from live execution and listings", () => {
  const ex = JSON.parse(readFileSync(join(process.cwd(), "../config/examples/project.example.json"), "utf8"));
  assert.equal(isPlaceholder(ex), true);
  const live = loadConfig(join(process.cwd(), "../config/examples"));
  assert.equal(live.projects.length, 0);
  assert.equal(live.excludedPlaceholders.length, 1);
});

test("Governance: semantic validation (empty scope, duplicate reviewers, unresolved policy, agent reviewer)", () => {
  const p = gifter();
  assert.deepEqual(validateProject(p, "gifter-escrow.json", policies), []);
  const bad = (mut: (x: ReturnType<typeof gifter>) => void, re: RegExp) => { const x = gifter(); mut(x); assert.ok(validateProject(x, "gifter-escrow.json", policies).some((i) => re.test(i.message)), re.source); };
  bad((x) => { x.research.scope = []; }, /scope/);
  bad((x) => { x.reviewers.push({ ...x.reviewers[0]! }); }, /unique/);
  bad((x) => { x.policyVersion = "pilot-policy-v9"; }, /does not resolve/);
  bad((x) => { x.reviewers = [{ github: "github-actions", githubId: 41898282, roles: ["adoption-acceptance"] }]; }, /./);
  bad((x) => { x.disclosure.publicFields.push("reviewers"); }, /may not be public/);
  bad((x) => { delete (x as { demonstrationNotice?: string }).demonstrationNotice; }, /demonstrationNotice/);
});

test("Validation: exact SHA required", () => {
  assert.equal(evaluateCandidate([run({ runId: 1 })], { ...cand, sha: "fb2bbfd" }, EXPECTED).passed, false);
  assert.equal(evaluateCandidate([run({ runId: 1 })], cand, EXPECTED).passed, true);
  assert.equal(evaluateCandidate([run({ runId: 1 }, BAD)], cand, EXPECTED).passed, false, "evidence for another SHA does not count");
});

test("Validation: required workflow identity verified (spoofed name from another workflow/repo/branch is ignored)", () => {
  for (const over of [{ workflowId: 9 }, { repositoryId: 9 }, { workflowPath: ".github/workflows/evil.yml" }, { headBranch: "attacker" }, { event: "pull_request_target" }]) {
    const v = evaluateCandidate([run({ runId: 5, ...over })], cand, EXPECTED);
    assert.equal(v.passed, false, JSON.stringify(over));
  }
});

test("Validation: known-bad candidate blocked; rerun semantics (newest run decides, older pass cannot hide newer failure)", () => {
  assert.equal(evaluateCandidate([run({ runId: 7 }, BAD, "failure")], { ...cand, sha: BAD }, EXPECTED).passed, false);
  const v = evaluateCandidate([run({ runId: 10 }), run({ runId: 11 }, GOOD, "failure")], cand, EXPECTED);
  assert.equal(v.passed, false);
  assert.equal(v.decidingRun?.runId, 11);
  const fixed = evaluateCandidate([run({ runId: 10 }, GOOD, "failure"), run({ runId: 11, runAttempt: 2 })], cand, EXPECTED);
  assert.equal(fixed.passed, true);
  assert.equal(evaluateCandidate([run({ runId: 12, status: "in_progress", conclusion: null })], cand, EXPECTED).passed, false);
  const noAttest = run({ runId: 13 });
  noAttest.jobs = noAttest.jobs.filter((j) => !j.name.startsWith("attest"));
  assert.equal(evaluateCandidate([noAttest], cand, EXPECTED).passed, false);
});

function input(over: Partial<BuildInput> = {}): BuildInput {
  return {
    project: gifter(),
    verdict: evaluateCandidate([run({ runId: 20 })], cand, EXPECTED),
    sourceDigest: "tree:" + "d".repeat(40),
    baseline: { sha: BAD, ancestry: "upstream-baseline-is-ancestor-of-candidate" },
    contributions: [{ title: "take_and_close fix", author: "Blockchains", prUrl: "https://github.com/Blockchains/gifter-escrow/pull/1", commits: [GOOD] }],
    narrative: { source: "operator", problem: "p", alternatives: [], risks: [], limitations: [], integration: "i", rollback: "r" },
    testConclusions: ["fixture passed"],
    version: 1,
    createdAt: "2026-11-15T16:00:00Z",
    ...over,
  };
}

test("Adoption: deterministic canonical bytes, hash over stored bytes, no overwrite, duplicate detection", () => {
  const d = tmp();
  const m = buildManifest(input());
  assert.equal(canonicalJson(m), canonicalJson(JSON.parse(canonicalJson(m))));
  const s1 = storeManifest(d, m);
  const s2 = storeManifest(d, buildManifest(input()));
  assert.equal(s1.created, true);
  assert.equal(s2.created, false);
  assert.equal(s1.sha256, s2.sha256);
  assert.equal(readManifestBytes(s1.path).sha256, s1.sha256);
  assert.ok(existingPackageFor(d, "gifter-escrow", GOOD));
  assert.throws(() => storeManifest(d, buildManifest(input({ testConclusions: ["changed"] }))), /refusing to overwrite/);
  assert.throws(() => buildManifest(input({ verdict: evaluateCandidate([run({ runId: 21 }, GOOD, "failure")], cand, EXPECTED) })), /not passed/);
});

function comment(over: Partial<GhIssueComment> = {}, body?: string, hash = ""): GhIssueComment {
  return { id: 1, body: body ?? `/sc-accept package=gifter-escrow-fb2bbfd2e101-v1 sha256=${hash} candidate=${GOOD}`, html_url: "https://github.com/Blockchains/sol-college/issues/9#issuecomment-1", created_at: "2026-11-15T17:00:00Z", updated_at: "2026-11-15T17:00:00Z", author_association: "OWNER", user: { login: "Blockchains", id: 11951015, type: "User" }, ...over };
}

function ctx(over: { comment?: GhIssueComment; head?: string; verdict?: ReturnType<typeof evaluateCandidate> } = {}) {
  const d = tmp();
  const m = buildManifest(input());
  const s = storeManifest(d, m);
  return { project: gifter(), policy, comment: over.comment ?? comment({}, undefined, s.sha256), commentRepo: "Blockchains/sol-college", manifest: m, storedManifestSha256: s.sha256, currentUpstreamHead: over.head ?? BAD, currentVerdict: over.verdict ?? evaluateCandidate([run({ runId: 20 })], cand, EXPECTED) };
}

test("Governance: authorised reviewer acceptance binds project, package, candidate, hash, baseline, reviewer, time", () => {
  const rec = verifyAcceptance(ctx());
  assert.equal(rec.reviewer.login, "Blockchains");
  assert.equal(rec.candidateSha, GOOD);
  assert.equal(rec.upstreamBaseline, BAD);
  const d = tmp();
  assert.equal(storeAcceptance(d, rec).created, true);
  assert.equal(storeAcceptance(d, rec).created, false, "duplicate acceptance does not create another");
});

test("Governance: unauthorised reviewer denied", () => {
  const c = ctx();
  assert.throws(() => verifyAcceptance({ ...c, comment: { ...c.comment, user: { login: "mallory", id: 42, type: "User" } } }), AcceptanceDenied);
  assert.throws(() => verifyAcceptance({ ...c, comment: { ...c.comment, user: { login: "Blockchains", id: 42, type: "User" } } }), /not an authorised/, "login reuse with a different account id is denied");
  assert.throws(() => verifyAcceptance({ ...c, comment: { ...c.comment, author_association: "NONE" } }), /association/);
});

test("Governance: agent cannot self-accept (bots, configured agent identities, non-command text)", () => {
  const c = ctx();
  assert.throws(() => verifyAcceptance({ ...c, comment: { ...c.comment, user: { login: "github-actions[bot]", id: 41898282, type: "Bot" } } }), /agents and bots/);
  assert.throws(() => verifyAcceptance({ ...c, comment: { ...c.comment, body: '{"reviewer":"Blockchains","accepted":true}' } }), /well-formed/);
});

test("Governance: stale acceptance denied (hash, upstream moved, newer failing run, edited comment)", () => {
  const c = ctx();
  assert.throws(() => verifyAcceptance({ ...c, storedManifestSha256: "0".repeat(64) }), /stale/);
  assert.throws(() => verifyAcceptance(ctx({ head: "e".repeat(40) })), /upstream head changed/);
  assert.throws(() => verifyAcceptance(ctx({ verdict: evaluateCandidate([run({ runId: 20 }), run({ runId: 30 }, GOOD, "failure")], cand, EXPECTED) })), /not passing/);
  assert.throws(() => verifyAcceptance(ctx({ verdict: evaluateCandidate([run({ runId: 20 }), run({ runId: 31 })], cand, EXPECTED) })), /newer validation run/);
  assert.throws(() => verifyAcceptance({ ...c, comment: { ...c.comment, updated_at: "2026-11-15T18:00:00Z" } }), /edited/);
});

test("Certification: lab merge insufficient; explicit project acceptance required; revocation visible", () => {
  const c = ctx();
  const acc = verifyAcceptance(c);
  const base = { manifest: c.manifest, manifestSha256: c.storedManifestSha256, subject: "Blockchains", issuedAt: "2026-11-15T17:05:00Z", verifyBaseUrl: "https://sol.college/campus/verify/" };
  assert.throws(() => issueCredential({ ...base, acceptance: undefined, acceptanceVerified: false, labMergeOnly: true }), CertificationRefused);
  assert.throws(() => issueCredential({ ...base, acceptance: undefined, acceptanceVerified: false }), /no verified project acceptance/);
  assert.throws(() => issueCredential({ ...base, acceptance: acc, acceptanceVerified: false }), /no verified/);
  assert.throws(() => issueCredential({ ...base, acceptance: { ...acc, manifestSha256: "f".repeat(64) }, acceptanceVerified: true }), /exact package/);
  assert.equal(draftStatus("p").status, "draft");
  const cred = issueCredential({ ...base, acceptance: acc, acceptanceVerified: true });
  assert.equal(cred.verification.type, "platform-published-verification-record");
  assert.ok(cred.disclaimers.some((d) => /accreditation/.test(d)));
  const d = tmp();
  assert.equal(publishCredential(d, cred).created, true);
  assert.equal(publishCredential(d, cred).created, false, "duplicate credential prevented");
  const reg = changeCredentialStatus(d, cred.credentialId, "revoked", "test revocation", "2026-11-15T18:00:00Z");
  assert.equal(reg.credentials[0]!.status, "revoked");
  assert.equal(reg.credentials[0]!.statusHistory.length, 2);
  assert.throws(() => changeCredentialStatus(d, cred.credentialId, "superseded", "x", "y"), /already revoked/);
});

test("Attendance/payment: pending transfer is not called verified; manual entitlement is not paid settlement", () => {
  const s = submitAttendance({ developer: "dev", wallet: "m4AcRjHcQzpvejFnU9KBEgf9z7pwni84CrGpARCoJpr", devnetSignature: "5".repeat(88), recipient: "m4AcRjHcQzpvejFnU9KBEgf9z7pwni84CrGpARCoJpr", amountLamports: 1000, window: { start: "a", end: "b" }, ruleVersion: "attendance-v1" });
  assert.equal(s.status, "pending");
  assert.doesNotMatch(attendanceLabel(s), /^verified/i);
  assert.match(attendanceLabel(s), /not verified/);
  assert.throws(() => manualReview(s, "mallory", true, "", "t", ["Blockchains"]));
  const r = manualReview(s, "Blockchains", true, "checked explorer", "t", ["Blockchains"]);
  assert.match(attendanceLabel(r), /not automatically verified/);
  assert.match(entitlementLabel({ plan: "pilot", status: "active", activation: "manual", paymentVerification: "none-manual-entitlement" }, "2026-11-15"), /payment not verified/);
  assert.match(entitlementLabel({ plan: "pilot", status: "active", activation: "manual", paymentVerification: "none-manual-entitlement", periodEnd: "2026-01-01" }, "2026-11-15"), /expired/);
  void cfg;
});
