"""Learning-product vertical slice: front door, preflight, focused loop, stuck help.

Static HTML + client JS (lesson.js / landing.js). No server state.
"""
from __future__ import annotations

from html import escape as E


def start_section_html():
  """Homepage front door: three routes + short recommender (wired in landing.js)."""
  return '''
<section class="band" id="start">
  <div class="inner">
    <p class="eyebrow">Front door</p>
    <h2>Find the right first lesson in two minutes</h2>
    <p class="lead">Multiple catalogues are fine. Multiple unexplained “first” choices are not. Pick a route — or answer four questions and get one recommendation. No wallet required.</p>
    <div class="start-routes" role="list">
      <a class="start-route" role="listitem" href="/lessons/first-transaction/">
        <b>New to Solana</b>
        <span>I want to understand wallets, transactions, and accounts.</span>
        <em>Start: Foundations 001</em>
      </a>
      <a class="start-route" role="listitem" href="/lessons/picassol-hackathon/">
        <b>Already a developer</b>
        <span>I write code and want to learn Solana’s model on a live app.</span>
        <em>Start: Picassol application lab</em>
      </a>
      <a class="start-route" role="listitem" href="/lessons/#challenges">
        <b>Here to investigate</b>
        <span>I want to test, debug, or review an application.</span>
        <em>Start: Debug laboratory</em>
      </a>
    </div>
    <p class="path-extras"><a href="/lessons/">Browse everything</a> · <a href="/lessons/path/">Learning path</a></p>

    <details class="start-quiz" id="start-quiz">
      <summary>Or answer four questions for a recommendation</summary>
      <form id="start-form" class="start-form">
        <fieldset>
          <legend>1. Have you submitted and inspected a Solana transaction?</legend>
          <label><input type="radio" name="q1" value="no" required> No</label>
          <label><input type="radio" name="q1" value="yes"> Yes</label>
        </fieldset>
        <fieldset>
          <legend>2. Can you explain the difference between an account and a program?</legend>
          <label><input type="radio" name="q2" value="no" required> Not yet</label>
          <label><input type="radio" name="q2" value="yes"> Yes</label>
        </fieldset>
        <fieldset>
          <legend>3. Are you comfortable reading TypeScript or Rust?</legend>
          <label><input type="radio" name="q3" value="no" required> Not really</label>
          <label><input type="radio" name="q3" value="yes"> Yes</label>
        </fieldset>
        <fieldset>
          <legend>4. Do you want guided practice or an independent challenge?</legend>
          <label><input type="radio" name="q4" value="guided" required> Guided practice</label>
          <label><input type="radio" name="q4" value="challenge"> Independent challenge</label>
        </fieldset>
        <p class="cta-row">
          <button type="submit" class="btn">Recommend a starting point</button>
          <button type="reset" class="btn ghost">Clear</button>
        </p>
      </form>
      <div class="start-result" id="start-result" hidden>
        <p class="eyebrow">Recommended starting point</p>
        <h3 id="start-result-title"></h3>
        <p id="start-result-why"></p>
        <p class="cta-row">
          <a class="btn" id="start-result-go" href="#">Start</a>
          <a class="btn ghost" href="/lessons/">Choose another route</a>
        </p>
      </div>
    </details>
  </div>
</section>
'''


