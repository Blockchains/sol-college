// Devnet end-to-end flow for the votara fork (DAO voting), mirroring the client's calls (client/votara-client/src/components).
// PDAs: dao ["dao"], config ["config"], treasury ["treasury"], gov mint ["governance_mint"], vault ["vault"],
// voter ["voter", wallet], proposal ["proposal", id u64 LE], analytics ["analytics", proposal], vote ["vote", proposal, voter].
// Usage (from client/votara-client/, @coral-xyz/anchor 0.32): node votara.mjs <idl.json> <rpc> <authority.json> [ui wallet]
import fs from 'fs';
import anchor from '@coral-xyz/anchor';
import { getOrCreateAssociatedTokenAccount, TOKEN_PROGRAM_ID } from '@solana/spl-token';
import { Connection, Keypair, PublicKey, SystemProgram, Transaction, LAMPORTS_PER_SOL, sendAndConfirmTransaction, SYSVAR_RENT_PUBKEY } from '@solana/web3.js';
const { AnchorProvider, Program, Wallet, BN } = anchor;
const [idlPath, rpc, kpPath] = process.argv.slice(2);
const A = Keypair.fromSecretKey(Uint8Array.from(JSON.parse(fs.readFileSync(kpPath, 'utf8'))));
// The public devnet RPC rate-limits hard (429). Retry those responses with backoff; resending the same signed tx is idempotent.
const rlFetch = async (url, opts) => { for (let i = 0; ; i++) { const r = await fetch(url, opts); if (r.status !== 429 || i >= 12) return r; await new Promise(z => setTimeout(z, 1500 * (i + 1))); } };
const conn = new Connection(rpc, { commitment: 'confirmed', fetch: rlFetch, disableRetryOnRateLimit: true });
conn.confirmTransaction = async (arg) => { const sig = typeof arg === 'string' ? arg : arg.signature;
  for (let i = 0; i < 90; i++) { const st = (await conn.getSignatureStatuses([sig])).value[0];
    if (st && (st.confirmationStatus === 'confirmed' || st.confirmationStatus === 'finalized')) {
      if (st.err) throw new Error('tx failed ' + JSON.stringify(st.err)); return { context: { slot: st.slot }, value: { err: st.err } }; }
    await new Promise(r => setTimeout(r, 1000)); } throw new Error('confirm timeout ' + sig); };
const idl = JSON.parse(fs.readFileSync(idlPath, 'utf8'));
const prog = (kp) => new Program(idl, new AnchorProvider(conn, new Wallet(kp), { commitment: 'confirmed' }));
const log = (o) => console.log(JSON.stringify(o)); const sleep = (ms) => new Promise(r => setTimeout(r, ms));
const err = (e) => String(e.error?.errorCode?.code || e.logs?.find(l => /Error|failed|already in use/.test(l)) || e.message).split('\n')[0].slice(0, 200);
const expectFail = async (label, fn) => { try { await fn(); log({ step: label, ok: false, error: 'UNEXPECTED SUCCESS' }); } catch (e) { log({ step: label, expectedFailure: true, error: err(e) }); } };
const P = prog(A), pid = P.programId;
const pda = (...s) => PublicKey.findProgramAddressSync(s.map(x => typeof x === 'string' ? Buffer.from(x) : x), pid)[0];
const dao = pda('dao'), config = pda('config'), treasury = pda('treasury'), govMint = pda('governance_mint'), vault = pda('vault');
const voterOf = (k) => pda('voter', k.toBuffer());
const B = Keypair.generate(), C = Keypair.generate();
log({ step: 'fund B and C', sig: await sendAndConfirmTransaction(conn, new Transaction().add(
  SystemProgram.transfer({ fromPubkey: A.publicKey, toPubkey: B.publicKey, lamports: 0.05 * LAMPORTS_PER_SOL }),
  SystemProgram.transfer({ fromPubkey: A.publicKey, toPubkey: C.publicKey, lamports: 0.05 * LAMPORTS_PER_SOL })), [A], { commitment: 'confirmed' }) });
