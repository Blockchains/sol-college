#!/usr/bin/env bash
# Box loop: every ~5 min, one push -> GitHub Actions build publishes the next queued lesson (PUBLISH_BATCH=1).
# Stops when stats.json on the live site reports waiting=0. gitleaks runs before every push (abort on finding).
cd "$(dirname "$0")/.."
INTERVAL="${INTERVAL:-300}"
while true; do
  w=$(curl -s --resolve sol.college:443:185.199.108.153 https://sol.college/stats.json | python3 -c "import json,sys;print(json.load(sys.stdin).get('waiting',1))" 2>/dev/null)
  [ "$w" = "0" ] && { echo "$(date -u +%FT%TZ) queue empty, stopping"; break; }
  busy=$(gh run list -w "Build and deploy Sol.College" -L 5 --json status -q '[.[]|select(.status=="queued" or .status=="pending" or .status=="waiting")]|length' 2>/dev/null)
  [ "${busy:-0}" != "0" ] && { sleep "$INTERVAL"; continue; }  # a build is already queued; it will pick up the elapsed-time batch
  echo "$(date -u +%FT%TZ) publish tick: waiting ${w:-?}" >> publish-batches.log
  git add publish-batches.log && gitleaks detect --source . --no-banner --redact >/dev/null 2>&1 && git commit -qm "publish: next lesson (waiting ${w:-?})" && git pull --rebase -q && gitleaks detect --source . --no-banner --redact >/dev/null 2>&1 && git push -q && echo "$(date -u +%FT%TZ) pushed (waiting ${w:-?})"
  sleep "$INTERVAL"
done
