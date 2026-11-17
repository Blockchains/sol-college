"""White papers and design notes in the Solana Library.

A page exists only for a document that was retrieved on 17 Nov 2026.
Every retrieved white paper, litepaper, language edition, design note,
design proposal, SIMD, and regulatory disclosure carries a full
section-by-section reading of the retrieved file. That reading is original
prose. It is not a verbatim copy of the paper, and a figure in the paper is
not a Sol.College measurement.
"""
import html, json, os, re, unicodedata, urllib.parse
CHECKED = '2026-11-17'
ISSUE = 'https://github.com/Blockchains/sol-college/issues/new'
READING_DIR = os.path.join(os.path.dirname(__file__), 'paper_readings')
READING_TYPES = ('White paper', 'Litepaper', 'Language edition', 'Design note', 'Design proposal', 'SIMD', 'Regulatory disclosure')

def E(s):
  return html.escape(str(s if s is not None else ''), quote=True)

def slugify(title):
  s = unicodedata.normalize('NFKD', str(title))
  s = s.encode('ascii', 'ignore').decode().lower()
  s = re.sub(r'[^a-z0-9]+', '-', s).strip('-')
  return re.sub(r'-{2,}', '-', s)[:90].strip('-')

def _paper(**kw):
  legacy = kw.pop('legacy', None)
  stable = kw.pop('stable_id', None)
  outline = kw.pop('outline', None) or []
  row = dict(version='Not stated on the pages read', date='Not stated on the pages read',
    authors='Not named in the file', language='English', topics=[], names_solana=True,
    related=[], bytes=None)
  row.update(kw)
  if not re.fullmatch(r'[a-z0-9-]+', row['slug']):
    raise SystemExit('paper: bad slug ' + row['slug'])
  row['id'] = stable or ('paper-' + row['slug'])
  row['legacy'] = legacy
  row['outline'] = [str(h) for h in outline][:30]
  row['path'] = '/library/papers/' + row['slug'] + '/'
  if len(row['desc']) > 158:
    raise SystemExit('paper: description over 158 ' + row['slug'] + ' ' + str(len(row['desc'])))
  if not re.search(r'\b(not|no|never)\b', row['desc'], re.I):
    raise SystemExit('paper: description has no limit ' + row['slug'])
  return row

WORM = 'https://github.com/wormhole-foundation/wormhole/blob/main/whitepapers/'
# (file, slug, title, nbytes, names Solana, what it says, how it talks about Solana, keywords)
WORMS = [
 ('0001_generic_message_passing.md', 'wormhole-generic-message-passing', 'Generic message passing', 20368, True,
  'The file’s objective is to make Wormhole a generic cross-chain messaging protocol and to take application-specific behaviour out of the core.',
  'The opening says the original design moved messages between Solana and Ethereum, and a later section discusses a Solana consistency level.',
  'Wormhole VAA generic messaging Solana Ethereum'),
 ('0002_governance_messaging.md', 'wormhole-governance-messaging', 'Governance messaging', 2411, True,
  'The file describes governance decisions being carried as Wormhole messages.',
  'It says governance happens in a smart contract on Solana, and that this contract passes finalized decisions on as VAAs. The contract itself is marked “to be specified”.',
  'Wormhole governance Solana VAA'),
 ('0003_token_bridge.md', 'wormhole-token-bridge', 'Token bridge', 24820, True,
  'The file describes a token bridge: assets are locked or burned on a source chain, and a message allows minting or unlocking on a destination chain.',
  'It names SPL on Solana next to ERC-20 on Ethereum, and discusses a paused-state check on both.',
  'Wormhole token bridge SPL ERC-20 Portal'),
 ('0004_message_publishing.md', 'wormhole-message-publishing', 'Message publishing', 5100, True,
  'The file describes how a contract publishes a Wormhole message and how a fee can be claimed.',
  'It says protocol fees are collected in a fee pool on Solana, and it treats a Solana program-derived address as one way to authorize a sender.',
  'Wormhole message publishing fee pool PDA Solana'),
 ('0005_data_availability.md', 'wormhole-data-availability', 'Data availability', 13601, True,
  'The file proposes that guardians gossip signed VAAs and store them locally, instead of racing to write the signed VAA into one chain.',
  'It says Wormhole v1 used Solana for that storage, and it gives a Solana outage as a reason transfers between other chains could stall.',
  'Wormhole data availability VAA Solana gossip'),
 ('0006_nft_bridge.md', 'wormhole-nft-bridge', 'NFT bridge', 7547, True,
  'The file describes moving NFTs across chains and the metadata standards that differ by chain.',
  'It names Metaplex SPL metadata as the Solana case, and a token-id width difference with Ethereum.',
  'Wormhole NFT bridge Metaplex Solana'),
 ('0007_governor.md', 'wormhole-governor', 'Governor', 16984, True,
  'The objective is to let guardians delay token-bridge messages when the aggregate notional value is extraordinarily large.',
  'The background cites Wormhole’s own 2 February 2022 incident report of a Solana contract bug used to mint wrapped ETH. This catalogue did not re-investigate that incident.',
  'Wormhole governor rate limit Solana incident'),
 ('0009_guardian_signer.md', 'wormhole-guardian-signer', 'Guardian signer', 3141, False,
  'The objective is to sign payloads so guardians can attest to events and identify themselves.',
  'The file does not contain the word Solana. It sits in the same whitepapers directory as files that do.',
  'Wormhole guardian signer attestation'),
 ('0010_integrity_checkers.md', 'wormhole-integrity-checkers', 'Integrity checkers', 4075, False,
  'The file describes Wormchain contracts that can block a cross-chain message after checking synchronized state, and that cannot create or modify the message.',
  'The file does not contain the word Solana.',
  'Wormhole integrity checker Wormchain'),
 ('0011_accountant.md', 'wormhole-global-accountant', 'Global accountant', 21930, True,
  'The objective is to limit, for registered token bridges, how many wrapped tokens can leave a chain relative to what was sent in, even if that chain is compromised.',
  'The examples move SOL between Solana and other chains. They are design examples, not measured balances.',
  'Wormhole accountant wrapped SOL Solana'),
 ('0012_ibc_generic_messaging.md', 'wormhole-ibc-messaging', 'IBC generic message emission', 8517, False,
  'The objective is to let guardians support IBC-enabled chains by running a Wormchain node rather than a full node for every chain.',
  'The file does not contain the word Solana.',
  'Wormhole IBC Wormchain guardian'),
 ('0013_ccq.md', 'wormhole-cross-chain-queries', 'Cross-chain queries', 26706, True,
  'The file proposes a way to pull an attestation about a connected chain, instead of only pushing messages. It says the initial release takes off-chain requests.',
  'It says the February 2024 release supports EVM chains and Solana, and it calls Solana account and program-derived-address queries experimental because a guardian may not be reading one agreed slot.',
  'Wormhole CCQ Solana account PDA query'),
 ('0014_transfer_verifier.md', 'wormhole-transfer-verifier', 'Transfer verifier', 10609, True,
  'The objective is to cross-check a core-bridge message against a matching token-bridge transfer.',
  'It contrasts chains that expose easy receipt data with Sui and Solana, which it says do not offer the same introspection.',
  'Wormhole transfer verifier Solana receipt'),
 ('0015_notary.md', 'wormhole-notary', 'Notary', 13132, False,
  'The objective is a general check that can delay a suspicious Wormhole message or block one it treats as malicious.',
  'The file does not contain the word Solana. It describes itself as acting on verification states, including those from the transfer verifier.',
  'Wormhole notary message delay'),
 ('0016_manager_service.md', 'wormhole-manager-service', 'Manager service', 21090, True,
  'The objective is a bridge for a chain without smart contracts. The design focuses on locking and unlocking Dogecoin with guardian-controlled scripts.',
  'A Solana destination is one of the examples: the deposit has to name the account that should receive the minted tokens.',
  'Wormhole Dogecoin Solana manager multisig'),
 ('0017_delegated_guardian_sets.md', 'wormhole-delegated-guardians', 'Delegated guardian sets', 20229, False,
  'The objective is to let a configured subset of guardians watch a particular chain and pass observations to the others.',
  'The file does not contain the word Solana. It says the current set has 19 guardians and that every guardian is expected to run infrastructure for every chain.',
  'Wormhole delegated guardian set'),
]

