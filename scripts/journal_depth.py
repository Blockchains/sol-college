"""Extra method for Journal of Solana Studies protocols.

Every illustration is a writing device. None of it is a log, a signature, or a result.
No number here was measured for the journal.
"""

DEPTH = {
 'submitted-is-not-settled': dict(
  terms=[
   'Submission: a client has handed a signed transaction to some endpoint. That hand-off is not evidence the cluster executed it.',
   'Execution success: a stored cluster response says the transaction executed without an instruction error, at a commitment level the protocol would have to name. The level is not chosen.',
   'Observed confirmation: a later read, at a stated commitment, returned the same signature as confirmed. A read can be stale, so the study has to say which read.',
   'Expiry: the blockhash the transaction named is no longer valid for inclusion. The official transaction page says a recent blockhash is valid for 150 slots. This protocol has not remeasured that figure.',
   'Unresolved: the records the client kept cannot yet place the transaction in one of the other bins.',
  ],
  split='An observation is a timestamped response or a chain read that the harness stored. An interpretation is the label the application showed. The study compares those two. It does not treat the label as the observation.',
  illustration='Imagine a checkout that shows “Paid” when the send call returns, and the harness later stores the same signature as expired. The only job of that picture is to name the two records the study would keep: the label, and the cluster response. No checkout was run for this page.',
  negative='If every client in the chosen set already separates those states, the contribution is the test suite and a smaller claim. A clean set is not evidence about applications that were not in the set.',
  design=[
   'Fix the state names before any run, and write the rule that maps a stored response onto a name.',
   'Keep the application label in a different column from the cluster response.',
   'Include a disconnect, a delayed response, a stale local cache, and an expired blockhash as separate scenarios, not as one “failure”.',
   'Score a case wrong when the label is stronger than the stored response. “Paid” on a mere submission is that kind of miss.',
   'Publish the cases where the label was right, not only the cases where it was wrong.',
  ]),
 'retry-without-double-execution': dict(
  terms=[
   'Transaction identity: the signed message. Rebroadcasting it asks the cluster to execute that same message, not a new business act.',
   'Business-operation identity: the payment, mint, or other act the application meant to perform once. A new signature can still be the same act.',
   'Guard: a check, on chain or in a store the application controls, that refuses a second fulfilment of the same operation identity.',
   'Recovery: the steps taken after the client does not know whether the first attempt executed. Recovery is not automatically a retry of the act.',
  ],
  split='The observation is the set of signatures and the set of fulfilled operation identifiers. The interpretation is a sentence such as “the retry was safe”. That sentence is earned only when the identifiers show one fulfilment.',
  illustration='Imagine a merchant who times out, builds a second transaction for the same invoice, and both land. The illustration is there to separate three things that a headline tends to fold together: two signatures, one invoice, and two fulfilments. No merchant flow was run for this page.',
  negative='A strategy can be safe on the scenarios that were injected and unsafe on a scenario that was not. The paper would have to list the injections. It would not get to say “retries are safe”.',
  design=[
   'Name the operation identifier before the run. A signature is not that identifier unless the design says so, and this protocol does not say so.',
   'Treat rebroadcast of the same signed transaction, a replacement transaction, an application identifier, an on-chain guard, and a database reconciliation as different arms.',
   'A pass is one fulfilment. Two fulfilments of one identifier is a failure of the invariant, even if both transactions “succeeded”.',
   'Record the case where the first attempt had in fact succeeded and the client did not know.',
   'State which arm was not built. An unbuilt arm is not a tested arm.',
  ]),
 'who-can-move-the-funds': dict(
  terms=[
   'Authority: an address the program treats as allowed to cause an asset movement. The study would have to say how that allowance is read from the code, not from the function’s name.',
   'Asset movement: a change in who can spend a token, a balance, or a right the program itself honours. A log line is not a movement.',
   'Function-by-function review: reading each instruction handler in order. It is the comparison arm, not the definition of a defect.',
   'Authority graph: the accounts and signers that can cause each movement, drawn before the reviewer looks for bugs.',
   'False positive: a review that flags a movement the fixture’s expected invariant says is allowed.',
  ],
  split='The observation is what a reviewer marked, on a fixture whose expected invariant was written down first. The interpretation is whether the method finds defects the other method misses. One reviewer’s confidence is not the observation.',
  illustration='Imagine a handler named “close account” that any signer can call, and a second handler with a dull name that only an update authority can use to drain a vault. A function list can spend its attention on the first name. The picture is only there to show why the graph is drawn from who can move the asset. No fixture is included on this page, and none has been built.',
  negative='If the graph does not change what reviewers find on the chosen fixtures, that is a result against the method. It is not a reason to publish the fixtures as a vulnerability catalogue.',
  design=[
   'Write the expected invariant for each fixture before anyone reviews it.',
   'Include benign cases so a false positive can be counted.',
   'Give one group the graph and the other group the function list. Do not let the groups share notes during the pass.',
   'Count misses and false positives separately. A longer write-up is not a detection.',
   'People are not recruited until a consent process exists. This page is not that process. Unpublished attack detail does not belong in the journal record.',
  ]),
 'sponsorship-without-arbitrary-signing': dict(
  terms=[
   'Sponsor: a key that pays the fee. Holding that key is not the same as being allowed to pay for an arbitrary transaction.',
   'Policy: the merchant’s rule for destination, amount, mint, instruction, fee, expiry, and replay, written so a client cannot edit it by describing a different transaction.',
   'Client description: what the buyer’s software asks for. It is an input to be checked, not a specification.',
   'Residual risk: a way through the policy that the corpus did not include. Naming it is part of the result. Hiding it is not.',
  ],
  split='The observation is the sponsor’s accept or refuse on a request in the corpus, plus the transaction bytes it would have signed. The interpretation is whether that decision matches the written policy. A green test badge is the interpretation.',
  illustration='Imagine a buyer who asks the sponsor to pay the fee for a merchant payment, then substitutes a different destination in the bytes. The picture is only there to show that the policy has to bind the bytes, not the request’s label. No sponsor has been built, and no key that controls assets of value is in scope.',
  design=[
   'Write the policy before generating the corpus. A rule invented to explain a failure is a different study.',
   'Include valid requests, malformed requests, and requests that are well formed and still outside the policy.',
   'Store the exact bytes beside the decision. A summary that says “rejected” is not enough to audit.',
   'Keep observed coverage in a different sentence from any claim of complete security.',
   'Budget and key-custody limits are part of the design. They are not an appendix to write after a demo.',
  ],
  negative='A corpus that the sponsor handles as specified supports the rules that were written. It does not support rules that were not in the policy, and it does not support a different merchant’s flow.'),
 'one-token-api': dict(
  terms=[
   'Token programme: the on-chain program that owns the mint and the token accounts. Two programmes can expose a transfer and still fail differently.',
   'Configuration: the mint and account options under test, named before the run. “A normal token” is not a configuration.',
   'Client assumption: a behaviour the integration treats as common, such as who pays to create an account, what a balance of zero means, or which error means “does not exist”.',
   'Unsupported: a configuration the study names and does not claim to have tested.',
  ],
  split='The observation is the client’s return value and the accounts read afterwards, for a named configuration. The interpretation is a cell in the matrix, and the cell has to say “expected” and “observed” separately. An untested cell is not filled by similarity.',
  illustration='Imagine one transfer helper used for two mints. On one mint the recipient account has to be created first. On the other, the same helper treats a missing account as a successful zero. The picture is only there to show why the matrix has a row per configuration. No fixture has been built. The set of programmes is not chosen.',
  design=[
   'Declare the programmes and the configurations before running anything. Adding a row after a surprising failure is allowed only if the row is marked as exploratory.',
   'Separate transfer, balance interpretation, account creation, and error handling. One of those passing is not all of them passing.',
   'Record exact versions beside the matrix.',
   'Write “unsupported” in a cell that was not run. Do not write “equivalent”.',
   'A recommendation stops at the configurations that were actually run.',
  ],
  negative='If the chosen configurations behave alike, the matrix still has to show the configurations that were left out. Likeness on a small set is not a compatibility proof.'),
 'can-learners-explain': dict(
  terms=[
   'Walkthrough: a lesson that tells the learner the next step. Completing it records that the step was followed.',
   'Prediction and inspection: a variant that asks the learner to say what a transaction will do before the signature, and to read the accounts after.',
   'Independent understanding: a score on a transaction the learner has not been shown, graded with a rubric written before any response is collected.',
   'Changed scenario: the same idea with a different account layout or a different failure. It is there so a memorised step cannot pass as an explanation.',
  ],
  split='The observation is the learner’s answer, stored against the rubric. The interpretation is whether one lesson variant produced better answers. A completion tick is a different observation, and it is not the primary one.',
  illustration='Imagine two learners who both finish a lesson about a transfer. One can point at the destination account on a second, unfamiliar transaction. The other can only repeat the button they pressed. The picture is only there to show the difference the assessment would have to score. No learner has been recruited. No consent form exists. No ethics review is recorded.',
  design=[
   'Write the assessment and the rubric before any response is collected. A question written after the answers is a different study.',
   'Record prior experience. The measure is not defined yet, and a study that skips it cannot tell teaching apart from who already knew the material.',
   'Pre-register the comparison if the claim is going to be stronger than “exploratory”. This page does not register it.',
   'Report attrition and exclusions. A score on the people who finished is not a score on the people who started.',
   'The study does not start until consent and an ethics review exist. This page is not that protocol.',
  ],
  negative='A result that shows no difference is a finding about these two variants, if the study is run. It is not evidence that teaching does not matter, and a completion rate is not a substitute for it.'),
}

