"""Static build prep for the chinesepowered-solana-cypherpunk (UniProof) fork's own Next.js app. Run from the repo root.
1. next.config.ts: static export under /dapps/chinesepowered-solana-cypherpunk/ (output export, basePath, trailingSlash, unoptimized images),
   and lint skipped during the build (the fork's own code fails its no-explicit-any lint rule, which stops `next build`).
2. (see below) src/idl/uniproof.ts imports ./uniproof.json, which is not committed (gitignored build output), so the app cannot build as-is.
   We write that JSON from the IDL literal committed in the same file's `export type Uniproof = {...}` (same content the
   Anchor CLI generates; every instruction discriminator in it matches sha256("global:<name>") of the program at this commit)."""
import json, pathlib
p = pathlib.Path('next.config.ts'); s = p.read_text()
s = s.replace('/* config options here */', "output: 'export',\n  basePath: '/dapps/chinesepowered-solana-cypherpunk',\n  trailingSlash: true,\n  images: { unoptimized: true },\n  eslint: { ignoreDuringBuilds: true },", 1)
p.write_text(s)
t = pathlib.Path('src/idl/uniproof.ts').read_text()
i = t.index('export type Uniproof = ') + len('export type Uniproof = '); j = t.index('export const IDL')
pathlib.Path('src/idl/uniproof.json').write_text(json.dumps(json.loads(t[i:j].strip().rstrip(';')), indent=2) + '\n')
# 3. tsconfig.json: leave the Anchor mocha tests (tests/*.ts, which import the uncommitted target/types) out of the app's type check.
c = json.loads(pathlib.Path('tsconfig.json').read_text()); c['exclude'] = sorted(set(c.get('exclude', []) + ['tests']))
pathlib.Path('tsconfig.json').write_text(json.dumps(c, indent=2) + '\n')
print('patched')
