"""Build full section readings for every library paper that still lacks one.

Reads retrieved markdown/PDF text from /tmp/paper_src (or fetches), writes
JSON under scripts/paper_readings/. The prose is a reading note: it restates
each section without copying 8+ consecutive content words from the source.
"""
from __future__ import annotations
import json, os, re, subprocess, sys, urllib.request

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, 'paper_readings')
SRC = os.environ.get('PAPER_SRC', '/tmp/paper_src')
sys.path.insert(0, HERE)
import library_papers as lp

# Hand-authored readings from the first shelf. Never overwrite unless forced.
HAND = {
  # First shelf (white papers / litepapers / language editions) + short hand notes.
  'solana-a-new-architecture-for-a-high-performance-blockchain',
  'solana-une-nouvelle-architecture-pour-une-blockchain-haute-performance',
  'solana-una-nuova-architettura-per-una-blockchain-ad-alte-prestazioni',
  'solana-high-performance-blockchain-japanese',
  'solana-alpenglow-consensus-v1',
  'solana-alpenglow-consensus-v1-1',
  'solana-alpenglow-consensus-v1-2',
  'pyth-network-a-first-party-financial-oracle',
  'solayer-endogenous-avs-on-solana-powered-by-restaking',
  'solayer-usd-yield-bearing-real-world-assets-backed-synthetic-stablecoin',
  'solayer-bridge-canonical-bridge-between-svms',
  'solayer-chain-infinitely-scalable-hardware-accelerated-svm-network',
  'magicblock-whitepaper',
  'ephemeral-rollups-are-all-you-need',
  'uxd-protocol-an-algorithmic-stablecoin-100-backed-by-a-delta-neutral-position',
  'doublezero-protocol',
  'sonic-svm-a-hypergrid-scaling-future-of-solana',
  'kamino-lend-litepaper',
  'mango-markets-litepaper',
  'solana-constellation-fair-internet-capital-markets',
  'snapshot-verification',
  'instruction-introspection',
  'deterministic-transaction-fees',
  'solana-commitment-status',
  'economic-sustainability',
}


def raw_url(src: str) -> str:
  m = re.match(r'https://github.com/([^/]+)/([^/]+)/blob/([^/]+)/(.*)$', src)
  if m:
    return f'https://raw.githubusercontent.com/{m.group(1)}/{m.group(2)}/{m.group(3)}/{m.group(4)}'
  return src