def worms():
  rows = []
  for fn, slug, title, nbytes, names, scope, solana, keys in WORMS:
    rows.append(_paper(
      slug=slugify(title), legacy=slug, stable_id='paper-' + slug, project='Wormhole', title=title, doc_type='Design note',
      version='Not a numbered paper version', date='Not stated in the file',
      authors='Not named in the file', language='English', topics=['bridging'],
      names_solana=names, bytes=nbytes,
      source=WORM + fn,
      retrieval='HTTP 200 on 17 Nov 2026 from the raw file in wormhole-foundation/wormhole, ' + format(nbytes, ',') + ' bytes.',
      scope=scope, solana=solana,
      limits='This is the file’s design. It is not evidence of what the deployed bridge does, and it is not a security review. Sol.College did not run the protocol.',
      keywords=keys,
      desc=title + ', a Wormhole design note read from the project repository. Not a security review.',
      related=['generic-message-passing'] if slugify(title) != 'generic-message-passing' else []))
  return rows

def papers():
  rows = [
    _paper(slug='solana-a-new-architecture-for-a-high-performance-blockchain', legacy='solana-whitepaper', stable_id='paper-solana-whitepaper', project='Solana', title='Solana: A new architecture for a high performance blockchain',
      doc_type='White paper', version='v0.8.14', authors='Anatoly Yakovenko', language='English',
      topics=['protocol', 'consensus'], names_solana=True, bytes=625176,
      source='https://github.com/solana-labs/whitepaper/blob/master/solana-whitepaper-en.pdf',
      retrieval='HTTP 200 on 17 Nov 2026 from the raw PDF in solana-labs/whitepaper, 625,176 bytes, 32 pages. The full text was read for the section-by-section reading on this page. solana.com/solana-whitepaper.pdf returned HTTP 429 from this machine, so that URL is not the copy that was read.',
      scope='The title page calls this a white paper. The abstract proposes Proof of History as a record of order and of the passage of time, to be used with a consensus algorithm, and it also proposes a proof-of-stake algorithm and a streaming proof of replication. The same abstract says the protocol is analyzed on a 1 gbps network and states a throughput of 710,000 transactions per second for that analysis.',
      solana='The paper is the Solana architecture paper. The title page also says it is not an offer to sell tokens and not a guarantee of how the network or any token will develop.',
      limits='The 710,000 figure is the paper’s analysis. Sol.College did not rerun it, and it is not a measurement of the live network. Later components such as Turbine, Gulf Stream, Sealevel, and Alpenglow are not this version’s claims unless the text says so. The reading note is not a verbatim copy of the PDF.',
      keywords='Solana white paper Proof of History PoH Yakovenko v0.8.14 710000',
      desc='Solana white paper v0.8.14 by Anatoly Yakovenko, read from the project repository. The throughput figure was not rerun.'),
    _paper(slug='solana-une-nouvelle-architecture-pour-une-blockchain-haute-performance', legacy='solana-whitepaper-fr', stable_id='paper-solana-whitepaper-fr', project='Solana', title='Solana : Une nouvelle architecture pour une blockchain haute performance',
      doc_type='Language edition', version='v0.8.14', authors='Anatoly Yakovenko', language='French',
      topics=['protocol'], names_solana=True, bytes=817398,
      source='https://github.com/solana-labs/whitepaper/blob/master/solana-whitepaper-fr.pdf',
      retrieval='HTTP 200 on 17 Nov 2026 from the raw PDF, 817,398 bytes, 34 pages. The full French text was read for the section-by-section reading on this page. That reading is English paraphrase of this PDF, not a line-by-line translation check against the English file.',
      scope='The title page is the French edition of the same repository’s white paper, version v0.8.14, with the same author name.',
      solana='The title names Solana. This record does not establish that every sentence matches the English PDF.',
      limits='A translation is not a second design. The reading note is not a sentence-by-sentence equivalence proof against the English PDF.',
      keywords='Solana livre blanc français Yakovenko v0.8.14',
      desc='French edition of the Solana white paper, v0.8.14. The body was not compared with the English text.',
      related=['solana-a-new-architecture-for-a-high-performance-blockchain']),
    _paper(slug='solana-una-nuova-architettura-per-una-blockchain-ad-alte-prestazioni', legacy='solana-whitepaper-it', stable_id='paper-solana-whitepaper-it', project='Solana', title='Solana: Una nuova architettura per una blockchain ad alte prestazioni',
      doc_type='Language edition', version='v0.8.14', authors='Anatoly Yakovenko', language='Italian',
      topics=['protocol'], names_solana=True, bytes=630897,
      source='https://github.com/solana-labs/whitepaper/blob/master/solana-whitepaper-it.pdf',
      retrieval='HTTP 200 on 17 Nov 2026 from the raw PDF, 630,897 bytes, 34 pages. The full Italian text was read for the section-by-section reading on this page. That reading is English paraphrase of this PDF, not a line-by-line translation check against the English file.',
      scope='The title page is the Italian edition of the same repository’s white paper, version v0.8.14, with the same author name.',
      solana='The title names Solana. This record does not establish that every sentence matches the English PDF.',
      limits='A translation is not a second design. The reading note is not a sentence-by-sentence equivalence proof against the English PDF.',
      keywords='Solana libro bianco italiano Yakovenko v0.8.14',
      desc='Italian edition of the Solana white paper, v0.8.14. The body was not compared with the English text.',
      related=['solana-a-new-architecture-for-a-high-performance-blockchain']),
    _paper(slug='solana-high-performance-blockchain-japanese', legacy='solana-whitepaper-ja', stable_id='paper-solana-whitepaper-ja', project='Solana', title='Solana: 高パフォーマンスなブロックチェーンを実現する新しいアーキテクチャ',
      doc_type='Language edition', version='v0.8.14', authors='Anatoly Yakovenko', language='Japanese',
      topics=['protocol'], names_solana=True, bytes=1109316,
      source='https://github.com/solana-labs/whitepaper/blob/master/solana-whitepaper-ja.pdf',
      retrieval='HTTP 200 on 17 Nov 2026 from the raw PDF, 1,109,316 bytes, 32 pages. The full Japanese text was read for the section-by-section reading on this page. That reading is English paraphrase of this PDF, not a line-by-line translation check against the English file.',
      scope='The title page is the Japanese edition of the same repository’s white paper, version v0.8.14, with the same author name.',
      solana='The title names Solana. This record does not establish that every sentence matches the English PDF.',
      limits='A translation is not a second design. The reading note is not a sentence-by-sentence equivalence proof against the English PDF.',
      keywords='Solana ホワイトペーパー 日本語 Yakovenko v0.8.14',
      desc='Japanese edition of the Solana white paper, v0.8.14. The body was not compared with the English text.',
      related=['solana-a-new-architecture-for-a-high-performance-blockchain']),
    _paper(slug='solana-alpenglow-consensus-v1', legacy='alpenglow-v1-0', stable_id='paper-alpenglow-v1-0', project='Anza', title='Solana Alpenglow Consensus',
      doc_type='White paper', version='v1', date='19 May 2025',
      authors='Quentin Kniep, Jakub Sliwinski, Roger Wattenhofer', language='English',
      topics=['consensus'], names_solana=True, bytes=583928,
      source='https://github.com/rogerANZA/Alpenglow-White-Paper/blob/main/Alpenglow-v1.0.pdf',
      retrieval='HTTP 200 on 17 Nov 2026 from the raw PDF, 583,928 bytes, 48 pages. The full text was read for the section-by-section reading on this page. The repository README calls this the original paper, dated 19 May 2025, which matches the title page.',
      scope='The abstract describes Alpenglow as a proof-of-stake consensus protocol. It says Votor can finalize in one voting round if 80 percent of stake is participating, and in two rounds if 60 percent is responsive, and that Rotor distributes blocks with erasure coding in proportion to stake. It states a “20+20” resilience: an adversary with 20 percent of stake, plus another 20 percent offline under stronger network assumptions.',
      solana='The title is “Solana Alpenglow Consensus”, and the affiliation on the title page is Anza.',
      limits='Those percentages are the paper’s claims. Sol.College did not rerun the proofs or the simulations. This version is not evidence of what a cluster runs. The reading note is not a verbatim copy of the PDF.',
      keywords='Alpenglow Votor Rotor Anza consensus 20+20 v1',
      desc='Alpenglow white paper v1, 19 May 2025, read from the Anza repository. The resilience claims were not rerun.'),
    _paper(slug='solana-alpenglow-consensus-v1-1', legacy='alpenglow-v1-1', stable_id='paper-alpenglow-v1-1', project='Anza', title='Solana Alpenglow Consensus',
      doc_type='White paper', version='v1.1', date='22 July 2025',
      authors='Quentin Kniep, Jakub Sliwinski, Roger Wattenhofer', language='English',
      topics=['consensus'], names_solana=True, bytes=600847,
      source='https://github.com/rogerANZA/Alpenglow-White-Paper/blob/main/Alpenglow-v1.1.pdf',
      retrieval='HTTP 200 on 17 Nov 2026 from the raw PDF, 600,847 bytes, 52 pages. The full text was read for the section-by-section reading on this page. The title page says White Paper v1.1, July 22, 2025. SIMD-0326 points at https://www.anza.xyz/alpenglow-1-1, which returned an HTML page, not this PDF.',
      scope='The abstract’s voting and resilience description matches the wording on the v1 title page: one round at 80 percent participation, two rounds at 60 percent, Rotor for block distribution, and “20+20” resilience. This record does not list every change from v1.',
      solana='The title is “Solana Alpenglow Consensus”, affiliation Anza. SIMD-0326 names this version as its companion paper and then lists sections it does not cover.',
      limits='The abstract is the paper’s claim. Activation on a cluster is not established by the PDF. Sol.College did not compare v1 and v1.1 line by line. The reading note is not a verbatim copy of the PDF.',
      keywords='Alpenglow v1.1 Votor Rotor SIMD-0326 Anza',
      desc='Alpenglow white paper v1.1, 22 July 2025. Activation on a cluster is not established by the PDF.',
      related=['solana-alpenglow-consensus-v1', 'simd-0326-alpenglow']),
    _paper(slug='solana-alpenglow-consensus-v1-2', legacy='alpenglow-v1-2', stable_id='paper-alpenglow-v1-2', project='Anza', title='Solana Alpenglow Consensus',
      doc_type='White paper', version='v1.2', date='29 July 2026',
      authors='Quentin Kniep, Jakub Sliwinski, Roger Wattenhofer', language='English',
      topics=['consensus'], names_solana=True, bytes=800667,
      source='https://drive.google.com/file/d/1RPJ9OyohFMuFfLmTB5ydPYlrKTIlUxq9/view',
      retrieval='The PDF was downloaded on 17 Nov 2026 from the Google Drive file linked by Quentin Kniep on anza-xyz/agave pull request 14122, 800,667 bytes, 81 pages. The full text was read for the section-by-section reading on this page, including the block-storage proof on pages 41–44. The title page says White Paper v1.2, July 29, 2026. The Anza blog post “Alpenglow: A New Consensus for Solana” names that version and that date. The blog HTML that was fetched did not include the Drive link.',
      scope='The abstract’s description of Votor, Rotor, and “20+20” resilience matches the wording on the v1.1 title page. This version adds material beyond v1.1, including a bounded-state argument and a Quantumglow section; those are the PDF’s own sections.',
      solana='The title is “Solana Alpenglow Consensus”, affiliation Anza.',
      limits='A matching title page is not a diff against v1.1. The proofs were not rerun. This file was not retrieved from an anza.xyz URL. The reading note is not a verbatim copy of the PDF.',
      keywords='Alpenglow v1.2 July 2026 Votor Rotor Anza',
      desc='Alpenglow white paper v1.2, 29 July 2026, from the Drive file named on the Agave pull request. Proofs were not rerun.',
      related=['solana-alpenglow-consensus-v1-1']),
    _paper(slug='simd-0326-alpenglow', project='Solana', title='SIMD-0326 Alpenglow',
      doc_type='SIMD', version='Created 25 July 2025', date='25 July 2025',
      authors='Quentin Kniep, Kobi Sliwinski, Roger Wattenhofer', language='English',
      topics=['consensus'], names_solana=True, bytes=10330,
      source='https://github.com/solana-foundation/solana-improvement-documents/blob/main/proposals/0326-alpenglow.md',
      retrieval='HTTP 200 on 17 Nov 2026 from the raw proposal, 10,330 bytes. The front matter and the summary were read. The front matter spells the second author Kobi Sliwinski. The white paper title page spells that name Jakub Sliwinski. Both spellings are kept.',
      scope='The summary says the proposal changes core consensus from Proof of History and Tower BFT to the Votor parts of Alpenglow. The front matter sets status to Review, category Standard, type Core, and leaves the feature key as a placeholder.',
      solana='It is a Solana Improvement Document. It says the companion paper is Alpenglow v1.1, and that Rotor, smart sampling, and lazy execution are outside this SIMD.',
      limits='Status Review is not acceptance and not activation. Every other proposal file that was retrieved has its own page. The status on that page is the label in that file.',
      keywords='SIMD-0326 Alpenglow Votor Tower BFT Proof of History Review',
      desc='SIMD-0326, status Review, proposes Alpenglow’s Votor in place of Tower BFT. Review is not activation.',
      related=['solana-alpenglow-consensus-v1-1']),
    _paper(slug='pyth-network-a-first-party-financial-oracle', legacy='pyth-whitepaper-v2', stable_id='paper-pyth-whitepaper-v2', project='Pyth', title='Pyth Network: A First-Party Financial Oracle',
      doc_type='White paper', version='2.0', date='28 September 2023',
      authors='Pyth Data Association', language='English',
      topics=['oracle'], names_solana=True, bytes=172342,
      source='https://pythdataassociation.com/whitepaper.pdf',
      retrieval='HTTP 200 on 17 Nov 2026, 172,342 bytes, 6 pages. The full text was read for the section-by-section reading on this page. A request for legacy.pyth.network/whitepaper.pdf was served the v2 file, so a distinct first-version PDF was not retrieved.',
      scope='Version 2.0, dated 28 September 2023, says the network publishes prices from trading firms, market makers, and exchanges, with a confidence interval. The overview uses a BTC/USD price of 65,000 plus or minus 50 as an example of what a feed can say.',
      solana='The introduction says the original white paper proposed a design focused on Solana, and that this version describes a cross-chain way to deliver prices.',
      limits='The example price is an illustration in the paper, not a live price. The first-version PDF was not in hand. Sol.College did not call a Pyth feed. The reading note is not a verbatim copy of the PDF.',
      keywords='Pyth oracle white paper v2 Solana first party 2023',
      desc='Pyth Network white paper version 2.0, 28 September 2023. The example price is not a live price.',
      related=[]),
    _paper(slug='solayer-endogenous-avs-on-solana-powered-by-restaking', legacy='solayer-restaking', stable_id='paper-solayer-restaking', project='Solayer', title='Solayer: Endogenous AVS on Solana Powered by Restaking',
      doc_type='Litepaper', version='v0, part 1', authors='Solayer Team', language='English',
      topics=['restaking'], names_solana=True, bytes=553383,
      source='https://github.com/solayer-labs/solayer-improvement-proposal/blob/main/whitepapers/solayer-litepaper-v0.pdf',
      retrieval='HTTP 200 on 17 Nov 2026 from the raw PDF, 553,383 bytes, 5 pages. The full text was read for the section-by-section reading on this page.',
      scope='The abstract describes a restaking market on Solana for what it calls endogenous actively validated services, aimed at on-chain applications rather than at securing a separate chain. It says delegated stake can be used with Solana’s stake-weighted quality of service so an application can seek block space.',
      solana='The title and the abstract name Solana. The introduction attributes the restaking idea to EigenLayer and contrasts that design’s use of Ethereum stake.',
      limits='“Part 1” and “v0” are the paper’s own labels. Yield, conversion, and slippage claims in the abstract were not checked. This is not evidence of a deployment. The reading note is not a verbatim copy of the PDF.',
      keywords='Solayer restaking AVS Solana litepaper stake weighted QoS',
      desc='Solayer restaking litepaper, v0 part 1, read from the project repository. Deployment was not checked.'),
    _paper(slug='solayer-usd-yield-bearing-real-world-assets-backed-synthetic-stablecoin', legacy='solayer-usd', stable_id='paper-solayer-usd', project='Solayer', title='Solayer USD: Yield-bearing Real World Assets Backed Synthetic Stablecoin',
      doc_type='Litepaper', version='v0, part 1', authors='Solayer Team', language='English',
      topics=['stablecoin'], names_solana=True, bytes=2614802,
      source='https://github.com/solayer-labs/solayer-improvement-proposal/blob/main/whitepapers/solayer-USD-litepaper-v0.pdf',
      retrieval='HTTP 200 on 17 Nov 2026 from the raw PDF, 2,614,802 bytes, 5 pages. The full text was read for the section-by-section reading on this page.',
      scope='The abstract describes sUSD as a dollar-pegged token backed by a basket of real-world assets, and says yield is applied by changing a Token-2022 balance multiplier rather than by changing the token amount. It also describes a request-for-quote path for subscription and redemption.',
      solana='The abstract says sUSD uses Solana’s Token-2022 extension and speaks of the Solana ecosystem. A 4 to 5 percent yield, a 170 billion dollar stablecoin market, and a 2.6 trillion dollar settlement figure appear as the paper’s citations. They were not checked.',
      limits='Those market and yield figures are the paper’s statements. Sol.College did not inspect a reserve, a multiplier, or an issuer. The reading note is not a verbatim copy of the PDF.',
      keywords='Solayer sUSD stablecoin Token-2022 RWA litepaper',
      desc='Solayer USD litepaper, v0 part 1. The yield and market figures were not checked.'),
    _paper(slug='solayer-bridge-canonical-bridge-between-svms', legacy='solayer-bridge', stable_id='paper-solayer-bridge', project='Solayer', title='Solayer Bridge: Canonical Bridge Between SVMs',
      doc_type='White paper', version='Not stated on the title page', authors='Solayer Team', language='English',
      topics=['bridging', 'svm'], names_solana=True, bytes=594192,
      source='https://github.com/solayer-labs/solayer-improvement-proposal/blob/main/whitepapers/solayer-bridge.pdf',
      retrieval='HTTP 200 on 17 Nov 2026 from the raw PDF, 594,192 bytes, 6 pages. The full text was read for the section-by-section reading on this page.',
      scope='The abstract describes a bridge for moving assets and calling across SVM environments, starting with Solana and Solayer. It names on-chain programs, a guardian quorum, threshold signatures, and two finality paths.',
      solana='The first section is titled as a bidirectional bridge between Solayer and Solana. It cites Wormhole, LayerZero, and Hyperlane as generic bridges it is not trying to be.',
      limits='The design is the paper’s design. Sol.College did not send a transaction across it and did not review the guardian set. The reading note is not a verbatim copy of the PDF.',
      keywords='Solayer bridge sBridge SVM Solana guardian',
      desc='Solayer bridge paper for SVM environments, starting with Solana. No transfer was sent.'),
    _paper(slug='solayer-chain-infinitely-scalable-hardware-accelerated-svm-network', legacy='solayer-chain', stable_id='paper-solayer-chain', project='Solayer', title='Solayer Chain: Infinitely Scalable Hardware-Accelerated SVM Network',
      doc_type='Litepaper', version='Not stated on the title page', date='6 January 2025',
      authors='Jason Li, Chaofan Shou, Qi Su, Chaz Cui, Tony Ke', language='English',
      topics=['svm', 'execution'], names_solana=True, bytes=605925,
      source='https://github.com/solayer-labs/solayer-improvement-proposal/blob/main/whitepapers/solayer_infinisvm_litepaper.pdf',
      retrieval='HTTP 200 on 17 Nov 2026 from the raw PDF, 605,925 bytes, 12 pages. The full text was read for the section-by-section reading on this page. The date on the title page is 6 January 2025.',
      scope='The abstract describes one global state machine split across microservices and hardware, with speculative execution before a sequencer and a hybrid proof-of-authority and proof-of-stake finality. It names InfiniBand RDMA and a shared-nothing key-value store.',
      solana='The title calls the network an SVM network. The abstract’s performance targets, including 1 million transactions per second and 100 Gbps, are the paper’s targets.',
      limits='A target in an abstract is not a benchmark Sol.College ran. “Infinitely scalable” is the title’s phrase, not a finding. The reading note is not a verbatim copy of the PDF.',
      keywords='Solayer Chain InfiniSVM SVM litepaper January 2025',
      desc='Solayer Chain litepaper, 6 January 2025. The throughput target was not benchmarked here.'),
    _paper(slug='magicblock-whitepaper', project='MagicBlock', title='MagicBlock Whitepaper',
      doc_type='White paper', version='Docs page', authors='Gabriele Picco, Andrea Fortugno', language='English',
      topics=['svm', 'games'], names_solana=True, bytes=834,
      source='https://docs.magicblock.gg/pages/overview/additional-information/whitepaper',
      retrieval='HTTP 200 on 17 Nov 2026 for the docs page. The Markdown source in magicblock-labs/docs is 834 bytes and was read in full for the reading on this page. It cites arXiv:2311.02650.',
      scope='The page says it proposes a framework that uses the Solana Virtual Machine to scale fully on-chain applications, and it introduces ephemeral rollups: dedicated runtimes, a configurable tick, provable sessions, and gasless transactions.',
      solana='The page names the Solana Virtual Machine. The longer argument is the arXiv paper it cites, which has its own record.',
      limits='This page is the short document the docs call a white paper. It is not the arXiv PDF, and it does not by itself show that a game is deployed. The reading note is not a verbatim copy of the docs page.',
      keywords='MagicBlock ephemeral rollup SVM white paper Picco Fortugno',
      desc='MagicBlock’s short white paper page on its docs site. It is not the arXiv PDF.',
      related=['ephemeral-rollups-are-all-you-need']),
    _paper(slug='ephemeral-rollups-are-all-you-need', legacy='ephemeral-rollups', stable_id='paper-ephemeral-rollups', project='MagicBlock', title='Ephemeral Rollups are All you Need',
      doc_type='White paper', version='arXiv:2311.02650v4', date='14 February 2025',
      authors='Gabriele Picco, Andrea Fortugno', language='English',
      topics=['svm', 'games'], names_solana=True, bytes=1322608,
      source='https://arxiv.org/pdf/2311.02650',
      retrieval='HTTP 200 on 17 Nov 2026 from arXiv, 1,322,608 bytes, 18 pages. The full text was read for the section-by-section reading on this page. The title page says version 4, 14 February 2025, and prints www.magicblock.gg. The MagicBlock docs page cites this identifier.',
      scope='The abstract proposes a framework for fully on-chain games that uses the Solana Virtual Machine so that scaling does not fragment state. It says both game state and game logic would live on the chain.',
      solana='The abstract names the Solana Virtual Machine. The paper’s claims about cost and trust were not remeasured.',
      limits='The reading note is not a review of the proofs or of a live game. arXiv listing is not peer review. The reading note is not a verbatim copy of the PDF.',
      keywords='ephemeral rollups arXiv 2311.02650 SVM MagicBlock Picco Fortugno',
      desc='Ephemeral Rollups are All you Need, arXiv:2311.02650v4. An arXiv listing is not peer review.',
      related=['magicblock-whitepaper']),
    _paper(slug='uxd-protocol-an-algorithmic-stablecoin-100-backed-by-a-delta-neutral-position', legacy='uxd-whitepaper', stable_id='paper-uxd-whitepaper', project='UXD Protocol', title='UXD Protocol: An Algorithmic Stablecoin 100% Backed by a Delta Neutral Position',
      doc_type='White paper', version='Not stated on the pages read', authors='Kento Inami', language='English',
      topics=['stablecoin'], names_solana=False, bytes=68001,
      source='https://docs.uxd.fi/uxdprotocol/resources/whitepaper',
      retrieval='The docs page titled Whitepaper was fetched on 17 Nov 2026 and links a PDF. That PDF was downloaded, HTTP 200, 68,001 bytes, and the full text was read for the section-by-section reading on this page. The PDF has no calendar date on the pages that were read.',
      scope='The abstract proposes a stablecoin backed by a delta-neutral position in perpetual swaps, so that a user can mint and redeem against a crypto asset at par. The body uses bitcoin and the US dollar as the running example and says other assets could be substituted.',
      solana='The PDF does not contain the word Solana. The project’s docs present this file as the white paper. That presentation is not a sentence in the PDF.',
      limits='Nothing in the PDF establishes a chain, a deployment, a reserve, or a redemption that was observed. The chain is not filled in from outside knowledge. The reading note is not a verbatim copy of the PDF.',
      keywords='UXD stablecoin delta neutral perpetual Inami',
      desc='UXD Protocol white paper by Kento Inami. The PDF does not contain the word Solana.',
      related=[]),
  ]
  rows.extend(worms())
  rows.extend(corpus())
  slugs = [r['slug'] for r in rows]
  if len(slugs) != len(set(slugs)):
    raise SystemExit('paper: duplicate slug')
  ids = [r['id'] for r in rows]
  if len(ids) != len(set(ids)):
    raise SystemExit('paper: duplicate id')
  for r in rows:
    if r['doc_type'] not in READING_TYPES:
      continue
    if not load_reading(r['slug']):
      continue
    ret = r['retrieval'].lower()
    if not any(x in ret for x in (
        'full text was read', 'was read in full', 'full markdown',
        'full litepaper', 'full french text was read', 'full italian text was read',
        'full japanese text was read')):
      r['retrieval'] = r['retrieval'].rstrip('.') + '. The full text was read for the section-by-section reading on this page.'
    lim = r['limits'].lower()
    if 'verbatim' not in lim and 'not a copy' not in lim and 'not a sentence-by-sentence' not in lim:
      r['limits'] = r['limits'].rstrip('.') + '. The reading note is not a verbatim copy of the file.'
  return rows

