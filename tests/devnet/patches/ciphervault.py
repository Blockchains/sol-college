"""Make the ciphervault fork's app/ build as a static site for sol.college.

Run from the fork's app/ directory: python3 ciphervault.py <program id>

What it changes, and only this:
- main.tsx: the fork points at a local validator (127.0.0.1:8899); we point it at devnet.
- anchor/setup.ts: the fork imports the IDL from target/ (a build artifact that is not
  committed); we import the IDL that is committed in app/src/anchor/, with its address set
  to our devnet program id (the instruction and account layout matches the program source).
- vite.config.ts: base set to /dapps/ciphervault/ so assets load from that path.
"""
import json, re, sys, pathlib
pid = sys.argv[1]
p = pathlib.Path('src/main.tsx'); s = p.read_text()
s = s.replace('"http://127.0.0.1:8899"', '"https://api.devnet.solana.com"'); p.write_text(s)
p = pathlib.Path('src/anchor/setup.ts'); s = p.read_text()
s = s.replace('import type { CipherValut } from "../../../target/types/cipher_valut";', 'type CipherValut = any;')
s = s.replace('import idl from "../../../target/idl/cipher_valut.json";', 'import idl from "./cipher_vault.json";')
s = s.replace('idl as CipherValut', 'idl as any'); p.write_text(s)
p = pathlib.Path('src/anchor/cipher_vault.json'); d = json.loads(p.read_text()); d['address'] = pid
p.write_text(json.dumps(d, indent=2))
p = pathlib.Path('vite.config.ts'); s = p.read_text()
if 'base:' not in s: s = s.replace('export default defineConfig({', "export default defineConfig({\n  base: '/dapps/ciphervault/',", 1)
p.write_text(s)
for f in pathlib.Path('src').rglob('*.ts*'):
    t = f.read_text()
    if 'target/types' in t or 'target/idl' in t: print('still references target/:', f)
print('patched')
