// Barn (OpenGrants) on devnet: sponsor and dev profiles, grant program, project, grant, milestone, payout in SOL.
// Usage (from the fork's protocol/ts dir, which has @coral-xyz/anchor 0.30):
//   node barn.mjs <idl.json> <rpc> <payer-keypair.json>
// The keypair file only pays: A (sponsor), B (dev) and C (an unrelated wallet) are fresh keys it funds with a little devnet SOL.
import fs from 'fs';
import anchor from '@coral-xyz/anchor';
const { AnchorProvider, Program, Wallet, BN } = anchor;
import { Connection, Keypair, PublicKey, SystemProgram, LAMPORTS_PER_SOL, Transaction, sendAndConfirmTransaction } from '@solana/web3.js';

const [idlPath, rpc, kpPath] = process.argv.slice(2);
const idl = JSON.parse(fs.readFileSync(idlPath, 'utf8'));
const PID = new PublicKey(idl.address);
// The public devnet RPC rate-limits hard (429). Retry those responses with backoff; resending the same signed tx is idempotent.
const rlFetch = async (url, opts) => { for (let i = 0; ; i++) { const r = await fetch(url, opts); if (r.status !== 429 || i >= 12) return r; await new Promise(z => setTimeout(z, 1500 * (i + 1))); } };
const conn = new Connection(rpc, { commitment: 'confirmed', fetch: rlFetch, disableRetryOnRateLimit: true });
const sleep = (ms) => new Promise(r => setTimeout(r, ms));
// This RPC has no websocket, so confirm by polling signature status instead of subscribing.
conn.confirmTransaction = async (arg) => { const sig = typeof arg === 'string' ? arg : arg.signature;
  for (let i = 0; i < 90; i++) { const st = (await conn.getSignatureStatuses([sig])).value[0];
    if (st && (st.confirmationStatus === 'confirmed' || st.confirmationStatus === 'finalized')) {
      if (st.err) throw Object.assign(new Error('tx failed ' + JSON.stringify(st.err)), { logs: (await conn.getTransaction(sig, { maxSupportedTransactionVersion: 0, commitment: 'confirmed' }))?.meta?.logMessages });
      return { context: { slot: st.slot }, value: { err: st.err } }; }
    await sleep(1000); } throw new Error('confirm timeout ' + sig); };
// The program allows one profile per wallet (authority PDA = [wallet]), so each run uses fresh role wallets funded by the payer.
const PAYER = Keypair.fromSecretKey(Uint8Array.from(JSON.parse(fs.readFileSync(kpPath, 'utf8'))));
const A = Keypair.generate();
const B = Keypair.generate(), C = Keypair.generate();
const NATIVE = new PublicKey('So11111111111111111111111111111111111111112');
const TOKEN = new PublicKey('TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA');
const ATA_PROG = new PublicKey('ATokenGPvbdGVxr1b2hvZbsiqW5xWH25efTNsLJA8knL');
const log = (o) => console.log(JSON.stringify({ t: new Date().toISOString(), ...o }));
const err = (e) => String(e.error?.errorCode?.code || e.logs?.find(l => /Error|failed|already in use/.test(l)) || e.message).split('\n')[0].slice(0, 200);
const prog = (kp) => new Program(idl, new AnchorProvider(conn, new Wallet(kp), { commitment: 'confirmed' }));
const P = prog(A);
const pda = (...s) => PublicKey.findProgramAddressSync(s, PID)[0];
const u32 = (n) => { const b = Buffer.alloc(4); b.writeUInt32LE(n); return b; };
const authorityOf = (k) => pda(k.toBuffer());
const profileOf = (seed) => pda(Buffer.from('profile'), Buffer.from(seed));
async function retry(f, n = 6) { for (let i = 0; ; i++) { try { return await f(); } catch (e) { if (i >= n || !/429|Too Many|fetch failed|blockhash|timed out|ECONNRESET/i.test(String(e.message || e))) throw e; await sleep(3000 * (i + 1)); } } }
async function expectFail(step, f) { try { const sig = await f(); log({ step, ok: false, unexpected_success: sig }); } catch (e) { log({ step, ok: true, rejected: err(e) }); } }

