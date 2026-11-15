import type { MindsPort } from "./port.ts";
import { capabilities, inventory, installedSdkVersion, mindDetail, telemetry } from "./ops.ts";
import { buildTaskMessage, validateTaskResponse, type TaskSpec } from "./task.ts";
import { shortRef } from "../lib/secrets.ts";

export interface SmokeOptions {
  /** Explicit target: the protected test-Mind id (never "first Mind"). */
  testMindId: string;
  /** Expected name, checked against getMind as a consistency guard (not used for selection). */
  expectedName: string;
  /** Message step only when the target is designated as a test Mind and the operator opted in. */
  allowMessage: boolean;
  designatedTestMind: boolean;
  timeoutMs: number;
  runId: string;
}

export interface SmokeStep {
  step: string;
  status: "PASS" | "FAIL" | "NOT EXECUTED";
  detail: string;
}

export async function runSmokeTest(minds: MindsPort, o: SmokeOptions): Promise<{ sdkVersion: string; target: string; steps: SmokeStep[] }> {
  const steps: SmokeStep[] = [];
  const add = (step: string, status: SmokeStep["status"], detail: string) => steps.push({ step, status, detail });
  const sdkVersion = installedSdkVersion();
  const inv = await inventory(minds);
  add("inventory", "PASS", `${inv.mindCount} Mind(s) on account, ${inv.conversationAliases.length} conversation(s)`);
  const listed = (await minds.listMinds()).some((m) => m.mindId === o.testMindId);
  add("mapping verification", listed ? "PASS" : "FAIL", listed ? `target ${shortRef(o.testMindId)} belongs to this Builder account` : "target is not on this account");
  if (!listed) return { sdkVersion, target: shortRef(o.testMindId), steps };
  const det = await mindDetail(minds, o.testMindId);
  const nameOk = det.name === o.expectedName;
  add("detail read", nameOk ? "PASS" : "FAIL", `name=${det.name} archetype=${det.archetype} enabled=${det.isEnabled}${nameOk ? "" : ` (expected ${o.expectedName})`}`);
  if (!nameOk) return { sdkVersion, target: shortRef(o.testMindId), steps };
  const tel = await telemetry(minds, o.testMindId);
  add("cognition read", "PASS", `balance=${tel.cognitionBalance.toFixed(2)} dailyBuckets=${tel.usageDaily.length} tools=${tel.byTool.map((t) => t.tool).join("|") || "none"}`);
  const cap = await capabilities(minds, o.testMindId);
  add("equipped capabilities read", "PASS", `skills=${cap.skills.length} apps=${cap.apps.map((a) => a.appName).join("|") || "none"} circleMembers=${cap.circle.memberCount}`);
  if (!o.designatedTestMind || !o.allowMessage) {
    const why = !o.designatedTestMind ? "target is not designated as a test Mind in protected mapping" : "message step not opted in";
    add("dedicated test alias", "NOT EXECUTED", why);
    add("harmless task-correlated message", "NOT EXECUTED", why);
    add("timeout/reply handling (live)", "NOT EXECUTED", why);
    return { sdkVersion, target: shortRef(o.testMindId), steps };
  }
  const spec: TaskSpec = {
    taskId: `smoke-${o.runId}`.toLowerCase().replace(/[^a-z0-9-]/g, "-"),
    project: "sol-college-smoke",
    kind: "smoke-test",
    instructions: "Harmless connectivity check. Reply with the response object only; summary should be the word 'pong'. Use empty arrays for facts, hypotheses, proposals, evidenceRefs and uncertainties.",
    sources: [],
    evidence: [],
    context: {},
  };
  const alias = `sc-smoke-${spec.taskId}`.slice(0, 120);
  await minds.ensureConversation(alias, o.testMindId);
  add("dedicated test alias", "PASS", `alias ${alias}`);
  const text = buildTaskMessage(spec);
  const before = await minds.getLatestHistoryFingerprint(alias);
  await minds.sendMessage({ alias, messageText: text });
  add("harmless task-correlated message", "PASS", `sent taskId ${spec.taskId}`);
  const outcome = await minds.waitForReply({ alias, timeoutMs: o.timeoutMs, sentMessageText: text, ...(before ? { afterFingerprint: before } : {}) });
  if (outcome.timedOut) {
    add("timeout/reply handling (live)", "PASS", `timed out after ${o.timeoutMs}ms; recorded as uncertain (no resend)`);
  } else {
    const v = validateTaskResponse(spec, outcome.reply);
    add("timeout/reply handling (live)", "PASS", `reply received (outcome.reply.messageText, ${String(outcome.reply.messageText ?? "").length} chars); structured validation ${v.ok ? "ok" : "failed: " + v.errors.slice(0, 3).join("; ")}`);
  }
  return { sdkVersion, target: shortRef(o.testMindId), steps };
}
