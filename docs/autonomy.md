# CTO autonomy (since 2026-11-15 16:23 GMT, owner instruction)

## What runs without the owner
`cto-autonomy.yml`: every 2 hours (cron `17 */2 * * *`, UTC) and on demand. Environment `minds` (main only,
no manual reviewer). Projects and the standing approval are listed in `config/autonomy.json`. Each pass, per project:

1. Reconcile pending Mind tasks from conversation history (never resends) and act on **validated** results:
   - research plan → opens at most one `research-question` issue per run (label `mind-proposed`, opened by
     github-actions[bot]) after deterministic checks: length, no secrets, no emails, no excluded topics
     (mainnet/keys/faucet), links only to github.com or sol.college, not a duplicate (hash marker).
   - adoption draft → builds the adoption package with code-assembled evidence (GitHub runs, commits, hashes) and
     the Mind's narrative marked `mind-draft`.
   - Lab Reporter → publishes the checked summary to `records/public/status/<slug>.json` (shown on the campus).
   - PR triage and upstream impact → kept private in the control repo; a public activity line only.
2. Upstream: reads the real upstream head; on change, records it (`records/public/upstream`) and asks the Mind for
   an impact assessment.
3. Lab pull requests (lab-fork PRs to upstream, and PRs inside the lab fork): for each new head SHA, dispatches
   `candidate-validation` (unless genuine evidence already exists) and asks the Mind to triage.
4. Passing candidates without a package: asks the Mind for an adoption draft.
5. Every 72 h: asks for the next research question. Every 12 h: asks for the Lab Reporter status.
Limits: at most 3 new Mind tasks and 1 issue per project per run. Tasks without a reply after 48 h are closed
without resend. Private records: `Blockchains/sol-college-control` (written through a deploy key scoped to that one
repo). The campus build is re-triggered after each pass.

## Coding, treasury and operations (since 2026-11-15 17:10 GMT, owner instructions t687u / t688u)
6. Coding: for the oldest open research question of a project with no patch yet, the Mind gets an `experiment-patch`
   task with the question, the lab head SHA and the files the question links to. A validated reply may carry one
   `{type:"patch"}` action (unified diff). The deterministic gate (`pilot/src/lab/patch.ts`) runs; the diff is
   stored privately and, after the control repo is pushed, `lab-patch.yml` applies it to `sc-lab/<project>/<task>`
   on the lab fork, runs gitleaks, pushes with that fork's deploy key and dispatches `candidate-validation` on the
   exact SHA. A lab PR on the fork is opened when `SC_LAB_PR_TOKEN` is configured; without it, the next pass treats
   `sc-lab/*` branch heads as candidates anyway (validation, PR triage, adoption draft).
7. Upstream PRs for verified fixes (standing permission): one focused PR per project, duplicate-checked. Opening a
   PR on someone else's repository needs a token with that right; GitHub Actions' token has none and deploy keys
   cannot open PRs, so this stays MANUAL SETUP REQUIRED until `SC_LAB_PR_TOKEN` (classic PAT, `public_repo`) exists in environments
   `minds` and `lab-coding`. Implemented in `runProject` step 4a: only for patches that change program/app source
   (`isFixPatch`; tests-only patches stay lab experiments), only after the newest genuine validation of the exact SHA
   passed, and only when the upstream has no open PR from the lab fork. The token is never given to a Mind.
8. Devnet treasury: a validated reply may carry `{type:"devnet-transfer",recipient,lamports,reason}`; it is
   dispatched to `devnet-treasury.yml`. **No caps and no recipient allowlist** (t688u); devnet only, key only as a
   protected secret, append-only ledger `records/public/treasury/ledger.jsonl`.
9. Operations: every pass writes `records/public/minds/<slug>.json` from the SDK (getMind status, cognition balance,
   daily usage, usage by tool, equipped Skills and Apps, project conversation count, SDK version).
Projects (7): gifter-escrow, sentient-send, ciphervault, colosseum, poe-solana, trustlock, orboracle-solana.

## What it never does
Create/enable/disable Minds, change Circles, pause/resume, equip Skills, accept packages, issue certificates
without a verified human acceptance, push to main or to upstream repositories (upstream only via PRs), touch mainnet, give any Mind a key, run
contributor code (validation runs in the separate secret-free workflow).

## What still needs the owner
1. `/sc-accept …` comment for each adoption package (the human acceptance; the bot is refused by design).
2. Approving `minds-admin` runs: Mind lifecycle (provision/pause/resume), Circle changes, equip/unequip.
3. Adding a project to `config/autonomy.json` or changing the standing approval (a commit to main).
4. Writing code: Minds now write patches (see 6); a token for opening PRs (`SC_LAB_PR_TOKEN`) is the one missing piece.

## Evidence of live runs (2026-11-15, GMT)
| Run | When | Result |
| --- | --- | --- |
| [43736138834](https://github.com/Blockchains/sol-college/actions/runs/43736138834) | 16:35 | first successful run: research-plan and progress-report tasks sent to both Minds; status published |
| [43737400469](https://github.com/Blockchains/sol-college/actions/runs/43737400469) | 16:47 | gifter replies validated (report published, plan proposals all filtered by the topic gate); sentient replies parked for operator review |
| [43737735184](https://github.com/Blockchains/sol-college/actions/runs/43737735184) | 16:50 | after the fixes below: Mind-proposed research issues opened, [#4](https://github.com/Blockchains/sol-college/issues/4) (gifter-escrow) and [#5](https://github.com/Blockchains/sol-college/issues/5) (sentient-send); both Lab Reporter statuses published to the campus |

Fixes made from those runs (all fail-closed, none resend a message):
- Boundary disclaimers such as "no mainnet keys" no longer count as raising an excluded topic; real mentions still do.
- `evidenceRefs` may cite source ids as well as evidence ids, matching the facts policy.
- A task in operator review is re-evaluated against correlated replies already in history (the Mind had sent a
  corrected JSON reply for the same taskId), at most 3 times; nothing is resent.
- A repeated `[research] <project>:` prefix in a proposal title is stripped.

sentient-send baseline validation (build-only, exact SHA a1c663d): [43736971628](https://github.com/Blockchains/sol-college/actions/runs/43736971628)
passed after two workflow fixes: the Anchor 0.32.1 release binary pinned by sha256 (npm has none), and, because the
candidate has no Cargo.lock, a lockfile resolved for the platform-tools cargo 1.84 plus the per-project pin
`blake3@1.8.2` (`validation.cargoPins`). Earlier failures: 43736019634, 43736417345, 43736709507.
