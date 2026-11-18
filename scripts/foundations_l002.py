"""Solana Foundations Lesson 002: Accounts, Ownership, and Authority.

Release candidate. Not a live Account Inspector product and not technically or learner verified.
Teaches: program ownership vs application authority; evidence-based account reasoning.
"""
from __future__ import annotations
import html

SITE = 'https://sol.college'
PUBLISHED = '2026-11-18'
SLUG = 'accounts-ownership'
PATH = f'/lessons/{SLUG}/'
ASSESS_PATH = f'/lessons/{SLUG}/assessment/'
L001_PATH = '/lessons/first-transaction/'
E = lambda s: html.escape(str(s if s is not None else ''), quote=True)

STATUS_ROWS = [
  ('Status', 'Release candidate. Automated structural checks recorded; learner testing and live specimens not completed.'),
  ('Version', '1.0'),
  ('Track', 'Solana Foundations'),
  ('Prerequisite', 'Lesson 001 completed, or equivalent understanding'),
  ('Audience', 'People new to Solana; no programming required'),
  ('Environment', 'Read-only devnet inspection; optional prepared state update'),
  ('Core learning time', 'About 60 minutes (design estimate, not a measured claim)'),
  ('Achievement', 'Account Investigator: Identify and Explain — not awarded until verification gates pass'),
  ('Technical verification', 'Automated structural checks only; learner testing and live specimens not completed'),
  ('Learner testing', 'Not completed for this release candidate'),
]

LESSON_DESC = (
  'RC foundations lesson: inspect Solana accounts, separate program ownership from authority, '
  'reason with evidence. Not yet technically verified.'
)
ASSESS_DESC = (
  'Rubric for Lesson 002: account metadata, program vs state, ownership vs authority, '
  'permission rules. Release candidate; every criterion required.'
)


def status_panel():
  body = ''.join(f'<dt>{E(k)}</dt><dd>{E(v)}</dd>' for k, v in STATUS_ROWS)
  return (
    '<section class=status-panel aria-label="Lesson status">'
    '<h2>Lesson status</h2>'
    f'<dl class=article-meta>{body}</dl>'
    '<p><b>Publication rule.</b> This page is a teaching specification and interface design. '
    'It must not be labelled verified until every specimen inspection is reproduced against a '
    'deployed teaching program, the read-only path works without a wallet, and a new learner can '
    'explain ownership versus authority on a fresh specimen. '
    '<b>Do not treat schematic addresses or decoded panels on this RC page as live account evidence.</b></p>'
    '</section>'
  )



def _workspace():
  import foundations_lesson as foundations_meta
  return foundations_meta.foundations_workspace_html(
    'accounts-ownership',
    act_anchor='#predict',
    act_cta_label='Jump to predict and test',
  )

