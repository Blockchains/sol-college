import fs from 'fs';
import { Connection, Keypair, PublicKey, SystemProgram, Transaction, TransactionInstruction, Ed25519Program, SYSVAR_INSTRUCTIONS_PUBKEY } from '@solana/web3.js';
import anchor from '@coral-xyz/anchor';
import { ed25519 } from '@noble/curves/ed25519';
const { AnchorProvider, Program, Wallet, BN } = anchor;
const TOKEN_PROGRAM_ID = new PublicKey('TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA');
const ASSOCIATED_TOKEN_PROGRAM_ID = new PublicKey('ATokenGPvbdGVxr1b2hvZbsiqW5xWH25efTNsLJA8knL');
const MINT = new PublicKey('BJMSdujxakjx7qypwfaFCnbkMTNPEYVWTTqnR9eJRL4D');

const idl = JSON.parse(fs.readFileSync(process.argv[2] || '/workspace/deai-work/proof/otomat.json', 'utf8'));
const payer = Keypair.fromSecretKey(Uint8Array.from(JSON.parse(fs.readFileSync(process.env.HOME + '/.config/solana/id.json', 'utf8'))));
const yaml = fs.readFileSync(process.env.HOME + '/.config/solana/cli/config.yml', 'utf8');
const rpc = (yaml.match(/json_rpc_url:\s*(\S+)/) || [])[1];
const programId = new PublicKey(idl.address);
const conn = new Connection(rpc, 'confirmed');
const payee = Keypair.generate();
const prog = new Program(idl, new AnchorProvider(conn, new Wallet(payer), { commitment: 'confirmed' }));
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

const DEPOSIT = 2_000_000;
const PAY = 1_000_000;
const [channel] = PublicKey.findProgramAddressSync(
  [Buffer.from('channel'), payer.publicKey.toBuffer(), payee.publicKey.toBuffer(), MINT.toBuffer()],
  programId
);
const [escrowAuth] = PublicKey.findProgramAddressSync(
  [Buffer.from('escrow_auth'), channel.toBuffer()],
  programId
);
const escrowAta = PublicKey.findProgramAddressSync(
  [escrowAuth.toBuffer(), TOKEN_PROGRAM_ID.toBuffer(), MINT.toBuffer()],
  ASSOCIATED_TOKEN_PROGRAM_ID
)[0];
const payerAta = await ensureAta(payer.publicKey);
const payeeAta = await ensureAta(payee.publicKey);
await mintTo(payerAta, DEPOSIT);
const expiry = Math.floor(Date.now()/1000) + 3600;
log({ step:'setup', program: programId.toBase58(), channel: channel.toBase58(), escrowAta: escrowAta.toBase58(), payee: payee.publicKey.toBase58(), expiry });

const sOpen = await prog.methods.openChannel(new BN(DEPOSIT), new BN(expiry), payer.publicKey)
  .accounts({
    payer: payer.publicKey,
    payee: payee.publicKey,
    mint: MINT,
    channel,
    escrowAuthority: escrowAuth,
    escrowAta,
    payerAta,
    tokenProgram: TOKEN_PROGRAM_ID,
    associatedTokenProgram: ASSOCIATED_TOKEN_PROGRAM_ID,
    systemProgram: SystemProgram.programId,
  }).rpc();
log({ step:'open_channel', ok:true, sig:sOpen, vaultBal: (await tokenBal(escrowAta)).toString() });
console.log('SIG open_channel', sOpen);

// negative: close without ed25519 pre-instruction
const dummySig = Buffer.alloc(64);
try {
  const bad = await prog.methods.closeChannel(new BN(PAY), new BN(1), Array.from(dummySig)).accounts({
    facilitator: payer.publicKey,
    channel,
    payer: payer.publicKey,
    payee: payee.publicKey,
    mint: MINT,
    escrowAuthority: escrowAuth,
    escrowAta,
    payeeAta,
    payerAta,
    instructions: SYSVAR_INSTRUCTIONS_PUBKEY,
    tokenProgram: TOKEN_PROGRAM_ID,
    systemProgram: SystemProgram.programId,
  }).rpc();
  log({ step:'negative_no_ed25519', ok:false, error:'UNEXPECTED SUCCESS', sig:bad });
  throw new Error('close without ed25519 unexpectedly succeeded');
} catch (e) {
  if (String(e.message).includes('unexpectedly succeeded')) throw e;
  log({ step:'negative_no_ed25519', expectedFailure:true, error: String(e.error?.errorCode?.code || e.error?.errorMessage || e.message).split('\n')[0].slice(0,240) });
}

const nonce = 1n;
const msg = Buffer.concat([
  Buffer.from('otomat/v2/check|'),
  channel.toBuffer(),
  Buffer.from(new BN(PAY).toArray('le', 8)),
  Buffer.from(new BN(Number(nonce)).toArray('le', 8)),
  Buffer.from(new BN(expiry).toArray('le', 8)),
]);
const signature = Buffer.from(ed25519.sign(msg, payer.secretKey.slice(0, 32)));
const edIx = Ed25519Program.createInstructionWithPublicKey({
  publicKey: payer.publicKey.toBytes(),
  message: msg,
  signature,
});

const beforePayee = await tokenBal(payeeAta);
const sClose = await prog.methods.closeChannel(new BN(PAY), new BN(Number(nonce)), Array.from(signature))
  .accounts({
    facilitator: payer.publicKey,
    channel,
    payer: payer.publicKey,
    payee: payee.publicKey,
    mint: MINT,
    escrowAuthority: escrowAuth,
    escrowAta,
    payeeAta,
    payerAta,
    instructions: SYSVAR_INSTRUCTIONS_PUBKEY,
    tokenProgram: TOKEN_PROGRAM_ID,
    systemProgram: SystemProgram.programId,
  }).preInstructions([edIx]).rpc();
const payeeDelta = (await tokenBal(payeeAta)) - beforePayee;
const escrowLeft = await tokenBal(escrowAta);
const channelAcc = await conn.getAccountInfo(channel);
log({ step:'close_channel', ok:true, sig:sClose, payeeDelta: payeeDelta.toString(), escrowLeft: escrowLeft.toString(), channelClosed: !channelAcc });
console.log('SIG close_channel', sClose);
if (payeeDelta !== BigInt(PAY)) throw new Error('payee did not receive '+PAY+' got '+payeeDelta);
log({ step:'DONE', ok:true });
process.exit(0);
