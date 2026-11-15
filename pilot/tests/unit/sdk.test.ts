// [mock] SDK-shape tests: fakes are typed against the installed @animocabrands/minds-client-lib interfaces.
import { test } from "node:test";
import assert from "node:assert/strict";
import { FakeMinds, validReplyFor } from "../fixtures/fake-minds.ts";
import { store, cfg } from "../fixtures/helpers.ts";
import { dispatchTask, validateTaskResponse, buildTaskMessage, type TaskSpec } from "../../src/minds/task.ts";
import { resolveProjectMind, parseMindMapping, AuthorityError } from "../../src/minds/authority.ts";
import { assessEquipment, equipApproved } from "../../src/minds/equip.ts";
import { planCircleChange, applyCirclePlan } from "../../src/minds/circle.ts";

const spec = (taskId = "task-000001"): TaskSpec => ({ taskId, project: "gifter-escrow", kind: "research-plan", instructions: "plan", sources: [{ id: "s1", url: "https://github.com/Blockchains/gifter-escrow" }], evidence: [], context: {} });
const deps = (m: FakeMinds) => ({ minds: m, store: store(), mindId: m.minds[0]!.mindId, aliasPrefix: "sc-gifter-escrow", timeoutMs: 50 });

test("SDK: reply text is read from outcome.reply.messageText (not a plain string, no .text/.content guessing)", async () => {
  const m = new FakeMinds();
  m.replyBehaviour = { kind: "reply", text: () => validReplyFor("task-000001", "gifter-escrow") };
  const r = await dispatchTask(deps(m), spec());
  assert.equal(r.state, "completed");
  assert.equal(r.response?.summary, "ok");
  const bad = validateTaskResponse(spec(), { fingerprint: "x", text: "{}" } as never);
  assert.equal(bad.ok, false);
  assert.match(bad.errors[0]!, /no messageText/);
});

test("SDK: waitForReply timeout returns {timedOut:true} and becomes uncertainty, not an exception or resend", async () => {
  const m = new FakeMinds();
  m.replyBehaviour = { kind: "timeout" };
  const d = deps(m);
  const r = await dispatchTask(d, spec());
  assert.equal(r.state, "uncertain");
  assert.equal(m.sendCalls.length, 1);
  const again = await dispatchTask(d, spec());
  assert.equal(again.state, "uncertain");
  assert.equal(m.sendCalls.length, 1, "no automatic resend after timeout");
});

test("SDK: task message carries protocol, taskId, project and expected response schema", () => {
  const t = buildTaskMessage(spec());
  for (const s of ["sc-task/1", "task-000001", "gifter-escrow", "sc-task-response/1"]) assert.ok(t.includes(s), s);
  assert.throws(() => buildTaskMessage(spec("BAD ID")));
});

test("SDK: reply with wrong taskId, project, unknown sources or validation claims is rejected", () => {
  const s = spec();
  const v = (txt: string) => validateTaskResponse(s, { fingerprint: "f", messageText: txt, senderType: 0 });
  assert.equal(v(validReplyFor("task-000002", "gifter-escrow")).ok, false);
  assert.equal(v(validReplyFor("task-000001", "other")).ok, false);
  assert.equal(v(validReplyFor("task-000001", "gifter-escrow", { facts: [{ statement: "x", sourceRefs: ["nope"] }] })).ok, false);
  const claim = v(validReplyFor("task-000001", "gifter-escrow", { validationStatus: "passed" }));
  assert.equal(claim.ok, false, "agent claim cannot manufacture passed validation");
  assert.ok(claim.errors.some((e) => e.includes("validationStatus")));
});

test("SDK: project mapping is enforced (approved status, protected entry, projectId, configVersion, account ownership)", async () => {
  const c = cfg();
  const m = new FakeMinds();
  const mindId = m.minds[0]!.mindId;
  const p = c.projects.find((x) => x.slug === "gifter-escrow")!;
  // public config says "proposed" -> denied even if a protected entry exists
  p.mind.mappingStatus = "proposed";
  const mapping = parseMindMapping(JSON.stringify({ [p.mind.mappingRef]: { projectId: p.projectId, mindId, configVersion: 1, approvedBy: "Blockchains", approvedAt: "2026-11-15T00:00:00Z", role: "project-cto" } }));
  await assert.rejects(resolveProjectMind({ cfg: c, mapping, slug: "gifter-escrow", operation: "telemetry", minds: m }), AuthorityError);
  p.mind.mappingStatus = "approved";
  const ok = await resolveProjectMind({ cfg: c, mapping, slug: "gifter-escrow", operation: "telemetry", minds: m });
  assert.equal(ok.mindId, mindId);
  await assert.rejects(resolveProjectMind({ cfg: c, mapping: { [p.mind.mappingRef]: { ...mapping[p.mind.mappingRef]!, projectId: "someone-else" } }, slug: "gifter-escrow", operation: "telemetry", minds: m }), /belongs to/);
  await assert.rejects(resolveProjectMind({ cfg: c, mapping: { [p.mind.mappingRef]: { ...mapping[p.mind.mappingRef]!, configVersion: 0 } }, slug: "gifter-escrow", operation: "telemetry", minds: m }), /not current/);
  await assert.rejects(resolveProjectMind({ cfg: c, mapping: { [p.mind.mappingRef]: { ...mapping[p.mind.mappingRef]!, mindId: "not-on-account" } }, slug: "gifter-escrow", operation: "telemetry", minds: m }), /not on this Builder account/);
  await assert.rejects(resolveProjectMind({ cfg: c, mapping, slug: "unknown-project", operation: "telemetry", minds: m }), /unknown/);
});

