// Devnet end-to-end flow for the poe-solana fork. Mirrors the fork's own app hooks
// (app/src/hooks/mutations/useRegisterUser, useCreatePoll, useMakeEstimate): same PDA seeds, same instructions.
// Usage (from the fork's app/ dir, after yarn install): node poe-solana.mjs <idl.json> <rpc> <tester-keypair.json>
// Prints one JSON line per step; never prints keys.
import fs from 'fs';
import anchor from '@coral-xyz/anchor';
import { Connection, Keypair, PublicKey } from '@solana/web3.js';
import { getAssociatedTokenAddressSync } from '@solana/spl-token';
const { AnchorProvider, Program, Wallet, BN } = anchor;
const [idlPath, rpc, kpPath] = process.argv.slice(2);
const idl = JSON.parse(fs.readFileSync(idlPath, 'utf8'));
const kp = Keypair.fromSecretKey(Uint8Array.from(JSON.parse(fs.readFileSync(kpPath, 'utf8'))));
const conn = new Connection(rpc, 'confirmed');
const provider = new AnchorProvider(conn, new Wallet(kp), { commitment: 'confirmed' });
const program = new Program(idl, provider);
const pid = program.programId, me = kp.publicKey;
const pda = (...s) => PublicKey.findProgramAddressSync(s, pid)[0];
const log = (o) => console.log(JSON.stringify(o));
const userPda = pda(Buffer.from('user'), me.toBuffer());
const mint = pda(Buffer.from('poeken_mint'));
const ata = getAssociatedTokenAddressSync(mint, me);
const statePda = pda(Buffer.from('poe_state'));
log({ step: 'setup', program: pid.toBase58(), tester: me.toBase58(), rpc });
// 1. register_user (mints the starting POEKEN balance to the user's ATA)
if (!(await conn.getAccountInfo(userPda))) {
  const sig = await program.methods.registerUser().accountsPartial({ user: userPda, mint, tokenAccount: ata }).rpc();
  log({ step: 'register_user', ok: true, sig });
}
const bal = await conn.getTokenAccountBalance(ata);
log({ step: 'read_token_balance', ata: ata.toBase58(), uiAmount: bal.value.uiAmountString });
// negative: registering the same wallet twice must fail (user PDA already initialised)
try { await program.methods.registerUser().accountsPartial({ user: userPda, mint, tokenAccount: ata }).rpc(); log({ step: 'register_user_twice', ok: false, error: 'UNEXPECTED SUCCESS' }); }
catch (e) { log({ step: 'register_user_twice', expectedFailure: true, error: String(e.message || e).split('\n')[0].slice(0, 200) }); }
// 2. create_poll: poll PDA seeded by state.numPolls (le u64), like useCreatePoll
const st = await program.account.poeState.fetch(statePda);
const pollId = st.numPolls;
const poll = pda(Buffer.from('poll'), pollId.toArrayLike(Buffer, 'le', 8));
const scoring = pda(Buffer.from('scoring_list'), poll.toBuffer());
const q = 'Sol.College devnet check ' + new Date().toISOString().slice(0, 16);
const sig2 = await program.methods.createPoll(q, 'End-to-end test poll created by tests/devnet/poe-solana.mjs', 0, 1.0)
  .accountsPartial({ resolver: me, state: statePda, poll, scoringList: scoring }).rpc();
log({ step: 'create_poll', ok: true, pollId: pollId.toString(), poll: poll.toBase58(), sig: sig2 });
// negative: lower > upper underflows (upper - lower) and the program must reject it
const pollAcc = await program.account.poll.fetch(poll);
const accs = (p) => ({
  user: userPda, poll, userEstimate: pda(Buffer.from('user_estimate'), poll.toBuffer(), me.toBuffer()),
  pollEstimateUpdate: pda(Buffer.from('poll_estimate_update'), poll.toBuffer(), p.numEstimateUpdates.toArrayLike(Buffer, 'le', 8)),
  scoringList: scoring, userScore: pda(Buffer.from('user_score'), poll.toBuffer(), me.toBuffer()),
  forecasterTokenAccount: ata, mint, escrowAccount: pda(Buffer.from('escrow')),
});
try { await program.methods.makeEstimate(70, 30).accountsPartial(accs(pollAcc)).rpc(); log({ step: 'make_estimate_inverted', ok: false, error: 'UNEXPECTED SUCCESS' }); }
catch (e) { log({ step: 'make_estimate_inverted', expectedFailure: true, error: String(e.message || e).split('\n')[0].slice(0, 200) }); }
// 3. make_estimate 30..70 -> collective estimate should become 50
const sig3 = await program.methods.makeEstimate(30, 70).accountsPartial(accs(pollAcc)).rpc();
const after = await program.account.poll.fetch(poll);
log({ step: 'make_estimate', ok: true, sig: sig3, collectiveEstimate: after.collectiveEstimate ?? null, numForecasters: String(after.numForecasters ?? ''), numEstimateUpdates: after.numEstimateUpdates.toString() });
const ue = await program.account.userEstimate.fetch(accs(pollAcc).userEstimate);
log({ step: 'read_user_estimate', lower: ue.lowerEstimate, upper: ue.upperEstimate });
