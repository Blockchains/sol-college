"""Click through a hosted fork app in headless Chromium with an injected test wallet.
The wallet registers through the Wallet Standard as "Phantom" (so both wallet-standard apps and apps that list
PhantomWalletAdapter pick it up) and signs with a devnet test keypair held only by this Python process.
Devnet HTTP RPC and websocket subscriptions from the page are served through a reachable devnet RPC
(the box cannot reach api.devnet.solana.com). Prints one JSON line per step.
Usage: python3 wallet_click.py <app> <base url> <tester keypair.json>   (app: poe | picassol | trustlock | gree)"""
import sys, json, time, base64, threading, urllib.request, re, os, pathlib
from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey
from playwright.sync_api import sync_playwright
def _box_rpc():
    """Box-side RPC for the harness (the page still talks to api.devnet.solana.com, which we intercept).
    Prefers SOLANA_RPC, then HELIUS_API_KEY (or /workspace/sol-college/keys/helius.env). Never prints the URL."""
    if os.environ.get('SOLANA_RPC'): return os.environ['SOLANA_RPC']
    k = os.environ.get('HELIUS_API_KEY', '')
    if not k:
        envp = pathlib.Path('/workspace/sol-college/keys/helius.env')
        if envp.exists():
            for line in envp.read_text().splitlines():
                if line.startswith('HELIUS_API_KEY='):
                    k = line.split('=', 1)[1].strip().strip('"').strip("'"); break
    if k: return 'https://devnet.helius-rpc.com/?api-key=' + k
    return 'https://solana-devnet.api.onfinality.io/public'
