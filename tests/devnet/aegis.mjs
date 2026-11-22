import fs from 'fs';
import crypto from 'crypto';
import { Keypair, PublicKey, SystemProgram, Transaction, TransactionInstruction, SYSVAR_RENT_PUBKEY } from '@solana/web3.js';
import { payer, conn, log, program, ata, ensureAta, mintTo, tokenBal, fund, sendIx, expectFail, BN, MINT, TOKEN_PROGRAM_ID, Wallet } from './lib/labcommon.mjs';
const idl = JSON.parse(fs.readFileSync(new URL('../../dapps/static/aegis/idl.json', import.meta.url),'utf8'));
const prog = program(idl); const pid = new PublicKey(idl.address);
const S = SystemProgram.programId; const me = payer.publicKey;
const JUP = new PublicKey('JUP6LkbZbjS1jKKwapdHNy74zcZ3tLUZoi5QNyVTaV4');
const FEED = 'ef0d8b6fda2ceba41da15d4095d1da392a0d2f8ed0c6c7bc0f4cfac8c280b56d'; // SOL/USD
const TREASURY = new PublicKey('En7DGt8B4LtuH2cwBMRofhdhgAJv18uGaDZDqCthS3QU');
const pda = (...s) => PublicKey.findProgramAddressSync(s.map(x => typeof x === 'string' ? Buffer.from(x) : x), pid)[0];
const protocol = pda('protocol'), protocolVault = pda('protocol_vault');
const agent = Keypair.generate(); const aprog = program(idl, agent);
const reputation = pda('reputation', agent.publicKey.toBuffer());
const policyCfg = pda('policy', me.toBuffer(), agent.publicKey.toBuffer());
const vault = pda('vault', MINT.toBuffer());
const intent = crypto.randomBytes(16); const intentArr = Array.from(intent);
const escrow = pda('escrow', intent, me.toBuffer());
const verification = pda('verification', intent, agent.publicKey.toBuffer());
log({ step:'setup', program: pid.toBase58(), protocol: protocol.toBase58(), agent: agent.publicKey.toBase58(), escrow: escrow.toBase58(), vault: vault.toBase58() });
if (!(await conn.getAccountInfo(protocol))) log({ step:'initialize', sig: await prog.methods.initialize(TREASURY, new BN(2_000_000_000), 5).accounts({ admin: me, protocol, protocolVault, systemProgram: S }).rpc() });
await fund(agent.publicKey, 2_100_000_000);
await expectFail('register_agent_below_min_stake', () => aprog.methods.registerAgent(new BN(1_000_000_000)).accounts({ agent: agent.publicKey, reputation, protocol, protocolVault, systemProgram: S }).rpc());
log({ step:'register_agent', sig: await aprog.methods.registerAgent(new BN(2_000_000_000)).accounts({ agent: agent.publicKey, reputation, protocol, protocolVault, systemProgram: S }).rpc(), stake: 2_000_000_000 });
log({ step:'configure_policy', sig: await prog.methods.configurePolicy(agent.publicKey, new BN(10_000_000), new BN(50_000_000), [JUP], 0, 0, new BN(0)).accounts({ owner: me, policyConfig: policyCfg, systemProgram: S }).rpc() });
const ownerAta = await ensureAta(me);
await mintTo(ownerAta, 1_000_000);
// second owner token account as destination
const dest = Keypair.generate();
const rent = await conn.getMinimumBalanceForRentExemption(165);
const initData = Buffer.concat([Buffer.from([18]), me.toBuffer()]);
await sendIx([SystemProgram.createAccount({ fromPubkey: me, newAccountPubkey: dest.publicKey, lamports: rent, space: 165, programId: TOKEN_PROGRAM_ID }),
  new TransactionInstruction({ programId: TOKEN_PROGRAM_ID, keys: [{ pubkey: dest.publicKey, isSigner:false, isWritable:true }, { pubkey: MINT, isSigner:false, isWritable:false }], data: initData })], [payer, dest]);
const now = Math.floor(Date.now()/1000);
const lockAcc = { owner: me, escrow, tokenMint: MINT, vault, ownerTokenAccount: ownerAta, agentReputation: reputation, protocol, agent: agent.publicKey, tokenProgram: TOKEN_PROGRAM_ID, systemProgram: S, rent: SYSVAR_RENT_PUBKEY };
log({ step:'lock_escrow', sig: await prog.methods.lockEscrow(intentArr, new BN(1_000_000), new BN(now + 3600)).accounts(lockAcc).rpc(), amount: 1_000_000, vault_balance: String(await tokenBal(vault)) });

