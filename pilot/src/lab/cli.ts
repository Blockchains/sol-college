/**
 * lab check --project <slug> --patch FILE [--sha256 HEX]   deterministic patch gate (exit 1 on failure)
 * lab branch --project <slug> --task <taskId>              prints the sc-lab branch name
 * Used by the protected lab-patch workflow; prints JSON only (no patch content).
 */
import { readFileSync } from "node:fs";
import { parseArgs } from "node:util";
import { loadConfig, getProject } from "../config/project.ts";
import { checkPatch, labBranch, patchPolicyFor } from "./patch.ts";

const { positionals, values } = parseArgs({ allowPositionals: true, options: { project: { type: "string" }, patch: { type: "string" }, sha256: { type: "string" }, task: { type: "string" } } });
const cfg = loadConfig();
const p = getProject(cfg, values.project ?? "");
if (positionals[0] === "check") {
  const diff = readFileSync(values.patch!, "utf8");
  const r = checkPatch(diff, patchPolicyFor(p.validation.programDir ?? "contract"));
  if (values.sha256 && values.sha256 !== r.sha256) r.reasons.push("patch sha256 does not match the dispatched hash"), (r.ok = false);
  console.log(JSON.stringify({ project: p.slug, ok: r.ok, reasons: r.reasons, files: r.files, added: r.added, removed: r.removed, sha256: r.sha256 }));
  if (!r.ok) process.exit(1);
} else if (positionals[0] === "branch") {
  console.log(labBranch(p.slug, values.task ?? ""));
} else throw new Error("usage: lab check|branch");
