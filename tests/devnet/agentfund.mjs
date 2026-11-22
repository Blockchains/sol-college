import fs from 'fs';
import { Keypair, PublicKey, SystemProgram } from '@solana/web3.js';
import { payer, conn, log, program, fund, expectFail, sendIx, BN } from './lib/labcommon.mjs';
const eidl = JSON.parse(fs.readFileSync(new URL('../../dapps/static/agentfund/idl.json', import.meta.url), 'utf8'));
const ridl = JSON.parse(fs.readFileSync(new URL('../../dapps/static/agentfund/registry_idl.json', import.meta.url), 'utf8'));
const qidl = JSON.parse(fs.readFileSync(new URL('../../dapps/static/agentfund/reputation_idl.json', import.meta.url), 'utf8'));
const eid = new PublicKey(eidl.address), rid = new PublicKey(ridl.address), qid = new PublicKey(qidl.address);
const pda = (p, ...s) => PublicKey.findProgramAddressSync(s.map(x => typeof x === 'string' ? Buffer.from(x) : x), p)[0];
const le = (n) => new BN(n).toArrayLike(Buffer, 'le', 4);
const SOL = new PublicKey('So11111111111111111111111111111111111111112');
const C = Keypair.generate(), X = Keypair.generate(), Y = Keypair.generate(), S = Keypair.generate();
await fund(C.publicKey, 20_000_000); await fund(X.publicKey, 12_000_000); await fund(Y.publicKey, 4_000_000); await fund(S.publicKey, 4_000_000);
const sleep = (ms) => new Promise(r => setTimeout(r, ms));
try {
const reg = program(ridl), rc = program(ridl, C), rs = program(ridl, S);
const rep = program(qidl), qs = program(qidl, S);
const esc = program(eidl), ec = program(eidl, C), ex = program(eidl, X), ey = program(eidl, Y), es = program(eidl, S);
const rconfig = pda(rid, 'config'), qconfig = pda(qid, 'config'), agent = pda(rid, 'agent', C.publicKey.toBuffer());
log({ step: 'setup', registry: rid.toBase58(), escrow: eid.toBase58(), reputation: qid.toBase58(), creator: C.publicKey.toBase58(), backer_x: X.publicKey.toBase58(), backer_y: Y.publicKey.toBase58() });
let sig;
if (!(await conn.getAccountInfo(rconfig))) { sig = await reg.methods.initialize(payer.publicKey).accountsPartial({ payer: payer.publicKey, config: rconfig }).rpc(); log({ step: 'registry_initialize', ok: true, sig }); }
if (!(await conn.getAccountInfo(qconfig))) { sig = await rep.methods.initialize(payer.publicKey).accountsPartial({ payer: payer.publicKey, config: qconfig }).rpc(); log({ step: 'reputation_initialize', ok: true, sig }); }
sig = await rc.methods.registerAgent('ipfs://lab-agent-profile').accountsPartial({ owner: C.publicKey, agent }).signers([C]).rpc();
log({ step: 'register_agent', ok: true, sig, agent: agent.toBase58() });
const now = Math.floor(Date.now() / 1000);
const mkProject = async (idx, goal, deadline, ms) => { const project = pda(rid, 'project', C.publicKey.toBuffer(), le(idx));
  const s1 = await rc.methods.createProject(`Qm-lab-${idx}`, new BN(goal), SOL, new BN(deadline), ms).accountsPartial({ creator: C.publicKey, agent, project }).signers([C]).rpc();
  const escrow = pda(eid, 'escrow', project.toBuffer());
  const s2 = await ec.methods.initializeEscrow(project, new BN(goal), new BN(deadline), ms, SOL).accountsPartial({ payer: C.publicKey, creator: C.publicKey, escrow, registryProject: project, mint: null, escrowAta: null }).signers([C]).rpc();
  return { project, escrow, s1, s2 }; };
await expectFail('create_project_zero_milestones', () => rc.methods.createProject('Qm-bad', new BN(1000), SOL, new BN(now + 600), 0).accountsPartial({ creator: C.publicKey, agent, project: pda(rid, 'project', C.publicKey.toBuffer(), le(0)) }).signers([C]).rpc());
const p1 = await mkProject(0, 4_000_000, now + 900, 2);
log({ step: 'create_project_1', ok: true, sig: p1.s1, project: p1.project.toBase58(), goal: 4_000_000, milestones: 2 });
log({ step: 'initialize_escrow_1', ok: true, sig: p1.s2, escrow: p1.escrow.toBase58() });
const project2 = pda(rid, 'project', C.publicKey.toBuffer(), le(1));
await expectFail('initialize_escrow_terms_mismatch', async () => { await rc.methods.createProject('Qm-lab-1', new BN(5_000_000), SOL, new BN(now + 40), 1).accountsPartial({ creator: C.publicKey, agent, project: project2 }).signers([C]).rpc();
  return ec.methods.initializeEscrow(project2, new BN(9_000_000), new BN(now + 40), 1, SOL).accountsPartial({ payer: C.publicKey, creator: C.publicKey, escrow: pda(eid, 'escrow', project2.toBuffer()), registryProject: project2, mint: null, escrowAta: null }).signers([C]).rpc(); });
log({ step: 'create_project_2', ok: true, project: project2.toBase58(), goal: 5_000_000, deadline_in_s: 40 });
const escrow2 = pda(eid, 'escrow', project2.toBuffer());
sig = await ec.methods.initializeEscrow(project2, new BN(5_000_000), new BN(now + 40), 1, SOL).accountsPartial({ payer: C.publicKey, creator: C.publicKey, escrow: escrow2, registryProject: project2, mint: null, escrowAta: null }).signers([C]).rpc();
log({ step: 'initialize_escrow_2', ok: true, sig, escrow: escrow2.toBase58() });
const contrib = (proj, who) => pda(eid, 'contribution', proj.toBuffer(), who.toBuffer());
const contribute = (p, kp, proj, esc_, amt) => p.methods.contribute(proj, new BN(amt)).accountsPartial({ escrow: esc_, contribution: contrib(proj, kp.publicKey), contributor: kp.publicKey, contributorAta: null, escrowAta: null }).signers([kp]).rpc();
await expectFail('contribute_zero', () => contribute(ex, X, p1.project, p1.escrow, 0));
sig = await contribute(ex, X, p1.project, p1.escrow, 3_000_000);
log({ step: 'contribute_x_3m', ok: true, sig });
const relIx = (idx, votes) => esc.methods.releaseMilestone(p1.project, idx).accountsPartial({ escrow: p1.escrow, creator: C.publicKey, escrowAta: null, creatorAta: null }).remainingAccounts(votes.map(v => ({ pubkey: v, isWritable: false, isSigner: false }))).rpc();
await expectFail('release_before_goal', () => relIx(0, []));
sig = await esc.methods.contributeFor(p1.project, new BN(1_000_000)).accountsPartial({ escrow: p1.escrow, contribution: contrib(p1.project, Y.publicKey), payer: payer.publicKey, beneficiary: Y.publicKey, payerAta: null, escrowAta: null }).rpc();
log({ step: 'contribute_for_y_1m_paid_by_lab', ok: true, sig, total_deposited: (await esc.account.escrowAccount.fetch(p1.escrow)).totalDeposited.toString() });
const voteP = (kp, idx) => pda(eid, 'vote', p1.project.toBuffer(), kp.publicKey.toBuffer(), Buffer.from([idx]));
const vote = (p, kp, idx, sup) => p.methods.voteMilestone(p1.project, idx, sup).accountsPartial({ escrow: p1.escrow, contribution: contrib(p1.project, kp.publicKey), voteAccount: voteP(kp, idx), voter: kp.publicKey }).signers([kp]).rpc();
await expectFail('vote_by_non_contributor', () => vote(es, S, 0, true));
sig = await vote(ey, Y, 0, true); log({ step: 'vote_y_milestone_0_yes_weight_1m', ok: true, sig });
await expectFail('release_insufficient_approval', () => relIx(0, [voteP(Y, 0)]));
sig = await vote(ex, X, 0, true); log({ step: 'vote_x_milestone_0_yes_weight_3m', ok: true, sig });
await expectFail('release_duplicate_vote_accounts', () => relIx(0, [voteP(X, 0), voteP(X, 0)]));
await expectFail('release_out_of_order', () => relIx(1, [voteP(X, 0)]));
let b = await conn.getBalance(C.publicKey);
sig = await relIx(0, [voteP(X, 0), voteP(Y, 0)]);
log({ step: 'release_milestone_0', ok: true, sig, creator_received: (await conn.getBalance(C.publicKey)) - b });
sig = await vote(ex, X, 1, true); log({ step: 'vote_x_milestone_1_yes', ok: true, sig });
b = await conn.getBalance(C.publicKey);
sig = await relIx(1, [voteP(X, 1)]);
log({ step: 'release_milestone_1_final', ok: true, sig, creator_received: (await conn.getBalance(C.publicKey)) - b, status: Object.keys((await esc.account.escrowAccount.fetch(p1.escrow)).status)[0] });
// registry status + reputation
await expectFail('update_status_by_stranger', () => rs.methods.updateProjectStatus({ complete: {} }).accountsPartial({ authority: S.publicKey, project: p1.project, config: rconfig }).signers([S]).rpc());
sig = await rc.methods.updateProjectStatus({ complete: {} }).accountsPartial({ authority: C.publicKey, project: p1.project, config: rconfig }).signers([C]).rpc();
log({ step: 'update_project_status_complete', ok: true, sig });
sig = await reg.methods.updateProjectMetadata('Qm-lab-0-final-report').accountsPartial({ authority: payer.publicKey, project: p1.project, config: rconfig }).rpc();
log({ step: 'update_project_metadata_by_platform', ok: true, sig });
const repP = pda(qid, 'reputation', C.publicKey.toBuffer());
sig = await rep.methods.initReputation().accountsPartial({ payer: payer.publicKey, agent: C.publicKey, reputation: repP }).rpc();
log({ step: 'init_reputation', ok: true, sig, score: (await rep.account.reputationAccount.fetch(repP)).score.toString() });
await expectFail('update_reputation_wrong_delta', () => rep.methods.updateReputation(new BN(99), 0).accountsPartial({ authority: payer.publicKey, config: qconfig, agent: C.publicKey, reputation: repP }).rpc());
await expectFail('update_reputation_by_stranger', () => qs.methods.updateReputation(new BN(15), 0).accountsPartial({ authority: S.publicKey, config: qconfig, agent: C.publicKey, reputation: repP }).signers([S]).rpc());
for (const [d, r, n] of [[15, 0, 'milestone_0'], [15, 0, 'milestone_1'], [50, 3, 'goal_reached']]) { sig = await rep.methods.updateReputation(new BN(d), r).accountsPartial({ authority: payer.publicKey, config: qconfig, agent: C.publicKey, reputation: repP }).rpc(); log({ step: `update_reputation_${n}`, ok: true, sig, delta: d }); }
log({ step: 'reputation_state', score: (await rep.account.reputationAccount.fetch(repP)).score.toString() });
// project 2: refund path
sig = await contribute(ex, X, project2, escrow2, 1_000_000); log({ step: 'contribute_x_project_2', ok: true, sig });
const refund = () => ex.methods.refund(project2).accountsPartial({ escrow: escrow2, contribution: contrib(project2, X.publicKey), contributor: X.publicKey, escrowAta: null, contributorAta: null }).signers([X]).rpc();
await expectFail('refund_before_deadline', refund);
while (Math.floor(Date.now() / 1000) < now + 55) await sleep(3000);
let done = false;
for (let i = 0; i < 10 && !done; i++) { try { b = await conn.getBalance(X.publicKey); sig = await refund(); log({ step: 'refund_after_deadline_goal_missed', ok: true, sig, backer_refunded: (await conn.getBalance(X.publicKey)) - b }); done = true; } catch (e) { if (!String(e).includes('DeadlineNotPassed')) throw e; await sleep(4000); } }
if (!done) throw new Error('refund not claimable');
await expectFail('contribute_after_deadline', () => contribute(ey, Y, project2, escrow2, 100_000));
await expectFail('refund_twice', refund);
} finally {
  for (const k of [C, X, Y, S]) { const l = await conn.getBalance(k.publicKey); if (l > 0) await sendIx([SystemProgram.transfer({ fromPubkey: k.publicKey, toPubkey: payer.publicKey, lamports: l })], [payer, k]).catch(e => log({ step: 'cleanup_error', key: k.publicKey.toBase58(), lamports: l })); }
  log({ step: 'cleanup_returned_lab_wallets' });
}
process.exit(0);
