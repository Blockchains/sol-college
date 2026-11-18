"""Journal of Solana Studies: the charter, the policies, and prospective protocols.

Nothing here is a completed study, a peer-reviewed paper, or a named editorial board.
A protocol describes a question and a proposed method. It does not report a result.
"""
import html, json, os, re, urllib.parse
PUBLISHED = '2026-11-17'
SITE = 'https://sol.college'
ISSUE = 'https://github.com/Blockchains/sol-college/issues/new'
COPE = 'https://publicationethics.org/guidance/guideline/principles-transparency-and-best-practice-scholarly-publishing'
def E(s):
  return html.escape(str(s if s is not None else ''), quote=True)
def issue(title, body):
  return ISSUE + '?title=' + urllib.parse.quote(title) + '&body=' + urllib.parse.quote(body)
PROPOSE = issue('Journal proposal', 'Research question:\n\nWhy it matters:\n\nProposed method, in outline:\n\nWhat you can and cannot share publicly:\n\nDo not include private keys, recovery phrases, or unpublished vulnerability details. This issue is public. A confidential manuscript system is not operating.\n')
CORRECTION = issue('Journal correction', 'Page:\n\nWhat is wrong:\n\nWhat the source says:\n\n')
REVIEWER = issue('Journal reviewer offer', 'Areas you can review:\n\nRelevant experience, in public terms:\n\nConflicts you would need to declare:\n\nAn offer does not appoint you. No review is under way.\n')
PROTOCOLS = [
 dict(slug='submitted-is-not-settled', n=1, section='Transactions and reliability',
  title='Submitted Is Not Settled',
  subtitle='A reproducible study of transaction-state handling in Solana applications',
  question='How accurately do application transaction-state models distinguish successful execution, observed confirmation, expiry, and unresolved submission?',
  why='An application that treats submission as settlement can tell a user that a payment finished when the evidence says otherwise.',
  comparisons=['Client disconnects.', 'Delayed responses.', 'Stale local state.', 'Expired transactions.', 'Classifications compared with an independent record of what the cluster returned.'],
  outputs=['State-machine definitions.', 'Reproducible scenarios.', 'Timestamped observations.', 'Classification rules.', 'An error analysis.', 'An anonymised dataset where publishing the raw records is safe.'],
  contribution='A reference model and a test suite for applications that must not mistake submission for completion.',
  ethics='No human subjects are proposed. The harness must not spend assets that have value. Devnet or a local validator is the intended setting, and that choice is not made yet.'),
 dict(slug='retry-without-double-execution', n=2, section='Transactions and reliability',
  title='Retry Without Double Execution',
  subtitle='Evaluating recovery strategies for Solana business operations',
  question='Under which tested conditions do retry and recovery strategies preserve the invariant that a business operation is performed at most once?',
  why='Rebroadcasting a transaction and repeating a business operation are different acts. Conflating them is how a retry becomes a second payment.',
  comparisons=['Rebroadcasting the same signed transaction.', 'Constructing a replacement transaction.', 'Application-level operation identifiers.', 'On-chain guards, where a design uses them.', 'Database-side reconciliation and fulfilment controls.'],
  outputs=['An explicit distinction between transaction identity and business-operation identity.', 'Fault-injection scenarios.', 'Invariant checks.', 'Recovery traces.', 'The limits of the design that was evaluated.'],
  contribution='A reproducible way to discuss idempotency without treating every retry as the same operation.',
  ethics='No human subjects are proposed. The scenarios must use test assets.'),
 dict(slug='who-can-move-the-funds', n=3, section='Security and authority',
  title='Who Can Move the Funds?',
  subtitle='An authority-centred evaluation of Solana application security',
  question='Can a structured authority model help reviewers identify defects missed by function-by-function review?',
  why='A checklist of function names can miss who is actually allowed to move an asset. A method is useful only if it can be compared with another method on the same cases.',
  comparisons=['Intentionally vulnerable local fixtures.', 'An authority graph for each fixture.', 'A documented review protocol.', 'Benign cases, so false positives can be counted.', 'Human reviewers only with consent and oversight, which are not yet designed.'],
  outputs=['Vulnerability fixtures.', 'Expected invariants.', 'A review rubric.', 'Detection and false-positive measures.', 'A statement of what the selected cases cannot support.'],
  contribution='An evaluable review method. Not another generic vulnerability checklist.',
  ethics='No fixture is included on this page. Unpublished attack detail does not belong in the journal record. If people review the fixtures, the study needs a consent process before anyone is recruited. None of that has been written.'),
 dict(slug='sponsorship-without-arbitrary-signing', n=4, section='Payments and applications',
  title='Sponsorship Without Arbitrary Signing',
  subtitle='Designing and testing a restricted transaction fee payer',
  question='Which validation rules are necessary to constrain a sponsor to a defined merchant-payment policy?',
  why='A fee payer that signs what a client describes can be talked into paying for a different transaction than the merchant intended.',
  comparisons=['Permitted transactions specified independently of the client description.', 'Valid, malformed, and adversarial requests.', 'Destination, amount, mint, instruction, fee, expiry, and replay rules.', 'Observed test coverage kept separate from any claim of complete security.'],
  outputs=['A policy specification.', 'A threat model.', 'A transaction corpus.', 'Test results.', 'Residual risks.', 'Operational budget controls.'],
  contribution='A reusable evaluation artifact for sponsored-payment integrations.',
  ethics='No sponsorship service has been built. The study must not use keys that control assets with value. Adversarial requests stay inside the test corpus.'),
 dict(slug='one-token-api', n=5, section='Software engineering',
  title='One Token API, Different Behaviour',
  subtitle='A compatibility evaluation of token-transfer integrations',
  question='Which integration assumptions fail across a defined selection of token configurations?',
  why='Calling two token programmes by one client interface does not make their failure modes the same.',
  comparisons=['A declared set of token programmes and configurations. The set is not chosen yet.', 'Controlled token fixtures.', 'Transfers, balance interpretation, account creation, and error handling.', 'Unsupported cases recorded as unsupported.'],
  outputs=['A compatibility matrix.', 'Test fixtures.', 'Exact versions.', 'Expected behaviour beside observed behaviour.', 'Recommendations that stop at the evidence.'],
  contribution='A maintained test framework for token compatibility.',
  ethics='No fixtures have been built. The matrix must not describe an untested configuration as equivalent to a tested one.'),
 dict(slug='can-learners-explain', n=6, section='Education',
  title='Can Learners Explain What They Just Signed?',
  subtitle='Evaluating transaction understanding in Solana education',
  question='Does a prediction-and-inspection lesson produce better independent understanding than a step-by-step walkthrough?',
  why='A completion tick records that someone followed a step. It does not record that they can explain a different transaction.',
  comparisons=['Two lesson variants aimed at the same material.', 'Eligibility and prior-experience measures, not yet defined.', 'An assessment specified before any response is collected.', 'Comprehension, and performance on a changed scenario.', 'Recruitment, exclusions, attrition, uncertainty, and the consent process.'],
  outputs=['A study protocol detailed enough to follow.', 'Lesson materials.', 'An assessment rubric.', 'Appropriately anonymised results.', 'Analysis code.', 'Threats to validity.'],
  contribution='Evidence about teaching, if the study is run. Completion rates are not that evidence.',
  ethics='No participant has been recruited. No consent form exists. No ethics review is recorded. The study does not start until those exist. This page is not that protocol.'),
 dict(slug='finality-under-named-rules', n=7, section='Protocol and runtime',
  title='Finality Under Named Rules',
  subtitle='A documentary and observational protocol for Solana consensus claims',
  question='When a public design file names a finality, resilience, or round rule, which of those claims can be checked as observations on a named cluster, and which remain only document sentences?',
  why='White papers and SIMDs on the shelf (including Proof of History / Tower wording and Alpenglow versions) supply sentences readers repeat as network facts. A study is useful only if it separates the file’s sentence from a stored cluster observation.',
  comparisons=['Documentary extraction from named shelf files (version pinned).', 'A named cluster and client versions (not chosen).', 'Commitment / vote / slot records the harness can store.', 'Claims that cannot be operationalised, recorded as non-operationalised.', 'Version drift: the same title at v1 vs v1.2 treated as different documents.'],
  outputs=['A claim inventory with document anchors.', 'Operationalisation rules written before any run.', 'Observation tables where a claim was checkable.', 'A residual list of claims that stayed documentary.', 'Threats to validity for both the extraction and the observation arms.'],
  contribution='A method for reading Solana consensus documents without laundering them into cluster measurements.',
  ethics='No validator keys. No mainnet disruption. Devnet or a local validator is the intended setting if the observational arm is ever built. Unpublished attack detail does not belong in the journal record.'),
 dict(slug='fee-and-rent-observation', n=8, section='Payments and applications',
  title='Fee and Rent Observation',
  subtitle='Walking balance changes against displayed costs on Solana workflows',
  question='For a named workflow, which balance changes appear in the records that a displayed fee or rent figure leaves out?',
  why='Shelf documents and product UIs name fees, rent, and compute charges. Users meet the sum of balance changes. The cost sketch is not enough: a protocol needs a fixed workflow and a column for every transfer.',
  comparisons=['A declared workflow (not chosen).', 'Displayed fee or rent figure as the product states it.', 'Full balance-change set across accounts touched.', 'Failed attempts and account-creation transfers as separate lines.', 'Official fee sentences retrieved for the library, cited as documents only.'],
  outputs=['Workflow definition.', 'Balance-change tables.', 'Omitted-cost inventory.', 'Exact program and client versions.', 'Limits of generalisation.'],
  contribution='A reproducible cost audit method for Solana application workflows.',
  ethics='Test assets only. No valuable mainnet funds. No human subjects.'),
 dict(slug='upgrade-bytes-and-disclosure', n=9, section='Security and authority',
  title='Upgrade Bytes and Disclosure',
  subtitle='Comparing loader authorities with what a signer is told',
  question='For named program deployments, does a user-reachable disclosure identify the upgrade authority the loader record names?',
  why='An upgradeable program can change what a prior signature effectively authorised. Marketing “immutable” and loader authorities are different records. Core BPF and loader SIMDs on the shelf supply design language; they are not the observation.',
  comparisons=['On-chain loader/authority reads (method fixed first).', 'User-reachable disclosures (site, docs, explorer text).', 'Programs labelled immutable vs upgradeable.', 'Mismatch cases counted separately from missing disclosures.', 'Documentary priors from upgrade SIMDs, cited as documents.'],
  outputs=['A disclosure rubric.', 'Paired (chain, disclosure) records.', 'Mismatch rates on the chosen set.', 'Exact slot/versions.', 'What the set cannot support.'],
  contribution='An evaluable method for upgrade-authority transparency claims.',
  ethics='Public deployments only. No unpublished exploit detail. No social engineering of authority holders.'),
]
SECTIONS = [
 ('Protocol and runtime', 'What behaviour follows from a particular execution rule or implementation?'),
 ('Transactions and reliability', 'How do submission, confirmation, retry, and recovery behave under stated conditions?'),
 ('Security and authority', 'Which invariants prevent a stated class of failure?'),
 ('Software engineering', 'Which development and testing practices detect a defect that matters?'),
 ('Infrastructure and measurement', 'How do RPC, indexing, networking, and client choices change what is observed?'),
 ('Payments and applications', 'How does a whole system verify, reconcile, and recover a financial operation?'),
 ('Human-computer interaction', 'Can a person tell what they are authorising, and what then happened?'),
 ('Economics and governance', 'What can a specified dataset support about incentives or participation?'),
 ('Education', 'Which teaching approach changes what a learner can do on a new problem?'),
]
def status_panel(kind):
  rows = [
    ('Article type', kind),
    ('Review status', 'Not peer reviewed. No reviewer has been assigned.'),
    ('Received', 'Not established. There is no submission system that records a received date.'),
    ('Revised', 'Not established.'),
    ('Accepted', 'Not established. Nothing has been accepted.'),
    ('Published', '17 Nov 2026, as this page. That date is not an acceptance date.'),
    ('Current version', 'First public text, 17 Nov 2026.'),
    ('Code', 'None.'),
    ('Data', 'None. No observations have been collected.'),
    ('Artifact evaluation', 'Not started.'),
    ('Funding', 'No external funding is recorded for this page.'),
    ('Conflicts', 'No person is named as an author. Sol.College is the publisher and can edit the page.'),
    ('Corrections', 'None.'),
  ]
  body = ''.join(f'<dt>{E(k)}</dt><dd>{E(v)}</dd>' for k, v in rows)
  return f'<section class=status-panel aria-label="Research status"><h2>Research status</h2><dl class=article-meta>{body}</dl></section>'