def lesson_html(css=''):
  docs = (
    '<p class=note>Official references: '
    '<a href="https://solana.com/docs/core/accounts/account-structure">Account structure</a>, '
    '<a href="https://solana.com/docs/core/accounts/modification-rules">Modification rules</a>, '
    '<a href="https://solana.com/docs/core/accounts/account-types">Account types</a>. '
    'The account’s <code>owner</code> field names a program; application authorities are permissions '
    'enforced by program rules and state—they are not interchangeable.</p>'
  )
  body = f'''{status_panel()}
<p class=lead>In <a href="{L001_PATH}">Lesson 001</a>, you checked where your SOL went. Now you investigate the accounts involved—and discover why “this is my wallet” and “this account’s owner is a program” can both be true.</p>
<p>You will inspect different accounts, separate <b>program ownership</b> from <b>user authority</b>, and explain what evidence you would need before saying someone controls an account.</p>
{docs}

<h2 id=safety>1. Safety boundary</h2>
<ul>
<li>No real funds are required.</li>
<li>No private key or recovery phrase should be entered into the lesson.</li>
<li>Reading public account information requires no transaction approval.</li>
<li>Any optional state-changing action must be explained separately before a wallet request appears.</li>
<li>Students may complete the core assessment through read-only investigation.</li>
</ul>

<h2 id=outcomes>2. Learning outcomes</h2>
<table>
<thead><tr><th>Outcome</th><th>Observable demonstration</th></tr></thead>
<tbody>
<tr><td>Describe an account using evidence</td><td>Identify address, owner program, executable status, lamports, and data length</td></tr>
<tr><td>Distinguish code from application state</td><td>Identify a prepared program account and a state account without relying on display names</td></tr>
<tr><td>Separate program ownership from authority</td><td>Explain the difference in a controlled application example</td></tr>
<tr><td>Reason about a proposed action</td><td>Identify the relevant program rule and required authorisation</td></tr>
<tr><td>Recognise incomplete evidence</td><td>Avoid inferring control, trustworthiness, or real-world identity from an address alone</td></tr>
</tbody>
</table>
<p>Do not assess memorisation of long addresses, raw binary layouts, or every account field. The <a href="{ASSESS_PATH}">assessment rubric</a> scores each criterion separately—no compensating total score.</p>

<h2 id=scope>3. What this lesson covers—and defers</h2>
<p><b>Included:</b> accounts as addressable on-chain records; the account <code>owner</code> field; executable versus non-executable; keypair signature versus programme-defined permission; a simple state account with a documented update authority; evidence-based classification.</p>
<p><b>Deferred to later lessons:</b> PDA derivation; cross-program invocation; token delegates and multisig; account reallocation and closing; upgrade authority in detail; Token Extensions. Do not overload the first account investigation with every exception.</p>

<h2 id=environment>4. Required learning environment (for a verified release)</h2>
<p>Build a read-only <b>Account Inspector</b> backed by actual RPC responses. This RC documents the required specimens; it does <b>not</b> yet provide verified live addresses.</p>
<table>
<thead><tr><th>Specimen</th><th>Purpose</th></tr></thead>
<tbody>
<tr><td>A. Student’s Lesson 001 sending account</td><td>Connect new concepts to familiar evidence</td></tr>
<tr><td>B. Student’s Lesson 001 recipient account</td><td>Compare another ordinary practice account</td></tr>
<tr><td>C. A deployed teaching program</td><td>Identify an executable account</td></tr>
<tr><td>D. A state account managed by that program</td><td>Distinguish stored application state from program code</td></tr>
<tr><td>E. A second state account with a different update authority</td><td>Independent comparison</td></tr>
</tbody>
</table>
<p><b>Teaching program (Profile Card).</b> Minimal reviewed example with profile state:</p>
<pre class=diagram>Profile state
update_authority: public key
display_name: bounded string
revision: integer

Documented update rule:
A display-name update requires the configured update authority to sign,
and the instruction must validate that signer against the authority stored in this profile.</pre>
<p>The program must not hold student funds or provide arbitrary withdrawal. The read-only lesson must remain usable even if the optional update transaction is unavailable.</p>
<p class=note>RC honesty: no placeholder address on this page is labelled as a live verified specimen. Instructor preparation must confirm every address exists on devnet, matches the intended owner and executable flag, and that source + tests enforce the claimed update rule—before calling the lesson verified.</p>

<h2 id=sequence>5. Lesson sequence</h2>
<table>
<thead><tr><th>Stage</th><th>Time</th><th>Student task</th></tr></thead>
<tbody>
<tr><td>Reconnect</td><td>~5 min</td><td>Revisit Lesson 001’s sender and recipient</td></tr>
<tr><td>Inspect</td><td>~10 min</td><td>Read the common account fields</td></tr>
<tr><td>Compare</td><td>~10 min</td><td>Distinguish program and state accounts</td></tr>
<tr><td>Investigate authority</td><td>~10 min</td><td>Trace the profile update rule</td></tr>
<tr><td>Predict and test</td><td>~10 min</td><td>Evaluate authorised and unauthorised updates</td></tr>
<tr><td>Independent challenge</td><td>~10 min</td><td>Analyse a fresh profile specimen</td></tr>
<tr><td>Explain and reflect</td><td>~5 min</td><td>Submit an evidence-based account explanation</td></tr>
</tbody>
</table>
<p>Times are design estimates until learner testing adjusts them.</p>

<h2 id=reconnect>6. Stage one — reconnect with Lesson 001</h2>
<p><b>Opening question (ungraded).</b> You signed a transfer from your practice wallet. Does that mean the wallet’s address must appear in its account’s <code>owner</code> field?</p>
<ul><li>Yes</li><li>No</li><li>Not sure</li></ul>
<p>Open the account used to send the Lesson 001 transfer. For an ordinary funded keypair account, the expected owner is the <b>System Program</b>—verify from the actual account response, not a fabricated screenshot.</p>
<p><b>First explanation.</b> Your signature and the account’s owner field answer different questions. The owner field identifies the program responsible for the account under runtime rules. Whether a particular instruction is authorised depends on the instruction and its permission checks.</p>
<p>Avoid the blanket statement “the owner is whoever has the private key.”</p>

<h2 id=inspect>7. Stage two — inspect the common fields</h2>
<pre class=diagram>ACCOUNT INSPECTOR (product requirement for verified release)
Network: Devnet
Address: [full, copyable address]
Observed at slot: [slot]
Fetched: [time]
Commitment: [configured commitment]
Owner program: [address and verified label]
Executable: Yes / No
Balance: [lamports] / [SOL]
Data length: [bytes]
[Raw account data] [Decoded view] [Open explorer]</pre>
<p>Concentrate on lamports, data length, owner, and executable. Solana accounts also expose rent-related metadata; those fields are out of scope for assessment here.</p>
<table>
<thead><tr><th>Field</th><th>What did you observe?</th><th>What does it tell you?</th></tr></thead>
<tbody>
<tr><td>Address</td><td></td><td>Which record was requested</td></tr>
<tr><td>Owner program</td><td></td><td>Which program owns the account</td></tr>
<tr><td>Executable</td><td></td><td>Whether it is marked executable</td></tr>
<tr><td>Lamports</td><td></td><td>The account’s SOL-denominated balance</td></tr>
<tr><td>Data length</td><td></td><td>How many bytes of account data were returned</td></tr>
</tbody>
</table>
<aside class=goals><h3>Important limits — teach explicitly</h3>
<ul>
<li>A SOL balance does not establish that an account is a person’s wallet.</li>
<li>A non-executable account is not automatically a wallet.</li>
<li>Non-empty data does not tell you its meaning without the appropriate schema.</li>
<li>A familiar explorer label is helpful context, not a replacement for raw account evidence.</li>
<li>Executable status alone is not a complete semantic classifier.</li>
</ul>
</aside>

<h2 id=compare>8. Stage three — compare code and state</h2>
<p>Open specimens C and D side by side (when the verified environment exists).</p>
<ol>
<li>Which account is executable?</li>
<li>Which account stores the profile state?</li>
<li>What program owns the profile state?</li>
<li>Is the profile account’s address the same as its owner program’s address?</li>
</ol>
<pre class=diagram>Teaching program
    owns/manages
        ↓
Profile state account

Profile state includes:
update_authority = [a separate address]</pre>
<p>Programs and mutable state are separate account roles. Do not teach that every executable account directly contains all its program bytecode: some loader arrangements place code in a separate program-data account.</p>
<p><b>Checkpoint.</b> Is the profile’s <code>update_authority</code> the same thing as the profile account’s runtime <code>owner</code>?</p>
<p><b>Expected answer.</b> No. The owner is the program. The update authority is a field interpreted and enforced by that program’s rules.</p>

<h2 id=authority>9. Stage four — trace an authority rule</h2>
<p>Show the same rule in three representations.</p>
<p><b>Plain language.</b> Only the configured update authority may change this profile’s display name through the update instruction.</p>
<pre class=diagram>Profile account: [address]
Owner program: [teaching program]
Decoded application data:
update_authority: [address A]
display_name: "Practice Profile"
revision: 1</pre>
<pre class=diagram>Rule pseudocode (explanatory — not deployed source):
require an actual signer
require signer.address == profile.update_authority
require profile belongs to the expected program
validate the proposed name
apply the update
increment revision</pre>
<p><b>Key teaching point.</b> Writing an address into a field does not, by itself, enforce permission. The program must check the relationship and the required authorisation.</p>
<p><b>Question.</b> If address B signs, but the stored update authority is address A, should this instruction accept the update?</p>
<p><b>Expected answer.</b> Not under the documented rule.</p>

<h2 id=predict>10. Stage five — predict and test</h2>
<p>Use a default read-only comparison of two reviewed execution examples. Optionally let appropriately configured students perform the authorised update themselves.</p>
<h3>Case A: authorised update</h3>
<pre class=diagram>Stored update authority: A
Actual signer: A
Requested action: Change display name</pre>
<p>Student predicts: Accept / Reject / Insufficient information. Then inspect authorisation evidence, execution result, state before and after, and revision change.</p>
<h3>Case B: unauthorised update</h3>
<pre class=diagram>Stored update authority: A
Actual signer: B
Requested action: Change display name</pre>
<p>Inspect a controlled test showing the documented rule rejecting the update. Evidence must identify whether this was a local automated test, a simulation, or a submitted devnet transaction. Do not present them as equivalent.</p>
<p><b>Student explanation.</b> “The second update was rejected because ______. The evidence that the profile did not change is ______.”</p>
<p>Do not require beginners to generate failed fee-charging transactions for assessment.</p>

<h2 id=optional>11. Optional live update</h2>
<p>Offer only when the student controls the fixture’s configured update authority.</p>
<pre class=diagram>You are about to update a practice profile.
Network: Devnet
Program: [address]
Profile account: [address]
Current name: [value]
New name: [value]
Expected:
• Display name changes
• Revision increases
• Fee payer pays the transaction fee
• No intended SOL transfer to another user
[Review wallet request]</pre>
<p>Apply Lesson 001’s review and verification workflow. A wallet request must not appear merely because the student opened the inspector.</p>

<h2 id=challenge>12. Independent investigation</h2>
<p>Open specimen E, a previously unseen profile. Provide raw fields, correctly identified schema, decoded state, update-rule description, and two proposed actions.</p>
<pre class=diagram>ACCOUNT INVESTIGATION
1. Account address:
2. Owner program:
3. Executable:
4. Application state or program account? Why?
5. Stored update authority:
6. Who must authorise the documented update?
7. Which proposed action should pass the rule?
8. What evidence supports your answer?
9. What cannot be established from this record alone?</pre>
<p>Example proposed actions: (1) the configured authority signs a permitted name update; (2) an unrelated address signs the same update. Explain the permission relationship—do not merely match addresses visually.</p>

<h2 id=misconceptions>13. Two misconception checks</h2>
<p><b>Check A — misleading label.</b> An explorer labels an address “Treasury.” Is that enough to establish who can withdraw its funds?</p>
<p><b>Expected.</b> No. Inspect the account type and relevant program rules or authorities. The label alone is insufficient.</p>
<p><b>Check B — misleading field name.</b> A decoded field is named <code>owner</code>. Does that necessarily mean it is the account’s runtime owner program?</p>
<p><b>Expected.</b> No. It may be application-defined data. Distinguish the raw account owner field from fields inside the account’s data.</p>

<h2 id=assessment>14. Assessment overview</h2>
<p>Same levels as Lesson 001: not yet / with support / independently / not assessable. Five criteria: account inspection; account-role distinction; ownership versus authority; permission reasoning; evidence limits.</p>
<p><b>Completion.</b> All five criteria at least with support. “Completed independently” only when all five are independent. No live state change is required. See the <a href="{ASSESS_PATH}">full rubric</a>.</p>
<p><b>Critical misconceptions requiring reassessment:</b></p>
<ul>
<li>“An account’s owner field always identifies the person holding its private key.”</li>
<li>“Any signer can edit any account.”</li>
<li>“A field named authority enforces permission automatically.”</li>
<li>“Executable means trustworthy.”</li>
<li>“An address label proves real-world identity.”</li>
</ul>

<h2 id=recovery>15. Recovery and accessibility</h2>
<table>
<thead><tr><th>Problem</th><th>Required response</th></tr></thead>
<tbody>
<tr><td>RPC unavailable</td><td>Preserve progress; labelled captured snapshot or resume later</td></tr>
<tr><td>Address not found</td><td>Show “No account returned on this network,” not “Empty wallet”</td></tr>
<tr><td>Decoder unavailable</td><td>Display raw metadata; do not invent decoded values</td></tr>
<tr><td>Unexpected owner or data format</td><td>Stop decoding and flag the mismatch</td></tr>
<tr><td>Snapshot differs from current data</td><td>Show provenance and observation times</td></tr>
<tr><td>Wallet unavailable</td><td>Continue the read-only route</td></tr>
<tr><td>Visual diagram inaccessible</td><td>Provide equivalent structured text</td></tr>
<tr><td>Optional update fails</td><td>Preserve evidence; assess reasoning separately</td></tr>
</tbody>
</table>
<p>A saved snapshot can support conceptual assessment, but must not be represented as a live observation.</p>

<h2 id=gates>16. Release gate</h2>
<ul>
<li>Technically reproduce every account inspection and prepared test.</li>
<li>Confirm source, schema, deployment, and specimens match.</li>
<li>Verify the read-only path without wallet connection.</li>
<li>Observe new learners completing the comparison task.</li>
<li>Check that students can explain the distinction on a fresh specimen.</li>
<li>Review accessibility.</li>
<li>Publish verification date, responsible reviewer, and limitations.</li>
</ul>
<p><b>Central question.</b> Who can change what—and what evidence supports that answer?</p>

<h2 id=next>17. Next</h2>
<p>Next foundations step: <a href="/lessons/instructions-programs/">Lesson 003 — Instructions and Programs</a> (release candidate). Until foundations are verified, the first live Stage 1 practice remains <a href="/lessons/picassol-hackathon/">Picassol</a>, which assumes you can reason about accounts and authority.</p>
<p class=cta>
<a class=btn href="{ASSESS_PATH}">Open the assessment rubric</a>
<a class="btn ghost" href="/lessons/instructions-programs/">Next: Lesson 003</a>
<a class="btn ghost" href="{L001_PATH}">Previous: Lesson 001</a>
</p>
'''
  rail = (
    '<nav class=rail aria-label="On this page">'
    '<a href="#workspace">Workspace</a>'
    '<a href="#safety">Safety</a><a href="#outcomes">Outcomes</a><a href="#scope">Scope</a>'
    '<a href="#environment">Environment</a><a href="#sequence">Sequence</a><a href="#reconnect">Reconnect</a>'
    '<a href="#inspect">Inspect</a><a href="#compare">Compare</a><a href="#authority">Authority</a>'
    '<a href="#predict">Predict</a><a href="#optional">Optional update</a><a href="#challenge">Challenge</a>'
    '<a href="#misconceptions">Checks</a><a href="#assessment">Assessment</a><a href="#recovery">Recovery</a>'
    '<a href="#gates">Release gates</a><a href="#next">Next</a></nav>'
  )
  return f'''{css}<div class=readbar aria-hidden=true><span></span></div>
<article class=lesson data-slug="{SLUG}">
<div class=lesson-layout><div class=lesson-main>
<nav class=crumbs aria-label=Breadcrumb><a href="/">Home</a> / <a href="/lessons/">Lessons</a> / <a href="/lessons/path/">Path</a> / <span>Accounts and ownership</span></nav>
<p class="eyebrow status-preview">Foundations · Lesson 002 · release candidate</p>
<h1>Accounts, Ownership, and Authority</h1>
<p class=lead>An address tells you where. The rules tell you who can act.</p>
{_workspace()}
{body}
</div>{rail}</div>
<div class=dock role=region aria-label="Lesson actions">
<a class=btn href="{ASSESS_PATH}">Assessment rubric</a>
<a class="btn ghost" href="/lessons/instructions-programs/">Next: Lesson 003</a>
<button type=button class="btn ghost" data-jump>Next section</button>
</div>
</article>'''


