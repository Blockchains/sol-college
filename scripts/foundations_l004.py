"""Solana Foundations Lesson 004: When One Transaction Contains Several Instructions.

Release candidate. Not a live multi-instruction lab and not technically or learner verified.
Teaches: sequential execution, atomicity, fees on failed execution, transaction boundaries.
"""
from __future__ import annotations
import html

SITE = 'https://sol.college'
PUBLISHED = '2026-11-18'
SLUG = 'transaction-atomicity'
PATH = f'/lessons/{SLUG}/'
ASSESS_PATH = f'/lessons/{SLUG}/assessment/'
L001_PATH = '/lessons/first-transaction/'
L002_PATH = '/lessons/accounts-ownership/'
L003_PATH = '/lessons/instructions-programs/'
E = lambda s: html.escape(str(s if s is not None else ''), quote=True)

STATUS_ROWS = [
  ('Status', 'Release candidate. Not yet technically or learner verified.'),
  ('Version', '1.0'),
  ('Track', 'Solana Foundations'),
  ('Prerequisites', 'Lessons 001–003, or equivalent understanding'),
  ('Audience', 'People new to Solana; no programming required'),
  ('Environment', 'Devnet, with local tests and clearly labelled captured evidence'),
  ('Core learning time', 'About 60–75 minutes (design estimate, not a measured claim)'),
  ('Achievement', 'Transaction Investigator: Reason About Atomicity — not awarded until verification gates pass'),
  ('Technical verification', 'Not completed — assert_revision teaching operation not yet deployed for this RC'),
  ('Learner testing', 'Not completed for this release candidate'),
]

LESSON_DESC = (
  'RC foundations lesson: multi-instruction transactions, atomicity, fees on failure, '
  'and transaction boundaries. Not yet technically verified.'
)
ASSESS_DESC = (
  'Rubric for Lesson 004: instruction order, atomicity, fees vs rollback, '
  'evidence types. Release candidate; every criterion required.'
)


def status_panel():
  body = ''.join(f'<dt>{E(k)}</dt><dd>{E(v)}</dd>' for k, v in STATUS_ROWS)
  return (
    '<section class=status-panel aria-label="Lesson status">'
    '<h2>Lesson status</h2>'
    f'<dl class=article-meta>{body}</dl>'
    '<p><b>Publication rule.</b> This page is a teaching specification and interface design. '
    'It must not be labelled verified until <code>assert_revision</code> is implemented and tested, '
    'all challenge cases are reproduced, and learners can explain atomicity without slogans. '
    '<b>Illustrative names and revision numbers on this RC page are not live observations. '
    'Local tests, simulations, and submitted devnet failures are not interchangeable evidence.</b></p>'
    '</section>'
  )


