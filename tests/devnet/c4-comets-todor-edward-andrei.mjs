// C4 Comets NameGen on devnet: init a user PDA, set a 64-byte name, read it, clear it, set again.
// Mirrors the app (web/app/page.tsx): raw instructions with IDL discriminators and toFixedU8_64.
// Usage: node c4-comets-todor-edward-andrei.mjs <idl.json> <rpc> <payer.json> <A.json> <B.json>
import fs from 'fs';
import { Connection, Keypair, PublicKey, SystemProgram, Transaction, TransactionInstruction, sendAndConfirmTransaction, LAMPORTS_PER_SOL } from '@solana/web3.js';

const [idlPath, rpc, payerPath, aPath, bPath] = process.argv.slice(2);
const rlFetch = async (url, opts) => { for (let i = 0; ; i++) { const r = await fetch(url, opts); if ((r.status !== 429 && r.status < 500) || i >= 12) return r; await new Promise(z => setTimeout(z, 1500 * (i + 1))); } };
const conn = new Connection(rpc, { commitment: 'confirmed', fetch: rlFetch, disableRetryOnRateLimit: true });
const sleep = (ms) => new Promise(r => setTimeout(r, ms));
const kp = (p) => Keypair.fromSecretKey(Uint8Array.from(JSON.parse(fs.readFileSync(p, 'utf8'))));
const idl = JSON.parse(fs.readFileSync(idlPath, 'utf8'));
const pid = new PublicKey(idl.address);
const log = (o) => console.log(JSON.stringify(o));
const err = (e) => String(e.logs?.find(l => /Error|failed|already in use|insufficient|Constraint/i.test(l)) || e.message).split('\n')[0].slice(0, 220);
const transient = (e) => /Backend error|StatusCode: 5|fetch failed|ECONNRESET|blockhash|429/i.test(String(e?.message || e));
const retry = async (fn) => { for (let i = 0; ; i++) { try { return await fn(); } catch (e) { if (!transient(e) || i >= 6) throw e; await sleep(4000 * (i + 1)); } } };
const expectFail = async (label, fn0) => { try { const s = await retry(fn0); log({ step: label, ok: false, error: 'UNEXPECTED SUCCESS', sig: s }); } catch (e) { log({ step: label, expectedFailure: true, error: err(e) }); } };

const disc = (name) => { const ins = idl.instructions.find(i => i.name === name); if (!ins?.discriminator) throw new Error('missing disc ' + name); return Buffer.from(ins.discriminator); };
const pdaOf = (authority) => PublicKey.findProgramAddressSync([Buffer.from('user'), authority.toBuffer()], pid)[0];
const to64 = (s) => { const out = Buffer.alloc(64); Buffer.from(s, 'utf8').copy(out, 0, 0, 64); return out; };
const readName = (data) => { const name = data.subarray(8 + 32, 8 + 32 + 64); let end = name.length; while (end > 0 && name[end - 1] === 0) end--; return name.subarray(0, end).toString('utf8'); };

const sendIx = async (signer, name, keys, tail) => {
  const data = tail ? Buffer.concat([disc(name), tail]) : disc(name);
  const ix = new TransactionInstruction({ programId: pid, keys, data });
  const tx = new Transaction().add(ix);
  return sendAndConfirmTransaction(conn, tx, [signer], { commitment: 'confirmed' });
};

const payer = kp(payerPath), A = kp(aPath), B = kp(bPath);
const SOL = LAMPORTS_PER_SOL;

const fund = async (k, sol, label) => {
  const need = Math.floor(sol * SOL);
  const bal = await retry(() => conn.getBalance(k.publicKey));
  if (bal >= need) { log({ step: `${label} already has ${(bal / SOL).toFixed(4)} SOL (need ${sol})`, ok: true, pubkey: k.publicKey.toBase58() }); return; }
  const lamports = need - bal;
  const sig = await retry(() => sendAndConfirmTransaction(conn,
    new Transaction().add(SystemProgram.transfer({ fromPubkey: payer.publicKey, toPubkey: k.publicKey, lamports })),
    [payer], { commitment: 'confirmed' }));
  log({ step: `fund ${label} ${(lamports / SOL).toFixed(4)} SOL`, ok: true, sig, pubkey: k.publicKey.toBase58() });
};

