import { existsSync, readFileSync, readdirSync } from "node:fs";
import { join } from "node:path";
import { SECTORS, type ProjectConfig, type Sector } from "../config/types.ts";
import { findSecretLeaks } from "../lib/secrets.ts";

export interface PublicRecordLink {
  type: "research-question" | "experiment" | "pull-request" | "validation-run" | "adoption-package" | "acceptance" | "credential" | "upstream-pr";
  title: string;
  url: string;
  at: string;
}

export interface ExperimentsFile {
  project: string;
  experiments: Array<{ id: string; title: string; status: "idea" | "approved-experiment" | "tested-candidate" | "project-accepted" | "superseded"; baseline: string; candidateSha?: string; links: PublicRecordLink[] }>;
}

export interface CampusProject {
  slug: string;
  displayName: string;
  description: string;
  sector: Sector;
  ownership: ProjectConfig["ownership"];
  demonstrationNotice: string | null;
  cto: { status: "approved" | "proposed" | "none"; label: string };
  assignments: Array<{ id: string; title: string; skills: string[]; status: string; issueUrl: string | null }>;
  requiredSkills: string[];
  status: string;
  lastUpdated: string;
  contactRoute: string;
  coordination: string;
  progression: { ideas: number; approvedExperiments: number; testedCandidates: number; adoptionPackages: number; projectAccepted: number; activeCredentials: number };
  records: PublicRecordLink[];
  repos: { upstream: string; lab: string };
}

export interface CampusData {
  schema: "sc-campus/1";
  sectors: Array<{ id: Sector; name: string; blurb: string; projectSlugs: string[] }>;
  projects: CampusProject[];
  credentials: Array<{ credentialId: string; subject: string; project: string; acceptedWork: string; packageId: string; acceptedCommit: string; reviewer: string; issuedAt: string; status: string; statusHistory: Array<{ status: string; changedAt: string; reason?: string }>; recordUrl: string }>;
  notices: string[];
}

const BLURB: Record<Sector, string> = {
  DeFi: "Shared room for decentralised-finance projects: escrows, swaps, lending, payments.",
  DePIN: "Shared room for decentralised physical-infrastructure projects.",
  DeAI: "Shared room for decentralised-AI projects.",
};

