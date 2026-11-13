"""Core lessons: one step-by-step lesson per app that is LIVE on devnet (dapps/live.json), rendered from a reusable template.
Usage: python3 scripts/core_lessons.py [site_dir]   (runs after scripts/live_devnet.py)

* Lesson content lives in dapps/lessons/<slug>.json (schema: dapps/lessons/README.md). Every code excerpt is a reference
  (path + line range at the fork's pinned commit, or a file in this repo at a pinned commit); the text is fetched from
  GitHub and cached in dapps/lessons/excerpts.json, never typed by hand.
* Proof (signatures, rejected cases) always comes from dapps/live.json, i.e. the recorded devnet runs.
* An app that goes live without a dapps/lessons/<slug>.json still gets a lesson in the same format, built automatically
  from its live.json entry (summary, source refs, proof); it is marked as a draft until a full lesson file is written.
* Site changes: /lessons/ and /lessons/<slug>/ (canonical), the same lesson at /explore/<slug>/, /lessons/path/ (beginner
  to advanced), /lessons/glossary/, the pivoted landing (scripts/landing.py) is written last; main nav on inner pages leads with Lessons, the learning path and the glossary.
"""
import json,os,re,sys,glob,html,urllib.request
S=sys.argv[1] if len(sys.argv)>1 else 'site'; E=lambda s:html.escape(str(s),quote=True)
LIVE=json.load(open('dapps/live.json')); LV={x['slug']:x for x in LIVE}
CACHE_F='dapps/lessons/excerpts.json'; CACHE=json.load(open(CACHE_F)) if os.path.exists(CACHE_F) else {}
GLOSS=json.load(open('dapps/lessons/glossary.json')) if os.path.exists('dapps/lessons/glossary.json') else dict(terms=[])
PATH=json.load(open('dapps/lessons/path.json')) if os.path.exists('dapps/lessons/path.json') else dict(stages=[])
TERMS={t['id']:t for t in GLOSS.get('terms',[])}
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
# CSS is loaded from a sibling file written at build-authoring time, inlined below by the next chunk.
_css=os.path.join(os.path.dirname(os.path.abspath(__file__)),'lesson.css')
CSS='<style>'+(open(_css).read() if os.path.exists(_css) else '')+'</style>'
DIFF_CLASS={'Beginner':'beg','Intermediate':'int','Advanced':'adv'}
def dchip(level):
  if not level: return ''
  return f'<span class="chip {DIFF_CLASS.get(level,"")}">{E(level)}</span>'
def concept_chip(cid):
  t=TERMS.get(cid); name=t['name'] if t else cid
  return f'<a class=chip href="/lessons/glossary/#{E(cid)}">{E(name)}</a>'
_LC={}
def lesson_of(x):
  if x['slug'] not in _LC:
    f=f'dapps/lessons/{x["slug"]}.json'; _LC[x['slug']]=json.load(open(f)) if os.path.exists(f) else auto_lesson(x)
  return _LC[x['slug']]
def path_sorted(items):
  return sorted(items, key=lambda x: (lesson_of(x).get('path_order') or 1000, x.get('verified') or '', x['slug']))
PATH_LIVE=path_sorted(LIVE)
PATH_I={x['slug']:i for i,x in enumerate(PATH_LIVE)}
def functional_of(x):
  """live.json 'functional' wins; else the lesson JSON; default 'full'.
  'partial' (also 'debug' / 'incomplete') is a debug challenge, not a live environment on the path."""
  raw=x.get('functional')
  if not raw: raw=lesson_of(x).get('functional')
  v=str(raw or 'full').strip().lower()
  return 'partial' if v in ('partial','part','debug','incomplete') else 'full'
FULL=path_sorted([x for x in LIVE if functional_of(x)=='full'])
PARTIAL=path_sorted([x for x in LIVE if functional_of(x)=='partial'])
FULL_I={x['slug']:i for i,x in enumerate(FULL)}
def stage_of(L):
  sid=L.get('path_stage')
  for st in PATH.get('stages',[]):
    if st['id']==sid: return st
  return None
