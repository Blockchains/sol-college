"""Static-export patch for gifter-escrow (gifter-escrow-frontend, Next 14.2).
- next.config.mjs: output 'export', basePath /dapps/gifter-escrow, trailingSlash, images unoptimized.
- The four Helius DAS call sites (hooks/useWalletTokens, hooks/useRewardTokenBalance,
  actions/getWalletTokens, actions/getTokens) read process.env.NEXT_PUBLIC_HELIUS_DAS_URL,
  which static_build.sh sets at build time from HELIUS_API_KEY (inlined only into the built JS).
- useWalletTokens: query key and ownerAddress use the wallet's base58 string (the fork
  used walletAddress?.toBase58, the function, so the token dropdown stayed empty).
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
(root / 'lib').mkdir(exist_ok=True)
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
    if "from '@/lib/helius'" not in s and 'from "@/lib/helius"' not in s:
        if 'HELIUS_DAS_URL' not in s.split('process.env')[0] if False else True:
            if "from '@/lib/helius'" not in s:
                s = "import { HELIUS_DAS_URL } from '@/lib/helius';\n" + s
    s, c = pat.subn('HELIUS_DAS_URL', s)
    n += c
    # already-env form used on the working fork
    s = s.replace('process.env.NEXT_PUBLIC_HELIUS_DAS_URL as string', 'HELIUS_DAS_URL')
    s = s.replace('process.env.NEXT_PUBLIC_HELIUS_DAS_URL', 'HELIUS_DAS_URL')
    if "from '@/lib/helius'" not in s and 'HELIUS_DAS_URL' in s:
        s = "import { HELIUS_DAS_URL } from '@/lib/helius';\n" + s
    p.write_text(s)

# Token dropdown: use the base58 string as the query key and as ownerAddress
hook = root / 'hooks/useWalletTokens.tsx'
hs = hook.read_text()
hs = hs.replace("queryKey: ['walletTokens', walletAddress?.toBase58],", "queryKey: ['walletTokens', walletAddress?.toBase58()],")
# If the hook still posts walletAddress (the PublicKey) as ownerAddress, use the string.
if re.search(r"ownerAddress:\s*walletAddress,", hs) and 'ownerAddress = walletAddress?.toBase58()' not in hs:
    hs = hs.replace('const { publicKey: walletAddress } = useWallet();',
                    "const { publicKey: walletAddress } = useWallet();\n  const ownerAddress = walletAddress?.toBase58();")
    hs = hs.replace('ownerAddress: walletAddress,', 'ownerAddress,')
    if 'enabled:' not in hs:
        hs = hs.replace("queryFn: fetchWalletTokens,\n  });",
                        "queryFn: fetchWalletTokens,\n    enabled: !!ownerAddress,\n  });")
hook.write_text(hs)
print('patched', root, 'helius sites replaced', n)
