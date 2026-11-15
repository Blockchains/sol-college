import type { CircleMember, CircleMutationResult } from "@animocabrands/minds-client-lib";
import type { Approval } from "./authority.ts";
import type { MindsPort } from "./port.ts";

export interface CirclePolicy {
  /** Exact emails approved for this project's private CTO Circle (humans or Minds). */
  approvedMembers: string[];
}

export interface CirclePlan {
  add: string[];
  remove: string[];
  rejected: Array<{ email: string; reason: string }>;
}

const lc = (s: string) => s.trim().toLowerCase();

/** Plan a Circle change: only approved, explicitly listed members; never public/wildcard. */
export function planCircleChange(current: CircleMember[], desiredAdd: string[], desiredRemove: string[], policy: CirclePolicy): CirclePlan {
  const approved = new Set(policy.approvedMembers.map(lc));
  const have = new Set(current.filter((m) => !m.isSteward).map((m) => lc(m.email ?? "")));
  const stewards = new Set(current.filter((m) => m.isSteward).map((m) => lc(m.email ?? "")));
  const rejected: CirclePlan["rejected"] = [];
  const add: string[] = [];
  for (const e of desiredAdd.map(lc)) {
    if (!/^[^@\s*]+@[^@\s*]+\.[^@\s*]+$/.test(e)) rejected.push({ email: e, reason: "not a single explicit email" });
    else if (!approved.has(e)) rejected.push({ email: e, reason: "not on the approved member list" });
    else if (!have.has(e)) add.push(e);
  }
  const remove: string[] = [];
  for (const e of desiredRemove.map(lc)) {
    if (stewards.has(e)) rejected.push({ email: e, reason: "steward cannot be removed by automation" });
    else if (have.has(e)) remove.push(e);
  }
  return { add, remove, rejected };
}

export interface CircleAudit {
  email: string;
  action: string;
  confirmedInFinalState: boolean;
}

export async function applyCirclePlan(minds: Pick<MindsPort, "addCircleMembers" | "removeCircleMembers" | "getCircle">, mindId: string, plan: CirclePlan, approval: Approval | undefined): Promise<CircleAudit[]> {
  if (!approval) throw new Error("Circle changes require explicit approval");
  if (plan.rejected.length) throw new Error(`plan has rejected members: ${plan.rejected.map((r) => r.email).join(", ")}`);
  const results: CircleMutationResult[] = [];
  if (plan.add.length) results.push(await minds.addCircleMembers(mindId, { emails: plan.add, isActive: true }));
  if (plan.remove.length) results.push(await minds.removeCircleMembers(mindId, { emails: plan.remove }));
  const fin = new Set((await minds.getCircle(mindId)).map((m) => lc(m.email ?? "")));
  const audit: CircleAudit[] = [];
  for (const r of results) for (const it of r.items) {
    const e = lc(it.email);
    const wantPresent = plan.add.includes(e);
    audit.push({ email: e, action: it.action ?? "unknown", confirmedInFinalState: wantPresent ? fin.has(e) : !fin.has(e) });
  }
  return audit;
}
