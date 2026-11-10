// Creates a Yes/No market that ends in <seconds> (default 300), for the UI click-through to bet on and claim.
// The hosted create form only allows end dates from tomorrow on, so a same-day claim needs a market made here.
// Usage (from frontend/): node sentient-short-market.mjs <idl.json> <rpc> <creator.json> [seconds]
import fs from 'fs';
import anchor from '@coral-xyz/anchor';
import { Connection, Keypair, PublicKey, LAMPORTS_PER_SOL } from '@solana/web3.js';
const { AnchorProvider, Program, Wallet, BN } = anchor;
const [idlPath, rpc, kpPath, secs = '300'] = process.argv.slice(2);
const A = Keypair.fromSecretKey(Uint8Array.from(JSON.parse(fs.readFileSync(kpPath, 'utf8'))));
const conn = new Connection(rpc, 'confirmed');
conn.confirmTransaction = async (arg) => { const sig = typeof arg === 'string' ? arg : arg.signature;
  for (let i = 0; i < 90; i++) { const st = (await conn.getSignatureStatuses([sig])).value[0];
    if (st && (st.confirmationStatus === 'confirmed' || st.confirmationStatus === 'finalized')) {
      if (st.err) throw new Error('tx failed ' + JSON.stringify(st.err)); return { context: { slot: st.slot }, value: { err: st.err } }; }
    await new Promise(r => setTimeout(r, 1000)); } throw new Error('confirm timeout ' + sig); };
const P = new Program(JSON.parse(fs.readFileSync(idlPath, 'utf8')), new AnchorProvider(conn, new Wallet(A), { commitment: 'confirmed' }));
const q = 'Short run ' + Date.now().toString(36);
const [market] = PublicKey.findProgramAddressSync([Buffer.from('market'), A.publicKey.toBuffer(), Buffer.from(q)], P.programId);
const end = (await conn.getBlockTime(await conn.getSlot('confirmed'))) + Number(secs);
const sig = await P.methods.createMarket(q, 'for the sol.college UI click-through', new BN(end), ['Yes', 'No'], new BN(LAMPORTS_PER_SOL)).accounts({ creator: A.publicKey }).rpc();
console.log(JSON.stringify({ step: 'create short market for the UI run', ok: true, sig, market: market.toBase58(), question: q, end }));
