import fs from 'fs';
import { Connection, Keypair, PublicKey, SystemProgram } from '@solana/web3.js';
import anchor from '@coral-xyz/anchor';
const { AnchorProvider, Program, Wallet, BN } = anchor;

const idl = JSON.parse(fs.readFileSync(process.argv[2], 'utf8'));
const payer = Keypair.fromSecretKey(Uint8Array.from(JSON.parse(fs.readFileSync(process.argv[3], 'utf8'))));
const providerKp = Keypair.fromSecretKey(Uint8Array.from(JSON.parse(fs.readFileSync(process.argv[4], 'utf8'))));
const yaml = fs.readFileSync(process.env.HOME + '/.config/solana/cli/config.yml', 'utf8');
const rpc = (yaml.match(/json_rpc_url:\s*(\S+)/) || [])[1];
const programId = new PublicKey(idl.address);
const conn = new Connection(rpc, 'confirmed');
const program = new Program(idl, new AnchorProvider(conn, new Wallet(payer), { commitment: 'confirmed' }));
const logp = process.env.PROOF_LOG;
const log = (o) => { console.log(JSON.stringify(o)); fs.appendFileSync(logp, JSON.stringify(o)+'\n'); };

const [globalState] = PublicKey.findProgramAddressSync([Buffer.from('global_state')], programId);
const [clientAgent] = PublicKey.findProgramAddressSync([Buffer.from('agent'), payer.publicKey.toBuffer()], programId);
const [providerAgent] = PublicKey.findProgramAddressSync([Buffer.from('agent'), providerKp.publicKey.toBuffer()], programId);
const serviceName = 'campus-scout-svc';
const [service] = PublicKey.findProgramAddressSync([Buffer.from('service'), providerAgent.toBuffer(), Buffer.from(serviceName)], programId);
const taskId = 1n;
const taskIdBuf = Buffer.alloc(8); taskIdBuf.writeBigUInt64LE(taskId);
const [task] = PublicKey.findProgramAddressSync([Buffer.from('task'), taskIdBuf], programId);
const [escrow] = PublicKey.findProgramAddressSync([Buffer.from('escrow'), task.toBuffer()], programId);

log({ step:'setup', program: programId.toBase58(), globalState: globalState.toBase58(),
      clientAgent: clientAgent.toBase58(), providerAgent: providerAgent.toBase58(),
      service: service.toBase58(), task: task.toBase58(), escrow: escrow.toBase58(),
      providerAuthority: providerKp.publicKey.toBase58() });

const sig = async (ix, extra={}) => {
  const s = await ix.rpc();
  log({ step: extra.step, ok:true, sig:s, ...extra.extra });
  console.log('SIG', extra.step, s);
  return s;
};

try {
  const gs = await conn.getAccountInfo(globalState);
  if (!gs) {
    await sig(program.methods.initialize().accounts({ globalState, authority: payer.publicKey, systemProgram: SystemProgram.programId }), { step:'initialize' });
  } else {
    log({ step:'initialize', ok:true, already:true });
  }
} catch (e) {
  log({ step:'initialize', ok:false, error: e.message || String(e) });
  throw e;
}

// negative: empty name
try {
  await program.methods.registerAgent('', 'https://sol.college/').accounts({
    agent: clientAgent, globalState, authority: payer.publicKey, systemProgram: SystemProgram.programId,
  }).rpc();
  log({ step:'register_agent_empty', expectedFailure:true, error:'unexpected success' });
} catch (e) {
  const msg = (e.error?.errorCode?.code) || e.message || String(e);
  log({ step:'register_agent_empty', expectedFailure:true, error: msg });
}

await sig(program.methods.registerAgent('campus-scout', 'https://sol.college/dapps/agentvault/').accounts({
  agent: clientAgent, globalState, authority: payer.publicKey, systemProgram: SystemProgram.programId,
}), { step:'register_agent_client' });

const providerProgram = new Program(idl, new AnchorProvider(conn, new Wallet(providerKp), { commitment: 'confirmed' }));
await sig(providerProgram.methods.registerAgent('campus-provider', 'https://sol.college/dapps/agentvault/').accounts({
  agent: providerAgent, globalState, authority: providerKp.publicKey, systemProgram: SystemProgram.programId,
}), { step:'register_agent_provider' });

// negative: price 0
try {
  await providerProgram.methods.createService(serviceName, 'lab service', new BN(0)).accounts({
    service, agent: providerAgent, authority: providerKp.publicKey, systemProgram: SystemProgram.programId,
  }).rpc();
  log({ step:'create_service_zero_price', expectedFailure:true, error:'unexpected success' });
} catch (e) {
  const msg = (e.error?.errorCode?.code) || e.message || String(e);
  log({ step:'create_service_zero_price', expectedFailure:true, error: msg });
}

await sig(providerProgram.methods.createService(serviceName, 'lab DeAI service on Sol.College', new BN(1_000_000)).accounts({
  service, agent: providerAgent, authority: providerKp.publicKey, systemProgram: SystemProgram.programId,
}), { step:'create_service' });

await sig(program.methods.createTask(new BN(1_000_000)).accounts({
  task, escrow, globalState, clientAgent, providerAgent, service,
  clientAuthority: payer.publicKey, systemProgram: SystemProgram.programId,
}), { step:'create_task' });

await sig(providerProgram.methods.acceptTask().accounts({
  task, providerAgent, providerAuthority: providerKp.publicKey,
}), { step:'accept_task' });

try {
  await sig(program.methods.completeTask().accounts({
    task, escrow, globalState, clientAgent, providerAgent,
    providerAuthority: providerKp.publicKey, clientAuthority: payer.publicKey,
    systemProgram: SystemProgram.programId,
  }), { step:'complete_task' });
} catch (e) {
  log({ step:'complete_task', ok:false, error: e.message || String(e), logs: e.transactionLogs || e.errorLogs });
}

const gs2 = await program.account.globalState.fetch(globalState);
const pa = await program.account.agent.fetch(providerAgent);
const t = await program.account.task.fetch(task);
log({ step:'fetch', ok:true, totalAgents: gs2.totalAgents.toString(), totalTasks: gs2.totalTasks.toString(),
      totalCompleted: gs2.totalCompleted.toString(), taskStatus: t.status, escrow: t.escrow.toString(),
      providerReputation: pa.reputation.toString(), providerCompleted: pa.tasksCompleted.toString() });
process.exit(0);
