"""Solana Foundations Lesson 001: Your First Solana Transaction.

Release candidate. Not a live-dApp walkthrough and not technically or learner verified.
Teaches: review intent, verify execution and commitment separately, stop when uncertain.
"""
from __future__ import annotations
import html, json, os
import foundations_l002 as l002

SITE = 'https://sol.college'
PUBLISHED = '2026-11-18'
SLUG = 'first-transaction'
PATH = f'/lessons/{SLUG}/'
ASSESS_PATH = f'/lessons/{SLUG}/assessment/'
L002_PATH = l002.PATH
E = lambda s: html.escape(str(s if s is not None else ''), quote=True)

STATUS_ROWS = [
  ('Status', 'Release candidate. Not yet technically or learner verified.'),
  ('Version', '1.1'),
  ('Track', 'Solana Foundations'),
  ('Audience', 'People new to Solana; no programming required'),
  ('Environment', 'Devnet only'),
  ('Core learning time', 'About 45–60 minutes (design estimate, not a measured claim)'),
  ('Setup allowance', 'Up to 15 additional minutes; not assessed'),
  ('Achievement', 'First Transaction: Authorise and Verify — not awarded until verification gates pass'),
  ('Technical verification', 'Not completed for this release candidate'),
  ('Learner testing', 'Not completed for this release candidate'),
]


def status_panel():
  body = ''.join(f'<dt>{E(k)}</dt><dd>{E(v)}</dd>' for k, v in STATUS_ROWS)
  return (
    '<section class=status-panel aria-label="Lesson status">'
    '<h2>Lesson status</h2>'
    f'<dl class=article-meta>{body}</dl>'
    '<p><b>Publication rule.</b> This page is a teaching specification and interface design. '
    'It must not be labelled verified until an end-to-end transfer is reproduced, '
    'execution and commitment are checked separately in the product, and a new learner can complete it without instructor gap-filling.</p>'
    '</section>'
  )


def outcomes():
  items = [
    'Identify the intended network, sender, recipient, amount, and fee payer.',
    'Compare the wallet request with the intended action and reject a mismatch.',
    'Establish whether the transaction executed successfully and reached the lesson’s required commitment.',
    'Reconcile the transfer and fee, then explain what the evidence does not establish.',
  ]
  return '<ol>' + ''.join(f'<li>{E(x)}</li>' for x in items) + '</ol>'


