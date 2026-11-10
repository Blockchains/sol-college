"""Make the votara fork's client/votara-client build as a static site for sol.college.

Run from client/votara-client/ (the program id is replaced in src/constants/constant.tsx and
src/idl/votara.json by dapps/static_build.sh before this runs).

What it changes, and only this:
- src/main.tsx: BrowserRouter -> HashRouter, so /dashboard, /proposals, /create, /treasury, /profile
  and /admin work on a static host (as #/dashboard and so on).
The base path comes from vite --base; the RPC defaults to devnet in the fork's own constants.
"""
import pathlib
p = pathlib.Path('src/main.tsx'); s = p.read_text()
s = s.replace('import { BrowserRouter }', 'import { HashRouter }').replace('<BrowserRouter>', '<HashRouter>').replace('</BrowserRouter>', '</HashRouter>')
p.write_text(s); print('patched')

# Bug fix in the fork: TokenBalance (shown on #/profile once you are a voter) reads the connection from the
# fork's own src/connection.tsx context, but that provider is never mounted (wallet.tsx mounts the wallet
# adapter's ConnectionProvider instead), so the whole app crashed with "useConnection must be inside
# <ConnectionProvider>". Point it at the wallet adapter's connection, which is the one that is mounted.
p = pathlib.Path('src/components/TokenBalance.tsx'); s = p.read_text()
s = s.replace('import { useConnection } from "../connection";', 'import { useConnection } from "@solana/wallet-adapter-react";')
s = s.replace('const connection = useConnection();', 'const { connection } = useConnection();')
p.write_text(s); print('patched TokenBalance')
