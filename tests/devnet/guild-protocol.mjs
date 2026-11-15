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

const mint = new PublicKey('A9keuhfy58ayz3SsovWahrX2cGwJFqx14h45KUtjNNCt');
const [config] = PublicKey.findProgramAddressSync([Buffer.from('config')], programId);
const [agent] = PublicKey.findProgramAddressSync([Buffer.from('agent'), payer.publicKey.toBuffer()], programId);
const [vault] = PublicKey.findProgramAddressSync([Buffer.from('vault'), agent.toBuffer()], programId);
log({ step:'setup', program: programId.toBase58(), config: config.toBase58(), agent: agent.toBase58(), vault: vault.toBase58() });

try {
  const s = await program.methods.initialize(mint, new BN(1_000_000), 2000).accounts({
    authority: payer.publicKey, config, treasury: payer.publicKey, systemProgram: SystemProgram.programId,
  }).rpc();
  log({ step:'initialize_fee_too_high', ok:false, error:'UNEXPECTED SUCCESS', sig:s });
  throw new Error('over-max fee unexpectedly succeeded');
} catch (e) {
  if (String(e.message).includes('unexpectedly succeeded')) throw e;
  const msg = String(e.error?.errorCode?.code || e.error?.errorMessage || e.message).split('\n')[0].slice(0, 240);
  log({ step:'initialize_fee_too_high', expectedFailure:true, error: msg });
}

if (!(await conn.getAccountInfo(config))) {
  const sig = await program.methods.initialize(mint, new BN(1_000_000), 250).accounts({
    authority: payer.publicKey, config, treasury: payer.publicKey, systemProgram: SystemProgram.programId,
  }).rpc();
  log({ step:'initialize', ok:true, sig });
  console.log('SIG initialize', sig);
} else {
  log({ step:'initialize', alreadyInitialized:true });
}
const cfg = await program.account.config.fetch(config);
log({ step:'fetch_config', ok:true, authority: cfg.authority.toBase58(), minBond: cfg.minBond.toString(), feeBps: cfg.feeBps, agentCount: cfg.agentCount.toString() });

try {
  const s = await program.methods.registerAgent('scout', new BN(1)).accounts({
    owner: payer.publicKey, config, agent, vault, systemProgram: SystemProgram.programId,
  }).rpc();
  log({ step:'register_agent_bond_too_low', ok:false, error:'UNEXPECTED SUCCESS', sig:s });
  throw new Error('low bond unexpectedly succeeded');
} catch (e) {
  if (String(e.message).includes('unexpectedly succeeded')) throw e;
  const msg = String(e.error?.errorCode?.code || e.error?.errorMessage || e.message).split('\n')[0].slice(0, 240);
  log({ step:'register_agent_bond_too_low', expectedFailure:true, error: msg });
}

const sig2 = await program.methods.registerAgent('campus-scout', new BN(1_000_000)).accounts({
  owner: payer.publicKey, config, agent, vault, systemProgram: SystemProgram.programId,
}).rpc();
log({ step:'register_agent', ok:true, sig: sig2 });
console.log('SIG register_agent', sig2);
const a = await program.account.agentProfile.fetch(agent);
log({ step:'fetch_agent', ok:true, owner: a.owner.toBase58(), handle: a.handle, bond: a.bond.toString(), active: a.active, trust: a.trust });
if (a.handle !== 'campus-scout') throw new Error('handle mismatch');
if (a.bond.toString() !== '1000000') throw new Error('bond mismatch');

process.exit(0);
