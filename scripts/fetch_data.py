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
def colosseum():
  try:
    st=json.loads(subprocess.check_output(['gh','api','repos/Blockchains/colosseum-forker/contents/state.json','-H','Accept: application/vnd.github.raw'],stderr=subprocess.DEVNULL))
    return {v['fork'].split('/')[-1].lower() for v in st.values() if v.get('fork') and v.get('status') in ('created','exists')}
  except Exception: return None
def main():
  src,names,items=catalog(); fs=forks()
  # Colosseum forks: the forker's state.json when the token can read it; otherwise every Solana-looking fork.
  # The catalog only refreshes nightly, so it is a union, never the only source (it was, and froze lessons at 356 repos).
  col=colosseum()
  solana=lambda r:re.search(KW,json.dumps(r['parent']).lower()+r['name'].lower())
  sel=[r for r in fs if r.get('parent') and r.get('defaultBranchRef') and ((names and r['name'] in names) or (r['name'].lower() in col if col else solana(r)))]
  print('forks:',len(fs),'colosseum list:',len(col) if col else 'n/a (keyword fallback)','selected:',len(sel))
  projects=[]
  for r in sel:
    p=r['parent']; lic=(p['licenseInfo'] or {}).get('spdxId')
    projects.append(dict(name=r['name'],fork=r['url'],original=p['url'],original_name=p['nameWithOwner'],description=p['description'] or '',homepage=p['homepageUrl'] or '',
      stars=p['stargazerCount'],forks=p['forkCount'],pushed=p['pushedAt'],license=lic,permissive=lic in PERMISSIVE,
      language=(p['primaryLanguage'] or {}).get('name'),languages=[x['name'] for x in p['languages']['nodes']],
      topics=[x['topic']['name'] for x in p['repositoryTopics']['nodes']],branch=r['defaultBranchRef']['name'],commit=r['defaultBranchRef']['target']['oid']))
  os.makedirs('work',exist_ok=True)
  def clone(pr):
    d='work/'+pr['name']
    if os.path.exists(d):
      subprocess.run(['timeout','120','sh','-c',f'git -C {d} fetch -q --depth 1 origin {pr["branch"]} && git -C {d} reset -q --hard FETCH_HEAD'],stderr=subprocess.DEVNULL)
    if not os.path.exists(d):
      subprocess.run(['timeout','180','git','clone','-q','--depth','1','--filter=blob:limit=150k',pr['fork']+'.git',d],stderr=subprocess.DEVNULL)
    if os.path.exists(d):
      pr['commit']=subprocess.run(['git','-C',d,'rev-parse','HEAD'],capture_output=True,text=True).stdout.strip() or pr['commit']
  with cf.ThreadPoolExecutor(6) as ex: list(ex.map(clone,projects))
  json.dump(dict(source=src,generated=time.strftime('%Y-%m-%dT%H:%M:%SZ',time.gmtime()),projects=projects),open(OUT+'/projects.json','w'),indent=1)
  print(len(projects),'projects')
main()
