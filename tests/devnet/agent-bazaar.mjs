import fs from 'fs';
import { Connection, Keypair, PublicKey, SystemProgram } from '@solana/web3.js';
import anchor from '@coral-xyz/anchor';
const { AnchorProvider, Program, Wallet, BN } = anchor;
const idl = JSON.parse(fs.readFileSync(process.argv[2], 'utf8'));
const payer = Keypair.fromSecretKey(Uint8Array.from(JSON.parse(fs.readFileSync(process.argv[3], 'utf8'))));
const yaml = fs.readFileSync(process.env.HOME + '/.config/solana/cli/config.yml', 'utf8');
const rpc = (yaml.match(/json_rpc_url:\s*(\S+)/) || [])[1];
const programId = new PublicKey(idl.address);
const conn = new Connection(rpc, 'confirmed');
const program = new Program(idl, new AnchorProvider(conn, new Wallet(payer), { commitment: 'confirmed' }));
const log = (o) => { console.log(JSON.stringify(o)); fs.appendFileSync(process.env.PROOF_LOG, JSON.stringify(o)+'\n'); };
const [state] = PublicKey.findProgramAddressSync([Buffer.from('protocol')], programId);
const [agent] = PublicKey.findProgramAddressSync([Buffer.from('agent'), Buffer.alloc(8)], programId);
const [rep] = PublicKey.findProgramAddressSync([Buffer.from('reputation'), Buffer.alloc(8)], programId);
log({ step:'setup', program: programId.toBase58(), state: state.toBase58(), agent: agent.toBase58(), reputation: rep.toBase58() });
try {
  const s = await program.methods.initialize(10001).accounts({ protocolState: state, authority: payer.publicKey, systemProgram: SystemProgram.programId }).rpc();
  log({ step:'initialize_invalid_fee', ok:false, error:'UNEXPECTED SUCCESS', sig:s });
  throw new Error('fee 10001 unexpectedly succeeded');
} catch (e) {
  if (String(e.message).includes('unexpectedly succeeded')) throw e;
  log({ step:'initialize_invalid_fee', expectedFailure:true, error: String(e.error?.errorCode?.code || e.error?.errorMessage || e.message).split('\n')[0].slice(0,240) });
}
if (!(await conn.getAccountInfo(state))) {
  const sig = await program.methods.initialize(250).accounts({ protocolState: state, authority: payer.publicKey, systemProgram: SystemProgram.programId }).rpc();
  log({ step:'initialize', ok:true, sig });
  console.log('SIG initialize', sig);
} else log({ step:'initialize', alreadyInitialized:true });
const st = await program.account.protocolState.fetch(state);
log({ step:'fetch_state', ok:true, authority: st.authority.toBase58(), fee: st.platformFeeBps, agentCount: st.agentCount.toString() });
const sig2 = await program.methods.registerAgent('campus-scout', 'Sol.College lab agent', 'https://sol.college/dapps/agent-bazaar/', []).accounts({
  protocolState: state, agentIdentity: agent, agentReputation: rep, owner: payer.publicKey, systemProgram: SystemProgram.programId,
}).rpc();
log({ step:'register_agent', ok:true, sig: sig2 });
console.log('SIG register_agent', sig2);
const a = await program.account.agentIdentity.fetch(agent);
log({ step:'fetch_agent', ok:true, name: a.name, owner: a.owner.toBase58(), active: a.active, agentId: a.agentId.toString() });
if (a.name !== 'campus-scout') throw new Error('name mismatch');
process.exit(0);