def lesson_html(css=''):
  docs = (
    '<p class=note>Official references: '
    '<a href="https://solana.com/docs/intro/quick-start/writing-to-network">Writing to the network</a>, '
    '<a href="https://solana.com/docs/core/fees/fee-structure">Fee structure</a>, '
    '<a href="https://solana.com/docs/core/transactions/transaction-pipeline">Transaction pipeline</a>. '
    'Instructions run in order; application-state changes are atomic within a transaction. '
    'A failed executed transaction can still charge a fee—do not shorten this to “nothing happens if it fails.”</p>'
  )
  body = f'''{status_panel()}
<p class=lead>In <a href="{L003_PATH}">Lesson 003</a> you followed one instruction from intention to an account change. Now you investigate what happens when a transaction contains several instructions.</p>
<p>You will compare a successful sequence with a sequence that fails partway through, then discover why putting two operations in one transaction is different from sending two transactions.</p>
{docs}

<h2 id=outcomes>1. Learning outcomes</h2>
<table>
<thead><tr><th>Outcome</th><th>Observable demonstration</th></tr></thead>
<tbody>
<tr><td>Identify a transaction’s instruction sequence</td><td>List the relevant instructions in execution order</td></tr>
<tr><td>Reason about sequential execution</td><td>Explain how a later instruction can depend on an earlier one</td></tr>
<tr><td>Explain atomicity</td><td>Predict the final application state when a later instruction fails</td></tr>
<tr><td>Separate state rollback from fees</td><td>Explain why a failed transaction can leave profile state unchanged while charging a fee</td></tr>
<tr><td>Identify the transaction boundary</td><td>Distinguish one multi-instruction transaction from multiple separate transactions</td></tr>
<tr><td>Interpret evidence carefully</td><td>Distinguish logs, simulation, execution results, and persisted state</td></tr>
</tbody>
</table>
<p>The <a href="{ASSESS_PATH}">assessment rubric</a> scores six criteria separately—no compensating total score. Submitting a deliberately failing transaction is not required.</p>

<h2 id=safety>2. Scope and safety</h2>
<p><b>Included:</b> two top-level instructions in one transaction; sequential execution; a later instruction reading an earlier instruction’s successful changes; rollback after failure; fees on an executed failed transaction; absence of automatic rollback across separate transactions.</p>
<p><b>Deferred:</b> CPI; durable nonces; compute optimisation; multi-transaction compensation systems; complex permission aggregation; trading design.</p>
<ul>
<li>Devnet practice funds only. No recovery phrases or private keys.</li>
<li>No real assets held by the teaching program.</li>
<li>Students are not required to submit a deliberately failing transaction.</li>
<li>All intentionally failing requests must be clearly labelled before signing.</li>
<li>Read-only and captured-evidence routes remain available.</li>
</ul>

<h2 id=app>3. Teaching operations (proposed for verified release)</h2>
<p>Reuse the Profile Card program from Lessons 002–003:</p>
<pre class=diagram>Profile state
update_authority: public key
display_name: bounded string
revision: integer

update_profile(new_name)
• Validates profile and authority; validates the name
• Changes display name; increments revision by one
• Leaves update authority unchanged

assert_revision(expected_revision)  ← new teaching operation
• Validates profile account and schema
• Succeeds if revision matches; defined error if not
• Makes no state change</pre>
<p>This is a <b>proposed addition</b> to the teaching program. It must be implemented, tested, and deployed before the live lesson is advertised. The read-only assertion creates a precise question: does the second instruction see the updated revision—and what remains if that second instruction rejects the transaction?</p>
<p class=note>RC honesty: no claim is made that <code>assert_revision</code> exists on a live deployment. Illustrative starting states (e.g. name “Comet”, revision 5) are illustrations—not live observations. Build live cases from the observed starting state.</p>

<h2 id=sequence>4. Lesson sequence</h2>
<table>
<thead><tr><th>Stage</th><th>Time</th><th>Student task</th></tr></thead>
<tbody>
<tr><td>Reconnect</td><td>~5 min</td><td>Identify the instruction and transaction boundary</td></tr>
<tr><td>Predict success</td><td>~10 min</td><td>Trace update followed by matching assertion</td></tr>
<tr><td>Inspect success</td><td>~10 min</td><td>Compare execution evidence with persisted state</td></tr>
<tr><td>Predict failure</td><td>~10 min</td><td>Trace update followed by mismatching assertion</td></tr>
<tr><td>Inspect failure</td><td>~10 min</td><td>Explain rollback, logs, and fee evidence</td></tr>
<tr><td>Separate transactions</td><td>~10 min</td><td>Identify why an earlier transaction remains effective</td></tr>
<tr><td>Independent challenge</td><td>~10 min</td><td>Evaluate reordered and split operations</td></tr>
<tr><td>Reflect</td><td>~5 min</td><td>Explain the atomicity boundary in plain language</td></tr>
</tbody>
</table>

<h2 id=boundary>5. Stage one — locate the boundary</h2>
<pre class=diagram>ONE TRANSACTION
┌──────────────────────────────────────────┐
│ Instruction 1: Update profile            │
│ Instruction 2: Assert profile revision   │
└──────────────────────────────────────────┘

TWO TRANSACTIONS
┌──────────────────────────────────────────┐
│ Transaction A: Update profile            │
└──────────────────────────────────────────┘
┌──────────────────────────────────────────┐
│ Transaction B: Assert profile revision   │
└──────────────────────────────────────────┘</pre>
<p><b>Opening question (ungraded).</b> Both examples contain two operations. Are their failure consequences necessarily the same?</p>
<p>Label transaction boundary, instruction order, target program, participating profile, and arguments. A button labelled “Run both” does not establish that the implementation submits one transaction—inspect the actual structure.</p>

<h2 id=success>6. Stage two — predict a successful sequence</h2>
<p><b>Case A — Update, then check the new revision</b> (illustrative starting state):</p>
<pre class=diagram>name: "Comet"   revision: 5

Instruction 1: update_profile("Orbit")
Instruction 2: assert_revision(6)</pre>
<pre class=diagram>PREDICTION WORKSHEET
After instruction 1 succeeds, I expect name / revision:
When instruction 2 runs, I expect it to read revision:
I expect instruction 2 to: [Succeed / Fail / Insufficient information]
If the transaction succeeds, the final profile should be:</pre>
<p><b>Expected reasoning.</b> Instruction 1 updates the name and increases the revision to 6. Instruction 2 runs afterwards and checks that updated revision. If all relevant conditions pass, the transaction succeeds and the updated profile persists.</p>
<p>Say: “The earlier instruction’s changes are available to the later instruction during execution.” Do <b>not</b> say: “The first instruction has permanently settled before the second begins.” The final outcome still depends on the rest of the transaction.</p>

<h2 id=inspect-ok>7. Stage three — inspect the successful result</h2>
<p>Use a live transaction where feasible, or verified captured evidence. Before signing: confirm network, program, profile, name, expected revision, fee payer, exact instruction sequence, and no unexpected operation. Then apply Lesson 001 verification: match the transaction; execution success; <code>finalized</code>; resulting profile; actual fee.</p>

<h2 id=fail>8. Stage four — predict a failing sequence</h2>
<p><b>Case B — Update, then check the old revision</b> (illustrative):</p>
<pre class=diagram>Starting name: "Orbit"   revision: 6

Instruction 1: update_profile("Nova")
Instruction 2: assert_revision(6)</pre>
<ol>
<li>What revision should instruction 1 produce?</li>
<li>What revision will instruction 2 compare against?</li>
<li>Should the assertion pass?</li>
<li>What profile state should remain after the transaction fails?</li>
<li>Could a transaction fee still be charged?</li>
</ol>
<p><b>Expected reasoning (reveal after predictions).</b> Instruction 1 would move the revision to 7; instruction 2 expects 6, so it fails; the profile update does not persist (name “Orbit”, revision 6); if submitted and executed as a failed transaction, a fee can still be charged.</p>

<h2 id=inspect-fail>9. Stage five — inspect failure without confusing evidence types</h2>
<p>Default route: reviewed local test, simulation, or captured devnet failure—labelled prominently.</p>
<table>
<thead><tr><th>Evidence type</th><th>What students may conclude</th></tr></thead>
<tbody>
<tr><td>Local test</td><td>Behaviour reproduced in the stated test environment</td></tr>
<tr><td>Simulation</td><td>Observed simulated execution under the stated conditions</td></tr>
<tr><td>Submitted devnet failure</td><td>A recorded transaction failed on devnet</td></tr>
<tr><td>Post-transaction state read</td><td>The profile’s observed state at the stated time and commitment</td></tr>
</tbody>
</table>
<p>A simulation does <b>not</b> establish that an actual fee was paid.</p>
<p>Inspect separately: (A) execution trace—instruction 1 may complete before instruction 2 errors; (B) persisted profile state—retains starting name and revision; (C) fee evidence—for an actual submitted executed failure, inspect the charged fee.</p>
<p><b>Misconception check.</b> “The logs say the first instruction succeeded. Does that establish that its update persisted?”</p>
<p><b>Expected.</b> No. Check the final transaction result and state evidence. A later failure can roll back that update.</p>

<h2 id=split>10. Stage six — split into separate transactions</h2>
<p><b>Case C — Successful update, then a separate failed check</b> (illustrative):</p>
<pre class=diagram>Start: name "Orbit", revision 6
Transaction A: update_profile("Nova")  → verified success → name "Nova", revision 7
Transaction B: assert_revision(6)      → fails</pre>
<p><b>Question.</b> Does Transaction B’s failure automatically restore the profile to “Orbit,” revision 6?</p>
<p><b>Expected.</b> No. The profile update completed in a separate successful transaction. The later failure does not automatically reverse it.</p>
<table>
<thead><tr><th>Arrangement</th><th>Outcome in this controlled example</th></tr></thead>
<tbody>
<tr><td>Update + failing assertion in one transaction</td><td>Profile update rolls back</td></tr>
<tr><td>Successful update, then failing assertion separately</td><td>Earlier profile update remains</td></tr>
<tr><td>Simulation only</td><td>Does not persist the update or establish payment of a real fee</td></tr>
</tbody>
</table>
<p><b>Product-design connection.</b> If a website shows one “Complete setup” button but sends three transactions, can it promise that all three happen or none happen? Not merely because they share one button—inspect transaction boundaries and recovery design.</p>

<h2 id=challenge>11. Independent challenge</h2>
<p>Starting state (illustration): name “Atlas”, revision 10. Assume all other checks pass and no concurrent updates.</p>
<table>
<thead><tr><th>Card</th><th>Arrangement</th></tr></thead>
<tbody>
<tr><td>A</td><td>One tx: update_profile("Beacon"); assert_revision(11)</td></tr>
<tr><td>B</td><td>One tx: update_profile("Beacon"); assert_revision(10)</td></tr>
<tr><td>C</td><td>One tx: assert_revision(10); update_profile("Beacon")</td></tr>
</tbody>
</table>
<p><b>Instructor key.</b> A: assertion passes after update → success → Beacon, 11. B: assertion fails after update → failure; update rolls back → Atlas, 10. C: assertion passes before update → success → Beacon, 11.</p>
<p><b>Follow-up.</b> Cards A and C have the same final state. Do they check the same condition at the same point? No—A checks the resulting revision after the update; C checks the starting revision before it.</p>

<h2 id=assessment>12. Assessment overview</h2>
<p>Six criteria: boundary identification; sequential reasoning; atomicity; fee distinction; evidence interpretation; transfer of understanding. All six at least with support. Record live / captured / mixed evidence route. See the <a href="{ASSESS_PATH}">full rubric</a>.</p>
<p><b>Critical misconceptions:</b> every instruction is a separate transaction; a successful instruction log proves its change persisted; a failed transaction always costs nothing; a later transaction automatically reverses an earlier one; one interface button means one atomic operation; a successful simulation proves the update happened on-chain.</p>

<h2 id=recovery>13. Recovery and accessibility</h2>
<table>
<thead><tr><th>Situation</th><th>Required response</th></tr></thead>
<tbody>
<tr><td>Starting revision has changed</td><td>Refresh and explain; rebuild only after reviewing the new state</td></tr>
<tr><td>Transaction status unresolved</td><td>Reconcile the existing attempt before repeating</td></tr>
<tr><td>Expected failure blocked by preflight</td><td>Record that no failed on-chain execution was demonstrated; use reviewed evidence</td></tr>
<tr><td>Logs unavailable</td><td>Do not invent the instruction trace</td></tr>
<tr><td>Unexpected state change</td><td>Stop the clean comparison; investigate concurrency or fixtures</td></tr>
<tr><td>Funding unavailable</td><td>Continue through the captured-evidence route</td></tr>
<tr><td>Student rejects the request</td><td>Return to review without penalty</td></tr>
</tbody>
</table>
<p>For optional submitted failures, disclose: “This transaction is intentionally expected to fail and may charge a devnet fee.” Do not silently disable preflight merely to complete a demonstration.</p>

<h2 id=gates>14. Release gate</h2>
<ul>
<li>Verify update and assertion behaviour; reproduce all independent challenge cases.</li>
<li>Confirm instruction order; unchanged profile after failed combined transaction; retained profile after separate failed transaction.</li>
<li>Distinguish simulated fee estimates from actually charged fees.</li>
<li>Test concurrent-update and unresolved-status handling; review evidence labels.</li>
<li>Observe learners explaining without slogans; publish versions, verification date, reviewer, limitations.</li>
</ul>
<p><b>Understanding to leave with.</b> Instructions run in order, but their application-state changes only persist if the transaction succeeds as a whole. A failed executed transaction can still charge a fee. Separate transactions have separate outcomes.</p>

<h2 id=next>15. Next</h2>
<p>Next foundations step (not yet published): <b>When Transactions Fail — Read Errors, Diagnose Causes, Recover Safely</b>. Until then, the first live Stage 1 practice remains <a href="/lessons/picassol-hackathon/">Picassol</a>.</p>
<p class=cta>
<a class=btn href="{ASSESS_PATH}">Open the assessment rubric</a>
<a class="btn ghost" href="{L003_PATH}">Previous: Lesson 003</a>
<a class="btn ghost" href="/lessons/path/">Learning path</a>
</p>
'''
  rail = (
    '<nav class=rail aria-label="On this page">'
    '<a href="#outcomes">Outcomes</a><a href="#safety">Safety</a><a href="#app">Teaching ops</a>'
    '<a href="#sequence">Sequence</a><a href="#boundary">Boundary</a><a href="#success">Success</a>'
    '<a href="#inspect-ok">Inspect OK</a><a href="#fail">Failure</a><a href="#inspect-fail">Inspect fail</a>'
    '<a href="#split">Split txs</a><a href="#challenge">Challenge</a><a href="#assessment">Assessment</a>'
    '<a href="#recovery">Recovery</a><a href="#gates">Release gates</a><a href="#next">Next</a></nav>'
  )
  return f'''{css}<div class=readbar aria-hidden=true><span></span></div>
<article class=lesson data-slug="{SLUG}">
<div class=lesson-layout><div class=lesson-main>
<nav class=crumbs aria-label=Breadcrumb><a href="/">Home</a> / <a href="/lessons/">Lessons</a> / <a href="/lessons/path/">Path</a> / <span>Transaction atomicity</span></nav>
<p class="eyebrow status-preview">Foundations · Lesson 004 · release candidate</p>
<h1>When One Transaction Contains Several Instructions</h1>
<p class=lead>Understand the order. Predict the outcome. Find the boundary.</p>
{body}
</div>{rail}</div>
<div class=dock role=region aria-label="Lesson actions">
<a class=btn href="{ASSESS_PATH}">Assessment rubric</a>
<a class="btn ghost" href="{L003_PATH}">Lesson 003</a>
<button type=button class="btn ghost" data-jump>Next section</button>
</div>
</article>'''


