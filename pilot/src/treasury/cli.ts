/**
 * treasury transfer --project P --recipient ADDR --lamports N --reason TEXT --task ID --requested-by NAME
 * Trusted runtime only (environment lab-treasury). Key from LAB_TREASURY_KEYPAIR; never printed.
 * Devnet asserted twice: config (host + genesis) and the live cluster's genesis hash before signing.
 */
import { parseArgs } from "node:util";
import { Connection, Keypair, LAMPORTS_PER_SOL, PublicKey, SystemProgram, Transaction, sendAndConfirmTransaction } from "@solana/web3.js";
import { appendLedger, assertDevnetConfig, checkTransferRequest, DEVNET_GENESIS, loadTreasury, readLedger, type LedgerEntry } from "./treasury.ts";

const { positionals, values } = parseArgs({ allowPositionals: true, options: { project: { type: "string" }, recipient: { type: "string" }, lamports: { type: "string" }, reason: { type: "string" }, task: { type: "string" }, "requested-by": { type: "string" }, "private-ledger": { type: "string" } } });

async function main(): Promise<void> {
  const cfg = loadTreasury();
  const conn = new Connection(cfg.rpcUrl, "confirmed");
  if (positionals[0] === "balance") {
    const live = await conn.getGenesisHash();
    console.log(JSON.stringify({ address: cfg.address, cluster: live === DEVNET_GENESIS ? "devnet" : "NOT-DEVNET", lamports: await conn.getBalance(new PublicKey(cfg.address)), ledgerEntries: readLedger().length }));
    return;
  }
  if (positionals[0] !== "transfer") throw new Error("usage: treasury balance|transfer");
  const req = { project: values.project ?? "", recipient: values.recipient ?? "", lamports: Number(values.lamports), reason: values.reason ?? "", taskId: values.task ?? "", requestedBy: values["requested-by"] ?? "" };
  const errs = checkTransferRequest(req, cfg.address);
  if (errs.length) throw new Error(`request rejected: ${errs.join("; ")}`);
  assertDevnetConfig(cfg);
  const live = await conn.getGenesisHash();
  if (live !== DEVNET_GENESIS) throw new Error("connected cluster is not devnet; refusing to sign");
  const raw = process.env["LAB_TREASURY_KEYPAIR"];
  if (!raw) throw new Error("LAB_TREASURY_KEYPAIR is not set");
  const kp = Keypair.fromSecretKey(Uint8Array.from(JSON.parse(raw) as number[]));
  if (kp.publicKey.toBase58() !== cfg.address) throw new Error("treasury key does not match config/treasury.json address");
  const tx = new Transaction().add(SystemProgram.transfer({ fromPubkey: kp.publicKey, toPubkey: new PublicKey(req.recipient), lamports: req.lamports }));
  const signature = await sendAndConfirmTransaction(conn, tx, [kp], { commitment: "confirmed" });
  const runUrl = process.env["GITHUB_RUN_ID"] ? `https://github.com/${process.env["GITHUB_REPOSITORY"]}/actions/runs/${process.env["GITHUB_RUN_ID"]}` : null;
  const entry: LedgerEntry = { schema: "sc-treasury-tx/1", at: new Date().toISOString(), cluster: "devnet", signature, from: cfg.address, recipient: req.recipient, lamports: req.lamports, sol: (req.lamports / LAMPORTS_PER_SOL).toString(), project: req.project, requestedBy: req.requestedBy, taskId: req.taskId, reason: req.reason.replace(/\s+/g, " ").slice(0, 300), runUrl };
  appendLedger(entry);
  if (values["private-ledger"]) appendLedger(entry, values["private-ledger"]);
  console.log(JSON.stringify({ ok: true, signature, explorer: `https://explorer.solana.com/tx/${signature}?cluster=devnet`, lamports: req.lamports, recipient: req.recipient, project: req.project }));
}
main().catch((e: unknown) => { console.error(`treasury: ${(e as Error).message}`); process.exit(1); });
