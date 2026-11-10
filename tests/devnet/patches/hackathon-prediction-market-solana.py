"""Static build prep for the hackathon-prediction-market-solana fork's own CRA app (prediction-market-frontend/).
Run from prediction-market-frontend/. The app has no router (tabs only) and already targets devnet, so the only
changes are: the base path comes from PUBLIC_URL at build time, and two small token-metadata JSON files are added
under public/meta/ for the YES/NO mints the sol.college test market points at (labelled as test data)."""
import json, pathlib
d = pathlib.Path('public/meta'); d.mkdir(parents=True, exist_ok=True)
for side in ('yes', 'no'):
    (d / f'{side}.json').write_text(json.dumps({'name': f'sol.college test {side.upper()}', 'symbol': f'SC{side.upper()}',
        'description': f'{side.upper()} outcome token of a devnet-only test market made by the sol.college scripts.'}, indent=2) + '\n')
print('patched')
