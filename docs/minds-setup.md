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

## Skills
The API exposes only Bazaar search and equip/unequip by `skillId`; it has no endpoint to create a Skill. Private
Skills are built by describing them to the Mind. That was not done in this run because the CTO Mind stopped replying
after the instructions message (see docs/verification.md). Third-party Bazaar Skills were not equipped: they are
unvetted instructions from other authors and none matches the playbooks. To build: send each playbook in
`config/minds/skills/` to the CTO Mind in its own conversation, tell it to keep the Skill private, then equip the
returned `skillId` with `minds equip gifter-escrow --skills <id>`. Publishing to Bazaar still needs separate approval.

## Still needing approval
1. **Circles**: none planned for the pilot. Public visitors are never added to a private CTO Circle.