def render(x,L,n):
  sl=x['slug']; draft=L.get('draft')
  kind=functional_of(x)
  if kind=='full':
    seq,si,pn=FULL,FULL_I.get(sl,0),len(FULL)
  else:
    seq,si,pn=PARTIAL,next((i for i,y in enumerate(PARTIAL) if y['slug']==sl),0),len(PARTIAL)
  stg=stage_of(L)
  nav=f'<nav class=crumbs aria-label=Breadcrumb><a href="/">Home</a> / <a href="/lessons/">Lessons</a> / <a href="/lessons/path/">Path</a> / <span>{E(L["title"])}</span></nav>'
  h=[nav,CSS,'<article class=lesson>']
  eyebrow='Core lesson · live on Solana devnet'
  if kind=='partial':
    eyebrow+=' · debug challenge'
  elif pn:
    eyebrow+=f' · path step {si+1} of {pn}'
  h.append(f'<p class=eyebrow>{E(eyebrow)}</p><h1>{E(L["title"])}</h1>')
  if L.get('summary'): h.append(f'<p class=lead>{md(L["summary"])}</p>')
  if draft: h.append('<p class=note>This lesson was generated automatically when the app went live: summary, source and proof are real; the full step-by-step walkthrough is being written.</p>')
  meta=[]
  if L.get('difficulty'): meta.append(dchip(L['difficulty']))
  if L.get('time'): meta.append(f'<span>{E(L["time"])} to work through</span>')
  if stg: meta.append(f'<span>Stage {stg["id"]}: <a href="/lessons/path/#stage-{stg["id"]}">{E(stg["name"])}</a></span>')
  if meta: h.append('<p class=meta-bar>'+' · '.join(meta)+'</p>')
  if L.get('objectives') or L.get('prereqs') or L.get('concepts'):
    g=['<aside class=goals>']
    if L.get('objectives'):
      g.append('<h2 id=goals>What you will be able to do</h2><ul>'+''.join(f'<li>{md(o)}</li>' for o in L['objectives'])+'</ul>')
    if L.get('prereqs'):
      g.append('<h3>Prerequisites</h3><ul>'+''.join(f'<li>{md(p)}</li>' for p in L['prereqs'])+'</ul>')
    if L.get('concepts'):
      g.append('<h3>Concepts you will meet</h3><p>'+' '.join(concept_chip(c) for c in L['concepts'])+' · <a href="/lessons/glossary/">Glossary</a></p>')
    g.append('</aside>')
    h.append(''.join(g))
  toc='<p class=toc><a href="#goals">Objectives</a><a href="#what">1 What it does</a><a href="#try">2 Try it</a><a href="#how">3 How it works</a><a href="#key">4 Key idea</a><a href="#frontend">5 Frontend</a><a href="#proof">6 Proof</a><a href="#exercises">7 Exercises</a>'
  if L.get('build'): toc+='<a href="#build">8 Build it locally</a>'
  h.append(toc+'</p>')
  h.append(f'<h2 id=what><span class=num>1</span>What the app does</h2><p>{md(L["what"])}</p>')
  h.append(f'<p><a class=btn href="{E(x["app"])}">Open the live app (devnet)</a> <a class="btn ghost" href="{E(x["fork"])}/tree/{E(x["commit"])}">Source @ {E(x["commit"][:7])}</a></p>')
  h.append(f'<dl class=facts><dt>Program (devnet)</dt><dd><a href="{AD(x["program"])}"><code>{E(x["program"])}</code></a></dd><dt>Fork</dt><dd><a href="{E(x["fork"])}">{E(x["fork"][19:])}</a> @ <code>{E(x["commit"][:7])}</code></dd><dt>Verified</dt><dd>{E(x["verified"])} (see <a href="#proof">Proof</a>)</dd>'+(f'<dt>What we changed</dt><dd>{md(L["app_note"])}</dd>' if L.get('app_note') else '')+'</dl>')
  pre=[dict(do='Install [Phantom](https://phantom.com) (or Solflare). In Phantom open Settings → Developer Settings, turn on Testnet Mode and pick Solana Devnet.',see='The wallet shows a devnet badge. Devnet SOL is free and worthless.'),
       dict(do='Copy your wallet address and request devnet SOL at [faucet.solana.com](https://faucet.solana.com).',see='About 1 SOL arrives within a few seconds. That covers every step below.')]
  def ev(s):
    r=''.join(f'<br><span class=ran>✅ {md(a)}: <a href="{TX(g)}"><code>{E(g[:16])}…</code></a></span>' for a,g in s.get('ran',[]))
    return r+(f'<br><span class=notran>◻️ {md(s["ran_note"])}</span>' if s.get('ran_note') else '')
  st=''.join(f'<li>{md(s["do"])}'+(f'<span class=see>{md(s["see"])}</span>' if s.get('see') else '')+ev(s)+'</li>' for s in pre+L['try_steps'])
  h.append(f'<h2 id=try><span class=num>2</span>Try it yourself</h2><p>Each step says what to do and what you should see. ✅ marks a step we clicked through in the hosted app ourselves, with its devnet transaction.</p><ol class=steps>{st}</ol>')
  h.append('<h2 id=how><span class=num>3</span>How it works</h2>')
  if L.get('diagram'): h.append(f'<pre class=diagram>{E(L["diagram"])}</pre>')
  if L.get('accounts'): h.append('<table><tr><th>Account</th><th>Address (seeds)</th><th>Holds</th></tr>'+''.join('<tr>'+''.join(f'<td>{md(c)}</td>' for c in r)+'</tr>' for r in L['accounts'])+'</table>')
  for ins in L['instructions']:
    h.append(f'<section class=instr><h3>{md(ins["name"])}</h3>'+(f'<p>{md(ins["intro"])}</p>' if ins.get('intro') else '')+''.join(code(x,r) for r in ins.get('refs',[]))+(('<ol class=steps>'+''.join(f'<li>{md(s)}</li>' for s in ins['steps'])+'</ol>') if ins.get('steps') else '')+'</section>')
  k=L['innovation']; h.append(f'<h2 id=key><span class=num>4</span>The key idea{": "+E(k["title"]) if k.get("title") else ""}</h2><p>{md(k["text"])}</p>'+''.join(code(x,r) for r in k.get('refs',[]))+''.join(f'<p>{md(p)}</p>' for p in k.get('more',[])))
  h.append('<h2 id=frontend><span class=num>5</span>Frontend wiring: how the app builds and sends each transaction</h2>')
  if not L['frontend']: h.append('<p>Not written yet for this app.</p>')
  for f in L['frontend']:
    h.append(f'<section class=instr><h3>{md(f["title"])}</h3>'+''.join(code(x,r) for r in f.get('refs',[]))+(('<ol class=steps>'+''.join(f'<li>{md(s)}</li>' for s in f['steps'])+'</ol>') if f.get('steps') else '')+'</section>')
  sig=''.join(f'<li class=ok>✅ {E(a)}<br><a href="{TX(s)}"><code>{E(s)}</code></a></li>' for a,s in x['steps'])
  neg=''.join(f'<li class=bad>⛔ {E(n_)}</li>' for n_ in x.get('negative',[]))
  h.append(f'<h2 id=proof><span class=num>6</span>Proof: real devnet transactions</h2><p>Recorded on {E(x["verified"])} by <a href="https://github.com/Blockchains/sol-college/blob/main/{E(x["flow"])}"><code>{E(x["flow"])}</code></a> (<a href="https://github.com/Blockchains/sol-college/blob/main/{E(x["log"])}">log</a>) and by clicking through the hosted app. Click a signature to open it on Solana Explorer. We do not invent signatures or logs.</p><ul class=sigs>{sig}</ul><h3>Rejected, as the program should</h3><ul>{neg}</ul>'+(f'<p><b>App check:</b> {E(x["ui_check"])}</p>' if x.get('ui_check') else '')+(f'<p><b>Not covered yet:</b> {md(L["not_covered"])}</p>' if L.get('not_covered') else (f'<p><b>Not covered yet:</b> {E(x["limits"])}</p>' if x.get('limits') else '')))
  def ex_block(j,e):
    b=f'<div class=ex><h3>Exercise {j}: {md(e["title"])}</h3><ol>'+''.join(f'<li>{md(s)}</li>' for s in e['steps'])+f'</ol><p><b>Expected result:</b> {md(e["expect"])}</p>'
    if e.get('hint'): b+=f'<p class=hint>{md(e["hint"])}</p>'
    if e.get('approach'): b+=f'<details class=sol><summary>How to approach it (a reference method, not a recorded run)</summary><p>{md(e["approach"])}</p></details>'
    return b+'</div>'
  ex=''.join(ex_block(j,e) for j,e in enumerate(L['exercises'],1))
  h.append(f'<h2 id=exercises><span class=num>7</span>Exercises</h2><p>Several exercises are real bugs we found in the program and proved on devnet. Hints are visible; the reference approach is folded so you can try first. We describe a method and, where we have them, recorded results — we do not invent outputs.</p>{ex}')
  cs=L.get('commit_suggestion')
  if cs:
    h.append('<section class=instr id=commit-suggestion><h3>Worked example: a commit suggestion</h3>')
    h.append('<p>A finding is useful when it comes back as a patch the project can review: the bug, the change, a regression test, and a retest on devnet. This is one we wrote, committed to our working fork, and (where noted) opened as a pull request on the original project.</p>')
    if cs.get('finding'): h.append(f'<p><b>Finding.</b> {md(cs["finding"])}</p>')
    if cs.get('patch'): h.append(f'<p><b>Patch.</b> {md(cs["patch"])}</p>')
    h.extend(code(x,r) for r in cs.get('refs',[]))
    if cs.get('test'): h.append(f'<p><b>Regression test.</b> {md(cs["test"])}</p>')
    if cs.get('retest'):
      items=''.join((f'<li>✅ {md(a)}<br><a href="{TX(s)}"><code>{E(s)}</code></a></li>' if s else f'<li>{md(a)}</li>') for a,s in cs['retest'])
      h.append(f'<p><b>Retest on devnet.</b></p><ul class=sigs>{items}</ul>')
    links=[]
    if cs.get('fork_commit'):
      url=cs['fork_commit'] if str(cs['fork_commit']).startswith('http') else f'{x["fork"]}/commit/{cs["fork_commit"]}'
      links.append(f'<a href="{E(url)}">Fix commit on our fork</a>')
    if cs.get('upstream_pr'):
      links.append(f'<a href="{E(cs["upstream_pr"])}">Pull request on the original project</a>')
    if links: h.append('<p>'+' · '.join(links)+'</p>')
    h.append('</section>')
  if L.get('build'):
    b=L['build']; repo=x['fork'].rstrip('/').split('/')[-1]
    cmds='git clone '+x['fork']+'\ncd '+repo+'\ngit checkout '+x['commit']+'\n'
    if b.get('dir') and b['dir'] not in ('.',''): cmds+='cd '+b['dir']+'\n'
    cmds+='# This program is written for Anchor '+str(b.get('anchor','(see Cargo.toml)'))+' — use that CLI:\n'
    cmds+='#   avm use '+str(b.get('anchor','VERSION'))+'\n'
    cmds+='#   # or invoke it directly, e.g. ~/.avm/bin/anchor-'+str(b.get('anchor','VERSION'))+'\n'
    cmds+='anchor build\n'
    if b.get('test'): cmds+=b['test']+'\n'
    h.append(f'<h2 id=build><span class=num>8</span>Build it yourself locally</h2><p>These commands clone the <b>exact commit</b> this lesson is built on and compile the program. Where we have run them, we say so and quote the result. We do not claim a successful build we have not produced.</p><pre class=diagram>{E(cmds)}</pre>')
    if b.get('note'): h.append(f'<p>{md(b["note"])}</p>')
    if b.get('ran'): h.append(f'<p><b>What we ran:</b> {md(b["ran"])}</p>')
  prev=seq[si-1] if si>0 else None
  nxt=seq[si+1] if si+1<pn else None
  navb='<p>'
  if prev: navb+=f'<a class="btn ghost" href="/lessons/{E(prev["slug"])}/">← {E(lesson_of(prev)["title"])}</a> '
  next_label='Next debug challenge' if kind=='partial' else 'Next on the path'
  if nxt: navb+=f'<a class=btn href="/lessons/{E(nxt["slug"])}/">{next_label}: {E(lesson_of(nxt)["title"])}</a> '
  navb+='<a class="btn ghost" href="/lessons/path/">The learning path</a> <a class="btn ghost" href="/lessons/">All lessons</a></p></article>'
  h.append(navb)
  return ''.join(h)
