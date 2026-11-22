// Signs a wire transaction (base64 on stdin) with a lab key from $KEYS (nosana-* only). Prints base64 of the signed tx. Never prints keys.
import { Keypair, VersionedTransaction, Transaction } from '@solana/web3.js';
import fs from 'fs';
const name = process.argv[2]; if (!/^nosana-[a-z-]+$/.test(name)) throw new Error('bad key name');
const KEYS = process.env.KEYS || '/workspace/sol-college/keys/portfolio';
const kp = Keypair.fromSecretKey(Uint8Array.from(JSON.parse(fs.readFileSync(`${KEYS}/${name}.json`))));
if (process.argv[3] === 'pubkey') { console.log(kp.publicKey.toBase58()); process.exit(0); }
if (process.argv[3] === 'message') { // sign raw message bytes (Wallet Standard solana:signMessage), ed25519 detached
  const crypto = await import('crypto'); const msg = Buffer.from(fs.readFileSync(0, 'utf8').trim(), 'base64');
  const key = crypto.createPrivateKey({ key: Buffer.concat([Buffer.from('302e020100300506032b657004220420', 'hex'), Buffer.from(kp.secretKey.slice(0, 32))]), format: 'der', type: 'pkcs8' });
  console.log(crypto.sign(null, msg, key).toString('base64')); process.exit(0); }
const raw = Buffer.from(fs.readFileSync(0, 'utf8').trim(), 'base64');
let out;
try { const tx = VersionedTransaction.deserialize(raw); tx.sign([kp]); out = tx.serialize(); }
catch { const tx = Transaction.from(raw); tx.partialSign(kp); out = tx.serialize({ requireAllSignatures: false }); }
console.log(Buffer.from(out).toString('base64'));
