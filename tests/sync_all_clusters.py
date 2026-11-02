"""After `anchor keys sync`: point every [programs.<cluster>] entry in Anchor.toml at the local keypair's address. keys sync only fixes the active cluster."""
import re,subprocess,glob,os
t=open('Anchor.toml').read()
for kp in glob.glob('target/deploy/*-keypair.json'):
  name=os.path.basename(kp)[:-13]; addr=subprocess.run(['solana','address','-k',kp],capture_output=True,text=True).stdout.strip()
  if addr:
    for n in {name,name.replace('_','-'),name.replace('-','_')}:
      t=re.sub(rf'(?m)^(\s*"?{re.escape(n)}"?\s*=\s*")[1-9A-HJ-NP-Za-km-z]{{32,44}}(")',rf'\g<1>{addr}\2',t)
open('Anchor.toml','w').write(t)
