import json,os,re,html,shutil,collections,glob,datetime
from content import LESSONS,NOTES,CATEGORIES,GUIDES
import hubs
GUIDES=GUIDES+[hubs.BUILD_DAPP]
SITE='https://sol.college'; OUT='site'; E=html.escape
data=json.load(open('data/projects.json')); P=data['projects']
shutil.rmtree(OUT,ignore_errors=True)
if os.path.isdir('legacy'): shutil.copytree('legacy',OUT)
else: os.makedirs(OUT)
SKIP=re.compile(r'(^|/)(node_modules|\.git|dist|build|target|vendor|\.next|coverage|fixtures?)(/|$)|\.min\.js$|\.d\.ts$')
def files(name,exts):
  root='work/'+name
  for dp,dn,fn in os.walk(root):
    rel=os.path.relpath(dp,root)
    if SKIP.search(rel+'/'): dn[:]=[];continue
    for f in fn:
      if f.endswith(exts):
        p=os.path.join(dp,f)
        try:
          if os.path.getsize(p)<150000: yield os.path.relpath(p,root),p
        except OSError: pass
def read(p):
  try: return open(p,encoding='utf-8').read()
  except Exception: return ''
# ---------- detection
def detect(pr):
  root='work/'+pr['name']; fw=set(); cargo=pkg=''
  for rel,p in files(pr['name'],('Cargo.toml','package.json','Anchor.toml','requirements.txt','pyproject.toml','go.mod')):
    t=read(p)
    if rel.endswith('Anchor.toml'): fw.add('Anchor')
    if rel.endswith('Cargo.toml'):
      if 'anchor-lang' in t: fw.add('Anchor')
      if re.search(r'^\s*pinocchio',t,re.M): fw.add('Pinocchio')
      if re.search(r'^\s*steel\s*=',t,re.M): fw.add('Steel')
      if re.search(r'^\s*solana-program\s*=',t,re.M): fw.add('Native Rust')
    if rel.endswith('package.json'):
      if '"@solana/kit"' in t: fw.add('@solana/kit')
      if '"@solana/web3.js"' in t: fw.add('web3.js')
      if '@metaplex-foundation' in t: fw.add('Metaplex')
      if '"@solana/actions"' in t: fw.add('Solana Actions')
      if '"@solana/pay"' in t: fw.add('Solana Pay')
      if 'solana-agent-kit' in t: fw.add('Solana Agent Kit')
      if '"next"' in t: fw.add('Next.js')
    if rel.endswith(('requirements.txt','pyproject.toml')) and re.search(r'\bsolana\b|solders',t): fw.add('solana-py')
    if rel.endswith('go.mod') and 'solana' in t: fw.add('solana-go')
  if 'Anchor' in fw: fw.discard('Native Rust')
  pr['frameworks']=sorted(fw); pr['cloned']=os.path.isdir(root)
  text=(pr['name']+' '+pr['description']+' '+' '.join(pr['topics'])).lower()
  pr['categories']=[c for c,rx in CATEGORIES if re.search(rx,text)][:2] or ['Other']
  pr['slug']=re.sub(r'[^a-z0-9-]+','-',pr['name'].lower())
for pr in P: detect(pr)
# ---------- excerpts
BAD=re.compile(r'polkadot|substrate|ink/|bench|fixture|config\.|vite|webpack|\.config|/bin/|paritygen|sema/|emit/|codegen|generated|idl\.|types\.rs$|_types\.rs$',re.I)
def excerpt_for(L):
  best=[]
  for pr in [p for p in P if p['permissive'] and p['cloned']]:
    top=None
    for rel,path in files(pr['name'],L['ext']):
      if BAD.search(rel): continue
      if re.search(r'(^|/)(tests?|__tests__)/|\.test\.|\.spec\.',rel) and L['slug']!='escrow': continue
      if L.get('pathpat') and not re.search(L['pathpat'],rel,re.I): continue
      lines=read(path).split('\n')
      for i,l in enumerate(lines):
        if len(l)<200 and re.search(L['pat'],l):
          s=max(0,i-4); e=min(len(lines),s+26)
          while e>i+1 and not lines[e-1].strip(): e-=1
          block=lines[s:e]
          if any(len(x)>180 for x in block): continue
          notes=[]
          for j,x in enumerate(block):
            for rx,msg in NOTES:
              if re.search(rx,x) and not any(n[1]==msg for n in notes): notes.append((s+j+1,msg,x.strip()[:90]))
          hits=sum(1 for x in block if re.search(L['pat'],x))
          sc=hits*2+len(notes)+(2 if re.search(r'program|src/(instructions|lib)',rel) else 0)
          if not top or sc>top[0]: top=(sc,dict(project=pr,file=rel,start=s+1,end=e,code='\n'.join(block),notes=notes[:7],url=f"{pr['fork']}/blob/{pr['commit']}/{rel}#L{s+1}-L{e}"))
    if top and (top[0]>=4 and top[1]['notes'] or top[0]>=5): best.append(top)
  best.sort(key=lambda t:(-t[0],-t[1]['project']['stars']))
  return [t[1] for t in best[:6]]
SRC_EXT=('.rs','.ts','.tsx','.js','.jsx','.py','.go','.sol','.move','.c','.cpp')
def manifest_cmds(pr):
  root='work/'+pr['name']; cmds=[]
  for rel,p in files(pr['name'],('package.json',)):
    if rel.count('/')>2: continue
    try: sc=json.load(open(p)).get('scripts',{})
    except Exception: continue
    d=os.path.dirname(rel) or '.'
    for k in ('dev','start','build','test','lint','deploy'):
      if k in sc: cmds.append((d,f"npm run {k}",sc[k][:120]))
  for rel,p in files(pr['name'],('Anchor.toml',)):
    d=os.path.dirname(rel) or '.'; cmds+= [(d,'anchor build','compile programs and generate IDLs'),(d,'anchor test','local validator + test suite')]
    m=re.search(r'\[scripts\]([^\[]*)',read(p))
    if m:
      for k,v in re.findall(r'^\s*([\w-]+)\s*=\s*"([^"]*)"',m.group(1),re.M): cmds.append((d,f'anchor run {k}',v[:120]))
  for rel,p in files(pr['name'],('Cargo.toml',)):
    if rel=='Cargo.toml': cmds+=[('.','cargo build','Rust workspace build'),('.','cargo test','Rust tests')]
  for rel,p in files(pr['name'],('go.mod',)):
    if rel=='go.mod': cmds+=[('.','go build ./...',''),('.','go test ./...','')]
  if os.path.exists(root+'/Makefile'):
    for t in re.findall(r'^([a-zA-Z][\w-]*):',read(root+'/Makefile'),re.M)[:8]: cmds.append(('.',f'make {t}','Makefile target'))
  seen=set(); return [c for c in cmds if not (c[:2] in seen or seen.add(c[:2]))][:16]
def readme_summary(pr):
  for n in ('README.md','readme.md','README.MD','Readme.md'):
    t=read(f"work/{pr['name']}/{n}")
    if t:
      t=re.sub(r'```.*?```|<[^>]+>|!\[[^\]]*\]\([^)]*\)','',t,flags=re.S)
      for para in re.split(r'\n\s*\n',t):
        x=' '.join(l.strip() for l in para.split('\n') if not l.strip().startswith(('#','|','[!','-','*','>','=')))
        x=re.sub(r'\[([^\]]+)\]\([^)]*\)',r'\1',x).strip()
        if len(x)>80: return x[:600]
  return ''
def arch(pr):
  root='work/'+pr['name']; top=collections.Counter(); ext=collections.Counter(); n=0
  for rel,p in files(pr['name'],SRC_EXT):
    n+=1; ext[os.path.splitext(rel)[1]]+=1; top[rel.split('/')[0] if '/' in rel else '(root)']+=1
  progs=sorted({os.path.dirname(os.path.dirname(r)) for r,_ in files(pr['name'],('lib.rs',)) if r.endswith('src/lib.rs') and 'programs/' in r})[:8]
  return n,top.most_common(8),ext.most_common(6),progs
def key_excerpts(pr,k=4):
  c=[]
  for rel,path in files(pr['name'],SRC_EXT):
    if BAD.search(rel) or re.search(r'\.test\.|\.spec\.|(^|/)tests?/',rel): continue
    lines=read(path).split('\n')
    for s in range(0,max(1,len(lines)-10),12):
      block=lines[s:s+24]
      while block and not block[-1].strip(): block.pop()
      if len(block)<6 or any(len(x)>180 for x in block): continue
      notes=[]
      for j,x in enumerate(block):
        for rx,msg in NOTES:
          if re.search(rx,x) and not any(q[1]==msg for q in notes): notes.append((s+j+1,msg,x.strip()[:90]))
      if len(notes)>=2: c.append((len(notes),rel,s,block,notes))
  c.sort(key=lambda t:-t[0]); out=[];usedf=set()
  for sc,rel,s,block,notes in c:
    if rel in usedf: continue
    usedf.add(rel); out.append(dict(project=pr,file=rel,start=s+1,end=s+len(block),code='\n'.join(block),notes=notes[:7],url=f"{pr['fork']}/blob/{pr['commit']}/{rel}#L{s+1}-L{s+len(block)}"))
    if len(out)>=k: break
  return out