# Lesson/inner pages must not use the pivoted landing as their chrome.
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import landing as _landing
_raw=open(f'{S}/index.html').read() if os.path.exists(f'{S}/index.html') else ''
home=_landing.page_shell(S) or _raw
if not home or _landing.is_landing(home):
  raise SystemExit('core_lessons: no non-landing HTML shell found; cannot wrap lesson pages')
def page(main,title,desc,path):
  t=re.sub(r'<main id=main>.*</main>',lambda _:f'<main id=main>{main}</main>',home,count=1,flags=re.S)
  t=re.sub(r'<title>.*?</title>',lambda _:f'<title>{E(title)}</title>',t,count=1)
  t=re.sub(r'<script type="application/ld\+json">.*?</script>','',t,flags=re.S)
  t=t.replace('href="https://sol.college/"',f'href="{SITE}{path}"').replace('content="https://sol.college/"',f'content="{SITE}{path}"')
  for a in ('name=description','property=og:description','name=twitter:description'): t=re.sub(f'(<meta {a} content=")[^"]*',lambda m:m.group(1)+E(desc),t,count=1)
  for a in ('property=og:title','name=twitter:title'): t=re.sub(f'(<meta {a} content=")[^"]*',lambda m:m.group(1)+E(title),t,count=1)
  return t
