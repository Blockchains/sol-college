# Permissions

## Workflow permissions
| Workflow | Token | Secrets | Environment | Runs contributor code |
| --- | --- | --- | --- | --- |
| pilot-ci | contents: read | none | none | no (this repo only) |
| candidate-validation | contents: read | **none** | none | **yes, isolated** (untrusted-validate job only) |
| minds-smoke-test | contents: read | Builder key | minds / minds-admin (message) | no |
| minds-admin | contents: read | Builder key, mapping | minds (read) / minds-admin (mutate) | no |
| coordination-request | contents: read, issues: write | Builder key, mapping, control deploy key | minds (auto; requester must be a configured reviewer) | no (issue text is data) |
| cto-autonomy | contents: write, issues: write, actions: write | Builder key, mapping, control deploy key | minds (auto, main only) | no |
| lab-patch | contents: write, actions: write | per-fork deploy key `LAB_DEPLOY_KEY_<SLUG>` (write, that fork only), control deploy key, optional `SC_LAB_PR_TOKEN` | lab-coding (auto, main only) | **no** (`git apply` of a gated diff; the build happens later in secret-free candidate-validation) |
| devnet-treasury | contents: write | `LAB_TREASURY_KEYPAIR` (devnet lab treasury), control deploy key | lab-treasury (auto, main only) | no |
| upstream-reconcile | contents: write | none | none | no |
| adoption-package | contents: write, actions: read | none | none | no |
| project-acceptance | contents: write, issues: write, actions: write | control deploy key (auto path only) | acceptance (auto path; main only, no reviewer) / none (comment path) | no |
| certificate-publication | contents: write, actions: write | none | none | no |
| campus-publication | contents: read, actions: write | none | none | no |
| build.yml (existing deploy) | contents: read, pages: write, id-token: write | CATALOG_TOKEN (optional, existing) | github-pages | no |

No workflow uses `pull_request_target`. Privileged jobs check out only this repository's default branch (and the
private control repo as data). Third-party actions are pinned to full SHAs (enforced by a unit test).

## Identities and acceptance
- **Auto-acceptance (owner policy, user instruction t690u, 2026-11-15 18:29 GMT).** No `/sc-accept` comment is
  required. `project-acceptance` (workflow_dispatch, environment `acceptance`, main only, no required reviewer) is
  started automatically after `adoption-package` or when `cto-autonomy` builds a package, and accepts only when ALL
  hold: candidate-validation passed on the exact candidate commit (newest genuine run = the package's run), the
  adoption package exists, its sha256 equals the recomputed canonical hash (and its evidence digest matches), and
  the candidate commit matches. The public acceptance record, the private log in the control repo and the
  certificate all say **"auto-accepted by owner policy (2026-11-15, user instruction)"** with `humanReviewed: false`:
  no human reviewed it. `certificate-publication` re-verifies the same conditions before issuing.
- Agent-authored work is never auto-accepted (no self-acceptance): a package whose contributor is a bot/agent identity
  (e.g. a Mind's lab patch pushed as `github-actions[bot]`) is refused. Added after the first chained run certified
  `gifter-escrow-036c6d5d6955-v1` to `github-actions[bot]`; that credential was revoked.
- The manual path below still works and is optional.
- Acceptance requires a new, unedited issue comment `/sc-accept …` by a configured reviewer: login **and** numeric
  account id **and** role `adoption-acceptance` **and** author association OWNER/MEMBER/COLLABORATOR. Bots and the
  configured agent identities are refused.
- Limitation: the Grok operator currently acts through the same GitHub account as the human owner (`Blockchains`).
  GitHub cannot distinguish them, so the rule "the agent never posts `/sc-accept`" is procedural. Fix: give the
  agent its own GitHub account or app and keep `Blockchains` as the only reviewer.

## Coding autonomy (owner instruction t687u, 2026-11-15 17:10 GMT)
A Mind writes code only as a unified diff inside a validated `experiment-patch` response. Code (never the Mind)
checks it (`pilot/src/lab/patch.ts`: at most 8 files / 400 changed lines / 60 KB; paths only under the project's
`programs/`, `tests/` and frontend `src/` dirs; refuses `.github/`, workflows, `.vscode`, Anchor.toml, package
manifests, lockfiles, toolchain files, build.rs, keypairs, `.env`, binaries, mode changes, renames, secret-shaped
lines and mainnet URLs), then `lab-patch` re-checks the stored diff's sha256, applies it to a fresh
`sc-lab/<project>/<task>` branch on the lab fork (never main, never overwrites an existing branch, never upstream),
runs gitleaks on the commit and refuses any `.github`/workflow path again, pushes with that fork's deploy key and
dispatches the secret-free `candidate-validation` on the exact SHA. Upstream changes are only ever pull requests.

## Devnet lab treasury (owner instructions t687u and t688u)
Address `En7DGt8B4LtuH2cwBMRofhdhgAJv18uGaDZDqCthS3QU`, funded with 10 devnet SOL from the deployer
(tx `5KpU25N7…zcLA4H`). **No spend caps**: no per-request cap, no per-project daily cap and no recipient allowlist
on devnet (t688u). Kept: devnet only (RPC host must be `api.devnet.solana.com` and the live genesis hash must be
devnet's, checked before signing; any other cluster is refused), the private key only as the GitHub secret
`LAB_TREASURY_KEYPAIR` in environment `lab-treasury` (never given to a Mind, never printed or recorded), and an
append-only ledger of every transaction (signature, amount, recipient, project, requesting Mind):
`records/public/treasury/ledger.jsonl` plus a private copy in the control repo. Requests come from Mind
`devnet-transfer` actions and are structurally checked (valid address, positive integer lamports, reason).

## What the CTO Mind is never given
Any private key (treasury included), mainnet keys, GitHub organisation admin, branch-protection bypass, arbitrary shell or SQL, other projects' credentials.
GitHub access for a Mind, if ever enabled, goes through a HelloMinds Connection (the equipped
"Animoca Minds Auth" app lists GitHub), restricted to the project's repos and read-only first; credentials are
entered in the Connections UI, never in conversation text.

## Recommended GitHub governance (not yet applied: changes protected settings, needs approval)
1. Ruleset on `main`: require a pull request with 1 approval and code-owner review; require status check `pilot-ci / ci`;
   block force pushes and deletions. Allow `github-actions[bot]` to push only to `records/public/**` (or move record
   writes to PRs).
2. Private control repo `Blockchains/sol-college-control` (created 2026-11-15): task records, provisioning state,
   autonomy state. Access: owner plus one **deploy key** with write access to that repository only (narrowest
   credential GitHub offers without a GitHub App), stored as `SC_CONTROL_DEPLOY_KEY` in environments `minds` and
   `minds-admin`. Fine-grained tokens cannot be created through the API.
