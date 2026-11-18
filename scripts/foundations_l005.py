"""Solana Foundations Lesson 005: When Transactions Fail.

Release candidate. Not a live incident lab and not technically or learner verified.
Teaches: classify before retrying; failure vs uncertainty; targeted correction; safe recovery.
"""
from __future__ import annotations
import html

SITE = 'https://sol.college'
PUBLISHED = '2026-11-18'
SLUG = 'transaction-failures'
PATH = f'/lessons/{SLUG}/'
ASSESS_PATH = f'/lessons/{SLUG}/assessment/'
L004_PATH = '/lessons/transaction-atomicity/'
L003_PATH = '/lessons/instructions-programs/'
E = lambda s: html.escape(str(s if s is not None else ''), quote=True)

STATUS_ROWS = [
  ('Status', 'Release candidate. Not yet technically or learner verified.'),
  ('Version', '1.0'),
  ('Track', 'Solana Foundations'),
  ('Prerequisites', 'Lessons 001–004, or equivalent understanding'),
  ('Audience', 'People new to Solana; no programming required'),
  ('Environment', 'Devnet, reviewed local tests, simulations, and clearly labelled captured evidence'),
  ('Core learning time', 'About 60–75 minutes (design estimate, not a measured claim)'),
  ('Achievement', 'Transaction Troubleshooter: Diagnose and Recover — not awarded until verification gates pass'),
  ('Technical verification', 'Not completed — evidence packs and error mappings not yet reproduced for this RC'),
  ('Learner testing', 'Not completed for this release candidate'),
]

LESSON_DESC = (
  'RC foundations lesson: classify failures, read errors, reconcile before retrying. '
  'Not yet technically verified.'
)
ASSESS_DESC = (
  'Rubric for Lesson 005: failure stages, error reading, uncertainty, safe recovery. '
  'Release candidate; every criterion required.'
)


def status_panel():
  body = ''.join(f'<dt>{E(k)}</dt><dd>{E(v)}</dd>' for k, v in STATUS_ROWS)
  return (
    '<section class=status-panel aria-label="Lesson status">'
    '<h2>Lesson status</h2>'
    f'<dl class=article-meta>{body}</dl>'
    '<p><b>Publication rule.</b> This page is a teaching specification and interface design. '
    'It must not be labelled verified until every incident pack is reproduced, error mappings match '
    'the deployed program, timeout reconciliation is tested, and learners choose a safe next action. '
    '<b>Do not invent signatures or log traces. Local tests, simulations, and submitted failures '
    'are not interchangeable. A deliberately failing transaction is never required.</b></p>'
    '</section>'
  )