SOLAPI=re.compile(r'\b(Connection|PublicKey|Keypair|Transaction|VersionedTransaction|TransactionMessage|SystemProgram|sendAndConfirmTransaction|sendTransaction|signTransaction|getLatestBlockhash|requestAirdrop|getBalance|getAccountInfo|getProgramAccounts|findProgramAddressSync|AnchorProvider|Program|useWallet|useConnection|WalletMultiButton|getAssociatedTokenAddress\w*|createMint|mintTo|createTransferInstruction|transfer|createUmi|mplTokenMetadata|ComputeBudgetProgram|invoke_signed|invoke|CpiContext|Pubkey|AccountInfo|msg!|require!|emit!|init_if_needed|has_one|seeds)\b')
def sol_files(pr,k=12):
  out=[]
  for rel,path in files(pr['name'],SRC_EXT):
    if BAD.search(rel): continue
    t=read(path)
    if not re.search(r'@solana/|@coral-xyz/anchor|@project-serum/anchor|anchor_lang|solana_program|@metaplex-foundation|pinocchio',t): continue
    c=collections.Counter(SOLAPI.findall(t))
    if c: out.append((sum(c.values()),rel,[a for a,_ in c.most_common(6)]))
  out.sort(key=lambda x:-x[0]); return out[:k]
EXCL=collections.Counter(); KEEP=[]
import tested
for pr in P:
  n=arch(pr)[0] if pr['cloned'] else 0
  pr['kx']=key_excerpts(pr) if (pr['permissive'] and n>=5) else []
  # Non-permissive or excerpt-less repos with real Solana code still get a structure lesson (no code quoted).
  pr['sf']=sol_files(pr) if (n>=5 and not pr['kx']) else []
  sol=n>=5 and (pr['kx'] or tested.how_it_works(pr,'work/'+pr['name']) or len(pr['sf'])>=2)
  if sol: KEEP.append(pr)
  else: EXCL['too little code' if n<5 else 'no Solana code found']+=1
import tested
UNP=tested.unpublished(); REMOVED=[(p,UNP[p['name']]) for p in KEEP if p['name'] in UNP]
KEEP=[p for p in KEEP if p['name'] not in UNP]
# Publish the backlog in batches: pages already in published.json stay; at most PUBLISH_BATCH new ones per build.
import urllib.request
PUB=os.environ.get('PUBLISHED_FROM','https://sol.college')+'/published.json'
try: prev=json.loads(urllib.request.urlopen(PUB,timeout=20).read())
except Exception: prev=None
if prev is None and os.path.exists('site_published.json'): prev=json.load(open('site_published.json'))
KNOWN={x['path'] for x in (prev or []) if x.get('type')!='updated'}
BATCH=int(os.environ.get('PUBLISH_BATCH','1'))
def dapp_verified(p):
  f=f"dapps/deployed/{p['slug']}.json"
  try: d=json.load(open(f)); return bool(d.get('devnet') and d.get('sigs'))
  except Exception: return False
# New lessons go live only once their own dapp is verified on devnet with a real transaction (dapps/deployed/<slug>.json has sigs).
new=[p for p in KEEP if f"/explore/{p['slug']}/" not in KNOWN]
PENDING_DAPP=[p for p in new if not dapp_verified(p)]
new=[p for p in new if dapp_verified(p)]
new.sort(key=lambda p:(-len(p['kx']),-len(p['sf']),-p['stars'],p['name']))
WAIT=(new[BATCH:] if prev is not None else [])+PENDING_DAPP
KEEP=[p for p in KEEP if p not in WAIT]
print('lessons kept:',len(KEEP),'awaiting dapp:',len(PENDING_DAPP),'waiting:',len(WAIT),'excluded:',dict(EXCL))
TOTAL=len(P); P=KEEP
LES=[]
for L in LESSONS:
  ex=excerpt_for(L)
  if ex: LES.append((L,ex))
# ---------- layout
CSS=open('scripts/style.css').read()
NAV=[('/learn-solana/','Learn Solana'),('/topics/','Topics'),('/explore/','Explore'),('/new/','New'),('/learn-by-example/','Learn by example'),('/what-to-build/','What to build'),('/how-to-build/','How to build')]
def fit(s,n):
  s=' '.join(s.split())
  if len(s)<=n: return s
  for sep in ((' | ',': ',' (',' — ') if n<=60 else ()):
    if sep in s and len(s.split(sep)[0])>=20 and len(s.rsplit(sep,1)[0])<=n: return s.rsplit(sep,1)[0].strip()
  return s[:n-1].rsplit(' ',1)[0].rstrip(',;:.-')+'…'
OGS=[('/learn-solana/','path'),('/learn-by-example/','learn'),('/explore/','explore'),('/how-to-build/','build'),('/what-to-build/','ideas'),('/topics/','topics'),('/glossary/','glossary'),('/faq/','faq')]
LASTMOD={}
def page(path,title,desc,body,ld=None,crumbs=None,og=None,noindex=False,lastmod=None):
  title=fit(title,60); desc=fit(desc,158); og=next((f'/og/{v}.png' for k,v in OGS if path.startswith(k)),'/og.png')
  if lastmod: LASTMOD[path]=lastmod
  url=SITE+path; lds=[dict({"@context":"https://schema.org"},**x) for x in (ld or [])]
  if crumbs: lds.append({"@context":"https://schema.org","@type":"BreadcrumbList","itemListElement":[{"@type":"ListItem","position":i+1,"name":n,"item":SITE+u} for i,(u,n) in enumerate(crumbs)]})
  nav=''.join(f'<a href="{u}"{" aria-current=page" if path.startswith(u) else ""}>{n}</a>' for u,n in NAV)
  bc=('<nav class=crumbs aria-label=Breadcrumb>'+' / '.join(f'<a href="{u}">{E(n)}</a>' for u,n in crumbs[:-1])+f' / <span>{E(crumbs[-1][1])}</span></nav>') if crumbs else ''
  h=f'''<!doctype html><html lang=en><head><meta charset=utf-8><meta name=viewport content="width=device-width,initial-scale=1">
<title>{E(title)}</title><meta name=description content="{E(desc)}"><link rel=canonical href="{url}">
{'<meta name=robots content="noindex">' if noindex else ''}<meta property=og:type content={'article' if path.startswith(('/learn-by-example/','/how-to-build/','/explore/')) and path.count('/')>2 else 'website'}><meta property=og:title content="{E(title)}"><meta property=og:description content="{E(desc)}"><meta property=og:url content="{url}"><meta property=og:site_name content="Sol.College"><meta property=og:locale content=en_GB><meta property=og:image content="{SITE}{og}"><meta property=og:image:width content=1200><meta property=og:image:height content=630><meta property=og:image:alt content="Sol.College: {E(title)}">
<meta name=twitter:card content=summary_large_image><meta name=twitter:title content="{E(title)}"><meta name=twitter:description content="{E(desc)}"><meta name=twitter:image content="{SITE}{og}">
<meta name=theme-color content="#0b0a14"><link rel=icon href="/favicon.ico" sizes=48x48><link rel=icon href="/favicon.svg" type="image/svg+xml"><link rel=icon type=image/png sizes=32x32 href="/favicon-32x32.png"><link rel=icon type=image/png sizes=16x16 href="/favicon-16x16.png"><link rel=apple-touch-icon sizes=180x180 href="/apple-touch-icon.png"><link rel=manifest href="/site.webmanifest"><link rel=alternate type=application/atom+xml href="/feed.xml" title="New on Sol.College"><link rel=alternate type=text/plain href="/llms.txt" title="llms.txt">
<style>{CSS}</style>{''.join(f'<script type="application/ld+json">{json.dumps(x)}</script>' for x in lds)}</head><body>
<a class=skip href="#main">Skip to content</a><header class=top><a class=brand href="/"><span class=logo aria-hidden=true></span>Sol.College</a><nav aria-label=Main>{nav}</nav></header>
<main id=main>{bc}{body}</main><footer><p>Sol.College: learn Solana from real code in the <a href="https://github.com/Blockchains/solana-superstack">SuperStack</a>. Code excerpts are quoted under their original permissive licences, with attribution and permalinks. Facts link to <a href="https://solana.com/docs">Solana</a> and <a href="https://www.anchor-lang.com/docs">Anchor</a> docs.</p>
<p><a href="/learn-solana/">Learn Solana</a> · <a href="/topics/">Topics</a> · <a href="/glossary/">Glossary</a> · <a href="/faq/">FAQ</a> · <a href="/explore/">Explore</a> · <a href="/learn-by-example/">Lessons</a> · <a href="/what-to-build/">Ideas</a> · <a href="/how-to-build/">Guides</a> · <a href="/edge-ai/">Solar AI edge nodes</a> · <a href="/legal/terms/">Terms</a> · <a href="/legal/privacy/">Privacy</a> · <a href="/feed.xml">Feed</a> · Data refreshed {data['generated'][:10]}</p></footer></body></html>'''
  d=OUT+path; os.makedirs(d,exist_ok=True); open(d+'index.html','w').write(h)
  if not noindex: SM.append(path)
