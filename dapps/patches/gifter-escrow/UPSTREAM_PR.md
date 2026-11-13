# Upstream PR: gifter-escrow take_and_close and token dropdown

- Upstream repo: https://github.com/berkaycirak/gifter-escrow
- Upstream default branch: `main`
- Fork branch (based on upstream main, no Sol.College program id): `fix/take-and-close-pda-seeds`
  https://github.com/Blockchains/gifter-escrow/tree/fix/take-and-close-pda-seeds
- Working fork (deployed version): https://github.com/Blockchains/gifter-escrow/commit/fb2bbfd
- Commits on the PR branch: `db240db` (remove println!), `a9967c0` (bind PDA seed bytes), `5628bfc` (token list query key and DAS URL)

## Proposed title

fix: take_and_close aborts with an access violation; token dropdown stays empty

## Proposed body

`take_and_close` never completed on devnet: the program aborted with an access violation, so a taker could not finish the swap.

There were two causes in the program:

1. `send_to_maker` started with `println!("Hello")`, which is not valid in a BPF program.
2. After removing that, Take still aborted during account validation (`Instruction: TakeAndClose`, then access violation `0x10008`, no inner CPI). The `seeds` attribute used `gifter_escrow_state.escrow_id.to_le_bytes().as_ref()`, which is a dangling pointer. The fix verifies the PDA in the handler with owned locals (and uses the same pattern in `refund`).

A localnet regression test is in `contract/tests/take-and-close.ts`: it creates two mints, opens an escrow, runs `take_and_close`, and checks both token balances and that the vault and state accounts are closed.

Separately, the Create form's token dropdown stayed empty because `useWalletTokens` put `walletAddress?.toBase58` (the function, not the string) in the react-query key, so a first fetch with a null wallet was never retried. The hook now uses the base58 string as the query key and as `ownerAddress`. The Helius DAS URL is read from `NEXT_PUBLIC_HELIUS_DAS_URL` instead of a hard-coded key.

This work comes from the Sol.College learning environment (https://sol.college), where the app is hosted at https://sol.college/dapps/gifter-escrow/ on a fixed devnet program.

### Devnet proof (fixed program `45C1bSkFCbjrqiQHqm8oS6J88jirW8rC46Qiu6TvoY6x`)

- Before (unfixed program `6Z5cvVUc…`): take aborted with an access violation: [devnet explorer, signature starting ck53TqoU](https://explorer.solana.com/tx/ck53TqoU8UfpBav2V3bE1oy4Wm2qvxeU6bgibkXqzCsbP4YbBxDGK98bJxoowGpKNwkkPotBtCxVfUQMEm2zZu7?cluster=devnet)
- After, T takes escrow #1 (pays 5 of mint B, receives 10 of mint A, vault and state close): `33yMgZzAaH3mMcHgSmQBRVb4FeRmu5gX6nkAMfJU2T8F8sAwqMDTVfgsVcg7MXPM28GoAo7RPC7E35NhkNSrLXZd`
- After, M refunds escrow #2 once a take for more mint B than the taker holds is rejected: `3qwx8QBC6Ai7a6ANH4PoaCqJS6DszHDXfPBFaVbN2wKZEtW9Rtu2PVmG3jChfZi4sffywm5npuJhir6RYgCiHjqJ`
- Upgrade that landed the seed-byte fix: `4HaARQTeA2dbGcQ73QuD3GDyrtd5xvZJHcDKZRKARioDdHNEjnYziDauM8d2Pi3tVZSZVhEunxkHvC872aafvs9n`

Hosted UI click-through (Create Escrow dialog; token dropdown listed mint A and mint B; then refund):

- UI create (give 1 of mint A, want 1 of mint B): `2c6QNtYzCDr2McZcXG9dsyD6e951w8EvA5QBAgwxCYG9uDjYD2a3B4xf9UV7QGk3rdJ7oDNNfex9bBHZTiMzujCk`
- UI refund of that escrow: `2GsfGiPtjNWfe32hunPNwEX7tLqVzP6v5zUmXe8j1XmbNWJzwzYnE84QbZKnGm5EHJNHrk4TXKgYM3RgX9rPPTTD`

Explorer (devnet): https://explorer.solana.com/tx/33yMgZzAaH3mMcHgSmQBRVb4FeRmu5gX6nkAMfJU2T8F8sAwqMDTVfgsVcg7MXPM28GoAo7RPC7E35NhkNSrLXZd?cluster=devnet

## Status

Click-through recorded. Opening the PR against berkaycirak/gifter-escrow from Blockchains:fix/take-and-close-pda-seeds.
