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

## What it never does
Create/enable/disable Minds, change Circles, pause/resume, equip Skills, accept packages, issue certificates
without a verified human acceptance, comment on or push to upstream repositories, touch mainnet or keys, run
contributor code (validation runs in the separate secret-free workflow).

## What still needs the owner
1. `/sc-accept …` comment for each adoption package (the human acceptance; the bot is refused by design).
2. Approving `minds-admin` runs: Mind lifecycle (provision/pause/resume), Circle changes, equip/unequip.
3. Adding a project to `config/autonomy.json` or changing the standing approval (a commit to main).
4. Writing code: Minds cannot push code, so experiments still need a contributor (human or coding agent) to open the
   lab PR. Everything after the PR is automatic.