SM=[]
def chips(xs,cls='chip'): return ''.join(f'<span class={cls}>{E(x)}</span>' for x in xs)
def card(pr):
  return f'''<article class=card><h3><a href="/explore/{pr['slug']}/">{E(pr['name'])}</a></h3><p>{E(pr['description'][:160])}</p><p class=meta>{ {'lesson':'📘 lesson','guide':'🧭 guide','listing':'listing'}.get(pr.get('level'),'')} · ★ {pr['stars']:,} · {E(pr['language'] or '—')} · {E(pr['license'] or 'no licence')}</p><div>{chips(pr['categories'])}{chips(pr['frameworks'][:4],'chip fw')}</div></article>'''
def code(ex):
  pr=ex['project']; lang='rust' if ex['file'].endswith('.rs') else 'ts'
  rows=''.join(f'<span class=ln data-n="{ex["start"]+i}">{E(l) or " "}</span>' for i,l in enumerate(ex['code'].split('\n')))
  notes=''.join(f'<li><b>Line {n}</b> <code>{E(x)}</code>: {E(m[0].upper()+m[1:])}</li>' for n,m,x in ex['notes'])
  return f'''<figure class=excerpt><figcaption><a href="/explore/{pr['slug']}/">{E(pr['original_name'])}</a> · <a href="{ex['url']}"><code>{E(ex['file'])}</code> L{ex['start']}–{ex['end']} @ {pr['commit'][:7]}</a> · {E(pr['license'])} · <a href="{pr['original']}">original</a></figcaption><pre class={lang}><code>{rows}</code></pre>{f'<ol class=notes>{notes}</ol>' if notes else ''}</figure>'''
# ---------- home
cats=collections.defaultdict(list)
for pr in P:
  for c in pr['categories']: cats[c].append(pr)
fwc=collections.Counter(f for p in P for f in p['frameworks'])
langc=collections.Counter(p['language'] or 'Other' for p in P)
nperm=sum(p['permissive'] for p in P)
src_note='the <a href="https://github.com/Blockchains/solana-superstack">Solana SuperStack catalog</a>' if data['source']=='superstack' else 'the Solana repositories forked into the <a href="https://github.com/Blockchains?tab=repositories&type=fork">Blockchains</a> GitHub account (the SuperStack catalog is being assembled and will replace this list automatically)'
top=sorted(P,key=lambda p:-p['stars'])[:6]
# ---------- explore
lessons_by_proj=collections.defaultdict(list)
for L,ex in LES:
  for x in ex: lessons_by_proj[x['project']['name']].append(L)
json.dump([dict(project=x['project']['name'],fork=x['project']['fork'],commit=x['project']['commit'],file=x['file'],start=x['start'],end=x['end'],url=x['url'],code=x['code']) for pr in P for x in pr['kx']]+[dict(project=x['project']['name'],fork=x['project']['fork'],commit=x['project']['commit'],file=x['file'],start=x['start'],end=x['end'],url=x['url'],code=x['code'],lesson=L['slug']) for L,ex in LES for x in ex],open(OUT+'/excerpts.json','w'))
DAPPS={}
STATIC_NOTE={'solstage-web':'The fork\'s own Vite/React frontend, with its built-in cluster switch (devnet / mainnet). It reads wallets and NFTs; it has no on-chain program of its own.',
 'stealthfolio':'The fork\'s own Next.js frontend (static export). Private transfers go through Light Protocol, whose relayer is a separate service the fork does not host.',
 'elyse':'The fork\'s own webpack frontend (wallet dashboard). It reads balances from public RPCs; it has no on-chain program of its own.'}
def static_dapp(sl):
  src=f'dapps/static/{sl}'
  if not os.path.isdir(src): return ''
  shutil.copytree(src,f'{OUT}/dapps/{sl}',dirs_exist_ok=True)
  return f'''<section class=note><h2>Open the dapp</h2><p><a class=btn href="/dapps/{sl}/">Open the dapp</a> {E(STATIC_NOTE.get(sl,"The fork's own frontend, built unchanged except for its base path."))} Connect your own wallet; every transaction is signed in your wallet. Use devnet with free SOL from <a href="https://faucet.solana.com">faucet.solana.com</a>. <b>Mainnet uses real tokens: alpha software, high risk.</b></p><p>Built with <code>dapps/static_build.sh {sl}</code>.</p></section>'''
MW=json.load(open('dapps/mainnet-wallets.json')) if os.path.exists('dapps/mainnet-wallets.json') else {'dapps':[]}
MWD={d['slug']:d for d in MW['dapps']}
if MW['dapps']:
  os.makedirs(f'{OUT}/dapps',exist_ok=True); shutil.copy('dapps/mainnet-wallets.json',f'{OUT}/dapps/mainnet-wallets.json')
