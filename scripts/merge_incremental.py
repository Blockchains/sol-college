"""Merge an incremental render (site_new/) into the previously deployed site (site/): add only newly published lesson pages."""
import json,os,shutil,re
OLD,NEW='site','site_new'
inc=json.load(open(NEW+'/incr.json')); di=json.load(open('data/incr.json')); cand=di['candidates']; inc['excluded']+=di.get('missing',[])
for path in inc['new']:
  slug=path.strip('/').split('/')[-1]
  for sub in ('explore','dapps'):
    if os.path.isdir(f'{NEW}/{sub}/{slug}'): shutil.copytree(f'{NEW}/{sub}/{slug}',f'{OLD}/{sub}/{slug}',dirs_exist_ok=True)
for f in ('published.json','feed.xml','CHANGELOG.md','new/index.html'): shutil.copy(f'{NEW}/{f}',f'{OLD}/{f}')
newslugs={p.strip('/').split('/')[-1] for p in inc['new']}
pj=json.load(open(OLD+'/projects.json')); have={x['s'] for x in pj}
pj+=[x for x in json.load(open(NEW+'/projects.json')) if x['s'] in newslugs and x['s'] not in have]
json.dump(pj,open(OLD+'/projects.json','w'))
sm=lambda f:re.findall(r'<url>.*?</url>',open(f).read())
old=sm(OLD+'/sitemap.xml'); locs=set(re.findall(r'<loc>(.*?)</loc>',''.join(old)))
add=[u for u in sm(NEW+'/sitemap.xml') if re.search(r'<loc>(.*?)</loc>',u).group(1) not in locs and '/explore/' in u and any(f'/explore/{s}/' in u for s in newslugs)]
open(OLD+'/sitemap.xml','w').write('<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n'+'\n'.join(old+add)+'\n</urlset>\n')
st=json.load(open(OLD+'/build-state.json')) if os.path.exists(OLD+'/build-state.json') else {}
st['excluded']=sorted(set(st.get('excluded',[]))|set(inc['excluded'])); json.dump(st,open(OLD+'/build-state.json','w'))
s=json.load(open(OLD+'/stats.json')); s['projects']=len(pj); s['waiting']=max(0,cand-len(inc['new'])-len(inc['excluded']))
s['pages']=len(locs)+len(add); json.dump(s,open(OLD+'/stats.json','w'))
print('merged new:',len(inc['new']),'excluded:',len(inc['excluded']),'waiting:',s['waiting'])
