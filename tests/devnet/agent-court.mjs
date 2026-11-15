import fs from 'fs';
import { Connection, Keypair, PublicKey, SystemProgram, Transaction, TransactionInstruction } from '@solana/web3.js';
import anchor from '@coral-xyz/anchor';
const { AnchorProvider, Program, Wallet, BN } = anchor;
const TOKEN_PROGRAM_ID = new PublicKey('TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA');
const ASSOCIATED_TOKEN_PROGRAM_ID = new PublicKey('ATokenGPvbdGVxr1b2hvZbsiqW5xWH25efTNsLJA8knL');
const MINT = new PublicKey('BJMSdujxakjx7qypwfaFCnbkMTNPEYVWTTqnR9eJRL4D');

const idl = JSON.parse(fs.readFileSync(process.argv[2] || '/workspace/deai-work/proof/agent-court.json', 'utf8'));
const payer = Keypair.fromSecretKey(Uint8Array.from(JSON.parse(fs.readFileSync(process.env.HOME + '/.config/solana/id.json', 'utf8'))));
const yaml = fs.readFileSync(process.env.HOME + '/.config/solana/cli/config.yml', 'utf8');
const rpc = (yaml.match(/json_rpc_url:\s*(\S+)/) || [])[1];
const programId = new PublicKey(idl.address);
const conn = new Connection(rpc, 'confirmed');
const agentB = Keypair.generate();
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
async function tokenBal(pk) { return BigInt((await conn.getTokenAccountBalance(pk)).value.amount); }

const serviceHash = Buffer.alloc(32, 21); serviceHash.write('court-job-1');
const [escrow] = PublicKey.findProgramAddressSync(
  [Buffer.from('escrow'), payer.publicKey.toBuffer(), agentB.publicKey.toBuffer(), serviceHash],
  programId
);
const [vault] = PublicKey.findProgramAddressSync([Buffer.from('vault'), escrow.toBuffer()], programId);
const aAta = await ensureAta(payer.publicKey);
const bAta = await ensureAta(agentB.publicKey);
await sendIx([SystemProgram.transfer({ fromPubkey: payer.publicKey, toPubkey: agentB.publicKey, lamports: 20_000_000 })], [payer]);
await mintTo(aAta, 2_000_000);
log({ step:'setup', program: programId.toBase58(), escrow: escrow.toBase58(), vault: vault.toBase58(), agentB: agentB.publicKey.toBase58() });

const sD = await prog.methods.deposit(new BN(1_000_000), Array.from(serviceHash), new BN(3600))
  .accounts({
    agentA: payer.publicKey,
    agentB: agentB.publicKey,
    mint: MINT,
    escrow,
    vault,
    agentATokenAccount: aAta,
    tokenProgram: TOKEN_PROGRAM_ID,
    associatedTokenProgram: ASSOCIATED_TOKEN_PROGRAM_ID,
    systemProgram: SystemProgram.programId,
  }).rpc();
log({ step:'deposit', ok:true, sig:sD, vaultBal: (await tokenBal(vault)).toString() });
console.log('SIG deposit', sD);

const sF = await prog.methods.fileDispute()
  .accounts({ signer: payer.publicKey, escrow }).rpc();
log({ step:'file_dispute', ok:true, sig:sF });
console.log('SIG file_dispute', sF);

const sV = await prog.methods.renderVerdict({ release: {} }, 0, 0)
  .accounts({ judge: payer.publicKey, escrow }).rpc();
log({ step:'render_verdict', ok:true, sig:sV, verdict:'Release' });
console.log('SIG render_verdict', sV);

const beforeB = await tokenBal(bAta);
const sC = await prog.methods.claim()
  .accounts({
    claimer: payer.publicKey,
    escrow,
    vault,
    mint: MINT,
    agentATokenAccount: aAta,
    agentBTokenAccount: bAta,
    agentA: payer.publicKey,
    tokenProgram: TOKEN_PROGRAM_ID,
  }).rpc();
const afterB = await tokenBal(bAta);
log({ step:'claim', ok:true, sig:sC, agentBDelta: (afterB-beforeB).toString() });
console.log('SIG claim', sC);
if (afterB-beforeB !== 1_000_000n) throw new Error('agent_b did not receive 1_000_000, got '+(afterB-beforeB));
log({ step:'DONE', ok:true });
process.exit(0);
