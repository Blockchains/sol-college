// Sol.College Squads V4 lab: devnet end-to-end flow with success, rejection and recovery cases.
// Usage: DEVNET_RPC=... KEYS=/path/to/keys node squads-v4.mjs > log.jsonl
// Keys are read from $KEYS and never printed. Each run creates a NEW multisig (fresh createKey), so a run is also the reset procedure.
import * as multisig from '@sqds/multisig';
import { Connection, Keypair, PublicKey, SystemProgram, Transaction, TransactionMessage, LAMPORTS_PER_SOL, sendAndConfirmTransaction } from '@solana/web3.js';
import fs from 'fs';
import assert from 'assert';

const RPC = process.env.DEVNET_RPC || 'https://api.devnet.solana.com';
const KEYS = process.env.KEYS || '/workspace/sol-college/keys/portfolio';
const PROGRAM_ID = new PublicKey('TZNQuhC8PSqQY7Szj9RJsMQirVooYSahh396QNqTMGU');
const FAUCET_NEVER = '58nzDwjUmR6jqCEGkvAkNt4EcdmYvf8xHzazUnELUMsp';
const conn = new Connection(RPC, 'confirmed');
const kp = (f) => Keypair.fromSecretKey(Uint8Array.from(JSON.parse(fs.readFileSync(f))));
const deployer = kp(process.env.DEPLOYER || '/home/box/.config/solana/id.json');
assert(deployer.publicKey.toBase58() !== FAUCET_NEVER, 'refusing to use the faucet wallet');
const K = (n) => kp(`${KEYS}/squads-${n}.json`);
const initializer = K('config-initializer'), treasury = K('treasury').publicKey;
const A = K('member-a'), B = K('member-b'), C = K('member-c'), outsider = K('outsider'), creator = K('creator');
const { Permissions } = multisig.types;
const log = (o) => console.log(JSON.stringify({ t: new Date().toISOString(), ...o }));
const opts = { programId: PROGRAM_ID, sendOptions: { skipPreflight: false } };
const sigs = [];
async function ok(step, p) {
  const sig = await p; await conn.confirmTransaction(sig, 'confirmed');
  const st = await conn.getSignatureStatus(sig, { searchTransactionHistory: true });
  assert(!st.value?.err, `${step} errored on-chain`);
  log({ step, ok: true, sig }); sigs.push([step, sig]); return sig;
}
async function mustFail(step, p, expect) {
  try { const sig = await p; await conn.confirmTransaction(sig, 'confirmed'); const st = await conn.getSignatureStatus(sig);
    if (!st.value?.err) { log({ step, ok: false, unexpected_success: sig }); throw new Error(`NEGATIVE CASE SUCCEEDED: ${step}`); }
    log({ step, rejected: true, sig, err: st.value.err }); return;
  } catch (e) {
    if (String(e.message).startsWith('NEGATIVE CASE SUCCEEDED')) throw e;
    const text = [e.message, ...(e.logs || e.transactionLogs || [])].join(' | ');
    const hit = expect.find((x) => text.includes(x));
    if (!hit) { log({ step, rejected: true, unexpected_error: text.slice(0, 600) }); throw new Error(`${step}: wrong error`); }
    log({ step, rejected: true, error: hit });
  }
}
async function fund(to, lamports, step) {
  const tx = new Transaction().add(SystemProgram.transfer({ fromPubkey: deployer.publicKey, toPubkey: to, lamports }));
  const sig = await sendAndConfirmTransaction(conn, tx, [deployer], { commitment: 'confirmed' });
  log({ step, ok: true, sig }); sigs.push([step, sig]); return sig;
}
const all = Permissions.all();