n=len(LIVE); cards=[]
for x in PATH_LIVE:
  L=lesson_of(x); sl=x['slug']; body=render(x,L,n)
  desc=(L.get('summary') or L['what'])[:155]
  pg=page(body,f'{L["title"]}: step-by-step Solana lesson, live on devnet | Sol.College',desc,f'/lessons/{sl}/')
  os.makedirs(f'{S}/lessons/{sl}',exist_ok=True); open(f'{S}/lessons/{sl}/index.html','w').write(pg)
  os.makedirs(f'{S}/explore/{sl}',exist_ok=True); open(f'{S}/explore/{sl}/index.html','w').write(pg)
  kind=functional_of(x)
  step=f"path {FULL_I[sl]+1}" if kind=='full' and sl in FULL_I else ('debug challenge' if kind=='partial' else (f"path {L['path_order']}" if L.get('path_order') else None))
  meta=' · '.join(filter(None,[L.get('difficulty'), L.get('time'), step]))
  chips=' '.join(concept_chip(c) for c in (L.get('concepts') or [])[:5])
  badge='<span class="chip">Debug challenge</span> ' if kind=='partial' else ''
  cards.append(f'<article class=card data-slug="{E(sl)}"><p class=meta>{badge}{dchip(L.get("difficulty",""))} {E(meta)}</p><h3><a href="/lessons/{E(sl)}/">{E(L["title"])}</a></h3><p>{md(L.get("summary") or L["what"][:200])}</p><p>{chips}</p><p><a href="/lessons/{E(sl)}/">Start the lesson</a> · <a href="{E(x["app"])}">Open the live app</a> · <a href="{AD(x["program"])}">program</a></p></article>')
