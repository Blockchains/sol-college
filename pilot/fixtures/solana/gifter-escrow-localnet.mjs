// Sol.College trusted Solana runtime fixture for gifter-escrow candidates.
// Runs against a local solana-test-validator that has the CANDIDATE's freshly built program loaded
// (solana-test-validator --bpf-program <idl.address> target/deploy/gifter_escrow.so). No devnet, no
// mainnet, no real funds. The fixture lives in Blockchains/sol-college (protected), not in the candidate,
// so a contributor cannot weaken it. Exit code 0 only if every positive step succeeds with the expected
// balances and every negative step is rejected by the program.
// Usage (from the candidate's contract/ directory, after yarn install):
//   node gifter-escrow-localnet.mjs <target/idl/gifter_escrow.json> <rpc> <payer.json>
import fs from 'fs';
import anchor from '@coral-xyz/anchor';
import { Connection, Keypair, PublicKey, SystemProgram, Transaction, LAMPORTS_PER_SOL, sendAndConfirmTransaction } from '@solana/web3.js';
import { TOKEN_PROGRAM_ID, ASSOCIATED_TOKEN_PROGRAM_ID, getAccount, getAssociatedTokenAddressSync, createAssociatedTokenAccountInstruction, createMintToInstruction, createInitializeMint2Instruction, MINT_SIZE } from '@solana/spl-token';
const { AnchorProvider, Program, Wallet, BN } = anchor;
const [idlPath, rpc, payerPath] = process.argv.slice(2);
const conn = new Connection(rpc, 'confirmed');
const idl = JSON.parse(fs.readFileSync(idlPath, 'utf8'));
const payer = Keypair.fromSecretKey(Uint8Array.from(JSON.parse(fs.readFileSync(payerPath, 'utf8'))));
const prog = (k) => new Program(idl, new AnchorProvider(conn, new Wallet(k), { commitment: 'confirmed' }));
const results = [];
let failed = false;
const log = (o) => { results.push(o); console.log(JSON.stringify(o)); };
const fail = (step, why) => { failed = true; log({ step, ok: false, error: why }); };
const errText = (e) => String(e?.error?.errorCode?.code || e?.logs?.find((l) => /Error|failed|already in use|insufficient|0x/i.test(l)) || e?.message || e).split('\n')[0].slice(0, 200);
const SOL = LAMPORTS_PER_SOL, DEC = 6, UNIT = 10 ** DEC;
const pid = new PublicKey(idl.address);
const escrowOf = (maker, id) => PublicKey.findProgramAddressSync([Buffer.from('gifter_escrow'), maker.toBuffer(), new BN(id).toArrayLike(Buffer, 'le', 8)], pid)[0];
const vaultOf = (state, mint) => getAssociatedTokenAddressSync(mint, state, true, TOKEN_PROGRAM_ID);
const ata = (owner, mint) => getAssociatedTokenAddressSync(mint, owner, false, TOKEN_PROGRAM_ID);
const tok = async (a) => { try { return Number((await getAccount(conn, a)).amount); } catch { return 0; } };
const send = (tx, signers) => sendAndConfirmTransaction(conn, tx, signers, { commitment: 'confirmed' });