def corpus():
  path = os.path.join(os.path.dirname(__file__), 'paper_corpus.json')
  if not os.path.exists(path):
    return []
  data = json.load(open(path, encoding='utf-8'))
  return [_paper(**row) for row in data]

def reading_path(slug):
  return os.path.join(READING_DIR, slug + '.json')

def load_reading(slug):
  path = reading_path(slug)
  if not os.path.exists(path):
    return None
  data = json.load(open(path, encoding='utf-8'))
  if data.get('slug') != slug:
    raise SystemExit('paper reading slug mismatch ' + slug)
  sections = data.get('sections') or []
  if not sections:
    raise SystemExit('paper reading empty ' + slug)
  for sec in sections:
    if not sec.get('heading') or not sec.get('paragraphs'):
      raise SystemExit('paper reading broken section ' + slug)
  return data

def reading_words(data):
  return sum(len(str(p).split()) for sec in data['sections'] for p in sec['paragraphs'])

def reading_search_text(slug):
  data = load_reading(slug)
  if not data:
    return ''
  parts = []
  for sec in data['sections']:
    parts.append(sec['heading'])
    parts.extend(sec['paragraphs'])
  return ' '.join(parts)

def reading_html(p):
  if p['doc_type'] not in READING_TYPES:
    return ''
  data = load_reading(p['slug'])
  if not data:
    raise SystemExit('paper reading missing for ' + p['slug'])
  blocks = [
    '<section class="paper-reading" id="full-reading">',
    '<h2>Full reading of the retrieved document</h2>',
    '<p>This section walks the retrieved file section by section in the file’s own order. '
    'The prose is a Sol.College reading note. It is not a verbatim copy of the source, not a peer review, '
    'and not a measurement of a live cluster. Figures that appear only as images in the file are noted from their captions. '
    'The source file stays at the link above.</p>',
    '<p class="meta">Reading covers %s page%s as stored for this record, across %s section%s (%s words of reading note).</p>' % (
      E(data.get('pages') or p.get('bytes') or '?'),
      '' if data.get('pages') == 1 else 's',
      E(len(data['sections'])),
      '' if len(data['sections']) == 1 else 's',
      E(format(reading_words(data), ','))),
  ]
  for sec in data['sections']:
    blocks.append('<section class="paper-section">')
    blocks.append('<h3>%s</h3>' % E(sec['heading']))
    if sec.get('where'):
      blocks.append('<p class="meta">%s</p>' % E(sec['where']))
    for para in sec['paragraphs']:
      blocks.append('<p>%s</p>' % E(para))
    blocks.append('</section>')
  blocks.append('</section>')
  return '\n'.join(blocks)

