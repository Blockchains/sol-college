# Setup

## Local (operator machine)
```bash
cd pilot
npm ci
npm run typecheck
npm test                      # unit + recovery + integration (live tests skipped unless opted in)
npm run config:validate
npm run campus:build -- ../site-pilot
```
Live, opt-in (never commit the key; the SDK does not read .env):
```bash
set -a; . /path/outside/repo/minds.env; set +a      # provides MINDS_BUILDER_API_KEY
npx tsx src/minds/cli.ts inventory
npx tsx src/minds/cli.ts smoke-test --mind-name <ExactName>
SC_LIVE_MINDS=1 SC_LIVE_BAZAAR=1 SC_LIVE_GITHUB=1 GH_TOKEN=$(gh auth token) npm run test:integration
unset MINDS_BUILDER_API_KEY
```

## GitHub configuration
| Item | State on 2026-11-15 | How |
| --- | --- | --- |
| Environment `minds` (main only, no reviewer) | configured | Settings > Environments |
| Environment `minds-admin` (main only, required reviewer @Blockchains) | configured | Settings > Environments |
| Secret `MINDS_BUILDER_API_KEY` in both environments | configured (environment-scoped, not repo-wide) | `gh secret set MINDS_BUILDER_API_KEY --env minds` |
| Secret `MINDS_PROJECT_MAP` (protected project->Mind mapping, JSON like `config/minds/mind-mapping.example.json`) | MANUAL SETUP REQUIRED after a CTO Mind is approved | `gh secret set MINDS_PROJECT_MAP --env minds-admin < map.json` |
| Variable `SC_CONTROL_REPO` + secret `SC_CONTROL_TOKEN` (private control repo, fine-grained token: contents write on that repo only) | MANUAL SETUP REQUIRED (repo creation needs approval) | see docs/permissions.md |
| Secret `SC_CIRCLE_APPROVED_MEMBERS` (comma-separated emails approved for a project's Circle) | MANUAL SETUP REQUIRED when Circles are used | environment `minds-admin` |
| Branch protection / rulesets on `main` (require PR review, code owners, required check `pilot-ci`) | NOT CONFIGURED (main is unprotected today) | see docs/permissions.md |
| Rotate the Builder key (it was pasted into chat) | RECOMMENDED | build.hellominds.ai/console, then re-run the two `gh secret set` commands |
