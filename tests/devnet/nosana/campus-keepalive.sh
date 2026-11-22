#!/usr/bin/env bash
# Keeps the Nosana campus worker and its rootless podman socket running (restarts either within 30 s). Devnet only.
# Start: nohup ./campus-keepalive.sh >/dev/null 2>&1 &   (does not survive a machine restart; start it again after one)
cd "$(dirname "$0")"
while true; do
  if ! curl -s --unix-socket /tmp/lab-podman/podman.sock http://d/_ping >/dev/null 2>&1; then
    mkdir -p /tmp/lab-podman; rm -f /tmp/lab-podman/podman.sock
    nohup podman system service --time=0 unix:///tmp/lab-podman/podman.sock >> /tmp/lab-podman/service.log 2>&1 &
    sleep 3
  fi
  pgrep -f 'node campus-worker.mjs' >/dev/null || nohup node campus-worker.mjs >> campus-worker.jsonl 2>> campus-worker.err &
  sleep 30
done
