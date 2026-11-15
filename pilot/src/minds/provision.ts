import { MindsApiError } from "@animocabrands/minds-client-lib";
import type { FileStore } from "../lib/store.ts";
import type { MindsPort } from "./port.ts";

export type ProvisionState =
  | "requested"
  | "creation-intent"
  | "creation-uncertain"
  | "mind-confirmed"
  | "mapping-recorded"
  | "conversation-configured"
  | "verified";

export interface ProvisionRecord {
  slug: string;
  projectId: string;
  state: ProvisionState;
  requestedName: string;
  archetype: string;
  approvalRef: string;
  mindId?: string;
  intentAt?: string;
  alias?: string;
  candidatesSeen?: string[];
  history: Array<{ at: string; state: ProvisionState; note: string }>;
}

export interface ProvisionRequest {
  slug: string;
  projectId: string;
  name: string;
  archetype: string;
  approvalRef: string;
}

const key = (slug: string) => `provision/${slug}`;
const now = () => new Date().toISOString();

function push(r: ProvisionRecord, state: ProvisionState, note: string): ProvisionRecord {
  return { ...r, state, history: [...r.history, { at: now(), state, note }] };
}

/** True when an error proves the request was rejected (no Mind can exist from it). */
function isDefinitiveRejection(e: unknown): boolean {
  return e instanceof MindsApiError && e.status >= 400 && e.status < 500 && e.status !== 408 && e.status !== 429;
}

/**
 * Idempotent provisioning. Never creates a second Mind for a project: once an intent is
 * recorded, an ambiguous outcome moves to creation-uncertain and requires operator resolution;
 * a Mind is never adopted just because its name matches.
 */
export async function provisionMind(minds: Pick<MindsPort, "checkMindName" | "awakenMind" | "listMinds">, store: FileStore, req: ProvisionRequest): Promise<ProvisionRecord> {
  const existing = store.read<ProvisionRecord>(key(req.slug));
  if (existing) {
    const r = existing.data;
    if (r.state === "mind-confirmed" || r.state === "mapping-recorded" || r.state === "conversation-configured" || r.state === "verified") return r;
    if (r.state === "creation-intent" || r.state === "creation-uncertain") {
      // Prior attempt may have created a Mind. Reconcile, never re-create.
      const owned = await minds.listMinds();
      const sameName = owned.filter((m) => (m.name ?? "") === r.requestedName).map((m) => m.mindId);
      const next = push({ ...r, candidatesSeen: sameName }, "creation-uncertain", sameName.length ? `found ${sameName.length} Mind(s) with the requested name; operator must confirm identity (name match is not proof)` : "no Mind with the requested name visible yet; operator must resolve before any retry");
      store.write(key(req.slug), next, existing.version);
      return next;
    }
  }
  let version = existing?.version ?? 0;
  let rec: ProvisionRecord = existing?.data ?? { slug: req.slug, projectId: req.projectId, state: "requested", requestedName: req.name, archetype: req.archetype, approvalRef: req.approvalRef, history: [{ at: now(), state: "requested", note: `approved by ${req.approvalRef}` }] };
  if (!existing) version = store.write(key(req.slug), rec, 0).version;

  const avail = await minds.checkMindName(req.name);
  if (!avail.isAvailable) {
    rec = push(rec, "requested", `name ${req.name} is not available; choose another name (not adopting the existing Mind)`);
    store.write(key(req.slug), rec, version);
    throw new Error(`Mind name ${req.name} is not available`);
  }
  rec = push({ ...rec, intentAt: now() }, "creation-intent", "intent recorded before awakenMind");
  version = store.write(key(req.slug), rec, version).version;
  try {
    const mind = await minds.awakenMind({ name: req.name, id: req.archetype });
    rec = push({ ...rec, mindId: mind.mindId }, "mind-confirmed", "awakenMind returned a mindId; recorded immediately");
    store.write(key(req.slug), rec, version);
    return rec;
  } catch (e) {
    if (isDefinitiveRejection(e)) {
      rec = push(rec, "requested", `awakenMind rejected: ${(e as MindsApiError).status} ${(e as MindsApiError).code}`);
      store.write(key(req.slug), rec, version);
      throw e;
    }
    rec = push(rec, "creation-uncertain", `awakenMind outcome unknown (${(e as Error).message}); not retrying automatically`);
    store.write(key(req.slug), rec, version);
    return rec;
  }
}

/** Operator resolution of an uncertain creation: explicitly confirm the Mind ID, or declare none was created. */
export function resolveUncertainProvision(store: FileStore, slug: string, resolution: { mindId: string; operator: string } | { noneCreated: true; operator: string }): ProvisionRecord {
  const cur = store.read<ProvisionRecord>(key(slug));
  if (!cur || cur.data.state !== "creation-uncertain") throw new Error(`no uncertain provisioning for ${slug}`);
  const next = "mindId" in resolution
    ? push({ ...cur.data, mindId: resolution.mindId }, "mind-confirmed", `operator ${resolution.operator} confirmed identity`)
    : push(cur.data, "requested", `operator ${resolution.operator} confirmed no Mind was created`);
  store.write(key(slug), next, cur.version);
  return next;
}

export function advanceProvision(store: FileStore, slug: string, to: "mapping-recorded" | "conversation-configured" | "verified", note: string, patch: Partial<ProvisionRecord> = {}): ProvisionRecord {
  const order: ProvisionState[] = ["mind-confirmed", "mapping-recorded", "conversation-configured", "verified"];
  const cur = store.read<ProvisionRecord>(key(slug));
  if (!cur) throw new Error(`no provisioning record for ${slug}`);
  const from = order.indexOf(cur.data.state);
  if (from < 0 || order.indexOf(to) !== from + 1) throw new Error(`illegal transition ${cur.data.state} -> ${to}`);
  const next = push({ ...cur.data, ...patch }, to, note);
  store.write(key(slug), next, cur.version);
  return next;
}
