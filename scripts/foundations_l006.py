"""Solana Foundations Lesson 006: Read and Write Application State.

Release candidate. Not a shipped profile editor product and not technically or learner verified.
Teaches: observation vs draft vs pending; read context; reconcile without false certainty.
"""
from __future__ import annotations
import html

SITE = 'https://sol.college'
PUBLISHED = '2026-11-18'
SLUG = 'application-state'
PATH = f'/lessons/{SLUG}/'
ASSESS_PATH = f'/lessons/{SLUG}/assessment/'
L005_PATH = '/lessons/transaction-failures/'
L004_PATH = '/lessons/transaction-atomicity/'
E = lambda s: html.escape(str(s if s is not None else ''), quote=True)

STATUS_ROWS = [
  ('Status', 'Release candidate. Not yet technically or learner verified.'),
  ('Version', '1.0'),
  ('Track', 'Solana Foundations'),
  ('Prerequisites', 'Lessons 001–005, or equivalent understanding'),
  ('Audience', 'People new to Solana; basic JS/TS or guided configuration route'),
  ('Environment', 'Devnet, with deterministic fixtures and a captured-evidence alternative'),
  ('Core learning time', 'About 75 minutes (design estimate, not a measured claim)'),
  ('Achievement', 'State Steward: Read, Update, Reconcile — not awarded until verification gates pass'),
  ('Technical verification', 'Not completed — starter project and fault harness not yet verified for this RC'),
  ('Learner testing', 'Not completed for this release candidate'),
]

LESSON_DESC = (
  'RC foundations lesson: keep observed account state separate from drafts and pending updates. '
  'Not yet technically verified.'
)
ASSESS_DESC = (
  'Rubric for Lesson 006: observation vs draft, read context, reconciliation, races. '
  'Release candidate; every criterion required.'
)


def status_panel():
  body = ''.join(f'<dt>{E(k)}</dt><dd>{E(v)}</dd>' for k, v in STATUS_ROWS)
  return (
    '<section class=status-panel aria-label="Lesson status">'
    '<h2>Lesson status</h2>'
    f'<dl class=article-meta>{body}</dl>'
    '<p><b>Publication rule.</b> This page is a teaching specification and interface design. '
    'It must not be labelled verified until the starter project builds cleanly, fault harness cases '
    'are deterministic, and learners (implementation and guided routes) complete the reconciliation '
    'behaviour. <b>Proposed client function names are teaching interfaces—not actual SDK methods. '
    'Do not claim a production Profile Editor ships with this RC.</b></p>'
    '</section>'
  )


