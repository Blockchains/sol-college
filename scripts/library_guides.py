"""Reading guides for The Solana Library.

Each guide teaches only distinctions already in the catalogue. It does not add a measurement.
A figure quoted from an official page is attributed to that page and was not remeasured here.
"""

GUIDES = [
 dict(slug='first-week', title='First week with Solana',
  question='Where do I start without pretending I have learned the whole system?',
  paras=[
   'Start with a map, then one distinction you can check, then one practice that the site has actually recorded. The official learning hub is a set of short introductions. The core-concepts page is the developer map: accounts, programs, instructions, transactions, fees, program-derived addresses, and cross-program calls. Those are different shelves. The learning hub is not a substitute for the concept index, and the concept index was not re-tested by running its examples.',
   'The distinction worth learning in the first week is the one in the address article and the token documentation. An address is not a wallet. A mint, a token account, and the wallet that is allowed to move the tokens are three different things. The official token page draws that distinction. The Sol.College article on addresses draws the related one. Neither page is a review of every wallet.',
   'Practice, when you want it, is a guided lesson on an app whose core flow the site recorded as working. The learning path lists those lessons. A tick stored in the browser means a step was checked on that machine. It does not mean you can explain a different transaction. The education sketch in the journal exists because that gap is a research question, not because the library has measured it.',
   'Do not treat the core-concepts page’s fee line as a fresh measurement. The page states a base fee of 5,000 lamports per signature. Sol.College has not remeasured the fee schedule for the catalogue. A SIMD number mentioned in a note on that page is not evidence the change is active.',
  ],
  next=[('ext-learn', 'Official learning hub'), ('ext-core', 'Core concepts'), ('art-address', 'An address is not a wallet'), ('lessons-path', 'Learning path')]),
 dict(slug='backend', title='A backend developer’s first shelf',
  question='Which records exist for someone who already knows queues, databases, and retries?',
  paras=[
   'The shelf is thin on purpose. There is no catalogue record yet for a queue, a database, or an idempotent worker. The pages named in the payments plan were not retrieved, so they are not holdings. What exists is how a transaction is read, how this site’s own evidence ledger is organised, and the official description of a transaction.',
   'The useful distinction is the one the journal’s second protocol is built around, and it is still only a protocol. Rebroadcasting a signed transaction and repeating a business operation are different acts. A backend that stores “we sent it” has not stored “the invoice was fulfilled once”. The library does not have a worked worker implementation. It has the transaction page, which says instructions in a transaction succeed or fail together, and the article that shows how this site reads a transaction.',
   'Expiry is the other distinction. The official transaction page says a recent blockhash is valid for 150 slots. The landing guide is the page about retries and lastValidBlockHeight. Those sentences are the pages’ statements. They were not remeasured here. A backend design that treats “the HTTP call returned” as “the payment settled” has left the catalogue’s transaction records and started making an assumption the records do not support.',
   'The testing and deploy guides on this site say what was run and what was not. Read the limitation on the card before copying a command into a clean machine. The install page says version numbers change. The installer was not run for the catalogue.',
  ],
  next=[('art-read-tx', 'How a transaction is read'), ('ext-transactions', 'Official transaction page'), ('ext-landing', 'Landing and retries'), ('guide-testing', 'Testing guide')]),
 dict(slug='rust', title='Rust and program development',
  question='What can you compile from this shelf, and what has this site actually built?',
  paras=[
   'The program shelf is a pixel account used as a program-derived address, a hosted escrow, one recorded build, and the Anchor documentation. Those are four different kinds of page. The pixel article is an explanation of one account. The escrow lesson is practice on a fork this site deployed. The build article records a build that was run, and it was not re-run for the catalogue. The Anchor pages are source-checked references: the destination was read, the examples were not run.',
   'A program-derived address is an address a program can sign for, derived from seeds. The article’s job is that mechanism in one account, not a survey of every program. Cross-program calls are on the core-concepts map. The catalogue does not claim a measured depth limit. A note on the concepts page mentions a SIMD in connection with depth. That mention is not activation evidence.',
   'The source library under /explore/ is generated walkthroughs of forks that have not been deployed. One index record covers the set. Do not count each walkthrough as a curated holding, and do not treat one as a lesson. A lesson is an app whose status the lesson page records.',
   'Before you copy an install command, read the limitation. The official install page describes an installer and says versions change. This catalogue did not run it. A command in a guide is not a clean-machine result unless the guide says the command was run and quotes the result.',
  ],
  next=[('art-pda', 'A PDA, from one pixel account'), ('lesson-gifter-escrow', 'Gifter lesson'), ('art-build', 'The recorded build'), ('ext-anchor', 'Anchor documentation')]),
 dict(slug='frontend', title='Frontend and wallet UX',
  question='What does this shelf actually say about a signature on a screen?',
  paras=[
   'There is no separate wallet-UX study in the catalogue. The lesson guide says when a wallet is required: only a step that sends a transaction needs one, and the site does not custody keys. Picassol is a recorded interface transaction, which means the lesson has a signature it can point at. That is a narrower fact than “wallet UX is solved”.',
   'The gap a reader keeps running into is the gap between the label on a button and the status of a signature. The journal’s first protocol is about that gap. It has not been run. The library’s transaction records are the official model: instructions succeed or fail together, and a blockhash expires. They are not a component library.',
   'The official learning hub has a wallet introduction among its short pages. Those introductions were not opened one by one for the catalogue. Linking the hub is not a review of each introduction.',
   'A completion tick in a lesson is stored in the browser. It is not a measure of whether a person can explain a second transaction. The educator’s room says the same thing, because it is a limit of the records and not a style choice.',
  ],
  next=[('lessons-guide', 'How to use a lesson'), ('lesson-picassol-hackathon', 'Picassol lesson'), ('ext-learn', 'Official learning hub'), ('gloss', 'Glossary')]),
 dict(slug='payments', title='Payments and commerce',
  question='What can you verify from this shelf, given that the payments docs were not retrieved?',
  paras=[
   'The collection plan named official payments pages. They were not retrieved, so they are not records. The shelf that remains is about inclusion and expiry, not about an invoice, a settlement file, or a reconciliation job. Using it as a payments integration guide would overclaim the holdings.',
   'What the shelf can teach is the difference between a submitted transaction and a settled one, and the difference between a displayed fee and a balance change. The official transaction page describes atomic execution and a blockhash lifetime of 150 slots, as that page’s statement. The landing guide discusses retries, priority fees, and public RPC limits. Sample clients on that guide were not run. Dollar figures on that page were not checked.',
   'The token records are the other half of a payment, and only the half that defines accounts. A mint, a token account, and the authority that may move the tokens are different. The article that follows one token balance is the Sol.College page that measures a case. The official token page is the reference. They are not the same record, and the library keeps both so a reader can see which sentences were run and which were only read.',
   'A sponsor that pays a fee for someone else is a journal protocol, not a library holding. No such sponsor has been built. The protocol’s point, which the library does not demonstrate, is that a fee payer who signs whatever the client describes can be asked to pay for a different transaction than the one the merchant meant.',
  ],
  next=[('ext-landing', 'Transaction landing'), ('ext-transactions', 'Transactions'), ('art-balance', 'Follow one token balance'), ('art-read-tx', 'Read a transaction')]),
 dict(slug='security', title='Security and review',
  question='Which questions can you ask with these records, and which investigations are not here?',
  paras=[
   'The security checklist is a list of questions. It is not a finding that any program passed or failed them. The escrow article is one recorded failure of a take, on a practice fork, with the limits that article states. It is not an exploit write-up, and it is not a claim about the original project’s production system. The case-study article records an opened pull request. It does not record a passing test and it does not record a merge.',
   'A technically reproduced example is a named run in a documented environment. The label does not mean a security review. The maintenance policy says that in a table, because the two phrases get conflated.',
   'Authority is the question the journal’s third protocol wants a method for: who can move the funds, drawn as a graph, compared with a function-by-function reading. No fixture is on that page. Unpublished attack detail does not belong in the journal record, and it does not belong in this guide either. If you need a vulnerability write-up, this shelf does not contain one.',
   'The source library’s undeployed walkthroughs are not evidence about a deployed program. The live-apps ledger is the deployment record for hosted devnet apps. A functional mark there is the deployment record. It is not a fresh run for this catalogue and not a statement that the program is safe.',
  ],
  next=[('guide-security-checklist', 'Security checklist'), ('art-take-failed', 'Why a take aborted'), ('art-case', 'The opened pull request'), ('live-index', 'Live apps ledger')]),
 dict(slug='validator', title='Validator and infrastructure',
  question='Where does the official site send an operator, and what has Sol.College not done?',
  paras=[
   'The network hub is a map. It routes to validator docs, RPC providers, explorers, status, and reports. Sol.College has not operated a validator. The child pages were not opened for this catalogue. A link on the hub is not a reviewed provider, and it is not a recommendation.',
   'The developer-resources page lists the kinds of tool the collection plan asked for, including RPC references and an AI-tools heading. Child tools were not opened. A directory entry is not a review of the product.',
   'Anything about performance belongs under the journal’s benchmark sketch until a write-up states the workload, the hardware, the client, and the failure rule. This guide will not repeat a transactions-per-second figure, because the catalogue does not contain one it has checked.',
   'If you came here to run a validator today, the honest next step is the official hub, with the limit above kept visible. This library is not an operations manual.',
  ],
  next=[('ext-network', 'Network hub'), ('ext-tools', 'Developer resources')]),
 dict(slug='research', title='Research and protocol changes',
  question='What does a SIMD record establish, and what does a mention of a SIMD number not establish?',
  paras=[
   'The Solana Improvement Documents repository holds proposed and accepted changes. Each proposal file that was retrieved has its own page. The status on that page is the label in that file. It is not a Sol.College observation that a cluster is running the change. SIMD-0326’s own front matter says its status is Review.',
   'A docs page can mention a SIMD number in a note, as the core-concepts page does for CPI depth and the transaction page does for a limit. A mention is not evidence the change is active. The journal’s methods page repeats this rule so a protocol cannot smuggle an activation claim in through a citation.',
   'Project white papers that were retrieved are a separate shelf, at the white paper catalogue. A page there is a reading note: the title, the version, and what the opening says the document is for. It is not a copy of the paper and not a literature review. The journal is where a question becomes a study, if one is ever run.',
   'Historical behaviour of the network is a subject with no record yet. Past failures that still matter are described inside current articles, on purpose, rather than filed as a retired document. Nothing in the catalogue is marked Replaced.',
  ],
  next=[('ext-simd', 'SIMD repository'), ('paper-solana-whitepaper', 'Solana white paper'), ('paper-alpenglow-v1-1', 'Alpenglow v1.1'), ('ext-core', 'Core concepts')]),
 dict(slug='agents', title='AI and agents',
  question='What is actually on the shelf for someone building an agent?',
  paras=[
   'The developer-resources page has an AI-tools heading. The child pages were not opened. Article titles 113 to 116 in the articles plan have no page. There is no catalogue record that evaluates an agent’s permissions, and there is no record of an agent that was run for this library.',
   'The nearest rigorous question is the journal sketch on generated patches: which checks detect an error that a plausible, compiling diff introduces. No model was run for that sketch, and no vulnerable patch is printed there. Fluency is not one of the checks.',
   'A campus room for a project is a listing in the public room list. It is not an evaluation of the agent’s work. Paused, where the campus uses that word, means that project’s CTO agent is not producing work. It does not mean the practice app is unavailable. That distinction is on the campus record, and this guide does not add a second one.',
   'If you need a permission model, start from the security checklist’s questions and the authority protocol’s terms. Neither is an agent framework. Saying so here is the point of a thin shelf: the absence is part of the guide.',
  ],
  next=[('ext-tools', 'Developer resources'), ('art-index', 'Articles index'), ('guide-security-checklist', 'Security checklist')]),
 dict(slug='educator', title='Teaching from these records',
  question='What can a teacher claim a learner has done, using only the records this site keeps?',
  paras=[
   'A guided lesson is a written walkthrough of an app recorded as working. A debug challenge is deployed, and a core flow does not complete. A preview has no teaching sequence. The lesson index separates those three. Teaching them as one “course completed” statistic would erase the distinction the catalogue exists to keep.',
   'A tick is stored in this browser under the lesson’s own key. It means the step was checked here. It does not mean the learner can explain a different transaction, name an account, or predict a failure. The journal protocol “Can Learners Explain What They Just Signed?” is the proposed study of that difference. No learner has been recruited. No consent form exists. A teacher should not describe this site as having measured learning.',
   'The path order is a practice order for the guided lessons. It is not a prerequisite graph of the whole protocol. The glossary is one glossary, not a set of holdings. Article hubs are not articles. The counting rules on the maintenance page exist so a syllabus does not inflate the shelf.',
   'Assessment material that would be fair to grade against is not in the library. A rubric written after the answers is not in the journal either. The protocol says the rubric would have to be fixed first. Until that happens, the honest classroom claim is: the student followed a recorded lesson, or they did not.',
  ],
  next=[('lessons-guide', 'How to use a lesson'), ('lessons-path', 'Learning path'), ('lessons-index', 'Lesson index'), ('gloss', 'Glossary')]),
]


