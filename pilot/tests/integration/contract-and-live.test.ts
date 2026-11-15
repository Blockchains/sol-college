// [contract] checks against the INSTALLED @animocabrands/minds-client-lib (no network).
// [live] tests are opt-in via env and are reported separately (SC_LIVE_GITHUB, SC_LIVE_BAZAAR, SC_LIVE_MINDS).
import { test } from "node:test";
import assert from "node:assert/strict";
import { BUILDER_API_KEY_ENV, createMindsClient } from "@animocabrands/minds-client-lib";
import { createServerMindsClient } from "../../src/minds/client.ts";
import { installedSdkVersion, inventory } from "../../src/minds/ops.ts";
import { GitHubApi, type GhRepo, type GhWorkflow } from "../../src/github/api.ts";
import { evaluateCandidate, fetchValidationEvidence } from "../../src/validation/evidence.ts";
import { GOOD, BAD, NEGATIVE } from "../fixtures/helpers.ts";

const PORT_METHODS = ["listMinds", "getMind", "checkMindName", "awakenMind", "updateMindStatus", "getCognitionBalance", "getCognitionUsage", "getCognitionUsageByTool", "listEquippedSkills", "equipSkills", "unequipSkills", "listEquippedApps", "equipApps", "unequipApps", "getCircle", "addCircleMembers", "removeCircleMembers", "ensureConversation", "getConversation", "listConversations", "sendMessage", "getHistory", "getLatestHistoryFingerprint", "waitForReply", "subscribeEvents", "eventsIterator", "getMindIdForAlias", "listCirclesForAccount", "createConversation"];

test("[contract] installed SDK exposes every method the adapter uses", () => {
  const c = createMindsClient({}) as unknown as Record<string, unknown>;
  for (const m of PORT_METHODS) assert.equal(typeof c[m], "function", m);
  const b = (c["bazaar"] ?? {}) as Record<string, unknown>;
  for (const m of ["listSkills", "getSkill", "listApps", "getApp", "collectSearchResults"]) assert.equal(typeof b[m], "function", `bazaar.${m}`);
  assert.equal(BUILDER_API_KEY_ENV, "MINDS_BUILDER_API_KEY");
  assert.match(installedSdkVersion(), /^\d+\.\d+\.\d+$/);
});

test("[contract] server client refuses to start without the Builder key (no browser/public fallback)", () => {
  assert.throws(() => createServerMindsClient({}), /MINDS_BUILDER_API_KEY is not set/);
});

test("[live] public Bazaar catalogue is reachable without a credential", { skip: !process.env["SC_LIVE_BAZAAR"] && "set SC_LIVE_BAZAAR=1" }, async () => {
  const r = await createMindsClient({}).bazaar.listSkills({ pageSize: 1 });
  assert.equal(typeof r.totalCount, "number");
});

test("[live] read-only Minds inventory with the protected Builder key", { skip: !(process.env["SC_LIVE_MINDS"] && process.env[BUILDER_API_KEY_ENV]) && "set SC_LIVE_MINDS=1 and the key" }, async () => {
  const inv = await inventory(createServerMindsClient());
  assert.ok(inv.mindCount >= 0);
  assert.ok(!JSON.stringify(inv).includes("@"), "no emails in sanitised inventory");
});

async function verdictFor(sha: string) {
  const gh = new GitHubApi(process.env["GITHUB_TOKEN"] ?? process.env["GH_TOKEN"]);
  const repo = "Blockchains/sol-college";
  const candidate = { project: "gifter-escrow", repo: "Blockchains/gifter-escrow", sha };
  const ev = await fetchValidationEvidence(gh, { workflowRepo: repo, workflowPath: ".github/workflows/candidate-validation.yml", titlePrefix: "candidate-validation", candidate, requiredJobs: ["untrusted-validate", "attest"] });
  const r = await gh.get<GhRepo & { default_branch: string }>(`/repos/${repo}`);
  const wf = await gh.get<GhWorkflow>(`/repos/${repo}/actions/workflows/candidate-validation.yml`);
  return evaluateCandidate(ev, candidate, { repositoryId: r.id, workflowId: wf.id, workflowPath: ".github/workflows/candidate-validation.yml", defaultBranch: r.default_branch, requiredJobs: ["untrusted-validate", "attest"] });
}

test("[live] GitHub evidence: known-good candidate (lab fix fb2bbfd) passes on its newest genuine run", { skip: !process.env["SC_LIVE_GITHUB"] && "set SC_LIVE_GITHUB=1" }, async () => {
  const v = await verdictFor(GOOD);
  assert.equal(v.passed, true, v.reasons.join("; "));
});

test("[live] GitHub evidence: negative-control candidate (e288388, maker underpaid by one unit) is blocked by the runtime fixture", { skip: !process.env["SC_LIVE_GITHUB"] && "set SC_LIVE_GITHUB=1" }, async () => {
  const v = await verdictFor(NEGATIVE);
  assert.equal(v.passed, false);
  assert.ok(v.decidingRun, "a genuine run exists and it failed");
});

// Honest record: the upstream baseline a9c3a41 (dangling PDA-seed temporaries, the cause of the devnet access
// violation) PASSES the local fixture with Solana 1.18.26 platform tools. The fixture does not reproduce that
// toolchain-dependent failure, so it is not claimed as a regression test for it.
test("[live] GitHub evidence: upstream baseline a9c3a41 has genuine evidence (fixture does not reproduce the devnet crash)", { skip: !process.env["SC_LIVE_GITHUB"] && "set SC_LIVE_GITHUB=1" }, async () => {
  const v = await verdictFor(BAD);
  assert.ok(v.decidingRun, "a genuine run exists");
});
