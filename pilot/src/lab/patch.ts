/**
 * Deterministic gate for Mind-authored patches (unified diff). A patch that fails any check is never applied.
 * Checks: size limits, path allowlist (project program/app/test dirs only), no CI/workflow/.github edits,
 * no keypairs/env files, no binary patches, no secret-shaped added lines. gitleaks runs again in the workflow.
 */
import { findSecretLeaks } from "../lib/secrets.ts";
import { sha256Hex } from "../lib/canonical.ts";

export interface PatchPolicy { maxFiles: number; maxChangedLines: number; maxBytes: number; allowedPrefixes: string[] }

export const DEFAULT_PATCH_LIMITS = { maxFiles: 8, maxChangedLines: 400, maxBytes: 60_000 };

const DENY = [
  /(^|\/)\.github(\/|$)/, /(^|\/)\.gitlab-ci/, /(^|\/)\.vscode(\/|$)/, /(^|\/)\.devcontainer(\/|$)/, /(^|\/)\.cursor(\/|$)/,
  /(^|\/)\.env(\.|$)/, /(^|\/)id\.json$/, /keypair/i, /(^|\/)target\/deploy\//, /\.(pem|key|so|exe|dll|dylib|bin|wasm)$/i,
  /(^|\/)Anchor\.toml$/, /(^|\/)package\.json$/, /(^|\/)(yarn\.lock|package-lock\.json|pnpm-lock\.yaml)$/, /(^|\/)build\.rs$/,
  /(^|\/)\.git(\/|$)/, /(^|\/)\.gitmodules$/, /(^|\/)rust-toolchain/, /(^|\/)\.cargo\//,
];

/** Allowed paths for a project: its Anchor program and tests, plus common frontend source dirs. */
export function patchPolicyFor(programDir: string): PatchPolicy {
  const base = programDir === "." ? "" : `${programDir.replace(/\/$/, "")}/`;
  return { ...DEFAULT_PATCH_LIMITS, allowedPrefixes: [`${base}programs/`, `${base}tests/`, "app/src/", "app/app/", "app/components/", "app/lib/", "src/", "frontend/src/", "web/src/", "components/", "lib/", "tests/"] };
}

export interface PatchCheck { ok: boolean; reasons: string[]; files: string[]; added: number; removed: number; sha256: string }

export function filesInPatch(diff: string): string[] {
  const files = new Set<string>();
  for (const line of diff.split("\n")) {
    let m = /^diff --git a\/(\S+) b\/(\S+)$/.exec(line);
    if (m) { files.add(m[1]!); files.add(m[2]!); continue; }
    m = /^(?:\+\+\+|---) (?:[ab]\/)?(\S+)/.exec(line);
    if (m && m[1] !== "/dev/null") files.add(m[1]!);
  }
  return [...files];
}

export function checkPatch(diff: string, policy: PatchPolicy): PatchCheck {
  const reasons: string[] = [];
  const text = diff.replace(/\r\n/g, "\n");
  const files = filesInPatch(text);
  const lines = text.split("\n");
  const added = lines.filter((l) => l.startsWith("+") && !l.startsWith("+++")).length;
  const removed = lines.filter((l) => l.startsWith("-") && !l.startsWith("---")).length;
  if (!/^(diff --git |--- )/m.test(text) || !/^@@ /m.test(text)) reasons.push("not a unified diff");
  if (Buffer.byteLength(text) > policy.maxBytes) reasons.push(`larger than ${policy.maxBytes} bytes`);
  if (files.length === 0) reasons.push("no files");
  if (files.length > policy.maxFiles) reasons.push(`more than ${policy.maxFiles} files`);
  if (added + removed > policy.maxChangedLines) reasons.push(`more than ${policy.maxChangedLines} changed lines`);
  if (/^(GIT binary patch|Binary files )/m.test(text)) reasons.push("binary patch");
  if (/^(new|deleted) file mode 1[02]0755|^(old|new) mode /m.test(text)) reasons.push("mode changes are not allowed");
  if (/^(rename|copy) (from|to) /m.test(text)) reasons.push("renames/copies are not allowed");
  if (/^(new file mode 120000|similarity index)/m.test(text)) reasons.push("symlinks are not allowed");
  for (const f of files) {
    if (f.includes("..") || f.startsWith("/")) reasons.push(`unsafe path ${f}`);
    else if (DENY.some((re) => re.test(f))) reasons.push(`path not allowed: ${f}`);
    else if (!policy.allowedPrefixes.some((p) => f.startsWith(p))) reasons.push(`outside the path allowlist: ${f}`);
  }
  const addedText = lines.filter((l) => l.startsWith("+") && !l.startsWith("+++")).join("\n");
  if (findSecretLeaks(addedText).length) reasons.push("added lines contain secret-shaped text");
  if (/\b(mainnet-beta|api\.mainnet)\b/i.test(addedText)) reasons.push("added lines reference mainnet");
  return { ok: reasons.length === 0, reasons: [...new Set(reasons)], files, added, removed, sha256: sha256Hex(Buffer.from(text, "utf8")) };
}

/** Branch name for a Mind patch: sc-lab/<slug>/<task>. Never main, never an upstream branch. */
export function labBranch(slug: string, taskId: string): string {
  const b = `sc-lab/${slug}/${taskId}`.replace(/[^A-Za-z0-9/._-]/g, "-").slice(0, 120);
  if (!/^sc-lab\/[a-z0-9-]+\/[a-z0-9][a-z0-9._-]*$/.test(b)) throw new Error(`bad lab branch ${b}`);
  return b;
}