// (an earlier attempt using the Hermes HTTP API got 401; the on-chain push-oracle account is used instead)
// Pyth push-oracle SOL/USD price account on devnet (shard 1), owned by the Pyth receiver program
const PRICE = new PublicKey('6bWEn5B8eJCRAek5acd3R7d4Sx3e7JWvt84srqqfYgt');
async function readPrice() {
  const d = (await conn.getAccountInfo(PRICE)).data; let o = 8+32; const tag = d[o]; o += 1; if (tag == 0) o += 1; o += 32;
  const price = d.readBigInt64LE(o); o += 16; const expo = d.readInt32LE(o); o += 4; const pt = Number(d.readBigInt64LE(o));
  return { price, expo, pt, age: Math.floor(Date.now()/1000) - pt };
}
let pr = await readPrice(); const t0 = Date.now();
while (pr.age > 120 && Date.now() - t0 < 420_000) { await new Promise(r => setTimeout(r, 5000)); pr = await readPrice(); }
log({ step:'pyth_price', account: PRICE.toBase58(), price: String(pr.price), expo: pr.expo, publish_time: pr.pt, age_s: pr.age });
const adj = 6 + pr.expo; const claimed = adj >= 0 ? pr.price * 10n ** BigInt(adj) : pr.price / 10n ** BigInt(-adj);
function u64(v){ const b=Buffer.alloc(8); b.writeBigUInt64LE(BigInt(v)); return b; }
function i64(v){ const b=Buffer.alloc(8); b.writeBigInt64LE(BigInt(v)); return b; }
function mkClaim(intentBuf, price) {
  const reasoning = Buffer.from('Sol.College lab: buy SOL at Pyth SOL/USD'); const rl = Buffer.alloc(4); rl.writeUInt32LE(reasoning.length);
  const t = Math.floor(Date.now()/1000);
  return Buffer.concat([intentBuf, Buffer.from([0]), JUP.toBuffer(), Buffer.from(FEED,'hex'), u64(price), u64(1), i64(t+3600), i64(t), u64(1), rl, reasoning, Buffer.from([0])]);
}
const sha = (b) => Array.from(crypto.createHash('sha256').update(b).digest());
const vAcc = (esc, ver) => ({ agent: agent.publicKey, escrow: esc, vault, ownerTokenAccount: ownerAta, ownerDestTokenAccount: dest.publicKey, reputation, protocol, protocolVault, policyConfig: policyCfg, verification: ver, pythPriceUpdate: PRICE, jupiterProgram: JUP, tokenProgram: TOKEN_PROGRAM_ID, systemProgram: S });
const claim = mkClaim(intent, claimed);
await expectFail('commit_zero_hash', () => aprog.methods.commit(intentArr, Array(32).fill(0)).accounts({ agent: agent.publicKey, escrow, agentReputation: reputation }).rpc());
log({ step:'commit', sig: await aprog.methods.commit(intentArr, sha(claim)).accounts({ agent: agent.publicKey, escrow, agentReputation: reputation }).rpc(), claimed_price_6dp: String(claimed) });
const destBefore = await tokenBal(dest.publicKey);
const sv = await aprog.methods.verifyAndExecute(intentArr, claim).accounts(vAcc(escrow, verification)).rpc();
const v = await prog.account.verificationRecord.fetch(verification); const e = await prog.account.escrowAccount.fetch(escrow);
log({ step:'verify_and_execute', sig: sv, decision: v.decision, hash_matched: v.hashMatched, oracle_matched: v.oracleMatched, policy_passed: v.policyPassed, oracle_price: String(v.oraclePrice), deviation_bps: v.priceDeviationBps, escrow_status: Object.keys(e.status)[0], dest_received: String((await tokenBal(dest.publicKey)) - destBefore), vault_balance: String(await tokenBal(vault)) });
// rejection path: commit one claim, reveal a different one -> refund + slash
const intent2 = crypto.randomBytes(16); const i2 = Array.from(intent2);
const escrow2 = pda('escrow', intent2, me.toBuffer()); const ver2 = pda('verification', intent2, agent.publicKey.toBuffer());
await mintTo(ownerAta, 500_000);
log({ step:'lock_escrow_2', sig: await prog.methods.lockEscrow(i2, new BN(500_000), new BN(Math.floor(Date.now()/1000) + 3600)).accounts({ ...lockAcc, escrow: escrow2 }).rpc() });
log({ step:'commit_2', sig: await aprog.methods.commit(i2, sha(mkClaim(intent2, claimed))).accounts({ agent: agent.publicKey, escrow: escrow2, agentReputation: reputation }).rpc() });
const ownerBefore = await tokenBal(ownerAta);
const sv2 = await aprog.methods.verifyAndExecute(i2, mkClaim(intent2, claimed * 2n)).accounts(vAcc(escrow2, ver2)).rpc();
const v2 = await prog.account.verificationRecord.fetch(ver2); const e2 = await prog.account.escrowAccount.fetch(escrow2); const r2 = await prog.account.reputationAccount.fetch(reputation);
log({ step:'verify_and_execute_mismatched_claim', sig: sv2, decision: v2.decision, hash_matched: v2.hashMatched, failure_code: v2.failureCode, escrow_status: Object.keys(e2.status)[0], owner_refunded: String((await tokenBal(ownerAta)) - ownerBefore), agent_stake_after: String(r2.stake), agent_score: r2.score });
process.exit(0);
