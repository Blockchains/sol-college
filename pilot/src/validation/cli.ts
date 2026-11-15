/** evidence <slug> <candidateSha>: fetch genuine GitHub evidence and print the verdict (read-only). */
import { loadConfig, getProject, getPolicy } from "../config/project.ts";
import { githubFromEnv, type GhRepo, type GhWorkflow } from "../github/api.ts";
import { evaluateCandidate, fetchValidationEvidence } from "./evidence.ts";

const [slug, sha] = process.argv.slice(2);
if (!slug || !sha) throw new Error("usage: evidence <slug> <sha>");
const cfg = loadConfig();
const p = getProject(cfg, slug);
const pol = getPolicy(cfg, p);
const gh = githubFromEnv();
const candidate = { project: p.slug, repo: p.lab.repo, sha };
const ev = await fetchValidationEvidence(gh, { workflowRepo: p.validation.workflowRepo, workflowPath: p.validation.workflowPath, titlePrefix: pol.validation.runTitlePrefix, candidate, requiredJobs: pol.validation.requiredJobs });
const repo = await gh.get<GhRepo & { default_branch: string }>(`/repos/${p.validation.workflowRepo}`);
const wf = await gh.get<GhWorkflow>(`/repos/${p.validation.workflowRepo}/actions/workflows/${p.validation.workflowPath.split("/").pop()}`);
const verdict = evaluateCandidate(ev, candidate, { repositoryId: repo.id, workflowId: wf.id, workflowPath: p.validation.workflowPath, defaultBranch: repo.default_branch, requiredJobs: pol.validation.requiredJobs });
console.log(JSON.stringify(verdict, null, 2));
process.exit(verdict.passed ? 0 : 3);