def lesson_html(css=''):
  docs = (
    '<p class=note>Official references: '
    '<a href="https://solana.com/docs/intro/quick-start/reading-from-network">Reading from the network</a>, '
    '<a href="https://solana.com/docs/rpc/http/getaccountinfo">getAccountInfo</a>, '
    '<a href="https://solana.com/docs/rpc">Solana RPC overview</a>, '
    '<a href="https://solana.com/docs/rpc/websocket/accountsubscribe">accountSubscribe</a>. '
    'A client displays observations of on-chain state—not a permanent, perfectly current copy of it.</p>'
  )
  body = f'''{status_panel()}
<p class=lead>Your transaction succeeded—but your application still shows the old name. Did the transaction fail? Is the screen stale? Did another update happen? Should you press “Save” again?</p>
<p>In this lesson you build a small profile editor that keeps observed account state separate from an unsaved draft and a pending update. Show progress honestly, refresh the right evidence, and avoid turning a stale screen into a duplicate action.</p>
{docs}

<h2 id=outcomes>1. Learning outcomes</h2>
<table>
<thead><tr><th>Outcome</th><th>Observable demonstration</th></tr></thead>
<tbody>
<tr><td>Separate client-side state</td><td>Distinguish observed account data, draft input, and pending intent</td></tr>
<tr><td>Interpret an account read</td><td>Identify network, address, commitment, context slot, and decoded values</td></tr>
<tr><td>Manage the update lifecycle</td><td>Preserve the original attempt and prevent accidental repeat submission</td></tr>
<tr><td>Reconcile after execution</td><td>Perform an appropriately contextualised account read after a successful transaction</td></tr>
<tr><td>Handle stale and failed reads</td><td>Preserve the last observation without representing it as newly verified</td></tr>
<tr><td>Detect a conflicting update</td><td>Explain why a stale draft should not silently overwrite newly observed data</td></tr>
</tbody>
</table>
<p>The <a href="{ASSESS_PATH}">assessment rubric</a> scores six criteria separately. Record implementation vs guided configuration route accurately.</p>

<h2 id=scope>2. Scope and prerequisites</h2>
<p><b>Included:</b> reading/decoding the prepared profile; controlled form state; loading/missing/error/stale/pending/verified states; transaction-to-read reconciliation; out-of-order client responses; changes from a second client; explicit refresh strategy.</p>
<p><b>Deferred:</b> production indexing; automatic multi-provider failover; full offline editing; multi-account snapshot consistency; automated conflict merging; WebSocket subscriptions except as optional extension; general exactly-once guarantees.</p>
<p><b>Programming prerequisite.</b> This is the first implementation-oriented lesson. Students need basic JavaScript/TypeScript (variables, functions, async, UI events) or the guided configuration route. Provide a short bridge exercise—do not assume Lessons 001–005 taught programming.</p>
<ul>
<li>Devnet only. No real-money deposits. No custom private-key input.</li>
<li>No wallet approval required to read public profile data.</li>
<li>No automatic replacement after an unresolved submission.</li>
<li>No silent update when a student opens or refreshes the editor.</li>
</ul>

<h2 id=app>3. Profile Card and client limitation</h2>
<p>Continue with <code>update_profile(new_name)</code>: changes name, increments revision by one, leaves authority unchanged.</p>
<p><b>Important limitation.</b> This operation does not yet require an expected revision. The client can detect an observed conflict and ask the student what to do, but a client-side check alone cannot guarantee that no other update occurs before execution. Stronger concurrency protection belongs in a later program-design lesson.</p>

<h2 id=editor>4. What the student builds</h2>
<pre class=diagram>PROFILE EDITOR — DEVNET

OBSERVED PROFILE
Name: Atlas
Revision: 12
Observed at slot: [slot]
Commitment: finalized
Fetched: [time]

YOUR DRAFT
[Harbour________________]

UPDATE STATUS
No update pending.

[Refresh] [Review update]</pre>
<p>After submission: show pending status and “Do not submit again” while retaining the previous observation. After successful execution but before a satisfactory read: “Transaction succeeded and reached finalized. Refreshing profile state… The displayed profile is still the previous observation.” Do not label old data “updated” merely because the transaction succeeded.</p>

<h2 id=starter>5. Starter-project requirements (for verified release)</h2>
<p>Provide a tested starter using the Sol.College stack and maintained Solana client tooling. Students complete small gaps—not wallet integration from scratch.</p>
<pre class=diagram>Proposed teaching interfaces (not actual SDK method names):
readProfile()
buildProfileUpdate()
requestAuthorisationAndSubmit()
observeExistingAttempt()
readProfileAfterTransaction()</pre>
<p>Student responsibilities: store observed data separately from the draft; clear read states; gate repeated submission; reconcile a successful attempt; prevent an old response from replacing a newer accepted observation; handle a newly observed conflicting revision. Ship exact tested SDK imports in the repository.</p>
<p class=note>RC honesty: no claim is made that this starter repository is published with this page. The lesson specifies what that project must provide.</p>

<h2 id=sequence>6. Lesson sequence</h2>
<table>
<thead><tr><th>Stage</th><th>Time</th><th>Student task</th></tr></thead>
<tbody>
<tr><td>Misleading interface</td><td>~5 min</td><td>Identify what the screen falsely implies</td></tr>
<tr><td>Model client state</td><td>~10 min</td><td>Separate observation, draft, and operation</td></tr>
<tr><td>Read with context</td><td>~10 min</td><td>Inspect a real profile response</td></tr>
<tr><td>Honest update</td><td>~15 min</td><td>Preserve evidence and show pending state</td></tr>
<tr><td>Reconcile</td><td>~10 min</td><td>Refresh using appropriate context</td></tr>
<tr><td>Races and conflicts</td><td>~10 min</td><td>Handle delayed responses and another client</td></tr>
<tr><td>Independent challenge</td><td>~10 min</td><td>Pass deterministic fault cases</td></tr>
<tr><td>Explain</td><td>~5 min</td><td>Describe what the editor can and cannot guarantee</td></tr>
</tbody>
</table>

<h2 id=misleading>7. Stage one — investigate the misleading editor</h2>
<p>Labelled simulation: student types “Harbour”; interface immediately displays “Saved”; wallet request is rejected; page continues displaying “Harbour” as the saved profile.</p>
<p><b>Expected.</b> The interface treated the draft or intended change as an observed on-chain result. Corrective design: show a draft immediately if labelled as a draft; do not erase the last observed account data or falsely report successful persistence.</p>

<h2 id=model>8. Stage two — model three separate things</h2>
<p><b>A. Observed profile:</b> address, network, display name, revision, update authority, context slot, requested commitment, fetched time.</p>
<p><b>B. Draft:</b> proposed display name, revision the edit began from, unsaved changes.</p>
<p><b>C. Update attempt:</b> attempt identifier, intended profile/name, starting revision, wallet approval, signature if known, execution result, commitment, transaction slot if established, reconciliation state.</p>
<p><b>Checkpoint.</b> If the transaction is unresolved, should the draft replace the observed profile? No—keep draft and pending attempt visible separately from the last observed account state.</p>
<p>Read states: Not loaded; Loading; Ready; Account not found; Read failed; Refreshing previous observation. “Account not found” and “read failed” are not interchangeable—the account-info API returns <code>null</code> when absent; a transport/RPC error is different.</p>

<h2 id=read>9. Stage three — read the profile with context</h2>
<p>Retrieve without connecting a wallet if the integration permits. Inspect network, address, owner program, expected schema, decoded values, requested commitment, response context slot, local fetch time. Validate owner and data format before decoding.</p>
<p><b>Context question.</b> Does <code>context.slot</code> tell you the exact slot in which this profile was last modified? No—it identifies the context used for the read.</p>
<p><b>Commitment question.</b> Should the editor silently combine a <code>processed</code> observation with a display that says “finalized”? No—configured and displayed evidence levels must stay consistent.</p>

<h2 id=lifecycle>10. Stage four — implement the update lifecycle</h2>
<ol>
<li>Begin editing from an observed profile.</li>
<li>Preserve the observation; validate the draft locally; review the intended update.</li>
<li>Request authorisation; record the attempt; track execution and commitment; reconcile.</li>
</ol>
<p>While awaiting approval or unresolved: disable another submission through the normal interface; preserve attempt details; permit safe navigation/resume; explain why another update is blocked. A disabled button is not an exactly-once guarantee across tabs or devices.</p>
<p><b>Prompt.</b> Which earlier lesson explains why a timeout must not simply re-enable “Send again”? Lesson 005—reconcile the original attempt before a replacement is considered.</p>

<h2 id=reconcile>11. Stage five — reconcile after success</h2>
<p>Transaction matches intended update, executed successfully, reached <code>finalized</code>, included at slot T. Retrieve the account at the same commitment, using an appropriate minimum context when supported (<code>commitment</code>, <code>minContextSlot</code>).</p>
<p>A minimum context slot asks the node not to answer from a context older than that threshold. It does <b>not</b> request a historical snapshot at exactly that slot, and it does not prevent later updates.</p>
<table>
<thead><tr><th>Observation</th><th>Honest interpretation</th></tr></thead>
<tbody>
<tr><td>Intended name and expected revision observed</td><td>Consistent with the completed update</td></tr>
<tr><td>Read context too old</td><td>Not a satisfactory post-transaction observation</td></tr>
<tr><td>Read fails</td><td>Transaction success remains established; refresh unresolved</td></tr>
<tr><td>Later revision appears</td><td>Another update may have occurred; inspect</td></tr>
<tr><td>Owner/schema differs</td><td>Stop decoding; flag environment/account problem</td></tr>
</tbody>
</table>
<p>Do not resend a successful update just because refreshing the profile failed. Transaction and subsequent read are separate operations.</p>

<h2 id=races>12. Stage six — out-of-order response</h2>
<pre class=diagram>Read A starts first.
Read B starts later.
Read B returns first with a newer acceptable observation.
Read A returns afterwards with an older observation.</pre>
<p>Prevent Read A from overwriting the accepted display. Consider network/account identity, request lifecycle, commitment policy, observation context. Do not compare slot numbers across different networks.</p>
<p><b>Checkpoint.</b> Why is “whichever response arrives last wins” unsafe? Arrival order is not necessarily observation order.</p>

<h2 id=conflict>13. Stage seven — recognise a conflicting draft</h2>
<p>Client A reads revision 12 and edits; Client B updates to revision 13; Client A refreshes with draft still open. Do not silently discard the draft or submit against the newly observed state. Show conflict disclosure with discard / keep-and-review options.</p>
<p>Even a fresh pre-submission read cannot eliminate a race before execution—that requires an appropriate program-enforced condition. Do not claim this lesson’s client-side warning provides that guarantee.</p>

<h2 id=challenge>14. Independent challenge</h2>
<table>
<thead><tr><th>Case</th><th>Required result</th></tr></thead>
<tbody>
<tr><td>Wallet request rejected</td><td>Observed profile intact; draft available; no success claim</td></tr>
<tr><td>Tx succeeds, refresh fails</td><td>Success separate from unresolved refresh; do not resend</td></tr>
<tr><td>Old response after newer accepted read</td><td>Do not regress the displayed observation</td></tr>
<tr><td>Another client updates during editing</td><td>Preserve draft; disclose conflict; require review</td></tr>
</tbody>
</table>

<h2 id=assessment>15. Assessment overview</h2>
<p>Six criteria: state separation; read interpretation; update lifecycle; reconciliation; race/conflict handling; honest limitations. All six at least with support. See the <a href="{ASSESS_PATH}">full rubric</a>.</p>
<p><b>Critical misconceptions:</b> input text is saved account state; transaction success means every later read already shows it; failed refresh means resent; context slot is last-modified slot; minContextSlot is an exact historical snapshot; last response received is newest; client-side revision warning eliminates concurrency races.</p>

<h2 id=recovery>16. Recovery and accessibility</h2>
<table>
<thead><tr><th>Situation</th><th>Required response</th></tr></thead>
<tbody>
<tr><td>Account missing</td><td>Specific absence state; not a blank valid profile</td></tr>
<tr><td>RPC error</td><td>Preserve last observation; label appropriately</td></tr>
<tr><td>Wrong network/address</td><td>Clear incompatible pending views; require deliberate review</td></tr>
<tr><td>Decoder mismatch</td><td>Stop decoding; no invented values</td></tr>
<tr><td>Session refreshed mid-attempt</td><td>Restore known attempt where safely supported; do not resubmit</td></tr>
<tr><td>Lacks programming prerequisites</td><td>Bridge exercise or guided route</td></tr>
<tr><td>Live environment unavailable</td><td>Deterministic fixtures with clear labels</td></tr>
</tbody>
</table>

<h2 id=extension>17. Optional extension: subscriptions</h2>
<p>After the core lesson: <code>accountSubscribe</code> at chosen commitment; handle disconnects; fresh read after reconnect; avoid duplicate/regressive updates; clean up on account change. Treat notifications as part of the observation system—not a guarantee the client never missed an update. Not a prerequisite for the core achievement.</p>

<h2 id=gates>18. Release gate</h2>
<ul>
<li>Verify starter from a clean setup; pin dependencies; confirm owner/schema validation.</li>
<li>Test missing-account and RPC-error states; rejection, timeout, refresh, resume.</li>
<li>Verify post-transaction read-context handling; delayed-response and two-client conflict.</li>
<li>Check accessibility; observe programming and guided-route learners.</li>
<li>Publish verification date, reviewer, versions, and limitations.</li>
</ul>
<p><b>Understanding to leave with.</b> My application keeps the user’s intention separate from what it has actually observed. It can track a successful transaction while still admitting that a refresh is unresolved. When new evidence arrives, it updates carefully rather than pretending the screen is always the chain.</p>

<h2 id=next>19. Next</h2>
<p>Next foundations step: <a href="/lessons/protecting-state-transitions/">Lesson 007 — Protecting State Transitions</a> (release candidate). Until foundations are verified, the first live Stage 1 practice remains <a href="/lessons/picassol-hackathon/">Picassol</a>.</p>
<p class=cta>
<a class=btn href="{ASSESS_PATH}">Open the assessment rubric</a>
<a class="btn ghost" href="/lessons/protecting-state-transitions/">Next: Lesson 007</a>
<a class="btn ghost" href="{L005_PATH}">Previous: Lesson 005</a>
</p>
'''
  rail = (
    '<nav class=rail aria-label="On this page">'
    '<a href="#outcomes">Outcomes</a><a href="#scope">Scope</a><a href="#app">Profile Card</a>'
    '<a href="#editor">Editor</a><a href="#starter">Starter</a><a href="#sequence">Sequence</a>'
    '<a href="#misleading">Misleading UI</a><a href="#model">Model</a><a href="#read">Read</a>'
    '<a href="#lifecycle">Lifecycle</a><a href="#reconcile">Reconcile</a><a href="#races">Races</a>'
    '<a href="#conflict">Conflict</a><a href="#challenge">Challenge</a><a href="#assessment">Assessment</a>'
    '<a href="#recovery">Recovery</a><a href="#extension">Extension</a><a href="#gates">Gates</a>'
    '<a href="#next">Next</a></nav>'
  )
  return f'''{css}<div class=readbar aria-hidden=true><span></span></div>
<article class=lesson data-slug="{SLUG}">
<div class=lesson-layout><div class=lesson-main>
<nav class=crumbs aria-label=Breadcrumb><a href="/">Home</a> / <a href="/lessons/">Lessons</a> / <a href="/lessons/path/">Path</a> / <span>Application state</span></nav>
<p class="eyebrow status-preview">Foundations · Lesson 006 · release candidate</p>
<h1>Read and Write Application State</h1>
<p class=lead>Build a client that knows the difference between a request and reality.</p>
{body}
</div>{rail}</div>
<div class=dock role=region aria-label="Lesson actions">
<a class=btn href="{ASSESS_PATH}">Assessment rubric</a>
<a class="btn ghost" href="/lessons/protecting-state-transitions/">Next: Lesson 007</a>
<button type=button class="btn ghost" data-jump>Next section</button>
</div>
</article>'''


