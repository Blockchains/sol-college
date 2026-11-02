import json,os,re,html,shutil,collections,glob,datetime
from content import LESSONS,NOTES,CATEGORIES,GUIDES
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
LES=[]
for L in LESSONS:
  ex=excerpt_for(L)
  if ex: LES.append((L,ex))
# ---------- layout
CSS=open('scripts/style.css').read()
NAV=[('/explore/','Explore'),('/learn-by-example/','Learn by example'),('/what-to-build/','What to build'),('/how-to-build/','How to build')]
def page(path,title,desc,body,ld=None,crumbs=None):
  url=SITE+path; lds=[dict({"@context":"https://schema.org"},**x) for x in (ld or [])]
  if crumbs: lds.append({"@context":"https://schema.org","@type":"BreadcrumbList","itemListElement":[{"@type":"ListItem","position":i+1,"name":n,"item":SITE+u} for i,(u,n) in enumerate(crumbs)]})
  nav=''.join(f'<a href="{u}"{" aria-current=page" if path.startswith(u) else ""}>{n}</a>' for u,n in NAV)
  bc=('<nav class=crumbs aria-label=Breadcrumb>'+' / '.join(f'<a href="{u}">{E(n)}</a>' for u,n in crumbs[:-1])+f' / <span>{E(crumbs[-1][1])}</span></nav>') if crumbs else ''
  h=f'''<!doctype html><html lang=en><head><meta charset=utf-8><meta name=viewport content="width=device-width,initial-scale=1">
<title>{E(title)}</title><meta name=description content="{E(desc)}"><link rel=canonical href="{url}">
<meta property=og:type content=website><meta property=og:title content="{E(title)}"><meta property=og:description content="{E(desc)}"><meta property=og:url content="{url}"><meta property=og:site_name content="Sol.College"><meta property=og:image content="{SITE}/og.png"><meta name=twitter:card content=summary_large_image>
<meta name=theme-color content="#0b0a14"><link rel=icon href="/favicon.svg" type="image/svg+xml"><link rel=icon href="/favicon.png" type="image/png"><link rel=alternate type=text/plain href="/llms.txt" title="llms.txt">
<style>{CSS}</style>{''.join(f'<script type="application/ld+json">{json.dumps(x)}</script>' for x in lds)}</head><body>
<a class=skip href="#main">Skip to content</a><header class=top><a class=brand href="/"><span class=logo aria-hidden=true></span>Sol.College</a><nav aria-label=Main>{nav}</nav></header>
<main id=main>{bc}{body}</main><footer><p>Sol.College: learn Solana from real code in the <a href="https://github.com/Blockchains/solana-superstack">SuperStack</a>. Code excerpts are quoted under their original permissive licences, with attribution and permalinks. Facts link to <a href="https://solana.com/docs">Solana</a> and <a href="https://www.anchor-lang.com/docs">Anchor</a> docs.</p>
<p><a href="/explore/">Explore</a> · <a href="/learn-by-example/">Lessons</a> · <a href="/what-to-build/">Ideas</a> · <a href="/how-to-build/">Guides</a> · <a href="/edge-ai/">Solar AI edge nodes</a> · <a href="/legal/terms">Terms</a> · <a href="/legal/privacy">Privacy</a> · Data refreshed {data['generated'][:10]}</p></footer></body></html>'''
  d=OUT+path; os.makedirs(d,exist_ok=True); open(d+'index.html','w').write(h); SM.append(path)
