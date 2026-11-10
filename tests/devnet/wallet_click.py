"""Click through a hosted fork app in headless Chromium with an injected test wallet.
The wallet registers through the Wallet Standard as "Phantom" (so both wallet-standard apps and apps that list
PhantomWalletAdapter pick it up) and signs with a devnet test keypair held only by this Python process.
Devnet HTTP RPC and websocket subscriptions from the page are served through a reachable devnet RPC
(the box cannot reach api.devnet.solana.com). Prints one JSON line per step.
Usage: python3 wallet_click.py <app> <base url> <tester keypair.json>   (app: poe | picassol | trustlock | gree)"""
import sys, json, time, base64, threading, urllib.request, re
from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey
from playwright.sync_api import sync_playwright
RPC = 'https://solana-devnet.api.onfinality.io/public'
A = '123456789ABCDEFGHJKLMNPQRSTUVWXYZabcdefghijkmnopqrstuvwxyz'
def b58(b):
    n = int.from_bytes(b, 'big'); s = ''
    while n: n, r = divmod(n, 58); s = A[r] + s
    return '1' * (len(b) - len(b.lstrip(b'\0'))) + s
app, base, kpf = sys.argv[1:4]  # trustlock also takes the beneficiary address as argv[4]
sk = bytes(json.load(open(kpf))); priv = Ed25519PrivateKey.from_private_bytes(sk[:32]); pub = sk[32:]; ADDR = b58(pub)
def log(**o): print(json.dumps(o), flush=True)
def rpc(body):
    for i in range(8):
        try:
            r = urllib.request.urlopen(urllib.request.Request(RPC, body, {'content-type': 'application/json'}), timeout=40).read()
            if b'429' in r and b'error' in r: raise RuntimeError('rate limited')  # public RPC throttle: back off and retry
            return r
        except Exception: time.sleep(1 + i)
    raise RuntimeError('rpc failed')
def cu16(b, i):
    v = s = 0
    while True:
        x = b[i]; i += 1; v |= (x & 0x7f) << s; s += 7
        if not x & 0x80: return v, i
def sign_tx(raw):
    b = bytearray(raw); n, i = cu16(b, 0); msg = bytes(b[i + 64 * n:])
    m = 1 if msg[0] & 0x80 else 0; nk, j = cu16(msg, m + 3)
    keys = [msg[j + 32 * k: j + 32 * (k + 1)] for k in range(nk)]
    idx = keys.index(pub); b[i + 64 * idx: i + 64 * (idx + 1)] = priv.sign(msg); return bytes(b)
SENT = []
def wallet_call(kind, payload):
    if kind == 'signTx': return [base64.b64encode(sign_tx(base64.b64decode(t))).decode() for t in payload]
    if kind == 'signAndSend':
        tx = sign_tx(base64.b64decode(payload))
        r = json.loads(rpc(json.dumps(dict(jsonrpc='2.0', id=1, method='sendTransaction', params=[base64.b64encode(tx).decode(), {'encoding': 'base64'}])).encode()))
        if 'error' in r: raise Exception(json.dumps(r['error'])[:300])
        SENT.append(r['result']); return r['result']
    if kind == 'signMsg': return base64.b64encode(priv.sign(base64.b64decode(payload))).decode()
INIT = r'''(() => {
  const addr = %(addr)s, pk = new Uint8Array(%(pub)s);
  const b64 = u => btoa(String.fromCharCode(...u)), ub64 = s => Uint8Array.from(atob(s), c => c.charCodeAt(0));
  const B58 = '123456789ABCDEFGHJKLMNPQRSTUVWXYZabcdefghijkmnopqrstuvwxyz';
  const de58 = s => { let n = 0n; for (const c of s) n = n * 58n + BigInt(B58.indexOf(c)); const out = []; while (n > 0n) { out.unshift(Number(n & 255n)); n >>= 8n; } for (const c of s) { if (c === '1') out.unshift(0); else break; } return new Uint8Array(out); };
  const chains = ['solana:devnet', 'solana:mainnet', 'solana:testnet', 'solana:localnet'];
  const account = { address: addr, publicKey: pk, chains, features: ['solana:signTransaction', 'solana:signAndSendTransaction', 'solana:signMessage'] };
  const listeners = {};
  const wallet = {
    version: '1.0.0', name: 'Phantom', chains, accounts: [],
    icon: 'data:image/svg+xml;base64,' + btoa('<svg xmlns="http://www.w3.org/2000/svg" width="8" height="8"><rect width="8" height="8" fill="#ab9ff2"/></svg>'),
    features: {
      'standard:connect': { version: '1.0.0', connect: async () => { wallet.accounts = [account]; (listeners.change || []).forEach(f => f({ accounts: wallet.accounts })); return { accounts: wallet.accounts }; } },
      'standard:disconnect': { version: '1.0.0', disconnect: async () => { wallet.accounts = []; } },
      'standard:events': { version: '1.0.0', on: (e, f) => { (listeners[e] = listeners[e] || []).push(f); return () => {}; } },
      'solana:signTransaction': { version: '1.0.0', supportedTransactionVersions: ['legacy', 0], signTransaction: async (...ins) => (await window.__scWallet('signTx', ins.map(x => b64(x.transaction)))).map(s => ({ signedTransaction: ub64(s) })) },
      'solana:signAndSendTransaction': { version: '1.0.0', supportedTransactionVersions: ['legacy', 0], signAndSendTransaction: async (...ins) => { const out = []; for (const x of ins) out.push({ signature: de58(await window.__scWallet('signAndSend', b64(x.transaction))) }); return out; } },
      'solana:signMessage': { version: '1.0.0', signMessage: async (...ins) => { const out = []; for (const x of ins) out.push({ signedMessage: x.message, signature: ub64(await window.__scWallet('signMsg', b64(x.message))) }); return out; } },
    },
  };
  const cb = ({ register }) => register(wallet);
  try { window.dispatchEvent(new CustomEvent('wallet-standard:register-wallet', { detail: cb })); } catch (e) {}
  window.addEventListener('wallet-standard:app-ready', ({ detail }) => cb(detail));
  localStorage.setItem('walletName', JSON.stringify('Phantom'));
})();''' % dict(addr=json.dumps(ADDR), pub=json.dumps(list(pub)))
def http_route(route, req):
    if req.method == 'OPTIONS': return route.fulfill(status=204, headers={'access-control-allow-origin': '*', 'access-control-allow-headers': '*', 'access-control-allow-methods': 'POST'})
    if req.method != 'POST': return route.abort()
    try:
        out = rpc(req.post_data_buffer)
        try:
            if b'sendTransaction' in req.post_data_buffer: SENT.append(json.loads(out)['result'])
        except Exception: pass
        route.fulfill(status=200, body=out, headers={'content-type': 'application/json', 'access-control-allow-origin': '*'})
    except Exception: route.abort()