def lesson_html(css=''):
  docs = (
    '<p class=note>Official references for the distinction this lesson teaches: '
    '<a href="https://solana.com/docs/core/transactions/transaction-pipeline">Transaction pipeline</a>, '
    '<a href="https://solana.com/docs/core/fees/fee-structure">Fee structure</a>, '
    '<a href="https://solana.com/docs/core/transactions/transaction-structure">Transaction structure</a>. '
    'A signature identifies an attempt; it is not, by itself, proof of successful execution.</p>'
  )
  body = f'''{status_panel()}
<p class=lead>By the end of this lesson, you will be able to review a simple Solana transfer before approving it, check whether it actually succeeded, and explain where the funds and fee went.</p>
<p>You will use <b>devnet practice SOL</b>—not real-money funds. You can stop, reject an unexpected request, or ask for help at any time. Stopping when something looks wrong is good practice.</p>
{docs}

<h2 id=promise>1. Scope and hard limits</h2>
<p>This lesson covers one simple transfer of native <b>devnet SOL</b> between two practice wallets under your control. It does not teach token transfers, program deployment, custody, investing, or general wallet security.</p>
<ul>
<li>Do not deposit real funds to complete the lesson.</li>
<li>Do not connect an everyday wallet that holds valuable assets.</li>
<li>Do not paste a recovery phrase or private key into Sol.College.</li>
<li>Do not share a secret in a screenshot, support message, or submitted work.</li>
<li>Do not approve an unexpected action merely to make progress.</li>
</ul>

<h2 id=outcomes>2. Four measurable outcomes</h2>
{outcomes()}
<p>Keep these visible while you work. The <a href="{ASSESS_PATH}">assessment rubric</a> scores each one separately. A high score on one criterion cannot compensate for failing a safety gate.</p>

<h2 id=environment>3. Controlled practice environment</h2>
<p>Use two dedicated, already-funded practice wallets:</p>
<ul>
<li><b>Practice Wallet A</b> — sender (and, in this lesson, fee payer).</li>
<li><b>Practice Wallet B</b> — recipient.</li>
</ul>
<p>The recipient does <b>not</b> need to approve this simple transfer. The sender authorises the movement from the sending account.</p>
<p>Environment requirements for a verified release (not yet satisfied for this RC): established wallet integrations only; no custom recovery-phrase UI; both addresses exist as suitable System Program accounts; recipient ≠ sender; application configuration prevents accidental mainnet submission; unnecessary signing actions disabled.</p>
<aside class=goals><h3>Preflight checklist (setup, not assessed)</h3>
<pre class=diagram>PRACTICE ENVIRONMENT
Application network: Devnet
Sending address: [address]
Recipient address: [address]
✓ Addresses are different
✓ Sender has sufficient practice funds
✓ Recipient is an existing suitable practice account
✓ Current balance data retrieved
Transfer amount: [amount]
Estimated transaction fee: [estimate]
[Start lesson]</pre>
<p>Check wallet network information where the integration exposes it. Do not pretend every wallet exposes an authoritative network-selection state. Identify the application’s RPC/network configuration clearly.</p>
<p>If practice funding is unavailable: save progress, offer another implemented route, or use a labelled observation mode. Never require a purchase or mainnet deposit as a workaround.</p>
</aside>

<h2 id=sequence>4. Lesson sequence</h2>
<table>
<thead><tr><th>Stage</th><th>Time</th><th>Student action</th></tr></thead>
<tbody>
<tr><td>Orient</td><td>~5 min</td><td>Learn the five things to check</td></tr>
<tr><td>See one example</td><td>~5 min</td><td>Examine an annotated transfer</td></tr>
<tr><td>Predict</td><td>~5 min</td><td>Record expected action and changes</td></tr>
<tr><td>Review and act</td><td>~10 min</td><td>Compare the request and approve or reject</td></tr>
<tr><td>Verify</td><td>~10 min</td><td>Check execution, commitment, and evidence</td></tr>
<tr><td>Explain</td><td>~5 min</td><td>Reconcile funds and fee</td></tr>
<tr><td>Independent challenge</td><td>~10 min</td><td>Repeat with less guidance</td></tr>
<tr><td>Exit check</td><td>~5 min</td><td>Explain a mismatch and an uncertain outcome</td></tr>
</tbody>
</table>
<p>Times are design estimates, not measured completion claims.</p>

<h2 id=five-checks>5. Stage one — five checks</h2>
<table>
<thead><tr><th>Term</th><th>Meaning in this lesson</th></tr></thead>
<tbody>
<tr><td>Network</td><td>The environment where this transfer will occur</td></tr>
<tr><td>Sender</td><td>The address whose SOL is being transferred</td></tr>
<tr><td>Recipient</td><td>The address intended to receive it</td></tr>
<tr><td>Amount</td><td>The practice SOL being transferred</td></tr>
<tr><td>Fee payer</td><td>The account paying the network transaction fee</td></tr>
</tbody>
</table>
<pre class=diagram>Before approving:
1. Am I in the intended practice environment?
2. Is the correct sending account selected?
3. Is the recipient correct?
4. Is the amount correct?
5. Does the requested action match this lesson?</pre>
<p><b>Critical interaction rule.</b> If the wallet request is unclear or does not match: reject it and return to review. Approval must not be the only action that advances the lesson.</p>

<h2 id=example>6. Stage two — one worked example</h2>
<pre class=diagram>DEMONSTRATION — NOT YOUR TRANSACTION
Intent: Transfer practice SOL from A to B.
Authorisation: A signs the transaction.
Submission: The signed transaction is sent to the network.
Observation: The application checks its status and execution result.
Accounting: B receives the transfer. A pays the transfer and applicable fee.</pre>
<p>If using real demonstration evidence, name the network and transaction. If using a schematic, label it as an illustration.</p>
<p><b>First comprehension question.</b> A transaction identifier is visible. What should you check next?</p>
<p><b>Expected response.</b> Whether it was observed on the intended network, whether <b>execution succeeded</b>, and whether it reached the required <b>commitment</b>. An identifier comes from a signature; its existence alone is not proof of successful execution.</p>

<h2 id=predict>7. Stage three — predict</h2>
<pre class=diagram>MY INTENT
Network:
Sender:
Recipient:
Transfer amount:
Expected fee payer:
I expect the recipient’s balance to: [Increase / Decrease / Stay the same]
I expect the sender’s balance to decrease by: [Transfer only / Transfer plus fee / Unsure]
Before approving, I will check: ________________</pre>
<p>Allow “Unsure.” The prediction is diagnostic, not a penalty. Store locally or through an explicitly consented learning account. Do not collect secrets.</p>

<h2 id=review>8. Stage four — review and act</h2>
<ol>
<li>Review the intended transfer in Sol.College.</li>
<li>Open the wallet request.</li>
<li>Compare the request with your intention.</li>
<li>Reject it if anything is unexpected.</li>
<li>Approve only when you understand the requested action.</li>
<li>Observe the application’s progress.</li>
</ol>
<p><b>Interface requirement — two separate status dimensions.</b></p>
<table>
<thead><tr><th>Dimension</th><th>Example states</th></tr></thead>
<tbody>
<tr><td>Observation / commitment</td><td>Not observed, processed, confirmed, finalized, unresolved</td></tr>
<tr><td>Execution result</td><td>Unknown, succeeded, failed</td></tr>
</tbody>
</table>
<p>Do <b>not</b> collapse these into one green “Confirmed” badge. A transaction can be confirmed on the network and still have failed execution while charging a fee.</p>
<p><b>Recommended completion condition for the practical transfer.</b> Treat it as successful only when:</p>
<ul>
<li>It is retrieved from the intended <b>devnet</b> environment.</li>
<li>The decoded transfer matches the intended sender, recipient, and amount.</li>
<li>The execution result contains <b>no error</b>.</li>
<li>It reaches the configured <code>finalized</code> commitment.</li>
</ul>
<p>You may show successful execution at an earlier commitment as an intermediate observation, but label it accurately. If finalization is delayed, preserve the attempt and let the learner resume. Finalization is the teaching policy for this lesson, not a universal Solana requirement.</p>

<h2 id=verify>9. Stage five — inspect the result</h2>
<pre class=diagram>DID IT DO WHAT YOU INTENDED?
Network: Devnet
Execution: Succeeded
Commitment: Finalized
Sender: [address]
Recipient: [address]
Transferred: [actual amount]
Fee payer: [address]
Fee charged: [actual fee]
[Inspect transaction]  [Show balance accounting]</pre>
<p>The panel must display <b>actual verified values</b>, not echoes of the original form. The verifier should inspect network configuration, the transaction matching the recorded signature, execution error metadata, required commitment, expected System Program transfer, source/destination/amount, fee payer, any reviewed compute-budget instructions the builder adds, and absence of unexpected value-moving instructions.</p>

<h2 id=accounting>10. Stage six — reconcile</h2>
<p>For the successful controlled transaction, where the sender pays the fee and no other balance-changing operation is included:</p>
<pre class=diagram>Sender decrease = Transfer amount + Transaction fee
Recipient increase = Transfer amount</pre>
<p>Use integer lamports internally. Convert for display without floating-point accounting. Prefer transaction-specific pre- and post-balances over two live wallet snapshots, which may include other activity.</p>
<p><b>Failure distinction (taught with a reviewed example, not required as a live failure).</b> If execution fails after fees are charged, the intended transfer may not occur even though the fee payer’s balance decreases. The documented pipeline can preserve the fee deduction while discarding other execution changes.</p>

<h2 id=explain>11. Stage seven — explain the evidence</h2>
<pre class=diagram>I intended to transfer ______ from ______ to ______ on devnet.
Before approval, I checked ______.
I established the result by checking ______.
The sender’s balance decreased by ______ because ______.
This record does not establish ______.</pre>
<p>Acceptable evidence limits include: an address does not establish real-world identity; successful execution does not establish a merchant’s honesty; this devnet exercise does not prove a mainnet payment; this simple transfer does not demonstrate that every wallet request is safe.</p>

<h2 id=challenge>12. Independent challenge</h2>
<p>Repeat with a different permitted amount, the same two practice wallets, the detailed walkthrough collapsed, and the five-check card still available. Independently: record intent, review the wallet request, approve or reject, inspect execution and commitment, reconcile, explain one evidence limitation.</p>
<p>Help ladder (recorded to guide support, not treated as misconduct): remind me of the goal → show the five checks → point me to the relevant evidence → show a worked explanation.</p>

<h2 id=scenarios>13. Two essential non-transaction challenges</h2>
<section class=instr>
<h3>Challenge A — destination mismatch</h3>
<p>Show a <b>labelled simulation</b> of an approval request whose recipient differs from the stated intention. Do not generate a real harmful signing request.</p>
<p><b>Question.</b> Approve, reject, or ask for clarification?</p>
<p><b>Expected.</b> Reject and investigate the mismatch.</p>
</section>
<section class=instr>
<h3>Challenge B — uncertain result</h3>
<p>Scenario: you approved a transfer; the page timed out; you have a transaction identifier, but the result is not yet established.</p>
<p><b>Expected.</b> Inspect or reconcile the existing attempt before initiating another transfer. Do not reward repeatedly pressing Send.</p>
</section>

<h2 id=assessment>14. Assessment and completion</h2>
<p>Use the <a href="{ASSESS_PATH}">Lesson 001 assessment rubric</a>. Four criteria, each marked <i>Not yet demonstrated</i>, <i>Demonstrated with support</i>, or <i>Demonstrated independently</i>:</p>
<ol>
<li>Safe authorisation (checks intent; rejects the simulated mismatch).</li>
<li>Correct verification (distinguishes identifier, execution result, and commitment).</li>
<li>Accounting (explains recipient increase and sender decrease).</li>
<li>Evidence boundaries (explains uncertainty and at least one limit of the record).</li>
</ol>
<p>Award the achievement only when the student completes a successful practical transfer, demonstrates all four criteria, and resolves any unsafe misconception through targeted reassessment. Observation-only participation earns a separate “Introduction completed” status—not practical mastery.</p>

<h2 id=recovery>15. Recovery and accessibility</h2>
<table>
<thead><tr><th>Situation</th><th>Required response</th></tr></thead>
<tbody>
<tr><td>Funding unavailable</td><td>Save progress; offer a documented alternative</td></tr>
<tr><td>Approval rejected</td><td>Return to review without blame</td></tr>
<tr><td>Unexpected wallet request</td><td>Stop, reject, and investigate</td></tr>
<tr><td>Insufficient funds</td><td>Recalculate amount and fee</td></tr>
<tr><td>Status unresolved</td><td>Reconcile; do not automatically send again</td></tr>
<tr><td>Execution failed</td><td>Explain the error and any charged fee</td></tr>
<tr><td>Explorer unavailable</td><td>Use the application’s sourced evidence; restore the link later</td></tr>
<tr><td>Page refreshed</td><td>Recover the existing attempt without resubmitting</td></tr>
<tr><td>Cannot operate the wallet</td><td>Accessible assistance or labelled observation mode</td></tr>
</tbody>
</table>
<p>Support keyboard operation, screen readers, readable addresses, non-colour status labels, adjustable text, and untimed approvals. Infrastructure failure must not fail the conceptual assessment.</p>

<h2 id=gates>16. Release checklist (before calling this verified)</h2>
<h3>Technical gate</h3>
<ul>
<li>End-to-end transfer reproduced.</li>
<li>Actual transaction data drives results.</li>
<li>Execution and commitment checked separately.</li>
<li>Balance equations match the constrained transaction.</li>
<li>Fee and amount estimation use current data.</li>
<li>Rejection, failure, timeout, refresh, and recovery tested.</li>
<li>Duplicate submission prevented.</li>
<li>No secret-bearing telemetry.</li>
<li>Practice funding and fallback verified.</li>
</ul>
<h3>Teaching gate</h3>
<ul>
<li>A new learner can start without instructor gap-filling.</li>
<li>Vocabulary is introduced before use.</li>
<li>The worked example does not reveal every assessment answer.</li>
<li>Learners explain outcomes rather than merely copy values.</li>
<li>Mismatch and uncertainty scenarios detect misconceptions.</li>
<li>Timing adjusted from observed sessions.</li>
<li>Accessibility barriers documented and addressed.</li>
</ul>
<h3>Publication gate</h3>
<ul>
<li>Named content owner.</li>
<li>Technical verification date.</li>
<li>Tested environment and versions.</li>
<li>Known limitations.</li>
<li>Correction-reporting link.</li>
<li>Review triggers for wallet or application changes.</li>
</ul>

<h2 id=next>17. Next</h2>
<p>Next foundations step: <a href="{L002_PATH}">Lesson 002 — Accounts, Ownership, and Authority</a> (release candidate). After foundations, the first live Stage 1 practice is <a href="/lessons/picassol-hackathon/">Picassol</a> — paint an on-chain pixel and meet PDAs.</p>
<p class=cta>
<a class=btn href="{ASSESS_PATH}">Open the assessment rubric</a>
<a class="btn ghost" href="{L002_PATH}">Next: Lesson 002</a>
<a class="btn ghost" href="/lessons/path/">Learning path</a>
</p>
<p class=note>Final judgment for this RC: it teaches three habits — review intent, verify evidence, stop when uncertain — but it is not “the best lesson” until a real beginner uses it, a technical reviewer reproduces it, and accessibility review is done.</p>
'''
  rail = (
    '<nav class=rail aria-label="On this page">'
    '<a href="#promise">Scope</a><a href="#outcomes">Outcomes</a><a href="#environment">Environment</a>'
    '<a href="#sequence">Sequence</a><a href="#five-checks">Five checks</a><a href="#example">Example</a>'
    '<a href="#predict">Predict</a><a href="#review">Review</a><a href="#verify">Verify</a>'
    '<a href="#accounting">Accounting</a><a href="#explain">Explain</a><a href="#challenge">Challenge</a>'
    '<a href="#scenarios">Scenarios</a><a href="#assessment">Assessment</a><a href="#recovery">Recovery</a>'
    '<a href="#gates">Release gates</a><a href="#next">Next</a></nav>'
  )
  return f'''{css}<div class=readbar aria-hidden=true><span></span></div>
<article class=lesson data-slug="{SLUG}">
<div class=lesson-layout><div class=lesson-main>
<nav class=crumbs aria-label=Breadcrumb><a href="/">Home</a> / <a href="/lessons/">Lessons</a> / <a href="/lessons/path/">Path</a> / <span>First transaction</span></nav>
<p class="eyebrow status-preview">Foundations · Lesson 001 · release candidate</p>
<h1>Your First Solana Transaction</h1>
<p class=lead>Know what you approve. Prove what happened.</p>
{body}
</div>{rail}</div>
<div class=dock role=region aria-label="Lesson actions">
<a class=btn href="{ASSESS_PATH}">Assessment rubric</a>
<a class="btn ghost" href="{L002_PATH}">Next: Lesson 002</a>
<button type=button class="btn ghost" data-jump>Next section</button>
</div>
</article>'''


