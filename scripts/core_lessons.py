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
_BLOB=re.compile(r'^https://github.com/([^/]+/[^/]+)/blob/([0-9a-f]{7,40})/(.+?)(?:#L(\d+)(?:-L(\d+))?)?$')
def ref_of(r):
  """A code reference is either {path,a,b} or [github blob url, note] from a newer lesson file."""
  if isinstance(r,dict) and r.get('path') and r.get('a'): return r
  url=note=''
  if isinstance(r,(list,tuple)) and r:
    url,note=str(r[0]),(str(r[1]) if len(r)>1 else '')
  elif isinstance(r,str) and r.startswith('http'): url=r
  elif isinstance(r,dict):
    url,note=str(r.get('url') or ''),str(r.get('note') or '')
  else: return None
  m=_BLOB.match(url)
  if not m: return dict(url=url,note=note)
  d=dict(repo=m[1],ref=m[2],path=m[3],note=note,url=url)
  if m[4]: d['a'],d['b']=int(m[4]),int(m[5] or m[4])
  return d
def lines(repo,ref,path):
  k=f'{repo}@{ref}:{path}'
  if k not in CACHE:
    u=f'https://raw.githubusercontent.com/{repo}/{ref}/{path}'
    CACHE[k]=urllib.request.urlopen(urllib.request.Request(u,headers={'User-Agent':'sol-college'}),timeout=30).read().decode('utf-8','replace').split('\n')
  return CACHE[k]
def code(x,r):
  """r: {path, a, b, [repo, ref], [note]} or [blob url, note] -> <figure> with the real lines and a permalink."""
  r=ref_of(r)
  if not r: return ''
  if not r.get('a') or not r.get('path'):
    url=r.get('url') or ''
    label=r.get('note') or r.get('path') or url
    return f'<p><a href="{E(url)}"><code>{E(label)}</code></a></p>' if url else ''
  repo=r.get('repo') or x['fork'][19:]; ref=r.get('ref') or x['commit']; a,b=r['a'],r['b']
  try: L=lines(repo,ref,r['path'])
  except Exception:
    url=r.get('url') or f'https://github.com/{repo}/blob/{ref}/{r["path"]}#L{a}-L{b}'
    return f'<p><a href="{E(url)}"><code>{E(r["path"])} L{a}–L{b}</code></a></p>'
  # Newlines between spans keep plain-text extraction readable; CSS still stacks .ln as blocks.
  body='\n'.join(f'<span class=ln data-n={n}>{E(L[n-1])}</span>' for n in range(a,min(b,len(L))+1) if 1<=n<=len(L))
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
# CSS and the lesson reader script are inlined so the paused Pages pipeline
# (which runs this file, not build.py) ships the reading UI.
_here=os.path.dirname(os.path.abspath(__file__))
_css=os.path.join(_here,'lesson.css')
_js=os.path.join(_here,'lesson.js')
_notice=os.path.join(_here,'release-notice.js')
CSS='<style>'+(open(_css).read() if os.path.exists(_css) else '')+'</style>'
if os.path.exists(_js):
  CSS+='<script>'+open(_js).read()+'</script>'
if os.path.exists(_notice):
  CSS+='<script>'+open(_notice).read()+'</script>'
DIFF_CLASS={'Beginner':'beg','Intermediate':'int','Advanced':'adv'}
def canon_diff(level):
  s=str(level or '').strip()
  return {'beginner':'Beginner','intermediate':'Intermediate','advanced':'Advanced'}.get(s.lower(), s)
def dchip(level):
  level=canon_diff(level)
  if not level: return ''
  return f'<span class="chip {DIFF_CLASS.get(level,"")}">{E(level)}</span>'
def concept_chip(cid):
  t=TERMS.get(cid); name=t['name'] if t else cid
  return f'<a class=chip href="/lessons/glossary/#{E(cid)}">{E(name)}</a>'
def ran_pairs(ran):
  """Recorded runs are either [label, signature] pairs or a prose note from a newer lesson file.
  A note is not a transaction, so it is not turned into an Explorer link."""
  if not ran: return []
  if isinstance(ran,str): return [(ran,'')]
  out=[]
  for item in ran if isinstance(ran,list) else []:
    if isinstance(item,str): out.append((item,''))
    elif isinstance(item,(list,tuple)):
      if len(item)>=2: out.append((str(item[0]),str(item[1] or '')))
      elif len(item)==1: out.append((str(item[0]),''))
    elif isinstance(item,dict):
      out.append((str(item.get('do') or item.get('label') or ''), str(item.get('sig') or item.get('signature') or '')))
  return out
def _row(r):
  if isinstance(r,str): return [r,'','']
  if isinstance(r,(list,tuple)):
    cells=[str(c) for c in r]
    return cells if len(cells)>=3 else cells+['']*(3-len(cells))
  return [str(r),'','']
def normalize(L):
  """Accept both the full lesson schema and the shorter files written for newer devnet apps."""
  L=dict(L)
  ins=L.get('instructions') or []
  if isinstance(ins,str): ins=[ins]
  L['instructions']=[i if isinstance(i,dict) else dict(name=str(i),steps=[],refs=[]) for i in ins]
  acc=L.get('accounts') or []
  if isinstance(acc,str): acc=[acc]
  L['accounts']=[_row(r) for r in acc] if isinstance(acc,list) else []
  inn=L.get('innovation')
  if isinstance(inn,str): L['innovation']=dict(text=inn,refs=[])
  elif not isinstance(inn,dict): L['innovation']=dict(text='',refs=[])
  fe=L.get('frontend')
  if isinstance(fe,str): L['frontend']=[dict(title='Frontend',steps=[fe],refs=[])] if fe else []
  elif not isinstance(fe,list): L['frontend']=[]
  else: L['frontend']=[f if isinstance(f,dict) else dict(title=str(f),steps=[],refs=[]) for f in fe]
  ex=L.get('exercises') or []
  if isinstance(ex,str): ex=[ex]
  nex=[]
  for e in ex if isinstance(ex,list) else []:
    if isinstance(e,str): nex.append(dict(title=e,steps=[],expect='Use the recorded devnet transactions on this page. This exercise does not add a result that was not recorded.'))
    elif isinstance(e,dict):
      e=dict(e); e.setdefault('title','Exercise'); e.setdefault('steps',[]); e.setdefault('expect','')
      nex.append(e)
  L['exercises']=nex
  steps=L.get('try_steps') or []
  L['try_steps']=[s if isinstance(s,dict) else dict(do=str(s)) for s in steps] if isinstance(steps,list) else []
  L.setdefault('what', L.get('summary') or '')
  L.setdefault('title','')
  b=L.get('build')
  if isinstance(b,str): L['build']=dict(note=b)
  elif b is not None and not isinstance(b,dict): L['build']=None
  cs=L.get('commit_suggestion')
  if isinstance(cs,str): L['commit_suggestion']=dict(finding=cs)
  elif cs is not None and not isinstance(cs,dict): L['commit_suggestion']=None
  return L
_LC={}
def lesson_of(x):
  if x['slug'] not in _LC:
    f=f'dapps/lessons/{x["slug"]}.json'; raw=json.load(open(f)) if os.path.exists(f) else auto_lesson(x)
    _LC[x['slug']]=normalize(raw)
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
def readiness(x):
  """Walkthrough readiness is not the same as the app being deployed.
  preview: no written lesson yet. challenge: a named core flow does not complete.
  guided: a written walkthrough of an app whose recorded core flows completed."""
  if lesson_of(x).get('draft'): return 'preview'
  if functional_of(x)=='partial': return 'challenge'
  return 'guided'
