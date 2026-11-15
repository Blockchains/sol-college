"""Public findings (records/public/findings/*.json) for the landing page, /findings/ and /live/.

Honesty rules:
- Every count is computed from the record (never typed into HTML).
- Upstream PR state is refreshed read-only from the GitHub API at build time when a token is
  available (GH_TOKEN/GITHUB_TOKEN); otherwise the recorded state is shown with its date.
- Records must not contain payloads, attacker infrastructure or secrets; build fails closed on secret-shaped text.
"""
from __future__ import annotations
import html, json, os, re, urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
E = lambda s: html.escape(str(s), quote=True)
PR_RE = re.compile(r'^https://github\.com/([^/]+)/([^/]+)/pull/(\d+)$')
SECRET_RE = re.compile(r'(gh[pousr]_[A-Za-z0-9]{20,}|eyJ[A-Za-z0-9_-]{20,}\.[A-Za-z0-9_-]{20,}|-----BEGIN [A-Z ]*PRIVATE KEY|AKIA[0-9A-Z]{16})')
_cache: dict = {}


def load(root=None, refresh=True) -> list[dict]:
    root = Path(root) if root else ROOT
    out = []
    for f in sorted((root / 'records' / 'public' / 'findings').glob('*.json'), reverse=True):
        text = f.read_text(encoding='utf-8')
        if SECRET_RE.search(text):
            raise SystemExit(f'findings: secret-shaped text in {f.name}; refusing to publish')
        d = json.loads(text)
        if refresh:
            for u in d.get('upstreams', []):
                if u.get('pr', {}).get('url'):
                    u['pr'] = {**u['pr'], **_live_state(u['pr']['url'])}
        out.append(d)
    return out


def _live_state(url: str) -> dict:
    tok = os.environ.get('GH_TOKEN') or os.environ.get('GITHUB_TOKEN')
    m = PR_RE.match(url)
    if not tok or not m or os.environ.get('FINDINGS_REFRESH') == '0':
        return {}
    if url in _cache:
        return _cache[url]
    res = {}
    try:
        req = urllib.request.Request(f'https://api.github.com/repos/{m[1]}/{m[2]}/pulls/{m[3]}',
                                     headers={'Authorization': f'Bearer {tok}', 'Accept': 'application/vnd.github+json',
                                              'User-Agent': 'sol-college-findings'})
        with urllib.request.urlopen(req, timeout=15) as r:
            p = json.load(r)
        state = 'merged' if p.get('merged_at') else p.get('state', 'open')
        res = {'state': state, 'checkedAt': (p.get('merged_at') or p.get('closed_at') or '')[:10] or None, 'live': True}
        res = {k: v for k, v in res.items() if v is not None}
    except Exception as e:  # network/API failure: keep the recorded state
        print('findings: could not refresh', url, type(e).__name__)
    _cache[url] = res
    return res


def stats(d: dict) -> dict:
    ups = d.get('upstreams', [])
    prs = [u for u in ups if u.get('pr', {}).get('url')]
    st = lambda s: sum(1 for u in prs if u['pr'].get('state') == s)
    return {
        'repos': len(ups),
        'branches': sum(int(u.get('forkBranchesCleaned') or 0) for u in ups),
        'prs': len(prs), 'open': st('open'), 'merged': st('merged'), 'closed': st('closed'),
        'alreadyClean': sum(1 for u in ups if u.get('status') == 'upstream_already_cleaned'),
        'upstreamInfectedBranches': sum(int(u.get('upstreamBranchesWithSignatures') or 0) for u in prs),
    }


def total_prs(findings) -> int:
    return sum(stats(d)['prs'] for d in findings)


def _state_badge(pr: dict) -> str:
    s = pr.get('state', 'open')
    when = pr.get('checkedAt') or pr.get('recordedAt') or ''
    src = 'live from GitHub' if pr.get('live') else f'recorded {when}'
    return f'<span class="fd-state fd-{E(s)}" title="{E(src)}">{E(s)}</span>'


def landing_cards(findings) -> str:
    out = []
    for d in findings[:1]:
        s = stats(d)
        out.append(
            f'<article class="glass find-card find-sec">'
            f'<p class="tag">Security finding · {E(d["discoveredAt"])}</p>'
            f'<h3>{E(d["shortTitle"])}</h3>'
            f'<p>Our automated review found an injected malware loader in {s["repos"]} Solana project forks. '
            f'We cleaned {s["branches"]} branches and opened {s["prs"]} fix pull requests to the original projects '
            f'({s["merged"]} merged, {s["open"]} open).</p>'
            f'<p><a href="/findings/{E(d["slug"])}/">Read the finding</a> · <a href="/findings/">All findings</a></p>'
            f'</article>')
    return '\n'.join(out)