def lesson_html(css=''):
  docs = (
    '<p class=note>Official references: '
    '<a href="https://solana.com/docs/rpc/http/simulatetransaction">simulateTransaction</a>, '
    '<a href="https://solana.com/docs/rpc/http/getsignaturestatuses">getSignatureStatuses</a>, '
    '<a href="https://solana.com/developers/cookbook/transactions/confirmation">Transaction confirmation &amp; expiration</a>, '
    '<a href="https://solana.com/developers/cookbook/transactions/retry">Retrying transactions</a>. '
    'Classify before retrying: what do we know, what remains unknown, and what evidence should we inspect next?</p>'
  )
  body = f'''{status_panel()}
<p class=lead>Not every unsuccessful interaction is a failed transaction. A wallet request can be rejected before submission. A simulation can identify a problem without broadcasting. A program can reject a submitted transaction. An application can also time out while the transaction succeeds.</p>
<p>In this lesson you separate those situations, find the most useful evidence, and choose a recovery action that does not accidentally repeat the operation. Central habit: <b>classify before retrying.</b></p>
{docs}

<h2 id=outcomes>1. Learning outcomes</h2>
<table>
<thead><tr><th>Outcome</th><th>Observable demonstration</th></tr></thead>
<tbody>
<tr><td>Locate the failure stage</td><td>Distinguish wallet rejection, preflight/simulation failure, execution failure, and unresolved observation</td></tr>
<tr><td>Interpret a structured error</td><td>Identify the failing operation and explain a relevant error using the supplied documentation</td></tr>
<tr><td>Separate evidence from inference</td><td>Distinguish “not observed” from “did not happen”</td></tr>
<tr><td>Select a targeted correction</td><td>Address the demonstrated cause instead of changing unrelated settings</td></tr>
<tr><td>Recover without blind repetition</td><td>Reconcile an existing attempt before authorising a replacement</td></tr>
<tr><td>Document an incident</td><td>Produce a concise, secret-free diagnosis and recovery record</td></tr>
</tbody>
</table>
<p>The <a href="{ASSESS_PATH}">assessment rubric</a> scores six criteria separately—no compensating total. No additional transaction is required merely to prove troubleshooting ability.</p>

<h2 id=safety>2. Scope and safety</h2>
<p><b>Included:</b> wallet rejection; invalid application input; incorrect update authority; simulation versus submitted execution; application timeout; recent-blockhash expiry at a conceptual level; reconciliation before replacement; clear incident reporting.</p>
<p><b>Deferred:</b> durable nonces; automated rebroadcast; priority-fee optimisation; arbitrary nested CPI debugging; production incident response; general exactly-once guarantees.</p>
<ul>
<li>No real funds. No recovery phrases or private keys.</li>
<li>No requirement to submit intentionally failing transactions.</li>
<li>No disabling safety checks merely to generate an error.</li>
<li>No automatic replacement while an earlier result remains unresolved.</li>
<li>Rejecting an unclear request is acceptable.</li>
</ul>

<h2 id=app>3. Attempt record (product requirement)</h2>
<p>Continue with the Profile Card program from Lessons 002–004 (<code>update_profile</code>, <code>assert_revision</code>). The interface must preserve an attempt record:</p>
<pre class=diagram>Attempt identifier · Intended action · Network
Program and profile addresses · Starting state and observation time
Wallet approval state · Signature, if known
Submission response or error · Blockhash lifetime information, where applicable
Observed execution result · Observed commitment · Relevant logs or error details
Next action · Resolution</pre>
<p>A signature can exist before a transaction has been observed on-chain. Its presence must not be treated as proof of submission or execution.</p>
<p>Avoid a misleading universal <code>TRANSACTION FAILED [TRY AGAIN]</code>. Prefer precise statuses: Approval rejected; Simulation failed — not broadcast by this attempt; Execution failed; Awaiting confirmation; Status unresolved; Expired — outcome reconciliation required. “Expired” and “never executed” are not interchangeable.</p>

<h2 id=packs>4. Four evidence packs (+ expiry)</h2>
<table>
<thead><tr><th>Pack</th><th>Scenario</th><th>Main teaching point</th></tr></thead>
<tbody>
<tr><td>A</td><td>Student rejects the wallet request</td><td>No need to diagnose program execution</td></tr>
<tr><td>B</td><td>Proposed name violates a documented validation rule</td><td>Correct the input, not the network</td></tr>
<tr><td>C</td><td>Wrong authority signs a profile update</td><td>A valid signature does not satisfy every permission rule</td></tr>
<tr><td>D</td><td>Application times out after submission</td><td>Reconcile before repeating</td></tr>
</tbody>
</table>
<p>Plus a shorter pack for recent-blockhash expiry. Each pack must identify whether it contains a local test, simulation, submitted devnet transaction, captured application event, or account observation. A simulation does not broadcast the transaction.</p>
<p class=note>RC honesty: evidence packs are specified here, not claimed as reproduced. Do not fabricate a transaction signature or log trace to make a pack look complete. Illustrative material must be labelled as illustrative.</p>

<h2 id=sequence>5. Lesson sequence</h2>
<table>
<thead><tr><th>Stage</th><th>Time</th><th>Student task</th></tr></thead>
<tbody>
<tr><td>Orient</td><td>~5 min</td><td>Separate unsuccessful interactions from failed execution</td></tr>
<tr><td>Classify</td><td>~10 min</td><td>Place evidence packs at the correct stage</td></tr>
<tr><td>Read an error</td><td>~10 min</td><td>Translate a documented error into a useful diagnosis</td></tr>
<tr><td>Choose a correction</td><td>~10 min</td><td>Fix only the demonstrated cause</td></tr>
<tr><td>Investigate uncertainty</td><td>~10 min</td><td>Reconcile a timed-out attempt</td></tr>
<tr><td>Understand expiry</td><td>~10 min</td><td>Separate transaction lifetime from observed outcome</td></tr>
<tr><td>Independent challenge</td><td>~10 min</td><td>Produce a diagnosis and recovery plan</td></tr>
<tr><td>Reflect</td><td>~5 min</td><td>Explain when not to retry</td></tr>
</tbody>
</table>

<h2 id=map>6. Stage one — troubleshooting map</h2>
<pre class=diagram>Intention → Construct request → Wallet approval
→ Optional simulation / preflight → Submission
→ Network observation and execution → Required commitment
→ Application reconciles result and state</pre>
<p>Implementations differ in the order and number of simulations. This is a teaching map, not a claim that every wallet follows an identical pipeline.</p>
<p><b>Opening question.</b> The application shows a red message. What does that establish?</p>
<p><b>Expected.</b> Something went wrong in the interaction, but the message alone may not establish where it happened or whether a transaction executed.</p>
<p><b>First diagnostic questions:</b> Was a signature requested? Approved? Broadcast by this attempt? Is a signature known? What do network observation and execution result show? What evidence is still missing?</p>

<h2 id=classify>7. Stage two — classify the four cases</h2>
<p><b>Case A — Wallet rejection.</b> Approval rejected; application submission not initiated. Do not inspect program logs for a profile-update failure that was never established. Respect the rejection; return to review only if the student wants to continue.</p>
<p><b>Case B — Invalid name.</b> Simulation error; not broadcast by this attempt. Correct the input and review a newly constructed request. Do not conclude the network is unavailable or that a fee was paid merely because simulation erred.</p>
<p><b>Case C — Wrong authority.</b> Profile authority A, signer B, documented authority-mismatch error. Confirm intended profile and practice wallet; use the legitimate configured authority if the student controls it; otherwise stop. Never ask for another person’s private key.</p>
<p><b>Case D — Timeout after submission.</b> Approval completed; signature known; submission timed out; execution not yet established. Outcome is unresolved—a timeout does not establish that the update failed. Inspect the existing signature; reconcile; do not immediately construct another update.</p>

<h2 id=error>8. Stage three — read an error without guessing</h2>
<pre class=diagram>ERROR-READING WORKSHEET
What was the intended operation?
Which instruction failed, if identified?
What structured error was returned?
Which documented rule does it relate to?
What relevant evidence supports that interpretation?
What remains uncertain?
What is the smallest justified correction?</pre>
<p>If evidence reports an instruction index, map it to the actual submitted list. Do not assume “Instruction 1” always means the profile update. Explain whether the displayed index is zero-based. An unfamiliar error code is a reason to look up the correct version—not invent a definition.</p>

<h2 id=correct>9. Stage four — choose a targeted correction</h2>
<p>For an input-validation error, choose among: change the RPC endpoint; increase the fee; correct the invalid input. Expected: correct the input—the other changes do not address that demonstrated cause.</p>
<p>Change one justified factor at a time. Before a corrected attempt: re-read the current profile; confirm authority and desired name; review whether the original attempt has a settled outcome; construct a fresh request only when appropriate; request fresh authorisation. Do not silently reuse an old prediction after the starting state changes.</p>

<h2 id=timeout>10. Stage five — reconcile an uncertain attempt</h2>
<pre class=diagram>Intent: "Atlas" → "Harbour" (revision 20 → 21)
Application timed out.

Investigation order:
1. Recover the original attempt record
2. Confirm the intended network
3. Query the known signature
4. Inspect any available execution result and commitment
5. Retrieve the transaction where available
6. Compare the actual instruction with the intended operation
7. Inspect profile state as supporting evidence</pre>
<p>A profile now showing “Harbour” does not necessarily identify which attempt caused the change. A matching current value is not a substitute for reconciling the transaction.</p>
<p><b>Missing status is not proof of failure.</b> Signature-status APIs can return <code>null</code>; by default, search may be limited to a recent status cache. Student wording: “We have not found a status through this query. That is not the same as proving the operation never happened.” If evidence remains insufficient, stop with an unresolved status and seek support.</p>

<h2 id=expiry>11. Stage six — understand expiry without a stopwatch rule</h2>
<p>For recent-blockhash transactions, clients obtain a blockhash with a <code>lastValidBlockHeight</code>. Track that lifetime rather than relying solely on a fixed number of seconds.</p>
<p>A signed transaction has a limited submission lifetime. If that lifetime passes, it cannot newly execute using that expired blockhash—but expiry does not, by itself, prove that the transaction did not execute earlier.</p>
<table>
<thead><tr><th>Situation</th><th>Appropriate reasoning</th></tr></thead>
<tbody>
<tr><td>Original may still be valid</td><td>Do not blindly create a replacement that could also execute</td></tr>
<tr><td>Original succeeded</td><td>Do not repeat the business action</td></tr>
<tr><td>Original failed</td><td>Correct the demonstrated cause before a new attempt</td></tr>
<tr><td>Lifetime expired; outcome sufficiently reconciled as not completed</td><td>Review current state; construct a replacement if still needed</td></tr>
<tr><td>Lifetime expired; historical outcome unresolved</td><td>Escalate or continue reconciliation; do not declare “never happened”</td></tr>
</tbody>
</table>
<p>Re-signing before the earlier transaction has expired can allow both to be accepted. “Wait 30 seconds, then click again” is not a reliable recovery policy. Students are not required to implement RPC polling or rebroadcast code.</p>

<h2 id=challenge>12. Independent challenge</h2>
<table>
<thead><tr><th>Card</th><th>Evidence</th><th>Appropriate response</th></tr></thead>
<tbody>
<tr><td>1</td><td>Wallet rejected; app did not submit</td><td>Respect rejection; no need to invent a program failure</td></tr>
<tr><td>2</td><td>Submitted; execution error = invalid name; profile unchanged; fee charged</td><td>Explain input error and fee; correct input; refresh; review new request</td></tr>
<tr><td>3</td><td>Signature known; submission timed out; one recent-status query null; lifetime not established</td><td>Preserve and reconcile; null does not justify immediate replacement</td></tr>
</tbody>
</table>
<pre class=diagram>For each card:
1. Intended action
2. Last stage established by evidence
3. What is known / unknown
4. Most useful next evidence
5. Appropriate next action / Action to avoid
6. What would justify a new attempt?</pre>

<h2 id=assessment>13. Assessment overview</h2>
<p>Six criteria: stage classification; error interpretation; evidence judgement; targeted correction; safe recovery; incident reporting. All six at least with support. See the <a href="{ASSESS_PATH}">full rubric</a>.</p>
<p><b>Critical misconceptions:</b> a red error means the program ran and failed; a timeout means nothing happened; a <code>null</code> status proves failure; a successful simulation proves submitted success; expiry proves the transaction never executed; increasing the fee fixes any error; sending again is always the fastest safe recovery.</p>

<h2 id=recovery>14. Recovery and accessibility</h2>
<table>
<thead><tr><th>Problem</th><th>Response</th></tr></thead>
<tbody>
<tr><td>Live error cannot be reproduced</td><td>Use a verified evidence pack</td></tr>
<tr><td>Error mapping does not match deployed version</td><td>Pause interpretation; correct the fixture</td></tr>
<tr><td>RPC unavailable</td><td>Preserve progress; do not invent a failure</td></tr>
<tr><td>Transaction history incomplete</td><td>State the limitation and escalate</td></tr>
<tr><td>Cannot use the wallet</td><td>Use the evidence-investigation route</td></tr>
<tr><td>Overwhelmed by logs</td><td>Start with structured error and relevant excerpt</td></tr>
<tr><td>Sensitive data in a support attachment</td><td>Stop sharing; follow the incident process</td></tr>
</tbody>
</table>

<h2 id=gates>15. Release gate</h2>
<ul>
<li>Reproduce every incident pack; validate error mappings against the actual program.</li>
<li>Confirm simulation and submission labels; test timeout reconciliation and missing-status handling.</li>
<li>Validate blockhash-lifetime handling; confirm no automatic duplicate update.</li>
<li>Verify the secret-free reporting workflow; observe new learners selecting a safe next action.</li>
<li>Publish verification date, responsible reviewer, versions, and limitations.</li>
</ul>
<p><b>Understanding to leave with.</b> I do not treat every problem as a failed transaction. I locate the stage, inspect the relevant evidence, explain what remains unknown, and resolve the original attempt before deciding whether to act again.</p>

<h2 id=next>16. Next</h2>
<p>Next foundations step (not yet published): <b>Read and Write Application State — Build a Reliable Client Workflow</b>. Until then, the first live Stage 1 practice remains <a href="/lessons/picassol-hackathon/">Picassol</a>.</p>
<p class=cta>
<a class=btn href="{ASSESS_PATH}">Open the assessment rubric</a>
<a class="btn ghost" href="{L004_PATH}">Previous: Lesson 004</a>
<a class="btn ghost" href="/lessons/path/">Learning path</a>
</p>
'''
  rail = (
    '<nav class=rail aria-label="On this page">'
    '<a href="#outcomes">Outcomes</a><a href="#safety">Safety</a><a href="#app">Attempt record</a>'
    '<a href="#packs">Evidence packs</a><a href="#sequence">Sequence</a><a href="#map">Map</a>'
    '<a href="#classify">Classify</a><a href="#error">Read error</a><a href="#correct">Correct</a>'
    '<a href="#timeout">Timeout</a><a href="#expiry">Expiry</a><a href="#challenge">Challenge</a>'
    '<a href="#assessment">Assessment</a><a href="#recovery">Recovery</a><a href="#gates">Gates</a>'
    '<a href="#next">Next</a></nav>'
  )
  return f'''{css}<div class=readbar aria-hidden=true><span></span></div>
<article class=lesson data-slug="{SLUG}">
<div class=lesson-layout><div class=lesson-main>
<nav class=crumbs aria-label=Breadcrumb><a href="/">Home</a> / <a href="/lessons/">Lessons</a> / <a href="/lessons/path/">Path</a> / <span>Transaction failures</span></nav>
<p class="eyebrow status-preview">Foundations · Lesson 005 · release candidate</p>
<h1>When Transactions Fail</h1>
<p class=lead>Read the evidence. Diagnose the cause. Recover safely.</p>
{body}
</div>{rail}</div>
<div class=dock role=region aria-label="Lesson actions">
<a class=btn href="{ASSESS_PATH}">Assessment rubric</a>
<a class="btn ghost" href="{L004_PATH}">Lesson 004</a>
<button type=button class="btn ghost" data-jump>Next section</button>
</div>
</article>'''


