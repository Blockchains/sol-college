// Devnet end-to-end flow for the OrbOracle-Solana fork (stake-weighted oracle), mirroring the app's own calls in
// src/components/createOracle.tsx and src/app/[oracleId]/InteractionClient.tsx (Anchor 0.31 resolves the PDAs:
// oracle = ["oracle", authority, weight mint], user = ["user", oracle, user], vault = oracle's associated token account).
// initialize -> fund -> deposit_tokens -> (deposit lock) -> submit_value -> vote -> withdraw_tokens, plus rejection cases.
// Usage (from the fork root): node orboracle-solana.mjs <idl.json> <rpc> <authority.json>
import fs from 'fs';
import anchor from '@coral-xyz/anchor';
import { Connection, Keypair, PublicKey, SystemProgram, Transaction, LAMPORTS_PER_SOL, sendAndConfirmTransaction } from '@solana/web3.js';
import { createMint, getOrCreateAssociatedTokenAccount, mintTo, getAccount } from '@solana/spl-token';
const { AnchorProvider, Program, Wallet, BN } = anchor;
const [idlPath, rpc, kpPath] = process.argv.slice(2);
const A = Keypair.fromSecretKey(Uint8Array.from(JSON.parse(fs.readFileSync(kpPath, 'utf8'))));
const conn = new Connection(rpc, 'confirmed');
conn.confirmTransaction = async (arg) => { const sig = typeof arg === 'string' ? arg : arg.signature;
  for (let i = 0; i < 90; i++) { const st = (await conn.getSignatureStatuses([sig])).value[0];
    if (st && (st.confirmationStatus === 'confirmed' || st.confirmationStatus === 'finalized')) {
      if (st.err) throw new Error('tx failed ' + JSON.stringify(st.err)); return { context: { slot: st.slot }, value: { err: st.err } }; }
    await new Promise(r => setTimeout(r, 1000)); } throw new Error('confirm timeout ' + sig); };