// 0. One-time program config (the lab's own initializer key, never the Squads team key)
const [programConfig] = multisig.getProgramConfigPda({ programId: PROGRAM_ID });
if (!(await conn.getAccountInfo(programConfig))) {
  if ((await conn.getBalance(initializer.publicKey)) < 0.01 * LAMPORTS_PER_SOL) await fund(initializer.publicKey, 0.01 * LAMPORTS_PER_SOL, 'fund lab config initializer');
  await mustFail('program_config_init by a non-initializer key is rejected', (async () => {
    const ix = multisig.generated.createProgramConfigInitInstruction({ programConfig, initializer: outsider.publicKey },
      { args: { authority: outsider.publicKey, multisigCreationFee: 0, treasury } }, PROGRAM_ID);
    const tx = new Transaction().add(ix); return await sendAndConfirmTransaction(conn, tx, [deployer, outsider]);
  })(), ['Unauthorized', '0x1786', 'custom program error']);
  await ok('program_config_init (lab initializer, fee 0, lab treasury)', (async () => {
    const ix = multisig.generated.createProgramConfigInitInstruction({ programConfig, initializer: initializer.publicKey },
      { args: { authority: initializer.publicKey, multisigCreationFee: 0, treasury } }, PROGRAM_ID);
    const tx = new Transaction().add(ix); return await sendAndConfirmTransaction(conn, tx, [deployer, initializer]);
  })());
} else log({ step: 'program config already initialised', programConfig: programConfig.toBase58() });
const cfg = await multisig.accounts.ProgramConfig.fromAccountAddress(conn, programConfig);
assert(cfg.treasury.equals(treasury)); log({ step: 'read program config', authority: cfg.authority.toBase58(), treasury: cfg.treasury.toBase58(), fee: cfg.multisigCreationFee.toString() });

// 1. Create the multisig: two practice members, threshold 1. Creator pays rent.
if ((await conn.getBalance(creator.publicKey)) < 0.01 * LAMPORTS_PER_SOL) await fund(creator.publicKey, 0.02 * LAMPORTS_PER_SOL, 'fund practice creator');
// Note: @sqds/multisig 2.1.4 rpc.proposalCreate drops its rentPayer argument (the proposal rent is always taken from the
// creator), so each practice member holds a little devnet SOL for proposal rent. See the improvement backlog.
for (const [n, m] of [['A', A], ['B', B], ['C', C]]) if ((await conn.getBalance(m.publicKey)) < 0.006 * LAMPORTS_PER_SOL) await fund(m.publicKey, 0.01 * LAMPORTS_PER_SOL, `fund practice member ${n} (proposal rent)`);
const createKey = Keypair.generate();
const [msPda] = multisig.getMultisigPda({ createKey: createKey.publicKey, programId: PROGRAM_ID });
const [vault] = multisig.getVaultPda({ multisigPda: msPda, index: 0, programId: PROGRAM_ID });
log({ step: 'addresses', multisig: msPda.toBase58(), vault: vault.toBase58() });
await ok('multisig_create_v2: members A,B (all permissions), threshold 1', multisig.rpc.multisigCreateV2({ connection: conn, treasury, createKey, creator,
  multisigPda: msPda, configAuthority: null, threshold: 1, members: [{ key: A.publicKey, permissions: all }, { key: B.publicKey, permissions: all }],
  timeLock: 0, rentCollector: vault, ...opts }));

const common = { connection: conn, feePayer: deployer, multisigPda: msPda, ...opts };
const nextIndex = async () => BigInt((await multisig.accounts.Multisig.fromAccountAddress(conn, msPda)).transactionIndex.toString()) + 1n;

// 2. Config transaction: add member C and raise threshold to 2 (approved under threshold 1)
let i = await nextIndex();
await ok(`config_transaction_create #${i}: AddMember C + ChangeThreshold 2`, multisig.rpc.configTransactionCreate({ ...common, transactionIndex: i, creator: A.publicKey,
  rentPayer: deployer.publicKey, signers: [A, deployer], actions: [{ __kind: 'AddMember', newMember: { key: C.publicKey, permissions: all } }, { __kind: 'ChangeThreshold', newThreshold: 2 }] }));