def crumbs(items):
  parts = ['<a href="/">Home</a>', '<a href="/journal/">Journal</a>']
  parts += items
  return '<nav class=crumbs aria-label=Breadcrumb>' + ' / '.join(parts) + '</nav>'
def shell(kicker, title, lead, body, trail):
  return f'{crumbs(trail)}<article class="lesson jss"><p class=eyebrow>{E(kicker)}</p><h1>{E(title)}</h1><p class=lead>{lead}</p>{body}</article>'
def _lis(items):
  return ''.join(f'<li>{E(x)}</li>' for x in items)
def meta_line(prefix, question):
  """A snippet that stays under 158 characters and keeps the page's limit."""
  full = prefix + question
  if len(full) <= 158:
    return full
  tail = ' No observations have been collected.'
  room = 158 - len(prefix) - len(tail)
  short = question.strip().rstrip('?.')
  if room >= 24:
    short = short[:room].rsplit(' ', 1)[0]
  stop = {'a', 'an', 'the', 'that', 'to', 'of', 'and', 'or', 'for', 'with', 'its', 'their', 'which', 'when', 'than', 'into', 'from', 'by', 'as', 'at', 'on', 'in'}
  while short and short.split()[-1].lower().strip(',;:.') in stop:
    short = short.rsplit(' ', 1)[0]
  short = short.rstrip(' ,;:.')
  text = prefix + short + '.' + tail
  if len(text) > 158:
    raise SystemExit('journal: meta description is over 158 characters')
  return text