async function fund(to, sol) {
  const before = await retry(() => conn.getBalance(to));
  if (before >= sol * LAMPORTS_PER_SOL) return log({ step: 'fund ' + to.toBase58().slice(0, 4), skipped: 'already funded' });
  const sig = await retry(() => sendAndConfirmTransaction(conn, new Transaction().add(SystemProgram.transfer({ fromPubkey: PAYER.publicKey, toPubkey: to, lamports: Math.round(sol * LAMPORTS_PER_SOL) })), [PAYER]));
  log({ step: 'fund ' + to.toBase58().slice(0, 4), sol, sig });
}

const tag = Date.now().toString(36);
const seedA = 'sponsor-' + tag, seedB = 'dev-' + tag;
const profA = profileOf(seedA), profB = profileOf(seedB);
const base = 'https://sol.college/dapps/barn/meta/';

log({ step: 'start', program: PID.toBase58(), sponsor: A.publicKey.toBase58(), dev: B.publicKey.toBase58(), other: C.publicKey.toBase58(), payer: PAYER.publicKey.toBase58(), payerBalance: (await conn.getBalance(PAYER.publicKey)) / LAMPORTS_PER_SOL });
await fund(A.publicKey, 0.06); await fund(B.publicKey, 0.03); await fund(C.publicKey, 0.01);
const create = async (kp, seed, uri) => retry(() => prog(kp).methods.createUser(seed, uri).accountsPartial({ signer: kp.publicKey, authority: authorityOf(kp.publicKey), profile: profileOf(seed), systemProgram: SystemProgram.programId }).rpc());
log({ step: 'create_user sponsor A', sig: await create(A, seedA, base + 'sponsor.json'), profile: profA.toBase58() });
log({ step: 'create_user dev B', sig: await create(B, seedB, base + 'dev.json'), profile: profB.toBase58() });
await expectFail('create_user with a seed that is already taken', () => create(C, seedB, base + 'dev.json'));

const gp0 = pda(Buffer.from('grant-program'), profA.toBuffer(), u32(0));
const addGP = (kp, prof) => prog(kp).methods.addGrantProgram(base + 'program.json').accountsPartial({ signer: kp.publicKey, authority: authorityOf(kp.publicKey), profile: prof, grantProgram: gp0, systemProgram: SystemProgram.programId }).rpc();
await expectFail('add_grant_program before the profile is a sponsor', () => addGP(A, profA));
// approve_sponsor only needs *some* signer as "admin": here C, a wallet with no role at all, approves A.
log({ step: 'approve_sponsor A, signed by unrelated wallet C as admin', sig: await retry(() => prog(C).methods.approveSponsor().accountsPartial({ admin: C.publicKey, signer: A.publicKey, authority: authorityOf(A.publicKey), profile: profA }).rpc()) });
log({ step: 'add_grant_program by sponsor A', sig: await retry(() => addGP(A, profA)), grantProgram: gp0.toBase58() });

const proj0 = pda(Buffer.from('project'), profB.toBuffer(), u32(0));
await expectFail('add_project by the sponsor (devs only)', () => prog(A).methods.addProject(base + 'project.json').accountsPartial({ signer: A.publicKey, authority: authorityOf(A.publicKey), profile: profA, project: pda(Buffer.from('project'), profA.toBuffer(), u32(1)), systemProgram: SystemProgram.programId }).rpc());
log({ step: 'add_project by dev B', sig: await retry(() => prog(B).methods.addProject(base + 'project.json').accountsPartial({ signer: B.publicKey, authority: authorityOf(B.publicKey), profile: profB, project: proj0, systemProgram: SystemProgram.programId }).rpc()), project: proj0.toBase58() });

const grant0 = pda(Buffer.from('grant'), gp0.toBuffer(), u32(0));
const award = (kp, prof) => prog(kp).methods.awardGrant(base + 'grant.json', new BN(0.02 * LAMPORTS_PER_SOL)).accountsPartial({ signer: kp.publicKey, authority: authorityOf(kp.publicKey), profile: prof, project: proj0, grantProgram: gp0, grant: grant0, paymentMint: NATIVE, systemProgram: SystemProgram.programId }).rpc();
await expectFail('award_grant by the dev', () => award(B, profB));
log({ step: 'award_grant 0.02 SOL (native mint) by sponsor A', sig: await retry(() => award(A, profA)), grant: grant0.toBase58() });
await expectFail('award a second grant to the same project', () => prog(A).methods.awardGrant(base + 'grant.json', new BN(1)).accountsPartial({ signer: A.publicKey, authority: authorityOf(A.publicKey), profile: profA, project: proj0, grantProgram: gp0, grant: pda(Buffer.from('grant'), gp0.toBuffer(), u32(1)), paymentMint: NATIVE, systemProgram: SystemProgram.programId }).rpc());

