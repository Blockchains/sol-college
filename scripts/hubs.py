"""Learning path, topic hubs, glossary and FAQ. Facts are general Solana facts linked to the official docs;
project lists are computed from the catalog at build time, so nothing here is hand-counted."""
import re,html
E=html.escape
D='https://solana.com/docs'
# lesson level, used for JSON-LD educationalLevel and the roadmap
LEVEL={'transactions':'Beginner','pdas':'Beginner','account-constraints':'Beginner','spl-tokens':'Intermediate','cpis':'Intermediate','token-2022':'Intermediate','nfts':'Intermediate','escrow':'Advanced','staking':'Advanced','compressed-nfts':'Advanced','oracles':'Advanced','solana-pay':'Intermediate','blinks-actions':'Intermediate','ai-agents':'Advanced'}
BUILD_DAPP=dict(slug="build-a-dapp", title="Build a Solana dapp end to end", body=[
 ("Scaffold the app","create-solana-dapp is the Solana Foundation's generator. It creates a web app plus an Anchor workspace, with wallet connection already wired up. Pick a template when prompted.","npx create-solana-dapp@latest"),
 ("Write the program","Start from the accounts, not the handlers: decide which accounts each instruction reads and writes, which must sign, and which are PDAs. The lessons on account constraints and PDAs show how real projects in the stack do this.",[("Lesson: Anchor account constraints","/learn-by-example/account-constraints/"),("Lesson: Program Derived Addresses","/learn-by-example/pdas/")]),
 ("Build, test and sync the program ID","anchor build compiles the program and writes the IDL to target/idl. anchor keys sync puts the program keypair's address into declare_id! and Anchor.toml. anchor test runs the test suite against a local validator.","anchor build\nanchor keys sync\nanchor test"),
 ("Deploy to devnet","Fund a development keypair with devnet SOL and deploy. Devnet SOL has no value.","solana config set --url devnet\nsolana airdrop 2\nanchor deploy --provider.cluster devnet"),
 ("Call it from the browser","The client loads the IDL, connects a wallet, builds the instruction and asks the wallet to sign. The Sol.College lesson dapps work this way: they bundle @coral-xyz/anchor, @solana/web3.js and the Phantom and Solflare wallet adapters, load each program's IDL, and send every transaction through your own wallet.",[("Anchor docs: TypeScript client","https://www.anchor-lang.com/docs/clients/typescript"),("Lesson: Building and sending transactions","/learn-by-example/transactions/"),("Sol.College dapp source","https://github.com/Blockchains/sol-college/tree/main/dapps/app")]),
 ("Harden before mainnet","Write failure-path tests, go through the security checklist, and use a multisig as upgrade authority.",[("Guide: Testing","/how-to-build/testing/"),("Guide: Security checklist","/how-to-build/security-checklist/"),("Guide: Deploy to mainnet","/how-to-build/deploy/")]),
])
TOPICS=[
 dict(slug='anchor',name='Anchor',title='Anchor tutorial: learn the Anchor framework from real code',intro="Anchor is the most widely used framework for writing Solana programs in Rust. It generates account (de)serialisation, checks account constraints declared in #[derive(Accounts)] structs, and emits an IDL that clients use to call the program.",
  lessons=['account-constraints','pdas','cpis','escrow'],guides=['anchor-workflow','testing','build-a-dapp'],fw={'Anchor'},docs=[('Anchor docs','https://www.anchor-lang.com/docs'),('Solana docs: Anchor quickstart',D+'/intro/quick-start')]),
 dict(slug='defi',name='DeFi',title='Solana DeFi development: vaults, swaps and escrow in real code',intro="DeFi programs on Solana hold assets in PDA-owned token accounts and move them with CPIs into the Token Program. Escrow, staking, swaps and lending all reuse the same building blocks: PDAs, token accounts, checked arithmetic and strict account validation.",
  lessons=['escrow','staking','pdas','cpis','spl-tokens','oracles'],guides=['security-checklist'],cat={'DeFi'},kw={'swap','amm','stake','staking','lending','vault'},docs=[('Solana docs: Tokens',D+'/tokens')]),
 dict(slug='payments',name='Payments',title='Solana payments development: Solana Pay and token transfers',intro="Payments on Solana are SOL or SPL token transfers. Solana Pay standardises payment request URLs and QR codes, and merchants confirm a payment by looking up its reference key on-chain.",
  lessons=['spl-tokens','transactions','solana-pay','blinks-actions'],guides=['build-a-dapp'],cat={'Payments'},fw={'Solana Pay'},kw={'payment'},docs=[('Solana Pay docs','https://docs.solanapay.com/'),('Solana docs: Tokens',D+'/tokens')]),
 dict(slug='nfts',name='NFTs',title='Solana NFT development: Metaplex and compressed NFTs in code',intro="Most Solana NFTs follow Metaplex standards: Token Metadata on a supply-1 mint, the newer single-account Metaplex Core, or compressed NFTs stored in a Merkle tree through Bubblegum.",
  lessons=['nfts','compressed-nfts','token-2022'],guides=[],cat={'NFTs & Digital Assets'},fw={'Metaplex'},kw={'nft','compressed'},docs=[('Metaplex developer docs','https://developers.metaplex.com/')]),
 dict(slug='tokens',name='Tokens',title='SPL tokens and Token-2022: mints, accounts and transfers',intro="Fungible tokens are accounts owned by a token program: a mint defines supply and decimals, and token accounts hold balances. Token-2022 is a second token program with optional extensions such as transfer fees, metadata and transfer hooks.",
  lessons=['spl-tokens','token-2022','cpis'],guides=[],kw={'mint','token-2022'},docs=[('Solana docs: Tokens',D+'/tokens'),('Solana docs: Token Extensions',D+'/tokens/extensions')]),
 dict(slug='zk-privacy',name='ZK and privacy',title='Zero-knowledge and privacy projects on Solana',intro="Solana supports zero-knowledge techniques in a few places, such as the confidential transfer extension of Token-2022 and ZK Compression. The projects below are those in the stack whose own descriptions or code mention privacy or zero-knowledge; read each one's README for what it actually implements.",
  lessons=['token-2022'],guides=[],text=r'\bzk\b|zk-|zero.knowledge|privacy|confidential',docs=[('Solana docs: Confidential transfer',D+'/tokens/extensions/confidential-transfer'),('ZK Compression docs','https://www.zkcompression.com/')]),
 dict(slug='wallets',name='Wallets',title='Solana wallet integration: connect, sign and send',intro="Wallets hold keys and sign transactions; apps never see the private key. A dapp builds a transaction, asks the connected wallet (through wallet-standard or a wallet adapter) to sign it, then sends it to an RPC node and confirms it.",
  lessons=['transactions'],guides=['build-a-dapp'],cat={'Wallets & Identity'},kw={'wallet'},docs=[('Solana docs: Transactions',D+'/core/transactions')]),
 dict(slug='sdks',name='Client SDKs',title='Solana client SDKs: web3.js, @solana/kit, Go and Python',intro="Clients talk to Solana over JSON-RPC. In TypeScript that is @solana/web3.js or its successor @solana/kit; other languages have community SDKs such as solana-go and solana-py. Anchor programs also get typed clients from their IDL.",
  lessons=['transactions'],guides=['build-a-dapp'],fw={'web3.js','@solana/kit','solana-go','solana-py'},docs=[('Solana docs: Clients',D+'/clients')]),
 dict(slug='native-rust',name='Native Rust',title='Native Rust Solana programs without Anchor',intro="Programs can also be written against solana-program directly, or with lightweight libraries such as Pinocchio or Steel. You handle account parsing and validation yourself, which costs more code but gives full control over compute and binary size.",
  lessons=['pdas','cpis'],guides=['security-checklist'],fw={'Native Rust','Pinocchio','Steel'},docs=[('Solana docs: Programs',D+'/programs')]),
 dict(slug='ai-agents',name='AI agents',title='AI agents on Solana: code from real projects',intro="Agent projects give an LLM tools that read chain state and build transactions, for example through Solana Agent Kit, with a human or a policy deciding what gets signed.",
  lessons=['ai-agents','transactions'],guides=[],cat={'AI & Agents'},fw={'Solana Agent Kit'},kw={'agent'},docs=[('Solana docs',D)]),
 dict(slug='gaming',name='Gaming',title='Solana game development: on-chain game state in real code',intro="On-chain games keep player and match state in PDAs and use the same token and NFT programs as everything else for items and rewards.",
  lessons=['pdas','nfts','compressed-nfts'],guides=[],cat={'Gaming'},kw={'game'},docs=[('Solana docs',D)]),
 dict(slug='governance',name='DAOs and governance',title='Solana DAO and governance programs in real code',intro="Governance programs record proposals and votes in program accounts and often control a treasury or a program's upgrade authority through a multisig.",
  lessons=['pdas','account-constraints'],guides=['deploy'],cat={'Governance & DAOs'},kw={'dao','governance','multisig'},docs=[('Squads docs','https://docs.squads.so/')]),
]
GLOSSARY=[
 ('Account',"Solana stores all state in accounts: an address, a lamport balance, an owner program and a data buffer. Only the owner program can change an account's data.",D+'/core/accounts',None),
 ('Lamport',"The smallest unit of SOL. One SOL is 1,000,000,000 lamports.",D+'/core/accounts',None),
 ('Rent exemption',"Accounts must hold a minimum lamport balance proportional to their size to stay on-chain. Closing an account returns that balance.",D+'/core/accounts','account-constraints'),
 ('Program',"Executable code deployed to an account. Programs are stateless; they read and write other accounts passed into each instruction. Ethereum calls these smart contracts.",D+'/core/programs',None),
 ('Instruction',"A call to one program: the program ID, the list of accounts it touches (with signer and writable flags), and an opaque data payload.",D+'/core/transactions','transactions'),
 ('Transaction',"One or more instructions plus signatures and a recent blockhash. Instructions in a transaction succeed or fail together.",D+'/core/transactions','transactions'),
 ('Recent blockhash',"A hash every transaction includes to prove it is fresh. A transaction whose blockhash is too old is rejected, so clients fetch one just before signing.",D+'/core/transactions','transactions'),
 ('Signer',"An account whose private key signed the transaction. Programs check signer flags to authorise actions.",D+'/core/transactions','account-constraints'),
 ('Program Derived Address (PDA)',"An address derived from seeds and a program ID that has no private key. Only that program can sign for it, through invoke_signed.",D+'/core/pda','pdas'),
 ('Bump seed',"The extra byte added to PDA seeds so the derived address falls off the ed25519 curve. The canonical bump is the first one that works, counting down from 255.",D+'/core/pda','pdas'),
 ('Cross-Program Invocation (CPI)',"One program calling an instruction on another, such as the Token Program. A PDA can sign a CPI with its seeds.",D+'/core/cpi','cpis'),
 ('SPL Token',"The standard token program for fungible and non-fungible tokens on Solana.",D+'/tokens','spl-tokens'),
 ('Mint account',"The account that defines a token: its supply, decimals and mint authority.",D+'/tokens','spl-tokens'),
 ('Token account',"An account holding a balance of one mint for one owner.",D+'/tokens','spl-tokens'),
 ('Associated Token Account (ATA)',"The canonical token account address for a given wallet and mint, derived deterministically so anyone can find it.",D+'/tokens','spl-tokens'),
 ('Token-2022',"A second token program, also called Token Extensions, that adds optional features such as transfer fees, metadata and transfer hooks.",D+'/tokens/extensions','token-2022'),
 ('Anchor',"A Rust framework for Solana programs that handles serialisation, account validation through constraints, and IDL generation.",'https://www.anchor-lang.com/docs','account-constraints'),
 ('IDL',"Interface Definition Language: a JSON description of a program's instructions and accounts that Anchor generates and clients use to build calls.",'https://www.anchor-lang.com/docs','transactions'),
 ('Account discriminator',"The first 8 bytes Anchor writes into each account it creates, identifying the account type so one type can't be passed off as another.",'https://www.anchor-lang.com/docs','account-constraints'),
 ('Compute units',"The measure of work a transaction may do. Each transaction has a compute limit, and clients can request a specific limit.",D+'/core/fees','transactions'),
 ('Priority fee',"An optional fee per compute unit, set with the Compute Budget program, that helps a transaction get scheduled when blocks are busy.",D+'/core/fees','transactions'),
 ('Commitment',"How final a read or confirmation is: processed, confirmed or finalized.",D+'/rpc','transactions'),
 ('Devnet',"A public Solana cluster for testing. Devnet SOL is free from the faucet and has no value.",'https://faucet.solana.com',None),
 ('Upgrade authority',"The key allowed to redeploy a program. Many teams hand it to a multisig, or remove it to make the program immutable.",D+'/programs/deploying',None),
 ('Metaplex',"The set of programs and standards most Solana NFTs use, including Token Metadata, Core and Bubblegum.",'https://developers.metaplex.com/','nfts'),
 ('Compressed NFT',"An NFT stored as a leaf in a concurrent Merkle tree rather than in its own accounts, which makes large mints cheap.",'https://developers.metaplex.com/bubblegum','compressed-nfts'),
 ('Solana Pay',"A URL standard for payment requests that wallets can scan as QR codes.",'https://docs.solanapay.com/','solana-pay'),
 ('Actions and Blinks',"Actions are APIs that return a signable transaction; Blinks are links that render an Action as buttons in a supporting client.",D+'/advanced/actions','blinks-actions'),
 ('Address lookup table',"An on-chain list of addresses that versioned transactions can reference by index, so they fit more accounts.",D+'/advanced/lookup-tables','transactions'),
 ('Sysvar',"Special accounts exposing cluster state to programs, such as Clock (time) and Rent.",D+'/core/accounts','staking'),
]
def slugify(s): return re.sub('[^a-z0-9]+','-',s.lower()).strip('-')
def render(g):
  page,P,LES,have,GUIDES,card,SITE,kw=g['page'],g['P'],g['LES'],g['have'],g['GUIDES'],g['card'],g['SITE'],g['kw']
  gd={x['slug']:x for x in GUIDES}
  def lesson_li(s): L=have[s]; return f'<li><a href="/learn-by-example/{s}/">{E(L["title"])}</a> <span class=chip>{LEVEL.get(s,"Intermediate")}</span></li>'
  def guide_li(s): return f'<li><a href="/how-to-build/{s}/">{E(gd[s]["title"])}</a></li>' if s in gd else ''
  lesson_link=lambda l: f' · <a href="/learn-by-example/{l}/">Lesson: {E(have[l]["title"])}</a>' if l in have else ''
  link_li=lambda n,u: f'<li><a href="{u}">{E(n)}</a></li>'
  K={p['name']:kw(p).split() for p in P}
  hubs=[]
  for T in TOPICS:
    ps=[p for p in P if set(p['categories'])&T.get('cat',set()) or set(p['frameworks'])&T.get('fw',set()) or set(K[p['name']])&T.get('kw',set()) or (T.get('text') and re.search(T['text'],(p['name']+' '+p['description']).lower()))]
    ls=[s for s in T['lessons'] if s in have]
    if not ps and not ls: continue
    T['ps']=sorted(ps,key=lambda p:-p['stars']); T['ls']=ls; hubs.append(T)
  TOPIC_OF={}
  for T in hubs:
    for s in T['ls']: TOPIC_OF.setdefault(s,[]).append(T)
  g['TOPIC_OF']=TOPIC_OF
  for T in hubs:
    other=''.join(f'<a class=chip href="/topics/{x["slug"]}/">{E(x["name"])}</a>' for x in hubs if x is not T)
    body=f'''<h1>{E(T['name'])} on Solana</h1><p class=lead>{E(T['intro'])}</p><p class=docs>Reference: {' · '.join(f'<a href="{u}">{E(n)}</a>' for n,u in T['docs'])}</p>
{f'<h2>Lessons</h2><ol>{"".join(lesson_li(s) for s in T["ls"])}</ol>' if T['ls'] else ''}
{f'<h2>Guides</h2><ul>{"".join(guide_li(s) for s in T["guides"])}</ul>' if [s for s in T['guides'] if s in gd] else ''}
<h2>Projects in the stack ({len(T['ps'])})</h2>{f'<div class=grid>{"".join(card(p) for p in T["ps"])}</div>' if T['ps'] else '<p>No published project walkthrough matches this topic yet. The lessons above use code from other projects in the stack.</p>'}
<h2>Other topics</h2><p>{other}</p>'''
    page(f"/topics/{T['slug']}/",T['title'],f"{T['intro'][:120].rsplit(' ',1)[0]}… Lessons, guides and {len(T['ps'])} real projects.",body,og='topics',
      ld=[{"@type":"CollectionPage","name":T['title'],"url":f"{SITE}/topics/{T['slug']}/","about":T['name'],"hasPart":[{"@type":"LearningResource","name":have[s]['title'],"url":f"{SITE}/learn-by-example/{s}/"} for s in T['ls']]}],
      crumbs=[('/','Home'),('/topics/','Topics'),(f"/topics/{T['slug']}/",T['name'])])
  page('/topics/','Solana development topics: DeFi, NFTs, tokens, Anchor','Solana development by topic: Anchor, DeFi, payments, NFTs, tokens, ZK and privacy, wallets, SDKs and more, each with lessons and real projects.',
    '<h1>Topics</h1><p class=lead>Every topic page collects the lessons, guides and real projects in the stack that touch it.</p><div class=grid>'+''.join(f'<article class=card><h3><a href="/topics/{T["slug"]}/">{E(T["name"])}</a></h3><p>{E(T["intro"][:150].rsplit(" ",1)[0])}…</p><p class=meta>{len(T["ls"])} lessons · {len(T["ps"])} projects</p></article>' for T in hubs)+'</div>',og='topics',
    ld=[{"@type":"CollectionPage","name":"Solana development topics","url":SITE+"/topics/"}],crumbs=[('/','Home'),('/topics/','Topics')])
  # ---- learning path
  STAGES=[
   ('Foundations','Beginner',"Learn the account model first: everything on Solana is an account, programs are stateless, and transactions list every account they touch up front. Then set up the toolchain and get devnet SOL.",
    [],['setup'],[('Solana docs: Core concepts',D+'/core'),('Glossary','/glossary/')]),
   ('Clients and transactions','Beginner',"Read state and send transactions from TypeScript before writing a program, so you know what a program receives.",['transactions'],[],[('Solana docs: Transactions',D+'/core/transactions')]),
   ('Your first Anchor program','Beginner',"Scaffold a workspace, declare accounts with constraints, and store state at PDAs.",['account-constraints','pdas'],['anchor-workflow'],[('Solana docs: Build your first program',D+'/intro/quick-start')]),
   ('Tokens and composition','Intermediate',"Create mints and token accounts, move tokens, and call other programs through CPIs, signing with PDAs where needed.",['spl-tokens','cpis','token-2022'],[],[]),
   ('Full-stack dapp','Intermediate',"Connect a wallet, call your program from the browser through its IDL, and deploy to devnet.",['nfts','solana-pay','blinks-actions'],['build-a-dapp','testing'],[]),
   ('Advanced patterns','Advanced',"Study complete programs: escrow, staking, oracles and compressed state, each from real projects in the stack.",['escrow','staking','oracles','compressed-nfts','ai-agents'],[],[('Browse topics','/topics/')]),
   ('Ship to production','Advanced',"Test the failure paths, review security, publish a verifiable build and move to mainnet with a multisig upgrade authority.",[],['security-checklist','deploy'],[]),
  ]
  body='<h1>Learn Solana development: a roadmap from beginner to advanced</h1><p class=lead>A free, ordered path through Sol.College. Each step links lessons built from real, permissively licensed code in the stack, practical guides, and the official docs. Work through it in order, or jump to the stage you need.</p><ol class=path>'
  parts=[]
  for i,(name,lvl,txt,ls,gs,docs) in enumerate(STAGES,1):
    ls=[s for s in ls if s in have]; gs=[s for s in gs if s in gd]
    parts+= [(have[s]['title'],f'/learn-by-example/{s}/') for s in ls]+[(gd[s]['title'],f'/how-to-build/{s}/') for s in gs]
    body+=f'<li><h2 id=stage-{i}>Stage {i}: {E(name)} <span class=chip>{lvl}</span></h2><p>{E(txt)}</p><ul>{"".join(lesson_li(s) for s in ls)}{"".join(guide_li(s).replace("</li>"," <span class=chip>Guide</span></li>") for s in gs)}{"".join(link_li(n,u) for n,u in docs)}</ul></li>'
  body+='</ol><h2>Then build something</h2><p>The <a href="/what-to-build/">what to build</a> pages show where the stack has few strong projects, and the <a href="/explore/">explorer</a> lets you filter real projects by framework to fork.</p>'
  page('/learn-solana/','Learn Solana development: beginner to advanced roadmap','A free Solana developer roadmap: accounts, transactions, Anchor, PDAs, tokens, CPIs, full-stack dapps, security and mainnet, with lessons from real code.',body,og='path',
    ld=[{"@type":"Course","name":"Learn Solana development","description":"A free roadmap from Solana fundamentals to production, built on lessons from real open-source code.","url":SITE+"/learn-solana/","provider":{"@type":"Organization","name":"Sol.College","url":SITE},"isAccessibleForFree":True,"educationalLevel":"Beginner to Advanced","inLanguage":"en","hasCourseInstance":{"@type":"CourseInstance","courseMode":"online","courseWorkload":"PT6H"},"offers":{"@type":"Offer","price":0,"priceCurrency":"USD","category":"Free"},"hasPart":[{"@type":"LearningResource","name":n,"url":SITE+u} for n,u in parts]}],
    crumbs=[('/','Home'),('/learn-solana/','Learn Solana')])
  # ---- glossary
  body='<h1>Solana glossary</h1><p class=lead>Core Solana and Anchor terms in plain English. Each links to the official docs and, where there is one, the Sol.College lesson that shows it in real code.</p><dl class=gloss>'
  for t,d,u,l in GLOSSARY:
    body+=f'<dt id={slugify(t)}>{E(t)}</dt><dd>{E(d)} <a href="{u}">Docs</a>{lesson_link(l)}</dd>'
  body+='</dl>'
  page('/glossary/','Solana glossary: PDAs, CPIs, accounts, tokens and more','Plain-English definitions of Solana and Anchor terms: accounts, lamports, PDAs, bumps, CPIs, SPL tokens, Token-2022, IDLs, compute units and more.',body,og='glossary',
    ld=[{"@type":"DefinedTermSet","name":"Solana glossary","url":SITE+"/glossary/","hasDefinedTerm":[{"@type":"DefinedTerm","name":t,"description":d,"url":f"{SITE}/glossary/#{slugify(t)}"} for t,d,u,l in GLOSSARY]}],crumbs=[('/','Home'),('/glossary/','Glossary')])
  # ---- FAQ
  n_les=len(LES)
  FAQ=[
   ("What language are Solana programs written in?","Most Solana programs are written in Rust, usually with the Anchor framework. Programs compile to eBPF-based bytecode (SBF) and run on the Solana runtime. Clients are commonly TypeScript, with community SDKs for other languages."),
   ("Do I need to know Rust to start?","Not on day one. You can learn the account model and send transactions from TypeScript first (stage 2 of the learning path). To write programs you will need Rust basics: ownership, structs, enums and Result."),
   ("What is Anchor and should I use it?","Anchor is a Rust framework that handles serialisation, account validation through declarative constraints, and IDL generation. Most programs in the stack that ship on-chain code use it. Native Rust, Pinocchio or Steel give more control at the cost of more code."),
   ("What is a PDA?","A Program Derived Address is an address derived from seeds and a program ID that has no private key, so only that program can sign for it. Programs use PDAs as deterministic homes for state and as vault authorities."),
   ("How do I get devnet SOL?","Use the official faucet at faucet.solana.com, or run solana airdrop 2 with the CLI pointed at devnet. Devnet SOL has no value."),
   ("What's the difference between the Token Program and Token-2022?","Token-2022 (Token Extensions) is a separate program with the same core layout plus optional extensions such as transfer fees, metadata and transfer hooks. Code has to pass the right token program ID for the mint it handles."),
   ("Where does the code on Sol.College come from?",f"From real open-source Solana projects forked into the Blockchains GitHub account. Only permissively licensed code is quoted, with attribution and a permalink to the exact lines at a pinned commit. There are currently {n_les} lessons and {len(P)} project walkthroughs."),
   ("Are the build guides tested?","Lesson projects are rebuilt and exercised on a local solana-test-validator by the repository's verification workflow, and each project page shows that run's result. Some projects also have a devnet dapp you can open with your own wallet."),
   ("Is Sol.College free?","Yes. Every lesson, guide and project page is free to read, with no sign-up."),
  ]
  body='<h1>Solana development FAQ</h1><p class=lead>Short answers to common questions from people learning to build on Solana, with links to go deeper.</p>'+''.join(f'<h2>{E(q)}</h2><p>{E(a)}</p>' for q,a in FAQ)+'<p>Next: the <a href="/learn-solana/">learning path</a>, the <a href="/glossary/">glossary</a>, or <a href="/learn-by-example/">all lessons</a>.</p>'
  page('/faq/','Solana development FAQ: Rust, Anchor, PDAs, devnet','Answers to common Solana developer questions: which language, whether you need Rust, Anchor, PDAs, devnet SOL, Token-2022, and how Sol.College works.',body,og='faq',
    ld=[{"@type":"FAQPage","mainEntity":[{"@type":"Question","name":q,"acceptedAnswer":{"@type":"Answer","text":a}} for q,a in FAQ]}],crumbs=[('/','Home'),('/faq/','FAQ')])
  return hubs