READY_LABEL={'guided':'Guided lesson','challenge':'Debug challenge','preview':'Project preview'}
READY_NOTE={
  'guided':'A written walkthrough. The recorded core flows completed on the verification date below. Known limits stay listed on the card and lesson.',
  'challenge':'The app is on devnet, but a named core flow does not complete. It is investigation practice, not a guided “core flows completed” environment.',
  'preview':'The app is on devnet. This page was generated from the deployment record. The full walkthrough is still being written.',
}
def task_html(s):
  s=E(re.sub(r'\[([^\]]+)\]\([^)]+\)', r'\1', str(s or '')))
  return re.sub(r'`([^`]+)`', r'<code>\1</code>', s)
def one_line(text, n=160):
  t=' '.join(str(text or '').split())
  if not t or len(t)<=n: return t
  return t[:n].rsplit(' ',1)[0]+'…'
import curriculum_copy as _cc
format_limit_text = _cc.format_limit_text


def format_prereq(p):
  """Resolve lesson-slug prerequisites to titled links; leave prose alone."""
  def resolve(slug):
    if slug not in LV:
      return None
    title = lesson_of(LV[slug]).get('title') or slug
    short = title.split(':')[0].strip()
    return f'[{short}](/lessons/{slug}/)'
  return _cc.format_prereq(p, resolve)


def limit_of(x):
  raw = lesson_of(x).get('not_covered') or x.get('limits') or ''
  return format_limit_text(raw)
