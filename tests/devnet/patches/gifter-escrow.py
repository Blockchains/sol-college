"""Static-export patch for gifter-escrow (gifter-escrow-frontend, Next 14.2).
- next.config.mjs: output 'export', basePath /dapps/gifter-escrow, trailingSlash, images unoptimized.
- The four Helius DAS call sites (hooks/useWalletTokens, hooks/useRewardTokenBalance,
  actions/getWalletTokens, actions/getTokens) had the author's API key hard-coded. They now
  read process.env.NEXT_PUBLIC_HELIUS_DAS_URL, which static_build.sh sets at build time from
  HELIUS_API_KEY (the value is inlined only into the built JS, never into source or the recipe).
- Program id is replaced by static_build.sh (sed), not here.
Usage: python3 gifter-escrow.py <fork root>   (the repo root, containing gifter-escrow-frontend/)
"""
import pathlib, re, sys
root = pathlib.Path(sys.argv[1] if len(sys.argv) > 1 else '.') / 'gifter-escrow-frontend'
(root / 'next.config.mjs').write_text("""/** @type {import('next').NextConfig} */
const nextConfig = {
  output: 'export',
  basePath: '/dapps/gifter-escrow',
  trailingSlash: true,
  images: { unoptimized: true },
  eslint: { ignoreDuringBuilds: true },
  typescript: { ignoreBuildErrors: true },
  env: {
    NEXT_PUBLIC_HELIUS_DAS_URL: process.env.NEXT_PUBLIC_HELIUS_DAS_URL || '',
  },
};

export default nextConfig;
""")
# shared helper — the URL is supplied at build time
(root / 'lib' / 'helius.ts').write_text(
    "/** DAS / enhanced RPC URL, filled at build time from NEXT_PUBLIC_HELIUS_DAS_URL. */\n"
    "export const HELIUS_DAS_URL = process.env.NEXT_PUBLIC_HELIUS_DAS_URL as string;\n"
)
pat = re.compile(r"'https://devnet\.helius-rpc\.com/\?api-key=[0-9a-fA-F-]+'")
n = 0
for p in [
    root / 'hooks/useRewardTokenBalance.tsx',
    root / 'hooks/useWalletTokens.tsx',
    root / 'actions/getWalletTokens.ts',
    root / 'actions/getTokens.ts',
]:
    s = p.read_text()
    if "from '@/lib/helius'" not in s:
        s = "import { HELIUS_DAS_URL } from '@/lib/helius';\n" + s
    s, c = pat.subn('HELIUS_DAS_URL', s)
    if c == 0:
        raise SystemExit(f'no helius url in {p}')
    p.write_text(s); n += c
print('patched', root, 'helius sites', n)
