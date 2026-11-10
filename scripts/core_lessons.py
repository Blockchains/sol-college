"""Core lessons: one step-by-step lesson per app that is LIVE on devnet (dapps/live.json), rendered from a reusable template.
Usage: python3 scripts/core_lessons.py [site_dir]   (runs after scripts/live_devnet.py)

* Lesson content lives in dapps/lessons/<slug>.json (schema: dapps/lessons/README.md). Every code excerpt is a reference
  (path + line range at the fork's pinned commit, or a file in this repo at a pinned commit); the text is fetched from
  GitHub and cached in dapps/lessons/excerpts.json, never typed by hand.
* Proof (signatures, rejected cases) always comes from dapps/live.json, i.e. the recorded devnet runs.
* An app that goes live without a dapps/lessons/<slug>.json still gets a lesson in the same format, built automatically
  from its live.json entry (summary, source refs, proof); it is marked as a draft until a full lesson file is written.
* Site changes: /lessons/ and /lessons/<slug>/ (canonical), the same lesson at /explore/<slug>/, homepage hero + "Core lessons"
  first, main nav leads with Lessons, and every source-only walkthrough is labelled "Source library (not yet live)"."""
import json,os,re,sys,glob,html,urllib.request
S=sys.argv[1] if len(sys.argv)>1 else 'site'; E=lambda s:html.escape(str(s),quote=True)
LIVE=json.load(open('dapps/live.json')); LV={x['slug']:x for x in LIVE}
CACHE_F='dapps/lessons/excerpts.json'; CACHE=json.load(open(CACHE_F)) if os.path.exists(CACHE_F) else {}
TX=lambda s:f'https://explorer.solana.com/tx/{s}?cluster=devnet'; AD=lambda a:f'https://explorer.solana.com/address/{a}?cluster=devnet'
SITE='https://sol.college'
def lines(repo,ref,path):
  k=f'{repo}@{ref}:{path}'
  if k not in CACHE:
    u=f'https://raw.githubusercontent.com/{repo}/{ref}/{path}'
    CACHE[k]=urllib.request.urlopen(urllib.request.Request(u,headers={'User-Agent':'sol-college'}),timeout=30).read().decode('utf-8','replace').split('\n')
  return CACHE[k]
def code(x,r):
  """r: {path, a, b, [repo, ref], [note]} -> <figure> with the real lines and a permalink."""
  repo=r.get('repo') or x['fork'][19:]; ref=r.get('ref') or x['commit']; L=lines(repo,ref,r['path']); a,b=r['a'],r['b']
  body=''.join(f'<span class=ln data-n={n}>{E(L[n-1])}</span>' for n in range(a,min(b,len(L))+1))
  url=f'https://github.com/{repo}/blob/{ref}/{r["path"]}#L{a}-L{b}'
  cap=f'<a href="{E(url)}"><code>{E(r["path"])}</code> L{a}–L{b}</a> · {E(repo)} @ <code>{E(ref[:7])}</code>'+(f' · {E(r["note"])}' if r.get('note') else '')
  return f'<figure class=excerpt><figcaption>{cap}</figcaption><pre>{body}</pre></figure>'
def md(s):
  """tiny inline markup for lesson text: `code`, **bold**, [text](url)."""
  s=E(s); s=re.sub(r'`([^`]+)`',r'<code>\1</code>',s); s=re.sub(r'\*\*(.+?)\*\*',r'<b>\1</b>',s)
  return re.sub(r'\[([^\]]+)\]\(([^)\s]+)\)',r'<a href="\2">\1</a>',s)