SM=[]
def chips(xs,cls='chip'): return ''.join(f'<span class={cls}>{E(x)}</span>' for x in xs)
def card(pr):
  return f'''<article class=card><h3><a href="/explore/{pr['slug']}/">{E(pr['name'])}</a></h3><p>{E(pr['description'][:160])}</p><p class=meta>★ {pr['stars']:,} · {E(pr['language'] or '—')} · {E(pr['license'] or 'no licence')}</p><div>{chips(pr['categories'])}{chips(pr['frameworks'][:4],'chip fw')}</div></article>'''
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
page('/','Sol.College: learn to build on Solana from real code','Explore the Solana SuperStack, study annotated excerpts from real open-source Solana projects, and find what to build next. Free and refreshed nightly.',
f'''<section class=hero><p class=eyebrow>Learn by example</p><h1>Learn Solana from <em>real code</em>.</h1><p class=lead>Every lesson here is built from excerpts of real, permissively licensed projects in {src_note}, with permalinks to the exact lines at a pinned commit and a plain-English walkthrough.</p>
<div class=stats><a href="/explore/"><b>{len(P)}</b>projects</a><a href="/learn-by-example/"><b>{len(LES)}</b>lessons</a><a href="/learn-by-example/"><b>{sum(len(e) for _,e in LES)}</b>annotated excerpts</a><a href="/what-to-build/"><b>{len(cats)}</b>idea pages</a></div>
<p class=cta><a class=btn href="/learn-by-example/">Start learning</a> <a class="btn ghost" href="/explore/">Explore the SuperStack</a></p></section>
<section><h2>Lessons</h2><div class=grid>{''.join(f'<article class=card><h3><a href="/learn-by-example/{L["slug"]}/">{E(L["title"])}</a></h3><p>{E(L["intro"][:150])}…</p><p class=meta>{len(ex)} real excerpts</p></article>' for L,ex in LES)}</div></section>
<section><h2>Most-starred projects in the stack</h2><div class=grid>{''.join(card(p) for p in top)}</div></section>
<section class=split><div><h2>What to build</h2><p>Idea pages built from the shape of the catalog: where strong projects are scarce, which stacks dominate each category, and a starter path through real modules.</p><a class=btn href="/what-to-build/">See the gaps</a></div><div><h2>How to build</h2><p>Practical guides to setup, the Anchor workflow, testing, deploying from devnet to mainnet, and a security checklist, each linked to the official docs.</p><a class=btn href="/how-to-build/">Read the guides</a></div></section>
<section class=note><h2>Also on Sol.College</h2><p>Our original programme on solar-powered AI edge nodes is still here: <a href="/edge-ai/">overview</a>, the <a href="/calculator">energy-to-compute calculator</a>, <a href="/learn">operator courses</a>, <a href="/resources">resources</a>, the <a href="/for-teams">pilot for teams</a> and <a href="/contact">contact</a>.</p></section>''',
ld=[{"@type":"WebSite","name":"Sol.College","url":SITE+"/","description":"Learn to build on Solana from real code."},{"@type":"EducationalOrganization","name":"Sol.College","url":SITE}])
# ---------- explore
json.dump([dict(n=p['name'],s=p['slug'],d=p['description'][:200],st=p['stars'],l=p['language'] or 'Other',c=p['categories'],f=p['frameworks'],u=p['pushed'][:10],lic=p['license'] or 'none',fk=p['fork'],o=p['original']) for p in P],open(OUT+'/projects.json','w'))
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
let r=P.filter(p=>(!q||(p.n+' '+p.d+' '+p.f.join(' ')).toLowerCase().includes(q))&&(!c||p.c.includes(c))&&(!f||p.f.includes(f))&&(!l||p.l===l)&&(!pm||PERM.test(p.lic)));
r.sort((a,b)=>s==='n'?a.n.localeCompare(b.n):s==='u'?b.u.localeCompare(a.u):b.st-a.st);
$('count').textContent=r.length+' of '+P.length+' projects';
$('res').innerHTML=r.map(p=>`<article class=card><h3><a href="/explore/${{p.s}}/">${{esc(p.n)}}</a></h3><p>${{esc(p.d.slice(0,160))}}</p><p class=meta>★ ${{p.st.toLocaleString()}} · ${{esc(p.l)}} · active ${{p.u}} · ${{esc(p.lic)}}</p><div>${{p.c.map(x=>`<span class=chip>${{esc(x)}}</span>`).join('')}}${{p.f.slice(0,4).map(x=>`<span class="chip fw">${{esc(x)}}</span>`).join('')}}</div><p class=meta><a href="${{p.fk}}">fork</a> · <a href="${{p.o}}">original</a></p></article>`).join('')}}
for(const id of['q','fc','ff','fl','so','fp'])$(id).addEventListener('input',draw);
</script>''',ld=[{"@type":"CollectionPage","name":"Solana SuperStack explorer","url":SITE+"/explore/"}],crumbs=[('/','Home'),('/explore/','Explore')])
lessons_by_proj=collections.defaultdict(list)
for L,ex in LES:
  for x in ex: lessons_by_proj[x['project']['name']].append(L)
for pr in P:
  ls=lessons_by_proj[pr['name']]
  page(f"/explore/{pr['slug']}/",f"{pr['name']}: Solana project ({', '.join(pr['categories'])})",(pr['description'] or pr['name'])[:150]+' Category, stack, licence and links to source.',
  f'''<h1>{E(pr['name'])}</h1><p class=lead>{E(pr['description'])}</p><dl class=facts><dt>Original</dt><dd><a href="{pr['original']}">{E(pr['original_name'])}</a></dd><dt>SuperStack fork</dt><dd><a href="{pr['fork']}">{E(pr['fork'][19:])}</a> @ <code>{pr['commit'][:7]}</code></dd><dt>Stars</dt><dd>{pr['stars']:,}</dd><dt>Last push (original)</dt><dd>{pr['pushed'][:10]}</dd><dt>Languages</dt><dd>{E(', '.join(pr['languages']) or '—')}</dd><dt>Detected stack</dt><dd>{chips(pr['frameworks'],'chip fw') or 'not detected'}</dd><dt>Categories</dt><dd>{''.join(f'<a class=chip href="/what-to-build/{re.sub("[^a-z0-9]+","-",c.lower()).strip("-")}/">{E(c)}</a>' for c in pr['categories'])}</dd><dt>Licence</dt><dd>{E(pr['license'] or 'none detected')}{'' if pr['permissive'] else ': not quoted on Sol.College'}</dd>{f'<dt>Homepage</dt><dd><a href="{E(pr["homepage"])}" rel=nofollow>{E(pr["homepage"])}</a></dd>' if pr['homepage'] else ''}</dl>
{('<h2>Used in lessons</h2><ul>'+''.join(f'<li><a href="/learn-by-example/{L["slug"]}/">{E(L["title"])}</a></li>' for L in ls)+'</ul>') if ls else ''}''',
  ld=[{"@type":"SoftwareSourceCode","name":pr['name'],"codeRepository":pr['original'],"programmingLanguage":pr['language'],"license":pr['license']}],crumbs=[('/','Home'),('/explore/','Explore'),(f"/explore/{pr['slug']}/",pr['name'])])
# ---------- lessons
page('/learn-by-example/','Learn Solana by example: annotated lessons from real code',f'{len(LES)} Solana lessons (PDAs, CPIs, SPL tokens, Token-2022, escrow, NFTs, oracles, Solana Pay, Blinks, AI agents) built from real code excerpts with permalinks.',
f'<h1>Learn by example</h1><p class=lead>Each lesson explains one concept, then walks through real excerpts from projects in the stack, pinned to a commit.</p><div class=grid>'+''.join(f'<article class=card><h3><a href="/learn-by-example/{L["slug"]}/">{E(L["title"])}</a></h3><p>{E(L["intro"][:170])}…</p><p class=meta>{len(ex)} excerpts from {", ".join(E(x["project"]["name"]) for x in ex[:3])}</p></article>' for L,ex in LES)+'</div>',
ld=[{"@type":"Course","name":"Learn Solana by example","description":"Annotated lessons built from real open-source Solana code.","url":SITE+"/learn-by-example/","provider":{"@type":"Organization","name":"Sol.College","url":SITE},"isAccessibleForFree":True,"hasCourseInstance":{"@type":"CourseInstance","courseMode":"online","courseWorkload":"PT3H"},"offers":{"@type":"Offer","price":0,"priceCurrency":"USD","category":"Free"},"hasPart":[{"@type":"LearningResource","name":L['title'],"url":f"{SITE}/learn-by-example/{L['slug']}/"} for L,_ in LES]}],crumbs=[('/','Home'),('/learn-by-example/','Learn by example')])
for i,(L,ex) in enumerate(LES):
  nxt=LES[(i+1)%len(LES)][0]
  page(f"/learn-by-example/{L['slug']}/",f"{L['title']}: Solana lesson with real code",L['intro'][:155],
  f'''<article class=lesson><h1>{E(L['title'])}</h1><p class=lead>{E(L['intro'])}</p><p class=docs>Reference: {' · '.join(f'<a href="{u}">{E(n)}</a>' for n,u in L['docs'])}</p>