NOT_LISTED = [
 ('Helium white paper, release 0.4.2 (14 November 2018)',
  'The PDF was retrieved from the Helium repository release, 1,220,902 bytes. The text does not contain the word Solana, so it is not listed as a Solana project paper.',
  'https://github.com/helium/whitepaper/releases/download/0.4.2/whitepaper.pdf'),
 ('Audius white paper, last update 8 October 2020',
  'The PDF at whitepaper.audius.co was retrieved, 6 pages. The text names Ethereum and does not contain the word Solana.',
  'https://whitepaper.audius.co/AudiusWhitepaper.pdf'),
 ('Solayer MiCA template',
  'mica-whitepaper.pdf in the Solayer repository is a blank reporting form. The spreadsheet beside it is not a protocol paper. Neither has a research page.',
  'https://github.com/solayer-labs/solayer-improvement-proposal/blob/main/whitepapers/mica-whitepaper.pdf'),
]
DOCS_WITHOUT_A_PAPER_LINK = [
 'https://docs.marinade.finance/',
 'https://docs.raydium.io/',
 'https://docs.orca.so/',
 'https://docs.marginfi.com/',
 'https://learn.sanctum.so/docs',
 'https://docs.zeta.markets/',
 'https://docs.parcl.co/',
 'https://docs.hivemapper.com/',
 'https://learn.nosana.com/',
 'https://know.rendernetwork.com/',
 'https://docs.debridge.com/',
 'https://docs.allbridge.io/',
 'https://docs.mayan.finance/',
 'https://www.eclipse.xyz/',
 'https://docs.neonevm.org/',
 'https://lightprotocol.com/',
 'https://www.zkcompression.com/home',
 'https://www.grass.io/',
 'https://staratlas.com/',
 'https://www.metaplex.com/docs',
 'https://io.net/docs/guides/getting-started',
]