def deepen_guides(guides):
  """Triple guide depth without adding measurements or unretrieved pages."""
  out = []
  for g in guides:
    g = dict(g)
    paras = list(g['paras'])
    title = g['title']
    question = g['question']
    next_ids = ', '.join(n for n, _ in g.get('next') or [])
    paras.append(
      'How this guide stays honest about “%s”: every distinction above is already on a catalogue page, a journal protocol, or an official URL the library retrieved. '
      'The guide does not add a fee schedule, a TPS figure, or a deployment the records do not contain. '
      'If a syllabus needs a claim stronger than those records, the claim has to wait for a page that stores it.'
      % title
    )
    paras.append(
      'The question this guide answers is only: %s '
      'A different question — “is the network safe?”, “which wallet is best?”, “will this yield hold?” — is outside the holdings named above. '
      'Pointing at the next links is not an endorsement of every sentence on those destinations; it is a map of what was filed.'
      % question
    )
    paras.append(
      'Teaching or building from this guide means keeping the same limits on the card the learner sees. A completion tick, a copied command, or a mentioned SIMD number does not become a measurement because a guide paragraph repeated it. '
      'Related catalogue ids named for the next step include: %s. Each id still has its own page and its own limitation line.'
      % (next_ids or 'none stored')
    )
    paras.append(
      'What this guide refuses: inventing a payments doc that was not retrieved, treating /explore/ walkthroughs as lessons, treating a white-paper reading note as a literature review, and treating a campus “paused” label as a story about students. '
      'Those refusals are the same refusals the maintenance policy and the journal methods page already print. The guide exists to put them in one shelf-sized path, not to soften them.'
    )
    g['paras'] = paras
    out.append(g)
  return out

GUIDES = deepen_guides(GUIDES)