def assessment_html(css=''):
  body = f'''{status_panel()}
<p class=lead>Determine whether the student can review a simple devnet SOL transfer, verify its outcome, explain the accounting, and respond safely to uncertainty.</p>
<p>This rubric assesses the outcomes in <a href="{PATH}">Lesson 001</a>. It does not certify general wallet security, programming ability, or readiness to handle real funds.</p>

<h2 id=levels>Performance levels</h2>
<table>
<thead><tr><th>Level</th><th>Meaning</th></tr></thead>
<tbody>
<tr><td>Not yet demonstrated</td><td>Evidence missing, materially incorrect, or shows an unresolved misconception</td></tr>
<tr><td>Demonstrated with support</td><td>Correct after a conceptual prompt</td></tr>
<tr><td>Demonstrated independently</td><td>Correct without a conceptual prompt</td></tr>
<tr><td>Not assessable</td><td>Infrastructure, accessibility, or evidence problems prevent a fair judgement</td></tr>
</tbody>
</table>
<p>Using the glossary, five-check card, accessibility tools, or ordinary interface instructions does not reduce an independent result. A conceptual prompt supplies part of the reasoning—for example, “Check whether execution failed even though the transaction was confirmed.”</p>

<h2 id=c1>Criterion 1 — Reviews and authorises the intended action</h2>
<p><b>Question.</b> Does the student understand what they are approving and notice a mismatch?</p>
<ul>
<li><b>Not yet:</b> cannot identify network/sender/recipient/amount/fee payer; approves the simulated mismatch; or says unexpected requests should be approved to continue.</li>
<li><b>With support:</b> checks correctly after prompting; rejects the mismatch after recognising it.</li>
<li><b>Independently:</b> checks network, sender, recipient, amount, fee payer; compares the wallet request; rejects the simulated mismatch without prompting.</li>
</ul>
<p><b>Critical misconception.</b> “I should approve it because the lesson told me to make a transfer.”</p>

<h2 id=c2>Criterion 2 — Verifies execution and commitment separately</h2>
<p><b>Question.</b> Does the student establish what happened rather than relying on a success message?</p>
<ul>
<li><b>Not yet:</b> treats a transaction identifier, wallet approval, or notification as proof of completion; or cannot distinguish execution from commitment.</li>
<li><b>With support:</b> finds the transaction and checks both after a conceptual prompt.</li>
<li><b>Independently:</b> locates the transaction on the intended network, matches transfer details to the intent record, checks that execution succeeded, and confirms <code>finalized</code> commitment.</li>
</ul>
<p><b>Critical misconception.</b> “Confirmed means every instruction succeeded.”</p>
<p>Finalization is the completion policy for this lesson. Students are not required to claim every Solana application must use that policy.</p>

<h2 id=c3>Criterion 3 — Reconciles the transfer and fee</h2>
<p><b>Question.</b> Can the student explain the balance changes in this controlled transaction?</p>
<ul>
<li><b>Not yet:</b> confuses transfer and fee; assigns the fee to the wrong party; or contradicts the evidence.</li>
<li><b>With support:</b> identifies transfer and fee correctly after prompting.</li>
<li><b>Independently:</b> uses transaction-specific evidence to show recipient gained the transfer amount and sender (also fee payer) lost transfer + actual fee.</li>
</ul>
<pre class=diagram>Sender decrease = Transfer amount + Transaction fee
Recipient increase = Transfer amount</pre>
<p>Assess interpretation, not mental arithmetic. Do not accept “the numbers match” without an explanation of why.</p>

<h2 id=c4>Criterion 4 — Handles uncertainty and evidence limits</h2>
<p><b>Question.</b> Does the student avoid unsafe repetition and avoid overstating what the record proves?</p>
<ul>
<li><b>Not yet:</b> immediately resends after an unresolved timeout; assumes a missing response proves failure; or claims successful execution establishes recipient identity/trustworthiness.</li>
<li><b>With support:</b> chooses to reconcile the original attempt and names a limit after prompting.</li>
<li><b>Independently:</b> inspects the existing attempt before another transfer; distinguishes “unknown” from “failed”; states at least one meaningful evidence limit.</li>
</ul>
<p><b>Critical misconception.</b> “If the page times out, the safe option is to send again immediately.”</p>

<h2 id=gates>Mandatory safety gates</h2>
<table>
<thead><tr><th>Gate</th><th>Required demonstration</th></tr></thead>
<tbody>
<tr><td>Appropriate environment</td><td>Uses designated devnet practice environment without depositing real funds</td></tr>
<tr><td>Credential boundary</td><td>Understands recovery phrase / private key must not be submitted</td></tr>
<tr><td>Mismatch response</td><td>Rejects the simulated unexpected destination</td></tr>
<tr><td>Uncertainty response</td><td>Does not initiate another transfer merely because the previous result is unresolved</td></tr>
</tbody>
</table>
<p>If a gate is not met: pause, explain without blame, provide targeted practice, reassess with a fresh scenario. Do not allow strength elsewhere to compensate.</p>

<h2 id=decisions>Completion decisions</h2>
<table>
<thead><tr><th>Decision</th><th>Requirements</th></tr></thead>
<tbody>
<tr><td>Completed independently</td><td>All four criteria independent; all safety gates; one verified successful practical transfer</td></tr>
<tr><td>Completed with support</td><td>All four at least with support; all safety gates; one verified successful practical transfer</td></tr>
<tr><td>Further practice needed</td><td>A criterion not demonstrated, or a safety gate unresolved</td></tr>
<tr><td>Assessment paused</td><td>Infrastructure/accessibility/evidence issues prevent fair completion</td></tr>
<tr><td>Observation completed</td><td>Conceptual route only; no practical mastery</td></tr>
</tbody>
</table>
<p>Never convert “assessment paused” into a failing grade. A completed transaction must not automatically award the whole lesson.</p>

<h2 id=tasks>Standard assessment tasks</h2>
<ol>
<li><b>Practical demonstration.</b> Complete a devnet transfer between designated practice wallets. Record intention before approval, then show how you established the result.</li>
<li><b>Destination mismatch.</b> Labelled simulation with a wrong recipient. Approve, reject, or clarify?</li>
<li><b>Uncertain outcome.</b> Timeout with an identifier but no established result. What next?</li>
<li><b>Evidence limits.</b> What does the record establish, and what is one thing it does not?</li>
</ol>

<h2 id=record>Assessor record template</h2>
<pre class=diagram>SOL.COLLEGE — LESSON 001 ASSESSMENT
Student identifier:
Assessment date:
Lesson version: 1.1
Assessor:
Practical transaction reference:
Network: Execution result: Commitment:
Criterion 1 — Authorisation:
Criterion 2 — Verification:
Criterion 3 — Accounting:
Criterion 4 — Uncertainty and evidence limits:
Safety gates: [ ] Environment [ ] Credentials [ ] Mismatch [ ] Uncertainty
Conceptual prompts provided:
Decision:
Feedback:
Reassessment needed:</pre>
<p>Store only what the learning record needs. Explain retention when a public transaction reference can associate a student with an address.</p>
<p class=cta><a class=btn href="{PATH}">Back to Lesson 001</a> <a class="btn ghost" href="/lessons/path/">Learning path</a></p>
'''
  rail = (
    '<nav class=rail aria-label="On this page">'
    '<a href="#levels">Levels</a><a href="#c1">Authorisation</a><a href="#c2">Verification</a>'
    '<a href="#c3">Accounting</a><a href="#c4">Uncertainty</a><a href="#gates">Safety gates</a>'
    '<a href="#decisions">Decisions</a><a href="#tasks">Tasks</a><a href="#record">Record</a></nav>'
  )
  return f'''{css}<div class=readbar aria-hidden=true><span></span></div>
<article class=lesson data-slug="{SLUG}-assessment">
<div class=lesson-layout><div class=lesson-main>
<nav class=crumbs aria-label=Breadcrumb><a href="/">Home</a> / <a href="/lessons/">Lessons</a> / <a href="{PATH}">First transaction</a> / <span>Assessment</span></nav>
<p class="eyebrow status-preview">Foundations · Lesson 001 assessment · release candidate</p>
<h1>Assessment rubric: Authorise and Verify</h1>
{body}
</div>{rail}</div>
</article>'''


