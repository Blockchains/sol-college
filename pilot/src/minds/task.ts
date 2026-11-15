import { createHash } from "node:crypto";
import type { MessageRecord, WaitForReplyOutcome } from "@animocabrands/minds-client-lib";
import type { FileStore } from "../lib/store.ts";
import type { MindsPort } from "./port.ts";

export const TASK_PROTOCOL = "sc-task/1";
export const RESPONSE_PROTOCOL = "sc-task-response/1";

export type TaskState = "queued" | "dispatch-intent" | "dispatched" | "uncertain" | "response-received" | "validated" | "completed" | "operator-review";

export interface SourceRef {
  id: string;
  url: string;
  sha?: string;
}

export interface TaskSpec {
  taskId: string;
  project: string;
  kind: "research-plan" | "upstream-impact" | "pr-triage" | "adoption-draft" | "smoke-test" | "progress-report" | "experiment-patch";
  instructions: string;
  sources: SourceRef[];
  evidence: SourceRef[];
  context: Record<string, unknown>;
}

export interface TaskResponse {
  protocol: typeof RESPONSE_PROTOCOL;
  taskId: string;
  project: string;
  summary: string;
  facts: Array<{ statement: string; sourceRefs: string[] }>;
  hypotheses: Array<{ statement: string; howToTest: string }>;
  proposals: Array<{ title: string; detail: string }>;
  evidenceRefs: string[];
  uncertainties: string[];
  /** Optional requested actions. Each is re-checked deterministically by code before anything runs. */
  actions?: MindAction[];
}

/** Actions a Mind may request; executed only by protected workflows after deterministic checks. */
export type MindAction =
  | { type: "patch"; title: string; rationale: string; patch?: string; patchLines?: string[]; patchBase64?: string }
  | { type: "devnet-transfer"; recipient: string; lamports: number; reason: string };

/** The diff text of a patch action. patchLines is preferred: chat formatting can strip newlines inside strings. */
export function patchText(a: { patch?: string; patchLines?: string[]; patchBase64?: string }): string {
  if (Array.isArray(a.patchLines)) return a.patchLines.join("\n").replace(/\n*$/, "\n");
  if (typeof a.patchBase64 === "string") return Buffer.from(a.patchBase64, "base64").toString("utf8");
  return (a.patch ?? "").replace(/\r\n/g, "\n");
}

export interface TaskRecord {
  spec: TaskSpec;
  alias: string;
  state: TaskState;
  messageText: string;
  fingerprintBefore?: string;
  response?: TaskResponse;
  rawReplyFingerprint?: string;
  /** Times an operator-review task was re-evaluated against its stored/corrected replies (bounded; never resends). */
  reviewAttempts?: number;
  interimReplies?: string[];
  errors: string[];
  history: Array<{ at: string; state: TaskState; note: string }>;
}

const TASK_ID_RE = /^[a-z0-9][a-z0-9-]{5,63}$/;

export function taskAlias(prefix: string, spec: TaskSpec): string {
  const full = `${prefix}-${spec.kind}-${spec.taskId}`;
  if (full.length <= 64) return full;
  // HelloMinds aliases are limited to 64 characters: keep the prefix and a stable hash of kind+taskId.
  return `${prefix.slice(0, 40)}-${createHash("sha256").update(`${spec.kind}:${spec.taskId}`).digest("hex").slice(0, 20)}`;
}

