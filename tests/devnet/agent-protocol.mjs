import fs from 'fs';
import { Keypair, PublicKey, SystemProgram } from '@solana/web3.js';
import { payer, conn, log, program, fund, expectFail, sendIx, BN } from './lib/labcommon.mjs';
const idl = JSON.parse(fs.readFileSync(new URL('../../dapps/static/agent-protocol/idl.json', import.meta.url), 'utf8'));
const prog = program(idl);
const pid = new PublicKey(idl.address);
const pda = (...s) => PublicKey.findProgramAddressSync(s.map(x => typeof x === 'string' ? Buffer.from(x) : x), pid)[0];
const le = (n) => new BN(n).toArrayLike(Buffer, 'le', 8);
const A = Keypair.generate(), B = Keypair.generate(), arb = Keypair.generate(), stranger = Keypair.generate();
await fund(A.publicKey, 140_000_000); await fund(B.publicKey, 15_000_000); await fund(arb.publicKey, 3_000_000); await fund(stranger.publicKey, 10_000_000);
try {
const pa = program(idl, A), pb = program(idl, B), parb = program(idl, arb), ps = program(idl, stranger);
const profA = pda('agent', A.publicKey.toBuffer()), profB = pda('agent', B.publicKey.toBuffer());
log({ step: 'setup', program: pid.toBase58(), agent_a: A.publicKey.toBase58(), agent_b: B.publicKey.toBase58(), arbiter: arb.publicKey.toBase58(), profile_a: profA.toBase58() });
await expectFail('register_empty_name', () => pa.methods.registerAgent('', 'x', 1, new BN(1_000_000)).accountsPartial({ owner: A.publicKey, agentProfile: profA }).signers([A]).rpc());
let sig = await pa.methods.registerAgent('lab-auditor', 'Reviews Anchor code', 0b11, new BN(1_000_000)).accountsPartial({ owner: A.publicKey, agentProfile: profA }).signers([A]).rpc();
log({ step: 'register_agent_a', ok: true, sig, price_lamports: 1_000_000 });
sig = await pb.methods.registerAgent('lab-tester', 'Writes tests', 0b1000, new BN(500_000)).accountsPartial({ owner: B.publicKey, agentProfile: profB }).signers([B]).rpc();
log({ step: 'register_agent_b', ok: true, sig });
sig = await pa.methods.updateAgent(null, 'Reviews Anchor programs on devnet', null, null, null).accountsPartial({ owner: A.publicKey, agentProfile: profA }).signers([A]).rpc();
log({ step: 'update_agent', ok: true, sig });
const nonceOf = async (p) => (await prog.account.agentProfile.fetch(p)).jobNonce.toNumber();
const jobPda = (client, prof, n) => pda('job', client.toBuffer(), prof.toBuffer(), le(n));
const invoke = (amt, n, opts = {}) => (opts.p || prog).methods.invokeAgent(opts.desc ?? 'Audit the lab escrow', new BN(amt), null, new BN(n), null, opts.arbiter ?? null, opts.fee ?? 0)
  .accountsPartial({ client: (opts.client || payer).publicKey, agentProfile: profA, job: jobPda((opts.client || payer).publicKey, profA, n) }).signers(opts.client ? [opts.client] : []).rpc();
let n = await nonceOf(profA);
await expectFail('invoke_below_price', () => invoke(500_000, n));
await expectFail('invoke_wrong_nonce', () => invoke(3_000_000, n + 5));
await expectFail('invoke_self', () => invoke(3_000_000, n, { p: pa, client: A }));
await expectFail('invoke_arbiter_fee_too_high', () => invoke(3_000_000, n, { arbiter: arb.publicKey, fee: 3000 }));
const job1 = jobPda(payer.publicKey, profA, n);
sig = await invoke(3_000_000, n);
log({ step: 'invoke_agent_job1', ok: true, sig, job: job1.toBase58(), escrow: 3_000_000 });
// delegation
const nb = await nonceOf(profB), child = pda('job', A.publicKey.toBuffer(), profB.toBuffer(), le(nb));
await expectFail('delegate_by_stranger', () => ps.methods.delegateTask('Write tests', new BN(1_000_000), new BN(nb)).accountsPartial({ delegatingAgent: stranger.publicKey, parentJob: job1, subAgentProfile: profB, childJob: pda('job', stranger.publicKey.toBuffer(), profB.toBuffer(), le(nb)) }).signers([stranger]).rpc());
sig = await pa.methods.delegateTask('Write tests for the audit', new BN(1_000_000), new BN(nb)).accountsPartial({ delegatingAgent: A.publicKey, parentJob: job1, subAgentProfile: profB, childJob: child }).signers([A]).rpc();
log({ step: 'delegate_task', ok: true, sig, child_job: child.toBase58(), delegated: 1_000_000 });
await expectFail('complete_parent_with_open_child', () => pa.methods.updateJob('ipfs://audit').accountsPartial({ agent: A.publicKey, job: job1 }).signers([A]).rpc());
sig = await pb.methods.updateJob('ipfs://tests').accountsPartial({ agent: B.publicKey, job: child }).signers([B]).rpc();
log({ step: 'update_job_child', ok: true, sig });
let before = await conn.getBalance(B.publicKey);
sig = await pa.methods.releasePayment().accountsPartial({ client: A.publicKey, agent: B.publicKey, agentProfile: profB, job: child, parentJob: job1 }).signers([A]).rpc();
log({ step: 'release_payment_child', ok: true, sig, sub_agent_received: (await conn.getBalance(B.publicKey)) - before });
await expectFail('update_job_empty_uri', () => pa.methods.updateJob('').accountsPartial({ agent: A.publicKey, job: job1 }).signers([A]).rpc());
sig = await pa.methods.updateJob('ipfs://audit-report').accountsPartial({ agent: A.publicKey, job: job1 }).signers([A]).rpc();
log({ step: 'update_job_parent', ok: true, sig });
await expectFail('release_by_stranger', () => ps.methods.releasePayment().accountsPartial({ client: stranger.publicKey, agent: A.publicKey, agentProfile: profA, job: job1, parentJob: null }).signers([stranger]).rpc());
before = await conn.getBalance(A.publicKey);
sig = await prog.methods.releasePayment().accountsPartial({ client: payer.publicKey, agent: A.publicKey, agentProfile: profA, job: job1, parentJob: null }).rpc();
log({ step: 'release_payment_job1', ok: true, sig, agent_received: (await conn.getBalance(A.publicKey)) - before });
await expectFail('rate_out_of_range', () => prog.methods.rateAgent(6).accountsPartial({ client: payer.publicKey, job: job1, agentProfile: profA, rating: pda('rating', job1.toBuffer()) }).rpc());
sig = await prog.methods.rateAgent(5).accountsPartial({ client: payer.publicKey, job: job1, agentProfile: profA, rating: pda('rating', job1.toBuffer()) }).rpc();
log({ step: 'rate_agent', ok: true, sig, score: 5 });
sig = await prog.methods.closeJob().accountsPartial({ client: payer.publicKey, job: job1 }).rpc();
log({ step: 'close_job', ok: true, sig });
// arbiter dispute
n = await nonceOf(profA); const job2 = jobPda(payer.publicKey, profA, n);
sig = await invoke(2_000_000, n, { arbiter: arb.publicKey, fee: 500 });
log({ step: 'invoke_agent_job2_with_arbiter', ok: true, sig, arbiter_fee_bps: 500 });
sig = await pa.methods.updateJob('ipfs://disputed').accountsPartial({ agent: A.publicKey, job: job2 }).signers([A]).rpc();
log({ step: 'update_job_2', ok: true, sig });
await expectFail('dispute_by_stranger', () => ps.methods.raiseDispute().accountsPartial({ disputant: stranger.publicKey, job: job2 }).signers([stranger]).rpc());
sig = await prog.methods.raiseDispute().accountsPartial({ disputant: payer.publicKey, job: job2 }).rpc();
log({ step: 'raise_dispute', ok: true, sig });
await expectFail('resolve_by_non_arbiter', () => ps.methods.resolveDisputeByArbiter(true).accountsPartial({ arbiter: stranger.publicKey, client: payer.publicKey, agent: A.publicKey, agentProfile: profA, job: job2, stakeVault: null }).signers([stranger]).rpc());
const bA = await conn.getBalance(A.publicKey), bR = await conn.getBalance(arb.publicKey);
sig = await parb.methods.resolveDisputeByArbiter(true).accountsPartial({ arbiter: arb.publicKey, client: payer.publicKey, agent: A.publicKey, agentProfile: profA, job: job2, stakeVault: null }).signers([arb]).rpc();
log({ step: 'resolve_dispute_by_arbiter_favor_agent', ok: true, sig, agent_received: (await conn.getBalance(A.publicKey)) - bA, arbiter_received: (await conn.getBalance(arb.publicKey)) - bR });
// reject + cancel
n = await nonceOf(profA); const job3 = jobPda(payer.publicKey, profA, n);
sig = await invoke(1_500_000, n); log({ step: 'invoke_agent_job3', ok: true, sig });
before = await conn.getBalance(payer.publicKey);
sig = await pa.methods.rejectJob().accountsPartial({ agent: A.publicKey, client: payer.publicKey, job: job3 }).signers([A]).rpc();
log({ step: 'reject_job_refund', ok: true, sig, job_closed: !(await conn.getAccountInfo(job3)) });
n = await nonceOf(profA); const job4 = jobPda(payer.publicKey, profA, n);
sig = await invoke(1_200_000, n); log({ step: 'invoke_agent_job4', ok: true, sig });
await expectFail('cancel_by_stranger', () => ps.methods.cancelJob().accountsPartial({ client: stranger.publicKey, job: job4 }).signers([stranger]).rpc());
sig = await prog.methods.cancelJob().accountsPartial({ client: payer.publicKey, job: job4 }).rpc();
log({ step: 'cancel_job_refund', ok: true, sig, job_closed: !(await conn.getAccountInfo(job4)) });
// stake
const vault = pda('stake', profA.toBuffer());
await expectFail('stake_below_minimum', () => pa.methods.stakeAgent(new BN(1_000_000)).accountsPartial({ owner: A.publicKey, agentProfile: profA, stakeVault: vault }).signers([A]).rpc());
sig = await pa.methods.stakeAgent(new BN(100_000_000)).accountsPartial({ owner: A.publicKey, agentProfile: profA, stakeVault: vault }).signers([A]).rpc();
log({ step: 'stake_agent', ok: true, sig, staked: 100_000_000 });
await expectFail('unstake_more_than_staked', () => pa.methods.unstakeAgent(new BN(200_000_000)).accountsPartial({ owner: A.publicKey, agentProfile: profA, stakeVault: vault }).signers([A]).rpc());
sig = await pa.methods.unstakeAgent(new BN(100_000_000)).accountsPartial({ owner: A.publicKey, agentProfile: profA, stakeVault: vault }).signers([A]).rpc();
const p = await prog.account.agentProfile.fetch(profA);
log({ step: 'unstake_agent', ok: true, sig, jobs_completed: p.jobsCompleted.toString(), rating_sum: p.ratingSum.toString(), stake_amount: p.stakeAmount.toString() });
} finally {
  for (const k of [A, B, arb, stranger]) { const l = await conn.getBalance(k.publicKey); if (l > 0) await sendIx([SystemProgram.transfer({ fromPubkey: k.publicKey, toPubkey: payer.publicKey, lamports: l })], [payer, k]).catch(e => log({ step: 'cleanup_error', key: k.publicKey.toBase58(), lamports: l, error: String(e).slice(0, 120) })); }
  log({ step: 'cleanup_returned_lab_wallets' });
}
process.exit(0);