await ok(`proposal_create #${i} by A`, multisig.rpc.proposalCreate({ ...common, transactionIndex: i, creator: A }));
await ok(`proposal_approve #${i} by A`, multisig.rpc.proposalApprove({ ...common, transactionIndex: i, member: A }));
await ok(`config_transaction_execute #${i} by A`, multisig.rpc.configTransactionExecute({ ...common, transactionIndex: i, member: A, rentPayer: deployer }));
let ms = await multisig.accounts.Multisig.fromAccountAddress(conn, msPda);
assert.equal(ms.threshold, 2); assert.equal(ms.members.length, 3);
log({ step: 'multisig after config', threshold: ms.threshold, members: ms.members.map((m) => m.key.toBase58()) });

// 3. Fund the VAULT (never the multisig account)
const FUND = 0.03 * LAMPORTS_PER_SOL, SEND = 0.01 * LAMPORTS_PER_SOL;
const msRentBefore = await conn.getBalance(msPda);
await fund(vault, FUND, 'fund vault PDA index 0 (not the multisig account)');
assert.equal(await conn.getBalance(msPda), msRentBefore, 'multisig account must not receive funds');

const recipient = Keypair.generate().publicKey;
const transferMsg = (lamports) => new TransactionMessage({ payerKey: vault, recentBlockhash: PublicKey.default.toBase58(),
  instructions: [SystemProgram.transfer({ fromPubkey: vault, toPubkey: recipient, lamports })] });

// 4. Unauthorised signer cannot create a transaction or proposal
i = await nextIndex();
await mustFail('vault_transaction_create by a non-member is rejected', multisig.rpc.vaultTransactionCreate({ ...common, transactionIndex: i, creator: outsider.publicKey,
  rentPayer: deployer.publicKey, signers: [outsider, deployer], vaultIndex: 0, ephemeralSigners: 0, transactionMessage: transferMsg(SEND) }), ['NotAMember', '0x1771']);

// 5. Threshold transfer with negative cases
await ok(`vault_transaction_create #${i}: vault -> recipient 0.01 SOL`, multisig.rpc.vaultTransactionCreate({ ...common, transactionIndex: i, creator: A.publicKey,
  rentPayer: deployer.publicKey, signers: [A, deployer], vaultIndex: 0, ephemeralSigners: 0, transactionMessage: transferMsg(SEND), memo: 'sol-college lab transfer' }));
await ok(`proposal_create #${i} by A`, multisig.rpc.proposalCreate({ ...common, transactionIndex: i, creator: A }));
await mustFail(`proposal_approve #${i} by outsider is rejected`, multisig.rpc.proposalApprove({ ...common, transactionIndex: i, member: outsider }), ['NotAMember', '0x1771']);
await ok(`proposal_approve #${i} by A (1 of 2)`, multisig.rpc.proposalApprove({ ...common, transactionIndex: i, member: A }));
await mustFail(`vault_transaction_execute #${i} with 1 of 2 approvals is rejected`, multisig.rpc.vaultTransactionExecute({ ...common, transactionIndex: i, member: C.publicKey, signers: [C] }), ['InvalidProposalStatus', '0x177d', '0x177c']);
await mustFail(`proposal_approve #${i} twice by A is rejected`, multisig.rpc.proposalApprove({ ...common, transactionIndex: i, member: A }), ['AlreadyApproved', '0x1779', '0x177a']);
await ok(`proposal_approve #${i} by B (2 of 2)`, multisig.rpc.proposalApprove({ ...common, transactionIndex: i, member: B }));
await mustFail(`vault_transaction_execute #${i} by outsider is rejected`, multisig.rpc.vaultTransactionExecute({ ...common, transactionIndex: i, member: outsider.publicKey, signers: [outsider] }), ['NotAMember', '0x1771']);
const vBefore = await conn.getBalance(vault), rBefore = await conn.getBalance(recipient);
await ok(`vault_transaction_execute #${i} by C`, multisig.rpc.vaultTransactionExecute({ ...common, transactionIndex: i, member: C.publicKey, signers: [C] }));
const vAfter = await conn.getBalance(vault), rAfter = await conn.getBalance(recipient);
assert.equal(rAfter - rBefore, SEND, 'recipient must receive exactly 0.01 SOL'); assert.equal(vBefore - vAfter, SEND, 'vault must lose exactly 0.01 SOL');
log({ step: 'balances after execute', vault_delta: vAfter - vBefore, recipient_delta: rAfter - rBefore });
await mustFail(`vault_transaction_execute #${i} a second time is rejected`, multisig.rpc.vaultTransactionExecute({ ...common, transactionIndex: i, member: C.publicKey, signers: [C] }), ['InvalidProposalStatus', '0x177d', '0x177c']);