def records():
  import solana_library as lib
  by_slug = dict((p['slug'], p) for p in papers())
  out = []
  subjects = {
    'protocol': ['research'], 'consensus': ['research', 'validators'], 'bridging': ['research'],
    'oracle': ['research', 'defi'], 'restaking': ['research', 'defi'], 'stablecoin': ['research', 'defi', 'tokens'],
    'svm': ['research'], 'execution': ['research'], 'games': ['research', 'games'],
    'lending': ['research', 'defi'], 'trading': ['research', 'defi'], 'networking': ['research', 'validators'],
    'token': ['research', 'tokens'],
  }
  for p in papers():
    subs = []
    for t in p['topics']:
      for s in subjects[t]:
        if s not in subs:
          subs.append(s)
    rels = []
    for slug in p['related']:
      other = by_slug[slug]
      rels.append(('Related document', other['id']))
    out.append(lib.base(
      id=p['id'], title=p['title'], purpose=p['scope'], type=p['doc_type'],
      subjects=subs, needs=['evidence', 'explain'], href=p['path'],
      publisher=p['authors'] if p['authors'] != 'Not named in the file' else p['project'],
      standing='External document, listed by Sol.College. Not an endorsement and not a review.',
      origin='external', language=p['language'],
      licence='Link only. The paper was not copied into this catalogue.',
      learn='What the retrieved document says it is, and which facts it does not establish.',
      why=p['solana'], limits=p['limits'], keywords=p['keywords'] + ' ' + p['project'] + ' ' + p['doc_type'] + ' ' + ' '.join(p.get('outline') or []),
      labels=['source-checked'], discovery='Retrieved by Sol.College on 17 Nov 2026. ' + p['retrieval'],
      verification='The source file was read on 17 Nov 2026. The protocol was not run.',
      relationships=rels, reviewed=CHECKED))
  return out

