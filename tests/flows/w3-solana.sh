#!/usr/bin/env bash
# w3-solana: build and deploy the w3 program, upload a static site with w3-uploader, then serve it back from chain through the Go gateway.
# Uses fresh throwaway keypairs only (the repo's committed sample signer is never used). Keys are never printed.
set -eu
cargo build-sbf --manifest-path=./w3/Cargo.toml --sbf-out-dir=dist/w3 2>&1 | tail -1
solana-keygen new --no-bip39-passphrase -s --force -o /tmp/sc-w3-prog.json >/dev/null
solana-keygen new --no-bip39-passphrase -s --force -o /tmp/sc-w3-signer.json >/dev/null
solana airdrop 100 $(solana address -k /tmp/sc-w3-signer.json) -u localhost >/dev/null
solana program deploy --program-id /tmp/sc-w3-prog.json -u localhost dist/w3/w3.so
PID=$(solana address -k /tmp/sc-w3-prog.json); echo "PROGRAM w3 $PID"
SK=$(python3 -c "
import json;b=bytes(json.load(open('/tmp/sc-w3-signer.json')));A='123456789ABCDEFGHJKLMNPQRSTUVWXYZabcdefghijkmnopqrstuvwxyz';n=int.from_bytes(b,'big');s=''
while n: n,r=divmod(n,58); s=A[r]+s
print('1'*(len(b)-len(b.lstrip(b'\0')))+s)")
mkdir -p /tmp/sc-w3-site && printf '<!doctype html><title>Hello from w3-solana</title><h1>Served from Solana accounts</h1>\n' > /tmp/sc-w3-site/index.html
(cd w3-uploader && cargo build --release 2>&1 | tail -1)
U=$PWD/target/release/w3-uploader; [ -x "$U" ] || U=$PWD/w3-uploader/target/release/w3-uploader
mkdir -p /tmp/sc-w3-run && cd /tmp/sc-w3-run
printf 'program: %s\nnetwork: localnet\nsigner: %s\ntrunk_size: 800\n' "$PID" "$SK" > w3-uploader.yaml; unset SK
RUST_LOG=info $U -a config_name -n solcollege 2>&1 | grep -vi signer | tail -3
RUST_LOG=info $U -a upload -d /tmp/sc-w3-site 2>&1 | grep -vi signer | tail -4
rm -f w3-uploader.yaml
cd - >/dev/null; cd gateway && go build -o /tmp/sc-w3-gateway . 2>&1 | tail -2
mkdir -p /tmp/sc-w3-gw && cd /tmp/sc-w3-gw && printf 'name_resolver: %s\nnetwork: localnet\nbind: :3105\n' "$PID" > gateway.yaml
/tmp/sc-w3-gateway start > /tmp/sc-w3-gw.log 2>&1 & GW=$!; trap 'kill $GW 2>/dev/null' EXIT; sleep 3
for i in 1 2 3 4 5; do OUT=$(curl -s -H 'Host: solcollege.w3sol.xyz' localhost:3105/index.html); [ -n "$OUT" ] && break; sleep 2; done
echo "GET solcollege.w3sol.xyz/index.html via gateway:"; echo "$OUT"
echo "$OUT" | grep -q 'Served from Solana accounts'
for s in $(solana transaction-history $PID -u localhost --limit 10 | grep -E '^[1-9A-HJ-NP-Za-km-z]{80,90}$'); do echo "SIG w3 $s"; done
