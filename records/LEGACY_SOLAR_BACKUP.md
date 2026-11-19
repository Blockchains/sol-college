# Legacy solar SPA backup

At pre-launch consolidation, the solar / energy-storage / local-AI SPA under
`legacy/` was removed from the public site build. A private tarball backup was
created outside the published tree. The `legacy/` directory is retained in the
repository for maintainer recovery but is no longer copied into `site/`.

Do not re-enable `shutil.copytree('legacy', OUT)` in `scripts/build.py`.
