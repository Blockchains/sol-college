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
  *) echo "no static recipe for $slug"; exit 2;;
esac
du -sh "$out"
