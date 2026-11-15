/**
 * autonomy [--dry-run] [--project slug]
 * One autonomy pass for every project in config/autonomy.json. Trusted runtime only (protected environment).
 * Prints a sanitised summary; never prints the Builder key, Mind IDs or private Mind output.
 */
import { parseArgs } from "node:util";
import { loadConfig } from "../config/project.ts";
import { githubFromEnv } from "../github/api.ts";
import { privateRecordsDir } from "../lib/paths.ts";
import { assertNoSecrets } from "../lib/secrets.ts";
import { FileStore } from "../lib/store.ts";
import { parseMindMapping } from "../minds/authority.ts";
import { builderKeyFromEnv, createServerMindsClient } from "../minds/client.ts";
import { loadAutonomy, runProject } from "./run.ts";

const { values } = parseArgs({ options: { "dry-run": { type: "boolean", default: false }, project: { type: "string" } } });
const cfg = loadConfig();
if (cfg.issues.length) throw new Error(`config invalid: ${cfg.issues.map((i) => i.message).join("; ")}`);
const auto = loadAutonomy();
const deps = {
  minds: createServerMindsClient(),
  gh: githubFromEnv(),
  store: new FileStore(privateRecordsDir()),
  cfg,
  mapping: parseMindMapping(process.env["MINDS_PROJECT_MAP"]),
  auto,
  now: () => new Date(),
  runUrl: process.env["GITHUB_RUN_ID"] ? `https://github.com/${process.env["GITHUB_REPOSITORY"]}/actions/runs/${process.env["GITHUB_RUN_ID"]}` : null,
  dryRun: values["dry-run"] ?? false,
};
const results: Array<Record<string, unknown>> = [];
let failed = 0;
for (const slug of auto.projects.filter((s) => !values.project || s === values.project)) {
  const lines: string[] = [];
  try {
    const { status } = await runProject(deps, slug, (s) => lines.push(s));
    results.push({ project: slug, ok: true, pendingTasks: status.pendingTasks, operatorReview: status.operatorReview, openLabPullRequests: status.openLabPullRequests, actions: lines });
  } catch (e) {
    failed++;
    results.push({ project: slug, ok: false, error: (e as Error).message.replace(/eyJ[A-Za-z0-9._-]+/g, "[REDACTED]").replace(/\b([0-9a-f]{8})-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}\b/gi, "$1…") });
  }
}
const out = JSON.stringify({ at: new Date().toISOString(), dryRun: deps.dryRun, results }, null, 2);
assertNoSecrets("autonomy output", out, [builderKeyFromEnv() ?? ""]);
console.log(out);
if (failed) process.exitCode = 1;
