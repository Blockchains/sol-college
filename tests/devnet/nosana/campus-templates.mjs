// Sol.College Nosana browser lab: the job templates the campus worker will run (an allow-list). Shared byte-for-byte by
// the browser app (nosana-dashboard fork, app/utils/campusTemplates.ts) and the worker, so both derive the same job
// definition JSON and therefore the same IPFS CIDv0 that goes on-chain in `list`.
export const MEMO_PREFIX = 'sol.college/nosana-job@1 ';
export const RESULT_SCHEMA = 'sol-college/nosana-result@1';
const IMAGE = 'docker.io/library/busybox:1.36';
const base = (id, cmd, extra = {}) => ({
  version: '0.1', type: 'container', meta: { trigger: 'dashboard', lab: 'sol-college-nosana-browser', template: id },
  ops: [{ type: 'container/run', id, args: { image: IMAGE, entrypoint: ['sh', '-c'], cmd: [cmd], ...extra.args }, ...(extra.results ? { results: extra.results } : {}) }],
});
export const TEXT_RE = /^[\x20-\x7E]{1,120}$/;
export const TEMPLATES = {
  'hello-sha256': {
    title: 'Deterministic hash job', description: 'Prints a fixed SHA-256 digest and a sum. Same input, same output on every run.',
    build: () => base('hello-sha256', "echo 'sol.college nosana lab: deterministic job'; printf 'sol.college-lab-fixture-v1' | sha256sum | cut -d' ' -f1 | sed 's/^/digest=/'; seq 1 5 | awk '{s+=$1} END {print \"sum=\" s}'",
      { results: { digest: 'digest=[0-9a-f]{64}', sum: 'sum=[0-9]+' } }),
  },
  'hash-text': {
    title: 'Hash my text', description: 'Your text (1 to 120 printable ASCII characters) is passed to the container as an environment variable and hashed.', param: 'text',
    build: ({ text }) => { if (!TEXT_RE.test(text || '')) throw new Error('text must be 1 to 120 printable ASCII characters');
      return base('hash-text', 'printf \'%s\' "$TEXT" | sha256sum | cut -d\' \' -f1 | sed \'s/^/digest=/\'; printf \'%s\' "$TEXT" | wc -c | sed \'s/^ */chars=/\'',
        { args: { env: { TEXT: text } }, results: { digest: 'digest=[0-9a-f]{64}', chars: 'chars=[0-9]+' } }); },
  },
  'fails-on-purpose': {
    title: 'Failing job (diagnosis practice)', description: 'Writes an error to stderr and exits with code 3, so you can practise diagnosing a failed job.',
    build: () => base('fails-on-purpose', "echo 'about to fail'; echo 'lab error: missing input file /data/in.csv' >&2; exit 3"),
  },
};
export const definitionBytes = (id, params = {}) => { const t = TEMPLATES[id]; if (!t) throw new Error('unknown template ' + id); return JSON.stringify(t.build(params)); };
export const memoFor = (id, params = {}) => MEMO_PREFIX + JSON.stringify(TEMPLATES[id].param ? { t: id, [TEMPLATES[id].param]: params[TEMPLATES[id].param] } : { t: id });
export function parseMemo(s) { if (typeof s !== 'string') return null; const i = s.indexOf(MEMO_PREFIX); if (i < 0) return null;
  try { const o = JSON.parse(s.slice(i + MEMO_PREFIX.length)); if (!TEMPLATES[o.t]) return null; return { id: o.t, params: TEMPLATES[o.t].param ? { [TEMPLATES[o.t].param]: o[TEMPLATES[o.t].param] } : {} }; } catch { return null; } }