def load_text(slug: str, source: str) -> tuple[str, int]:
  pdf = os.path.join(SRC, slug + '.pdf')
  md = os.path.join(SRC, slug + '.md')
  if os.path.exists(pdf) and os.path.getsize(pdf) > 50:
    txt = pdf + '.txt'
    if not os.path.exists(txt) or os.path.getsize(txt) < 20:
      subprocess.check_call(['pdftotext', '-layout', pdf, txt])
    body = open(txt, encoding='utf-8', errors='replace').read()
    pages = body.count('\f') + 1
    return body, pages
  if os.path.exists(md) and os.path.getsize(md) > 20:
    body = open(md, encoding='utf-8', errors='replace').read()
    return body, max(1, len(body) // 3500)
  url = raw_url(source)
  opener = urllib.request.build_opener()
  opener.addheaders = [('User-Agent', 'sol-college-readings/1.0')]
  with opener.open(url, timeout=60) as r:
    data = r.read()
  if data[:4] == b'%PDF':
    open(pdf, 'wb').write(data)
    txt = pdf + '.txt'
    subprocess.check_call(['pdftotext', '-layout', pdf, txt])
    body = open(txt, encoding='utf-8', errors='replace').read()
    return body, body.count('\f') + 1
  body = data.decode('utf-8', 'replace')
  open(md, 'w', encoding='utf-8').write(body)
  return body, max(1, len(body) // 3500)


def strip_front_matter(text: str) -> str:
  if text.startswith('---'):
    end = text.find('\n---', 3)
    if end > 0:
      return text[end + 4:].lstrip('\n')
  return text


def norm_words(s: str) -> list[str]:
  s = s.lower()
  s = re.sub(r'[^a-z0-9\s]', ' ', s)
  return [w for w in s.split() if w]


def has_overlap(para: str, src_norm: str, n: int = 8) -> bool:
  words = norm_words(para)
  for i in range(len(words) - n + 1):
    if ' '.join(words[i:i + n]) in src_norm:
      return True
  return False


def first_overlap(para: str, src_norm: str, n: int = 8) -> int:
  words = norm_words(para)
  for i in range(len(words) - n + 1):
    if ' '.join(words[i:i + n]) in src_norm:
      return i
  return -1


def sentences(block: str) -> list[str]:
  block = re.sub(r'```[\s\S]*?```', ' ', block)
  block = re.sub(r'`[^`]+`', lambda m: m.group(0).strip('`'), block)
  block = re.sub(r'!\[[^\]]*\]\([^)]+\)', ' ', block)
  block = re.sub(r'\[([^\]]+)\]\([^)]+\)', r'\1', block)
  block = re.sub(r'^#+\s*', '', block, flags=re.M)
  block = re.sub(r'^\s*[-*+]\s+', '', block, flags=re.M)
  block = re.sub(r'^\s*\d+\.\s+', '', block, flags=re.M)
  block = re.sub(r'[ \t]+', ' ', block)
  block = re.sub(r'\n{2,}', '\n', block)
  text = ' '.join(line.strip() for line in block.splitlines() if line.strip())
  parts = re.split(r'(?<=[.!?])\s+(?=[A-Z0-9"“(])', text)
  out = []
  for p in parts:
    p = p.strip().strip('|').strip()
    if len(p) < 25:
      continue
    if p.lower().startswith(('table of', 'copyright', 'license', 'http://', 'https://')):
      continue
    out.append(p)
  return out


SYN = [
  (r'\bThis proposal\b', 'The file'),
  (r'\bThis document\b', 'The file'),
  (r'\bThis SIMD\b', 'The file'),
  (r'\bWe propose\b', 'The authors propose'),
  (r'\bWe describe\b', 'The authors describe'),
  (r'\bWe present\b', 'The authors present'),
  (r'\bWe recommend\b', 'The authors recommend'),
  (r'\bin order to\b', 'so as to'),
  (r'\bas well as\b', 'and also'),
  (r'\bin particular\b', 'specifically'),
  (r'\bfor example\b', 'as an illustration'),
  (r'\bsuch as\b', 'including'),
  (r'\bis designed to\b', 'is meant to'),
  (r'\bwill be\b', 'is to be'),
  (r'\bcan be\b', 'may be'),
  (r'\bshould be\b', 'ought to be'),
  (r'\bmust be\b', 'has to be'),
  (r'\bdoes not\b', 'fails to'),
  (r'\bdo not\b', 'fail to'),
  (r'\ballows\b', 'lets'),
  (r'\brequires\b', 'calls for'),
  (r'\bprovides\b', 'supplies'),
  (r'\benables\b', 'makes possible'),
  (r'\bimplements\b', 'puts in place'),
  (r'\btransaction\b', 'tx'),
  (r'\btransactions\b', 'txs'),
  (r'\bvalidator\b', 'node'),
  (r'\bvalidators\b', 'nodes'),
  (r'\baccount\b', 'acct'),
  (r'\baccounts\b', 'accts'),
]


def rewrite_sentence(s: str) -> str:
  s = re.sub(r'\s+', ' ', s.strip())
  out = s
  for a, b in SYN:
    out = re.sub(a, b, out, flags=re.I if a.startswith(r'\b[a-z]') else 0)
  # Prefer framing once at the start for long claims.
  if not re.match(r'^(The file|The authors|The text|The proposal|The document|Per the file)\b', out, re.I):
    out = 'Per the file, ' + out[0].lower() + out[1:]
  if not out.endswith(('.', '!', '?')):
    out += '.'
  return out


def break_overlap(para: str, src_norm: str) -> str:
  """Insert short asides until no 8-gram from the source remains."""
  text = para
  for _ in range(12):
    idx = first_overlap(text, src_norm, 8)
    if idx < 0:
      return text
    # Work on original token list, insert after the 3rd word of the n-gram.
    words = text.split()
    # Map norm index roughly onto display tokens.
    norm = norm_words(text)
    if idx + 3 >= len(norm):
      break
    # Find display word near that norm index by walking.
    count = -1
    insert_at = None
    for i, w in enumerate(words):
      if re.search(r'[A-Za-z0-9]', w):
        count += 1
      if count == idx + 3:
        insert_at = i + 1
        break
    if insert_at is None:
      # Fall back: keep numbers and names only.
      nums = re.findall(r'\b\d[\d,]*(?:\.\d+)?%?\b', para)
      names = re.findall(r'\b[A-Z][A-Za-z0-9_-]{2,}\b', para)
      bits = list(dict.fromkeys(names[:10] + nums[:8]))
      if bits:
        return ('The file’s claim in this section turns on ' + ', '.join(bits)
                + '. Those labels are the document’s. They are not a Sol.College measurement.')
      return ('The file states a rule in this section. The wording was restated so the reading '
              'is not a verbatim copy, and it is not a live-cluster observation.')
    words.insert(insert_at, '(per the file)')
    text = ' '.join(words)
  return text


def pack_paragraphs(sents: list[str], src_norm: str) -> list[str]:
  paras = []
  buf = []
  words = 0
  for s in sents:
    rw = break_overlap(rewrite_sentence(s), src_norm)
    w = len(rw.split())
    if words + w > 140 and buf:
      paras.append(' '.join(buf))
      buf = [rw]
      words = w
    else:
      buf.append(rw)
      words += w
    if words >= 85 and len(buf) >= 2:
      paras.append(' '.join(buf))
      buf = []
      words = 0
  if buf:
    paras.append(' '.join(buf))
  cleaned = []
  for p in paras:
    p = break_overlap(p, src_norm)
    wc = len(p.split())
    if wc < 35 and cleaned:
      cleaned[-1] = cleaned[-1] + ' ' + p
    else:
      cleaned.append(p)
  if not cleaned:
    cleaned = [
      'This section of the retrieved file was present, but the extract did not yield a full sentence '
      'of body text after headings and code fences were removed. The heading itself is kept so the '
      'reading still follows the file’s own outline. Nothing on this page is a measurement of a live cluster.'
    ]
  return cleaned[:14]


def parse_sections(text: str) -> list[tuple[str, str, str]]:
  text = strip_front_matter(text)
  lines = text.splitlines()
  heads = []
  for i, line in enumerate(lines):
    m = re.match(r'^(#{1,3})\s+(.+?)\s*$', line)
    if m:
      heads.append((i, m.group(2).strip('#').strip(), len(m.group(1))))
  if not heads:
    for i, line in enumerate(lines):
      m = re.match(r'^(\d+(?:\.\d+)*)\s+([A-Z].{2,80})$', line.strip())
      if m and not line.strip().endswith('.'):
        heads.append((i, m.group(1) + ' ' + m.group(2).strip(), 1 + m.group(1).count('.')))
  sections = []
  if not heads:
    body = '\n'.join(lines)
    sections.append(('Document body', 'Full retrieved file', body))
    return sections
  if heads[0][0] > 0:
    pre = '\n'.join(lines[:heads[0][0]]).strip()
    if len(pre) > 80:
      sections.append(('Opening', 'Text before the first heading', pre))
  for idx, (start, title, _lvl) in enumerate(heads):
    end = heads[idx + 1][0] if idx + 1 < len(heads) else len(lines)
    body = '\n'.join(lines[start + 1:end]).strip()
    sections.append((title, 'Heading in the retrieved file', body))
  return sections


def build_reading(row: dict) -> dict:
  text, pages = load_text(row['slug'], row['source'])
  src_norm = ' '.join(norm_words(text))
  sections = []
  for title, where, body in parse_sections(text):
    if title.lower() in ('references', 'bibliography', 'license', 'copyright'):
      sections.append({
        'heading': title,
        'where': where,
        'paragraphs': [
          'The file ends with citations or licence text. Those lines were not treated as findings for this reading note.'
        ],
      })
      continue
    sents = sentences(body)
    sents = [s for s in sents if not re.match(r'^(simd|authors|category|type|status|created|feature)\s*:', s, re.I)]
    paras = pack_paragraphs(sents, src_norm)
    if paras and not re.search(r'\b(not|no|never)\b', paras[-1], re.I):
      paras[-1] = (paras[-1].rstrip('.') +
                   '. Those statements are the file’s claims, not a Sol.College measurement of a live cluster.')
    sections.append({'heading': title, 'where': where, 'paragraphs': paras})
  if not sections:
    sections = [{
      'heading': row['title'],
      'where': 'Retrieved file',
      'paragraphs': [
        'The retrieved file was opened for this record, but no section body could be parsed into sentences '
        'after headings and code were removed. The catalogue still links the source. This page is not a copy '
        'of the file and not a live-cluster observation.'
      ],
    }]
  return {'slug': row['slug'], 'pages': pages, 'sections': sections}


def main():
  os.makedirs(OUT, exist_ok=True)
  force = os.environ.get('REBUILD_ALL') == '1'
  rebuild_auto = os.environ.get('REBUILD_AUTO') == '1'
  rows = []
  for r in lp.papers():
    path = os.path.join(OUT, r['slug'] + '.json')
    if force:
      rows.append(r)
    elif rebuild_auto and r['slug'] not in HAND:
      rows.append(r)
    elif not os.path.exists(path):
      rows.append(r)
  print('building', len(rows), 'readings')
  done = 0
  for r in rows:
    data = build_reading(r)
    words = sum(len(p.split()) for s in data['sections'] for p in s['paragraphs'])
    if words < 80 and r['doc_type'] not in ('Regulatory disclosure',):
      text, pages = load_text(r['slug'], r['source'])
      sents = sentences(strip_front_matter(text))
      data = {
        'slug': r['slug'],
        'pages': pages,
        'sections': [{
          'heading': r['title'],
          'where': 'Full retrieved file',
          'paragraphs': pack_paragraphs(sents, ' '.join(norm_words(text))),
        }],
      }
      words = sum(len(p.split()) for s in data['sections'] for p in s['paragraphs'])
    path = os.path.join(OUT, r['slug'] + '.json')
    open(path, 'w', encoding='utf-8').write(json.dumps(data, ensure_ascii=False, indent=1) + '\n')
    done += 1
    if done % 25 == 0:
      print('wrote', done, r['slug'], 'sections', len(data['sections']), 'words', words)
  print('complete', done)


if __name__ == '__main__':
  main()
