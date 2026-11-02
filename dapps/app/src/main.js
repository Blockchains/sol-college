// Sol.College lesson dapp: a generic, IDL-driven client for one fork's Anchor program.
// All signing happens in the user's own wallet (Phantom / Solflare via wallet-adapter). No private key ever touches this page.
import { Connection, PublicKey, SystemProgram, SYSVAR_RENT_PUBKEY, LAMPORTS_PER_SOL } from '@solana/web3.js';
import { AnchorProvider, Program, BN } from '@coral-xyz/anchor';
import { PhantomWalletAdapter } from '@solana/wallet-adapter-phantom';
import { SolflareWalletAdapter } from '@solana/wallet-adapter-solflare';
const RPC = { devnet: 'https://api.devnet.solana.com', mainnet: 'https://api.mainnet-beta.solana.com' };
const WELL_KNOWN = { systemProgram: SystemProgram.programId.toBase58(), rent: SYSVAR_RENT_PUBKEY.toBase58(),
  tokenProgram: 'TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA', token2022Program: 'TokenzQdBNbLqP5VEhdkAS6EPFLC1PHnBqCXEpPxuEb',
  associatedTokenProgram: 'ATokenGPvbdGVxr1b2hvZbsiqW5xWH25efTNsLJA8knL', tokenMetadataProgram: 'metaqbxxUerdq28cj1RbAWkYQm3ybzjb6a8bt518x1s' };