/** Message constructed internally; callers cannot inject a free-form prompt around it. */
export function buildTaskMessage(spec: TaskSpec): string {
  if (!TASK_ID_RE.test(spec.taskId)) throw new Error(`invalid taskId ${spec.taskId}`);
  const envelope = {
    protocol: TASK_PROTOCOL,
    taskId: spec.taskId,
    project: spec.project,
    kind: spec.kind,
    instructions: spec.instructions,
    sources: spec.sources,
    evidence: spec.evidence,
    context: spec.context,
    expectedResponse: {
      protocol: RESPONSE_PROTOCOL,
      fields: ["protocol", "taskId", "project", "summary", "facts[{statement,sourceRefs[]}]", "hypotheses[{statement,howToTest}]", "proposals[{title,detail}]", "evidenceRefs[]", "uncertainties[]", "actions[] (optional): {type:'patch',title,rationale,patchLines:[<one string per line of a unified diff against the lab head given in context>]} | {type:'devnet-transfer',recipient,lamports,reason}"],
      rules: [
        "Reply with exactly one fenced ```json block containing the response object.",
        "Only cite sourceRefs and evidenceRefs by the ids listed in this task.",
        "Separate facts (with sources) from hypotheses (with a test).",
        "You cannot mark validation as passed; validation status comes only from GitHub workflow evidence.",
      ],
    },
  };
  return `SOL.COLLEGE STRUCTURED TASK ${spec.taskId}\n\`\`\`json\n${JSON.stringify(envelope, null, 2)}\n\`\`\``;
}

export interface ParsedResponse {
  ok: boolean;
  response?: TaskResponse;
  errors: string[];
}

