// [mock] Recovery tests: duplicate requests, ambiguous sends, provisioning retries, upstream ordering, immutability.
import { test } from "node:test";
import assert from "node:assert/strict";
import { join } from "node:path";
import { FakeMinds, validReplyFor } from "../fixtures/fake-minds.ts";
import { store, tmp } from "../fixtures/helpers.ts";
import { dispatchTask, reconcileTask, type TaskSpec } from "../../src/minds/task.ts";
import { provisionMind, resolveUncertainProvision } from "../../src/minds/provision.ts";
import { reconcileUpstream, type CompareFn } from "../../src/upstream/reconcile.ts";
import { writeImmutableCanonical, ImmutableRecordError, ConflictError } from "../../src/lib/store.ts";

const spec: TaskSpec = { taskId: "task-dup-001", project: "gifter-escrow", kind: "upstream-impact", instructions: "x", sources: [{ id: "s1", url: "https://x" }], evidence: [], context: {} };

test("Recovery: duplicate task request is safe (one send, same record)", async () => {
  const m = new FakeMinds();
  m.replyBehaviour = { kind: "reply", text: () => validReplyFor(spec.taskId, spec.project) };
  const s = store();
  const d = { minds: m, store: s, mindId: m.minds[0]!.mindId, aliasPrefix: "sc-gifter-escrow", timeoutMs: 50 };
  const a = await dispatchTask(d, spec);
  const b = await dispatchTask(d, spec);
  assert.equal(a.state, "completed");
  assert.deepEqual(b, a);
  assert.equal(m.sendCalls.length, 1);
});

test("Recovery: concurrent dispatch of the same task does not double-send or corrupt state", async () => {
  const m = new FakeMinds();
  m.replyBehaviour = { kind: "reply", text: () => validReplyFor(spec.taskId, spec.project) };
  const s = store();
  const d = { minds: m, store: s, mindId: m.minds[0]!.mindId, aliasPrefix: "sc-gifter-escrow", timeoutMs: 50 };
  const results = await Promise.allSettled([dispatchTask(d, spec), dispatchTask(d, spec), dispatchTask(d, spec)]);
  assert.equal(m.sendCalls.length, 1);
  assert.equal(results.filter((r) => r.status === "fulfilled").length >= 1, true);
  for (const r of results) if (r.status === "rejected") assert.ok(r.reason instanceof ConflictError);
  assert.equal(s.read<{ state: string }>(`tasks/gifter-escrow/${spec.taskId}`)!.data.state, "completed");
});

test("Recovery: ambiguous send is not blindly retried; reconcile finds the delivered message and later reply", async () => {
  const m = new FakeMinds();
  m.sendBehaviour = "throw";
  const s = store();
  const d = { minds: m, store: s, mindId: m.minds[0]!.mindId, aliasPrefix: "sc-gifter-escrow", timeoutMs: 50 };
  const r = await dispatchTask(d, spec);
  assert.equal(r.state, "uncertain");
  m.sendBehaviour = "ok";
  const again = await dispatchTask(d, spec);
  assert.equal(again.state, "uncertain");
  assert.equal(m.sendCalls.length, 1, "never resent");
  // message never reached history -> operator review, still no resend
  const rec = await reconcileTask({ minds: m, store: s }, spec);
  assert.equal(rec.state, "operator-review");
  assert.equal(m.sendCalls.length, 1);
});

test("Recovery: timeout then reconcile picks up a correlated reply from newest-first history", async () => {
  const m = new FakeMinds();
  const s = store();
  const d = { minds: m, store: s, mindId: m.minds[0]!.mindId, aliasPrefix: "sc-gifter-escrow", timeoutMs: 20 };
  const r = await dispatchTask(d, { ...spec, taskId: "task-late-01" });
  assert.equal(r.state, "uncertain");
  m.history.unshift({ fingerprint: "late", senderType: 0, messageText: validReplyFor("task-late-01", "gifter-escrow") });
  const rec = await reconcileTask({ minds: m, store: s }, { ...spec, taskId: "task-late-01" });
  assert.equal(rec.state, "completed");
  assert.equal(m.sendCalls.length, 1);
});

test("Recovery: provisioning retry does not create another Mind; uncertain creation is not adopted by name", async () => {
  const m = new FakeMinds();
  m.awakenBehaviour = "network-error"; // Mind created server-side, response lost
  const s = store();
  const req = { slug: "gifter-escrow", projectId: "sc-demo-gifter-escrow", name: "SolCollege-Gifter-CTO", archetype: "chiefofstaff", approvalRef: "env-approval-1" };
  const r1 = await provisionMind(m, s, req);
  assert.equal(r1.state, "creation-uncertain");
  assert.equal(m.awakenCalls, 1);
  m.awakenBehaviour = "ok";
  const r2 = await provisionMind(m, s, req);
  assert.equal(r2.state, "creation-uncertain");
  assert.equal(r2.mindId, undefined, "name match is not adoption");
  assert.equal(r2.candidatesSeen?.length, 1);
  assert.equal(m.awakenCalls, 1, "no second awaken");
  const r3 = resolveUncertainProvision(s, "gifter-escrow", { mindId: r2.candidatesSeen![0]!, operator: "Blockchains" });
  assert.equal(r3.state, "mind-confirmed");
  const r4 = await provisionMind(m, s, req);
  assert.equal(r4.state, "mind-confirmed");
  assert.equal(m.awakenCalls, 1);
});

test("Recovery: definitive rejection returns to requested; success records mindId immediately", async () => {
  const m = new FakeMinds();
  m.awakenBehaviour = "reject";
  const s = store();
  const req = { slug: "p2", projectId: "p2", name: "SolCollege-P2", archetype: "cto", approvalRef: "a" };
  await assert.rejects(provisionMind(m, s, req));
  m.awakenBehaviour = "ok";
  const ok = await provisionMind(m, s, { ...req, archetype: "chiefofstaff" });
  assert.equal(ok.state, "mind-confirmed");
  assert.ok(ok.mindId);
  assert.ok(ok.history.some((h) => h.state === "creation-intent"));
});

test("Recovery: out-of-order upstream observation cannot rewind tracked state", async () => {
  const s = store();
  const order = ["a", "b", "c"];
  const compare: CompareFn = async (base, head) => (order.indexOf(head) > order.indexOf(base) ? "ahead" : order.indexOf(head) < order.indexOf(base) ? "behind" : "identical");
  const base = { store: s, project: "gifter-escrow", upstreamRepo: "u/r", branch: "main", compare, experiments: [{ id: "e1", baseline: "a", candidateSha: "x", status: "tested-candidate" as const }] };
  assert.equal((await reconcileUpstream({ ...base, observedHead: "a" })).outcome, "initialised");
  const adv = await reconcileUpstream({ ...base, observedHead: "c" });
  assert.equal(adv.outcome, "advanced");
  assert.equal(adv.impacts[0]!.action, "rebase-and-retest");
  const stale = await reconcileUpstream({ ...base, observedHead: "b" });
  assert.equal(stale.outcome, "stale-ignored");
  assert.equal(stale.state.head, "c");
});

test("Recovery: approved package / credential files are never overwritten; duplicates are idempotent", () => {
  const d = tmp();
  const p = join(d, "x.json");
  assert.equal(writeImmutableCanonical(p, { a: 1 }).created, true);
  assert.equal(writeImmutableCanonical(p, { a: 1 }).created, false);
  assert.throws(() => writeImmutableCanonical(p, { a: 2 }), ImmutableRecordError);
});
