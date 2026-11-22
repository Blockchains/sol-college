"""Headless browser check of the Sol.College Nosana dashboard fork (campus build) on devnet.
Connects a Wallet Standard test wallet (it hands each transaction to sign.mjs on the box, so keys never enter the page),
posts template jobs from the UI and waits for the campus worker's verified result.
Usage: python3 ui_test.py <app_url> [key-name] > ui.jsonl"""
import json, subprocess, sys, time, datetime, hashlib
from urllib.parse import urlparse
from playwright.sync_api import sync_playwright
URL = sys.argv[1].rstrip('/') + '/'; WHO = sys.argv[2] if len(sys.argv) > 2 else 'nosana-browser-tester'
D = '/workspace/sol-college/portfolio/nosana/ui'
def log(**o): print(json.dumps({'t': datetime.datetime.utcnow().isoformat() + 'Z', **o}), flush=True)
def pub(name): return subprocess.check_output(['node', 'sign.mjs', name, 'pubkey'], cwd=D, text=True).strip()
INIT = r"""
(() => {
  const ADDR = %(addr)s, PK = Uint8Array.from(%(pk)s);
  const account = { address: ADDR, publicKey: PK, chains: ['solana:devnet'], features: ['solana:signTransaction', 'solana:signMessage'], label: 'lab' };
  const listeners = {};
  const b64 = (u) => btoa(String.fromCharCode(...u)); const unb64 = (s) => Uint8Array.from(atob(s), c => c.charCodeAt(0));
  const wallet = {
    version: '1.0.0', name: 'Lab Test Wallet', icon: 'data:image/svg+xml;base64,PHN2ZyB4bWxucz0iaHR0cDovL3d3dy53My5vcmcvMjAwMC9zdmciLz4=',
    chains: ['solana:devnet'], accounts: [],
    features: {
      'standard:connect': { version: '1.0.0', connect: async () => { wallet.accounts = [account]; (listeners.change||[]).forEach(f => f({ accounts: wallet.accounts })); return { accounts: wallet.accounts }; } },
      'standard:disconnect': { version: '1.0.0', disconnect: async () => { wallet.accounts = []; (listeners.change||[]).forEach(f => f({ accounts: [] })); } },
      'standard:events': { version: '1.0.0', on: (ev, f) => { (listeners[ev] = listeners[ev] || []).push(f); return () => {}; } },
      'solana:signTransaction': { version: '1.0.0', supportedTransactionVersions: ['legacy', 0],
        signTransaction: async (...inputs) => { const out = []; for (const i of inputs) { const s = await window.labSign(b64(i.transaction)); out.push({ signedTransaction: unb64(s) }); } return out; } },
      'solana:signMessage': { version: '1.0.0', signMessage: async (...inputs) => { const out = []; for (const i of inputs) { const s = await window.labSignMessage(b64(i.message)); out.push({ signedMessage: i.message, signature: unb64(s) }); } return out; } },
    },
  };
  const cb = ({ register }) => register(wallet);
  try { window.dispatchEvent(new CustomEvent('wallet-standard:register-wallet', { detail: cb })); } catch (e) {}
  window.addEventListener('wallet-standard:app-ready', ({ detail }) => cb(detail));
})();
"""
def b58decode(s):
    A = '123456789ABCDEFGHJKLMNPQRSTUVWXYZabcdefghijkmnopqrstuvwxyz'; n = 0
    for c in s: n = n * 58 + A.index(c)
    return list(n.to_bytes(32, 'big'))
