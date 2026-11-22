// Open the Sol.College browser market (idempotent): price 0 practice NOS, so a browser wallet only needs devnet SOL.
// Authority = lab authority. Writes S.campusMarket to lab-state.json. Usage: node campus-market.mjs
import { address } from '@solana/kit';
import { signer, labClient, loadState, saveState } from './lab.mjs';
const log = (o) => console.log(JSON.stringify({ t: new Date().toISOString(), ...o }));
const S = loadState(); const kit = labClient(await signer('nosana-authority'));
if (!S.campusMarket) {
  const ix = await kit.jobs.open({ jobPrice: 0, jobTimeout: 300, jobExpiration: 86400, nodeStakeMinimum: 0 });
  const market = ix.accounts.find((a) => a.signer && a.address !== kit.wallet.address)?.address;
  const sig = await kit.solana.buildSignAndSend(ix);
  S.campusMarket = String(market); saveState(S); log({ step: 'open browser market (price 0, timeout 300 s)', market: S.campusMarket, sig });
}
const m = await kit.jobs.market(address(S.campusMarket));
log({ step: 'browser market', market: S.campusMarket, jobPrice: String(m.jobPrice), jobTimeout: String(m.jobTimeout), queueType: m.queueType, vault: String(m.vault) });
process.exit(0);