/** Allowlisted public projection. Only fields named here can reach the public site. */
export function buildCampusData(projects: ProjectConfig[], recordsDir: string, repoBlobBase: string): CampusData {
  const live = projects.filter((p) => p.publicListing.approved && p.research.authorised && !p.placeholder);
  const regPath = join(recordsDir, "certificates", "registry.json");
  const registry = existsSync(regPath) ? (JSON.parse(readFileSync(regPath, "utf8")) as { credentials: Array<{ credentialId: string; subject: string; project: string; packageId: string; path: string; status: string; statusHistory: Array<{ status: string; changedAt: string; reason?: string }> }> }) : { credentials: [] };
  const credentials: CampusData["credentials"] = [];
  for (const c of registry.credentials) {
    if (!live.some((p) => p.slug === c.project)) continue;
    const full = JSON.parse(readFileSync(join(recordsDir, "certificates", c.path), "utf8")) as { acceptedWork: string; acceptedCommit: string; acceptanceEvidence: { reviewer: string }; issuedAt: string };
    credentials.push({ credentialId: c.credentialId, subject: c.subject, project: c.project, acceptedWork: full.acceptedWork, packageId: c.packageId, acceptedCommit: full.acceptedCommit, reviewer: full.acceptanceEvidence.reviewer, issuedAt: full.issuedAt, status: c.status, statusHistory: c.statusHistory.map((h) => ({ status: h.status, changedAt: h.changedAt, ...(h.reason ? { reason: h.reason } : {}) })), recordUrl: `${repoBlobBase}/records/public/certificates/${c.path}` });
  }
  const out: CampusProject[] = live.map((p) => {
    const expPath = join(recordsDir, "experiments", `${p.slug}.json`);
    const exps = existsSync(expPath) ? (JSON.parse(readFileSync(expPath, "utf8")) as ExperimentsFile).experiments : [];
    const pkgDir = join(recordsDir, "adoption", p.slug);
    const pkgs = existsSync(pkgDir) ? readdirSync(pkgDir).filter((f) => f.endsWith(".json")) : [];
    const accDir = join(recordsDir, "acceptance", p.slug);
    const accs = existsSync(accDir) ? readdirSync(accDir).filter((f) => f.endsWith(".json")) : [];
    const records: PublicRecordLink[] = exps.flatMap((e) => e.links);
    for (const f of pkgs) {
      const m = JSON.parse(readFileSync(join(pkgDir, f), "utf8")) as { packageId: string; createdAt: string };
      records.push({ type: "adoption-package", title: `Adoption package ${m.packageId}`, url: `${repoBlobBase}/records/public/adoption/${p.slug}/${f}`, at: m.createdAt });
    }
    for (const f of accs) {
      const a = JSON.parse(readFileSync(join(accDir, f), "utf8")) as { packageId: string; decidedAt: string; reviewer: { login: string } };
      records.push({ type: "acceptance", title: `Accepted by ${a.reviewer.login}: ${a.packageId}`, url: `${repoBlobBase}/records/public/acceptance/${p.slug}/${f}`, at: a.decidedAt });
    }
    records.sort((a, b) => b.at.localeCompare(a.at));
    const activeCreds = credentials.filter((c) => c.project === p.slug && c.status === "active").length;
    const lastUpdated = records[0]?.at ?? p.research.authorisedAt;
    const ctoLabel = p.mind.mappingStatus === "approved" ? "Sol.College-operated CTO Mind (asynchronous: requests are handled by GitHub workflows, not live chat)" : p.mind.mappingStatus === "proposed" ? "CTO Mind proposed, not yet provisioned (awaiting operator approval)" : "No CTO Mind assigned";
    const status = accs.length ? "Has project-accepted contributions" : pkgs.length ? "Adoption package awaiting project decision" : exps.some((e) => e.status === "tested-candidate") ? "Tested candidate" : exps.length ? "Experiment in progress" : "Listed";
    return {
      slug: p.slug,
      displayName: p.displayName,
      description: p.description,
      sector: p.sector,
      ownership: p.ownership,
      demonstrationNotice: p.demonstrationNotice ?? null,
      cto: { status: p.mind.mappingStatus, label: ctoLabel },
      assignments: p.publicListing.assignments.map((a) => ({ id: a.id, title: a.title, skills: a.skills, status: a.status, issueUrl: a.issueUrl ?? null })),
      requiredSkills: [...new Set(p.publicListing.assignments.flatMap((a) => a.skills))].sort(),
      status,
      lastUpdated,
      contactRoute: p.publicListing.contactRoute,
      coordination: "Asynchronous. Open a coordination request on GitHub; a protected workflow handles it. There is no live chat and no response is simulated.",
      progression: {
        ideas: exps.filter((e) => e.status === "idea").length,
        approvedExperiments: exps.filter((e) => e.status !== "idea").length,
        testedCandidates: exps.filter((e) => ["tested-candidate", "project-accepted"].includes(e.status)).length,
        adoptionPackages: pkgs.length,
        projectAccepted: accs.length,
        activeCredentials: activeCreds,
      },
      records,
      repos: { upstream: p.upstream.repo, lab: p.lab.repo },
    };
  });
  const data: CampusData = {
    schema: "sc-campus/1",
    sectors: SECTORS.map((s) => ({ id: s, name: s, blurb: BLURB[s], projectSlugs: out.filter((p) => p.sector === s).map((p) => p.slug) })),
    projects: out,
    credentials,
    notices: [
      "Sol.College is a GitHub-native asynchronous pilot. Nothing on this page is a live conversation.",
      "Projects marked as Sol.College demonstrations are run by Sol.College on its own forks. They do not imply a partnership with the upstream authors.",
      "Credentials are platform-published verification records. They are not accreditations, not on-chain and not cryptographically signed.",
    ],
  };
  assertPublicSafe(data);
  return data;
}

const FORBIDDEN_KEYS = new Set(["mindId", "email", "walletAddress", "mappingRef", "reviewers", "entitlement", "transcript", "builderApiKey", "humanId", "partyId", "configVersion"]);

export function assertPublicSafe(data: unknown): void {
  const walk = (v: unknown, path: string) => {
    if (Array.isArray(v)) v.forEach((x, i) => walk(x, `${path}[${i}]`));
    else if (v && typeof v === "object") for (const [k, x] of Object.entries(v)) {
      if (FORBIDDEN_KEYS.has(k)) throw new Error(`private field ${path}.${k} in public projection`);
      walk(x, `${path}.${k}`);
    }
    else if (typeof v === "string" && /@hellominds\.ai|[A-Za-z0-9._%+-]+@gmail\.com/.test(v)) throw new Error(`email-like value at ${path}`);
  };
  walk(data, "$");
  const leaks = findSecretLeaks(JSON.stringify(data), [process.env["MINDS_BUILDER_API_KEY"] ?? ""]);
  if (leaks.length) throw new Error(`secret-like content in projection: ${leaks.join(",")}`);
}