def preflight_html(app_href: str, title: str = 'this lab') -> str:
  """Reusable setup gate before practical mode."""
  app = E(app_href)
  t = E(title)
  return f'''
<section class="preflight" id="preflight" data-learning="preflight">
  <p class="eyebrow">Preflight</p>
  <h2>Ready for {t}?</h2>
  <p>Setup must not consume confidence before the lesson. You can read everything in observation mode without a wallet.</p>
  <ul class="preflight-ready">
    <li>You can read the lesson without a wallet</li>
    <li>Correct application environment: <b>Devnet</b></li>
    <li>Supported browser: modern Chromium, Firefox, or Safari</li>
  </ul>
  <div class="preflight-modes" role="group" aria-label="Practice mode">
    <button type="button" class="btn" data-mode="observe">Use observation mode</button>
    <button type="button" class="btn ghost" data-mode="practical">Guided practical setup</button>
  </div>
  <div class="preflight-practical" id="preflight-practical" hidden>
    <p><b>When you choose practical mode:</b></p>
    <ul>
      <li>Connect a <b>separate practice wallet</b> set to Devnet (never a mainnet seed you care about)</li>
      <li>Confirm sufficient practice balance for the estimated costs in this lesson</li>
      <li>Faucet availability varies — if funding fails, stay in observation mode; faucet access is not graded</li>
      <li>Open the practice app in a tab you can return from: <a href="{app}" target="_blank" rel="noopener">Open practice app</a></li>
    </ul>
    <p class="note">“Not connected” is different from “unsupported wallet.” An RPC error is not the same as insufficient funds. Do not buy tokens to bypass a faucet problem.</p>
  </div>
  <p class="preflight-status" id="preflight-status" aria-live="polite"></p>
</section>
'''


def stuck_html() -> str:
  return '''
<section class="stuck" id="stuck" data-learning="stuck">
  <p class="eyebrow">Stuck</p>
  <h2>What is stopping you?</h2>
  <div class="stuck-choices" role="list">
    <button type="button" role="listitem" data-stuck="concept">I do not understand the concept</button>
    <button type="button" role="listitem" data-stuck="wallet">My wallet is not working</button>
    <button type="button" role="listitem" data-stuck="tx">The transaction result is unclear</button>
    <button type="button" role="listitem" data-stuck="ui">The application looks different</button>
    <button type="button" role="listitem" data-stuck="diff">My result differs from the example</button>
    <button type="button" role="listitem" data-stuck="a11y">I need accessibility support</button>
  </div>
  <div class="stuck-panel" id="stuck-panel" hidden></div>
  <aside class="attempt-recovery" id="attempt-recovery" data-learning="attempt">
    <h3>Attempt recovery</h3>
    <p>Timeout, rejection, failure, and success need different next steps. Do not send a second transaction until you know what happened to the first.</p>
    <label class="loop-opt">Intended operation
      <input type="text" id="attempt-op" placeholder="e.g. create_pixel at (12, 34)" autocomplete="off">
    </label>
    <label class="loop-opt">Network
      <select id="attempt-network">
        <option value="devnet">Devnet</option>
        <option value="other">Other / unsure</option>
      </select>
    </label>
    <label class="loop-opt">Status
      <select id="attempt-status">
        <option value="">Not recorded</option>
        <option value="wallet_rejected">Wallet rejected / closed (not submitted)</option>
        <option value="submitted_unknown">Submitted — result unknown / timed out</option>
        <option value="pending">Pending / still processing</option>
        <option value="failed">Failed on-chain (execution error)</option>
        <option value="confirmed">Confirmed success</option>
      </select>
    </label>
    <label class="loop-opt">Signature if known
      <input type="text" id="attempt-pending-sig" placeholder="Base58 signature" autocomplete="off">
    </label>
    <p class="note" id="attempt-guidance" hidden></p>
    <p class="cta-row">
      <button type="button" class="btn" id="attempt-save">Save attempt state</button>
      <a class="btn ghost" id="attempt-explorer" href="https://explorer.solana.com/?cluster=devnet" target="_blank" rel="noopener">Open Explorer (devnet)</a>
    </p>
    <p class="lab-save" id="attempt-save-status" aria-live="polite"></p>
  </aside>
</section>
'''


def _opt(value: str, label: str) -> str:
  return f'<label class="loop-opt"><input type="radio" name="loop-predict" value="{E(value)}"> {E(label)}</label>'