def auto_lesson(x):
  refs=[]
  for label,url in x.get('source',[]):
    m=re.match(r'https://github.com/([^/]+/[^/]+)/blob/([0-9a-f]{40})/(.+?)#L(\d+)(?:-L(\d+))?$',url)
    if m: refs.append(dict(repo=m[1],ref=m[2],path=m[3],a=int(m[4]),b=int(m[5] or m[4]),note=label))
  return dict(draft=True,title=x['name'],what=x['learn'],app_note=x.get('app_kind',''),
    try_steps=[dict(do=f'Open the app at [{x["app"]}]({x["app"]}) and connect a wallet set to devnet.',see='Your wallet address appears in the app.'),
               dict(do='Repeat the actions listed under Proof below, in that order, approving each transaction in your wallet.',see='Each approved transaction appears on Solana Explorer (devnet) with status Success.')],
    instructions=[dict(name=r['note'],steps=[],refs=[r]) for r in refs],
    innovation=dict(text=x['learn'],refs=refs[:1]),frontend=[],
    exercises=[dict(title='Read a proof transaction',steps=['Open the first signature under Proof on Solana Explorer (devnet).','Scroll to Instruction details and Program logs.'],expect=f'The program {x["program"]} is invoked and the transaction succeeded.')])
CSS='<style>.lesson ol.steps>li{margin:0 0 14px}.lesson .see{color:var(--mut);display:block;margin-top:4px}.lesson .see:before{content:"You should see: ";color:var(--a);font-weight:700}.lesson .toc{display:flex;flex-wrap:wrap;gap:6px 14px;font-size:14px}.lesson pre.diagram{background:#0d0c1c;border:1px solid var(--line);border-radius:12px;padding:14px 16px;white-space:pre;overflow:auto}.lesson .instr{border-left:3px solid var(--b);padding-left:16px;margin:28px 0}.lesson .ex{background:var(--panel);border:1px solid var(--line);border-radius:12px;padding:14px 18px;margin:14px 0}.lesson .ok{color:var(--a)}.lesson .bad{color:#ff7a90}.lesson .num{display:inline-block;min-width:1.8em;height:1.8em;line-height:1.8em;text-align:center;border-radius:50%;background:var(--b);color:#fff;font-weight:800;margin-right:8px}.lesson table{width:100%;border-collapse:collapse}.lesson td,.lesson th{border-bottom:1px solid var(--line);padding:8px;text-align:left;vertical-align:top}</style>'
def render(x,L,i,n):
  sl=x['slug']; draft=L.get('draft')
  nav=f'<nav class=crumbs aria-label=Breadcrumb><a href="/">Home</a> / <a href="/lessons/">Lessons</a> / <span>{E(L["title"])}</span></nav>'
  h=[nav,CSS,'<article class=lesson>',f'<p class=eyebrow>Core lesson {i} of {n} · live on Solana devnet</p><h1>{E(L["title"])}</h1>']
  if draft: h.append('<p class=note>This lesson was generated automatically when the app went live: summary, source and proof are real; the full step-by-step walkthrough is being written.</p>')
  h.append('<p class=toc><a href="#what">1 What it does</a><a href="#try">2 Try it</a><a href="#how">3 How it works</a><a href="#key">4 Key idea</a><a href="#frontend">5 Frontend</a><a href="#proof">6 Proof</a><a href="#exercises">7 Exercises</a></p>')
  # 1
  h.append(f'<h2 id=what><span class=num>1</span>What the app does</h2><p>{md(L["what"])}</p>')
  h.append(f'<p><a class=btn href="{E(x["app"])}">Open the live app (devnet)</a> <a class="btn ghost" href="{E(x["fork"])}/tree/{E(x["commit"])}">Source @ {E(x["commit"][:7])}</a></p>')
  h.append(f'<dl class=facts><dt>Program (devnet)</dt><dd><a href="{AD(x["program"])}"><code>{E(x["program"])}</code></a></dd><dt>Fork</dt><dd><a href="{E(x["fork"])}">{E(x["fork"][19:])}</a> @ <code>{E(x["commit"][:7])}</code></dd><dt>Verified</dt><dd>{E(x["verified"])} (see <a href="#proof">Proof</a>)</dd>'+(f'<dt>What we changed</dt><dd>{md(L["app_note"])}</dd>' if L.get('app_note') else '')+'</dl>')
  # 2
  pre=[dict(do='Install [Phantom](https://phantom.com) (or Solflare). In Phantom open Settings → Developer Settings, turn on Testnet Mode and pick Solana Devnet.',see='The wallet shows a devnet badge. Devnet SOL is free and worthless.'),
       dict(do=f'Copy your wallet address and request devnet SOL at [faucet.solana.com](https://faucet.solana.com).',see='About 1 SOL arrives within a few seconds. That covers every step below.')]
  st=''.join(f'<li>{md(s["do"])}'+(f'<span class=see>{md(s["see"])}</span>' if s.get('see') else '')+'</li>' for s in pre+L['try_steps'])
  h.append(f'<h2 id=try><span class=num>2</span>Try it yourself</h2><ol class=steps>{st}</ol>')
  # 3
  h.append('<h2 id=how><span class=num>3</span>How it works</h2>')
  if L.get('diagram'): h.append(f'<pre class=diagram>{E(L["diagram"])}</pre>')
  if L.get('accounts'): h.append('<table><tr><th>Account</th><th>Address (seeds)</th><th>Holds</th></tr>'+''.join('<tr>'+''.join(f'<td>{md(c)}</td>' for c in r)+'</tr>' for r in L['accounts'])+'</table>')
  for ins in L['instructions']:
    h.append(f'<section class=instr><h3>{md(ins["name"])}</h3>'+(f'<p>{md(ins["intro"])}</p>' if ins.get('intro') else '')+''.join(code(x,r) for r in ins.get('refs',[]))+(('<ol class=steps>'+''.join(f'<li>{md(s)}</li>' for s in ins['steps'])+'</ol>') if ins.get('steps') else '')+'</section>')
  # 4
  k=L['innovation']; h.append(f'<h2 id=key><span class=num>4</span>The key idea{": "+E(k["title"]) if k.get("title") else ""}</h2><p>{md(k["text"])}</p>'+''.join(code(x,r) for r in k.get('refs',[]))+''.join(f'<p>{md(p)}</p>' for p in k.get('more',[])))
  # 5
  h.append('<h2 id=frontend><span class=num>5</span>Frontend wiring: how the app builds and sends each transaction</h2>')
  if not L['frontend']: h.append('<p>Not written yet for this app.</p>')
  for f in L['frontend']:
    h.append(f'<section class=instr><h3>{md(f["title"])}</h3>'+''.join(code(x,r) for r in f.get('refs',[]))+(('<ol class=steps>'+''.join(f'<li>{md(s)}</li>' for s in f['steps'])+'</ol>') if f.get('steps') else '')+'</section>')
  # 6
  sig=''.join(f'<li class=ok>✅ {E(a)}<br><a href="{TX(s)}"><code>{E(s)}</code></a></li>' for a,s in x['steps'])
  neg=''.join(f'<li class=bad>⛔ {E(n_)}</li>' for n_ in x.get('negative',[]))
  h.append(f'<h2 id=proof><span class=num>6</span>Proof: real devnet transactions</h2><p>Recorded on {E(x["verified"])} by <a href="https://github.com/Blockchains/sol-college/blob/main/{E(x["flow"])}"><code>{E(x["flow"])}</code></a> (<a href="https://github.com/Blockchains/sol-college/blob/main/{E(x["log"])}">log</a>) and by clicking through the hosted app. Click a signature to open it on Solana Explorer.</p><ul class=sigs>{sig}</ul><h3>Rejected, as the program should</h3><ul>{neg}</ul>'+(f'<p><b>App check:</b> {E(x["ui_check"])}</p>' if x.get('ui_check') else '')+(f'<p><b>Not covered yet:</b> {E(x["limits"])}</p>' if x.get('limits') else ''))
  # 7
  ex=''.join(f'<div class=ex><h3>Exercise {j}: {md(e["title"])}</h3><ol>'+''.join(f'<li>{md(s)}</li>' for s in e['steps'])+f'</ol><p><b>Expected result:</b> {md(e["expect"])}</p></div>' for j,e in enumerate(L['exercises'],1))
  h.append(f'<h2 id=exercises><span class=num>7</span>Exercises</h2>{ex}')
  nxt=[y for y in LIVE if y['slug']!=sl]
  h.append('<p>'+(f'<a class=btn href="/lessons/{E(LIVE[i % n]["slug"])}/">Next lesson: {E(lesson_of(LIVE[i % n])["title"])}</a> ' if n>1 else '')+'<a class="btn ghost" href="/lessons/">All lessons</a></p></article>')
  return ''.join(h)
