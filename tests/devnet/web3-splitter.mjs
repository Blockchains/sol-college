// Devnet end-to-end flow for the web3-splitter fork (token splitter vault), mirroring the app's own calls in
// src/components/CreateSplitter.vue and ClaimFromSplitter.vue: vault PDA = ["vault", name, authority, mint], vault token
// account = the vault's associated token account. Runs create -> deposit -> update -> claim -> delete and the rejection
// cases, and records exactly what the program does (including where it differs from what the app promises).
// Usage (from the fork root, @project-serum/anchor 0.26 as in the app): node web3-splitter.mjs <idl.json> <programId> <rpc> <authority.json>
import fs from 'fs';
import anchor from '@project-serum/anchor';
import { Connection, Keypair, PublicKey, SystemProgram, Transaction, LAMPORTS_PER_SOL } from '@solana/web3.js';
import { createMint, getOrCreateAssociatedTokenAccount, mintTo, getAssociatedTokenAddressSync, getAccount, TOKEN_PROGRAM_ID, ASSOCIATED_TOKEN_PROGRAM_ID } from '@solana/spl-token';
const { AnchorProvider, Program, Wallet, BN } = anchor;
const [idlPath, pidS, rpc, kpPath] = process.argv.slice(2);
const A = Keypair.fromSecretKey(Uint8Array.from(JSON.parse(fs.readFileSync(kpPath, 'utf8'))));
const conn = new Connection(rpc, 'confirmed');
// Confirm by polling getSignatureStatuses (the public devnet RPC we use has no websocket subscriptions).
conn.confirmTransaction = async (arg) => { const sig = typeof arg === 'string' ? arg : arg.signature;
  for (let i = 0; i < 90; i++) { const st = (await conn.getSignatureStatuses([sig])).value[0];
    if (st && (st.confirmationStatus === 'confirmed' || st.confirmationStatus === 'finalized')) {
      if (st.err) throw new Error('tx failed ' + JSON.stringify(st.err)); return { context: { slot: st.slot }, value: { err: st.err } }; }
    await new Promise(r => setTimeout(r, 1000)); } throw new Error('confirm timeout ' + sig); };
const idl = JSON.parse(fs.readFileSync(idlPath, 'utf8')); const pid = new PublicKey(pidS);
const prog = (kp) => new Program(idl, pid, new AnchorProvider(conn, new Wallet(kp), { commitment: 'confirmed' }));
const log = (o) => console.log(JSON.stringify(o));
const err = (e) => String(e.error?.errorCode?.code || e.logs?.find(l => /Error|failed/.test(l)) || e.message).split('\n')[0].slice(0, 200);
const B = Keypair.generate(), C = Keypair.generate();
const fund = new Transaction().add(SystemProgram.transfer({ fromPubkey: A.publicKey, toPubkey: B.publicKey, lamports: 0.02 * LAMPORTS_PER_SOL }),
  SystemProgram.transfer({ fromPubkey: A.publicKey, toPubkey: C.publicKey, lamports: 0.02 * LAMPORTS_PER_SOL }));
log({ step: 'fund B and C (fees)', sig: await anchor.web3.sendAndConfirmTransaction(conn, fund, [A], { commitment: 'confirmed' }) });
const mint = await createMint(conn, A, A.publicKey, null, 6);
const aAta = await getOrCreateAssociatedTokenAccount(conn, A, mint, A.publicKey);
await mintTo(conn, A, mint, aAta.address, A, 1000e6);
const name = 'sc-' + Date.now().toString(36);
const [vault] = PublicKey.findProgramAddressSync([Buffer.from('vault'), Buffer.from(name), A.publicKey.toBytes(), mint.toBytes()], pid);
const vaultAta = getAssociatedTokenAddressSync(mint, vault, true);
const bal = async (a) => { try { return Number((await getAccount(conn, a)).amount) / 1e6; } catch { return null; } };
log({ step: 'setup', program: pidS, authority: A.publicKey.toBase58(), B: B.publicKey.toBase58(), outsider: C.publicKey.toBase58(), mint: mint.toBase58(), name, vault: vault.toBase58(), vaultTokenAccount: vaultAta.toBase58() });
const initAcc = { vault, authority: A.publicKey, vaultTokenAccount: vaultAta, token: mint, tokenProgram: TOKEN_PROGRAM_ID, systemProgram: SystemProgram.programId, associatedTokenProgram: ASSOCIATED_TOKEN_PROGRAM_ID };
const P = prog(A);
for (const [label, pc, ac] of [['initialize_percent_sum_90', [60, 30], [A.publicKey, B.publicKey]], ['initialize_length_mismatch', [100], [A.publicKey, B.publicKey]]]) {
  try { await P.methods.initialize(name, pc.map(x => new BN(x)), ac).accounts(initAcc).rpc(); log({ step: label, ok: false, error: 'UNEXPECTED SUCCESS' }); }
  catch (e) { log({ step: label, expectedFailure: true, error: err(e) }); } }
