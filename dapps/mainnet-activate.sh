#!/usr/bin/env bash
# Background watcher: polls each dapp's own mainnet wallet (and the shared deploy wallet) every 5 min; see dapps/mainnet_activate.py.
# Start: nohup dapps/mainnet-activate.sh >>/tmp/mainnet-activate.log 2>&1 &
cd "$(dirname "$0")/.."
while true; do timeout 3600 python3 dapps/mainnet_activate.py once; sleep "${INTERVAL:-300}"; done
