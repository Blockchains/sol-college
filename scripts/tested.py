"""Render the verified build guide for a fork lesson from tests/results/<slug>.json (written by tests/run_fork.py)."""
import json,os,re,html,glob
E=html.escape
REPO='https://github.com/Blockchains/sol-college'
SPECS=json.load(open('tests/specs.json')) if os.path.exists('tests/specs.json') else {}
def result(pr):
  f=f"tests/results/{re.sub(r'[^a-z0-9-]+','-',pr['name'].lower())}.json"
  return json.load(open(f)) if os.path.exists(f) else None
def unpublished():
  return {k:v['unpublish'] for k,v in SPECS.items() if v.get('unpublish')}
def envnames(root):
  out={}
  for f in glob.glob(root+'/**/.env*example*',recursive=True)+glob.glob(root+'/**/.env.template',recursive=True)+glob.glob(root+'/**/.env.sample',recursive=True):
    if 'node_modules' in f: continue
    names=[m for m in re.findall(r'^\s*#?\s*([A-Z][A-Z0-9_]{2,})\s*=',open(f,errors='replace').read(),re.M)]
    if names: out[os.path.relpath(f,root)]=list(dict.fromkeys(names))
  return out
def how_it_works(pr,root):
  """Instruction handlers and account structs, with permalinks at the pinned commit."""
  ins=[];acc={}
  for f in glob.glob(root+'/**/*.rs',recursive=True):
    if re.search(r'/(target|node_modules|tests?)/',f): continue
    rel=os.path.relpath(f,root); src=open(f,errors='replace').read().split('\n')
    for i,l in enumerate(src):
      m=re.search(r'pub fn (\w+)\s*(?:<[^>]*>)?\(\s*ctx:\s*Context<(?:\'\w+,\s*)*(\w+)',l)
      if m: ins.append((m.group(1),m.group(2),rel,i+1))
      m=re.search(r'pub struct (\w+)<\'info>',l)
      if m and i>0 and 'Accounts' in ' '.join(src[max(0,i-3):i]): acc[m.group(1)]=(rel,i+1)
      m=re.search(r'^\s*pub enum (\w*Instruction\w*)',l)
      if m:
        for j in range(i+1,min(i+80,len(src))):
          if src[j].strip().startswith('}'): break
          v=re.match(r'\s*([A-Z]\w+)\s*[,{(]?',src[j])
          if v and not src[j].strip().startswith('//'): ins.append((v.group(1),None,rel,j+1))
  L=lambda rel,n:f"{pr['fork']}/blob/{pr['commit']}/{rel}#L{n}"
  rows=[]
  for name,ctx,rel,n in ins[:30]:
    a=acc.get(ctx) if ctx else None
    rows.append(f'<tr><td><a href="{L(rel,n)}"><code>{E(name)}</code></a></td><td>{f"<a href={chr(34)}{L(*a)}{chr(34)}><code>{E(ctx)}</code></a>" if a else (f"<code>{E(ctx)}</code>" if ctx else "native instruction variant")}</td><td><code>{E(rel)}:{n}</code></td></tr>')
  return rows
def badge(res,funds):
  d=res['tested']; log=f"{REPO}/blob/main/tests/logs/{res['slug']}.log"
  s={'operational':f'✅ Operational, verified {d}','partial':f'🟡 Partly operational, verified {d}','builds':f'🟡 Builds, verified {d}','fails':f'❌ Does not build as-is, checked {d}'}[res['status']]
  b=f'<p class=badges><a class="chip ok" href="{log}">{E(s)}</a> <a class=chip href="{log}">Tested on {d}: full log</a> <a class=chip href="{REPO}/blob/main/tests/results/{res["slug"]}.json">results.json</a>'
  if funds: b+=' <span class="chip warn">⚠️ Needs real funds to run on mainnet</span>'
  return b+'</p>'
