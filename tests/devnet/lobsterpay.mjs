import fs from 'fs';
import { Keypair, PublicKey, SystemProgram } from '@solana/web3.js';
import { payer, conn, log, program, ata, ensureAta, mintTo, tokenBal, expectFail, BN, MINT, TOKEN_PROGRAM_ID, ASSOCIATED_TOKEN_PROGRAM_ID } from './lib/labcommon.mjs';
const idl = JSON.parse(fs.readFileSync(new URL('../../dapps/static/lobsterpay/idl.json', import.meta.url),'utf8'));
const prog = program(idl); const pid = new PublicKey(idl.address);
const TREASURY = new PublicKey('DvcQMhZmhZZQ1CX6FhGkyAiPr3YtNbBuLDP3QpuBRTHp');
const owner = payer.publicKey;
const [vault] = PublicKey.findProgramAddressSync([Buffer.from('vault'), owner.toBuffer()], pid);
const [policy] = PublicKey.findProgramAddressSync([Buffer.from('policy'), vault.toBuffer()], pid);
const [feeVault] = PublicKey.findProgramAddressSync([Buffer.from('fee_vault'), owner.toBuffer()], pid);
const merchant = Keypair.generate().publicKey; const stranger = Keypair.generate().publicKey;
log({ step:'setup', program: pid.toBase58(), vault: vault.toBase58(), policy: policy.toBase58(), feeVault: feeVault.toBase58(), merchant: merchant.toBase58() });
if (!(await conn.getAccountInfo(vault))) {
  const s = await prog.methods.initializeVault({ allowedActions: new BN(7), maxPerTxAmountAtomic: new BN(2_000_000), dailyLimitAmountAtomic: new BN(10_000_000), maxSlippageBps: 100, authorizedAgent: null })
    .accounts({ owner, vault, policy, systemProgram: SystemProgram.programId }).rpc();
  log({ step:'initialize_vault', sig:s });
}
let s = await prog.methods.updatePolicy({ paused: null, allowedActions: null, maxPerTxAmountAtomic: null, dailyLimitAmountAtomic: null, maxSlippageBps: null, allowedMints: [MINT], allowedDestinations: [merchant], allowedExternalPrograms: null })
  .accounts({ owner, vault, policy }).rpc();
log({ step:'update_policy', sig:s, allowedMints:[MINT.toBase58()], allowedDestinations:[merchant.toBase58()] });
if (!(await conn.getAccountInfo(feeVault))) {
  s = await prog.methods.initializeFeeVault().accounts({ owner, vault, feeVault, systemProgram: SystemProgram.programId }).rpc();
  log({ step:'initialize_fee_vault', sig:s });
}
s = await prog.methods.depositFees({ amount: new BN(2_000_000) }).accounts({ owner, feeVault, systemProgram: SystemProgram.programId }).rpc();
log({ step:'deposit_fees', sig:s, lamports:2_000_000 });
const vaultAta = ata(vault);
s = await prog.methods.ensureVaultTokenAccount().accounts({ payer: owner, vault, mint: MINT, vaultTokenAccount: vaultAta, tokenProgram: TOKEN_PROGRAM_ID, associatedTokenProgram: ASSOCIATED_TOKEN_PROGRAM_ID, systemProgram: SystemProgram.programId }).rpc();
log({ step:'ensure_vault_token_account', sig:s, vaultAta: vaultAta.toBase58() });
log({ step:'mint_to_vault', sig: await mintTo(vaultAta, 1_000_000) });
const merchAta = await ensureAta(merchant); const tAta = await ensureAta(TREASURY); const strAta = await ensureAta(stranger);
const t0 = await tokenBal(tAta);
const payAcc = (dest) => ({ authority: owner, vault, policy, feeVault, mint: MINT, vaultTokenAccount: vaultAta, destinationTokenAccount: dest, treasuryTokenAccount: tAta, tokenProgram: TOKEN_PROGRAM_ID });
await expectFail('execute_pay_exact_non_allowlisted_destination', () => prog.methods.executePayExact({ amount: new BN(100_000), requestHash: Array(32).fill(1) }).accounts(payAcc(strAta)).rpc());
await expectFail('execute_pay_exact_over_per_tx_limit', () => prog.methods.executePayExact({ amount: new BN(3_000_000), requestHash: Array(32).fill(2) }).accounts(payAcc(merchAta)).rpc());
s = await prog.methods.executePayExact({ amount: new BN(1_000_000), requestHash: Array(32).fill(3) }).accounts(payAcc(merchAta)).rpc();
log({ step:'execute_pay_exact', sig:s, merchant_received: String(await tokenBal(merchAta)), treasury_fee: String((await tokenBal(tAta)) - t0), vault_left: String(await tokenBal(vaultAta)) });
