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
 'finality-under-named-rules': dict(
  terms=[
   'Document claim: a sentence in a retrieved white paper or SIMD that names a finality, resilience, round, or vote rule. The claim is anchored to a catalogue slug and version string.',
   'Operationalisation: a rule that maps a document claim onto bytes or slots a harness could store. Claims that cannot be mapped stay labelled non-operationalised.',
   'Cluster observation: a stored response from a named cluster at a named commitment, with client versions recorded. An illustration is not this observation.',
   'Version pin: Alpenglow v1, v1.1, and v1.2 on the shelf are different documents. Mixing their sentences without a pin is a methods error.',
   'Process label: SIMD status words such as Review or Activated are the file’s labels. They are not journal peer review and not a Sol.College cluster reading.',
  ],
  split='The observation is either (a) the extracted sentence with its document anchor or (b) the harness record from a cluster. The interpretation is “the network does X”. That interpretation is forbidden until (b) exists and matches the operationalisation written before the run.',
  illustration='Imagine a reader who quotes “20+20” resilience from an Alpenglow PDF as if it were a measurement of today’s validators. The picture’s only job is to force two columns: PDF sentence, and validator set observation. No validator set was measured for this page.',
  negative='If every checkable claim on the chosen documents already matches the chosen cluster records, the contribution is the inventory method and a smaller claim. Agreement on a convenience sample is not agreement on the whole shelf.',
  design=[
   'Build the claim inventory from named shelf slugs before any cluster query. Adding a claim after a surprising observation is exploratory and must be labelled.',
   'Write operationalisation rules in the same pass as the inventory. A rule invented to rescue a mismatch is a different study.',
   'Keep PDF version strings in the primary key. Do not collapse v1 and v1.2.',
   'Record non-operationalised claims in public. Silence is not operationalisation.',
   'If the observational arm is built, name the cluster, the RPC, the commitment, and the client versions. “Solana” alone is not a system.',
   'Cite appraisals for bibliographic hygiene. Do not cite an appraisal as a measurement.',
  ]),
 'fee-and-rent-observation': dict(
  terms=[
   'Displayed cost: the fee or rent figure a product or docs page shows for a step.',
   'Balance-change set: every lamport and token delta across accounts touched by the workflow, including failed attempts.',
   'Omitted cost: a member of the balance-change set that the displayed cost does not include.',
   'Documentary fee sentence: an official or design-file sentence about fees retrieved for the library. It is prior wording, not a remeasurement.',
  ],
  split='The observation is the balance-change set and the displayed figure, stored side by side. The interpretation is “users pay X”. That sentence is earned only from the set, not from the display alone.',
  illustration='Imagine a checkout that prints a signature fee and is silent about creating an associated token account in the same workflow. The picture forces the missing line into the table. No checkout was costed for this page.',
  negative='A workflow whose display matches its balance changes answers the question for that workflow only. Likeness does not travel to a different account layout.',
  design=[
   'Declare the workflow and the accounts of interest before the run.',
   'Include at least one failing attempt as its own row.',
   'Cite shelf fee documents as priors with catalogue links. Do not paste their figures into the observation column.',
   'Keep token amounts and lamports in separate columns.',
   'State which mint and which program versions were used.',
  ]),
 'upgrade-bytes-and-disclosure': dict(
  terms=[
   'Loader authority: the address a stated on-chain record names as allowed to supply new program bytes.',
   'User-reachable disclosure: a statement available without a private channel — a site, a docs page, an explorer field the study pre-registers as in scope.',
   'Mismatch: the disclosure names a different authority, omits it, or uses a word such as immutable while the loader record names an authority.',
   'Documentary upgrade prior: a retrieved SIMD or design note about upgrades. Prior wording, not an inspected deployment.',
  ],
  split='The observation is the pair (loader record, disclosure text) at a recorded time. The interpretation is whether a careful reader of only the disclosure would identify the loader authority.',
  illustration='Imagine a landing page that says “immutable” while the loader account still names an upgrade authority. The picture is the pair of records. No deployment was inspected for this page.',
  negative='If the chosen set already discloses correctly, the result is about that set. It is not a finding that all programs disclose correctly.',
  design=[
   'Fix the on-chain read method and the disclosure sources before collecting pairs.',
   'Count missing disclosure separately from wrong disclosure.',
   'Do not use private messages as disclosure.',
   'Pin program ids and slots on every row.',
   'Keep unpublished exploit detail out of the journal record.',
  ]),
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
 dict(slug='vote-credits-and-schedule', title='Vote Credits and Leader Schedule',
  section='Protocol and runtime',
  question='When a design file changes how vote credits or leader schedules are computed, which observable records would a study have to store before and after to say the change landed?',
  why='Shelf documents name timely vote credits, vote-account versions, and address-keyed leader schedules. A status label on a SIMD is not a before/after table from a named cluster.',
  terms=['Vote credit rule: the formula or process a named document states for counting credits.', 'Leader schedule rule: how a named document assigns slots to vote accounts.', 'Before/after observation: two stored reads from a named cluster at named slots, with client versions.', 'Document delta: the difference between two retrieved file versions, kept separate from any cluster delta.'],
  split='The observation is either the document delta (with pinned versions) or the stored cluster records. The interpretation “credits changed on mainnet” requires the second.',
  illustration='Imagine a reader who treats “Activated” on a vote-credits SIMD as proof their stake earned differently yesterday. The picture forces a document column and a cluster column. No stake account was read for this sketch.',
  negative='Agreement between a document and one cluster sample is not agreement for every epoch or every client.'),
 dict(slug='slashable-evidence-records', title='Slashable Evidence Records',
  section='Security and authority',
  question='How do public write-ups of slashable behaviour keep suspected, verified, and acted-on evidence in separate sentences?',
  why='Slashable-event and slashing-rules documents on the shelf supply process language. A reader who collapses those words into one adjective cannot tell what evidence existed.',
  terms=['Suspected: a reason to look, short of a stored verification.', 'Verified: a named check against a named evidence format succeeded, as the study’s rubric defines it.', 'Acted-on: a recorded response (for example a stake penalty) the study can point at. A design note is not this state.', 'Evidence format: the bytes or fields a retrieved slashing document names.'],
  split='The observation is which states a write-up earns under a pre-fixed rubric. The interpretation is the write-up’s own word for severity.',
  illustration='Imagine a post that says “slashed” beside a screenshot with no evidence object and no stake account change. The picture is the missing record. No slash was verified for this sketch.',
  negative='A corpus that already separates the states is a finding about that corpus only.'),
 dict(slug='commitment-across-providers', title='Commitment Across Providers',
  section='Infrastructure and measurement',
  question='For the same signature, do named RPC providers return the same commitment classification under a fixed polling rule?',
  why='Commitment-status and optimistic-confirmation documents name labels. Applications often treat one provider’s label as the cluster’s label.',
  terms=['Commitment label: the string a provider returns for a signature under a named method.', 'Polling rule: the interval, the method, and the stop condition, written before the run.', 'Disagreement: two providers that disagree on the label at the same wall-clock sample, or that cross the finish line in a different order.'],
  split='The observation is the set of (provider, timestamp, label) rows. The interpretation is “the transaction is confirmed”.',
  illustration='Imagine one wallet that flips to confirmed while another still shows processed for the same signature. The picture is the disagreement a study would store. No provider was polled for this sketch.',
  negative='Agreement among the chosen providers answers the question for that set and that rule only.'),
 dict(slug='tower-alpenglow-document-delta', title='Tower and Alpenglow Document Delta',
  section='Protocol and runtime',
  question='Which claims appear in Alpenglow shelf versions that do not appear in Tower BFT and white-paper wording, when both are treated only as documents?',
  why='Readers often narrate a migration as if the PDFs were already the live schedule. A documentary delta is a measurable reading of the shelf; a cluster migration is a different study.',
  terms=['Document claim: a sentence with a catalogue anchor and a version pin.', 'Delta: a claim present in one pinned set and absent in another, scored with rules fixed first.', 'Non-operationalised: a claim that cannot be mapped to a harness record yet; it stays in the document column.'],
  split='The observation is the scored presence/absence matrix across pinned files. The interpretation is that the network has migrated.',
  illustration='Imagine a slide that quotes Alpenglow resilience language as if Tower pages never existed. The picture forces a two-column inventory. No validator set was compared for this sketch.',
  negative='A clean documentary delta does not measure activation. Activation needs cluster records the Finality Under Named Rules protocol would keep.'),
 dict(slug='rent-exemption-paths', title='Rent Exemption Paths',
  section='Payments and applications',
  question='Which account-creation paths leave a balance that a product’s “rent exempt” sentence does not name?',
  why='Storage-rent and economics documents on the shelf state rent language. Product copy often collapses several transfers into one adjective.',
  terms=['Rent-exempt balance: the minimum a named rule requires for an account of a stated size. The study would cite which rule and would not invent a figure.', 'Path: the sequence of creates and funds in a workflow, including failed creates.', 'Unnamed transfer: a balance change on the path that the product sentence omits.'],
  split='The observation is the path’s balance-change set beside the product sentence. The interpretation is “users only pay rent”.',
  illustration='Imagine a flow that creates a token account and a metadata account while the UI says a single rent-exempt fee. The picture is the missing line. No path was costed for this sketch.',
  negative='One product that already lists every transfer answers the question for that product only.'),
 dict(slug='stake-delegation-disclosure', title='Stake Delegation Disclosure',
  section='Economics and governance',
  question='Can a delegator following only public statements identify which vote account and which withdraw authority a stake account currently names?',
  why='Stake-delegation and vote-account documents describe fields. Wallet and pool UIs may show a name that is not those fields.',
  terms=['Vote account field: the address a stake account’s delegation record names.', 'Withdraw authority: the address allowed to withdraw, as the study’s on-chain read defines it.', 'Public statement: a UI string, a pool page, or a docs line the study pre-registers as in scope.'],
  split='The observation is the pair (on-chain fields, public statement) at a recorded slot. The interpretation is whether a careful reader of only the statement would identify those addresses.',
  illustration='Imagine a liquid-staking page that shows a brand name while the stake account points at a different vote account. The picture is the pair. No stake account was read for this sketch.',
  negative='Correct disclosure on the chosen set is a finding about that set only.'),
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
