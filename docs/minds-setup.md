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

Publishing any Skill to Bazaar still needs separate approval (superseded below: all ten now built).


## Five more CTO Minds (2026-11-15 17:13 GMT, owner instruction t687u)
Same idempotent `minds provision` (archetype `chiefofstaff`), mapping entries `<slug>-cto` in `MINDS_PROJECT_MAP`
(environments `minds` and `minds-admin`), instructions v1 (sha256 `a593cb66ef37…`) delivered and acknowledged by
each, research authorisation and first research question from a documented bug in the Sol.College devnet record.
All are Sol.College-owned demonstration labs on our forks; no upstream author has joined Sol.College.

| Mind | Project | Sector | First research question |
| --- | --- | --- | --- |
| SolCollege-CipherVault-CTO | ciphervault (yashwankhade5/CipherVault) | DeFi | [#6](https://github.com/Blockchains/sol-college/issues/6) |
| SolCollege-Colosseum-CTO | colosseum (NovenGrid/Colosseum) | DeFi | [#7](https://github.com/Blockchains/sol-college/issues/7) |
| SolCollege-PoE-CTO | poe-solana (ProofOfEstimate/poe-solana) | DeFi | [#8](https://github.com/Blockchains/sol-college/issues/8) |
| SolCollege-TrustLock-CTO | trustlock (Solana-TrustLock/TrustLock) | DeFi | [#9](https://github.com/Blockchains/sol-college/issues/9) |
| SolCollege-OrbOracle-CTO | orboracle-solana (StabilityNexus/OrbOracle-Solana) | DeFi | [#10](https://github.com/Blockchains/sol-college/issues/10) |

Sector: none of the fully working devnet apps is genuinely DePIN or DeAI (they are a multisig, staking, a
forecasting poll, a time-locked escrow and a price oracle), so all are in DeFi. picassol-hackathon (no upstream),
gree (NFT mint) and c4-comets (display names) fit none of the three rooms and were not given a Mind.

## All ten playbooks built by every Mind (skills-v2, 2026-11-15 17:13-17:20 GMT)
Requested in conversation `<prefix>-skills-v2` (the six remaining playbooks for the first two Minds, all ten for the
new five). Confirmed with `listEquippedSkills`: **70 Skills, 10 per Mind**, all private; public Bazaar search for
"SolCollege", "Sol.College" and "Sol College" returns 0. Equipped apps: "Animoca Minds Auth" only. Circles: steward
only on every Mind (unchanged).

| Mind | Skill | skillId |
| --- | --- | --- |
| SolCollege-Gifter-CTO | Sol.College Adoption Editor | 9D13D141-F36B-1410-8467-00039CE7DF11 |
| SolCollege-Gifter-CTO | Sol.College Contributor Guide | 9313D141-F36B-1410-8467-00039CE7DF11 |
| SolCollege-Gifter-CTO | Sol.College Credential Explainer | A013D141-F36B-1410-8467-00039CE7DF11 |
| SolCollege-Gifter-CTO | Sol.College Lab Reporter | EEA8D041-F36B-1410-8467-00039CE7DF11 |
| SolCollege-Gifter-CTO | Sol.College PR Triage | EBA8D041-F36B-1410-8467-00039CE7DF11 |
| SolCollege-Gifter-CTO | Sol.College Project Navigator | E5A8D041-F36B-1410-8467-00039CE7DF11 |
| SolCollege-Gifter-CTO | Sol.College Public Campus Representative | A713D141-F36B-1410-8467-00039CE7DF11 |
| SolCollege-Gifter-CTO | Sol.College Research Planner | E9A8D041-F36B-1410-8467-00039CE7DF11 |
| SolCollege-Gifter-CTO | Sol.College Upstream Analyst | 9813D141-F36B-1410-8467-00039CE7DF11 |
| SolCollege-Gifter-CTO | Sol.College Validation Coordinator | 9A13D141-F36B-1410-8467-00039CE7DF11 |
| SolCollege-Sentient-CTO | SolCollege_AdoptionEditor | C413D141-F36B-1410-8467-00039CE7DF11 |
| SolCollege-Sentient-CTO | SolCollege_ContributorGuide | B713D141-F36B-1410-8467-00039CE7DF11 |
| SolCollege-Sentient-CTO | SolCollege_CredentialExplainer | C813D141-F36B-1410-8467-00039CE7DF11 |
| SolCollege-Sentient-CTO | SolCollege_LabReporter | 3BAED041-F36B-1410-8467-00039CE7DF11 |
| SolCollege-Sentient-CTO | SolCollege_ProjectNavigator | 2EAED041-F36B-1410-8467-00039CE7DF11 |
| SolCollege-Sentient-CTO | SolCollege_PRTriage | 38AED041-F36B-1410-8467-00039CE7DF11 |
| SolCollege-Sentient-CTO | SolCollege_PublicCampusRepresentative | CD13D141-F36B-1410-8467-00039CE7DF11 |
| SolCollege-Sentient-CTO | SolCollege_ResearchPlanner | 31AED041-F36B-1410-8467-00039CE7DF11 |
| SolCollege-Sentient-CTO | SolCollege_UpstreamAnalyst | BD13D141-F36B-1410-8467-00039CE7DF11 |
| SolCollege-Sentient-CTO | SolCollege_ValidationCoordinator | C313D141-F36B-1410-8467-00039CE7DF11 |
| SolCollege-CipherVault-CTO | SolCollegeAdoptionEditorBody | 7718D141-F36B-1410-8467-00039CE7DF11 |
| SolCollege-CipherVault-CTO | SolCollegeContributorGuideBody | 7018D141-F36B-1410-8467-00039CE7DF11 |
| SolCollege-CipherVault-CTO | SolCollegeCredentialExplainerBody | 7E18D141-F36B-1410-8467-00039CE7DF11 |
| SolCollege-CipherVault-CTO | SolCollegeLabReporterBody | 6918D141-F36B-1410-8467-00039CE7DF11 |
| SolCollege-CipherVault-CTO | SolCollegeProjectNavigatorBody | 4718D141-F36B-1410-8467-00039CE7DF11 |
| SolCollege-CipherVault-CTO | SolCollegePRTriageBody | 6218D141-F36B-1410-8467-00039CE7DF11 |
| SolCollege-CipherVault-CTO | SolCollegePublicCampusRepresentativeBody | 8118D141-F36B-1410-8467-00039CE7DF11 |
| SolCollege-CipherVault-CTO | SolCollegeResearchPlannerBody | 6018D141-F36B-1410-8467-00039CE7DF11 |
| SolCollege-CipherVault-CTO | SolCollegeUpstreamAnalystBody | 7518D141-F36B-1410-8467-00039CE7DF11 |
| SolCollege-CipherVault-CTO | SolCollegeValidationCoordinatorBody | 7618D141-F36B-1410-8467-00039CE7DF11 |
| SolCollege-Colosseum-CTO | Sol.College CTO Adoption Editor | 4319D141-F36B-1410-8467-00039CE7DF11 |
| SolCollege-Colosseum-CTO | Sol.College CTO Contributor Guide | 3519D141-F36B-1410-8467-00039CE7DF11 |
| SolCollege-Colosseum-CTO | Sol.College CTO Credential Explainer | 4819D141-F36B-1410-8467-00039CE7DF11 |
| SolCollege-Colosseum-CTO | Sol.College CTO Lab Reporter | 3219D141-F36B-1410-8467-00039CE7DF11 |
| SolCollege-Colosseum-CTO | Sol.College CTO PR Triage | 3119D141-F36B-1410-8467-00039CE7DF11 |
| SolCollege-Colosseum-CTO | Sol.College CTO Project Navigator | 2819D141-F36B-1410-8467-00039CE7DF11 |
| SolCollege-Colosseum-CTO | Sol.College CTO Public Campus Representative | 4C19D141-F36B-1410-8467-00039CE7DF11 |
| SolCollege-Colosseum-CTO | Sol.College CTO Research Planner | 2F19D141-F36B-1410-8467-00039CE7DF11 |
| SolCollege-Colosseum-CTO | Sol.College CTO Upstream Analyst | 3719D141-F36B-1410-8467-00039CE7DF11 |
| SolCollege-Colosseum-CTO | Sol.College CTO Validation Coordinator | 3C19D141-F36B-1410-8467-00039CE7DF11 |
| SolCollege-PoE-CTO | SolCollege_Adoption_Editor | 3E16D141-F36B-1410-8467-00039CE7DF11 |
| SolCollege-PoE-CTO | SolCollege_Contributor_Guide | 2916D141-F36B-1410-8467-00039CE7DF11 |
| SolCollege-PoE-CTO | SolCollege_Credential_Explainer | 4216D141-F36B-1410-8467-00039CE7DF11 |
| SolCollege-PoE-CTO | SolCollege_Lab_Reporter | 2216D141-F36B-1410-8467-00039CE7DF11 |
| SolCollege-PoE-CTO | SolCollege_PR_Triage | 1F16D141-F36B-1410-8467-00039CE7DF11 |
| SolCollege-PoE-CTO | SolCollege_Project_Navigator | 1316D141-F36B-1410-8467-00039CE7DF11 |
| SolCollege-PoE-CTO | SolCollege_Public_Campus_Representative | 4916D141-F36B-1410-8467-00039CE7DF11 |
| SolCollege-PoE-CTO | SolCollege_Research_Planner | 1A16D141-F36B-1410-8467-00039CE7DF11 |
| SolCollege-PoE-CTO | SolCollege_Upstream_Analyst | 3016D141-F36B-1410-8467-00039CE7DF11 |
| SolCollege-PoE-CTO | SolCollege_Validation_Coordinator | 3716D141-F36B-1410-8467-00039CE7DF11 |
| SolCollege-TrustLock-CTO | SolCollege Adoption Editor | 1B18D141-F36B-1410-8467-00039CE7DF11 |
| SolCollege-TrustLock-CTO | SolCollege Contributor Guide | 1718D141-F36B-1410-8467-00039CE7DF11 |
| SolCollege-TrustLock-CTO | SolCollege Credential Explainer | 2118D141-F36B-1410-8467-00039CE7DF11 |
| SolCollege-TrustLock-CTO | SolCollege Lab Reporter | 1418D141-F36B-1410-8467-00039CE7DF11 |
| SolCollege-TrustLock-CTO | SolCollege PR Triage | 0D18D141-F36B-1410-8467-00039CE7DF11 |
| SolCollege-TrustLock-CTO | SolCollege Project Navigator | 1017D141-F36B-1410-8467-00039CE7DF11 |
| SolCollege-TrustLock-CTO | SolCollege Public Campus Representative | 2218D141-F36B-1410-8467-00039CE7DF11 |
| SolCollege-TrustLock-CTO | SolCollege Research Planner | 0918D141-F36B-1410-8467-00039CE7DF11 |
| SolCollege-TrustLock-CTO | SolCollege Upstream Analyst | 1818D141-F36B-1410-8467-00039CE7DF11 |
| SolCollege-TrustLock-CTO | SolCollege Validation Coordinator | 1A18D141-F36B-1410-8467-00039CE7DF11 |
| SolCollege-OrbOracle-CTO | SolCollegeAdoptionEditor | 3514D141-F36B-1410-8467-00039CE7DF11 |
| SolCollege-OrbOracle-CTO | SolCollegeContributorGuide | 2C14D141-F36B-1410-8467-00039CE7DF11 |
| SolCollege-OrbOracle-CTO | SolCollegeCredentialExplainer | 3814D141-F36B-1410-8467-00039CE7DF11 |
| SolCollege-OrbOracle-CTO | SolCollegeLabReporter | 2A14D141-F36B-1410-8467-00039CE7DF11 |
| SolCollege-OrbOracle-CTO | SolCollegeProjectNavigator | 2114D141-F36B-1410-8467-00039CE7DF11 |
| SolCollege-OrbOracle-CTO | SolCollegePRTriage | 2514D141-F36B-1410-8467-00039CE7DF11 |
| SolCollege-OrbOracle-CTO | SolCollegePublicCampusRepresentative | 3D14D141-F36B-1410-8467-00039CE7DF11 |
| SolCollege-OrbOracle-CTO | SolCollegeResearchPlanner | 2214D141-F36B-1410-8467-00039CE7DF11 |
| SolCollege-OrbOracle-CTO | SolCollegeUpstreamAnalyst | 2F14D141-F36B-1410-8467-00039CE7DF11 |
| SolCollege-OrbOracle-CTO | SolCollegeValidationCoordinator | 3214D141-F36B-1410-8467-00039CE7DF11 |

## Still needing approval
1. **Circles**: none planned for the pilot. Public visitors are never added to a private CTO Circle.