async function main() {
  const prog_info = await conn.getAccountInfo(pid);
  if (!prog_info?.executable) throw new Error(`program ${pid.toBase58()} is not loaded on the local validator`);
  log({ step: 'program loaded on local validator', ok: true, program: pid.toBase58() });
  const M = Keypair.generate(), T = Keypair.generate(), X = Keypair.generate();
  await send(new Transaction().add(
    SystemProgram.transfer({ fromPubkey: payer.publicKey, toPubkey: M.publicKey, lamports: 0.2 * SOL }),
    SystemProgram.transfer({ fromPubkey: payer.publicKey, toPubkey: T.publicKey, lamports: 0.2 * SOL }),
    SystemProgram.transfer({ fromPubkey: payer.publicKey, toPubkey: X.publicKey, lamports: 0.05 * SOL })), [payer]);
  const newMint = async () => {
    const mint = Keypair.generate();
    const lamports = await conn.getMinimumBalanceForRentExemption(MINT_SIZE);
    await send(new Transaction().add(
      SystemProgram.createAccount({ fromPubkey: payer.publicKey, newAccountPubkey: mint.publicKey, space: MINT_SIZE, lamports, programId: TOKEN_PROGRAM_ID }),
      createInitializeMint2Instruction(mint.publicKey, DEC, payer.publicKey, null, TOKEN_PROGRAM_ID)), [payer, mint]);
    return mint.publicKey;
  };
  const mintA = await newMint(), mintB = await newMint();
  for (const [o, m] of [[M, mintA], [M, mintB], [T, mintA], [T, mintB], [X, mintA]])
    await send(new Transaction().add(createAssociatedTokenAccountInstruction(payer.publicKey, ata(o.publicKey, m), o.publicKey, m, TOKEN_PROGRAM_ID)), [payer]);
  await send(new Transaction().add(createMintToInstruction(mintA, ata(M.publicKey, mintA), payer.publicKey, 1000 * UNIT, [], TOKEN_PROGRAM_ID)), [payer]);
  await send(new Transaction().add(createMintToInstruction(mintB, ata(T.publicKey, mintB), payer.publicKey, 1000 * UNIT, [], TOKEN_PROGRAM_ID)), [payer]);
  log({ step: 'setup: two 6-decimal mints, five ATAs, balances minted', ok: true });
  const accts = (k, id) => { const state = escrowOf(k.publicKey, id); return { state, vault: vaultOf(state, mintA) }; };
  const create = (k, id, dep, want) => { const { state, vault } = accts(k, id); return prog(k).methods.createEscrow(new BN(id), new BN(dep * UNIT), new BN(want * UNIT)).accounts({ maker: k.publicKey, mintA, mintB, makerTokenAccountA: ata(k.publicKey, mintA), gifterEscrowState: state, escrowVault: vault, systemProgram: SystemProgram.programId, associatedTokenProgram: ASSOCIATED_TOKEN_PROGRAM_ID, tokenProgram: TOKEN_PROGRAM_ID }).rpc(); };
  const refund = (k, id) => { const { state, vault } = accts(k, id); return prog(k).methods.refund().accounts({ maker: k.publicKey, mintA, makerTokenAccountA: ata(k.publicKey, mintA), gifterEscrowState: state, escrowVault: vault, systemProgram: SystemProgram.programId, associatedTokenProgram: ASSOCIATED_TOKEN_PROGRAM_ID, tokenProgram: TOKEN_PROGRAM_ID }).rpc(); };
  const take = (t, maker, id) => { const state = escrowOf(maker, id); return prog(t).methods.takeAndClose().accounts({ maker, taker: t.publicKey, mintA, mintB, makerTokenAccountB: ata(maker, mintB), takerTokenAccountA: ata(t.publicKey, mintA), takerTokenAccountB: ata(t.publicKey, mintB), gifterEscrowState: state, escrowVault: vaultOf(state, mintA), systemProgram: SystemProgram.programId, associatedTokenProgram: ASSOCIATED_TOKEN_PROGRAM_ID, tokenProgram: TOKEN_PROGRAM_ID }).rpc(); };
  const positive = async (step, fn, check) => { try { const sig = await fn(); const c = check ? await check() : { ok: true }; if (!c.ok) fail(step, `post-condition failed: ${JSON.stringify(c)}`); else log({ step, ok: true, sig, ...c }); } catch (e) { fail(step, errText(e)); } };
  const negative = async (step, fn) => { try { const sig = await fn(); fail(step, `UNEXPECTED SUCCESS ${sig}`); } catch (e) { log({ step, ok: true, expectedRejection: errText(e) }); } };

  await positive('create escrow #1 (deposit 10 A, want 5 B)', () => create(M, 1, 10, 5), async () => ({ ok: (await tok(accts(M, 1).vault)) === 10 * UNIT, vault: (await tok(accts(M, 1).vault)) / UNIT }));
  await negative('create escrow #1 again is rejected', () => create(M, 1, 10, 5));
  await negative("outsider cannot refund maker's escrow", () => refund(X, 1));
  const tA0 = await tok(ata(T.publicKey, mintA)), mB0 = await tok(ata(M.publicKey, mintB));
  await positive('take_and_close #1 swaps and closes', () => take(T, M.publicKey, 1), async () => {
    const tGain = (await tok(ata(T.publicKey, mintA))) - tA0, mGain = (await tok(ata(M.publicKey, mintB))) - mB0;
    const vaultClosed = !(await conn.getAccountInfo(accts(M, 1).vault)), stateClosed = !(await conn.getAccountInfo(accts(M, 1).state));
    return { ok: tGain === 10 * UNIT && mGain === 5 * UNIT && vaultClosed && stateClosed, takerGainA: tGain / UNIT, makerGainB: mGain / UNIT, vaultClosed, stateClosed };
  });
  await negative('take_and_close #1 again is rejected', () => take(T, M.publicKey, 1));
  await positive('create escrow #2 wanting more than the taker holds', () => create(M, 2, 1, 10000));
  await negative('take_and_close #2 with insufficient mint B is rejected', () => take(T, M.publicKey, 2));
  const mA0 = await tok(ata(M.publicKey, mintA));
  await positive('refund #2 returns the deposit', () => refund(M, 2), async () => { const g = (await tok(ata(M.publicKey, mintA))) - mA0; return { ok: g === 1 * UNIT, makerRefundA: g / UNIT }; });
}

main().catch((e) => fail('fixture crashed', errText(e))).finally(() => {
  fs.writeFileSync(process.env.FIXTURE_RESULT || 'fixture-result.json', JSON.stringify({ fixture: 'gifter-escrow-localnet', passed: !failed, steps: results }, null, 2));
  console.log(failed ? 'FIXTURE FAILED' : 'FIXTURE PASSED');
  process.exit(failed ? 1 : 0);
});
