/** Minimal GitHub REST client (fetch-based, injectable for tests). Read-only unless noted. */
export type FetchLike = (url: string, init?: { method?: string; headers?: Record<string, string>; body?: string }) => Promise<{ ok: boolean; status: number; json: () => Promise<unknown>; text: () => Promise<string> }>;

export class GitHubApi {
  constructor(private readonly token: string | undefined, private readonly fetcher: FetchLike = fetch as unknown as FetchLike, private readonly base = "https://api.github.com") {}

  async get<T>(path: string): Promise<T> {
    const headers: Record<string, string> = { accept: "application/vnd.github+json", "x-github-api-version": "2022-11-28", "user-agent": "sol-college-pilot" };
    if (this.token) headers["authorization"] = `Bearer ${this.token}`;
    const r = await this.fetcher(`${this.base}${path}`, { headers });
    if (!r.ok) throw new Error(`GitHub GET ${path} -> ${r.status}`);
    return (await r.json()) as T;
  }

  /** Write call (POST/PATCH). Only used by workflows whose token permissions allow it. 204 -> undefined. */
  async send<T>(method: "POST" | "PATCH", path: string, body: unknown): Promise<T | undefined> {
    const headers: Record<string, string> = { accept: "application/vnd.github+json", "x-github-api-version": "2022-11-28", "user-agent": "sol-college-pilot", "content-type": "application/json" };
    if (this.token) headers["authorization"] = `Bearer ${this.token}`;
    const r = await this.fetcher(`${this.base}${path}`, { method, headers, body: JSON.stringify(body) });
    if (!r.ok) throw new Error(`GitHub ${method} ${path} -> ${r.status}`);
    if (r.status === 204) return undefined;
    const t = await r.text();
    return (t ? JSON.parse(t) : undefined) as T | undefined;
  }
}

export interface GhRepo { id: number; full_name: string; private: boolean }
export interface GhWorkflow { id: number; path: string; name: string; state: string }
export interface GhRun {
  id: number;
  name: string;
  display_title: string;
  path: string;
  workflow_id: number;
  head_sha: string;
  head_branch: string;
  event: string;
  status: string;
  conclusion: string | null;
  run_attempt: number;
  created_at: string;
  html_url: string;
  repository: { id: number; full_name: string };
}
export interface GhJob { id: number; name: string; status: string; conclusion: string | null; run_attempt: number; head_sha: string }
export interface GhArtifact { id: number; name: string; digest?: string | null; expired: boolean; size_in_bytes: number }
export interface GhCompare { status: "ahead" | "behind" | "identical" | "diverged"; ahead_by: number; behind_by: number; merge_base_commit: { sha: string } }
export interface GhIssueComment { id: number; body: string; html_url: string; created_at: string; updated_at: string; author_association: string; user: { login: string; id: number; type: string } }

export function githubFromEnv(fetcher?: FetchLike): GitHubApi {
  return new GitHubApi(process.env["GITHUB_TOKEN"] ?? process.env["GH_TOKEN"], fetcher);
}
