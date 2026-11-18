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
</section>
'''


def _opt(value: str, label: str) -> str:
  return f'<label class="loop-opt"><input type="radio" name="loop-predict" value="{E(value)}"> {E(label)}</label>'


def workspace_html(loop: dict, app_href: str, platform_sigs: list | None = None) -> str:
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
    hist = f'<ul class="ev-list">{items}</ul>'
  app = E(app_href)
  def p(text):
    return f'<p>{E(text)}</p>' if text else ''

  return f'''
<section class="lab-workspace" id="workspace" data-learning="workspace" data-predict-answer="{predict_ok}">
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
        <button type="button" class="btn" data-loop-mark="transfer">Save demonstration status</button>
        <p class="cta-row">
          <a class="btn ghost" href="#exercises">Open full exercises</a>
          <a class="btn ghost" href="#proof">Platform proof records</a>
          <a class="btn ghost" href="/lessons/path/">Choose next step</a>
        </p>
      </div>
    </div>
    <aside class="lab-evidence" aria-label="Evidence drawer">
      <h3>Evidence drawer</h3>
      <p class="note">Platform signatures below are historical Sol.College records — not proof of your action.</p>
      {hist or '<p class="note">No platform signatures attached.</p>'}
      <h4>Your attempt</h4>
      <dl class="ev-attempt" id="ev-attempt">
        <dt>Mode</dt><dd id="ev-mode">Not chosen</dd>
        <dt>Prediction</dt><dd id="ev-predict">—</dd>
        <dt>Route</dt><dd id="ev-route">—</dd>
        <dt>Outcome</dt><dd id="ev-outcome">—</dd>
      </dl>
      <p><a href="#stuck">I am stuck</a></p>
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