def render(x,L,n):
  sl=x['slug']
  ready=readiness(x)
  seq=[y for y in PATH_LIVE if readiness(y)==ready]
  si=next(i for i,y in enumerate(seq) if y['slug']==sl)
  pn=len(seq)
  stg=stage_of(L)
  nav=f'<nav class=crumbs aria-label=Breadcrumb><a href="/">Home</a> / <a href="/lessons/">Lessons</a> / <a href="/lessons/path/">Path</a> / <span>{E(L["title"])}</span></nav>'
  sections=[]
  assess_href=f'/lessons/{sl}/assessment/' if (L.get('learning_loop') or L.get('assessment')) else ''
  if L.get('learning_loop'):
    sections+=[('preflight','Preflight'),('workspace','Workspace'),('stuck','Stuck')]
  if L.get('objectives') or L.get('prereqs') or L.get('concepts'): sections.append(('goals','What you will practise'))
  sections+=[('try','Guided lesson'),('how','Explanation'),('proof','Evidence'),('exercises','Exercises')]
  if L.get('build'): sections.append(('build','Build lab'))
  rail_links=''.join(f'<a href="#{i}">{E(name)}</a>' for i,name in sections)
  if assess_href:
    rail_links+=f'<a href="{E(assess_href)}">Rubric</a>'
  rail='<nav class=rail aria-label="On this page">'+rail_links+'</nav>'
  h=[CSS,'<div class=readbar aria-hidden=true><span></span></div>',f'<article class=lesson data-slug="{E(sl)}">','<div class=lesson-layout><div class=lesson-main>',nav]
  eyebrow=READY_LABEL[ready]+' · live on Solana devnet'
  # Path position only for lessons inside numbered stages 1–3. Catalogue extras must not look like path steps.
  if stg and isinstance(stg.get('id'), int) and L.get('path_order'):
    staged=[]
    for y in PATH_LIVE:
      so=stage_of(lesson_of(y))
      if so and so.get('id')==stg['id']:
        staged.append(y)
    if len(staged)>1:
      try:
        local=next(i for i,y in enumerate(staged) if y['slug']==sl)+1
        eyebrow+=f' · stage {stg["id"]}, step {local} of {len(staged)} (path {L["path_order"]})'
      except StopIteration:
        pass
  elif ready=='guided' and not stg:
    eyebrow+=' · catalogue lesson (not a numbered path step)'
  h.append(f'<p class="eyebrow status-{ready}">{E(eyebrow)}</p><h1>{E(L["title"])}</h1>')
  if L.get('summary'): h.append(f'<p class=lead>{md(L["summary"])}</p>')
  h.append(f'<p class="status status-{ready}">{E(READY_NOTE[ready])}</p>')
  lim=limit_of(x)
  if lim: h.append(f'<p class=limit><b>Known limit, before you start.</b> {md(lim)}</p>')
  h.append('<!--sc-article-->')
  meta=[]
  if L.get('difficulty'): meta.append(dchip(L['difficulty']))
  if L.get('time'): meta.append(f'<span>{E(L["time"])} recorded</span>')
  if x.get('verified'): meta.append(f'<span>Verified {E(x["verified"])}</span>')
  if stg: meta.append(f'<span>Stage {stg["id"]}: <a href="/lessons/path/#stage-{stg["id"]}">{E(stg["name"])}</a></span>')
  if meta: h.append('<p class=meta-bar>'+' · '.join(meta)+'</p>')
  # Layer map: keep the primary learner flow short; later sections are optional depth.
  layer_bits=[
    ('#try','Guided lesson'),
    ('#how','Technical explanation'),
    ('#proof','Evidence'),
  ]
  if L.get('build'): layer_bits.append(('#build','Build laboratory'))
  layer_bits.append(('#exercises','Exercises'))
  if assess_href:
    layer_bits.append((assess_href,'Assessment rubric'))
  h.append(
    '<nav class=layers aria-label="Lesson layers">'
    +''.join(f'<a href="{href}">{E(label)}</a>' for href,label in layer_bits)
    +'</nav>'
    '<p class=note>Start with <b>Try it</b> or the workspace. Technical explanation, evidence, build steps, and exercises are linked layers — you do not need to absorb them all at once. The assessment rubric is separate from exercise ticks.</p>'
  )
  dock=f'<div class=dock role=region aria-label="Lesson actions"><a class=btn href="{E(x["app"])}">Open the app</a><button type=button class="btn ghost" data-jump>Next section</button>'
  # next lesson is filled in after seq is known; placeholder replaced below
  h.append('<!--dock-->')
  if L.get('objectives') or L.get('prereqs') or L.get('concepts'):
    g=['<aside class=goals>']
    if L.get('student_outcome'):
      g.append(f'<p class=lead><b>You will:</b> {md(L["student_outcome"])}</p>')
    if L.get('objectives'):
      g.append('<h2 id=goals>What you will practise</h2><ul>'+''.join(f'<li>{md(o)}</li>' for o in L['objectives'])+'</ul>')
      g.append('<p class=note>Completing the reading alone does not by itself demonstrate these abilities. Exercises and recorded evidence are where you show understanding.</p>')
    if L.get('prereqs'):
      g.append('<h3>Prerequisites</h3><ul>'+''.join(f'<li>{md(format_prereq(p))}</li>' for p in L['prereqs'])+'</ul>')
    if L.get('concepts'):
      g.append('<h3>Concepts you will meet</h3><p>'+' '.join(concept_chip(c) for c in L['concepts'])+' · <a href="/lessons/glossary/">Glossary</a></p>')
    if L.get('delivery'):
      g.append(f'<p class=meta>Delivery: {E(L["delivery"])}</p>')
    g.append('</aside>')
    h.append(''.join(g))
  import learning_layer as _ll
  if L.get('learning_loop'):
    h.append(_ll.preflight_html(x['app'], L.get('student_outcome') or L.get('title') or 'this lab'))
    h.append(_ll.environment_panel_html(x.get('verified') or '', x.get('ui_check') or ''))
    sigs = list(x.get('steps') or [])
    is_debug = (L.get('track') == 'debug-laboratory') or (ready == 'challenge')
    ws_kwargs = dict(
      content_version=str(L.get('content_version') or ''),
      assess_href=assess_href,
    )
    if is_debug:
      ws_kwargs.update(
        eyebrow='Debug laboratory workspace',
        prepare_note=(
          'Complete <a href="#preflight">preflight</a>. Prefer observation of recorded proofs. '
          'Diagnose the documented gap — do not claim an unproven production fix. Then continue to Predict.'
        ),
        act_cta_label='Open the live app (observe carefully)',
      )
    h.append(_ll.workspace_html(
      L['learning_loop'], x['app'], sigs,
      **ws_kwargs,
    ))
    _mis = (L.get('assessment') or {}).get('criteria') or []
    h.append(_ll.stuck_html(_mis))
    h.append('<p class=note id=reference-layers>Reference layers below stay available. The workspace above is the focused student path.</p>')
  h.append(f'<h2 id=what><span class=num>1</span>What the app does</h2><p>{md(L["what"])}</p>')
  h.append(f'<p><a class=btn href="{E(x["app"])}">Open the live app (devnet)</a> <a class="btn ghost" href="{E(x["fork"])}/tree/{E(x["commit"])}">Source @ {E(x["commit"][:7])}</a></p>')
  h.append(f'<dl class=facts><dt>Program (devnet)</dt><dd><a href="{AD(x["program"])}"><code>{E(x["program"])}</code></a></dd><dt>Fork</dt><dd><a href="{E(x["fork"])}">{E(x["fork"][19:])}</a> @ <code>{E(x["commit"][:7])}</code></dd><dt>Verified</dt><dd>{E(x["verified"])} (see <a href="#proof">Proof</a>)</dd>'+(f'<dt>What we changed</dt><dd>{md(L["app_note"])}</dd>' if L.get('app_note') else '')+'</dl>')
  # Wallet/faucet stay in preflight for loop lessons; keep them in try steps for others.
  if L.get('learning_loop'):
    pre=[]
  else:
    pre=[dict(do='Install [Phantom](https://phantom.com) (or Solflare). In Phantom open Settings → Developer Settings, turn on Testnet Mode and pick Solana Devnet.',see='The wallet shows a devnet badge. Devnet SOL is free and worthless.'),
         dict(do='Copy your wallet address and request enough practice funds at [faucet.solana.com](https://faucet.solana.com) for the estimated costs shown in this lesson.',see='Faucet availability, limits, and timing vary. If funding is unavailable, save your progress or use the observation route (read accounts and recorded proofs without sending a transaction). Do not treat faucet access as a graded requirement.')]
  def ev(s):
    bits=[]
    for a,g in ran_pairs(s.get('ran')):
      if g: bits.append(f'<br><span class=ran>✅ {md(a)}: <a href="{TX(g)}"><code>{E(g[:16])}…</code></a></span>')
      else: bits.append(f'<br><span class=ran>✅ {md(a)}</span>')
    r=''.join(bits)
    return r+(f'<br><span class=notran>◻️ {md(s["ran_note"])}</span>' if s.get('ran_note') else '')
  steps_all=pre+L['try_steps']
  st=''.join(
    '<li class=step><label class=step-check>'
    f'<input type=checkbox data-step="{i}" aria-label="Mark step {i+1} done">'
    f'<span>{md(s["do"])}</span></label>'
    +(f'<span class=see>{md(s["see"])}</span>' if s.get('see') else '')
    +ev(s)+'</li>'
    for i,s in enumerate(steps_all))
  h.append(f'<h2 id=try><span class=num>2</span>Try it yourself</h2><p>This is the guided lesson. Check a step when you have done it. This browser remembers the ticks for this lesson. ✅ marks a step we clicked through in the hosted app ourselves, with its devnet transaction.</p><p class=meta id=step-status></p><ol class=steps>{st}</ol>')
  h.append('<div class=layer-block id=explain-layer>')
  h.append('<p class="eyebrow">Technical explanation</p>')
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
  h.append('</div>')
  sig=''.join(f'<li class=ok>✅ {E(a)}<br><a href="{TX(s)}"><code>{E(s)}</code></a></li>' for a,s in x['steps'])
  neg=''.join(f'<li class=bad>⛔ {E(n_)}</li>' for n_ in x.get('negative',[]))
  proof_limit = format_limit_text(L.get('not_covered') or x.get('limits') or '')
  h.append('<p class="eyebrow">Evidence record</p>')
  h.append(f'<h2 id=proof><span class=num>6</span>Proof: real devnet transactions</h2><p>Recorded on {E(x["verified"])} by <a href="https://github.com/Blockchains/sol-college/blob/main/{E(x["flow"])}"><code>{E(x["flow"])}</code></a> (<a href="https://github.com/Blockchains/sol-college/blob/main/{E(x["log"])}">log</a>) and by clicking through the hosted app. Click a signature to open it on Solana Explorer. We do not invent signatures or logs.</p><ul class=sigs>{sig}</ul><h3>Rejected, as the program should</h3><ul>{neg}</ul>'+(f'<p><b>App check:</b> {E(x["ui_check"])}</p>' if x.get('ui_check') else '')+(f'<p><b>Not covered yet:</b> {md(proof_limit)}</p>' if proof_limit else ''))
  def ex_block(j,e):
    b=f'<div class=ex><h3>Exercise {j}: {md(e["title"])}</h3><ol>'+''.join(f'<li>{md(s)}</li>' for s in e['steps'])+f'</ol><p><b>Expected result:</b> {md(e["expect"])}</p>'
    if e.get('hint'): b+=f'<p class=hint>{md(e["hint"])}</p>'
    if e.get('approach'): b+=f'<details class=sol><summary>How to approach it (a reference method, not a recorded run)</summary><p>{md(e["approach"])}</p></details>'
    return b+'</div>'
  ex=''.join(ex_block(j,e) for j,e in enumerate(L['exercises'],1))
  h.append('<p class="eyebrow">Assessment</p>')
  h.append(f'<h2 id=exercises><span class=num>7</span>Exercises</h2><p>Several exercises are real bugs we found in the program and proved on devnet. Hints are visible; the reference approach is folded so you can try first. We describe a method and, where we have them, recorded results — we do not invent outputs. Completing an exercise is where you demonstrate understanding.</p>{ex}')
  cs=L.get('commit_suggestion')
  if cs:
    h.append('<section class=instr id=commit-suggestion><h3>Worked example: a commit suggestion</h3>')
    h.append('<p>A finding is useful when it comes back as a patch the project can review: the bug, the change, a regression test, and a retest on devnet. This is one we wrote, committed to our working fork, and (where noted) opened as a pull request on the original project. Suitable investigations can develop into tests, patches, or upstream contributions — not every exercise must become a patch.</p>')
    if cs.get('finding'): h.append(f'<p><b>Finding.</b> {md(cs["finding"])}</p>')
    if cs.get('patch'): h.append(f'<p><b>Patch.</b> {md(cs["patch"])}</p>')
    h.extend(code(x,r) for r in cs.get('refs',[]))
    if cs.get('test'): h.append(f'<p><b>Regression test.</b> {md(cs["test"])}</p>')
    if cs.get('retest'):
      items=''.join((f'<li>✅ {md(a)}<br><a href="{TX(s)}"><code>{E(s)}</code></a></li>' if s else f'<li>{md(a)}</li>') for a,s in ran_pairs(cs['retest']))
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
    h.append('<p class="eyebrow">Build laboratory</p>')
    h.append(f'<h2 id=build><span class=num>8</span>Build it yourself locally</h2><p>These commands clone the <b>exact commit</b> this lesson is built on and compile the program. Where we have run them, we say so and quote the result. We do not claim a successful build we have not produced.</p><pre class=diagram>{E(cmds)}</pre>')
    if b.get('note'): h.append(f'<p>{md(b["note"])}</p>')
    if b.get('ran'): h.append(f'<p><b>What we ran:</b> {md(b["ran"])}</p>')
  prev=seq[si-1] if si>0 else None
  nxt=seq[si+1] if si+1<pn else None
  navb='<p>'
  if prev: navb+=f'<a class="btn ghost" href="/lessons/{E(prev["slug"])}/">← {E(lesson_of(prev)["title"])}</a> '
  next_label={'guided':'Next guided lesson','challenge':'Next debug challenge','preview':'Next preview'}[ready]
  if nxt: navb+=f'<a class=btn href="/lessons/{E(nxt["slug"])}/">{next_label}: {E(lesson_of(nxt)["title"])}</a> '
  navb+='<a class="btn ghost" href="/lessons/path/">The learning path</a> <a class="btn ghost" href="/lessons/">All lessons</a> <a class="btn ghost" href="/lessons/guide/">How to use a lesson</a></p>'
  h.append(navb)
  h.append('</div>'+rail+'</div></article>')
  if nxt: dock+=f'<a class="btn ghost" href="/lessons/{E(nxt["slug"])}/">{next_label}</a>'
  dock+='</div>'
  return ''.join(h).replace('<!--dock-->',dock,1)
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
  url=f'{SITE}{path}'
  t=re.sub(r'(<link rel=canonical href=")[^"]*"',lambda m:m.group(1)+url+'"',t,count=1)
  t=re.sub(r'(<meta property=og:url content=")[^"]*"',lambda m:m.group(1)+url+'"',t,count=1)
  for a in ('name=description','property=og:description','name=twitter:description'): t=re.sub(f'(<meta {a} content=")[^"]*',lambda m:m.group(1)+E(desc),t,count=1)
  for a in ('property=og:title','name=twitter:title'): t=re.sub(f'(<meta {a} content=")[^"]*',lambda m:m.group(1)+E(title),t,count=1)
  return t
