// Sol.College lab flow for AgentsPay (devnet). Uses the upstream SDK from the lab tree.
import fs from "node:fs";
import crypto from "node:crypto";
import { Connection, Keypair, PublicKey, SystemProgram, Transaction, sendAndConfirmTransaction } from "@solana/web3.js";
import { getOrCreateAssociatedTokenAccount, mintTo, getAccount, getAssociatedTokenAddressSync } from "@solana/spl-token";
import { AgentsPayClient, gatewaySimulatedMeasurement, TeeType, signVoucher, signReceipt, nextTranscriptHash, ZERO_HASH } from "@agentspay/sdk";
const LOG = process.env.PROOF_LOG;
const log = (o: any) => { const s = JSON.stringify(o, (_, v) => typeof v === "bigint" ? v.toString() : v); console.log(s); if (LOG) fs.appendFileSync(LOG, s + "\n"); };
const yaml = fs.readFileSync(process.env.HOME + "/.config/solana/cli/config.yml", "utf8");
const conn = new Connection(yaml.match(/json_rpc_url:\s*(\S+)/)![1], "confirmed");
const admin = Keypair.fromSecretKey(Uint8Array.from(JSON.parse(fs.readFileSync(process.env.HOME + "/.config/solana/id.json", "utf8"))));
const programId = new PublicKey("8BXi7XdZ6gRqGbGBCUEZN3TMV629uuHTUcEYtdqW6th");
const MINT = new PublicKey("BJMSdujxakjx7qypwfaFCnbkMTNPEYVWTTqnR9eJRL4D");
const TREASURY = new PublicKey("En7DGt8B4LtuH2cwBMRofhdhgAJv18uGaDZDqCthS3QU");
const verifier = Keypair.generate(), operator = Keypair.generate(), payer = Keypair.generate(), enclave = Keypair.generate();
async function fund(k: PublicKey, lamports: number) { await sendAndConfirmTransaction(conn, new Transaction().add(SystemProgram.transfer({ fromPubkey: admin.publicKey, toPubkey: k, lamports })), [admin]); }
await fund(verifier.publicKey, 50_000_000); await fund(operator.publicKey, 200_000_000); await fund(payer.publicKey, 200_000_000);
const A = AgentsPayClient.fromKeypair(conn, admin, { programId });
const V = AgentsPayClient.fromKeypair(conn, verifier, { programId });
const O = AgentsPayClient.fromKeypair(conn, operator, { programId });
const P = AgentsPayClient.fromKeypair(conn, payer, { programId });
log({ step: "setup", program: programId.toBase58(), config: A.pdas.config().toBase58(), verifier: verifier.publicKey.toBase58(), operator: operator.publicKey.toBase58(), payer: payer.publicKey.toBase58(), enclave: enclave.publicKey.toBase58() });
const wrap = async (step: string, f: () => Promise<any>, extra: any = {}) => { const r = await f(); const sig = typeof r === "string" ? r : r?.signature; log({ step, sig, ...extra }); return r; };
if (!(await conn.getAccountInfo(A.pdas.config())))
  await wrap("initialize", () => A.initialize({ treasury: TREASURY, verifiers: [verifier.publicKey], verifierThreshold: 1, protocolFeeBps: 100, maxAttestationTtl: 7 * 24 * 3600, allowSimulatedTee: true }));
const measurement = gatewaySimulatedMeasurement({ version: "0.1.0", backend: "echo", model: "echo-1" });
await wrap("approve_measurement", () => A.approveMeasurement({ teeType: TeeType.Simulated, value: measurement, modelHash: new Uint8Array(32), label: "agentspay-gateway 0.1.0 echo:echo-1" }));
const reg = await wrap("register_provider", () => O.registerProvider({ payout: operator.publicKey, endpoint: "https://sol.college/dapps/agentspay/" }));
const sub = await wrap("submit_attestation", () => O.submitAttestation({ enclaveKey: enclave.publicKey, encryptionKey: new Uint8Array(32).fill(5), teeType: TeeType.Simulated, measurement, evidenceHash: crypto.createHash("sha256").update("sol-college-sim-evidence").digest(), evidenceUri: "https://sol.college/", requestedTtl: 24 * 3600 }));
// negative: a non-verifier cannot approve
try { await P.approveAttestation(sub.attestation); log({ step: "approve_attestation_by_non_verifier", unexpected_success: true }); } catch (e: any) { log({ step: "approve_attestation_by_non_verifier", rejected: true, reason: e?.error?.errorCode?.code ?? String(e.message).slice(0, 160) }); }
await wrap("approve_attestation", () => V.approveAttestation(sub.attestation));
const payerAta = await getOrCreateAssociatedTokenAccount(conn, admin, MINT, payer.publicKey);
await mintTo(conn, admin, MINT, payerAta.address, admin, 2_000_000n);
const open = await wrap("open_session", () => P.openSession({ provider: reg.provider, mint: MINT, deposit: 1_000_000n, pricePerUnit: 1_000n, authorizedSigner: payer.publicKey }), {});
const session: PublicKey = open.session;
log({ step: "session", session: session.toBase58(), escrow_balance: (await getAccount(conn, getAssociatedTokenAddressSync(MINT, session, true))).amount });
const now = BigInt(Math.floor(Date.now() / 1000));
const t1 = nextTranscriptHash(ZERO_HASH, "prompt: hello", "echo: hello");
const voucher = signVoucher({ session, cumulativeAmount: 600_000n, expiresAt: 0n }, payer);
const receipt = signReceipt({ session, cumulativeUnits: 500n, transcriptHash: t1, issuedAt: now }, enclave);
// negative: receipt signed by a key that is not the attested enclave
const fakeReceipt = signReceipt({ session, cumulativeUnits: 500n, transcriptHash: t1, issuedAt: now }, Keypair.generate());
try { await O.settle(session, voucher, fakeReceipt); log({ step: "settle_with_forged_receipt", unexpected_success: true }); } catch (e: any) { const m = (e?.logs || []).find((l: string) => /Error/.test(l)) || String(e.message).slice(0, 200); log({ step: "settle_with_forged_receipt", rejected: true, reason: m }); }
const payoutAta = getAssociatedTokenAddressSync(MINT, operator.publicKey); const trAta = getAssociatedTokenAddressSync(MINT, TREASURY);
const bal = async (a: PublicKey) => { try { return (await getAccount(conn, a)).amount; } catch { return 0n; } };
const tr0 = await bal(trAta);
const s1 = await O.settle(session, voucher, receipt);
log({ step: "settle", sig: s1, metered: "500 units x 1000 = 500000", payout_received: await bal(payoutAta), treasury_fee: (await bal(trAta)) - tr0 });
const pr0 = await bal(payerAta.address);
const c = await O.settleAndClose(session);
log({ step: "close_session", sig: c, payer_refund: (await bal(payerAta.address)) - pr0, session_closed: !(await conn.getAccountInfo(session)) });
process.exit(0);
