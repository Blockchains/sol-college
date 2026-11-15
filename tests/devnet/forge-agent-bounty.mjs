import fs from 'fs';
import { Connection, Keypair, PublicKey, SystemProgram } from '@solana/web3.js';
import anchor from '@coral-xyz/anchor';
const { AnchorProvider, Program, Wallet } = anchor;
const idl = JSON.parse(fs.readFileSync(process.argv[2], 'utf8'));
const payer = Keypair.fromSecretKey(Uint8Array.from(JSON.parse(fs.readFileSync(process.argv[3], 'utf8'))));
const yaml = fs.readFileSync(process.env.HOME + '/.config/solana/cli/config.yml', 'utf8');
const rpc = (yaml.match(/json_rpc_url:\s*(\S+)/) || [])[1];
const programId = new PublicKey(idl.address);
const conn = new Connection(rpc, 'confirmed');
const program = new Program(idl, new AnchorProvider(conn, new Wallet(payer), { commitment: 'confirmed' }));
const log = (o) => { console.log(JSON.stringify(o)); fs.appendFileSync(process.env.PROOF_LOG, JSON.stringify(o)+'\n'); };
const [market] = PublicKey.findProgramAddressSync([Buffer.from('marketplace')], programId);
log({ step:'setup', program: programId.toBase58(), marketplace: market.toBase58() });
if (!(await conn.getAccountInfo(market))) {
  const sig = await program.methods.initialize().accounts({ marketplace: market, authority: payer.publicKey, systemProgram: SystemProgram.programId }).rpc();
  log({ step:'initialize', ok:true, sig });
  console.log('SIG initialize', sig);
} else log({ step:'initialize', alreadyInitialized:true });
const m = await program.account.marketplace.fetch(market);
log({ step:'fetch_marketplace', ok:true, authority: m.authority.toBase58(), totalBounties: m.totalBounties.toString() });
if (m.authority.toBase58() !== payer.publicKey.toBase58()) throw new Error('authority mismatch');
try {
  const s = await program.methods.initialize().accounts({ marketplace: market, authority: payer.publicKey, systemProgram: SystemProgram.programId }).rpc();
  log({ step:'initialize_twice', ok:false, error:'UNEXPECTED SUCCESS', sig:s });
  throw new Error('second initialize unexpectedly succeeded');
} catch (e) {
  if (String(e.message).includes('unexpectedly succeeded')) throw e;
  log({ step:'initialize_twice', expectedFailure:true, error: String(e.error?.errorCode?.code || e.error?.errorMessage || e.message).split('\n')[0].slice(0,240) });
}
process.exit(0);