def protocol_page(p):
  import journal_depth as depth
  import journal_priors as priors
  extra = depth.DEPTH[p['slug']]
  comps = _lis(p['comparisons'])
  outs = _lis(p['outputs'])
  body = f'''{status_panel('Research protocol. Not a completed study.')}
<p><b>This page is prospective.</b> It states the question, the terms a study would have to fix, and the records it would keep. It does not state a result. No observations have been collected. No number in a later paper may be copied back onto this page unless the study has been run and checked.</p>
<h2>Research question</h2>
<p>{E(p['question'])}</p>
<h2>Why this matters</h2>
<p>{E(p['why'])}</p>
<h2>Terms to fix before any collection</h2>
<p>A later paper that uses these words with a different meaning is not a run of this protocol. The definitions are part of the design. They are not findings.</p>
<ul>{_lis(extra['terms'])}</ul>
<h2>Observation and interpretation</h2>
<p>{E(extra['split'])}</p>
<h2>How the study would be built</h2>
<ul>{_lis(extra['design'])}</ul>
<h2>Comparison conditions</h2>
<p>These are the arms. The sample, the cluster, and the analysis have not been chosen.</p>
<ul>{comps}</ul>
<h2>Illustration, not data</h2>
<p>{E(extra['illustration'])}</p>
<h2>What a negative result would mean</h2>
<p>{E(extra['negative'])}</p>
{priors.priors_html(E, p['slug'])}
<h2>Hypotheses</h2>
<p>Exploratory. No hypothesis is registered. If the study is run without a question fixed first, the write-up stays labelled as exploratory.</p>
<h2>System, sample, and analysis</h2>
<p>Not chosen. Versions, clusters, client libraries, the workload, the exclusions, and the analysis are not established. “Not chosen” is a fact about this page. It is not a suggestion that any convenient choice will do after the data exist.</p>
<h2>Primary outcome</h2>
<p>The question names what a result would have to speak to. No outcome has been measured.</p>
<h2>Ethical and security considerations</h2>
<p>{E(p['ethics'])}</p>
<h2>Expected artifacts</h2>
<ul>{outs}</ul>
<p>An artifact that does not exist is not listed as available. The four labels on the <a href="/journal/methods/#artifacts">methods page</a> stay separate: available, inspected, reproduced, replicated.</p>
<h2>Known threats to validity</h2>
<p>The cases are not selected. Until they are, the study cannot support a claim about Solana applications in general. A result, if one is later published, will be limited to the conditions that were actually run. A clean result on a convenience sample is still a convenience sample.</p>
<h2>What this page is not</h2>
<p>It is not peer-reviewed research. It is not a preprint of findings. The potential contribution, if the work is done carefully, would be: {E(p['contribution'])}</p>
<p><a href="/journal/programme/">Back to the programme</a> · <a href="/journal/methods/">How to read a protocol</a> · <a href="/journal/policies/#integrity">Research integrity</a></p>'''
  title = p['title']
  desc = meta_line('Prospective protocol. ', p['question'])
  html = shell('Protocol · Volume 1 · not started', title, E(p['subtitle']), body, [f'<span>{E(title)}</span>'])
  return p['slug'], title, desc, html
