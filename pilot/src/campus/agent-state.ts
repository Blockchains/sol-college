// Campus display state of a project's CTO agent. Mirrors scripts/landing.py:_agent_state (tested for agreement).
// Source of truth: config/autonomy.json (maintained by the autonomy worker). Paused: a "paused" map entry
// ({status, reason, ...}), a "paused"/"disabled" list, an "enabled" map set to false, or a project entry object
// with enabled:false / paused:true. A project with an approved Mind that autonomy.json does not schedule at all is
// shown as paused. A scheduled agent is also shown as paused when its operations snapshot
// (records/public/minds/<slug>.json, published by the autonomy loop) says paused / not enabled, or its cognition
// balance is at or below zero (it cannot produce work). Topping up credits flips it back on the next build.
import { existsSync, readFileSync } from "node:fs";
import { join } from "node:path";
import { REPO_ROOT } from "../lib/paths.ts";

export interface AgentState { state: "active" | "paused" | "none"; label: string; note: string }

const readJson = (f: string): Record<string, unknown> | null => {
  try { return existsSync(f) ? (JSON.parse(readFileSync(f, "utf8")) as Record<string, unknown>) : null; } catch { return null; }
};
const s = (v: unknown, max = 240) => (typeof v === "string" ? v.slice(0, max) : "");

export function agentState(slug: string, mappingStatus: string, root: string = REPO_ROOT): AgentState {
  if (mappingStatus !== "approved") return { state: "none", label: "", note: "No CTO agent provisioned" };
  const fromConfig = configState(slug, root);
  if (fromConfig.state !== "active") return fromConfig;
  const ops = readJson(join(root, "records", "public", "minds", `${slug}.json`));
  if (ops) {
    const bal = ops["cognitionBalance"], at = s(ops["balanceCheckedAt"] ?? ops["at"], 16).replace("T", " ");
    if (ops["paused"] === true || ops["isEnabled"] === false) return { state: "paused", label: "Paused", note: s(ops["pausedReason"]) || `Paused (${s(ops["status"], 60) || "Mind not enabled"})` };
    if (typeof bal === "number" && bal <= 0) return { state: "paused", label: "No credits", note: `Out of credits: HelloMinds cognition balance ${bal.toFixed(2)}${at ? ` (checked ${at} UTC)` : ""}. This agent cannot produce work until its credits are topped up.` };
  }
  return fromConfig;
}

function configState(slug: string, root: string): AgentState {
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
  if (flag === false) return { state: "paused", label: "Paused", note: reason || "Paused in config/autonomy.json" };
  if (flag === true) return { state: "active", label: "Active", note: "Active: scheduled autonomy runs" };
  if (!listed) return { state: "paused", label: "Paused", note: "Paused: not in the autonomy schedule" };
  return { state: "active", label: "Active", note: "Active: scheduled autonomy runs" };
}
