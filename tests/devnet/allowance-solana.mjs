import fs from 'fs';
import { Connection, Keypair, PublicKey, SystemProgram, Transaction, TransactionInstruction, SYSVAR_RENT_PUBKEY } from '@solana/web3.js';
import anchor from '@coral-xyz/anchor';
const { AnchorProvider, Program, Wallet, BN } = anchor;
const TOKEN_PROGRAM_ID = new PublicKey('TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA');
const ASSOCIATED_TOKEN_PROGRAM_ID = new PublicKey('ATokenGPvbdGVxr1b2hvZbsiqW5xWH25efTNsLJA8knL');
const MINT = new PublicKey('BJMSdujxakjx7qypwfaFCnbkMTNPEYVWTTqnR9eJRL4D');

const idl = JSON.parse(fs.readFileSync(process.argv[2] || '/workspace/deai-work/proof/allowance.json', 'utf8'));
const payer = Keypair.fromSecretKey(Uint8Array.from(JSON.parse(fs.readFileSync(process.env.HOME + '/.config/solana/id.json', 'utf8'))));
const yaml = fs.readFileSync(process.env.HOME + '/.config/solana/cli/config.yml', 'utf8');
const rpc = (yaml.match(/json_rpc_url:\s*(\S+)/) || [])[1];
const programId = new PublicKey(idl.address);
const conn = new Connection(rpc, 'confirmed');
const agent = Keypair.generate();
const merchant = Keypair.generate();
const prog = new Program(idl, new AnchorProvider(conn, new Wallet(payer), { commitment: 'confirmed' }));
const agentProg = new Program(idl, new AnchorProvider(conn, new Wallet(agent), { commitment: 'confirmed' }));
const log = (o) => { console.log(JSON.stringify(o)); if (process.env.PROOF_LOG) fs.appendFileSync(process.env.PROOF_LOG, JSON.stringify(o)+'\n'); };

function ata(owner) {
  return PublicKey.findProgramAddressSync(
    [owner.toBuffer(), TOKEN_PROGRAM_ID.toBuffer(), MINT.toBuffer()],
    ASSOCIATED_TOKEN_PROGRAM_ID
  )[0];
}
async function sendIx(ixs, signers) {
  const tx = new Transaction().add(...ixs);
  tx.feePayer = payer.publicKey;
  tx.recentBlockhash = (await conn.getLatestBlockhash()).blockhash;
  tx.sign(...signers);
  const sig = await conn.sendRawTransaction(tx.serialize());
  await conn.confirmTransaction(sig, 'confirmed');
  return sig;
}
async function ensureAta(owner) {
  const dest = ata(owner);
  if (await conn.getAccountInfo(dest)) return dest;
  const ix = new TransactionInstruction({
    programId: ASSOCIATED_TOKEN_PROGRAM_ID,
    keys: [
      { pubkey: payer.publicKey, isSigner: true, isWritable: true },
      { pubkey: dest, isSigner: false, isWritable: true },
      { pubkey: owner, isSigner: false, isWritable: false },
      { pubkey: MINT, isSigner: false, isWritable: false },
      { pubkey: SystemProgram.programId, isSigner: false, isWritable: false },
      { pubkey: TOKEN_PROGRAM_ID, isSigner: false, isWritable: false },
    ],
    data: Buffer.from([0]),
  });
  await sendIx([ix], [payer]);
  return dest;
}
async function mintTo(dest, amount) {
  const data = Buffer.alloc(9); data[0]=7; data.writeBigUInt64LE(BigInt(amount),1);
  const ix = new TransactionInstruction({
    programId: TOKEN_PROGRAM_ID,
    keys: [
      { pubkey: MINT, isSigner: false, isWritable: true },
      { pubkey: dest, isSigner: false, isWritable: true },
      { pubkey: payer.publicKey, isSigner: true, isWritable: false },
    ],
    data,
  });
  return sendIx([ix], [payer]);
}
async function tokenBal(pk) { return BigInt((await conn.getTokenAccountBalance(pk)).value.amount); }

const [vault] = PublicKey.findProgramAddressSync([Buffer.from('vault'), payer.publicKey.toBuffer()], programId);
const [session] = PublicKey.findProgramAddressSync([Buffer.from('session'), vault.toBuffer(), agent.publicKey.toBuffer()], programId);
const vaultAta = ata(vault);
const ownerAta = await ensureAta(payer.publicKey);
const merchantAta = await ensureAta(merchant.publicKey);
await sendIx([SystemProgram.transfer({ fromPubkey: payer.publicKey, toPubkey: agent.publicKey, lamports: 20_000_000 })], [payer]);
await mintTo(ownerAta, 5_000_000);
log({ step:'setup', program: programId.toBase58(), vault: vault.toBase58(), session: session.toBase58(), agent: agent.publicKey.toBase58(), merchant: merchant.publicKey.toBase58() });

