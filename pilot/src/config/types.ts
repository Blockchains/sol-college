export type Sector = "DeFi" | "DePIN" | "DeAI";
export const SECTORS: readonly Sector[] = ["DeFi", "DePIN", "DeAI"] as const;

export type ReviewerRole = "experiment-permission" | "rebase-permission" | "compatibility-attestation" | "adoption-acceptance";

export interface RepoRef {
  repo: string;
  branch: string;
}

export interface Assignment {
  id: string;
  title: string;
  skills: string[];
  status: "open" | "in-progress" | "closed";
  issueUrl?: string;
}

export interface ProjectConfig {
  schemaVersion: 1;
  placeholder?: boolean;
  projectId: string;
  slug: string;
  displayName: string;
  description: string;
  sector: Sector;
  ownership: "sol-college-demonstration" | "participating-project";
  demonstrationNotice?: string;
  upstream: RepoRef;
  lab: RepoRef;
  mind: { mappingRef: string; mappingStatus: "approved" | "proposed" | "none"; configVersion: number; conversationPrefix?: string };
  research: { authorised: boolean; authorisedBy: string; authorisedAt: string; authorisationRef: string; scope: string[]; exclusions: string[] };
  reviewers: Array<{ github: string; githubId: number; roles: ReviewerRole[] }>;
  policyVersion: string;
  publicListing: { approved: boolean; assignments: Assignment[]; contactRoute: string };
  disclosure: { securityReports: "private-only"; mindsTranscripts: "private-only"; publicFields: string[] };
  entitlement: {
    plan: string;
    status: "active" | "paused" | "expired";
    periodStart?: string;
    periodEnd?: string;
    activation: "manual";
    paymentVerification: "none-manual-entitlement" | "not-applicable-demonstration";
    usageAllowanceCognition?: number;
  };
  validation: { workflowRepo: string; workflowPath: string; fixture: string; programDir?: string; anchorVersion: string; solanaVersion: string; rustToolchain: string };
}

export interface Policy {
  policyVersion: string;
  operations: { readOnly: string[]; requiresApproval: string[]; approvalMechanism: string };
  agentIdentities: string[];
  acceptance: { command: string; requiredRole: ReviewerRole; allowedAuthorAssociations: string[]; staleIf: string[] };
  validation: { requiredJobs: string[]; rerunPolicy: string; runTitlePrefix: string };
  certification: { verificationType: string; signed: boolean; notes: string };
}
