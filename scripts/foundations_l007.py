"""Solana Foundations Lesson 007: Protecting State Transitions.

Release candidate. Not a shipped Profile Card product and not technically or learner verified.
Teaches: expected-revision guards; program-enforced preconditions; conflict without silent overwrite.
"""
from __future__ import annotations
import html

SITE = 'https://sol.college'
PUBLISHED = '2026-11-18'
SLUG = 'protecting-state-transitions'
PATH = f'/lessons/{SLUG}/'
ASSESS_PATH = f'/lessons/{SLUG}/assessment/'
L006_PATH = '/lessons/application-state/'
L005_PATH = '/lessons/transaction-failures/'
E = lambda s: html.escape(str(s if s is not None else ''), quote=True)

STATUS_ROWS = [
  ('Status', 'Release candidate. Automated structural checks recorded; learner testing and live specimens not completed.'),
  ('Version', '1.0'),
  ('Track', 'Solana Foundations'),
  ('Prerequisites', 'Lessons 001–006, or equivalent understanding'),
  ('Audience', 'People new to Solana; basic TypeScript; guided Rust reading provided'),
  ('Environment', 'Local test environment first; optional devnet verification'),
  ('Core learning time', 'About 75–90 minutes (design estimate, not a measured claim)'),
  ('Achievement', 'State Guardian: Enforce Before Updating — not awarded until verification gates pass'),
  ('Technical verification', 'Automated structural checks only; learner testing and live specimens not completed'),
  ('Learner testing', 'Not completed for this release candidate'),
]

LESSON_DESC = (
  'RC foundations lesson: enforce expected revisions in-program; handle stale updates without silent overwrite. '
  'Not yet technically verified.'
)
ASSESS_DESC = (
  'Rubric for Lesson 007: stale-write race, guarded transition, tests, conflict recovery. '
  'Release candidate; every criterion required.'
)


def status_panel():
  body = ''.join(f'<dt>{E(k)}</dt><dd>{E(v)}</dd>' for k, v in STATUS_ROWS)
  return (
    '<section class=status-panel aria-label="Lesson status">'
    '<h2>Lesson status</h2>'
    f'<dl class=article-meta>{body}</dl>'
    '<p><b>Publication rule.</b> This page is a teaching specification and interface design. '
    'It must not be labelled verified until the guarded handler builds from a clean checkout, '
    'isolated negative tests assert unchanged state, the two-client experiment is reproducible, '
    'and learners (implementation and guided routes) complete conflict recovery without silent resubmit. '
    '<b>Handler snippets are explanatory pseudocode—not literal SDK function names. '
    'Do not claim a production concurrency product ships with this RC. '
    'Do not advertise a universal guarantee while an unguarded update path remains available.</b></p>'
    '</section>'
  )



def _workspace():
  import foundations_lesson as foundations_meta
  return foundations_meta.foundations_workspace_html(
    'protecting-state-transitions',
    act_anchor='#predict',
    act_cta_label='Jump to predict the guarded outcome',
  )