def workspace_html(
  loop: dict,
  app_href: str,
  platform_sigs: list | None = None,
  *,
  content_version: str = '',
  assess_href: str = '',
) -> str:
  """Focused Predict → Act → Inspect → Explain → Transfer workspace."""
  if not loop:
    return ''
  objective = E(loop.get('objective') or 'Complete one focused task')
  predict_q = E(loop.get('predict_question') or 'What do you expect to happen?')
  options = loop.get('predict_options') or []
  opts = ''.join(_opt(o.get('id', str(i)), o.get('label', '')) for i, o in enumerate(options))
  predict_ok = E(loop.get('predict_answer') or '')
  predict_why = loop.get('predict_why') or ''
  act = loop.get('act') or ''
  inspect_fields = loop.get('inspect') or []
  inspect_rows = ''.join(
    f'<tr><th>{E(r.get("label",""))}</th><td><input type="text" data-inspect="{E(r.get("id",""))}" '
    f'placeholder="{E(r.get("placeholder",""))}" autocomplete="off"></td></tr>'
    for r in inspect_fields
  )
  explain_q = E(loop.get('explain_question') or 'Why did that happen?')
  transfer = loop.get('transfer') or ''
  hist = ''
  if platform_sigs:
    items = ''.join(
      f'<li><span class="ev-tag">Platform historical</span> {E(a)} — '
      f'<a href="https://explorer.solana.com/tx/{E(s)}?cluster=devnet"><code>{E(s[:16])}…</code></a></li>'
      for a, s in platform_sigs[:4] if s
    )
    hist = (
      '<ul class="ev-list">' + items + '</ul>'
      '<p class="note">These are Sol.College records, not your completion proof.</p>'
    )
  app = E(app_href)
  ver = E(content_version or '')
  assess = E(assess_href or '#exercises')
  assess_label = 'Open assessment rubric' if assess_href else 'Open full exercises'
  def p(text):
    return f'<p>{E(text)}</p>' if text else ''

  return f'''
<section class="lab-workspace" id="workspace" data-learning="workspace" data-predict-answer="{predict_ok}" data-content-version="{ver}">
  <div class="lab-version-banner" id="lab-version-banner" hidden role="status"></div>
  <header class="lab-bar">
    <div>
      <p class="eyebrow">Application lab workspace</p>
      <h2 id="workspace-title">{objective}</h2>
    </div>
    <p class="lab-save" id="lab-save" aria-live="polite">Not saved yet on this device</p>
  </header>
  <div class="lab-grid">
    <nav class="lab-steps" aria-label="Learning loop">
      <ol>
        <li><button type="button" data-loop-step="prepare" class="is-current">Prepare</button></li>
        <li><button type="button" data-loop-step="predict">Predict</button></li>
        <li><button type="button" data-loop-step="act">Act</button></li>
        <li><button type="button" data-loop-step="inspect">Inspect</button></li>
        <li><button type="button" data-loop-step="explain">Explain</button></li>
        <li><button type="button" data-loop-step="transfer">Demonstrate</button></li>
      </ol>
      <p class="note">Ticks below mean <b>step visited</b> or <b>you marked done</b> — not proof of mastery. Assessment is separate.</p>
    </nav>
    <div class="lab-main">
      <div class="loop-panel" data-panel="prepare">
        <h3>Prepare</h3>
        <p>Complete <a href="#preflight">preflight</a>. Choose observation or practical mode. Then continue to Predict.</p>
        <button type="button" class="btn" data-loop-next="predict">Continue to Predict</button>
      </div>
      <div class="loop-panel" data-panel="predict" hidden>
        <h3>Predict</h3>
        <p>{predict_q}</p>
        <div class="loop-options">{opts}</div>
        <button type="button" class="btn" data-loop-check-predict>Lock prediction</button>
        <p class="loop-feedback" id="predict-feedback" hidden></p>
        <p class="note" id="predict-why" hidden>{E(predict_why)}</p>
        <button type="button" class="btn ghost" data-loop-next="act" hidden id="predict-continue">Continue to Act</button>
      </div>
      <div class="loop-panel" data-panel="act" hidden>
        <h3>Act</h3>
        {p(act)}
        <p class="cta-row">
          <a class="btn" href="{app}" target="_blank" rel="noopener">Open practice app</a>
          <button type="button" class="btn ghost" data-loop-mark="act">I completed the allowed action</button>
        </p>
        <button type="button" class="btn" data-loop-next="inspect">Continue to Inspect</button>
      </div>
      <div class="loop-panel" data-panel="inspect" hidden>
        <h3>Inspect</h3>
        <p>Record what you observed. Distinguish <b>platform historical evidence</b> from <b>your attempt</b>.</p>
        <table class="inspect-table"><tbody>{inspect_rows}</tbody></table>
        <label class="loop-opt">Evidence route:
          <select id="evidence-route">
            <option value="observe">Captured / observation</option>
            <option value="live">Live practical (my wallet)</option>
            <option value="local">Local test</option>
            <option value="guided">Guided investigation</option>
          </select>
        </label>
        <label class="loop-opt">Public signature (optional)
          <input type="text" id="attempt-sig" data-inspect="sig" placeholder="Base58 signature if you sent one" autocomplete="off">
        </label>
        <p class="note" id="inspect-stale" hidden>Restored observation notes may be stale — shared canvas state can change. Re-check account existence before treating Create/Update as current.</p>
        <button type="button" class="btn" data-loop-mark="inspect">Save inspection notes</button>
        <button type="button" class="btn ghost" data-loop-next="explain">Continue to Explain</button>
      </div>
      <div class="loop-panel" data-panel="explain" hidden>
        <h3>Explain</h3>
        <p>{explain_q}</p>
        <textarea id="loop-explain" rows="5" placeholder="Write your explanation in your own words…"></textarea>
        <button type="button" class="btn" data-loop-mark="explain">Save explanation</button>
        <button type="button" class="btn ghost" data-loop-next="transfer">Continue to Demonstrate</button>
      </div>
      <div class="loop-panel" data-panel="transfer" hidden>
        <h3>Demonstrate</h3>
        {p(transfer)}
        <label class="loop-opt">Outcome
          <select id="loop-outcome">
            <option value="">Not yet assessed</option>
            <option value="independent">Completed independently</option>
            <option value="support">Completed with support</option>
            <option value="practice">Further practice needed</option>
            <option value="paused">Assessment paused</option>
          </select>
        </label>
        <p class="note">Self-marked outcome is a draft. Independent completion requires the <a href="{assess}">assessment rubric</a>.</p>
        <button type="button" class="btn" data-loop-mark="transfer">Save demonstration status</button>
        <p class="cta-row">
          <a class="btn" href="{assess}">{assess_label}</a>
          <a class="btn ghost" href="#proof">Platform proof records</a>
          <a class="btn ghost" href="/lessons/path/">Choose next step</a>
        </p>
      </div>
    </div>
    <aside class="lab-evidence" aria-label="Evidence drawer">
      <h3>Evidence drawer</h3>
      <p class="note">Tag every item by provenance. Platform history is not your completion proof.</p>
      {hist or '<p class="note">No platform signatures attached.</p>'}
      <h4>Your attempt</h4>
      <p><span class="ev-tag" id="ev-route-tag">Unspecified</span></p>
      <dl class="ev-attempt" id="ev-attempt">
        <dt>Mode</dt><dd id="ev-mode">Not chosen</dd>
        <dt>Prediction</dt><dd id="ev-predict">—</dd>
        <dt>Route</dt><dd id="ev-route">—</dd>
        <dt>Signature</dt><dd id="ev-sig">—</dd>
        <dt>Observed at</dt><dd id="ev-observed">—</dd>
        <dt>Attempt status</dt><dd id="ev-attempt-status">—</dd>
        <dt>Outcome</dt><dd id="ev-outcome">—</dd>
      </dl>
      <p><a href="#stuck">I am stuck</a> · <a href="#attempt-recovery">Attempt recovery</a></p>
    </aside>
  </div>
  <nav class="lab-mobile-tabs" aria-label="Mobile workspace tabs">
    <a href="#workspace">Learn</a>
    <a href="{app}" target="_blank" rel="noopener">Practise</a>
    <a href="#proof">Evidence</a>
  </nav>
</section>
'''