<h2>Real code, line by line</h2><p>{len(ex)} excerpts from different projects. Each caption links the exact lines at the fork's pinned commit. The notes below each excerpt explain the lines that matter.</p>{''.join(code(x) for x in ex)}
<h2>Go further</h2><ul>{''.join(f'<li><a href="/explore/{x["project"]["slug"]}/">{E(x["project"]["name"])}</a>: explore the full project</li>' for x in ex)}<li>Next lesson: <a href="/learn-by-example/{nxt['slug']}/">{E(nxt['title'])}</a></li></ul></article>''',
  ld=[{"@type":"LearningResource","name":L['title'],"description":L['intro'],"learningResourceType":"Annotated code example","educationalLevel":"Intermediate","isAccessibleForFree":True,"isPartOf":{"@type":"Course","name":"Learn Solana by example","url":SITE+"/learn-by-example/"},"citation":[x['url'] for x in ex]}],
  crumbs=[('/','Home'),('/learn-by-example/','Learn by example'),(f"/learn-by-example/{L['slug']}/",L['title'])])
# ---------- ideas
lesson_for_cat={'DeFi':['pdas','cpis','spl-tokens','oracles','escrow'],'Payments':['solana-pay','spl-tokens','blinks-actions','transactions'],'NFTs & Digital Assets':['nfts','compressed-nfts','token-2022'],'AI & Agents':['ai-agents','transactions','blinks-actions'],'Gaming':['pdas','compressed-nfts','transactions'],'DePIN':['oracles','compressed-nfts','spl-tokens'],'Consumer & Social':['blinks-actions','compressed-nfts','solana-pay'],'Wallets & Identity':['transactions','pdas'],'Governance & DAOs':['pdas','cpis','account-constraints'],'Infrastructure & Tooling':['transactions','account-constraints'],'Other':['pdas','cpis']}
have={L['slug']:L for L,_ in LES}; ideas=[]
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
# ---------- legacy home preserved at /edge-ai/
if os.path.exists('legacy/index.html'):
  t=open('legacy/index.html').read()
  t=re.sub(r'<script(?![^>]*ld\+json)[^>]*>.*?</script>','',t,flags=re.S); t=re.sub(r'<link rel="modulepreload"[^>]*>','',t)
  t=t.replace('<link rel="canonical" href="https://sol.college/"/>','<link rel="canonical" href="https://sol.college/edge-ai/"/>')
  os.makedirs(OUT+'/edge-ai',exist_ok=True); open(OUT+'/edge-ai/index.html','w').write(t)
legacy=[os.path.dirname(os.path.relpath(f,'legacy')) for f in glob.glob('legacy/**/index.html',recursive=True)]
# ---------- seo files
today=datetime.date.today().isoformat()
urls=sorted(set(SM+['/edge-ai/']+['/'+l for l in legacy if l and l!='.']))
open(OUT+'/sitemap.xml','w').write('<?xml version="1.0" encoding="UTF-8"?><urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">'+''.join(f'<url><loc>{SITE}{u}</loc><lastmod>{today}</lastmod></url>' for u in urls)+'</urlset>')
open(OUT+'/robots.txt','w').write(f'User-agent: *\nAllow: /\nDisallow: /auth\n\nSitemap: {SITE}/sitemap.xml\n')
open(OUT+'/llms.txt','w').write(f"# Sol.College\n\n> Learn to build on Solana from real code: an explorer of the Solana SuperStack, annotated lessons built from permissively licensed excerpts with permalinks, idea pages and practical guides.\n\n## Lessons\n"+''.join(f"- [{L['title']}]({SITE}/learn-by-example/{L['slug']}/): {L['intro'][:120]}\n" for L,_ in LES)+"\n## Guides\n"+''.join(f"- [{g['title']}]({SITE}/how-to-build/{g['slug']}/)\n" for g in GUIDES)+"\n## What to build\n"+''.join(f"- [{c}]({SITE}/what-to-build/{s}/)\n" for c,s,_,_ in ideas)+f"\n## Data\n- [Project catalog JSON]({SITE}/projects.json): {len(P)} projects\n- [Explorer]({SITE}/explore/)\n\n## Optional\n- [Solar AI edge nodes programme]({SITE}/edge-ai/)\n")
for f in ('favicon.svg','og.png'):
  if os.path.exists('static/'+f): shutil.copy('static/'+f,OUT+'/'+f)
open(OUT+'/CNAME','w').write(os.environ.get('SITE_CNAME','')) if os.environ.get('SITE_CNAME') else None
open(OUT+'/.nojekyll','w').write('')
shutil.copy(OUT+'/index.html',OUT+'/404.html') if not os.path.exists(OUT+'/404.html') else None
json.dump(dict(projects=len(P),lessons=len(LES),excerpts=sum(len(e) for _,e in LES),ideas=len(ideas),guides=len(GUIDES),pages=len(urls)),open(OUT+'/stats.json','w'))
print(open(OUT+'/stats.json').read())
