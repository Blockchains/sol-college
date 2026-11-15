// Campus display state of a project's CTO agent. Mirrors scripts/landing.py:_agent_state (tested for agreement).
// Source of truth: config/autonomy.json (maintained by the autonomy worker). Paused: a "paused" map entry
// ({status, reason, ...}), a "paused"/"disabled" list, an "enabled" map set to false, or a project entry object
// with enabled:false / paused:true. A project with an approved Mind that autonomy.json does not schedule at all is
// shown as paused. Everything else that is scheduled is active.
import { existsSync, readFileSync } from "node:fs";
import { join } from "node:path";
import { REPO_ROOT } from "../lib/paths.ts";

export interface AgentState { state: "active" | "paused" | "none"; note: string }

const readJson = (f: string): Record<string, unknown> | null => {
  try { return existsSync(f) ? (JSON.parse(readFileSync(f, "utf8")) as Record<string, unknown>) : null; } catch { return null; }
};
const s = (v: unknown, max = 240) => (typeof v === "string" ? v.slice(0, max) : "");

export function agentState(slug: string, mappingStatus: string, root: string = REPO_ROOT): AgentState {
  if (mappingStatus !== "approved") return { state: "none", note: "No CTO agent provisioned" };
  const auto = readJson(join(root, "config", "autonomy.json")) ?? {};
  const projects = Array.isArray(auto["projects"]) ? (auto["projects"] as unknown[]) : [];
  let listed = false;
  let flag: boolean | null = null;
  let reason = "";
  for (const e of projects) {
    if (e === slug) listed = true;
    else if (e && typeof e === "object") {
      const o = e as Record<string, unknown>;
      if ((o["slug"] ?? o["project"] ?? o["id"]) !== slug) continue;
      listed = true;
      if (o["paused"] === true || o["enabled"] === false) flag = false;
      else if (o["enabled"] === true || o["paused"] === false) flag = true;
      reason = s(o["pausedReason"] ?? o["reason"] ?? o["note"]);
    }
  }
  const en = auto["enabled"];
  if (flag === null && en && typeof en === "object" && !Array.isArray(en) && typeof (en as Record<string, unknown>)[slug] === "boolean") flag = (en as Record<string, boolean>)[slug]!;
  const pz = auto["paused"], dz = auto["disabled"];
  if (flag === null && ((Array.isArray(pz) && pz.includes(slug)) || (Array.isArray(dz) && dz.includes(slug)))) flag = false;
  if (flag === null && pz && typeof pz === "object" && !Array.isArray(pz) && slug in (pz as object)) {
    flag = false;
    const v = (pz as Record<string, unknown>)[slug];
    if (!reason && v && typeof v === "object") {
      const o = v as Record<string, unknown>; const st = s(o["status"], 60), rs = s(o["reason"]);
      reason = s(st ? `${st.charAt(0).toUpperCase()}${st.slice(1)}${rs ? `: ${rs}` : ""}` : rs);
    } else if (!reason) reason = s(v);
  }
  if (flag === false) return { state: "paused", note: reason || "Paused in config/autonomy.json" };
  if (flag === true) return { state: "active", note: "Active: scheduled autonomy runs" };
  if (!listed) return { state: "paused", note: "Paused: not in the autonomy schedule" };
  return { state: "active", note: "Active: scheduled autonomy runs" };
}