_LC={}
def lesson_of(x):
  if x['slug'] not in _LC:
    f=f'dapps/lessons/{x["slug"]}.json'; _LC[x['slug']]=json.load(open(f)) if os.path.exists(f) else auto_lesson(x)
  return _LC[x['slug']]
home=open(f'{S}/index.html').read()
def page(main,title,desc,path):
  t=re.sub(r'<main id=main>.*</main>',lambda _:f'<main id=main>{main}</main>',home,count=1,flags=re.S)
  t=re.sub(r'<title>.*?</title>',lambda _:f'<title>{E(title)}</title>',t,count=1)
  t=re.sub(r'<script type="application/ld\+json">.*?</script>','',t,flags=re.S)
  t=t.replace('href="https://sol.college/"',f'href="{SITE}{path}"').replace('content="https://sol.college/"',f'content="{SITE}{path}"')
  for a in ('name=description','property=og:description','name=twitter:description'): t=re.sub(f'(<meta {a} content=")[^"]*',lambda m:m.group(1)+E(desc),t,count=1)
  for a in ('property=og:title','name=twitter:title'): t=re.sub(f'(<meta {a} content=")[^"]*',lambda m:m.group(1)+E(title),t,count=1)
  return t
n=len(LIVE); cards=[]
for i,x in enumerate(LIVE,1):
  L=lesson_of(x); sl=x['slug']; body=render(x,L,i,n)
  desc=(L.get('summary') or L['what'])[:155]
  pg=page(body,f'{L["title"]}: step-by-step Solana lesson, live on devnet | Sol.College',desc,f'/lessons/{sl}/')
  os.makedirs(f'{S}/lessons/{sl}',exist_ok=True); open(f'{S}/lessons/{sl}/index.html','w').write(pg)
  os.makedirs(f'{S}/explore/{sl}',exist_ok=True); open(f'{S}/explore/{sl}/index.html','w').write(pg)  # old URL: same lesson, canonical is /lessons/<slug>/
  cards.append(f'<article class=card><p class=meta>Lesson {i} · live on devnet</p><h3><a href="/lessons/{E(sl)}/">{E(L["title"])}</a></h3><p>{md(L.get("summary") or L["what"][:200])}</p><p><a href="/lessons/{E(sl)}/">Start the lesson</a> · <a href="{E(x["app"])}">Open the live app</a> · <a href="{AD(x["program"])}">program</a></p></article>')