log({ step: 'setup', program: pid.toBase58(), authority: A.publicKey.toBase58(), B: B.publicKey.toBase58(), C: C.publicKey.toBase58(), dao: dao.toBase58() });
if (!(await conn.getAccountInfo(dao))) log({ step: 'initialize_dao', ok: true, sig: await P.methods.initializeDao().accountsPartial({ authority: A.publicKey, dao, config, systemProgram: SystemProgram.programId }).rpc() });
if (!(await conn.getAccountInfo(treasury))) log({ step: 'initialize_treasury (gov mint + vault PDAs)', ok: true, sig: await P.methods.initializeTreasury().accountsPartial({ authority: A.publicKey, dao, treasury, governanceTokenMint: govMint, vault, tokenProgram: TOKEN_PROGRAM_ID, systemProgram: SystemProgram.programId, rent: SYSVAR_RENT_PUBKEY }).rpc() });
const upd = (kp, vp, q) => prog(kp).methods.updateConfig(new BN(vp), new BN(0), q, null, null, null, null).accountsPartial({ authority: kp.publicKey, dao, config }).rpc();
await expectFail('update_config_by_non_authority', () => upd(B, 40, 2));
log({ step: 'update_config: voting period 40 s, timelock 0, quorum 2 voters (defaults are 7 days and 10 voters)', ok: true, sig: await upd(A, 40, 2) });
const ata = async (k) => (await getOrCreateAssociatedTokenAccount(conn, A, govMint, k)).address;
const stake = async (kp, amt) => prog(kp).methods.stakeTokens(new BN(amt)).accountsPartial({ voterAuthority: kp.publicKey, dao, voter: voterOf(kp.publicKey), treasury, governanceTokenMint: govMint, userTokenAccount: await ata(kp.publicKey), vault, tokenProgram: TOKEN_PROGRAM_ID, systemProgram: SystemProgram.programId }).rpc();
log({ step: 'B stakes 100 while holding 0 gov tokens (stake_tokens moves no tokens)', ok: true, sig: await stake(B, 100), Bpower: (await P.account.voter.fetch(voterOf(B.publicKey))).votingPower.toNumber() });
log({ step: 'C stakes 40', ok: true, sig: await stake(C, 40) });
let d = await P.account.dao.fetch(dao); const id = d.totalProposals.toNumber();
const proposal = pda('proposal', new BN(id).toArrayLike(Buffer, 'le', 8)), analytics = pda('analytics', proposal.toBuffer());
const create = (t, pidN = id) => P.methods.createProposal(new BN(pidN), t, 'Created by the sol.college devnet run', { general: {} }, new BN(0), false, false, new BN(0)).accountsPartial({ creator: A.publicKey, dao, config, treasury, voter: voterOf(A.publicKey), proposal: pda('proposal', new BN(pidN).toArrayLike(Buffer, 'le', 8)), analytics: pda('analytics', pda('proposal', new BN(pidN).toArrayLike(Buffer, 'le', 8)).toBuffer()), systemProgram: SystemProgram.programId }).rpc();
await expectFail('create_proposal_title_over_100_chars', () => create('x'.repeat(101)));
log({ step: `create_proposal #${id}`, ok: true, sig: await create('Fund the sol.college devnet lessons'), proposal: proposal.toBase58() });
const vote = (kp, v) => prog(kp).methods.castVote(v).accountsPartial({ authority: kp.publicKey, dao, proposal, analytics, voter: voterOf(kp.publicKey), voteRecord: pda('vote', proposal.toBuffer(), voterOf(kp.publicKey).toBuffer()), systemProgram: SystemProgram.programId }).rpc();
log({ step: 'B votes Yes (power 100)', ok: true, sig: await vote(B, { yes: {} }) });
log({ step: 'C votes No (power 40)', ok: true, sig: await vote(C, { no: {} }) });
await expectFail('B_votes_twice', () => vote(B, { no: {} }));
const fin = (kp) => prog(kp).methods.finalizeProposal().accountsPartial({ authority: kp.publicKey, dao, config, treasury, proposal, analytics }).rpc();
await expectFail('finalize_before_end', () => fin(A));
const p0 = await P.account.proposal.fetch(proposal);
while ((await conn.getBlockTime(await conn.getSlot('confirmed'))) < p0.endTime.toNumber() + 2) await sleep(5000);
await expectFail('A_votes_after_end', () => vote(A, { yes: {} }));
await expectFail('finalize_by_non_authority', () => fin(B));
const sf = await fin(A); const p1 = await P.account.proposal.fetch(proposal);
log({ step: 'finalize_proposal', ok: true, sig: sf, status: Object.keys(p1.status)[0], yes: p1.yesVotes.toNumber(), no: p1.noVotes.toNumber(), uniqueVoters: p1.uniqueVoters.toNumber(), quorumReached: p1.quorumReached });
log({ step: 'gov token supply after all of this', supply: (await conn.getTokenSupply(govMint)).value.uiAmountString });
log({ step: 'authority gov-token account (for the UI buy step)', ata: (await ata(A.publicKey)).toBase58() });