if (!(await conn.getAccountInfo(vault))) {
  const s = await prog.methods.initVault()
    .accounts({
      owner: payer.publicKey,
      vault,
      mint: MINT,
      vaultAta,
      tokenProgram: TOKEN_PROGRAM_ID,
      associatedTokenProgram: ASSOCIATED_TOKEN_PROGRAM_ID,
      systemProgram: SystemProgram.programId,
    }).rpc();
  log({ step:'init_vault', ok:true, sig:s });
  console.log('SIG init_vault', s);
} else {
  log({ step:'init_vault', skipped:true });
}

const vaultBal0 = (await conn.getAccountInfo(vaultAta)) ? await tokenBal(vaultAta) : 0n;
if (vaultBal0 < 3_000_000n) {
  await mintTo(ownerAta, 5_000_000);
  const sDep = await prog.methods.deposit(new BN(5_000_000))
    .accounts({
      owner: payer.publicKey,
      vault,
      mint: MINT,
      ownerAta,
      vaultAta,
      tokenProgram: TOKEN_PROGRAM_ID,
    }).rpc();
  log({ step:'deposit', ok:true, sig:sDep, vaultBal: (await tokenBal(vaultAta)).toString() });
  console.log('SIG deposit', sDep);
} else {
  log({ step:'deposit', skipped:true, vaultBal: vaultBal0.toString() });
}

const now = Math.floor(Date.now()/1000);
const params = {
  perRequestCap: new BN(1_000_000),
  dailyCap: new BN(3_000_000),
  otherDailyCap: new BN(0),
  minReputation: 0,
  expiresAt: new BN(now + 86400),
  merchants: [{ merchant: merchant.publicKey, label: 'lab-shop', dailyCap: new BN(2_000_000) }],
};
if (!(await conn.getAccountInfo(session))) {
  const sSess = await prog.methods.createSession(params)
    .accounts({
      owner: payer.publicKey,
      vault,
      agent: agent.publicKey,
      session,
      systemProgram: SystemProgram.programId,
    }).rpc();
  log({ step:'create_session', ok:true, sig:sSess });
  console.log('SIG create_session', sSess);
} else {
  log({ step:'create_session', skipped:true });
}

try {
  await agentProg.methods.agentPay(new BN(2_000_000), 'over cap lab')
    .accountsPartial({
      agent: agent.publicKey,
      vault,
      session,
      mint: MINT,
      vaultAta,
      merchant: merchant.publicKey,
      merchantAta,
      registryAgent: programId,
      atomStats: programId,
      pending: programId,
      tokenProgram: TOKEN_PROGRAM_ID,
    }).rpc();
  throw new Error('over-cap agent_pay unexpectedly succeeded');
} catch (e) {
  if (String(e.message).includes('unexpectedly succeeded')) throw e;
  log({ step:'negative_over_cap', expectedFailure:true, error: String(e.error?.errorCode?.code || e.error?.errorMessage || e.message).split('\n')[0].slice(0,240) });
}

const beforeMerch = await tokenBal(merchantAta);
const sPay = await agentProg.methods.agentPay(new BN(1_000_000), 'lab purchase')
  .accountsPartial({
    agent: agent.publicKey,
    vault,
    session,
    mint: MINT,
    vaultAta,
    merchant: merchant.publicKey,
    merchantAta,
    registryAgent: programId,
    atomStats: programId,
    pending: programId,
    tokenProgram: TOKEN_PROGRAM_ID,
  }).rpc();
const afterMerch = await tokenBal(merchantAta);
log({ step:'agent_pay', ok:true, sig:sPay, merchantDelta: (afterMerch-beforeMerch).toString() });
console.log('SIG agent_pay', sPay);
if (afterMerch-beforeMerch !== 1_000_000n) throw new Error('merchant did not receive 1_000_000');

const beforeOwner = await tokenBal(ownerAta);
const left = await tokenBal(vaultAta);
const sW = await prog.methods.withdraw(new BN(left.toString()))
  .accounts({
    owner: payer.publicKey,
    vault,
    mint: MINT,
    ownerAta,
    vaultAta,
    tokenProgram: TOKEN_PROGRAM_ID,
  }).rpc();
const afterOwner = await tokenBal(ownerAta);
log({ step:'withdraw', ok:true, sig:sW, ownerDelta: (afterOwner-beforeOwner).toString(), vaultLeft: (await tokenBal(vaultAta)).toString() });
console.log('SIG withdraw', sW);
log({ step:'DONE', ok:true });
process.exit(0);