def sketch_page(s):
  import journal_priors as priors
  body = f'''{status_panel('Research sketch. Not a full protocol. Not a completed study.')}
<p><b>This is a sketch.</b> It names the question, the terms, and the records a study would keep. It is not a protocol a team could run tomorrow: the sample, the environment, and the analysis are not specified. No observations have been collected.</p>
<h2>Research question</h2>
<p>{E(s['question'])}</p>
<h2>Why this matters</h2>
<p>{E(s['why'])}</p>
<h2>Terms to fix first</h2>
<ul>{_lis(s['terms'])}</ul>
<h2>Observation and interpretation</h2>
<p>{E(s['split'])}</p>
<h2>Illustration, not data</h2>
<p>{E(s['illustration'])}</p>
<h2>What a negative result would mean</h2>
<p>{E(s['negative'])}</p>
<h2>What is still missing before this is a protocol</h2>
<ul>
<li>A named system, with versions.</li>
<li>A sample or a workload chosen before the run.</li>
<li>Exclusion rules and a primary outcome written tightly enough to score.</li>
<li>An ethics note where people or valuable assets would be involved. Several of these sketches must not recruit anyone until that note exists.</li>
</ul>
{priors.priors_html(E, s['slug'])}
<p>It is not peer-reviewed research. A sketch that sounds specific is still a sketch.</p>
<p><a href="/journal/programme/#sketches">Back to the programme</a> · <a href="/journal/methods/">How to read a protocol</a></p>'''
  title = s['title']
  desc = meta_line('Research sketch, not a study. ', s['question'])
  html = shell('Sketch · not a protocol · not started', title, 'A question with its terms. Not a method a team can run, and not a result.', body, [f'<span>{E(title)}</span>'])
  return s['slug'], title, desc, html
