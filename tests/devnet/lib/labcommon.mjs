import fs from 'fs';
import { Connection, Keypair, PublicKey, SystemProgram, Transaction, TransactionInstruction } from '@solana/web3.js';
import anchor from '@coral-xyz/anchor';
export const { AnchorProvider, Program, Wallet, BN } = anchor;
export const TOKEN_PROGRAM_ID = new PublicKey('TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA');
export const ASSOCIATED_TOKEN_PROGRAM_ID = new PublicKey('ATokenGPvbdGVxr1b2hvZbsiqW5xWH25efTNsLJA8knL');
export const MINT = new PublicKey('BJMSdujxakjx7qypwfaFCnbkMTNPEYVWTTqnR9eJRL4D');
export const BPF_LOADER = new PublicKey('BPFLoaderUpgradeab1e11111111111111111111111');
export const payer = Keypair.fromSecretKey(Uint8Array.from(JSON.parse(fs.readFileSync(process.env.HOME + '/.config/solana/id.json', 'utf8'))));
const yaml = fs.readFileSync(process.env.HOME + '/.config/solana/cli/config.yml', 'utf8');
const rpc = (yaml.match(/json_rpc_url:\s*(\S+)/) || [])[1];
export const conn = new Connection(rpc, 'confirmed');
export const log = (o) => { console.log(JSON.stringify(o)); if (process.env.PROOF_LOG) fs.appendFileSync(process.env.PROOF_LOG, JSON.stringify(o)+'\n'); };
export function program(idl, kp = payer) { return new Program(idl, new AnchorProvider(conn, new Wallet(kp), { commitment: 'confirmed' })); }
export function ata(owner, mint = MINT) {
  return PublicKey.findProgramAddressSync([owner.toBuffer(), TOKEN_PROGRAM_ID.toBuffer(), mint.toBuffer()], ASSOCIATED_TOKEN_PROGRAM_ID)[0];
}
export async function sendIx(ixs, signers) {
  const tx = new Transaction().add(...ixs);
  tx.feePayer = payer.publicKey;
  tx.recentBlockhash = (await conn.getLatestBlockhash()).blockhash;
  tx.sign(...signers);
  const sig = await conn.sendRawTransaction(tx.serialize());
  await conn.confirmTransaction(sig, 'confirmed');
  return sig;
}
export async function ensureAta(owner, mint = MINT) {
  const dest = ata(owner, mint);
  if (await conn.getAccountInfo(dest)) return dest;
  const ix = new TransactionInstruction({ programId: ASSOCIATED_TOKEN_PROGRAM_ID, keys: [
      { pubkey: payer.publicKey, isSigner: true, isWritable: true },
      { pubkey: dest, isSigner: false, isWritable: true },
      { pubkey: owner, isSigner: false, isWritable: false },
      { pubkey: mint, isSigner: false, isWritable: false },
      { pubkey: SystemProgram.programId, isSigner: false, isWritable: false },
      { pubkey: TOKEN_PROGRAM_ID, isSigner: false, isWritable: false } ], data: Buffer.from([1]) });
  await sendIx([ix], [payer]);
  return dest;
}
export async function mintTo(dest, amount) {
  const data = Buffer.alloc(9); data[0]=7; data.writeBigUInt64LE(BigInt(amount),1);
  return sendIx([new TransactionInstruction({ programId: TOKEN_PROGRAM_ID, keys: [
      { pubkey: MINT, isSigner: false, isWritable: true },
      { pubkey: dest, isSigner: false, isWritable: true },
      { pubkey: payer.publicKey, isSigner: true, isWritable: false } ], data })], [payer]);
}
export async function fund(pk, lamports) { return sendIx([SystemProgram.transfer({ fromPubkey: payer.publicKey, toPubkey: pk, lamports })], [payer]); }
export async function tokenBal(pk) { const i = await conn.getAccountInfo(pk); if (!i) return 0n; return BigInt((await conn.getTokenAccountBalance(pk)).value.amount); }
export async function expectFail(name, fn) {
  try { const s = await fn(); log({ step: name, unexpected_success: true, sig: s }); return false; }
  catch (e) { const m = (e.error?.errorCode?.code) || (e.logs||[]).find(l=>/Error/.test(l)) || String(e.message||e).slice(0,200); log({ step: name, rejected: true, reason: m }); return true; }
}
