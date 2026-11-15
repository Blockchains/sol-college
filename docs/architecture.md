# Sol.College pilot architecture (GitHub-native asynchronous mode)

## What exists (inspected 2026-11-15)
- Static site generator in Python (`scripts/*.py`) deployed to GitHub Pages by `.github/workflows/build.yml`
  (hourly, on push, on dispatch). Custom domain sol.college. No server-side runtime, no backend, no database.
- `dapps/app` (esbuild bundle) and `dapps/static/*` hosted devnet frontends; `tests/` fork verification.
- Hosted services referenced by existing code: none required by the site build. `verify-forks.yml` uses an
  embedded (local, npm) Postgres for some fork flows; that is local tooling on the runner, not a hosted service,
  and the pilot does not use it. Supabase appears only as a publishable key inside the archived legacy bundle.
- No pre-existing Minds integration, no Node/TypeScript workspace for coordination, no secrets except Pages.

## Selected mode: B, GitHub-native asynchronous
GitHub Pages cannot hold secrets or run a backend, and Grok chat is not an always-on server, so:

| Concern | Where it runs |
| --- | --- |
| Public campus (`/campus/`) | Static files built by `build.yml` from the allowlisted projection (`pilot/src/campus`). No API calls from browsers. |
| Minds calls (Builder key) | Only in GitHub Actions jobs bound to environments `minds` (read-only, main only) or `minds-admin` (required reviewer). |
| Candidate validation (untrusted code) | `candidate-validation.yml`, no secrets, read-only token, hosted ephemeral runner, trusted fixture from this repo. |
| Engineering records | GitHub issues (research questions, experiments, coordination requests), lab PRs, Actions runs. |
| Public records | `records/public/` (adoption manifests, acceptances, credential registry, upstream state). Immutable files. |
| Private records | Proposed private control repo (`vars.SC_CONTROL_REPO`); not created (needs approval). Workflows that would store Minds output fail closed until it exists. |
| Persistent CTO identity and reasoning | HelloMinds Minds owned by the Sol.College Builder account. |

Latency: requests are asynchronous (minutes, plus human approval for privileged runs). Nothing on the site is a live conversation.

## Code layout
- `pilot/` Node 22, TypeScript strict, npm lockfile. `src/minds` (typed SDK adapter, authority, provisioning,
  equipment, Circles, task correlation, smoke test, CLI), `src/validation` (GitHub evidence + verdict),
  `src/upstream`, `src/adoption`, `src/acceptance`, `src/certification`, `src/attendance`, `src/campus`,
  `src/coordination`. Tests in `pilot/tests/{unit,recovery,integration}`.
- `config/` schema, policy, live project configs, examples (placeholders excluded), Minds instructions and Skill playbooks.
- `campus/` static 2D page + optional three.js scene (bundled at build).

## Flow (success criterion)
research question issue -> experiment issue + isolated lab branch/PR (baseline recorded) -> candidate commit ->
`candidate-validation` (exact SHA, Solana runtime fixture) -> `adoption-package` (evidence from GitHub API,
canonical bytes, sha256) -> reviewer posts `/sc-accept package=… sha256=… candidate=…` -> `project-acceptance`
(re-verifies everything, records once) -> `certificate-publication` (fails closed without verified acceptance)
-> `campus-publication` -> `build.yml` deploys.
