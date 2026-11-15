import { test } from "node:test";
import assert from "node:assert/strict";
import { readFileSync } from "node:fs";
import { join } from "node:path";
import { parse } from "yaml";
import { loadAutonomy, pickProposal, publicTextCheck } from "../../src/autonomy/run.ts";
import { REPO_ROOT } from "../../src/lib/paths.ts";

const resp = (proposals: Array<{ title: string; detail: string }>) => ({ protocol: "sc-task-response/1" as const, taskId: "t-000001", project: "p", summary: "s", facts: [], hypotheses: [], proposals, evidenceRefs: [], uncertainties: [] });

test("Autonomy: public Mind text is gated (secrets, emails, excluded topics, outside links, length)", () => {
  assert.equal(publicTextCheck("The take handler now validates the vault PDA before transfer.", 200).ok, true);
  assert.equal(publicTextCheck("Contact me at someone@example.com about the vault PDA.", 200).ok, false);
  assert.equal(publicTextCheck("Deploy this to mainnet with the upgrade authority keypair.", 200).ok, false);
  assert.equal(publicTextCheck("See https://evil.example/x for the escrow details please.", 200).ok, false);
  assert.equal(publicTextCheck("x".repeat(300), 200).ok, false);
  assert.equal(publicTextCheck("Token " + ["eyJhbGciOiJIUzI1NiJ9", "eyJzdWIiOiIxIn0", "c2lnbmF0dXJlLXNpZ25hdHVyZQ"].join(".") + " leaked here", 400).ok, false);
});

test("Autonomy: proposals become issues only once, and only when they pass the checks", () => {
  const good = { title: "Assert refund closes the vault and state", detail: "The fixture checks only the returned balance after refund; does refund close both accounts and return rent to the maker?" };
  const p1 = pickProposal(resp([{ title: "short", detail: "too short" }, good]), []);
  assert.ok(p1);
  assert.equal(p1.title, good.title);
  assert.equal(pickProposal(resp([good]), [p1.hash]), null, "duplicate is skipped");
  assert.equal(pickProposal(resp([{ title: "Move funds on mainnet now", detail: "Use the mainnet deployer key to migrate the escrows quickly and quietly." }]), []), null);
});

test("Autonomy: standing approval excludes lifecycle, Circles, pausing and acceptance; workflow runs in env 'minds'", () => {
  const a = loadAutonomy();
  const ex = a.standingApproval.excludes.join(" ").toLowerCase();
  for (const w of ["lifecycle", "circle", "pause", "acceptance", "mainnet"]) assert.ok(ex.includes(w), w);
  const y = parse(readFileSync(join(REPO_ROOT, ".github/workflows/cto-autonomy.yml"), "utf8")) as { jobs: Record<string, { environment: string }> };
  assert.equal(y.jobs["autonomy"]!.environment, "minds");
  const text = readFileSync(join(REPO_ROOT, "pilot/src/autonomy/run.ts"), "utf8");
  for (const forbidden of ["awakenMind", "updateMindStatus", "addCircleMembers", "removeCircleMembers", "equipSkills", "sc-accept"]) assert.ok(!text.includes(forbidden), forbidden);
});