const ms = (i) => pda(Buffer.from('grant-milestone'), grant0.toBuffer(), u32(i));
const addMs = (i, sol) => retry(() => prog(B).methods.addGrantMilestone(base + 'milestone.json', new BN(sol * LAMPORTS_PER_SOL)).accountsPartial({ signer: B.publicKey, authority: authorityOf(B.publicKey), profile: profB, project: proj0, grant: grant0, grantMilestone: ms(i), systemProgram: SystemProgram.programId }).rpc());
log({ step: 'add_grant_milestone #0 (0.015 SOL) by dev B', sig: await addMs(0, 0.015) });
log({ step: 'add_grant_milestone #1 (0.01 SOL, over what is left of the grant) by dev B', sig: await addMs(1, 0.01) });
const upd = (kp, prof, method, i) => prog(kp).methods[method]().accountsPartial({ signer: kp.publicKey, authority: authorityOf(kp.publicKey), profile: prof, project: proj0, grant: grant0, grantProgram: gp0, grantMilestone: ms(i) }).rpc();
const settle = (i) => prog(A).methods.settleGrantMilestone().accountsPartial({ signer: A.publicKey, to: B.publicKey, authority: authorityOf(A.publicKey), profile: profA, grant: grant0, grantMilestone: ms(i), signerTokenAccount: A.publicKey, paymentMint: NATIVE, tokenProgram: TOKEN, associatedTokenProgram: ATA_PROG, systemProgram: SystemProgram.programId }).rpc();
await expectFail('accept milestone #0 by the dev', () => upd(B, profB, 'acceptGrantMilestone', 0));
await expectFail('settle milestone #0 before it is accepted', () => settle(0));
log({ step: 'review_grant_milestone #0 (dev submits it)', sig: await retry(() => upd(B, profB, 'reviewGrantMilestone', 0)) });
log({ step: 'accept_grant_milestone #0 by sponsor A', sig: await retry(() => upd(A, profA, 'acceptGrantMilestone', 0)) });
const bBefore = await conn.getBalance(B.publicKey);
log({ step: 'settle_grant_milestone #0: sponsor A pays dev B 0.015 SOL', sig: await retry(() => settle(0)) });
log({ step: 'dev B balance change (SOL)', delta: ((await conn.getBalance(B.publicKey)) - bBefore) / LAMPORTS_PER_SOL });
await expectFail('settle milestone #0 a second time', () => settle(0));
log({ step: 'review_grant_milestone #1 (dev submits it)', sig: await retry(() => upd(B, profB, 'reviewGrantMilestone', 1)) });
log({ step: 'revise_grant_milestone #1 by sponsor A (sends it back to in-progress)', sig: await retry(() => upd(A, profA, 'reviseGrantMilestone', 1)) });
log({ step: 'review #1 again', sig: await retry(() => upd(B, profB, 'reviewGrantMilestone', 1)) });
log({ step: 'accept #1 by sponsor A', sig: await retry(() => upd(A, profA, 'acceptGrantMilestone', 1)) });
await expectFail('settle milestone #1: 0.015 + 0.01 is more than the 0.02 SOL grant', () => settle(1));
log({ step: 'add_grant_milestone #2 (0.001 SOL) by dev B', sig: await addMs(2, 0.001) });
log({ step: 'review #2', sig: await retry(() => upd(B, profB, 'reviewGrantMilestone', 2)) });
log({ step: 'reject_grant_milestone #2 by sponsor A', sig: await retry(() => upd(A, profA, 'rejectGrantMilestone', 2)) });
await expectFail('revise milestone #2 after it was rejected (rejected is final)', () => upd(B, profB, 'reviseGrantMilestone', 2));
const g = await P.account.grant.fetch(grant0);
log({ step: 'grant state', approved: g.approvedAmount.toNumber() / LAMPORTS_PER_SOL, paidOut: g.paidOut.toNumber() / LAMPORTS_PER_SOL, milestones: g.count });