n=len(LIVE); cards=[]; LAB_ASSESS_PATHS=[]
import learning_layer as _ll_write
for x in PATH_LIVE:
  L=lesson_of(x); sl=x['slug']; body=render(x,L,n)
  raw=' '.join(str(L.get('summary') or L['what']).split())
  desc=raw if len(raw)<=158 else raw[:157].rsplit(' ',1)[0].rstrip(',;:.')+'…'
  pg=page(body,f'{L["title"]}: step-by-step Solana lesson, live on devnet | Sol.College',desc,f'/lessons/{sl}/')
  os.makedirs(f'{S}/lessons/{sl}',exist_ok=True); open(f'{S}/lessons/{sl}/index.html','w').write(pg)
  os.makedirs(f'{S}/explore/{sl}',exist_ok=True); open(f'{S}/explore/{sl}/index.html','w').write(pg)
  if L.get('learning_loop') or L.get('assessment'):
    assess_body=CSS+_ll_write.assessment_html(L,sl)
    assess_desc=(f'Assessment rubric for {L.get("title") or sl}: independent criteria, honesty gates, and completion decisions.')
    if len(assess_desc)>158: assess_desc=assess_desc[:157].rsplit(' ',1)[0]+'…'
    ap=page(assess_body,f'{L["title"]}: assessment rubric | Sol.College',assess_desc,f'/lessons/{sl}/assessment/')
    os.makedirs(f'{S}/lessons/{sl}/assessment',exist_ok=True); open(f'{S}/lessons/{sl}/assessment/index.html','w').write(ap)
    LAB_ASSESS_PATHS.append(f'/lessons/{sl}/assessment/')
  ready=readiness(x)
  diff=canon_diff(L.get('difficulty') or '')
  task=L.get('student_outcome') or (L.get('objectives') or [None])[0] or L.get('summary') or L.get('what') or L['title']
  pre=format_prereq((L.get('prereqs') or [None])[0])
  lim=one_line(limit_of(x), 140)
  chips=' '.join(concept_chip(c) for c in (L.get('concepts') or [])[:4])
  plain=re.sub(r'\[([^\]]+)\]\([^)]+\)',r'\1', task+' '+(L.get('summary') or ''))
  blob=' '.join([plain, L['title'], diff, READY_LABEL[ready], ' '.join(L.get('concepts') or [])]).lower()
  bits=[dchip(diff) if diff else '', E(L['time'])+' recorded' if L.get('time') else '', 'verified '+E(x['verified']) if x.get('verified') else '']
  if L.get('track')=='application-lab':
    bits.insert(0, 'Application lab')
  elif L.get('track')=='debug-laboratory':
    bits.insert(0, 'Debug laboratory')
  if L.get('delivery'):
    bits.append(E(L['delivery']))
  if ready=='challenge':
    action='Open the challenge'
  elif L.get('learning_loop'):
    action='Start the lab'
  elif ready=='guided':
    action='Start the lesson'
  else:
    action='Read the preview'
  limit_html=f'<p class=limit>Known limit: {E(lim)}</p>' if lim else ''
  prereq_html=f'<p class=prereq>Before this: {md(one_line(pre, 180))}</p>' if pre else ''
  if lim and ('[' in lim or lim.startswith('{')):
    # format_limit_text should already have cleaned this; refuse raw arrays in cards.
    limit_html=f'<p class=limit>Known limit: see the lesson page for recorded gaps.</p>'
  cards.append(
    f'<article class="card ready-{ready}" data-lesson data-slug="{E(sl)}" data-diff="{E(diff)}" data-format="{ready}" data-text="{E(blob)}">'
    f'<p class="eyebrow status-{ready}">{E(READY_LABEL[ready])}</p>'
    f'<h3><a href="/lessons/{E(sl)}/">{task_html(task)}</a></h3>'
    f'<p class=project>{E(L["title"])}</p>'
    f'{limit_html}{prereq_html}'
    f'<p class=meta>{" · ".join(b for b in bits if b)}</p>'
    f'<p>{chips}</p>'
    f'<p class=cta><a class=btn href="/lessons/{E(sl)}/">{action}</a> · <a href="{E(x["app"])}">Open the app</a></p></article>'
  )
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
    first=items[0]
    body=f'<section class=path-stage id=stage-{st["id"]}><h2>Stage {st["id"]}: {E(st["name"])} {dchip(st["level"])} · recorded times add to {mins} min</h2><p>{md(st["blurb"])}</p><p><a class=btn href="/lessons/{E(first["slug"])}/">Start stage {st["id"]}</a></p>'
    if with_cards:
      body+='<div class=grid>'+''.join(cards[PATH_I[x['slug']]] for x in items)+'</div>'
    else:
      body+=f'<ol>{lis}</ol>'
    out.append(body+'</section>')
  return ''.join(out)
GUIDED=[x for x in PATH_LIVE if readiness(x)=='guided']
CHALLENGES=[x for x in PATH_LIVE if readiness(x)=='challenge']
PREVIEWS=[x for x in PATH_LIVE if readiness(x)=='preview']
ng,nc,nv=len(GUIDED),len(CHALLENGES),len(PREVIEWS)
staged_ids={st['id'] for st in PATH.get('stages',[])}
STAGED=[x for x in GUIDED if lesson_of(x).get('path_stage') in staged_ids]
ELECTIVES=[x for x in GUIDED if lesson_of(x).get('path_stage') not in staged_ids]
ns,ne=len(STAGED),len(ELECTIVES)
def _mins(x):
  m=re.search(r'(\d+)',lesson_of(x).get('time') or '0'); return int(m.group(1)) if m else 0
hours_staged=round(sum(_mins(x) for x in STAGED)/60,1)
hours_electives=round(sum(_mins(x) for x in ELECTIVES)/60,1)
hours_guided=round(sum(_mins(x) for x in GUIDED)/60,1)
hours_challenges=round(sum(_mins(x) for x in CHALLENGES)/60,1)


