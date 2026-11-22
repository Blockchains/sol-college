import fs from 'fs';
import { Keypair, PublicKey, SystemProgram } from '@solana/web3.js';
import { payer, conn, log, program, fund, expectFail, sendIx, BN } from './lib/labcommon.mjs';
const idl = JSON.parse(fs.readFileSync(new URL('../../dapps/static/sentinel-ai/idl.json', import.meta.url), 'utf8'));
const prog = program(idl);
const pid = new PublicKey(idl.address);
const pda = (...s) => PublicKey.findProgramAddressSync(s.map(x => typeof x === 'string' ? Buffer.from(x) : x), pid)[0];
const agent = Keypair.generate(), receiver = Keypair.generate(), other = Keypair.generate(), stranger = Keypair.generate();
await fund(agent.publicKey, 12_000_000); await fund(stranger.publicKey, 2_000_000);
try {
const profile = pda('agent_profile', agent.publicKey.toBuffer()), policy = pda('agent_policy', payer.publicKey.toBuffer());
log({ step: 'setup', program: pid.toBase58(), profile: profile.toBase58(), policy: policy.toBase58(), agent: agent.publicKey.toBase58(), receiver: receiver.publicKey.toBase58() });
let sig = await prog.methods.initializeAgentProfile().accountsPartial({ agentProfile: profile, agent: agent.publicKey, payer: payer.publicKey }).rpc();
log({ step: 'initialize_agent_profile', ok: true, sig, reputation: 50 });
sig = await prog.methods.setPolicy(new BN(5_000_000), receiver.publicKey, new BN(40), false, new BN(3_000_000), new BN(70)).accountsPartial({ agentPolicy: policy, owner: payer.publicKey }).rpc();
log({ step: 'set_policy', ok: true, sig, max_amount: 5_000_000, min_reputation: 40, high_value_threshold: 3_000_000, high_value_min_reputation: 70 });
const ag = program(idl, agent);
const submit = (amt, to = receiver.publicKey) => ag.methods.submitTransaction(new BN(amt)).accountsPartial({ agentProfile: profile, agentPolicy: policy, agent: agent.publicKey, receiver: to }).signers([agent]).rpc();
sig = await submit(1_000_000);
log({ step: 'submit_transaction', ok: true, sig, receiver_lamports: await conn.getBalance(receiver.publicKey), reputation: (await prog.account.agentProfile.fetch(profile)).reputationScore.toString() });
await expectFail('submit_over_max', () => submit(6_000_000));
await expectFail('submit_wrong_receiver', () => submit(1_000_000, other.publicKey));
await expectFail('submit_high_value_low_reputation', () => submit(4_000_000));
let p = await prog.account.agentProfile.fetch(profile);
log({ step: 'state_after_rejections', consecutive_failures: p.consecutiveFailures, total_transactions: p.totalTransactions.toString(), frozen: p.frozen, note: 'rejections revert, so failure counters do not persist' });
await expectFail('freeze_by_stranger', () => program(idl, stranger).methods.freezeAgent().accountsPartial({ agentProfile: profile, agent: agent.publicKey, owner: stranger.publicKey }).signers([stranger]).rpc());
sig = await prog.methods.freezeAgent().accountsPartial({ agentProfile: profile, agent: agent.publicKey, owner: payer.publicKey }).rpc();
log({ step: 'freeze_agent', ok: true, sig });
await expectFail('submit_while_frozen', () => submit(1_000_000));
sig = await prog.methods.unfreezeAgent().accountsPartial({ agentProfile: profile, agent: agent.publicKey, owner: payer.publicKey }).rpc();
log({ step: 'unfreeze_agent', ok: true, sig });
sig = await submit(2_000_000);
p = await prog.account.agentProfile.fetch(profile);
log({ step: 'submit_transaction_2', ok: true, sig, receiver_lamports: await conn.getBalance(receiver.publicKey), reputation: p.reputationScore.toString(), successful: p.successfulTransactions.toString() });
} finally {
  for (const k of [agent, receiver, stranger]) { const l = await conn.getBalance(k.publicKey); if (l > 0) await sendIx([SystemProgram.transfer({ fromPubkey: k.publicKey, toPubkey: payer.publicKey, lamports: l })], [payer, k]); }
  log({ step: 'cleanup_returned_lab_wallets' });
}
process.exit(0);