def policies_page():
  body = f'''{status_panel('Journal policy.')}
<p>These are the rules for a journal that has not yet accepted a paper. They bind the pages published now. They are not a claim that a review process is running.</p>
<p>The wording is aimed at the transparency principles published by the Committee on Publication Ethics and the organisations named with them: <a href="{COPE}">Principles of Transparency and Best Practice in Scholarly Publishing</a>. Sol.College is not a member of COPE, and membership is not claimed. The same is true of any indexer or publisher association.</p>
<h2 id=identity>Publisher</h2>
<p>The publisher is Sol.College. Reading is free. There is no submission fee and no publication fee. If a fee is introduced later, it has to be stated before a person submits, including who can ask for a waiver. No fee exists today.</p>
<p>No ISSN, DOI, impact factor, or indexing status is displayed, because none has been assigned. An identifier will be shown only after it is actually issued.</p>
<h2 id=independence>Editorial independence</h2>
<p>Independence is not established. There is no editorial board. No person is listed as an editor, because nobody has agreed to serve. A name will be added only after that person has agreed in terms that can be shown.</p>
<p>Sol.College can edit these pages. That is a conflict to manage, not a reason to pretend the journal is already separate from its publisher. The safeguards that would make “independent” true are not in place yet:</p>
<ul>
<li>Publish who the publisher is and where money comes from. The publisher is Sol.College. No external funder is recorded.</li>
<li>Authors and reviewers disclose relevant interests. There are no named authors or reviewers.</li>
<li>A handling editor with no stake decides when the publisher is a party to the work. No such editor exists.</li>
<li>An author does not decide on their own paper. There is no decision process yet.</li>
<li>A sponsor does not choose the finding or the acceptance. No sponsor is recorded, and no paper has been accepted.</li>
<li>Advertising is separate from research. These pages carry no advertisement.</li>
<li>Criticism of Sol.College is eligible under the same rules as any other submission.</li>
</ul>
<h2 id=review>Peer review</h2>
<p>The process below is the one the journal intends to use for a completed study. It is not operating.</p>
<ol>
<li>Submission.</li>
<li>Screening for scope, ethics, and completeness.</li>
<li>A methods assessment.</li>
<li>Independent subject-matter review. The aim is two qualified reviewers where that is feasible, plus a statistical or security reviewer when the work needs one. Two reviews do not, by themselves, make a result true.</li>
<li>Artifact evaluation when the paper depends on code or data.</li>
<li>Revision and a response.</li>
<li>An editorial decision.</li>
<li>Copyediting and a metadata check.</li>
<li>Publication.</li>
<li>Corrections, argument, and replication after publication.</li>
</ol>
<p>Until reviewers are available, the journal may publish a protocol or a working paper. Either label has to be visible. A protocol is not peer-reviewed research. No working paper is published in this release.</p>
<p>Reviewer reports will not be invented. An automated comment is not an independent expert review. Offering to review, through the public issue tracker, does not appoint anyone.</p>
<h2 id=integrity>Research integrity</h2>
<p>The journal will not publish an invented measurement, a fabricated participant, a fictitious reviewer report, or a manufactured citation. Observations and interpretation stay apart. Exploratory work is labelled exploratory.</p>
<p>A numerical result goes in an abstract only after it exists and has been checked. The protocols and the sketches in this release have no results. An illustration on a protocol page is a writing device. It is not a log.</p>
<h2 id=data>Data and code</h2>
<p>Where a study can share its materials, the package is part of the publication: a readme, an environment manifest, lockfiles, source, build and test instructions, the experiment configuration, the data that can be shared, analysis scripts, expected outputs, known limits, a licence, and checksums or release identifiers.</p>
<p>Four labels stay separate. Artifacts available means the materials can be fetched. Artifacts inspected means a reviewer looked at the documentation. Results reproduced means an independent evaluator got the stated result. Independently replicated means a separate study tested the finding with its own approach. A repository link is not any of the last three.</p>
<p>Privacy, security, or another real restriction is stated. It is not hidden. Nothing in this release has data or code behind it, because nothing has been run.</p>
<h2 id=corrections>Corrections</h2>
<p>A correction is a visible part of the publication, linked from the status panel. This release has no correction. An error on a charter or protocol page can be reported through a public GitHub issue: <a href="{E(CORRECTION)}">report a correction</a>. That tracker is public. Do not put a private key, a recovery phrase, or unpublished vulnerability details in it.</p>
<h2 id=ai>Use of automated tools</h2>
<p>A human author or editor remains responsible. Material help is disclosed, including drafting, translation, code generation, data cleaning, analysis help, literature search, and figures. Citations, code, data transformations, and conclusions are checked by a person.</p>
<p>The journal refuses fabricated sources, synthetic data presented as observation, a reviewer identity or a review that was generated and presented as a person, upload of a confidential submission to an external system without permission, and any description of an automated review as independent expert peer review.</p>
<p>These charter pages were drafted with automated assistance and edited as Sol.College pages. They report no observation.</p>
<h2 id=fees>Fees</h2>
<p>Reading is free. Submission is free. Publication is free. There is no waiver to request, because there is no charge.</p>
<h2 id=submit>How to propose work</h2>
<p>A confidential manuscript system is not operating. Do not send a manuscript that has to stay private. A proposal that can be public uses <a href="{E(PROPOSE)}">this GitHub issue</a>. A person who wants to be considered as a reviewer later uses <a href="{E(REVIEWER)}">this issue</a>. Neither issue starts a review.</p>
<p><a href="/journal/">Back to the journal</a></p>'''
  return shell('Policies', 'How the journal is run',
    'The rules for pages that exist, and the review process that does not yet run.',
    body, ['<span>Policies</span>'])
def call_page():
  body = f'''{status_panel('Call for papers. Not a paper.')}
<blockquote>
<p>The Journal of Solana Studies invites original research into the reliability, security, performance, usability, and operation of Solana systems.</p>
<p>We welcome empirical studies, reproducible systems papers, replication work, negative results, research artifacts, and critical reviews.</p>
<p>Submissions should state a clear research question, explain their methods, distinguish observations from interpretation, and provide the materials necessary to evaluate their claims wherever that is ethically and technically possible.</p>
<p>The founding programme focuses on transaction-state handling, recovery and idempotency, authority boundaries, restricted fee sponsorship, token compatibility, developer education, consensus document claims, fee and rent observation, and upgrade-authority disclosure. Those nine items are protocols on this site. Further questions are sketches. A source-appraisal series reads documents the library already retrieved. None of them is a finding.</p>
<p>The journal does not publish promotional investment material, unsupported performance claims, or work whose conclusion is fixed by a sponsor.</p>
<p>Review status, conflicts, funding, artifact availability, and material limits will be disclosed for every publication. Today those disclosures are: not reviewed, no named author, no external funding, no artifacts, and no completed study.</p>
</blockquote>
<h2>What a proposal needs</h2>
<p>For an empirical study, send a protocol before a conclusion. The protocol names the question, why it matters, the prior evidence, whether the work is a pre-specified test or an exploration, the system, the sample or workload, the comparisons, the primary outcomes, the analysis, the exclusions, the ethical and security limits, the artifacts, and the threats to validity.</p>
<h2 id=submit>Where to send it</h2>
<p>Use <a href="{E(PROPOSE)}">a public GitHub issue</a>. The issue tracker is public. It is not a confidential editorial office. Do not include private keys, recovery phrases, or unpublished vulnerability details. A manuscript that cannot be public has nowhere to go yet, and it should not be pasted here in the hope that it stays private.</p>
<p>No acceptance rate is stated, because no decision has been made.</p>
<p><a href="/journal/programme/">The founding programme</a> · <a href="/journal/policies/">Policies</a></p>'''
  return shell('Call for papers', 'Founding call for papers',
    'Proposals are welcome. A proposal is not a publication, and this call is not a completed study.',
    body, ['<span>Call for papers</span>'])
