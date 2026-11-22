import fs from 'fs';
import { Keypair, PublicKey, SystemProgram } from '@solana/web3.js';
import { payer, conn, log, program, fund, expectFail, sendIx, BN } from './lib/labcommon.mjs';
const idl = JSON.parse(fs.readFileSync(new URL('../../dapps/static/bountygraph/idl.json', import.meta.url), 'utf8'));
const prog = program(idl);
const pid = new PublicKey(idl.address);
const pda = (...s) => PublicKey.findProgramAddressSync(s.map(x => typeof x === 'string' ? Buffer.from(x) : x), pid)[0];
const authority = Keypair.generate(), agent = Keypair.generate(), stranger = Keypair.generate();
await fund(authority.publicKey, 40_000_000); await fund(agent.publicKey, 6_000_000); await fund(stranger.publicKey, 3_000_000);
try {
const ap = program(idl, authority), ag = program(idl, agent);
const graph = pda('graph', authority.publicKey.toBuffer());
const task = (id) => pda('task', graph.toBuffer(), new BN(id).toArrayLike(Buffer, 'le', 8));
const escrow = (t) => pda('escrow', t.toBuffer());
log({ step: 'setup', program: pid.toBase58(), graph: graph.toBase58(), authority: authority.publicKey.toBase58(), agent: agent.publicKey.toBase58() });
let sig = await ap.methods.initializeGraph({ maxDependenciesPerTask: 4 }).accountsPartial({ graph, authority: authority.publicKey }).signers([authority]).rpc();
log({ step: 'initialize_graph', ok: true, sig });
const mk = (id, deps, extra = []) => ap.methods.createTask({ taskId: new BN(id), rewardLamports: new BN(10_000_000), dependencies: deps.map(d => new BN(d)) }).accountsPartial({ graph, authority: authority.publicKey, creator: authority.publicKey, task: task(id) }).remainingAccounts(extra.map(pubkey => ({ pubkey, isSigner: false, isWritable: false }))).signers([authority]).rpc();
sig = await mk(1, []); log({ step: 'create_task_1', ok: true, sig, task: task(1).toBase58() });
sig = await mk(2, [1], [task(1)]); log({ step: 'create_task_2_depends_on_1', ok: true, sig, task: task(2).toBase58() });
await expectFail('create_task_self_dependency', () => mk(3, [3], [task(1)]));
await expectFail('create_task_missing_dep_accounts', () => mk(3, [1]));
const fundIt = (t, amt, signer = authority, p = ap) => p.methods.fundTask(new BN(amt)).accountsPartial({ task: t, escrow: escrow(t), funder: signer.publicKey }).signers([signer]).rpc();
await expectFail('fund_over_reward', () => fundIt(task(1), 20_000_000));
sig = await fundIt(task(1), 10_000_000); log({ step: 'fund_task_1', ok: true, sig, escrow: escrow(task(1)).toBase58() });
await expectFail('fund_twice', () => fundIt(task(1), 1_000_000));
sig = await fundIt(task(2), 10_000_000); log({ step: 'fund_task_2', ok: true, sig });
const rcpt = (t, who, deps = []) => program(idl, who).methods.submitReceipt({ workHash: Array(32).fill(3), uri: 'https://sol.college/dapps/bountygraph/receipt' }).accountsPartial({ task: t, receipt: pda('receipt', t.toBuffer(), who.publicKey.toBuffer()), agent: who.publicKey }).remainingAccounts(deps.map(pubkey => ({ pubkey, isSigner: false, isWritable: false }))).signers([who]).rpc();
await expectFail('submit_receipt_dependency_open', () => rcpt(task(2), agent, [task(1)]));
sig = await rcpt(task(1), agent); log({ step: 'submit_receipt_1', ok: true, sig });
await expectFail('claim_by_non_completer', () => program(idl, stranger).methods.claimReward().accountsPartial({ task: task(1), escrow: escrow(task(1)), agent: stranger.publicKey }).signers([stranger]).rpc());
let b = await conn.getBalance(agent.publicKey);
sig = await ag.methods.claimReward().accountsPartial({ task: task(1), escrow: escrow(task(1)), agent: agent.publicKey }).signers([agent]).rpc();
log({ step: 'claim_reward_1', ok: true, sig, agent_received: (await conn.getBalance(agent.publicKey)) - b });
sig = await rcpt(task(2), agent, [task(1)]); log({ step: 'submit_receipt_2_after_dep', ok: true, sig });
const disp = pda('dispute', task(2).toBuffer(), authority.publicKey.toBuffer());
sig = await ap.methods.disputeTask({ reason: 'output did not match spec' }).accountsPartial({ task: task(2), dispute: disp, initiator: authority.publicKey }).signers([authority]).rpc();
log({ step: 'dispute_task_2', ok: true, sig, dispute: disp.toBase58() });
await expectFail('claim_while_disputed', () => ag.methods.claimReward().accountsPartial({ task: task(2), escrow: escrow(task(2)), agent: agent.publicKey }).signers([agent]).rpc());
await expectFail('resolve_bad_split', () => ap.methods.resolveDispute({ creatorPct: 60, workerPct: 60 }).accountsPartial({ graph, authority: authority.publicKey, task: task(2), dispute: disp, escrow: escrow(task(2)), creator: authority.publicKey, worker: agent.publicKey }).signers([authority]).rpc());
b = await conn.getBalance(agent.publicKey);
sig = await ap.methods.resolveDispute({ creatorPct: 30, workerPct: 70 }).accountsPartial({ graph, authority: authority.publicKey, task: task(2), dispute: disp, escrow: escrow(task(2)), creator: authority.publicKey, worker: agent.publicKey }).signers([authority]).rpc();
log({ step: 'resolve_dispute_30_70', ok: true, sig, worker_received: (await conn.getBalance(agent.publicKey)) - b });
} finally {
for (const k of [agent, authority, stranger]) { const l = await conn.getBalance(k.publicKey); if (l > 0) await sendIx([SystemProgram.transfer({ fromPubkey: k.publicKey, toPubkey: payer.publicKey, lamports: l })], [payer, k]); }
log({ step: 'cleanup_returned_lab_wallets' });
}
process.exit(0);