// 6. Rejection path: proposal rejected by 2 members cannot execute
const j = await nextIndex();
await ok(`vault_transaction_create #${j}: second transfer`, multisig.rpc.vaultTransactionCreate({ ...common, transactionIndex: j, creator: B.publicKey,
  rentPayer: deployer.publicKey, signers: [B, deployer], vaultIndex: 0, ephemeralSigners: 0, transactionMessage: transferMsg(SEND) }));
await ok(`proposal_create #${j} by B`, multisig.rpc.proposalCreate({ ...common, transactionIndex: j, creator: B }));
await ok(`proposal_reject #${j} by A`, multisig.rpc.proposalReject({ ...common, transactionIndex: j, member: A }));
await ok(`proposal_reject #${j} by C (rejection cutoff reached)`, multisig.rpc.proposalReject({ ...common, transactionIndex: j, member: C }));
await mustFail(`vault_transaction_execute #${j} after rejection is rejected`, multisig.rpc.vaultTransactionExecute({ ...common, transactionIndex: j, member: B.publicKey, signers: [B] }), ['InvalidProposalStatus', '0x177d', '0x177c']);

// 7. Recovery path: approved proposal is cancelled before execution
const k = await nextIndex();
await ok(`vault_transaction_create #${k}: third transfer`, multisig.rpc.vaultTransactionCreate({ ...common, transactionIndex: k, creator: C.publicKey,
  rentPayer: deployer.publicKey, signers: [C, deployer], vaultIndex: 0, ephemeralSigners: 0, transactionMessage: transferMsg(SEND) }));
await ok(`proposal_create #${k} by C`, multisig.rpc.proposalCreate({ ...common, transactionIndex: k, creator: C }));
await ok(`proposal_approve #${k} by A`, multisig.rpc.proposalApprove({ ...common, transactionIndex: k, member: A }));
await ok(`proposal_approve #${k} by C (approved)`, multisig.rpc.proposalApprove({ ...common, transactionIndex: k, member: C }));
await ok(`proposal_cancel #${k} by A`, multisig.rpc.proposalCancel({ ...common, transactionIndex: k, member: A }));
await ok(`proposal_cancel #${k} by B (cancelled)`, multisig.rpc.proposalCancel({ ...common, transactionIndex: k, member: B }));
await mustFail(`vault_transaction_execute #${k} after cancel is rejected`, multisig.rpc.vaultTransactionExecute({ ...common, transactionIndex: k, member: C.publicKey, signers: [C] }), ['InvalidProposalStatus', '0x177d', '0x177c']);
assert.equal(await conn.getBalance(vault), vAfter, 'vault must be unchanged by rejected/cancelled proposals');

// 8. Inspect proposal history
ms = await multisig.accounts.Multisig.fromAccountAddress(conn, msPda);
const history = [];
for (let n = 1n; n <= BigInt(ms.transactionIndex.toString()); n++) {
  const [p] = multisig.getProposalPda({ multisigPda: msPda, transactionIndex: n, programId: PROGRAM_ID });
  const pr = await multisig.accounts.Proposal.fromAccountAddress(conn, p);
  history.push({ index: Number(n), status: pr.status.__kind, approved: pr.approved.length, rejected: pr.rejected.length, cancelled: pr.cancelled.length });
}
log({ step: 'proposal history', history });
assert.deepEqual(history.map((h) => h.status), ['Executed', 'Executed', 'Rejected', 'Cancelled']);
log({ step: 'DONE', multisig: msPda.toBase58(), vault: vault.toBase58(), vault_lamports: await conn.getBalance(vault), sigs: sigs.length });
process.exit(0);
