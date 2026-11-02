"""Build, test and run one Sol.College fork lesson end to end on localnet. Writes tests/results/<slug>.json and tests/logs/<slug>.log.
Usage: python3 tests/run_fork.py <work-dir-name> [<work-dir-name>...]"""
import json,os,re,subprocess,sys,time,shutil,glob,signal
ROOT=os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PROJ={p['name']:p for p in json.load(open(ROOT+'/data/projects.json'))['projects']}
B='/tmp/scbuild'; os.makedirs(B,exist_ok=True); os.makedirs(ROOT+'/tests/results',exist_ok=True); os.makedirs(ROOT+'/tests/logs',exist_ok=True)
ENV=dict(os.environ,CI='1',NEXT_TELEMETRY_DISABLED='1',NX_NO_CLOUD='true',NX_DAEMON='false',ANCHOR_PROVIDER_URL='http://127.0.0.1:8899',
  PATH=':'.join([os.path.expanduser(p) for p in ['~/tbin','~/.cargo/bin','~/.local/share/solana/install/active_release/bin','~/.local/bin']]+[os.environ['PATH']]))
ENV['ANCHOR_WALLET']=os.path.expanduser('~/.config/solana/id.json')
RED=[(re.compile(r'(api[-_]?key=|token=|secret=)[^\s&"]+',re.I),r'\1[REDACTED]'),(re.compile(r'https://[^\s"]*(helius|alchemy|quiknode|quicknode|infura|ankr)[^\s"]*',re.I),'https://[REDACTED-RPC]'),
     (re.compile(r'\b[1-9A-HJ-NP-Za-km-z]{80,90}\b'),'[REDACTED-KEY]'),(re.compile(r'/home/box'),'~')]
def red(s):
  for rx,r in RED: s=rx.sub(r,s)
  return s
def ver(c):
  try: return subprocess.run(c,shell=True,capture_output=True,text=True,env=ENV,timeout=30).stdout.strip().split('\n')[0]
  except Exception: return ''
VERS=dict(rust=ver('rustc -V'),solana=ver('solana --version'),anchor=ver('anchor --version'),node=ver('node -v'),npm=ver('npm -v'),pnpm=ver('pnpm -v'),go=ver('go version'))
class Run:
  def __init__(s,name):
    s.p=PROJ[name]; s.slug=re.sub(r'[^a-z0-9-]+','-',name.lower()); s.dir=f'{B}/{s.slug}'; s.steps=[]; s.log=open(f'{ROOT}/tests/logs/{s.slug}.log','w'); s.sigs=[]; s.urls=[]
  def sh(s,phase,cmd,cwd='.',timeout=1500,ok=None):
    t=time.time(); s.log.write(red(f'\n$ (cd {cwd} && {cmd})\n')); s.log.flush()
    try:
      r=subprocess.run(cmd,shell=True,cwd=os.path.join(s.dir,cwd),capture_output=True,text=True,env=ENV,timeout=timeout,errors='replace'); out=r.stdout+r.stderr; code=r.returncode
    except subprocess.TimeoutExpired as e: out=((e.stdout or b'').decode(errors='replace') if isinstance(e.stdout,bytes) else (e.stdout or ''))+f'\nTIMEOUT after {timeout}s'; code=124
    raw=out; out=red(out); s.log.write(out[-60000:]+f'\n[exit {code}, {time.time()-t:.0f}s]\n'); s.log.flush()
    tail='\n'.join([l for l in out.strip().split('\n') if l.strip()][-6:])[-900:]
    st=dict(phase=phase,cwd=cwd,cmd=red(cmd).replace('~/.avm/bin/anchor-','anchor@').replace('~/.config/solana/id.json','~/.config/solana/id.json'),exit=code,secs=round(time.time()-t),tail=tail); s.steps.append(st); return code==0,(raw if phase in ('verify','run') else out)
def pm(d):
  return 'pnpm' if os.path.exists(d+'/pnpm-lock.yaml') else 'yarn' if os.path.exists(d+'/yarn.lock') else 'npm'