def lesson_html(css=''):
  docs = (
    '<p class=note>Official references: '
    '<a href="https://www.anchor-lang.com/docs/references/account-constraints">Anchor account constraints</a>, '
    '<a href="https://www.anchor-lang.com/docs/references/account-types">Anchor account types</a>, '
    '<a href="https://www.anchor-lang.com/docs/basics/program-structure">Program structure</a>. '
    'A client-side warning helps the user decide. '
    '<b>A program-enforced precondition</b> decides whether the transition is permitted when the instruction executes. '
    'They are not substitutes for one another.</p>'
  )
  body = f'''{status_panel()}
<p class=lead>In Lesson 006, your client noticed when a profile changed while you were editing. But another update can still happen after your last read and before your transaction executes.</p>
<p>Now you move an important condition into the program: “Only apply this update if the profile is still at the revision I reviewed.” Build and test that condition, then teach the client to handle a rejected stale update without silently overwriting someone else’s work.</p>
{docs}

<h2 id=outcomes>1. Learning outcomes</h2>
<table>
<thead><tr><th>Outcome</th><th>Observable demonstration</th></tr></thead>
<tbody>
<tr><td>Explain a stale-write race</td><td>Show how a profile can change after a client’s last read</td></tr>
<tr><td>Specify a transition invariant</td><td>State the conditions required for a permitted update</td></tr>
<tr><td>Enforce an expected revision</td><td>Reject a request whose expected revision differs from current state</td></tr>
<tr><td>Preserve authorisation</td><td>Keep signer and authority checks separate from the revision check</td></tr>
<tr><td>Test competing edits</td><td>Show that two requests based on the same revision cannot both apply through the guarded path</td></tr>
<tr><td>Handle conflict deliberately</td><td>Refresh, preserve the draft, and require renewed review rather than automatically overwriting</td></tr>
</tbody>
</table>
<p>The <a href="{ASSESS_PATH}">assessment rubric</a> scores six criteria separately. Record program-implementation vs guided-investigation route accurately. Passing the conceptual route must not be recorded as independently authored Rust code.</p>

<h2 id=scope>2. Scope and safety</h2>
<p><b>Included:</b> expected-revision updates; program-side validation; checked revision increments; negative tests; two-client conflict experiments; client recovery after a stale-revision error; limits of the guarantee.</p>
<p><b>Deferred:</b> distributed locks; multi-account concurrency schemes; automatic field merging; general-purpose operation identifiers; production upgrade governance; strong guarantees across arbitrary programs or alternative mutation paths.</p>
<ul>
<li>Local fixtures and devnet practice accounts only. Do not modify an unrelated production program.</li>
<li>No real funds required. No private keys or recovery phrases submitted to Sol.College.</li>
<li>Do not disable authority checks to make a test pass.</li>
<li>Students need not deploy their own program to complete the conceptual route.</li>
</ul>

<h2 id=problem>3. Start with the problem</h2>
<p>Existing profile: <code>update_authority</code>, <code>display_name</code>, <code>revision</code>. Existing instruction: <code>update_profile(new_name)</code>.</p>
<pre class=diagram>Profile begins: name = "Atlas", revision = 12

Tab A reads revision 12.
Tab B reads revision 12.

Tab B updates the name to "Beacon" → revision 13.
Tab A submits its older draft: "Harbour".</pre>
<p>With only the earlier update rule, Tab A may still be authorised. The program has not been instructed to reject edits based on an older revision.</p>
<p><b>Opening question.</b> Did Tab A lack permission—or did it act on an outdated assumption?</p>
<p><b>Expected answer.</b> It may have had permission. The missing condition concerns the state on which its decision was based. Authorisation and freshness are different checks.</p>

<h2 id=guard>4. Specify the protected operation</h2>
<pre class=diagram>update_profile_checked(
    new_name,
    expected_revision
)</pre>
<p>The instruction must verify: (1) expected profile account and schema; (2) required signer; (3) signer matches stored update authority; (4) proposed name is valid; (5) stored revision equals expected revision; (6) a safe next revision. Only then apply the name change and revision increment.</p>
<p>Anchor account-validation mechanisms for signer requirements and stored authority relationships should remain explicit alongside the new state precondition.</p>
<pre class=diagram>If authorised
and input is valid
and current_revision == expected_revision
and the revision can be incremented safely:

    apply the name
    increment the revision once

Otherwise:

    do not apply the profile update</pre>
<p>A failed executed transaction can still charge a fee; “no profile update” must not be presented as “no possible cost.”</p>

<h2 id=guarantee>5. Define the guarantee before writing code</h2>
<p>For a single profile, with every relevant update routed through this guarded rule:</p>
<blockquote>After one request advances revision R to R+1, another request still expecting R must be rejected.</blockquote>
<p><b>Required assumptions:</b> revision increases monotonically; does not wrap around; is not reset or reused; other mutation paths do not bypass the policy; the profile is the intended account; validation is correctly implemented.</p>
<p>Do not advertise a universal guarantee based on one guarded function while leaving an unrestricted update path available.</p>
<p><b>Teaching-environment requirement.</b> Use a separate lab deployment or disable the old unguarded update path for the guarded exercise. Keep Lessons 002–006 available against their documented versions rather than silently changing their semantics.</p>

<h2 id=sequence>6. Lesson sequence</h2>
<table>
<thead><tr><th>Stage</th><th>Approx.</th><th>Student task</th></tr></thead>
<tbody>
<tr><td>Investigate the race</td><td>10 min</td><td>Trace two edits based on the same revision</td></tr>
<tr><td>Write the invariant</td><td>10 min</td><td>Separate authorisation, input validity, and expected state</td></tr>
<tr><td>Implement the guard</td><td>15 min</td><td>Add expected-revision validation and safe increment</td></tr>
<tr><td>Test the program</td><td>20 min</td><td>Verify success, rejection, and unchanged state</td></tr>
<tr><td>Update the client</td><td>10 min</td><td>Send the reviewed revision and handle conflict</td></tr>
<tr><td>Two-client experiment</td><td>10 min</td><td>Observe one update succeed and the stale one fail</td></tr>
<tr><td>Explain the limits</td><td>5 min</td><td>Identify bypasses and non-guarantees</td></tr>
</tbody>
</table>

<h2 id=predict>7. Stage one: predict the guarded outcome</h2>
<pre class=diagram>Starting: name "Atlas", revision 12

Tab B: new_name = "Beacon", expected_revision = 12
Tab A: new_name = "Harbour", expected_revision = 12

Assume Tab B executes successfully first.</pre>
<p>After Tab B: name “Beacon”, revision 13. Tab A expects 12 but encounters 13 → guarded update rejected. The program does not decide that “Beacon” is the better name; it enforces the condition attached to the request.</p>

<h2 id=implement>8. Stage two: implement the guarded transition</h2>
<p>Provide a tested starter program and version-pinned development environment. Students complete a small handler or equivalent guided exercise.</p>
<pre class=diagram>Explanatory pseudocode (not literal SDK functions):

validate_profile_account()
require_actual_authority_signature()
require_authority_matches_profile()

validate_name(new_name)

require(
    profile.revision == expected_revision,
    StaleRevision
)

next_revision = checked_increment(profile.revision)
require_increment_succeeded(next_revision)

profile.display_name = new_name
profile.revision = next_revision</pre>
<ul>
<li>Use the framework’s established account and signer types; explicit errors; validate before assigning.</li>
<li>Use checked arithmetic for the revision; preserve the update authority.</li>
<li>Avoid account reallocation in this exercise.</li>
<li>Do not duplicate checks inconsistently between client and program.</li>
</ul>
<p><b>Student question.</b> Does knowing the current revision give an unrelated person permission to edit the profile?</p>
<p><b>Expected answer.</b> No. The revision check does not replace signer and authority validation.</p>

<h2 id=tests>9. Stage three: test the contract</h2>
<p>Use isolated fixtures. Each test establishes its own starting state.</p>
<table>
<thead><tr><th>Test</th><th>Setup</th><th>Expected result</th></tr></thead>
<tbody>
<tr><td>Correct update</td><td>Correct authority, valid name, matching revision</td><td>Name changes; revision increases once</td></tr>
<tr><td>Stale revision</td><td>Current 13; request expects 12</td><td>Rejected; profile unchanged</td></tr>
<tr><td>Future revision</td><td>Current 13; request expects 14</td><td>Rejected; profile unchanged</td></tr>
<tr><td>Wrong authority</td><td>Unrelated signer; matching revision</td><td>Rejected; profile unchanged</td></tr>
<tr><td>Invalid name</td><td>Correct signer and revision; invalid name</td><td>Rejected; profile unchanged</td></tr>
<tr><td>Missing signature</td><td>Authority address without required authorisation</td><td>Rejected; profile unchanged</td></tr>
<tr><td>Revision overflow</td><td>Revision at integer maximum</td><td>Rejected; no wraparound or update</td></tr>
<tr><td>Repeated stale request</td><td>Success then new request with old expected revision</td><td>Second update rejected</td></tr>
<tr><td>Authority preservation</td><td>Successful update</td><td>Authority remains unchanged</td></tr>
</tbody>
</table>
<p><b>Evidence.</b> For rejected updates, compare all relevant profile fields before and after. Checking only that the client displayed an error is insufficient.</p>
<p><b>Precision.</b> For the stale-revision test, keep the signer and name valid. For an authority test, use a matching revision so it genuinely tests authority validation.</p>

<h2 id=client>10. Stage four: connect the guard to the client</h2>
<pre class=diagram>Draft:
new_name = "Harbour"
based_on_revision = 12

Instruction arguments:
new_name = "Harbour"
expected_revision = 12</pre>
<p><b>Do not silently “fix” a conflict:</b> StaleRevision → fetch revision 13 → automatically resubmit old draft expecting 13. That can overwrite the intervening edit without renewed review.</p>
<pre class=diagram>THIS PROFILE CHANGED BEFORE YOUR UPDATE COULD APPLY

Your draft was based on revision 12.
The update was rejected because the profile had changed.

Latest observed profile:
Name: Beacon
Revision: 13

Your draft:
Harbour

[Discard draft]
[Review draft against latest state]</pre>
<p>After review, the student may deliberately prepare a new update based on the newer observation. A fresh request requires the normal approval and verification workflow.</p>
<p><b>Error-handling precision.</b> Only display a definitive stale-revision rejection when the evidence establishes it. If submission timed out and execution remains unresolved, use Lesson 005’s reconciliation workflow—not the conflict screen.</p>

<h2 id=experiment>11. Stage five: controlled two-client experiment</h2>
<ol>
<li>Both clients read the same profile at revision R.</li>
<li>Each prepares a different draft expecting R.</li>
<li>Client B submits; verify successful execution and required commitment.</li>
<li>Client A submits its stale request; inspect rejection.</li>
<li>Read the resulting profile; confirm B’s state remains and revision is R+1.</li>
</ol>
<p>Sequential submission makes the experiment reproducible. It still shows that an intervening update invalidates the older precondition.</p>
<p><b>Optional concurrency extension.</b> Submit two distinct requests expecting R without choosing the winner in advance. Under the exercise’s assumptions, at most one may apply through the guarded path. Neither is guaranteed to succeed if other conditions fail. Do not claim “Both cannot be processed at the same time, so a revision guard is unnecessary.” Execution ordering does not make a stale user intention current.</p>

<h2 id=challenge>12. Independent challenge</h2>
<pre class=diagram>Current profile: name = "Cedar", revision = 20, authority = A

A: A signs; valid name; expects 20
B: A signs; valid name; expects 19
C: B signs; valid name; expects 20
D: A signs; invalid name; expects 20
E: After A’s successful update, a new request still expects 20
F: Client refreshes after a conflict and silently resubmits the old draft using the latest revision</pre>
<p>Explain which checks pass or fail; whether the profile should change; what the client should display; what evidence supports the conclusion; why case F is poor conflict handling even if the program accepts the new request.</p>
<p><b>Instructor summary:</b> A may succeed if all stated conditions hold; B fails revision; C fails authority; D fails input validation; E is stale after earlier success; F bypasses meaningful user review—revision matching is not equivalent to informed intent.</p>

<h2 id=limits>13. Limits of expected revisions</h2>
<p>This pattern does <b>not</b> establish: real-world identity; trustworthiness of the authority; correctness of the new content; fair ordering between competing requests; a universal exactly-once business-operation guarantee; protection against mutation paths that ignore the revision policy; freedom from all stale-read or observation problems.</p>
<p>It is a bounded safeguard: apply this change only if this account is still at the expected revision when the guarded instruction executes.</p>
<p>Also distinguish a newly constructed request from rebroadcasting the same signed transaction. Do not call every repeated action a “replay” without explaining what was repeated.</p>

<h2 id=assessment>14. Assessment overview</h2>
<p>Six criteria: race explanation; invariant specification; program enforcement; test quality; client recovery; guarantee boundaries. All six at least with support. See the <a href="{ASSESS_PATH}">full rubric</a>.</p>
<p><b>Critical misconceptions:</b> a fresh client read eliminates all races; matching the revision replaces authority validation; a stale request should be automatically retried with the newest revision; a revision number guarantees exactly-once execution for every business operation; the guard protects updates that use an unguarded alternative; rejecting the stale update means the winning content is correct.</p>

<h2 id=recovery>15. Recovery and accessibility</h2>
<table>
<thead><tr><th>Situation</th><th>Required response</th></tr></thead>
<tbody>
<tr><td>Toolchain unavailable</td><td>Guided route or local test evidence</td></tr>
<tr><td>Wrong program version</td><td>Stop and identify the mismatch</td></tr>
<tr><td>Profile changes unexpectedly</td><td>Re-establish the fixture; preserve evidence</td></tr>
<tr><td>Expected error differs</td><td>Diagnose the actual failing check before claiming a pass</td></tr>
<tr><td>Conflict read fails</td><td>Preserve draft and show unresolved refresh</td></tr>
<tr><td>Submission outcome unknown</td><td>Reconcile before replacement</td></tr>
<tr><td>Student rejects request</td><td>Return to review without penalty</td></tr>
<tr><td>Learner new to Rust</td><td>Annotated handler walkthroughs and a bounded exercise</td></tr>
</tbody>
</table>
<p>Keep error messages plain, specific, and accessible. Never rely on colour alone to communicate a conflict.</p>

<h2 id=gates>16. Release gate</h2>
<ul>
<li>Reproduce the guarded handler from a clean checkout; confirm instruction interface and generated client agree.</li>
<li>Verify authority, schema, input, revision, and overflow checks.</li>
<li>Audit every relevant mutation path in the lab deployment; confirm the old unguarded path does not undermine the exercise.</li>
<li>Reproduce the two-client experiment; test conflict versus unresolved-submission messaging.</li>
<li>Confirm no automatic revision-refresh-and-resubmit behaviour; review accessibility.</li>
<li>Observe learners explaining the guarantee on a fresh scenario; publish verification date, reviewer, versions, and limitations.</li>
</ul>
<p><b>Understanding to leave with.</b> My client can warn about a changed profile, but the program must enforce any condition that needs to hold at execution. An expected revision prevents a stale update from applying through the guarded path. If it is rejected, I refresh and review—not silently overwrite.</p>

<h2 id=next>17. Next</h2>
<p>Foundations 001–007 end here for the current release candidate. The first live Stage 1 practice is <a href="/lessons/picassol-hackathon/">Picassol</a> — paint an on-chain pixel and meet PDAs in an application lab. A future foundations lesson on Program-Derived Addresses may be added later; it does not block Stage 1.</p>
<p class=cta>
<a class=btn href="{ASSESS_PATH}">Open the assessment rubric</a>
<a class="btn ghost" href="{L006_PATH}">Previous: Lesson 006</a>
<a class="btn ghost" href="/lessons/path/">Learning path</a>
</p>
'''
  rail = (
    '<nav class=rail aria-label="On this page">'
    '<a href="#workspace">Workspace</a>'
    '<a href="#outcomes">Outcomes</a><a href="#scope">Scope</a><a href="#problem">Problem</a>'
    '<a href="#guard">Guard</a><a href="#guarantee">Guarantee</a><a href="#sequence">Sequence</a>'
    '<a href="#predict">Predict</a><a href="#implement">Implement</a><a href="#tests">Tests</a>'
    '<a href="#client">Client</a><a href="#experiment">Experiment</a><a href="#challenge">Challenge</a>'
    '<a href="#limits">Limits</a><a href="#assessment">Assessment</a><a href="#recovery">Recovery</a>'
    '<a href="#gates">Gates</a><a href="#next">Next</a></nav>'
  )
  return f'''{css}<div class=readbar aria-hidden=true><span></span></div>
<article class=lesson data-slug="{SLUG}">
<div class=lesson-layout><div class=lesson-main>
<nav class=crumbs aria-label=Breadcrumb><a href="/">Home</a> / <a href="/lessons/">Lessons</a> / <a href="/lessons/path/">Path</a> / <span>Protecting state transitions</span></nav>
<p class="eyebrow status-preview">Foundations · Lesson 007 · release candidate</p>
<h1>Protecting State Transitions</h1>
<p class=lead>Expected revisions and program-enforced checks.</p>
{_workspace()}
{body}
</div>{rail}</div>
<div class=dock role=region aria-label="Lesson actions">
<a class=btn href="{ASSESS_PATH}">Assessment rubric</a>
<a class="btn ghost" href="{L006_PATH}">Lesson 006</a>
<button type=button class="btn ghost" data-jump>Next section</button>
</div>
</article>'''