const idl = JSON.parse(fs.readFileSync(idlPath, 'utf8'));
const prog = (kp) => new Program(idl, new AnchorProvider(conn, new Wallet(kp), { commitment: 'confirmed' }));
const log = (o) => console.log(JSON.stringify(o)); const sleep = (ms) => new Promise(r => setTimeout(r, ms));
const err = (e) => String(e.error?.errorCode?.code || e.logs?.find(l => /Error|failed/.test(l)) || e.message).split('\n')[0].slice(0, 200);
const expectFail = async (label, fn) => { try { await fn(); log({ step: label, ok: false, error: 'UNEXPECTED SUCCESS' }); } catch (e) { log({ step: label, expectedFailure: true, error: err(e) }); } };
const P = prog(A), pid = P.programId;
const B = Keypair.generate();
log({ step: 'fund B (fees)', sig: await sendAndConfirmTransaction(conn, new Transaction().add(SystemProgram.transfer({ fromPubkey: A.publicKey, toPubkey: B.publicKey, lamports: 0.03 * LAMPORTS_PER_SOL })), [A], { commitment: 'confirmed' }) });
const mint = await createMint(conn, A, A.publicKey, null, 6);
const aAta = await getOrCreateAssociatedTokenAccount(conn, A, mint, A.publicKey);
const bAta = await getOrCreateAssociatedTokenAccount(conn, A, mint, B.publicKey);
await mintTo(conn, A, mint, aAta.address, A, 1000e6); await mintTo(conn, A, mint, bAta.address, A, 500e6);
const [oracle] = PublicKey.findProgramAddressSync([Buffer.from('oracle'), A.publicKey.toBuffer(), mint.toBuffer()], pid);
const userPda = (u) => PublicKey.findProgramAddressSync([Buffer.from('user'), oracle.toBuffer(), u.toBuffer()], pid)[0];
log({ step: 'setup', program: pid.toBase58(), authority: A.publicKey.toBase58(), B: B.publicKey.toBase58(), weightMint: mint.toBase58(), oracle: oracle.toBase58() });
const params = (o) => ({ name: 'SOL/USD (sol.college test)', description: 'Devnet test feed', rewardBps: new BN(1000), halfLifeSeconds: new BN(3600), quorum: new BN(2000), depositLockingPeriod: new BN(8), withdrawalLockingPeriod: new BN(8), alpha: new BN(1), ...o });
const initAcc = { payer: A.publicKey, authority: A.publicKey, weightMint: mint };
await expectFail('initialize_empty_name', () => P.methods.initialize(params({ name: '' })).accounts(initAcc).rpc());
await expectFail('initialize_reward_over_100pct', () => P.methods.initialize(params({ rewardBps: new BN(100001) })).accounts(initAcc).rpc());
const s1 = await P.methods.initialize(params({})).accounts(initAcc).rpc(); log({ step: 'initialize (8s deposit/withdraw locks)', ok: true, sig: s1 });
const s2 = await P.methods.fund(new BN(0.05 * LAMPORTS_PER_SOL)).accounts({ funder: A.publicKey, oracleState: oracle }).rpc();
log({ step: 'fund reward pool 0.05 SOL', ok: true, sig: s2, oracleLamports: await conn.getBalance(oracle) });
await expectFail('fund_zero', () => P.methods.fund(new BN(0)).accounts({ funder: A.publicKey, oracleState: oracle }).rpc());
const dep = (kp, amt) => prog(kp).methods.depositTokens(new BN(amt)).accounts({ user: kp.publicKey, weightMint: mint, oracleState: oracle }).rpc();
const s3 = await dep(A, 300e6); log({ step: 'deposit_tokens A 300', ok: true, sig: s3 });
const s4 = await dep(B, 100e6); log({ step: 'deposit_tokens B 100', ok: true, sig: s4 });
await expectFail('submit_value_while_tokens_locked', () => P.methods.submitValue(new BN(150_000_000)).accounts({ user: A.publicKey, oracleState: oracle }).rpc());
await sleep(12000);
const s5 = await P.methods.submitValue(new BN(150_000_000)).accounts({ user: A.publicKey, oracleState: oracle }).rpc();
let st = await P.account.oracleState.fetch(oracle); log({ step: 'submit_value A 150.000000', ok: true, sig: s5, aggregated: st.aggregatedValue.toString(), latest: st.latestValue.toString() });
const s6 = await prog(B).methods.submitValue(new BN(160_000_000)).accounts({ user: B.publicKey, oracleState: oracle }).rpc();
st = await P.account.oracleState.fetch(oracle); log({ step: 'submit_value B 160.000000', ok: true, sig: s6, aggregated: st.aggregatedValue.toString(), latest: st.latestValue.toString(), history: st.priceHistory.length, oracleLamports: await conn.getBalance(oracle) });
const s7 = await prog(B).methods.voteBlacklist(A.publicKey).accounts({ user: B.publicKey, oracleState: oracle }).rpc();
st = await P.account.oracleState.fetch(oracle); log({ step: 'vote_blacklist A by B', ok: true, sig: s7, targets: st.targets.map(t => JSON.parse(JSON.stringify(t))) });
await expectFail('withdraw_more_than_unlocked', () => prog(B).methods.withdrawTokens(new BN(101e6)).accounts({ user: B.publicKey, weightMint: mint, oracleState: oracle }).rpc());
await sleep(10000);
const before = Number((await getAccount(conn, bAta.address)).amount);
const s8 = await prog(B).methods.withdrawTokens(new BN(40e6)).accounts({ user: B.publicKey, weightMint: mint, oracleState: oracle }).rpc();
log({ step: 'withdraw_tokens B 40', ok: true, sig: s8, Breceived: (Number((await getAccount(conn, bAta.address)).amount) - before) / 1e6 });
st = await P.account.oracleState.fetch(oracle); log({ step: 'final state', totalDeposited: st.totalDepositedTokens.toNumber() / 1e6, aggregated: st.aggregatedValue.toString(), history: st.priceHistory.length });
await expectFail('submit_value_by_blacklisted_A', () => P.methods.submitValue(new BN(999_000_000)).accounts({ user: A.publicKey, oracleState: oracle }).rpc());
