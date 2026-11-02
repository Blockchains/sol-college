#!/usr/bin/env bash
# SCA (native escrow program): build, deploy to the local validator, and run the repo's own client flow
# (create sale -> buyer -> 3 arbiters -> approvals -> deposit -> dispute -> evidence -> votes -> claim).
# Pinata (IPFS, needs a paid/registered JWT) is replaced by a local stub that returns a fixed placeholder CID.
set -eu
(cd program/sca && cargo build-sbf 2>&1 | tail -2)
mkdir -p keys; for k in programowner program seller buyer arbiter1 arbiter2 arbiter3; do solana-keygen new --no-bip39-passphrase -s --force -o keys/$k.json >/dev/null; done
for k in programowner seller buyer arbiter1 arbiter2 arbiter3; do solana airdrop 50 $(solana address -k keys/$k.json) -u localhost >/dev/null; done
PID=$(solana address -k keys/program.json)
solana program deploy --keypair keys/programowner.json --program-id keys/program.json -u localhost program/sca/target/deploy/sca.so
echo "PROGRAM sca $PID"
cd test
sed -i "s/7f3bKvFg9WrUr3RGig5gGj8GnEFYMML86ffgxaH19ft1/$PID/" src/sca.ts
cat > src/pinata.ts <<'TS'
// Local stand-in for Pinata: the program only stores the CID bytes, so a fixed placeholder works offline.
const store: Record<string, object> = {};
export async function upload(obj: object): Promise<string> { const cid = "QmSolCollegeLocalPlaceholderCid00000000000000"; store[cid] = obj; return cid; }
export async function download(ipfs: string): Promise<object> { return store[ipfs] ?? {}; }
TS
npm install --no-audit --no-fund >/dev/null 2>&1
npx tsc
node dist/index.js | tee /tmp/sc-sca-flow.log
grep -oE '"[1-9A-HJ-NP-Za-km-z]{80,90}"' /tmp/sc-sca-flow.log | tr -d '"' | nl -w1 -s' ' | sed 's/^/SIG step/'
solana transaction-history $PID -u localhost --limit 30 | tail -3
