// Devnet end-to-end flow for the ciphervault fork (SOL multisig vault), mirroring the app's calls in app/src/App.tsx.
// PDAs: multisig = ["multisig", creator, name], vault = ["vault", multisig], transaction = ["transaction", multisig, count u32 LE].
// Usage (from app/, @coral-xyz/anchor 0.32): node ciphervault.mjs <idl.json> <rpc> <creator.json>
import fs from 'fs';
import anchor from '@coral-xyz/anchor';
import { Connection, Keypair, PublicKey, SystemProgram, Transaction, LAMPORTS_PER_SOL, sendAndConfirmTransaction } from '@solana/web3.js';
const { AnchorProvider, Program, Wallet, BN } = anchor;
const [idlPath, rpc, kpPath] = process.argv.slice(2);
const A = Keypair.fromSecretKey(Uint8Array.from(JSON.parse(fs.readFileSync(kpPath, 'utf8'))));
const conn = new Connection(rpc, 'confirmed');
conn.confirmTransaction = async (arg) => { const sig = typeof arg === 'string' ? arg : arg.signature;
  for (let i = 0; i < 90; i++) { const st = (await conn.getSignatureStatuses([sig])).value[0];
    if (st && (st.confirmationStatus === 'confirmed' || st.confirmationStatus === 'finalized')) {
      if (st.err) throw new Error('tx failed ' + JSON.stringify(st.err)); return { context: { slot: st.slot }, value: { err: st.err } }; }
    await new Promise(r => setTimeout(r, 1000)); } throw new Error('confirm timeout ' + sig); };
const idl = JSON.parse(fs.readFileSync(idlPath, 'utf8'));
const prog = (kp) => new Program(idl, new AnchorProvider(conn, new Wallet(kp), { commitment: 'confirmed' }));
const log = (o) => console.log(JSON.stringify(o));
const err = (e) => String(e.error?.errorCode?.code || e.logs?.find(l => /Error|failed/.test(l)) || e.message).split('\n')[0].slice(0, 200);
const expectFail = async (label, fn) => { try { await fn(); log({ step: label, ok: false, error: 'UNEXPECTED SUCCESS' }); } catch (e) { log({ step: label, expectedFailure: true, error: err(e) }); } };
const probe = async (label, fn) => { try { log({ step: label, probe: true, succeeded: true, sig: await fn() }); } catch (e) { log({ step: label, probe: true, succeeded: false, error: err(e) }); } };
const P = prog(A), pid = P.programId, SOL = LAMPORTS_PER_SOL;
const B = Keypair.generate(), C = Keypair.generate(), D = Keypair.generate(), R = Keypair.generate();
log({ step: 'fund B and D (D is not an owner)', sig: await sendAndConfirmTransaction(conn, new Transaction().add(
  SystemProgram.transfer({ fromPubkey: A.publicKey, toPubkey: B.publicKey, lamports: 0.05 * SOL }),
  SystemProgram.transfer({ fromPubkey: A.publicKey, toPubkey: D.publicKey, lamports: 0.05 * SOL })), [A], { commitment: 'confirmed' }) });
const name = 'solcollege-' + Date.now().toString(36);
const pdas = (n) => { const [ms] = PublicKey.findProgramAddressSync([Buffer.from('multisig'), A.publicKey.toBuffer(), Buffer.from(n)], pid);
  const [vault] = PublicKey.findProgramAddressSync([Buffer.from('vault'), ms.toBuffer()], pid); return { ms, vault }; };
const { ms, vault } = pdas(name);
log({ step: 'setup', program: pid.toBase58(), A: A.publicKey.toBase58(), B: B.publicKey.toBase58(), C: C.publicKey.toBase58(), D: D.publicKey.toBase58(), recipient: R.publicKey.toBase58(), multisig: ms.toBase58(), vault: vault.toBase58(), name });
const createMs = (n, owners, amt) => { const p = pdas(n); return P.methods.createMultisig(2, owners, n, amt).accountsPartial({ multiSig: p.ms, vault: p.vault, creator: A.publicKey, systemProgram: SystemProgram.programId }).rpc(); };
await expectFail('create_duplicate_owners', () => createMs(name + 'd', [A.publicKey, B.publicKey, B.publicKey], new BN(0.01 * SOL)));
await probe('create_with_amount_None (#[instruction] declares amount: u64, the handler takes Option<u64>)', () => createMs(name + 'n', [A.publicKey, B.publicKey, C.publicKey], null));
const s1 = await createMs(name, [A.publicKey, B.publicKey, C.publicKey], new BN(0.2 * SOL));
let m = await P.account.multisig.fetch(ms);
log({ step: 'create_multisig 2-of-3 (A,B,C) with 0.2 SOL', ok: true, sig: s1, threshold: m.threshold, owners: m.owners.length, vaultSol: (await conn.getBalance(vault)) / SOL });
const txPda = (count) => PublicKey.findProgramAddressSync([Buffer.from('transaction'), ms.toBuffer(), new BN(count).toArrayLike(Buffer, 'le', 4)], pid)[0];
const propose = (kp, amt) => prog(kp).methods.createTransaction(new BN(amt), null).accountsPartial({ multisig: ms, proposer: kp.publicKey, transactionAccount: txPda(m.transactionCount), reciepient: R.publicKey, vault, systemProgram: SystemProgram.programId }).rpc();
await expectFail('non_owner_D_proposes', () => propose(D, 0.01 * SOL));
const t0 = txPda(m.transactionCount);
const s2 = await propose(A, 0.05 * SOL);
log({ step: 'A proposes 0.05 SOL to recipient (A auto-approves)', ok: true, sig: s2, transaction: t0.toBase58() });
const execute = (kp, t) => prog(kp).methods.fnExecute().accountsPartial({ multisig: ms, signer: kp.publicKey, transactionAccount: t, vault, reciepientAccount: R.publicKey, systemProgram: SystemProgram.programId }).rpc();
await expectFail('execute_with_1_of_2_approvals', () => execute(A, t0));
const approve = (kp, t) => prog(kp).methods.approval().accountsPartial({ approver: kp.publicKey, multisig: ms, transaction: t }).rpc();
await expectFail('non_owner_D_approves', () => approve(D, t0));
log({ step: 'B approves (2 of 2)', ok: true, sig: await approve(B, t0) });
const s3 = await execute(A, t0);
let t = await P.account.transactionAccount.fetch(t0);
log({ step: 'A executes', ok: true, sig: s3, executed: t.executed, recipientSol: (await conn.getBalance(R.publicKey)) / SOL, vaultSol: (await conn.getBalance(vault)) / SOL });
await probe('execute the same transaction again (fn_execute never checks `executed`)', () => execute(A, t0));
log({ step: 'after', recipientSol: (await conn.getBalance(R.publicKey)) / SOL, vaultSol: (await conn.getBalance(vault)) / SOL });
