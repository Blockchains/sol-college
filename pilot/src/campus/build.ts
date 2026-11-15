/** campus:build <siteDir>: writes <siteDir>/campus/ (static assets + allowlisted data.json). */
import { cpSync, mkdirSync, writeFileSync, readdirSync, readFileSync, rmSync } from "node:fs";
import { buildSync } from "esbuild";
import { join, resolve } from "node:path";
import { loadConfig } from "../config/project.ts";
import { PUBLIC_RECORDS_DIR, REPO_ROOT } from "../lib/paths.ts";
import { assertNoSecrets } from "../lib/secrets.ts";
import { buildCampusData } from "./projection.ts";

const site = resolve(process.argv[2] ?? join(REPO_ROOT, "site"));
const cfg = loadConfig();
if (cfg.issues.length) {
  for (const i of cfg.issues) console.error(`config error: ${i.file}: ${i.message}`);
  process.exit(1);
}
const data = buildCampusData(cfg.projects, PUBLIC_RECORDS_DIR, "https://github.com/Blockchains/sol-college/blob/main");
const out = join(site, "campus");
mkdirSync(out, { recursive: true });
cpSync(join(REPO_ROOT, "campus"), out, { recursive: true, filter: (src) => !src.includes("/campus/src") });
rmSync(join(out, "src"), { recursive: true, force: true });
// 3D view: bundle three.js (MIT, exact version in pilot/package-lock.json) with the scene code.
buildSync({ entryPoints: [join(REPO_ROOT, "campus/src/campus3d.js")], bundle: true, minify: true, format: "esm", target: "es2020", outfile: join(out, "campus3d.js"), nodePaths: [join(REPO_ROOT, "pilot/node_modules")], legalComments: "eof", logLevel: "warning" });
writeFileSync(join(out, "data.json"), JSON.stringify(data, null, 1) + "\n");
// final gate: nothing secret-shaped in any published campus file
const key = process.env["MINDS_BUILDER_API_KEY"] ?? "";
const walk = (d: string): string[] => readdirSync(d, { withFileTypes: true }).flatMap((e) => (e.isDirectory() ? walk(join(d, e.name)) : [join(d, e.name)]));
for (const f of walk(out)) if (/\.(json|html|js|css)$/.test(f) && !f.endsWith("campus3d.js")) assertNoSecrets(f, readFileSync(f, "utf8"), [key]);
console.log(JSON.stringify({ wrote: out, projects: data.projects.map((p) => `${p.sector}/${p.slug}`), credentials: data.credentials.length }));