def stage_blocks(with_cards=True, pool=None):
  if pool is None: pool=FULL
  out=[]
  for st in PATH.get('stages',[]):
    items=[x for x in pool if lesson_of(x).get('path_stage')==st['id']]
    if not items: continue
    mins=0
    for x in items:
      t=lesson_of(x).get('time') or ''
      m=re.search(r'(\d+)',t); mins+=int(m.group(1)) if m else 0
    lis=''
    for x in items:
      L=lesson_of(x)
      lis+=f'<li><a href="/lessons/{E(x["slug"])}/"><b>{E(L["title"])}</b></a> · {E(L.get("time") or "")} · {E(L.get("summary") or "")}</li>'
    body=f'<section class=path-stage id=stage-{st["id"]}><h2>Stage {st["id"]}: {E(st["name"])} {dchip(st["level"])} · about {mins} min</h2><p>{md(st["blurb"])}</p><ol>{lis}</ol>'
    if with_cards:
      body+='<div class=grid>'+''.join(cards[PATH_I[x['slug']]] for x in items)+'</div>'
    out.append(body+'</section>')
  return ''.join(out)
grid=f'<div class=grid>{"".join(cards)}</div>'
nf,np=len(FULL),len(PARTIAL)
intro='<p>Every lesson here is an app that is <b>running on Solana devnet right now</b>, with its own working frontend. You use it with your own wallet, then take it apart step by step: the accounts, each instruction in the real code, the one idea that makes it work, how the frontend sends each transaction, and the real transactions that prove it works, including the inputs it rejects. A <a href="/lessons/path/">learning path</a> orders the fully working environments from beginner to advanced, and a <a href="/lessons/glossary/">glossary</a> explains every concept they teach.</p>'
debug=''
if PARTIAL:
  dbg_cards=''.join(cards[PATH_I[x['slug']]] for x in PARTIAL)
  debug='<section class=path-stage id=debug-challenges><h2>Debug challenges</h2><p>These apps are on devnet, but a core flow does not complete yet (a swap that crashes, a claim that cannot pay out, a market with no redeem). Use them to practise finding the bug, writing a patch and a regression test, and retesting on devnet. They are not listed as live environments on the <a href="/lessons/path/">learning path</a> until the fork is fully working.</p><div class=grid>'+dbg_cards+'</div></section>'