hosts = set(); fails = 0
with sync_playwright() as p:
    addr = pub(WHO); browser = p.chromium.launch(); ctx = browser.new_context(viewport={'width': 1280, 'height': 1000})
    page = ctx.new_page(); signed = []
    def lab_sign(b64tx): signed.append(1); return subprocess.check_output(['node', 'sign.mjs', WHO], cwd=D, input=b64tx, text=True).strip()
    page.expose_function('labSign', lab_sign)
    page.expose_function('labSignMessage', lambda b64m: subprocess.check_output(['node', 'sign.mjs', WHO, 'message'], cwd=D, input=b64m, text=True).strip())
    page.add_init_script(INIT % {'addr': json.dumps(addr), 'pk': json.dumps(b58decode(addr))})
    page.on('request', lambda r: hosts.add(urlparse(r.url).netloc) if r.url.startswith(('http', 'ws')) else None)
    page.on('console', lambda m: m.type == 'error' and log(console_error=m.text[:300]))
    # 1. markets load without a wallet
    page.goto(URL + '#/campus'); page.get_by_text('base units of practice NOS per second').first.wait_for(timeout=60000)
    log(step='markets page (no wallet)', ok=True, footer_has_source='Blockchains/nosana-dashboard' in page.inner_text('[data-testid=gpl-footer]'))
    page.screenshot(path=f'{D}/ui-markets.png', full_page=True)
    # 2. connect the wallet from the post page
    page.goto(URL + '#/campus/post'); time.sleep(2)
    page.get_by_role('button', name='Select Wallet').first.click() if page.get_by_role('button', name='Select Wallet').count() else page.get_by_text('Connect', exact=False).first.click()
    time.sleep(1); page.get_by_text('Lab Test Wallet').first.click()
    page.locator('[data-testid=wallet-address]').wait_for(timeout=30000); log(step='wallet connected', wallet=addr, badge=page.inner_text('[data-testid=wallet-address]'))
    results = {}
    for tpl, text in [('hash-text', 'Sol.College DeAI lab ' + datetime.datetime.utcnow().strftime('%H:%M:%S')), ('fails-on-purpose', None)]:
        page.goto(URL + '#/campus/post'); page.locator(f'[data-testid=tpl-{tpl}]').check()
        if text: page.locator('[data-testid=job-text]').fill(text)
        time.sleep(1); cid = page.inner_text('[data-testid=def-cid]')
        n0 = len(signed); page.locator('[data-testid=post-job]').click()
        try: page.wait_for_url('**#/campus/jobs/**', timeout=90000)
        except Exception:
            err = page.locator('[data-testid=post-error]'); log(step='post FAILED ' + tpl, error=err.inner_text() if err.count() else None); page.screenshot(path=f'{D}/ui-fail.png', full_page=True); raise
        job = page.url.split('/campus/jobs/')[1]; t0 = time.time()
        log(step=f'UI posted {tpl} job', job=job, definition_cid=cid, signatures_requested=len(signed) - n0)
        page.locator('[data-testid=result-status]').wait_for(timeout=180000)
        st = page.inner_text('[data-testid=result-status]'); ver = page.locator('[data-testid=result-verified]').count() > 0
        vals = [v.inner_text() for v in page.locator('[data-testid=result-value]').all()]
        diag = page.inner_text('[data-testid=diagnosis]') if page.locator('[data-testid=diagnosis]').count() else None
        log(step=f'UI shows result for {tpl}', job=job, state=page.inner_text('[data-testid=job-state]'), status=st, memo_verified=ver, values=vals, diagnosis=diag,
            result_cid=page.inner_text('[data-testid=result-cid]'), seconds=round(time.time() - t0, 1))
        page.screenshot(path=f'{D}/ui-job-{tpl}.png', full_page=True)
        if tpl == 'hash-text':
            want = 'digest=' + hashlib.sha256(text.encode()).hexdigest(); assert st == 'success' and ver and want in vals, (st, ver, vals, want)
        else:
            assert st == 'failed' and ver and diag and 'code 3' in diag
        results[tpl] = job
    page.goto(URL + '#/campus'); time.sleep(6); page.screenshot(path=f'{D}/ui-myjobs.png', full_page=True)
    log(step='your jobs table', rows=page.locator('[data-testid=jobs-table] tbody tr').count())
    browser.close()
log(step='network hosts contacted', hosts=sorted(hosts)); log(step='DONE', jobs=results)
