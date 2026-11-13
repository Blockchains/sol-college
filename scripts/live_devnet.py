"""Post-build pass over the deployed site dir (full or incremental): honest per-lesson status, the 'Live on devnet' page
and homepage section, and the forks' own hosted apps. Usage: python3 scripts/live_devnet.py [site_dir]
Data: dapps/live.json (forks whose own app is hosted and whose devnet flow was run end to end, with tx signatures),
dapps/deployed/*.json (programs on devnet), tests/results/*.json (captured build/test runs)."""
import json,os,re,sys,glob,shutil,html
S=sys.argv[1] if len(sys.argv)>1 else 'site'; E=lambda s:html.escape(str(s),quote=True)
LIVE=json.load(open('dapps/live.json')); LV={x['slug']:x for x in LIVE}
BLK=json.load(open('dapps/blocked.json')) if os.path.exists('dapps/blocked.json') else {}
DEP={os.path.basename(f)[:-5]:json.load(open(f)) for f in glob.glob('dapps/deployed/*.json')}
RES={}
for f in glob.glob('tests/results/*.json'):
  if f.endswith('permalinks.json'): continue
  d=json.load(open(f)); RES[d.get('slug') or os.path.basename(f)[:-5]]=d
pub=json.load(open(f'{S}/published.json')) if os.path.exists(f'{S}/published.json') else []
slugs=sorted({re.sub(r'^/explore/|/$','',x['path']) for x in pub if x.get('path','').startswith('/explore/')})
TX=lambda s:f'https://explorer.solana.com/tx/{s}?cluster=devnet'; AD=lambda a:f'https://explorer.solana.com/address/{a}?cluster=devnet'
def tier(sl):
  if sl in LV: return 'live'
  if DEP.get(sl,{}).get('devnet'): return 'program_only'
  if os.path.isdir(f'dapps/static/{sl}'): return 'client_app'
  r=RES.get(sl)
  if r: return 'run_failed' if r.get('status')=='fails' else 'run_captured'
  return 'source_only'
BANNER={
 'live':lambda sl:f'✅ <b>Live on devnet, verified {E(LV[sl]["verified"])}.</b> The fork&#39;s own app is hosted at <a href="{E(LV[sl]["app"])}">{E(LV[sl]["app"])}</a> and its core flow was run on devnet with real transactions (and rejected bad input). <a href="/live/#{sl}">Evidence</a>.',
 'program_only':lambda sl:f'⚠️ <b>Program deployed on devnet, app not verified.</b> Program <a href="{AD(DEP[sl]["devnet"])}"><code>{E(DEP[sl]["devnet"][:8])}…</code></a> is on devnet and answered a test transaction, but the page at /dapps/{sl}/ is a generic console built from the IDL, not the fork&#39;s own app, and the fork&#39;s full workflow has not been verified end to end.',
 'client_app':lambda sl:f'🌐 <b>The fork&#39;s own frontend is hosted at <a href="/dapps/{sl}/">/dapps/{sl}/</a> (client-only, no program of its own).</b> It builds and serves; a wallet-signed flow has not been verified end to end.',
 'run_captured':lambda sl:f'🔧 <b>Build output captured ({E(RES[sl].get("tested",""))}), no hosted app yet.</b> The step-by-step guide below shows the real commands and results from our run; the fork&#39;s own app is not hosted or verified.',
 'run_failed':lambda sl:f'❌ <b>Our build/run of this fork failed ({E(RES[sl].get("tested",""))}).</b> The walkthrough below is from the source only; the failing step is shown in the guide.',
 'source_only':lambda sl:'📄 <b>Source walkthrough only.</b> This page is generated from the code at a pinned commit. We have not built or run this fork yet, so there is no captured output and no verified app.'}
counts={}; audit=[]
def sub_marked(t,key,new,anchor_re):
  m=re.compile(f'<!--{key}-->.*?<!--/{key}-->',re.S)
  blk=f'<!--{key}-->{new}<!--/{key}-->'
  if m.search(t): return m.sub(lambda _:blk,t,count=1)
  return re.sub(anchor_re,lambda x:x.group(0)+blk,t,count=1,flags=re.S)
