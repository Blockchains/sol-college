import fs from 'fs';
import { Keypair, PublicKey, SystemProgram } from '@solana/web3.js';
import { payer, conn, log, program, fund, expectFail, sendIx, BN } from './lib/labcommon.mjs';
const ridl = JSON.parse(fs.readFileSync(new URL('../../dapps/static/chai-sol/registry_idl.json', import.meta.url), 'utf8'));
const eidl = JSON.parse(fs.readFileSync(new URL('../../dapps/static/chai-sol/idl.json', import.meta.url), 'utf8'));
const reg = program(ridl), esc = program(eidl);
const rid = new PublicKey(ridl.address), eid = new PublicKey(eidl.address);
const pda = (p, ...s) => PublicKey.findProgramAddressSync(s.map(x => typeof x === 'string' ? Buffer.from(x) : x), p)[0];
const agent = Keypair.generate(), stranger = Keypair.generate(), freeWallet = Keypair.generate();
await fund(agent.publicKey, 30_000_000); await fund(stranger.publicKey, 5_000_000);
try {
const config = pda(rid, 'config'), oracleCfg = pda(eid, 'oracle_config');
const agentAcc = pda(rid, 'agent', agent.publicKey.toBuffer());
log({ step: 'setup', registry: rid.toBase58(), escrow: eid.toBase58(), agent: agent.publicKey.toBase58(), config: config.toBase58(), oracle_config: oracleCfg.toBase58() });
let sig;
if (!(await conn.getAccountInfo(config))) { sig = await reg.methods.initialize().accountsPartial({ registryConfig: config, admin: payer.publicKey }).rpc(); log({ step: 'registry_initialize', ok: true, sig }); }
const ra = program(ridl, agent);
await expectFail('register_name_too_long', () => ra.methods.registerAgent('x'.repeat(51), 'gpt', 'https://github.com/x').accountsPartial({ agentAccount: agentAcc, signer: agent.publicKey }).signers([agent]).rpc());
sig = await ra.methods.registerAgent('lab-agent', 'llama-3', 'https://github.com/Blockchains/chai-sol').accountsPartial({ agentAccount: agentAcc, signer: agent.publicKey }).signers([agent]).rpc();
log({ step: 'register_agent', ok: true, sig, agent_account: agentAcc.toBase58() });
sig = await ra.methods.updateAgent('https://sol.college/dapps/chai-sol/').accountsPartial({ agentAccount: agentAcc, signer: agent.publicKey }).signers([agent]).rpc();
log({ step: 'update_agent', ok: true, sig });
await expectFail('verify_by_stranger', () => program(ridl, stranger).methods.verifyAgent(90, 'rust').accountsPartial({ agentAccount: agentAcc, registryConfig: config, admin: stranger.publicKey }).signers([stranger]).rpc());
await expectFail('verify_score_over_100', () => reg.methods.verifyAgent(101, 'rust').accountsPartial({ agentAccount: agentAcc, registryConfig: config, admin: payer.publicKey }).rpc());
sig = await reg.methods.verifyAgent(88, 'anchor,rust').accountsPartial({ agentAccount: agentAcc, registryConfig: config, admin: payer.publicKey }).rpc();
const a = await reg.account.agentAccount.fetch(agentAcc);
log({ step: 'verify_agent', ok: true, sig, reputation: a.reputation, verified: a.verified });
const freeAcc = pda(rid, 'agent', freeWallet.publicKey.toBuffer());
sig = await reg.methods.registerAgentFree(freeWallet.publicKey, 'sponsored', 'claude', 'https://github.com/x').accountsPartial({ agentAccount: freeAcc, registryConfig: config, admin: payer.publicKey }).rpc();
log({ step: 'register_agent_free', ok: true, sig });
sig = await reg.methods.closeAgent().accountsPartial({ agentAccount: freeAcc, registryConfig: config, admin: payer.publicKey }).rpc();
log({ step: 'close_agent', ok: true, sig });
// escrow
if (!(await conn.getAccountInfo(oracleCfg))) { sig = await esc.methods.initializeOracle(payer.publicKey).accountsPartial({ oracleConfig: oracleCfg, admin: payer.publicKey }).rpc(); log({ step: 'initialize_oracle', ok: true, sig }); }
const ea = program(eidl, agent), es = program(eidl, stranger);
const tid = (n) => `lab-${Date.now() % 1e7}-${n}`;
const t1id = tid(1), t1 = pda(eid, 'task', payer.publicKey.toBuffer(), t1id);
sig = await esc.methods.initializeTask(t1id, new BN(3_000_000), 'Summarise a devnet log').accountsPartial({ poster: payer.publicKey, taskEscrow: t1 }).rpc();
log({ step: 'initialize_task_1', ok: true, sig, task: t1.toBase58(), bounty: 3_000_000 });
await expectFail('assign_by_stranger', () => es.methods.assignAgent(stranger.publicKey).accountsPartial({ poster: stranger.publicKey, taskEscrow: t1 }).signers([stranger]).rpc());
sig = await esc.methods.assignAgent(agent.publicKey).accountsPartial({ poster: payer.publicKey, taskEscrow: t1 }).rpc();
log({ step: 'assign_agent', ok: true, sig });
await expectFail('submit_by_unassigned', () => es.methods.submitResult('https://x', Array(32).fill(1)).accountsPartial({ worker: stranger.publicKey, taskEscrow: t1, taskResult: pda(eid, 'result', t1.toBuffer()) }).signers([stranger]).rpc());
const r1 = pda(eid, 'result', t1.toBuffer());
sig = await ea.methods.submitResult('https://sol.college/r/1', Array(32).fill(7)).accountsPartial({ worker: agent.publicKey, taskEscrow: t1, taskResult: r1 }).signers([agent]).rpc();
log({ step: 'submit_result', ok: true, sig });
await expectFail('reclaim_before_48h', () => ea.methods.reclaimTimeout().accountsPartial({ worker: agent.publicKey, taskEscrow: t1, taskResult: r1 }).signers([agent]).rpc());
await expectFail('verify_by_non_oracle', () => es.methods.verifyResult(true).accountsPartial({ oracle: stranger.publicKey, oracleConfig: oracleCfg, taskEscrow: t1, taskResult: r1, worker: agent.publicKey }).signers([stranger]).rpc());
let before = await conn.getBalance(agent.publicKey);
sig = await esc.methods.verifyResult(true).accountsPartial({ oracle: payer.publicKey, oracleConfig: oracleCfg, taskEscrow: t1, taskResult: r1, worker: agent.publicKey }).rpc();
log({ step: 'verify_result_pass', ok: true, sig, agent_received: (await conn.getBalance(agent.publicKey)) - before });
await expectFail('verify_twice', () => esc.methods.verifyResult(true).accountsPartial({ oracle: payer.publicKey, oracleConfig: oracleCfg, taskEscrow: t1, taskResult: r1, worker: agent.publicKey }).rpc());
// task 2: failed verification then cancel/refund
const t2id = tid(2), t2 = pda(eid, 'task', payer.publicKey.toBuffer(), t2id), r2 = pda(eid, 'result', t2.toBuffer());
sig = await esc.methods.initializeTask(t2id, new BN(2_000_000), 'Second task').accountsPartial({ poster: payer.publicKey, taskEscrow: t2 }).rpc();
log({ step: 'initialize_task_2', ok: true, sig });
sig = await ea.methods.submitResult('https://sol.college/r/2', Array(32).fill(9)).accountsPartial({ worker: agent.publicKey, taskEscrow: t2, taskResult: r2 }).signers([agent]).rpc();
log({ step: 'submit_result_2', ok: true, sig });
sig = await esc.methods.verifyResult(false).accountsPartial({ oracle: payer.publicKey, oracleConfig: oracleCfg, taskEscrow: t2, taskResult: r2, worker: agent.publicKey }).rpc();
log({ step: 'verify_result_fail_reopens', ok: true, sig, status: Object.keys((await esc.account.taskEscrow.fetch(t2)).status)[0] });
await expectFail('cancel_by_stranger', () => es.methods.cancelTask().accountsPartial({ poster: stranger.publicKey, taskEscrow: t2 }).signers([stranger]).rpc());
sig = await esc.methods.cancelTask().accountsPartial({ poster: payer.publicKey, taskEscrow: t2 }).rpc();
log({ step: 'cancel_task_refund', ok: true, sig, escrow_closed: !(await conn.getAccountInfo(t2)) });
// task 3: direct completion by poster
const t3id = tid(3), t3 = pda(eid, 'task', payer.publicKey.toBuffer(), t3id);
sig = await esc.methods.initializeTask(t3id, new BN(1_000_000), 'Direct pay').accountsPartial({ poster: payer.publicKey, taskEscrow: t3 }).rpc();
log({ step: 'initialize_task_3', ok: true, sig });
sig = await esc.methods.assignAgent(agent.publicKey).accountsPartial({ poster: payer.publicKey, taskEscrow: t3 }).rpc();
log({ step: 'assign_agent_3', ok: true, sig });
await expectFail('complete_to_wrong_agent', () => esc.methods.completeTask().accountsPartial({ poster: payer.publicKey, agent: stranger.publicKey, taskEscrow: t3 }).rpc());
before = await conn.getBalance(agent.publicKey);
sig = await esc.methods.completeTask().accountsPartial({ poster: payer.publicKey, agent: agent.publicKey, taskEscrow: t3 }).rpc();
log({ step: 'complete_task', ok: true, sig, agent_received: (await conn.getBalance(agent.publicKey)) - before });
await expectFail('complete_twice', () => esc.methods.completeTask().accountsPartial({ poster: payer.publicKey, agent: agent.publicKey, taskEscrow: t3 }).rpc());
} finally {
  for (const k of [agent, stranger]) { const l = await conn.getBalance(k.publicKey); if (l > 0) await sendIx([SystemProgram.transfer({ fromPubkey: k.publicKey, toPubkey: payer.publicKey, lamports: l })], [payer, k]); }
  log({ step: 'cleanup_returned_lab_wallets' });
}
process.exit(0);