lead_extra=(', plus %s <a href="#debug-challenges">debug challenges</a>' % np) if np else ''
idx=f'<nav class=crumbs aria-label=Breadcrumb><a href="/">Home</a> / <span>Lessons</span></nav><h1>Lessons: live Solana apps, step by step</h1><p class=lead>{nf} fully working live environments, ordered along the <a href="/lessons/path/">learning path</a>{lead_extra}. A new lesson appears here automatically when another app goes live on devnet.</p>{intro}{stage_blocks()}{debug}<p class=note>Looking for the 2,000+ code walkthroughs generated from source? They are in the <a href="/explore/">Source library (not yet live)</a>. They have not been built or run, so they are not lessons.</p>'
os.makedirs(f'{S}/lessons',exist_ok=True); open(f'{S}/lessons/index.html','w').write(page(idx,'Lessons: live Solana devnet apps, step by step | Sol.College',f'{nf} step-by-step Solana lessons on fully working devnet apps, plus {np} debug challenges. Real code and real transactions, ordered from beginner to advanced.','/lessons/'))
# ---- learning path page
def _mins(x):
  m=re.search(r'(\d+)',lesson_of(x).get('time') or '0'); return int(m.group(1)) if m else 0
hours=round(sum(_mins(x) for x in FULL)/60,1)
first=FULL[0] if FULL else (PATH_LIVE[0] if PATH_LIVE else LIVE[0])
debug_path=''
if PARTIAL:
  lis=''
  for x in PARTIAL:
    L=lesson_of(x); st=stage_of(L); stn=('Stage %s' % st['id']) if st else ''
    lis+=f'<li><a href="/lessons/{E(x["slug"])}/"><b>{E(L["title"])}</b></a> · {E(L.get("time") or "")} · {E(stn)} · {E(L.get("summary") or "")}</li>'
  debug_path='<section class=path-stage id=debug-challenges><h2>Debug challenges</h2><p>These apps are live on devnet but a core flow is not fully working yet. They are not counted as live environments on this path. Work them as investigation practice: find the bug, propose a patch and a regression test, then retest on devnet. When our fork is fully working, the lesson moves into the stage above.</p><ol>'+lis+'</ol></section>'
