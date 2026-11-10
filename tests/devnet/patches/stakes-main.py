"""Make the stakes-main (stakes.wtf) fork's app/ build as a static site for sol.college.

Run from the fork's app/ directory: python3 stakes-main.py
(the program id is replaced in src/constants/solana.ts by dapps/static_build.sh before this runs).

What it changes, and only this:
- src/App.tsx: BrowserRouter -> HashRouter, so /create and /vesting work on a static host
  (pages are #/create and #/vesting).
The RPC comes from VITE_RPC_URL at build time (devnet), and the base path from vite --base.
"""
import pathlib
p = pathlib.Path('src/App.tsx'); s = p.read_text()
s = s.replace('import { BrowserRouter }', 'import { HashRouter }').replace('<BrowserRouter>', '<HashRouter>').replace('</BrowserRouter>', '</HashRouter>')
p.write_text(s); print('patched')
# - @solana/spl-token 0.4 (from the lockfile) pulls in spl-type-length-value, which imports node's
#   crypto.createHash; vite can't bundle that, so 'crypto' is aliased to a 10-line sha256 shim
#   built on @noble/hashes (already a dependency of @solana/web3.js).
pathlib.Path('src/crypto-shim.ts').write_text('''import { sha256 } from "@noble/hashes/sha256";
export function createHash(alg: string) {
  if (alg !== "sha256") throw new Error("only sha256 is shimmed");
  const parts: Uint8Array[] = [];
  const h = { update(d: Uint8Array | string) { parts.push(typeof d === "string" ? new TextEncoder().encode(d) : d); return h; },
    digest() { const all = new Uint8Array(parts.reduce((n, p) => n + p.length, 0)); let o = 0; for (const p of parts) { all.set(p, o); o += p.length; }
      return Buffer.from(sha256(all)); } };
  return h;
}
export default { createHash };
''')
p = pathlib.Path('vite.config.ts'); s = p.read_text()
if 'crypto-shim' not in s:
    s = s.replace('alias: {', 'alias: {\n      "crypto": path.resolve("./src/crypto-shim.ts"),', 1)
p.write_text(s); print('crypto shim added')
