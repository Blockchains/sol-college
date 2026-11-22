import fs from 'fs';
import { Keypair, PublicKey, SystemProgram } from '@solana/web3.js';
import { payer, conn, log, program, fund, expectFail, sendIx, BN } from './lib/labcommon.mjs';
const idl = JSON.parse(fs.readFileSync(new URL('../../dapps/static/verifiagent/idl.json', import.meta.url), 'utf8'));
const pid = new PublicKey(idl.address);
const pda = (...s) => PublicKey.findProgramAddressSync(s.map(x => typeof x === 'string' ? Buffer.from(x) : x), pid)[0];
const le = (n) => new BN(n).toArrayLike(Buffer, 'le', 8);
const w = Keypair.generate(), stranger = Keypair.generate();
await fund(w.publicKey, 12_000_000); await fund(stranger.publicKey, 6_000_000);
try {
const pw = program(idl, w), ps = program(idl, stranger), prog = program(idl);
const agent = pda('agent', w.publicKey.toBuffer());
log({ step: 'setup', program: pid.toBase58(), agent_wallet: w.publicKey.toBase58(), agent: agent.toBase58() });
let sig = await pw.methods.initializeAgent().accountsPartial({ agent, wallet: w.publicKey }).signers([w]).rpc();
let a = await prog.account.agent.fetch(agent);
log({ step: 'initialize_agent', ok: true, sig, trust_level: Object.keys(a.trustLevel)[0] });
await expectFail('initialize_agent_twice', () => pw.methods.initializeAgent().accountsPartial({ agent, wallet: w.publicKey }).signers([w]).rpc());
const hash = (n) => Array.from({ length: 32 }, (_, i) => (i * 7 + n) & 255);
const traces = [];
for (const [i, t] of [[0, 'swap_quote'], [1, 'llm_inference']].entries()) {
  const tr = pda('trace', w.publicKey.toBuffer(), le(i));
  sig = await pw.methods.logActivity(hash(i), t[1]).accountsPartial({ agent, trace: tr, wallet: w.publicKey }).signers([w]).rpc();
  a = await prog.account.agent.fetch(agent); traces.push(tr);
  log({ step: `log_activity_${i}`, ok: true, sig, action_type: t[1], trace: tr.toBase58(), total_activities: a.totalActivities.toString(), trust_level: Object.keys(a.trustLevel)[0] });
}
await expectFail('log_activity_other_agent', () => ps.methods.logActivity(hash(9), 'spoof').accountsPartial({ agent, trace: pda('trace', stranger.publicKey.toBuffer(), le(2)), wallet: stranger.publicKey }).signers([stranger]).rpc());
await expectFail('log_activity_type_too_long', () => pw.methods.logActivity(hash(3), 'x'.repeat(120)).accountsPartial({ agent, trace: pda('trace', w.publicKey.toBuffer(), le(2)), wallet: w.publicKey }).signers([w]).rpc());
sig = await prog.methods.verifyTrace().accountsPartial({ trace: traces[1] }).rpc();
const t = await prog.account.activityTrace.fetch(traces[1]);
log({ step: 'verify_trace', ok: true, sig, index: t.index.toString(), action_type: t.actionType, verified: t.verified });
await expectFail('verify_trace_on_agent_account', () => prog.methods.verifyTrace().accountsPartial({ trace: agent }).rpc());
} finally {
  for (const k of [w, stranger]) { const l = await conn.getBalance(k.publicKey); if (l > 0) await sendIx([SystemProgram.transfer({ fromPubkey: k.publicKey, toPubkey: payer.publicKey, lamports: l })], [payer, k]); }
  log({ step: 'cleanup_returned_lab_wallets' });
}
process.exit(0);
