/**
 * Devnet lab treasury. No spend caps and no recipient allowlist (owner instruction t688u).
 * Kept: devnet-only (RPC host + genesis hash asserted before signing), the key only from the protected
 * secret (never logged or returned), and an append-only ledger of every transaction.
 */
import { appendFileSync, existsSync, mkdirSync, readFileSync } from "node:fs";
import { dirname, join } from "node:path";
import { REPO_ROOT } from "../lib/paths.ts";

export const DEVNET_GENESIS = "EtWTRABZaYq6iMfeYKouRu166VU2xqa1wcaWoxPkrZBG";
export const DEVNET_HOST = "api.devnet.solana.com";

export interface TreasuryConfig { schema: "sc-treasury/1"; cluster: "devnet"; genesisHash: string; rpcUrl: string; address: string }
export interface TransferRequest { project: string; recipient: string; lamports: number; reason: string; taskId: string; requestedBy: string }
export interface LedgerEntry { schema: "sc-treasury-tx/1"; at: string; cluster: "devnet"; signature: string; from: string; recipient: string; lamports: number; sol: string; project: string; requestedBy: string; taskId: string; reason: string; runUrl: string | null }

export function loadTreasury(): TreasuryConfig {
  const c = JSON.parse(readFileSync(join(REPO_ROOT, "config", "treasury.json"), "utf8")) as TreasuryConfig;
  assertDevnetConfig(c);
  return c;
}

/** Throws unless the config can only ever reach devnet. */
export function assertDevnetConfig(c: Pick<TreasuryConfig, "cluster" | "genesisHash" | "rpcUrl">): void {
  if (c.cluster !== "devnet") throw new Error("treasury cluster must be devnet");
  if (c.genesisHash !== DEVNET_GENESIS) throw new Error("treasury genesis hash is not devnet's");
  const u = new URL(c.rpcUrl);
  if (u.protocol !== "https:" || u.hostname !== DEVNET_HOST) throw new Error(`treasury RPC must be https://${DEVNET_HOST}`);
}

const BASE58 = /^[1-9A-HJ-NP-Za-km-z]{32,44}$/;

/** Structural checks only (no caps, no allowlist by owner instruction). */
export function checkTransferRequest(r: TransferRequest, treasuryAddress: string): string[] {
  const e: string[] = [];
  if (!/^[a-z0-9-]+$/.test(r.project)) e.push("bad project slug");
  if (!BASE58.test(r.recipient)) e.push("recipient is not a base58 address");
  if (r.recipient === treasuryAddress) e.push("recipient is the treasury itself");
  if (!Number.isSafeInteger(r.lamports) || r.lamports <= 0) e.push("lamports must be a positive integer");
  if (typeof r.reason !== "string" || r.reason.trim().length < 4 || r.reason.length > 300) e.push("reason must be 4-300 characters");
  if (!/^[A-Za-z0-9._-]{1,80}$/.test(r.taskId)) e.push("bad taskId");
  if (!/^[A-Za-z0-9._ -]{1,80}$/.test(r.requestedBy)) e.push("bad requestedBy");
  return e;
}

export const LEDGER = join(REPO_ROOT, "records", "public", "treasury", "ledger.jsonl");

/** Append-only: entries are only ever appended; an existing signature is never rewritten. */
export function appendLedger(entry: LedgerEntry, file = LEDGER): void {
  mkdirSync(dirname(file), { recursive: true });
  if (existsSync(file) && readFileSync(file, "utf8").includes(`"signature":"${entry.signature}"`)) return;
  appendFileSync(file, JSON.stringify(entry) + "\n");
}

export function readLedger(file = LEDGER): LedgerEntry[] {
  return existsSync(file) ? readFileSync(file, "utf8").split("\n").filter(Boolean).map((l) => JSON.parse(l) as LedgerEntry) : [];
}
