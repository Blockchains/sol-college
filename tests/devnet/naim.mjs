import fs from 'fs';
import path from 'path';
import { fileURLToPath } from 'url';
import { Connection, Keypair, PublicKey, SystemProgram } from '@solana/web3.js';
import anchor from '@coral-xyz/anchor';
const { AnchorProvider, Program, Wallet, BN } = anchor;
const __dirname = path.dirname(fileURLToPath(import.meta.url));
const idlPath = process.argv[2] || path.join(__dirname, '../../dapps/build/naim/naim.json');
const payerPath = process.argv[3] || path.join(process.env.HOME, '.config/solana/id.json');
const yaml = fs.readFileSync(path.join(process.env.HOME, '.config/solana/cli/config.yml'), 'utf8');
const rpc = (yaml.match(/json_rpc_url:\s*(\S+)/) || [])[1];
if (!rpc) throw new Error('no rpc in solana config');
const payer = Keypair.fromSecretKey(Uint8Array.from(JSON.parse(fs.readFileSync(payerPath, 'utf8'))));
const idl = JSON.parse(fs.readFileSync(idlPath, 'utf8'));
const programId = new PublicKey(idl.address);
const conn = new Connection(rpc, 'confirmed');
const program = new Program(idl, new AnchorProvider(conn, new Wallet(payer), { commitment: 'confirmed' }));
const log = (o) => { console.log(JSON.stringify(o)); fs.appendFileSync(process.env.PROOF_LOG || '/tmp/naim-proof.jsonl', JSON.stringify(o)+'\n'); };
const [config] = PublicKey.findProgramAddressSync([Buffer.from('config')], programId);
const params = {
  treasury: payer.publicKey,
  fee14: new BN(1_000_000), fee59: new BN(500_000), fee10Plus: new BN(100_000),
  verifyFee: new BN(50_000), registrationPeriod: new BN(365 * 24 * 3600), gracePeriod: new BN(30 * 24 * 3600),
};
log({ step: 'setup', program: programId.toBase58(), admin: payer.publicKey.toBase58(), config: config.toBase58() });
if (!(await conn.getAccountInfo(config))) {
  try {
    const s = await program.methods.initialize({ ...params, registrationPeriod: new BN(0) }).accounts({
      config, admin: payer.publicKey, systemProgram: SystemProgram.programId,
    }).rpc();
    log({ step: 'initialize_invalid_period', ok: false, error: 'UNEXPECTED SUCCESS', sig: s });
    throw new Error('invalid period unexpectedly succeeded');
  } catch (e) {
    if (String(e.message).includes('unexpectedly succeeded')) throw e;
    const msg = String(e.error?.errorCode?.code || e.error?.errorMessage || e.message).split('\n')[0].slice(0, 240);
    log({ step: 'initialize_invalid_period', expectedFailure: true, error: msg });
  }
  const sig = await program.methods.initialize(params).accounts({
    config, admin: payer.publicKey, systemProgram: SystemProgram.programId,
  }).rpc();
  log({ step: 'initialize', ok: true, sig });
} else {
  log({ step: 'initialize', alreadyInitialized: true, config: config.toBase58() });
}
const cfg = await program.account.config.fetch(config);
log({ step: 'fetch_config', ok: true, admin: cfg.admin.toBase58(), treasury: cfg.treasury.toBase58(), registrationPeriod: cfg.registrationPeriod.toString() });
if (cfg.admin.toBase58() !== payer.publicKey.toBase58()) throw new Error('admin mismatch');
try {
  const s = await program.methods.initialize(params).accounts({
    config, admin: payer.publicKey, systemProgram: SystemProgram.programId,
  }).rpc();
  log({ step: 'initialize_twice', ok: false, error: 'UNEXPECTED SUCCESS', sig: s });
  throw new Error('second initialize unexpectedly succeeded');
} catch (e) {
  if (String(e.message).includes('unexpectedly succeeded')) throw e;
  const msg = String(e.error?.errorCode?.code || e.error?.errorMessage || e.message).split('\n')[0].slice(0, 240);
  log({ step: 'initialize_twice', expectedFailure: true, error: msg });
}
process.exit(0);
