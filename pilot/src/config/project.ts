import { readFileSync, readdirSync, existsSync } from "node:fs";
import { join } from "node:path";
import { createRequire } from "node:module";
import type { ErrorObject, ValidateFunction } from "ajv";
import { CONFIG_DIR } from "../lib/paths.ts";
import type { Policy, ProjectConfig } from "./types.ts";

const require = createRequire(import.meta.url);
// ajv ships CJS; load through require so NodeNext + verbatimModuleSyntax stay strict-clean.
const AjvCtor = require("ajv").default as new (opts: Record<string, unknown>) => { compile: (s: object) => ValidateFunction; addFormat: (n: string, f: RegExp) => void };

const PLACEHOLDER_RE = /(example|placeholder|todo|changeme|xxx|00000000-0000)/i;

export interface ValidationIssue {
  file: string;
  message: string;
}

export interface LoadedConfig {
  projects: ProjectConfig[];
  policies: Map<string, Policy>;
  issues: ValidationIssue[];
  excludedPlaceholders: string[];
}

let validator: ValidateFunction | undefined;
function schemaValidator(): ValidateFunction {
  if (validator) return validator;
  const ajv = new AjvCtor({ allErrors: true, strict: true });
  ajv.addFormat("date-time", /^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}(\.\d+)?(Z|[+-]\d{2}:\d{2})$/);
  ajv.addFormat("date", /^\d{4}-\d{2}-\d{2}$/);
  ajv.addFormat("uri", /^https:\/\/[^\s]+$/);
  const schema = JSON.parse(readFileSync(join(CONFIG_DIR, "schemas/project.schema.json"), "utf8")) as object;
  validator = ajv.compile(schema);
  return validator;
}

export function isPlaceholder(p: Partial<ProjectConfig>): boolean {
  if (p.placeholder === true) return true;
  return [p.projectId, p.slug, p.displayName, p.upstream?.repo, p.lab?.repo].some((v) => typeof v === "string" && PLACEHOLDER_RE.test(v));
}

/** JSON Schema + semantic validation. Returns issues; empty = valid. */
export function validateProject(raw: unknown, file: string, policies: Map<string, Policy>): ValidationIssue[] {
  const issues: ValidationIssue[] = [];
  const v = schemaValidator();
  if (!v(raw)) {
    for (const e of (v.errors ?? []) as ErrorObject[]) issues.push({ file, message: `schema ${e.instancePath || "/"} ${e.message ?? ""}`.trim() });
    return issues;
  }
  const p = raw as ProjectConfig;
  const blank = (s: string) => s.trim().length === 0;
  if (blank(p.displayName) || blank(p.slug) || blank(p.upstream.branch) || blank(p.lab.branch)) issues.push({ file, message: "names and branches must be non-empty" });
  if (p.research.scope.length === 0 || p.research.scope.some(blank)) issues.push({ file, message: "research scope must be non-empty" });
  if (p.research.exclusions.length === 0) issues.push({ file, message: "research exclusions must be explicit (non-empty)" });
  const logins = p.reviewers.map((r) => r.github.toLowerCase());
  if (new Set(logins).size !== logins.length) issues.push({ file, message: "reviewers must be unique" });
  const ids = p.reviewers.map((r) => r.githubId);
  if (new Set(ids).size !== ids.length) issues.push({ file, message: "reviewer GitHub ids must be unique" });
  if (!p.reviewers.some((r) => r.roles.includes("adoption-acceptance"))) issues.push({ file, message: "at least one adoption-acceptance reviewer is required" });
  const policy = policies.get(p.policyVersion);
  if (!policy) issues.push({ file, message: `policy ${p.policyVersion} does not resolve` });
  else {
    const strip = (a: string) => a.toLowerCase().replace(/\[bot\]$/, "");
    const agents = new Set(policy.agentIdentities.map(strip));
    for (const r of p.reviewers) if (agents.has(strip(r.github))) issues.push({ file, message: `agent identity ${r.github} cannot be a reviewer` });
  }
  if (p.ownership === "sol-college-demonstration" && !p.demonstrationNotice) issues.push({ file, message: "demonstration projects must carry a demonstrationNotice" });
  if (p.ownership === "participating-project" && p.entitlement.paymentVerification === "not-applicable-demonstration") issues.push({ file, message: "participating projects cannot use the demonstration entitlement" });
  if (!p.research.authorised && p.publicListing.approved && !isPlaceholder(p)) issues.push({ file, message: "public listing requires research authorisation" });
  const forbiddenPublic = ["mindId", "email", "walletAddress", "reviewers", "entitlement", "mind"];
  for (const f of p.disclosure.publicFields) if (forbiddenPublic.includes(f)) issues.push({ file, message: `field ${f} may not be public` });
  if (file && !file.endsWith(`${p.slug}.json`)) issues.push({ file, message: `file name must be ${p.slug}.json` });
  return issues;
}

export function loadPolicies(dir = join(CONFIG_DIR, "policies")): Map<string, Policy> {
  const m = new Map<string, Policy>();
  for (const f of readdirSync(dir).filter((x) => x.endsWith(".json"))) {
    const pol = JSON.parse(readFileSync(join(dir, f), "utf8")) as Policy;
    m.set(pol.policyVersion, pol);
  }
  return m;
}

/** Loads live projects (config/projects). Placeholders are excluded from live execution. */
export function loadConfig(dir = join(CONFIG_DIR, "projects"), policies = loadPolicies()): LoadedConfig {
  const issues: ValidationIssue[] = [];
  const projects: ProjectConfig[] = [];
  const excludedPlaceholders: string[] = [];
  const files = existsSync(dir) ? readdirSync(dir).filter((x) => x.endsWith(".json")).sort() : [];
  const slugs = new Set<string>();
  const projectIds = new Set<string>();
  for (const f of files) {
    let raw: unknown;
    try {
      raw = JSON.parse(readFileSync(join(dir, f), "utf8"));
    } catch (e) {
      issues.push({ file: f, message: `invalid JSON: ${(e as Error).message}` });
      continue;
    }
    if (raw && typeof raw === "object" && isPlaceholder(raw as Partial<ProjectConfig>)) {
      excludedPlaceholders.push(f);
      continue;
    }
    const fileIssues = validateProject(raw, f, policies);
    if (fileIssues.length) {
      issues.push(...fileIssues);
      continue;
    }
    const p = raw as ProjectConfig;
    if (isPlaceholder(p)) {
      excludedPlaceholders.push(f);
      continue;
    }
    if (slugs.has(p.slug)) issues.push({ file: f, message: `duplicate slug ${p.slug}` });
    if (projectIds.has(p.projectId)) issues.push({ file: f, message: `duplicate projectId ${p.projectId}` });
    slugs.add(p.slug);
    projectIds.add(p.projectId);
    projects.push(p);
  }
  return { projects, policies, issues, excludedPlaceholders };
}

export function getProject(cfg: LoadedConfig, slug: string): ProjectConfig {
  const p = cfg.projects.find((x) => x.slug === slug);
  if (!p) throw new Error(`unknown or non-live project: ${slug}`);
  return p;
}

export function getPolicy(cfg: LoadedConfig, p: ProjectConfig): Policy {
  const pol = cfg.policies.get(p.policyVersion);
  if (!pol) throw new Error(`policy ${p.policyVersion} not found`);
  return pol;
}
