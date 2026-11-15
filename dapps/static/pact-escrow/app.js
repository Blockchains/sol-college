import { Connection, PublicKey, SystemProgram, Transaction, TransactionInstruction } from 'https://esm.sh/@solana/web3.js@1.98.2';

const cfg = await (await fetch('./config.json')).json();
const PROGRAM = new PublicKey(cfg.programs.devnet);
const RPC = {
  devnet: 'https://api.devnet.solana.com',
};
let net = 'devnet';
let wallet = null;
let provider = null;

const logEl = document.getElementById('log');
const who = document.getElementById('who');
const pdaEl = document.getElementById('pda');
function log(msg) {
  const li = document.createElement('li');
  li.textContent = typeof msg === 'string' ? msg : JSON.stringify(msg);
  logEl.prepend(li);
}
function u64le(n) {
  const b = new ArrayBuffer(8);
  new DataView(b).setBigUint64(0, BigInt(n), true);
  return new Uint8Array(b);
}
function seeds() {
  const seller = new PublicKey(document.getElementById('seller').value.trim());
  const seed = BigInt(document.getElementById('seed').value.trim() || '0');
  const amount = BigInt(document.getElementById('amount').value.trim() || '0');
  return { seller, seed, amount };
}
function derive(buyer, seller, seed) {
  return PublicKey.findProgramAddressSync(
    [new TextEncoder().encode('escrow'), buyer.toBytes(), seller.toBytes(), u64le(seed)],
    PROGRAM
  );
}
function refreshPda() {
  try {
    if (!wallet) { pdaEl.textContent = ''; return; }
    const { seller, seed } = seeds();
    const [escrow, bump] = derive(wallet, seller, seed);
    pdaEl.innerHTML = 'Escrow PDA <code>' + escrow.toBase58() + '</code> bump ' + bump;
  } catch (e) {
    pdaEl.textContent = '';
  }
}
['seller','seed'].forEach((id) => document.getElementById(id).addEventListener('input', refreshPda));

async function connect(kind) {
  const inj = kind === 'solflare' ? window.solflare : window.solana;
  if (!inj) { log(kind + ' is not installed'); return; }
  const res = await inj.connect();
  const pk = new PublicKey((res && res.publicKey) ? res.publicKey : inj.publicKey);
  wallet = pk;
  provider = inj;
  who.textContent = 'Connected ' + pk.toBase58() + ' on devnet. Transactions are signed in your wallet.';
  refreshPda();
}
document.querySelector('[data-wallet=phantom]').onclick = () => connect('phantom');
document.querySelector('[data-wallet=solflare]').onclick = () => connect('solflare');

async function send(ix) {
  if (!provider || !wallet) throw new Error('connect a wallet first');
  const conn = new Connection(RPC.devnet, 'confirmed');
  const { blockhash, lastValidBlockHeight } = await conn.getLatestBlockhash();
  const tx = new Transaction({ feePayer: wallet, blockhash, lastValidBlockHeight }).add(ix);
  const signed = await provider.signTransaction(tx);
  const sig = await conn.sendRawTransaction(signed.serialize());
  await conn.confirmTransaction({ signature: sig, blockhash, lastValidBlockHeight }, 'confirmed');
  return sig;
}

document.getElementById('create').onclick = async () => {
  try {
    const { seller, seed, amount } = seeds();
    const [escrow] = derive(wallet, seller, seed);
    const data = new Uint8Array(17);
    data[0] = 0;
    data.set(u64le(amount), 1);
    data.set(u64le(seed), 9);
    const ix = new TransactionInstruction({
      programId: PROGRAM,
      keys: [
        { pubkey: wallet, isSigner: true, isWritable: true },
        { pubkey: seller, isSigner: false, isWritable: false },
        { pubkey: escrow, isSigner: false, isWritable: true },
        { pubkey: SystemProgram.programId, isSigner: false, isWritable: false },
      ],
      data,
    });
    const sig = await send(ix);
    log('create_escrow ' + sig + ' escrow ' + escrow.toBase58());
  } catch (e) { log('create failed: ' + (e.message || e)); }
};

document.getElementById('release').onclick = async () => {
  try {
    const { seller, seed } = seeds();
    const [escrow] = derive(wallet, seller, seed);
    const ix = new TransactionInstruction({
      programId: PROGRAM,
      keys: [
        { pubkey: wallet, isSigner: true, isWritable: true },
        { pubkey: seller, isSigner: false, isWritable: true },
        { pubkey: escrow, isSigner: false, isWritable: true },
      ],
      data: new Uint8Array([1]),
    });
    const sig = await send(ix);
    log('release ' + sig);
  } catch (e) { log('release failed: ' + (e.message || e)); }
};

document.getElementById('refund').onclick = async () => {
  try {
    const { seller, seed } = seeds();
    const [escrow] = derive(wallet, seller, seed);
    const ix = new TransactionInstruction({
      programId: PROGRAM,
      keys: [
        { pubkey: wallet, isSigner: false, isWritable: true },
        { pubkey: seller, isSigner: true, isWritable: true },
        { pubkey: escrow, isSigner: false, isWritable: true },
      ],
      data: new Uint8Array([2]),
    });
    const sig = await send(ix);
    log('refund ' + sig);
  } catch (e) { log('refund failed: ' + (e.message || e)); }
};

document.getElementById('fetch').onclick = async () => {
  try {
    const { seller, seed } = seeds();
    const buyer = wallet;
    if (!buyer) throw new Error('connect a wallet first');
    const [escrow] = derive(buyer, seller, seed);
    const conn = new Connection(RPC.devnet, 'confirmed');
    const info = await conn.getAccountInfo(escrow);
    if (!info) { log('escrow ' + escrow.toBase58() + ' does not exist'); return; }
    const status = ['Active','Released','Refunded'][info.data[80]] || String(info.data[80]);
    const amount = new DataView(info.data.buffer, info.data.byteOffset + 72, 8).getBigUint64(0, true);
    log('escrow ' + escrow.toBase58() + ' owner ' + info.owner.toBase58() + ' lamports ' + info.lamports + ' amount ' + amount + ' status ' + status);
  } catch (e) { log('fetch failed: ' + (e.message || e)); }
};
