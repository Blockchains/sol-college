/**
 * Versioned CTO instructions, delivered through the only supported surface the SDK exposes for this:
 * a message in a dedicated configuration conversation (`<prefix>-instructions-<sha12>`). Sent at most once
 * per instructions hash from this store's point of view; ambiguous sends become `uncertain` and are never
 * resent automatically. The Mind's acknowledgement is recorded, but acknowledgement is not proof that the
 * Mind will always follow the instructions: every structured reply is still validated by code.
 */
import { sha256Hex } from "../lib/canonical.ts";
import type { FileStore } from "../lib/store.ts";
import type { MindsPort } from "./port.ts";

export interface ConfigureRecord {
  alias: string;
  sha256: string;
  state: "intent" | "sent" | "acknowledged" | "uncertain";
  replyChars: number;
  replyFingerprint?: string;
  history: Array<{ at: string; state: string; note: string }>;
}

export async function configureInstructions(
  minds: Pick<MindsPort, "ensureConversation" | "getLatestHistoryFingerprint" | "sendMessage" | "waitForReply">,
  store: FileStore,
  o: { mindId: string; prefix: string; text: string; timeoutMs: number },
): Promise<ConfigureRecord> {
  const sha256 = sha256Hex(Buffer.from(o.text, "utf8"));
  const alias = `${o.prefix}-instructions-${sha256.slice(0, 12)}`;
  const key = `configure/${alias}`;
  return store.withLockAsync(key, async () => {
    const existing = store.read<ConfigureRecord>(key);
    if (existing) return existing.data; // never resend the same instructions
    const at = () => new Date().toISOString();
    let rec: ConfigureRecord = { alias, sha256, state: "intent", replyChars: 0, history: [{ at: at(), state: "intent", note: "instructions recorded" }] };
    let v = store.write(key, rec, 0).version;
    await minds.ensureConversation(alias, o.mindId);
    const before = await minds.getLatestHistoryFingerprint(alias);
    const messageText = `SOL.COLLEGE OPERATING INSTRUCTIONS (sha256 ${sha256})\nThese instructions apply to all Sol.College conversations with you. Reply with a short acknowledgement that restates the scope, the evidence rules and the response format in your own words. Do not take any other action.\n\n${o.text}`;
    try {
      await minds.sendMessage({ alias, messageText });
    } catch (e) {
      rec = { ...rec, state: "uncertain", history: [...rec.history, { at: at(), state: "uncertain", note: `send outcome unknown: ${(e as Error).message}` }] };
      store.write(key, rec, v);
      return rec;
    }
    rec = { ...rec, state: "sent", history: [...rec.history, { at: at(), state: "sent", note: "sendMessage returned" }] };
    v = store.write(key, rec, v).version;
    const outcome = await minds.waitForReply({ alias, timeoutMs: o.timeoutMs, sentMessageText: messageText, ...(before ? { afterFingerprint: before } : {}) });
    if (outcome.timedOut) {
      rec = { ...rec, state: "uncertain", history: [...rec.history, { at: at(), state: "uncertain", note: "no acknowledgement before timeout" }] };
    } else {
      const text = outcome.reply.messageText ?? "";
      rec = { ...rec, state: "acknowledged", replyChars: text.length, ...(outcome.reply.fingerprint ? { replyFingerprint: outcome.reply.fingerprint } : {}), history: [...rec.history, { at: at(), state: "acknowledged", note: "acknowledgement received" }] };
    }
    store.write(key, rec, v);
    return rec;
  });
}
