#!/usr/bin/env bash
# Runs the built tokengator API against a throwaway local Postgres and exercises register -> me via GraphQL.
# All secrets are generated per run and never printed.
set -eu
PG=${PG_BIN:-/home/box/pg/node_modules/@embedded-postgres/linux-x64/native/bin}; [ -x $PG/initdb ] || PG=/usr/lib/postgresql/17/bin; D=/tmp/sc-pg-tokengator; rm -rf $D; $PG/initdb -D $D -U postgres -A trust >/dev/null
$PG/pg_ctl -D $D -o "-p 5433 -k /tmp" -l $D.log start >/dev/null; trap '$PG/pg_ctl -D $D stop -m fast >/dev/null; kill $API 2>/dev/null || true' EXIT
solana-keygen new --no-bip39-passphrase -s -o /tmp/sc-tg-feepayer.json --force >/dev/null
cat > .env <<E
API_URL=http://localhost:3000/api
WEB_URL=http://localhost:3000
DATABASE_URL=postgresql://postgres@localhost:5433/tokengator?schema=public
DATABASE_PROVISION=true
AUTH_PASSWORD_ENABLED=true
AUTH_REGISTER_ENABLED=true
AUTH_SOLANA_ENABLED=true
COOKIE_DOMAINS=localhost
JWT_SECRET=$(openssl rand -hex 32)
SESSION_SECRET=$(openssl rand -hex 32)
HOST=127.0.0.1
PORT=3000
SOLANA_ENDPOINT=${SOLANA_ENDPOINT:-http://127.0.0.1:8899}
SOLANA_FEE_PAYER_SECRET_KEY=$(cat /tmp/sc-tg-feepayer.json)
SOLANA_FEE_PAYER_MINIMAL_BALANCE=0
E
pnpm -s cloak generate 2>/dev/null | grep -oE 'CLOAK_(MASTER_KEY|KEYCHAIN)=\S+' >> .env; grep -c '^CLOAK_' .env
pnpm prisma db push --skip-generate 2>&1 | tail -2
NODE_ENV=production node dist/apps/api/main.js > /tmp/sc-tg-api.log 2>&1 & API=$!
for i in $(seq 90); do curl -s -o /dev/null -w '%{http_code}' localhost:3000/api/uptime 2>/dev/null | grep -qE '200|404' && break; sleep 2; done
q(){ curl -s -c /tmp/sc-tg.jar -b /tmp/sc-tg.jar -H 'content-type: application/json' localhost:3000/graphql -d "$1"; echo; }
echo "uptime:"; q '{"query":"{ uptime }"}'
echo "register:"; q '{"query":"mutation { register(input:{username:\"solcollege\",password:\"localtest-only\"}) { id username role } }"}'
echo "me:"; q '{"query":"{ me { username role } }"}' | tee /tmp/sc-tg-me.json
grep -q '"username":"solcollege"' /tmp/sc-tg-me.json || { tail -30 /tmp/sc-tg-api.log; exit 1; }
echo "web UI:"; curl -s localhost:3000/ | grep -o '<title>[^<]*' || true