def programme_page():
  cards = ''.join(
    f'<a class=card href="/journal/protocols/{E(p["slug"])}/"><p class=eyebrow>Protocol {p["n"]} · not started</p><h3>{E(p["title"])}</h3><p>{E(p["question"])}</p></a>'
    for p in PROTOCOLS)
  import journal_depth as depth
  sketches = ''.join(
    f'<a class=card href="/journal/sketches/{E(s["slug"])}/"><p class=eyebrow>Sketch · {E(s["section"])}</p><h3>{E(s["title"])}</h3><p>{E(s["question"])}</p></a>'
    for s in depth.SKETCHES)
  body = f'''{status_panel('Research programme. Not an issue of papers.')}
<p>Volume 1 is the name of this programme: reliability, authority, and evidence. It is not a bound issue. No paper has been accepted into it. The aim is studies that are actually run, not sixty titles. Nine prospective protocols are listed below; each cites retrieved library documents as documentary priors only.</p>
<p>Each protocol below says how a study would have to define its terms and which records it would keep. The sample is still not chosen. No observations have been collected.</p>
<div class=hub-grid>{cards}</div>
<h2 id=sketches>Research sketches</h2>
<p>A sketch is a question with its terms. It is not yet a protocol: the system, the sample, and the analysis are missing. None of them has a result. Several sketches cite the same library shelf as documentary priors.</p>
<div class=hub-grid>{sketches}</div>
<h2 id=appraisals>Source appraisals</h2>
<p>The <a href="/journal/notes/">appraisal series</a> applies one instrument to every document the library retrieved on 17 Nov 2026. An appraisal quotes the catalogue’s stored sentences and says what a citation may not infer. It is not a line-by-line review, and it is not a study that was run. Consensus, fee, upgrade, and related files now point at the matching open protocols where a later study could cite them.</p>
<p><a href="/journal/methods/">How to read a protocol</a> · <a href="/journal/call/">Call for papers</a></p>'''
  return shell('Volume 1', 'Reliability, authority, and evidence',
    'Nine prospective protocols and research sketches. None has been run.',
    body, ['<span>Programme</span>'])
def home_page():
  kinds = [
    ('Library record', 'Help someone find a resource', 'The description matches the resource.'),
    ('Educational article', 'Explain a concept or a method', 'Clear, correct, and useful. The articles on this site are this kind of page.'),
    ('Guided lesson', 'Develop a skill', 'A person can do the thing the lesson names. A tick is not understanding.'),
    ('Journal paper', 'Investigate a stated question', 'A method, evidence, analysis, and limits. None is published yet.'),
    ('Editorial or perspective', 'Make an argument', 'The argument is marked as an argument. None is published yet.'),
  ]
  kind_rows = ''.join(f'<tr><td>{E(a)}</td><td>{E(b)}</td><td>{E(c)}</td></tr>' for a, b, c in kinds)
  cards = ''.join(
    f'<a class=card href="/journal/protocols/{E(p["slug"])}/"><p class=eyebrow>Protocol {p["n"]} · {E(p["section"])}</p><h3>{E(p["title"])}</h3><p>{E(p["question"])}</p></a>'
    for p in PROTOCOLS)
  sections = ''.join(f'<tr><td>{E(n)}</td><td>{E(q)}</td><td>No publication yet.</td></tr>' for n, q in SECTIONS)
  bib = '''@misc{solcollege2026jsscharter,
  title = {Journal of Solana Studies: founding charter},
  author = {{Sol.College}},
  year = {2026},
  url = {https://sol.college/journal/},
  note = {Charter, policies, and prospective protocols. No research paper is included.}
}'''
  body = f'''<p>The Journal of Solana Studies publishes original research into Solana’s technology, applications, infrastructure, security, economics, and human use.</p>
<p>Reproducible experiments, systems research, replication studies, negative results, and critical investigations are in scope. The purpose is to improve understanding. It is not to promote a token, a project, or a conclusion chosen in advance.</p>
<p>Every publication is supposed to state what was investigated, how the evidence was obtained, what the evidence supports, and what remains uncertain. The pages in this release cannot do the middle two of those, because no study has been run.</p>
<aside class=status-panel>
<p><b>What this release contains.</b> The charter, the policies, the call for papers, a methods note, nine prospective protocols with documentary priors from the Solana Library shelf, research sketches, and a source-appraisal series over documents the library retrieved. No research paper has been published. No peer review has been conducted. No editor is named. Editorial independence is not established: Sol.College is the publisher and the only party that can change these pages.</p>
</aside>
<p class=cta><a class=btn href="/journal/programme/">Read the protocols</a> <a class="btn ghost" href="/journal/call/#submit">Submit a proposal</a></p>
<h2>How a journal paper differs</h2>
<p>A long tutorial is not research. A technical article is not peer reviewed. This journal is meant to publish fewer pieces than the articles list, and to require more evidence from each one. The articles list is at <a href="/articles/">Articles</a>. Practice is at <a href="/lessons/">Lessons</a>. Finding a source belongs in the <a href="/library/">Solana Library</a>. Reporting of what is happening belongs in <a href="/degen/">The Degen</a>.</p>
<table><thead><tr><th>Publication</th><th>Purpose</th><th>Standard</th></tr></thead><tbody>{kind_rows}</tbody></table>
<h2 id=latest>Latest publications</h2>
<p>There are no completed publications. A protocol is not a paper. A source appraisal is not a paper. Review status for each item below is: not peer reviewed. The <a href="/journal/notes/">appraisal series</a> is a reading of retrieved documents, not a results issue.</p>
<div class=hub-grid>{cards}</div>
<h2 id=programme>Current research programme</h2>
<p><a href="/journal/programme/">Reliability, authority, and evidence</a>. Nine protocols (including finality under named rules, fee and rent observation, and upgrade disclosure), research sketches, and <a href="/journal/notes/">source appraisals</a> of retrieved documents. No data. <a href="/journal/methods/">How to read them</a>.</p>
<h2 id=scope>Scope</h2>
<p>Sections open when there is a credible study and someone competent to review it. Opening a row here does not open a section.</p>
<table><thead><tr><th>Section</th><th>The sort of question</th><th>Publications</th></tr></thead><tbody>{sections}</tbody></table>
<h2 id=policies>Journal policies</h2>
<ul>
<li><a href="/journal/policies/#independence">Editorial independence</a></li>
<li><a href="/journal/policies/#review">Peer review</a></li>
<li><a href="/journal/policies/#integrity">Research integrity</a></li>
<li><a href="/journal/policies/#data">Data and code</a></li>
<li><a href="/journal/policies/#corrections">Corrections</a></li>
<li><a href="/journal/policies/#ai">Automated tools</a></li>
<li><a href="/journal/policies/#fees">Fees</a></li>
<li><a href="/journal/methods/">How to read a protocol</a></li>
<li><a href="/journal/call/">Founding call for papers</a></li>
<li><a href="/journal/notes/">Source appraisals</a></li>
</ul>
<h2>Citation</h2>
<p>There is no DOI. This citation is for the charter, not for a research finding.</p>
<pre class=sh><code>{E(bib)}</code></pre>'''
  return shell('JSS · Published by Sol.College', 'Journal of Solana Studies',
    'Advance understanding of Solana through evidence that others can inspect, question, and reproduce.',
    body, [])
