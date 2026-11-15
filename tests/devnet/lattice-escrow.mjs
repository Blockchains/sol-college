import fs from 'fs';
import { Connection, Keypair, PublicKey, SystemProgram } from '@solana/web3.js';
import anchor from '@coral-xyz/anchor';
const { AnchorProvider, Program, Wallet, BN } = anchor;

const idl = JSON.parse(fs.readFileSync(process.argv[2], 'utf8'));
const lattice = Keypair.fromSecretKey(Uint8Array.from(JSON.parse(fs.readFileSync(process.argv[3], 'utf8'))));
const payer = Keypair.fromSecretKey(Uint8Array.from(JSON.parse(fs.readFileSync(process.argv[4], 'utf8'))));
const agent = Keypair.fromSecretKey(Uint8Array.from(JSON.parse(fs.readFileSync(process.argv[5], 'utf8'))));
const yaml = fs.readFileSync(process.env.HOME + '/.config/solana/cli/config.yml', 'utf8');
const rpc = (yaml.match(/json_rpc_url:\s*(\S+)/) || [])[1];
const programId = new PublicKey(idl.address);
const conn = new Connection(rpc, 'confirmed');
const payerProg = new Program(idl, new AnchorProvider(conn, new Wallet(payer), { commitment: 'confirmed' }));
const authProg = new Program(idl, new AnchorProvider(conn, new Wallet(lattice), { commitment: 'confirmed' }));
const log = (o) => { console.log(JSON.stringify(o)); if (process.env.PROOF_LOG) fs.appendFileSync(process.env.PROOF_LOG, JSON.stringify(o)+'\n'); };

const TXID = 'campus-scout-1';
const AMOUNT = 1_000_000n;
const FEE = AMOUNT / 67n;
const [escrow] = PublicKey.findProgramAddressSync(
  [Buffer.from('escrow'), payer.publicKey.toBuffer(), Buffer.from(TXID)],
  programId
);
log({ step:'setup', program: programId.toBase58(), escrow: escrow.toBase58(), payer: payer.publicKey.toBase58(), agent: agent.publicKey.toBase58(), lattice: lattice.publicKey.toBase58(), fee: FEE.toString() });

const beforePayer = await conn.getBalance(payer.publicKey);
const beforeAgent = await conn.getBalance(agent.publicKey);
const beforeLat = await conn.getBalance(lattice.publicKey);
const existing = await conn.getAccountInfo(escrow);
log({ step:'balances_before', payer: beforePayer, agent: beforeAgent, lattice: beforeLat, existing: !!existing });

if (!existing) {
  const s = await payerProg.methods.createEscrow(TXID, new BN(AMOUNT.toString()), new BN(86400))
    .accounts({
      payer: payer.publicKey,
      agent: agent.publicKey,
      latticeWallet: lattice.publicKey,
      escrowAccount: escrow,
      systemProgram: SystemProgram.programId,
    }).rpc();
  log({ step:'create_escrow', ok:true, sig:s });
  console.log('SIG create_escrow', s);
}

const mid = await conn.getAccountInfo(escrow);
log({ step:'after_create', escrowLamports: mid.lamports, owner: mid.owner.toBase58(), len: mid.data.length });

// negative: wrong authority (payer tries to release)
try {
  const s = await payerProg.methods.releaseEscrow()
    .accounts({
      authority: payer.publicKey,
      agent: agent.publicKey,
      latticeWallet: lattice.publicKey,
      escrowAccount: escrow,
    }).rpc();
  log({ step:'negative_wrong_authority', ok:false, error:'UNEXPECTED SUCCESS', sig:s });
  throw new Error('wrong authority unexpectedly succeeded');
} catch (e) {
  if (String(e.message).includes('unexpectedly succeeded')) throw e;
  log({ step:'negative_wrong_authority', expectedFailure:true, error: String(e.error?.errorCode?.code || e.error?.errorMessage || e.message).split('\n')[0].slice(0,240) });
}

const s2 = await authProg.methods.releaseEscrow()
  .accounts({
    authority: lattice.publicKey,
    agent: agent.publicKey,
    latticeWallet: lattice.publicKey,
    escrowAccount: escrow,
  }).rpc();
log({ step:'release_escrow', ok:true, sig:s2 });
console.log('SIG release_escrow', s2);

const afterPayer = await conn.getBalance(payer.publicKey);
const afterAgent = await conn.getBalance(agent.publicKey);
const afterLat = await conn.getBalance(lattice.publicKey);
const afterEscrow = await conn.getAccountInfo(escrow);
const acc = await authProg.account.escrowAccount.fetch(escrow);
log({
  step:'fetch', ok:true, status: acc.status, amount: acc.amount.toString(), fee: acc.fee.toString(),
  after: { payer: afterPayer, agent: afterAgent, lattice: afterLat, escrow: afterEscrow.lamports },
  deltas: { agent: afterAgent-beforeAgent, lattice: afterLat-beforeLat },
});
if (!acc.status.released) throw new Error('expected released, got '+JSON.stringify(acc.status));
if (BigInt(acc.fee.toString()) !== FEE) throw new Error('fee expected '+FEE+' got '+acc.fee);
if (BigInt(afterAgent-beforeAgent) !== (AMOUNT-FEE)) throw new Error('agent payout expected '+(AMOUNT-FEE)+' got '+(afterAgent-beforeAgent));
process.exit(0);
