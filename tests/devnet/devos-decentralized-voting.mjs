// DeVos (devos-decentralized-voting fork) on devnet: an election with two positions, a voter allow-list, voting, and the winner calculation,
// plus the program's rejections. The app's Create Election page only calls create_election / add_position / add_candidate
// (devos-app/utils/solana.ts); the rest has no UI and is exercised here.
// Usage (from devos-app/, @project-serum/anchor 0.26): node devos-decentralized-voting.mjs <idl.json> <rpc> <payer.json>
// The payer funds fresh keys (A = election authority, V and W = voters, X = outsider) and gets the unspent SOL back at the end.
import fs from 'fs';
import anchor from '@project-serum/anchor';
import { Connection, Keypair, PublicKey, SystemProgram, Transaction, LAMPORTS_PER_SOL, sendAndConfirmTransaction } from '@solana/web3.js';
const { AnchorProvider, Program, Wallet } = anchor;
const [idlPath, rpc, payerPath] = process.argv.slice(2);
const rlFetch = async (url, opts) => { for (let i = 0; ; i++) { const r = await fetch(url, opts); if ((r.status !== 429 && r.status < 500) || i >= 12) return r; await new Promise(z => setTimeout(z, 1500 * (i + 1))); } };
const conn = new Connection(rpc, { commitment: 'confirmed', fetch: rlFetch, disableRetryOnRateLimit: true });
const sleep = (ms) => new Promise(r => setTimeout(r, ms));
conn.confirmTransaction = async (arg) => { const sig = typeof arg === 'string' ? arg : arg.signature;
  for (let i = 0; i < 90; i++) { const st = (await conn.getSignatureStatuses([sig])).value[0];
    if (st && (st.confirmationStatus === 'confirmed' || st.confirmationStatus === 'finalized')) {
      if (st.err) throw new Error('tx failed ' + JSON.stringify(st.err)); return { context: { slot: st.slot }, value: { err: st.err } }; }
    await sleep(1000); } throw new Error('confirm timeout ' + sig); };
const kp = (p) => Keypair.fromSecretKey(Uint8Array.from(JSON.parse(fs.readFileSync(p, 'utf8'))));
const idl = JSON.parse(fs.readFileSync(idlPath, 'utf8')); const pid = new PublicKey(idl.metadata.address);
const prog = (k) => new Program(idl, pid, new AnchorProvider(conn, new Wallet(k), { commitment: 'confirmed' }));
const log = (o) => console.log(JSON.stringify(o));
const err = (e) => String(e.error?.errorCode?.code || e.logs?.find(l => /Error|failed|already in use|insufficient/i.test(l)) || e.message).split('\n')[0].slice(0, 200);
const transient = (e) => /Backend error|StatusCode: 5|fetch failed|ECONNRESET|blockhash/i.test(String(e?.message || e));
const retry = async (fn) => { for (let i = 0; ; i++) { try { return await fn(); } catch (e) { if (!transient(e) || i >= 6) throw e; await sleep(4000 * (i + 1)); } } };
const expectFail = async (label, fn0) => { const fn = () => retry(fn0); try { const s = await fn(); log({ step: label, ok: false, error: 'UNEXPECTED SUCCESS', sig: s }); } catch (e) { log({ step: label, expectedFailure: true, error: err(e) }); } };
const SOL = LAMPORTS_PER_SOL; const payer = kp(payerPath);
const A = Keypair.generate(), V = Keypair.generate(), W = Keypair.generate(), X = Keypair.generate(); const keyDir = payerPath.replace(/[^/]*$/, '');
const tag = A.publicKey.toBase58().slice(0, 6);
for (const [n, k] of [['A', A], ['V', V], ['W', W], ['X', X]]) try { fs.writeFileSync(`${process.env.ROLE_KEY_DIR || keyDir}devos-${n}-${tag}.json`, JSON.stringify(Array.from(k.secretKey)), { mode: 0o600 }); } catch {}
const NAME = `sc-${tag}`;
const elOf = (auth) => PublicKey.findProgramAddressSync([Buffer.from(NAME), auth.toBuffer()], pid)[0];
const EL = elOf(A.publicKey); const sys = SystemProgram.programId;
log({ step: 'setup', program: pid.toBase58(), A: A.publicKey.toBase58(), V: V.publicKey.toBase58(), W: W.publicKey.toBase58(), X: X.publicKey.toBase58(), election: EL.toBase58(), name: NAME });
log({ step: 'fund A 0.03, V 0.005, W 0.005, X 0.005 SOL', sig: await sendAndConfirmTransaction(conn, new Transaction().add(
  SystemProgram.transfer({ fromPubkey: payer.publicKey, toPubkey: A.publicKey, lamports: 0.03 * SOL }),
  SystemProgram.transfer({ fromPubkey: payer.publicKey, toPubkey: V.publicKey, lamports: 0.005 * SOL }),
  SystemProgram.transfer({ fromPubkey: payer.publicKey, toPubkey: W.publicKey, lamports: 0.005 * SOL }),
  SystemProgram.transfer({ fromPubkey: payer.publicKey, toPubkey: X.publicKey, lamports: 0.005 * SOL })), [payer], { commitment: 'confirmed' }) });
