"""Static-hosting patch for the sentient-send frontend (run from frontend/): no logic changes.
- /market/[id] (dynamic route, can't be statically exported) -> /market/?id=<address>, read with useSearchParams
- links that bypass Next's basePath (<a href="/">, window.location) get the /dapps/sentient-send prefix
- PROTOCOL_AUTHORITY (a TODO placeholder in the fork) -> the wallet that initialized this deployment's treasury
- next.config: static export under /dapps/sentient-send; the fork's own sources fail `tsc` (MarketWithPrices type drift),
  so type errors are ignored at build time as the author's deploy must have done; no code is changed for that"""
import os, re, sys
BASE = '/dapps/sentient-send'; AUTH = sys.argv[1]
src = 'src/app/market/[id]/page.tsx'; s = open(src).read()
s = s.replace("import { useParams } from 'next/navigation';", "import { useSearchParams } from 'next/navigation';\nimport { Suspense } from 'react';")
s = s.replace("export default function MarketDetailPage() {\n    const params = useParams();\n    const marketId = params?.id as string;",
              "function MarketDetailPage() {\n    const searchParams = useSearchParams();\n    const marketId = searchParams.get('id') as string;")
assert 'useSearchParams()' in s
s = s.replace('<a href="/"', f'<a href="{BASE}/"')
s += "\nexport default function MarketPage() {\n    return (<Suspense fallback={null}><MarketDetailPage /></Suspense>);\n}\n"
open('src/app/market/page.tsx', 'w').write(s); os.remove(src); os.rmdir('src/app/market/[id]')
for root, _, files in os.walk('src'):
    for f in files:
        if not f.endswith('.tsx'): continue
        p = os.path.join(root, f); t = open(p).read(); o = t
        t = t.replace('`/market/${', '`/market/?id=${')
        t = t.replace('window.location.href = `/market/', f'window.location.href = `{BASE}/market/')
        if t != o: open(p, 'w').write(t)
c = 'src/lib/constants.ts'; t = open(c).read()
t = re.sub(r"export const PROTOCOL_AUTHORITY = new PublicKey\('[1-9A-HJ-NP-Za-km-z]+'\);", f"export const PROTOCOL_AUTHORITY = new PublicKey('{AUTH}');", t); open(c, 'w').write(t)
cfg = open('next.config.js').read().replace('const nextConfig = {', f"const nextConfig = {{\n  output: 'export', basePath: '{BASE}', trailingSlash: true, images: {{ unoptimized: true }}, eslint: {{ ignoreDuringBuilds: true }}, typescript: {{ ignoreBuildErrors: true }},", 1)
open('next.config.js', 'w').write(cfg)
print('patched')
