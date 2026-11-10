"""Make the barn fork's Next.js app (app/) build as a static site for sol.college.

Run from the fork root. What it changes, and only this:
- app/next.config.mjs: output 'export', basePath /dapps/barn, trailingSlash, unoptimized images.
- The three dynamic pages app/src/app/{project,program,profile}/[address]/page.tsx can't be pre-rendered
  for accounts that don't exist yet, so each moves to .../view/page.tsx and reads the address from
  ?a=<pubkey> (wrapped in Suspense, as Next needs for useSearchParams in a static export).
- Links to /project/<pk>, /program/<pk>, /profile/<pk> become /<kind>/view/?a=<pk>.
"""
import pathlib, re, shutil
root = pathlib.Path('app')
(root / 'next.config.mjs').write_text('''/** @type {import('next').NextConfig} */
const nextConfig = {
\toutput: "export",
\tbasePath: "/dapps/barn",
\ttrailingSlash: true,
\timages: { unoptimized: true },
};

export default nextConfig;
''')
for kind in ('project', 'program', 'profile'):
    src = root / f'src/app/{kind}/[address]/page.tsx'
    s = src.read_text()
    m = re.search(r'export default function (\w+)\(\{ params \}: \{ params: \{ address: string \} \}\) \{', s)
    name = m.group(1)
    s = s.replace(m.group(0), f'function {name}Inner() {{\n\tconst params = {{ address: useSearchParams().get("a") || "" }};')
    s = s.replace('"use client";\n', '"use client";\n\nimport { Suspense } from "react";\nimport { useSearchParams } from "next/navigation";\n', 1)
    s += f'\nexport default function {name}() {{\n\treturn (\n\t\t<Suspense fallback={{null}}>\n\t\t\t<{name}Inner />\n\t\t</Suspense>\n\t);\n}}\n'
    dst = root / f'src/app/{kind}/view/page.tsx'; dst.parent.mkdir(exist_ok=True); dst.write_text(s)
    shutil.rmtree(src.parent)
for f in (root / 'src').rglob('*.tsx'):
    s = f.read_text(); t = re.sub(r'href=\{`/(project|program|profile)/\$\{', r'href={`/\1/view/?a=${', s)
    if t != s: f.write_text(t); print('links', f)
print('patched')

# Sample metadata the on-chain records point at (the app reads each account's `uri` as JSON).
# These are served from /dapps/barn/meta/ and are labelled as sol.college test data.
import json
meta = {
    'sponsor.json': {'name': 'sol.college test sponsor', 'bio': 'Devnet test profile made by the sol.college scripts.'},
    'dev.json': {'name': 'sol.college test dev', 'bio': 'Devnet test profile made by the sol.college scripts.'},
    'program.json': {'name': 'sol.college test grant program', 'description': 'Devnet-only grant program used to check the app works.'},
    'project.json': {'name': 'sol.college test project', 'description': 'Devnet-only project used to check the app works.', 'objectives': ['Get a milestone paid on devnet']},
    'grant.json': {'name': 'sol.college test grant', 'description': 'A 0.02 devnet SOL grant.'},
    'milestone.json': {'name': 'sol.college test milestone', 'description': 'A devnet-only milestone.'},
}
d = root / 'public/meta'; d.mkdir(parents=True, exist_ok=True)
for k, v in meta.items(): (d / k).write_text(json.dumps(v, indent=2) + '\n')