def path_progress_html():
  """Device-local foundations + core path progress panel (Release E)."""
  import json as _json
  foundations = [
    {'id': 'first-transaction', 'title': '001 First transaction', 'href': '/lessons/first-transaction/'},
    {'id': 'accounts-ownership', 'title': '002 Accounts & ownership', 'href': '/lessons/accounts-ownership/'},
    {'id': 'instructions-programs', 'title': '003 Instructions & programs', 'href': '/lessons/instructions-programs/'},
    {'id': 'transaction-atomicity', 'title': '004 Transaction atomicity', 'href': '/lessons/transaction-atomicity/'},
    {'id': 'transaction-failures', 'title': '005 Transaction failures', 'href': '/lessons/transaction-failures/'},
    {'id': 'application-state', 'title': '006 Application state', 'href': '/lessons/application-state/'},
    {'id': 'protecting-state-transitions', 'title': '007 Protecting state transitions', 'href': '/lessons/protecting-state-transitions/'},
  ]
  core = []
  for x in PATH_LIVE:
    L = lesson_of(x)
    if L.get('path_stage') in (1, 2, 3):
      core.append({
        'id': x['slug'],
        'title': L.get('title') or x['slug'],
        'href': f"/lessons/{x['slug']}/",
        'stage': L.get('path_stage'),
        'order': L.get('path_order'),
      })
  core.sort(key=lambda r: (int(r.get('stage') or 0), int(r.get('order') or 0)))
  payload = _json.dumps({'foundations': foundations, 'core': core}).replace('<', '\\u003c')
  return (
    '<section class="path-progress" id="path-progress" hidden data-learning="progress">'
    '<p class="eyebrow">On this device</p>'
    '<h2>Your learning progress</h2>'
    '<p class="note">Visited or marked workspace steps are <b>not</b> proof of mastery. '
    'Assessment rubrics are separate. Progress stays in this browser only.</p>'
    '<div id="path-progress-body"></div>'
    '<p class="path-progress-actions">'
    '<button type="button" class="btn ghost" id="path-progress-export">Download local progress (JSON)</button> '
    '<label class="btn ghost path-progress-import-label" for="path-progress-import">Restore from JSON<input type="file" id="path-progress-import" accept="application/json,.json" hidden></label> '
    '<button type="button" class="btn ghost" id="path-progress-clear">Clear local progress on this device</button>'
    '</p>'
    f'<script type="application/json" id="path-progress-data">{payload}</script>'
    '</section>'
  )
inventory_line=(
  f'{ng} guided lessons ({ns} on the core staged path, {ne} electives), '
  f'{nc} debug challenges, and {nv} project preview{"s" if nv!=1 else ""}.'
)
starter=next((x for x in GUIDED if canon_diff(lesson_of(x).get('difficulty'))=='Beginner'), GUIDED[0] if GUIDED else None)
next_step=''
if starter:
  SL=lesson_of(starter)
  task=(SL.get('objectives') or [None])[0] or SL.get('summary') or SL['title']
  pre=format_prereq((SL.get('prereqs') or [None])[0])
  bits=' · '.join(b for b in [(SL.get('time')+' recorded') if SL.get('time') else '', 'Guided lesson'] if b)
  lim=one_line(limit_of(starter), 180)
  lim_html=f'<p class=limit>Known limit: {E(lim)}</p>' if lim else ''
  pre_html=f'<p class=prereq>Before this: {md(pre)}</p>' if pre else ''
  next_step=(f'<section class=next-step id=next><p class=eyebrow>Your next step</p><h2>New here? Start with foundations, then this live lesson.</h2>'
    f'<p class=project>First: foundations Lessons <a href="/lessons/first-transaction/">001</a>–'
    f'<a href="/lessons/accounts-ownership/">002</a>–'
    f'<a href="/lessons/instructions-programs/">003</a>–'
    f'<a href="/lessons/transaction-atomicity/">004</a>–'
    f'<a href="/lessons/transaction-failures/">005</a>–'
    f'<a href="/lessons/application-state/">006</a>–'
    f'<a href="/lessons/protecting-state-transitions/">007</a> (release candidates). '
    f'Then: {E(SL["title"])}</p><p class=task>{md(task)}</p><p class=meta>{E(bits)}</p>'
    f'{lim_html}{pre_html}'
    f'<p class=cta><a class=btn href="/lessons/first-transaction/">Start Lesson 001</a> '
    f'<a class="btn ghost" href="/lessons/accounts-ownership/">002</a> '
    f'<a class="btn ghost" href="/lessons/instructions-programs/">003</a> '
    f'<a class="btn ghost" href="/lessons/transaction-atomicity/">004</a> '
    f'<a class="btn ghost" href="/lessons/transaction-failures/">005</a> '
    f'<a class="btn ghost" href="/lessons/application-state/">006</a> '
    f'<a class="btn ghost" href="/lessons/protecting-state-transitions/">007</a> '
    f'<a class="btn ghost" href="/lessons/{E(starter["slug"])}/">Skip to Picassol</a></p>'
    f'<p class=note>Foundations teach review/verification, ownership, instructions, atomicity, failure recovery, honest client state, and program-enforced revisions. '
    f'They are release candidates — not yet technically or learner verified.</p></section>')
picks=''
picks+=('<a class=path-pick href="#foundations"><b>Solana Foundations</b>'
        '<span><span class="chip beg">Beginner</span> · Lessons 001–007 · release candidates</span></a>')
picks+=('<a class=path-pick href="#entry-routes"><b>Choose your entry</b>'
        '<span>New to Solana → Foundations · Already comfortable → application labs</span></a>')
for st in PATH.get('stages',[]):
  items=[x for x in GUIDED if lesson_of(x).get('path_stage')==st['id']]
  if not items: continue
  picks+=f'<a class=path-pick href="#stage-{st["id"]}"><b>{E(st["name"])}</b><span>{dchip(st["level"])} · {len(items)} core-path lessons</span></a>'
if ELECTIVES:
  picks+=f'<a class=path-pick href="#electives"><b>Electives</b><span>{ne} additional guided lessons</span></a>'
if CHALLENGES:
  picks+=f'<a class=path-pick href="#debug-challenges"><b>Debug laboratory</b><span>{nc} independent challenges</span></a>'
choose=f'<section class=choose id=paths><h2>Choose a path</h2><div class=path-picks>{picks}</div></section>' if picks else ''
debug=''
if CHALLENGES:
  dbg_cards=''.join(cards[PATH_I[x['slug']]] for x in CHALLENGES)
  debug=(''
    '<section class=path-stage id=debug-challenges><h2>Debug laboratory</h2>'
    f'<p>{nc} independent challenges. These apps are on devnet, but a named core flow does not complete. '
    'They are investigation practice, not guided lessons, and they are <b>not required</b> to finish the core staged path. '
    'A broken flow can still be an excellent lesson — it is not labelled as a completed core-flow environment.</p>'
    '<div class=grid>'+dbg_cards+'</div></section>')
more=''
if ELECTIVES:
  more=('<section class=path-stage id=electives><h2>Electives</h2>'
        f'<p>These {ne} guided lessons have a written walkthrough and recorded core-flow completion. '
        'They are electives — catalogue lessons outside the numbered three-stage core path. '
        'Cards show difficulty, duration, and the verification date when those fields exist in the lesson record.</p>'
        '<div class=grid>'+''.join(cards[PATH_I[x['slug']]] for x in ELECTIVES)+'</div></section>')
preview=''
if PREVIEWS:
  preview=('<section class=path-stage id=previews><h2>Project previews</h2>'
    '<p>The app is deployed. The full teaching sequence is not written yet, so these are not shown as guided lessons.</p>'
    '<div class=grid>'+''.join(cards[PATH_I[x['slug']]] for x in PREVIEWS)+'</div></section>')
count_line=(
  f'{inventory_line} '
  f'Core staged path recorded time ≈ {hours_staged} h; electives ≈ {hours_electives} h; '
  f'all guided lessons ≈ {hours_guided} h'
  + (f'; debug laboratory ≈ {hours_challenges} h' if hours_challenges else '')
  + '. '
  'A guided lesson requires a written walkthrough and recorded completion of the flows the lesson teaches. '
  'Verification dates on cards are per-app evidence dates; they are not a live “running right now” check.'
)
entry_routes=(''
  '<section class=path-stage id=entry-routes>'
  '<h2>Start here: two entry routes</h2>'
  '<p><b>New to Solana?</b> Begin with <a href="/lessons/first-transaction/">Foundations Lesson 001</a> '
  '(release candidates 001–007). Learn execution vs commitment, accounts, instructions, atomicity, failures, '
  'client state, and expected revisions before Stage 1 application labs.</p>'
  f'<p><b>Already comfortable with transactions and accounts?</b> Start the core application path at '
  f'<a href="/lessons/{E((starter or GUIDED[0])["slug"])}/">{E(lesson_of(starter or GUIDED[0])["title"])}</a> '
  '(Stage 1). Foundations remain optional enrichment.</p>'
  '<p class=cta>'
  '<a class=btn href="/lessons/first-transaction/">New to Solana: Foundations 001</a> '
  f'<a class="btn ghost" href="/lessons/{E((starter or GUIDED[0])["slug"])}/">Application labs: Stage 1</a> '
  '<a class="btn ghost" href="/lessons/path/">Open the learning path</a>'
  '</p></section>')