test("SDK: unsupported operation is rejected and mutations need a matching approval (not an agent)", async () => {
  const c = cfg();
  const m = new FakeMinds();
  const p = c.projects.find((x) => x.slug === "gifter-escrow")!;
  p.mind.mappingStatus = "approved";
  const mapping = { [p.mind.mappingRef]: { projectId: p.projectId, mindId: m.minds[0]!.mindId, configVersion: 1, approvedBy: "Blockchains", approvedAt: "x", role: "project-cto" as const } };
  await assert.rejects(resolveProjectMind({ cfg: c, mapping, slug: "gifter-escrow", operation: "delete-account", minds: m }), /not permitted/);
  await assert.rejects(resolveProjectMind({ cfg: c, mapping, slug: "gifter-escrow", operation: "pause", minds: m }), /requires approval/);
  await assert.rejects(resolveProjectMind({ cfg: c, mapping, slug: "gifter-escrow", operation: "pause", approval: { approvedBy: "Blockchains", ref: "r1", action: "resume", projectSlug: "gifter-escrow" }, minds: m }), /does not cover/);
  await assert.rejects(resolveProjectMind({ cfg: c, mapping, slug: "gifter-escrow", operation: "pause", approval: { approvedBy: "github-actions[bot]", ref: "r1", action: "pause", projectSlug: "gifter-escrow" }, minds: m }), /agent identity/);
  const ok = await resolveProjectMind({ cfg: c, mapping, slug: "gifter-escrow", operation: "pause", approval: { approvedBy: "Blockchains", ref: "r1", action: "pause", projectSlug: "gifter-escrow" }, minds: m });
  assert.ok(ok.mindId);
});

test("SDK: Skill/App equipment completeness is checked against mutation results and final state", async () => {
  const m = new FakeMinds();
  m.equipDrop = ["skill-b"];
  const r = await equipApproved(m, m.minds[0]!.mindId, "skills", ["skill-a", "skill-b"]);
  assert.equal(r.complete, false);
  assert.deepEqual(r.missingFromFinalState, ["skill-b"]);
  assert.deepEqual(r.mutationMissing, ["skill-b"]);
  const full = assessEquipment("apps", ["A1"], { results: [{ appId: "a1", isEquipped: true }] }, ["A1"]);
  assert.equal(full.complete, true, "ids compare case-insensitively (API returns upper-case UUIDs)");
});

test("SDK: Circle changes require approval and only approved explicit members", async () => {
  const m = new FakeMinds();
  const plan = planCircleChange(await m.getCircle(), ["dev@example.org", "*@example.org", "stranger@x.io"], ["steward@example.org"], { approvedMembers: ["dev@example.org"] });
  assert.deepEqual(plan.add, ["dev@example.org"]);
  assert.equal(plan.rejected.length, 3);
  await assert.rejects(applyCirclePlan(m, "id", { add: ["dev@example.org"], remove: [], rejected: [] }, undefined), /approval/);
  const audit = await applyCirclePlan(m, "id", { add: ["dev@example.org"], remove: [], rejected: [] }, { approvedBy: "Blockchains", ref: "r", action: "circle-add", projectSlug: "gifter-escrow" });
  assert.deepEqual(audit, [{ email: "dev@example.org", action: "added", confirmedInFinalState: true }]);
});

test("SDK: HTML-formatted replies (<br>, &quot;) are normalised; progress notes without JSON are interim, not invalid", async () => {
  const { validateTaskResponse, isInterimReply } = await import("../../src/minds/task.ts");
  const s = spec("html-reply-task");
  const obj = { protocol: "sc-task-response/1", taskId: s.taskId, project: s.project, summary: "ok", facts: [], hypotheses: [], proposals: [], evidenceRefs: [], uncertainties: [] };
  const html = "Result for <b>" + s.taskId + "</b>:<br>```json<br>" + JSON.stringify(obj, null, 1).replace(/\n/g, "<br>").replace(/"/g, "&quot;") + "<br>```";
  assert.equal(validateTaskResponse(s, { fingerprint: "f", senderType: 0, messageText: html }).ok, true);
  assert.equal(isInterimReply("Task <b>" + s.taskId + "</b> received. I'm pulling the commits now."), true);
  assert.equal(isInterimReply(html), false);
});
