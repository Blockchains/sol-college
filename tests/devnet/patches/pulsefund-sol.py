"""Static build prep for the pulsefund-sol fork's own Next.js app (frontend/). Run from frontend/.
Changes only what static hosting needs: basePath + unoptimized images for `next export`, and the unused
pages/api/hello.ts example route removed (a static site has no server). App code is unchanged."""
import pathlib, re
p = pathlib.Path('next.config.js'); s = p.read_text()
s = s.replace("reactStrictMode: true,", "reactStrictMode: true,\n  basePath: '/dapps/pulsefund-sol',\n  trailingSlash: true,", 1)
s = s.replace("images: {", "images: {\n    unoptimized: true,", 1)
p.write_text(s)
pathlib.Path('src/pages/api/hello.ts').unlink(missing_ok=True)
print('patched')