def page_html(p, by_slug):
  rels = []
  for slug in p['related']:
    o = by_slug[slug]
    rels.append(f'<li><a href="{E(o["path"])}">{E(o["title"])}</a> · {E(o["project"])}</li>')
  rel_html = '<ul>' + ''.join(rels) + '</ul>' if rels else '<p>None recorded.</p>'
  report = ISSUE + '?title=' + urllib.parse.quote('Paper correction: ' + p['title']) + '&body=' + urllib.parse.quote('Record: ' + p['id'] + '\n\nWhat is wrong:\n\nWhat the source says:\n\n')
  named = 'The file contains the word Solana.' if p['names_solana'] else 'The file does not contain the word Solana.'
  reading = reading_html(p)
  outline = ''
  if p.get('outline') and p['doc_type'] not in READING_TYPES:
    outline = ('<h2>Heading outline</h2><p>These headings are the file’s own. The text under them was not copied onto this page.</p><ol>'
      + ''.join(f'<li>{E(h)}</li>' for h in p.get('outline') or []) + '</ol>')
  return f'''<article class="lesson lib-page">
<nav class=crumbs aria-label=Breadcrumb><a href="/">Home</a> / <a href="/library/">Library</a> / <a href="/library/papers/">White papers</a> / <span>{E(p["title"])}</span></nav>
<p class=eyebrow>{E(p["project"])} · {E(p["doc_type"])}</p>
<h1>{E(p["title"])}</h1>
<p class=lead>{E(p["scope"] if len(p["scope"]) <= 280 else p["scope"][:277].rsplit(" ", 1)[0] + "…")}</p>
<p>{E(named)} Listing the document does not mean Sol.College wrote it, ran it, or endorses it.</p>
<dl class=article-meta>
<dt>Project</dt><dd>{E(p["project"])}</dd>
<dt>Document type</dt><dd>{E(p["doc_type"])}</dd>
<dt>Version</dt><dd>{E(p["version"])}</dd>
<dt>Date on the document</dt><dd>{E(p["date"])}</dd>
<dt>Authors, as named</dt><dd>{E(p["authors"])}</dd>
<dt>Language</dt><dd>{E(p["language"])}</dd>
<dt>Topics</dt><dd>{E(", ".join(p["topics"]))}</dd>
<dt>Source</dt><dd><a href="{E(p["source"])}">{E(p["source"])}</a></dd>
<dt>Retrieval</dt><dd>{E(p["retrieval"])}</dd>
<dt>Stable id</dt><dd><code>{E(p["id"])}</code></dd>
</dl>
<h2>What the document says it is</h2>
<p>{E(p["scope"])}</p>
{outline}
{reading}
<h2>Solana, as this document states it</h2>
<p>{E(p["solana"])}</p>
<h2>What this record does not establish</h2>
<p>{E(p["limits"])}</p>
<h2>Related documents in this catalogue</h2>
{rel_html}
<p><a href="{E(report)}">Report a problem</a> · <a href="/library/papers/">All white papers</a> · <a href="/library/">Library</a></p>
</article>'''

