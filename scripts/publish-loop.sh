#!/usr/bin/env bash
# Box loop: one publish tick per build. Each GitHub Actions build publishes ALL queued lessons (PUBLISH_BATCH=1000).
# Self-heals git state (detached HEAD / stale rebase) before every push. gitleaks runs before every push (abort on finding).
cd "$(dirname "$0")/.."
INTERVAL="${INTERVAL:-300}"
heal(){ git rebase --abort 2>/dev/null; git merge --abort 2>/dev/null; git checkout -q main 2>/dev/null || git checkout -q -B main origin/main; }
while true; do
  heal
  w=$(curl -s https://sol.college/stats.json | python3 -c "import json,sys;print(json.load(sys.stdin).get('waiting',1))" 2>/dev/null)
  [ "$w" = "0" ] && { echo "$(date -u +%FT%TZ) queue empty, stopping"; break; }
  busy=$(gh run list -w "Build and deploy Sol.College" -L 5 --json status -q '[.[]|select(.status!="completed")]|length' 2>/dev/null)
  [ "${busy:-0}" != "0" ] && { sleep "$INTERVAL"; continue; }  # a build is running/queued; it publishes everything waiting
  echo "$(date -u +%FT%TZ) publish tick: waiting ${w:-?}" >> publish-batches.log
  git add publish-batches.log && gitleaks detect --source . --no-banner --redact >/dev/null 2>&1 && git commit -qm "publish: queued lessons (waiting ${w:-?})" \
    && git pull --rebase -q origin main && gitleaks detect --source . --no-banner --redact >/dev/null 2>&1 && git push -q origin main \
    && echo "$(date -u +%FT%TZ) pushed (waiting ${w:-?})" || { echo "$(date -u +%FT%TZ) push failed; healing"; heal; git reset -q --soft origin/main 2>/dev/null; }
  sleep "$INTERVAL"
done
