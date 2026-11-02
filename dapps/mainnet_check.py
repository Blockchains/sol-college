"""Read-only: for each lesson fork, find declare_id!/Anchor.toml program IDs at the pinned commit and ask a free public mainnet RPC whether an executable program exists there. Sends no transactions."""
import json,re,glob,urllib.request,os
RPC='https://api.mainnet-beta.solana.com'; out={}
def info(pk):
  q=json.dumps(dict(jsonrpc='2.0',id=1,method='getAccountInfo',params=[pk,{'encoding':'base64','dataSlice':{'offset':0,'length':0}}])).encode()
  r=json.loads(urllib.request.urlopen(urllib.request.Request(RPC,q,{'content-type':'application/json'}),timeout=20).read())
  v=r.get('result',{}).get('value'); return bool(v and v.get('executable'))
import sys
for d in ['work/'+n for n in sys.argv[1:]]:
  ids=set()
  for f in glob.glob(d+'/**/*.rs',recursive=True)+glob.glob(d+'/**/Anchor.toml',recursive=True):
    if '/node_modules/' in f or '/target/' in f: continue
    t=open(f,errors='replace').read()
    ids|=set(re.findall(r'declare_id!\(\s*"([1-9A-HJ-NP-Za-km-z]{32,44})"',t))
    if f.endswith('Anchor.toml'):
      m=re.search(r'\[programs\.mainnet\]([^\[]*)',t)
      if m: ids|=set(re.findall(r'"([1-9A-HJ-NP-Za-km-z]{32,44})"',m.group(1)))
  if ids:
    out[os.path.basename(d)]={}
    for i in sorted(ids):
      try: out[os.path.basename(d)][i]=info(i)
      except Exception as e: out[os.path.basename(d)][i]='error:'+type(e).__name__
json.dump(out,open('dapps/mainnet_programs.json','w'),indent=1)
for k,v in out.items(): print(k,v)