def _hosted_ui_label(ui_check: str) -> str:
  t = (ui_check or '').lower()
  if not t:
    return 'Unspecified — see Proof for method details.'
  if 'not yet' in t or ('script' in t and 'ui' in t):
    return 'Partial: some steps are script-verified; hosted UI may still be open.'
  if 'clicked' in t or 'hosted' in t or 'browser' in t or 'phantom' in t:
    return 'Hosted UI notes recorded (not a live uptime claim).'
  return 'Method notes recorded (see Proof).'


def environment_panel_html(verified: str = '', ui_check: str = '') -> str:
  v = E(verified or 'unknown')
  ui = E(ui_check or 'See lesson Proof for method details.')
  hosted = E(_hosted_ui_label(ui_check))
  return f'''
<aside class="env-health" id="env-health">
  <p class="eyebrow">Environment health</p>
  <p>Separate from your performance. A broken lab is not a failed student. These labels are not live uptime.</p>
  <dl class="facts">
    <dt>Program flow</dt><dd>Last recorded reproduction: {v}</dd>
    <dt>Hosted UI</dt><dd>{hosted}</dd>
    <dt>Method detail</dt><dd>{ui}</dd>
    <dt>Frontend / RPC</dt><dd>Checked when you open the app; failures here are infrastructure, not assessment.</dd>
    <dt>If unavailable</dt><dd>Save progress, use observation/captured evidence, or pause — do not invent a transaction.</dd>
  </dl>
</aside>
'''