const create = () => prog(A).methods.createElection(NAME, 2, 1, [V.publicKey]).accounts({ election: EL, authority: A.publicKey, systemProgram: sys }).rpc();
const addPos = (k, n, el = EL) => prog(k).methods.addPosition(NAME, n).accounts({ election: el, authority: k.publicKey }).rpc();
const addCand = (i, n) => prog(A).methods.addCandidate(NAME, i, n).accounts({ election: EL, authority: A.publicKey }).rpc();
const toggle = () => prog(A).methods.toggleElection(NAME).accounts({ election: EL, authority: A.publicKey }).rpc();
const vote = (k, p, c) => prog(k).methods.vote(NAME, A.publicKey, p, c).accounts({ election: EL, voter: k.publicKey }).rpc();
const winner = () => prog(A).methods.getWinner(NAME).accounts({ election: EL, authority: A.publicKey }).rpc();
const state = async () => { const e = await retry(() => prog(A).account.election.fetch(EL));
  return { is_open: e.isOpen, positions: e.positions.map(p => ({ name: p.name, candidates: p.candidates.map(c => `${c.name}:${c.voteCount.toString()}`) })), voters: e.voters.length, votes: e.votes.length,
    winners: e.winners.map(w => `${w.positionName}=${w.candidateNames.join('|')}`) }; };
log({ step: 'A creates the election (max 2 positions, 1 candidate each plus Abstain, voters [V]; PDA [name, authority])', ok: true, sig: await retry(create), rent_sol: (await conn.getBalance(EL)) / SOL, bytes: (await conn.getAccountInfo(EL)).data.length });
await expectFail('A creates the same election again', create);
await expectFail('X adds a position to A\'s election (seeds use the signer, so the PDA does not match)', () => addPos(X, 'Mayor'));
log({ step: 'A adds position President', ok: true, sig: await retry(() => addPos(A, 'President')) });
log({ step: 'A adds position Treasurer', ok: true, sig: await retry(() => addPos(A, 'Treasurer')) });
await expectFail('A adds a third position (max 2)', () => addPos(A, 'Secretary'));
await expectFail('A adds President again', () => addPos(A, 'President'));
log({ step: 'A adds candidate Alice to President', ok: true, sig: await retry(() => addCand(0, 'Alice')) });
log({ step: 'A adds candidate Bob to Treasurer', ok: true, sig: await retry(() => addCand(1, 'Bob')) });
await expectFail('A adds a second candidate to President (max 1 plus Abstain)', () => addCand(0, 'Carol'));
await expectFail('A adds a candidate to position 5 (does not exist)', () => addCand(5, 'Dan'));
await expectFail('V votes before the election is opened', () => vote(V, 0, 0));
log({ step: 'A opens the election (toggle_election)', ok: true, sig: await retry(toggle) });
await expectFail('A adds a candidate while the election is open', () => addCand(1, 'Eve'));
log({ step: 'V votes Alice for President', ok: true, sig: await retry(() => vote(V, 0, 0)) });
await expectFail('V votes for President again', () => vote(V, 0, 1));
await expectFail('X (not on the voter list) votes', () => vote(X, 0, 0));
await expectFail('V votes for candidate 7 of Treasurer (does not exist)', () => vote(V, 1, 7));
log({ step: 'V votes Abstain for Treasurer', ok: true, sig: await retry(() => vote(V, 1, 1)) });
log({ step: 'A calls tally_votes (it only writes the counts to the program log)', ok: true, sig: await retry(() => prog(A).methods.tallyVotes(NAME).accounts({ election: EL, authority: A.publicKey }).rpc()) });
await expectFail('A calls get_winner while the election is open', winner);
log({ step: 'A closes the election', ok: true, sig: await retry(toggle) });
log({ step: 'A calls get_winner', ok: true, sig: await retry(winner) });
log({ step: 'state after get_winner', ...(await state()) });
log({ step: 'A adds voter W after the result (add_voter reallocs the account)', ok: true, sig: await retry(() => prog(A).methods.addVoter(NAME, W.publicKey).accounts({ election: EL, authority: A.publicKey, systemProgram: sys }).rpc()) });
log({ step: 'A reopens the closed election (toggle has no finished state)', ok: true, sig: await retry(toggle) });
log({ step: 'W votes Abstain for President after the winners were stored', ok: true, sig: await retry(() => vote(W, 0, 1)) });
log({ step: 'state: the stored winners were not updated', ...(await state()) });
for (const k of [A, V, W, X]) { const b = await conn.getBalance(k.publicKey); if (b > 10000)
  log({ step: 'return unspent SOL to the payer', from: k.publicKey.toBase58(), sol: (b - 5000) / SOL,
    sig: await retry(() => sendAndConfirmTransaction(conn, new Transaction().add(SystemProgram.transfer({ fromPubkey: k.publicKey, toPubkey: payer.publicKey, lamports: b - 5000 })), [k], { commitment: 'confirmed' })) }); }