finder='''<div class=finder id=browse><label>Search lessons <input id=lesson-q type=search placeholder="escrow, PDA, oracle, beginner" autocomplete=off></label>
<div class="finder-row finder-diff" role=group aria-label=Level>
<button type=button data-diff="" aria-pressed=true>All levels</button>
<button type=button data-diff=Beginner>Beginner</button>
<button type=button data-diff=Intermediate>Intermediate</button>
<button type=button data-diff=Advanced>Advanced</button>
</div>
<div class="finder-row finder-format" role=group aria-label=Format>
<button type=button data-format="" aria-pressed=true>All formats</button>
<button type=button data-format=guided>Guided lesson</button>
<button type=button data-format=challenge>Debug challenge</button>
<button type=button data-format=preview>Project preview</button>
</div>
<div class="finder-row finder-touch" role=group aria-label="Device progress">
<button type=button data-touch="" aria-pressed=true>All lessons</button>
<button type=button data-touch=touched>Touched on this device</button>
</div>
<p class=meta id=lesson-count></p></div>
<p class=meta id=lesson-empty hidden>No lesson matches that search.</p>'''
intro=('<p>A guided lesson is a written walkthrough of an app whose recorded core flows completed on a stated verification date. '
  'A debug challenge is an app that is deployed but does not complete a named core flow. '
  'A project preview has the app and the recorded proof, and the teaching sequence is still being written. '
  'The <a href="/articles/">articles</a> explain the same recorded work without asking you to practise it. '
  'The <a href="/library/">library</a> is the catalogue of those pages, the lessons, and the official references that were checked. '
  'The <a href="/lessons/glossary/">glossary</a> explains the terms. You can read any lesson without a wallet. '
  'The wallet is needed only when a step asks you to send a transaction.</p>'
  '<p class=note>Dates on this site mean different things: a lesson’s “verified” date is when that app’s recorded flows were last reproduced; '
  'footer “catalogue generated” dates mark when the static pages were built from the inventory. Neither is a live uptime claim.</p>'
  '<p class=note>Every lesson should produce evidence of understanding. Suitable investigations can develop into tests, patches, or upstream contributions — '
  'an explanation or evidence record is a valid outcome when a code change is not appropriate.</p>')
import foundations_lesson as _foundations
foundations_block=_foundations.foundations_path_section()+_foundations.foundations_card_html()
idx=(f'<nav class=crumbs aria-label=Breadcrumb><a href="/">Home</a> / <span>Lessons</span></nav>{CSS}'
  f'<h1>Learn Solana by making real things work.</h1>'
  f'<p class=lead>Run a transaction on a devnet app, see what changed, and check it against the recorded proof.</p>'
  f'<p class=counts>{count_line}</p>'
  f'<p class=resume id=resume hidden></p>'
  f'{path_progress_html()}'
  f'{entry_routes}'
  f'{_ll_write.community_section_html()}'
  f'{next_step}{choose}{finder}{foundations_block}{stage_blocks(pool=GUIDED)}{more}{debug}{preview}'
  f'<div class=index-intro>{intro}<p><a href="/lessons/guide/">How to use a lesson</a> · <a href="/how-to-build/">How to build your own</a></p></div>'
  f'<p class=note>Looking for the 2,000+ code walkthroughs generated from source? They are in the <a href="/explore/">Source library (not yet live)</a>. They have not been built or run, so they are not lessons.</p>')
desc=(f'{ng} guided Solana lessons ({ns} core path, {ne} electives), {nc} debug challenges, and {nv} project preview. '
      'Counts come from the same records as the catalogue.')
os.makedirs(f'{S}/lessons',exist_ok=True); open(f'{S}/lessons/index.html','w').write(page(idx,'Lessons | Sol.College',desc,'/lessons/'))
# ---- learning path page
first=starter or (GUIDED[0] if GUIDED else LIVE[0])
debug_path=''
if PARTIAL:
  lis=''
  for x in PARTIAL:
    L=lesson_of(x); st=stage_of(L); stn=('Stage %s' % st['id']) if st else ''
    lis+=f'<li><a href="/lessons/{E(x["slug"])}/"><b>{E(L["title"])}</b></a> · {E(L.get("time") or "")} · {E(stn)} · {E(L.get("summary") or "")}</li>'
  debug_path=(''
    '<section class=path-stage id=debug-challenges><h2>Debug laboratory</h2>'
    f'<p>{nc} independent challenges. These apps are live on devnet but a core flow is not fully working yet. '
    'They are listed here for investigation practice and are <b>not required</b> to complete the core staged path. '
    'Find the bug, propose a patch and a regression test, then retest on devnet. '
    'When our fork is fully working, the lesson can move into a stage above.</p>'
    f'<ol>{lis}</ol></section>')
electives_path=''
if ELECTIVES:
  lis=''
  for x in ELECTIVES:
    L=lesson_of(x)
    lis+=f'<li><a href="/lessons/{E(x["slug"])}/"><b>{E(L["title"])}</b></a> · {E(L.get("time") or "")} · {E(L.get("summary") or "")}</li>'
  electives_path=(''
    '<section class=path-stage id=electives><h2>Electives</h2>'
    f'<p>{ne} additional guided lessons with recorded core-flow completion. '
    f'Recorded times add to about {hours_electives} hours. They are optional after or alongside the core staged path.</p>'
    f'<ol>{lis}</ol></section>')
path_parts=[]
path_parts.append('<nav class=crumbs aria-label=Breadcrumb><a href="/">Home</a> / <a href="/lessons/">Lessons</a> / <span>Learning path</span></nav>')
path_parts.append(CSS)
path_parts.append('<h1>The path: become a Solana developer with live apps</h1>')
path_parts.append(
  f'<p class=lead>One curriculum inventory: <b>{ns} core staged lessons</b> (about {hours_staged} h), '
  f'<b>{ne} electives</b> (about {hours_electives} h), and a <b>debug laboratory</b> of {nc} challenges. '
  f'Together with foundations, that is the learner route. The wider catalogue lists {ng} guided lessons and {nc} debug challenges. '
  'Project previews stay on the <a href="/lessons/">lessons index</a>.</p>'
)
path_parts.append(entry_routes)
path_parts.append('<p>When you finish the <b>core staged path</b> you will have practised deriving PDAs, moving SOL and tokens with CPIs, '
  'locking funds against the on-chain clock, authorizing with <code>has_one</code>, finding a missing account check, '
  'and reading a market, a staking program or an oracle. Completing the reading alone does not by itself demonstrate those abilities — '
  'exercises and assessments establish what you showed. Every concept links to the <a href="/lessons/glossary/">glossary</a>.</p>')
path_parts.append('<p class=resume id=resume hidden></p>')
path_parts.append(path_progress_html())
path_parts.append(_foundations.foundations_path_section())
path_parts.append('<h2 id=core-path>Core application path</h2>')
path_parts.append(f'<p>{ns} guided lessons across the numbered stages below. Recorded times add to about {hours_staged} hours.</p>')
path_parts.append(stage_blocks(False, GUIDED))
path_parts.append(electives_path)
path_parts.append(debug_path)
path_parts.append('<p class=note>Core stages list guided lessons only: a written walkthrough, and a core flow recorded as working. '
  'Electives and the debug laboratory are optional. The 2,000+ source-only walkthroughs stay in the <a href="/explore/">Source library</a>. '
  'They have not been deployed or run, so they are not on this path.</p>')
