import { test } from "node:test";
import assert from "node:assert/strict";
import { checkPatch, labBranch, patchPolicyFor } from "../../src/lab/patch.ts";
import { assertDevnetConfig, appendLedger, checkTransferRequest, readLedger, DEVNET_GENESIS } from "../../src/treasury/treasury.ts";
import { validateTaskResponse, type TaskSpec } from "../../src/minds/task.ts";
import { mkdtempSync } from "node:fs";
import { tmpdir } from "node:os";
import { join } from "node:path";

const diff = (path: string, add = "+    let ok = true;") => `diff --git a/${path} b/${path}\n--- a/${path}\n+++ b/${path}\n@@ -1,2 +1,3 @@\n fn main() {\n${add}\n }\n`;
const pol = patchPolicyFor(".");

test("Lab patch gate: program source passes; workflow, CI, toolchain, manifests and keys are refused", () => {
  assert.equal(checkPatch(diff("programs/cipher-valut/src/lib.rs"), pol).ok, true);
  for (const bad of [".github/workflows/x.yml", "Anchor.toml", "package.json", ".vscode/tasks.json", "keys/id.json", "programs/x/build.rs", "rust-toolchain.toml", "../etc/passwd", "README.md"])
    assert.equal(checkPatch(diff(bad), pol).ok, false, bad);
  assert.equal(checkPatch(diff("programs/a/src/lib.rs", "+let url = \"https://api.mainnet-beta.solana.com\";"), pol).ok, false);
  assert.equal(checkPatch("not a diff", pol).ok, false);
  const big = `diff --git a/programs/a/src/lib.rs b/programs/a/src/lib.rs\n--- a/programs/a/src/lib.rs\n+++ b/programs/a/src/lib.rs\n@@ -1 +1,500 @@\n` + Array.from({ length: 500 }, (_, i) => `+// ${i}`).join("\n");
  assert.equal(checkPatch(big, pol).ok, false);
  assert.ok(patchPolicyFor("contract").allowedPrefixes.includes("contract/programs/"));
});

test("Lab branch is always sc-lab/<project>/<task>", () => {
  assert.equal(labBranch("ciphervault", "patch-ciphervault-6-2026111517"), "sc-lab/ciphervault/patch-ciphervault-6-2026111517");
  assert.throws(() => labBranch("Main", ""));
});

test("Treasury: devnet only; no caps or allowlist, but structural checks remain", () => {
  assertDevnetConfig({ cluster: "devnet", genesisHash: DEVNET_GENESIS, rpcUrl: "https://api.devnet.solana.com" });
  assert.throws(() => assertDevnetConfig({ cluster: "devnet", genesisHash: DEVNET_GENESIS, rpcUrl: "https://api.mainnet-beta.solana.com" }));
  assert.throws(() => assertDevnetConfig({ cluster: "devnet", genesisHash: "5eykt4UsFv8P8NJdTREpY1vzqKqZKvdpKuc147dw2N9d", rpcUrl: "https://api.devnet.solana.com" }));
  assert.throws(() => assertDevnetConfig({ cluster: "mainnet-beta" as "devnet", genesisHash: DEVNET_GENESIS, rpcUrl: "https://api.devnet.solana.com" }));
  const ok = { project: "ciphervault", recipient: "BP1uwSaTHXvgN8sPQJgaor6iBoT3KYjnZNnkvJr71zDv", lamports: 50_000_000_000, reason: "fund multisig test", taskId: "patch-x-1", requestedBy: "SolCollege-CipherVault-CTO" };
  assert.deepEqual(checkTransferRequest(ok, "En7DGt8B4LtuH2cwBMRofhdhgAJv18uGaDZDqCthS3QU"), []); // 50 SOL: no cap
  assert.ok(checkTransferRequest({ ...ok, lamports: 0 }, "x").length > 0);
  assert.ok(checkTransferRequest({ ...ok, recipient: "not-an-address" }, "x").length > 0);
  assert.ok(checkTransferRequest({ ...ok, recipient: "En7DGt8B4LtuH2cwBMRofhdhgAJv18uGaDZDqCthS3QU" }, "En7DGt8B4LtuH2cwBMRofhdhgAJv18uGaDZDqCthS3QU").length > 0);
});

test("Treasury ledger is append-only and never duplicates a signature", () => {
  const f = join(mkdtempSync(join(tmpdir(), "led-")), "l.jsonl");
  const e = { schema: "sc-treasury-tx/1" as const, at: "t", cluster: "devnet" as const, signature: "sig1", from: "a", recipient: "b", lamports: 1, sol: "0.000000001", project: "p", requestedBy: "m", taskId: "t", reason: "r", runUrl: null };
  appendLedger(e, f); appendLedger(e, f); appendLedger({ ...e, signature: "sig2" }, f);
  assert.deepEqual(readLedger(f).map((x) => x.signature), ["sig1", "sig2"]);
});

test("Mind actions are schema-checked in task responses", () => {
  const spec: TaskSpec = { taskId: "patch-a-000001", project: "a", kind: "experiment-patch", instructions: "", sources: [], evidence: [], context: {} };
  const base = { protocol: "sc-task-response/1", taskId: spec.taskId, project: "a", summary: "s", facts: [], hypotheses: [], proposals: [], evidenceRefs: [], uncertainties: [] };
  const msg = (o: unknown) => ({ messageText: "```json\n" + JSON.stringify(o) + "\n```" }) as never;
  assert.equal(validateTaskResponse(spec, msg({ ...base, actions: [{ type: "patch", title: "t", rationale: "r", patch: "diff" }] })).ok, true);
  assert.equal(validateTaskResponse(spec, msg({ ...base, actions: [{ type: "devnet-transfer", recipient: "x", lamports: 1.5, reason: "r" }] })).ok, false);
  assert.equal(validateTaskResponse(spec, msg({ ...base, actions: [{ type: "mainnet-transfer" }] })).ok, false);
});
