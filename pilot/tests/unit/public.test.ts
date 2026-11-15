// [contract] Public projection + secrets hygiene + workflow static checks.
import { test } from "node:test";
import assert from "node:assert/strict";
import { readFileSync, readdirSync } from "node:fs";
import { join } from "node:path";
import { parse } from "yaml";
import { buildCampusData, assertPublicSafe } from "../../src/campus/projection.ts";
import { PUBLIC_RECORDS_DIR, REPO_ROOT } from "../../src/lib/paths.ts";
import { findSecretLeaks } from "../../src/lib/secrets.ts";
import { cfg, gifter, tmp } from "../fixtures/helpers.ts";

test("Public: campus projection has exactly the three sector rooms and excludes private data", () => {
  const data = buildCampusData(cfg().projects, PUBLIC_RECORDS_DIR, "https://github.com/Blockchains/sol-college/blob/main");
  assert.deepEqual(data.sectors.map((s) => s.id), ["DeFi", "DePIN", "DeAI"]);
  const s = JSON.stringify(data);
  for (const k of ["mindId", "mappingRef", "reviewers", "entitlement", "githubId", "@gmail.com", "configVersion"]) assert.ok(!s.includes(k), k);
  assert.throws(() => assertPublicSafe({ projects: [{ mindId: "x" }] }), /private field/);
  assert.throws(() => assertPublicSafe({ note: "contact blockchainlabs@gmail.com" }), /email/);
});

test("Public: no fabricated activity (records only from files; lastUpdated from records or authorisation, not now)", () => {
  const empty = tmp();
  const data = buildCampusData([gifter()], empty, "https://x");
  const p = data.projects[0]!;
  assert.equal(p.records.length, 0);
  assert.deepEqual(Object.values(p.progression), [0, 0, 0, 0, 0, 0]);
  assert.equal(p.lastUpdated, gifter().research.authorisedAt);
  assert.match(p.coordination, /no live chat/i);
});

test("Public: unapproved or unauthorised projects are not listed", () => {
  const g = gifter();
  g.publicListing.approved = false;
  assert.equal(buildCampusData([g], tmp(), "https://x").projects.length, 0);
});

test("Secrets: Builder key never appears in public records, campus assets or config", () => {
  const key = process.env["MINDS_BUILDER_API_KEY"] ?? "";
  const walk = (d: string): string[] => readdirSync(d, { withFileTypes: true }).flatMap((e) => (e.isDirectory() ? (e.name === "vendor" ? [] : walk(join(d, e.name))) : [join(d, e.name)]));
  for (const dir of ["records/public", "campus", "config", "docs"]) {
    let files: string[] = [];
    try { files = walk(join(REPO_ROOT, dir)); } catch { continue; }
    for (const f of files) assert.deepEqual(findSecretLeaks(readFileSync(f, "utf8"), [key]), [], f);
  }
  const fakeJwt = ["eyJ" + "hbGciOiJub25lIn0aa", "eyJ" + "zdWIiOiJ0ZXN0In0aa", "c2lnbmF0dXJlLWZha2U"].join("."); // synthetic, assembled at runtime
  assert.deepEqual(findSecretLeaks(fakeJwt), ["jwt-shaped-token"]);
});

type Wf = { on: unknown; permissions?: unknown; jobs: Record<string, { steps?: Array<Record<string, unknown>>; environment?: unknown; permissions?: unknown }> };
const wf = (n: string) => ({ text: readFileSync(join(REPO_ROOT, ".github/workflows", n), "utf8"), y: parse(readFileSync(join(REPO_ROOT, ".github/workflows", n), "utf8")) as Wf });

test("Workflows: every workflow file is valid YAML with jobs", () => {
  for (const f of readdirSync(join(REPO_ROOT, ".github/workflows")).filter((x) => x.endsWith(".yml"))) assert.ok(Object.keys(wf(f).y.jobs).length > 0, f);
});

test("Secrets: contributor-code workflow references no secrets and has a read-only token", () => {
  const { text, y } = wf("candidate-validation.yml");
  assert.ok(!/secrets\./.test(text), "no secrets.* in the untrusted workflow");
  assert.deepEqual(y.permissions, { contents: "read" });
  assert.ok(!/pull_request_target/.test(text));
  assert.ok(!JSON.stringify(y.jobs["attest"]).includes("candidate_sha }}\" , path"), "attest does not checkout");
  assert.ok(!(y.jobs["attest"]!.steps ?? []).some((s) => String(s["uses"] ?? "").startsWith("actions/checkout")), "attest never checks out candidate code");
});

test("Secrets: every privileged workflow uses a protected environment and never checks out untrusted refs", () => {
  for (const f of readdirSync(join(REPO_ROOT, ".github/workflows")).filter((x) => x.endsWith(".yml"))) {
    const { text, y } = wf(f);
    if (text.includes("pull_request_target")) assert.fail(`${f}: pull_request_target is not used in this pilot`);
    if (/secrets\.MINDS_BUILDER_API_KEY/.test(text)) {
      for (const [name, job] of Object.entries(y.jobs)) {
        if (!JSON.stringify(job).includes("MINDS_BUILDER_API_KEY")) continue;
        assert.ok(job.environment, `${f}/${name} must run in a protected environment`);
        for (const s of job.steps ?? []) if (String(s["uses"] ?? "").startsWith("actions/checkout")) {
          const w = (s["with"] ?? {}) as Record<string, unknown>;
          const controlRepo = w["repository"] === "${{ vars.SC_CONTROL_REPO }}";
          assert.ok(!w["ref"] && (!w["repository"] || controlRepo), `${f}/${name} checks out only this repository's default ref (or the private control repo as data)`);
        }
      }
    }
  }
});

test("Secrets: third-party actions are pinned to full commit SHAs in pilot workflows", () => {
  for (const f of readdirSync(join(REPO_ROOT, ".github/workflows")).filter((x) => x.endsWith(".yml"))) {
    if (f === "verify-forks.yml") continue; // pre-existing workflow, documented in docs/limitations.md
    for (const m of readFileSync(join(REPO_ROOT, ".github/workflows", f), "utf8").matchAll(/uses:\s*([^\s#]+)/g)) {
      const u = m[1]!;
      if (u.startsWith("./")) continue;
      assert.match(u, /@[0-9a-f]{40}$/, `${f}: ${u}`);
    }
  }
});