const $ = (s) => document.querySelector(s), esc = (s) => String(s).replace(/[&<>"]/g, (c) => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;' }[c]));
const camel = (s) => s.replace(/_([a-z0-9])/g, (_, c) => c.toUpperCase());
let cfg, idl, net = new URLSearchParams(location.search).get('network') === 'mainnet' ? 'mainnet' : 'devnet', wallet = null, conn, program;
const wallets = { phantom: new PhantomWalletAdapter(), solflare: new SolflareWalletAdapter() };
function log(html) { const li = document.createElement('li'); li.innerHTML = html; $('#log').prepend(li); }
const explorer = (kind, v) => `https://explorer.solana.com/${kind}/${v}${net === 'devnet' ? '?cluster=devnet' : ''}`;
function pid() { return cfg.programs[net]; }
function setNet(n) {
  net = n; history.replaceState(null, '', '?network=' + n);
  for (const b of document.querySelectorAll('[data-net]')) b.setAttribute('aria-pressed', b.dataset.net === n);
  $('#netinfo').innerHTML = n === 'devnet'
    ? `<p><b>Devnet:</b> test tokens with no value. Get free devnet SOL at <a href="https://faucet.solana.com" target=_blank rel=noopener>faucet.solana.com</a> (or <code>solana airdrop 2 -ud</code>), and switch your wallet to Devnet (Phantom: Settings → Developer settings → Testnet mode; Solflare: Settings → Network → Devnet).</p>`
    : `<div class=warn><b>Mainnet: real tokens. Alpha, high-risk software.</b> This is unaudited code from a hackathon/open-source fork, shown for learning. You can lose everything you send. There is no promised return of any kind. Use a fresh wallet with a small amount, and read every transaction in your wallet before you approve it.</div>`;
  const p = pid();
  if (!p) {
    $('#app').innerHTML = n === 'mainnet' ? `<p class=disabled>Not yet deployed on mainnet. Deploying needs owner approval, so mainnet mode is disabled for this dapp.</p>` : '<p class=disabled>Not deployed on this network yet.</p>';
    return;
  }
  conn = new Connection(RPC[n], 'confirmed'); render();
}
function provider() {
  const w = wallet ? { publicKey: wallet.publicKey, signTransaction: (t) => wallet.signTransaction(t), signAllTransactions: (t) => wallet.signAllTransactions(t) }
    : { publicKey: PublicKey.default, signTransaction: async () => { throw new Error('Connect a wallet first'); }, signAllTransactions: async () => { throw new Error('Connect a wallet first'); } };
  return new AnchorProvider(conn, w, { commitment: 'confirmed' });
}
function parseArg(t, v) {
  if (typeof t === 'string') {
    if (/^[ui](64|128|256)$/.test(t)) return new BN(v.trim() || '0');
    if (/^[uif](8|16|32)$|^f64$/.test(t)) return Number(v);
    if (t === 'bool') return v === 'true';
    if (t === 'pubkey' || t === 'publicKey') return new PublicKey(v.trim());
    if (t === 'string') return v;
    if (t === 'bytes') return Buffer.from(JSON.parse(v || '[]'));
  }
  if (t.option) return v.trim() === '' ? null : parseArg(t.option, v);
  const j = JSON.parse(v || 'null'), conv = (tt, x) => {
    if (typeof tt === 'string') return /^[ui](64|128)$/.test(tt) ? new BN(String(x)) : (tt === 'pubkey' || tt === 'publicKey') ? new PublicKey(x) : x;
    if (tt.array) return x.map((y) => conv(tt.array[0], y)); if (tt.vec) return x.map((y) => conv(tt.vec, y)); return x;
  };
  return conv(t, j);
}
const tname = (t) => typeof t === 'string' ? t : JSON.stringify(t);
function flatAccounts(accs, pre = '') { return accs.flatMap((a) => a.accounts ? flatAccounts(a.accounts, pre + a.name + '.') : [{ ...a, path: pre + a.name }]); }
function render() {
  program = new Program({ ...idl, address: pid() }, provider());
  const ixs = idl.instructions.map((ix) => {
    const accs = flatAccounts(ix.accounts).map((a) => {
      const auto = a.address || a.pda || WELL_KNOWN[camel(a.name)] || a.signer;
      const val = a.address || WELL_KNOWN[camel(a.name)] || '';
      return `<label>${esc(a.path)}${a.signer ? ' <small>(signer: your wallet' + (a.writable ? ', writable' : '') + ')</small>' : a.pda ? ' <small>(PDA, derived automatically)</small>' : a.writable ? ' <small>(writable)</small>' : ''}
        <input data-acc="${esc(a.path)}" value="${esc(val)}" placeholder="${auto ? 'auto' : 'account address'}" ${a.pda || (a.signer && !val) ? 'disabled' : ''}></label>`;
    }).join('');
    const args = ix.args.map((a) => `<label>${esc(a.name)} <small>${esc(tname(a.type))}</small><input data-arg="${esc(a.name)}" placeholder="${esc(tname(a.type))}"></label>`).join('');
    return `<details class=ix><summary><code>${esc(ix.name)}</code></summary><form data-ix="${esc(ix.name)}">${args}${accs}<button>Sign in wallet and send</button></form></details>`;
  }).join('');
  const accts = (idl.accounts || []).map((a) => `<button type=button data-fetch="${esc(a.name)}">List ${esc(a.name)} accounts</button>`).join(' ');
  $('#app').innerHTML = `<p>Program <a href="${explorer('address', pid())}" target=_blank rel=noopener><code>${pid()}</code></a> on ${net}.</p><h2>Instructions</h2>${ixs}<h2>On-chain state</h2><p>${accts || 'This IDL declares no account types.'}</p><pre id=state></pre>`;
  for (const f of document.querySelectorAll('form[data-ix]')) f.onsubmit = (e) => { e.preventDefault(); send(f); };
  for (const b of document.querySelectorAll('[data-fetch]')) b.onclick = () => fetchAll(b.dataset.fetch);
}
async function send(f) {
  try {
    if (!wallet) throw new Error('Connect a wallet first');
    if (net === 'mainnet' && !confirm('Mainnet uses real funds. This is alpha, unaudited software and you can lose what you send. Continue to your wallet?')) return;
    const ix = idl.instructions.find((i) => i.name === f.dataset.ix);
    const args = ix.args.map((a) => parseArg(a.type, f.querySelector(`[data-arg="${a.name}"]`).value));
    const accs = {}; for (const a of flatAccounts(ix.accounts)) {
      const v = f.querySelector(`[data-acc="${a.path}"]`).value.trim();
      const key = camel(a.path.split('.').pop());
      if (v) accs[key] = new PublicKey(v); else if (a.signer && !a.pda) accs[key] = wallet.publicKey;
    }
    const m = program.methods[camel(ix.name)](...args).accountsPartial(accs);
    const tx = await m.transaction(); tx.feePayer = wallet.publicKey; tx.recentBlockhash = (await conn.getLatestBlockhash()).blockhash;
    const signed = await wallet.signTransaction(tx);
    const sig = await conn.sendRawTransaction(signed.serialize()); await conn.confirmTransaction(sig, 'confirmed');
    log(`✅ <code>${esc(ix.name)}</code> <a href="${explorer('tx', sig)}" target=_blank rel=noopener>${sig.slice(0, 16)}…</a>`);
  } catch (e) { log(`❌ ${esc(e.message || e)}`); }
}
async function fetchAll(name) {
  try { const rows = await program.account[camel(name).replace(/^./, (c) => c.toLowerCase())].all();
    $('#state').textContent = JSON.stringify(rows.slice(0, 50).map((r) => ({ address: r.publicKey.toBase58(), ...r.account })), (k, v) => v && v._bn ? new BN(v).toString() : v && v.toBase58 ? v.toBase58() : v, 1) || '[]';
  } catch (e) { $('#state').textContent = 'Error: ' + e.message; }
}
async function connect(k) {
  const w = wallets[k];
  try { await w.connect(); wallet = w; $('#who').innerHTML = `Connected <code>${w.publicKey.toBase58()}</code>`; refreshBal(); if (pid()) render(); }
  catch (e) { log(`❌ ${esc(k)}: ${esc(e.message || 'wallet not found; install it first')}`); }
}
async function refreshBal() { if (wallet && conn) { const b = await conn.getBalance(wallet.publicKey); $('#who').innerHTML += ` · ${(b / LAMPORTS_PER_SOL).toFixed(4)} SOL on ${net}`; } }
async function main() {
  cfg = await (await fetch('config.json')).json(); idl = await (await fetch('idl.json')).json();
  document.title = `${cfg.name}: live dapp | Sol.College`; $('#title').textContent = cfg.name;
  $('#meta').innerHTML = `Program from <a href="${cfg.fork}/tree/${cfg.commit}">${esc(cfg.fork.replace('https://github.com/', ''))}@${cfg.commit.slice(0, 7)}</a> · <a href="${esc(cfg.lesson)}">Lesson and build guide</a>`;
  for (const b of document.querySelectorAll('[data-net]')) { b.onclick = () => setNet(b.dataset.net); if (b.dataset.net === 'mainnet' && !cfg.programs.mainnet) b.title = 'Not yet deployed on mainnet'; }
  for (const b of document.querySelectorAll('[data-wallet]')) b.onclick = () => connect(b.dataset.wallet);
  setNet(net);
}
main().catch((e) => { $('#app').textContent = 'Failed to load: ' + e.message; });