MAINNET_JS='''<script>(function(){const RPCS=['https://api.mainnet-beta.solana.com','https://solana-rpc.publicnode.com'];
document.querySelectorAll('.golive:not([data-done])').forEach(async el=>{el.dataset.done=1;const a=el.dataset.addr,need=+el.dataset.need,st0=el.dataset.status;
const q=s=>el.querySelector(s);q('.cp').onclick=()=>navigator.clipboard.writeText(a).then(()=>{q('.cp').textContent='Copied'});
try{let b=null;for(const u of RPCS){try{const r=await fetch(u,{method:'POST',headers:{'content-type':'application/json'},body:JSON.stringify({jsonrpc:'2.0',id:1,method:'getBalance',params:[a]})});b=(await r.json()).result.value/1e9;break}catch(e){}}if(b===null)throw 0;const p=Math.min(100,b/need*100);q('progress').value=p;q('.amt').textContent=b.toFixed(3)+' / '+need+' SOL ('+p.toFixed(0)+'%)';
let st=st0;if(st==='Devnet only'&&b>0)st=b>=need?'Funded, deploying soon':'Funding';q('.st').textContent=st}catch(e){q('.amt').textContent='Could not read the mainnet balance right now.'}});})();</script>'''
def mainnet_panel(sl):
  d=MWD.get(sl)
  if not d: return ''
  qr=open(f'dapps/qr/{sl}.svg').read(); qr=qr[qr.index('<svg'):].replace('<svg ','<svg style="width:168px;height:168px;display:block" ',1)
  live=f'<p><b>Live on mainnet:</b> program <a href="https://explorer.solana.com/address/{E(d["mainnet_program"])}"><code>{E(d["mainnet_program"])}</code></a></p>' if d.get('mainnet_program') else ''
  extra=f' After deploy, it needs about {d["extra_to_use_sol"]} SOL more to actually be used.' if d.get('extra_to_use_sol') else ''
  return f'''<section class="note golive" data-addr="{E(d['address'])}" data-need="{d['sol_needed']}" data-status="{E(d['status'])}"><h2>Go live on mainnet</h2>{live}
<p>This dapp runs on <b>devnet</b> until its own mainnet wallet is funded. Send <b>{d['sol_needed']} SOL</b> (estimate incl. ~10% margin) to the address below and it deploys to mainnet automatically.{extra} Leftover SOL after deploy is refunded only to the owner wallet.</p>
<div style="display:flex;gap:18px;flex-wrap:wrap;align-items:center"><div style="background:#fff;padding:6px;border-radius:6px" role=img aria-label="QR code of the funding address">{qr}</div>
<div style="flex:1;min-width:240px"><p>Funding address:<br><code class=addr style="word-break:break-all;font-size:15px">{E(d['address'])}</code> <button class="btn cp" type=button>Copy</button></p>
<p>Funding progress: <progress max=100 value=0 style="width:100%"></progress><br><span class=amt>reading mainnet balance...</span></p><p>Status: <b class=st>{E(d['status'])}</b></p></div></div>
<div class=warn><b>Alpha, high-risk, unaudited software.</b> Funding pays only for deploying this program; it buys nothing and no return of any kind is promised. Mainnet uses real funds and you can lose what you send. Alternative: fund every dapp at once via <code>{E(MW['shared_wallet']['address'])}</code> ({MW['shared_wallet']['sol_needed_all']} SOL for all; <a href="/dapps/mainnet-wallets.json">registry</a>).</div>{MAINNET_JS}</section>'''
def dapp(pr):
  sl=re.sub(r'[^a-z0-9-]+','-',pr['name'].lower()); f=f'dapps/deployed/{sl}.json'
  if os.path.isdir(f'dapps/static/{sl}'): return static_dapp(sl)
  if not (os.path.exists(f) and os.path.exists('dapps/app/dist/app.js')): return ''
  d=json.load(open(f)); idls=sorted(glob.glob(f'dapps/build/{sl}/*.json'))
  idls=[x for x in idls if not x.endswith('-keypair.json') and (not d.get('idl') or x.endswith(d['idl']))]
  if not d.get('devnet') or not idls: return ''
  o=f'{OUT}/dapps/{sl}/'; os.makedirs(o,exist_ok=True)
  open(o+'index.html','w').write(open('dapps/app/index.html').read().replace('</body>','<div style="max-width:900px;margin:24px auto;padding:0 16px">'+mainnet_panel(sl)+'</div></body>')); shutil.copy('dapps/app/dist/app.js',o); shutil.copy(idls[0],o+'idl.json')
  json.dump(dict(name=pr['name'],fork=pr['fork'],commit=pr['commit'],lesson=f"/explore/{pr['slug']}/",programs=dict(devnet=d['devnet'],mainnet=d.get('mainnet'))),open(o+'config.json','w'))
  DAPPS[pr['name']]=d
  mn=f"Mainnet: upstream program <code>{E(d['mainnet'])}</code> (alpha, high risk, real funds)" if d.get('mainnet') else 'Mainnet: not yet deployed on mainnet (needs owner approval), so it is disabled'
  sig=''.join(f'<li><code>{E(x["label"])}</code> <a href="https://explorer.solana.com/tx/{E(x["sig"])}?cluster=devnet">{E(x["sig"][:20])}…</a></li>' for x in d.get('sigs',[])[:8])
  return f'''<section class=note><h2>Open the dapp</h2>{f'<p><b>✅ Operational on devnet, verified {E(d.get("verified",""))}</b></p>' if d.get('sigs') else '<p>Deployed on devnet; the full in-browser flow is not yet proven end to end.</p>'}<p><a class=btn href="/dapps/{sl}/">Open the dapp</a> Connect Phantom or Solflare. Every transaction is signed in your own wallet.</p><ul><li>Devnet (test tokens): program <a href="https://explorer.solana.com/address/{E(d['devnet'])}?cluster=devnet"><code>{E(d['devnet'])}</code></a>. Get free devnet SOL at <a href="https://faucet.solana.com">faucet.solana.com</a>.</li><li>{mn}</li></ul>{f'<p>Devnet proof, verified {E(d.get("verified",""))}: real transactions sent through this program on devnet.</p><ul class=sigs>{sig}</ul>' if sig else ''}</section>'''
TOPICS=['escrow','vault','oracle','swap','stake','staking','nft','mint','pda','cpi','token-2022','auction','dao','governance','prediction','payment','solana pay','blink','airdrop','lottery','amm','lending','bridge','dispute','game','agent','metadata','compressed','merkle','multisig','subscription','marketplace','reward','vesting','faucet']
def kw(p):
  t=set()
  for L in lessons_by_proj.get(p['name'],[]): t.update([L['slug'],L['title'].lower()])
  blob=' '.join(x['code'].lower()+' '+x['file'].lower() for x in p['kx'])+' '+(p['description'] or '').lower()
  src=''.join(read(q)[:20000].lower() for _,q in list(files(p['name'],('.rs','.ts','.tsx','.js')))[:200]) if p['cloned'] else ''
  t.update(w for w in TOPICS if w in blob or w in src)
  return ' '.join(sorted(t))