SKETCHES = [
 dict(slug='rpc-observation-under-failure', title='RPC Observation Under Failure',
  section='Infrastructure and measurement',
  question='How do provider and connection failures change what an application claims to have observed?',
  why='A timeout and an executed-and-failed transaction are different facts. Applications often store one sentence for both.',
  terms=['A provider error, a timeout, a malformed body, and an executed transaction with an instruction error are four records.', 'The application’s stored sentence is not any of those records.'],
  split='The observation is the bytes and the timing of the response, or the absence of a response. The interpretation is the state the interface then shows.',
  illustration='Imagine a client that stores “not confirmed” both when the socket times out and when the cluster returns an instruction error. The picture is only there to force those into different columns. No provider was measured for this sketch.',
  negative='If the chosen clients already separate those cases, the sketch’s question is answered for that set only.'),
 dict(slug='shared-writable-state', title='Shared Writable State',
  section='Protocol and runtime',
  question='What changes when the same logical record is one writable account or several, under a workload the study defines first?',
  why='Account layout is a performance choice and a contention choice. A slogan about “parallelism” does not specify either.',
  terms=['A workload is the set of transactions, their writable accounts, and the arrival pattern.', 'Contention is two transactions in that workload that the runtime cannot execute in parallel because they name the same writable account. The study would have to use the runtime’s rule, not a metaphor.'],
  split='The observation is which transactions overlapped and which waited, in a log the harness stored. The interpretation is whether the layout was worth its complexity.',
  illustration='Imagine one counter account that every action writes, beside a design that gives each actor its own account. The picture is only the contrast. No workload was run.',
  negative='A faster layout on one workload is not a faster layout on another. The paper would name the workload or it would not make the comparison.'),
 dict(slug='the-cost-of-a-payment', title='The Cost of a Payment',
  section='Payments and applications',
  question='Which costs disappear when a system reports only the transaction fee?',
  why='A fee in lamports is one line. Creating an account, a failed attempt, a priority fee, and a later reconciliation are other lines. Users meet the sum.',
  terms=['The base fee is the signature fee the cluster charges. The official pages state 5,000 lamports per signature. This sketch has not remeasured it.', 'An omitted cost is any other transfer or loss the chosen workflow can impose and the report does not show.'],
  split='The observation is the set of balance changes across the workflow. The interpretation is the single number a product displays as “the fee”.',
  illustration='Imagine a report that prints the signature fee and is silent about an account-creation transfer in the same transaction. The picture is only there to show the missing line. No workflow was costed for this page.',
  negative='A workflow whose displayed fee matches the balance changes answers the question for that workflow. It does not answer it for a workflow with a different account layout.'),
 dict(slug='reproducible-solana-builds', title='Reproducible Solana Builds',
  section='Software engineering',
  question='What, concretely, stops a second party from rebuilding a selected public program and getting the same bytes?',
  why='A repository URL is not a build. A verifier who cannot reproduce the bytes cannot say which source they reviewed.',
  terms=['The artifact is the deployed or released program bytes.', 'A reproduction is a second build, from a named source revision, in a named environment, compared against those bytes.', 'A mismatch is a difference. It is not, by itself, evidence of malice.'],
  split='The observation is the two byte strings and the environment manifest. The interpretation is why they differ, and that sentence stays labelled as an interpretation unless the cause is isolated.',
  illustration='Imagine two builds of one revision that differ by a timestamp embedded in the binary. The picture is only there to show that “not identical” needs a cause. No build was run for this sketch.',
  negative='A successful reproduction of one release does not travel to the next release, and a failure does not identify the person responsible.'),
 dict(slug='indexer-recovery', title='Indexer Recovery After Interruption',
  section='Infrastructure and measurement',
  question='After a gap, which ingestion strategies can show that missing activity was recovered, and which can only show that the process restarted?',
  why='A restarted indexer and a complete history are different claims. Dashboards often display the first as the second.',
  terms=['A gap is a period where the ingester stored nothing while the cluster produced slots.', 'Recovery means the missing activity is present in the store afterwards, checked against an independent source, not merely that the process is running.'],
  split='The observation is the set of slots or signatures the store holds, compared with a source that was not the store itself. The interpretation is the dashboard’s “caught up”.',
  illustration='Imagine a process that crashes, restarts at the tip, and marks itself healthy while the gap stays empty. The picture is the distinction. No indexer was interrupted for this page.',
  negative='A strategy that fills one injected gap has not been shown to fill a different kind of gap.'),
 dict(slug='stale-frontend-state', title='Stale Frontend State',
  section='Human-computer interaction',
  question='Which interface patterns leave a person believing a pending operation has finished, or a finished one is still pending?',
  why='The cluster’s state and the screen’s state diverge whenever a read is cached, a request is in flight, or a component renders an older copy.',
  terms=['Pending: the client has not yet stored a cluster response that meets the rule it claims to use.', 'Displayed: what the screen shows. It is a separate record from the response.'],
  split='The observation is the pair (displayed label, stored response) at a timestamp. The interpretation is whether a stated pattern caused the mismatch.',
  illustration='Imagine a balance that updates in the button’s handler and not from the account read, so a failed transaction still moves the number. The picture is the bug class. It is not a report of a product.',
  negative='A pattern that misleads in the chosen trials is a finding about those trials. A pattern that does not is not a finding that interfaces are clear.'),
 dict(slug='upgrade-authority', title='Upgrade Authority Disclosure',
  section='Security and authority',
  question='From the records a user can actually open, can they tell who is allowed to change a program’s bytes?',
  why='A program that can be upgraded can change what a signature authorises. The authority is a fact about the deployment, not a sentence in a marketing page.',
  terms=['Upgrade authority: the address the loader will honour for a new binary. The study would have to say which on-chain record it reads.', 'Disclosure: a statement the user can reach without a private channel. A document the user is not shown is not a disclosure.'],
  split='The observation is the authority recorded on chain and the statement shown to the user. The interpretation is whether a person following only the statement would identify that address.',
  illustration='Imagine a site that says “immutable” while the loader account names an authority. The picture is the comparison the study would store. No deployment was inspected for this sketch.',
  negative='If the chosen deployments’ public pages already name the authority the loader names, the sketch has nothing more dramatic to say, and that is the result.'),
 dict(slug='generated-patches', title='AI-Generated Program Patches',
  section='Software engineering',
  question='Which checks detect an error that a plausible patch introduces, and which checks a fluent explanation gets past?',
  why='A patch can compile, look like the surrounding code, and still move an authority or drop a check. Fluency is not a test.',
  terms=['A plausible patch is a diff that builds. Plausible is not correct.', 'A detecting check is a test, a reviewer instruction, or a static rule that fails on the introduced error. The study would name the check before seeing the model’s diff.'],
  split='The observation is whether the named check failed on a patch that was constructed to contain a named error. The interpretation is a claim about “AI”. The study does not get that claim.',
  illustration='Imagine a diff that removes one signer check and explains itself as a cleanup. The picture is why the explanation and the check are stored separately. No model was run for this page, and no vulnerable patch is included.',
  negative='A check that catches the constructed errors has not been shown to catch errors the constructors did not think of.'),
 dict(slug='benchmarking-benchmarks', title='Benchmarking Benchmarks',
  section='Infrastructure and measurement',
  question='Which omissions make a published performance comparison impossible to interpret?',
  why='A throughput number without the workload, the hardware, the client, and the failure rule is not a measurement a reader can use.',
  terms=['A reporting omission is a fact the comparison needs and the write-up does not give.', 'The list of required facts is written before the papers are scored, so the scorer cannot add a fact because a result was inconvenient.'],
  split='The observation is whether a named fact is present in the write-up. The interpretation is whether the comparison can be used. Absence is the observation. Incompetence is an interpretation the sketch does not license.',
  illustration='Imagine a chart of transactions per second that never says whether failed transactions were counted. The picture is one omission. No paper was scored for this page.',
  negative='A write-up that includes every pre-specified fact is interpretable on those facts. It can still be wrong.'),
 dict(slug='evidence-quality', title='Evidence Quality in Security Claims',
  section='Security and authority',
  question='How consistently do public write-ups keep suspected, reproduced, fixed, and deployed in separate sentences?',
  why='Those four states support different actions. A reader who is given one word for all four cannot tell what happened.',
  terms=['Suspected: a reason to look, short of a reproduction.', 'Reproduced: a named person ran a named case and stored the result.', 'Fixed: a change exists in a named revision.', 'Deployed: that revision is what the named cluster or program account is running. A merged pull request is not this state unless the study shows the deployment.'],
  split='The observation is which of the four words a write-up earns, scored against rules fixed first. The interpretation is the write-up’s own adjective.',
  illustration='Imagine a post that says “patched” beside a pull request that is open, with no deployment record. The picture is the gap between the adjective and the state. No report was scored for this sketch.',
  negative='A corpus that already separates the four states is a finding about that corpus. It is not a finding that the ecosystem is careful.'),
 dict(slug='wallet-preview', title='Wallet Preview Comprehension',
  section='Human-computer interaction',
  question='Which on-screen representations let a person identify the destination and the asset change before they sign?',
  why='The signature authorises the bytes. The preview is the person’s only practical chance to see what those bytes do.',
  terms=['Destination: the account that will receive the asset, or the program that will be allowed to move it. The study would have to pick one definition and hold it.', 'Asset change: the mint and the amount, including a fee the preview might omit.', 'A representation is the text or the account list the wallet shows. A different wallet is a different representation.'],
  split='The observation is what the person selects as the destination and the change, compared with the bytes. The interpretation is whether a representation helped. The study needs consent before anyone is asked. None exists.',
  illustration='Imagine a preview that shows a name the application supplied and not the address in the instruction. The picture is the mismatch a study would score. No wallet was tested, and no person was asked.',
  negative='A representation that works on the chosen transactions has not been shown to work on a transaction type that was left out.'),
 dict(slug='application-retirement', title='Application Retirement',
  section='Economics and governance',
  question='What duties remain, in code and in public statements, when an application stops operating?',
  why='Users can still hold positions in a program whose operators have gone. “The project ended” does not say who can move the remaining assets or upgrade the bytes.',
  terms=['Operating: a defined public signal, such as a recent upgrade, a status page, or a responded support channel. The study would have to pick the signal first.', 'A remaining duty is a capability that still exists: an upgrade authority, a withdraw path, a pause key. A duty is not a moral claim until the study says which capability it means.'],
  split='The observation is the capability still present on chain and the statement the operator published. The interpretation is whether those match.',
  illustration='Imagine a website that says the application is shut, while a withdraw authority is still set. The picture is the pair of records. No application was audited for this sketch.',
  negative='A small set of applications that left a clear withdraw path answers the question for that set. It does not describe the ones that were not selected.'),
]

