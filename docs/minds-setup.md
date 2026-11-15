# HelloMinds setup

SDK: `@animocabrands/minds-client-lib` 0.1.7 (exact, in `pilot/package-lock.json`; package license "UNLICENSED,
private alpha tooling"). API host fixed by the SDK (`https://api.build.hellominds.ai`). Methods and types used by the
adapter are checked against the installed package by `tests/integration/contract-and-live.test.ts`.

## Account state (2026-11-15, after the user's 15:35 GMT approval)
- 2 Minds on the Builder account:
  - "College" (pre-existing, `chiefofstaff`): not mapped to any project; only read, never messaged.
  - "SolCollege-Gifter-CTO" (`4073cf41…`, `chiefofstaff`, created 15:37 GMT by `minds provision`, idempotent: a rerun
    returned the same Mind and created nothing). Mapped to `gifter-escrow` in the protected secret `MINDS_PROJECT_MAP`
    (environments `minds` and `minds-admin`) as `project-cto`, plus a `test` entry pointing at the same Mind so the
    smoke test's harmless message goes only to it. Public config `mind.mappingStatus` = `approved`.
- Equipped: app "Animoca Minds Auth" (default); no Skills. Circle: steward only (unchanged).
- Instructions v1 (`config/minds/cto-instructions-v1.md`, sha256 `a593cb66ef37…`) delivered with `minds configure` in
  conversation `sc-gifter-escrow-instructions-a593cb66ef37`; the Mind acknowledged and restated scope, evidence rules
  and response format. The SDK has no instructions/persona endpoint, so a message is the only supported surface;
  acknowledgement does not guarantee compliance (every structured reply is validated by code).

## Second CTO Mind (2026-11-15 16:25 GMT)
- "SolCollege-Sentient-CTO" (`13a9d041…`, `chiefofstaff`) for `sentient-send` (DeFi, Sol.College-owned demonstration
  lab on Blockchains/sentient.send; no partnership with the upstream author). Same idempotent provisioning, mapping
  entry `sentient-send-cto`, instructions v1 (acknowledged), autonomy schedule. First research question: issue #3
  (questions over 32 bytes fail because the question is a PDA seed).

## Skills (built by the Minds themselves, 2026-11-15)
Requested in conversation `<prefix>-skills-v1` with four playbooks (Project Navigator, Research Planner, PR Triage,
Lab Reporter): private, no Bazaar. Each Mind built, registered unlisted (`isListed=false`) and equipped all four;
confirmed independently with `listEquippedSkills`, and a public Bazaar search for "Sol.College"/"SolCollege" returns
nothing.

| Mind | Skill | skillId |
| --- | --- | --- |
| SolCollege-Gifter-CTO | Sol.College Project Navigator | E5A8D041-F36B-1410-8467-00039CE7DF11 |
| SolCollege-Gifter-CTO | Sol.College Research Planner | E9A8D041-F36B-1410-8467-00039CE7DF11 |
| SolCollege-Gifter-CTO | Sol.College PR Triage | EBA8D041-F36B-1410-8467-00039CE7DF11 |
| SolCollege-Gifter-CTO | Sol.College Lab Reporter | EEA8D041-F36B-1410-8467-00039CE7DF11 |
| SolCollege-Sentient-CTO | SolCollege_ProjectNavigator | 2EAED041-F36B-1410-8467-00039CE7DF11 |
| SolCollege-Sentient-CTO | SolCollege_ResearchPlanner | 31AED041-F36B-1410-8467-00039CE7DF11 |
| SolCollege-Sentient-CTO | SolCollege_PRTriage | 38AED041-F36B-1410-8467-00039CE7DF11 |
| SolCollege-Sentient-CTO | SolCollege_LabReporter | 3BAED041-F36B-1410-8467-00039CE7DF11 |

The other six playbooks are not built yet. Publishing any Skill to Bazaar still needs separate approval.

## Still needing approval
1. **Circles**: none planned for the pilot. Public visitors are never added to a private CTO Circle.