def assessment_html(css=''):
  assert len(LESSON_DESC) <= 158 and len(ASSESS_DESC) <= 158, (len(LESSON_DESC), len(ASSESS_DESC))
  body = f'''{status_panel()}
<p class=lead>Determine whether a student can inspect a Solana account, distinguish program ownership from application-defined authority, and use evidence to explain who may perform a particular action.</p>
<p>This rubric assesses <a href="{PATH}">Lesson 002</a>’s prepared teaching examples. It does not certify ability to audit arbitrary programs, assess wallet custody, or establish that an application is secure. No practical transaction is required.</p>

<h2 id=levels>Performance levels</h2>
<table>
<thead><tr><th>Level</th><th>Meaning</th></tr></thead>
<tbody>
<tr><td>Not yet demonstrated</td><td>Evidence missing, materially incorrect, or unresolved misconception</td></tr>
<tr><td>Demonstrated with support</td><td>Correct after a conceptual prompt</td></tr>
<tr><td>Demonstrated independently</td><td>Correct without a conceptual prompt</td></tr>
<tr><td>Not assessable</td><td>Technical, accessibility, or evidence problems prevent fair judgement</td></tr>
</tbody>
</table>
<p>Glossary, field reference card, supplied schema and update-rule description, accessibility tools, notes, and ordinary navigation help do not reduce an independent result. A conceptual prompt supplies part of the reasoning—for example, “Separate the account’s raw owner field from the authority stored inside its data.”</p>

<h2 id=materials>Assessment materials</h2>
<p>Provide a fresh specimen set that was not the lesson’s worked example: teaching program (P), profile state (S), authority scenarios, and an evidence-limit scenario. Supply the profile schema and documented update rule. Do not require undocumented binary schema discovery.</p>

<h2 id=c1>Criterion 1 — Reads account metadata accurately</h2>
<p><b>Question.</b> Can the student distinguish observed account facts from interpretations?</p>
<ul>
<li><b>Not yet:</b> misidentifies essential fields; confuses address with owner program; treats unavailable information as zero/empty.</li>
<li><b>With support:</b> correctly identifies required fields after a prompt or correction.</li>
<li><b>Independently:</b> correctly identifies address, owner program, executable status, lamports, and data length; distinguishes missing information from observed values.</li>
</ul>
<p>Do not assess address memorisation. Copying values is acceptable. A loading failure is not scored as inability to inspect.</p>

<h2 id=c2>Criterion 2 — Distinguishes program and state accounts</h2>
<p><b>Question.</b> Can the student classify the supplied examples using evidence rather than names?</p>
<ul>
<li><b>Not yet:</b> classifies solely by labels; assumes every non-executable account is a wallet; cannot distinguish prepared program from profile state.</li>
<li><b>With support:</b> correctly identifies both after prompting with a supporting fact.</li>
<li><b>Independently:</b> uses executable status, owner information, supplied schema, and documented relationship.</li>
</ul>
<p>Do not accept “Non-executable means it is a profile.” Do not require loader-internals explanations.</p>

<h2 id=c3>Criterion 3 — Separates program ownership from application authority</h2>
<p><b>Question.</b> Can the student explain the two different permission concepts?</p>
<ul>
<li><b>Not yet:</b> says runtime owner is necessarily the private-key holder; treats <code>update_authority</code> as the raw owner; assumes an authority field enforces itself.</li>
<li><b>With support:</b> separates owner program and stored update authority after a conceptual prompt.</li>
<li><b>Independently:</b> identifies different roles and explains that the program’s update rule must validate authorisation.</li>
</ul>
<p><b>Critical misconception.</b> “Putting my address in the authority field automatically prevents other people from changing the data.”</p>

<h2 id=c4>Criterion 4 — Reasons correctly about an update request</h2>
<p>Assume stored update authority is address A; other stated checks pass.</p>
<table>
<thead><tr><th>Scenario</th><th>Proposed request</th></tr></thead>
<tbody>
<tr><td>A</td><td>Address A actually signs a permitted display-name update</td></tr>
<tr><td>B</td><td>Address B actually signs the same update</td></tr>
<tr><td>C</td><td>Request includes address A, but A has not signed</td></tr>
</tbody>
</table>
<ul>
<li><b>Not yet:</b> accepts unrelated signer; treats including an address as obtaining its signature; predicts without the rule.</li>
<li><b>With support:</b> resolves all scenarios after prompting about signer status or authority match.</li>
<li><b>Independently:</b> A satisfies the stated check; B and C do not—based on actual signer status and address matching.</li>
</ul>
<p>Prefer “Scenario A should pass the stated authority check” over “Scenario A is guaranteed to succeed on the network.”</p>

<h2 id=c5>Criterion 5 — Recognises the limits of the evidence</h2>
<p><b>Question.</b> Does the student avoid claiming more than the account record establishes?</p>
<ul>
<li><b>Not yet:</b> treats a label as identity proof; assumes executable means trustworthy; interprets arbitrary decoded <code>owner</code> as runtime owner; presents a snapshot as current live observation.</li>
<li><b>With support:</b> identifies relevant limits after prompting.</li>
<li><b>Independently:</b> names at least two meaningful limits (account interpretation + provenance/identity/trustworthiness).</li>
</ul>

<h2 id=checks>Mandatory conceptual checks</h2>
<table>
<thead><tr><th>Check</th><th>Required understanding</th></tr></thead>
<tbody>
<tr><td>Address versus owner</td><td>Account address and owner-program address are different fields</td></tr>
<tr><td>Owner versus authority</td><td>Runtime owner is not interchangeable with application-defined authority</td></tr>
<tr><td>Rule enforcement</td><td>A stored authority value does not enforce permission by itself</td></tr>
<tr><td>Signer versus included address</td><td>Listing an address ≠ its holder authorising the action</td></tr>
<tr><td>Evidence limits</td><td>Labels, executable status, and decoded fields do not establish safety or identity alone</td></tr>
</tbody>
</table>
<p>Unresolved foundational misconceptions require pause, targeted practice, and fresh reassessment. Strength elsewhere must not compensate.</p>

<h2 id=decisions>Completion decisions</h2>
<table>
<thead><tr><th>Decision</th><th>Requirements</th></tr></thead>
<tbody>
<tr><td>Completed independently</td><td>All five criteria independent; all conceptual checks satisfied</td></tr>
<tr><td>Completed with support</td><td>All five at least with support; all conceptual checks satisfied</td></tr>
<tr><td>Further practice needed</td><td>One or more criteria not yet demonstrated</td></tr>
<tr><td>Assessment paused</td><td>Evidence, accessibility, or infrastructure prevents fair judgement</td></tr>
</tbody>
</table>
<p>Captured-evidence route is valid when labelled honestly: “Assessment completed using captured evidence.” Do not describe it as independent live inspection. No fee expenditure or real-money deposit is required.</p>

<h2 id=tasks>Standard assessment sequence</h2>
<ol>
<li><b>Inspect.</b> Record essential fields for specimens P and S; source and observation time.</li>
<li><b>Classify.</b> Which is the prepared program? Which stores profile state? Evidence?</li>
<li><b>Explain control.</b> Identify owner program and update authority; different roles.</li>
<li><b>Apply the rule.</b> Evaluate scenarios A–C; which part of the rule each satisfies or fails.</li>
<li><b>Bound the conclusion.</b> Two conclusions you cannot justify from these records alone.</li>
</ol>

<h2 id=record>Assessor record template</h2>
<pre class=diagram>SOL.COLLEGE — LESSON 002 ASSESSMENT
Student identifier:
Assessment date:
Lesson version: 1.0
Rubric version: 1.0 — proposed; requires assessor calibration
Assessor:
Evidence route: [ ] Live inspection  [ ] Verified captured evidence
Network: Specimen identifiers: Source / observation time:
Criterion 1 — Account metadata:
Criterion 2 — Program and state distinction:
Criterion 3 — Ownership and authority:
Criterion 4 — Permission reasoning:
Criterion 5 — Evidence limits:
Conceptual checks:
[ ] Address versus owner
[ ] Owner versus authority
[ ] Rule enforcement
[ ] Signer versus included address
[ ] Evidence limits
Conceptual prompts provided:
Decision:
Feedback:
Reassessment required:</pre>
<p class=cta><a class=btn href="{PATH}">Back to Lesson 002</a> <a class="btn ghost" href="{L001_PATH}">Lesson 001</a> <a class="btn ghost" href="/lessons/path/">Learning path</a></p>
'''
  rail = (
    '<nav class=rail aria-label="On this page">'
    '<a href="#levels">Levels</a><a href="#materials">Materials</a><a href="#c1">Metadata</a>'
    '<a href="#c2">Program/state</a><a href="#c3">Ownership</a><a href="#c4">Permission</a>'
    '<a href="#c5">Evidence limits</a><a href="#checks">Conceptual checks</a>'
    '<a href="#decisions">Decisions</a><a href="#tasks">Tasks</a><a href="#record">Record</a></nav>'
  )
  return f'''{css}<div class=readbar aria-hidden=true><span></span></div>
<article class=lesson data-slug="{SLUG}-assessment">
<div class=lesson-layout><div class=lesson-main>
<nav class=crumbs aria-label=Breadcrumb><a href="/">Home</a> / <a href="/lessons/">Lessons</a> / <a href="{PATH}">Accounts and ownership</a> / <span>Assessment</span></nav>
<p class="eyebrow status-preview">Foundations · Lesson 002 assessment · release candidate</p>
<h1>Assessment rubric: Account Investigator</h1>
{body}
</div>{rail}</div>
</article>'''


def card_html():
  return (
    f'<article class="card ready-preview" data-lesson data-slug="{SLUG}" data-diff="Beginner" data-format="foundations" '
    f'data-text="accounts ownership authority program state update inspector foundations">'
    f'<p class="eyebrow status-preview">Foundations · Lesson 002 · release candidate</p>'
    f'<h3><a href="{PATH}">An address tells you where. The rules tell you who can act.</a></h3>'
    f'<p class=project>Accounts, Ownership, and Authority</p>'
    f'<p class=limit>Known limit: teaching specification only until the Profile Card program and specimens are '
    f'deployed and verified. Program ownership and application authority must stay separate concepts.</p>'
    f'<p class=meta><span class="chip beg">Beginner</span> · ~60 min design estimate · Read-only first</p>'
    f'<p class=cta><a class=btn href="{PATH}">Open Lesson 002</a> · <a href="{ASSESS_PATH}">Assessment rubric</a></p>'
    f'</article>'
  )