def index_html(rows):
  projects = sorted(set(p['project'] for p in rows))
  types = sorted(set(p['doc_type'] for p in rows))
  topics = sorted(set(t for p in rows for t in p['topics']))
  langs = sorted(set(p['language'] for p in rows))
  def opts(xs):
    return ''.join(f'<option value="{E(x)}">{E(x)}</option>' for x in xs)
  cards = []
  for p in rows:
    blob = ' '.join([p['title'], p['project'], p['doc_type'], p['authors'], p['version'], p['date'],
      p['scope'], p['solana'], p['limits'], p['keywords'], ' '.join(p['topics']), p['language'],
      ' '.join(p.get('outline') or []), reading_search_text(p['slug'])]).lower()
    cards.append(f'''<article class="card paper" data-project="{E(p["project"])}" data-type="{E(p["doc_type"])}" data-topics="{E(" ".join(p["topics"]))}" data-lang="{E(p["language"])}" data-solana="{"yes" if p["names_solana"] else "no"}" data-search="{E(blob)}">
<h3><a href="{E(p["path"])}">{E(p["title"])}</a></h3>
<p class=meta>{E(p["project"])} · {E(p["doc_type"])} · {E(p["version"])} · {E(p["language"])}</p>
<p>{E(p["scope"])}</p>
<p class=limit>{E(p["limits"])}</p>
</article>''')
  absent = ''.join(f'<li><a href="{E(u)}">{E(n)}</a>. {E(w)}</li>' for n, w, u in NOT_LISTED)
  docs = ''.join(f'<li><a href="{E(u)}">{E(u)}</a></li>' for u in DOCS_WITHOUT_A_PAPER_LINK)
  data = json.dumps([dict(slug=p['slug'], title=p['title'], project=p['project'], type=p['doc_type'],
    version=p['version'], date=p['date'], authors=p['authors'], language=p['language'], topics=p['topics'],
    names_solana=p['names_solana'], source=p['source'], path=p['path']) for p in rows], ensure_ascii=False)
  return f'''<article class="lesson lib-page">
<nav class=crumbs aria-label=Breadcrumb><a href="/">Home</a> / <a href="/library/">Library</a> / <span>White papers</span></nav>
<p class=eyebrow>Solana Library</p>
<h1>White papers</h1>
<p class=lead>Retrieved white papers, SIMDs, and design notes. One page each. Every retrieved file on this shelf carries a full section-by-section reading. The URL is the document’s title. The file itself stays at the source.</p>
<p>Search matches the words on these pages, including the reading notes. It does not answer from outside the catalogue, and it does not decide which paper is right when two of them disagree. A document that was not retrieved is not given a page. A reading note is not a verbatim copy of the paper.</p>
<form id=paper-form class=finder role=search>
<label>Search titles, authors, and what the paper says
<input id=paper-q type=search placeholder="Proof of History, Pyth, Votor, sUSD" autocomplete=off>
</label>
<div class=finder-row>
<label>Project <select id=paper-project><option value="">Any</option>{opts(projects)}</select></label>
<label>Type <select id=paper-type><option value="">Any</option>{opts(types)}</select></label>
<label>Topic <select id=paper-topic><option value="">Any</option>{opts(topics)}</select></label>
<label>Language <select id=paper-lang><option value="">Any</option>{opts(langs)}</select></label>
</div>
<p><label><input id=paper-solana type=checkbox> Only files that contain the word Solana</label></p>
<p class=meta id=paper-count></p>
</form>
<p id=paper-empty hidden>No retrieved paper contains every word of that query.</p>
<div id=paper-list>
{''.join(cards)}
</div>
<h2>Retrieved, and not listed as Solana papers</h2>
<ul>{absent}</ul>
<h2>Docs pages that did not link a paper</h2>
<p>Each of these pages was fetched on 17 Nov 2026. The links on the page did not include a white paper, a litepaper, or a PDF. The rest of the site was not crawled, so this is not a claim that no paper exists anywhere under that name.</p>
<ul>{docs}</ul>
<p>The machine-readable list of the {len(rows)} records is <a href="/library/papers/catalogue.json">catalogue.json</a>. It has the bibliographic fields, not the papers.</p>
<p><a href="/library/">Back to the library</a> · <a href="/library/policy/">How a record is counted</a></p>
</article>
<script type="application/json" id=paper-data>{data.replace('<', '\\u003c')}</script>
<script>
(function(){{
  var q = document.getElementById('paper-q');
  var items = [].slice.call(document.querySelectorAll('.paper'));
  var count = document.getElementById('paper-count');
  var empty = document.getElementById('paper-empty');
  var stop = 'a an the to of on in for and or a'.split(' ');
  function words(s){{
    var latin = (s.toLowerCase().match(/[a-z0-9_'+-]+/g) || []).filter(function(w){{ return w.length >= 2 && stop.indexOf(w) < 0; }});
    var cjk = s.match(/[\u3040-\u30ff\u3400-\u9fff]+/g) || [];
    return latin.concat(cjk);
  }}
  function apply(){{
    var query = (q.value || '').trim();
    var ws = words(query);
    var project = document.getElementById('paper-project').value;
    var type = document.getElementById('paper-type').value;
    var topic = document.getElementById('paper-topic').value;
    var lang = document.getElementById('paper-lang').value;
    var only = document.getElementById('paper-solana').checked;
    var shown = 0;
    items.forEach(function(el){{
      var ok = true;
      if (project && el.getAttribute('data-project') !== project) ok = false;
      if (type && el.getAttribute('data-type') !== type) ok = false;
      if (topic && el.getAttribute('data-topics').split(' ').indexOf(topic) < 0) ok = false;
      if (lang && el.getAttribute('data-lang') !== lang) ok = false;
      if (only && el.getAttribute('data-solana') !== 'yes') ok = false;
      if (ok && ws.length){{
        var blob = el.getAttribute('data-search') || '';
        if (!ws.every(function(w){{ return blob.indexOf(w) >= 0; }})) ok = false;
      }}
      el.hidden = !ok;
      if (ok) shown++;
    }});
    count.textContent = shown + ' of ' + items.length + ' papers';
    empty.hidden = shown !== 0;
  }}
  document.getElementById('paper-form').addEventListener('submit', function(e){{ e.preventDefault(); apply(); }});
  q.addEventListener('input', apply);
  ['paper-project','paper-type','paper-topic','paper-lang','paper-solana'].forEach(function(id){{
    document.getElementById(id).addEventListener('change', apply);
  }});
  apply();
}})();
</script>'''