json.dump([dict(k=kw(p),n=p['name'],s=p['slug'],d=p['description'][:200],st=p['stars'],l=p['language'] or 'Other',c=p['categories'],f=p['frameworks'],u=p['pushed'][:10],lic=p['license'] or 'none',fk=p['fork'],o=p['original']) for p in P],open(OUT+'/projects.json','w'))
opt=lambda xs:''.join(f'<option>{E(x)}</option>' for x in xs)
page('/explore/','Explore the Solana SuperStack: projects by category and framework',f'Search and filter {len(P)} Solana projects by category, framework (Anchor, native, Pinocchio), language, stars and activity, with links to forks and originals.',
f'''<h1>Explore the SuperStack</h1><p class=lead>{len(P)} projects from {src_note}. Filter by category, framework, language, licence and activity.</p>
<form class=filters role=search onsubmit="return false"><label>Search<input id=q type=search placeholder="escrow, oracle, agent…"></label><label>Category<select id=fc><option value="">All</option>{opt(sorted(cats))}</select></label><label>Framework<select id=ff><option value="">All</option>{opt(sorted(fwc))}</select></label><label>Language<select id=fl><option value="">All</option>{opt(sorted(langc))}</select></label><label>Sort<select id=so><option value=st>Stars</option><option value=u>Recently active</option><option value=n>Name</option></select></label><label class=chk><input id=fp type=checkbox> Permissive licence only</label></form>
<p id=count aria-live=polite></p><div id=res class=grid>{''.join(card(p) for p in sorted(P,key=lambda p:-p['stars']))}</div>
<script>
const P=[],$=id=>document.getElementById(id),esc=s=>String(s).replace(/[&<>"]/g,c=>({{'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;'}}[c]));
const PERM=/^(MIT|Apache-2.0|BSD-2-Clause|BSD-3-Clause|ISC|CC0-1.0|Unlicense|0BSD|MIT-0)$/;
fetch('/projects.json').then(r=>r.json()).then(d=>{{P.push(...d);const u=new URLSearchParams(location.search);for(const[k,id]of[['q','q'],['category','fc'],['framework','ff'],['language','fl'],['sort','so']])if(u.get(k))$(id).value=u.get(k);draw()}});
function draw(){{const q=$('q').value.toLowerCase(),c=$('fc').value,f=$('ff').value,l=$('fl').value,s=$('so').value,pm=$('fp').checked;
let r=P.filter(p=>(!q||(p.n+' '+p.d+' '+p.f.join(' ')+' '+(p.k||'')).toLowerCase().includes(q))&&(!c||p.c.includes(c))&&(!f||p.f.includes(f))&&(!l||p.l===l)&&(!pm||PERM.test(p.lic)));
r.sort((a,b)=>s==='n'?a.n.localeCompare(b.n):s==='u'?b.u.localeCompare(a.u):b.st-a.st);
$('count').textContent=r.length+' of '+P.length+' projects';
$('res').innerHTML=r.map(p=>`<article class=card><h3><a href="/explore/${{p.s}}/">${{esc(p.n)}}</a></h3><p>${{esc(p.d.slice(0,160))}}</p><p class=meta>★ ${{p.st.toLocaleString()}} · ${{esc(p.l)}} · active ${{p.u}} · ${{esc(p.lic)}}</p><div>${{p.c.map(x=>`<span class=chip>${{esc(x)}}</span>`).join('')}}${{p.f.slice(0,4).map(x=>`<span class="chip fw">${{esc(x)}}</span>`).join('')}}</div><p class=meta><a href="${{p.fk}}">fork</a> · <a href="${{p.o}}">original</a></p></article>`).join('')}}
for(const id of['q','fc','ff','fl','so','fp'])$(id).addEventListener('input',draw);
</script>''',ld=[{"@type":"CollectionPage","name":"Solana SuperStack explorer","url":SITE+"/explore/"}],crumbs=[('/','Home'),('/explore/','Explore')])
lesson_for_cat={'DeFi':['pdas','cpis','spl-tokens','oracles','escrow'],'Payments':['solana-pay','spl-tokens','blinks-actions','transactions'],'NFTs & Digital Assets':['nfts','compressed-nfts','token-2022'],'AI & Agents':['ai-agents','transactions','blinks-actions'],'Gaming':['pdas','compressed-nfts','transactions'],'DePIN':['oracles','compressed-nfts','spl-tokens'],'Consumer & Social':['blinks-actions','compressed-nfts','solana-pay'],'Wallets & Identity':['transactions','pdas'],'Governance & DAOs':['pdas','cpis','account-constraints'],'Infrastructure & Tooling':['transactions','account-constraints'],'Other':['pdas','cpis']}
have={L['slug']:L for L,_ in LES}
QUEUE=[]
ideas=[]
LEVEL=collections.Counter()
for pr in P:
  ls=lessons_by_proj[pr['name']]; n,top,ext,progs=arch(pr) if pr['cloned'] else (0,[],[],[])
  summ=readme_summary(pr) if pr['cloned'] else ''; cmds=manifest_cmds(pr) if pr['cloned'] else []
  kx=pr['kx']
  level='lesson' if kx else ('guide' if n>=5 else 'listing'); LEVEL[level]+=1; pr['level']=level
  facts=f"""<dl class=facts><dt>Original</dt><dd><a href="{pr['original']}">{E(pr['original_name'])}</a></dd><dt>SuperStack fork</dt><dd><a href="{pr['fork']}">{E(pr['fork'][19:])}</a> @ <a href="{pr['fork']}/tree/{pr['commit']}"><code>{pr['commit'][:7]}</code></a></dd><dt>Stars</dt><dd>{pr['stars']:,}</dd><dt>Last push (original)</dt><dd>{pr['pushed'][:10]}</dd><dt>Languages</dt><dd>{E(', '.join(pr['languages']) or '—')}</dd><dt>Detected stack</dt><dd>{chips(pr['frameworks'],'chip fw') or 'not detected'}</dd><dt>Categories</dt><dd>{''.join(f'<a class=chip href="/what-to-build/{re.sub("[^a-z0-9]+","-",c.lower()).strip("-")}/">{E(c)}</a>' for c in pr['categories'])}</dd><dt>Licence</dt><dd>{E(pr['license'] or 'none detected')}{'' if pr['permissive'] else ': code not quoted on Sol.College'}</dd>{f'<dt>Homepage</dt><dd><a href="{E(pr["homepage"])}" rel=nofollow>{E(pr["homepage"])}</a></dd>' if pr['homepage'] else ''}</dl>"""
  badge={'lesson':'Full lesson','guide':('Structure lesson (licence does not allow quoting code)' if not pr['permissive'] else 'Structure lesson'),'listing':'Listing only: too little code to teach from'}[level]
  body=f"<p class=eyebrow>{badge}</p><h1>{E(pr['name'])}</h1><p class=lead>{E(pr['description'])}</p>"
  if level=='listing':
    body+=facts+f"<p>This fork has {n} source files we can read, which isn't enough to build a lesson from. It's listed for completeness.</p>"
  else:
    body+=('<h2>What it does</h2><p>From the project README:</p><blockquote>'+E(summ)+'</blockquote>' if summ and pr['permissive'] else '')+facts
    body+=f"<h2>Architecture</h2><p>{n} source files. By extension: {', '.join(f'{E(e)} ×{c}' for e,c in ext)}.</p><table class=tbl><thead><tr><th>Top-level directory</th><th>Source files</th></tr></thead><tbody>"+''.join(f'<tr><td><a href="{pr["fork"]}/tree/{pr["commit"]}/{"" if d=="(root)" else E(d)}"><code>{E(d)}</code></a></td><td>{c}</td></tr>' for d,c in top)+"</tbody></table>"
    if progs: body+="<p>On-chain programs: "+', '.join(f'<a href="{pr["fork"]}/tree/{pr["commit"]}/{E(p)}"><code>{E(p)}</code></a>' for p in progs)+"</p>"
    hw=tested.how_it_works(pr,'work/'+pr['name']) if not kx else []
    if hw: body+="<h2>How it works: instructions and accounts</h2><p>Each instruction handler and the accounts struct it validates, found by reading the Rust source. Links go to the exact line at the pinned commit.</p><table class=tbl><thead><tr><th>Instruction</th><th>Accounts</th><th>Source</th></tr></thead><tbody>"+''.join(hw)+"</tbody></table>"
    if pr.get('sf'): body+="<h2>Where the Solana code lives</h2><p>Source files that import a Solana SDK, ranked by how many Solana APIs they use, with the APIs each one calls. Read them in this order to see how the app talks to the chain.</p><table class=tbl><thead><tr><th>File</th><th>Solana APIs used</th></tr></thead><tbody>"+''.join(f'<tr><td><a href="{pr["fork"]}/blob/{pr["commit"]}/{E(rel)}"><code>{E(rel)}</code></a></td><td>{", ".join(f"<code>{E(a)}</code>" for a in aps)}</td></tr>' for _,rel,aps in pr['sf'])+"</tbody></table>"
    if kx: body+=tested.guide(pr,'work/'+pr['name'])
    dh=dapp(pr)
    if not dh:
      QUEUE.append((pr['slug'],pr['fork'],pr['commit'],'anchor' if 'Anchor' in pr['frameworks'] else ('program' if progs else 'client')))
      dh=f'<section class=note><h2>Dapp: deploying</h2><p>This fork is queued for its own live dapp on Sol.College, with a Devnet/Mainnet switch. It appears here, at <code>/dapps/{pr["slug"]}/</code>, once it is deployed and checked on devnet. Until then, run it locally with the commands below.</p></section>'
    body+=dh+mainnet_panel(re.sub(r'[^a-z0-9-]+','-',pr['name'].lower()))
    if kx: body+="<h2>Key code, explained</h2><p>Excerpts chosen automatically where the code uses the most Solana concepts, pinned to the fork's commit.</p>"+''.join(code(x) for x in kx)
    if cmds: body+="<h2>How to run, build and test</h2><p>These commands come from the repo's own manifests (package.json scripts, Anchor.toml, Cargo, go.mod, Makefile). Check the README for prerequisites and environment variables.</p><table class=tbl><thead><tr><th>Directory</th><th>Command</th><th>Runs</th></tr></thead><tbody>"+''.join(f'<tr><td><code>{E(d)}</code></td><td><code>{E(c)}</code></td><td>{E(x) if pr["permissive"] or not x else ""}</td></tr>' for d,c,x in cmds)+"</tbody></table>"
    else: body+="<h2>How to run</h2><p>No package.json, Anchor.toml, Cargo.toml, go.mod or Makefile was found near the root. See the project README.</p>"
    ideas_l=[have[s] for s in lesson_for_cat.get(pr['categories'][0],[]) if s in have][:3]
    body+="<h2>What you could build from it</h2><ul>"+f"<li>Fork <a href='{pr['fork']}'>the SuperStack copy</a> and extend it within the {E(pr['categories'][0])} gaps listed on <a href='/what-to-build/{re.sub('[^a-z0-9]+','-',pr['categories'][0].lower()).strip('-')}/'>the idea page</a>.</li>"+''.join(f'<li>Learn the pattern first: <a href="/learn-by-example/{L["slug"]}/">{E(L["title"])}</a></li>' for L in ideas_l)+"</ul>"
  if ls: body+='<h2>Used in lessons</h2><ul>'+''.join(f'<li><a href="/learn-by-example/{L["slug"]}/">{E(L["title"])}</a></li>' for L in ls)+'</ul>'
  page(f"/explore/{pr['slug']}/",f"{pr['name']}: Solana {'code walkthrough' if level=='lesson' else ('lesson' if level=='guide' else 'project')} ({pr['categories'][0]})",fit((pr['description'] or pr['name']+': open-source Solana project.').rstrip('.')+'.',95)+' Architecture, key code, how to run it, and what to build.',body,lastmod=pr['pushed'][:10],
  ld=[{"@type":"SoftwareSourceCode","name":pr['name'],"url":f"{SITE}/explore/{pr['slug']}/","codeRepository":pr['original'],"isBasedOn":pr['fork'],"runtimePlatform":"Solana","programmingLanguage":pr['language'],"license":pr['license']}]+([{"@type":"LearningResource","name":pr['name']+" code walkthrough","isAccessibleForFree":True,"citation":[x['url'] for x in kx]}] if kx else ([{"@type":"LearningResource","name":pr['name']+" structure lesson","isAccessibleForFree":True,"learningResourceType":"Code walkthrough","url":f"{SITE}/explore/{pr['slug']}/"}] if level=='guide' else [])),crumbs=[('/','Home'),('/explore/','Explore'),(f"/explore/{pr['slug']}/",pr['name'])])
