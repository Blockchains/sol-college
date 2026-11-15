import type { LoadedConfig } from "../config/project.ts";
import { getPolicy, getProject } from "../config/project.ts";
import type { Policy, ProjectConfig } from "../config/types.ts";
import type { MindsPort } from "./port.ts";

export interface MindMappingEntry {
  projectId: string;
  mindId: string;
  configVersion: number;
  approvedBy: string;
  approvedAt: string;
  role: "project-cto" | "public-campus" | "test";
  testMind?: boolean;
}

export type MindMapping = Record<string, MindMappingEntry>;

/** Parse the protected mapping (GitHub environment secret MINDS_PROJECT_MAP). */
export function parseMindMapping(raw: string | undefined): MindMapping {
  if (!raw) return {};
  const parsed = JSON.parse(raw) as unknown;
  if (typeof parsed !== "object" || parsed === null || Array.isArray(parsed)) throw new Error("MINDS_PROJECT_MAP must be a JSON object");
  const out: MindMapping = {};
  for (const [ref, v] of Object.entries(parsed as Record<string, unknown>)) {
    if (ref.startsWith("_")) continue;
    const e = v as Partial<MindMappingEntry>;
    if (!e || typeof e.mindId !== "string" || typeof e.projectId !== "string" || typeof e.configVersion !== "number" || typeof e.approvedBy !== "string") {
      throw new Error(`mapping ${ref} is malformed`);
    }
    out[ref] = e as MindMappingEntry;
  }
  return out;
}

export class AuthorityError extends Error {
  constructor(message: string) {
    super(message);
    this.name = "AuthorityError";
  }
}

export interface Approval {
  /** Who approved (GitHub login) and the reference (environment approval run id, or operator ticket). */
  approvedBy: string;
  ref: string;
  action: string;
  projectSlug: string;
}

export interface ResolvedProjectMind {
  project: ProjectConfig;
  policy: Policy;
  mapping: MindMappingEntry;
  mindId: string;
}

/**
 * Resolve the approved Mind for a project. Callers pass a project slug, never a Mind ID.
 * Checks: project exists and is live (not placeholder), mapping approved in public config and
 * present in protected mapping, projectId and configVersion match, operation permitted (with
 * approval for mutations), and the Mind belongs to this Builder account (listMinds).
 */
export async function resolveProjectMind(args: {
  cfg: LoadedConfig;
  mapping: MindMapping;
  slug: string;
  operation: string;
  approval?: Approval | undefined;
  minds: Pick<MindsPort, "listMinds">;
}): Promise<ResolvedProjectMind> {
  const project = getProject(args.cfg, args.slug);
  const policy = getPolicy(args.cfg, project);
  authoriseOperation(policy, args.operation, args.slug, args.approval);
  if (project.mind.mappingStatus !== "approved") throw new AuthorityError(`project ${args.slug} has no approved Mind mapping (status ${project.mind.mappingStatus})`);
  const entry = args.mapping[project.mind.mappingRef];
  if (!entry) throw new AuthorityError(`protected mapping ${project.mind.mappingRef} is missing`);
  if (entry.projectId !== project.projectId) throw new AuthorityError(`mapping ${project.mind.mappingRef} belongs to ${entry.projectId}, not ${project.projectId}`);
  if (entry.configVersion !== project.mind.configVersion) throw new AuthorityError(`mapping configVersion ${entry.configVersion} is not current (${project.mind.configVersion})`);
  const owned = await args.minds.listMinds();
  if (!owned.some((m) => m.mindId === entry.mindId)) throw new AuthorityError(`mapped Mind is not on this Builder account`);
  return { project, policy, mapping: entry, mindId: entry.mindId };
}

export function authoriseOperation(policy: Policy, operation: string, slug: string, approval?: Approval): void {
  if (policy.operations.readOnly.includes(operation)) return;
  if (!policy.operations.requiresApproval.includes(operation)) throw new AuthorityError(`operation ${operation} is not permitted by ${policy.policyVersion}`);
  if (!approval) throw new AuthorityError(`operation ${operation} requires approval`);
  if (approval.action !== operation || approval.projectSlug !== slug) throw new AuthorityError(`approval ${approval.ref} does not cover ${operation} on ${slug}`);
  if (!approval.approvedBy || !approval.ref) throw new AuthorityError("approval is incomplete");
  if (policy.agentIdentities.map((a) => a.toLowerCase()).includes(approval.approvedBy.toLowerCase())) throw new AuthorityError("an agent identity cannot approve");
}
