"""Per-dapp mainnet activation. Each dapp has its own payer wallet at ~/.solcollege/dapp-wallets/<slug>.json (never committed).
When a wallet's mainnet balance covers sol_needed (dapps/mainnet-wallets.json), deploy that dapp's program to mainnet with that
wallet as payer, hand the upgrade authority to the owner (~/.solcollege/upgrade-authority.txt), refund leftover SOL ONLY to that
owner address, flip the dapp's Mainnet mode (dapps/deployed/<slug>.json "mainnet"), log it in dapps/mainnet-live.json, and push.
The shared deploy wallet (~/.solcollege/mainnet-deployer.json) can pay for any dapp instead ("fund everything at once").
Usage: python3 dapps/mainnet_activate.py once            # one mainnet pass
       python3 dapps/mainnet_activate.py dryrun <slug>  # same path on devnet with the slug's devnet twin wallet; writes nothing to the repo"""
import json,os,sys,glob,subprocess,datetime
H=os.path.expanduser; ROOT=os.path.dirname(os.path.dirname(os.path.abspath(__file__))); os.chdir(ROOT)
W=H('~/.solcollege/dapp-wallets'); AUTHF=H('~/.solcollege/upgrade-authority.txt'); SHARED=H('~/.solcollege/mainnet-deployer.json')
REG='dapps/mainnet-wallets.json'
def log(*a): print(datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'),*a,flush=True)
def sh(c,t=1800):
  r=subprocess.run(c,shell=True,capture_output=True,text=True,timeout=t); return r.returncode,(r.stdout+r.stderr).strip()
def bal(addr,rpc):
  c,o=sh(f'solana balance {addr} -u {rpc} --lamports',60); return int(o.split()[0])/1e9 if c==0 else None
def owner():
  if not os.path.exists(AUTHF): return None
  a=open(AUTHF).read().strip()
  return a if 32<=len(a)<=44 and a.isalnum() else None
def deploy(slug,payer,rpc,auth):
  """deploy -> set authority -> refund. Returns dict of signatures/program id or raises."""
  so=glob.glob(f'dapps/build/{slug}/*.so')[0]; kp=so[:-3]+'-keypair.json'
  pid=sh(f'solana address -k {kp}')[1]; out=dict(program=pid)
  c,o=sh(f'solana program show {pid} -u {rpc}',60)
  if c:
    c,o=sh(f'solana program deploy --program-id {kp} {so} -u {rpc} --keypair {payer} --upgrade-authority {payer} --max-len {os.path.getsize(so)} --max-sign-attempts 50 --with-compute-unit-price 1000 --output json')
    if c: sh(f'solana program close --buffers -u {rpc} --keypair {payer} --bypass-warning'); raise RuntimeError('deploy failed: '+o[-300:])
    out['deploy_sig']=(sh(f'solana transaction-history {pid} -u {rpc} --limit 1',60)[1].split() or [None])[0]
  c,o=sh(f'solana program set-upgrade-authority {pid} --new-upgrade-authority {auth} --skip-new-upgrade-authority-signer-check --upgrade-authority {payer} --keypair {payer} -u {rpc} --output json')
  if c and 'Account not upgradeable' not in o: raise RuntimeError('authority transfer failed: '+o[-300:])
  c2,o2=sh(f'solana program show {pid} -u {rpc} --output json',60); a=json.loads(o2).get('authority')
  if a!=auth: raise RuntimeError(f'authority is {a}, expected owner')
  out['authority']=a
  c,o=sh(f'solana transfer {auth} ALL --allow-unfunded-recipient --keypair {payer} -u {rpc} --output json',120)  # leftover -> owner only
  c3,o3=sh(f'solana transaction-history {json.loads(o2)["programdataAddress"]} -u {rpc} --limit 1',60); out['authority_sig']=(o3.split() or [None])[0]
  if c==0: out['refund_sig']=json.loads(o[o.index('{'):]).get('signature')
  return out
def push(msg):
  c,o=sh(f'cd {ROOT} && git add dapps && gitleaks detect --source . --no-banner --redact >/dev/null 2>&1 && git commit -qm "{msg}" && gitleaks detect --source . --no-banner --redact >/dev/null 2>&1 && git pull --rebase -q && gitleaks detect --source . --no-banner --redact >/dev/null 2>&1 && git push -q',600)
  log('push', 'ok' if c==0 else 'FAILED '+o[-200:])
def setstatus(R,slug,st,**k):
  for d in R['dapps']:
    if d['slug']==slug: d['status']=st; d.update(k)
  json.dump(R,open(REG,'w'),indent=1)
def once():
  R=json.load(open(REG)); RPC='https://api.mainnet-beta.solana.com'; auth=owner(); changed=[]
  shared=R['shared_wallet']['address']; sb=bal(shared,RPC) or 0
  for d in R['dapps']:
    if d['status']=='Live on mainnet': continue
    s=d['slug']; b=bal(d['address'],RPC)
    if b is None: continue
    payer=f'{W}/{s}.json' if b>=d['sol_needed'] else (SHARED if sb>=d['sol_needed'] else None)
    if not payer: log(f'{s}: {b:.4f}/{d["sol_needed"]} SOL'); continue
    if not auth:
      if d['status']!='Funded, awaiting owner address': setstatus(R,s,'Funded, awaiting owner address'); changed.append(s)
      log(f'{s}: funded but no owner address; not deploying'); continue
    if payer==SHARED and not os.path.exists(f'{W}/{s}.json'): continue
    log(f'{s}: deploying to mainnet, payer {"shared" if payer==SHARED else "own"} wallet'); setstatus(R,s,'Deploying'); push(f'mainnet: deploying {s}')
    try: r=deploy(s,payer,RPC,auth)
    except Exception as e: log(f'{s}: FAILED {e}'); setstatus(R,s,'Funding',last_error=str(e)[:200]); push(f'mainnet: {s} deploy failed, back to funding'); continue
    if payer==SHARED: sb=bal(shared,RPC) or 0
    f=f'dapps/deployed/{s}.json'; D=json.load(open(f)) if os.path.exists(f) else dict(slug=s)
    D['mainnet']=r['program']; json.dump(D,open(f,'w'),indent=1)
    L=json.load(open('dapps/mainnet-live.json')) if os.path.exists('dapps/mainnet-live.json') else []
    L.append(dict(slug=s,program=r['program'],published=datetime.datetime.utcnow().strftime('%Y-%m-%dT%H:%M:%SZ'),deploy_sig=r.get('deploy_sig'),type='live-mainnet'))
    json.dump(L,open('dapps/mainnet-live.json','w'),indent=1)
    setstatus(R,s,'Live on mainnet',mainnet_program=r['program'],deploy_sig=r.get('deploy_sig')); push(f'mainnet: {s} live on mainnet ({r["program"]})')
    log(f'{s}: LIVE {r}')
def dryrun(s):
  R=json.load(open(REG)); d=next(x for x in R['dapps'] if x['slug']==s); RPC='https://api.devnet.solana.com'
  twin=f'{W}/{s}-devtwin.json'; b=bal(d['devnet_twin'],RPC); need=d['sol_needed']
  log(f'DRYRUN {s}: devnet twin balance {b} need {need}')
  if b<need: log('DRYRUN: underfunded, status stays Funding'); return
  auth=owner()
  if not auth: log('DRYRUN: funded but no owner address -> would mark "Funded, awaiting owner address"'); return
  r=deploy(s,twin,RPC,auth); log('DRYRUN deploy/authority/refund:',json.dumps(r))
  tmp=f'/tmp/dryrun-{s}'; os.makedirs(tmp,exist_ok=True)
  D=dict(slug=s); D['mainnet']=r['program']; json.dump(D,open(f'{tmp}/deployed.json','w'),indent=1)
  log(f'DRYRUN mode flip written to {tmp}/deployed.json (not pushed):',json.dumps(D))
if __name__=='__main__':
  {'once':lambda:once(),'dryrun':lambda:dryrun(sys.argv[2])}[sys.argv[1]]()