def assessment_html(css=''):
  assert len(LESSON_DESC) <= 158 and len(ASSESS_DESC) <= 158, (len(LESSON_DESC), len(ASSESS_DESC))
  body = f'''{status_panel()}
<p class=lead>Determine whether a student can identify where an interaction went wrong, interpret the relevant evidence, distinguish failure from uncertainty, and choose a recovery action that avoids accidental repetition.</p>
<p>This rubric assesses <a href="{PATH}">Lesson 005</a>’s controlled Profile Card evidence packs. It does not certify production incident-response competence, arbitrary program debugging, or exactly-once guarantees. A live or deliberately failing transaction is never required.</p>

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
<p>Glossary, troubleshooting map, version-matched error reference, attempt record, expiry card, accessibility tools, and ordinary navigation do not reduce an independent result. Looking up an unfamiliar error in the correct reference is expected skill.</p>

<h2 id=materials>Assessment materials</h2>
<p>Fresh packs A–E: approval rejected; simulation failure; execution failure; submission timeout; expiry investigation. Each must identify network, evidence type, source/time, program/client version, known limitations, and whether any conclusion is deliberately unresolved. Do not use invented signatures or undocumented error meanings as if verified.</p>

<h2 id=c1>Criterion 1 — Locates the established failure stage</h2>
<ul>
<li><b>Not yet:</b> treats every error as failed on-chain execution; confuses wallet rejection with program rejection; assigns a definitive outcome to an unresolved timeout.</li>
<li><b>Independently:</b> distinguishes approval rejection, simulation/preflight failure, submitted execution failure, and unresolved observation; states limits of each classification.</li>
</ul>
<p><b>Critical misconception.</b> “The page displayed an error, so the transaction must have executed and failed.”</p>

<h2 id=c2>Criterion 2 — Interprets a documented error</h2>
<ul>
<li><b>Independently:</b> uses the supplied version-matched reference; identifies the failing instruction where available; connects the error to the specific input or authority rule.</li>
</ul>
<p>Do not require memorisation of error codes or interpretation of undocumented codes. Provide the actual instruction list if an index is supplied.</p>

<h2 id=c3>Criterion 3 — Separates known failure from missing evidence</h2>
<pre class=diagram>Wallet approval: Completed
Signature: Known
Submission response: Timed out
One recent-status query: null
Transaction lifetime: Not established</pre>
<ul>
<li><b>Independently:</b> states what is known and unknown; explains why the observation is insufficient; proposes a relevant reconciliation step.</li>
</ul>
<p><b>Critical misconception.</b> Treating a timeout or one <code>null</code> status as proof that the operation never happened.</p>

<h2 id=c4>Criterion 4 — Chooses a targeted correction</h2>
<table>
<thead><tr><th>Demonstrated cause</th><th>Appropriate correction</th></tr></thead>
<tbody>
<tr><td>Name violates documented rule</td><td>Correct the name and review the resulting request</td></tr>
<tr><td>Signer ≠ profile authority</td><td>Confirm profile; select legitimate authorised practice wallet, or stop</td></tr>
<tr><td>Wallet request rejected</td><td>Respect rejection; return to review only if desired</td></tr>
<tr><td>Evidence insufficient</td><td>Continue investigation rather than inventing a fix</td></tr>
</tbody>
</table>
<p>Never recommend obtaining someone else’s signing credentials. Before a new attempt: original outcome sufficiently resolved; current state/authority understood; intended action still needed; new request reviewed and authorised.</p>

<h2 id=c5>Criterion 5 — Recovers without blind repetition</h2>
<table>
<thead><tr><th>Scenario</th><th>Expected reasoning</th></tr></thead>
<tbody>
<tr><td>Original succeeded</td><td>Do not repeat the completed business action</td></tr>
<tr><td>Original failed with documented input error</td><td>Correct cause; refresh state; review a new attempt</td></tr>
<tr><td>Outcome unresolved; may remain valid</td><td>Continue reconciliation; do not blindly replace</td></tr>
<tr><td>Lifetime expired; historical outcome unresolved</td><td>Expiry alone does not justify declaring the operation absent</td></tr>
<tr><td>Lifetime expired; non-completion sufficiently established</td><td>Review current state; decide whether a fresh request is still needed</td></tr>
</tbody>
</table>
<p>Rebroadcasting the same signed transaction and constructing a replacement are different actions. Do not use “retry” so vaguely that the proposed action is unclear.</p>

<h2 id=c6>Criterion 6 — Produces a useful incident report</h2>
<pre class=diagram>INCIDENT SUMMARY
Intended action · Network and application context
Attempt identifier or transaction reference, if available
What the evidence establishes · What remains unknown
Relevant error and reference, if available
Most likely diagnosis, with stated confidence
Next evidence · Recommended next action · Action to avoid
What would justify a new attempt</pre>
<p>If a student includes a secret, stop sharing and follow the college’s incident process before continuing.</p>

<h2 id=checks>Mandatory conceptual checks</h2>
<table>
<thead><tr><th>Check</th><th>Required understanding</th></tr></thead>
<tbody>
<tr><td>Error stage</td><td>Unsuccessful interaction ≠ failed on-chain execution</td></tr>
<tr><td>Simulation</td><td>Simulation ≠ submitted outcome or actual fee payment</td></tr>
<tr><td>Missing evidence</td><td>Timeout or missing status ≠ automatically proof of failure</td></tr>
<tr><td>Expiry</td><td>Expiry ≠ proof that execution never happened earlier</td></tr>
<tr><td>Replacement risk</td><td>Repeating an unresolved action can produce an unintended duplicate</td></tr>
<tr><td>Evidence-led correction</td><td>Recovery should address the demonstrated cause</td></tr>
<tr><td>Secret protection</td><td>No private keys or recovery phrases in records</td></tr>
</tbody>
</table>
<p>Unresolved recovery misconceptions require pause, targeted practice, and fresh reassessment. Strength elsewhere must not compensate.</p>

<h2 id=decisions>Completion decisions</h2>
<table>
<thead><tr><th>Decision</th><th>Requirements</th></tr></thead>
<tbody>
<tr><td>Completed independently</td><td>All six criteria independent; all conceptual checks satisfied</td></tr>
<tr><td>Completed with support</td><td>All six at least with support; all conceptual checks satisfied</td></tr>
<tr><td>Further practice needed</td><td>One or more criteria not yet demonstrated</td></tr>
<tr><td>Assessment paused</td><td>Evidence, infrastructure, accessibility, or disclosure issues prevent fair completion</td></tr>
</tbody>
</table>
<p>Record evidence route: live / captured / mixed. A student can fully demonstrate troubleshooting without submitting a new transaction.</p>

<h2 id=tasks>Standard assessment sequence</h2>
<ol>
<li><b>Classify.</b> Last stage established by each evidence pack (Criterion 1).</li>
<li><b>Diagnose.</b> Use the supplied reference to explain this error (2).</li>
<li><b>Bound uncertainty.</b> Separate known facts from unresolved questions (3).</li>
<li><b>Correct.</b> Choose the smallest justified correction (4).</li>
<li><b>Recover.</b> Investigate, replace, or stop—and why (5).</li>
<li><b>Report.</b> Concise handover for another investigator (6).</li>
</ol>

<h2 id=record>Assessor record template</h2>
<pre class=diagram>SOL.COLLEGE — LESSON 005 ASSESSMENT
Student identifier:
Assessment date:
Lesson version: 1.0
Rubric version: 1.0 — proposed; requires assessor calibration
Assessor:
Evidence route: [ ] Live  [ ] Captured  [ ] Mixed
Criterion 1 — Failure-stage classification:
Criterion 2 — Error interpretation:
Criterion 3 — Failure versus uncertainty:
Criterion 4 — Targeted correction:
Criterion 5 — Safe recovery:
Criterion 6 — Incident report:
Conceptual checks:
[ ] Error stage
[ ] Simulation limits
[ ] Missing evidence
[ ] Expiry limits
[ ] Replacement risk
[ ] Evidence-led correction
[ ] Secret protection
Conceptual prompts:
Decision:
Feedback:
Reassessment required:</pre>
<p class=cta><a class=btn href="{PATH}">Back to Lesson 005</a> <a class="btn ghost" href="{L004_PATH}">Lesson 004</a> <a class="btn ghost" href="/lessons/path/">Learning path</a></p>
'''
  rail = (
    '<nav class=rail aria-label="On this page">'
    '<a href="#levels">Levels</a><a href="#materials">Materials</a><a href="#c1">Stage</a>'
    '<a href="#c2">Error</a><a href="#c3">Uncertainty</a><a href="#c4">Correction</a>'
    '<a href="#c5">Recovery</a><a href="#c6">Report</a><a href="#checks">Checks</a>'
    '<a href="#decisions">Decisions</a><a href="#tasks">Tasks</a><a href="#record">Record</a></nav>'
  )
  return f'''{css}<div class=readbar aria-hidden=true><span></span></div>
<article class=lesson data-slug="{SLUG}-assessment">
<div class=lesson-layout><div class=lesson-main>
<nav class=crumbs aria-label=Breadcrumb><a href="/">Home</a> / <a href="/lessons/">Lessons</a> / <a href="{PATH}">Transaction failures</a> / <span>Assessment</span></nav>
<p class="eyebrow status-preview">Foundations · Lesson 005 assessment · release candidate</p>
<h1>Assessment rubric: Transaction Troubleshooter</h1>
{body}
</div>{rail}</div>
</article>'''


def card_html():
  return (
    f'<article class="card ready-preview" data-lesson data-slug="{SLUG}" data-diff="Beginner" data-format="foundations" '
    f'data-text="transaction failures diagnose recover timeout expiry simulation foundations">'
    f'<p class="eyebrow status-preview">Foundations · Lesson 005 · release candidate</p>'
    f'<h3><a href="{PATH}">Read the evidence. Diagnose the cause. Recover safely.</a></h3>'
    f'<p class=project>When Transactions Fail</p>'
    f'<p class=limit>Known limit: teaching specification only until evidence packs and error mappings are '
    f'reproduced. Classify before retrying — a timeout is not proof of failure.</p>'
    f'<p class=meta><span class="chip beg">Beginner</span> · ~60–75 min design estimate · Evidence packs first</p>'
    f'<p class=cta><a class=btn href="{PATH}">Open Lesson 005</a> · <a href="{ASSESS_PATH}">Assessment rubric</a></p>'
    f'</article>'
  )