def assessment_html(css=''):
  assert len(LESSON_DESC) <= 158 and len(ASSESS_DESC) <= 158, (len(LESSON_DESC), len(ASSESS_DESC))
  body = f'''{status_panel()}
<p class=lead>Determine whether a student can explain a stale-write race, specify and enforce a guarded update, test its boundaries, and handle a rejected stale request without silently overwriting intervening work.</p>
<p>This rubric evaluates <a href="{PATH}">Lesson 007</a>’s controlled Profile Card program and client. It does not certify production readiness, general concurrency safety, security-audit competence, or exactly-once business execution. Record program-implementation vs guided-investigation route accurately.</p>

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
<p>Lesson notes, schema, framework docs, starter docs, debugging tools, and accessibility tools do not reduce an independent result. Looking up syntax does not, by itself, reduce independence.</p>

<h2 id=setup>Assessment setup</h2>
<pre class=diagram>Profile: update_authority, display_name, revision
Guarded instruction: update_profile_checked(new_name, expected_revision)

Must validate: account/schema, signature, authority match, name validity,
revision equality, safe increment.
On success: name changes, revision +1, authority preserved.
On rejection: profile update must not persist.</pre>
<p>Evidence: starting fixture; program source or guided implementation; instruction evidence; test results with state assertions; client conflict demo; limitations statement. Identify local execution, simulation, or submitted devnet transactions.</p>

<h2 id=c1>Criterion 1 — Explains the stale-write race</h2>
<ul>
<li><b>Not yet:</b> treats stale state as necessarily an authority failure; assumes a fresh read eliminates all races; cannot identify the intervening update.</li>
<li><b>Independently:</b> explains the read–intervening update–submission sequence and distinguishes permission to act from the state assumption underlying the action.</li>
</ul>
<p>Scenario: both tabs read revision 12; B updates to 13; A submits draft based on 12; both use legitimate authority. Ask: is A necessarily unauthorised? What assumption became outdated? Why is a client-only check insufficient?</p>

<h2 id=c2>Criterion 2 — Specifies the guarded transition</h2>
<ul>
<li><b>Independently:</b> separately specifies account validity, signature, authority, input validity, revision equality, and safe increment; states exact permitted state change and rejection behaviour.</li>
</ul>
<p><b>Critical misconception.</b> “Anyone who supplies the right revision may update the profile.”</p>

<h2 id=c3>Criterion 3 — Demonstrates program-side enforcement</h2>
<ul>
<li><b>Not yet:</b> only a client-side comparison; removes existing authorisation checks; permits wraparound; claims protection despite a relevant unguarded path.</li>
<li><b>Independently:</b> demonstrates the guarded program path; preserves existing validation; uses a safe increment; identifies how relevant mutation paths affect the claimed guarantee.</li>
</ul>
<p>Do not require one particular framework syntax. A repository containing the right code is insufficient if the student cannot explain the checks. Guided route: identify enforcing checks, configure the guarded path, demonstrate rejection through tests, explain why client-only is weaker.</p>

<h2 id=c4>Criterion 4 — Designs and interprets meaningful tests</h2>
<table>
<thead><tr><th>Test</th><th>Expected result</th></tr></thead>
<tbody>
<tr><td>Valid update</td><td>Name changes; revision +1; authority unchanged</td></tr>
<tr><td>Stale revision</td><td>Rejected; profile unchanged</td></tr>
<tr><td>Future revision</td><td>Rejected; profile unchanged</td></tr>
<tr><td>Wrong authority</td><td>Rejected; profile unchanged</td></tr>
<tr><td>Invalid name</td><td>Rejected; profile unchanged</td></tr>
<tr><td>Missing required signature</td><td>Rejected; profile unchanged</td></tr>
<tr><td>Revision overflow</td><td>Rejected; no wraparound</td></tr>
<tr><td>Newly constructed stale request</td><td>Second update rejected</td></tr>
</tbody>
</table>
<p>For rejection cases, compare <code>display_name</code>, <code>revision</code>, and <code>update_authority</code> before and after. For stale-revision tests, keep signer and name valid. Identify whether a missing-signature request was rejected during construction, verification, simulation, or program execution.</p>

<h2 id=c5>Criterion 5 — Handles conflicts without silent overwrite</h2>
<p><b>Confirmed stale revision:</b> show rejection; preserve draft; retrieve latest profile where possible; compare revisions; offer discard or deliberate review; do not silently resubmit.</p>
<p><b>Unresolved submission:</b> preserve original attempt; state outcome unresolved; reconcile before replacement; do not display a definitive stale-revision diagnosis without supporting evidence.</p>
<p><b>Acceptable explanation.</b> “Refreshing the expected revision and silently resubmitting could overwrite the intervening edit. The user must review the new state and decide whether the draft is still appropriate.”</p>

<h2 id=c6>Criterion 6 — States the guarantee and its limits</h2>
<ul>
<li><b>Independently:</b> explains the same-revision exclusion property; states necessary assumptions; distinguishes “at most one” from “exactly one”; identifies meaningful non-guarantees.</li>
</ul>
<p>Required: “If one request advances this profile from revision R to R+1, another request still expecting R must be rejected through the guarded path.” Address monotonic revisions; consistent enforcement across relevant mutation paths; correct account and authority validation; the possibility that neither competing request succeeds; newly constructed request vs rebroadcasting identical signed bytes.</p>
<p>At least two non-guarantees (examples): winning content is not necessarily correct; no fair ordering; no real-world identity; does not prevent every duplicate business action; does not protect an unguarded alternative path; does not make all client observations current.</p>

<h2 id=transfer>Independent transfer challenge</h2>
<pre class=diagram>name: "Cedar", revision: 20, authority: A
A may succeed · B revision mismatch · C authority mismatch · D input failure
E stale after success · F silent retry = poor conflict handling</pre>
<p>Ask which rule determines the outcome, what state should remain, and what the client should do next. The student must explain the result, not merely identify a matching address or number.</p>

<h2 id=checks>Mandatory conceptual checks</h2>
<table>
<thead><tr><th>Check</th><th>Required understanding</th></tr></thead>
<tbody>
<tr><td>Client versus program</td><td>A client warning does not enforce an execution-time condition</td></tr>
<tr><td>Authority versus revision</td><td>Revision matching does not replace authorisation</td></tr>
<tr><td>Guarded transition</td><td>Rejection must not persist the profile update</td></tr>
<tr><td>Conflict review</td><td>A stale draft must not be silently resubmitted against a refreshed revision</td></tr>
<tr><td>Mutation-path consistency</td><td>A relevant unguarded path can undermine the claimed protection</td></tr>
<tr><td>Guarantee boundary</td><td>At most one matching-revision update ≠ universal exactly-once</td></tr>
</tbody>
</table>

<h2 id=decisions>Completion decisions</h2>
<table>
<thead><tr><th>Decision</th><th>Requirements</th></tr></thead>
<tbody>
<tr><td>Completed independently</td><td>All six criteria independent; required tests completed; conceptual checks satisfied</td></tr>
<tr><td>Completed with support</td><td>All six at least with support; required tests completed; conceptual checks satisfied</td></tr>
<tr><td>Further practice needed</td><td>A criterion not yet demonstrated</td></tr>
<tr><td>Assessment paused</td><td>Technical, accessibility, or evidence issues prevent fair judgement</td></tr>
</tbody>
</table>
<p>Record route and environment separately (program implementation or guided investigation; local, devnet, or mixed). A guided investigation may demonstrate independent understanding but must not be recorded as independently authored code. No additional fee-paying transaction is required solely for reassessment.</p>

<h2 id=record>Assessor record template</h2>
<pre class=diagram>SOL.COLLEGE — LESSON 007 ASSESSMENT
Student identifier:
Assessment date:
Lesson version: 1.0
Rubric version: 1.0 — proposed; requires assessor calibration
Assessor:
Route: [ ] Program implementation  [ ] Guided configuration and investigation
Environment: [ ] Local tests  [ ] Devnet  [ ] Mixed
Criterion 1 — Stale-write race:
Criterion 2 — Transition specification:
Criterion 3 — Program enforcement:
Criterion 4 — Test quality:
Criterion 5 — Client conflict handling:
Criterion 6 — Guarantee and limits:
Required tests:
[ ] Valid update
[ ] Stale revision
[ ] Future revision
[ ] Wrong authority
[ ] Invalid name
[ ] Missing required signature
[ ] Revision overflow
[ ] Newly constructed stale request
Client demonstrations:
[ ] Confirmed conflict
[ ] Unresolved submission
[ ] No silent refresh-and-resubmit
Conceptual checks:
[ ] Client versus program
[ ] Authority versus revision
[ ] Guarded transition
[ ] Conflict review
[ ] Mutation-path consistency
[ ] Guarantee boundary
Decision:
Feedback:
Reassessment required:</pre>
<p class=cta><a class=btn href="{PATH}">Back to Lesson 007</a> <a class="btn ghost" href="{L006_PATH}">Lesson 006</a> <a class="btn ghost" href="/lessons/path/">Learning path</a></p>
'''
  rail = (
    '<nav class=rail aria-label="On this page">'
    '<a href="#levels">Levels</a><a href="#setup">Setup</a><a href="#c1">Race</a>'
    '<a href="#c2">Invariant</a><a href="#c3">Enforcement</a><a href="#c4">Tests</a>'
    '<a href="#c5">Conflict</a><a href="#c6">Limits</a><a href="#transfer">Transfer</a>'
    '<a href="#checks">Checks</a><a href="#decisions">Decisions</a><a href="#record">Record</a></nav>'
  )
  return f'''{css}<div class=readbar aria-hidden=true><span></span></div>
<article class=lesson data-slug="{SLUG}-assessment">
<div class=lesson-layout><div class=lesson-main>
<nav class=crumbs aria-label=Breadcrumb><a href="/">Home</a> / <a href="/lessons/">Lessons</a> / <a href="{PATH}">Protecting state transitions</a> / <span>Assessment</span></nav>
<p class="eyebrow status-preview">Foundations · Lesson 007 assessment · release candidate</p>
<h1>Assessment rubric: State Guardian</h1>
{body}
</div>{rail}</div>
</article>'''


def card_html():
  return (
    f'<article class="card ready-preview" data-lesson data-slug="{SLUG}" data-diff="Beginner" data-format="foundations" '
    f'data-text="expected revision stale write guard program conflict protect state transitions foundations">'
    f'<p class="eyebrow status-preview">Foundations · Lesson 007 · release candidate</p>'
    f'<h3><a href="{PATH}">Expected revisions and program-enforced checks.</a></h3>'
    f'<p class=project>Protecting State Transitions</p>'
    f'<p class=limit>Known limit: teaching specification only until the guarded handler and conflict UI '
    f'are verified. Client warning ≠ program precondition.</p>'
    f'<p class=meta><span class="chip beg">Beginner</span> · ~75–90 min design estimate · Local tests first</p>'
    f'<p class=cta><a class=btn href="{PATH}">Open Lesson 007</a> · <a href="{ASSESS_PATH}">Assessment rubric</a></p>'
    f'</article>'
  )
