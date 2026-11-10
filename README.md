# Sol.College

Learn to build on Solana from real code. This is the static site generator for https://sol.college.

- `scripts/fetch_data.py` reads `catalog.json` from [Blockchains/solana-superstack](https://github.com/Blockchains/solana-superstack). If that file isn't available, it falls back to the Solana repositories forked into the Blockchains account. It then shallow-clones each project.
- `scripts/build.py` detects stacks and categories and extracts lesson excerpts. Only permissively licensed code is quoted, with permalinks pinned to the fork's commit. It also writes the explorer, idea pages, guides, sitemap, robots and llms.txt.
- `legacy/` holds the original Sol.College solar AI edge-node pages, served at their original URLs. The original home page moved to `/edge-ai/`.
- GitHub Actions rebuilds and deploys nightly, on every push, and on a `catalog-updated` repository_dispatch.

## Live on devnet and lesson status (2026-11-10)

- `dapps/live.json` lists forks whose **own** app is hosted at `/dapps/<slug>/` against a program deployed on Solana devnet, with the devnet flow run end to end (`tests/devnet/<slug>.mjs`, logs in `tests/devnet/logs/`, positive and negative cases, signatures verified finalized). Frontends are built with `dapps/static_build.sh <slug> <clone>`.
- `scripts/live_devnet.py` runs after every build: it adds an honest status line to every lesson page (live / program only / client app / build output only / build failed / source only), writes `/lesson-audit.json`, the `/live/` page and the homepage "Live on devnet" section.
- Publishing of new source-only lessons is paused by default (`PUBLISH_PAUSED`, repo variable; set to `0` to resume).
