import fs from 'fs';
import { Keypair, PublicKey, SystemProgram, ComputeBudgetProgram } from '@solana/web3.js';
import { ed25519 } from '@noble/curves/ed25519';
import { payer, conn, log, program, fund, expectFail, sendIx, BN, MINT, ata, ensureAta, mintTo, tokenBal } from './lib/labcommon.mjs';
const eidl = JSON.parse(fs.readFileSync(new URL('../../dapps/static/agentpay-conduit/idl.json', import.meta.url), 'utf8'));
const ridl = JSON.parse(fs.readFileSync(new URL('../../dapps/static/agentpay-conduit/registry_idl.json', import.meta.url), 'utf8'));
const eid = new PublicKey(eidl.address), rid = new PublicKey(ridl.address);
const pda = (p, ...s) => PublicKey.findProgramAddressSync(s.map(x => typeof x === 'string' ? Buffer.from(x) : x), p)[0];
const G = Keypair.generate(), A = Keypair.generate(), P = Keypair.generate(), stranger = Keypair.generate();
await fund(G.publicKey, 15_000_000); await fund(A.publicKey, 20_000_000); await fund(stranger.publicKey, 3_000_000);
const cu = [ComputeBudgetProgram.setComputeUnitLimit({ units: 1_400_000 })];
try {
const reg = program(ridl), rg = program(ridl, G), rs = program(ridl, stranger);
const name = `lab-weather-${Date.now() % 1e6}`, prov = pda(rid, 'provider', payer.publicKey.toBuffer(), name);
log({ step: 'setup', registry: rid.toBase58(), escrow: eid.toBase58(), gateway: G.publicKey.toBase58(), agent: A.publicKey.toBase58(), provider_wallet: P.publicKey.toBase58(), provider: prov.toBase58() });
const regIx = (n, price, cat) => reg.methods.registerProvider(n, Array(32).fill(5), new BN(price), cat, 1, P.publicKey, G.publicKey).accountsPartial({ owner: payer.publicKey, provider: pda(rid, 'provider', payer.publicKey.toBuffer(), n) }).rpc();
await expectFail('register_empty_name', () => regIx('', 1000, 0));
await expectFail('register_zero_price', () => regIx(name, 0, 0));
await expectFail('register_bad_category', () => regIx(name, 1000, 9));
let sig = await regIx(name, 10_000, 4);
log({ step: 'register_provider', ok: true, sig, name, price_usdc: 10_000, category: 'Agent', agent_type: 'Agent' });
sig = await reg.methods.updateProvider(new BN(20_000), null).accountsPartial({ owner: payer.publicKey, provider: prov }).rpc();
log({ step: 'update_provider_price', ok: true, sig, price_usdc: 20_000 });
await expectFail('increment_by_non_gateway', () => rs.methods.incrementCallCount().accountsPartial({ gatewayAuthority: stranger.publicKey, provider: prov }).signers([stranger]).rpc());
sig = await rg.methods.incrementCallCount().accountsPartial({ gatewayAuthority: G.publicKey, provider: prov }).signers([G]).rpc();
log({ step: 'increment_call_count', ok: true, sig, total_calls: (await reg.account.apiProvider.fetch(prov)).totalCalls.toString() });
// escrow channel 1: settle with a signed voucher
const pa = program(eidl, A), pg = program(eidl, G), pst = program(eidl, stranger);
const agentAta = await ensureAta(A.publicKey); await mintTo(agentAta, 2_000_000);
const providerAta = ata(P.publicKey);
const cid = () => Array.from(Keypair.generate().publicKey.toBytes());
const open = (id, amt, timeout) => { const ch = pda(eid, 'channel', A.publicKey.toBuffer(), Buffer.from(id)); return pa.methods.openChannel(id, new BN(amt), P.publicKey, G.publicKey, new BN(timeout)).accountsPartial({ agent: A.publicKey, channel: ch, usdcMint: MINT, agentTokenAccount: agentAta, vault: ata(ch) }).signers([A]).rpc(); };
const id1 = cid(), ch1 = pda(eid, 'channel', A.publicKey.toBuffer(), Buffer.from(id1));
await expectFail('open_zero_deposit', () => open(id1, 0, 600));
await expectFail('open_invalid_timeout', () => open(id1, 1_000_000, 0));
sig = await open(id1, 1_000_000, 600);
log({ step: 'open_channel', ok: true, sig, channel: ch1.toBase58(), deposit: 1_000_000, vault_balance: (await tokenBal(ata(ch1))).toString() });
const voucher = (id, amt, signer = A) => { const m = Buffer.alloc(40); Buffer.from(id).copy(m, 0); m.writeBigUInt64LE(BigInt(amt), 32); return Array.from(ed25519.sign(m, signer.secretKey.slice(0, 32))); };
const settle = (id, ch, amt, sigBytes, p = pg, gw = G) => p.methods.settle(new BN(amt), sigBytes).accountsPartial({ gateway: gw.publicKey, channel: ch, agent: A.publicKey, provider: P.publicKey, usdcMint: MINT, vault: ata(ch), providerTokenAccount: providerAta, agentTokenAccount: agentAta }).preInstructions(cu).signers([gw]).rpc();
await expectFail('settle_forged_voucher', () => settle(id1, ch1, 400_000, voucher(id1, 400_000, stranger)));
await expectFail('settle_voucher_amount_mismatch', () => settle(id1, ch1, 500_000, voucher(id1, 400_000)));
await expectFail('settle_overdraw', () => settle(id1, ch1, 1_500_000, voucher(id1, 1_500_000)));
await expectFail('settle_by_non_gateway', () => settle(id1, ch1, 400_000, voucher(id1, 400_000), pst, stranger));
const agentBefore = await tokenBal(agentAta);
sig = await settle(id1, ch1, 400_000, voucher(id1, 400_000));
log({ step: 'settle_signed_voucher', ok: true, sig, cumulative_amount: 400_000, provider_received: (await tokenBal(providerAta)).toString(), agent_refunded: (await tokenBal(agentAta) - agentBefore).toString(), channel_closed: !(await conn.getAccountInfo(ch1)) });
// channel 2: timeout refund
const id2 = cid(), ch2 = pda(eid, 'channel', A.publicKey.toBuffer(), Buffer.from(id2));
sig = await open(id2, 300_000, 3);
log({ step: 'open_channel_2_timeout_3s', ok: true, sig, channel: ch2.toBase58() });
const refund = () => pa.methods.claimRefund().accountsPartial({ agent: A.publicKey, channel: ch2, usdcMint: MINT, vault: ata(ch2), agentTokenAccount: agentAta }).signers([A]).rpc();
await expectFail('claim_refund_before_timeout', refund);
let ok = false;
for (let i = 0; i < 12 && !ok; i++) { await new Promise(r => setTimeout(r, 4000)); try { const b = await tokenBal(agentAta); sig = await refund(); log({ step: 'claim_refund_after_timeout', ok: true, sig, refunded: (await tokenBal(agentAta) - b).toString(), channel_closed: !(await conn.getAccountInfo(ch2)) }); ok = true; } catch (e) { if (!String(e).includes('TimeoutNotReached')) throw e; } }
if (!ok) throw new Error('refund never became claimable');
sig = await reg.methods.updateProvider(null, false).accountsPartial({ owner: payer.publicKey, provider: prov }).rpc();
log({ step: 'update_provider_inactive', ok: true, sig });
await expectFail('deregister_by_stranger', () => rs.methods.deregisterProvider().accountsPartial({ owner: stranger.publicKey, provider: prov }).signers([stranger]).rpc());
sig = await reg.methods.deregisterProvider().accountsPartial({ owner: payer.publicKey, provider: prov }).rpc();
await new Promise(r => setTimeout(r, 3000)); log({ step: 'deregister_provider', ok: true, sig, closed: !(await conn.getAccountInfo(prov, 'confirmed')) });
} finally {
  for (const k of [G, A, P, stranger]) { const l = await conn.getBalance(k.publicKey); if (l > 0) await sendIx([SystemProgram.transfer({ fromPubkey: k.publicKey, toPubkey: payer.publicKey, lamports: l })], [payer, k]).catch(e => log({ step: 'cleanup_error', key: k.publicKey.toBase58(), lamports: l })); }
  log({ step: 'cleanup_returned_lab_wallets' });
}
process.exit(0);
