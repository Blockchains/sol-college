#!/usr/bin/env bash
# Background loop: when devnet balance covers the next program (≈2x .so size in rent + margin), deploy + prove it, rebuild, commit, push (gitleaks first).
cd "$(dirname "$0")/.."
Q="${QUEUE:-poe-solana valhalla}"
while true; do
  extra=$(cat /workspace/sol-college-dapp-queue.txt /workspace/sol-college/dapp-queue.txt 2>/dev/null | tr '\n' ' ')
  for s in $Q $extra; do
    [ -f dapps/deployed/$s.json ] && python3 -c "import json,sys;sys.exit(0 if json.load(open('dapps/deployed/$s.json')).get('devnet') else 1)" && continue
    so=$(ls dapps/build/$s/*.so 2>/dev/null | head -1); [ -z "$so" ] && continue
    need=$(python3 -c "print(round(__import__('os').path.getsize('$so')*0.00000696*1.05+0.1,2))")
    bal=$(solana balance -ud 2>/dev/null | awk '{print $1}')
    python3 -c "import sys;sys.exit(0 if float('${bal:-0}')>=$need else 1)" || { echo "$(date +%H:%M) wait $s need $need have $bal"; continue; }
    echo "$(date +%H:%M) deploying $s"; timeout 1800 python3 dapps/deploy.py $s devnet >/tmp/ad-$s.log 2>&1
    python3 -c "
import json;f='dapps/deployed/$s.json';d=json.load(open(f));d.setdefault('mainnet',None);json.dump(d,open(f,'w'),indent=1)"
    python3 scripts/build.py >/dev/null 2>&1; git add -A dapps && gitleaks detect --source . --no-banner --redact >/dev/null 2>&1 && git commit -qm "dapps: devnet deploy + proof for $s" && gitleaks detect --source . --no-banner --redact >/dev/null 2>&1 && git pull --rebase -q && git push -q && echo "$(date +%H:%M) pushed $s"
  done
  sleep 600
done