def proof_card(findings) -> str:
    n = total_prs(findings)
    if not n or not findings:
        return ''
    return (f'<a class="glass proof-card" href="/findings/{E(findings[0]["slug"])}/"><b>{n}</b>'
            f'<span>security fix pull requests opened to original projects</span>'
            f'<small>Counted from recorded PR links in our public findings. Each project decides whether to merge.</small></a>')


def live_section(findings) -> str:
    if not findings:
        return ''
    rows = []
    for d in findings:
        s = stats(d)
        rows.append(f'<li><a href="/findings/{E(d["slug"])}/"><b>{E(d["title"])}</b></a> ({E(d["discoveredAt"])}): '
                    f'{s["repos"]} repos and {s["branches"]} branches cleaned; {s["prs"]} upstream fix PRs '
                    f'({s["merged"]} merged, {s["open"]} open, {s["closed"]} closed).</li>')
    return ('<h2 id=findings>Security findings</h2><p>Proactive findings from Sol.College\'s automated review of the '
            'repositories behind the campus. Fixes are offered upstream as pull requests; projects decide.</p><ul>'
            + ''.join(rows) + '</ul><p><a href="/findings/">All findings</a></p>')


def finding_page(d: dict) -> str:
    s = stats(d)
    rows = []
    for u in d['upstreams']:
        up = E(u['upstream'])
        if u.get('pr', {}).get('url'):
            status = f'<a href="{E(u["pr"]["url"])}">PR #{E(u["pr"]["url"].rsplit("/", 1)[1])}</a> {_state_badge(u["pr"])}'
        else:
            status = f'<span class="fd-state fd-clean">already clean</span> <small>{E(u.get("note", ""))}</small>'
        other = int(u.get('upstreamBranchesWithSignatures') or 0)
        rows.append(f'<tr><td><a href="https://github.com/{up}">{up}</a></td><td>{status}</td>'
                    f'<td>{other} of {int(u.get("upstreamBranchesScanned") or 0)}</td>'
                    f'<td><a href="https://github.com/{E(u["fork"])}">{E(u["fork"].split("/")[1])}</a> · {int(u["forkBranchesCleaned"])}</td></tr>')
    li = lambda xs: '<ul>' + ''.join(f'<li>{E(x)}</li>' for x in xs) + '</ul>'
    return (
        f'<p class=crumbs><a href="/findings/">Findings</a></p>'
        f'<h1>{E(d["title"])}</h1>'
        f'<p class=lead>{E(d["summary"])}</p>'
        f'<div class="fd-stats">'
        f'<div><b>{s["repos"]}</b><span>affected repos found</span></div>'
        f'<div><b>{s["branches"]}</b><span>branches cleaned in our forks</span></div>'
        f'<div><b>{s["prs"]}</b><span>fix PRs opened upstream</span></div>'
        f'<div><b>{s["merged"]}</b><span>merged by the projects</span></div>'
        f'</div>'
        f'<p><small>Discovered {E(d["discoveredAt"])} by {E(d["discoveredBy"])}. Severity: {E(d["severity"])}. '
        f'PR states are {"refreshed from GitHub at build time" if any(u.get("pr", {}).get("live") for u in d["upstreams"]) else "as recorded"}.</small></p>'
        f'<h2>What the malware does</h2>{li(d["behaviour"])}'
        f'<h2>How we found and fixed it</h2><p>{E(d["method"])}</p>'
        f'<p>Our forks: {int(d["ourForks"]["reposCleaned"])} repos, {int(d["ourForks"]["branchesCleaned"])} branches cleaned with normal commits '
        f'(no history rewritten); a re-scan on {E(d["ourForks"]["rescanAt"])} found nothing left. {E(d["ourForks"]["securityIssues"])}</p>'
        f'<h2>Fixes offered to the original projects</h2>'
        f'<p>{s["prs"]} pull requests opened, {s["alreadyClean"]} upstream projects were already clean. '
        f'Still-infected upstream branches beyond the default branch are listed in each PR for the maintainers.</p>'
        f'<div class=fd-table><table><thead><tr><th>Original project</th><th>Status</th><th>Upstream branches with signatures</th><th>Our fork · branches cleaned</th></tr></thead>'
        f'<tbody>{"".join(rows)}</tbody></table></div>'
        f'<h2>If you used one of these repos</h2>{li(d["recommendations"])}'
        f'<h2>Responsible disclosure</h2><p>{E(d["disclosure"])}</p><p><small>{E(d["notAudit"])}</small></p>'
        f'<p><a href="https://github.com/Blockchains/sol-college/blob/main/records/public/findings/{E(d["id"])}.json">Source record (JSON)</a></p>'
    )


