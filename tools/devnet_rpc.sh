# Source this on the box to set DEVNET_RPC for deploys and tests. Never echo $DEVNET_RPC (it may contain a key).
# Order: $SOLANA_RPC, then $HELIUS_API_KEY, then /workspace/sol-college/keys/helius.env, then the public OnFinality URL.
# Hosted wallet apps keep using https://api.devnet.solana.com in the browser; only box-side work uses this.
# Usage: set -a; source tools/devnet_rpc.sh; set +a   (or: . tools/devnet_rpc.sh)
if [ -n "${SOLANA_RPC:-}" ]; then
  DEVNET_RPC=$SOLANA_RPC
else
  if [ -z "${HELIUS_API_KEY:-}" ] && [ -f /workspace/sol-college/keys/helius.env ]; then
    # shellcheck source=/dev/null
    . /workspace/sol-college/keys/helius.env
  fi
  if [ -n "${HELIUS_API_KEY:-}" ]; then
    DEVNET_RPC="https://devnet.helius-rpc.com/?api-key=${HELIUS_API_KEY}"
  else
    DEVNET_RPC=https://solana-devnet.api.onfinality.io/public
  fi
fi
export DEVNET_RPC
