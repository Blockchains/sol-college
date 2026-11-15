# Verification evidence (2026-11-15, times GMT)

Repo commit at time of writing: see `git log` (f53d142 and later). Runs are in https://github.com/Blockchains/sol-college/actions.

| Check | Result | Command / run | Notes |
| --- | --- | --- | --- |
| TypeScript strict typecheck | PASS | `cd pilot && npm run typecheck` | Node 22 in CI, strict + exactOptionalPropertyTypes |
| Unit + recovery + contract tests | PASS (42 pass, 0 fail, 5 live skipped) | `npm test`, CI `pilot-ci` | |
| Live GitHub evidence tests | PASS (3/3) | `SC_LIVE_GITHUB=1 npm run test:integration` | good fb2bbfd passes; negative control e288388 blocked; baseline a9c3a41 has genuine evidence |
| Live Bazaar + Minds read-only tests | PASS (2/2) | `SC_LIVE_BAZAAR=1 SC_LIVE_MINDS=1 …` | key from box-only file, never printed |
| Config validation | PASS | `npm run config:validate` | 1 live project, 0 placeholders |
| Candidate validation, exact PR head 5628bfc | PASS | run 43730277119 | Anchor 0.30.1 build + Solana runtime fixture on solana-test-validator; untrusted job has no secrets |
| Candidate validation, negative control e288388 | FAIL as intended | run 43730202863 | fixture: makerGainB 4.999999 ≠ 5, run blocked |
| Candidate validation, upstream baseline a9c3a41 | PASS (limitation) | run 43729455493 | fixture does not reproduce the toolchain-dependent devnet crash |
| Adoption package | PASS | run 43731781862, commit 91ede63 | `gifter-escrow-5628bfc9439f-v1`, sha256 70ae6f6d…f4da, deciding run 43730277119 |
| Project acceptance | NOT EXECUTED (needs the human reviewer) | `/sc-accept …` comment by @Blockchains | the agent must not post it |
| Certificate | NOT EXECUTED | follows acceptance automatically | fails closed without verified acceptance |
| Minds smoke test, read-only, on Actions (College) | PASS | run 43729497471 (env `minds`) | message steps NOT EXECUTED (not a test Mind) |
| CTO Mind provisioning | PASS | `minds provision gifter-escrow --name SolCollege-Gifter-CTO --archetype chiefofstaff` | idempotent rerun created nothing; approval: user instruction 15:35 GMT |
| Protected mapping | PASS | `MINDS_PROJECT_MAP` in envs `minds`, `minds-admin`; `minds project/capabilities/telemetry gifter-escrow` | |
| Minds smoke test with message (local operator) | PASS (8/8) | `minds smoke-test --mind-name SolCollege-Gifter-CTO --allow-message …` | reply received in ~60 s |
| Minds smoke test with message, on Actions | PASS (8/8; reply step = timeout handled) | run 43731784210 (env `minds-admin`, approved under the user's instruction) | Mind did not reply within 180 s; recorded uncertain, no resend |
| CTO instructions v1 delivered | PASS | `minds configure gifter-escrow …` | acknowledged (1644 chars) |
| Structured task (PR triage of 5628bfc) | PASS (completed after operator re-evaluation) | `minds task gifter-escrow --spec …`, then `reconcileTask` | interim note at ~11 min, final sc-task-response/1 at ~15 min: 9 sourced facts, 3 hypotheses, 3 proposals, 4 uncertainties. First validated as operator-review (a fact cited an evidence id); policy updated so facts may cite any id listed in the task; same stored reply re-evaluated, never resent. The Mind found a real fixture gap: refund closure is not asserted |
| Private Skills built/equipped | NOT EXECUTED | — | no create-Skill API; Mind-built Skills postponed (Mind slow to reply); third-party Skills not equipped |
| Landing hero: 3D campus first, lazy three.js | PASS | live https://sol.college/ (Playwright, desktop 1440×900) | 3D after load; FCP ≈1.2 s, campus3d.js (139 KB) requested after first paint |
| Landing: keyboard (focus scene, arrows, Enter) opens overlay | PASS | Playwright | |
| Landing: clicking a 3D avatar opens overlay | PASS | Playwright pixel-located click | |
| Landing: mobile (390×844, touch) | PASS: 2D rooms, three.js not requested | Playwright | |
| Landing: prefers-reduced-motion | PASS: 2D rooms, three.js not requested | Playwright | |
| /, /campus/, /campus/data.json, /live/, /lessons/ | PASS (HTTP 200) | curl | dapps/live.json is a build input (repo), consumed by the landing/live builds; it is not served as a URL (unchanged) |
| gitleaks before each push | PASS | `minds-private/push.sh` (fails closed) | one earlier false positive (synthetic test JWT) fixed and allow-listed |
| Branch protection / CODEOWNERS enforcement | MANUAL SETUP REQUIRED | — | see permissions.md |
| Private control repo | MANUAL SETUP REQUIRED (needs approval) | — | coordination workflow fails closed |
