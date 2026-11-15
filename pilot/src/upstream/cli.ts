/** upstream <slug>: read the actual upstream head, reconcile against recorded state, print impact. */
import { readFileSync, existsSync } from "node:fs";
import { join } from "node:path";
import { loadConfig, getProject } from "../config/project.ts";
import { githubFromEnv } from "../github/api.ts";
import { FileStore } from "../lib/store.ts";
import { PUBLIC_RECORDS_DIR } from "../lib/paths.ts";
import { githubCompare, reconcileUpstream, type ExperimentRef } from "./reconcile.ts";

const [slug] = process.argv.slice(2);
if (!slug) throw new Error("usage: upstream <slug>");
const p = getProject(loadConfig(), slug);
const gh = githubFromEnv();
const head = (await gh.get<{ commit: { sha: string } }>(`/repos/${p.upstream.repo}/branches/${encodeURIComponent(p.upstream.branch)}`)).commit.sha;
const expFile = join(PUBLIC_RECORDS_DIR, "experiments", `${slug}.json`);
const experiments: ExperimentRef[] = existsSync(expFile) ? (JSON.parse(readFileSync(expFile, "utf8")) as { experiments: ExperimentRef[] }).experiments : [];
const store = new FileStore(join(PUBLIC_RECORDS_DIR, "upstream"));
const res = await reconcileUpstream({ store, project: slug, upstreamRepo: p.upstream.repo, branch: p.upstream.branch, observedHead: head, compare: githubCompare(gh, p.upstream.repo), experiments });
console.log(JSON.stringify(res, null, 2));