await fund(A, 0.05, 'A');
await fund(B, 0.03, 'B');

const pdaA = pdaOf(A.publicKey);
const pdaB = pdaOf(B.publicKey);
log({ step: 'pdas', A: A.publicKey.toBase58(), pdaA: pdaA.toBase58(), B: B.publicKey.toBase58(), pdaB: pdaB.toBase58(), program: pid.toBase58() });

const initKeys = (auth, pda) => [
  { pubkey: pda, isSigner: false, isWritable: true },
  { pubkey: auth.publicKey, isSigner: true, isWritable: true },
  { pubkey: SystemProgram.programId, isSigner: false, isWritable: false },
];
const nameKeys = (auth, pda) => [
  { pubkey: pda, isSigner: false, isWritable: true },
  { pubkey: auth.publicKey, isSigner: true, isWritable: false },
];

// If a previous run already inited A, skip init and log that
const infoA = await retry(() => conn.getAccountInfo(pdaA));
if (!infoA) {
  log({ step: 'A inits user PDA', ok: true, sig: await retry(() => sendIx(A, 'init_user', initKeys(A, pdaA))) });
} else {
  log({ step: 'A user PDA already exists from a previous run', ok: true, pda: pdaA.toBase58() });
}

await expectFail('A inits a second time (one PDA per wallet)', () => sendIx(A, 'init_user', initKeys(A, pdaA)));
await expectFail('A sets a name before the PDA exists — using B\'s uninitialised PDA with A as authority (seeds will not match, or account missing)', () => sendIx(A, 'set_name', nameKeys(A, pdaB), to64('too-soon')));

const name1 = 'shadow-college';
log({ step: `A saves name "${name1}"`, ok: true, sig: await retry(() => sendIx(A, 'set_name', nameKeys(A, pdaA), to64(name1))) });
{
  const info = await retry(() => conn.getAccountInfo(pdaA));
  const got = readName(info.data);
  log({ step: 'A reads on-chain name', ok: got === name1, name: got });
  if (got !== name1) throw new Error('name mismatch: ' + got);
}

log({ step: 'A clears the name', ok: true, sig: await retry(() => sendIx(A, 'clear_name', nameKeys(A, pdaA))) });
{
  const info = await retry(() => conn.getAccountInfo(pdaA));
  const got = readName(info.data);
  log({ step: 'A reads after clear (must be empty)', ok: got === '', name: got || '' });
  if (got !== '') throw new Error('clear failed: ' + got);
}

const name2 = 'nova-2026';
log({ step: `A saves a second name "${name2}"`, ok: true, sig: await retry(() => sendIx(A, 'set_name', nameKeys(A, pdaA), to64(name2))) });
{
  const info = await retry(() => conn.getAccountInfo(pdaA));
  const got = readName(info.data);
  log({ step: 'A reads second name', ok: got === name2, name: got });
  if (got !== name2) throw new Error('second name mismatch: ' + got);
}

await expectFail('B sets a name on A\'s PDA (B is not the authority; seeds are [user, authority])', () => sendIx(B, 'set_name', nameKeys(B, pdaA), to64('hijack')));
await expectFail('B clears A\'s name', () => sendIx(B, 'clear_name', nameKeys(B, pdaA)));

// return leftover SOL (leave rent-exempt floor on the PDA; wallets keep a dust amount)
for (const k of [A, B]) {
  const bal = await conn.getBalance(k.publicKey);
  if (false)  // leave SOL on A/B for the UI click-through; recover later if needed {
    log({ step: 'return unspent SOL to the payer', from: k.publicKey.toBase58(), sol: (bal - 5000) / SOL,
      sig: await sendAndConfirmTransaction(conn, new Transaction().add(SystemProgram.transfer({ fromPubkey: k.publicKey, toPubkey: payer.publicKey, lamports: bal - 5000 })), [k], { commitment: 'confirmed' }) });
  }
}
log({ step: 'done', ok: true });