def page_title(p, title_counts):
  """Browser title: keep the document name, disambiguate collisions with version or type."""
  title = p['title']
  if title_counts.get(title, 0) <= 1:
    return title
  ver = (p.get('version') or '').strip()
  if ver and not ver.lower().startswith('not'):
    return f'{title} ({ver})'
  return f'{title} ({p["doc_type"]})'

def write_pages(S, page, css):
  import solana_library as lib
  rows = papers()
  by_slug = dict((p['slug'], p) for p in rows)
  title_counts = {}
  for p in rows:
    title_counts[p['title']] = title_counts.get(p['title'], 0) + 1
  paths = []
  os.makedirs(S + '/library/papers', exist_ok=True)
  catalogue = [dict(slug=p['slug'], title=p['title'], project=p['project'], type=p['doc_type'],
    version=p['version'], date=p['date'], authors=p['authors'], language=p['language'], topics=p['topics'],
    names_solana=p['names_solana'], bytes=p['bytes'], source=p['source'], path=p['path'],
    scope=p['scope'], solana=p['solana'], limits=p['limits'], retrieved=CHECKED) for p in rows]
  open(S + '/library/papers/catalogue.json', 'w').write(json.dumps(catalogue, ensure_ascii=False, indent=2))
  desc = 'White papers and design notes retrieved for the Solana Library, one page each. A missing file is not given a page.'
  lib.write_page(S, page, css, '/library/papers/', 'White papers', desc, index_html(rows),
    lib.ld('White papers', desc, '/library/papers/'))
  paths.append('/library/papers/')
  for p in rows:
    about = {'@type': 'ScholarlyArticle', 'name': p['title'], 'url': p['source'], 'inLanguage': p['language']}
    if p['authors'] in ('Pyth Data Association', 'Solayer Team'):
      about['author'] = {'@type': 'Organization', 'name': p['authors']}
    elif p['authors'] != 'Not named in the file':
      about['author'] = [{'@type': 'Person', 'name': a.strip()} for a in p['authors'].split(',')]
    heading = page_title(p, title_counts)
    data = lib.ld(heading, p['desc'], p['path'])
    data['about'] = about
    # Keep a top-level ScholarlyArticle node so the SEO pass treats the page as typed.
    data['mentions'] = about
    lib.write_page(S, page, css, p['path'], heading, p['desc'], page_html(p, by_slug), data)
    paths.append(p['path'])
    if p.get('legacy') and p['legacy'] != p['slug']:
      old = '/library/papers/' + p['legacy'] + '/'
      note = f'''<article class="lesson lib-page">
<nav class=crumbs aria-label=Breadcrumb><a href="/">Home</a> / <a href="/library/">Library</a> / <a href="/library/papers/">White papers</a></nav>
<h1>This record moved</h1>
<p>The page for {E(p["title"])} is now <a href="{E(p["path"])}">{E(p["path"])}</a>. The address is the document’s title.</p>
</article>'''
      lib.write_page(S, page, css, old, heading, 'This record moved. The text was not copied.', note,
        lib.ld(heading, 'This record moved.', old))
      dest = S + old + 'index.html'
      html_page = open(dest, encoding='utf-8').read()
      if 'noindex' not in html_page.lower():
        html_page = html_page.replace('</head>', '<meta name=robots content="noindex,follow"></head>', 1)
        open(dest, 'w', encoding='utf-8').write(html_page)
      paths.append(old)
  return paths