def methods_page():
  body = f'''{status_panel('Methods note. Not a study.')}
<p>This page is how to read the rest of the journal. It is not a result, and it is not a textbook of the Solana protocol. No observations have been collected.</p>
<h2>What a protocol is for</h2>
<p>A protocol is a promise about the records a study will keep, written before those records exist. It fixes the words, the comparison, and the difference between a stored response and a sentence about that response. A protocol that is written after the numbers is a description of a result, and this journal would label it as one.</p>
<p>The nine founding protocols are detailed enough to argue with. They cite retrieved library documents as priors, not as results. They are not detailed enough to run: versions, samples, and analyses are deliberately still open, and the page says so. Filling those blanks after seeing the data would be a different study.</p>
<h2>What a sketch is for</h2>
<p>A sketch holds the question and the terms so the question does not get replaced by a vaguer one later. It is missing the sample, the system, and the scoring rule. Treating a sketch as a method is the mistake the label is there to prevent.</p>
<h2>Observation and interpretation</h2>
<p>An observation is a record the harness stored: bytes, a signature status, an account read, a reviewer’s mark on a fixture whose expected answer was written first, a learner’s answer against a rubric. An interpretation is a sentence that says what those records mean. The journal keeps them in different paragraphs because the sentence can be wrong while the record is intact, and the record can be missing while the sentence sounds finished.</p>
<p>An illustration on a protocol page is neither. It is a picture used to show which two columns the study would need. It is not a log from a cluster, and it must not be quoted as one.</p>
<h2 id=artifacts>Four artifact labels</h2>
<p>These words are not synonyms.</p>
<ul>
<li><b>Available.</b> A reader can fetch the materials.</li>
<li><b>Inspected.</b> A reviewer looked at the documentation and says what they looked at.</li>
<li><b>Reproduced.</b> An independent evaluator got the stated result from those materials.</li>
<li><b>Replicated.</b> A separate study tested the finding with its own approach.</li>
</ul>
<p>A repository link is only a candidate for the first. Nothing in this release has any of the four, because nothing has been run.</p>
<h2>What this journal will not count</h2>
<ul>
<li>A completion tick, as evidence a person understood a different transaction.</li>
<li>A function name, as evidence of who can move an asset.</li>
<li>A client’s success callback, as evidence a payment settled.</li>
<li>A second signature, as evidence a second business act was intended, or that it was not.</li>
<li>A SIMD number mentioned on a docs page, as evidence the change is active. The <a href="/library/">library</a> states the same limit on the SIMD repository.</li>
<li>A benchmark number without the workload, as a measurement.</li>
</ul>
<h2>Where the neighbouring publications stop</h2>
<p>The <a href="/library/">library</a> points at sources. The <a href="/articles/">articles</a> explain a recorded case. The <a href="/degen/">Degen</a> is for reporting and argument about what is happening. A journal page that wants to be news, or a news page that wants to be a study, has to move. This release has no study and no report.</p>
<h2>What a source appraisal is for</h2>
<p>An appraisal takes one library record retrieved on 17 Nov 2026 and states the estimand that record can support: a claim about what the file says, on the sentences the catalogue stored. It copies a SIMD status when the file prints one, and it leaves that word as a label. Activated, Accepted, and Implemented are not recoded into a cluster observation, and Review is not this journal’s peer review. The series is indexed at <a href="/journal/notes/">source appraisals</a>. No appraisal collected an observation.</p>
<p><a href="/journal/programme/">The programme</a> · <a href="/journal/policies/">Policies</a></p>'''
  return shell('Methods', 'How to read a protocol',
    'Terms, records, and the difference between an illustration and a result.',
    body, ['<span>Methods</span>'])
