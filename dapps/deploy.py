"""Deploy one fork's built program to devnet (or localnet), run the IDL-driven proof, and record dapps/deployed/<slug>.json.
Usage: python3 dapps/deploy.py <slug> [devnet|localnet]. Never mainnet: the cluster argument is restricted on purpose."""
import json,os,re,subprocess,sys,glob,datetime
slug=sys.argv[1]; cl=sys.argv[2] if len(sys.argv)>2 else 'devnet'
assert cl in ('devnet','localnet'), 'only devnet/localnet are allowed'
RPC={'devnet':'https://api.devnet.solana.com','localnet':'http://127.0.0.1:8899'}[cl]
H=os.path.expanduser; ROOT=os.path.dirname(os.path.dirname(os.path.abspath(__file__))); B=f'{ROOT}/dapps/build/{slug}'
def sh(c,**k): r=subprocess.run(c,shell=True,capture_output=True,text=True,**k); return r.returncode,(r.stdout+r.stderr)
sos=glob.glob(B+'/*.so'); out=dict(slug=slug,cluster=cl,steps=[])
for so in sos:
  name=os.path.basename(so)[:-3]; kp=f'{B}/{name}-keypair.json'; idl=f'{B}/{name}.json'
  if not (os.path.exists(kp) and os.path.exists(idl)): continue
  j=json.load(open(idl))
  pid0=sh(f'solana address -k {kp}')[1].strip()
  if 'address' not in j:
    j.setdefault('metadata',{})['address']=pid0; json.dump(j,open(idl,'w'))  # legacy (<0.30) IDL: convert to the 0.30 spec the dapp's client reads
    c,o=sh(f'{H("~/.avm/bin/anchor-0.30.1")} idl convert {idl} -o {B}/{name}.idl30.json'); idl=f'{B}/{name}.idl30.json' if c==0 else idl
  ov=f'{ROOT}/dapps/overrides/{slug}.json'
  if os.path.exists(ov):  # PDA seeds copied by hand from the program source (legacy IDLs omit them), so the client can derive the accounts
    O=json.load(open(ov)); J=json.load(open(idl))
    for ix in J['instructions']:
      for a in ix['accounts']:
        o=O.get(ix['name']+'.'+a['name']) or O.get(a['name'])
        if o: a['pda']={'seeds':o['seeds']}
    idl=f'{B}/{name}.idl30.json'; json.dump(J,open(idl,'w'),indent=1)
  pid=sh(f'solana address -k {kp}')[1].strip()
  c,o=sh(f'solana program show {pid} -u {RPC}')
  if c: c,o=sh(f'solana program deploy --program-id {kp} {so} -u {RPC} --max-len {os.path.getsize(so)} --max-sign-attempts 50',timeout=1800)
  out['steps'].append(dict(cmd=f'solana program deploy --program-id <{name}-keypair> {name}.so -u {cl}',exit=c,tail=o.strip().split('\n')[-2:]))
  if c: sh(f'solana program close --buffers -u {RPC} --bypass-warning'); continue
  c,o=sh(f'node proof.mjs {idl} {pid} {RPC} {H("~/.config/solana/id.json")}',cwd=f'{ROOT}/dapps/app',timeout=900)
  sigs=[dict(label=a,sig=b) for a,b in re.findall(r'^SIG (\S+) (\S+)$',o,re.M)]
  out.update(program=name,idl=os.path.basename(idl),**{cl:pid},sigs=sigs,skipped=re.findall(r'^SKIP (.*)$',o,re.M),verified=datetime.date.today().isoformat())
  break
os.makedirs(f'{ROOT}/dapps/deployed',exist_ok=True)
f=f'{ROOT}/dapps/deployed/{slug}.json' if cl=='devnet' else f'{ROOT}/dapps/build/{slug}/localnet.json'
prev=json.load(open(f)) if os.path.exists(f) else {}
prev.update(out); json.dump(prev,open(f,'w'),indent=1); print(json.dumps({k:v for k,v in out.items() if k!='steps'},indent=1))