const s1 = await P.methods.initialize(name, [new BN(60), new BN(40)], [A.publicKey, B.publicKey]).accounts(initAcc).rpc();
log({ step: 'initialize 60% A / 40% B', ok: true, sig: s1 });
const depAcc = { vault, authority: A.publicKey, systemProgram: SystemProgram.programId, token: mint, associatedTokenProgram: ASSOCIATED_TOKEN_PROGRAM_ID, tokenProgram: TOKEN_PROGRAM_ID, vaultTokenAccount: vaultAta, singerTokenAccount: aAta.address };
const s2 = await P.methods.deposite(new BN(100e6)).accountsStrict(depAcc).rpc();
let v = await P.account.vault.fetch(vault);
log({ step: 'deposite 100 tokens', ok: true, sig: s2, vaultTokens: await bal(vaultAta), total: v.total.toNumber() / 1e6, accountsVault: v.accountsVault.map(x => x.toNumber() / 1e6) });
try { await prog(B).methods.update([new BN(50), new BN(50)]).accounts({ vault, authority: B.publicKey, systemProgram: SystemProgram.programId }).rpc(); log({ step: 'update_by_non_authority', ok: false, error: 'UNEXPECTED SUCCESS' }); }
catch (e) { log({ step: 'update_by_non_authority', expectedFailure: true, error: err(e) }); }
const s3 = await P.methods.update([new BN(70), new BN(30)]).accounts({ vault, authority: A.publicKey, systemProgram: SystemProgram.programId }).rpc();
v = await P.account.vault.fetch(vault);
log({ step: 'update to 70/30 by authority', ok: true, sig: s3, percentages: v.percentages.map(x => x.toNumber()), accountsVaultUnchanged: v.accountsVault.map(x => x.toNumber() / 1e6) });
const claimAcc = (kp) => ({ vault, claimer: kp.publicKey, vaultTokenAccount: vaultAta, singerTokenAccount: getAssociatedTokenAddressSync(mint, kp.publicKey), token: mint, associatedTokenProgram: ASSOCIATED_TOKEN_PROGRAM_ID, tokenProgram: TOKEN_PROGRAM_ID, systemProgram: SystemProgram.programId });
try { await prog(C).methods.claim().accounts(claimAcc(C)).rpc(); log({ step: 'claim_by_outsider', ok: false, error: 'UNEXPECTED SUCCESS' }); }
catch (e) { log({ step: 'claim_by_outsider', expectedFailure: true, error: err(e) }); }
try { const sb = await prog(B).methods.claim().accounts(claimAcc(B)).rpc(); v = await P.account.vault.fetch(vault);
  log({ step: 'claim_by_B (40% recipient)', ok: true, sig: sb, Btokens: await bal(getAssociatedTokenAddressSync(mint, B.publicKey)), vaultTokens: await bal(vaultAta), total: v.total.toNumber() / 1e6 }); }
catch (e) { log({ step: 'claim_by_B (40% recipient)', failed: true, error: err(e), note: 'claim signs for the vault PDA with seeds [vault, name, CLAIMER, mint]; they only match the PDA when the claimer is the authority' }); }
const before = await bal(aAta.address);
const sa = await P.methods.claim().accounts(claimAcc(A)).rpc(); v = await P.account.vault.fetch(vault);
log({ step: 'claim_by_A (authority, 60% recipient)', ok: true, sig: sa, Areceived: (await bal(aAta.address)) - before, vaultTokens: await bal(vaultAta), total: v.total.toNumber() / 1e6, accountsVault: v.accountsVault.map(x => x.toNumber() / 1e6) });
try { await prog(B).methods.delete().accounts({ vault, authority: B.publicKey, systemProgram: SystemProgram.programId }).rpc(); log({ step: 'delete_by_non_authority', ok: false, error: 'UNEXPECTED SUCCESS' }); }
catch (e) { log({ step: 'delete_by_non_authority', expectedFailure: true, error: err(e) }); }
const s5 = await P.methods.delete().accounts({ vault, authority: A.publicKey, systemProgram: SystemProgram.programId }).rpc();
log({ step: 'delete by authority', ok: true, sig: s5, vaultClosed: (await conn.getAccountInfo(vault)) === null, vaultTokensLeft: await bal(vaultAta) });