INST={'pnpm':'pnpm install --no-frozen-lockfile','yarn':'npx -y yarn@1 install --ignore-engines --network-timeout 600000','npm':'npm install --no-audit --no-fund --legacy-peer-deps'}
RUNC={'pnpm':'pnpm run','yarn':'npx -y yarn@1 run','npm':'npm run'}
VAL=None
def validator(start,extra=()):
  global VAL
  if VAL: VAL.terminate(); VAL.wait(); VAL=None
  subprocess.run('pkill -f solana-test-validator',shell=True); time.sleep(3)
  if start:
    shutil.rmtree('/tmp/sc-ledger',ignore_errors=True)
    VAL=subprocess.Popen(['solana-test-validator','--reset','--quiet','--ledger','/tmp/sc-ledger',*extra],env=ENV,stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL)
    for _ in range(90):
      if subprocess.run('solana cluster-version -u localhost',shell=True,env=ENV,capture_output=True).returncode==0: break
      time.sleep(1)
    for _ in range(60):
      time.sleep(1)
      if subprocess.run('solana cluster-version -u localhost',shell=True,env=ENV,capture_output=True).returncode==0: return True
    return False
def run(name,extra=None):
  r=Run(name); p=r.p; shutil.rmtree(r.dir,ignore_errors=True)
  r.sh('clone',f"git clone -q --filter=blob:none {p['fork']}.git {r.dir} && git -C {r.dir} checkout -q {p['commit']}",cwd='/tmp',timeout=600)
  sp=json.load(open(ROOT+'/tests/specs.json')).get(name,{}) if os.path.exists(ROOT+'/tests/specs.json') else {}
  for c in sp.get('pre',[]): r.sh('configure',c['cmd'],c.get('cwd','.'))
  anchors=sorted(os.path.dirname(os.path.relpath(f,r.dir)) or '.' for f in glob.glob(r.dir+'/**/Anchor.toml',recursive=True) if 'node_modules' not in f)
  anchors=[a for a in anchors if a not in sp.get('skip_anchor',[])]
  progids={}
  apps=sp.get('apps')
  if apps is None:
    apps=[os.path.dirname(os.path.relpath(f,r.dir)) or '.' for f in glob.glob(r.dir+'/package.json')+glob.glob(r.dir+'/*/package.json') if 'node_modules' not in f]
    apps=[a for a in apps if a not in anchors]
  installed=set()
  for a in (['.'] if os.path.exists(r.dir+'/package.json') else [])+apps+anchors:
    if a in installed or not os.path.exists(f'{r.dir}/{a}/package.json'): continue
    installed.add(a); r.sh('install',INST[pm(f'{r.dir}/{a}')],a,timeout=1800)
  for a in anchors:
    ad=f'{r.dir}/{a}'; cargo=' '.join(open(x).read() for x in glob.glob(ad+'/programs/*/Cargo.toml'))
    m=re.search(r'anchor-lang\s*=\s*(?:\{[^}]*version\s*=\s*)?"[=^~]?(\d+\.\d+)\.(\d+)',cargo); av={'0.29':'0.29.0','0.30':'0.30.1','0.31':'0.31.1','0.32':'0.32.1'}.get(m.group(1) if m else '','0.29.0' if m and m.group(1) in ('0.24','0.25','0.26','0.27','0.28') else '0.32.1')
    A=('RUSTUP_TOOLCHAIN=nightly-2025-04-01 ' if av.startswith('0.30') else '')+os.path.expanduser(f'~/.avm/bin/anchor-{av}'); r.anchor_version=av
    lk=ad+'/Cargo.lock'
    if os.path.exists(lk) and re.search(r'^version = 4$',open(lk).read(),re.M):
      open(lk,'w').write(re.sub(r'^version = 4$','version = 3',open(lk).read(),flags=re.M)); r.steps.append(dict(phase='configure',cwd=a,cmd="Cargo.lock 'version = 4' -> 'version = 3' (the cargo bundled with Solana platform-tools cannot read v4 lockfiles)",exit=0,secs=0,tail=''))
    if os.path.exists(ad+'/package.json'): r.sh('install',INST[pm(ad)],a)
    r.sh('configure',f'{A} keys sync && python3 {ROOT}/tests/sync_all_clusters.py',a)
    ok,out=r.sh('build',f'{A} build',a,timeout=2400)
    for _ in range(3):
      fx=("cargo update -p ahash --precise 0.8.11 && sed -i 's/^version = 4/version = 3/' Cargo.lock" if 'stdsimd' in out else "cargo update -p proc-macro2 && sed -i 's/^version = 4/version = 3/' Cargo.lock" if 'SourceFile' in out or 'source_file' in out else None) if not ok else None
      if not fx: break
      r.sh('fix',fx,a); r.steps=[x for x in r.steps if not (x['phase']=='build' and x['cwd']==a)]
      ok,out=r.sh('build',f'{A} build',a,timeout=2400)
    if not ok: continue
    for kp in glob.glob(f'{ad}/target/deploy/*-keypair.json'): progids[os.path.basename(kp)[:-13]]=ver(f'solana address -k {kp}')
    if glob.glob(ad+'/tests/*.ts')+glob.glob(ad+'/tests/*.js'):
      at=open(ad+'/Anchor.toml').read()
      if 'metaqbxx' not in at and subprocess.run(f"grep -rqsE 'mpl-token-metadata|mpl_token_metadata|metaqbxx' {ad}/programs {ad}/tests",shell=True).returncode==0:
        open(ad+'/Anchor.toml','a').write('\n[[test.genesis]]\naddress = "metaqbxxUerdq28cj1RbAWkYQm3ybzjb6a8bt518x1s"\nprogram = "'+os.path.expanduser('~/tbin/mpl_token_metadata.so')+'"\n')
        r.steps.append(dict(phase='configure',cwd=a,cmd='add Metaplex Token Metadata to [[test.genesis]] in Anchor.toml (program bytes dumped read-only from a public cluster)',exit=0,secs=0,tail=''))
      tok,_=r.sh('test',f'{A} test --skip-build --provider.cluster localnet --provider.wallet {ENV["ANCHOR_WALLET"]}',a,timeout=1500)
      led=ad+'/.anchor/test-ledger' if tok else None
    else: led=None
    # Always deploy to a fresh validator (reusing anchor's test-ledger was flaky); wait until it answers before deploying.
    gx=('--bpf-program','metaqbxxUerdq28cj1RbAWkYQm3ybzjb6a8bt518x1s',os.path.expanduser('~/tbin/mpl_token_metadata.so')) if 'metaqbxx' in open(ad+'/Anchor.toml').read() else ()
    led=None
    if validator(True,gx): r.sh('deploy',f'solana airdrop 100 -u localhost >/dev/null; {A} deploy --provider.cluster localnet --provider.wallet {ENV["ANCHOR_WALLET"]}',a,timeout=600)
    else: r.steps.append(dict(phase='deploy',cwd=a,cmd='solana-test-validator did not become ready in 150s',exit=1,secs=150,tail=''))
    for prog,pid in progids.items():
      ok,out=r.sh('verify',f'solana program show {pid} -u localhost && solana transaction-history {pid} -u localhost --limit 20',a,timeout=60)
      if ok and led and os.path.isdir(led): r.steps.append(dict(phase='deploy',cwd=a,cmd='anchor test (deploys to its local validator)',exit=0,secs=0,tail=out.split('\n')[0][:200]))
      r.sigs+=[(prog,pid,x) for x in re.findall(r'^([1-9A-HJ-NP-Za-km-z]{80,90})\s*$',out,re.M)]
    validator(False)
  # cargo (non-anchor) programs / workspaces
  for c in sp.get('cargo',[]): r.sh(c.get('phase','build'),c['cmd'],c.get('cwd','.'),timeout=2400)
  # JS apps
  for a in apps:
    d=f'{r.dir}/{a}'
    try: scripts=json.load(open(d+'/package.json')).get('scripts',{})
    except Exception: continue
    m=pm(d)
    if 'build' in scripts: r.sh('build',f'{RUNC[m]} build',a,timeout=1800)
    if 'test' in scripts and not re.search(r'no test specified|anchor test',scripts['test']): r.sh('test',f'{RUNC[m]} test -- --watchAll=false 2>&1 || {RUNC[m]} test',a,timeout=900) if 'jest' in scripts['test'] else r.sh('test',f'{RUNC[m]} test',a,timeout=900)
  for c in sp.get('run',[]):  # serve and probe
    if c.get('validator'):
      validator(True)
      for _ in range(60):
        if subprocess.run('solana cluster-version -u localhost',shell=True,env=ENV,capture_output=True).returncode==0: break
        time.sleep(1)
      subprocess.run('solana airdrop 100 -u localhost',shell=True,env=ENV,capture_output=True)
    _,out=r.sh('run',c['cmd'].replace('/workspace/sol-college/repo',ROOT),c.get('cwd','.'),timeout=c.get('timeout',300))
    for lab,sig in re.findall(r'^SIG (\S+) ([1-9A-HJ-NP-Za-km-z]{80,90})\s*$',out,re.M): r.sigs.append((lab,'',sig))
    for lab,pid in re.findall(r'^PROGRAM (\S+) ([1-9A-HJ-NP-Za-km-z]{32,44})\s*$',out,re.M): progids[lab]=pid
    if c.get('validator'): validator(False)
  validator(False)
  ph=lambda k:[s for s in r.steps if s['phase']==k]
  ok=lambda k:ph(k) and all(s['exit']==0 for s in ph(k))
  builds_ok=ok('build'); tests_ok=ok('test'); dep_ok=ok('deploy')
  exercised=bool(ok('run')) or bool(ok('test')) or any(s[1]=='' for s in r.sigs)
  status='operational' if builds_ok and exercised and (tests_ok or not ph('test')) and (dep_ok or not anchors) else 'partial' if builds_ok and exercised else 'builds' if builds_ok else 'fails'
  res=dict(name=name,slug=r.slug,fork=p['fork'],commit=p['commit'],tested=time.strftime('%Y-%m-%d'),versions=VERS,anchor_dirs=anchors,apps=apps,program_ids=progids,
    anchor_version=getattr(r,'anchor_version',None),signatures=r.sigs[:12],steps=r.steps,build=('pass' if builds_ok else 'fail' if ph('build') else 'none'),test=('pass' if tests_ok else 'fail' if ph('test') else 'none'),
    deploy=('pass' if dep_ok else 'fail' if ph('deploy') else 'none'),status=status,notes=sp.get('notes',''))
  json.dump(res,open(f'{ROOT}/tests/results/{r.slug}.json','w'),indent=1); r.log.close()
  print(name,status,'build',res['build'],'test',res['test'],'deploy',res['deploy'],'sigs',len(r.sigs),flush=True)
for n in sys.argv[1:]:
  try: run(n)
  except Exception as e: print(n,'ERROR',e,flush=True)
  sl=re.sub(r'[^a-z0-9-]+','-',n.lower())
  for f in glob.glob(f'{B}/{sl}/**/target/idl/*.json',recursive=True)+glob.glob(f'{B}/{sl}/**/target/deploy/*.so',recursive=True)+glob.glob(f'{B}/{sl}/**/target/deploy/*-keypair.json',recursive=True):
    if '/node_modules/' in f: continue
    d=f'{ROOT}/dapps/build/{sl}/'; os.makedirs(d,exist_ok=True); shutil.copy(f,d)
  if not os.environ.get('KEEP'): subprocess.run(f"find {B}/{re.sub(r'[^a-z0-9-]+','-',n.lower())} -maxdepth 6 -type d \\( -name node_modules -o -name target -o -name .next \\) -prune -exec rm -rf {{}} +",shell=True)
