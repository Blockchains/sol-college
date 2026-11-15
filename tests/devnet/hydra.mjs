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
const [registry] = PublicKey.findProgramAddressSync([Buffer.from('registry')], programId);
const [agent] = PublicKey.findProgramAddressSync([Buffer.from('agent'), payer.publicKey.toBuffer()], programId);
log({ step:'setup', program: programId.toBase58(), registry: registry.toBase58(), agent: agent.toBase58() });
if (!(await conn.getAccountInfo(registry))) {
  const sig = await program.methods.initialize().accounts({ registry, authority: payer.publicKey, systemProgram: SystemProgram.programId }).rpc();
  log({ step:'initialize', ok:true, sig });
  console.log('SIG initialize', sig);
} else log({ step:'initialize', alreadyInitialized:true });
const r = await program.account.registry.fetch(registry);
log({ step:'fetch_registry', ok:true, authority: r.authority.toBase58(), totalAgents: r.totalAgents.toString() });
try {
  const s = await program.methods.registerRootAgent('x'.repeat(33), 'research').accounts({
    registry, agent, wallet: payer.publicKey, authority: payer.publicKey, systemProgram: SystemProgram.programId,
  }).rpc();
  log({ step:'register_root_name_too_long', ok:false, error:'UNEXPECTED SUCCESS', sig:s });
  throw new Error('long name unexpectedly succeeded');
} catch (e) {
  if (String(e.message).includes('unexpectedly succeeded')) throw e;
  log({ step:'register_root_name_too_long', expectedFailure:true, error: String(e.error?.errorCode?.code || e.error?.errorMessage || e.message).split('\n')[0].slice(0,240) });
}
const sig2 = await program.methods.registerRootAgent('campus-scout', 'sol-college-lab').accounts({
  registry, agent, wallet: payer.publicKey, authority: payer.publicKey, systemProgram: SystemProgram.programId,
}).rpc();
log({ step:'register_root_agent', ok:true, sig: sig2 });
console.log('SIG register_root_agent', sig2);
const a = await program.account.agentAccount.fetch(agent);
log({ step:'fetch_agent', ok:true, name: a.name, specialization: a.specialization, isActive: a.isActive, depth: a.depth, wallet: a.wallet.toBase58() });
if (a.name !== 'campus-scout') throw new Error('name mismatch');
process.exit(0);
