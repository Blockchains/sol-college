"""Throttled filler for an upgradeable-loader buffer account, for rate-limited public RPCs where `solana program deploy`
gives up ("Max retries exceeded"). Reads the buffer, re-sends only chunks that differ from the .so, one tx at a time.
After it reports complete, finish with: solana program deploy --buffer <buffer keypair> --program-id <program keypair> <so>.
Usage: python3 fill_buffer.py <rpc> <authority keypair.json> <buffer pubkey> <program.so>"""
import sys, json, time, base64, struct, urllib.request
from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey
A = '123456789ABCDEFGHJKLMNPQRSTUVWXYZabcdefghijkmnopqrstuvwxyz'
def b58d(s):
    n = 0
    for c in s: n = n * 58 + A.index(c)
    b = n.to_bytes((n.bit_length() + 7) // 8, 'big'); return b'\0' * (len(s) - len(s.lstrip('1'))) + b
def b58e(b):
    n = int.from_bytes(b, 'big'); s = ''
    while n: n, r = divmod(n, 58); s = A[r] + s
    return '1' * (len(b) - len(b.lstrip(b'\0'))) + s
rpc_url, kpf, buf_s, so = sys.argv[1:5]
sk = bytes(json.load(open(kpf))); priv = Ed25519PrivateKey.from_private_bytes(sk[:32]); auth = sk[32:]
buf = b58d(buf_s).rjust(32, b'\0'); loader = b58d('BPFLoaderUpgradeab1e11111111111111111111111')
def rpc(method, params):
    for i in range(30):
        try:
            r = json.loads(urllib.request.urlopen(urllib.request.Request(rpc_url, json.dumps(dict(jsonrpc='2.0', id=1, method=method, params=params)).encode(), {'content-type': 'application/json'}), timeout=40).read())
            if 'result' in r: return r['result']
            if r.get('error', {}).get('code') not in (-32029, 429): return r
        except Exception: pass
        time.sleep(min(2 + i, 15))
    raise RuntimeError('rpc failed ' + method)
data = open(so, 'rb').read(); HDR = 37; CH = 950
def current():
    v = rpc('getAccountInfo', [buf_s, {'encoding': 'base64'}])['value']; return base64.b64decode(v['data'][0])[HDR:]
def write_tx(off, chunk, bh):
    ix = struct.pack('<IIQ', 1, off, len(chunk)) + chunk  # compact-u16 length below: 1 byte under 128 (a 2-byte form is rejected as non-canonical)
    msg = bytes([1, 0, 1]) + bytes([3]) + auth + buf + loader + bh + bytes([1, 2, 2, 1, 0]) + (bytes([len(ix)]) if len(ix) < 128 else bytes([len(ix) & 0x7f | 0x80, len(ix) >> 7])) + ix
    return bytes([1]) + priv.sign(msg) + msg
for rnd in range(6):
    cur = current(); todo = [o for o in range(0, len(data), CH) if cur[o:o + CH] != data[o:o + CH]]
    print(json.dumps(dict(round=rnd, chunks_left=len(todo), total=(len(data) + CH - 1) // CH)), flush=True)
    if not todo: print('BUFFER COMPLETE', flush=True); break
    bh = None; t0 = 0
    for k, o in enumerate(todo):
        if time.time() - t0 > 30: bh = b58d(rpc('getLatestBlockhash', [{'commitment': 'confirmed'}])['value']['blockhash']).rjust(32, b'\0'); t0 = time.time()
        rpc('sendTransaction', [base64.b64encode(write_tx(o, data[o:o + CH], bh)).decode(), {'encoding': 'base64', 'skipPreflight': True}])
        time.sleep(0.25)
        if k % 50 == 0: print(json.dumps(dict(sent=k, of=len(todo))), flush=True)
    time.sleep(20)
