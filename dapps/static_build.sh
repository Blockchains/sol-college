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
  *) echo "no static recipe for $slug"; exit 2;;
esac
du -sh "$out"
