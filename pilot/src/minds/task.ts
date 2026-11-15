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
  kind: "research-plan" | "upstream-impact" | "pr-triage" | "adoption-draft" | "smoke-test" | "progress-report";
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
}

export interface TaskRecord {
  spec: TaskSpec;
  alias: string;
  state: TaskState;
  messageText: string;
  fingerprintBefore?: string;
  response?: TaskResponse;
  rawReplyFingerprint?: string;
  errors: string[];
  history: Array<{ at: string; state: TaskState; note: string }>;
}

const TASK_ID_RE = /^[a-z0-9][a-z0-9-]{5,63}$/;

export function taskAlias(prefix: string, spec: TaskSpec): string {
  return `${prefix}-${spec.kind}-${spec.taskId}`.slice(0, 120);
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
      fields: ["protocol", "taskId", "project", "summary", "facts[{statement,sourceRefs[]}]", "hypotheses[{statement,howToTest}]", "proposals[{title,detail}]", "evidenceRefs[]", "uncertainties[]"],
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

function extractJson(text: string): unknown {
  const m = /```json\s*([\s\S]*?)```/.exec(text);
  const body = m?.[1] ?? text;
  return JSON.parse(body.trim());
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
    else for (const s of fact.sourceRefs) if (!allowedSources.has(String(s))) errors.push(`fact cites unknown source ${String(s)}`);
  }
  for (const h of arr("hypotheses")) {
    const hy = h as { statement?: unknown; howToTest?: unknown };
    if (typeof hy.statement !== "string" || typeof hy.howToTest !== "string") errors.push("each hypothesis needs statement and howToTest");
  }
  for (const p of arr("proposals")) {
    const pr = p as { title?: unknown; detail?: unknown };
    if (typeof pr.title !== "string" || typeof pr.detail !== "string") errors.push("each proposal needs title and detail");
  }
  for (const e of arr("evidenceRefs")) if (!allowedEvidence.has(String(e))) errors.push(`unknown evidence ref ${String(e)}`);
  arr("uncertainties");
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
  if (!["uncertain", "dispatched", "dispatch-intent"].includes(rec.state)) return rec;
  const rows = await deps.minds.getHistory(rec.alias, { limit: 50 });
  const sentIdx = rows.findIndex((r) => r.senderType === 1 && r.messageText === rec.messageText);
  if (sentIdx < 0) {
    const next = transition(rec, "operator-review", "sent message not found in recent history; operator must decide whether to resend");
    deps.store.write(k, next, cur.version);
    return next;
  }
  // newest-first: replies to our message have smaller indexes than sentIdx
  const reply = rows.slice(0, sentIdx).reverse().find((r) => r.senderType !== 1 && typeof r.messageText === "string" && r.messageText.includes(spec.taskId));
  if (!reply) {
    const next = transition(rec, "uncertain", "message delivered; no correlated reply yet");
    deps.store.write(k, next, cur.version);
    return next;
  }
  return acceptReply(deps.store, k, rec, cur.version, reply);
}