path_parts=[]
path_parts.append('<nav class=crumbs aria-label=Breadcrumb><a href="/">Home</a> / <a href="/lessons/">Lessons</a> / <span>Learning path</span></nav>')
path_parts.append(CSS)
path_parts.append('<h1>The path: become a Solana developer with live apps</h1>')
path_parts.append('<p class=lead>%s fully working live environments, ordered by the concepts they teach — not by when they went live. Each one is a real app running on Solana devnet, with a working frontend, the program\'s real code at a pinned commit, and the transactions that prove it. About %s hours of hands-on work.</p>' % (nf, hours))
path_parts.append('<p>When you finish this path you will be able to derive PDAs, move SOL and tokens with CPIs, lock funds against the on-chain clock, authorize with <code>has_one</code>, find a missing account check, and read a market, a staking program or an oracle. Every concept links to the <a href="/lessons/glossary/">glossary</a>.</p>')
path_parts.append(f'<p class=cta><a class=btn href="/lessons/{E(first["slug"])}/">Start with lesson 1: {E(lesson_of(first)["title"])}</a> <a class="btn ghost" href="/lessons/">All lessons</a></p>')
path_parts.append(stage_blocks(False))
path_parts.append(debug_path)
path_parts.append('<p class=note>Only apps whose core flow is fully working on devnet (<code>functional: full</code>) are listed as live environments in the stages above. New live apps are added to the path by concept, not by date. The <a href="/lessons/">lessons index</a> always has the full list, including debug challenges. The 2,000+ source-only walkthroughs stay in the <a href="/explore/">Source library</a> — they have not been deployed or run, so they are not on this path.</p>')
path_body='\n'.join(path_parts)
os.makedirs(f'{S}/lessons/path',exist_ok=True)
open(f'{S}/lessons/path/index.html','w').write(page(path_body,'The path: become a Solana developer with live apps | Sol.College',f'A beginner-to-advanced path through {nf} fully working Solana devnet apps: PDAs, CPIs, rent, authorization, markets and oracles, with real code and real transactions.','/lessons/path/'))
# ---- glossary, with "shown in these lessons"
shown={}
for x in PATH_LIVE:
  for c in lesson_of(x).get('concepts') or []:
    shown.setdefault(c,[]).append(x)
def gloss_item(t):
  les=shown.get(t['id'],[])
  links=' '.join(f'<a href="/lessons/{E(x["slug"])}/">{E(lesson_of(x)["title"].split(":")[0])}</a>' for x in les) or '—'
  docs=f' · <a href="{E(t["docs"])}">Official docs</a>' if t.get('docs') else ''
  return f'<dt id="{E(t["id"])}">{E(t["name"])}</dt><dd>{md(t["def"])}{docs}<br><small>Shown in: {links}</small></dd>'
