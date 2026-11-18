"""Solana Foundations Lesson 003: Instructions and Programs.

Release candidate. Not a live instruction inspector product and not technically or learner verified.
Teaches: how an instruction becomes a verified account change; request ≠ outcome.
"""
from __future__ import annotations
import html

SITE = 'https://sol.college'
PUBLISHED = '2026-11-18'
SLUG = 'instructions-programs'
PATH = f'/lessons/{SLUG}/'
ASSESS_PATH = f'/lessons/{SLUG}/assessment/'
L001_PATH = '/lessons/first-transaction/'
L002_PATH = '/lessons/accounts-ownership/'
E = lambda s: html.escape(str(s if s is not None else ''), quote=True)

STATUS_ROWS = [
  ('Status', 'Release candidate. Not yet technically or learner verified.'),
  ('Version', '1.0'),
  ('Track', 'Solana Foundations'),
  ('Prerequisites', 'Lessons 001 and 002, or equivalent understanding'),
  ('Audience', 'People new to Solana; no programming required'),
  ('Environment', 'Solana devnet, with a clearly labelled captured-evidence alternative'),
  ('Core learning time', 'About 60 minutes (design estimate, not a measured claim)'),
  ('Achievement', 'Instruction Investigator: Trace and Verify — not awarded until verification gates pass'),
  ('Technical verification', 'Not completed — Profile Card update instruction and decoder not yet verified for this RC'),
  ('Learner testing', 'Not completed for this release candidate'),
]

LESSON_DESC = (
  'RC foundations lesson: inspect a Solana instruction, predict state change, '
  'trace intent to evidence. Not yet technically verified.'
)
ASSESS_DESC = (
  'Rubric for Lesson 003: instruction structure, permissions vs authority, '
  'prediction, evidence tracing. Release candidate; every criterion required.'
)


def status_panel():
  body = ''.join(f'<dt>{E(k)}</dt><dd>{E(v)}</dd>' for k, v in STATUS_ROWS)
  return (
    '<section class=status-panel aria-label="Lesson status">'
    '<h2>Lesson status</h2>'
    f'<dl class=article-meta>{body}</dl>'
    '<p><b>Publication rule.</b> This page is a teaching specification and interface design. '
    'It must not be labelled verified until the complete update workflow is reproduced against a '
    'deployed teaching program, the inspector matches the actual instruction, and a new learner can '
    'complete the independent mismatch challenge. '
    '<b>Do not treat schematic instruction panels on this RC page as live transaction evidence. '
    'Illustrative, simulated, local-test, and submitted-devnet records are not interchangeable.</b></p>'
    '</section>'
  )


