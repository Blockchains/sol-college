import fs from 'fs';
import { Connection, Keypair, PublicKey, SystemProgram, Transaction, TransactionInstruction, sendAndConfirmTransaction } from '@solana/web3.js';

const buyer = Keypair.fromSecretKey(Uint8Array.from(JSON.parse(fs.readFileSync(process.argv[2], 'utf8'))));
const seller = Keypair.fromSecretKey(Uint8Array.from(JSON.parse(fs.readFileSync(process.argv[3], 'utf8'))));
const yaml = fs.readFileSync(process.env.HOME + '/.config/solana/cli/config.yml', 'utf8');
const rpc = (yaml.match(/json_rpc_url:\s*(\S+)/) || [])[1];
const conn = new Connection(rpc, 'confirmed');
const log = (o) => { console.log(JSON.stringify(o)); if (process.env.PROOF_LOG) fs.appendFileSync(process.env.PROOF_LOG, JSON.stringify(o)+'\n'); };

const PROGRAM = new PublicKey('BA6gPuCDWSBrtsPr5WBMBLtEr2cRAUAbC3Ljg4mR6DDp');
const AMOUNT = 1_000_000n;
const SEED = 20261115n;
const seedBuf = Buffer.alloc(8); seedBuf.writeBigUInt64LE(SEED);
const [escrow, bump] = PublicKey.findProgramAddressSync(
  [Buffer.from('escrow'), buyer.publicKey.toBuffer(), seller.publicKey.toBuffer(), seedBuf],
  PROGRAM
);
log({ step:'setup', program: PROGRAM.toBase58(), escrow: escrow.toBase58(), bump, seed: SEED.toString(), buyer: buyer.publicKey.toBase58(), seller: seller.publicKey.toBase58() });

const beforeBuyer = await conn.getBalance(buyer.publicKey);
const beforeSeller = await conn.getBalance(seller.publicKey);
const existing = await conn.getAccountInfo(escrow);
log({ step:'balances_before', buyer: beforeBuyer, seller: beforeSeller, existing: !!existing });

async function send(ix, signers, label) {
  const tx = new Transaction().add(ix);
  const sig = await sendAndConfirmTransaction(conn, tx, signers, { commitment: 'confirmed' });
  log({ step:label, ok:true, sig });
  console.log('SIG', label, sig);
  return sig;
}

if (!existing) {
  const data = Buffer.alloc(1 + 8 + 8);
  data[0] = 0;
  data.writeBigUInt64LE(AMOUNT, 1);
  data.writeBigUInt64LE(SEED, 9);
  const ix = new TransactionInstruction({
    programId: PROGRAM,
    keys: [
      { pubkey: buyer.publicKey, isSigner: true, isWritable: true },
      { pubkey: seller.publicKey, isSigner: false, isWritable: false },
      { pubkey: escrow, isSigner: false, isWritable: true },
      { pubkey: SystemProgram.programId, isSigner: false, isWritable: false },
    ],
    data,
  });
  await send(ix, [buyer], 'create_escrow');
} else {
  log({ step:'create_escrow', skipped:true });
}

const midBuyer = await conn.getBalance(buyer.publicKey);
const midEscrow = await conn.getBalance(escrow);
const info = await conn.getAccountInfo(escrow);
const status = info.data[80];
const storedAmount = info.data.readBigUInt64LE(72);
log({ step:'after_create', buyer: midBuyer, escrowLamports: midEscrow, owner: info.owner.toBase58(), status, storedAmount: storedAmount.toString(), dataLen: info.data.length });

const rel = Buffer.from([1]);
const ix2 = new TransactionInstruction({
  programId: PROGRAM,
  keys: [
    { pubkey: buyer.publicKey, isSigner: true, isWritable: true },
    { pubkey: seller.publicKey, isSigner: false, isWritable: true },
    { pubkey: escrow, isSigner: false, isWritable: true },
  ],
  data: rel,
});
await send(ix2, [buyer], 'release');

const afterBuyer = await conn.getBalance(buyer.publicKey);
const afterSeller = await conn.getBalance(seller.publicKey);
const afterEscrow = await conn.getBalance(escrow);
const info2 = await conn.getAccountInfo(escrow);
log({
  step:'fetch',
  ok:true,
  status: info2.data[80],
  after: { buyer: afterBuyer, seller: afterSeller, escrow: afterEscrow },
  deltas: { buyer: afterBuyer - beforeBuyer, seller: afterSeller - beforeSeller, escrow: afterEscrow - (existing ? (await (async()=>0)()) : 0) },
  sellerDeltaFromMid: afterSeller - beforeSeller,
});
if (info2.data[80] !== 1) throw new Error('expected STATUS_RELEASED=1, got '+info2.data[80]);
if (BigInt(afterSeller - beforeSeller) !== AMOUNT) throw new Error('seller payout expected 1000000, got '+(afterSeller-beforeSeller));

// negative: amount=0 create with a different seed
try {
  const seed2 = Buffer.alloc(8); seed2.writeBigUInt64LE(99n);
  const [escrow2] = PublicKey.findProgramAddressSync(
    [Buffer.from('escrow'), buyer.publicKey.toBuffer(), seller.publicKey.toBuffer(), seed2],
    PROGRAM
  );
  const data = Buffer.alloc(1 + 8 + 8);
  data[0] = 0;
  data.writeBigUInt64LE(0n, 1);
  data.writeBigUInt64LE(99n, 9);
  const ix = new TransactionInstruction({
    programId: PROGRAM,
    keys: [
      { pubkey: buyer.publicKey, isSigner: true, isWritable: true },
      { pubkey: seller.publicKey, isSigner: false, isWritable: false },
      { pubkey: escrow2, isSigner: false, isWritable: true },
      { pubkey: SystemProgram.programId, isSigner: false, isWritable: false },
    ],
    data,
  });
  const tx = new Transaction().add(ix);
  const s = await sendAndConfirmTransaction(conn, tx, [buyer], { commitment: 'confirmed' });
  log({ step:'negative_zero_amount', ok:false, error:'UNEXPECTED SUCCESS', sig:s });
  throw new Error('zero amount unexpectedly succeeded');
} catch (e) {
  if (String(e.message).includes('unexpectedly succeeded')) throw e;
  log({ step:'negative_zero_amount', expectedFailure:true, error: String(e.message).split('\n')[0].slice(0,240) });
}

process.exit(0);