# ---------- topic hubs, learning path, glossary, FAQ
HUBS=hubs.render(globals()); TOPIC_OF=globals().get('TOPIC_OF',{})
page('/','Sol.College: learn Solana development from real code','Free Solana tutorials built from real open-source code: a beginner-to-advanced path, annotated Anchor lessons, topic hubs, guides and a project explorer.',
f'''<section class=hero><p class=eyebrow>Learn by example</p><h1>Learn Solana from <em>real code</em>.</h1><p class=lead>Every lesson here is built from excerpts of real, permissively licensed projects in {src_note}, with permalinks to the exact lines at a pinned commit and a plain-English walkthrough.</p>
<div class=stats><a href="/explore/"><b>{len(P)}</b>projects</a><a href="/learn-by-example/"><b>{len(LES)}</b>lessons</a><a href="/learn-by-example/"><b>{sum(len(e) for _,e in LES)}</b>annotated excerpts</a><a href="/what-to-build/"><b>{len(cats)}</b>idea pages</a></div>
<p class=cta><a class=btn href="/learn-solana/">Start the learning path</a> <a class="btn ghost" href="/learn-by-example/">All lessons</a> <a class="btn ghost" href="/explore/">Explore the SuperStack</a></p></section>
<section><h2>Lessons</h2><div class=grid>{''.join(f'<article class=card><h3><a href="/learn-by-example/{L["slug"]}/">{E(L["title"])}</a></h3><p>{E(L["intro"][:150])}…</p><p class=meta>{len(ex)} real excerpts</p></article>' for L,ex in LES)}</div></section>
<section><h2>Learn by topic</h2><p>{' '.join(f'<a class=chip href="/topics/{T["slug"]}/">{E(T["name"])}</a>' for T in HUBS)} · <a href="/glossary/">Glossary</a> · <a href="/faq/">FAQ</a></p></section>
<section><h2>Most-starred projects in the stack</h2><div class=grid>{''.join(card(p) for p in sorted(P,key=lambda p:-p['stars'])[:6])}</div></section>
<section class=split><div><h2>What to build</h2><p>Idea pages built from the shape of the catalog: where strong projects are scarce, which stacks dominate each category, and a starter path through real modules.</p><a class=btn href="/what-to-build/">See the gaps</a></div><div><h2>How to build</h2><p>Practical guides to setup, the Anchor workflow, testing, deploying from devnet to mainnet, and a security checklist, each linked to the official docs.</p><a class=btn href="/how-to-build/">Read the guides</a></div></section>
<section class=note><h2>Also on Sol.College</h2><p>Our original programme on solar-powered AI edge nodes is still here: <a href="/edge-ai/">overview</a>, the <a href="/calculator">energy-to-compute calculator</a>, <a href="/learn">operator courses</a>, <a href="/resources">resources</a>, the <a href="/for-teams">pilot for teams</a> and <a href="/contact">contact</a>.</p></section>''',
ld=[{"@type":"WebSite","@id":SITE+"/#website","name":"Sol.College","url":SITE+"/","inLanguage":"en","description":"Learn to build on Solana from real code.","publisher":{"@id":SITE+"/#org"},"potentialAction":{"@type":"SearchAction","target":{"@type":"EntryPoint","urlTemplate":SITE+"/explore/?q={search_term_string}"},"query-input":"required name=search_term_string"}},{"@type":["Organization","EducationalOrganization"],"@id":SITE+"/#org","name":"Sol.College","url":SITE+"/","logo":SITE+"/android-chrome-512x512.png","sameAs":["https://github.com/Blockchains/sol-college"]}])
# ---------- lessons
page('/learn-by-example/','Learn Solana by example: annotated lessons from real code',f'{len(LES)} Solana lessons (PDAs, CPIs, SPL tokens, Token-2022, escrow, NFTs, oracles, Solana Pay, Blinks, AI agents) built from real code excerpts with permalinks.',
f'<h1>Learn by example</h1><p class=lead>Each lesson explains one concept, then walks through real excerpts from projects in the stack, pinned to a commit.</p><div class=grid>'+''.join(f'<article class=card><h3><a href="/learn-by-example/{L["slug"]}/">{E(L["title"])}</a></h3><p>{E(L["intro"][:170])}…</p><p class=meta>{len(ex)} excerpts from {", ".join(E(x["project"]["name"]) for x in ex[:3])}</p></article>' for L,ex in LES)+'</div>',
ld=[{"@type":"Course","name":"Learn Solana by example","description":"Annotated lessons built from real open-source Solana code.","url":SITE+"/learn-by-example/","provider":{"@type":"Organization","name":"Sol.College","url":SITE},"isAccessibleForFree":True,"hasCourseInstance":{"@type":"CourseInstance","courseMode":"online","courseWorkload":"PT3H"},"offers":{"@type":"Offer","price":0,"priceCurrency":"USD","category":"Free"},"hasPart":[{"@type":"LearningResource","name":L['title'],"url":f"{SITE}/learn-by-example/{L['slug']}/"} for L,_ in LES]}],crumbs=[('/','Home'),('/learn-by-example/','Learn by example')])
def related(L):
  ts=TOPIC_OF.get(L['slug'],[]); out=[]
  for T in ts:
    for s in T['ls']:
      if s!=L['slug'] and have[s] not in out: out.append(have[s])
  return out[:5] or [x for x,_ in LES if x is not L][:3]
for i,(L,ex) in enumerate(LES):
  nxt=LES[(i+1)%len(LES)][0]
  page(f"/learn-by-example/{L['slug']}/",f"{L['title']} | Solana tutorial",L['intro'],
  f'''<article class=lesson><h1>{E(L['title'])}</h1><p class=lead>{E(L['intro'])}</p><p class=docs>Reference: {' · '.join(f'<a href="{u}">{E(n)}</a>' for n,u in L['docs'])}</p>
<h2>Real code, line by line</h2><p>{len(ex)} excerpts from different projects. Each caption links the exact lines at the fork's pinned commit. The notes below each excerpt explain the lines that matter.</p>{''.join(code(x) for x in ex)}
<h2>Go further</h2><ul>{''.join(f'<li><a href="/explore/{x["project"]["slug"]}/">{E(x["project"]["name"])}</a>: explore the full project</li>' for x in ex)}<li>Next lesson: <a href="/learn-by-example/{nxt['slug']}/">{E(nxt['title'])}</a></li></ul>
<h2>Related lessons</h2><ul>{''.join(f'<li><a href="/learn-by-example/{R["slug"]}/">{E(R["title"])}</a></li>' for R in related(L))}</ul>
<p>Topics: {''.join(f'<a class=chip href="/topics/{T["slug"]}/">{E(T["name"])}</a>' for T in TOPIC_OF.get(L['slug'],[]))} · <a href="/learn-solana/">Learning path</a> · <a href="/glossary/">Glossary</a></p></article>''',
  ld=[{"@type":"LearningResource","name":L['title'],"description":L['intro'],"url":f"{SITE}/learn-by-example/{L['slug']}/","inLanguage":"en","learningResourceType":"Annotated code example","educationalLevel":hubs.LEVEL.get(L['slug'],'Intermediate'),"teaches":L['title'],"isAccessibleForFree":True,"provider":{"@type":"Organization","name":"Sol.College","url":SITE},"isPartOf":{"@type":"Course","name":"Learn Solana by example","url":SITE+"/learn-by-example/","provider":{"@type":"Organization","name":"Sol.College","url":SITE}},"citation":[x['url'] for x in ex]}]+[{"@type":"SoftwareSourceCode","name":f"{x['project']['name']}: {x['file']}","codeRepository":x['project']['fork'],"url":x['url'],"programmingLanguage":"Rust" if x['file'].endswith('.rs') else "TypeScript","license":x['project']['license']} for x in ex[:3]],
  crumbs=[('/','Home'),('/learn-by-example/','Learn by example'),(f"/learn-by-example/{L['slug']}/",L['title'])])
