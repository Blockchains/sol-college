import fs from 'fs';
import { Connection, Keypair, PublicKey, SystemProgram, Transaction, TransactionInstruction, SYSVAR_RENT_PUBKEY } from '@solana/web3.js';
import anchor from '@coral-xyz/anchor';
const { AnchorProvider, Program, Wallet, BN } = anchor;
const TOKEN_PROGRAM_ID = new PublicKey('TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA');
const ASSOCIATED_TOKEN_PROGRAM_ID = new PublicKey('ATokenGPvbdGVxr1b2hvZbsiqW5xWH25efTNsLJA8knL');
const MINT = new PublicKey('BJMSdujxakjx7qypwfaFCnbkMTNPEYVWTTqnR9eJRL4D');

const idl = JSON.parse(fs.readFileSync(process.argv[2] || '/workspace/deai-work/proof/escrowagent.json', 'utf8'));
const payer = Keypair.fromSecretKey(Uint8Array.from(JSON.parse(fs.readFileSync(process.env.HOME + '/.config/solana/id.json', 'utf8'))));
const yaml = fs.readFileSync(process.env.HOME + '/.config/solana/cli/config.yml', 'utf8');
const rpc = (yaml.match(/json_rpc_url:\s*(\S+)/) || [])[1];
const programId = new PublicKey(idl.address);
const conn = new Connection(rpc, 'confirmed');
const providerKp = Keypair.generate();
const prog = new Program(idl, new AnchorProvider(conn, new Wallet(payer), { commitment: 'confirmed' }));
const providerProg = new Program(idl, new AnchorProvider(conn, new Wallet(providerKp), { commitment: 'confirmed' }));
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
async function tokenBal(pk) {
  const i = await conn.getAccountInfo(pk);
  if (!i) return 0n;
  return BigInt((await conn.getTokenAccountBalance(pk)).value.amount);
}

const [config] = PublicKey.findProgramAddressSync([Buffer.from('protocol_config')], programId);
const taskHash = Buffer.alloc(32, 11); taskHash.write('ea-job-1');
const [escrow] = PublicKey.findProgramAddressSync(
  [Buffer.from('escrow'), payer.publicKey.toBuffer(), providerKp.publicKey.toBuffer(), taskHash],
  programId
);
const [vault] = PublicKey.findProgramAddressSync([Buffer.from('vault'), escrow.toBuffer()], programId);
const [vaultAuth] = PublicKey.findProgramAddressSync([Buffer.from('vault_authority'), escrow.toBuffer()], programId);
const clientAta = await ensureAta(payer.publicKey);
const providerAta = await ensureAta(providerKp.publicKey);
const feeAta = clientAta; // fee_authority = payer, fee bps = 0
await sendIx([SystemProgram.transfer({ fromPubkey: payer.publicKey, toPubkey: providerKp.publicKey, lamports: 30_000_000 })], [payer]);
await mintTo(clientAta, 2_000_000);
log({ step:'setup', program: programId.toBase58(), config: config.toBase58(), escrow: escrow.toBase58(), vault: vault.toBase58(), provider: providerKp.publicKey.toBase58() });

if (!(await conn.getAccountInfo(config))) {
  const s = await prog.methods.initializeProtocol(
      payer.publicKey, 0, 0, new BN(1), new BN(0), new BN(1), new BN(7*86400)
    )
    .accounts({
      admin: payer.publicKey,
      config,
      systemProgram: SystemProgram.programId,
    }).rpc();
  log({ step:'initialize_protocol', ok:true, sig:s });
  console.log('SIG initialize_protocol', s);
} else {
  log({ step:'initialize_protocol', skipped:true });
}

const now = Math.floor(Date.now()/1000);
const sC = await prog.methods.createEscrow(
    new BN(1_000_000), new BN(now + 3600), new BN(1), Array.from(taskHash),
    { multiSigConfirm: {} }, 0
  )
  .accounts({
    client: payer.publicKey,
    provider: providerKp.publicKey,
    arbitrator: PublicKey.default,
    config,
    escrow,
    tokenMint: MINT,
    clientTokenAccount: clientAta,
    escrowVault: vault,
    escrowVaultAuthority: vaultAuth,
    tokenProgram: TOKEN_PROGRAM_ID,
    systemProgram: SystemProgram.programId,
    rent: SYSVAR_RENT_PUBKEY,
  }).rpc();
log({ step:'create_escrow', ok:true, sig:sC, vaultBal: (await tokenBal(vault)).toString() });
console.log('SIG create_escrow', sC);

const sA = await providerProg.methods.acceptEscrow()
  .accounts({ provider: providerKp.publicKey, config, escrow }).rpc();
log({ step:'accept_escrow', ok:true, sig:sA });
console.log('SIG accept_escrow', sA);

const proof = Buffer.alloc(64, 3);
const sP = await providerProg.methods.submitProof({ signedConfirmation: {} }, Array.from(proof))
  .accounts({ provider: providerKp.publicKey, config, escrow }).rpc();
log({ step:'submit_proof', ok:true, sig:sP });
console.log('SIG submit_proof', sP);

const beforeProv = await tokenBal(providerAta);
const sF = await prog.methods.confirmCompletion()
  .accounts({
    client: payer.publicKey,
    config,
    escrow,
    escrowVault: vault,
    escrowVaultAuthority: vaultAuth,
    providerTokenAccount: providerAta,
    protocolFeeAccount: feeAta,
    clientTokenAccount: clientAta,
    tokenProgram: TOKEN_PROGRAM_ID,
  }).rpc();
const afterProv = await tokenBal(providerAta);
log({ step:'confirm_completion', ok:true, sig:sF, providerDelta: (afterProv-beforeProv).toString(), escrowClosed: !(await conn.getAccountInfo(escrow)) });
console.log('SIG confirm_completion', sF);
if (afterProv-beforeProv !== 1_000_000n) throw new Error('provider did not receive 1_000_000, got '+(afterProv-beforeProv));
log({ step:'DONE', ok:true });
process.exit(0);