def assessment_html(css=''):
  assert len(LESSON_DESC) <= 158 and len(ASSESS_DESC) <= 158, (len(LESSON_DESC), len(ASSESS_DESC))
  body = f'''{status_panel()}
<p class=lead>Determine whether a student can trace instruction order, identify transaction boundaries, predict application-state rollback, distinguish fees from rolled-back changes, and interpret evidence accurately.</p>
<p>This rubric assesses <a href="{PATH}">Lesson 004</a>’s controlled Profile Card examples. It does not certify arbitrary transaction analysis, production recovery design, or smart-contract security review. A deliberately failing transaction is never required for completion.</p>

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
<p>Glossary, documented teaching-program rules, worksheets, calculator, accessibility tools, and ordinary navigation do not reduce an independent result. Example prompt: “Check whether the failed assertion is in the same transaction as the update.”</p>

<h2 id=materials>Assessment setup</h2>
<p>Supply <code>update_profile</code> and <code>assert_revision</code> rules explicitly. Evidence package: starting state; transaction diagrams; successful combined tx; failed combined tx; separate-transaction example; fee evidence (actual charged fee or clearly labelled alternative); independent scenarios; provenance. A simulator’s fee estimate must not be labelled as an actually paid fee.</p>

<h2 id=c1>Criterion 1 — Identifies transaction boundaries</h2>
<ul>
<li><b>Not yet:</b> treats every instruction as a separate transaction, or assumes one interface button guarantees one transaction.</li>
<li><b>Independently:</b> groups instructions by actual transaction boundary; explains that interface grouping does not establish atomicity.</li>
</ul>
<p><b>Critical misconception.</b> “They were launched by the same button, so they must succeed or fail together.”</p>

<h2 id=c2>Criterion 2 — Traces sequential execution</h2>
<p>Start Atlas/10; one tx: update_profile("Beacon"), assert_revision(11).</p>
<ul>
<li><b>Independently:</b> tracks state after each instruction; explains what the next reads; distinguishes intermediate execution state from the final persisted result.</li>
</ul>
<p>Expected: revision becomes 11 during execution; assertion reads 11; the first instruction is not a separately completed transaction.</p>

<h2 id=c3>Criterion 3 — Predicts rollback after a later failure</h2>
<p>Start Atlas/10/A; one tx: update_profile("Beacon"), assert_revision(10). Instruction 1 succeeds during execution; instruction 2 fails.</p>
<ul>
<li><b>Independently:</b> later failure prevents profile changes from persisting → final Atlas, 10, authority A.</li>
</ul>
<p><b>Critical misconception.</b> “The logs say the first instruction succeeded, so the name must now be Beacon.”</p>

<h2 id=c4>Criterion 4 — Separates rollback from transaction fees</h2>
<table>
<thead><tr><th>Case</th><th>What to establish</th></tr></thead>
<tbody>
<tr><td>Reject wallet request before submission</td><td>Does not establish executed on-chain tx or charged fee</td></tr>
<tr><td>Simulation reports program failure</td><td>Simulated execution—not evidence of an actual fee</td></tr>
<tr><td>Submitted tx executes and fails</td><td>Inspect metadata for actual charged fee; profile changes may still roll back</td></tr>
</tbody>
</table>
<ul>
<li><b>Independently:</b> a submitted executed failure can charge a fee while profile changes roll back; distinguish rejection before submission and simulation-only evidence.</li>
</ul>

<h2 id=c5>Criterion 5 — Interprets different evidence types</h2>
<ul>
<li><b>Independently:</b> uses each evidence source for its appropriate purpose; checks provenance and timing; identifies when the conclusion remains unresolved.</li>
</ul>
<p>A justified “insufficient evidence” is a valid demonstration of judgement. Do not invent conclusions from missing traces.</p>

<h2 id=c6>Criterion 6 — Applies the boundary to new arrangements</h2>
<p>Start each from Cedar/20:</p>
<table>
<thead><tr><th>Scenario</th><th>Arrangement</th><th>Expected</th><th>Final</th></tr></thead>
<tbody>
<tr><td>A</td><td>One tx: update Harbour, assert 21</td><td>Success</td><td>Harbour, 21</td></tr>
<tr><td>B</td><td>One tx: update Harbour, assert 20</td><td>Failure; rollback</td><td>Cedar, 20</td></tr>
<tr><td>C</td><td>One tx: assert 20, then update Harbour</td><td>Success</td><td>Harbour, 21</td></tr>
<tr><td>D</td><td>Tx1 updates Harbour (verified); Tx2 asserts 20 and fails</td><td>Earlier remains</td><td>Harbour, 21</td></tr>
</tbody>
</table>
<p><b>Follow-up.</b> A and C finish with the same state—did they check the same condition at the same point? No: A checks after the update; C checks before.</p>

<h2 id=checks>Mandatory conceptual checks</h2>
<table>
<thead><tr><th>Check</th><th>Required understanding</th></tr></thead>
<tbody>
<tr><td>Transaction boundary</td><td>One transaction can contain several instructions</td></tr>
<tr><td>Execution order</td><td>A later instruction can read earlier changes during that transaction’s execution</td></tr>
<tr><td>Atomicity</td><td>A later failure prevents the combined transaction’s profile changes from persisting</td></tr>
<tr><td>Fee distinction</td><td>Application-state rollback does not necessarily reverse a charged execution fee</td></tr>
<tr><td>Separate outcomes</td><td>A later failed transaction does not automatically reverse an earlier successful one</td></tr>
<tr><td>Evidence limits</td><td>Logs or simulation alone do not establish persisted on-chain state</td></tr>
</tbody>
</table>
<p>Unresolved atomicity misconceptions require pause, targeted practice, and fresh reassessment. Strength elsewhere must not compensate.</p>

<h2 id=decisions>Completion decisions</h2>
<table>
<thead><tr><th>Decision</th><th>Requirements</th></tr></thead>
<tbody>
<tr><td>Completed independently</td><td>All six criteria independent; all conceptual checks satisfied</td></tr>
<tr><td>Completed with support</td><td>All six at least with support; all conceptual checks satisfied</td></tr>
<tr><td>Further practice needed</td><td>At least one criterion not yet demonstrated</td></tr>
<tr><td>Assessment paused</td><td>Technical, accessibility, or evidence issues prevent fair assessment</td></tr>
</tbody>
</table>
<p>Record evidence route: live practical / captured-evidence / mixed. Local tests and simulations must be identified—not described as live devnet transactions.</p>

<h2 id=tasks>Standard assessment sequence</h2>
<ol>
<li><b>Identify boundaries.</b> Mark which instructions belong to each transaction (Criterion 1).</li>
<li><b>Trace execution.</b> Write the revision after each instruction (2).</li>
<li><b>Predict failure.</b> Final profile after the later instruction fails (3).</li>
<li><b>Explain cost.</b> Whether this evidence establishes a fee was charged (4).</li>
<li><b>Evaluate evidence.</b> What each record proves and what remains unknown (5).</li>
<li><b>Transfer understanding.</b> Resolve the four fresh scenarios and explain the difference (6).</li>
</ol>
<p>Record predictions before revealing corresponding results.</p>

<h2 id=record>Assessor record template</h2>
<pre class=diagram>SOL.COLLEGE — LESSON 004 ASSESSMENT
Student identifier:
Assessment date:
Lesson version: 1.0
Rubric version: 1.0 — proposed; requires assessor calibration
Assessor:
Evidence route: [ ] Live practical  [ ] Captured evidence  [ ] Mixed
Evidence types: [ ] Submitted devnet  [ ] Local test  [ ] Simulation  [ ] Captured state
Criterion 1 — Transaction boundaries:
Criterion 2 — Sequential execution:
Criterion 3 — Atomic rollback:
Criterion 4 — Fees and rollback:
Criterion 5 — Evidence interpretation:
Criterion 6 — Independent application:
Conceptual checks:
[ ] Transaction boundary
[ ] Execution order
[ ] Atomicity
[ ] Fee distinction
[ ] Separate outcomes
[ ] Evidence limits
Conceptual prompts:
Decision:
Feedback:
Reassessment required:</pre>
<p class=cta><a class=btn href="{PATH}">Back to Lesson 004</a> <a class="btn ghost" href="{L003_PATH}">Lesson 003</a> <a class="btn ghost" href="/lessons/path/">Learning path</a></p>
'''
  rail = (
    '<nav class=rail aria-label="On this page">'
    '<a href="#levels">Levels</a><a href="#materials">Materials</a><a href="#c1">Boundaries</a>'
    '<a href="#c2">Sequence</a><a href="#c3">Rollback</a><a href="#c4">Fees</a>'
    '<a href="#c5">Evidence</a><a href="#c6">Transfer</a><a href="#checks">Checks</a>'
    '<a href="#decisions">Decisions</a><a href="#tasks">Tasks</a><a href="#record">Record</a></nav>'
  )
  return f'''{css}<div class=readbar aria-hidden=true><span></span></div>
<article class=lesson data-slug="{SLUG}-assessment">
<div class=lesson-layout><div class=lesson-main>
<nav class=crumbs aria-label=Breadcrumb><a href="/">Home</a> / <a href="/lessons/">Lessons</a> / <a href="{PATH}">Transaction atomicity</a> / <span>Assessment</span></nav>
<p class="eyebrow status-preview">Foundations · Lesson 004 assessment · release candidate</p>
<h1>Assessment rubric: Transaction Investigator</h1>
{body}
</div>{rail}</div>
</article>'''


def card_html():
  return (
    f'<article class="card ready-preview" data-lesson data-slug="{SLUG}" data-diff="Beginner" data-format="foundations" '
    f'data-text="transaction atomicity multi instruction rollback fee assert revision foundations">'
    f'<p class="eyebrow status-preview">Foundations · Lesson 004 · release candidate</p>'
    f'<h3><a href="{PATH}">Understand the order. Predict the outcome. Find the boundary.</a></h3>'
    f'<p class=project>When One Transaction Contains Several Instructions</p>'
    f'<p class=limit>Known limit: teaching specification only until <code>assert_revision</code> is deployed and verified. '
    f'Failed executed transactions can still charge a fee.</p>'
    f'<p class=meta><span class="chip beg">Beginner</span> · ~60–75 min design estimate · Devnet or captured evidence</p>'
    f'<p class=cta><a class=btn href="{PATH}">Open Lesson 004</a> · <a href="{ASSESS_PATH}">Assessment rubric</a></p>'
    f'</article>'
  )
