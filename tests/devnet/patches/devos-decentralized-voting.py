"""Static-export patch for devos-decentralized-voting (devos-app, Next 14.2).
- next.config.mjs: output 'export', basePath /dapps/devos-decentralized-voting, trailingSlash, images unoptimized,
  eslint/type errors not fatal (the fork's code has implicit-any params).
- OwnedElections/[electionName] and EnrolledElections/[electionName] (static mock pages) move to .../view/?n=<name>,
  because a static export can't pre-render election names that don't exist yet.
- The program id is replaced by static_build.sh (sed), not here.
Usage: python3 devos-decentralized-voting.py <fork root>"""
import pathlib, re, shutil, sys
root = pathlib.Path(sys.argv[1] if len(sys.argv) > 1 else '.') / 'devos-app'
(root / 'next.config.mjs').write_text("""/** @type {import('next').NextConfig} */
const nextConfig = {
  output: 'export',
  basePath: '/dapps/devos-decentralized-voting',
  trailingSlash: true,
  images: { unoptimized: true },
  eslint: { ignoreDuringBuilds: true },
  typescript: { ignoreBuildErrors: true },
};

export default nextConfig;
""")
for kind in ('OwnedElections', 'EnrolledElections'):
    src = root / f'app/{kind}/[electionName]/page.tsx'
    if src.exists():
        s = src.read_text()
        s = s.replace('import { useParams } from "next/navigation";', 'import { useSearchParams } from "next/navigation";\nimport { Suspense } from "react";')
        s = s.replace('const params = useParams();', 'const _sp = useSearchParams();\n  const params = { electionName: _sp.get("n") || "" };')
        m = re.search(r'export default function (\w+)\(', s); name = m.group(1)
        s = s.replace(f'export default function {name}(', f'function {name}(', 1)
        s += f'\nexport default function Page() {{\n  return <Suspense fallback={{null}}><{name} /></Suspense>;\n}}\n'
        dst = root / f'app/{kind}/view/page.tsx'; dst.parent.mkdir(parents=True, exist_ok=True); dst.write_text(s)
        shutil.rmtree(src.parent)
    p = root / f'app/{kind}/page.tsx'
    p.write_text(p.read_text().replace(f'router.push(`/{kind}/${{electionName}}`)', f'router.push(`/{kind}/view/?n=${{encodeURIComponent(electionName)}}`)'))
print('patched', root)
