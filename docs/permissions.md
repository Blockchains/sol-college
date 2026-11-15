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
| upstream-reconcile | contents: write | none | none | no |
| adoption-package | contents: write, actions: read | none | none | no |
| project-acceptance | contents: write, issues: write, actions: write | none | none | no |
| certificate-publication | contents: write, actions: write | none | none | no |
| campus-publication | contents: read, actions: write | none | none | no |
| build.yml (existing deploy) | contents: read, pages: write, id-token: write | CATALOG_TOKEN (optional, existing) | github-pages | no |

No workflow uses `pull_request_target`. Privileged jobs check out only this repository's default branch (and the
private control repo as data). Third-party actions are pinned to full SHAs (enforced by a unit test).

## Identities and acceptance
- Acceptance requires a new, unedited issue comment `/sc-accept …` by a configured reviewer: login **and** numeric
  account id **and** role `adoption-acceptance` **and** author association OWNER/MEMBER/COLLABORATOR. Bots and the
  configured agent identities are refused.
- Limitation: the Grok operator currently acts through the same GitHub account as the human owner (`Blockchains`).
  GitHub cannot distinguish them, so the rule "the agent never posts `/sc-accept`" is procedural. Fix: give the
  agent its own GitHub account or app and keep `Blockchains` as the only reviewer.

## What the CTO Mind is never given
Mainnet keys, GitHub organisation admin, branch-protection bypass, arbitrary shell or SQL, other projects' credentials.
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