def ws_route(ws):
    subs = {}; nxt = [1]
    def watch(sid, sig):
        for _ in range(120):
            r = json.loads(rpc(json.dumps(dict(jsonrpc='2.0', id=1, method='getSignatureStatuses', params=[[sig]])).encode()))
            v = r['result']['value'][0]
            if v and v.get('confirmationStatus') in ('confirmed', 'finalized'):
                subs[sid] = ('note', dict(jsonrpc='2.0', method='signatureNotification', params=dict(result=dict(context=dict(slot=v['slot']), value=dict(err=v['err'])), subscription=sid))); return
            time.sleep(1)
    def on_msg(m):
        for o in (lambda x: x if isinstance(x, list) else [x])(json.loads(m)):
            meth = o.get('method', '')
            if 'id' not in o: continue  # ping / keepalive
            if meth.endswith('Unsubscribe'): ws.send(json.dumps(dict(jsonrpc='2.0', id=o['id'], result=True))); continue
            sid = nxt[0]; nxt[0] += 1; ws.send(json.dumps(dict(jsonrpc='2.0', id=o['id'], result=sid)))
            if meth == 'signatureSubscribe': threading.Thread(target=watch, args=(sid, o['params'][0]), daemon=True).start()
    ws.on_message(on_msg); ws._sc = subs
    WSS.append(ws)
WSS = []
def pump(pg, ms):
    end = time.time() + ms / 1000
    while time.time() < end:
        for ws in WSS:
            for sid, v in list(getattr(ws, '_sc', {}).items()):
                if v and v[0] == 'note':
                    try: ws.send(json.dumps(v[1]))
                    except Exception: pass
                    ws._sc[sid] = None
        pg.wait_for_timeout(500)
def connect(pg, label='Select Wallet'):
    if ADDR[:4] in body(pg): return  # autoConnect already picked the injected wallet
    btn = pg.get_by_role('button', name=re.compile(label, re.I)).first
    if not btn.count(): return
    btn.click(); pg.wait_for_timeout(800)
    opt = pg.get_by_text('Phantom', exact=False).last
    if opt.count(): opt.click()
    pump(pg, 2500)
