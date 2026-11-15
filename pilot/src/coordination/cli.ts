/**
 * coordination <owner/repo> <issueNumber>
 * Privileged: runs only in the protected 'minds-admin' environment from the default branch.
 * Validates the request, collects scoped context, calls the project's approved Mind with a structured
 * task, validates the reply and preserves the private result in SC_PRIVATE_RECORDS_DIR (a checkout of a
 * private control repository). Prints only sanitised status.
 */
import { loadConfig, getProject } from "../config/project.ts";
import { githubFromEnv } from "../github/api.ts";
import { FileStore } from "../lib/store.ts";
import { privateRecordsDir } from "../lib/paths.ts";
import { createServerMindsClient } from "../minds/client.ts";
import { parseMindMapping, resolveProjectMind } from "../minds/authority.ts";
import { dispatchTask } from "../minds/task.ts";
import { buildCoordinationTask, parseCoordinationRequest, requestAuthorised } from "./request.ts";

const [repo, num] = process.argv.slice(2);
if (!repo || !num) throw new Error("usage: coordination <owner/repo> <issue>");
const store = new FileStore(privateRecordsDir()); // fails closed if no private location is configured
const gh = githubFromEnv();
const issue = await gh.get<{ number: number; html_url: string; body: string; user: { login: string; id: number }; author_association: string; state: string }>(`/repos/${repo}/issues/${num}`);
if (issue.state !== "open") throw new Error("request issue is not open");
const req = parseCoordinationRequest(issue.body ?? "");
const cfg = loadConfig();
const p = getProject(cfg, req.project);
if (!requestAuthorised(p, issue.user.login, issue.user.id, issue.author_association)) throw new Error("requester is not authorised for this project");
const minds = createServerMindsClient();
const approval = process.env["SC_APPROVAL_REF"] ? { approvedBy: process.env["SC_APPROVED_BY"] ?? "", ref: process.env["SC_APPROVAL_REF"], action: "message", projectSlug: p.slug } : undefined;
const resolved = await resolveProjectMind({ cfg, mapping: parseMindMapping(process.env["MINDS_PROJECT_MAP"]), slug: p.slug, operation: "message", approval, minds });
const head = async (r: string, b: string) => (await gh.get<{ commit: { sha: string } }>(`/repos/${r}/branches/${encodeURIComponent(b)}`)).commit.sha;
const spec = buildCoordinationTask(p, req, { number: issue.number, url: issue.html_url }, { lab: await head(p.lab.repo, p.lab.branch), upstream: await head(p.upstream.repo, p.upstream.branch) });
const rec = await dispatchTask({ minds, store, mindId: resolved.mindId, aliasPrefix: p.mind.conversationPrefix ?? `sc-${p.slug}`, timeoutMs: 180_000 }, spec);
console.log(JSON.stringify({ taskId: spec.taskId, state: rec.state, note: rec.state === "completed" ? "validated result stored privately" : rec.state === "uncertain" ? "no confirmed reply yet; will reconcile, not resend" : "operator review required" }));
