// Devnet end-to-end flow for the TrustLock fork (dead man's switch), mirroring components/DeadManSwitch.tsx:
// escrow PDA = ["escrow", owner, seed]; initialize + deposit, checkin to extend, claim after the deadline pays the beneficiary.
// The app's IDL makes the beneficiary sign claim (the beneficiary claims from their own wallet); here the owner pays the fee.
// Negatives: past deadline, zero deposit, claim before the deadline. Usage (from the fork root, anchor 0.28):
// node trustlock.mjs <legacy idl.json> <programId> <rpc> <owner.json>
import fs from 'fs';
import anchor from '@coral-xyz/anchor';
import { Connection, Keypair, PublicKey, SystemProgram, LAMPORTS_PER_SOL } from '@solana/web3.js';
const { AnchorProvider, Program, Wallet, BN } = anchor;
const [idlPath, pidS, rpc, kpPath] = process.argv.slice(2);
const kp = Keypair.fromSecretKey(Uint8Array.from(JSON.parse(fs.readFileSync(kpPath, 'utf8'))));
const conn = new Connection(rpc, 'confirmed');
// Confirm by polling getSignatureStatuses (the public devnet RPC we used has no websocket subscriptions).
conn.confirmTransaction = async (arg) => { const sig = typeof arg === 'string' ? arg : arg.signature;
  for (let i = 0; i < 90; i++) { const st = (await conn.getSignatureStatuses([sig])).value[0];
    if (st && (st.confirmationStatus === 'confirmed' || st.confirmationStatus === 'finalized')) return { context: { slot: st.slot }, value: { err: st.err } };
    await new Promise(r => setTimeout(r, 1000)); } throw new Error('confirm timeout ' + sig); };
const provider = new AnchorProvider(conn, new Wallet(kp), { commitment: 'confirmed' });
const program = new Program(JSON.parse(fs.readFileSync(idlPath, 'utf8')), new PublicKey(pidS), provider);
const log = (o) => console.log(JSON.stringify(o)); const sleep = (ms) => new Promise(r => setTimeout(r, ms));
const owner = kp.publicKey, benKp = Keypair.generate(), beneficiary = benKp.publicKey, seed = Date.now().toString();
const [escrow] = PublicKey.findProgramAddressSync([Buffer.from('escrow'), owner.toBuffer(), Buffer.from(seed)], program.programId);
const now = async () => (await conn.getBlockTime(await conn.getSlot('confirmed')));
const err = (e) => String(e.error?.errorCode?.code || e.message).split('\n')[0].slice(0, 160);
const acc = { owner, escrow, systemProgram: SystemProgram.programId };
log({ step: 'setup', program: pidS, owner: owner.toBase58(), beneficiary: beneficiary.toBase58(), escrow: escrow.toBase58() });
try { await program.methods.initialize(new BN((await now()) - 60), beneficiary, seed).accounts(acc).rpc(); log({ step: 'initialize_past_deadline', ok: false, error: 'UNEXPECTED SUCCESS' }); }
catch (e) { log({ step: 'initialize_past_deadline', expectedFailure: true, error: err(e) }); }
const s1 = await program.methods.initialize(new BN((await now()) + 45), beneficiary, seed).accounts(acc).rpc();
log({ step: 'initialize', ok: true, sig: s1 });
const s2 = await program.methods.deposit(new BN(0.02 * LAMPORTS_PER_SOL)).accounts(acc).rpc();
log({ step: 'deposit 0.02 SOL', ok: true, sig: s2, escrowLamports: await conn.getBalance(escrow) });
try { await program.methods.deposit(new BN(0)).accounts(acc).rpc(); log({ step: 'deposit_zero', ok: false, error: 'UNEXPECTED SUCCESS' }); }
catch (e) { log({ step: 'deposit_zero', expectedFailure: true, error: err(e) }); }
const s3 = await program.methods.checkin(new BN((await now()) + 60)).accounts({ owner, escrow }).rpc();
const ea = await program.account.escrow.fetch(escrow);
log({ step: 'checkin (extend deadline)', ok: true, sig: s3, deadline: ea.deadline.toString(), lastCheckin: ea.lastCheckin.toString() });
try { await program.methods.claim().accounts({ beneficiary, escrow, systemProgram: SystemProgram.programId }).signers([benKp]).rpc(); log({ step: 'claim_before_deadline', ok: false, error: 'UNEXPECTED SUCCESS' }); }
catch (e) { log({ step: 'claim_before_deadline', expectedFailure: true, error: err(e) }); }
while ((await now()) < ea.deadline.toNumber() + 2) await sleep(5000);
const s4 = await program.methods.claim().accounts({ beneficiary, escrow, systemProgram: SystemProgram.programId }).signers([benKp]).rpc();
log({ step: 'claim after deadline', ok: true, sig: s4, beneficiaryLamports: await conn.getBalance(beneficiary), escrowClosed: (await conn.getAccountInfo(escrow)) === null });