def live_section(x):
  st=''.join(f'<li>{E(a)}: <a href="{TX(s)}"><code>{E(s[:20])}…</code></a></li>' for a,s in x['steps'])
  ng=''.join(f'<li>{E(n)}</li>' for n in x['negative'])
  src=''.join(f'<li><a href="{E(u)}">{E(l)}</a></li>' for l,u in x['source'])
  return f'''<section class=note id="{E(x["slug"])}"><h2>{E(x["name"])}</h2><p><a class=btn href="{E(x["app"])}">Open the app (devnet)</a> <a class="btn ghost" href="{E(x["lesson"])}">Read the lesson</a></p>
<p><b>You will learn:</b> {E(x["learn"])}</p><ul>{src}</ul>
<p><b>App:</b> {E(x["app_kind"])}</p><p><b>Program on devnet:</b> <a href="{AD(x["program"])}"><code>{E(x["program"])}</code></a> · fork <a href="{E(x["fork"])}/tree/{E(x["commit"])}">{E(x["fork"][19:])} @ <code>{E(x["commit"][:7])}</code></a></p>
<p><b>Devnet proof, {E(x["verified"])}</b> (run by <a href="https://github.com/Blockchains/sol-college/blob/main/{E(x["flow"])}"><code>{E(x["flow"])}</code></a>, which mirrors the app&#39;s own transaction code; <a href="https://github.com/Blockchains/sol-college/blob/main/{E(x["log"])}">log</a>):</p><ul class=sigs>{st}</ul><p><b>Rejected as expected:</b></p><ul>{ng}</ul><p><b>App check:</b> {E(x["ui_check"])}</p><p><b>Not covered:</b> {E(x["limits"])}</p></section>'''
for sl in slugs:
  t_=tier(sl); counts[t_]=counts.get(t_,0)+1; audit.append(dict(slug=sl,status=t_,lesson=f'/explore/{sl}/',app=LV[sl]['app'] if sl in LV else None,verified=(LV.get(sl) or {}).get('verified') or (RES.get(sl) or {}).get('tested'),blocked=BLK.get(sl) if t_!='live' else None))
  fp=f'{S}/explore/{sl}/index.html'
  if not os.path.exists(fp): continue
  t=open(fp).read()
  t=sub_marked(t,'sc-status',f'<p class=note role=status>{BANNER[t_](sl)}'+(f' <b>Why it is not live yet:</b> {E(BLK[sl])}' if sl in BLK and t_!='live' else '')+'</p>',r'<main id=main>(?:<nav class=crumbs.*?</nav>)?')
  if t_=='live':
    x=LV[sl]; new=f'<section class=note><h2>Open the dapp</h2><p><b>✅ Live on devnet, verified {E(x["verified"])}</b>: the fork&#39;s own app.</p><p><a class=btn href="{E(x["app"])}">Open the app</a> Connect Phantom or Solflare set to devnet; every transaction is signed in your own wallet. Free devnet SOL: <a href="https://faucet.solana.com">faucet.solana.com</a>.</p><p>{E(x["app_kind"])}</p><p>Program <a href="{AD(x["program"])}"><code>{E(x["program"])}</code></a>. Proof transactions and failure cases: <a href="/live/#{sl}">Live on devnet</a>.</p></section>'
    t=re.sub(r'<section class=note><h2>Open the dapp</h2>.*?</section>',lambda _:new,t,count=1,flags=re.S)
  elif t_=='program_only':
    t=t.replace('✅ Operational on devnet, verified','Program deployed on devnet (generic IDL console; the fork&#39;s own app is not verified), first test transaction')
  open(fp,'w').write(t)
for x in LIVE:
  d=f'{S}/dapps/{x["slug"]}'; shutil.rmtree(d,ignore_errors=True); shutil.copytree(f'dapps/static/{x["slug"]}',d)
json.dump(dict(counts=counts,total=len(slugs),lessons=audit),open(f'{S}/lesson-audit.json','w'),indent=0)
summary=f'<p>Of {len(slugs)} published walkthroughs: <b>{counts.get("live",0)}</b> live and verified on devnet with the fork&#39;s own app, {counts.get("program_only",0)} with a program on devnet but no verified app, {counts.get("client_app",0)} with the fork&#39;s own client-only frontend hosted but no verified wallet flow, {counts.get("run_captured",0)} with captured build output only, {counts.get("run_failed",0)} whose build/run failed, and <b>{counts.get("source_only",0)}</b> source-only walkthroughs that have not been run yet. Every lesson page now shows its status. <a href="/lesson-audit.json">Full list (JSON)</a>.</p>'
# The pivoted homepage is owned by scripts/landing.py (written at the end of core_lessons.py).
# Do not inject the old "Live on devnet" section into index.html. Use a non-landing shell for /live/.
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import landing as _landing
_home=open(f'{S}/index.html').read() if os.path.exists(f'{S}/index.html') else ''
home=_landing.page_shell(S) or _home
if home and not _landing.is_landing(home) and 'data-landing=' not in (_home or ''):
    # First-run / rollback only: leave a pre-landing index alone for the lesson-page shell.
    pass
# /live/ page in a non-landing shell
body=f'<h1>Live on devnet</h1><p class=lead>Solana forks from the SuperStack running as their own apps on devnet, each with its program deployed and its core flow exercised with real devnet transactions. Use a wallet set to devnet; devnet SOL is free at <a href="https://faucet.solana.com">faucet.solana.com</a> and has no value.</p>'+''.join(live_section(x) for x in LIVE)+'<h2>Status of every lesson</h2>'+summary
lp=re.sub(r'<main id=main>.*</main>',lambda _:f'<main id=main>{body}</main>',re.sub(r'<!--sc-live-->.*?<!--/sc-live-->','',home,flags=re.S),count=1,flags=re.S) if home and '<main id=main>' in home else None
if lp:
  lp=re.sub(r'<title>.*?</title>','<title>Live on devnet: verified Solana apps | Sol.College</title>',lp,count=1)
  lp=re.sub(r'<script type="application/ld\+json">.*?</script>','',lp,flags=re.S)
  for a,b in [('href="https://sol.college/"','href="https://sol.college/live/"'),('content="https://sol.college/"','content="https://sol.college/live/"')]: lp=lp.replace(a,b)
  lp=re.sub(r'(<meta name=description content=")[^"]*','\\1Solana forks running as their own apps on devnet, with program IDs, real proof transactions and failure cases.',lp,count=1)
  os.makedirs(f'{S}/live',exist_ok=True); open(f'{S}/live/index.html','w').write(lp)
sm=f'{S}/sitemap.xml'
if os.path.exists(sm) and '/live/</loc>' not in open(sm).read():
  t=open(sm).read(); open(sm,'w').write(t.replace('</urlset>','<url><loc>https://sol.college/live/</loc></url>\n</urlset>'))
print('live_devnet:',counts,'total',len(slugs),'live apps',[x['slug'] for x in LIVE])