def foundations_card_html():
  """Cards for lessons index: foundations gateway before Stage 1."""
  l001 = (
    f'<article class="card ready-preview" data-lesson data-slug="{SLUG}" data-diff="Beginner" data-format="foundations" '
    f'data-text="first transaction authorise verify execution commitment fee mismatch foundations">'
    f'<p class="eyebrow status-preview">Foundations · Lesson 001 · release candidate</p>'
    f'<h3><a href="{PATH}">Know what you approve. Prove what happened.</a></h3>'
    f'<p class=project>Your First Solana Transaction</p>'
    f'<p class=limit>Known limit: teaching specification only until technical and learner verification gates pass. '
    f'Execution result and commitment must be checked separately — “Confirmed” is not synonymous with success.</p>'
    f'<p class=meta><span class="chip beg">Beginner</span> · 45–60 min design estimate · Devnet only</p>'
    f'<p class=cta><a class=btn href="{PATH}">Open Lesson 001</a> · <a href="{ASSESS_PATH}">Assessment rubric</a></p>'
    f'</article>'
  )
  return l001 + l002.card_html()


def foundations_path_section():
  return (
    '<section class=path-stage id=foundations>'
    '<h2>Foundations · before Stage 1</h2>'
    '<p>Start here if you are new to Solana. '
    'Lesson 001 teaches review and verification of <b>execution and commitment as separate questions</b>. '
    'Lesson 002 teaches <b>program ownership versus application authority</b> through account investigation. '
    'Both are <b>release candidates</b>: not yet technically or learner verified, and not live dApp walkthroughs.</p>'
    f'<p><a class=btn href="{PATH}">Start Lesson 001</a> '
    f'<a class="btn ghost" href="{L002_PATH}">Lesson 002: Accounts and ownership</a> '
    f'<a class="btn ghost" href="{ASSESS_PATH}">001 rubric</a> '
    f'<a class="btn ghost" href="{l002.ASSESS_PATH}">002 rubric</a></p>'
    '</section>'
  )


