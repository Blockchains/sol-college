"""Make the colosseum fork's ui/ build as a static site for sol.college.

Run from the fork's ui/ directory: python3 colosseum.py <program id> <admin authority>

What it changes, and only this:
- anchor-idl/idl.json and idl.ts: the program address becomes our devnet program id.
- components/Body.tsx and AdminBody.tsx: the staking vault is a PDA of a hard-coded admin
  (7ivun...); we set that constant to the wallet that initialised our vault.
- next.config.ts: static export with base path /dapps/colosseum (and /admin/ as admin/index.html).
"""
import sys, pathlib
pid, admin = sys.argv[1:3]
OLD_PID, OLD_ADMIN = 'Djo4ajv8rFv4i8Bt27BEtsUA5G3ToKBC5b2JKeF7i2nw', '7ivunejTCC3g6gWqYZqVRpthdyj29vPmVas5YcCy5Yh8'
for f in ['anchor-idl/idl.json', 'anchor-idl/idl.ts']:
    p = pathlib.Path(f); p.write_text(p.read_text().replace(OLD_PID, pid))
for f in ['components/Body.tsx', 'components/AdminBody.tsx']:
    p = pathlib.Path(f); p.write_text(p.read_text().replace(OLD_ADMIN, admin))
pathlib.Path('next.config.ts').write_text('''import type { NextConfig } from "next";

const nextConfig: NextConfig = {
  output: "export", basePath: "/dapps/colosseum", trailingSlash: true, images: { unoptimized: true },
  eslint: { ignoreDuringBuilds: true },
};

export default nextConfig;
''')
print('patched')
