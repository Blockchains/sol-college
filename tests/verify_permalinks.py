"""Check every quoted excerpt against the fork at its pinned commit: the file must exist on GitHub and the cited lines must match the quote exactly.
Usage: python3 tests/verify_permalinks.py [site/excerpts.json]  -> writes tests/results/permalinks.json"""
import json,sys,urllib.request,collections
ex=json.load(open(sys.argv[1] if len(sys.argv)>1 else 'site/excerpts.json')); cache={}; out=[]
for x in ex:
  raw=x['fork'].replace('https://github.com/','https://raw.githubusercontent.com/')+f"/{x['commit']}/{x['file']}"
  if raw not in cache:
    try: cache[raw]=urllib.request.urlopen(raw,timeout=30).read().decode('utf-8','replace').split('\n')
    except Exception as e: cache[raw]=str(e)
  src=cache[raw]
  if isinstance(src,str): ok,why=False,'fetch failed: '+src
  else:
    got=[l.rstrip('\r') for l in src[x['start']-1:x['end']]]; ok=got==x['code'].split('\n'); why='' if ok else 'lines differ'
  out.append(dict(project=x['project'],lesson=x.get('lesson'),url=x['url'],ok=ok,why=why))
bad=[o for o in out if not o['ok']]
json.dump(dict(checked=len(out),ok=len(out)-len(bad),failures=bad),open('tests/results/permalinks.json','w'),indent=1)
print(f"{len(out)-len(bad)}/{len(out)} excerpts match their permalink"); [print('FAIL',b['url'],b['why']) for b in bad]
sys.exit(1 if bad else 0)