grid=f'<div class=grid>{"".join(cards)}</div>'
intro='<p>Every lesson here is an app that is <b>running on Solana devnet right now</b>, with its own working frontend. You use it with your own wallet, then take it apart step by step: the accounts, each instruction in the real code, the one idea that makes it work, how the frontend sends each transaction, and the real transactions that prove it works, including the inputs it rejects.</p>'
idx=f'<nav class=crumbs aria-label=Breadcrumb><a href="/">Home</a> / <span>Lessons</span></nav><h1>Lessons: live Solana apps, step by step</h1><p class=lead>{n} core lessons. A new lesson appears here automatically when another app goes live on devnet.</p>{intro}{grid}<p class=note>Looking for the 2,000+ code walkthroughs generated from source? They are in the <a href="/explore/">Source library (not yet live)</a>. They have not been built or run, so they are not lessons.</p>'
os.makedirs(f'{S}/lessons',exist_ok=True); open(f'{S}/lessons/index.html','w').write(page(idx,'Lessons: live Solana devnet apps, step by step | Sol.College',f'{n} step-by-step Solana lessons, each built on an app that is live on devnet with a working frontend, real code and real transactions.','/lessons/'))
# ---- homepage: hero + core lessons first, live section folded into it, source material relabelled
hero=f'<section class=hero><p class=eyebrow>Learn Solana from live apps</p><h1>Use a <em>live</em> Solana app. Then take it apart.</h1><p class=lead>Each lesson is a real app running on Solana devnet with a working frontend. Connect a devnet wallet, use it, then follow the code step by step, with the transactions that prove it works.</p><p class=cta><a class=btn href="/lessons/{E(LIVE[0]["slug"])}/">Start lesson 1</a> <a class="btn ghost" href="/lessons/">All {n} lessons</a> <a class="btn ghost" href="/explore/">Source library (not yet live)</a></p></section>'
H=re.sub(r'<section class=hero>.*?</section>',lambda _:hero,home,count=1,flags=re.S)
H=re.sub(r'<!--sc-live-->.*?<!--/sc-live-->','',H,flags=re.S)
core=f'<!--sc-core--><section id=lessons><h2>Core lessons: live on devnet</h2>{intro}{grid}<p><a class=btn href="/lessons/">All lessons</a> <a class="btn ghost" href="/live/">Proof for every live app</a></p></section><!--/sc-core-->'
H=re.sub(r'<!--sc-core-->.*?<!--/sc-core-->','',H,flags=re.S).replace('</section>','</section>'+core,1)
H=H.replace('<section><h2>Lessons</h2>','<section><h2>Source library: concept walkthroughs</h2><p class=note>Annotated excerpts from source code, not live apps. Start with the <a href="/lessons/">core lessons</a>.</p>',1)
open(f'{S}/index.html','w').write(H)
# ---- nav, footer and source-library labels on every page
NAV='<nav aria-label=Main><a href="/lessons/">Lessons</a><a href="/live/">Live apps</a><a href="/learn-solana/">Learn Solana</a><a href="/how-to-build/">How to build</a><a href="/explore/">Source library</a></nav>'
for fp in glob.glob(f'{S}/**/*.html',recursive=True):
  if '/dapps/' in fp or '/legacy/' in fp: continue
  t=open(fp,errors='replace').read(); o=t
  t=re.sub(r'<nav aria-label=Main>.*?</nav>',NAV,t,count=1,flags=re.S)
  t=t.replace('<a href="/explore/">Explore</a> · <a href="/learn-by-example/">Lessons</a>','<a href="/lessons/">Lessons</a> · <a href="/explore/">Source library</a> · <a href="/learn-by-example/">Concept walkthroughs</a>')
  m=re.match(rf'{re.escape(S)}/explore/([^/]+)/index.html$',fp)
  if m and m[1] not in LV:
    t=t.replace('<a href="/explore/">Explore</a> /','<a href="/explore/">Source library</a> /',1).replace('<p class=eyebrow>Full lesson</p>','<p class=eyebrow>Source library · not yet live · not a lesson</p>',1)
    t=re.sub(r'<!--sc-lib-->.*?<!--/sc-lib-->','',t,flags=re.S)
    t=t.replace('<main id=main>','<main id=main><!--sc-lib--><p class=note>📚 <b>Source library (not yet live).</b> A walkthrough generated from this fork&#39;s code. It has not been deployed or run, so it is not a lesson. Real lessons use apps that are live on devnet: <a href="/lessons/">see the lessons</a>.</p><!--/sc-lib-->',1)
  if fp==f'{S}/explore/index.html':
    t=t.replace('<span>Explore</span>','<span>Source library</span>',1).replace('<h1>Explore the SuperStack</h1>','<h1>Source library (not yet live)</h1><p class=note>These are code walkthroughs generated from forks in the Solana SuperStack. They have <b>not</b> been deployed or run, so they are reference material, not lessons. For real lessons on live devnet apps, go to <a href="/lessons/">Lessons</a>.</p>',1)
  if t!=o: open(fp,'w').write(t)
sm=f'{S}/sitemap.xml'
if os.path.exists(sm):
  t=open(sm).read(); add=''.join(f'<url><loc>{SITE}{p}</loc></url>\n' for p in ['/lessons/']+[f'/lessons/{x["slug"]}/' for x in LIVE] if f'<loc>{SITE}{p}</loc>' not in t)
  if add: open(sm,'w').write(t.replace('</urlset>',add+'</urlset>'))
json.dump(CACHE,open(CACHE_F,'w'),indent=0)
print('core_lessons:',[(x['slug'],'draft' if lesson_of(x).get('draft') else 'full') for x in LIVE])
