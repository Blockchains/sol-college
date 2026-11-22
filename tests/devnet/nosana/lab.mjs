// Sol.College Nosana lab: shared config. Devnet only, lab program ids, lab practice NOS mint. Keys are read from $KEYS and never printed.
import fs from 'fs';
import crypto from 'crypto';
import bs58 from 'bs58';
import { createNosanaClient } from '@nosana/kit';
import { createKeyPairSignerFromBytes, address } from '@solana/kit';

export const FAUCET_NEVER = '58nzDwjUmR6jqCEGkvAkNt4EcdmYvf8xHzazUnELUMsp';
export const KEYS = process.env.KEYS || '/workspace/sol-college/keys/portfolio';
export const RPC = process.env.DEVNET_RPC || 'https://api.devnet.solana.com';
if (/mainnet/i.test(RPC)) throw new Error('refusing to run against mainnet');
export const LAB = {
  jobs: '4nFPjT5MgCtYheCHGACin9S8N56Cg1RTBAhFQv43Ybxb',
  stake: 'qqA8dv9jjMYZJgVKBdiCjSL9MYQviiEN4R93dVuYeJR',
  rewards: 'EWdwdb7Jbjd2hSYAUKz5NTTCJSRgkZNH6tbXprAv3LEY',
  nos: 'GKkroxnqiJvxyVUXKu9BAEttwGkZH5zSn8zvZ5b5fPt7',
  authority: 'sZWwGfLUsuZSYW2vkF4RFBgQRQeq1HqXzzWPDPPFWQD',
  authorityAta: 'Hz8amGzuMqXU9tQbEak2SHXShMahnKhx3LprtwS8Semn',
};
export const STATE_FILE = new URL('./lab-state.json', import.meta.url);
export const loadState = () => (fs.existsSync(STATE_FILE) ? JSON.parse(fs.readFileSync(STATE_FILE)) : {});
export const saveState = (s) => fs.writeFileSync(STATE_FILE, JSON.stringify(s, null, 2));
export const secret = (name) => Uint8Array.from(JSON.parse(fs.readFileSync(`${KEYS}/${name}.json`)));
export const signer = (name) => createKeyPairSignerFromBytes(secret(name));

// Explicit devnet config: the node/kit defaults (mainnet, Nosana IPFS/API endpoints) are never used for the declared workflow.
export function labClient(wallet) {
  const c = createNosanaClient('devnet', {
    solana: { cluster: 'devnet', rpcEndpoint: RPC, commitment: 'confirmed',
      priorityFees: { type: 'fixed', microLamports: 1000 } },
    programs: {
      nosTokenAddress: address(LAB.nos), jobsAddress: address(LAB.jobs), rewardsAddress: address(LAB.rewards), stakeAddress: address(LAB.stake),
      poolsAddress: address('11111111111111111111111111111111'), merkleDistributorAddress: address('11111111111111111111111111111111'),
      rewardsPoolAddress: address('11111111111111111111111111111111'),
    },
    logLevel: 'error',
  });
  if (wallet) c.wallet = wallet;
  return c;
}

// Real IPFS CIDv0 (dag-pb + UnixFS file, single chunk <= 256 KiB), so lab hashes match `ipfs add --cid-version 0`.
const varint = (n) => { const o = []; while (n > 127) { o.push((n & 127) | 128); n >>>= 7; } o.push(n); return Buffer.from(o); };
export function cidV0(bytes) {
  bytes = Buffer.from(bytes); if (bytes.length > 262144) throw new Error('single-chunk CIDv0 only');
  const unixfs = Buffer.concat([Buffer.from([0x08, 0x02]), bytes.length ? Buffer.concat([Buffer.from([0x12]), varint(bytes.length), bytes]) : Buffer.alloc(0), Buffer.from([0x18]), varint(bytes.length)]);
  const node = Buffer.concat([Buffer.from([0x0a]), varint(unixfs.length), unixfs]);
  const digest = crypto.createHash('sha256').update(node).digest();
  return bs58.encode(Buffer.concat([Buffer.from([0x12, 0x20]), digest]));
}
// Lab content store: content-addressed files on the box, published under sol.college/dapps/nosana/ipfs/. Reads re-hash and verify.
export const STORE = process.env.NOSANA_LAB_STORE || '/workspace/sol-college/portfolio/nosana/store';
export function storePut(obj) { const b = Buffer.from(typeof obj === 'string' ? obj : JSON.stringify(obj)); const cid = cidV0(b); fs.mkdirSync(STORE, { recursive: true }); fs.writeFileSync(`${STORE}/${cid}`, b); return cid; }
export function storeGet(cid) { const b = fs.readFileSync(`${STORE}/${cid}`); if (cidV0(b) !== cid) throw new Error(`content store hash mismatch for ${cid}`); return b; }