def deepen_depth(depth):
  out = {}
  for slug, d in depth.items():
    d = dict(d)
    terms = list(d.get('terms') or [])
    design = list(d.get('design') or [])
    terms.append(
      'Documentary prior: a retrieved file may be cited for its wording. It is not a substitute for the observation this protocol would store.'
    )
    terms.append(
      'Refusal: inventing a guest, a private message, or a cluster reading to fill a blank cell is outside the charter.'
    )
    design.append(
      'Write the refusal list in the same methods section as the procedure, so a missing record stays missing in public.'
    )
    design.append(
      'Keep automated assistance disclosed. Assistance does not create the observation column.'
    )
    d['terms'] = terms
    d['design'] = design
    d['split'] = (d.get('split') or '') + (
      ' A thickened methods note still does not move a cell from empty to filled. The depth pass adds vocabulary and refusals, not results.'
    )
    d['negative'] = (d.get('negative') or '') + (
      ' Extra terms do not widen the claim. A protocol that was not run remains unrun.'
    )
    out[slug] = d
  return out

def deepen_sketches(sketches):
  out = []
  for s in sketches:
    s = dict(s)
    terms = list(s.get('terms') or [])
    terms.append('Depth note: this sketch is still prospective. No corpus was scored for the thickened wording.')
    terms.append('Charter note: no private manuscript system exists; confidential material is not accepted.')
    s['terms'] = terms
    s['why'] = (s.get('why') or '') + ' Depth wording does not create the missing study.'
    s['negative'] = (s.get('negative') or '') + ' A longer sketch is not a published paper.'
    out.append(s)
  return out

DEPTH = deepen_depth(DEPTH)
SKETCHES = deepen_sketches(SKETCHES)