def guide(pr,root):
  res=result(pr)
  if not res: return ''
  sp=SPECS.get(pr['name'],{}); funds=sp.get('needs_real_funds'); v=res['versions']
  st=lambda ph:[s for s in res['steps'] if s['phase']==ph]
  def rows(ss): return ''.join(f'<tr><td><code>{E(s["cwd"])}</code></td><td><code>{E(s["cmd"])}</code></td><td>{"✅ pass" if s["exit"]==0 else f"❌ exit {s[chr(101)+chr(120)+chr(105)+chr(116)]}"}</td><td>{s["secs"]}s</td></tr>' for s in ss)
  def tbl(ss): return f'<table class=tbl><thead><tr><th>Directory</th><th>Command</th><th>Result</th><th>Time</th></tr></thead><tbody>{rows(ss)}</tbody></table>' if ss else ''
  def fails(ss): return ''.join(f'<details><summary>Output tail: <code>{E(s["cmd"][:80])}</code></summary><pre class=sh><code>{E(s["tail"])}</code></pre></details>' for s in ss if s['exit'])
  h=badge(res,funds)
  if funds: h+=f'<div class="note warn"><h2>High risk: this app moves real money on mainnet</h2><p>{E(funds)} We never connected a funded wallet, signed a mainnet transaction or spent real funds while testing it. If you run the mainnet steps below, use a fresh wallet holding only what you can afford to lose, read every transaction before you sign it, and start with tiny amounts. Unaudited hackathon code can lose funds.</p></div>'
  anc=res.get('anchor_version'); slug=pr['fork'].rstrip('/').split('/')[-1]
  h+=f'<h2>Build it yourself: step-by-step guide</h2><p>Every command below was run on {res["tested"]} by <a href="{REPO}/blob/main/tests/run_fork.py"><code>tests/run_fork.py</code></a> against the pinned commit, and the results come from that run. The full output is in the <a href="{REPO}/blob/main/tests/logs/{res["slug"]}.log">committed log</a>.</p>'
  h+='<h3>1. Prerequisites (versions we tested with)</h3><ul>'+''.join(f'<li>{E(k)}: <code>{E(x)}</code></li>' for k,x in [('Rust',v.get('rust')),('Solana CLI (Agave)',v.get('solana')),('Anchor (via avm)',anc),('Node.js',v.get('node')),('npm',v.get('npm')),('pnpm',v.get('pnpm')),('Go',v.get('go') if 'go' in json.dumps(res['steps']) else None)] if x)+'</ul>'
  if anc: h+=f'<pre class=sh><code>cargo install --git https://github.com/coral-xyz/anchor avm --locked\navm install {anc} && avm use {anc}\nsh -c "$(curl -sSfL https://release.anza.xyz/stable/install)"</code></pre>'
  h+=f'<h3>2. Clone at the tested commit</h3><pre class=sh><code>git clone {pr["fork"]}.git && cd {slug}\ngit checkout {pr["commit"]}</code></pre>'
  pre=sp.get('pre',[]); env=envnames(root)
  h+='<h3>3. Configure</h3>'
  if env: h+='<p>The repo reads these environment variables. Copy the example file and fill in your own values. Never commit real keys.</p><ul>'+''.join(f'<li><code>{E(f)}</code>: '+', '.join(f'<code>{E(n)}</code>' for n in ns[:40])+'</li>' for f,ns in env.items())+'</ul>'
  else: h+='<p>No environment file is needed.</p>'
  if pre: h+='<p>Fixes we had to apply to the pinned commit before it would build or run, with the reason for each:</p><ol>'+''.join(f'<li><code>{E(c["cmd"])}</code>{(" (in <code>"+E(c["cwd"])+"</code>)") if c.get("cwd") else ""}. {E(c.get("why",""))}</li>' for c in pre)+'</ol>'
  for n,(t,ph) in enumerate([('Install dependencies','install'),('Build','build'),('Test','test'),('Deploy to a local validator','deploy'),('Run and exercise it','run')],4):
    ss=st(ph)+(st('fix') if ph=='build' else [])
    if ph=='deploy' and anc and not ss: ss=[]
    if not ss and ph not in ('deploy',): continue
    h+=f'<h3>{n}. {t}</h3>'
    if ph=='deploy' and anc: h+='<pre class=sh><code>solana-test-validator --reset   # separate terminal\nsolana config set -ul && solana airdrop 100\nanchor deploy --provider.cluster localnet</code></pre>'
    h+=tbl(ss)+fails(ss)
  if res.get('program_ids'):
    h+='<h3>Proof: program IDs and transactions</h3><ul>'+''.join(f'<li><code>{E(k)}</code>: <code>{E(p)}</code> (local validator)</li>' for k,p in res['program_ids'].items())+'</ul>'
  if res.get('signatures'): h+=f'<p>Transaction signatures recorded on the local validator ({len(res["signatures"])} shown). Local ledgers are thrown away after the run, so these work as receipts in the log and can\'t be looked up on an explorer:</p><ul class=sigs>'+''.join(f'<li><code>{E(s[0])}</code> <code>{E(s[2][:20])}…{E(s[2][-8:])}</code></li>' for s in res['signatures'][:12])+'</ul>'
  if anc or res.get('program_ids'):
    h+='<h3>Deploy to devnet (free)</h3><pre class=sh><code>solana config set --url devnet\nsolana airdrop 2   # or https://faucet.solana.com\nanchor deploy --provider.cluster devnet   # native: solana program deploy target/deploy/&lt;name&gt;.so\n# point the frontend RPC env var at https://api.devnet.solana.com</code></pre>'
  if funds: h+='<h3>Mainnet (your own wallet, at your own risk)</h3><ol><li>Use a dedicated wallet, and fund it with only a small amount.</li><li>Set the RPC env var to a mainnet endpoint you control (<code>https://api.mainnet-beta.solana.com</code> is rate-limited).</li><li>Build and start the app exactly as above, then connect the wallet in the browser.</li><li>Simulate first: check the amounts, recipients and programs your wallet shows before you sign.</li></ol>'
  if sp.get('notes'): h+=f'<p class=meta>Notes: {E(sp["notes"])}</p>'
  hw=how_it_works(pr,root)
  if hw: h+='<h2>How it works</h2><p>Every instruction handler in the program, with the accounts struct it validates. Each link points to the line at the pinned commit.</p><table class=tbl><thead><tr><th>Instruction</th><th>Accounts</th><th>Where</th></tr></thead><tbody>'+''.join(hw)+'</tbody></table>'
  ex=['Add an integration test that runs the main flow end to end and asserts every account state change.','Add a negative test: call each instruction with the wrong signer or account and check that it fails.']
  if hw: ex+=['Add an event (<code>emit!</code>) to each state-changing instruction and subscribe to it from the client.','Replace any unchecked <code>AccountInfo</code> with typed accounts plus <code>has_one</code>/<code>seeds</code> constraints.']
  if res.get('apps') or st('run'): ex+=['Make the frontend read the cluster from an env var, deploy it to GitHub Pages and point it at your devnet program.']
  ex+=['Wire the build into CI by copying this site\'s <a href="'+REPO+'/blob/main/.github/workflows/verify-forks.yml">verify-forks workflow</a>.']
  h+='<h2>Extend it</h2><ol>'+''.join(f'<li>{x}</li>' for x in ex)+'</ol>'
  return h