# ---------- ideas
for c,ps in sorted(cats.items(),key=lambda kv:len(kv[1])):
  slug=re.sub('[^a-z0-9]+','-',c.lower()).strip('-'); strong=[p for p in ps if p['stars']>=100]; act=[p for p in ps if p['pushed']>='2025-11']
  fw=collections.Counter(f for p in ps for f in p['frameworks']).most_common(6); lg=collections.Counter(p['language'] or 'Other' for p in ps).most_common(4)
  onchain=[p for p in ps if set(p['frameworks'])&{'Anchor','Pinocchio','Native Rust','Steel'}]
  gaps=[]
  if len(strong)<3: gaps.append(f"Only {len(strong)} project(s) here have 100+ stars. There's room for a reference-quality open-source project.")
  if not onchain: gaps.append("No project in this category ships its own on-chain program (Anchor, Pinocchio or native) that we detected. Most are clients or off-chain services, so an open, audited program is a clear gap.")
  elif len(onchain)<len(ps)/3: gaps.append(f"Only {len(onchain)} of {len(ps)} projects include an on-chain program. The rest are off-chain or client code.")
  if len(act)<len(ps)/2: gaps.append(f"{len(ps)-len(act)} of {len(ps)} projects haven't been pushed to in the last 12 months. Maintained successors are needed.")
  if not [p for p in ps if p['permissive']]: gaps.append("None of these projects is permissively licensed, so builders can't freely reuse them. An MIT or Apache-2.0 implementation would fill that gap.")
  start=[p for p in sorted(ps,key=lambda p:-p['stars']) if p['permissive']][:4]
  path_l=[have[s] for s in lesson_for_cat.get(c,[]) if s in have]
  ideas.append((c,slug,len(ps),len(strong)))
  page(f'/what-to-build/{slug}/',f'What to build in Solana {c}: gaps, common stacks and a starter path',f'{len(ps)} {c} projects analysed: where strong projects are scarce, which stacks they use, and a starter path through real code.',
  f'''<h1>What to build: {E(c)}</h1><p class=lead>Based on {len(ps)} projects in the stack in this category, {len(strong)} with 100+ stars and {len(act)} active in the last year.</p>
<h2>Gaps we see</h2><ul>{''.join(f'<li>{E(g)}</li>' for g in gaps) or '<li>This category is comparatively well served. Look for niches inside it, or improve on the leaders below.</li>'}</ul>
<h2>Common stacks</h2><p>{chips([f"{k} ×{v}" for k,v in fw],'chip fw') or 'No framework detected.'}</p><p>Languages: {', '.join(f'{E(k)} ({v})' for k,v in lg)}</p>
<h2>Starter path</h2><ol>{''.join(f'<li>Lesson: <a href="/learn-by-example/{L["slug"]}/">{E(L["title"])}</a></li>' for L in path_l)}{''.join(f'<li>Study and fork <a href="/explore/{p["slug"]}/">{E(p["name"])}</a> ({E(p["license"])}, ★{p["stars"]:,}): <a href="{p["fork"]}">SuperStack module</a></li>' for p in start)}<li>Follow <a href="/how-to-build/anchor-workflow/">the Anchor workflow</a> and the <a href="/how-to-build/security-checklist/">security checklist</a>, then <a href="/how-to-build/deploy/">deploy to devnet</a>.</li></ol>
<h2>Projects in this category</h2><div class=grid>{''.join(card(p) for p in sorted(ps,key=lambda p:-p['stars'])[:24])}</div><p><a href="/explore/?category={E(c)}">See all {len(ps)} in the explorer →</a></p>''',
  ld=[{"@type":"Article","headline":f"What to build in Solana {c}","about":c}],crumbs=[('/','Home'),('/what-to-build/','What to build'),(f'/what-to-build/{slug}/',c)])
page('/what-to-build/','What to build on Solana: gaps and patterns from real projects','Idea pages from catalog analysis: categories with few strong projects, common stacks per category, and starter paths into real code.',
'<h1>What to build</h1><p class=lead>Ordered from least served to most served. "Strong" means 100+ GitHub stars on the original repository.</p><table class=tbl><thead><tr><th>Category</th><th>Projects</th><th>Strong</th><th></th></tr></thead><tbody>'+''.join(f'<tr><td>{E(c)}</td><td>{n}</td><td>{s}</td><td><a href="/what-to-build/{sl}/">Gaps and starter path →</a></td></tr>' for c,sl,n,s in ideas)+'</tbody></table>',crumbs=[('/','Home'),('/what-to-build/','What to build')])
# ---------- guides
for g in GUIDES:
  b=''
  for h,t,x in g['body']:
    b+=f'<h2>{E(h)}</h2><p>{E(t)}</p>'
    if isinstance(x,str): b+=f'<pre class=sh><code>{E(x)}</code></pre>'
    elif x: b+='<ul>'+''.join(f'<li><a href="{u}">{E(n)}</a></li>' for n,u in x)+'</ul>'
  page(f"/how-to-build/{g['slug']}/",g['title']+' | Sol.College',g['title']+': a practical guide with links to the official Solana and Anchor docs.',f'<article class=lesson><h1>{E(g["title"])}</h1>{b}<p class=docs>Commands and APIs change, so the official <a href="https://solana.com/docs">Solana docs</a> and <a href="https://www.anchor-lang.com/docs">Anchor docs</a> are the source of truth.</p></article>',
  ld=[{"@type":"HowTo","name":g['title'],"step":[{"@type":"HowToStep","name":h,"text":t} for h,t,_ in g['body']]}],crumbs=[('/','Home'),('/how-to-build/','How to build'),(f"/how-to-build/{g['slug']}/",g['title'])])
page('/how-to-build/','How to build on Solana: setup, Anchor, testing, deploy, security','Practical Solana guides: environment setup, Anchor workflow, testing, deploying to devnet and mainnet, and a security checklist.',
'<h1>How to build</h1><div class=grid>'+''.join(f'<article class=card><h3><a href="/how-to-build/{g["slug"]}/">{E(g["title"])}</a></h3><p>{E(g["body"][0][1][:140])}…</p></article>' for g in GUIDES)+'</div>',crumbs=[('/','Home'),('/how-to-build/','How to build')])
# ---------- changelog of published fork pages
prev=prev or []
known={x['path'] for x in prev if x.get('type')!='updated'}; now=datetime.datetime.now(datetime.timezone.utc).strftime('%Y-%m-%dT%H:%M:%SZ')
for pr in P:
  pth=f"/explore/{pr['slug']}/"
  if pth not in known: prev.append(dict(path=pth,url=SITE+pth,project=pr['name'],original=pr['original_name'],published=now))
  res=tested.result(pr) if pr['kx'] else None
  if res and not any(x.get('type')=='updated' and x['path']==pth and x.get('tested')==res['tested'] for x in prev):
    prev.append(dict(path=pth,url=SITE+pth,project=pr['name'],original=pr['original_name'],published=now,type='updated',tested=res['tested'],status=res['status']))
live={f"/explore/{p['slug']}/" for p in P}
for m in (json.load(open('dapps/mainnet-live.json')) if os.path.exists('dapps/mainnet-live.json') else []):
  pth=f"/explore/{m['slug']}/"
  if not any(x.get('type')=='live-mainnet' and x['path']==pth for x in prev): prev.append(dict(path=pth,url=SITE+pth,project=m['slug']+': Live on mainnet',original='mainnet program '+m['program'],published=m['published'],type='live-mainnet',program=m['program']))
cur=[x for x in prev if x['path'] in live]; cur.sort(key=lambda x:x['published'],reverse=True)
json.dump(prev,open(OUT+'/published.json','w'),indent=1)
RANK={'client':0,'program':1,'anchor':2}
def qk(p):
  k='anchor' if 'Anchor' in p['frameworks'] else ('program' if any(r.endswith('src/lib.rs') for r,_ in files(p['name'],('lib.rs',))) else 'client')
  rs=sum(1 for r,_ in files(p['name'],('.rs',)) if 'programs/' in r or r.endswith('lib.rs'))
  return (RANK[k],rs,-p['stars']),k,rs
QL=sorted(((qk(p),p) for p in PENDING_DAPP),key=lambda x:x[0][0])
open(OUT+'/dapp-queue.txt','w').write('# Cheapest first (client-only, then smallest programs). slug fork commit kind rust_files. New lessons publish only after dapps/deployed/<slug>.json has devnet sigs.\n'+''.join(f"{p['slug']} {p['fork']} {p['commit']} {k} {rs}\n" for (_,k,rs),p in QL)+''.join(f'{a} {b} {c} {d} live-lesson\n' for a,b,c,d in QUEUE))
open(OUT+'/CHANGELOG.md','w').write('# Sol.College published fork lessons\n\n| Published (UTC) | Change | Project | URL |\n|---|---|---|---|\n'+''.join(f"| {x['published']} | {'updated: '+x.get('status','')+' build guide' if x.get('type')=='updated' else 'new'} | {x['project']} | {x['url']} |\n" for x in cur))
page('/new/','New on Sol.College: recently published Solana code lessons','The newest Solana project walkthroughs published on Sol.College, with timestamps. Also available as published.json and CHANGELOG.md.',
'<h1>New on Sol.College</h1><p class=lead>Every fork walkthrough, newest first. Machine-readable: <a href="/published.json">published.json</a> · <a href="/CHANGELOG.md">CHANGELOG.md</a></p><table class=tbl><thead><tr><th>Published (UTC)</th><th>Project</th><th>Original</th></tr></thead><tbody>'+''.join(f'<tr><td>{x["published"][:16].replace("T"," ")}</td><td><a href="{x["path"]}">{E(x["project"])}</a>{" <span class=chip>updated: tested build guide</span>" if x.get("type")=="updated" else (" <span class=chip>Live on mainnet</span>" if x.get("type")=="live-mainnet" else "")}</td><td>{E(x["original"])}</td></tr>' for x in cur)+'</tbody></table>',crumbs=[('/','Home'),('/new/','New')])
# ---------- legacy home preserved at /edge-ai/
if os.path.exists('legacy/index.html'):
  t=open('legacy/index.html').read()
  t=re.sub(r'<script(?![^>]*ld\+json)[^>]*>.*?</script>','',t,flags=re.S); t=re.sub(r'<link rel="modulepreload"[^>]*>','',t)
  t=t.replace('<link rel="canonical" href="https://sol.college/"/>','<link rel="canonical" href="https://sol.college/edge-ai/"/>')
  os.makedirs(OUT+'/edge-ai',exist_ok=True); open(OUT+'/edge-ai/index.html','w').write(t)
