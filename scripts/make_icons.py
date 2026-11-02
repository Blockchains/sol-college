"""Dev-only: regenerate favicons and Open Graph images into static/. Run: python3 scripts/make_icons.py (needs Pillow)."""
from PIL import Image,ImageDraw,ImageFont
import json
BG=(11,10,20); A=(20,241,149); B=(153,69,255)
FB='/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf'; FR='/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf'
def grad(w,h):
  g=Image.new('RGB',(w,h)); px=g.load()
  for x in range(w):
    for y in range(h):
      t=(x/w+y/h)/2; px[x,y]=tuple(int(A[i]+(B[i]-A[i])*t) for i in range(3))
  return g
def mark(size,pad=0.0,round_=True):
  S=size*4; im=Image.new('RGBA',(S,S),(0,0,0,0)); d=ImageDraw.Draw(im)
  d.rounded_rectangle([0,0,S-1,S-1],radius=int(S*0.25) if round_ else 0,fill=BG+(255,))
  m=Image.new('L',(S,S),0); dm=ImageDraw.Draw(m); u=S/64
  for y in (14,29,44):  # three slanted bars, Solana-style
    dm.polygon([(20*u,y*u),(48*u,y*u),(44*u,(y+6)*u),(16*u,(y+6)*u)],fill=255)
  im.paste(grad(S,S),(0,0),m)
  return im.resize((size,size),Image.LANCZOS)
out='static/'
for n,s in [('favicon-16x16.png',16),('favicon-32x32.png',32),('android-chrome-192x192.png',192),('android-chrome-512x512.png',512),('favicon.png',64)]:
  mark(s).save(out+n,optimize=True)
mark(180,round_=False).convert('RGB').save(out+'apple-touch-icon.png',optimize=True)
mark(48).save(out+'favicon.ico',sizes=[(16,16),(32,32),(48,48)])
json.dump({"name":"Sol.College","short_name":"Sol.College","description":"Learn Solana development from real open-source code.","start_url":"/","scope":"/","display":"standalone","background_color":"#0b0a14","theme_color":"#0b0a14","icons":[{"src":"/android-chrome-192x192.png","sizes":"192x192","type":"image/png"},{"src":"/android-chrome-512x512.png","sizes":"512x512","type":"image/png","purpose":"any maskable"}]},open(out+'site.webmanifest','w'),indent=1)
def og(fn,kicker,title):
  W,H=1200,630; im=Image.new('RGB',(W,H),BG); d=ImageDraw.Draw(im)
  bar=grad(W,10); im.paste(bar,(0,H-10))
  im.paste(mark(120),(80,80),mark(120))
  d.text((228,104),'Sol.College',font=ImageFont.truetype(FB,56),fill=(255,255,255))
  d.text((82,250),kicker.upper(),font=ImageFont.truetype(FB,30),fill=A)
  f=ImageFont.truetype(FB,64); words=title.split(); lines=[''];
  for w in words:
    t=(lines[-1]+' '+w).strip()
    if d.textlength(t,font=f)>1040: lines.append(w)
    else: lines[-1]=t
  for i,l in enumerate(lines[:3]): d.text((80,300+i*78),l,font=f,fill=(236,235,255))
  d.text((82,H-70),'sol.college · learn Solana from real code',font=ImageFont.truetype(FR,28),fill=(169,166,201))
  im.quantize(64).save(out+fn,optimize=True)
og('og.png','Learn Solana by example','Build on Solana from real, open-source code')
for k,kick,t in [('learn','Lessons','Annotated Solana lessons from real code'),('explore','Explore','Solana projects by category and framework'),('build','How to build','Setup, Anchor, testing, deploy, security'),('ideas','What to build','Gaps and starter paths in the Solana stack'),('path','Learning path','Learn Solana: a beginner-to-advanced roadmap'),('topics','Topics','DeFi, payments, NFTs, tokens, wallets, Anchor'),('glossary','Glossary','Solana terms explained with real code'),('faq','FAQ','Solana development questions, answered')]:
  og(f'og/{k}.png',kick,t)