path_body='\n'.join(path_parts)
os.makedirs(f'{S}/lessons/path',exist_ok=True)
open(f'{S}/lessons/path/index.html','w').write(page(
  path_body,
  'The path: become a Solana developer with live apps | Sol.College',
  f'Core path: {ns} staged lessons (~{hours_staged} h). Electives: {ne}. Debug laboratory: {nc}. Catalogue: {ng} guided + {nc} challenges.',
  '/lessons/path/',
))
# ---- glossary, with "shown in these lessons"
shown={}
for x in PATH_LIVE:
  for c in lesson_of(x).get('concepts') or []:
    shown.setdefault(c,[]).append(x)
def gloss_item(t):
  les=shown.get(t['id'],[])
  links=' '.join(f'<a href="/lessons/{E(x["slug"])}/">{E(lesson_of(x)["title"].split(":")[0])}</a>' for x in les) or '—'
  docs=f' · <a href="{E(t["docs"])}">Official docs</a>' if t.get('docs') else ''
  hay=' '.join([t['name'], t.get('def') or '', t['id']]).lower()
  return f'<dt id="{E(t["id"])}" data-term="{E(hay)}">{E(t["name"])}</dt><dd>{md(t["def"])}{docs}<br><small>Shown in: {links}</small></dd>'
g_toc=' · '.join(f'<a href="#{E(t["id"])}">{E(t["name"])}</a>' for t in GLOSS.get('terms',[]))
gloss_body=f'''<nav class=crumbs aria-label=Breadcrumb><a href="/">Home</a> / <a href="/lessons/">Lessons</a> / <span>Glossary</span></nav>
{CSS}
<h1>{E(GLOSS.get("title") or "Solana developer glossary")}</h1>
<p class=lead>{md(GLOSS.get("lead") or "")}</p>
<div class=finder><label>Find a term <input id=gloss-q type=search placeholder="PDA, rent, has_one" autocomplete=off></label></div>
<p class=toc>{g_toc}</p>
<dl class=gloss>{''.join(gloss_item(t) for t in GLOSS.get("terms",[]))}</dl>
<p class=note>These are the terms the <a href="/lessons/path/">core lessons</a> use. For a broader list that also covers the source library, see the site <a href="/glossary/">glossary</a>.</p>'''
os.makedirs(f'{S}/lessons/glossary',exist_ok=True)
open(f'{S}/lessons/glossary/index.html','w').write(page(gloss_body,'Solana developer glossary: PDAs, CPIs, rent, has_one and more | Sol.College','Plain-English Solana and Anchor terms, each linked to the live lesson that shows the term in real code.','/lessons/glossary/'))
# ---- how to use a lesson, and the how-to-build guides (incremental deploys skip build.py)
def _guide_page(body, title, desc, path):
  return page(CSS+body, title, desc, path)
learner = '''<div class=readbar aria-hidden=true><span></span></div>
<article class=lesson data-slug=guide-using-a-lesson>
<div class=lesson-layout><div class=lesson-main>
<nav class=crumbs aria-label=Breadcrumb><a href="/">Home</a> / <a href="/lessons/">Lessons</a> / <span>How to use a lesson</span></nav>
<p class=eyebrow>Guide</p>
<h1>How to use a lesson</h1>
<p class=lead>A lesson is a devnet app you can open, plus the accounts, instructions and transactions that explain it. Nothing here asks you to wait for a cohort.</p>
<section class=path-stage id=s0><h2><span class=num>0</span>Choose your entry route</h2>
<p><b>New to Solana:</b> start with <a href="/lessons/first-transaction/">Foundations Lesson 001</a> through 007 (release candidates — not yet technically or learner verified). <b>Already comfortable with transactions and accounts:</b> start Stage 1 on the <a href="/lessons/path/#core-path">core application path</a>. Do not require a complete beginner to learn PDAs and instruction construction in the same first hour as reviewing a transfer.</p></section>
<section class=path-stage id=s1><h2><span class=num>1</span>Start from the path</h2>
<p>The <a href="/lessons/">lessons index</a> separates foundations, the core staged path, electives, debug challenges and project previews, and it remembers the last lesson you opened in this browser. The <a href="/lessons/path/">learning path</a> lists the core staged lessons first, then electives and the debug laboratory. You can read a lesson without connecting a wallet.</p></section>
<section class=path-stage id=s2><h2><span class=num>2</span>Use your own devnet wallet</h2>
<p>Install Phantom or Solflare, switch it to Solana <b>devnet</b>, and request test SOL from <a href="https://faucet.solana.com">faucet.solana.com</a> while you are signed in. The public RPC airdrop is closed. Devnet SOL has no value. Open the app from the lesson and approve each transaction yourself. Reject anything unexpected.</p></section>
<section class=path-stage id=s3><h2><span class=num>3</span>Check off the steps</h2>
<p>On Try it, tick a step when you have done it. The ticks stay in this browser, on this device. A green check with an explorer link is a step we already ran, with the real signature. A signature is never invented.</p></section>
<section class=path-stage id=s4><h2><span class=num>4</span>Read the proof before you trust the prose</h2>
<p>Section 6 lists the recorded devnet transactions. Open one on Solana Explorer and read the instruction and the program logs. Check execution result and commitment separately when the lesson asks. If a step has no signature, the lesson says so.</p></section>
<section class=path-stage id=s5><h2><span class=num>5</span>Try an exercise before you open the approach</h2>
<p>Hints stay visible. The reference approach is folded. A checked step means you followed the instruction. It does not, by itself, mean you can explain the accounts. The exercises are the check. Debug challenges are apps whose core flow does not complete. They are practice for finding the bug, not guided lessons.</p></section>
<section class=path-stage id=s6><h2><span class=num>6</span>Build your own after the path</h2>
<p>The <a href="/how-to-build/">how to build</a> guides cover the toolchain, the Anchor workflow, tests, deploy and a security checklist. They link the official docs because commands change.</p></section>
<p class=cta><a class=btn href="/lessons/first-transaction/">Start Lesson 001</a> <a class="btn ghost" href="/lessons/path/">Open the path</a> <a class="btn ghost" href="/how-to-build/">How to build</a></p>
</div>
<nav class=rail aria-label="On this page"><a href="#s0">0. Foundations</a><a href="#s1">1. Start from the path</a><a href="#s2">2. Your wallet</a><a href="#s3">3. Check off steps</a><a href="#s4">4. Read the proof</a><a href="#s5">5. Exercises</a><a href="#s6">6. Build your own</a></nav>
</div>
<div class=dock role=region aria-label="Guide actions"><a class=btn href="/lessons/first-transaction/">Lesson 001</a><a class="btn ghost" href="/lessons/path/">Open the path</a><button type=button class="btn ghost" data-jump>Next section</button></div>
</article>'''
os.makedirs(f'{S}/lessons/guide',exist_ok=True)
open(f'{S}/lessons/guide/index.html','w').write(_guide_page(learner,'How to use a Sol.College lesson | Sol.College','Open a live devnet lesson, check off the steps in your browser, and read the recorded transactions before you trust the prose.','/lessons/guide/'))
def write_guides():
  import content,hubs
  guides=list(content.GUIDES)+[hubs.BUILD_DAPP]
  os.makedirs(f'{S}/how-to-build',exist_ok=True)
  crumbs='<nav class=crumbs aria-label=Breadcrumb><a href="/">Home</a> / <span>How to build</span></nav>'
  open(f'{S}/how-to-build/index.html','w').write(page(crumbs+CSS+'<h1>How to build</h1>'+content.guide_index(guides),'How to build on Solana: setup, Anchor, testing, deploy, security | Sol.College','Practical Solana guides: environment setup, Anchor workflow, testing, deploying to devnet and mainnet, and a security checklist.','/how-to-build/'))
  for g in guides:
    c=f'<nav class=crumbs aria-label=Breadcrumb><a href="/">Home</a> / <a href="/how-to-build/">How to build</a> / <span>{E(g["title"])}</span></nav>'
    os.makedirs(f'{S}/how-to-build/{g["slug"]}',exist_ok=True)
    open(f'{S}/how-to-build/{g["slug"]}/index.html','w').write(page(c+CSS+content.guide_article(g),g['title']+' | Sol.College',g['title']+': a practical Solana guide with links to the official docs.',f'/how-to-build/{g["slug"]}/'))
  return [f'/how-to-build/{g["slug"]}/' for g in guides]+['/how-to-build/','/lessons/guide/']+FOUNDATIONS_PATHS
