"""Fetch the SuperStack catalog (or fall back to Solana forks in the Blockchains account) and shallow-clone permissively licensed repos."""
import json,os,re,subprocess,time,concurrent.futures as cf,urllib.request
OUT='data'; os.makedirs(OUT,exist_ok=True)
PERMISSIVE={'MIT','Apache-2.0','BSD-2-Clause','BSD-3-Clause','ISC','CC0-1.0','Unlicense','0BSD','MIT-0'}
KW=r'solana|anchor|pinocchio|colosseum|metaplex|blinks?\b|spl[- ]token|token-2022|helius|jupiter|phantom'
def gh(args):
  for i in range(6):
    try: return subprocess.check_output(['gh']+args,stderr=subprocess.DEVNULL)
    except subprocess.CalledProcessError: time.sleep(4*(i+1))
  raise SystemExit('gh failed: '+' '.join(args[:2]))
def catalog():
  try:
    raw=gh(['api','repos/Blockchains/solana-superstack/contents/catalog.json','-H','Accept: application/vnd.github.raw'])
    c=json.loads(raw); items=c if isinstance(c,list) else c.get('projects') or c.get('repos') or []
    names=set()
    for it in items:
      n=it if isinstance(it,str) else (it.get('fork') or it.get('name') or it.get('repo') or '')
      names.add(n.split('/')[-1])
    print('catalog.json entries:',len(names)); return 'superstack',names,items
  except SystemExit: print('catalog.json not available; using Blockchains Solana forks'); return 'forks',None,[]
Q='''query($c:String){user(login:"Blockchains"){repositories(first:40,after:$c,isFork:true){pageInfo{hasNextPage endCursor} nodes{name url pushedAt defaultBranchRef{name target{oid}}
 parent{nameWithOwner url stargazerCount forkCount pushedAt description homepageUrl licenseInfo{spdxId} primaryLanguage{name} languages(first:6,orderBy:{field:SIZE,direction:DESC}){nodes{name}} repositoryTopics(first:12){nodes{topic{name}}}}}}}}'''
def forks():
  out=[];c=None
  while True:
    d=json.loads(gh(['api','graphql','-f','query='+Q]+(['-f','c='+c] if c else [])))['data']['user']['repositories']
    out+=d['nodes']
    if not d['pageInfo']['hasNextPage']: return out
    c=d['pageInfo']['endCursor']
QL='''query($c:String){user(login:"Blockchains"){repositories(first:100,after:$c,isFork:true){pageInfo{hasNextPage endCursor} nodes{name url pushedAt defaultBranchRef{name target{oid}}}}}}'''
PF='''parent{nameWithOwner url stargazerCount forkCount pushedAt description homepageUrl licenseInfo{spdxId} primaryLanguage{name} languages(first:6,orderBy:{field:SIZE,direction:DESC}){nodes{name}} repositoryTopics(first:12){nodes{topic{name}}}}'''
def forks_light():
  # Fast listing (no parent metadata): the full query pages 40 forks at a time and took ~8 min for ~3800 forks.
  out=[];c=None
  while True:
    d=json.loads(gh(['api','graphql','-f','query='+QL]+(['-f','c='+c] if c else [])))['data']['user']['repositories']
    out+=d['nodes']
    if not d['pageInfo']['hasNextPage']: return out
    c=d['pageInfo']['endCursor']
def parents(rs):
  for i in range(0,len(rs),25):
    q='query{'+' '.join(f'r{j}: repository(owner:"Blockchains",name:{json.dumps(r["name"])}){{name url defaultBranchRef{{name target{{oid}}}} {PF}}}' for j,r in enumerate(rs[i:i+25]))+'}'
    try: d=json.loads(subprocess.check_output(['gh','api','graphql','-f','query='+q],stderr=subprocess.DEVNULL))['data']
    except subprocess.CalledProcessError as e: d=(json.loads(e.output or b'{}').get('data') or {})  # NOT_FOUND names return partial data
    for j,r in enumerate(rs[i:i+25]):
      x=d.get(f'r{j}') or {}; r.update(name=x.get('name',r['name']),url=x.get('url'),defaultBranchRef=x.get('defaultBranchRef'),parent=x.get('parent'))
def colosseum():
  try:
    st=json.loads(subprocess.check_output(['gh','api','repos/Blockchains/colosseum-forker/contents/state.json','-H','Accept: application/vnd.github.raw'],stderr=subprocess.DEVNULL))
    return {v['fork'].split('/')[-1].lower() for v in st.values() if v.get('fork') and v.get('status') in ('created','exists')}
  except Exception: return None
