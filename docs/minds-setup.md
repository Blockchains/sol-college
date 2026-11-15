# HelloMinds setup

SDK: `@animocabrands/minds-client-lib` 0.1.7 (exact, in `pilot/package-lock.json`; package license "UNLICENSED,
private alpha tooling"). API host fixed by the SDK (`https://api.build.hellominds.ai`). Methods and types used by the
adapter are checked against the installed package by `tests/integration/contract-and-live.test.ts`.

## Account inventory (read-only, 2026-11-15)
- 1 Mind on the Builder account: "College", archetype `chiefofstaff`, enabled; equipped app "Animoca Minds Auth"
  (verified, v1.1.11); no equipped Skills; Circle = steward only; no conversations.
- Supported creation type discovered from a real Mind: `chiefofstaff` (the SDK documents `id` as an open slug; `cto`
  is not assumed).
- "College" is not designated as a test Mind and is not mapped to any project. It was only read, never messaged.

## Waiting for approval (nothing below has been done)
1. **Test Mind** for the smoke test's message step. Either designate "College" as the test Mind, or create
   `SolCollege-Test-CTO` (`awakenMind({ name: "SolCollege-Test-CTO", id: "chiefofstaff" })`; name currently available).
   Creating a Mind may be billable.
2. **Project CTO Mind** for gifter-escrow, e.g. `SolCollege-Gifter-CTO` (archetype `chiefofstaff`), via
   `minds-admin` action `provision`. Then record its id in `MINDS_PROJECT_MAP` and change `mind.mappingStatus` to
   `approved` in `config/projects/gifter-escrow.json` through a reviewed commit.
3. **Instructions**: paste `config/minds/cto-instructions-v1.md` into the Mind (through its own supported surfaces).
4. **Skills**: the ten playbooks in `config/minds/skills/` are playbooks only. Building them is done by describing them
   to the Mind (Registry Offering, App Manifest, Tool Schemas, Skill Playbook); publishing to Bazaar is public and
   must not include private project information. Equip by approved `skillId` via `minds-admin` action `equip`.
5. **Connections**: GitHub through "Animoca Minds Auth" only if needed, restricted repos, read-only first, keys
   entered in My Connections (never in chat).
6. **Circles**: none planned for the pilot. Public visitors are never added to a private CTO Circle.