def assessment_html(lesson: dict, slug: str) -> str:
  """Independent rubric page for an application lab (not exercise ticks)."""
  title = E(lesson.get('title') or slug)
  path = f'/lessons/{E(slug)}/'
  assess = lesson.get('assessment') or {}
  purpose = E(assess.get('purpose') or (
    'Determine whether the student can decide create vs update from account evidence, '
    'explain PDA address stability, and label evidence honestly.'
  ))
  criteria = assess.get('criteria') or []
  if not criteria:
    # Generic fallback — never Picassol-specific wording for other labs.
    loop = lesson.get('learning_loop') or {}
    outcome = (lesson.get('student_outcome') or loop.get('objective')
               or 'the stated lab outcome')
    explain_q = loop.get('explain_question') or 'Why did the observed result follow from the instruction chosen?'
    transfer = loop.get('transfer') or 'Apply the same rule on a fresh example without re-reading the walkthrough.'
    criteria = [
      {
        'id': 'c1',
        'title': 'Chooses the correct action from account evidence',
        'question': f'Does the student decide the next instruction from observed account state for: {outcome}?',
        'not_yet': 'Picks an instruction without checking whether the relevant account exists or matches seeds.',
        'support': 'Correct after a prompt to inspect getAccountInfo / Explorer at the derived address.',
        'independent': 'Records the relevant address, account existence, and the instruction that follows from that evidence.',
        'misconception': '“The UI button alone tells me which instruction to send.”',
      },
      {
        'id': 'c2',
        'title': 'Explains the observed result',
        'question': explain_q,
        'not_yet': 'Cannot connect seeds, authority, or CPI behaviour to the result.',
        'support': 'Gives a correct explanation after a conceptual prompt tied to Proof or the program path.',
        'independent': 'Names the constraint or state transition that produced the observed outcome.',
        'misconception': '“A successful signature means I understand the accounts.”',
      },
      {
        'id': 'c3',
        'title': 'Labels evidence provenance',
        'question': 'Does the student distinguish platform historical proof from their own attempt?',
        'not_yet': 'Treats a Sol.College Proof signature as proof they completed the action.',
        'support': 'Corrects the mix-up after a prompt about historical vs my attempt tags.',
        'independent': 'Tags route (observation / live / local / guided) and does not claim historical signatures as personal completion.',
        'misconception': '“Any successful signature on the lesson page counts as my mastery.”',
      },
      {
        'id': 'c4',
        'title': 'Transfers to a fresh example',
        'question': transfer,
        'not_yet': 'Cannot generalise beyond the walked-through example.',
        'support': 'States the rule after revisiting the predict-why note.',
        'independent': 'Applies the same decision rule on a fresh case with the evidence needed.',
        'misconception': '“I finished because I followed the buttons once.”',
      },
    ]
  crit_html = []
  for i, c in enumerate(criteria, 1):
    crit_html.append(
      f'<h2 id="{E(c.get("id") or f"c{i}")}">Criterion {i} — {E(c.get("title") or "")}</h2>'
      f'<p><b>Question.</b> {E(c.get("question") or "")}</p>'
      f'<ul>'
      f'<li><b>Not yet:</b> {E(c.get("not_yet") or "")}</li>'
      f'<li><b>With support:</b> {E(c.get("support") or "")}</li>'
      f'<li><b>Independently:</b> {E(c.get("independent") or "")}</li>'
      f'</ul>'
      + (f'<p><b>Critical misconception.</b> {E(c["misconception"])}</p>' if c.get('misconception') else '')
    )
  return f'''
<nav class="crumbs" aria-label="Breadcrumb"><a href="/">Home</a> / <a href="/lessons/">Lessons</a> / <a href="{path}">{title}</a> / <span>Assessment</span></nav>
<p class="eyebrow">Assessment rubric</p>
<h1>{title}: assessment</h1>
<p class="lead">{purpose}</p>
<p>This rubric assesses the application-lab outcomes in <a href="{path}">the lesson</a>. Self-marked workspace outcomes are drafts. Exercise checklist ticks are not mastery.</p>

<h2 id="levels">Performance levels</h2>
<table>
<thead><tr><th>Level</th><th>Meaning</th></tr></thead>
<tbody>
<tr><td>Not yet demonstrated</td><td>Evidence missing, materially incorrect, or shows an unresolved misconception</td></tr>
<tr><td>Demonstrated with support</td><td>Correct after a conceptual prompt</td></tr>
<tr><td>Demonstrated independently</td><td>Correct without a conceptual prompt</td></tr>
<tr><td>Not assessable</td><td>Infrastructure, accessibility, or evidence problems prevent a fair judgement</td></tr>
</tbody>
</table>

{''.join(crit_html)}

<h2 id="gates">Mandatory honesty gates</h2>
<table>
<thead><tr><th>Gate</th><th>Required demonstration</th></tr></thead>
<tbody>
<tr><td>Devnet practice environment</td><td>Does not treat mainnet funds as required for completion</td></tr>
<tr><td>No secrets</td><td>Does not submit recovery phrases or private keys</td></tr>
<tr><td>Evidence provenance</td><td>Does not claim platform historical signatures as personal completion</td></tr>
<tr><td>Observation ≠ practical mastery</td><td>Observation mode alone cannot award independent practical completion</td></tr>
</tbody>
</table>

<h2 id="decisions">Completion decisions</h2>
<table>
<thead><tr><th>Decision</th><th>Requirements</th></tr></thead>
<tbody>
<tr><td>Completed independently</td><td>All criteria independent; all honesty gates</td></tr>
<tr><td>Completed with support</td><td>All criteria at least with support; all honesty gates</td></tr>
<tr><td>Further practice needed</td><td>A criterion not demonstrated, or a gate unresolved</td></tr>
<tr><td>Assessment paused</td><td>Infrastructure/accessibility/evidence issues prevent fair completion</td></tr>
<tr><td>Observation completed</td><td>Conceptual / captured-evidence route only; not practical mastery</td></tr>
</tbody>
</table>
<p>Never convert “assessment paused” into a failing grade. A successful transaction alone must not automatically award the whole lesson.</p>
<p class="cta-row"><a class="btn" href="{path}#workspace">Return to workspace</a> <a class="btn ghost" href="{path}#exercises">Practice exercises</a></p>
'''