def slug(n): return re.sub(r'[^a-z0-9-]+','-',n.lower())
def incremental(src,col,prev):
  pub={x['path'] for x in json.load(open(prev+'/published.json')) if x.get('type')!='updated'}
  st=json.load(open(prev+'/build-state.json')) if os.path.exists(prev+'/build-state.json') else {}
  exc={x.lower() for x in st.get('excluded',[])}
  # No fork listing (paging ~3800 forks took 3-8 min): candidates come straight from the colosseum/catalog names.
  cand=sorted(n for n in col if f"/explore/{slug(n)}/" not in pub and n not in exc)
  sel=[dict(name=n) for n in cand[:int(os.environ.get('CLONE_N','60'))]]; parents(sel)
  missing=[r['name'] for r in sel if not (r.get('parent') and r.get('defaultBranchRef'))]
  sel=[r for r in sel if r['name'] not in missing]
  json.dump(dict(candidates=len(cand),missing=missing),open(OUT+'/incr.json','w'))
  print('incremental: candidates',len(cand),'cloning',len(sel),'missing',len(missing))
  finish(src,sel)
def main():
  src,names,items=catalog(); prev=os.environ.get('INCREMENTAL_PREV')
  if prev:
    col=(colosseum() or set())|{n.lower() for n in (names or [])}
    if col: return incremental(src,col,prev)
  fs=forks()
  # Colosseum forks: the forker's state.json when the token can read it; otherwise every Solana-looking fork.
  # The catalog only refreshes nightly, so it is a union, never the only source (it was, and froze lessons at 356 repos).
  col=colosseum()
  solana=lambda r:re.search(KW,json.dumps(r['parent']).lower()+r['name'].lower())
  sel=[r for r in fs if r.get('parent') and r.get('defaultBranchRef') and ((names and r['name'] in names) or (r['name'].lower() in col if col else solana(r)))]
  print('forks:',len(fs),'colosseum list:',len(col) if col else 'n/a (keyword fallback)','selected:',len(sel))
  finish(src,sel)
def finish(src,sel):
  projects=[]
  for r in sel:
    p=r['parent']; lic=(p['licenseInfo'] or {}).get('spdxId')
    projects.append(dict(name=r['name'],fork=r['url'],original=p['url'],original_name=p['nameWithOwner'],description=p['description'] or '',homepage=p['homepageUrl'] or '',
      stars=p['stargazerCount'],forks=p['forkCount'],pushed=p['pushedAt'],license=lic,permissive=lic in PERMISSIVE,
      language=(p['primaryLanguage'] or {}).get('name'),languages=[x['name'] for x in p['languages']['nodes']],
      topics=[x['topic']['name'] for x in p['repositoryTopics']['nodes']],branch=r['defaultBranchRef']['name'],commit=r['defaultBranchRef']['target']['oid']))
  os.makedirs('work',exist_ok=True)
  def clone(pr):
    # Disk-lean clones: the CI runner ran out of disk with full checkouts of ~1300 forks (+20 GB cache).
    # Keep only the source tree plus a .commit marker; drop .git and dirs build.py never reads.
    d='work/'+pr['name']; mk=d+'/.commit'
    have=open(mk).read().strip() if os.path.exists(mk) else (subprocess.run(['git','-C',d,'rev-parse','HEAD'],capture_output=True,text=True).stdout.strip() if os.path.exists(d+'/.git') else '')
    if not (have and have==pr['commit']):
      subprocess.run(['rm','-rf',d])
      subprocess.run(['timeout','180','git','clone','-q','--depth','1','--filter=blob:limit=150k',pr['fork']+'.git',d],stderr=subprocess.DEVNULL)
      if not os.path.exists(d): return
      have=subprocess.run(['git','-C',d,'rev-parse','HEAD'],capture_output=True,text=True).stdout.strip() or pr['commit']
    pr['commit']=have
    open(mk,'w').write(have)
    subprocess.run(['sh','-c',f'rm -rf {d}/.git; find {d} -type d \\( -name node_modules -o -name target -o -name .next -o -name coverage -o -name vendor \\) -prune -exec rm -rf {{}} + 2>/dev/null'])
  with cf.ThreadPoolExecutor(16) as ex: list(ex.map(clone,projects))
  json.dump(dict(source=src,generated=time.strftime('%Y-%m-%dT%H:%M:%SZ',time.gmtime()),projects=projects),open(OUT+'/projects.json','w'),indent=1)
  print(len(projects),'projects')
main()