def body(pg): return pg.inner_text('body')
def sigs_new(before): return SENT[before:]
def run(pg):
    if app == 'gree':
        pg.goto(base + '#/gree', wait_until='domcontentloaded'); pump(pg, 4000); connect(pg)
        pump(pg, 3000); n = len(SENT); log(step='connected', text=body(pg)[:200])
        pg.get_by_role('button', name=re.compile('Run program', re.I)).click(); pump(pg, 30000)
        t = body(pg); m = re.search(r'Minted NFT:\s*(\w+)', t); log(step='run_program', minted=m.group(1) if m else None, sent=sigs_new(n), toast=t[:300])
    elif app == 'poe':
        q = 'Clicked through by wallet_click.py ' + time.strftime('%H:%M:%S')
        pg.goto(base + 'create-poll/', wait_until='domcontentloaded'); pump(pg, 5000); connect(pg, 'Connect wallet'); pump(pg, 3000)
        pg.get_by_placeholder(re.compile('Will SOL hit')).fill(q)
        pg.get_by_placeholder(re.compile('Explain exactly')).fill('Created from the hosted app by an injected devnet test wallet.')
        pg.get_by_role('combobox').nth(0).click(); pg.wait_for_timeout(500); pg.get_by_role('option').first.click(); pg.wait_for_timeout(300)
        pg.get_by_role('combobox').nth(1).click(); pg.wait_for_timeout(500); pg.get_by_role('option').first.click(); pg.wait_for_timeout(300)
        n = len(SENT); pg.get_by_role('button', name=re.compile('^Submit$', re.I)).last.click(); pump(pg, 25000)
        log(step='create_poll_via_ui', question=q, sent=sigs_new(n))
        pg.goto(base, wait_until='domcontentloaded'); pump(pg, 8000)
        card = pg.locator('div', has_text=q).filter(has=pg.get_by_role('button', name=re.compile('Submit Estimate'))).last
        th = card.get_by_role('slider')
        log(step='poll_card_found', found=q in body(pg), sliders=th.count())
        if th.count() >= 2:
            th.nth(0).focus(); [pg.keyboard.press('ArrowRight') for _ in range(20)]
            th.nth(1).focus(); [pg.keyboard.press('ArrowLeft') for _ in range(20)]
        elif th.count() == 1:
            th.nth(0).focus(); [pg.keyboard.press('ArrowRight') for _ in range(10)]
        n = len(SENT); card.get_by_role('button', name=re.compile('Submit Estimate')).click(); pump(pg, 25000)
        t = body(pg); i = t.find(q); log(step='submit_estimate_via_ui', sent=sigs_new(n), card=t[i:i+200] if i >= 0 else None)
    elif app == 'picassol':
        pg.goto(base, wait_until='domcontentloaded'); pump(pg, 4000); connect(pg); pump(pg, 10000)
        import random; x, y = random.randint(20, 180), random.randint(20, 180)
        log(step='canvas', cells=pg.locator('td[id^="pixel-"]').count(), target=f'pixel-{x}-{y}')
        n = len(SENT); pg.locator(f'#pixel-{x}-{y}').click(); pump(pg, 25000)
        log(step='click_pixel', x=x, y=y, sent=sigs_new(n), style=pg.locator(f'#pixel-{x}-{y}').get_attribute('style'))
    elif app in ('trustlock', 'trustlock-claim'):
        pg.goto(base, wait_until='domcontentloaded'); pump(pg, 4000); connect(pg, r'\bConnect$'); pump(pg, 6000)
        log(step='connected_dashboard', url=pg.url, text=body(pg)[:300])  # Homepage renders <Dashboard/> once connected
        if app == 'trustlock':
            ben = sys.argv[4]
            pump(pg, 4000); have = pg.get_by_role('button', name=re.compile(r'^Check In')).count()
            for k in range(max(0, 2 - have)):  # escrow 1: check-in then cancel; escrow 2: left for the beneficiary to claim
                pg.get_by_placeholder('Enter Solana address').fill(ben); pg.get_by_placeholder('Enter amount in SOL').fill('0.1')
                n = len(SENT); pg.get_by_role('button', name=re.compile('15s Escrow for testing')).click(); pump(pg, 30000)
                log(step=f'create_15s_escrow_{k+1}', sent=sigs_new(n)); pump(pg, 4000)
            cards = pg.get_by_role('button', name=re.compile(r'^Check In')).count(); log(step='owner_cards', count=cards)
            pg.locator('input[type=number][min="0"]').first.fill('1')  # Days field of the first escrow card
            n = len(SENT); pg.get_by_role('button', name=re.compile(r'^Check In')).first.click(); pump(pg, 25000)
            log(step='check_in_plus_1_day', sent=sigs_new(n))
            n = len(SENT); pg.get_by_role('button', name=re.compile(r'^Cancel')).first.click(); pump(pg, 25000)
            log(step='cancel_refund', sent=sigs_new(n), remaining_cards=pg.get_by_role('button', name=re.compile(r'^Cancel')).count())
        else:
            pump(pg, 5000); btns = pg.get_by_role('button', name=re.compile(r'^Claim')); log(step='claimable', count=btns.count())
            n = len(SENT); btns.last.click(); pump(pg, 25000); log(step='claim', sent=sigs_new(n))
with sync_playwright() as p:
    b = p.chromium.launch(); ctx = b.new_context(viewport={'width': 1280, 'height': 900}); pg = ctx.new_page(); errs = []
    pg.on('pageerror', lambda e: errs.append(str(e)[:200]))
    pg.on('console', lambda m: errs.append('console:' + m.text[:200]) if m.type == 'error' else None)
    ctx.expose_function('__scWallet', wallet_call); ctx.add_init_script(INIT)
    ctx.route(re.compile(r'https://api\.devnet\.solana\.com/?.*'), http_route)
    ctx.route_web_socket(re.compile(r'wss://api\.devnet\.solana\.com/?.*'), ws_route)
    log(step='setup', app=app, wallet=ADDR, url=base)
    try: run(pg)
    finally:
        pg.screenshot(path=f'/tmp/sc-e2e/click-{app}.png'); log(step='done', sent=SENT, errors=errs[:8]); b.close()