legacy=[os.path.dirname(os.path.relpath(f,'legacy')) for f in glob.glob('legacy/**/index.html',recursive=True)]
# ---------- 404
page('/404/','Page not found | Sol.College','This page does not exist. Try the learning path, the lessons or the project explorer.',
'<h1>Page not found</h1><p class=lead>That address doesn\'t exist on Sol.College, or it moved.</p><ul><li><a href="/learn-solana/">Learn Solana: the learning path</a></li><li><a href="/learn-by-example/">All lessons</a></li><li><a href="/topics/">Topics</a></li><li><a href="/explore/">Explore projects</a> (searchable)</li><li><a href="/glossary/">Glossary</a> · <a href="/faq/">FAQ</a></li></ul>',noindex=True)
shutil.move(OUT+'/404/index.html',OUT+'/404.html'); shutil.rmtree(OUT+'/404',ignore_errors=True)
# ---------- legacy pages: trailing-slash canonicals (GitHub Pages redirects /x to /x/) and the shared icon set
ICONS='<link rel="icon" href="/favicon.ico" sizes="48x48"/><link rel="icon" href="/favicon.svg" type="image/svg+xml"/><link rel="apple-touch-icon" href="/apple-touch-icon.png"/><link rel="manifest" href="/site.webmanifest"/><meta name="theme-color" content="#0b0a14"/>'
legacy=[os.path.dirname(os.path.relpath(f,'legacy')) for f in glob.glob('legacy/**/index.html',recursive=True)]
for l in legacy+['edge-ai']:
  fp=f'{OUT}/{l}/index.html'.replace('/./','/')
  if not os.path.exists(fp): continue
  t=open(fp,encoding='utf-8',errors='surrogateescape').read()
  t=re.sub(r'((?:rel="canonical" href|property="og:url" content)="https://sol\.college/[^"]*?[^/"])"',r'\1/"',t)
  LT={'about':'About SOL.COLLEGE: solar-powered AI infrastructure','contact':'Contact SOL.COLLEGE: nodes, courses and pilots','edge-ai':'SOL.COLLEGE: solar-powered AI edge nodes and training','learn':'Solar, storage and local AI courses | SOL.COLLEGE'}
  if l in LT: t=re.sub(r'<title>[^<]*</title>',f'<title>{LT[l]}</title>',t,1)
  t=re.sub(r'(<meta name="description" content=")([^"]*)"',lambda m:m.group(1)+(m.group(2) if len(html.unescape(m.group(2)))<=158 else E(fit(html.unescape(m.group(2)),158)))+'"',t,1)
  if l=='auth': t=t.replace('<head>','<head><meta name="robots" content="noindex"/>',1)
  if '/site.webmanifest' not in t: t=t.replace('</head>',ICONS+'</head>',1)
  open(fp,'w',encoding='utf-8',errors='surrogateescape').write(t)
# ---------- seo files
today=datetime.date.today().isoformat(); gen=data['generated'][:10]
import subprocess
try: LEGACY_LM=subprocess.run(['git','log','-1','--format=%cs','--','legacy'],capture_output=True,text=True).stdout.strip() or today
except Exception: LEGACY_LM=today
urls=sorted(set(SM+['/edge-ai/']+['/'+l+'/' for l in legacy if l and l!='.' and l!='auth']))
def lm(u):
  if u in LASTMOD: return max(LASTMOD[u],gen) if u.startswith('/explore/') else LASTMOD[u]
  return today if u in SM else LEGACY_LM
open(OUT+'/sitemap.xml','w').write('<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n'+''.join(f'<url><loc>{SITE}{u}</loc><lastmod>{lm(u)}</lastmod></url>\n' for u in urls)+'</urlset>\n')
open(OUT+'/sitemap-index.xml','w').write(f'<?xml version="1.0" encoding="UTF-8"?>\n<sitemapindex xmlns="http://www.sitemaps.org/schemas/sitemap/0.9"><sitemap><loc>{SITE}/sitemap.xml</loc><lastmod>{today}</lastmod></sitemap></sitemapindex>\n')
open(OUT+'/robots.txt','w').write(f'User-agent: *\nAllow: /\nDisallow: /auth\n\nSitemap: {SITE}/sitemap.xml\n')
# Atom feed of newly published lessons and project walkthroughs
xe=lambda x:html.escape(str(x),quote=True)
ent=[x for x in cur if x.get('type')!='updated'][:50]
open(OUT+'/feed.xml','w').write(f'<?xml version="1.0" encoding="utf-8"?>\n<feed xmlns="http://www.w3.org/2005/Atom"><title>New on Sol.College</title><subtitle>New Solana code walkthroughs built from real open-source projects</subtitle><link href="{SITE}/feed.xml" rel="self"/><link href="{SITE}/new/"/><id>{SITE}/feed.xml</id><updated>{(ent[0]["published"] if ent else now)}</updated><author><name>Sol.College</name></author><icon>{SITE}/favicon-32x32.png</icon>'+''.join(f'<entry><title>{xe(x["project"])}: Solana code walkthrough</title><link href="{xe(x["url"])}"/><id>{xe(x["url"])}</id><published>{x["published"]}</published><updated>{x["published"]}</updated><summary>Walkthrough of {xe(x["original"])}: architecture, annotated code, and how to build and run it.</summary></entry>' for x in ent)+'</feed>\n')
open(OUT+'/llms.txt','w').write(f"# Sol.College\n\n> Learn to build on Solana from real code: an explorer of the Solana SuperStack, annotated lessons built from permissively licensed excerpts with permalinks, idea pages and practical guides.\n\n## Lessons\n"+''.join(f"- [{L['title']}]({SITE}/learn-by-example/{L['slug']}/): {L['intro'][:120]}\n" for L,_ in LES)+"\n## Start here\n- [Learn Solana: beginner-to-advanced path]({SITE}/learn-solana/)\n- [Topics]({SITE}/topics/)\n- [Glossary]({SITE}/glossary/)\n- [FAQ]({SITE}/faq/)\n\n## Guides\n"+''.join(f"- [{g['title']}]({SITE}/how-to-build/{g['slug']}/)\n" for g in GUIDES)+"\n## What to build\n"+''.join(f"- [{c}]({SITE}/what-to-build/{s}/)\n" for c,s,_,_ in ideas)+f"\n## Data\n- [Project catalog JSON]({SITE}/projects.json): {len(P)} projects\n- [Explorer]({SITE}/explore/)\n\n## Optional\n- [Solar AI edge nodes programme]({SITE}/edge-ai/)\n")
for f in os.listdir('static'):
  (shutil.copytree if os.path.isdir('static/'+f) else shutil.copy)('static/'+f,OUT+'/'+f)
open(OUT+'/CNAME','w').write(os.environ.get('SITE_CNAME','')) if os.environ.get('SITE_CNAME') else None
open(OUT+'/.nojekyll','w').write('')
shutil.copy(OUT+'/index.html',OUT+'/404.html') if not os.path.exists(OUT+'/404.html') else None
json.dump(dict(projects=len(P),lessons=len(LES),excerpts=sum(len(e) for _,e in LES),ideas=len(ideas),levels=dict(LEVEL),forks_total=TOTAL,excluded=dict(EXCL),waiting=len(WAIT),awaiting_dapp=len(PENDING_DAPP),guides=len(GUIDES),pages=len(urls)),open(OUT+'/stats.json','w'))
BASE=os.environ.get('SITE_BASE','').rstrip('/')
if BASE:
  SM=list(SM)  # preview under a project-pages subpath: rewrite root-relative links in generated pages
  for f in SM:
    fp=OUT+f+'index.html'; t=open(fp).read()
    t=re.sub(r'(href|src)="/(?!/)',lambda m:f'{m.group(1)}="{BASE}/',t).replace("fetch('/projects.json')",f"fetch('{BASE}/projects.json')").replace('href="/explore/${{','href="'+BASE+'/explore/${{').replace('href="/explore/${p.s}',f'href="{BASE}/explore/${{p.s}}')
    open(fp,'w').write(t)
print(open(OUT+'/stats.json').read())