def assessment_html(css=''):
  assert len(LESSON_DESC) <= 158 and len(ASSESS_DESC) <= 158, (len(LESSON_DESC), len(ASSESS_DESC))
  body = f'''{status_panel()}
<p class=lead>Determine whether a student can keep observed account data separate from user input and pending operations, interpret read context, reconcile updates, and handle stale responses or conflicting edits without misleading the user.</p>
<p>This rubric evaluates <a href="{PATH}">Lesson 006</a>’s controlled Profile Card client. It does not certify production readiness, general-purpose state synchronisation, security-audit competence, or exactly-once execution. Record implementation vs guided configuration route accurately.</p>

<h2 id=levels>Performance levels</h2>
<table>
<thead><tr><th>Level</th><th>Meaning</th></tr></thead>
<tbody>
<tr><td>Not yet demonstrated</td><td>Missing, materially incorrect, or unresolved misconception</td></tr>
<tr><td>Demonstrated with support</td><td>Correct after a conceptual prompt</td></tr>
<tr><td>Demonstrated independently</td><td>Correct without a conceptual prompt</td></tr>
<tr><td>Not assessable</td><td>Technical, accessibility, or evidence problems prevent fair judgement</td></tr>
</tbody>
</table>
<p>Lesson notes, starter docs, SDK docs, schema, debugging tools, and accessibility tools do not reduce an independent result. Looking up an API or using a debugger does not, by itself, reduce independence.</p>

<h2 id=materials>Assessment materials</h2>
<p>Tested starter or guided environment: profile specimen; read evidence; update attempt; fault harness (delays, rejected approval, failed reads, competing updates); expected behaviours; version record. Distinguish live RPC, deterministic fixture, simulation, submitted transaction, and illustrative interface.</p>

<h2 id=c1>Criterion 1 — Separates observation, draft, and update attempt</h2>
<ul>
<li><b>Not yet:</b> draft replaces observed profile as though saved; pending intent presented as completed; rejection destroys last valid observation.</li>
<li><b>Independently:</b> maintains distinct observed-profile, draft, and attempt records through editing, rejection, and pending execution.</li>
</ul>
<p><b>Critical misconception.</b> “The input contains the new name, so the profile is updated.”</p>

<h2 id=c2>Criterion 2 — Reads and interprets account data with context</h2>
<ul>
<li><b>Independently:</b> validates expected account and schema; records network and context; accurately explains commitment, context slot, fetch time, and missing-data states.</li>
</ul>
<p>Distinguish Loading / Account returned / Account not found / Read failed / Refreshing while retaining previous observation. Context slot is not necessarily the last-modified slot.</p>

<h2 id=c3>Criterion 3 — Manages the update lifecycle honestly</h2>
<p>Fixture: approved; signature known; submission times out; outcome not yet established.</p>
<ul>
<li><b>Independently:</b> attempt remains visible; signature retained; result unresolved; no replacement via normal submission; student explains continued reconciliation.</li>
</ul>
<p>A disabled button protects ordinary repeated interaction—not exactly-once across tabs/devices.</p>

<h2 id=c4>Criterion 4 — Reconciles successful transaction with subsequent read</h2>
<pre class=diagram>Transaction: Execution succeeded. Required finalized commitment reached.
Subsequent profile read: RPC error.</pre>
<p>Expected: “Transaction succeeded and reached finalized. Profile refresh is unresolved. The displayed profile is the previous observation.” Must not say “Update failed. Send again.”</p>
<p>Where using transaction slot and <code>minContextSlot</code>: explain why older context may be unsuitable; why minimum context is not an exact historical snapshot; why a later revision does not automatically mean the original transaction failed.</p>

<h2 id=c5>Criterion 5 — Handles delayed responses and conflicting edits</h2>
<p><b>Test A — Out-of-order:</b> delayed older observation must not replace accepted newer one. Do not accept “Always use the largest slot.”</p>
<p><b>Test B — Concurrent edit:</b> draft from revision 12; another client reaches 13; first client observes 13. Preserve draft; show conflict; deliberate discard or review; no silent resubmission. Both tests required.</p>

<h2 id=c6>Criterion 6 — Explains limitations with evidence</h2>
<ul>
<li><b>Independently:</b> states tested protections; identifies residual limits; ties statements to demonstrated cases.</li>
</ul>
<p>Must address: what prevents misleading state; what the submission guard protects; why a pre-submission refresh does not eliminate all concurrency races; what happens when evidence remains insufficient.</p>

<h2 id=matrix>Required fault-test matrix</h2>
<table>
<thead><tr><th>Test</th><th>Required outcome</th></tr></thead>
<tbody>
<tr><td>Edit without submission</td><td>Draft changes; observed profile does not</td></tr>
<tr><td>Wallet request rejected</td><td>No success claim; observation preserved</td></tr>
<tr><td>Submission unresolved</td><td>Attempt retained; no blind replacement</td></tr>
<tr><td>Success + refresh failure</td><td>Success and refresh uncertainty separate</td></tr>
<tr><td>Account not found</td><td>Specific absence state</td></tr>
<tr><td>RPC read failure</td><td>Error ≠ absence; previous observation labelled</td></tr>
<tr><td>Delayed older response</td><td>Accepted observation does not regress</td></tr>
<tr><td>Concurrent edit detected</td><td>Draft preserved; conflict disclosed</td></tr>
<tr><td>Owner/schema mismatch</td><td>Decoding stops</td></tr>
</tbody>
</table>

<h2 id=checks>Mandatory conceptual checks</h2>
<table>
<thead><tr><th>Check</th><th>Required understanding</th></tr></thead>
<tbody>
<tr><td>Draft versus observation</td><td>Unsaved input ≠ observed account state</td></tr>
<tr><td>Attempt versus outcome</td><td>Pending request ≠ completed update</td></tr>
<tr><td>Execution versus refresh</td><td>Failed read does not reverse established transaction success</td></tr>
<tr><td>Context interpretation</td><td>Context slot ≠ necessarily last-modified slot</td></tr>
<tr><td>Read ordering</td><td>Last response received ≠ necessarily newest acceptable observation</td></tr>
<tr><td>Concurrency</td><td>Client-side checking alone does not eliminate races</td></tr>
<tr><td>Honest uncertainty</td><td>Insufficient evidence should remain explicit</td></tr>
</tbody>
</table>

<h2 id=decisions>Completion decisions</h2>
<table>
<thead><tr><th>Decision</th><th>Requirements</th></tr></thead>
<tbody>
<tr><td>Completed independently</td><td>All six criteria independent; required fault tests passed; conceptual checks satisfied</td></tr>
<tr><td>Completed with support</td><td>All six at least with support; fault tests passed; conceptual checks satisfied</td></tr>
<tr><td>Further practice needed</td><td>A criterion not yet demonstrated or required behaviour incorrect</td></tr>
<tr><td>Assessment paused</td><td>Technical, accessibility, or evidence issues prevent fair assessment</td></tr>
</tbody>
</table>
<p>Record precisely, e.g. “Completed independently — implementation route with deterministic fixtures.” A fixture-based result must not be described as a live devnet workflow. A supplied implementation the student cannot explain is insufficient.</p>

<h2 id=record>Assessor record template</h2>
<pre class=diagram>SOL.COLLEGE — LESSON 006 ASSESSMENT
Student identifier:
Assessment date:
Lesson version: 1.0
Rubric version: 1.0 — proposed; requires assessor calibration
Assessor:
Route: [ ] Implementation  [ ] Guided configuration
Evidence: [ ] Live  [ ] Fixtures  [ ] Mixed
Criterion 1 — State separation:
Criterion 2 — Read interpretation:
Criterion 3 — Update lifecycle:
Criterion 4 — Reconciliation:
Criterion 5 — Races and conflicts:
Criterion 6 — Evidence and limitations:
Conceptual checks:
[ ] Draft versus observation
[ ] Attempt versus outcome
[ ] Execution versus refresh
[ ] Context interpretation
[ ] Read ordering
[ ] Concurrency
[ ] Honest uncertainty
Decision:
Feedback:
Reassessment required:</pre>
<p class=cta><a class=btn href="{PATH}">Back to Lesson 006</a> <a class="btn ghost" href="{L005_PATH}">Lesson 005</a> <a class="btn ghost" href="/lessons/path/">Learning path</a></p>
'''
  rail = (
    '<nav class=rail aria-label="On this page">'
    '<a href="#levels">Levels</a><a href="#materials">Materials</a><a href="#c1">Separation</a>'
    '<a href="#c2">Read</a><a href="#c3">Lifecycle</a><a href="#c4">Reconcile</a>'
    '<a href="#c5">Races</a><a href="#c6">Limits</a><a href="#matrix">Fault matrix</a>'
    '<a href="#checks">Checks</a><a href="#decisions">Decisions</a><a href="#record">Record</a></nav>'
  )
  return f'''{css}<div class=readbar aria-hidden=true><span></span></div>
<article class=lesson data-slug="{SLUG}-assessment">
<div class=lesson-layout><div class=lesson-main>
<nav class=crumbs aria-label=Breadcrumb><a href="/">Home</a> / <a href="/lessons/">Lessons</a> / <a href="{PATH}">Application state</a> / <span>Assessment</span></nav>
<p class="eyebrow status-preview">Foundations · Lesson 006 assessment · release candidate</p>
<h1>Assessment rubric: State Steward</h1>
{body}
</div>{rail}</div>
</article>'''


def card_html():
  return (
    f'<article class="card ready-preview" data-lesson data-slug="{SLUG}" data-diff="Beginner" data-format="foundations" '
    f'data-text="application state draft observation reconcile client race conflict foundations">'
    f'<p class="eyebrow status-preview">Foundations · Lesson 006 · release candidate</p>'
    f'<h3><a href="{PATH}">Build a client that knows the difference between a request and reality.</a></h3>'
    f'<p class=project>Read and Write Application State</p>'
    f'<p class=limit>Known limit: teaching specification only until the starter project and fault harness '
    f'are verified. Observation ≠ draft ≠ pending update.</p>'
    f'<p class=meta><span class="chip beg">Beginner</span> · ~75 min design estimate · First implementation lesson</p>'
    f'<p class=cta><a class=btn href="{PATH}">Open Lesson 006</a> · <a href="{ASSESS_PATH}">Assessment rubric</a></p>'
    f'</article>'
  )
