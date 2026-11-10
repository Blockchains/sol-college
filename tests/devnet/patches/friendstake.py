"""Static-export patch for friendstake (app/friendstake/web, Next 13.4 + Nx).
- next.config.js: output 'export', basePath /dapps/friendstake, trailingSlash, images unoptimized.
- The dynamic pages bet/[address], list-bets/[address] and account/[address] can't be pre-rendered for
  accounts that don't exist yet, so each moves to .../view/page.tsx and reads the address from ?a=.
  The bet list's 'See More' link is a plain <a>, so it gets the basePath written in.
- Removes the scaffold's app/api/hello route (not used by the app; not exportable).
- Program id is replaced by static_build.sh (sed), not here.
Usage: python3 friendstake.py <repo root>   (the fork root, containing app/friendstake/web)"""
import pathlib, re, shutil, sys
root = pathlib.Path(sys.argv[1] if len(sys.argv) > 1 else '.') / 'app/friendstake/web'
cfg = root / 'next.config.js'
s = cfg.read_text()
if "output: 'export'" not in s:
    s = s.replace('const nextConfig = {', "const nextConfig = {\n  output: 'export',\n  basePath: '/dapps/friendstake',\n  trailingSlash: true,\n  images: { unoptimized: true },", 1)
    cfg.write_text(s)
for kind in ('bet', 'list-bets', 'account'):
    src = root / f'app/{kind}/[address]/page.tsx'
    if src.exists():
        body = src.read_text()
        m = re.search(r'return <(\w+) />;', body)
        comp = m.group(1)
        body = body.replace("import ", "import { Suspense } from 'react';\nimport ", 1).replace(f'return <{comp} />;', f'return <Suspense fallback={{null}}><{comp} /></Suspense>;')
        dst = root / f'app/{kind}/view/page.tsx'
        dst.parent.mkdir(parents=True, exist_ok=True)
        dst.write_text(body)
        shutil.rmtree(src.parent)
for f in ('components/bet/bet-info.tsx', 'components/bet/bet-list.tsx', 'components/account/account-detail-feature.tsx'):
    p = root / f; s = p.read_text()
    s = s.replace("import { useParams } from 'next/navigation';", "import { useSearchParams } from 'next/navigation';")
    s = s.replace('const params = useParams();', "const _sp = useSearchParams();\n  const params = { address: _sp.get('a') || '' };")
    s = s.replace('}, [params]);', '}, [params.address]);')
    p.write_text(s)
for f, a, b in (('components/account/account-list-feature.tsx', '`/account/${', '`/account/view?a=${'),
                ('components/bet/bet-ui.tsx', 'href={`/bet/${', 'href={`/dapps/friendstake/bet/view?a=${'),  # plain <a>, so Next's basePath isn't applied
                ('components/bet/bet-list-connect.tsx', '`/list-bets/${', '`/list-bets/view?a=${')):
    p = root / f; p.write_text(p.read_text().replace(a, b))
shutil.rmtree(root / 'app/api', ignore_errors=True)
print('patched', root)