def _write_one(S, page, css, path, assess_path, lesson_body, assess_body, title, assess_title, lesson_desc, assess_desc):
  assert len(lesson_desc) <= 158 and len(assess_desc) <= 158, (len(lesson_desc), len(assess_desc))
  os.makedirs(f'{S}{path}', exist_ok=True)
  os.makedirs(f'{S}{assess_path}', exist_ok=True)
  open(f'{S}{path}index.html', 'w').write(page(lesson_body, title, lesson_desc, path))
  open(f'{S}{assess_path}index.html', 'w').write(page(assess_body, assess_title, assess_desc, assess_path))
  for p, h, d in ((path, title.split(' |')[0], lesson_desc), (assess_path, assess_title.split(' |')[0], assess_desc)):
    fp = f'{S}{p}index.html'
    data = {
      '@context': 'https://schema.org', '@type': 'LearningResource',
      'headline': h, 'description': d,
      'datePublished': PUBLISHED, 'dateModified': PUBLISHED,
      'educationalLevel': 'Beginner',
      'learningResourceType': 'Lesson',
      'isAccessibleForFree': True,
      'provider': {'@type': 'Organization', 'name': 'Sol.College', 'url': SITE + '/'},
      'url': SITE + p,
    }
    t = open(fp).read()
    blob = json.dumps(data, ensure_ascii=False).replace('</', '<\\/')
    if '"@type": "LearningResource"' not in t and '"@type":"LearningResource"' not in t:
      t = t.replace('</head>', f'<script type="application/ld+json">{blob}</script></head>', 1)
      open(fp, 'w').write(t)
  return [path, assess_path]


def write(S, page, css):
  """Write foundations lesson + assessment pages. Returns paths for sitemap."""
  lesson_desc = (
    'RC foundations lesson: review a devnet SOL transfer, check execution and commitment separately, '
    'reconcile the fee. Not yet technically verified.'
  )
  assess_desc = (
    'Rubric for Lesson 001: authorisation, execution vs commitment, accounting, uncertainty. '
    'Release candidate; every criterion required.'
  )
  paths = _write_one(
    S, page, css, PATH, ASSESS_PATH,
    lesson_html(css), assessment_html(css),
    'Your First Solana Transaction | Sol.College',
    'Lesson 001 assessment rubric | Sol.College',
    lesson_desc, assess_desc,
  )
  paths += _write_one(
    S, page, css, l002.PATH, l002.ASSESS_PATH,
    l002.lesson_html(css), l002.assessment_html(css),
    'Accounts, Ownership, and Authority | Sol.College',
    'Lesson 002 assessment rubric | Sol.College',
    l002.LESSON_DESC, l002.ASSESS_DESC,
  )
  return paths