CSS = ('<style>.fd-stats{display:grid;grid-template-columns:repeat(auto-fit,minmax(150px,1fr));gap:12px;margin:18px 0}'
       '.fd-stats div{border:1px solid rgba(255,255,255,.12);border-radius:14px;padding:14px 16px}'
       '.fd-stats b{display:block;font-size:2rem;line-height:1.1}.fd-stats span{opacity:.75;font-size:.9rem}'
       '.fd-table{overflow-x:auto}.fd-table table{border-collapse:collapse;width:100%;font-size:.92rem}'
       '.fd-table th,.fd-table td{text-align:left;padding:7px 9px;border-bottom:1px solid rgba(127,127,127,.25);vertical-align:top}'
       '.fd-state{display:inline-block;padding:1px 8px;border-radius:999px;font-size:.78rem;font-weight:700;text-transform:uppercase;letter-spacing:.04em;background:rgba(127,127,127,.2)}'
       '.fd-open{background:rgba(20,241,149,.18)}.fd-merged{background:rgba(153,69,255,.3)}.fd-closed{background:rgba(255,90,90,.2)}.fd-clean{background:rgba(127,127,127,.18)}</style>')


def _wrap(shell: str, body: str, title: str, desc: str, path: str) -> str:
    t = re.sub(r'<main id=main>.*</main>', lambda _: f'<main id=main>{CSS}{body}</main>', shell, count=1, flags=re.S)
    t = re.sub(r'<title>.*?</title>', lambda _: f'<title>{E(title)}</title>', t, count=1, flags=re.S)
    t = re.sub(r'<script type="application/ld\+json">.*?</script>', '', t, flags=re.S)
    t = re.sub(r'(<meta name=description content=")[^"]*', lambda m: m.group(1) + E(desc), t, count=1)
    for a in ('href="https://sol.college/"', 'content="https://sol.college/"'):
        t = t.replace(a, a.replace('https://sol.college/', f'https://sol.college{path}'))
    return t


def write_pages(site, shell: str, findings=None) -> int:
    site = Path(site)
    findings = load() if findings is None else findings
    if not findings or not shell or '<main id=main>' not in shell:
        print('findings: no records or no inner-page shell; pages not written')
        return 0
    idx = ['<h1>Findings</h1><p class=lead>Proactive security and reliability findings from Sol.College\'s automated review. '
           'Each one ends in fixes offered to the projects concerned; the projects decide.</p><ul>']
    for d in findings:
        s = stats(d)
        idx.append(f'<li><a href="/findings/{E(d["slug"])}/"><b>{E(d["title"])}</b></a> — {E(d["discoveredAt"])}. '
                   f'{s["repos"]} repos, {s["branches"]} branches cleaned, {s["prs"]} upstream PRs ({s["merged"]} merged).</li>')
        (site / 'findings' / d['slug']).mkdir(parents=True, exist_ok=True)
        (site / 'findings' / d['slug'] / 'index.html').write_text(
            _wrap(shell, finding_page(d), f'{d["shortTitle"]} | Sol.College findings', d['summary'][:300], f'/findings/{d["slug"]}/'), encoding='utf-8')
    idx.append('</ul>')
    (site / 'findings').mkdir(parents=True, exist_ok=True)
    (site / 'findings' / 'index.html').write_text(
        _wrap(shell, ''.join(idx), 'Findings | Sol.College', 'Security findings from Sol.College and the fixes offered upstream.', '/findings/'), encoding='utf-8')
    sm = site / 'sitemap.xml'
    if sm.exists():
        t = sm.read_text(encoding='utf-8')
        for p in ['/findings/'] + [f'/findings/{d["slug"]}/' for d in findings]:
            if f'https://sol.college{p}</loc>' not in t:
                t = t.replace('</urlset>', f'<url><loc>https://sol.college{p}</loc></url>\n</urlset>')
        sm.write_text(t, encoding='utf-8')
    print('findings: wrote', len(findings), 'finding pages; upstream PRs', total_prs(findings))
    return len(findings)