g_toc=' · '.join(f'<a href="#{E(t["id"])}">{E(t["name"])}</a>' for t in GLOSS.get('terms',[]))
gloss_body=f'''<nav class=crumbs aria-label=Breadcrumb><a href="/">Home</a> / <a href="/lessons/">Lessons</a> / <span>Glossary</span></nav>
{CSS}
<h1>{E(GLOSS.get("title") or "Solana developer glossary")}</h1>
<p class=lead>{md(GLOSS.get("lead") or "")}</p>
<p class=toc>{g_toc}</p>
<dl class=gloss>{''.join(gloss_item(t) for t in GLOSS.get("terms",[]))}</dl>
<p class=note>These are the terms the <a href="/lessons/path/">core lessons</a> use. For a broader list that also covers the source library, see the site <a href="/glossary/">glossary</a>.</p>'''
os.makedirs(f'{S}/lessons/glossary',exist_ok=True)
open(f'{S}/lessons/glossary/index.html','w').write(page(gloss_body,'Solana developer glossary: PDAs, CPIs, rent, has_one and more | Sol.College','Plain-English Solana and Anchor terms — PDAs, CPIs, rent, account constraints, bonding curves — each linked to the live Sol.College lesson that shows it in real code.','/lessons/glossary/'))
# ---- homepage: owned by the landing-page worker. Do not rewrite site/index.html.
# ---- nav, footer and source-library labels on every page (skip the homepage)
NAV='<nav aria-label=Main><a href="/lessons/">Lessons</a><a href="/lessons/path/">Learning path</a><a href="/lessons/glossary/">Glossary</a><a href="/live/">Live apps</a><a href="/how-to-build/">How to build</a><a href="/explore/">Source library</a></nav>'
for fp in glob.glob(f'{S}/**/*.html',recursive=True):
  if '/dapps/' in fp or '/legacy/' in fp: continue
  if os.path.normpath(fp)==os.path.normpath(f'{S}/index.html'): continue
  t=open(fp,errors='replace').read(); o=t
  t=re.sub(r'<nav aria-label=Main>.*?</nav>',NAV,t,count=1,flags=re.S)
  t=t.replace('<a href="/explore/">Explore</a> · <a href="/learn-by-example/">Lessons</a>','<a href="/lessons/">Lessons</a> · <a href="/lessons/path/">Learning path</a> · <a href="/lessons/glossary/">Glossary</a> · <a href="/explore/">Source library</a> · <a href="/learn-by-example/">Concept walkthroughs</a>')
  m=re.match(rf'{re.escape(S)}/explore/([^/]+)/index.html$',fp)
  if m and m[1] not in LV:
    t=t.replace('<a href="/explore/">Explore</a> /','<a href="/explore/">Source library</a> /',1).replace('<p class=eyebrow>Full lesson</p>','<p class=eyebrow>Source library · not yet live · not a lesson</p>',1)
    t=re.sub(r'<!--sc-lib-->.*?<!--/sc-lib-->','',t,flags=re.S)
    t=t.replace('<main id=main>','<main id=main><!--sc-lib--><p class=note>📚 <b>Source library (not yet live).</b> A walkthrough generated from this fork&#39;s code. It has not been deployed or run, so it is not a lesson. Real lessons use apps that are live on devnet: <a href="/lessons/">see the lessons</a>.</p><!--/sc-lib-->',1)
  if fp==f'{S}/explore/index.html':
    t=t.replace('<span>Explore</span>','<span>Source library</span>',1).replace('<h1>Explore the SuperStack</h1>','<h1>Source library (not yet live)</h1><p class=note>These are code walkthroughs generated from forks in the Solana SuperStack. They have <b>not</b> been built or run, so they are reference material, not lessons. For real lessons on live devnet apps, go to <a href="/lessons/">Lessons</a> or the <a href="/lessons/path/">learning path</a>.</p>',1)
  if t!=o: open(fp,'w').write(t)
sm=f'{S}/sitemap.xml'
if os.path.exists(sm):
  t=open(sm).read(); add=''.join(f'<url><loc>{SITE}{p}</loc></url>\n' for p in ['/lessons/','/lessons/path/','/lessons/glossary/']+[f'/lessons/{x["slug"]}/' for x in LIVE] if f'<loc>{SITE}{p}</loc>' not in t)
  if add: open(sm,'w').write(t.replace('</urlset>',add+'</urlset>'))
json.dump(CACHE,open(CACHE_F,'w'),indent=0)
print('core_lessons:',[(x['slug'],('draft' if lesson_of(x).get('draft') else 'full'),functional_of(x)) for x in PATH_LIVE])
_landing.write_home(S)
_landing.enrich_lessons(S)
