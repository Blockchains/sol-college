# Limitations (honest list)

- No live CTO Mind for gifter-escrow yet: creating one needs approval, so coordination requests fail closed and no
  structured task has been sent to any Mind.
- No private control repository yet (needs approval), so privileged workflows that would store Minds output refuse to run.
- Acceptance and certificate are implemented and tested, but the real acceptance must be posted by the human reviewer.
  The operator agent shares the `Blockchains` GitHub identity, which GitHub cannot tell apart (see permissions.md).
- `main` has no branch protection; CODEOWNERS is advisory until a ruleset is enabled.
- The file-lock store serialises one store; two independent stores (e.g. two runners without the shared control repo)
  could each record an intent. Workflow concurrency groups reduce but do not eliminate this.
- Live events (`subscribeEvents`, `eventsIterator`) are not used: there is no secure always-on runtime. Not exposed to browsers.
- Attendance: no verified Solana data connection is configured, so submissions stay `pending` until manual review; no
  automatic verification, no faucet automation. Subscriptions are manual entitlements, not verified payments. Mind
  wallet metadata (`walletAddress`, `chain: base`) does not provide Solana signing or billing.
- Credentials are platform-published records: not accredited, not on-chain, not cryptographically signed.
- Candidate validation runs on GitHub-hosted runners; isolation is GitHub's job isolation, nothing stronger. The
  untrusted job downloads toolchains from release.anza.xyz and npm (build tools, not hosted services).
- Pre-existing `verify-forks.yml` still uses tag-pinned actions; it is outside the pilot and untouched.
- The SDK package is labelled private alpha; its API may change. The contract test will flag missing methods.