def ld(title, desc, path):
  return {'@context': 'https://schema.org', '@type': 'WebPage', 'headline': title, 'description': desc,
    'datePublished': PUBLISHED, 'dateModified': PUBLISHED,
    'publisher': {'@type': 'Organization', 'name': 'Sol.College', 'url': SITE + '/'},
    'mainEntityOfPage': SITE + path}
def write_page(S, page, css, path, title, desc, main, data):
  doc_title = title + (' | Sol.College' if title == 'Journal of Solana Studies' else ' | Journal of Solana Studies')
  html_page = page(css + main, doc_title, desc, path)
  blob = json.dumps(data, ensure_ascii=False).replace('</', '<\\/')
  html_page = html_page.replace('</head>', '<script type="application/ld+json">' + blob + '</script></head>', 1)
  if '<h1>' not in html_page:
    raise SystemExit('journal: missing h1 ' + path)
  os.makedirs(os.path.dirname(f'{S}{path}index.html'), exist_ok=True)
  open(f'{S}{path}index.html', 'w').write(html_page)
def write(S, page, css):
  pages = []
  home = home_page()
  desc = 'Journal of Solana Studies: charter, protocols, sketches, and appraisals of retrieved documents. No study is complete and nothing is peer reviewed.'
  write_page(S, page, css, '/journal/', 'Journal of Solana Studies', desc, home, ld('Journal of Solana Studies', desc, '/journal/'))
  pages.append(('/journal/', 'Journal of Solana Studies', desc))
  pol = policies_page()
  pdesc = 'Publisher, independence, review, integrity, data, corrections, automated tools, and fees. The review process is not operating.'
  write_page(S, page, css, '/journal/policies/', 'Journal policies', pdesc, pol, ld('Journal policies', pdesc, '/journal/policies/'))
  pages.append(('/journal/policies/', 'Journal policies', pdesc))
  call = call_page()
  cdesc = 'Founding call for papers. Proposals that can be public go to a GitHub issue. Confidential manuscripts are not accepted, because no private system exists.'
  write_page(S, page, css, '/journal/call/', 'Founding call for papers', cdesc, call, ld('Founding call for papers', cdesc, '/journal/call/'))
  pages.append(('/journal/call/', 'Founding call for papers', cdesc))
  prog = programme_page()
  gdesc = 'Volume 1 proposes nine studies of reliability, authority, consensus claims, and evidence. None has been run.'
  write_page(S, page, css, '/journal/programme/', 'Reliability, authority, and evidence', gdesc, prog, ld('Reliability, authority, and evidence', gdesc, '/journal/programme/'))
  pages.append(('/journal/programme/', 'Reliability, authority, and evidence', gdesc))
  import journal_depth as depth
  meth = methods_page()
  mdesc = 'How to read a Journal of Solana Studies protocol: terms, records, illustrations, and the four artifact labels. No study has been run.'
  write_page(S, page, css, '/journal/methods/', 'How to read a protocol', mdesc, meth, ld('How to read a protocol', mdesc, '/journal/methods/'))
  pages.append(('/journal/methods/', 'How to read a protocol', mdesc))
  for s in depth.SKETCHES:
    slug, title, pdesc, html = sketch_page(s)
    path = f'/journal/sketches/{slug}/'
    write_page(S, page, css, path, title, pdesc, html, ld(title, pdesc, path))
    pages.append((path, title, pdesc))
  for p in PROTOCOLS:
    slug, title, pdesc, html = protocol_page(p)
    path = f'/journal/protocols/{slug}/'
    write_page(S, page, css, path, title, pdesc, html, ld(title, pdesc, path))
    pages.append((path, title, pdesc))
  import journal_appraisals as appraisals
  for path, title, pdesc, html in appraisals.pages():
    write_page(S, page, css, path, title, pdesc, html, ld(title, pdesc, path))
    pages.append((path, title, pdesc))
  # The generated pages must not look like finished research.
  for path, _t, _d in pages:
    text = open(f'{S}{path}index.html').read()
    if 'No observations have been collected.' not in text and path != '/journal/':
      if path not in ('/journal/policies/', '/journal/call/', '/journal/programme/'):
        raise SystemExit('journal: protocol missing the empty-data line ' + path)
    if re.search(r'peer-reviewed research', text, re.I) and 'not peer-reviewed research' not in text.lower() and 'Not peer reviewed' not in text:
      raise SystemExit('journal: peer-review claim ' + path)
    for banned in ('impact factor', 'ISSN ', ' doi:'):
      if banned.lower() in text.lower() and 'none has been assigned' not in text.lower() and 'no doi' not in text.lower() and 'no issn' not in text.lower():
        raise SystemExit('journal: credential language ' + path + ' ' + banned)
  home_text = open(f'{S}/journal/index.html').read()
  if 'No research paper has been published.' not in home_text:
    raise SystemExit('journal: homepage overclaims')
  if home_text.lower().count('not peer reviewed') < 1:
    raise SystemExit('journal: homepage review status missing')
  llms = f'{S}/llms.txt'
  if os.path.exists(llms):
    block = '\n## Journal\n' + ''.join(f'- [{t}]({SITE}{p}): {d}\n' for p, t, d in pages)
    text = re.sub(r'\n## Journal\n.*?(?=\n## |\Z)', '', open(llms).read(), flags=re.S)
    open(llms, 'w').write(text.rstrip() + '\n' + block)
  print('journal:', len(pages), 'pages')
  return [p for p, _t, _d in pages]
