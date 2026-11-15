import fs from 'fs';
import path from 'path';
import { fileURLToPath } from 'url';
import { Connection, Keypair, PublicKey, SystemProgram } from '@solana/web3.js';
import anchor from '@coral-xyz/anchor';
const { AnchorProvider, Program, Wallet, BN } = anchor;

const __dirname = path.dirname(fileURLToPath(import.meta.url));
const idlPath = process.argv[2] || path.join(__dirname, '../../dapps/build/zeroai/zeroai_program.json');
const payerPath = process.argv[3] || path.join(process.env.HOME, '.config/solana/id.json');
const yaml = fs.readFileSync(path.join(process.env.HOME, '.config/solana/cli/config.yml'), 'utf8');
const rpc = (yaml.match(/json_rpc_url:\s*(\S+)/) || [])[1];
if (!rpc) throw new Error('no rpc in solana config');

const payer = Keypair.fromSecretKey(Uint8Array.from(JSON.parse(fs.readFileSync(payerPath, 'utf8'))));
const idl = JSON.parse(fs.readFileSync(idlPath, 'utf8'));
const programId = new PublicKey(idl.address);
const conn = new Connection(rpc, 'confirmed');
const provider = new AnchorProvider(conn, new Wallet(payer), { commitment: 'confirmed' });
const program = new Program(idl, provider);
const log = (o) => { console.log(JSON.stringify(o)); fs.appendFileSync(process.env.PROOF_LOG || '/tmp/zeroai-proof.jsonl', JSON.stringify(o)+'\n'); };

const FEEDS = {
  btcFeed: new PublicKey('HovQMDrbAgAYPCmHVSrezcSmkMtXSSUsLDFANExrZh2J'),
  ethFeed: new PublicKey('EdVCmQ9FSPcVe5YySXDPCRmc8aDQLKJ9xvYBMZPie1Vw'),
  solFeed: new PublicKey('J83w4HKfqxwcq3BEMMkPFSppX3gqekLyLJBexebFVkix'),
  bnbFeed: new PublicKey('GwzBgrXb4PG59zjce24SF2b9JXbLEjJJTBkmytuEZj1b'),
  dogeFeed: new PublicKey('4L6YhY8VvUgmqG5MvJkUJATtzB2rFqdrJwQCmFLv4Jzy'),
  jupFeed: new PublicKey('Gh9hscza9YaCzr84tNV1NZQfpqoL3csYnWDygDkQmBU2'),
};

const vault = Keypair.generate();
const [gamesPda] = PublicKey.findProgramAddressSync([Buffer.from('games'), payer.publicKey.toBuffer()], programId);
log({ step: 'setup', program: programId.toBase58(), admin: payer.publicKey.toBase58(), vault: vault.publicKey.toBase58(), games: gamesPda.toBase58() });

const sig = await program.methods.initvault({ admin: payer.publicKey, ...FEEDS }).accounts({
  payer: payer.publicKey, vault: vault.publicKey, systemProgram: SystemProgram.programId,
}).signers([vault]).rpc();
log({ step: 'initvault', ok: true, sig });
console.log('SIG initvault', sig);

const v = await program.account.vault.fetch(vault.publicKey);
log({ step: 'fetch_vault', ok: true, admin: v.admin.toBase58(), btcFeed: v.btcFeed.toBase58() });
if (v.admin.toBase58() !== payer.publicKey.toBase58()) throw new Error('admin mismatch');

// initgames only works once per admin (fixed PDA). If it already exists, fetch it.
const existing = await conn.getAccountInfo(gamesPda);
if (!existing) {
  const sig2 = await program.methods.initgames().accounts({
    vault: vault.publicKey, games: gamesPda, admin: payer.publicKey, systemProgram: SystemProgram.programId,
  }).rpc();
  log({ step: 'initgames', ok: true, sig: sig2 });
  console.log('SIG initgames', sig2);
} else {
  log({ step: 'initgames', alreadyInitialized: true, games: gamesPda.toBase58() });
}
const g = await program.account.instantWinGame.fetch(gamesPda);
log({ step: 'fetch_games', ok: true, author: g.author.toBase58(), count: g.count.toString(), symbol: g.symbol });

try {
  const s = await program.methods.initvault({ admin: payer.publicKey, ...FEEDS }).accounts({
    payer: payer.publicKey, vault: vault.publicKey, systemProgram: SystemProgram.programId,
  }).signers([vault]).rpc();
  log({ step: 'initvault_twice', ok: false, error: 'UNEXPECTED SUCCESS', sig: s });
  throw new Error('second initvault unexpectedly succeeded');
} catch (e) {
  if (String(e.message).includes('unexpectedly succeeded')) throw e;
  const msg = String(e.error?.errorCode?.code || e.error?.errorMessage || e.message).split('\n')[0].slice(0, 240);
  log({ step: 'initvault_twice', expectedFailure: true, error: msg });
}

const pythOk = await conn.getAccountInfo(FEEDS.btcFeed);
log({ step: 'pyth_btc_exists', ok: !!pythOk, owner: pythOk ? pythOk.owner.toBase58() : null });
if (pythOk) {
  try {
    const prices = [new BN(645391234), new BN(43218765), new BN(1901827), new BN(6201780), new BN(1780), new BN(9230)];
    const sig3 = await program.methods.addgame(['BTC','ETH','SOL','BNB','DOGE','JUP'], prices).accounts({
      vault: vault.publicKey, game: gamesPda, admin: payer.publicKey,
      pythBtc: FEEDS.btcFeed, pythEth: FEEDS.ethFeed, pythSol: FEEDS.solFeed,
      pythBnb: FEEDS.bnbFeed, pythDoge: FEEDS.dogeFeed, pythJup: FEEDS.jupFeed,
    }).rpc();
    log({ step: 'addgame', ok: true, sig: sig3 });
    console.log('SIG addgame', sig3);
    const g2 = await program.account.instantWinGame.fetch(gamesPda);
    log({ step: 'fetch_games_after_add', ok: true, count: g2.count.toString(), closeprice: (g2.closeprice || []).map(x => x.toString()) });
  } catch (e) {
    const msg = String(e.error?.errorCode?.code || e.error?.errorMessage || e.message).split('\n')[0].slice(0, 240);
    log({ step: 'addgame', ok: false, error: msg });
  }
}
process.exit(0);
