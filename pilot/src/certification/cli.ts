/**
 * certificate issue <packageId> <subjectLogin>   (fails closed unless a recorded acceptance re-verifies against GitHub)
 * certificate revoke <credentialId> <reason...>  /  certificate supersede <credentialId> <newId> <reason...>
 */
import { readFileSync, existsSync } from "node:fs";
import { join } from "node:path";
import { loadConfig } from "../config/project.ts";
import { githubFromEnv, type GhIssueComment } from "../github/api.ts";
import { PUBLIC_RECORDS_DIR } from "../lib/paths.ts";
import { readManifestBytes } from "../adoption/package.ts";
import { parseAcceptanceComment, type AcceptanceRecord } from "../acceptance/accept.ts";
import { changeCredentialStatus, issueCredential, publishCredential, CertificationRefused } from "./certificate.ts";

const [cmd, a, b, ...rest] = process.argv.slice(2);
const certDir = join(PUBLIC_RECORDS_DIR, "certificates");
if (cmd === "issue") {
  if (!a || !b) throw new Error("usage: certificate issue <packageId> <subject>");
  const project = loadConfig().projects.find((p) => a.startsWith(`${p.slug}-`));
  if (!project) throw new CertificationRefused("unknown project for package");
  const accPath = join(PUBLIC_RECORDS_DIR, "acceptance", project.slug, `${a}.json`);
  const acc = existsSync(accPath) ? (JSON.parse(readFileSync(accPath, "utf8")) as AcceptanceRecord) : undefined;
  let verified = false;
  if (acc && acc.method === "auto-owner-policy") {
    // Re-verify the policy conditions now: same package bytes/hash/candidate and a still-passing exact-SHA validation.
    const { verifyAutoAcceptance } = await import("../acceptance/accept.ts");
    const { getPolicy } = await import("../config/project.ts");
    const { evaluateCandidate, fetchValidationEvidence } = await import("../validation/evidence.ts");
    const g = githubFromEnv();
    const pol = getPolicy(loadConfig(), project);
    const pkg = readManifestBytes(join(PUBLIC_RECORDS_DIR, "adoption", project.slug, `${a}.json`));
    const candidate = { project: project.slug, repo: project.lab.repo, sha: pkg.manifest.candidate.sha };
    const ev = await fetchValidationEvidence(g, { workflowRepo: project.validation.workflowRepo, workflowPath: project.validation.workflowPath, titlePrefix: pol.validation.runTitlePrefix, candidate, requiredJobs: pol.validation.requiredJobs });
    const repo = await g.get<{ id: number; default_branch: string }>(`/repos/${project.validation.workflowRepo}`);
    const wf = await g.get<{ id: number }>(`/repos/${project.validation.workflowRepo}/actions/workflows/${project.validation.workflowPath.split("/").pop()}`);
    const verdict = evaluateCandidate(ev, candidate, { repositoryId: repo.id, workflowId: wf.id, workflowPath: project.validation.workflowPath, defaultBranch: repo.default_branch, requiredJobs: pol.validation.requiredJobs });
    const again = verifyAutoAcceptance({ project, manifest: pkg.manifest, storedBytes: pkg.bytes, storedManifestSha256: pkg.sha256, currentVerdict: verdict, now: acc.decidedAt });
    verified = again.acceptanceId === acc.acceptanceId && again.manifestSha256 === acc.manifestSha256 && again.candidateSha === acc.candidateSha;
  } else if (acc) {
    // Re-verify the acceptance evidence still exists on GitHub, unedited, from the same account.
    const c = await githubFromEnv().get<GhIssueComment>(`/repos/${acc.evidence.repo}/issues/comments/${acc.evidence.commentId}`);
    const cmdNow = parseAcceptanceComment(c.body);
    verified = Boolean(cmdNow && c.user.id === acc.reviewer.id && c.created_at === c.updated_at && cmdNow.packageId === acc.packageId && cmdNow.manifestSha256 === acc.manifestSha256 && cmdNow.candidateSha === acc.candidateSha && project.reviewers.some((r) => r.githubId === c.user.id && r.roles.includes("adoption-acceptance")));
  }
  const { manifest, sha256 } = readManifestBytes(join(PUBLIC_RECORDS_DIR, "adoption", project.slug, `${a}.json`));
  const cred = issueCredential({ acceptance: acc, acceptanceVerified: verified, manifest, manifestSha256: sha256, subject: b, issuedAt: new Date().toISOString(), verifyBaseUrl: "https://sol.college/campus/" });
  const r = publishCredential(certDir, cred);
  console.log(JSON.stringify({ outcome: r.created ? "issued" : "exists", credentialId: cred.credentialId, path: `records/public/certificates/${r.path}` }));
} else if (cmd === "revoke" || cmd === "supersede") {
  if (!a) throw new Error("credential id required");
  const reason = (cmd === "supersede" ? rest : [b ?? "", ...rest]).join(" ").trim();
  if (!reason) throw new Error("reason required");
  const reg = changeCredentialStatus(certDir, a, cmd === "revoke" ? "revoked" : "superseded", reason, new Date().toISOString(), cmd === "supersede" ? b : undefined);
  console.log(JSON.stringify({ outcome: cmd, credentialId: a, status: reg.credentials.find((c) => c.credentialId === a)?.status }));
} else {
  throw new Error("usage: certificate issue|revoke|supersede ...");
}