FOUNDATIONS_PATHS=_foundations.write(S, page, CSS)
GUIDE_PATHS=write_guides()
import articles as _articles
ARTICLE_PATHS=_articles.write(S, page, CSS)
import journal as _journal
JOURNAL_PATHS=_journal.write(S, page, CSS)
import solana_library as _solib
LIBRARY_PATHS=_solib.write(S, page, CSS, LIVE, lesson_of, functional_of, readiness, limit_of, one_line)
import standard as _standard
STANDARD_PATHS=_standard.write(S, page, CSS)
import events as _events
EVENT_PATHS=_events.write(S, page, CSS)
# ---- homepage: owned by the landing-page worker. Do not rewrite site/index.html.
# ---- nav, footer and source-library labels on every page (skip the homepage)
_FOUNDATIONS_NAV=_foundations.foundations_main_nav_items()
NAV=(
  '<nav aria-label=Main>'
  '<details class=nav-lessons><summary>Lessons</summary><div>'
  f'{_FOUNDATIONS_NAV}'
  '</div></details>'
  '<a href="/events/">Events</a><a href="/articles/">Articles</a>'
  '<details><summary>More</summary><div>'
  '<a href="/library/">Library</a><a href="/journal/">Journal</a><a href="/degen/">The Degen</a>'
  '<a href="/lessons/path/">Learning path</a><a href="/lessons/#foundations">Foundations</a>'
  '<a href="/lessons/glossary/">Glossary</a><a href="/live/">Live apps</a>'
  '<a href="/campus/">Campus</a><a href="/how-to-build/">How to build</a>'
  '<a href="/explore/">Source library</a>'
  '</div></details></nav>'
)
TOP_CSS=(
  '<style id=sc-top>'
  'html,body{overflow-x:clip;max-width:100%}'
  'main,#main{max-width:100%;overflow-x:clip;min-width:0}'
  '.top{flex-wrap:wrap;gap:8px 16px;align-items:center;padding:8px clamp(12px,3vw,32px);min-height:52px;max-width:100%;min-width:0}'
  '.brand{font-size:16px}.logo{width:22px;height:22px}'
  '.top nav{flex-wrap:wrap;align-items:center;gap:2px;max-width:100%;min-width:0}'
  '.top nav a,.top nav summary{font-size:14px;font-weight:600;padding:6px 8px;border-radius:8px}'
  '.top nav details{position:relative}'
  '.top nav summary{list-style:none;cursor:pointer;color:var(--mut)}'
  '.top nav summary::-webkit-details-marker{display:none}'
  '.top nav summary::after{content:" ▾";font-size:.7em}'
  '.top nav details>div{display:none;position:absolute;left:0;top:calc(100% + 8px);z-index:30;min-width:min(230px,92vw);max-width:min(92vw,280px);max-height:min(70vh,520px);overflow:auto;padding:6px;flex-direction:column;background:#14122a;border:1px solid var(--line);border-radius:12px;box-shadow:0 16px 40px rgba(0,0,0,.45)}'
  '.top nav details[open]>div{display:flex}'
  '.top nav details:last-of-type>div{left:auto;right:0}'
  '.top nav details a{white-space:nowrap}'
  '.crumbs{max-width:100%;overflow-wrap:anywhere;word-break:break-word}'
  '.crumbs>span{display:inline}'
  '.foundations-seq{display:flex;flex-wrap:wrap;align-items:center;gap:6px 10px;margin:10px 0 14px;padding:8px 10px;border:1px solid var(--line);border-radius:10px;background:rgba(20,18,42,.55);max-width:100%}'
  '.foundations-seq-label{font-size:12px;font-weight:700;letter-spacing:.04em;text-transform:uppercase;color:var(--mut);margin-right:4px}'
  '.foundations-seq a,.foundations-seq span[aria-current=page]{font-size:13px;font-weight:650;padding:4px 8px;border-radius:8px;text-decoration:none}'
  '.foundations-seq a{color:var(--fg)}'
  '.foundations-seq span[aria-current=page]{background:var(--accent,#7dffb3);color:#0b0a14}'
  '@media(max-width:600px){'
  '.top{gap:6px 10px;padding:8px 12px}'
  '.top nav a,.top nav summary{padding:6px 7px;font-size:13px}'
  '.top nav details>div{left:0;right:auto;max-width:min(92vw,calc(100vw - 24px));min-width:0;width:min(260px,calc(100vw - 24px))}'
  '.top nav details:last-of-type>div{left:auto;right:0}'
  '.crumbs>span{display:block;margin-top:2px}'
  '}'
  '</style>'
)
for fp in glob.glob(f'{S}/**/*.html',recursive=True):
  if '/dapps/' in fp or '/legacy/' in fp: continue
  if os.path.normpath(fp)==os.path.normpath(f'{S}/index.html'): continue
  t=open(fp,errors='replace').read(); o=t
  t=re.sub(r'<nav aria-label=Main>.*?</nav>',NAV,t,count=1,flags=re.S)
  t=re.sub(r'<style id=sc-top>.*?</style>','',t,count=1,flags=re.S)
  if '<nav aria-label=Main>' in t and '</head>' in t:
    t=t.replace('</head>',TOP_CSS+'</head>',1)
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
  t=open(sm).read(); add=''.join(f'<url><loc>{SITE}{p}</loc></url>\n' for p in ['/lessons/','/lessons/path/','/lessons/glossary/','/lessons/guide/']+[f'/lessons/{x["slug"]}/' for x in LIVE]+LAB_ASSESS_PATHS+GUIDE_PATHS+ARTICLE_PATHS+JOURNAL_PATHS+LIBRARY_PATHS+STANDARD_PATHS+EVENT_PATHS if f'<loc>{SITE}{p}</loc>' not in t)
  if add: open(sm,'w').write(t.replace('</urlset>',add+'</urlset>'))
json.dump(CACHE,open(CACHE_F,'w'),indent=0)
print('core_lessons:',[(x['slug'],('draft' if lesson_of(x).get('draft') else 'full'),functional_of(x)) for x in PATH_LIVE])
_landing.START_LESSON='/lessons/first-transaction/'
_landing.write_home(S)
_landing.enrich_lessons(S)
import release_identity as _release
_rel=_release.write_artifacts(S, os.path.join(_here,'..'))
# Stamp release identity on every HTML page (including homepage) so reviewers can identify the build.
for fp in glob.glob(f'{S}/**/*.html',recursive=True):
  if '/dapps/' in fp or '/legacy/' in fp: continue
  t=open(fp,errors='replace').read(); o=t
  t=_release.inject_into_html(t,_rel)
  if t!=o: open(fp,'w').write(t)
# Keep curriculum summary in sync with sitemap when present.
sm=f'{S}/sitemap.xml'
if os.path.exists(sm):
  t=open(sm).read()
  add=''.join(f'<url><loc>{SITE}{p}</loc></url>\n' for p in ['/releases/'] if f'<loc>{SITE}{p}</loc>' not in t)
  if add: open(sm,'w').write(t.replace('</urlset>',add+'</urlset>'))
import seo as _seo
_seo.apply(S)
