import { test } from "node:test";
import assert from "node:assert/strict";
import { looksLikeDefect, retryablePatch, loadAutonomy, type AutonomyState } from "../../src/autonomy/run.ts";

test("Focus (t695u): the four Minds out of credits are skipped by the loop, the three running ones are not", () => {
  const a = loadAutonomy();
  for (const s of ["ciphervault", "colosseum", "poe-solana", "trustlock"]) assert.equal(a.paused?.[s]?.status, "paused (no credits)");
  for (const s of ["gifter-escrow", "sentient-send", "orboracle-solana"]) assert.equal(a.paused?.[s], undefined);
});

test("Defect questions ask for a program-source fix; failed attempts are retried up to 3 times", () => {
  assert.ok(looksLikeDefect("market questions over 32 bytes fail (question used as a PDA seed)"));
  assert.ok(!looksLikeDefect("How does the time-decayed average behave under skewed submissions?"));
  const st = { project: "x", tasks: { t1: { kind: "experiment-patch", createdAt: "", handled: "operator-review" } }, patchRequests: { u: "t1" }, patchAttempts: { u: 1 } } as unknown as AutonomyState;
  assert.ok(retryablePatch(st, "u"));
  (st.patchAttempts as Record<string, number>)["u"] = 3;
  assert.ok(!retryablePatch(st, "u"));
});

test("Replies with JS-style .replace() after a JSON string are evaluated literally and nothing else", async () => {
  const { repairStringReplaceCalls } = await import("../../src/minds/task.ts");
  assert.equal(repairStringReplaceCalls(`["a\\/\\/b".replace("\\/\\/","//"),"+ \\u0020x".replace(' ',''),"ok"]`), `["a//b","+ x","ok"]`);
  assert.equal(repairStringReplaceCalls(`{"a":"b"}`), `{"a":"b"}`);
});