def lesson_html(css=''):
  docs = (
    '<p class=note>Official references: '
    '<a href="https://solana.com/docs/core/instructions">Instructions</a>, '
    '<a href="https://solana.com/docs/core/instructions/instruction-structure">Instruction structure</a>, '
    '<a href="https://solana.com/docs/core/instructions/instruction-introspection">Instruction introspection</a>. '
    'An instruction identifies a program, an ordered account list, and data interpreted by that program.</p>'
  )
  body = f'''{status_panel()}
<p class=lead>In <a href="{L001_PATH}">Lesson 001</a> you authorised a transfer and verified its result. In <a href="{L002_PATH}">Lesson 002</a> you separated program ownership from application authority. Now you connect them: how does clicking “Update profile” become a request a program can understand—and an account change you can verify?</p>
<p>You will inspect an instruction, predict its effect, review the transaction carrying it, and compare the result with your intention.</p>
{docs}

<h2 id=not>1. What this lesson is not</h2>
<p>You are not yet writing a Solana program, manually encoding instruction bytes, or auditing arbitrary wallet requests. The goal is to understand the structure and trace one controlled operation.</p>

<h2 id=outcomes>2. Learning outcomes</h2>
<table>
<thead><tr><th>Outcome</th><th>Observable demonstration</th></tr></thead>
<tbody>
<tr><td>Distinguish instruction, program, account, and transaction</td><td>Correctly explain each role in a profile update</td></tr>
<tr><td>Identify an instruction’s three components</td><td>Locate the program ID, account list, and instruction data</td></tr>
<tr><td>Explain account permissions</td><td>Distinguish signer and writable requirements without treating either as unlimited authority</td></tr>
<tr><td>Predict the intended state change</td><td>Describe what should change and what should remain unchanged</td></tr>
<tr><td>Trace intent to evidence</td><td>Compare the submitted operation and resulting state with the original intention</td></tr>
<tr><td>Recognise interpretation limits</td><td>Explain why a friendly label, successful simulation, or plausible-looking byte string is insufficient by itself</td></tr>
</tbody>
</table>
<p>The <a href="{ASSESS_PATH}">assessment rubric</a> scores six criteria separately—no compensating total score.</p>

<h2 id=safety>3. Scope and safety</h2>
<p><b>Included:</b> one bounded profile-update instruction; program ID; account metadata; instruction data and decoded representation; requested permissions versus program authorisation; before-and-after state; a transaction containing the update.</p>
<p><b>Deferred:</b> PDA derivation and signing; CPI; address lookup tables; manual serialization; general-purpose transaction decoding; multi-instruction rollback experiments; program deployment.</p>
<ul>
<li>Devnet only. No real-money deposit.</li>
<li>No recovery phrases or private keys submitted to the lesson.</li>
<li>No signature request merely to inspect an instruction.</li>
<li>Reject an unexpected request.</li>
<li>Do not repeat an unresolved transaction before reconciling the existing attempt.</li>
</ul>
<p>A read-only evidence route remains available if wallet or funding access is unavailable.</p>

<h2 id=app>4. Reuse the Lesson 002 teaching application</h2>
<p>Same reviewed Profile Card program and schema:</p>
<pre class=diagram>Profile state
update_authority: public key
display_name: bounded string
revision: integer

Documented update operation must:
1. Check the expected profile account
2. Require the configured update authority to sign
3. Validate the proposed display name
4. Change the display name
5. Increase the revision by one
6. Leave the update authority unchanged</pre>
<p>These are requirements for the teaching application—not claims about an existing deployed implementation on this RC page.</p>
<p><b>Controlled experiment:</b> the student’s profile already exists; allocated space supports the permitted update; the student controls its configured update authority; no account creation, reallocation, token operation, or SOL transfer is included; fees are paid by an identified practice account; optional reset is a separate explained operation.</p>

<h2 id=sequence>5. Lesson sequence</h2>
<table>
<thead><tr><th>Stage</th><th>Time</th><th>Student task</th></tr></thead>
<tbody>
<tr><td>Connect concepts</td><td>~5 min</td><td>Map intention → instruction → transaction → state change</td></tr>
<tr><td>Inspect instruction</td><td>~10 min</td><td>Program ID, accounts, instruction data</td></tr>
<tr><td>Predict</td><td>~5 min</td><td>Record expected before/after state</td></tr>
<tr><td>Review and submit</td><td>~10 min</td><td>Compare request; approve or reject</td></tr>
<tr><td>Verify</td><td>~10 min</td><td>Match intent, submitted instruction, and observed state</td></tr>
<tr><td>Controlled failures</td><td>~5 min</td><td>Wrong authority, invalid input, missing writable</td></tr>
<tr><td>Independent challenge</td><td>~10 min</td><td>Select matching instruction card; reject mismatches</td></tr>
</tbody>
</table>

<h2 id=workspace>6. Lesson workspace (product requirement)</h2>
<pre class=diagram>LESSON 003 — INSTRUCTIONS AND PROGRAMS
Steps: Understand → Inspect → Predict → Review → Verify → Independent investigation

LEARN                         INSPECT
What is the program           Program [address + verified label]
being asked to do?            Accounts [role / signer / writable]
                              Instruction data [decoded op + args]
                              [Show raw representation]</pre>
<p>Keep raw bytes collapsed initially. Clearly label whether a panel is an illustrative example, a locally constructed instruction, a simulation, or an actual submitted transaction.</p>

<h2 id=concepts>7. Stage one — connect the four concepts</h2>
<pre class=diagram>Student intention → Client constructs an instruction → Transaction carries it
→ Required parties authorise → Network executes → Program validates
→ Profile state changes—or the operation fails</pre>
<table>
<thead><tr><th>Concept</th><th>Role in this exercise</th></tr></thead>
<tbody>
<tr><td>Program</td><td>Implements the profile-update rules</td></tr>
<tr><td>Account</td><td>Holds the profile state or participates in authorisation</td></tr>
<tr><td>Instruction</td><td>Specifies the requested operation and inputs</td></tr>
<tr><td>Transaction</td><td>Carries the instruction for authorisation and execution</td></tr>
</tbody>
</table>
<p><b>Checkpoint.</b> Is the button labelled “Update profile” itself the instruction?</p>
<p><b>Expected.</b> No. It is an interface action that causes the client to construct a request. Inspect what the client actually constructs.</p>

<h2 id=inspect>8. Stage two — inspect the instruction</h2>
<p>An instruction has three central components: <b>program ID</b>, <b>account metadata</b>, and <b>instruction data</b>.</p>
<h3>A — Program ID</h3>
<pre class=diagram>Target program: [teaching program address]</pre>
<p>A familiar program name does <b>not</b> establish that this is the intended program address. The address must match the reviewed configuration for this environment.</p>
<h3>B — Accounts</h3>
<p>Illustrative teaching design (must be checked against the real instruction definition before verified release):</p>
<table>
<thead><tr><th>Position</th><th>Role</th><th>Signer?</th><th>Writable?</th></tr></thead>
<tbody>
<tr><td>1</td><td>Profile state</td><td>No</td><td>Yes</td></tr>
<tr><td>2</td><td>Update authority</td><td>Yes</td><td>No</td></tr>
</tbody>
</table>
<ul>
<li><b>Signer</b> means the operation requires the relevant signing authority.</li>
<li><b>Writable</b> allows the account to be modified during execution, subject to runtime and program rules.</li>
<li>Neither flag removes the need for the program’s validation logic.</li>
</ul>
<p>Label views separately: <b>Instruction requirements</b> vs <b>Transaction-level permissions</b>. The authority may also be the fee payer; transaction-level permissions can differ from the standalone instruction view.</p>
<h3>C — Instruction data</h3>
<pre class=diagram>Decoded operation: update_profile
Arguments: display_name = "Comet"
Raw instruction data: [actual encoded bytes — collapsed by default]</pre>
<p>The network does not infer the meaning of “Comet.” The program interprets the supplied bytes using its defined encoding. Students are not required to memorise the encoding.</p>

<h2 id=predict>9. Stage three — predict the state change</h2>
<pre class=diagram>BEFORE
display_name: "Practice Profile"
revision: 4
update_authority: [address A]

NEW NAME: "Comet"

Expected after success:
display_name: "Comet"
revision: 5
update_authority: unchanged</pre>
<pre class=diagram>PREDICTION WORKSHEET
I expect the instruction to call: ________
I expect it to update this profile: ________
The required update authority is: ________
After success — display_name / revision / update_authority:
Fee payer: ________</pre>
<p>Distinguish the profile-data update from the fee payer’s SOL balance change.</p>

<h2 id=review>10. Stage four — review before signing</h2>
<ol>
<li>Review the target program, profile account, required update authority, and proposed name.</li>
<li>Identify the fee payer and estimated fee.</li>
<li>Inspect the transaction request.</li>
<li>Reject it if it does not match the intended action.</li>
<li>Approve only when the request is understood.</li>
</ol>
<pre class=diagram>PRACTICE PROFILE UPDATE
Network: Devnet
Program: [address]   Profile: [address]
Change: "Practice Profile" → "Comet"
Expected revision: 4 → 5
Update authority: Unchanged
Fee payer: [address]
No intended token transfer.
No intended SOL transfer beyond the network fee.
[Review wallet request]</pre>
<p>Wallets may not decode the custom operation into the same friendly description. Do <b>not</b> teach “the website says it is safe, so ignore the wallet.” If you cannot reconcile the request with the reviewed teaching interface and documented program, stop and ask for help.</p>
<p>The lesson’s custom inspector is scoped to this known program—not a universal transaction-safety tool.</p>
<p><b>Simulation, if available:</b> a pre-submission check, not a guarantee. “This simulation reports what happened under the simulated conditions. We still need to inspect the actual submitted transaction and resulting state.”</p>

<h2 id=verify>11. Stage five — verify what happened</h2>
<p>Reuse Lesson 001’s verification process: correct network; matching transaction; successful execution; required <code>finalized</code> commitment; actual fee payer and fee; no unexplained extra operation. Then connect to the account investigation.</p>
<table>
<thead><tr><th>Layer</th><th>Question</th></tr></thead>
<tbody>
<tr><td>Intent</td><td>What did I mean to request?</td></tr>
<tr><td>Submitted instruction</td><td>Which program, accounts, and arguments were actually supplied?</td></tr>
<tr><td>Observed state</td><td>What changed in the profile?</td></tr>
</tbody>
</table>
<table>
<thead><tr><th>Item</th><th>Expected</th><th>Observed</th></tr></thead>
<tbody>
<tr><td>Target program</td><td>Reviewed teaching program</td><td></td></tr>
<tr><td>Profile account</td><td>Student’s prepared profile</td><td></td></tr>
<tr><td>Operation</td><td>Update display name</td><td></td></tr>
<tr><td>Name</td><td>Student’s chosen name</td><td></td></tr>
<tr><td>Revision</td><td>Previous revision + 1</td><td></td></tr>
<tr><td>Update authority</td><td>Unchanged</td><td></td></tr>
<tr><td>Execution</td><td>Succeeded</td><td></td></tr>
<tr><td>Commitment</td><td>Finalized</td><td></td></tr>
</tbody>
</table>
<p><b>State-evidence limitation.</b> An instruction records the request. It does not, by itself, provide a complete before-and-after account-data history. Capture initial state, retrieve resulting state, use an isolated profile, record observation slots/times, and pause if another update intervenes.</p>

<h2 id=failures>12. Stage six — investigate controlled failures</h2>
<p>Use reviewed captured tests or simulations. Students do not need to pay fees to produce these failures.</p>
<p><b>Case A — Wrong authority.</b> Stored A, signer B. Marking B as a signer does <b>not</b> make B authorised; the program must check against the stored authority.</p>
<p><b>Case B — Invalid input.</b> Correct authority signs, but the name violates validation. A valid signature does <b>not</b> guarantee success.</p>
<p><b>Case C — Read-only profile.</b> Required permissions and program authorisation are separate. An authorised signer does not make every requested write permissible.</p>

<h2 id=challenge>13. Independent challenge</h2>
<p>Three prepared instruction cards (labelled simulations—not real unexpected wallet requests):</p>
<table>
<thead><tr><th>Card</th><th>Description</th></tr></thead>
<tbody>
<tr><td>A</td><td>Correct program, profile, authority, and permitted name</td></tr>
<tr><td>B</td><td>Correct-looking operation label but the wrong target program</td></tr>
<tr><td>C</td><td>Correct target program but the wrong profile account</td></tr>
</tbody>
</table>
<ol>
<li>Identify the card matching the stated intention.</li>
<li>Explain the role of its three instruction components.</li>
<li>Identify the required signer and writable account.</li>
<li>Predict the profile changes.</li>
<li>Explain why the other cards should not be approved for this intention.</li>
</ol>

<h2 id=assessment>14. Assessment overview</h2>
<p>Six criteria: concept separation; instruction structure; permission reasoning; prediction; evidence tracing; judgement (reject mismatches and name evidence limits). All six at least with support for completion. Record live practical vs captured-evidence route. See the <a href="{ASSESS_PATH}">full rubric</a>.</p>
<p><b>Critical misconceptions:</b> transaction = instruction; a signer can change any account; writable means the program must change the account; a valid signature guarantees success; a friendly label proves the request; a successful simulation proves the submitted transaction succeeded.</p>

<h2 id=recovery>15. Recovery and accessibility</h2>
<table>
<thead><tr><th>Situation</th><th>Required response</th></tr></thead>
<tbody>
<tr><td>Profile missing</td><td>Restore or prepare a fixture before continuing</td></tr>
<tr><td>Authority does not match student</td><td>Explain; never ask for someone else’s secret</td></tr>
<tr><td>Decoder unavailable</td><td>Do not invent a decoded instruction</td></tr>
<tr><td>Program or schema mismatch</td><td>Stop the live workflow and flag the environment</td></tr>
<tr><td>Wallet rejects</td><td>Return to review without penalty</td></tr>
<tr><td>Transaction unresolved</td><td>Reconcile before retrying</td></tr>
<tr><td>Concurrent state change</td><td>Explain ambiguity; repeat only when controlled</td></tr>
<tr><td>RPC unavailable</td><td>Save progress or use labelled captured evidence</td></tr>
<tr><td>Cannot use the wallet</td><td>Continue with the conceptual assessment</td></tr>
</tbody>
</table>

<h2 id=gates>16. Release gate</h2>
<ul>
<li>Reproduce the complete workflow.</li>
<li>Confirm the inspector matches the actual instruction.</li>
<li>Confirm the decoder matches the deployed schema.</li>
<li>Check transaction-level versus instruction-level permission displays.</li>
<li>Test state observations and concurrency handling.</li>
<li>Confirm rejection and failure cases; label all captured evidence correctly.</li>
<li>Observe new learners completing the independent challenge.</li>
<li>Publish verification date, versions, responsible reviewer, and limitations.</li>
</ul>
<p><b>Understanding to leave with.</b> An instruction tells a specific program what operation is requested, which accounts participate, and what inputs to use. The program and runtime still enforce the rules. Verify the submitted request and the resulting state rather than trusting the button label.</p>

<h2 id=next>17. Next</h2>
<p>Next foundations step: <a href="/lessons/transaction-atomicity/">Lesson 004 — When One Transaction Contains Several Instructions</a> (release candidate). Until foundations are verified, the first live Stage 1 practice remains <a href="/lessons/picassol-hackathon/">Picassol</a>.</p>
<p class=cta>
<a class=btn href="{ASSESS_PATH}">Open the assessment rubric</a>
<a class="btn ghost" href="/lessons/transaction-atomicity/">Next: Lesson 004</a>
<a class="btn ghost" href="{L002_PATH}">Previous: Lesson 002</a>
</p>
'''
  rail = (
    '<nav class=rail aria-label="On this page">'
    '<a href="#not">Scope</a><a href="#outcomes">Outcomes</a><a href="#safety">Safety</a>'
    '<a href="#app">Teaching app</a><a href="#sequence">Sequence</a><a href="#workspace">Workspace</a>'
    '<a href="#concepts">Concepts</a><a href="#inspect">Inspect</a><a href="#predict">Predict</a>'
    '<a href="#review">Review</a><a href="#verify">Verify</a><a href="#failures">Failures</a>'
    '<a href="#challenge">Challenge</a><a href="#assessment">Assessment</a><a href="#recovery">Recovery</a>'
    '<a href="#gates">Release gates</a><a href="#next">Next</a></nav>'
  )
  return f'''{css}<div class=readbar aria-hidden=true><span></span></div>
<article class=lesson data-slug="{SLUG}">
<div class=lesson-layout><div class=lesson-main>
<nav class=crumbs aria-label=Breadcrumb><a href="/">Home</a> / <a href="/lessons/">Lessons</a> / <a href="/lessons/path/">Path</a> / <span>Instructions and programs</span></nav>
<p class="eyebrow status-preview">Foundations · Lesson 003 · release candidate</p>
<h1>Instructions and Programs</h1>
<p class=lead>How an action becomes an account change</p>
{body}
</div>{rail}</div>
<div class=dock role=region aria-label="Lesson actions">
<a class=btn href="{ASSESS_PATH}">Assessment rubric</a>
<a class="btn ghost" href="/lessons/transaction-atomicity/">Next: Lesson 004</a>
<button type=button class="btn ghost" data-jump>Next section</button>
</div>
</article>'''


