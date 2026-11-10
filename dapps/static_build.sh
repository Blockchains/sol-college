#!/usr/bin/env bash
# Build non-Anchor forks' own frontends as static sites hosted at /dapps/<slug>/. Usage: dapps/static_build.sh <slug> <clone dir>
set -euo pipefail
slug=$1; src=$2; out=$(cd "$(dirname "$0")" && pwd)/static/$slug; rm -rf "$out"; mkdir -p "$out"
case $slug in
  solstage-web) cd "$src" && npm ci --no-audit --no-fund --legacy-peer-deps >/dev/null && npx tsc && npx vite build --base /dapps/$slug/ && cp -r dist/. "$out/";;
  elyse) cd "$src/elyse-app" && npm ci --no-audit --no-fund --legacy-peer-deps >/dev/null && npm run build && cp -r dist/. "$out/";;
  stealthfolio) cd "$src/nextjs" && npm ci --no-audit --no-fund --legacy-peer-deps >/dev/null && cat > next.config.mjs <<C
export default { output: 'export', basePath: '/dapps/$slug', images: { unoptimized: true }, eslint: { ignoreDuringBuilds: true }, typescript: { ignoreBuildErrors: false } };
C
     npx next build && cp -r out/. "$out/";;
  poe-solana) # fork's own Next.js app, pointed at the devnet program built from the same commit (its committed app IDL is from a later program version)
     cp "$(dirname "$out")/../build/poe-solana/poe.json" "$src/app/src/idl/poe.json"; cd "$src/app"
     printf "module.exports = { output: 'export', basePath: '/dapps/%s', trailingSlash: true, images: { unoptimized: true }, eslint: { ignoreDuringBuilds: true } }\n" "$slug" > next.config.js
     python3 - <<'P'
p='src/app/poll/[id]/page.tsx'; s=open(p).read()
s=s.replace('export default function PollDetails({ params }: { params: { id: string } }) {','function PollDetails() {\n  const searchParams = useSearchParams();\n  const params = { id: searchParams.get("id") || "0" };',1)
s=s.replace('import { useRouter } from "next/navigation";','import { useRouter, useSearchParams } from "next/navigation";\nimport { Suspense } from "react";',1)
open('src/app/poll/page.tsx','w').write(s+'\nexport default function PollPage() {\n  return (<Suspense fallback={null}><PollDetails /></Suspense>);\n}\n')
for f,a,b in [('src/components/poll-card.tsx','href={"/poll/" + pollId}','href={"/poll/?id=" + pollId}'),('src/components/my-polls-tab.tsx','router.push("/poll/" + poll.id)','router.push("/poll/?id=" + poll.id)')]:
  t=open(f).read(); assert a in t; open(f,'w').write(t.replace(a,b))