RPC = _box_rpc()
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
# Legacy injected provider (window.solana / window.phantom.solana, the pre-Wallet-Standard Phantom API) for apps that call it directly
# instead of the wallet adapter (devos: utils/solana.ts passes window.solana to AnchorProvider). It signs web3.js Transaction objects
# by signing serializeMessage() with the same test key; the PublicKey class is taken from the transaction's own instructions.
LEGACY = r'''(() => {
  const addr = %(addr)s, pk = new Uint8Array(%(pub)s);
  const b64 = u => btoa(String.fromCharCode(...u)), ub64 = s => Uint8Array.from(atob(s), c => c.charCodeAt(0));
  const shim = { toBase58: () => addr, toString: () => addr, toBuffer: () => pk, toBytes: () => pk, toJSON: () => addr, equals: o => String(o) === addr };
  const sign = async (tx) => { const PK = tx.instructions[0].programId.constructor; const me = new PK(addr);
    if (!tx.feePayer || String(tx.feePayer) === addr) tx.feePayer = me;
    const sig = ub64(await window.__scWallet('signMsg', b64(tx.serializeMessage()))); tx.addSignature(me, sig); return tx; };
  const p = { isPhantom: true, isConnected: true, publicKey: shim, connect: async () => ({ publicKey: shim }), disconnect: async () => {}, on: () => {}, off: () => {},
    request: async (a) => { if ((a && a.method) === 'connect') return { publicKey: shim }; throw new Error('unsupported ' + (a && a.method)); },
    signTransaction: sign, signAllTransactions: async (txs) => { for (const t of txs) await sign(t); return txs; } };
  window.solana = p; window.phantom = { solana: p };
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
    elif app == 'splitter':  # argv: name mint pda
        name, mint, pda = sys.argv[4:7]
        pg.goto(base + '#/create', wait_until='domcontentloaded'); pump(pg, 4000); connect(pg); pump(pg, 4000)
        log(step='connected', wallet_shown=ADDR[:4] in body(pg))
        pg.get_by_placeholder('Splitter Name').fill(name); pg.get_by_placeholder('Token address').fill(mint)
        pg.get_by_placeholder('Address', exact=True).fill(ADDR); pg.get_by_placeholder('%').fill('100')
        pg.locator('button.btn-square').first.click(); pump(pg, 800)
        n = len(SENT); pg.get_by_role('button', name=re.compile(r'^Create$')).click(); pump(pg, 25000)
        log(step='create_splitter_via_ui', sent=sigs_new(n))
        pg.goto(base + '#/action', wait_until='domcontentloaded'); pump(pg, 5000); connect(pg); pump(pg, 3000)
        pg.get_by_placeholder('Your Splitter PDA').fill(pda); pg.get_by_text('Get it').click(); pump(pg, 6000)
        log(step='get_splitter', text=body(pg)[:600])
        pg.get_by_placeholder(re.compile('Deposite Amount')).fill('25')
        n = len(SENT); pg.locator('a.btn', has_text=re.compile(r'^\s*Deposite\s*$')).click(); pump(pg, 25000)
        log(step='deposit_25_via_ui', sent=sigs_new(n))
        pg.get_by_text('Get it').click(); pump(pg, 5000)
        n = len(SENT); pg.get_by_text(re.compile(r'^\s*Claim\s*$')).first.click(); pump(pg, 25000)
        log(step='claim_via_ui', sent=sigs_new(n))
    elif app == 'orboracle':  # argv: weight mint, oracle PDA (["oracle", wallet, mint])
        mint, oracle = sys.argv[4:6]
        pg.goto(base + 'create/', wait_until='domcontentloaded'); pump(pg, 5000); connect(pg); pump(pg, 4000)
        log(step='connected', wallet_shown=ADDR[:4] in body(pg))
        pg.get_by_placeholder('SOL / USD Oracle').fill('UI test feed'); pg.get_by_placeholder(re.compile("Describe your oracle")).fill('Created by clicking the hosted app')
        pg.get_by_placeholder('Token mint address').fill(mint)
        locks = pg.get_by_placeholder('3600'); locks.nth(1).fill('5'); locks.nth(2).fill('5')
        n = len(SENT); pg.get_by_role('button', name=re.compile(r'Create Oracle')).click(); pump(pg, 25000)
        log(step='create_oracle_via_ui', sent=sigs_new(n), text=body(pg)[body(pg).find('deployed'):][:200])
        pg.goto(base + 'o/?oracle=' + oracle, wait_until='domcontentloaded'); pump(pg, 8000)
        pg.get_by_placeholder('Enter amount to deposit').fill('50')
        n = len(SENT); pg.get_by_role('button', name=re.compile(r'^Deposit Tokens')).click(); pump(pg, 25000)
        log(step='deposit_50_via_ui', sent=sigs_new(n)); pump(pg, 8000)
        pg.get_by_placeholder(re.compile('Enter price value')).fill('123.45')
        n = len(SENT); pg.get_by_role('button', name=re.compile(r'^Submit Value')).click(); pump(pg, 25000)
        log(step='submit_value_via_ui', sent=sigs_new(n), text=body(pg)[:900])
    elif app == 'sentient':  # argv[4]: a short market (ends in minutes) made by sentient-short-market.mjs
        import datetime as dt
        short = sys.argv[4]
        end = (dt.datetime.now() + dt.timedelta(days=1)).replace(second=0, microsecond=0)  # the form's minimum is tomorrow
        pg.goto(base + 'create/', wait_until='domcontentloaded'); pump(pg, 5000); connect(pg); pump(pg, 4000)
        log(step='connected', wallet_shown=ADDR[:4] in body(pg))
        q = 'UI run ' + str(int(time.time()))[-6:] + ' ok?'
        pg.get_by_placeholder('Who will win the 2024 election?').fill(q)
        sides = pg.get_by_placeholder(re.compile(r'^Option \d'))
        sides.nth(0).fill('Yes'); sides.nth(1).fill('No')
        pg.locator('input[type=date]').fill(end.strftime('%Y-%m-%d')); pg.locator('input[type=time]').fill(end.strftime('%H:%M'))
        pg.locator('input[type=number]').last.fill('1')
        n = len(SENT); pg.get_by_role('button', name=re.compile(r'^Create Market')).click(); pump(pg, 30000)
        log(step='create_market_via_ui', question=q, ends=end.isoformat(), sent=sigs_new(n), url=pg.url, text='' if sigs_new(n) else body(pg)[-400:])
        def bet(label):
            pump(pg, 6000)
            pg.get_by_role('button', name=re.compile(r'^\s*Yes')).first.click(); pump(pg, 500)
            pg.get_by_placeholder('0.1').fill('0.1')
            n = len(SENT); pg.get_by_role('button', name=re.compile(r'^Bet .* SOL on Yes')).click(); pump(pg, 25000)
            log(step=label, sent=sigs_new(n))
        bet('bet_0.1_on_Yes_via_ui (market made in the UI)')
        pg.goto(base + 'market/?id=' + short, wait_until='domcontentloaded'); bet('bet_0.1_on_Yes_via_ui (short market)')
        pump(pg, 1000); t_end = int(sys.argv[5])
        while time.time() < t_end + 20: pump(pg, 5000)
        pg.reload(wait_until='domcontentloaded'); pump(pg, 8000)
        if pg.get_by_role('button', name=re.compile(r'Resolve Market')).count():
            n = len(SENT); pg.get_by_role('button', name=re.compile(r'Resolve Market')).click(); pump(pg, 25000)
            log(step='resolve_via_ui', sent=sigs_new(n)); pg.reload(wait_until='domcontentloaded'); pump(pg, 8000)
        btn = pg.get_by_role('button', name=re.compile(r'^Claim [0-9.]+ SOL'))
        if btn.count():
            label = btn.first.inner_text(); n = len(SENT); btn.first.click(); pump(pg, 25000)
            log(step='claim_winnings_via_ui', button=label, sent=sigs_new(n)); pg.reload(wait_until='domcontentloaded'); pump(pg, 8000)
        else: log(step='claim_winnings_via_ui', error='no Claim button', text=body(pg)[:900])
        log(step='final_page', text=body(pg)[:700])
    elif app in ('cipher', 'cipher-approve'):  # cipher argv: owner2 recipient multisig-name; cipher-approve: none
        pg.goto(base, wait_until='domcontentloaded'); pump(pg, 5000); connect(pg, r'Connect Now'); pump(pg, 8000)
        log(step='connected', wallet_shown=ADDR[:4] in body(pg))
        if app == 'cipher':
            owner2, recipient, name = sys.argv[4:7]
            pg.get_by_role('button', name=re.compile(r'^\s*Multisigs')).first.click(); pump(pg, 2000)
            pg.get_by_role('button', name=re.compile(r'New Multisig')).first.click(); pump(pg, 1000)
            pg.get_by_placeholder('e.g., Operations Treasury').fill(name); pg.locator('#threshold').fill('2')
            pg.locator('#balance').fill('1')  # the dialog parses this with parseInt, so fractions of a SOL become 0
            pg.get_by_placeholder('Owner 1 address').fill(ADDR); pg.get_by_placeholder('Owner 2 address').fill(owner2)
            n = len(SENT); pg.get_by_role('button', name=re.compile(r'^Create Multisig')).click(); pump(pg, 30000)
            log(step='create_multisig_2of2_via_ui', sent=sigs_new(n), text=body(pg)[:500])
            pg.get_by_role('button', name=re.compile(r'^\s*Transactions')).first.click(); pump(pg, 3000)
            pg.get_by_role('button', name=re.compile(r'New Transaction')).first.click(); pump(pg, 1000)
            pg.locator('#multisig').click(); pump(pg, 800); pg.get_by_role('option', name=re.compile(name)).first.click(); pump(pg, 500)
            pg.get_by_placeholder('Enter Solana address').fill(recipient); pg.get_by_placeholder('0.00').fill('0.02')
            n = len(SENT); pg.get_by_role('button', name=re.compile(r'Create Transaction')).click(); pump(pg, 30000)
            log(step='propose_0.02_SOL_via_ui', sent=sigs_new(n), text=body(pg)[:700])
        else:
            pg.get_by_role('button', name=re.compile(r'^\s*Transactions')).first.click(); pump(pg, 8000)
            n = len(SENT); pg.get_by_role('button', name=re.compile(r'^Approve$')).first.click(); pump(pg, 30000)
            log(step='approve_via_ui', sent=sigs_new(n)); pump(pg, 8000)
            n = len(SENT); pg.get_by_role('button', name=re.compile(r'^Execute$')).first.click(); pump(pg, 30000)
            log(step='execute_via_ui', sent=sigs_new(n), text=body(pg)[:900])
    elif app == 'colosseum':  # the test wallet is the build's admin: initialise + deposit on /admin/, then stake, try unstake, claim
        pg.goto(base + 'admin/', wait_until='domcontentloaded'); pump(pg, 5000); connect(pg); pump(pg, 5000)
        log(step='connected_admin', wallet_shown=ADDR[:4] in body(pg))
        n = len(SENT); pg.get_by_role('button', name=re.compile(r'^Admin Initialise')).click(); pump(pg, 25000)
        log(step='admin_initialise_via_ui', sent=sigs_new(n))
        pg.locator('input[type=number]').first.fill('0.1')
        n = len(SENT); pg.get_by_role('button', name=re.compile(r'^Admin Deposit')).click(); pump(pg, 25000)
        log(step='admin_deposit_0.1_via_ui', sent=sigs_new(n))
        pg.locator('input[type=number]').last.fill('150')
        n = len(SENT); pg.get_by_role('button', name=re.compile(r'^Admin Config')).click(); pump(pg, 25000)
        log(step='admin_config_apy_150_via_ui', sent=sigs_new(n), text=body(pg)[:400])
        pg.goto(base, wait_until='domcontentloaded'); pump(pg, 6000); connect(pg); pump(pg, 4000)
        pg.locator('input[type=number]').first.fill('0.05'); pg.get_by_role('button', name=re.compile(r'^7 days')).click()
        n = len(SENT); pg.get_by_role('button', name=re.compile(r'^Stake ')).click(); pump(pg, 25000)
        log(step='stake_0.05_for_7_days_via_ui', sent=sigs_new(n))
        n = len(SENT); pg.get_by_role('button', name=re.compile(r'^UnStake ')).click(); pump(pg, 15000)
        log(step='unstake_before_7_days_via_ui (should be rejected)', sent=sigs_new(n), text=body(pg)[-300:])
        pump(pg, 8000)
        n = len(SENT); pg.get_by_role('button', name=re.compile(r'^Get Reward')).click(); pump(pg, 25000)
        log(step='get_reward_via_ui', sent=sigs_new(n)); pg.reload(wait_until='domcontentloaded'); pump(pg, 8000)
        log(step='final_page', text=body(pg)[:800])
    elif app == 'stakes':  # argv: pool mint, a second existing mint for the Create attempt
        mint, other = sys.argv[4:6]
        pg.goto(base + '#/create', wait_until='domcontentloaded'); pump(pg, 5000); connect(pg); pump(pg, 4000)
        log(step='connected', wallet_shown=ADDR[:4] in body(pg))
        pg.get_by_placeholder('Token mint address...').fill(other)
        n = len(SENT); pg.get_by_role('button', name=re.compile(r'^Create$')).click(); pump(pg, 20000)
        log(step='create_pool_via_ui (app IDL has no fee_receiver)', sent=sigs_new(n))
        pg.goto(base + '#/', wait_until='domcontentloaded'); pump(pg, 10000)
        row = pg.get_by_text(mint[:4] + '...' + mint[-4:]).first; row.click(); pump(pg, 3000)
        pg.locator('input[type=number]').first.fill('100')
        n = len(SENT); pg.get_by_role('button', name=re.compile(r'^Stake$')).last.click(); pump(pg, 25000)
        log(step='stake_100_via_ui', sent=sigs_new(n))
        pg.get_by_role('button', name=re.compile(r'^Bribe$')).first.click(); pump(pg, 800)
        pg.locator('input[type=number]').first.fill('20')
        n = len(SENT); pg.get_by_role('button', name=re.compile(r'^Bribe$')).last.click(); pump(pg, 25000)
        log(step='bribe_20_via_ui', sent=sigs_new(n))
        pg.get_by_role('button', name=re.compile(r'^Claim$')).first.click(); pump(pg, 3000)
        n = len(SENT); pg.get_by_role('button', name=re.compile(r'^Unstake$')).click(); pump(pg, 25000)
        log(step='unstake_via_ui', sent=sigs_new(n))
        pump(pg, 6000); pg.goto(base + '#/vesting', wait_until='domcontentloaded'); pump(pg, 10000)
        n = len(SENT); pg.get_by_role('button', name=re.compile(r'^Claim$')).first.click(); pump(pg, 25000)
        log(step='claim_vested_via_ui', sent=sigs_new(n), text=body(pg)[:600])
    elif app == 'stakes-unstake':  # argv: pool mint; unstake from the Claim tab, then claim on #/vesting
        mint = sys.argv[4]
        pg.goto(base + '#/', wait_until='domcontentloaded'); pump(pg, 5000); connect(pg); pump(pg, 10000)
        row = pg.get_by_text(mint[:4] + '...' + mint[-4:]).first; row.click(); pump(pg, 4000)
        pg.get_by_role('button', name=re.compile(r'^Claim$')).first.click(); pump(pg, 4000)
        u = pg.get_by_role('button', name=re.compile(r'^Unstake$'))
        log(step='claim_tab', unstake_buttons=u.count(), enabled=u.first.is_enabled() if u.count() else None, text=body(pg)[:700])
        n = len(SENT); u.first.click(); pump(pg, 25000)
        log(step='unstake_via_ui', sent=sigs_new(n))
        pump(pg, 8000); pg.goto(base + '#/vesting', wait_until='domcontentloaded'); pump(pg, 12000)
        log(step='vesting_page', text=body(pg)[:600])
        n = len(SENT); pg.get_by_role('button', name=re.compile(r'^Claim$')).first.click(); pump(pg, 25000)
        log(step='claim_vested_via_ui', sent=sigs_new(n)); pg.reload(wait_until='domcontentloaded'); pump(pg, 10000)
        log(step='vesting_page_after', text=body(pg)[:600])
    elif app == 'stakes-create':  # argv: an existing mint with no pool yet
        pg.goto(base + '#/create', wait_until='domcontentloaded'); pump(pg, 5000); connect(pg); pump(pg, 4000)
        pg.get_by_placeholder('Token mint address...').fill(sys.argv[4])
        n = len(SENT); pg.get_by_role('button', name=re.compile(r'^Create$')).click(); pump(pg, 20000)
        log(step='create_pool_via_ui', sent=sigs_new(n), text=body(pg)[:300])
    elif app == 'votara':  # the test wallet is the DAO authority (set up by votara.mjs); register, buy, propose, vote, finalize
        pg.goto(base + '#/profile', wait_until='domcontentloaded'); pump(pg, 8000); connect(pg); pump(pg, 6000)
        log(step='connected', wallet_shown=ADDR[:4] in body(pg))
        b = pg.get_by_role('button', name=re.compile(r'Register Voter'))
        if b.count():
            n = len(SENT); b.first.click(); pump(pg, 25000); log(step='register_voter_via_ui', sent=sigs_new(n))
        else: log(step='register_voter_via_ui', note='no Register button (voter already exists)', text=body(pg)[:300])
        pg.goto(base + '#/treasury', wait_until='domcontentloaded'); pump(pg, 8000)
        pg.locator('input[type=number]').first.fill('10')
        n = len(SENT); pg.get_by_role('button', name=re.compile(r'Swap SOL for VTR')).first.click(); pump(pg, 25000)
        log(step='buy_10_tokens_via_ui', sent=sigs_new(n), text=body(pg)[:400] if not sigs_new(n) else '')
        pg.goto(base + '#/create', wait_until='domcontentloaded'); pump(pg, 8000)
        pg.get_by_placeholder(re.compile('e.g. Implement Quadratic')).fill('UI proposal ' + str(int(time.time()))[-5:])
        pg.get_by_placeholder(re.compile('Provide a detailed description')).fill('Made by clicking the hosted app on sol.college')
        n = len(SENT); pg.get_by_role('button', name=re.compile(r'Broadcast Proposal|Register to Propose')).first.click(); pump(pg, 25000)
        log(step='create_proposal_via_ui', sent=sigs_new(n), text=body(pg)[:300] if not sigs_new(n) else ''); t_created = time.time()
        pg.goto(base + '#/proposals', wait_until='domcontentloaded'); pump(pg, 10000)
        pg.get_by_text(re.compile(r'^UI proposal')).first.click(); pump(pg, 6000)
        pg.get_by_role('button', name=re.compile(r'^Yes$')).first.click(); pump(pg, 500)
        n = len(SENT); pg.get_by_role('button', name=re.compile(r'Confirm Yes Vote')).click(); pump(pg, 25000)
        log(step='vote_yes_via_ui', sent=sigs_new(n))
        while time.time() < t_created + 160: pump(pg, 5000)
        f = pg.get_by_role('button', name=re.compile(r'Finalize & Pick Winner'))
        n = len(SENT)
        if f.count(): f.first.click(); pump(pg, 25000)
        log(step='finalize_via_ui', buttons=f.count(), sent=sigs_new(n), text=body(pg)[:900])
    elif app == 'barn':  # argv[4] = step; each step runs as one role (sponsor = tester, dev = tester2)
        step = sys.argv[4]; M = 'https://sol.college/dapps/barn/meta/'
        def popover(trigger, fills, button):
            pg.get_by_text(trigger, exact=True).first.click(); pump(pg, 1500)
            for ph, v in fills: pg.get_by_placeholder(ph).fill(v)
            n = len(SENT); pg.get_by_role('button', name=button, exact=True).last.click(); pump(pg, 25000); return sigs_new(n)
        def press(label):
            b = pg.get_by_role('button', name=label, exact=True)
            if not b.count(): b = pg.get_by_text(label, exact=True)
            if not b.count(): return {'missing': label, 'text': body(pg)[:600]}
            n = len(SENT); b.first.click(); pump(pg, 25000); return sigs_new(n)
        def go(path): pg.goto(base + path, wait_until='domcontentloaded'); pump(pg, 9000)
        go('profile/'); connect(pg); pump(pg, 8000); log(step='connected', wallet_shown=ADDR[:4] in body(pg))
        if step in ('sponsor-setup', 'dev-setup'):
            role = 'sponsor' if step == 'sponsor-setup' else 'dev'
            log(step='create_user_profile_via_ui', sent=popover('Create User Profile', [('Enter username', 'ui-' + role + '-' + str(int(time.time()))[-6:]), ('Enter Profile URI', M + role + '.json')], 'Create'))
            if role == 'sponsor':
                go('admin/'); log(step='approve_sponsor_self_via_ui', sent=popover('Approve Sponsor', [('Enter Sponsor', ADDR)], 'Approve'))
                go('profile/'); log(step='add_grant_program_via_ui', sent=popover('Add Grant Program', [('Grant Program URI', M + 'program.json')], 'Add Grant Program'))
            else:
                go('profile/'); log(step='add_project_via_ui', sent=popover('Add New Project', [('Project URI', M + 'project.json')], 'Add New Project'))
            log(step='profile_page', text=body(pg)[:500])
        elif step == 'award':
            gp, proj = sys.argv[5:7]; go('program/view/?a=' + gp)
            log(step='award_grant_0.01_SOL_via_ui', sent=popover('Award Grant', [('Amount in SOL', '0.01'), ('Enter Project', proj), ('Enter Grant URI', M + 'grant.json')], 'Award Grant'))
        elif step == 'milestone':
            proj = sys.argv[5]; go('project/view/?a=' + proj)
            log(step='add_milestone_0.005_SOL_via_ui', sent=popover('Add New Milestone', [('Amount in SOL', '0.005'), ('Enter Grant URI', M + 'milestone.json')], 'Add New Milestone'))
            go('project/view/?a=' + proj); log(step='review_milestone_via_ui', sent=press('Review'))
        elif step == 'review':
            proj = sys.argv[5]; go('project/view/?a=' + proj); log(step='review_milestone_via_ui', sent=press('Review'))
        elif step == 'settle':
            proj = sys.argv[5]; go('project/view/?a=' + proj)
            log(step='accept_milestone_via_ui', sent=press('Accept'))
            go('project/view/?a=' + proj); log(step='settle_payment_via_ui', sent=press('Settle Payment'))
            go('project/view/?a=' + proj); log(step='project_page', text=body(pg)[:900])
    elif app == 'hpm':  # test wallet = config authority + market creator (set up by hackathon-prediction-market-solana.mjs)
        M = 'https://sol.college/dapps/hackathon-prediction-market-solana/meta/'
        def tab(t):
            pg.keyboard.press('Escape'); pump(pg, 800)
            for b in pg.get_by_role('button', name=re.compile(r'^(✕|×|Close)$')).all():
                try: b.click(timeout=2000)
                except Exception: pass
            pg.get_by_role('button', name=re.compile(t)).first.click(); pump(pg, 6000)
        step = sys.argv[4] if len(sys.argv) > 4 else 'all'  # 'rest' skips Create Market (already done in an earlier run)
        def click_last(t):
            n = len(SENT); pg.get_by_role('button', name=re.compile(t)).last.click(); pump(pg, 30000); return sigs_new(n)
        pg.goto(base, wait_until='domcontentloaded'); pump(pg, 8000); connect(pg); pump(pg, 6000)
        log(step='connected', wallet_shown=ADDR[:4] in body(pg))
        if step == 'all':
          tab('Create Market')
          pg.get_by_placeholder('YES', exact=True).fill('UIYES'); pg.get_by_placeholder('https://example.com/yes-token.json').fill(M + 'yes.json')
          pg.get_by_placeholder('NO', exact=True).fill('UINO'); pg.get_by_placeholder('https://example.com/no-token.json').fill(M + 'no.json')
          pg.get_by_placeholder('MATCH_2024_001').fill('UI' + str(int(time.time()))[-3:])
          ws = pg.get_by_placeholder('Solana Wallet Address'); ids = pg.get_by_placeholder(re.compile('^Steam ID'))
          team = [ADDR, 'SysvarC1ock11111111111111111111111111111111', 'BP1uwSaTHXvgN8sPQJgaor6iBoT3KYjnZNnkvJr71zDv', '11111111111111111111111111111111', 'SysvarRent111111111111111111111111111111111']
          for i in range(5): ws.nth(i).fill(team[i]); ids.nth(i).fill('U' + str(i))
          log(step='create_market_via_ui', sent=click_last('Create Market$'), text=body(pg)[-400:])
          pump(pg, 15000)
        def pick_ui_market():  # choose the market whose option mentions UIYES (the one made through the app), else log the options
            for sel in pg.locator('select').all():
                opts = [(o.get_attribute('value'), o.inner_text()) for o in sel.locator('option').all()]
                hit = [v for v, t in opts if v and 'UIYES' in t]
                log(step='select_options', options=[t[:60] for v, t in opts][:8], picked=hit[-1:] )
                if hit: sel.select_option(hit[-1]); pump(pg, 3000); return True
            return False
        if step != 'resolve':
          tab('Liquidity'); pick_ui_market()
          pg.locator('input[type=number]').first.fill('0.02')
          log(step='add_liquidity_0.02_via_ui', sent=click_last('Add Liquidity'))
          tab('Trade'); pump(pg, 4000); pick_ui_market()
          pg.locator('input[type=number]').first.fill('0.005')
          log(step='buy_yes_0.005_SOL_via_ui', sent=click_last('Buy YES Tokens'))
          pg.get_by_role('button', name=re.compile('Sell')).first.click(); pump(pg, 1500)
          pg.locator('input[type=number]').first.fill('1')
          log(step='sell_1_yes_via_ui', sent=click_last('Sell YES Tokens'), text=body(pg)[-300:])
        tab('Resolution'); pump(pg, 6000)
        sel = pg.locator('select').first; vals = [o.get_attribute('value') for o in sel.locator('option').all()]; vals = [v for v in vals if v]
        log(step='resolution_markets_listed', markets=vals)
        if vals: sel.select_option(vals[-1]); pump(pg, 5000)
        log(step='resolve_team_won_via_ui', sent=click_last('Resolve Market'), text=body(pg)[-500:])
    elif app == 'pulsefund':  # test wallet creates its campaign on /create/, then Contribute on a home card (the app donates 0.2 SOL to the CONNECTED wallet's campaign)
        nm = 'UI campaign ' + str(int(time.time()))[-4:]
        pg.goto(base + 'create/', wait_until='domcontentloaded'); pump(pg, 6000); connect(pg); pump(pg, 4000)
        log(step='connected', wallet_shown=ADDR[:4] in body(pg))
        pg.locator('input[name=name]').fill(nm); pg.locator('textarea[name=description]').fill('Made through the hosted app by the sol.college click test')
        pg.locator('input[name=projectUrl]').fill('https://sol.college/'); pg.locator('input[name=category]').fill('Education')
        pg.locator('input[name=targetAmount]').fill('1000000000')
        n = len(SENT); pg.locator('button[type=submit]').click(); pump(pg, 30000); log(step='create_campaign_via_ui', name=nm, sent=sigs_new(n))
        pg.goto(base, wait_until='domcontentloaded'); pump(pg, 15000); connect(pg); pump(pg, 8000)
        card = pg.locator('div.max-w-sm', has_text=nm)
        log(step='home_lists_campaign', found=card.count(), text=card.first.inner_text()[:200] if card.count() else body(pg)[:300])
        if card.count():
            n = len(SENT); card.first.get_by_role('button', name='Contribute').click(); pump(pg, 30000); log(step='contribute_via_ui (0.2 SOL)', sent=sigs_new(n))
            pg.reload(); pump(pg, 15000); connect(pg); pump(pg, 6000)
            log(step='card_after', text=pg.locator('div.max-w-sm', has_text=nm).first.inner_text()[:200])
    elif app == 'uniproof':  # test wallet = university authority, issues a credential to itself, signs as registrar and dean, then checks /student/ and /verify/
        def btn(rx): return pg.get_by_role('button', name=re.compile(rx, re.I))
        def close_dialog():
            for b in btn(r'^(OK|Close|Got it|Done)$').all():
                try: b.click(timeout=2000)
                except Exception: pass
        pg.goto(base + 'university/', wait_until='domcontentloaded'); pump(pg, 8000); connect(pg); pump(pg, 8000)
        log(step='connected', wallet_shown=ADDR[:4] in body(pg))
        if btn('Initialize University').count():
            pg.get_by_placeholder('e.g., Stanford University').fill('sol.college UI University')
            n = len(SENT); btn('Initialize University').first.click(); pump(pg, 25000); log(step='initialize_university_via_ui', sent=sigs_new(n)); close_dialog(); pump(pg, 5000)
        pg.get_by_placeholder("Student's Solana wallet address").fill(ADDR)
        pg.get_by_placeholder('e.g., Bachelor of Science').fill('Bachelor of Science')
        pg.get_by_placeholder('e.g., Computer Science').fill('Computer Science')
        pg.locator('input[type=date]').first.fill('2026-06-30')
        pg.get_by_placeholder('IPFS or Arweave link to additional data').fill('https://sol.college/')
        n = len(SENT); btn('Issue Credential').last.click(); pump(pg, 25000)
        m = re.search(r'Credential Address:\s*([1-9A-HJ-NP-Za-km-z]{32,44})', body(pg)); cred = m.group(1) if m else None
        log(step='issue_credential_via_ui', sent=sigs_new(n), issued_pda=cred); close_dialog(); pump(pg, 3000)
        if cred:
            pg.get_by_placeholder('Paste credential address here').fill(cred)
            n = len(SENT); btn('Registrar').first.click(); pump(pg, 25000); log(step='sign_as_registrar_via_ui', sent=sigs_new(n)); close_dialog(); pump(pg, 3000)
            pg.get_by_placeholder('Paste credential address here').fill(cred)
            n = len(SENT); btn('Dean').first.click(); pump(pg, 25000); log(step='sign_as_dean_via_ui', sent=sigs_new(n)); close_dialog(); pump(pg, 3000)
            pg.goto(base + 'verify/', wait_until='domcontentloaded'); pump(pg, 6000)
            pg.get_by_placeholder('e.g., 7xKX...').fill(cred); btn('Verify').last.click(); pump(pg, 15000)
            log(step='verify_page', text=body(pg)[:600])
            pg.goto(base + 'student/', wait_until='domcontentloaded'); pump(pg, 8000); connect(pg); pump(pg, 12000)
            log(step='student_page', text=body(pg)[:600])
    elif app == 'friendstake':  # test wallet is maker, opponent and judge: make, take, "Taker wins"; then a second bet made and cancelled
        def btn(rx): return pg.get_by_role('button', name=re.compile(rx, re.I))
        tag = str(int(time.time()))[-4:]
        def make(desc):
            pg.goto(base + 'bet/', wait_until='domcontentloaded'); pump(pg, 6000); connect(pg); pump(pg, 6000)
            btn(r'^Create Bet$').first.click(); pump(pg, 1500)
            pg.get_by_placeholder('Opponent').fill(ADDR); pg.get_by_placeholder('Judge').fill(ADDR)
            pg.get_by_placeholder('Description').fill(desc); pg.get_by_placeholder('Amount').fill('0.01')
            n = len(SENT); btn(r'^Create$').first.click(); pump(pg, 25000); log(step=f'make_via_ui ({desc}, 0.01 SOL)', sent=sigs_new(n))
        def open_bet(desc):
            pg.goto(base + f'list-bets/view/?a={ADDR}', wait_until='domcontentloaded'); pump(pg, 6000); connect(pg); pump(pg, 12000)
            row = pg.locator('tr', has_text=desc).first
            href = row.locator('a[href*="bet/view"]').first.get_attribute('href'); log(step=f'list shows {desc}', href=href)
            row.locator('a[href*="bet/view"]').first.click(); pump(pg, 12000); connect(pg); pump(pg, 8000)
        if len(sys.argv) > 4:  # resume: cancel an existing open bet by its address (argv[4]), e.g. after an RPC 503
            pg.goto(base + f'bet/view/?a={sys.argv[4]}', wait_until='domcontentloaded'); pump(pg, 8000); connect(pg); pump(pg, 10000)
            n = len(SENT); btn(r'^Cancel Bet$').first.click(); pump(pg, 25000); log(step='cancel_via_ui (resumed)', bet=sys.argv[4], sent=sigs_new(n)); return
        make(f'ui-{tag}'); open_bet(f'ui-{tag}')
        n = len(SENT); btn(r'^Take Bet$').first.click(); pump(pg, 25000); log(step='take_via_ui', sent=sigs_new(n))
        pg.reload(); pump(pg, 8000); connect(pg); pump(pg, 8000)
        n = len(SENT); btn(r'^Taker wins$').first.click(); pump(pg, 25000); log(step='settle_taker_wins_via_ui', sent=sigs_new(n))
        make(f'uc-{tag}'); open_bet(f'uc-{tag}')
        n = len(SENT); btn(r'^Cancel Bet$').first.click(); pump(pg, 25000); log(step='cancel_via_ui', sent=sigs_new(n))
    elif app == 'devos':  # Create Election page: election name, one position, two candidates, Submit (create_election, add_position, add_candidate x2)
        pg.goto(base, wait_until='domcontentloaded'); pump(pg, 6000); connect(pg, 'Select Wallet'); pump(pg, 4000)
        log(step='connected_on_home', wallet_shown=ADDR[:4] in body(pg), text=body(pg)[:200])
        pg.goto(base + 'CreateElection/', wait_until='domcontentloaded'); pump(pg, 6000)
        if ADDR[:4] not in body(pg):
            connect(pg); pump(pg, 4000)
        log(step='on_create_election', wallet_shown=ADDR[:4] in body(pg), text=body(pg)[:250])
        name = 'ui-' + str(int(time.time()))[-5:]
        pg.locator('input[type=text]').first.fill(name)
        pg.get_by_role('button', name='Add Position').click(); pump(pg, 800)
        pg.get_by_placeholder('Position Name').first.fill('President')
        pg.get_by_role('button', name='Add Candidate').first.click(); pump(pg, 800)
        c = pg.get_by_placeholder('Candidate Name'); c.nth(0).fill('Alice'); c.nth(1).fill('Bob')
        n = len(SENT); pg.get_by_role('button', name='Submit').click(); pump(pg, 60000)
        log(step=f'submit_election_via_ui ({name}: President = Alice, Bob)', sent=sigs_new(n), success_shown='created successfully' in body(pg))
    elif app == 'gifter':  # DAS-backed token dropdown (mints A,B were funded to the test wallet); Create then Cancel (refund). take is proven by the script.
        pg.goto(base, wait_until='domcontentloaded'); pump(pg, 8000); connect(pg); pump(pg, 8000)
        log(step='connected', wallet_shown=ADDR[:4] in body(pg), text=body(pg)[:400])
        # The escrow list is fetched once on connect and does not auto-refresh; leftover cards (from a prior run) are refunded first.
        n = len(SENT)
        can = pg.get_by_role('button', name=re.compile(r'^Cancel$', re.I))
        if can.count():
            can.first.click(); pump(pg, 30000)
            log(step='cancel_leftover_escrow_via_ui (refund)', sent=sigs_new(n), text=body(pg)[:400])
            pg.reload(wait_until='domcontentloaded'); pump(pg, 8000); connect(pg); pump(pg, 8000)
        # The token form lives in a Dialog behind the Create Escrow trigger.
        pg.get_by_role('button', name=re.compile(r'^Create Escrow$', re.I)).click(); pump(pg, 8000)
        opts = pg.locator('select option').all(); vals = [o.get_attribute('value') for o in opts]
        nonempty = [v for v in vals if v]
        log(step='token_dropdown', option_count=len(opts), nonempty_values=nonempty[:8])
        if len(nonempty) >= 2:
            prefer = ['6yHzRTmukfp7DVAHNAb7hC5NxN6JDnPUSHWm22Exswpu', '13WYoT3wv15uao4pu7kWffJZgbvLyKf8SkEivuLowwJ1']
            give = next((m for m in prefer if m in nonempty), nonempty[0])
            want = next((m for m in prefer if m in nonempty and m != give), next((m for m in nonempty if m != give), nonempty[0]))
            pg.locator('select').nth(0).select_option(give)
            pg.locator('select').nth(1).select_option(want)
            amts = pg.get_by_placeholder('Enter amount')
            amts.nth(0).fill('1'); amts.nth(1).fill('1')
            n = len(SENT); pg.get_by_role('button', name=re.compile(r'^Create$', re.I)).click(); pump(pg, 40000)
            log(step='create_escrow_via_ui (give 1 of token 1, want 1 of token 2)', sent=sigs_new(n), give=give, want=want, text=body(pg)[:400])
            # Close the dialog and reload so the new card is fetched.
            pg.keyboard.press('Escape'); pump(pg, 1000)
            pg.reload(wait_until='domcontentloaded'); pump(pg, 8000); connect(pg); pump(pg, 8000)
            n = len(SENT)
            can = pg.get_by_role('button', name=re.compile(r'^Cancel$', re.I))
            if can.count():
                can.first.click(); pump(pg, 30000)
                log(step='cancel_escrow_via_ui (refund)', sent=sigs_new(n), text=body(pg)[:400])
            else:
                log(step='cancel_escrow_via_ui', sent=[], error='no Cancel button')
        else:
            log(step='create_escrow_via_ui', sent=[], error='token dropdown still empty')
    elif app == 'c4':  # NameGen: Connect Phantom, Init PDA, Generate, Save, Read, Clear
        pg.goto(base, wait_until='domcontentloaded'); pump(pg, 4000); connect(pg, 'Connect Phantom'); pump(pg, 3000)
        log(step='connected', wallet_shown=ADDR[:4] in body(pg), text=body(pg)[:300])
        n = len(SENT)
        pg.get_by_role('button', name='Init').click(); pump(pg, 25000)
        log(step='init_via_ui', sent=sigs_new(n), text=body(pg)[:300])
        pg.get_by_role('button', name='Generate').click(); pump(pg, 1000)
        n = len(SENT)
        pg.get_by_role('button', name='Save').click(); pump(pg, 25000)
        log(step='save_via_ui', sent=sigs_new(n), text=body(pg)[:400])
        pg.get_by_role('button', name='Read').click(); pump(pg, 8000)
        log(step='read_via_ui', text=body(pg)[:400])
        n = len(SENT)
        pg.get_by_role('button', name='Clear').click(); pump(pg, 25000)
        log(step='clear_via_ui', sent=sigs_new(n), text=body(pg)[:400])
with sync_playwright() as p:
    b = p.chromium.launch(); ctx = b.new_context(viewport={'width': 1280, 'height': 900}); pg = ctx.new_page(); errs = []
    pg.on('pageerror', lambda e: errs.append(str(e)[:200]))
    pg.on('console', lambda m: errs.append('console:' + m.text[:200]) if m.type == 'error' or __import__('os').environ.get('SC_DEBUG') else None)
    ctx.expose_function('__scWallet', wallet_call); ctx.add_init_script(INIT)
    if app in ('devos', 'c4'): ctx.add_init_script(LEGACY)
    ctx.route(re.compile(r'https://api\.devnet\.solana\.com/?.*'), http_route)
    ctx.route(re.compile(r'https://[^/]*helius-rpc\.com/.*'), http_route)  # proxy DAS (key is domain-restricted; box RPC is already Helius)
    ctx.route_web_socket(re.compile(r'wss://api\.devnet\.solana\.com/?.*'), ws_route)
    log(step='setup', app=app, wallet=ADDR, url=base)
    try: run(pg)
    finally:
        pg.screenshot(path=f'/tmp/sc-e2e/click-{app}.png'); log(step='done', sent=SENT, errors=errs[:8]); b.close()