def assessment_html(css=''):
  assert len(LESSON_DESC) <= 158 and len(ASSESS_DESC) <= 158, (len(LESSON_DESC), len(ASSESS_DESC))
  body = f'''{status_panel()}
<p class=lead>Determine whether a student can interpret a prepared instruction, distinguish permissions from authority, predict a controlled state change, and trace the outcome back to the original intention.</p>
<p>This rubric assesses <a href="{PATH}">Lesson 003</a>’s reviewed Profile Card examples. It does not certify decoding arbitrary transactions, auditing programs, or establishing that an unfamiliar wallet request is safe.</p>

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
<p>Glossary, instruction-structure card, schema, update rule, prediction worksheet, accessibility tools, and ordinary navigation do not reduce an independent result. Example conceptual prompt: “A signer flag and the program’s authority check answer different questions.”</p>

<h2 id=materials>Assessment materials</h2>
<p>Fresh evidence package: intent card; initial state with observation time/slot; instruction record; transaction record; resulting state; challenge cards A–C; provenance note (live / simulated / local test / captured). Decoder and schema must match the reviewed teaching program.</p>

<h2 id=c1>Criterion 1 — Distinguishes the four core concepts</h2>
<ul>
<li><b>Not yet:</b> treats button, instruction, program, and transaction as interchangeable.</li>
<li><b>With support:</b> distinguishes the four after a prompt.</li>
<li><b>Independently:</b> program implements rules; profile account stores state; instruction requests an operation; transaction carries it for authorisation and execution.</li>
</ul>
<p><b>Critical misconception.</b> “The button label is the instruction, so it tells us exactly what will happen.”</p>

<h2 id=c2>Criterion 2 — Interprets the instruction’s three components</h2>
<ul>
<li><b>Not yet:</b> confuses program ID with profile address; omits a component; relies on a friendly label without context.</li>
<li><b>With support:</b> identifies the three components after prompting.</li>
<li><b>Independently:</b> identifies program ID, ordered account list, and instruction data; uses supplied decoder and schema.</li>
</ul>
<p>Do not require memorising addresses, manual byte decoding, or serialization internals.</p>

<h2 id=c3>Criterion 3 — Separates permissions from authorisation</h2>
<p>Assume stored update authority is A.</p>
<table>
<thead><tr><th>Scenario</th><th>Expected reasoning</th></tr></thead>
<tbody>
<tr><td>A signs; profile writable; inputs valid</td><td>Stated conditions satisfied</td></tr>
<tr><td>B signs; profile writable</td><td>Signer ≠ stored-authority match</td></tr>
<tr><td>A listed but has not signed</td><td>Including the address ≠ signer requirement</td></tr>
<tr><td>A signs; profile not writable</td><td>Authorisation does not supply missing writable access</td></tr>
</tbody>
</table>
<p><b>Independently:</b> required authority must actually sign; profile must be writable; program must still validate the signer and enforce other rules.</p>

<h2 id=c4>Criterion 4 — Predicts the intended change and its boundaries</h2>
<ul>
<li><b>Not yet:</b> predicts an authority change; omits revision rule; invents an intended asset transfer; cannot identify fee payer.</li>
<li><b>Independently:</b> predicts chosen display name, revision +1, unchanged update authority, fee payer cost; distinguishes these from the profile-data change.</li>
</ul>

<h2 id=c5>Criterion 5 — Traces intention to execution and observed state</h2>
<ul>
<li><b>Not yet:</b> treats success notification, signature, decoded request, or simulation as sufficient proof of the completed state change.</li>
<li><b>Independently:</b> matches submitted program/accounts/arguments to intent; checks successful execution and <code>finalized</code>; compares appropriately sourced before-and-after state.</li>
</ul>
<p>If another update intervenes or observations cannot be reconciled, “the comparison is inconclusive” is appropriate—mark affected evidence not assessable rather than requiring a false conclusion.</p>

<h2 id=c6>Criterion 6 — Rejects mismatches and limits unsupported conclusions</h2>
<table>
<thead><tr><th>Card</th><th>Prepared request</th></tr></thead>
<tbody>
<tr><td>A</td><td>Correct program, profile, authority, and permitted name</td></tr>
<tr><td>B</td><td>Familiar operation label but wrong target program</td></tr>
<tr><td>C</td><td>Correct program but wrong profile account</td></tr>
</tbody>
</table>
<ul>
<li><b>Independently:</b> selects A; rejects B and C with specific reasons; explains at least one meaningful limitation of labels, decoding, or simulation.</li>
</ul>
<p>Do not require declaring a mismatched request malicious. Establishing that it does not match the intention is enough.</p>

<h2 id=checks>Mandatory conceptual checks</h2>
<table>
<thead><tr><th>Check</th><th>Required understanding</th></tr></thead>
<tbody>
<tr><td>Instruction versus transaction</td><td>Related but not interchangeable</td></tr>
<tr><td>Program identity</td><td>A friendly name does not replace the target program address</td></tr>
<tr><td>Signer versus authority</td><td>A signature alone does not satisfy every program rule</td></tr>
<tr><td>Writable versus permission to act</td><td>Writable access does not grant unrestricted authorisation</td></tr>
<tr><td>Request versus outcome</td><td>Constructing, decoding, or simulating a request does not prove its submitted outcome</td></tr>
<tr><td>Matching intention</td><td>A wrong program or profile is sufficient reason to stop</td></tr>
</tbody>
</table>
<p>Unresolved critical misconceptions require pause, targeted practice, and fresh reassessment. Strength elsewhere must not compensate.</p>

<h2 id=decisions>Completion decisions</h2>
<table>
<thead><tr><th>Decision</th><th>Requirements</th></tr></thead>
<tbody>
<tr><td>Completed independently</td><td>All six criteria independent; all conceptual checks satisfied</td></tr>
<tr><td>Completed with support</td><td>All six at least with support; all conceptual checks satisfied</td></tr>
<tr><td>Further practice needed</td><td>One or more criteria not yet demonstrated</td></tr>
<tr><td>Assessment paused</td><td>Technical, accessibility, or evidence issues prevent fair judgement</td></tr>
</tbody>
</table>
<p>Record evidence route: live practical / captured-evidence / mixed. Captured-evidence can establish conceptual understanding; it must not be recorded as a live transaction completed by the student. A technically successful update must not automatically award the lesson.</p>

<h2 id=tasks>Standard assessment sequence</h2>
<ol>
<li><b>Explain the workflow.</b> How the button action becomes an account change (Criterion 1).</li>
<li><b>Inspect the instruction.</b> Three components and their roles (2).</li>
<li><b>Apply the rules.</b> Signer and writable scenarios (3).</li>
<li><b>Predict.</b> What should change and remain unchanged (4).</li>
<li><b>Verify.</b> Compare intention, submitted request, and observed outcome (5).</li>
<li><b>Challenge.</b> Select matching card; reject mismatches; state an evidence limit (6).</li>
</ol>

<h2 id=record>Assessor record template</h2>
<pre class=diagram>SOL.COLLEGE — LESSON 003 ASSESSMENT
Student identifier:
Assessment date:
Lesson version: 1.0
Rubric version: 1.0 — proposed; requires assessor calibration
Assessor:
Evidence route: [ ] Live practical  [ ] Captured evidence  [ ] Mixed
Network: Program/interface version: Profile specimen:
Transaction reference, if applicable:
Criterion 1 — Concept separation:
Criterion 2 — Instruction structure:
Criterion 3 — Permissions and authorisation:
Criterion 4 — Predicted changes:
Criterion 5 — Evidence tracing:
Criterion 6 — Judgement and evidence limits:
Conceptual checks:
[ ] Instruction versus transaction
[ ] Program identity
[ ] Signer versus authority
[ ] Writable versus authorisation
[ ] Request versus outcome
[ ] Matching intention
Conceptual prompts:
Decision:
Feedback:
Reassessment required:</pre>
<p class=cta><a class=btn href="{PATH}">Back to Lesson 003</a> <a class="btn ghost" href="{L002_PATH}">Lesson 002</a> <a class="btn ghost" href="/lessons/path/">Learning path</a></p>
'''
  rail = (
    '<nav class=rail aria-label="On this page">'
    '<a href="#levels">Levels</a><a href="#materials">Materials</a><a href="#c1">Concepts</a>'
    '<a href="#c2">Structure</a><a href="#c3">Permissions</a><a href="#c4">Prediction</a>'
    '<a href="#c5">Tracing</a><a href="#c6">Judgement</a><a href="#checks">Checks</a>'
    '<a href="#decisions">Decisions</a><a href="#tasks">Tasks</a><a href="#record">Record</a></nav>'
  )
  return f'''{css}<div class=readbar aria-hidden=true><span></span></div>
<article class=lesson data-slug="{SLUG}-assessment">
<div class=lesson-layout><div class=lesson-main>
<nav class=crumbs aria-label=Breadcrumb><a href="/">Home</a> / <a href="/lessons/">Lessons</a> / <a href="{PATH}">Instructions and programs</a> / <span>Assessment</span></nav>
<p class="eyebrow status-preview">Foundations · Lesson 003 assessment · release candidate</p>
<h1>Assessment rubric: Instruction Investigator</h1>
{body}
</div>{rail}</div>
</article>'''


def card_html():
  return (
    f'<article class="card ready-preview" data-lesson data-slug="{SLUG}" data-diff="Beginner" data-format="foundations" '
    f'data-text="instructions programs update profile trace verify simulation foundations">'
    f'<p class="eyebrow status-preview">Foundations · Lesson 003 · release candidate</p>'
    f'<h3><a href="{PATH}">How an action becomes an account change</a></h3>'
    f'<p class=project>Instructions and Programs</p>'
    f'<p class=limit>Known limit: teaching specification only until the Profile Card update instruction '
    f'and decoder are verified. Simulation is not proof of submitted success.</p>'
    f'<p class=meta><span class="chip beg">Beginner</span> · ~60 min design estimate · Devnet or captured evidence</p>'
    f'<p class=cta><a class=btn href="{PATH}">Open Lesson 003</a> · <a href="{ASSESS_PATH}">Assessment rubric</a></p>'
    f'</article>'
  )