P
     rm -rf "src/app/poll/[id]"; npx -y yarn@1 install --frozen-lockfile --ignore-engines >/dev/null && npx next build && cp -r out/. "$out/";;
  picassol-hackathon) # fork's own Next.js 12 app on the devnet program; the MongoDB points API (pages/api) is not hosted
     cd "$src/frontend"; sed -i 's/"5rV2CJ8bYV4qEt8qcmhZ1Ty3o6eM7K1LAJDDFipPNyx2"/"GsFGX3pzdgzugAfjcxH9Lbbz2aPZgXyvBoXkNnmxXwuY"/' pages/index.tsx; rm -rf pages/api
     printf "module.exports = { basePath: '/dapps/%s', trailingSlash: true, images: { unoptimized: true }, eslint: { ignoreDuringBuilds: true }, typescript: { ignoreBuildErrors: true } }\n" "$slug" > next.config.js
     npm ci --no-audit --no-fund --legacy-peer-deps >/dev/null
     NEXT_PUBLIC_SOLANA_RPC_ENDPOINT=https://api.devnet.solana.com NEXT_PUBLIC_FEE_RECIPIENT_ADDRESS=BP1uwSaTHXvgN8sPQJgaor6iBoT3KYjnZNnkvJr71zDv NEXT_PUBLIC_FEE_AMOUNT_SOL=0 sh -c 'npx next build && npx next export -o out' && cp -r out/. "$out/";;
  trustlock) # fork's own Next.js 14 app on the program deployed from switch/ (see dapps/deployed/trustlock.json)
     cd "$src"; sed -i "s/8hK7vGkWap7CwfWnZG8igqz5uxevUDTbhoeuCcwgvpYq/6km4NhrxLPcMTXVmZyKsBBsmmoqXHu1NT6P5uFL5FFjP/" components/DeadManSwitch.tsx
     printf "module.exports = { output: 'export', basePath: '/dapps/%s', trailingSlash: true, images: { unoptimized: true }, eslint: { ignoreDuringBuilds: true }, webpack: (c) => { c.resolve.fallback = { fs: false }; return c; } }\n" "$slug" > next.config.js
     npm ci --no-audit --no-fund --legacy-peer-deps >/dev/null && npx next build && cp -r out/. "$out/";;
  gree) # fork's own create-solana-dapp app; author's commented initNft re-enabled (tests/devnet/patches/gree.patch)
     cd "$src" && git apply "$(dirname "$out")/../../tests/devnet/patches/gree.patch" && npm ci --no-audit --no-fund --legacy-peer-deps >/dev/null && npx nx build web --baseHref=/dapps/$slug/ --skip-nx-cache && cp -r dist/web/. "$out/";;
  web3-splitter) # fork's own Vue 3 + Vite app on the program deployed from splitterprogram/ (see dapps/deployed/web3-splitter.json); hash routing for static hosting
     cd "$src"; sed -i "s/EbSG8YorD2N1QHoiayDba3cuDQsyUJ7ysocjHVaLb9b5/4c4CWSs9m2VbNW9Hn7WqAZv84JMKRWtq5fESGWT5yjm1/" src/lib/useWorkspace.ts src/lib/splitterprogram.json
     sed -i 's/import { createWebHistory, createRouter }/import { createWebHashHistory, createRouter }/; s/history: createWebHistory(import.meta.env.BASE_URL)/history: createWebHashHistory()/' src/main.js
     npx -y yarn@1.22.22 install --frozen-lockfile --ignore-engines >/dev/null && npx vite build --base=/dapps/$slug/ && cp -r dist/. "$out/";;
  orboracle-solana) # fork's own Next.js 15 static export on the program deployed from anchor/programs/oracle (see dapps/deployed/orboracle-solana.json)
     cd "$src"; grep -rl 9oPLPE3PC9ok7T8UL9ZMfrNyPkhtaHh1mM9wFk2fWEVJ anchor/src | xargs sed -i "s/9oPLPE3PC9ok7T8UL9ZMfrNyPkhtaHh1mM9wFk2fWEVJ/3xqEVjy3zVjVnyb4qBa5xoBAQ9x4JhHowcV6JPQWXXqx/g"
     sed -i "s#basePath: '/solana.orb-oracle.stabulity.nexus'#basePath: '/dapps/$slug', trailingSlash: true#" next.config.ts
     npm ci --no-audit --no-fund --legacy-peer-deps >/dev/null && npx next build && cp -r out/. "$out/";;
  sentient-send) # fork's own Next.js app (frontend/) as a static export on the program deployed from programs/prediction-market (see dapps/deployed/sentient-send.json)
     cd "$src/frontend" && python3 "$(dirname "$out")/../../tests/devnet/patches/sentient-send.py" BP1uwSaTHXvgN8sPQJgaor6iBoT3KYjnZNnkvJr71zDv
     sed -i "s/C3LRoEztvLPioY3ruddYGTT9qxzvqBivHzgmpGJuQ9CT/22cDf4bbQM34qF9fcX5v6wb6a8cR9XsZMRpGPUtPx2b5/g" src/lib/constants.ts src/lib/idl.ts
     npm install --no-audit --no-fund >/dev/null && npm i -D --no-audit --no-fund @types/bn.js >/dev/null && npx next build && cp -r out/. "$out/";;
  ciphervault) # fork's own React + Vite app (app/) on the program deployed from programs/cipher-valut (see dapps/deployed/ciphervault.json)
     cd "$src/app" && python3 "$(dirname "$out")/../../tests/devnet/patches/ciphervault.py" DYfkSaTdCBjEFk1fGWhBc7uR7mSVBz2dogsaupzxVzgG
     npx -y yarn@1.22.22 install --frozen-lockfile --ignore-engines >/dev/null && npx vite build && cp -r dist/. "$out/";;
  colosseum) # fork's own Next.js 15 app (ui/) on the program deployed from contract/programs/staking (see dapps/deployed/colosseum.json); admin = test wallet m4Ac...
     cd "$src/ui" && python3 "$(dirname "$out")/../../tests/devnet/patches/colosseum.py" JxbbWRxjVcbAE98o13Yo2EFFEP1paTX8q8SvuPvSaDL m4AcRjHcQzpvejFnU9KBEgf9z7pwni84CrGpARCoJpr
     npx -y yarn@1.22.22 install --frozen-lockfile --ignore-engines >/dev/null && npx next build && cp -r out/. "$out/";;
  stakes-main) # fork's own React + Vite app (app/) on the program deployed from programs/stakes-wtf (see dapps/deployed/stakes-main.json); hash routing
     cd "$src/app" && sed -i "s/stkWEMeJyUyoqZu6C65z21Vzt3CezXRuix7oqJ78RwS/EeLuB1th9zFmokFiXgz78fLoD4rWfjLrAcFYBrQEjXoD/" src/constants/solana.ts
     python3 "$(dirname "$out")/../../tests/devnet/patches/stakes-main.py"
     npx -y yarn@1.22.22 install --frozen-lockfile --ignore-engines >/dev/null && VITE_RPC_URL=https://api.devnet.solana.com npx vite build --base=/dapps/$slug/ && cp -r dist/. "$out/";;
  votara) # fork's own React + Vite app (client/votara-client) on the program deployed from votara/programs/votara (see dapps/deployed/votara.json); hash routing + TokenBalance fix
     cd "$src/client/votara-client" && sed -i "s/CXJXjwHGo67zYveByRp2aydFgXHRcPTEQbRt8iNQEtvF/CwcPGjsQLgCkLsRtmhdypJLCqynT2BnzMAxaBpgcRuLt/g" src/constants/constant.tsx src/idl/votara.json
     python3 "$(dirname "$out")/../../tests/devnet/patches/votara.py"
     npm ci --no-audit --no-fund >/dev/null && npx vite build --base=/dapps/$slug/ && cp -r dist/. "$out/";;
  barn) # fork's own Next.js app (app/) as a static export on the program deployed from protocol/programs/barn (see dapps/deployed/barn.json); per-account pages read ?a=<pk>
     cd "$src" && sed -i "s/Aoofv5iGzdDeyySpT9QsiFaK7Db7SKyycb7nTEU1oTYE/EmyKYV3hFaFw4znLhGSTG6Eo4QGadVb6TnkvWYYm8X77/g" protocol/ts/src/idl/barn.json protocol/ts/src/idl/barn.ts
     python3 "$(dirname "$out")/../../tests/devnet/patches/barn.py"
     npx -y pnpm@9.4.0 install --frozen-lockfile >/dev/null && (cd protocol/ts && npx -y pnpm@9.4.0 build) && cd app && NEXT_PUBLIC_RPC_ENDPOINT=https://api.devnet.solana.com NEXT_PUBLIC_RPC_CLUSTER=devnet npx next build && cp -r out/. "$out/";;
  hackathon-prediction-market-solana) # fork's own CRA app (prediction-market-frontend) on the program deployed from programs/prediction-market (see dapps/deployed/hackathon-prediction-market-solana.json)
     cd "$src" && sed -i "s/ACZKSY2dWcYHLF3ZPeUwcLVi3h6n2rsyTqXTLe42gxG3/8REA8GCiJh1c5ZsosFyT1SFmHjFqoZoonyCVrw1CbPFH/g" prediction-market-frontend/src/contexts/PredictionMarketContext.tsx prediction-market-frontend/src/prediction_market.json prediction-market-frontend/src/prediction_market.ts prediction-market-frontend/src/prediction_market_idl.ts
     # dependency installs as used on 2026-11-10: root yarn install (the app imports @solana/spl-token from the root), app npm install, then ajv@8 for CRA
     yarn install --frozen-lockfile >/dev/null && cd prediction-market-frontend && python3 "$(dirname "$out")/../../tests/devnet/patches/hackathon-prediction-market-solana.py"
     npm install --legacy-peer-deps --no-audit --no-fund >/dev/null && npm i --no-save --legacy-peer-deps ajv@8 >/dev/null && PUBLIC_URL=/dapps/$slug GENERATE_SOURCEMAP=false CI=false npx react-app-rewired build && cp -r build/. "$out/";;
  pulsefund-sol) # fork's own Next.js app (frontend/) as a static export on the program deployed from anchor-project/programs/smart-contracts (see dapps/deployed/pulsefund-sol.json)
     cd "$src/frontend" && sed -i "s/CQcG2qZooAYoeE96ZYKJd3omq2DPWHozSceSnuCxRv8U/DMZWuAaGAS8wKmdk7x6SczU5JCSrUWaYuZi7HKt6N6xe/g" src/idl/idl.json
     python3 "$(dirname "$out")/../../tests/devnet/patches/pulsefund-sol.py"
     npx -y yarn@1.22.22 install --frozen-lockfile >/dev/null && npx next build && npx next export -o out && cp -r out/. "$out/";;
  chinesepowered-solana-cypherpunk) # fork's own Next.js app (UniProof) as a static export on the program deployed from programs/uniproof (see dapps/deployed/chinesepowered-solana-cypherpunk.json)
     cd "$src" && sed -i "s/EZJvyE9P18XuEX1JsEpGcyoRkEz9c9dvYui6364K86cy/3VR7pfgtaE1oeEeHC1ouLUXDAEnh9nhaP1D5Ex3gWcUD/g" src/idl/uniproof.ts src/lib/solana/uniproof-client.ts
     python3 "$(dirname "$out")/../../tests/devnet/patches/chinesepowered-solana-cypherpunk.py"
     npx -y pnpm@9 install --frozen-lockfile >/dev/null && npx next build && cp -r out/. "$out/";;
  *) echo "no static recipe for $slug"; exit 2;;
esac
du -sh "$out"
