import fs from 'fs';
import { Keypair, PublicKey, SystemProgram } from '@solana/web3.js';
import { payer, conn, log, program, fund, expectFail, ensureAta, mintTo, tokenBal, sendIx, BN, MINT, TOKEN_PROGRAM_ID } from './lib/labcommon.mjs';
const idl = JSON.parse(fs.readFileSync(new URL('../../dapps/static/pincerpay/idl.json', import.meta.url), 'utf8'));
const prog = program(idl);
const pid = new PublicKey(idl.address);
const pda = (...s) => PublicKey.findProgramAddressSync(s.map(x => typeof x === 'string' ? Buffer.from(x) : x), pid)[0];
const agent = Keypair.generate(), merchant = Keypair.generate(), stranger = Keypair.generate();
await fund(stranger.publicKey, 3_000_000);
try {
const config = pda('config'), feeVault = pda('fee_vault');
const decimals = (await conn.getParsedAccountInfo(MINT)).value.data.parsed.info.decimals;
const agentAta = await ensureAta(agent.publicKey), merchantAta = await ensureAta(merchant.publicKey), feeAta = await ensureAta(feeVault), labAta = await ensureAta(payer.publicKey);
await mintTo(agentAta, 3_000_000);
log({ step: 'setup', program: pid.toBase58(), config: config.toBase58(), fee_vault: feeVault.toBase58(), agent: agent.publicKey.toBase58(), merchant: merchant.publicKey.toBase58(), decimals });
let sig;
if (!(await conn.getAccountInfo(config))) { sig = await prog.methods.initialize(100).accountsPartial({ config, authority: payer.publicKey }).rpc(); log({ step: 'initialize', ok: true, sig, fee_bps: 100 }); }
const mid = Array.from(Keypair.generate().publicKey.toBytes().slice(0, 16));
const name = Array.from(Buffer.concat([Buffer.from('Lab Research API'), Buffer.alloc(16)]).subarray(0, 32));
const macc = pda('merchant', Buffer.from(mid));
sig = await prog.methods.registerMerchant(mid, name).accountsPartial({ config, merchantAccount: macc, merchantOwner: merchant.publicKey, merchantUsdcAta: merchantAta, authority: payer.publicKey }).rpc();
log({ step: 'register_merchant', ok: true, sig, merchant_account: macc.toBase58() });
const nonce = async () => pda('settlement', new BN((await prog.account.programConfig.fetch(config)).nonce).toArrayLike(Buffer, 'le', 8));
const settle = async (amt, p = prog, auth = payer, extra = []) => p.methods.settlePayment(new BN(amt), decimals).accountsPartial({ config, merchantAccount: macc, settlementRecord: await nonce(), agentUsdcAccount: agentAta, merchantUsdcAccount: merchantAta, feeVaultAuthority: feeVault, feeVaultUsdcAccount: feeAta, usdcMint: MINT, agent: agent.publicKey, authority: auth.publicKey, tokenProgram: TOKEN_PROGRAM_ID }).signers([agent, ...extra]).rpc();
await expectFail('settle_zero', () => settle(0));
await expectFail('settle_by_non_authority', () => settle(1000, program(idl, stranger), stranger, [stranger]));
const rec = await nonce();
sig = await settle(1_000_000);
log({ step: 'settle_payment', ok: true, sig, settlement: rec.toBase58(), merchant_tokens: (await tokenBal(merchantAta)).toString(), fee_vault_tokens: (await tokenBal(feeAta)).toString() });
const hash = Array.from(Buffer.alloc(64, 0xab));
await expectFail('record_x402_zero_hash', async () => prog.methods.recordX402Settlement(new BN(250_000), Array(64).fill(0)).accountsPartial({ config, merchantAccount: macc, settlementRecord: await nonce(), agent: agent.publicKey, authority: payer.publicKey }).rpc());
sig = await prog.methods.recordX402Settlement(new BN(250_000), hash).accountsPartial({ config, merchantAccount: macc, settlementRecord: await nonce(), agent: agent.publicKey, authority: payer.publicKey }).rpc();
log({ step: 'record_x402_settlement', ok: true, sig });
await expectFail('withdraw_fees_over_balance', () => prog.methods.withdrawFees(new BN(1_000_000_000)).accountsPartial({ config, feeVaultAuthority: feeVault, feeVaultUsdcAccount: feeAta, destinationUsdcAccount: labAta, usdcMint: MINT, authority: payer.publicKey, tokenProgram: TOKEN_PROGRAM_ID }).rpc());
sig = await prog.methods.withdrawFees(new BN(10_000)).accountsPartial({ config, feeVaultAuthority: feeVault, feeVaultUsdcAccount: feeAta, destinationUsdcAccount: labAta, usdcMint: MINT, authority: payer.publicKey, tokenProgram: TOKEN_PROGRAM_ID }).rpc();
log({ step: 'withdraw_fees', ok: true, sig, amount: 10_000 });
sig = await prog.methods.deregisterMerchant().accountsPartial({ config, merchantAccount: macc, authority: payer.publicKey }).rpc();
log({ step: 'deregister_merchant', ok: true, sig });
await expectFail('settle_after_deregister', () => settle(1000));
const m = await prog.account.merchantAccount.fetch(macc);
log({ step: 'state', total_settled: m.totalSettled.toString(), settlement_count: m.settlementCount.toString(), active: m.active });
} finally {
  const l = await conn.getBalance(stranger.publicKey); if (l > 0) await sendIx([SystemProgram.transfer({ fromPubkey: stranger.publicKey, toPubkey: payer.publicKey, lamports: l })], [payer, stranger]);
}
process.exit(0);