/** Minds replies arrive as light HTML (<br>, <b>, entities). Normalise to plain text before parsing. */
export function normaliseReplyText(text: string): string {
  return text
    .replace(/<br\s*\/?>/gi, "\n")
    .replace(/<\/?(?:p|div|pre|code|b|i|strong|em|span|ul|ol|li)(?:\s[^>]*)?>/gi, "")
    .replace(/&quot;/g, '"').replace(/&#39;/g, "'").replace(/&lt;/g, "<").replace(/&gt;/g, ">").replace(/&nbsp;/g, " ").replace(/&amp;/g, "&");
}

/** A reply with no JSON block at all is an interim progress note, not a final (or invalid) answer. */
export function isInterimReply(text: string): boolean {
  const t = normaliseReplyText(text);
  return !/```/.test(t) && !/\{\s*"protocol"/.test(t);
}

function extractJson(text: string): unknown {
  const t = normaliseReplyText(text);
  const m = /```(?:json)?\s*([\s\S]*?)```/.exec(t);
  const body = m?.[1] ?? t.slice(t.indexOf("{"), t.lastIndexOf("}") + 1);
  try { return JSON.parse(body.trim()); } catch (e) {
    const repaired = repairStringReplaceCalls(body.trim());
    if (repaired === body.trim()) throw e;
    return JSON.parse(repaired);
  }
}

/**
 * Minds sometimes write a JSON string followed by a JavaScript-style `.replace(a, b)` call (to dodge chat formatting of
 * `//` or `&`). Evaluate exactly that pattern (first-occurrence replace with string literals, as in JavaScript) and
 * nothing else; the result must still parse as JSON and pass every normal check.
 */
export function repairStringReplaceCalls(body: string): string {
  const lit = String.raw`(?:"(?:[^"\\]|\\.)*"|'(?:[^'\\]|\\.)*')`;
  const re = new RegExp(String.raw`("(?:[^"\\]|\\.)*")((?:\.replace\(\s*${lit}\s*,\s*${lit}\s*\))+)`, "g");
  const one = new RegExp(String.raw`\.replace\(\s*(${lit})\s*,\s*(${lit})\s*\)`, "g");
  const unq = (l: string) => (l.startsWith("'") ? JSON.parse(`"${l.slice(1, -1).replace(/\\'/g, "'").replace(/"/g, '\\"')}"`) : JSON.parse(l)) as string;
  return body.replace(re, (_all, str: string, calls: string) => {
    let v = JSON.parse(str) as string;
    for (const c of calls.matchAll(one)) v = v.replace(unq(c[1]!), () => unq(c[2]!));
    return JSON.stringify(v);
  });
}

const FORBIDDEN_CLAIM_KEYS = ["validationStatus", "validation", "accepted", "acceptance", "certificate", "testsPassed", "conclusion"];

/** Validate a reply against the task: protocol, taskId, project, schema, permitted references. */
export function validateTaskResponse(spec: TaskSpec, reply: MessageRecord): ParsedResponse {
  const errors: string[] = [];
  const text = reply.messageText;
  if (typeof text !== "string" || text.length === 0) return { ok: false, errors: ["reply has no messageText"] };
  let obj: unknown;
  try {
    obj = extractJson(text);
  } catch {
    return { ok: false, errors: ["reply does not contain a parseable JSON block"] };
  }
  if (typeof obj !== "object" || obj === null || Array.isArray(obj)) return { ok: false, errors: ["response is not an object"] };
  const r = obj as Record<string, unknown>;
  if (r["protocol"] !== RESPONSE_PROTOCOL) errors.push(`protocol must be ${RESPONSE_PROTOCOL}`);
  if (r["taskId"] !== spec.taskId) errors.push("taskId mismatch");
  if (r["project"] !== spec.project) errors.push("project mismatch");
  if (typeof r["summary"] !== "string") errors.push("summary must be a string");
  for (const k of FORBIDDEN_CLAIM_KEYS) if (k in r) errors.push(`field ${k} is not accepted from an agent`);
  const arr = (k: string) => (Array.isArray(r[k]) ? (r[k] as unknown[]) : (errors.push(`${k} must be an array`), []));
  const allowedSources = new Set(spec.sources.map((s) => s.id));
  const allowedEvidence = new Set(spec.evidence.map((s) => s.id));
  for (const f of arr("facts")) {
    const fact = f as { statement?: unknown; sourceRefs?: unknown };
    if (typeof fact.statement !== "string" || !Array.isArray(fact.sourceRefs) || fact.sourceRefs.length === 0) errors.push("each fact needs a statement and at least one sourceRef");
    // Facts may cite any id listed in the task (sources or evidence); nothing else.
    else for (const s of fact.sourceRefs) if (!allowedSources.has(String(s)) && !allowedEvidence.has(String(s))) errors.push(`fact cites unknown source ${String(s)}`);
  }
  for (const h of arr("hypotheses")) {
    const hy = h as { statement?: unknown; howToTest?: unknown };
    if (typeof hy.statement !== "string" || typeof hy.howToTest !== "string") errors.push("each hypothesis needs statement and howToTest");
  }
  for (const p of arr("proposals")) {
    const pr = p as { title?: unknown; detail?: unknown };
    if (typeof pr.title !== "string" || typeof pr.detail !== "string") errors.push("each proposal needs title and detail");
  }
  for (const e of arr("evidenceRefs")) if (!allowedEvidence.has(String(e)) && !allowedSources.has(String(e))) errors.push(`unknown evidence ref ${String(e)}`);
  arr("uncertainties");
  if ("actions" in r) {
    if (!Array.isArray(r["actions"])) errors.push("actions must be an array");
    else for (const a of r["actions"] as unknown[]) {
      const x = a as Record<string, unknown>;
      if (x?.["type"] === "patch") { const hasBody = typeof x["patch"] === "string" || typeof x["patchBase64"] === "string" || (Array.isArray(x["patchLines"]) && (x["patchLines"] as unknown[]).every((l) => typeof l === "string"));
        if (typeof x["title"] !== "string" || typeof x["rationale"] !== "string" || !hasBody) errors.push("patch action needs title, rationale and patchLines (or patch / patchBase64)"); }
      else if (x?.["type"] === "devnet-transfer") { if (typeof x["recipient"] !== "string" || !Number.isInteger(x["lamports"]) || typeof x["reason"] !== "string") errors.push("devnet-transfer action needs recipient, integer lamports and reason"); }
      else errors.push(`unknown action type ${String(x?.["type"])}`);
    }
  }
  if (errors.length) return { ok: false, errors };
  return { ok: true, response: r as unknown as TaskResponse, errors: [] };
}

const key = (spec: TaskSpec) => `tasks/${spec.project}/${spec.taskId}`;
const now = () => new Date().toISOString();

function transition(r: TaskRecord, state: TaskState, note: string): TaskRecord {
  return { ...r, state, history: [...r.history, { at: now(), state, note }] };
}

export interface DispatchDeps {
  minds: Pick<MindsPort, "ensureConversation" | "getLatestHistoryFingerprint" | "sendMessage" | "waitForReply" | "getHistory">;
  store: FileStore;
  mindId: string;
  aliasPrefix: string;
  timeoutMs: number;
}

/**
 * Dispatch a structured task exactly once from this store's point of view. Duplicate requests
 * return the existing record. Ambiguous sends and timeouts become `uncertain` and are never
 * resent automatically; use reconcileTask() then operator review.
 */
export async function dispatchTask(deps: DispatchDeps, spec: TaskSpec): Promise<TaskRecord> {
  const k = key(spec);
  return deps.store.withLockAsync(k, async () => {
    const existing = deps.store.read<TaskRecord>(k);
    if (existing) {
      if (existing.data.state === "queued") {
        // safe to continue: nothing was sent
      } else {
        return existing.data; // duplicate request: never re-send
      }
    }
    const alias = taskAlias(deps.aliasPrefix, spec);
    const messageText = buildTaskMessage(spec);
    let rec: TaskRecord = existing?.data ?? { spec, alias, state: "queued", messageText, errors: [], history: [{ at: now(), state: "queued", note: "task recorded" }] };
    let v = existing?.version ?? deps.store.write(k, rec, 0).version;

    await deps.minds.ensureConversation(alias, deps.mindId);
    const before = await deps.minds.getLatestHistoryFingerprint(alias);
    rec = transition(before === undefined ? rec : { ...rec, fingerprintBefore: before }, "dispatch-intent", "intent and pre-send fingerprint recorded");
    v = deps.store.write(k, rec, v).version;
    try {
      await deps.minds.sendMessage({ alias, messageText });
    } catch (e) {
      rec = transition({ ...rec, errors: [...rec.errors, `send: ${(e as Error).message}`] }, "uncertain", "send outcome unknown; not resending");
      deps.store.write(k, rec, v);
      return rec;
    }
    rec = transition(rec, "dispatched", "sendMessage returned");
    v = deps.store.write(k, rec, v).version;

    let outcome: WaitForReplyOutcome;
    try {
      outcome = await deps.minds.waitForReply({ alias, timeoutMs: deps.timeoutMs, sentMessageText: messageText, ...(rec.fingerprintBefore ? { afterFingerprint: rec.fingerprintBefore } : {}) });
    } catch (e) {
      rec = transition({ ...rec, errors: [...rec.errors, `wait: ${(e as Error).message}`] }, "uncertain", "waiting failed; reply may still arrive");
      deps.store.write(k, rec, v);
      return rec;
    }
    if (outcome.timedOut) {
      rec = transition(rec, "uncertain", "timed out; the Mind may still act or reply. Reconcile history before any resend.");
      deps.store.write(k, rec, v);
      return rec;
    }
    return acceptReply(deps.store, k, rec, v, outcome.reply);
  });
}

function acceptReply(store: FileStore, k: string, rec0: TaskRecord, v0: number, reply: MessageRecord): TaskRecord {
  if (typeof reply.messageText === "string" && isInterimReply(reply.messageText)) {
    const rec = transition({ ...rec0, interimReplies: [...(rec0.interimReplies ?? []), reply.fingerprint] }, "uncertain", "interim progress reply (no JSON block); waiting for the final reply. Reconcile later; never resend.");
    store.write(k, rec, v0);
    return rec;
  }
  let rec = transition({ ...rec0, rawReplyFingerprint: reply.fingerprint }, "response-received", "reply received");
  let v = store.write(k, rec, v0).version;
  const parsed = validateTaskResponse(rec.spec, reply);
  if (!parsed.ok || !parsed.response) {
    rec = transition({ ...rec, errors: [...rec.errors, ...parsed.errors] }, "operator-review", "reply failed validation");
    store.write(k, rec, v);
    return rec;
  }
  rec = transition({ ...rec, response: parsed.response }, "validated", "response validated against task");
  v = store.write(k, rec, v).version;
  rec = transition(rec, "completed", "private result preserved");
  store.write(k, rec, v);
  return rec;
}

/**
 * Reconcile an uncertain/dispatched task from conversation history (newest-first). Finds our
 * sent message by its exact text and a later Mind reply carrying the taskId. Never resends.
 */
export async function reconcileTask(deps: Pick<DispatchDeps, "minds" | "store">, spec: TaskSpec): Promise<TaskRecord> {
  const k = key(spec);
  const cur = deps.store.read<TaskRecord>(k);
  if (!cur) throw new Error(`no task record ${spec.taskId}`);
  const rec = cur.data;
  if (rec.state === "operator-review") return reviewTask(deps, spec, cur.version, rec);
  if (!["uncertain", "dispatched", "dispatch-intent"].includes(rec.state)) return rec;
  const rows = await deps.minds.getHistory(rec.alias, { limit: 50 });
  const sentIdx = rows.findIndex((r) => r.senderType === 1 && r.messageText === rec.messageText);
  if (sentIdx < 0) {
    const next = transition(rec, "operator-review", "sent message not found in recent history; operator must decide whether to resend");
    deps.store.write(k, next, cur.version);
    return next;
  }
  // newest-first: replies to our message have smaller indexes than sentIdx
  // Prefer the earliest correlated reply that carries a JSON block; interim progress notes keep the task open.
  const replies = rows.slice(0, sentIdx).reverse().filter((r) => r.senderType !== 1 && typeof r.messageText === "string");
  // A Mind sometimes sends a corrected reply for the same taskId ("formatting correction"): the newest correlated
  // reply that validates wins; otherwise fall back to the earliest correlated one (which may go to operator review).
  const reply = [...replies].reverse().find((r) => !isInterimReply(r.messageText as string) && normaliseReplyText(r.messageText as string).includes(spec.taskId) && validateTaskResponse(spec, r).ok)
    ?? replies.find((r) => !isInterimReply(r.messageText as string) && normaliseReplyText(r.messageText as string).includes(spec.taskId))
    ?? replies.find((r) => normaliseReplyText(r.messageText as string).includes(spec.taskId));
  if (!reply) {
    const next = transition(rec, "uncertain", "message delivered; no correlated reply yet");
    deps.store.write(k, next, cur.version);
    return next;
  }
  return acceptReply(deps.store, k, rec, cur.version, reply);
}

export const MAX_REVIEW_ATTEMPTS = 3;

/**
 * Re-evaluate an operator-review task whose reply failed validation: the Mind sometimes sends a
 * corrected reply for the same taskId, and the response policy may have been widened since. Looks
 * only at correlated replies already in history (newest-first), accepts the newest one that now
 * validates, and never resends. Bounded by MAX_REVIEW_ATTEMPTS; tasks parked because the sent
 * message was not found are left for the operator.
 */
async function reviewTask(deps: Pick<DispatchDeps, "minds" | "store">, spec: TaskSpec, version: number, rec: TaskRecord): Promise<TaskRecord> {
  const k = key(spec);
  const attempts = rec.reviewAttempts ?? 0;
  if (attempts >= MAX_REVIEW_ATTEMPTS || rec.history.some((h) => h.note.startsWith("sent message not found"))) return rec;
  const rows = await deps.minds.getHistory(rec.alias, { limit: 50 });
  const sentIdx = rows.findIndex((r) => r.senderType === 1 && r.messageText === rec.messageText);
  const counted = { ...rec, reviewAttempts: attempts + 1 };
  if (sentIdx < 0) { deps.store.write(k, counted, version); return counted; }
  const replies = rows.slice(0, sentIdx).filter((r) => r.senderType !== 1 && typeof r.messageText === "string" && !isInterimReply(r.messageText as string) && normaliseReplyText(r.messageText as string).includes(spec.taskId));
  for (const reply of replies) {
    if (!validateTaskResponse(spec, reply).ok) continue;
    const reopened = transition({ ...counted, errors: [] }, "uncertain", `re-evaluated a correlated reply already in history (attempt ${attempts + 1}); nothing was resent`);
    return acceptReply(deps.store, k, reopened, version, reply);
  }
  deps.store.write(k, counted, version);
  return counted;
}
