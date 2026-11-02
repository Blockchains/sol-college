# Sol.College

Learn to build on Solana from real code. This is the static site generator for https://sol.college.

- `scripts/fetch_data.py` reads `catalog.json` from [Blockchains/solana-superstack](https://github.com/Blockchains/solana-superstack). If that file isn't available, it falls back to the Solana repositories forked into the Blockchains account. It then shallow-clones each project.
- `scripts/build.py` detects stacks and categories and extracts lesson excerpts. Only permissively licensed code is quoted, with permalinks pinned to the fork's commit. It also writes the explorer, idea pages, guides, sitemap, robots and llms.txt.
- `legacy/` holds the original Sol.College solar AI edge-node pages, served at their original URLs. The original home page moved to `/edge-ai/`.
- GitHub Actions rebuilds and deploys nightly, on every push, and on a `catalog-updated` repository_dispatch.
