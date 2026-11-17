"""Close readings for The Degen. Facts below are taken from pages retrieved on 17 Nov 2026.

A paragraph may paraphrase. It may not add a number, a person, or a scene that the cited page does not contain.
"""

def R(title, desk, desk_name, feature, desc, deck, question, paragraphs, says, paid, decides, limits, sources, related=()):
    READINGS.append(dict(title=title, desk=desk, desk_name=desk_name, feature=feature, desc=desc, deck=deck,
        question=question, paragraphs=paragraphs, says=says, paid=paid, decides=decides, limits=limits,
        sources=list(sources), related=list(related)))

READINGS = []

# --- Hardware: Seed Vault, Seeker, Ledger Atom, SKR ---

R(
 title='The Phone That Calls Itself a Hardware Wallet',
 desk='chain-watch', desk_name='Chain Watch', feature='Claim Check',
 desc='Seeker’s product page calls Seed Vault a hardware wallet. The developer doc describes a phone service. This reading did not open a device.',
 deck='The product page puts “hardware wallet” on a phone. The developer documentation describes a system service inside that phone. Both pages were retrieved. Neither was a device in the hand.',
 question='What do the retrieved Seeker pages assign to hardware, and what do they leave inside Android?',
 paragraphs=[
  'The Seeker product page does not whisper the claim. In the block it numbers 002, under the heading Secure by Default, the visible text says “Hardware wallet for digital assets with Seed Vault.” A hardware wallet, in the plain sense a reader brings to that sentence, is a machine whose job is to hold a key and to show a human what is about to be signed. A phone is a general-purpose computer. It also runs a store, a radio, and whatever application the dApp Store will install next. The product page sets those two objects in one line.',
  'The same page, further down, is more specific and less grand. Under Seed Vault Wallet it says “Native hardware Seed Vault and mobile wallet featuring fingerprint access and doubletap transactions. Built exclusively for Solana Seeker.” The specifications table lists a power-button fingerprint sensor next to the words Seed Vault, and it lists a MediaTek Dimensity 7300, 8 GB of RAM, 128 GB of storage, a 6.36 inch AMOLED display, a 4500 mAh battery, and a body of 73.5 by 154.8 by 9.3 millimetres. Those are phone specifications. The page does not publish a separate secure-element certification, a model number for a discrete chip, or a threat model.',
  'The developer documentation, last modified on the docs site as 26 October 2026, uses a different noun. It calls Seed Vault “a hardware-level secure key custody system built into Seeker” and then “a system service providing secure key custody to Wallet apps.” The mechanism it names is not a second gadget in a pocket. It is “secure execution environments available on mobile devices (such as secure operating modes of the processor and/or secure auxiliary coprocessors).” Keys, seeds, and secrets “never leave the secure execution environment,” while “UI components built into Android handle interaction with the user.” The hardware, on this page, is a privileged mode of the phone. The screen the human trusts is Android’s.',
  'That split is the whole story the two pages can support. Marketing says hardware wallet. The engineer’s page says a system service, an Android Keystore backed by the device’s secure execution environment, and a signature that still requires a biometric fingerprint or a PIN entered through Android’s interface. A reader who wanted the claim “this is the same object as a dedicated signer with its own screen” will not find that sentence on either page. A reader who wanted the claim “the key is just another file in the photo roll” will not find that sentence either.',
  'The product page also sells a life, not only a key. Block 001 says “Store, spend, trade, and earn, all on your phone.” Block 003 says “Transact and trade on the go, whenever the opportunity strikes.” Block 004 says “Earn rewards and grow your assets from your phone.” The dApp Store line lists payments, DeFi, AI, DePIN, NFTs, and gaming, plus “exclusive dApps only available on Solana Mobile.” A hardware wallet that is also a store is a hardware wallet with a distribution channel attached. Who picks what ships in that store is a power question. This reading only has the product page’s boast, not the store’s review rules.',
  'The paper did not buy a Seeker, did not tap the power button, and did not inspect a secure element under a microscope. The specifications are the page’s specifications. If a later teardown disagrees with the Dimensity 7300 or the battery size, the page is what was wrong, or the teardown is, and this reading will not guess which. The useful distinction, today, is linguistic. “Hardware wallet” on the product page is a category claim. “System service” and “secure execution environment” on the developer page are mechanism claims. A college newspaper should not let the category eat the mechanism.',
 ],
 says=[
  'The Seeker product page labels Seed Vault “Hardware wallet for digital assets with Seed Vault.”',
  'The same page lists a power-button fingerprint sensor, a Dimensity 7300, 8 GB of RAM, 128 GB of storage, and a 4500 mAh battery.',
  'The developer page calls Seed Vault a system service and says keys never leave the secure execution environment.',
  'The developer page says Android UI components handle the interaction, and that every signature needs a biometric fingerprint or a PIN.',
 ],
 paid=[
  'Neither page is a fee schedule. The product page’s “earn” line does not name a recipient.',
  'A later Solana Mobile post, read separately, describes an SKR buy-and-burn funded from validator and Seed Vault Wallet revenue. That post is not this page.',
 ],
 decides=[
  'The developer page says the user authorises each signature. It does not say the user can audit the secure execution environment.',
  'The product page does not name who decides which exclusive dApps ship.',
 ],
 limits=[
  'This reading did not open a Seeker and did not verify the secure-element claim in hardware.',
  '“Hardware wallet” here is the product page’s phrase. It is not a finding that Seeker matches any particular dedicated signer.',
  'No threat model, certification identifier, or chip vendor for the vault was on the pages read.',
 ],
 sources=[
  dict(label='Seeker product page', url='https://solanamobile.com/seeker', note='HTTP 200 on 17 Nov 2026. The visible marketing text and the specifications block were read.'),
  dict(label='Seed Vault, Solana Mobile docs', url='https://docs.solanamobile.com/solana-mobile-stack/seed-vault', note='HTTP 200 on 17 Nov 2026. The docs site records a last modification of 26 October 2026.'),
 ],
 related=['seed-vault-is-a-system-service-not-a-second-gadget', 'double-tap-is-a-fingerprint-on-the-phone-you-already-hold'],
)

R(
 title='Seed Vault Is a System Service, Not a Second Gadget',
 desk='chain-watch', desk_name='Chain Watch', feature='The Fine Print',
 desc='The Seed Vault doc says keys stay in a secure execution environment and Android draws the prompt. No device was opened.',
 deck='The developer page is short on purpose. It names a system service, an Android Keystore, and a rule that every signature needs a person. It does not name a chip.',
 question='What custody mechanism does the Seed Vault developer page actually specify?',
 paragraphs=[
  'The Seed Vault page on the Solana Mobile docs site is not a white paper. It is a short hardware note, and its shortness is part of the record. The description line says Seed Vault is “a hardware-level secure key custody system built into Seeker.” The first paragraph then defines it as “a system service providing secure key custody to Wallet apps.” A system service is software the operating system exposes to other software. The hardware claim sits in the next clause: the service integrates with “secure execution environments available on mobile devices (such as secure operating modes of the processor and/or secure auxiliary coprocessors).” The “and/or” is the page’s own hedge. It does not tell a reader whether Seeker uses a mode of the main processor, an auxiliary coprocessor, or both.',
  'The promise that follows is the one a custody review has to hold onto. “Your keys, seeds, and secrets never leave the secure execution environment, while UI components built into Android handle interaction with the user to provide a secure transaction signing experience.” The secret stays. The pixels move. That is a familiar design in phones that already pay for groceries with a fingerprint. It is not, on this page, a design in which a second screen outside Android shows the destination address. The page does not say the prompt is rendered inside the secure environment. It says Android’s UI components handle the interaction.',
  'Three bullets carry the rest of the mechanism. Secure key storage “leverages the Android Keystore backed by the device’s secure execution environment to store and sign with your keys.” User-authorized signing requires “explicit user approval via secure biometric fingerprint or PIN code entry” on every signing operation. The service is “available as an Android system service to wallet apps.” A dApp, the page is careful to add, usually never talks to that service directly. “Most developers interact with Seed Vault indirectly through the Mobile Wallet Adapter protocol. MWA handles the communication between your app, the wallet app, and Seed Vault.” The wallet app is the middle. The dApp asks the wallet. The wallet asks the vault. The user sees an Android prompt.',
  'There is a second interface, and the page restricts who it is for. The Seed Vault SDK “is designed for wallet developers building apps that interface directly with Seed Vault.” It “includes a simulator for testing on standard Android devices.” If you are building a dApp, the page says, use the MWA SDK instead. The simulator sentence matters. A wallet developer can test against a pretend vault on an ordinary Android phone. A test that passes on the simulator has not, by this page’s own description, run inside Seeker’s secure execution environment. The page does not say the simulator is a security boundary. It says it is for testing.',
  'The wallet that ships on the phone is named, and so is what it holds. “Users create their primary wallet during device onboarding that holds their Seeker Genesis Token. The Seed Vault Wallet is the built-in wallet app on Seeker that interfaces directly with Seed Vault.” The primary account and the genesis token are coupled at setup, on this page. The page does not describe what happens to the token if the phone is wiped, sold, or lost. That silence is a limit, not a hidden answer.',
  'A reader who stops at “hardware-level” will miss the operational sentence. Every signature needs a fresh approval. The key does not sign because an app in the background asked politely. That is the property that makes a vault different from a hot key in an application sandbox, and it is the property this page actually states. What the page does not state is the failure mode: what the user sees if the secure environment and the Android prompt disagree, who can update the service, and which party can replace the prompt. Those are the next documents. They were not this one.',
 ],
 says=[
  'Seed Vault is described as a system service backed by a secure execution environment, with an explicit and/or between processor modes and auxiliary coprocessors.',
  'Keys, seeds, and secrets never leave that environment, while Android UI components handle the user interaction.',
  'Every signing operation requires a biometric fingerprint or a PIN.',
  'dApps are told to use Mobile Wallet Adapter. The Seed Vault SDK is for wallet developers and includes a simulator for ordinary Android devices.',
  'The built-in Seed Vault Wallet is created during onboarding and holds the Seeker Genesis Token.',
 ],
 paid=['This page has no fee, no reward, and no revenue share.'],
 decides=[
  'The user must approve each signature. The page does not name an administrator who can sign without that approval.',
  'Wallet developers may integrate the SDK directly. dApp developers are pointed at Mobile Wallet Adapter instead.',
 ],
 limits=[
  'The page does not identify a chip, a certification, or a vendor for the secure execution environment.',
  'It does not say the transaction preview is rendered inside the secure environment. It attributes the UI to Android.',
  'The simulator is a testing tool on this page. A passing simulator run is not evidence about Seeker hardware.',
  'No phone was opened for this reading.',
 ],
 sources=[dict(label='Seed Vault, Solana Mobile docs', url='https://docs.solanamobile.com/solana-mobile-stack/seed-vault', note='HTTP 200 on 17 Nov 2026. Last modified on the docs site: 26 October 2026.')],
 related=['the-phone-that-calls-itself-a-hardware-wallet', 'eight-seeds-and-saga-is-still-in-the-sentence'],
)

R(
 title='Eight Seeds, and Saga Is Still in the Sentence',
 desk='chain-watch', desk_name='Chain Watch', feature='The Fine Print',
 desc='The Seed Vault help page allows eight seeds on Seeker and on Saga, each with its own password. No device was checked.',
 deck='A help-centre article from 9 July 2025 still covers Saga as well as Seeker, and it puts a number on the vault: eight seeds, not one.',
 question='What does the help page actually let a person store, separate, and approve?',
 paragraphs=[
  'The help article is dated 9 July 2025 and it is filed under Security and Best Practices. Its first sentence is broader than the 2026 developer page. Seed Vault, it says, “is a built-in security feature on Solana Seeker and Saga devices” that safeguards “secrets, such as seed phrases and private keys.” It “operates within the phone’s most secure hardware environment—completely isolated from Android and other apps” so that the secrets stay protected “even if the operating system is compromised.” The developer page retrieved in November 2026 speaks about Seeker and about Android drawing the prompt. This older help page speaks about both phones and about isolation from Android even when the operating system is compromised. The two sentences are not the same claim. This reading does not pick a winner. It records that both were still on the public web on 17 Nov 2026.',
  'The number is the useful part. Secure storage “stores up to 8 seeds (12- or 24-word phrases) in a protected environment, encrypted and isolated from Android and apps.” Eight is not a metaphor. A person can keep more than one phrase. The next bullet tells you why that might matter. “Each seed is secured with a unique password and optional biometrics (e.g., fingerprint). You can set stronger security for long-term holdings or faster access for day-to-day accounts.” The vault, on this page, is not one identity. It is up to eight, and the lock on each can be different. A day-to-day account can be made easier than a long-term one. The page does not say what “easier” costs if the easier factor is the one a thief can satisfy.',
  'Full user control, in the article’s heading, means “manage exactly which apps can access each seed.” The point of that, the article says, is “privacy and separation between different wallets.” An application is not granted the phone. It is granted a seed, or it is not. The signing sentence matches the developer page in spirit and adds the password the developer page also allows via PIN. “Wallet apps submit a signing request to the Seed Vault. You authorize it with your password or biometrics, and the Vault signs the transaction without ever exposing your private key.” The key stays. The app receives a signature, not the phrase.',
  'The last feature is the one a person switching apps will feel. “On a traditional phone, switching wallet apps often means manually copying and pasting your seed phrases.” The article calls that “risky and error-prone.” With Seed Vault, “there’s no need to expose sensitive information. You just approve access using your password or fingerprint, making migration between apps both safer and more convenient.” The migration the page describes is an approval, not a paste. That is a real difference if the approval dialog tells the truth about which app is asking. The page does not exhibit the dialog. It describes the intended path.',
  'Related articles listed at the bottom, and not opened for this reading, include setting up the wallet, best practices for the seed phrase, restoring an existing wallet, what to do if a Seeker is lost or stolen, and how to re-import a renamed or renumbered seed. The titles alone are a map of the failure cases the help centre expects: loss, theft, and a seed whose name no longer matches. This reading does not summarise pages it did not retrieve. The titles are evidence of what the help centre thinks is adjacent, not evidence of what those articles conclude.',
  'Eight seeds on a phone that also runs a store is a cultural fact as much as a technical one. The help page is offering a way to keep a spending account and a savings account under different locks without pasting phrases into chat. Whether people use it that way is not in the article. The article’s instruction is the part a newspaper can print.',
 ],
 says=[
  'The 9 July 2025 help article says Seed Vault is on both Seeker and Saga.',
  'It stores up to eight seeds, each a 12-word or 24-word phrase, encrypted and isolated from Android and from apps.',
  'Each seed has its own password and optional biometrics, so a long-term holding and a day-to-day account can be locked differently.',
  'Apps are granted access per seed. Signing requires a password or biometrics, and the private key is not exposed.',
  'Moving between wallet apps is described as an approval, not as pasting a seed phrase.',
 ],
 paid=['The help article names no fee and no reward.'],
 decides=[
  'The holder chooses the password and whether biometrics are enabled, per seed.',
  'The holder decides which apps may access each seed.',
 ],
 limits=[
  'The article is dated 9 July 2025. The developer page retrieved later does not repeat the number eight or the word Saga. This reading does not know which sentence a current device follows.',
  'Isolation “even if the operating system is compromised” is the help page’s claim. It was not tested here.',
  'The related help articles were not opened.',
 ],
 sources=[dict(label='Understanding and using Seed Vault features', url='https://wallet-help.solanamobile.com/en/articles/11727979-understanding-and-using-seed-vault-features', note='HTTP 200 on 17 Nov 2026. The article date on the page is 9 July 2025.')],
 related=['seed-vault-is-a-system-service-not-a-second-gadget', 'the-blog-says-non-transferable-the-token-doc-describes-a-transfer'],
)

R(
 title='Double-Tap Is a Fingerprint on the Phone You Already Hold',
 desk='culture', desk_name='Internet culture', feature='The Fine Print',
 desc='Solana Mobile’s wallet post says a double-tap and a fingerprint sign every trade. The paper did not tap a phone.',
 deck='The 14 July 2026 post sells a gesture. The gesture is the entire approval ceremony: side button, finger, done. The post also says Solflare built the wallet that sits on the vault.',
 question='What does the Seed Vault Wallet post say the human actually does, and who does it say built the software?',
 paragraphs=[
  'The post is dated 14 July 2026 and it is written in the company’s voice. It opens with a dilemma it wants to be the answer to: “users have historically been forced to choose between security and convenience,” either “a hardware wallet that requires carrying multiple devices and complex workflows” or “software wallets that expose private keys to countless attack vectors.” Solana Mobile “built the Seed Vault Wallet to solve this problem for the Solana Seeker.” The next sentence names the partner. “To achieve it, we partnered with Solflare — a team that understands Solana users better than anyone — to create a mobile wallet that plugs directly into the Seeker’s Seed Vault hardware implementation.” The post thinks this is “the first mobile wallet that provides hardware-level security without sacrificing the seamless experience people expect from their phones.” “We think” is in the post. It is not a survey.',
  'Any mobile Solana wallet, the post says, will work on a Seeker. Seed Vault Wallet is “the only one that’s built specifically for your device,” and the post calls it “the most secure and seamless way to transact in all of Web3 mobile.” Superlatives are the post’s, and this reading does not adopt them. The exclusive function the post adds is not a market. “It’s the home to your Genesis Token, which is the key to unlocking rewards and exclusives throughout the Solana ecosystem.” The wallet is the door for a token that other wallets, on this account, do not house.',
  'The architecture section splits the phone in two, more concretely than the developer doc. “Seed Vault Hardware: A dedicated security module integrated to your phone’s secure element that stores private keys in a Trusted Execution Environment. This hardware vault operates independently from Android and remains isolated from all apps and processes on your device.” “Seed Vault Wallet App: The software interface that communicates with the Seed Vault hardware.” The post uses “secure element” and “Trusted Execution Environment” as if they were one object. The developer doc said processor modes and/or auxiliary coprocessors. A secure element is a specific kind of claim. The post makes it. The doc page retrieved the same day does not use those two words. Both pages are the company’s. They are not the same sentence.',
  'Then the gesture. “Every Seed Vault Wallet transaction follows the same simple pattern: double-tap the side button, place your finger on the sensor, and confirm.” Swaps, staking, and NFT mints all use that pattern. “The hardware fingerprint sensor connects directly to the Seed Vault. Your biometric data authorizes transactions at the hardware level.” The post also says the biometric system “operates independently of Android’s fingerprint features,” a “dedicated crypto authentication layer that works even if your phone’s main security is compromised.” That is a stronger isolation claim than “Android draws the prompt.” It says the fingerprint check for crypto is not Android’s ordinary fingerprint check. This reading did not watch a compromise. It can say the post asserts a separate layer.',
  'Setup is where the romance meets a piece of paper. A new wallet “generates fresh private keys directly in the Seed Vault hardware and provides a 12-word recovery phrase. Write this phrase on the included Seed Card and store it securely.” Importing an existing wallet means typing “your current Solana wallet’s seed phrase” into the device. The post says a new wallet is “the most secure, as the seeds will be freshly generated and only on your Seeker device.” The import path, by that logic, starts with a phrase that has already lived somewhere else. The post still offers the import. It does not describe how the typed phrase is wiped from the screen, the keyboard, or memory.',
  'Recovery, later, walks back any fantasy that the phone is the only copy that matters. “Your seed phrase provides complete wallet recovery on any Solana-compatible device. However, Seeker-specific features like your Genesis Token and enhanced security remain tied to the hardware.” Lose or destroy the phone and the phrase restores a wallet, not the phone’s privileges. “While the Seed Vault protects against most attack vectors, physical loss or destruction of your phone requires seed phrase recovery.” “Most” is the post’s quantifier. It is not a list.',
  'The cultural point is the gesture’s smoothness. A culture that rewards speed will like a double-tap that works for a swap and for a signature it does not understand. The post says the wallet displays “transaction details and fee estimates,” “recipient addresses and amounts,” “smart contract interactions and permissions,” and “security warnings for suspicious activity,” and only then the double-tap. The order on the page is details first, finger second. Whether the screen is readable in a hurry is not a fact this page can settle. The page’s own design intent is that the same ceremony covers every application, including ones that “recognize Seeker users automatically, often providing enhanced features, exclusive access, or improved rewards.” A gesture that unlocks a reward is still a signature. The post does not say the reward line is shown with the same weight as the fee.',
 ],
 says=[
  'The 14 July 2026 post says Solana Mobile partnered with Solflare to build Seed Vault Wallet on Seeker’s hardware implementation.',
  'It describes a secure element and a Trusted Execution Environment isolated from Android, and a wallet app that never lets the private key leave that hardware.',
  'Approval is a double-tap of the side button plus a fingerprint, for swaps, staking, and mints alike.',
  'A new wallet yields a 12-word phrase to be written on an included Seed Card. Importing means entering an existing phrase.',
  'The post says the phrase restores the wallet on any Solana-compatible device, while the Genesis Token and the enhanced security stay tied to the hardware.',
 ],
 paid=[
  'The post says the Genesis Token unlocks rewards and exclusives. It does not price them.',
  'It says applications may offer enhanced features or improved rewards to recognised Seeker users. It does not name a payer.',
 ],
 decides=[
  'The holder double-taps and authenticates. The post says the wallet shows details before that gesture.',
  'Solana Mobile names Solflare as the partner that built the wallet software. The post does not describe a contract, a revenue share, or an exit.',
 ],
 limits=[
  '“Secure element” appears in this post and not in the developer doc retrieved the same day. This reading does not resolve the wording.',
  '“Most attack vectors” is not a catalogue.',
  'No phone was tapped. The gesture is the post’s description, not an observation.',
  'Superlatives in the post (“most secure,” “first”) are the company’s, not a finding.',
 ],
 sources=[dict(label='Seed Vault Wallet — Solana Seeker’s Native Mobile Wallet', url='https://solanamobile.com/blog/seed-vault-wallet-solana-seekers-native-mobile-wallet', note='HTTP 200 on 17 Nov 2026. The post is dated 14 July 2026.')],
 related=['the-phone-that-calls-itself-a-hardware-wallet', 'the-blog-says-non-transferable-the-token-doc-describes-a-transfer'],
)

R(
 title='The Blog Says Non-Transferable. The Token Doc Describes a Transfer',
 desk='investigations', desk_name='Investigations', feature='Claim Check',
 desc='A July 2026 post calls the Genesis Token non-transferable. The developer doc describes a transfer. The paper did not ask which sentence governs.',
 deck='Two Solana Mobile pages, both public on 17 Nov 2026, do not use the same verb for the same token. One forbids a transfer. One specifies one.',
 question='Which retrieved sentence governs whether a Seeker Genesis Token can move?',
 paragraphs=[
  'The wallet post of 14 July 2026 is unambiguous in its adjective. After wallet creation, “you’ll claim your Seeker Genesis Token — a unique, non-transferable NFT that proves device ownership to applications across Solana.” The product page agrees in spelling if not in hyphenation: “Each Seeker generates its own non-transferrable Genesis Token, which unlocks exclusive onchain rewards and experiences throughout the Solana Mobile ecosystem.” Two marketing surfaces, one claim. The token does not move. It proves a device. It unlocks rewards.',
  'The developer document retrieved the same day, titled Seeker Genesis Token, does not repeat the adjective. It says the token “is a unique NFT that represents a verified owner of a Seeker device. It can only be minted once per device and is minted into the primary account in a user’s Seed Vault Wallet.” Once per device is a supply rule. It is not, by itself, a transfer rule. The transfer rule comes in the next section, and it is a permission, not a ban. “The Seeker Genesis Token can only be transferred between a user’s wallet accounts on a permissioned basis within the Seed Vault Wallet. A transfer occurs when a user changes their primary account in the Seed Vault Wallet.” The mint address “remains the same when it is transferred.”',
  'So the token can move, on the developer page, and the movement that counts is a change of primary account inside one person’s Seed Vault Wallet. It is not described as a sale, a gift to a stranger, or an open transfer on any marketplace. “Permissioned” and “within the Seed Vault Wallet” are the fences. A reader who only saw the blog would think the fence is a wall. A reader who only saw the doc would not know the blog is still calling the wall a wall.',
  'The developer page then explains why the mint address matters more than the wallet that currently holds the token. Its anti-sybil example is an in-app rewards claim that wants to pay once per device. The app should check three things. The connected wallet owns a Seeker Genesis Token. The user proves ownership by signing a message. The token “has not been previously used to claim a reward,” which means checking that its mint address has not been seen before. “Step 3 is crucial to exclude wallets that have previously claimed the reward on another wallet (and then transferred the SGT to a new wallet).” The document’s own example assumes a transfer has happened. A non-transferable token would not need step 3 in that form.',
  'This is the kind of discrepancy a newspaper can print without a phone call, and should not pretend to close without one. The blog and the product page are newer or older depending on which date you trust. The blog is dated. The product page, as retrieved, is not. The developer page carries no date in the markdown that was fetched. Last-modified headers were not compared. Nobody at Solana Mobile was asked which sentence they want a developer to code against. The paper’s rule is that silence is not agreement. Here the silence is the company’s, because the company was not asked, and the disagreement is already on the public web.',
  'What a developer should do, if they follow the page that contains code, is treat the mint address as the durable identity and expect the token to be able to change wallets inside the vault. What a holder should believe, if they follow the blog, is that the token cannot be transferred at all. Both instructions cannot be the whole truth. Printing both is the finding this reading is allowed to have. Declaring which implementation is on a device in a pocket would be a report. No device was inspected.',
 ],
 says=[
  'The 14 July 2026 wallet post calls the Seeker Genesis Token a unique, non-transferable NFT.',
  'The Seeker product page calls it a non-transferrable Genesis Token.',
  'The developer doc says the token can be transferred between a user’s own wallet accounts inside Seed Vault Wallet when the primary account changes, and that the mint address stays the same.',
  'The same doc’s anti-sybil example tells apps to remember the mint address precisely because a token might be transferred to a new wallet after a claim.',
 ],
 paid=['The marketing pages say the token unlocks rewards. They do not name an amount or a payer.'],
 decides=[
  'On the developer page, a user changes primary account inside Seed Vault Wallet and that change is the transfer.',
  'An app that wants one claim per device is told to decide based on the mint address, not the current wallet.',
 ],
 limits=[
  'Solana Mobile was not asked which page governs.',
  'No token account was read on-chain for this piece.',
  '“Permissioned” is not defined on the page beyond “within the Seed Vault Wallet.”',
 ],
 sources=[
  dict(label='Seed Vault Wallet post', url='https://solanamobile.com/blog/seed-vault-wallet-solana-seekers-native-mobile-wallet', note='HTTP 200 on 17 Nov 2026. Dated 14 July 2026.'),
  dict(label='Seeker product page', url='https://solanamobile.com/seeker', note='HTTP 200 on 17 Nov 2026.'),
  dict(label='Seeker Genesis Token docs', url='https://docs.solanamobile.com/solana-mobile-stack/seeker-genesis-token.md', note='HTTP 200 on 17 Nov 2026. The markdown page was read.'),
 ],
 related=['anti-sybil-is-a-mint-address-not-a-face', 'double-tap-is-a-fingerprint-on-the-phone-you-already-hold'],
)

R(
 title='Anti-Sybil Is a Mint Address, Not a Face',
 desk='power', desk_name='Power and politics', feature='The Fine Print',
 desc='The Genesis Token doc tells apps to remember a mint address, not a person. A wallet may hold more than one. No app was tested.',
 deck='The page that explains how to recognise a Seeker owner also explains how that recognition fails if you only check the wallet in front of you.',
 question='What does “one per device” mean once the token is allowed to move between a user’s own accounts?',
 paragraphs=[
  'The developer page’s anti-sybil example is the most politically interesting paragraph in the Seeker stack, and it is written as an implementation note. An application wants to give a reward once per device. Owning the token is not enough, because the token can arrive in a wallet that did not mint it. Signing a message is not enough, because a signature proves control of a wallet, not uniqueness of a device. The durable identifier the page offers is the mint address. Record it. If you have seen it, you have paid this device already, even if the token now sits somewhere else.',
  'The page is explicit that a wallet can hold more than one Seeker Genesis Token. “A wallet can hold more than one SGT, so keep every mint: if one has already claimed, another may not have.” The function it recommends, getSeekerGenesisTokens, “returns the mint address of every SGT the wallet currently holds, or an empty list.” It “skips token accounts with a zero balance, which a wallet keeps after transferring its SGT out.” A zero-balance account is a ghost of a token that left. An app that treated the ghost as ownership would be wrong, and the library’s authors say they skip it. An app that treated a single boolean, hasSeekerGenesisToken, as a once-per-human check would also be wrong, because the page says a wallet may hold several and because a person may hold several wallets. The boolean answers a narrower question: does this wallet hold at least one right now?',
  'The token itself is not a plain SPL token. “The Seeker Genesis Token implements Token Extensions (formerly Token-2022).” The extensions named are Metadata Pointer, and Token Group Member and Pointer. The group address and the metadata address printed on the page are the same base58 string, GT22s89nU4iWFkNXj1Bw6uYhJJWDRPpShHt4Bk8f99Te. An individual token example is also printed, 5mXbkqKz883aufhAsx3p5Z1NcvD2ppZbdTTznM6oUKLj, as an explorer link. This reading did not open the explorer. The addresses are what the doc prints. Group membership is how the library “verifies each token.” A token that merely looks like an NFT is not, on this page, a Seeker Genesis Token. It has to belong to the group.',
  'The package is @solana-mobile/skr-genesis-token, installed alongside @solana/kit, and the page says it “works with any mainnet RPC endpoint.” The code sample is short. It creates an RPC client from an environment variable and maps the returned tokens to their mints. The licence line says the samples are Apache 2.0. None of that is a privacy policy. An app that records every mint it has ever paid has built a list of devices it has recognised. The page calls that an anti-sybil measure. It does not call it a person, and it does not say how long the list should live.',
  'Power, in this design, sits with whoever keeps the list and with whoever can mint. The mint happens “once per device” into “the primary account.” The page does not say what a user can do if the primary account is created under a cloud restore, a warranty replacement, or a second-hand phone. Those are the cases where “once” becomes a fight. They are not specified here. What is specified is the check a careful app must perform, and the ways a lazy check will pay twice or pay the wrong wallet.',
  'A culture that treats a phone as a personality will want the Genesis Token to mean “a real human, early, worthy of a reward.” The document will not support that sentence. It will support “a mint address we have not paid yet, held by a wallet that can sign, currently, and recognised as a member of this token group.” That is a smaller fact. It is the one the page is willing to stand behind, and it is the one a reward programme can audit.',
 ],
 says=[
  'The doc says one token is minted per device, into the primary Seed Vault Wallet account.',
  'It can move between that user’s accounts inside the wallet, and the mint address does not change.',
  'An anti-sybil claim should check ownership, a signature, and whether that mint address has already been paid.',
  'A wallet may hold more than one token. Zero-balance leftovers after a transfer are skipped by getSeekerGenesisTokens.',
  'The token uses Token Extensions, including a group membership the library checks. The group address is printed on the page.',
 ],
 paid=['The page describes a rewards claim as the example. It does not set an amount, a token, or a sponsor.'],
 decides=[
  'The application decides whether a mint address has already been paid, by keeping its own record.',
  'The user decides to change primary account, which is the transfer the page describes.',
  'The library decides group membership. The page does not say a user can appeal that check.',
 ],
 limits=[
  'No reward app was run. The three-step check is the doc’s example, not a field test.',
  'The explorer links were not opened.',
  'The page does not define what happens to “once per device” if the device is replaced.',
 ],
 sources=[dict(label='Seeker Genesis Token docs', url='https://docs.solanamobile.com/solana-mobile-stack/seeker-genesis-token.md', note='HTTP 200 on 17 Nov 2026.')],
 related=['the-blog-says-non-transferable-the-token-doc-describes-a-transfer', 'skr-inflation-starts-at-ten-percent-and-does-not-compound'],
)

R(
 title='SKR Inflation Starts at Ten Percent and Does Not Compound',
 desk='money', desk_name='Money and markets', feature='The Fine Print',
 desc='The SKR doc sets inflation at 10 percent, decaying 25 percent a year to a 2 percent floor, and says it is linear. No balance was queried.',
 deck='The token page is short. The numbers it does publish are about issuance, epochs, and a cooldown, not about a price.',
 question='What does the SKR page say a holder is actually owed, and who do they have to delegate to in order to be owed it?',
 paragraphs=[
  'The SKR page introduces the asset in a sentence that does several jobs at once. “SKR is the native asset of the Solana Mobile ecosystem. It distributes control, powers curation, and aligns incentives across builders, users, and hardware partners.” The next line is the political theory: “Via SKR, the community governs, builders keep what they earn, and users own a stake in the value they create.” Those are purpose sentences. They do not specify a vote, a fee switch, or a cap table. A reading that treated them as a constitution would be inventing the articles. The page’s concrete constitution is the parameter list underneath.',
  'The mint address is printed: SKRbvo6Gf7GondiT3BbTfuRDPqLWei4j2Qy2NPGZhW3. The token type is “SPL Token,” not Token-2022. That is a different standard from the Genesis Token, which the other page says uses Token Extensions. SKR, on this page, is an ordinary SPL token with a published mint. This reading did not fetch the mint account, so the supply, the freeze authority, and the mint authority are not facts here. The page does not print them.',
  'Staking is where the page becomes a schedule. “SKR holders can stake their tokens to participate in the ecosystem. Stakers delegate their stake to a Guardian.” Participation, in the only mechanism this page defines, is delegation to a guardian, not a direct vote on a feature. Inflation “starts at 10% and decays 25% per year until reaching a 2% terminal rate.” And then the sentence a sloppy annualised chart will get wrong: “Inflation is linear (not compounding).” A linear schedule that decays by a quarter of itself each year until a floor is a specific machine. This reading will not turn it into an annual percentage yield, because the page does not say what the percentage is a percentage of, beyond the word inflation, and it does not say who receives the new tokens. It says the rate starts, decays, and stops decaying at two percent, and that the decay is not compound interest.',
  'Time is specified more tightly than yield. “Staking epochs are 2 days.” “Unstaking is immediate and tokens stop earning rewards right away.” “There is a 48-hour cooldown to withdraw after unstaking.” Immediate unstaking plus a two-day wait to withdraw is a pair, not a contradiction. The tokens leave the earning set at once. They do not become spendable at once. A person who needed them inside the hour would find, on this page, that the earning stops and the withdrawal does not start. The page does not say what happens to a reward already accrued at the moment of unstaking, beyond “stop earning.”',
  'Four addresses are printed and worth keeping as addresses rather than as folklore. The staking programme is SKRskrmtL83pcL4YqLWt6iPefDqwXQWHSw9S9vz94BZ. The stake config is 4HQy82s9CHTv1GsYKnANHMiHfhcqesYkK6sB3RDSYyqw. The stake vault is 8isViKbwhuhFhsv2t8vaFL74pKCqaFPQXo1KkeQwZbB8. The Solana Mobile Guardian Pool is DPJ58trLsF9yPrBa2pk6UaRkvqW8hWUYjawe788WBuqr. The page links a staking portal and a white paper. Neither of those was the page retrieved for this reading. The portal is where the page says a holder can stake. What the portal shows on a given day is not in this record.',
  '“Builders keep what they earn” is the sentence a sceptical reader came for, and the page does not show the earning. It shows an inflation schedule, a guardian as the delegate, a two-day epoch, and a two-day cooldown. Control, on the only operational paragraph, is delegated. A guardian is a person or an operator the page does not name, except by the existence of a Solana Mobile Guardian Pool address. Who may be a guardian, how a guardian is removed, and what a guardian can do with delegated stake besides “participate” are not on this page. A later card on a different post names Helius and Jito as the first third-party guardians. That card was not this document, and it is not smuggled in as this document’s rule.',
 ],
 says=[
  'SKR is named as the native asset of the Solana Mobile ecosystem and as an SPL token, with a printed mint address.',
  'Holders stake by delegating to a Guardian.',
  'Inflation starts at 10 percent, decays 25 percent per year, and reaches a 2 percent terminal rate. The page says the inflation is linear, not compounding.',
  'Epochs last 2 days. Unstaking is immediate and stops rewards at once. Withdrawal waits through a 48-hour cooldown.',
  'The staking programme, stake config, stake vault, and Solana Mobile Guardian Pool addresses are printed on the page.',
 ],
 paid=[
  'The page does not say who receives newly issued SKR.',
  'It says stakers earn rewards while staked and stop earning immediately on unstake. It does not define the reward unit beyond that.',
 ],
 decides=[
  'A holder decides to stake, to which guardian to delegate, and when to unstake.',
  'The page does not describe a vote. “The community governs” is not given a procedure here.',
 ],
 limits=[
  'The mint account was not read. Supply and authorities are unknown to this reading.',
  'The staking portal and the SKR white paper were not the pages retrieved.',
  'Linear inflation is not converted here into a yield, because the page does not give the base the percentage applies to beyond the word inflation.',
 ],
 sources=[dict(label='SKR, Solana Mobile docs', url='https://docs.solanamobile.com/solana-mobile-stack/skr.md', note='HTTP 200 on 17 Nov 2026. The markdown page was read. The linked white paper was not.')],
 related=['anti-sybil-is-a-mint-address-not-a-face', 'ledger-atom-is-still-written-in-the-future-tense'],
)

R(
 title='Ledger Atom Is Still Written in the Future Tense',
 desk='power', desk_name='Power and politics', feature='Claim Check',
 desc='The 14 October 2026 post says Ledger Atom will carry the Seeker app. The verbs are future. No device was reviewed.',
 deck='Solana Mobile’s partnership post announces a second house for the same store. It also announces figures for the first house. The figures are the company’s, and the device is not yet in the prose as a thing that exists.',
 question='What has the partnership post actually committed to, and which of its numbers did the paper not recount?',
 paragraphs=[
  'The post is dated 14 October 2026 and it says the announcement happened “live on stage at Ledger Op3n 2026 in Paris.” Solana Mobile “announced Ledger as its first hardware expansion partner. The Solana dApp Store and wallet will be combined into one Seeker app and integrated with Ledger Atom.” “Will be” is the tense of the integration. The post is not a review of a shipping product. It is a description of a plan made on a stage, plus a set of claims about Seeker’s past.',
  'The device, as specified here, “leverages Android Open Source Project (AOSP) alongside a Secure Element (EAL6+) running Ledger OS, with the display and touch control physically isolated from the Android operating system.” The Seeker app “will be integrated with this secure technology and preinstalled.” Signing “will happen in Ledger Atom’s Secure Mode, backed by the Secure Element and Ledger OS, so the transaction users confirm is the one they sign.” Isolation of the display from Android is the property the Seed Vault developer doc does not claim for the phone. This post claims it for a different device, in the future tense, and attributes the secure element rating EAL6+ to that design. This reading did not see a certificate. EAL6+ is the post’s parenthetical.',
  'Distribution is part of the security claim, and the post is specific. “Ledger Atom will only be sold directly on Ledger’s official site.” Reservations “are open now” at a Ledger address the post prints as ledger.com/seeker. Anti-tamper measures “will contain” methods “to help detect if the enclosure has been opened,” from packaging to the device. “Will” again. A reservation page is not a device. The post says the app will be “preloaded and featured on Ledger Atom’s home screen,” and that “1500+ dApps available today on Seeker” are “coming to Ledger Atom.” Coming is not arrived.',
  'The past-tense numbers are doing the work of proof. “Seeker has proven people will hold and use their assets from hardware built for it, with over $13B in transaction volume on Seeker, 154 million transactions, and over 1,500 apps on the Solana dApp Store.” The about section repeats a wider device count: “With over 200,000 devices sold and $13B+ in transaction volume.” The post also says Solana Mobile “shipped the Saga in 2023 and the Seeker in 2025.” A quoted passage attributed to Anatoly Yakovenko says the phone proved a community “shipping over a thousand apps with billions in transaction volume from over 100,000 users.” A quoted passage attributed to Ian Rogers of Ledger praises Seeker for making self-custody “feel natural on mobile.” These sentences are in the post. They are not interviews the paper conducted. The paper did not add the transaction volumes up, did not count the devices, and did not ask either speaker to confirm the wording. A company’s announcement is a source for what the company said. It is not, by itself, an audit.',
  'The industrial argument is the one that will outlive the keynote. “App stores are one of the least contestable markets in the world. A few companies decide what ships and take up to a 30% cut of every transaction. Solana Mobile built the Solana dApp Store to change that.” Developers, the post says, “can ship the crypto features other app stores often restrict, get reviewed in days instead of weeks.” “It was never supposed to live on just Seeker.” If you own a Seeker, “nothing changes.” If you build for Solana Mobile, “the same Solana dApp Store submission now reaches an expanded audience.” “Now” is a strong word next to so many wills. The submission’s reach, on the post’s own later sentences, expands when Atom ships. The post does not say a second store review is required. It also does not show a builder’s submission landing on an Atom device, because the device is still being described as forthcoming.',
  'There is a March 2026 prehistory inside the post. The partnership “builds on the hardware expansion Solana Mobile began in March 2026, when it opened the Solana Mobile Stack to Android manufacturers at Mobile World Congress in Barcelona.” SKR is “at the heart of it all, allowing users to be rewarded for participating in the ecosystem, developers for building and hardware manufacturers for integrating.” That is the same purpose language as the SKR doc, plus a new payee: the hardware manufacturer. The rate, the token, and the condition are not in this post. The existence of a third kind of recipient is.',
 ],
 says=[
  'The 14 October 2026 post says the Seeker app and dApp Store will be integrated with Ledger Atom, announced at Ledger Op3n in Paris.',
  'It describes Atom as AOSP plus a Secure Element rated EAL6+ running Ledger OS, with display and touch isolated from Android. The description is prospective.',
  'It says Atom will be sold only on Ledger’s site, and that reservations are open.',
  'It states Seeker figures: over $13B transaction volume, 154 million transactions, over 1,500 apps, and, in the about section, over 200,000 devices sold. A passage attributed to Anatoly Yakovenko says over a thousand apps, billions in volume, and over 100,000 users.',
  'It says other app stores take up to a 30 percent cut, and that the Solana dApp Store was built so the experience would not live only on Seeker.',
 ],
 paid=[
  'The post says users, developers, and hardware manufacturers are rewarded via SKR. It sets no rate.',
  'It contrasts a cut of up to 30 percent on other stores with its own store. It does not print the Solana dApp Store’s fee on this page.',
 ],
 decides=[
  'The post says a few companies decide what ships in ordinary app stores. It says Solana Mobile’s store reviews in days instead of weeks. It does not name the reviewers.',
  'Ledger, on this page, decides to sell Atom only on its own site. Solana Mobile decides the integration. Both are the post’s account.',
 ],
 limits=[
  'No Ledger Atom was handled. The device is described in the future tense.',
  'The volume, device, user, and app counts were not re-counted. They are the post’s figures, including a passage the post attributes to named people.',
  'The paper did not ask Yakovenko or Rogers to confirm the quotations.',
  'EAL6+ was not checked against a certificate.',
 ],
 sources=[dict(label='Solana Mobile announces Ledger as its first hardware expansion partner', url='https://solanamobile.com/blog/solana-mobile-announces-ledger-as-its-first-hardware-expansion-partner', note='HTTP 200 on 17 Nov 2026. The post is dated 14 October 2026.')],
 related=['skr-inflation-starts-at-ten-percent-and-does-not-compound', 'the-phone-that-calls-itself-a-hardware-wallet'],
)

R(
 title='Degen Mode Starts the Slider at 125 Times',
 desk='money', desk_name='Money and markets', feature='The Fine Print',
 desc='Flash Trade’s Degen Mode page starts the leverage slider at 125x and removes stop orders. The trading screen was not opened.',
 deck='The page that names itself after the culture also publishes the constraint it removes and the constraint it adds. The slider does not start at one.',
 question='What does the public Degen Mode page say a trader can no longer do, and where does it say the control begins?',
 paragraphs=[
  'Flash Trade’s own page calls Degen Mode an “ultra-high leverage trading environment designed for experienced traders seeking maximum position amplification.” It “removes traditional safety constraints while implementing strict risk controls to maintain platform stability.” The danger box is not subtle. “This feature is designed for expert traders only. The extreme leverage available can result in rapid and complete loss of capital. Only trade with funds you can afford to lose entirely.” A newspaper that covers leverage has to print the warning in the same piece as the multiple, because the multiple is the product and the warning is the term.',
  'The control a person meets first is not a text box. “Slider Range: Starts at 125x leverage minimum.” The page also says “Starting Leverage: 125x” and “Maximum Leverage: 500x liquidation threshold.” A slider that begins at one hundred and twenty-five is a design decision written down. You do not wander into this mode at two times and lean forward. The floor of the control is already a number most perpetual interfaces treat as a ceiling. The assignment board of this paper asks what a leverage slider lets a person do before they have read a disclosure, and it says no designer has been interviewed. This reading does not close that assignment. It reads one public page. The page puts the disclosure and the 125x floor in the same document. It does not say which one the interface shows first.',
  'What the mode removes is as important as what it multiplies. “No Limit Orders: Market orders only.” “No TP/SL Support: Take profit and stop loss orders unavailable.” “Cannot transition from normal mode using remove collateral.” Existing positions “must be closed before mode switching,” though “you can transition from Degen Mode to normal mode without restrictions” once that closing has happened. The limit-order tab is “completely hidden.” The tools a person would use to leave a position without watching it are the tools the page turns off. What remains is “instant execution at current market prices.”',
  'The costs are split in a way the headline “zero trading costs” does not survive. “Swap Fees: Completely eliminated on all trades.” “Position Fees: Standard open/close fees still apply.” Zero applies to the swap. It does not apply to the open and the close. A reader who repeats “zero fees” has dropped the second bullet. The page also says there is a “liquidation buffer” described as “extended maintenance margin requirements,” without putting the extension’s size in this document. The number lives, if it lives, on another page.',
  'The assets are a short list. SOL, BTC, and ETH. The table gives each a max leverage of 500, and then a max position size and a max exposure: SOL 100k and 450k, BTC 250k and 833k, ETH 100k and 375k. The page does not say what unit the k is, though the surrounding prose is about position size. This reading will not upgrade “100k” into a dollar measurement the page did not label. It will say the table prints those figures next to those assets, and that the page calls them strict upper limits “to manage platform risk,” with “automatic validation of position parameters” and a minimum position size that is only described as “higher entry requirements than normal mode.” Higher than what is not numbered here.',
  'The risk box adds the consequence of a slider with no stop. “Positions can be liquidated with minimal price movement.” “Limited risk management tools available.” “Potential for complete position loss within seconds.” “Strict position caps to protect overall system stability.” The caps protect the platform, on the page’s own wording. They are not described as a cap on the trader’s ambition for the trader’s sake. A culture that uses “degen” as a compliment will find its name on a mode that hides the limit-order tab and starts at 125x. The page is not embarrassed. It is also not vague about who the mode is not for.',
 ],
 says=[
  'Degen Mode is described as experimental, for expert traders, with a warning of rapid and complete loss.',
  'The leverage slider starts at 125x. The page lists a 500x liquidation threshold as the maximum.',
  'Swap fees are eliminated. Open and close position fees still apply.',
  'Limit orders and take-profit or stop-loss orders are unavailable. The limit-order tab is hidden. Positions must be closed before switching modes.',
  'The page’s table lists SOL, BTC, and ETH, each with max leverage 500, and prints max position and max exposure figures beside them.',
 ],
 paid=[
  'The page says standard open and close fees still apply. It does not restate the rate on this page.',
  'Swap fees inside this mode are described as eliminated.',
 ],
 decides=[
  'The trader chooses to enter the mode. The page says the slider does not offer a setting below 125x.',
  'The protocol, not the trader, hides limit orders and take-profit or stop-loss in this mode.',
 ],
 limits=[
  'The trading screen was not opened. The slider is the page’s description.',
  'No designer was interviewed. This is not the assignment “The Leverage Slider Is a Design Decision,” which remains unreported.',
  'The unit of the “100k” and “250k” figures is not defined on the page. They are not converted here.',
  'The size of the “extended” liquidation buffer is not on this page.',
 ],
 sources=[dict(label='Degen Mode, Flash Trade docs', url='https://docs.flash.trade/flash-trade/getting-started/degen-mode.md', note='HTTP 200 on 17 Nov 2026. The markdown page was read.')],
 related=['five-hundred-times-and-the-orders-turned-off', 'a-funded-wallet-that-says-zero-risk-and-then-describes-the-keys'],
)

R(
 title='Five Hundred Times, and the Orders Turned Off',
 desk='money', desk_name='Money and markets', feature='Claim Check',
 desc='Flash’s margin page sets Degen Mode at up to 500x initial on three assets, against 1000x maintenance. No position was opened.',
 deck='A second Flash page puts the 500x boast next to a maintenance multiple, a date, and a reminder that the slider in the interface is the live number.',
 question='What leverage does the margin framework actually publish, and which number does it tell the reader not to trust if the two disagree?',
 paragraphs=[
  'The margin framework page separates two floors. Initial margin is “the minimum collateral to open a position,” equal to position size times one over max initial leverage. Maintenance margin is “the minimum collateral to keep it open,” equal to position size times one over max maintenance leverage. Crossing the second triggers liquidation. The gap between them is “your buffer.” A mode that raises only the initial cap, and leaves maintenance far higher, is a mode that lets you open closer to the liquidation line. The page says this in a table rather than in a sermon.',
  'Standard initial leverage “caps at 100x on crypto markets and 200x on synthetic markets in the trade panel.” Degen Mode “raises the initial cap to 500x on SOL, BTC, and ETH.” Maintenance leverage on those same crypto majors is listed as 1000x. Forex pairs are listed at 200x initial and 2000x maintenance, with no Degen Mode column. Metals sit at 100 to 130x initial and 200x maintenance. Oil and gas sit at 7 to 12x initial and 50 to 100x maintenance. DeFi pool markets sit at 13 to 60x initial and 100x maintenance. Meme markets sit at 30x initial and 50x maintenance. Equities sit at 25x initial and 50x maintenance. The wild number is not evenly distributed. The page concentrates 500x on three crypto majors and leaves meme markets, the cultural centre of the word degen, at a 30x initial cap.',
  'Every one of those figures is fenced. “Values are per-market protocol parameters as of 2026-07-03 and are tuned over time; the leverage slider in the trade panel always shows the live limit for the selected market.” A reading that prints 500x as eternal is already out of date relative to the page’s own sentence. The page tells you the date of the snapshot and tells you the interface wins if the snapshot and the interface disagree. This reading did not open the interface. The snapshot is the record. The instruction to prefer the panel is also the record.',
  'There is a second way the buffer shrinks, and it does not require a move in the mid price. “During periods of extreme volatility, position pricing follows conservative principles: the oracle’s confidence interval is applied so that prices used for opening, closing, and liquidation calculations maximize liabilities and minimize assets for traders.” For longs, “the lower bound of the oracle confidence interval values your collateral and PnL.” For shorts, “the upper bound” prices the position, “reducing recognized profit while volatility is elevated.” The practical line the page adds is to “run lower leverage and keep collateral well above the minimum” because “liquidation distance is shorter than it looks.” A 500x initial cap and a confidence interval that marks your assets down are two different ways of standing nearer the exit. The page describes both.',
  'Who the buffer protects is a question the formulas answer indirectly. Maintenance margin is a protocol parameter. The trader does not set 1000x. The trader sets the initial leverage, inside a cap the protocol published, and then lives with a maintenance line the protocol also published. When volatility widens the oracle’s interval, the protocol’s pricing rule marks the account in the direction that makes liquidation more likely, not less. That is a choice. The page calls it conservative. Conservative for the pool and conservative for the trader are not the same direction, and the page’s own “maximize liabilities and minimize assets for traders” picks a direction.',
 ],
 says=[
  'Initial margin opens a position. Maintenance margin keeps it open. The page gives both as size divided by a max leverage.',
  'Degen Mode raises initial leverage to 500x on SOL, BTC, and ETH. Maintenance on those markets is listed at 1000x.',
  'Meme markets are listed at 30x initial and 50x maintenance. Forex maintenance is listed at 2000x. The table is dated 2026-07-03 and marked tunable.',
  'The trade panel’s slider is declared the live limit if it disagrees with the table.',
  'In extreme volatility the oracle confidence interval is applied to maximize trader liabilities and minimize trader assets.',
 ],
 paid=['The margin page does not set a fee. It sets how close a position stands to a liquidation, which the liquidation page treats as a payment to the pool.'],
 decides=[
  'The protocol publishes the caps and the volatility pricing rule.',
  'The trader chooses a leverage inside the cap. The page says the panel, not this table, is the live control.',
 ],
 limits=[
  'The trade panel was not opened on 17 Nov 2026. The 2026-07-03 table may already have moved.',
  '500x is an initial cap on three assets in this table, not a description of every Flash market.',
  'No position was opened and no liquidation price was computed from a live oracle.',
 ],
 sources=[dict(label='Margin Framework, Flash Trade docs', url='https://docs.flash.trade/flash-trade/flash-trade-protocol/perpetuals-specifications/margin-framework.md', note='HTTP 200 on 17 Nov 2026.')],
 related=['degen-mode-starts-the-slider-at-125-times', 'the-maintenance-margin-is-not-returned'],
)

R(
 title='A Funded Wallet That Says Zero Risk and Then Describes the Keys',
 desk='investigations', desk_name='Investigations', feature='Claim Check',
 desc='Flash’s Funded Wallet page says zero risk to your funds, then says Flash holds the keys and the principal. No code was redeemed.',
 deck='The headline offers the house’s money and none of the loss. The same page says you do not hold the keys, you do not keep the starting balance, and the clock starts when you trade.',
 question='Which sentences on the Funded Wallet page limit the sentence “zero risk to your own funds”?',
 paragraphs=[
  'The page’s title block is a slogan. “Trade with Flash Trade’s capital. Keep the profits. Zero risk to your own funds.” A hint underneath repeats the offer: “We fund the stack. You keep the gains.” If a reading stopped there it would be an advertisement. The rest of the page is the term sheet, and the term sheet does not say the trader has nothing at stake in any sense a careful person would recognise. It says the money that can be lost is not the trader’s deposit.',
  'The mechanics table is plain. Starting capital: the wallet “is pre-funded with USDC.” Time limit: “15 minutes from your first trade.” Profit split: “You keep 100% of profits above starting balance.” Markets: “All markets including Degen Mode (up to 500x).” Transaction fees: “Handled by the platform.” Wallet management: “No seed phrase or signing required.” A worked example uses round numbers the page itself invented as an illustration, not as a quote of a live account. Starting balance 100 USDC, end at 150, “your profit to keep” 50. The example is the page’s arithmetic. It is not a result the paper observed.',
  'The keys are the part a custody reading cannot skip. “No seed phrase — Flash Trade controls the wallet infrastructure.” “No transaction signing — Every trade executes seamlessly.” “No gas fees — Platform covers all transaction costs.” An FAQ asks “Do I need a connected wallet?” and answers “Yes. The Funded Wallet is fully abstracted — external wallet connection required but is not used for trading can create a social account through Privy.” The sentence is ungrammatical on the page. This reading will not repair it into a cleaner product claim. What it clearly contains is the name Privy, a social account, an external wallet connection that is required, and a statement that the external wallet is not what trades. Flash controls the infrastructure. The trader does not sign. A mode that calls itself zero risk because the principal is the house’s is also a mode in which the trader cannot inspect a signature, because there is no signature of theirs to inspect.',
  'Loss is defined narrowly and then repeated. “If the balance drops below the starting amount, you simply don’t profit — but you don’t owe anything either.” “Can I withdraw the initial funded amount? No. Only profits above the starting balance are withdrawable. The initial capital belongs to Flash Trade.” Zero risk, unpacked, means you cannot finish owing the house the stake it lent you. It does not mean you control the account. It does not mean a profit is automatic. It does not mean the fifteen minutes are a suggestion. “The 15-minute window is strict.” The timer “starts on your first trade, not when you claim the wallet.” “Each code grants access to one Funded Wallet session.” Codes “are distributed through Flash Trade promotions, partnerships, and community events.” A code is a key to someone else’s wallet for a quarter of an hour.',
  'Degen Mode is not fenced off from this arrangement. The page says the funded session can use it, “125x–500x,” and then warns that “high leverage significantly increases liquidation risk.” The same page that removed the trader’s deposit invites the trader into the mode that removed stop orders. Limit orders and take-profit or stop-loss “are available during your Funded Wallet session,” with a warning that if the starting amount “is not greater than $10 you will not be able to use these features.” Ten dollars is a threshold for tools, not a promise that a session is funded with more than ten dollars. The page’s example used one hundred. The page does not say every code loads one hundred.',
  'A culture that treats a coupon as courage will like this product. The page is honest enough, in the body, to say whose money it is and who holds the keys. The headline is not as careful as the FAQ. Printing them together is the check. No code was entered. No Privy account was created. The contradiction a reader needs is already in the prose the company published.',
 ],
 says=[
  'The page says “zero risk to your own funds” and “you keep the gains.”',
  'It also says Flash controls the wallet, there is no seed phrase and no transaction signing, and the starting capital remains Flash’s.',
  'Profits above the starting balance are the trader’s. Losses below it are not a debt. The example on the page is 100 USDC growing to 150, of which 50 is the profit.',
  'The timer is 15 minutes from the first trade. Each code is one session. The page names Privy for a social account.',
  'Degen Mode up to 500x is included. Order tools are unavailable if the starting amount is not greater than 10 dollars.',
 ],
 paid=[
  'The trader is paid only the amount above the starting balance, after the session.',
  'The starting USDC belongs to Flash. Gas, the page says, is handled by the platform.',
  'A code comes from promotions, partnerships, or community events. The page does not say what those partners are paid.',
 ],
 decides=[
  'Flash decides the starting amount, the markets, and the infrastructure, including the keys.',
  'The trader decides when the first trade starts the clock, and what to do inside fifteen minutes.',
 ],
 limits=[
  'No code was redeemed and no session was observed.',
  'The ungrammatical Privy sentence is quoted as a broken sentence, not repaired into a policy.',
  '“Zero risk” is the page’s headline. The finding is the set of sentences that sit under it, not a measurement of anyone’s loss.',
 ],
 sources=[dict(label='Funded Wallet, Flash Trade docs', url='https://docs.flash.trade/flash-trade/getting-started/funded-wallet.md', note='HTTP 200 on 17 Nov 2026.')],
 related=['degen-mode-starts-the-slider-at-125-times', 'a-session-key-that-can-trade-and-cannot-withdraw'],
)

R(
 title='A Hundred Times Leverage Dies on a Quarter of a Percent',
 desk='money', desk_name='Money and markets', feature='The Fine Print',
 desc='Flash’s max-profit page caps major-crypto profit at 25 percent of size. At 100x that is a 0.25 percent move. No trade was placed.',
 deck='The page that limits how much a winning position can be paid is more important than the page that advertises the multiple. The cap binds early, and the page shows the arithmetic.',
 question='Who sets the maximum a winning perpetual can pay, and how soon does the published cap arrive?',
 paragraphs=[
  'Flash’s max-profit page begins with a distinction a leverage advertisement does not make. “Every position has a hard cap on how much profit it can realize. That cap is set when the position opens, based on how much collateral the pool sets aside to pay you out.” It is “separate from your leverage, your liquidation price, or your collateral.” You can be right about the direction, still be far from liquidation, and still be finished, because the pool locked a payout on the way in and will not pay past it.',
  'The lock is a formula the page prints. Locked dollars equal size in dollars times max payoff in basis points, divided by 10,000, plus collateral in dollars. The first term is “the maximum the pool will pay out as profit.” The second “ensures your own collateral is always fully covered.” At settlement, payout is the minimum of profit plus collateral, and that locked amount. Maximum profit is therefore size times the payoff parameter over 10,000. The page calls the price where this binds the max profit price. For a long it is entry plus max profit over size. For a short it is entry minus that quantity. “For shorts with a 100% max payoff, the max profit price effectively reaches $0.” A short that is allowed a one-hundred-percent payoff only finishes its cap if the asset is worth nothing.',
  'The parameter is not one number for every market, and the page dates it. “As of 2026-07-03; tunable: major crypto markets — BTC, ETH, SOL — cap profit at 25% of position size; most alt, meme, and synthetic markets cap at 50–100%; a few markets run higher on one side.” The position panel “shows your position’s live max profit price.” Again the panel is the authority and this reading did not open it. The dated sentence is what can be printed.',
  'The worked consequence is the sentence that should be taped above a 100x button. “On major crypto markets the 25% cap binds sooner than you might expect at high leverage: a 100x BTC long hits its max profit on a 0.25% favorable move.” The page also says this is why “a take-profit order cannot be placed past the max profit price.” The interface will not let you aim a take-profit beyond a profit the pool has refused to escrow. A trader who thinks in multiples hears 100x and imagines a doubled account on a one percent move. The page’s arithmetic says the major-crypto cap arrives at a quarter of one percent, and then the position stops earning even if the market keeps going.',
  'Why the pool does this is stated, and it is about the pool. “The cap is most relevant for synthetic markets — forex, commodities, and tokenized equities — where the pool is backed by USDC rather than the native asset, protecting the pool from outsized payouts.” The beneficiary of the cap, in that sentence, is the pool. The trader meets it as a ceiling. On majors the same idea “binds sooner” precisely because leverage is high and the payoff fraction is the smaller one, 25 percent of size. A culture of wild multiples and a pool that escrows a quarter of size are the same market described from two chairs. The page sits in both and does not apologise.',
 ],
 says=[
  'Every position has a max-profit cap set at open, separate from leverage and from liquidation.',
  'The pool locks size times max payoff over 10,000, plus collateral. Payout cannot exceed that lock.',
  'As of 2026-07-03, BTC, ETH, and SOL cap profit at 25 percent of position size. Most alt, meme, and synthetic markets cap at 50 to 100 percent. The parameter is tunable.',
  'The page says a 100x BTC long hits that cap on a 0.25 percent favorable move, and that a take-profit cannot be placed past the max-profit price.',
  'A short with a 100 percent max payoff only meets the cap if the price reaches zero.',
 ],
 paid=[
  'The trader is paid at most the locked profit. Further favorable movement is not paid.',
  'The page says the cap protects a USDC-backed pool from outsized payouts on synthetics.',
 ],
 decides=[
  'Max payoff is a per-market parameter the page calls tunable. The trader does not set it.',
  'The position panel is declared the live display. This reading did not open it.',
 ],
 limits=[
  'No position was opened. The 0.25 percent figure is the page’s illustration for a 100x BTC long under a 25 percent cap, not a fill.',
  'The table is dated 2026-07-03. The page says it can change.',
  '“A few markets run higher on one side” is not itemised here.',
 ],
 sources=[dict(label='Max Profit, Flash Trade docs', url='https://docs.flash.trade/flash-trade/flash-trade-protocol/perpetuals-specifications/max-profit.md', note='HTTP 200 on 17 Nov 2026.')],
 related=['five-hundred-times-and-the-orders-turned-off', 'the-maintenance-margin-is-not-returned'],
)

R(
 title='The Maintenance Margin Is Not Returned',
 desk='money', desk_name='Money and markets', feature='Who Gets Paid?',
 desc='Flash’s liquidation page says the pool is the counterparty and leftover maintenance margin is not returned. No account was liquidated.',
 deck='The page that explains the liquidation price also explains who keeps what is left. There is no insurance fund in the design it describes.',
 question='When a Flash position crosses maintenance, who is paid, and what does the trader not get back?',
 paragraphs=[
  'The liquidation page defines the price as “the threshold at which a position is automatically closed to prevent further losses.” Three inputs set it. Maintenance margin is “the minimum collateral a position must keep, equal to position size times one over max maintenance leverage.” Unsettled obligations are “fees the position owes the pool (the close fee plus accrued margin fees),” and they “reduce your effective collateral continuously, moving the liquidation price even without price action.” Collateral and entry do the rest: “more collateral (lower leverage) puts the liquidation price further away.” A position can drift toward liquidation because a fee accrued, not because the chart moved. That is the sentence a screenshot of a price will never show.',
  'The maintenance multiples are dated, again, to 2026-07-03 and marked tunable. Crypto pool markets, 1000x. Gold pool forex, 2000x. Gold pool metals, 200x. Gold pool oil and gas, 50 to 100x. DeFi pool markets, 100x. “Meme, FART, Ore, Equity markets,” 50x. The page tells the reader to “watch the panel, not the math,” because the live liquidation price is shown before you confirm and on every open position. This reading watched the page.',
  'Then the payees. “Keeper bots continuously monitor every position and liquidate promptly once a position exceeds its maintenance threshold, executing on Flash’s low-latency execution layer.” The keepers are the hands. The economics sit in the next paragraph. “Flash’s margining engine does not require an insurance fund: the pool that backs each position is always the counterparty, so there is always liquidity to close against. Liquidation proceeds are another source of yield for liquidity providers — any remaining maintenance margin is not returned to the trader.” The leftover is not a refund. It is yield. The design the page describes does not need a fund to make the other side whole, because the pool was the other side the entire time, and the remainder of the maintenance margin joins the pool’s income.',
  'That is a different story from a venue that socialises a shortfall through an insurance fund and returns a surplus to the account. Flash’s page says it does not require the fund, and it says the trader does not receive the remainder. A liquidity provider reading the same paragraph is reading a fee. A trader reading it is reading a forfeiture that happens at the moment the position was supposed to be merely closed. “Automatically closed to prevent further losses” and “remaining maintenance margin is not returned” are both on the page. The first is the purpose. The second is the price of the purpose, paid by the account that crossed the line, to the pool that was already the counterparty.',
 ],
 says=[
  'Liquidation price depends on maintenance margin, on fees still owed, and on collateral and entry.',
  'Fees owed move the liquidation price even when the asset price does not.',
  'Maintenance leverage figures are listed by pool and dated 2026-07-03, including 1000x for crypto and 50x for meme, FART, Ore, and equity markets.',
  'The page says no insurance fund is required because the pool is always the counterparty.',
  'Any remaining maintenance margin is not returned to the trader. It is described as yield for liquidity providers.',
 ],
 paid=[
  'Liquidity providers receive liquidation proceeds, including remaining maintenance margin, as yield.',
  'The trader does not receive that remainder.',
  'Keeper bots perform the liquidation. This page does not say they are paid a separate fee.',
 ],
 decides=[
  'The protocol sets maintenance leverage and the rule that the remainder is not returned.',
  'Keeper bots decide the moment of execution once the threshold is crossed, on the page’s account. The trader does not confirm the liquidation.',
 ],
 limits=[
  'No account was liquidated and no pool balance was read.',
  'The keeper’s pay, if any, is not on this page.',
  'The 2026-07-03 figures are marked tunable, and the page says the panel is the live price.',
 ],
 sources=[dict(label='Liquidation, Flash Trade docs', url='https://docs.flash.trade/flash-trade/flash-trade-protocol/perpetuals-specifications/liquidation.md', note='HTTP 200 on 17 Nov 2026.')],
 related=['five-hundred-times-and-the-orders-turned-off', 'the-pool-is-the-other-side-of-every-trade'],
)

R(
 title='Meme Markets Pay a Different Open Fee',
 desk='money', desk_name='Money and markets', feature='Who Gets Paid?',
 desc='Flash’s fee page charges meme markets 0.1 percent to open and close, and majors 0.02 percent. The panel was not opened.',
 deck='The fee page refuses a single number. It also refuses to let a meme and a major share a rate, and it says the panel, not the table, is the bill.',
 question='What does a Flash trade cost on the page, and which of those costs is hidden if you only read the open-fee column?',
 paragraphs=[
  'The fee page lists three costs and then spends the rest of its length saying the table is not the invoice. Open and close fees are “a flat percentage of position size, charged when opening and when closing.” Trade spread is “a size-based spread applied on entry and exit.” Margin, or borrow, fees are “continuous fees on open positions based on pool utilization.” “The order panel shows your exact fees before you confirm any trade — that readout is always the authority for your specific order.” A newspaper can print the table. It cannot print the panel it did not open, and the page has told it not to pretend the table is the panel.',
  'The table is dated 2026-07-03 and labelled tunable. Majors, including SOL, BTC, ETH, ZEC, BNB and other crypto-pool markets, 0.02 percent open and close. Forex, metals, and commodities, 0.02 percent. Equities, 0.02 percent, with AMD at 0.05 percent. HYPE, 0.02 percent. JUP and JTO, 0.1 percent. “Meme markets — BONK, PENGU, PUMP, WIF, FARTCOIN,” 0.1 percent. KMNO and PYTH, 0.2 percent. ORE, 0.5 percent. The culture and the schedule meet in that meme line. The assets a timeline treats as the joke are, on this page, priced at five times the open fee of SOL. ORE is priced at twenty-five times SOL’s open fee. The page does not explain the multiple. It prints it.',
  'The spread is the cost a single percentage will omit. It applies to the execution price. Larger positions cross more of it. It is charged on both legs, so “a take-profit target needs to clear roughly two spreads before the position is net positive.” It varies by market and by conditions. “The order panel’s entry price already includes it — compare the entry price against the oracle price to see the spread you’re paying.” Two spreads before a take-profit is even a win is a design fact. It is also a fact the max-profit page complicates, because a take-profit on a major cannot be placed past a cap that may arrive first. This page does not do that arithmetic. It only insists the spread is paid twice.',
  'Margin fees accrue by utilization. Below a 72 percent “optimal-utilization threshold,” they “scale linearly with utilization.” Above it, “the step rate increases to incentivize liquidity.” “A 90% utilization cap applies across all pools.” The formula on the page is written for the region at or above 72 percent. The hourly rate is not a single basis point in the prose. The page says the hourly fee “shows in the order panel” and “rates move with pool utilization in real time.” A position held is a position rented. The rent is not in the open-fee column.',
  'Collateral that has to be swapped into the position’s backing asset pays a further pool swap fee “calculated from pool balance ratios — depositing an underweight asset is cheaper.” The page distinguishes that conversion from “the Swap page in the app, which routes spot swaps through Jupiter.” USDC itself has a special schedule at the liquidity layer: add or mint at 0 basis points, remove or burn at 15. A person who deposits USDC and later leaves is not, on this table, charged symmetrically.',
  'The page ends with a restriction that is not a fee and should not be smoothed into one. xStocks “are tokenized equity products issued by Backed Assets (JE) Limited, now part of the Kraken group.” They “are not marketed, offered, or solicited to U.S. persons or within the United States,” nor where sanctions or a local prohibition apply. They “do not represent direct ownership of the underlying shares.” A leverage product that lists equities is, on this page, also a geographic and legal fence. The fence is the issuer’s, as the page states it. This reading did not test who the interface blocks.',
 ],
 says=[
  'A trade has an open and close fee, a spread on both entry and exit, and a continuous margin fee tied to utilization.',
  'As of 2026-07-03 the open and close fee is 0.02 percent on the listed majors and 0.1 percent on the listed meme markets, 0.2 percent on KMNO and PYTH, and 0.5 percent on ORE.',
  'The spread is paid twice. A take-profit must clear roughly two spreads to be net positive, on the page’s wording.',
  'Margin fees scale with utilization below 72 percent and step up above it. Utilization is capped at 90 percent.',
  'Minting USDC liquidity is listed at 0 basis points and burning it at 15. xStocks are restricted, including a statement that they are not offered to U.S. persons.',
 ],
 paid=[
  'The open and close fee is a percentage of size, paid on the way in and the way out. The page does not, on this document, split it between pool and protocol.',
  'Spread is paid as a worse execution price, not as a separate line the page itemises in dollars.',
  'Margin fees are paid continuously to the economics of the pool. The hourly rate is whatever the panel shows.',
 ],
 decides=[
  'The protocol sets the dated table and says it tunes it.',
  'The order panel is the authority for a specific order. The trader decides whether to confirm after reading it.',
 ],
 limits=[
  'The panel was not opened. No live fee was read on 17 Nov 2026.',
  'The fee split between liquidity providers and the protocol is a different page.',
  'The xStocks restriction was not tested against an interface.',
 ],
 sources=[dict(label='Fees, Flash Trade docs', url='https://docs.flash.trade/flash-trade/flash-trade-protocol/perpetuals-specifications/fees.md', note='HTTP 200 on 17 Nov 2026.')],
 related=['the-meme-pool-keeps-a-larger-share-of-the-fee', 'a-hundred-times-leverage-dies-on-a-quarter-of-a-percent'],
)

R(
 title='The Meme Pool Keeps a Larger Share of the Fee',
 desk='money', desk_name='Money and markets', feature='Who Gets Paid?',
 desc='Flash’s fee-distribution page gives the meme pool 80 percent and the crypto pool 70. It does not say 80 percent of what, beyond fees. No pool was read.',
 deck='The shortest money page in the set is a table of percentages. The interesting column is not the biggest number. It is the fact that the meme pool is not on the same share as SOL.',
 question='Who receives Flash’s trading fees, pool by pool, according to the distribution page?',
 paragraphs=[
  'The fee-distribution page is a single idea and a table. “Liquidity providers on flash trade earn fees through trading activities over Flash Liquidity Pools.” Each pool “has different asset backing and support different market profiles which generates fees according to the volumes each pool serves. The fee is distributed every hour to liquidity providers.” Hourly, not when you feel like claiming, is the cadence, though another page in the same documentation set says sFLP rewards are claimed by hand. This page says the fee is distributed every hour. It does not reconcile the two. A reader who needs the claim button should not pretend this page described it.',
  'The split “between liquidity providers and protocol” is the table. Crypto pool, 70 percent. Stable pool, 70 percent. Solana DeFi pool, 70 percent. Meme pool, 80 percent. WIF pool, 80 percent. Samo pool, 95 percent, marked deprecated. Fart pool, 80 percent. Ore pool, 90 percent. Equities pool, 80 percent. The page does not say the remainder is the protocol’s in those words next to each row. It says the table is the fee share, and the introduction says each pool has a different split between liquidity providers and the protocol. The complement is the inference. This reading will call 70 percent the liquidity providers’ share where the table says 70 percent, and it will not invent a second recipient beyond the protocol the introduction named.',
  'The cultural sorting is visible in the rows. The crypto pool, which the other pages associate with SOL, BTC, and ETH, keeps the liquidity provider at 70. The meme pool, the WIF pool, and the fart pool keep the liquidity provider at 80. Ore keeps 90. A deprecated Samo row still prints 95. The joke assets, on this page, pay a larger published share to the people who posted the liquidity than the major-crypto pool does. Whether that compensates for the higher open fee on meme markets is a multiplication this page does not perform. The open fee is 0.1 percent in the fee table. The share is 80 percent here. Eighty percent of a fee that is five times larger is not a number this reading will present as a yield. It will present the two published figures and stop.',
  'Who is not in the table matters. There is no row for a referrer, no row for a keeper, no row for the trader’s rebate. Those parties, if they are paid, are paid under a document this page is not. The hourly distribution is to liquidity providers, at the share the row prints, from “fees.” Which fees — open, spread, margin, liquidation remainder — the page does not itemise. “Fees” is the whole word. A precise who-gets-paid map would name each stream. This page names the pools and a percentage. That is a real document. It is not a complete one.',
 ],
 says=[
  'Fees are distributed every hour to liquidity providers, and pools do not share one split.',
  'The crypto, stable, and Solana DeFi pools are listed at 70 percent. The meme, WIF, fart, and equities pools are listed at 80 percent. Ore is listed at 90 percent. Samo is listed at 95 percent and marked deprecated.',
  'The introduction says the split is between liquidity providers and the protocol.',
 ],
 paid=[
  'Liquidity providers are paid hourly at the row’s percentage.',
  'The protocol is the other party named in the introduction. The page does not print the protocol’s percentage as its own column.',
 ],
 decides=['The page presents the splits as pool parameters. It does not say who may change a row, or when the Samo row was deprecated.'],
 limits=[
  'No pool account was read. The table is the page, not a balance.',
  'The page does not define which fee streams enter the hourly distribution.',
  'A larger share of a higher fee is not computed here as a yield.',
 ],
 sources=[dict(label='Fee Distribution, Flash Trade docs', url='https://docs.flash.trade/flash-trade/flash-trade-protocol/technical-architecture/fee-distribution.md', note='HTTP 200 on 17 Nov 2026.')],
 related=['meme-markets-pay-a-different-open-fee', 'the-pool-is-the-other-side-of-every-trade'],
)

R(
 title='The Pool Is the Other Side of Every Trade',
 desk='money', desk_name='Money and markets', feature='Who Gets Paid?',
 desc='Flash’s pool-to-peer page says liquidity providers are the counterparty to every trader. No pool deposit was made.',
 deck='The mechanism page retires the order book in a sentence and replaces it with a pool, an oracle, and a simple direction of money: traders’ losses are the pool’s gains.',
 question='Who is on the other side of a Flash trade, according to the page that names the mechanism?',
 paragraphs=[
  'The page defines pool-to-peer as “a mechanism of liquidity provision for perpetuals DEXs where trader’s orders are instantly matched and executed against a pool of liquidity at the price published by a decentralized oracle.” It “eliminates the need for traditional order books by creating a unified liquidity pool that serves as the counterparty to all trades.” There is no person on the other side of your click. There is a pool, and the price is an oracle’s price rather than a price someone rested in a book. The page lists that as a benefit: “No waiting for order matching,” “pool aggregates all LP contributions,” “oracle pricing eliminates bid-ask spreads,” “always available liquidity for supported assets.” “Eliminates bid-ask spreads” sits next to the fee page’s size-based spread. This page says the oracle removes the book’s spread. The fee page says a spread is still applied. Both were retrieved. This reading will not force them into one sentence they did not write.',
  'Two entities, and only two, are given headings. Liquidity providers “deposit their assets in the pool which will in turn act as the liquidity against which other traders can trade and in return the LP provider earns fees.” They “become the counterparty to all trader positions, earning a share of trading fees, margin fees, and liquidation penalties in proportion to their pool contribution.” That list is the missing itemisation the distribution page did not give. Trading fees, margin fees, and liquidation penalties are the three streams named here, shared in proportion to contribution. Traders “collateralize their position using any asset and then gain the price exposure of the asset in the pool. When traders profit, they’re paid from the pool; when they lose, their losses flow back to the pool, benefiting LPs.” The direction of loss is not a metaphor. A trader’s loss is an LP’s benefit, on this page, because the LP was the counterparty.',
  'The oracle is the match. “This oracle system provides real-time market prices, allowing for instant trade execution without waiting for order book matching or dealing with slippage from insufficient liquidity at specific price levels.” Instant, and without the book’s empty-level slippage, is the claim. The page does not say the oracle cannot be wrong, stale, or wide. The pricing-engine page, read separately, is where those words live. Here the oracle is the thing that makes a pool feel like a market. A trader who wanted another trader on the other side will not find one in this design. A liquidity provider who wanted to choose their counterparty will not find that choice either. Contribution is the exposure. Proportion is the share.',
  'The page says “24/7 trading” and “always available liquidity for supported assets.” Other pages in the same docs set market hours for synthetics and a close-only mode when volatility breaks a threshold. This page’s “always” is the mechanism page’s “always.” It is not a promise that every market is open in every hour, because this page does not mention those other rules. A reader who staples the pages together has to let the specific rule beat the general adverb. The paper will not staple them into a single finding. It will say this page claims an oracle and a pool are enough to stand as the entire other side, and that the money, when the trader is wrong, is described as flowing to the people who deposited.',
 ],
 says=[
  'Pool-to-peer executes against a liquidity pool at an oracle price and says it removes the need for an order book.',
  'Liquidity providers are the counterparty to every trader position.',
  'They earn a share of trading fees, margin fees, and liquidation penalties in proportion to what they deposited.',
  'Trader profits are paid from the pool. Trader losses flow back to the pool.',
  'The page lists instant execution, aggregated liquidity, the elimination of bid-ask spreads, and round-the-clock availability as the benefits.',
 ],
 paid=[
  'Liquidity providers are paid fees, margin fees, and liquidation penalties, pro rata.',
  'Traders are paid from the pool only when the position wins. When it loses, the pool is the beneficiary named.',
 ],
 decides=[
  'A liquidity provider decides to deposit and thereby accepts the counterparty role.',
  'A trader decides the leverage and the asset. The oracle, not a resting order, sets the price the page describes.',
 ],
 limits=[
  'No deposit was made and no oracle price was read.',
  'This page’s claim that oracle pricing eliminates bid-ask spreads is not reconciled here with the fee page’s spread.',
  '“Always available” is this page’s phrase. Other retrieved pages describe hours and close-only mode. Those rules are not restated as if this page contained them.',
 ],
 sources=[dict(label='Pool-to-Peer Mechanism, Flash Trade docs', url='https://docs.flash.trade/flash-trade/flash-trade-protocol/technical-architecture/pool-to-peer-mechanism.md', note='HTTP 200 on 17 Nov 2026.')],
 related=['the-maintenance-margin-is-not-returned', 'the-meme-pool-keeps-a-larger-share-of-the-fee'],
)

R(
 title='A Session Key That Can Trade and Cannot Withdraw',
 desk='chain-watch', desk_name='Chain Watch', feature='The Fine Print',
 desc='Flash’s one-click page puts a temporary signing key in the browser for about seven days. It cannot withdraw. No session was created.',
 deck='The speed feature is a second key. The page is specific about what that key may sign, where it lives, and the SOL you only get back if you close it.',
 question='What does enabling one-click trading hand to the browser, and what does the page say that key cannot do?',
 paragraphs=[
  'The page sells speed in a sentence. “Trade at V2 speed without approving a wallet popup on every order. One click to open, one click to close.” The mechanism is not a faster popup. “Enabling One-Click Trading creates a session key — a temporary signing key that lives in your browser and signs trades for you. Orders execute the moment you click: your hand speed stays the bottleneck, not your wallet. Sessions expire automatically (about 7 days), and you can close them at any time.” About seven days is the page’s approximation. A key in the browser is a different custody story from Seed Vault’s claim that the secret never leaves a secure element. This is Flash’s web interface, not the phone. The page puts the signing key where the page is being read.',
  'Setup is one approval. “In the order panel, click Enable One-Click Trading and approve the setup once with your main wallet. That’s it — orders now execute on click.” One signature creates a signer that will not ask again. The page’s own boundary is the important half. The key “can open, close, and manage positions using funds already deposited in your Flash account.” It “cannot withdraw. Moving funds out always requires your main wallet’s signature.” The key “stays on your device.” Closing sessions “revokes it immediately.” A session key that can trade and cannot withdraw is a narrower weapon than a seed phrase. It is still a weapon for as long as the deposited funds can be traded, including, if the account is in that mode, the leverage the other pages describe. The page does not say the session key is barred from Degen Mode. It says the key can manage positions with funds already deposited.',
  'There is a deposit the page wants back. “Each session account holds a small SOL deposit (Solana account rent). When sessions expire or you’re done trading, close them to get that SOL back: open Settings, bottom-right of the screen, then One-Click Trading, and click Close Sessions and Reclaim.” Rent is not a fee for the trade. It is the cost of the account that holds the delegation, returned when the account is closed. A person who enables the feature and never closes the session has, on this page, left that SOL sitting there until expiry and a later reclaim. The page does not say the SOL returns itself.',
  'Set next to the funded wallet, the two speed products are opposites in custody and twins in haste. The funded wallet says Flash holds the keys and you do not sign. One-click says you sign once, and a browser key signs after that, but you still hold the withdrawal. A reader who wanted “no popups” can get there by giving up the signature or by giving up the key’s location. The page is clear about the second bargain. It does not discuss what a malicious browser extension could ask the session key to do inside the “manage positions” grant. That silence is a limit. The grant, as written, is already wide enough to open and close. On a venue whose other page starts a slider at 125x, open and close is the whole risk.',
 ],
 says=[
  'One-click trading creates a temporary signing key in the browser. Sessions expire in about seven days.',
  'The key can open, close, and manage positions using funds already deposited. It cannot withdraw.',
  'Setup is a single approval by the main wallet. Closing sessions revokes the key and is how the page says you reclaim the SOL rent deposited in the session account.',
 ],
 paid=[
  'The page describes a small SOL rent deposit per session account, returned when the session is closed.',
  'It does not add a trading fee for the feature itself.',
 ],
 decides=[
  'The trader decides to enable the key and to close it.',
  'Until it is closed or it expires, the browser key can sign the actions the page lists, without a further popup.',
 ],
 limits=[
  'No session was created and no browser key was inspected.',
  '“About 7 days” is the page’s phrase, not a measured expiry.',
  'The page does not say whether a session key can enter Degen Mode. It says the key can manage positions with deposited funds.',
 ],
 sources=[dict(label='One-Click Trading, Flash Trade docs', url='https://docs.flash.trade/flash-trade/getting-started/one-click-trading.md', note='HTTP 200 on 17 Nov 2026.')],
 related=['a-funded-wallet-that-says-zero-risk-and-then-describes-the-keys', 'degen-mode-starts-the-slider-at-125-times'],
)

R(
 title='A Volatility Flag Can Close the Door',
 desk='chain-watch', desk_name='Chain Watch', feature='The Fine Print',
 desc='Flash’s pricing page can set a high-volatility flag from Pyth and switch a market to close-only. No flag was observed.',
 deck='The oracle is not only a price. On this page it is also a switch that can stop new risk while leaving liquidations running.',
 question='When does the pricing page say a market stops opening positions, and whose price is it using when it does?',
 paragraphs=[
  'The pricing-engine page says Pyth is “our primary pricing reference.” Volatility is monitored “by comparing the reported price to the exponential moving average reported by Pyth’s oracles.” If the difference “exceeds a predefined threshold, the High Volatility Flag is set.” If it exceeds “a greater threshold, Close Only mode activates — restricting all interactions except liquidations, closing positions, and removing liquidity.” The door does not slam on the way out. It slams on the way in. A trader who wanted to add risk in the moment the flag was designed for is the person the mode is built to refuse. A trader who needs to leave, and a liquidator, are the people it still serves.',
  'The thresholds are ranges, not a single nerve. Crypto majors, about 2 percent. Metals, 0.66 percent. Forex, 0.33 percent. Crude oil, 2.2 percent. Natural gas, 0.6 percent. “Solana DeFi and Meme assets,” about 5 percent. Tokenized equities, 11.7 percent. “Exact thresholds are tuned per asset” and “may change.” The current flag “is visible in the trade UI.” The tilde on 2 percent and 5 percent is the page’s. This reading will not turn a tilde into a basis point. A meme asset is allowed a wider gap between spot and average before the flag, on this table, than a forex pair. The page calls that a risk profile. It does not show the study.',
  'A second trigger uses the confidence interval. “Prices reported by Pyth are considered invalid if the volatility flag is set and the confidence interval exceeds 1% of the reported price.” Then “Flash uses a proprietary backup oracle system” so that on-chain pricing can continue. The backup is named as proprietary. Its authors, its inputs, and its error are not on the page. If the flag is not set but the interval is still wider than 1 percent, “the protocol continues using Pyth’s reported price. The wide confidence interval alone does not necessitate corrective action.” Both conditions are required for the invalidation the page describes. One of them is not enough.',
  'During the flag, “a fixed fee is added to new position opens and size increases.” It is “not applied on closes, liquidations, or stable conditions.” “Specific bps vary by asset risk profile,” and the live fee “is surfaced in the trade UI when the High Volatility Flag is active.” The fee and the close-only mode are different severities. The page describes a flag that adds a fee, and a greater threshold that stops new risk. A reader cannot tell from this page alone how far apart those two thresholds sit, because both are “predefined” and only the spot-versus-average ranges are tabulated. The missing gap is a gap. It stays one.',
 ],
 says=[
  'Pyth is the primary pricing reference. A gap between Pyth’s price and Pyth’s exponential moving average sets a high-volatility flag, and a greater gap sets close-only mode.',
  'Close-only mode still allows liquidations, closing positions, and removing liquidity.',
  'The page prints spot-versus-average ranges, including about 2 percent for crypto majors and about 5 percent for Solana DeFi and meme assets, and says they are tuned.',
  'If the flag is set and Pyth’s confidence interval exceeds 1 percent of the price, Pyth’s price is treated as invalid and a proprietary backup oracle is used.',
  'A volatility fee is added on opens and size increases while the flag is on, and not on closes or liquidations.',
 ],
 paid=[
  'The volatility fee is paid when opening or increasing under the flag. The page does not name the recipient on this document.',
  'Closes and liquidations do not pay that fee, on the page’s rule.',
 ],
 decides=[
  'The protocol sets the thresholds and can tune them. The trade UI is where the page says the flag is visible.',
  'The backup oracle is proprietary. The page does not say a trader can choose it or inspect it.',
 ],
 limits=[
  'No flag was observed and the trade UI was not opened.',
  'The backup oracle’s method is not described. “Proprietary” is the whole account.',
  'Tildes in the threshold table are not sharpened here into exact percentages.',
 ],
 sources=[dict(label='Pricing Engine, Flash Trade docs', url='https://docs.flash.trade/flash-trade/flash-trade-protocol/technical-architecture/pricing-engine.md', note='HTTP 200 on 17 Nov 2026.')],
 related=['five-hundred-times-and-the-orders-turned-off', 'the-maintenance-margin-is-not-returned'],
)

R(
 title='FAFtarchy Sends the Decision to a Market',
 desk='power', desk_name='Power and politics', feature='The Fine Print',
 desc='Flash’s governance page says a proposal passes by the TWAP of two markets, and that the markets are hosted on MetaDAO. No proposal was traded.',
 deck='The page replaces a ballot with two prices. It also names the venue where those prices are supposed to live, and it does not pretend the paper watched one settle.',
 question='Who decides a Flash proposal, according to the FAFtarchy page, and what is the paper not claiming to have seen?',
 paragraphs=[
  'The page defines futarchy in its own simile. “Futarchy is a governance system where decisions are made through prediction markets instead of traditional voting. Think of it as betting on beliefs — the market decides what’s best for the protocol.” Flash’s version is named FAFtarchy. “Instead of counting votes, each proposal opens conditional markets and the market’s judgment determines the outcome.” The simile is the page’s. A bet and a belief are not the same object, and the page uses both words on purpose. Participants “put value behind their beliefs, so decisions aggregate information rather than sentiment.” That is the argument. It is not a result.',
  'The procedure is four steps. A proposal “is drafted” after ideas “incubate with the community in Flash Labs” and are “formalized against the proposal standards.” Then “two conditional markets open,” a PASS market and a FAIL market, “side by side.” Participants “back the outcome they believe helps Flash Trade.” The page points at a further document, Voting on Proposals, which was not retrieved for this reading. Third, “the Time-Weighted Average Price of the two markets determines the outcome — the side the market values more wins.” Fourth, “approved proposals execute on-chain. Trades on the losing side are refunded.” A refund for the losing side is a specific promise. The page does not say in which asset, at which price, or after what delay. It says the trades are refunded.',
  'Where it happens is a delegation. “Discussion and drafting: Flash Labs.” “Proposal rules: FAFtarchy Commandments.” “Trading on proposals: Voting on Proposals — live proposals are hosted on MetaDAO.” The decision Flash calls its own is traded, on this page, on someone else’s venue. MetaDAO’s own overview, read separately, describes decision markets and names Flash among the organisations whose decisions have run there. This page says the live proposals are hosted there. A reader who wanted Flash’s governance to be a room full of token holders raising hands will not find the room. They will find a pair of markets and a link.',
  'What the page does not provide is a proposal. There is no question on the table, no TWAP, no refund transaction, no list of who was allowed to trade the conditional markets. “Voting rewards popularity; markets reward being right” is an aphorism the page offers in a hint. Being right, here, means the side the TWAP values more. It does not mean the side that later made the protocol richer, because the page does not describe a look-back. The market’s judgment is the outcome. Whether the market was wise is a later question, and this page does not ask it. The paper did not trade either side. Printing the procedure is not the same as attending a decision.',
 ],
 says=[
  'FAFtarchy decides proposals with conditional markets rather than by counting votes.',
  'A PASS market and a FAIL market trade. The time-weighted average price of the two decides. The side valued more wins.',
  'Approved proposals execute on-chain. Trades on the losing side are refunded.',
  'The page says live proposals are hosted on MetaDAO.',
 ],
 paid=[
  'The page says participants put value behind their beliefs. It does not specify the stake or the payoff.',
  'Losing-side trades are refunded. The asset and the delay are not specified on this page.',
 ],
 decides=[
  'The TWAP of the two markets decides the proposal, on this page.',
  'Drafting is placed in Flash Labs, against the FAFtarchy Commandments, which were not the page retrieved.',
  'MetaDAO is named as the host of the live markets.',
 ],
 limits=[
  'No proposal was opened and no conditional market was traded.',
  'The Voting on Proposals page and the Commandments were not retrieved.',
  'A refund is asserted. Its mechanics are not.',
 ],
 sources=[dict(label='FAFtarchy Governance, Flash Trade docs', url='https://docs.flash.trade/flash-trade/flash-trade-protocol/faf-token/faftarchy-governance.md', note='HTTP 200 on 17 Nov 2026.')],
 related=['ninety-six-proposals-and-no-vote', 'the-pass-market-and-the-fail-market'],
)

R(
 title='Two Hundred and Fifty Times Against the Pool',
 desk='money', desk_name='Money and markets', feature='The Fine Print',
 desc='Jupiter’s perps page sets JLP markets at up to 250x and a 10 dollar minimum. The paper did not open a position.',
 deck='The parameter table is the product. Leverage, a position cap, an order cap, and a minimum collateral sit in one box, and the pool is named as the counterparty.',
 question='What does Jupiter’s own perps page say a trader on SOL, ETH, or BTC is actually doing?',
 paragraphs=[
  'Jupiter’s page calls the product “a perpetual futures exchange built on Solana.” On SOL, ETH, and BTC, “traders borrow assets from the Jupiter Liquidity Pool (JLP) to open leveraged positions, while liquidity providers earn a share of the fees generated by trading activity.” The position “is priced using onchain oracles rather than an orderbook: a trade executes at the oracle price when it is processed, within your slippage tolerance.” A price-impact fee “is applied instead to protect liquidity providers from large or imbalanced trades.” Borrowing from a pool, at an oracle, with a fee whose job is to protect the lender, is the whole shape. It is the same shape Flash’s pool-to-peer page describes, with different names and a different published maximum.',
  'The maximum is in a table the page limits to “the JLP markets (SOL, ETH, BTC).” Maximum leverage 250x. Leverage range 1.1x to 250x. Maximum positions 6, “one per market/side.” Maximum limit orders 20 per pair and side. Minimum collateral “$10 per new position.” Beta markets “set their own leverage limits and order caps.” The 250x figure is not a house rule for every ticker on the app. It is the published cap for three markets. A slider that can display 250 is a slider that can also display 1.1, and the page prints both ends. Unlike Flash’s Degen Mode page, this page does not say the control starts at 250. It says 250 is the top of a range that begins just above one.',
  'Collateral is asymmetric, and the page spends a sentence on the labels. SOL long collateral is SOL. SOL short collateral is USDC. ETH long is wETH. ETH short is USDC. BTC long is wBTC. BTC short is USDC. “The app labels the ETH and BTC collateral tokens ETH and BTC: they are wETH and wBTC, the Portal-bridged versions on Solana.” A long is collateralised in the thing you are long. A short is collateralised in USDC. The friendly label hides a bridge. The page does not hide it. It says the label and the bridge token in the same breath. “Traders can hold up to 6 simultaneous positions on them: one per asset per side.”',
  'Who sits on the other side is not a crowd of shorts. “The pool earns 75% of the trading fees of the SOL, ETH, and BTC markets.” “JLP holders act as the counterparty to all trades on these markets: when traders profit, the pool pays out; when traders lose, those losses flow back into the pool.” The same paragraph says the pool earns 75 percent of the fees from those markets, “swaps, and JLP minting/burning.” Beta markets “do not use the JLP pool.” A person who buys JLP to earn fees has, on this page, also agreed to pay traders when traders win. The 75 percent is a share of fees. The PnL is a separate exposure, and the page states it as the nature of the counterparty role rather than as a yield.',
  'The risk box is the page’s own, and it is specific enough to quote as terms. “Leveraged positions can be liquidated if collateral falls below the maintenance margin.” “Borrow fees accrue continuously and move your liquidation price closer to the current price over time.” “Oracle prices may differ from prices on other venues.” “The protocol has been audited but no audit eliminates all risk.” “Only trade with funds you can afford to lose.” A borrow fee that walks the liquidation price toward the market, even when you are idle, is the same kind of fact as Flash’s unsettled obligations. The multiple is the advertisement. The walking price is the term. This reading did not open a position, so it does not have a liquidation price of its own. It has the page’s warning that the fee moves the line.',
 ],
 says=[
  'JLP markets let traders borrow from the JLP pool to lever long or short SOL, ETH, and BTC. Fills are at the oracle price, within slippage, plus a price-impact fee.',
  'The published range is 1.1x to 250x, with at most six positions, one per market and side, at most 20 limit orders per pair and side, and a 10 dollar minimum on a new position.',
  'Longs post the asset. Shorts post USDC. The page says the ETH and BTC labels are Portal-bridged wETH and wBTC.',
  'JLP holders are the counterparty. The pool earns 75 percent of the trading fees on those three markets, and also a share of swap and mint or burn fees. Trader profits are paid by the pool. Trader losses flow to it.',
  'Borrow fees accrue continuously and move the liquidation price. An audit is not, on the page, the elimination of risk.',
 ],
 paid=[
  'Liquidity providers earn 75 percent of the named fees and take the other side of trader PnL.',
  'Traders pay borrow fees, base fees, and price-impact fees, as the page’s “how it works” line lists them.',
  'The other 25 percent of trading fees is not given a recipient on this page.',
 ],
 decides=[
  'The trader chooses leverage inside the published range and posts the collateral the side requires.',
  'The pool’s rules, not an order book, set the counterparty. Beta markets are explicitly outside this pool.',
 ],
 limits=[
  'No position was opened and no fee was paid.',
  '250x is the page’s cap for JLP markets, not for the beta markets it points at.',
  'The recipient of the remaining 25 percent of trading fees is not named here.',
 ],
 sources=[dict(label='Jupiter Perps user docs', url='https://docs.jup.ag/user-docs/trade/perps', note='HTTP 200 on 17 Nov 2026.')],
 related=['a-keeper-co-signs-or-comes-back-later', 'the-leverage-between-two-tiers-inherits-the-higher-cap'],
)

R(
 title='A Keeper Co-Signs, or Comes Back Later',
 desk='chain-watch', desk_name='Chain Watch', feature='The Fine Print',
 desc='Jupiter’s technical page says a keeper operated by Jupiter must complete a JLP trade. The paper did not submit one.',
 deck='The click is not the fill. On the JLP markets the page describes, a service Jupiter runs either co-signs at once or returns with a second transaction.',
 question='Who has to show up after the trader signs, and what does the page say is not a trade until they do?',
 paragraphs=[
  'The technical reference says Jupiter Perps “executes trade actions through keepers, in one of two ways. The jup.ag app picks the path for each action.” The first path is a request and a fulfillment. The trader submits a transaction “containing all required trade parameters.” “A keeper detects the request onchain, validates it, and submits a second transaction to execute the trade. The trade is only finalized when this second transaction is confirmed by the Solana network.” Limit orders and take-profit or stop-loss orders “are executed this way when their trigger price is reached.” The second path is a single transaction: “the trader signs one transaction that a Jupiter keeper co-signs and submits right away, with no request account for market trades. Closing a position from jup.ag uses this path by default.”',
  'A co-signature is a second will. The trader’s signature is not sufficient on that path, on this page, because the keeper must sign too. On the request path the trader’s signature is sufficient to ask, and insufficient to finish. “There is a short delay between request submission and trade execution. The trade is not live until the keeper’s fulfillment transaction is confirmed.” A person who has signed and is staring at a spinner has not, in the page’s terms, got a position. They have got a request. The page does not say what the spinner should admit.',
  'Who the keepers are is not a permissionless set. “Keepers are offchain services operated by Jupiter that continuously poll the Solana blockchain for pending trade requests. Jupiter runs two keepers in parallel.” The actions they process include opening and closing, increasing and decreasing, depositing and withdrawing collateral, and creating, editing, and triggering both take-profit or stop-loss orders and limit orders. Two keepers, both Jupiter’s, polling. The page does not say a third party can run one. Flash’s liquidation page says keeper bots monitor positions and does not, in that document, reserve the role to Flash. Jupiter’s page reserves the operation. The difference is the kind of power a “decentralised perps” headline usually skips.',
  'Beta markets are the exception the same page carves out. They “do not use the request fulfillment model, the keepers, or the JLP custody accounts.” “An order is a single transaction that you sign with your Solana wallet; it is relayed to GUM, the orderbook trading engine that runs these markets, matched there, and the resulting fill is pushed back to the app.” The transaction “can be viewed on Solscan.” Prices on the stock markets “come from Chainlink oracles.” A reader leaving the JLP markets does not leave dependency. They trade a keeper they do not co-sign with for an engine named GUM and, on the stock markets, a different oracle. The page is the map. The paper did not send either kind of transaction.',
 ],
 says=[
  'On JLP markets the app chooses between a request plus a later keeper transaction, and a single transaction the keeper co-signs.',
  'The trade is not final until the keeper’s transaction confirms. Limit and take-profit or stop-loss orders use the request path.',
  'Closing from jup.ag uses the co-signed path by default.',
  'Jupiter operates the keepers and runs two in parallel.',
  'Beta markets skip the keepers and the JLP custody accounts. The trader signs one transaction, GUM matches it, and stock-market prices are attributed to Chainlink.',
 ],
 paid=['This page does not price the keeper. It says the keeper’s transaction is what finalises the trade.'],
 decides=[
  'The jup.ag app picks the path.',
  'Jupiter’s keepers validate and either co-sign or submit the second transaction.',
  'On the request path, the position does not exist until the keeper’s transaction confirms.',
 ],
 limits=[
  'No trade was submitted. The delay was not timed.',
  '“Short delay” is the page’s phrase, not a measurement.',
  'The page does not say an outside party can run a JLP keeper.',
 ],
 sources=[dict(label='Jupiter Perps technical reference', url='https://docs.jup.ag/user-docs/trade/perps/technical-reference', note='HTTP 200 on 17 Nov 2026.')],
 related=['two-hundred-and-fifty-times-against-the-pool', 'three-oracles-and-a-chart-that-claims-to-be-the-truth'],
)

R(
 title='Three Oracles, and a Chart That Claims to Be the Truth',
 desk='chain-watch', desk_name='Chain Watch', feature='Claim Check',
 desc='Jupiter’s technical page ranks Edge, Chainlink, and Pyth, and says its own chart is the source of truth. No price was compared.',
 deck='The oracle section is a procedure for disagreement. It also contains a sentence that tells a trader which screen to believe when the screens diverge.',
 question='Which price does the page say Jupiter Perps will use, and which price does it tell the trader to obey?',
 paragraphs=[
  'The page says token prices “are sourced from three independent onchain price oracles.” Edge by Chaos Labs is primary. Chainlink and Pyth are “verification and fallback.” The selection is a ladder. “If the Edge oracle is not stale and its price is within a defined threshold of both Chainlink and Pyth, the Edge price is used.” If Edge “is stale or outside the threshold, Chainlink and Pyth prices are compared. If they are within the threshold of each other, the more recent of the two is used.” The page’s own summary, as retrieved, stops the ladder there. A defined threshold that is not given a number in the sentences read is a hole. This reading will not invent the basis points.',
  'Updates happen “both during trade execution and via a dedicated keeper that runs independently.” The price can move because a trade forced a look, or because a keeper looked on its own. “Prices used in Jupiter Perps may differ from prices on other venues. The Jupiter Perps price chart is the source of truth for trade decisions.” That last sentence is a claim about authority, not about accuracy. The chart is the truth for the purpose of deciding, because the fill will use the oracle procedure above, and the chart is where the page tells you to look. A trader who saw a different price on another venue and feels cheated is, on this page, looking at the wrong screen. The page does not say the chart cannot be stale. It says it is the one that counts.',
  'The same document’s beta note complicates the word “the” in “the oracle.” Stock markets on the beta list “come from Chainlink oracles.” They are not described as running the Edge-then-Chainlink-then-Pyth ladder. A house with two price regimes is a house that can show a SOL trader one procedure and a stock trader another. The page says so. It does not say the thresholds are the same, because it does not print the thresholds in the sentences this reading is using.',
  'A source of truth that is allowed to differ from every other venue is the point of an oracle design and the beginning of a dispute. The page chooses the first and does not describe a dispute process. There is no named delay, no published divergence log, and no promise that Edge, Chainlink, and Pyth were read by the paper. They were named. Naming is what this page can support. A comparison of their prints at a minute on 17 Nov 2026 was not done.',
 ],
 says=[
  'Jupiter Perps names Edge by Chaos Labs as the primary oracle and Chainlink and Pyth as verification and fallback.',
  'Edge is used when it is not stale and within a defined threshold of both of the others. Otherwise Chainlink and Pyth are compared, and the more recent is used if they agree within the threshold.',
  'A keeper updates prices independently of trades. The page says Jupiter’s own chart is the source of truth for trade decisions, and that its prices may differ from other venues.',
  'Stock markets in the beta section are priced from Chainlink, not described with the three-oracle ladder.',
 ],
 paid=['The oracle section names no fee for the price itself.'],
 decides=[
  'The ladder decides which feed is used. The threshold is “defined” and not numbered in the sentences read.',
  'The page tells the trader to treat the Jupiter Perps chart as the decision price.',
 ],
 limits=[
  'No oracle account was read and no two venues were compared.',
  'The numeric threshold is not in the sentences this reading relies on. It is not invented.',
  '“Source of truth” is the page’s instruction, not a finding that the chart was right.',
 ],
 sources=[dict(label='Jupiter Perps technical reference', url='https://docs.jup.ag/user-docs/trade/perps/technical-reference', note='HTTP 200 on 17 Nov 2026.')],
 related=['a-keeper-co-signs-or-comes-back-later', 'two-hundred-and-fifty-times-against-the-pool'],
)

R(
 title='The Leverage Between Two Tiers Inherits the Higher Cap',
 desk='money', desk_name='Money and markets', feature='The Fine Print',
 desc='Jupiter’s beta page says 15x inherits a 20x position cap, and take-profit is unavailable. No beta order was sent.',
 deck='The beta markets are an order book, a single collateral, and a tier table that punishes a number sitting between two rungs. The page dates the caps.',
 question='What does the beta-market page say changes when a trader leaves the JLP pool?',
 paragraphs=[
  'The beta page says these markets are “the perpetual markets Jupiter Perps offers beyond SOL, ETH, and BTC.” They are “powered by GUM, an orderbook trading engine, rather than by the JLP pool.” The rules that follow are a clean break. “USDC collateral, a funding rate instead of a borrow fee, taker and maker fees, and one net position per market.” They are “in early release with limited features: take profit and stop loss orders are not available, position and order sizes are capped, and each market sets its own maximum leverage.” The badge on jup.ag is how the page says you know you are in this list. Early release is the page’s label. It is not a date for leaving early release.',
  'Collateral “is USDC on every Beta market, for longs and shorts alike.” That is the opposite of the JLP markets, where a long posts the asset. Funding replaces the borrow fee and is “applied hourly.” A market order pays a taker fee. A limit order pays a maker fee. “Same-side trades” on JLP markets merge. Beta markets allow “one net position per market.” You do not hold a long and a short in the same name as two tickets. You hold a net.',
  'The tier rule is the sentence a slider will not explain unless the popover is read. “Beta markets use risk tiers: the larger a position, the more margin it needs and the lower its maximum leverage. The leverage you use therefore sets your position cap.” “A leverage between two tiers gets the cap of the higher-leverage tier: on a market with 20x, 10x and 5x tiers, 15x has the 20x cap.” Fifteen is closer to ten, and the page gives it the tighter cap, the one that belongs to twenty. “Exposure exactly at a tier’s cap falls into the next tier.” Open orders that can increase the position count. Reduce-only closes do not. A limit order “counts at its limit price or the mark price, whichever is higher.” The cap “is a limit on your exposure, not the depth of the orderbook.”',
  'The page prints a shared margin schedule. At 50x, initial margin 2 percent and maintenance 1 percent. At 25x, 4 and 2. At 20x, 5 and 2.5. At 10x, 10 and 5. At 5x, 20 and 10. “The initial margin is one rate on the whole position: its value divided by your leverage.” The example is “a $15,000 JUP position at 10x needs $1,500.” Maintenance “rises gradually: each slice of a position pays its own tier’s rate.” Caps are dated. “Values on November 13, 2026; the popover prevails.” JUP’s 20x tier is listed at $10,000 and its 10x tier at $20,000. ZEC, BNB, and NEAR are given a 50x cap of $10,000. HYPE’s table starts at 25x. A worked refusal is printed: a $9,000 JUP position at 20x with $750 of open orders uses $9,750 of a $10,000 cap, and an increase of $500 is refused with “The 20x position cap is $10,000. Reduce size or lower leverage to 10x.” The popover wins if the page and the app disagree. The page was read. The popover was not opened.',
 ],
 says=[
  'Beta markets run on GUM’s order book, not the JLP pool. Collateral is USDC for longs and shorts. Funding is hourly. Take-profit and stop-loss are not available.',
  'There is one net position per market. Taker and maker fees replace the JLP base fee and price-impact fee.',
  'A leverage between two tiers inherits the higher tier’s position cap. The page’s example is that 15x gets the 20x cap.',
  'The margin rates are printed, from 2 percent initial at 50x to 20 percent initial at 5x. Position caps are dated 13 November 2026, and the popover is declared the authority.',
  'The page includes a worked JUP refusal at the $10,000 cap for 20x.',
 ],
 paid=[
  'Taker fees apply to market orders and maker fees to limit orders. The rates are not in the sentences used here.',
  'Funding is paid between longs and shorts hourly, not to the JLP pool, because these markets do not use that pool.',
 ],
 decides=[
  'Each market sets its maximum leverage and its caps. The page says the in-app popover prevails over the dated table.',
  'The trader’s chosen leverage selects the cap, including the rule that an in-between leverage inherits the tighter one.',
 ],
 limits=[
  'No beta order was sent and the popover was not opened.',
  'The 13 November 2026 caps may have moved. The page says so by deferring to the popover.',
  'Fee rates for taker and maker are not stated in this reading because they were not the figures copied from the retrieved text used here.',
 ],
 sources=[dict(label='Jupiter Perps beta markets', url='https://docs.jup.ag/user-docs/trade/perps/beta-markets', note='HTTP 200 on 17 Nov 2026. The page dates a cap table to 13 November 2026.')],
 related=['two-hundred-and-fifty-times-against-the-pool', 'a-keeper-co-signs-or-comes-back-later'],
)

R(
 title='The Curve That Does Not Ask the Creator for Both Sides',
 desk='culture', desk_name='Internet culture', feature='The Fine Print',
 desc='Raydium’s LaunchLab overview says a creator no longer has to seed both sides of a pool. No launch was created.',
 deck='The overview is a story about who used to need capital, and a machine that lets a buyer be the liquidity. The machine’s exact formula is a different page, and the two pages do not match.',
 question='What problem does the LaunchLab overview say the bonding curve solves, and what does graduation do to the mint?',
 paragraphs=[
  'The overview’s problem statement is about access to the launch itself. “Before LaunchLab, launching a new token on Raydium required the creator to seed an AMM pool with both sides of the pair up front — meaning the team had to provide the quote-side liquidity out of pocket. This favored well-funded projects and gated access to the launchpad mechanism on initial capital.” The curve “replaces that opening step.” Buyers “acquire the token by sending quote to the curve, which atomically mints or releases base-token units at a price determined by the curve formula and current supply. No pre-seeded liquidity required.” A meme launch, in this telling, is a way to stop asking a team for the other side of the pool before anyone has bought. The buyer’s payment is the liquidity. That is the cultural and the mechanical claim in one paragraph.',
  'Graduation is the moment the curve stops being the market. It happens “when quote_vault.balance is at least the graduation threshold.” The threshold “is set at Initialize and is typically chosen so that at graduation the curve’s implied price matches the price the AMM pool will open at.” At that moment the programme “snapshots the remaining base vault and the quote vault,” creates a CPMM pool with those reserves, “revokes the base mint’s mint authority (so no more base tokens can ever be minted),” and sets the launch’s status to Graduated. “Post-graduation, Buy and Sell reject.” Trading “continues on the resulting CPMM pool, which is indistinguishable from any other Raydium CPMM pool.” The mint authority dying is the part a buyer cannot see in the price. It is the part that decides whether the curve’s supply was the supply.',
  'The overview also names who holds the liquidity afterwards, and it dates a change. “For migrations executed after the 2026-08-17 upgrade, platform_scale plus creator_scale is locked through LP-Lock,” and “one Fee Key goes to platform_nft_wallet when this share is non-zero.” The sentence before that upgrade is started on the page and was not needed to print a complete pre-upgrade rule, so this reading does not invent the earlier split. What can be said is that the page treats the lock as a dated policy, not as an eternal burn, and that a fee key can go to a platform wallet when the share is not zero. “Even if post-graduation trading pushes the AMM pool price back below the graduation price, the launch does not revert to the curve.” There is no undo.',
  'Fees are admitted and then deferred. “Some launches direct a share to the creator as an ongoing revenue stream.” “Default rates are documented on the bonding-curve page. The exact split is stored on LaunchState.fees and can differ per launch.” Post-graduation fees “follow the CPMM config the pool was created with (typically AmmConfig 0, the 0.25% tier).” A creator who no longer has to seed the quote side may still have a fee switch. The overview says the switch exists and that its exact position is per launch. A buyer who does not read LaunchState.fees does not know which launch they are in. The page has told them the place to look.',
 ],
 says=[
  'LaunchLab removes the requirement that a creator seed both sides of a Raydium pool before trading.',
  'Buyers pay quote into a curve and receive base tokens. Graduation happens when the quote vault meets a threshold set at initialisation.',
  'At graduation the base mint authority is revoked, buys and sells on the curve reject, and trading continues on a CPMM pool.',
  'The page says that after the 2026-08-17 upgrade, platform scale plus creator scale is locked through LP-Lock, and a fee key can go to the platform NFT wallet.',
  'A launch does not fall back onto the curve if the pool price later drops. Creator fee splits vary per launch.',
 ],
 paid=[
  'The creator may receive an ongoing fee share. The exact split is on the launch’s fee state, not a single rate on this page.',
  'Post-graduation trading fees follow the CPMM config, typically the 0.25 percent tier named on the page.',
  'Buyers pay quote into the curve. That quote becomes the pool’s other side.',
 ],
 decides=[
  'The creator sets curve parameters and the threshold at initialisation, within the programme’s rules.',
  'Graduation is described as automatic once the vault meets the threshold. The migration instruction’s signer is a different page.',
 ],
 limits=[
  'No launch was created and no mint authority was inspected.',
  'The pre-upgrade LP arrangement is not fully stated here, because the retrieved overview’s earlier branch was not copied into a complete rule.',
  'The overview’s formula sentence is challenged by the bonding-curve page. That disagreement is its own reading.',
 ],
 sources=[dict(label='LaunchLab overview, Raydium docs', url='https://docs.raydium.io/products/launchlab/overview', note='HTTP 200 on 17 Nov 2026.')],
 related=['one-raydium-page-says-quadratic-another-says-constant-product', 'the-migration-wallet-is-who-graduates-the-pool'],
)

R(
 title='One Raydium Page Says Quadratic. Another Says Constant Product',
 desk='investigations', desk_name='Investigations', feature='Claim Check',
 desc='Raydium’s overview sketches a quadratic curve. Its other page says pump-style launches use constant product. The programme was not run.',
 deck='Two pages on the same documentation site describe the curve a meme launch actually follows. They do not describe the same curve. This reading prints both and does not pretend to have run the code.',
 question='What curve does each retrieved Raydium page say a pump-style launch uses?',
 paragraphs=[
  'The overview reaches for a lineage. “The most common is a quadratic bonding curve analogous to the Pump.fun / Curve.fi / Bancor lineage,” and it offers a sketch, “price of s equals k times the square of s over S max, or similar — exact formula is curve-config dependent.” The hedges are doing a lot of work. “Or similar” and “curve-config dependent” mean the displayed formula might not be the formula. The name Pump.fun is in the sentence. A reader of only this page would leave thinking the common LaunchLab curve is the quadratic one associated with that venue.',
  'The bonding-curve page, retrieved the same day, sorts the shapes by an integer. Curve type 0 is “constant-product (virtual-reserves).” Curve type 1 is fixed-price. Curve type 2 is linear-price. “The default and most-used curve” is type 0. “Pump-style launches all use this form.” The form is a constant-product curve that “pretends there is a” virtual reserve, so that the invariant used before graduation is the same kind of curve the pool will use after, and “the marginal price at base sold equals base supply graduation equals the price the post-graduation pool opens at.” Fixed price is “a flat-price curve” where “every buy and sell happens at a constant price,” which the page says is “useful for fair launches where the team wants uniform pricing for all participants.” Linear price “increases linearly with base sold,” and “early buyers pay close to zero, late buyers pay substantially more.”',
  'Those are three different promises to the person who arrives first. A constant-product virtual reserve rises as a hyperbola. A fixed price does not care when you arrived. A linear price, on the page’s own description, charges the late buyer more along a straight slope, with early buyers near zero. The overview’s quadratic sketch is a fourth shape, and it is the one the overview attaches to the words Pump-style. The bonding-curve page attaches those same words to type 0. Both pages are Raydium’s. The paper did not execute InitializeV2, did not read a LaunchState account, and did not decide which page the programme obeys. A claim check that declared a winner without the account would be a guess the style book forbids.',
  'What the bonding-curve page does specify, and the overview’s sketch does not replace, is the fee field and the graduation fraction. Buy fee is a numerator over a denominator, “for example 100 over 10,000 equals 1.00 percent.” Protocol share, creator share, and LP share “split” that fee. Base supply graduation is “usually 0.8 times base supply max,” and “the remaining 20 percent becomes the post-graduation pool’s initial LP.” The quote reserve target equals the cost of buying that graduation supply, times one plus the buy fee rate. A worked figure on the page sets base supply graduation at 800,000,000. The 80 percent and the 1 percent example are the page’s examples. They are not a survey of launches. They are enough to show that “the curve” is not only a shape. It is a fee split and a leftover fifth of the supply that becomes the pool.',
 ],
 says=[
  'The LaunchLab overview describes the common curve as quadratic and analogous to Pump.fun, with an explicit hedge that the exact formula depends on config.',
  'The bonding-curve page says curve type 0, constant product with virtual reserves, is the default, and that pump-style launches all use it.',
  'Type 1 is a fixed price. Type 2 is linear, with early buyers paying close to zero on the page’s description.',
  'An example buy fee is 1 percent, written as 100 over 10,000. Graduation supply is usually 80 percent of the max, and the remaining 20 percent is described as the pool’s initial LP.',
 ],
 paid=[
  'The buy fee is split among protocol, creator, and LP shares stored on the launch. The page says the shares use a common denominator. It does not print one universal split.',
  'The remaining 20 percent of supply is described as liquidity, not as a payment to buyers.',
 ],
 decides=[
  'Curve type is selected at initialisation. The bonding-curve page says the choice is stored on the launch.',
  'Which of Raydium’s two explanations matches a given launch is not decided by this reading.',
 ],
 limits=[
  'The programme was not executed and no launch account was decoded.',
  '“Or similar” on the overview means the quadratic display is not, even on that page, a guarantee.',
  'Pump.fun’s own programme was not retrieved. The name appears only as Raydium’s analogy.',
 ],
 sources=[
  dict(label='LaunchLab overview', url='https://docs.raydium.io/products/launchlab/overview', note='HTTP 200 on 17 Nov 2026.'),
  dict(label='LaunchLab bonding curve', url='https://docs.raydium.io/products/launchlab/bonding-curve', note='HTTP 200 on 17 Nov 2026.'),
 ],
 related=['the-curve-that-does-not-ask-the-creator-for-both-sides', 'the-migration-wallet-is-who-graduates-the-pool'],
)

R(
 title='The Migration Wallet Is Who Graduates the Pool',
 desk='power', desk_name='Power and politics', feature='Who Gets Paid?',
 desc='Raydium’s instruction page says the old initialise always fails, and a migration wallet graduates the pool. No transaction was sent.',
 deck='The overview says graduation happens. The instruction page says who is allowed to press it, and it says the old entry point is dead on purpose.',
 question='Who is allowed to create a launch, who is allowed to graduate it, and who is allowed to collect which fee?',
 paragraphs=[
  'The instruction page is a table of permissions wearing the clothes of an interface definition. CreateConfig and UpdateConfig belong to the programme admin, with a delegated create-config authority also able to call CreateConfig. Initialize, the original entry, is callable by nobody. “It always fails with NotApproved.” It is “retained only so the discriminator stays occupied and the IDL stays stable.” The page says to use InitializeV2. A later note is even flatter. Since the 2026-09 upgrade the handler “is now nothing but a log” that says to use initialize_v2, and NotApproved, error 6000. “The failure is now unconditional.” Existing launches “are unaffected” and “trade and graduate normally.” A dead instruction kept so the shape of the interface does not move is a political object. New creators cannot use the door. Old launches are not thrown out.',
  'InitializeV2 is “anyone (creator)” for an SPL token base mint. It “records amm_creator_fee_on for the eventual CPMM graduation, and accepts a Token-2022 quote mint.” InitializeWithToken2022 is anyone, for a Token-2022 base mint. The page says every new initialisation “must set migrate_type to CPSWAP.” An attempt to start a new AMM v4 pool “returns MigrateTypeNotMatch.” The creator-fee flag “only selects whether the resulting CPMM creator fee applies to the quote token or both tokens. It does not select the target programme.” The creator chooses a fee base. The creator does not choose to stay on the old AMM.',
  'Graduation is not “anyone.” MigrateToAmm is the “migration wallet,” and it is “legacy AMM v4 graduation for pools initialized before CPMM-only creation was enforced.” MigrateToCpswap is also the migration wallet, and “all newly initialized launches use this path.” It “wraps InitializeWithPermission on CPMM.” The overview’s “automatic” graduation and this page’s named wallet are not the same sentence. Automatic may describe the trigger. The instruction page describes the signer. This reading will not collapse them. A migration wallet is a key. The page does not print the key’s address in the portion used here. It prints the role.',
  'Fees have owners. CollectFee is admin, to “sweep protocol fees from a launch.” CollectMigrateFee is admin. ClaimCreatorFee is the creator, “during the curve phase.” CreateVestingAccount is the creator, allocating locked tokens to a beneficiary “unlocked after graduation.” ClaimVestedToken is the beneficiary. Platform admin can create platform config, claim platform fees, and maintain an allowlist “when that platform enables restriction.” A curve-rule manager, or the platform admin, manages the launch-parameter rule of a global config. The cast is larger than a lone deployer and a bonding curve. There is a programme admin, a migration wallet, a creator, a beneficiary, a platform admin, and a rule manager. Restriction is a feature the page says a platform can enable. It does not say which platform has enabled it.',
  'One more sweep arrived with a date. “CollectExcessLamports” may be called by the programme admin or “the dedicated collect-lamports wallet,” to “sweep lamports above the rent-exempt minimum from LaunchLab-controlled vaults and PDAs. Added 2026-09.” Rent left on the programme’s own accounts can be taken by an admin or by a dedicated wallet. Buyers do not receive that dust, on this description. The page is a map of who may move value after the meme has done its work. The paper sent none of the instructions.',
 ],
 says=[
  'Initialize always fails with NotApproved and is kept so the discriminator stays occupied. InitializeV2 is the path for a new SPL launch, and anyone who is the creator may call it.',
  'New launches must set the migration type to CPSWAP. MigrateToCpswap is callable by the migration wallet. The legacy AMM migration is also the migration wallet, for older pools.',
  'Admin sweeps protocol fees and migration fees. The creator claims creator fees during the curve. A beneficiary claims vested tokens after graduation.',
  'A platform can enable an allowlist. CollectExcessLamports, added in the page’s 2026-09 note, lets an admin or a dedicated wallet sweep leftover lamports.',
 ],
 paid=[
  'Protocol fees are swept by admin. Creator fees are claimed by the creator during the curve. Vested tokens are claimed by the beneficiary after graduation.',
  'Leftover rent lamports on programme-controlled accounts can be swept by admin or by the dedicated wallet. The page does not assign them to buyers.',
 ],
 decides=[
  'The programme admin decides config and fee sweeps. The migration wallet decides the graduation transaction, in the sense that the instruction names that wallet as the caller.',
  'A platform admin can restrict who may use a config, if restriction is enabled. The page does not say it is enabled for any named platform.',
 ],
 limits=[
  'No instruction was submitted and no migration-wallet address was read from chain.',
  '“Automatic” on the overview and “migration wallet” here are both printed. This reading does not decide which word a buyer experiences.',
  'Error codes are the page’s. They were not reproduced in a transaction.',
 ],
 sources=[dict(label='LaunchLab instructions', url='https://raydium.mintlify.app/products/launchlab/instructions', note='HTTP 200 on 17 Nov 2026. The instruction table and the 2026-09 notes were read.')],
 related=['the-curve-that-does-not-ask-the-creator-for-both-sides', 'one-raydium-page-says-quadratic-another-says-constant-product'],
)

R(
 title='Ninety-Six Proposals, and No Vote',
 desk='power', desk_name='Power and politics', feature='Claim Check',
 desc='MetaDAO’s overview says it has run 96 proposals for 14 organisations since November 2023, by trading rather than voting. The paper did not trade one.',
 deck='The page counts its own history and names three decisions a reader will have heard of. The count is the page’s. The mechanism is the part that matters.',
 question='What does MetaDAO’s overview say has already been decided, and what does it say was not a vote?',
 paragraphs=[
  'The overview starts with a count and a date. “MetaDAO originally started as a governance project — since November 2023 we’ve run 96 proposals for 14 organizations.” The decisions it chooses to name are “Jito’s fee switch decision,” “Flash’s decision to start passing revenue back to stakers,” and “all of Sanctum’s governance decisions.” Those names are the page’s examples. This reading did not open the Jito proposal, the Flash proposal, or a Sanctum proposal. It can say MetaDAO claims those decisions ran through it. It cannot say what the proposals contained, who was allowed to trade them, or whether the organisations did what the markets said. Flash’s own FAFtarchy page, retrieved separately, says live proposals are hosted on MetaDAO. The two pages point at each other. Neither is a transcript.',
  'The difference, in the next paragraph, is the entire product. “The difference between governance on MetaDAO and elsewhere is that there isn’t any voting, only trading. This system of governance is called decision markets.” People “trade in markets that correspond to what would be the value of this token if this proposal passed, and what would be the value of this token if this proposal failed.” Organisations “accept a proposal when traders think it will make the token’s value increase and reject them when traders think it will make the token’s value decrease.” Value, on this page, is the token’s value. A proposal that helps users and hurts the token is, by the rule as written, a proposal the organisation is told to reject. The page does not discuss that case. The rule is the case.',
  'A count of 96 is a denominator someone will want to turn into a success rate. The page does not give the number accepted, the number rejected, or the number that passed the market and were not executed. Fourteen organisations is not a list. Three examples are not fourteen. A newspaper that printed “MetaDAO has successfully governed fourteen organisations ninety-six times” would be adding the adjective the page did not use. The page says it has run 96 proposals. Run is its verb. The paper did not recount them.',
 ],
 says=[
  'Since November 2023 the page says MetaDAO has run 96 proposals for 14 organisations.',
  'It names Jito’s fee switch, Flash’s decision to pass revenue to stakers, and all of Sanctum’s governance decisions as examples.',
  'It says there is no voting, only trading, in markets on the token’s value if a proposal passes and if it fails.',
  'Acceptance follows traders thinking the token’s value would increase. Rejection follows the opposite.',
 ],
 paid=['The overview does not specify who profits from being right in a decision market. It says traders express a view of the token’s value.'],
 decides=[
  'The organisation, on this page, accepts or rejects by reading which conditional market implies the higher token value.',
  'Traders decide by trading. The page says they do not vote.',
 ],
 limits=[
  'The 96 and the 14 were not independently counted.',
  'The named Jito, Flash, and Sanctum decisions were not opened.',
  'No conditional market was traded by the paper.',
 ],
 sources=[dict(label='Introduction to Decision Markets, MetaDAO docs', url='https://docs.metadao.fi/governance/overview', note='HTTP 200 on 17 Nov 2026.')],
 related=['faftarchy-sends-the-decision-to-a-market', 'the-pass-market-and-the-fail-market'],
)

R(
 title='The Pass Market and the Fail Market',
 desk='opinion', desk_name='Opinion and debate', feature='Claim Check',
 desc='MetaDAO’s page argues that a DAO which still uses token voting will look malicious. That argument is the page’s, not a finding. No market was traded.',
 deck='The overview does not stop at a mechanism. It makes a moral claim about everyone who has not adopted it. The claim is printed. It is not adopted.',
 question='What would count against the page’s claim that decision markets are the competent way to share ownership?',
 paragraphs=[
  'This page is a document reading of an argument, and the label on it is not Opinion. The paper is not adopting the argument. The Opinion desk’s rule is that an argument needs a critic’s restatement and a statement of what would defeat it. The page supplies the argument. This reading supplies the restatement and the missing test, and then stops, because the test was not run.',
  'The page’s claim, in its own voice, is that decision markets aim at a kind of intelligence, that it does not know if they are there yet, and that they “appear” to make it harder to rug an initial offering “when the funds are stored in a treasury with decision market oversight.” The hedge “appear” is the page’s. The stronger sentence comes next. “All DAOs that persist with token voting over decision markets should begin to feel increasingly uncomfortable, because in time it will be assumed that any DAO still carrying on this way is malicious or incompetent.” The choice the page offers a founder is binary. “If you want people to share ownership of your business, you either become a normal company with no governance token, or you bind your fate to decision markets and let the market decide.”',
  'A critic can restate that without caricature. The page says token voting will come to look like malice or incompetence, and that shared ownership of a business should be either ordinary corporate ownership or a decision market. What would count against it is also sayable from the page’s own earlier sentences. The page has already said it does not know if the markets are “quite at that level of intelligence yet.” A single decision market that accepts a proposal the token likes and the treasury does not survive would count against the comfort the later sentence demands. A proposal that helps the people who use a product and hurts the token’s price would, under the rule on the same page, be rejected. If that outcome is common, the binary looks less like competence and more like a rule that the token’s price is the only principal. The page does not record such a case. It also does not record a case that would confirm the rug sentence. “Appear” is still the verb on the rug.',
  'The paper does not conclude that voting DAOs are malicious. That sentence is MetaDAO’s, and it is a prediction about what “in time it will be assumed,” which is a claim about other people’s future beliefs. Beliefs are not a finding. The mechanism above the sermon — two markets, pass and fail, token value as the score — is the part a reader can go and watch. This reading did not watch one. Until someone does, with a named proposal and a recorded TWAP, the sermon is a sermon. The style book allows a document to be quoted. It does not allow the quote to be promoted into the paper’s verdict.',
 ],
 says=[
  'The page says decision markets appear to make ICO rugs harder when funds sit in a treasury those markets oversee, and it says it does not know if the markets are at the intended level of intelligence.',
  'It says DAOs that keep using token voting should become uncomfortable, because they will be assumed malicious or incompetent.',
  'It says shared ownership should be either a normal company without a governance token, or decision markets.',
 ],
 paid=['No fee is specified. The argument is about who should be trusted with a treasury, not about a rate.'],
 decides=[
  'The page wants organisations to let the pass market and the fail market decide.',
  'The paper does not decide that. The page’s prediction about other people’s assumptions is not a finding.',
 ],
 limits=[
  'No proposal, treasury, or rug was investigated.',
  '“Appear” and “in time it will be assumed” are the page’s hedges. They are not evidence.',
  'This is not the commissioned essay for or against memecoins. Those assignments remain unwritten.',
 ],
 sources=[dict(label='Introduction to Decision Markets, MetaDAO docs', url='https://docs.metadao.fi/governance/overview', note='HTTP 200 on 17 Nov 2026.')],
 related=['ninety-six-proposals-and-no-vote', 'faftarchy-sends-the-decision-to-a-market'],
)

R(
 title='A Tip Can Be Spent on the Wrong Leader',
 desk='money', desk_name='Money and markets', feature='Who Gets Paid?',
 desc='Jito’s send page says a bundle needs a tip to one of eight accounts, and a tip to a non-Jito leader is wasted. No bundle was sent.',
 deck='The page that explains faster landing also explains a payment that can buy nothing. The warning is in the document. The paper did not test it.',
 question='Who is paid when a transaction tries to land through Jito, and when does the page say that payment does not buy priority?',
 paragraphs=[
  'Jito’s low-latency send document describes a bundle as something a tip makes eligible. “A tip is necessary for the bundle to be considered. The tip can be any instruction, top-level or inner, that transfers SOL to one of the 8 tip accounts.” The page says clients should keep enough balance, and should make the tip conditional “especially if tipping as a separate transaction.” “If the tip is too low, the bundle might not be selected during the auction.” There is a method, getTipAccounts, “to retrieve the tip accounts.” “Ideally, select one of the accounts at random to reduce contention.” The page also says the tip accounts “have remained constant.” Random selection among a stable list is the advice. A reader who hard-codes one account has not broken the payment. They have ignored a congestion hint.',
  'The waste is the sentence that belongs in a who-gets-paid box. “Tips do not prioritize transactions for validators that are not Jito-Solana leaders, so tipping in these cases will be ineffective and a waste of money.” A leader who is not running the client the system expects will not treat the tip as priority. The SOL still moves, if the transfer is in the transaction. The page calls that a waste. It does not say the tip is refunded. Ineffective and wasted is the whole remedy on offer: do not do it. A trader, a sniper, or a wallet that adds a tip to every send has, on this page, a way to pay an auction that is not being held.',
  'There is a second way to miss. “When tipping make sure to not use Address Lookup Tables for the tip accounts.” The page does not, in the sentences read, spell the failure mode beyond the instruction not to. The instruction is enough to print. A tip account that is reached through a lookup table is a tip the document tells you not to construct. Combined with the leader warning, the page is a short manual of payments that feel like priority and are not. The auction, when it is running, is the thing the tip is for. The page says a low tip might lose that auction. It does not print a schedule of winning tips. A number copied from a dashboard of recent tips would be that dashboard’s number. This page does not include one.',
  'Who receives the tip is “one of the 8 tip accounts.” The page does not, in the sentences this reading uses, describe the path from those accounts to a validator’s reward. It tells the sender to pick one, ideally at random, and to expect nothing if the leader is outside the set that honours the tip. Power sits with whoever is the leader in the slots that matter, and with whoever operates the auction the page says will ignore a low tip. The sender’s decision is the amount and the account. The page is frank that one of those decisions can be pure loss. The paper sent no bundle and paid no tip.',
 ],
 says=[
  'A tip is required for a bundle to be considered. It is a SOL transfer to one of eight tip accounts, which the page says can be fetched and have remained constant.',
  'The page advises choosing one of the eight at random.',
  'A tip that is too low might lose the auction. A tip paid when the leader is not a Jito-Solana leader does not buy priority and is described as a waste of money.',
  'The page says not to use address lookup tables for the tip accounts.',
 ],
 paid=[
  'The tip is paid in SOL to one of the eight tip accounts.',
  'The page does not say a wasted tip is refunded.',
  'It does not publish a winning tip amount.',
 ],
 decides=[
  'The sender chooses the amount and which tip account to pay.',
  'The auction selects bundles. A non-Jito leader, on this page, does not treat the tip as priority.',
 ],
 limits=[
  'No bundle was sent and no tip account balance was read.',
  'The path from the eight accounts to a validator reward is not in the sentences used here.',
  '“Might not be selected” is the page’s word for a low tip. No auction was observed.',
 ],
 sources=[dict(label='Jito low-latency transaction send', url='https://docs.jito.wtf/lowlatencytxnsend/', note='HTTP 200 on 17 Nov 2026.')],
 related=['velocity-says-it-forked-drift-and-that-drift-is-paused'],
)

R(
 title='Velocity Says It Forked Drift, and That Drift Is Paused',
 desk='investigations', desk_name='Investigations', feature='Claim Check',
 desc='Velocity’s migration page says it is a new programme, not an upgrade, and that the Drift programme is paused. The paper did not query the programme.',
 deck='A request for Drift’s docs on 17 Nov 2026 was answered by Velocity. Velocity’s own page says the old programme is paused and that no balance came along.',
 question='What does the migration page claim happened to Drift, and which of those claims did the paper not check on-chain?',
 paragraphs=[
  'On 17 Nov 2026 a request for the documentation index at docs.drift.trade was answered by docs.velocity.exchange. That is a retrieval fact about a URL. It is not, by itself, a statement that Drift’s programme is gone. The statement comes from a page on the site that answered. “Velocity Protocol is a fork of Drift Protocol v2, taken at Drift SDK v2.163.0-beta.0. It is not an upgrade of Drift in place. It is an entirely new onchain program deployment with a new program ID, a reduced feature set, and its own renamed SDK. The Drift program is paused, and no onchain state carries over: user accounts must be re-initialized and balances start fresh on Velocity.”',
  'The address warning is specific because a careless integrator will do the dangerous thing. “Because the program ID changed, every PDA address is different from Drift,” even for seeds the page says are “byte-for-byte unchanged,” and it lists user, user stats, perp market, spot market, spot market vault, and insurance fund vault. “One trading seed was also renamed: the State PDA seed went from drift_state to velocity_state. Never reuse a Drift-derived address on Velocity.” A paused programme and a new programme that reuses the old mental model is how people send funds to an address that does not mean what it meant last month. The page is written to stop that. This reading did not derive an address either way.',
  '“The Drift program is paused” is the sentence a claim check has to leave standing as a claim. It is on Velocity’s migration page. The paper did not read Drift’s programme account, did not ask Drift, and did not try to send a Drift instruction. A fork’s documentation has a reason to say the thing it forked is paused. That reason is not evidence, and it is not a reason to suppress the sentence. The sentence is printed. The check that would make it a finding — the account, the owner, the last successful instruction — was not done. Until it is done, the honest line is the one this paragraph just drew.',
  'The index of the same site says Velocity “is not open source yet,” and that what remains for an outside contributor “is a shorter list than most projects but not an empty one.” That sentence is the index’s, retrieved as llms.txt. The contributing page itself was not opened. A reduced feature set, a closed source, and a warning that every address moved are three different limits on the word “fork.” A fork can mean the code is public and the state continued. This page means the opposite on both counts: new deployment, no state, and, on the index, source that is not yet open. Traders who still say Drift because the interface feels familiar are using a name the migration page is trying to retire. The paper will use the name the page uses, and will not pretend the pause was observed.',
 ],
 says=[
  'A request for docs.drift.trade’s index on 17 Nov 2026 resolved to docs.velocity.exchange.',
  'The migration page says Velocity is a fork of Drift v2 at SDK v2.163.0-beta.0, a new programme id, a reduced feature set, and a renamed SDK.',
  'It says the Drift programme is paused and that no on-chain state carries over. Balances start fresh. Every PDA differs, and the state seed was renamed from drift_state to velocity_state.',
  'The retrieved documentation index says Velocity is not open source yet.',
 ],
 paid=['The migration page does not describe a fee for moving. It says balances do not move.'],
 decides=[
  'Velocity’s page tells integrators never to reuse a Drift address.',
  'Whether the Drift programme is in fact paused was not decided here. The page asserts it. The account was not read.',
 ],
 limits=[
  'No programme account was queried. “Paused” remains the page’s claim.',
  'The contributing guide was not opened. The “not open source yet” line is from the index that was retrieved.',
  'No user balance was compared between the two programmes.',
 ],
 sources=[
  dict(label='Migrating from Drift, Velocity docs', url='https://docs.velocity.exchange/developers/migrate-from-drift.md', note='HTTP 200 on 17 Nov 2026.'),
  dict(label='Velocity documentation index', url='https://docs.velocity.exchange/llms.txt', note='HTTP 200 on 17 Nov 2026. A request to https://docs.drift.trade/llms.txt resolved here.'),
 ],
 related=['a-liquidation-on-velocity-is-a-position-you-inherit', 'the-builder-fee-sits-on-top-and-a-bit-can-switch-it-off'],
)

R(
 title='A Liquidation on Velocity Is a Position You Inherit',
 desk='money', desk_name='Money and markets', feature='Who Gets Paid?',
 desc='Velocity’s liquidation tutorial says the liquidator takes the position and is paid in discounted collateral. No bot was run.',
 deck='The page refuses the picture of a forced sale into a book. The payment is a discount, and the discount is not profit until the inheritor can get out.',
 question='What does the liquidation tutorial say a liquidator is actually paid, and what must they already have?',
 paragraphs=[
  'The tutorial’s first correction is the whole piece. “A liquidation on Velocity is not a forced sale into the book. It is a liability transfer: the liquidator takes the failing account’s position onto its own books and is paid for doing so with the liquidatee’s collateral at a discount.” The matching bot and the trigger bot, the page says, “are paid a flat fee for pressing a button. This one is paid in risk it has to carry and then unwind.” A flat fee and a discount on someone else’s position are different businesses. The page wants a builder to notice before they copy the wrong bot.',
  'Two consequences follow, and the page says both shape the code. “A liquidator needs collateral, because the inherited position has to fit inside the liquidator’s own initial margin requirement. It also needs an exit, because the discount is only profit once the position is closed at a price near the one it was inherited at.” A liquidator who cannot post margin cannot take the position. A liquidator who takes it and cannot leave owns the risk they were paid to remove. The discount is not cash in the sentence. It becomes cash, the page says, only at the exit. That is a who-gets-paid rule with a condition the headline “paid at a discount” usually drops.',
  'The page is a tutorial for a bot anyone can run, in a system the same documentation index describes as having “no central matching engine.” The crossing, triggering, and closing “that a centralized exchange does in-process is done by offchain agents anyone can run, and the protocol pays per action.” The liquidation bot is the action that is not a flat fee. Permissionless, on this account, means anyone who can post the margin and stand the exit. It does not mean anyone with a script and an empty account. The paper did not run the bot, did not take a position, and did not measure a discount. The structure of the payment is what the tutorial is willing to teach.',
 ],
 says=[
  'Velocity describes liquidation as a transfer of the position onto the liquidator’s books, not a sale into the order book.',
  'The liquidator is paid with the liquidatee’s collateral at a discount, and the page says that discount is profit only after the position is closed near the inheritance price.',
  'The liquidator must have enough collateral for the inherited position to fit their own initial margin.',
  'Matching and trigger bots are described as flat-fee actions. Liquidation is described as paid in risk.',
 ],
 paid=[
  'The liquidatee’s collateral, at a discount, is the payment. It is not described as a separate token reward.',
  'The liquidator is not paid the discount in full, on this page, until they exit.',
 ],
 decides=[
  'Anyone who can run the bot and post the margin may liquidate, on the tutorial’s account. The paper did not verify that no key is required.',
  'The protocol defines the discount. The page does not print the rate in the sentences used here.',
 ],
 limits=[
  'No bot was run and no discount was observed.',
  'The discount rate is not stated in the portion this reading relies on. It is not guessed.',
  '“Anyone can run” is the documentation index’s description of keepers, paired here with the tutorial’s margin requirement.',
 ],
 sources=[
  dict(label='Velocity liquidation bot tutorial', url='https://docs.velocity.exchange/developers/trading-automation/keeper-bots/liquidation-bot.md', note='HTTP 200 on 17 Nov 2026.'),
  dict(label='Velocity documentation index', url='https://docs.velocity.exchange/llms.txt', note='HTTP 200 on 17 Nov 2026. The index says there is no central matching engine and that keepers are paid per action.'),
 ],
 related=['velocity-says-it-forked-drift-and-that-drift-is-paused', 'the-maintenance-margin-is-not-returned'],
)

R(
 title='The Builder Fee Sits on Top, and a Bit Can Switch It Off',
 desk='money', desk_name='Money and markets', feature='Who Gets Paid?',
 desc='Velocity’s builder-code page puts an app fee on top of the taker fee, capped at 1 percent, and a feature bit can disable it. No order was sent.',
 deck='The page answers a question interfaces usually hide: how the app that sent you there gets paid, in the programme, and how a single bit turns the rail off, referrals included.',
 question='Who can charge a fee on Velocity order flow, who set the ceiling, and what else goes dark when the bit is clear?',
 paragraphs=[
  'The page opens on the app’s problem. “A frontend that routes order flow to Velocity has no way to charge for it. It can build the interface, hold the users, and send the orders, and every basis point of the fee goes to the protocol and its makers.” The workarounds it rejects are “a separate backend” that takes custody, or a wrapper that “adds latency.” Builder codes “close that gap in the program itself. An order carries an identifier for the app that built it and a fee rate the user has approved in advance. The fill charges that fee on top of the taker fee, credits it to the builder, and the builder collects it later. No custody, no wrapper program, no relationship between the builder and the maker who filled the order.”',
  'The unit is small and the cap is not. “Builder fees are denominated in tenths of a basis point.” One unit is 0.001 percent, so 100 units are 10 basis points and 1,000 units are 100 basis points, which the page calls 1 percent. The fee is “notional times fee in tenth-basis-points, divided by 100,000.” It “does not reduce the taker’s fee tier or the protocol’s cut.” It accrues to the builder’s RevenueShareEscrow. Two ceilings are independent. The user sets a maximum per builder “which the program accepts with no upper bound of its own.” Separately, MAX_BUILDER_FEE_TENTH_BPS “caps the fee actually charged at 1000 tenth-bps, 1% of the filled notional.” An order above that “is rejected with InvalidBuilderFee,” error 6319. An order above the user’s own approved maximum is rejected too. The user can approve a number the programme will still refuse to charge. The programme will not charge more than 1 percent of notional, on this page, no matter what the user approved.',
  'The rail is behind a bit. State.featureBitFlags carries BuilderCodes, and “setting the bit takes a deliberate call” that “only the cold admin may sign.” Clearing the bit can be signed by “the cold, warm, or hot feature-flag key.” While the bit is clear, “no fill path loads that escrow at all,” and “the program treats every order as if it had no builder code. No fee is charged and nothing accrues.” The page then says this is “not only about builder fees.” “Referrer rewards and referee discounts ride the same RevenueShareEscrow,” so while the bit is clear “neither leg of the referral program is computed either.” One switch, three products: the app’s fee, the referrer’s reward, the referee’s discount. A hot key can turn them off. Only the cold admin, on this page, can turn them on.',
  'Silence is part of the design, and the page is proud of it in one place and not in another. An escrow “with no rows silently suppresses every fee, discount, and reward rather than failing.” The user must create the escrow before they can approve a builder, and numOrders must be at least 1. “settleRevenueShare is the exception and reverts outright” when the feature is disabled. Two of the three paths are silent. A trader who does not see a fee is not, on this page, looking at proof that no fee rail exists. They may be looking at a clear bit or an empty escrow. The paper did not read the bit on the state account. The page says to read it rather than assume.',
 ],
 says=[
  'A builder fee is carried on the order, approved in advance by the user, charged on top of the taker fee, and later collected by the builder.',
  'The unit is a tenth of a basis point. The programme caps the charged fee at 1 percent of notional even if the user approved more.',
  'Orders over the cap or over the user’s approved maximum are rejected.',
  'A feature bit gates the rail. Only the cold admin can enable it. The cold, warm, or hot key can disable it.',
  'While the bit is off, builder fees, referrer rewards, and referee discounts are not computed. An escrow with no rows suppresses them silently.',
 ],
 paid=[
  'The builder is credited the fee in a revenue-share escrow. The protocol’s cut of the taker fee is not reduced.',
  'Referrers and referees share that escrow’s rail. They are unpaid, on this page, whenever the bit is clear.',
 ],
 decides=[
  'The user approves a builder and a maximum. The programme enforces a separate 1 percent cap.',
  'The cold admin enables the feature. A hotter key can disable it.',
 ],
 limits=[
  'The feature bit on the live state account was not read.',
  'No order was built and no fee was charged.',
  'The taker-fee schedule this fee sits on is a different page and was not the source for a rate here.',
 ],
 sources=[dict(label='Velocity Builder Codes', url='https://docs.velocity.exchange/developers/builder-codes.md', note='HTTP 200 on 17 Nov 2026.')],
 related=['velocity-says-it-forked-drift-and-that-drift-is-paused', 'a-tip-can-be-spent-on-the-wrong-leader'],
)

R(
 title='The Auction That Delays the Fill on Purpose',
 desk='chain-watch', desk_name='Chain Watch', feature='The Fine Print',
 desc='Velocity’s JIT page says a taker order waits for makers to compete before it hits the book or the AMM. No auction was watched.',
 deck='Speed is the usual boast. This page describes a wait, inserted so that a market maker who was not resting an order can still win the fill.',
 question='Who benefits from the delay Velocity inserts before a taker order is allowed to hit the book?',
 paragraphs=[
  'The page names JIT, just-in-time auctions, as “Velocity’s price discovery mechanism.” “When a taker order arrives, market order or aggressive limit crossing the spread, it enters an auction where market makers compete to fill it at better prices before it hits the DLOB or AMM.” The order does not go straight at the resting book. It waits, on purpose, in a room the page says will often produce a better price. “Without JIT, taker orders would immediately execute against resting DLOB orders or the AMM at potentially worse prices.” The delay is the product. A culture that measures a venue by the time from click to fill is being told, on this page, that a little time was added back.',
  'The benefits are assigned. The auction aims to “improve price execution for takers by giving makers time to offer better prices,” to “reduce adverse selection by letting makers react to toxic flow,” to “increase competition among market makers for the same fill,” and to “enable offchain quoting where makers don’t need to rest orders, just respond to auctions.” Takers are promised a better price. Makers are promised a chance to see the toxic flow before they are filled against their resting quote, and a chance to quote without leaving an order on the book. Those are not the same benefit. A taker who wanted the resting price immediately is the person the mechanism delays. A maker who did not want to be picked off is the person it protects. The page states both purposes and does not pretend they are one.',
  'The paper did not time an auction and did not read the parameters the page says every such order carries. The opening of the page is the claim: a taker order is not allowed to hit the book or the AMM until makers have had a competition. How long that competition lasts, in slots or in milliseconds, is a number this reading will not import from memory. The documentation index, retrieved the same day, says Solana’s slot time “is dropping from 400ms to 200ms in steps, so a slot count is no longer a stable unit of time.” A delay measured in slots is, on that index, a delay whose wall-clock length is moving. This reading does not staple a slot count the auction page’s opening did not print onto that warning. It says the auction is a deliberate wait, and that the same site has warned that slots are no longer a clock. The two sentences are both retrieved. The arithmetic between them was not supplied by either page.',
 ],
 says=[
  'A marketable taker order enters a just-in-time auction before it can be filled by the DLOB or the AMM.',
  'The page says the auction exists to improve taker prices, to let makers react to toxic flow, to increase competition, and to allow off-chain quotes.',
  'The documentation index says slot time is dropping from 400 milliseconds to 200 milliseconds, so a slot count is not a stable unit of time.',
 ],
 paid=[
  'Makers who win the auction fill the taker. The page’s opening does not print their fee.',
  'The taker is delayed in exchange for the chance of a better price. No better price was measured here.',
 ],
 decides=[
  'The protocol inserts the auction. Makers decide whether to respond.',
  'The taker does not, on this page’s opening, opt out of the wait.',
 ],
 limits=[
  'No auction was observed. Duration parameters were not copied because they were not in the opening section this reading uses.',
  'The slot-time warning is the index’s general warning. It is not a measurement of an auction’s length.',
 ],
 sources=[
  dict(label='JIT Auctions, Velocity docs', url='https://docs.velocity.exchange/developers/market-makers/jit-auctions.md', note='HTTP 200 on 17 Nov 2026. The opening of the page was read.'),
  dict(label='Velocity documentation index', url='https://docs.velocity.exchange/llms.txt', note='HTTP 200 on 17 Nov 2026. The slot-duration summary was read there. The slot-duration page itself was not.'),
 ],
 related=['a-liquidation-on-velocity-is-a-position-you-inherit', 'a-keeper-co-signs-or-comes-back-later'],
)

R(
 title='Three Cards on a Wallet Post Are Not Three Stories',
 desk='investigations', desk_name='Investigations', feature='Claim Check',
 desc='The Seed Vault Wallet post carries cards about guardians, a hackathon, and a buy-and-burn. The full posts were not opened. The cards are not findings.',
 deck='A page retrieved for one purpose also advertises three others. The honest use of those advertisements is to say what the card says, and to stop.',
 question='What can a newspaper print from a card it did not open?',
 paragraphs=[
  'The Seed Vault Wallet post of 14 July 2026 ends with three cards. They are not the article. They are the article’s suggestions, and they contain claims a careless reading will promote into the body. This reading writes them down as cards, because they were on a page that was retrieved, and it refuses to write them down as reported events, because the posts they point at were not opened.',
  'The first card is dated 11 November 2026 and headed “Introducing The First Solana Mobile Guardians.” The sentences on the card say guardians “are independent operators who run automated checks on every new app and update on the Solana dApp Store, recording each vote onchain.” “The first third party Solana Mobile Guardians, Helius and Jito, are now live.” Independent, automated, every new app, on-chain votes, and two named operators: that is a power story if the post it points to supports it. The card is four lines. It does not define the vote, the quorum, or what happens when the operators disagree. Helius and Jito are named. They were not asked. The SKR page, read separately, says stakers delegate to a guardian and prints a Solana Mobile Guardian Pool address. It does not name Helius or Jito. The card names them. The token page does not. Both facts can be printed. Neither makes the other false, and neither was checked against a vote account.',
  'The second card is dated 10 November 2026. “Builders submitted 469 mobile-first crypto apps to CLOCK IN, the Solana Mobile hackathon with RadiantsDAO, competing for $135,000 in prizes. Meet the ten winners, led by grand prize winner Sprouts, plus the SKR and ORE track winners.” Four hundred and sixty-nine, one hundred and thirty-five thousand dollars, ten winners, a grand prize name, two track names, and a partner named RadiantsDAO. Those are the card’s figures. The paper did not count the submissions, did not see the prize pot, and did not speak to anyone called Sprouts. Sprouts is the card’s name for a grand prize winner. This reading will not decide whether Sprouts is a person, a team, or a product. The campus desk does not get a dispatch out of a card. A dispatch would require the event page, a way for a reader to check the list, and a source who agreed to be described. None of that was opened.',
  'The third card is dated 3 November 2026. “A portion of revenue from Solana Mobile’s validator and Seed Vault Wallet will be used by the SKR Buy and Burn Program to buy and burn SKR. The Program began buy and burns on October 15, 2026, and every burn is verifiable onchain.” A portion, two revenue sources, a start date, and a promise that burns can be verified. “A portion” is not a percentage. “Will be used” sits next to “began” on 15 October. The card claims the programme has started and that the mechanism is public. The paper did not find a burn transaction. Verifiable is the card’s adjective. Verified is a different verb, and it was not performed.',
  'The rule this piece exists to demonstrate is the one the style book already prints. A fluent paragraph is not a source. A card is a source for its own sentences and for nothing they point at. The Degen can tell a reader that Solana Mobile’s wallet post, as retrieved, is willing to say these three things in its margin. It cannot tell a reader that the guardians voted, that 469 teams competed, or that a burn landed, because those verbs require the pages and the accounts that were left unopened. Leaving them unopened is the method. Filling them in from the card’s adjectives would be the failure.',
 ],
 says=[
  'A card dated 11 November 2026 says Helius and Jito are the first third-party Solana Mobile Guardians, running automated checks and recording votes on-chain.',
  'A card dated 10 November 2026 says CLOCK IN, with RadiantsDAO, drew 469 submissions for $135,000 in prizes, with ten winners and a grand prize named Sprouts.',
  'A card dated 3 November 2026 says a portion of validator and Seed Vault Wallet revenue buys and burns SKR, that burns began on 15 October 2026, and that every burn is verifiable on-chain.',
 ],
 paid=[
  'The burn card says a portion of two revenue streams is used to buy and burn SKR. It does not state the portion.',
  'The hackathon card states a $135,000 prize figure. The paper did not see the payment.',
 ],
 decides=[
  'The guardian card says independent operators check apps and record votes. It does not say who appoints them.',
  'None of the three cards was followed to its post. No decision was confirmed.',
 ],
 limits=[
  'The three full posts were not opened. Figures on the cards were not re-counted.',
  'No burn transaction and no guardian vote were read.',
  'Sprouts is not described as a student or as a person. The card does not say which it is.',
 ],
 sources=[dict(label='Seed Vault Wallet post, related cards', url='https://solanamobile.com/blog/seed-vault-wallet-solana-seekers-native-mobile-wallet', note='HTTP 200 on 17 Nov 2026. The cards at the foot of the post were read. The posts they link were not.')],
 related=['skr-inflation-starts-at-ten-percent-and-does-not-compound', 'double-tap-is-a-fingerprint-on-the-phone-you-already-hold'],
)

R(
 title='The Page That Says the Oracle Removes the Spread, and the Page That Charges It Twice',
 desk='investigations', desk_name='Investigations', feature='Claim Check',
 desc='One Flash page says oracle pricing eliminates bid-ask spreads. Another says a spread is charged on entry and on exit. No trade was priced.',
 deck='Both sentences are Flash’s. They were retrieved on the same day. A reader who quotes only the friendlier one has not read the fee.',
 question='What can be said when two pages of one protocol disagree about whether a spread exists?',
 paragraphs=[
  'The pool-to-peer page lists benefits in a table. One cell says oracle pricing “eliminates bid-ask spreads.” The matching, it says, happens “at the price published by a decentralized oracle,” and the trader does not “deal with slippage from insufficient liquidity at specific price levels.” On that page the oracle is a way to stop paying the book’s spread. The sentence is clean. It is also not the only sentence Flash published.',
  'The fee page says a “size-based spread” is “applied on entry and exit.” “It is charged on both legs: you pay spread when you open and again when you close. A take-profit target needs to clear roughly two spreads before the position is net positive.” The spread “varies per market and with market conditions.” The way to see it is to “compare the entry price against the oracle price.” The fee page therefore assumes an oracle price and a worse entry price, and it names the difference a spread. The mechanism page says the oracle eliminated the spread. The fee page says the spread is the difference from the oracle. A protocol can mean that there is no order-book spread and that there is still an execution spread. It can also mean that one page was not updated when the other was written. This reading cannot tell those stories apart, because it did not ask the authors and it did not open the panel the fee page says is the authority.',
  'What the paper can do is refuse the friendlier sentence as a summary. Any description of Flash that says “no spread, the oracle is the price” has dropped the fee page. Any description that says “the spread is a hidden tax” has gone past the fee page, which tells the reader the panel’s entry price already includes it and tells them how to see it: compare it with the oracle. Visible in a panel the paper did not open is not the same as hidden. It is also not the same as eliminated. The two pages, printed side by side, are the finding. A reconciliation would be a third document or a trade. Neither is in the record.',
 ],
 says=[
  'The pool-to-peer page says oracle pricing eliminates bid-ask spreads and avoids slippage from thin book levels.',
  'The fee page says a size-based spread is charged on entry and again on exit, and that the entry price should be compared with the oracle price to see it.',
  'The fee page says a take-profit has to clear roughly two spreads before it is net positive.',
 ],
 paid=[
  'If the fee page governs, the trader pays the spread twice, as a worse price rather than as a separate invoice line.',
  'The mechanism page does not name a spread recipient because it says the spread was eliminated.',
 ],
 decides=[
  'The paper does not decide which page a live order follows.',
  'The fee page says the order panel is the authority for a specific trade. The panel was not opened.',
 ],
 limits=[
  'No order was quoted and no author was asked.',
  'A possible reconciliation — no book spread, but an execution spread — is a hypothesis. It is not a finding.',
 ],
 sources=[
  dict(label='Pool-to-Peer Mechanism', url='https://docs.flash.trade/flash-trade/flash-trade-protocol/technical-architecture/pool-to-peer-mechanism.md', note='HTTP 200 on 17 Nov 2026.'),
  dict(label='Fees', url='https://docs.flash.trade/flash-trade/flash-trade-protocol/perpetuals-specifications/fees.md', note='HTTP 200 on 17 Nov 2026.'),
 ],
 related=['the-pool-is-the-other-side-of-every-trade', 'meme-markets-pay-a-different-open-fee'],
)

R(
 title='The Vault and the Browser Key Are Not the Same Bargain',
 desk='culture', desk_name='Internet culture', feature='Claim Check',
 desc='Solana Mobile says the key never leaves a secure element. Flash says a session key lives in the browser. No device and no browser were tested.',
 deck='The hardware story and the perps story are both on the public web. One refuses to let the secret out. The other puts a signer where the page is.',
 question='What is a reader being asked to trust in each design, according to the pages that describe them?',
 paragraphs=[
  'The Seed Vault Wallet post says the private keys “exist only in tamper-resistant hardware” and “never exist outside this secure environment.” “Even with root access to your phone, malicious software cannot access the Seed Vault contents or monitor your crypto activities.” The gesture in front of that claim is a double-tap and a fingerprint. The recovery, on the same post, is a 12-word phrase written on a card, which “provides complete wallet recovery on any Solana-compatible device,” while “Seeker-specific features like your Genesis Token and enhanced security remain tied to the hardware.” The secret is in the phone until the phrase is the secret, and the phrase is on paper. The post does not call the card a hardware wallet. It calls it the way back.',
  'Flash’s one-click page, retrieved the same day, describes a different signer for a different job. A session key “lives in your browser and signs trades for you.” It lasts “about 7 days.” It can “open, close, and manage positions using funds already deposited.” It cannot withdraw. The main wallet still has to sign to move funds out. A person can hold a Seeker in one pocket and a browser session in the other, and the two pages will not be describing one key. They will be describing two bargains. The phone bargain is that malware, even with root, cannot see the vault, if the post is right. The browser bargain is that a key which can trade cannot steal the deposit by withdrawing it, if the page is right. Neither page was tested against the attack it names.',
  'The funded-wallet page makes a third bargain, and it uses the words zero risk. Flash “controls the wallet infrastructure.” There is “no seed phrase” and “no transaction signing.” The starting capital “belongs to Flash.” The trader keeps what is above it after fifteen minutes. Set beside the Seed Card, this is the opposite instruction. One company tells you to write the phrase down and keep it off the device. Another tells you there is no phrase, because you were never the custodian. A culture that uses the same word, degen, for a phone that wants to be a vault and for a mode that starts at 125x will blur those instructions. The pages do not blur them. They are unusually clear, and they clear in different directions.',
  'What a reader should not do is average them into “Solana security.” A secure element that survives root, a browser key that expires in about a week, and a house wallet with no phrase are three products. Two of them were built to reach a perps book faster. One of them was built so the key would not have to live in the book’s page at all. The paper did not root a phone and did not install an extension. It can say which page promises which protection, and it can say that a protection described on a page is not a protection observed.',
 ],
 says=[
  'The Seed Vault Wallet post says private keys never exist outside the secure environment, and that root access still cannot read the vault or monitor its activity.',
  'The same post says a 12-word phrase on the included card recovers the wallet on any compatible device, while the Genesis Token stays tied to the hardware.',
  'Flash’s one-click page says a session key lives in the browser, can manage deposited positions, cannot withdraw, and expires in about seven days.',
  'Flash’s funded-wallet page says Flash holds the keys, there is no seed phrase, and the principal remains Flash’s.',
 ],
 paid=['None of the three pages prices the protection. The funded-wallet page prices the profit split. The session page mentions SOL rent. The phone post mentions rewards unlocked by the Genesis Token, without an amount.'],
 decides=[
  'The holder of a Seeker decides whether to write the phrase down and whether to import an old one.',
  'The Flash user decides whether to enable a browser key or redeem a funded code. Flash decides the funded wallet’s keys.',
 ],
 limits=[
  'No phone was rooted and no browser key was created.',
  'The root-resistance sentence is the post’s. It was not tested.',
  '“About 7 days” and “zero risk” are the pages’ phrases, already fenced in the readings that take each page alone.',
 ],
 sources=[
  dict(label='Seed Vault Wallet post', url='https://solanamobile.com/blog/seed-vault-wallet-solana-seekers-native-mobile-wallet', note='HTTP 200 on 17 Nov 2026.'),
  dict(label='One-Click Trading', url='https://docs.flash.trade/flash-trade/getting-started/one-click-trading.md', note='HTTP 200 on 17 Nov 2026.'),
  dict(label='Funded Wallet', url='https://docs.flash.trade/flash-trade/getting-started/funded-wallet.md', note='HTTP 200 on 17 Nov 2026.'),
 ],
 related=['double-tap-is-a-fingerprint-on-the-phone-you-already-hold', 'a-session-key-that-can-trade-and-cannot-withdraw', 'a-funded-wallet-that-says-zero-risk-and-then-describes-the-keys'],
)

R(
 title='The Forex Line Is the Wilder Number',
 desk='money', desk_name='Money and markets', feature='The Fine Print',
 desc='Flash’s margin table lists forex maintenance leverage at 2000x and crypto Degen Mode at 500x initial. The panel was not opened.',
 deck='The number people repeat is 500. The table’s larger multiple is on currencies, and it is a maintenance figure, which is not the same kind of boast.',
 question='Which published Flash multiple is actually the largest, and what does that multiple mean?',
 paragraphs=[
  'Degen Mode’s page puts 500 in the headline position: maximum leverage, SOL and BTC and ETH, a slider that starts at 125. The margin framework page, dated 2026-07-03 and marked tunable, puts that 500 in a cell under “Degen Mode” for crypto majors, and puts 1000 in the maintenance column beside it. Then it puts 2000 in the maintenance column for forex, with a standard initial cap of 200x and a dash where Degen Mode would be. Oil and gas sit at 7 to 12x initial. Meme markets sit at 30x initial. The table is a rebuke to the idea that the wildness lives where the culture says it lives.',
  'Maintenance leverage is not a slider. The page defines it as the denominator in the minimum collateral required to keep a position open. A 2000x maintenance line means the position’s minimum collateral, by the formula position size times one over that leverage, is a very small fraction of size. The buffer between a 200x initial forex cap and a 2000x maintenance line is wide in the formula and, the same page warns, shorter than it looks when the oracle’s confidence interval is applied against the trader. A large maintenance multiple is not a gift of 2000 times the position. It is a statement of how little collateral the protocol requires before it liquidates, on the formula as written. Confusing it with the initial cap is how a headline gets made out of the wrong column.',
  'The meme row is the cultural correction. Meme markets, 30x initial, 50x maintenance, and no Degen Mode dash filled in. The assets a timeline would call the degen trade are, in this snapshot, the ones with the tighter initial cap. Majors get the 500x mode. Forex gets the 2000x maintenance number and a 200x initial cap without that mode. The page says the slider in the panel is the live limit and that the values are tuned. This reading prints the snapshot and the warning, and it does not open the panel. A reader who wants the wildest number on the retrieved page will find it in the forex maintenance cell. A reader who wants the wildest initial cap will find Degen Mode on three crypto majors. Both readers are reading. They are not reading the same column.',
 ],
 says=[
  'As of the 2026-07-03 table, forex initial leverage is 200x and maintenance is 2000x. Degen Mode is not listed for forex.',
  'Crypto majors are 100x standard initial, 500x in Degen Mode, and 1000x maintenance.',
  'Meme markets are 30x initial and 50x maintenance.',
  'The page says these are tunable and that the trade panel’s slider is the live limit.',
 ],
 paid=['The margin table does not assign a fee. It assigns how close a position stands to liquidation, which other pages treat as a pool outcome.'],
 decides=[
  'The protocol publishes the caps. The trader chooses a leverage inside the initial cap the panel shows.',
  'Maintenance leverage is not described as the trader’s choice.',
 ],
 limits=[
  'The panel was not opened. The July 2026 snapshot may have moved.',
  'A 2000x maintenance figure is not restated here as permission to open a 2000x position. The initial cap in that row is 200x.',
 ],
 sources=[dict(label='Margin Framework, Flash Trade docs', url='https://docs.flash.trade/flash-trade/flash-trade-protocol/perpetuals-specifications/margin-framework.md', note='HTTP 200 on 17 Nov 2026.')],
 related=['five-hundred-times-and-the-orders-turned-off', 'degen-mode-starts-the-slider-at-125-times'],
)

R(
 title='The Meme Is Not Where the Multiple Lives',
 desk='culture', desk_name='Internet culture', feature='Claim Check',
 desc='Flash prices listed meme markets at a higher open fee and a lower leverage cap than SOL. The culture and the table do not match. No trade was placed.',
 deck='BONK, WIF, and the rest of the joke are on the fee page at 0.1 percent and on the margin page at 30x. The 500x mode is reserved for three majors.',
 question='What do the retrieved Flash pages actually offer a meme market, compared with what they offer SOL?',
 paragraphs=[
  'A culture that says degen and means a dog on a chart will look for the multiple next to the dog. Flash’s retrieved pages put the multiple next to SOL, BTC, and ETH, and put the dog in a more expensive, less levered row. The fee table dated 2026-07-03 lists meme markets — the page names BONK, PENGU, PUMP, WIF, and FARTCOIN — at 0.1 percent to open and to close. Majors, including SOL, are at 0.02 percent. ORE is at 0.5 percent. The margin table of the same date lists meme markets at 30x initial and 50x maintenance. Degen Mode, 125x to 500x, “currently” lists SOL, BTC, and ETH, and the margin page’s Degen column is filled for those three and dashed for meme markets.',
  'The fee-distribution table then pays the meme pool’s liquidity providers 80 percent, against 70 percent for the crypto pool. A higher open fee, a larger share to the pool, a lower leverage cap, and a mode that does not include the meme: that is a coherent commercial picture, and it is not the picture the word degen usually draws. The pool that specialises in the joke keeps more of a larger fee and offers less leverage. The pool that specialises in the majors keeps less of a smaller fee and, in one mode, offers the slider that starts at 125. Who that arrangement is for is a question the pages do not answer in a sentence. They answer it in the rows.',
  'Degen Mode’s own asset restriction is explicit. “Currently limited to SOL, BTC, and ETH.” The funded-wallet page says the session can trade “meme markets (BONK, WIF, PENGU, etc.)” and that Degen Mode is enabled at 125x to 500x. It does not say the meme markets themselves go to 500x. Reading the funded page alone could blur that. Reading it beside the margin table and the Degen Mode asset list unblurs it. The session may be allowed into the mode, and the mode may still refuse the meme. This reading did not click the market selector. The lists are the record. A joke that cannot reach the slider with its name on it is still, on these pages, a listed market. It is listed at a price and a cap the majors do not share.',
 ],
 says=[
  'The fee page lists named meme markets at 0.1 percent open and close, against 0.02 percent for the majors, as of 2026-07-03.',
  'The margin page lists meme markets at 30x initial leverage. Degen Mode’s page limits that mode to SOL, BTC, and ETH.',
  'The distribution page lists the meme pool’s liquidity-provider share at 80 percent and the crypto pool’s at 70 percent.',
  'The funded-wallet page names meme markets as available and names Degen Mode as available. It does not say meme markets inherit 500x.',
 ],
 paid=[
  'A meme-market open fee is five times the major’s open fee in the dated table, before the pool’s share is applied.',
  'The meme pool’s liquidity providers are assigned a larger share of fees than the crypto pool’s.',
 ],
 decides=[
  'The protocol’s tables decide the cap and the fee. The Degen Mode page decides which assets the mode lists.',
  'The paper does not decide that the live panel still matches the July snapshot.',
 ],
 limits=[
  'No market selector was opened.',
  'The tables are dated and the pages say numbers are tuned. “Five times” is this reading’s comparison of 0.1 and 0.02, not a fee the panel displayed.',
 ],
 sources=[
  dict(label='Fees', url='https://docs.flash.trade/flash-trade/flash-trade-protocol/perpetuals-specifications/fees.md', note='HTTP 200 on 17 Nov 2026.'),
  dict(label='Margin Framework', url='https://docs.flash.trade/flash-trade/flash-trade-protocol/perpetuals-specifications/margin-framework.md', note='HTTP 200 on 17 Nov 2026.'),
  dict(label='Degen Mode', url='https://docs.flash.trade/flash-trade/getting-started/degen-mode.md', note='HTTP 200 on 17 Nov 2026.'),
  dict(label='Fee Distribution', url='https://docs.flash.trade/flash-trade/flash-trade-protocol/technical-architecture/fee-distribution.md', note='HTTP 200 on 17 Nov 2026.'),
  dict(label='Funded Wallet', url='https://docs.flash.trade/flash-trade/getting-started/funded-wallet.md', note='HTTP 200 on 17 Nov 2026.'),
 ],
 related=['the-forex-line-is-the-wilder-number', 'meme-markets-pay-a-different-open-fee'],
)

R(
 title='Two Keepers You Cannot Join, or a Bot Anyone May Run',
 desk='power', desk_name='Power and politics', feature='Claim Check',
 desc='Jupiter says it operates two keepers. Velocity’s index says anyone may run the bots the protocol pays. No bot was operated.',
 deck='Both venues need a machine between a click and a fill. They do not describe the same permission to be that machine.',
 question='Who is allowed to finish a trade, on each retrieved page?',
 paragraphs=[
  'Jupiter’s technical reference is possessive. Keepers “are offchain services operated by Jupiter.” “Jupiter runs two keepers in parallel.” They poll for requests and they co-sign or they submit the second transaction that makes a JLP trade real. The page does not advertise a third seat. A trader who has signed has not finished. A stranger with a script has not been invited, in the sentences retrieved, to finish it for them. The power to complete the market is an operational fact about one company, stated as architecture.',
  'Velocity’s documentation index, which answered when Drift’s index was requested, describes the opposite invitation. “Velocity has no central matching engine. The crossing, triggering and closing that a centralized exchange does in-process is done by offchain agents anyone can run, and the protocol pays per action.” The liquidation tutorial narrows “anyone” with a margin requirement, but it does not replace “anyone” with a company name. A bot that matches, a bot that triggers, and a bot that inherits a position are jobs the index says are paid, and jobs it says are open. Open is not the same as easy. The tutorial says the liquidator must fit the position inside their own initial margin and must have an exit. The permission and the capital requirement are both printed.',
  'Flash’s liquidation page sits between them and does not choose. “Keeper bots continuously monitor every position and liquidate promptly.” It does not say Flash operates them, and it does not say anyone may. The sentence is a description of monitoring, not of a licence. A comparison that forced Flash into one of the other two camps would be inventing a clause. The paper’s job is to leave the clause missing.',
  'A reader who hears “on-chain perps” and pictures a trade that settles because the chain saw a signature has, on Jupiter’s page, a correction waiting. The chain has to see the keeper as well. A reader who hears the same phrase and pictures a company matching engine has, on Velocity’s index, a different correction. The engine is a crowd of bots the protocol pays, or it is two keepers a company runs, depending on which page you picked up. The paper picked up both and ran neither. The difference in the sentence “who may finish this” is the power story. The multiples are downstream of it.',
 ],
 says=[
  'Jupiter’s technical page says Jupiter operates the keepers and runs two of them in parallel, and that a JLP trade is not final without the keeper’s transaction.',
  'Velocity’s index says there is no central matching engine and that anyone can run the off-chain agents, which the protocol pays per action.',
  'Velocity’s liquidation tutorial adds that the liquidator must post margin for the inherited position.',
  'Flash’s liquidation page says keeper bots monitor and liquidate, without saying who may operate them.',
 ],
 paid=[
  'Velocity’s index says the protocol pays per action. The liquidation tutorial says that payment is a discount on collateral, not a flat fee.',
  'Jupiter’s keeper page, in the section read, does not price the keeper.',
 ],
 decides=[
  'On the Jupiter page, Jupiter’s keepers decide the fulfillment after the trader has signed.',
  'On the Velocity index, the set of operators is “anyone,” qualified by the tutorial’s capital requirement for liquidators.',
 ],
 limits=[
  'No keeper was run and no Jupiter keeper key was identified on-chain.',
  'Flash is not assigned to either model. Its page does not say.',
  '“Anyone” was not tested by attempting to run a bot.',
 ],
 sources=[
  dict(label='Jupiter Perps technical reference', url='https://docs.jup.ag/user-docs/trade/perps/technical-reference', note='HTTP 200 on 17 Nov 2026.'),
  dict(label='Velocity documentation index', url='https://docs.velocity.exchange/llms.txt', note='HTTP 200 on 17 Nov 2026.'),
  dict(label='Velocity liquidation bot', url='https://docs.velocity.exchange/developers/trading-automation/keeper-bots/liquidation-bot.md', note='HTTP 200 on 17 Nov 2026.'),
  dict(label='Flash liquidation', url='https://docs.flash.trade/flash-trade/flash-trade-protocol/perpetuals-specifications/liquidation.md', note='HTTP 200 on 17 Nov 2026.'),
 ],
 related=['a-keeper-co-signs-or-comes-back-later', 'a-liquidation-on-velocity-is-a-position-you-inherit'],
)

R(
 title='A Long and a Short, or One Net Position',
 desk='money', desk_name='Money and markets', feature='The Fine Print',
 desc='Jupiter’s JLP markets allow one long and one short in the same asset. Beta markets allow one net. No position was opened.',
 deck='The same brand’s two engines do not let a trader hold the same kind of inventory. The page that says so also says which collateral each engine demands.',
 question='What inventory does each Jupiter perps engine allow, and what collateral does it demand for it?',
 paragraphs=[
  'On the JLP markets the user page is permissive in a specific way. “Traders can hold up to 6 simultaneous positions,” and the six are “one per asset per side.” SOL, ETH, and BTC, long and short, fill the six. A long and a short in the same name are both allowed, and “same-side trades merge.” You do not stack two SOL longs as two tickets. You do stack a SOL long beside a SOL short, because they are different sides. The beta page describes the other engine. “One net position per market.” A long and a short in one beta name collapse into a net. The early-release label sits on that stricter inventory, not on the pool.',
  'Collateral follows the inventory. JLP longs post the asset: SOL, or the wrapped ETH, or the wrapped BTC. The page is explicit that the app’s ETH and BTC labels “are wETH and wBTC, the Portal-bridged versions on Solana.” JLP shorts post USDC. Beta markets post “USDC on every Beta market, for longs and shorts alike.” A trader who learned the collateral rule on SOL and then opens a beta stock market is under a different rule, and the beta page says so in a comparison table. The cost of holding changes with the engine too. JLP charges a borrow fee “on the position size, counted against collateral.” Beta charges “funding between longs and shorts, applied hourly.” Take-profit and stop-loss exist on JLP markets and “are not available” on beta markets.',
  'Six tickets versus one net is not a moral difference. It is a difference in what a hedge looks like. On the pool, a trader can be long and short the same asset at once, posting different collateral for each, paying a borrow fee that the risk box says walks the liquidation price closer even while the position sits. On the order book, the page says the position is a net, so the hedge is not two tickets. It is a smaller ticket. The paper did not open either ticket. The pages are the inventory rules. A reader who treats “Jupiter perps” as one market will miss the moment the collateral, the fee, and the meaning of “position” all change, which the docs mark with a badge.',
 ],
 says=[
  'JLP markets allow up to six positions, one per asset per side, so a long and a short in the same asset can both be open. Same-side trades merge.',
  'Beta markets allow one net position. Take-profit and stop-loss are not available there.',
  'JLP longs post the asset, and the page says ETH and BTC labels are Portal-bridged wrapped tokens. JLP shorts post USDC. Beta posts USDC for both sides.',
  'JLP charges a borrow fee against collateral. Beta charges hourly funding between longs and shorts.',
 ],
 paid=[
  'The borrow fee is paid on JLP position size and counts against collateral.',
  'Funding on beta markets is between longs and shorts, not described as a payment to the JLP pool.',
 ],
 decides=[
  'The engine, not the trader, decides whether two sides are two positions or one net.',
  'The trader chooses the engine by choosing the market. The page says the beta badge is the mark.',
 ],
 limits=[
  'No position was opened.',
  'Portal bridge risk for wETH and wBTC is named by the page’s identification of the tokens. It is not a separate audit.',
 ],
 sources=[
  dict(label='Jupiter Perps', url='https://docs.jup.ag/user-docs/trade/perps', note='HTTP 200 on 17 Nov 2026.'),
  dict(label='Beta markets', url='https://docs.jup.ag/user-docs/trade/perps/beta-markets', note='HTTP 200 on 17 Nov 2026.'),
 ],
 related=['two-hundred-and-fifty-times-against-the-pool', 'the-leverage-between-two-tiers-inherits-the-higher-cap'],
)

R(
 title='The Dated Table Loses to the Panel',
 desk='chain-watch', desk_name='Chain Watch', feature='The Fine Print',
 desc='Flash and Jupiter both print leverage tables and then tell the reader the live panel wins. The panels were not opened.',
 deck='A snapshot with a date is a real document. It is also, on these pages, a document that has already agreed to be overruled.',
 question='What is the status of a published number once the page that published it defers to a screen?',
 paragraphs=[
  'Flash’s margin page prints a table and then disowns it in the same breath. “Values are per-market protocol parameters as of 2026-07-03 and are tuned over time; the leverage slider in the trade panel always shows the live limit.” The fee page says the order panel “is always the authority for your specific order,” and dates its open-fee table to the same day. The max-profit page dates its payoff caps to 2026-07-03 and says the position panel shows the live max-profit price. The liquidation page says to “watch the panel, not the math.” Four pages, one gesture. The prose will give you a number. The prose will also tell you not to trade the prose.',
  'Jupiter’s beta page does the same thing with a closer date. “Values on November 13, 2026; the popover prevails.” The popover, not the documentation, is the cap. A $10,000 JUP figure in the doc is a figure as of that day, and the page has pre-announced its own obsolescence. This is a better habit than an undated boast, and it is a worse habit than a number a reader can check without opening an account. The paper can print the dated number and the deference. It cannot print the panel. The style book says the paper does not describe a screen it did not open. These pages are asking every reader to open one. The reading stops where the page points at the glass.',
  'The practical consequence is for anyone quoting this newspaper later. A sentence that says “Flash meme markets are 30x” is true as a description of a table dated 3 July 2026, and incomplete if it drops the page’s next clause. A sentence that says “the cap is whatever the panel showed someone on a different day” is a rumour about a screen. The form this paper will use is the dated table plus the refusal. That is less shareable than a multiple. It is the only form the retrieved pages actually support. When a future correction comes, it will be because a panel was opened and written down with its own date, or because the docs changed. It will not be because a slider was imagined.',
 ],
 says=[
  'Flash’s margin, fee, max-profit, and liquidation pages defer live numbers to the trade panel and date at least the margin and fee snapshots to 2026-07-03.',
  'Jupiter’s beta page dates position caps to 13 November 2026 and says the popover prevails.',
  'Both sets of pages still print the numbers. The deference does not delete the snapshot.',
 ],
 paid=['No fee is at issue. The status of a published number is.'],
 decides=[
  'The pages decide that the interface outranks the table for a live order.',
  'This newspaper decides not to describe the interface it did not open.',
 ],
 limits=[
  'No panel and no popover were opened on 17 Nov 2026.',
  'A dated snapshot is not a claim that the number was still on the panel that afternoon.',
 ],
 sources=[
  dict(label='Flash margin framework', url='https://docs.flash.trade/flash-trade/flash-trade-protocol/perpetuals-specifications/margin-framework.md', note='HTTP 200 on 17 Nov 2026.'),
  dict(label='Flash fees', url='https://docs.flash.trade/flash-trade/flash-trade-protocol/perpetuals-specifications/fees.md', note='HTTP 200 on 17 Nov 2026.'),
  dict(label='Jupiter beta markets', url='https://docs.jup.ag/user-docs/trade/perps/beta-markets', note='HTTP 200 on 17 Nov 2026.'),
 ],
 related=['the-forex-line-is-the-wilder-number', 'the-leverage-between-two-tiers-inherits-the-higher-cap'],
)

R(
 title='An Old Seed Typed into a New Phone',
 desk='culture', desk_name='Internet culture', feature='The Fine Print',
 desc='The Seed Vault post says a fresh phrase is safer than an imported one, and still offers the import. No phrase was typed.',
 deck='The setup page tells you the safer choice and then shows you the other door. The other door is how a history of trades moves onto the hardware.',
 question='What does the post say changes, and what does it say does not, when a person imports a seed instead of generating one?',
 paragraphs=[
  'The post’s setup is a fork. “New Wallet: The app generates fresh private keys directly in the Seed Vault hardware and provides a 12-word recovery phrase. Write this phrase on the included Seed Card.” “Import Existing: Enter your current Solana wallet’s seed phrase to migrate your holdings into the Seed Vault. Your transaction history and associated accounts transfer automatically.” Then the ranking. “A new wallet is the most secure, as the seeds will be freshly generated and only on your Seeker device.” The import is not forbidden. It is described, and it is described as less secure, because the phrase has already lived somewhere else. The post does not list the somewheres. A screenshot, a notes app, a previous phone, a chat: none of those are named. “Only on your Seeker” is the property the new wallet has and the imported one, by the post’s logic, has already lost.',
  'What does transfer, on the import path, is “transaction history and associated accounts.” The holdings move because the phrase is the holdings. The history the post mentions is the chain’s history, available to anyone who knows the accounts, not a private diary the phone uniquely recovers. The post does not say the old copy of the phrase is destroyed. Typing a phrase into a new device does not, on any sentence retrieved, erase the phrase from the place it was typed out of. The safer path is the one that never had another copy. The offered path is the one that brings the old life along, including whatever else that phrase could already sign.',
  'The help article from 2025 describes a different migration, between apps on a phone that already has the vault. “There’s no need to expose sensitive information. You just approve access using your password or fingerprint.” That is an approval, not a paste, and it assumes the seed is already inside. The 2026 post’s import is the paste the help article calls risky, performed once, at the door, in order to get the seed inside. The two pages are not in conflict if they are read as two moments. They are in conflict if a reader thinks “Seed Vault means I never type a phrase.” The post’s import button is the sentence that makes that thought false. The paper did not type one.',
 ],
 says=[
  'The post says a new wallet generates keys in the hardware and shows a 12-word phrase to write on the included card.',
  'It says importing means entering an existing phrase, and that history and associated accounts come with it.',
  'It says the new wallet is the most secure because the seeds are fresh and only on the device.',
  'The 2025 help article says moving between wallet apps on the vault is an approval, not a paste.',
 ],
 paid=['No fee is charged for either setup path on these pages.'],
 decides=[
  'The holder chooses generate or import. The post ranks generate as safer and still implements import.',
  'The post does not say the old copy of an imported phrase is wiped.',
 ],
 limits=[
  'No phrase was entered and no old device was wiped.',
  '“Most secure” is the post’s ranking, not a test.',
 ],
 sources=[
  dict(label='Seed Vault Wallet post', url='https://solanamobile.com/blog/seed-vault-wallet-solana-seekers-native-mobile-wallet', note='HTTP 200 on 17 Nov 2026.'),
  dict(label='Seed Vault help article', url='https://wallet-help.solanamobile.com/en/articles/11727979-understanding-and-using-seed-vault-features', note='HTTP 200 on 17 Nov 2026. Dated 9 July 2025.'),
 ],
 related=['double-tap-is-a-fingerprint-on-the-phone-you-already-hold', 'eight-seeds-and-saga-is-still-in-the-sentence'],
)

R(
 title='The College Rule Sits Next to the Multiple',
 desk='opinion', desk_name='Opinion and debate', feature='Claim Check',
 desc='The paper’s own policy says a student is not required to trade or take a loss. The perps pages describe 250x and 500x. No student was assigned either.',
 deck='One of this paper’s opinion assignments asks whether a college should teach leveraged trading. It is still an assignment. This reading only puts the published rule next to the published multiples.',
 question='What do the college’s own pages forbid, and what do the retrieved perps pages offer, when they are read on the same day?',
 paragraphs=[
  'The policies page of this newspaper says “a student is not required to trade, deposit funds, take a loss, or hand over personal financial details in order to report for the paper or to complete coursework.” If a story needs the writer to try a product, “the trial uses a simulation or a test environment, and the piece says what that trial cannot show.” “No such assignment has been given to a student. No student is named on these pages.” The opinion desk already lists the question “Should a college teach leveraged trading?” as a beat, and the assignment board says the leverage-slider piece has not been reported and that no designer has been interviewed. Those sentences are the college’s. They are not a review of Flash or of Jupiter. They are the rule under which a review would have to be done.',
  'The pages retrieved on 17 Nov 2026 are the thing the rule is about, whether or not a seminar is ever convened. Jupiter’s perps page prints 1.1x to 250x on the JLP markets, a 10 dollar minimum, a borrow fee that moves the liquidation price, and a warning to trade only with funds you can afford to lose. Flash’s Degen Mode page starts a slider at 125x, lists 500x, removes stop orders and limit orders, and warns of complete loss within seconds. The funded-wallet page offers that mode with the house’s capital and a fifteen-minute clock. None of those pages is coursework. All of them are public, specific, and aimed at a person with a finger on a button. A college that teaches how these mechanisms work is not, by the policy, a college that may require the button. A college that assigned the button would be breaking a rule it printed before this edition existed.',
  'This reading does not answer the assignment. An answer would be an argument about what should be taught, with a statement of what would defeat it, and a named writer’s interests. The publisher is the only author on these pages, and no holding is on file because no person is named. What can be said without becoming that essay is narrower. The mechanisms are now in the reading edition as documents. The prohibition on requiring a deposit or a loss is still the policy. The slider assignment is still not reported. A reader who came for a verdict on whether 500x belongs in a classroom will not find it. They will find the terms, and the rule that a student does not have to touch them.',
 ],
 says=[
  'The Degen policies page says a student is not required to trade, deposit, take a loss, or hand over financial details for coursework or for reporting.',
  'It says a product trial, if one is ever assigned, uses a simulation and states what the simulation cannot show. It says no such assignment has been given.',
  'Jupiter’s page prints a 250x cap and a 10 dollar minimum. Flash’s Degen Mode page prints a 125x floor and a 500x figure, without stop orders.',
 ],
 paid=['The college pages describe no tuition for this paper. The perps pages describe fees and, in the funded-wallet case, a profit split. None of those payments is a student requirement.'],
 decides=[
  'The publisher wrote the student rule and can edit it. The policy says there is no separate editor who can overrule the publisher.',
  'No student was asked to decide anything about these products.',
 ],
 limits=[
  'This is not the opinion assignment on teaching leverage, and it is not the slider assignment. Both remain unreported.',
  'No student is named. No course was observed requiring a deposit.',
 ],
 sources=[
  dict(label='Jupiter Perps', url='https://docs.jup.ag/user-docs/trade/perps', note='HTTP 200 on 17 Nov 2026.'),
  dict(label='Degen Mode', url='https://docs.flash.trade/flash-trade/getting-started/degen-mode.md', note='HTTP 200 on 17 Nov 2026.'),
  dict(label='The Degen policies', url='https://sol.college/degen/policies/', note='The college’s own published rule, quoted as the rule on the page, not as an outside report.'),
 ],
 related=['degen-mode-starts-the-slider-at-125-times', 'two-hundred-and-fifty-times-against-the-pool'],
)

R(
 title='Android Draws the Prompt the Help Page Says Android Cannot See',
 desk='investigations', desk_name='Investigations', feature='Claim Check',
 desc='The help page says Seed Vault is isolated even if Android is compromised. The developer page says Android draws the signing prompt. No phone was compromised.',
 deck='Two Solana Mobile pages describe the same vault’s relationship to the operating system. One banishes Android. One employs it. The paper did not stage the attack either page is about.',
 question='What does each retrieved page claim Android can and cannot do to a Seed Vault signature?',
 paragraphs=[
  'The help article of 9 July 2025 says Seed Vault “operates within the phone’s most secure hardware environment—completely isolated from Android and other apps—to ensure that your sensitive information remains protected, even if the operating system is compromised.” Isolation is complete, in that sentence, and it survives a compromised operating system. The secret and the system are on opposite sides of a wall. The article also says signing is something you authorise “with your password or biometrics,” without saying which component paints the password box.',
  'The developer page retrieved on 17 Nov 2026 draws the wall in a different place. Keys, seeds, and secrets “never leave the secure execution environment, while UI components built into Android handle interaction with the user to provide a secure transaction signing experience.” The secret stays. The interaction is Android’s. A prompt built by the operating system is the thing a compromised operating system is good at lying about. The developer page does not say the prompt is drawn inside the secure environment. It assigns the UI to Android and the key to the environment. The help page’s “completely isolated” and the developer page’s “Android handles interaction” can both be true if isolation means the key material and not the pixels. They cannot both be true if isolation means the user is shown a screen Android cannot forge. Neither page makes that distinction in those words. A reader has to notice that the pages chose different nouns.',
  'The July 2026 wallet post adds a third formulation. The biometric system “operates independently of Android’s fingerprint features” and “works even if your phone’s main security is compromised.” It also says that “even with root access,” malicious software “cannot access the Seed Vault contents or monitor your crypto activities.” Cannot monitor is stronger than cannot read the key. It claims the activity itself is invisible to root. The developer page does not say that. The help page says the information remains protected if the operating system is compromised, which is closer to the post, and still does not say “cannot monitor.” Three pages, three strengths. The paper will not average them into a single security rating. It will say the strongest monitoring claim is in the marketing post, the UI concession is in the developer doc, and the word “completely” is in a help article from 2025 that also still mentions Saga.',
  'What would settle it is a compromised device, a prompt, and a log. None of those is in the record. Until they are, the discrepancy is the story. A phone sold as a hardware wallet has published, in its own docs, both a promise that Android is on the wrong side of the wall and a design in which Android paints the wall’s only window. That is worth more than a repeated slogan. It is the fine print of the slogan.',
 ],
 says=[
  'The 9 July 2025 help article says the vault is completely isolated from Android even if the operating system is compromised.',
  'The developer page says Android UI components handle the signing interaction, while keys never leave the secure execution environment.',
  'The 14 July 2026 post says the crypto biometric layer is independent of Android’s fingerprint features and that root cannot read the vault or monitor its activity.',
 ],
 paid=['No fee is attached to these claims.'],
 decides=[
  'The pages do not say the user can choose which component draws the prompt.',
  'The paper does not decide which formulation a device implements.',
 ],
 limits=[
  'No phone was rooted and no prompt was photographed.',
  'A possible reconciliation — the key is isolated and the pixels are not — is a reading of the nouns. It is not a finding about a device.',
 ],
 sources=[
  dict(label='Seed Vault help article', url='https://wallet-help.solanamobile.com/en/articles/11727979-understanding-and-using-seed-vault-features', note='HTTP 200 on 17 Nov 2026. Dated 9 July 2025.'),
  dict(label='Seed Vault developer doc', url='https://docs.solanamobile.com/solana-mobile-stack/seed-vault', note='HTTP 200 on 17 Nov 2026.'),
  dict(label='Seed Vault Wallet post', url='https://solanamobile.com/blog/seed-vault-wallet-solana-seekers-native-mobile-wallet', note='HTTP 200 on 17 Nov 2026.'),
 ],
 related=['seed-vault-is-a-system-service-not-a-second-gadget', 'eight-seeds-and-saga-is-still-in-the-sentence'],
)

R(
 title='Seventy-Five Percent Has a Missing Quarter',
 desk='money', desk_name='Money and markets', feature='Who Gets Paid?',
 desc='Jupiter’s perps page assigns 75 percent of JLP-market trading fees to the pool. It does not name the other 25 percent. No fee was traced.',
 deck='The counterparty is described with unusual clarity. The fee split is described with a hole, and the hole is part of the page.',
 question='Who does the Jupiter perps page say is paid, and which share does it leave unnamed?',
 paragraphs=[
  'The page is precise about the pool’s role and then precise about a percentage that does not add to a hundred. “In return, the pool earns 75% of the trading fees of the SOL, ETH, and BTC markets.” The same paragraph adds that liquidity providers earn “75% of the fees generated by trading on the JLP markets, swaps, and JLP minting/burning.” JLP holders “act as the counterparty to all trades on these markets: when traders profit, the pool pays out; when traders lose, those losses flow back into the pool.” A reader can draw the counterparty arrow. A reader cannot, from this page, draw the remaining quarter of the trading fee. Twenty-five percent is what arithmetic does to seventy-five. The page does not say “the protocol keeps 25 percent,” and this reading will not say it for the page.',
  'What the trader pays is listed separately from that split. The how-it-works line says the trader “pays borrow fees, base fees, and price impact fees.” The price-impact fee exists “to protect liquidity providers from large or imbalanced trades.” Borrow fees “accrue continuously and move your liquidation price closer to the current price over time.” So the pool is protected by a fee whose size grows with the trade’s imbalance, and the trader’s liquidation line moves because a borrow fee accrues, and the pool also receives 75 percent of trading fees and the trader’s losses. That is a stack of flows toward the pool. It is not a complete stack, because the unnamed quarter is still unnamed, and because the page does not say whether borrow fees and price-impact fees are inside the “trading fees” the 75 percent applies to or beside them. The grammar does not force the answer. Forcing it would be a finding.',
  'Beta markets are the control. They “do not use the JLP pool.” Their fees are taker and maker fees, and their funding is between longs and shorts. The 75 percent sentence is fenced to the SOL, ETH, and BTC markets. A person who provides JLP is not, on this page, the counterparty to the beta book. A person who trades beta is not paying the pool the page has just described. The missing quarter and the fenced percentage are both reasons to read the market badge before repeating “JLP earns the fees.” The paper did not trace a fee account. The hole is the page’s, and it is printable because the page printed 75 and stopped.',
 ],
 says=[
  'The pool earns 75 percent of the trading fees on the SOL, ETH, and BTC markets, and the page also attaches 75 percent to swap and to JLP mint and burn fees.',
  'Traders pay borrow fees, base fees, and price-impact fees. Price impact is described as protection for liquidity providers. Borrow fees move the liquidation price.',
  'The page does not name a recipient for the other 25 percent of trading fees.',
  'Beta markets do not use the JLP pool.',
 ],
 paid=[
  'JLP holders are paid 75 percent of the fees the page names, and they pay trader profits out of the pool.',
  'The remaining share of trading fees has no recipient in the retrieved text.',
 ],
 decides=['The page states the 75 percent. It does not say who sets it or who receives the rest.'],
 limits=[
  'No fee account was read.',
  'This reading does not fill the unnamed quarter in with a protocol treasury or any other payee.',
  'Whether borrow fees sit inside the 75 percent base is not stated. It stays unstated.',
 ],
 sources=[dict(label='Jupiter Perps', url='https://docs.jup.ag/user-docs/trade/perps', note='HTTP 200 on 17 Nov 2026.')],
 related=['two-hundred-and-fifty-times-against-the-pool', 'a-long-and-a-short-or-one-net-position'],
)

R(
 title='One Page Needs No Insurance Fund. Another Still Names the Vault',
 desk='investigations', desk_name='Investigations', feature='Claim Check',
 desc='Flash says no insurance fund is required. Velocity still names an insurance-fund vault seed. No vault was read.',
 deck='The words “insurance fund” appear in two retrieved documents and do not mean the same thing. One is a denial. One is a renamed address.',
 question='What does each page actually say an insurance fund is doing?',
 paragraphs=[
  'Flash’s liquidation page makes the absence a feature. “Flash’s margining engine does not require an insurance fund: the pool that backs each position is always the counterparty, so there is always liquidity to close against.” The remainder of the maintenance margin “is not returned to the trader” and is “another source of yield for liquidity providers.” The pool is the backstop because the pool was the other side. A fund that socialises a shortfall is, on this page, unnecessary. The page does not say a shortfall cannot happen. It says the design does not require that particular pot.',
  'Velocity’s migration page, describing a fork of Drift, lists seeds that “are byte-for-byte unchanged” and still produce different addresses because the programme id changed. The list includes “insurance_fund_vault.” The seed’s name survived. The page does not say the vault is funded, empty, or retired. It says the address is different and must not be copied from Drift. A name in a list of PDAs is not a balance. It is evidence that the fork’s account layout still has a slot called an insurance fund, in the same breath as the page says no Drift state came along and balances start fresh.',
  'A reader who wants one Solana-perps truth about insurance funds will not get it from these two pages, and should not. Flash is describing a pool-to-peer design in which the LP is the counterparty and the leftover margin is yield. Velocity is describing address hygiene for a fork that still knows what an insurance-fund vault is. The paper did not read either account. Printing both sentences is the check. Concluding that “Solana perps have no insurance” would erase the seed. Concluding that “the fund protects you” would erase Flash’s explicit denial and would invent a balance Velocity’s page does not show.',
 ],
 says=[
  'Flash’s liquidation page says an insurance fund is not required because the pool is always the counterparty, and that remaining maintenance margin is not returned to the trader.',
  'Velocity’s migration page lists insurance_fund_vault among seeds whose text did not change and whose addresses all did.',
  'The same Velocity page says no on-chain state carries over and balances start fresh.',
 ],
 paid=[
  'On the Flash page, liquidity providers are paid the liquidation remainder as yield.',
  'On the Velocity page, the insurance-fund vault is a name, not a described payout.',
 ],
 decides=[
  'Flash’s design, as written, decides the pool is the backstop.',
  'Velocity’s page decides that old insurance-fund addresses must not be reused. It does not decide the vault’s balance.',
 ],
 limits=[
  'No vault account was read on either programme.',
  'The two pages are not claims about the same deployment.',
 ],
 sources=[
  dict(label='Flash liquidation', url='https://docs.flash.trade/flash-trade/flash-trade-protocol/perpetuals-specifications/liquidation.md', note='HTTP 200 on 17 Nov 2026.'),
  dict(label='Migrating from Drift', url='https://docs.velocity.exchange/developers/migrate-from-drift.md', note='HTTP 200 on 17 Nov 2026.'),
 ],
 related=['the-maintenance-margin-is-not-returned', 'velocity-says-it-forked-drift-and-that-drift-is-paused'],
)

R(
 title='A Stock Token the Fee Page Will Not Offer to a U.S. Person',
 desk='power', desk_name='Power and politics', feature='The Fine Print',
 desc='Flash’s fee page says xStocks are not offered to U.S. persons and are not the shares themselves. The block was not tested.',
 deck='The same fee schedule that prices a meme also carries a legal fence around tokenized equities. The fence is the page’s. The paper did not try to cross it.',
 question='What does the fee page say an equity perpetual is, and who does it say must not be sold one?',
 paragraphs=[
  'Most of Flash’s fee page is a table of open fees and a formula for utilization. At the bottom, in a warning, the subject changes. “xStocks are tokenized equity products issued by Backed Assets (JE) Limited, now part of the Kraken group. xStocks are not marketed, offered, or solicited to U.S. persons or within the United States, nor in any jurisdiction subject to international sanctions or where such activity is otherwise prohibited.” They “do not represent direct ownership of the underlying shares.” The margin page lists equities at 25x initial leverage and 50x maintenance, and the pricing page lists tokenized equities with an 11.7 percent volatility threshold, wider than crypto majors. A product that can be levered, on one page, is a product that cannot be offered to a class of people, on another, and is not the thing it is named after.',
  'The issuer is named and the seller’s duty is written as a prohibition on marketing, offering, and soliciting. The page does not say what the interface does if a U.S. person arrives anyway. It does not define U.S. person. It does not say the paper tested a block. A prohibition in a docs warning is a term. A geofence in an app is a mechanism. This reading has the term. The funded-wallet page says synthetic markets include equities and that “standard market hours apply” for FX, metals, and commodities. It does not repeat the U.S. person sentence. A session aimed at a new user can, on that page, reach synthetic markets, and the fee page’s warning still sits on xStocks whether or not the session page remembered to point at it.',
  '“Do not represent direct ownership” is the sentence a ticker will not display. A reader who sees a familiar equity name on a perps slate is, if this warning governs, looking at a token issued by a named company, not at the share. The leverage in the margin table applies to that token’s market. The ownership in a brokerage account is a different object. The page is doing the work a headline will not do, and it is doing it in a warning under a fee schedule, which is where fine print goes to be skipped. Printing it here is the point of the feature called The Fine Print.',
 ],
 says=[
  'The fee page says xStocks are issued by Backed Assets (JE) Limited, now part of the Kraken group, and are not the underlying shares.',
  'It says they are not marketed, offered, or solicited to U.S. persons, in the United States, in sanctioned jurisdictions, or where prohibited.',
  'The margin page lists equities at 25x initial and 50x maintenance. The pricing page lists an 11.7 percent threshold for tokenized equities.',
 ],
 paid=['The warning is not a fee. Equities are in the 0.02 percent open-fee row, with AMD called out at 0.05 percent, on the same page.'],
 decides=[
  'The page states who must not be solicited. It does not describe an enforcement mechanism.',
  'The issuer is named. The interface’s behaviour toward a prohibited person is not.',
 ],
 limits=[
  'No account was opened and no geofence was tested.',
  '“U.S. person” is the page’s term. It is not defined in the warning.',
 ],
 sources=[
  dict(label='Flash fees', url='https://docs.flash.trade/flash-trade/flash-trade-protocol/perpetuals-specifications/fees.md', note='HTTP 200 on 17 Nov 2026.'),
  dict(label='Flash margin framework', url='https://docs.flash.trade/flash-trade/flash-trade-protocol/perpetuals-specifications/margin-framework.md', note='HTTP 200 on 17 Nov 2026.'),
  dict(label='Flash pricing engine', url='https://docs.flash.trade/flash-trade/flash-trade-protocol/technical-architecture/pricing-engine.md', note='HTTP 200 on 17 Nov 2026.'),
 ],
 related=['meme-markets-pay-a-different-open-fee', 'a-volatility-flag-can-close-the-door'],
)

R(
 title='Eight Seeds, and One Token That Is Minted Once',
 desk='chain-watch', desk_name='Chain Watch', feature='The Fine Print',
 desc='The help page allows eight seed phrases. The Genesis Token doc mints one token per device. The two limits are not the same limit. No device was counted.',
 deck='A phone that can hold eight phrases and a token that can be minted only once per device is a phone with two different ideas of identity. Both ideas are published.',
 question='What does “one Seeker” mean once the vault is allowed to hold eight seeds?',
 paragraphs=[
  'The help article’s storage limit is eight. “Up to 8 seeds (12- or 24-word phrases),” each with “a unique password and optional biometrics,” so that a long-term holding and a day-to-day account can be locked differently, and so that apps can be granted access “per seed.” Eight identities, separated on purpose. The Genesis Token doc’s limit is one mint per device, into “the primary account” created “during device onboarding.” The token can later move between that user’s own accounts inside the wallet, and the mint address does not change. A device has one genesis mint and as many as eight phrases. The primary account is where the token starts. It is not, on the help page, the only account the vault will hold.',
  'Anti-sybil logic on the token page depends on the mint, not on the phrase count. An app that wants to pay once per device is told to remember the mint address, because the token might be transferred to another of the user’s wallets after a claim. A wallet might hold more than one genesis token, the page says, so a boolean is the wrong check. Eight seeds make that warning concrete. If each seed can have accounts, and the token can move among the user’s accounts, then “one phone” is not “one wallet” and not “one phrase.” It is one mint address, plus whatever else the vault was willing to store. An app that counted seeds would be counting the wrong thing. An app that counted wallets would pay the same device twice. The doc’s instruction is to count mints.',
  'The product page’s “non-transferrable” and the blog’s “non-transferable” sit awkwardly on top of this, and that awkwardness is already its own reading. Here the point is the capacity. A hardware wallet in the old sense often holds one seed and makes you feel that one seed is the person. These two pages, read together, describe a phone that will hold a handful of phrases and a device token that is minted once and then allowed to follow the primary account around inside the vault. Identity, for rewards, is the mint. Identity, for custody, is whichever of the eight you unlocked. The paper did not count the seeds on a phone. The numbers are the pages’ numbers, and they answer different questions.',
 ],
 says=[
  'The help article caps the vault at eight 12-word or 24-word seeds, with separate locks and per-seed app access.',
  'The Genesis Token doc says one token is minted per device, into the primary account, and may move between the user’s accounts inside Seed Vault Wallet without changing its mint address.',
  'The same doc says a wallet can hold more than one such token, so a reward check should remember every mint.',
 ],
 paid=['Rewards are the use case the token page describes. No reward amount is set.'],
 decides=[
  'The holder decides how many of the eight seeds to use and which apps may see each.',
  'An app decides whether a mint address has already been paid.',
 ],
 limits=[
  'No device was inspected. Eight and one are documentation limits, not a census.',
  'The marketing pages’ non-transferable wording is not re-decided here.',
 ],
 sources=[
  dict(label='Seed Vault help article', url='https://wallet-help.solanamobile.com/en/articles/11727979-understanding-and-using-seed-vault-features', note='HTTP 200 on 17 Nov 2026.'),
  dict(label='Seeker Genesis Token', url='https://docs.solanamobile.com/solana-mobile-stack/seeker-genesis-token.md', note='HTTP 200 on 17 Nov 2026.'),
 ],
 related=['eight-seeds-and-saga-is-still-in-the-sentence', 'anti-sybil-is-a-mint-address-not-a-face'],
)

R(
 title='Graduation Does Not Fall Back',
 desk='culture', desk_name='Internet culture', feature='Chain of Events',
 desc='Raydium’s overview says a launch that has graduated cannot return to the curve, even if the price falls. No launch was watched.',
 deck='The cultural moment of a meme launch is the curve. The overview’s event, in time order, ends the curve on purpose and refuses to reopen it.',
 question='What is the order of a LaunchLab launch on the overview page, and which step cannot be undone?',
 paragraphs=[
  'The overview tells the story in an order a chart will scramble. First the creator no longer has to seed both sides. Buyers send quote. The curve mints or releases base tokens at a price the formula sets. The quote vault accumulates. That accumulation is the balance checked against the graduation threshold, which was set at initialisation. Second, when the vault meets the threshold, the programme snapshots what remains of the base and what was collected in quote, creates a CPMM pool with those reserves, revokes the base mint’s authority so no further base tokens can be minted, and marks the launch graduated. Third, buys and sells on the curve reject. Trading continues on the pool, “indistinguishable from any other Raydium CPMM pool.” Fourth, and this is the sentence the culture of “it can always come back” does not survive: “Even if post-graduation trading pushes the AMM pool price back below the graduation price, the launch does not revert to the curve.”',
  'The order matters because the incentives reverse at the snapshot. Before it, a buyer is trading with a formula and, on the bonding-curve page, paying a fee that can include a creator share. After it, the buyer is trading a pool, the mint cannot grow, and the overview says the fees follow the pool’s config, typically a 0.25 percent tier. The creator’s ongoing share, if the launch has one, is whatever LaunchState.fees stored, and the instruction page says the creator claims curve-phase fees with a different instruction from the one a beneficiary uses after graduation. The overview’s time order and the instruction page’s callers are the same event seen as a story and as a permission. This reading keeps them as a sequence of claims, not as a transaction the paper sent.',
  'There is no fifth step in which the community votes the curve back into existence. The page is explicit that a price reversal does not reopen it. A launch that “graduates” has, in ordinary speech, succeeded. In this document, graduation is also the end of the mechanism that let people buy without a seeded pool. What remains is an ordinary pool and a mint that cannot be increased. Whether that is a promise or a trap depends on what was said in the launch’s own metadata, which this overview does not contain. The irreversible step is the part the overview is willing to put in order. The paper did not watch one happen.',
 ],
 says=[
  'The overview orders a launch as curve trading, then a threshold, then a CPMM pool, a revoked mint authority, and a status of graduated.',
  'Curve buys and sells reject after that. The pool is described as an ordinary Raydium CPMM pool.',
  'The page says the launch does not revert to the curve even if the pool price later falls below the graduation price.',
 ],
 paid=[
  'Before graduation, buyers pay quote into the curve. A creator share may apply and is stored per launch.',
  'After graduation, fees follow the pool config. The page names a typical 0.25 percent tier.',
 ],
 decides=[
  'The threshold is set at initialisation. Crossing it is the event the page describes as graduation.',
  'No later price action, on this page, can decide to reopen the curve.',
 ],
 limits=[
  'No launch was observed graduating.',
  'The migration wallet’s role is a different page. It is not restated here as if the overview named the signer.',
 ],
 sources=[dict(label='LaunchLab overview', url='https://docs.raydium.io/products/launchlab/overview', note='HTTP 200 on 17 Nov 2026.')],
 related=['the-curve-that-does-not-ask-the-creator-for-both-sides', 'the-migration-wallet-is-who-graduates-the-pool'],
)

R(
 title='Inflation That Decays and Does Not Compound',
 desk='money', desk_name='Money and markets', feature='The Fine Print',
 desc='The SKR page sets a 10 percent start, a 25 percent yearly decay, and a 2 percent floor, and says the schedule is linear. No issuance was measured.',
 deck='A percentage that decays by a quarter of itself each year is a specific machine. The page forbids the usual shortcut of compounding it, and it never says who receives the new tokens.',
 question='What can be computed from the SKR inflation sentence, and what must not be computed because the page does not supply it?',
 paragraphs=[
  'The sentence is short and already fenced. “Inflation starts at 10% and decays 25% per year until reaching a 2% terminal rate. Inflation is linear (not compounding).” Linear, not compounding, means a reader may not treat the 10 percent as a rate that itself earns the next year’s 10 percent. The decay is on the inflation rate. Twenty-five percent per year, applied to the rate, is a quarter of the current rate removed each year, until the rate is two percent and the decay stops. The page says “until reaching.” It does not print the year-by-year table. A careful paraphrase can say the rate falls by a quarter of itself annually and stops falling at the floor. It cannot say, from this page, what supply that rate is applied to, because the page never names the base. Ten percent of an unstated supply is not a number of tokens.',
  'The timing rules are better specified than the base. Epochs are two days. Unstaking is immediate and “tokens stop earning rewards right away.” Withdrawal waits forty-eight hours. A holder can leave the earning set in an instant and still not spend the tokens for two days. The page does not say whether a reward already accrued is paid at the unstake instant or only at an epoch boundary. “Stop earning” is not “forfeit what you earned.” It is also not “the reward token arrives in the same transaction.” The gap stays.',
  'Delegation is the condition on the whole schedule. Stakers “delegate their stake to a Guardian.” The inflation sentence sits in that section. A holder who does not delegate is not, on this page, described as earning the schedule. The Solana Mobile Guardian Pool has a printed address. Individual guardians are not listed on this page. A card on a different post names Helius and Jito. That card is not this schedule. The schedule is a rate, a decay, a floor, a denial of compounding, a two-day epoch, and a two-day cooldown, available to a holder who has delegated. Everything a yield advertisement would add — a token count, a recipient, a compounding APY — is exactly what the page withholds, and the withholding is the fact.',
 ],
 says=[
  'SKR inflation starts at 10 percent, decays 25 percent per year, and stops at a 2 percent terminal rate. The page says this inflation is linear, not compounding.',
  'Epochs last two days. Unstaking stops rewards immediately. A 48-hour cooldown applies before withdrawal.',
  'Stakers delegate to a guardian. The page does not say who receives newly issued tokens.',
 ],
 paid=[
  'Rewards are said to stop immediately on unstake. The asset of the reward, beyond SKR’s inflation sentence, is not itemised.',
  'No recipient of new issuance is named.',
 ],
 decides=[
  'The published schedule decides the shape of the rate. The holder decides whether to delegate and when to unstake.',
  'The page does not give the holder a way to change the 10, the 25, or the 2.',
 ],
 limits=[
  'No supply was read, so the percentages are not turned into a token count.',
  'Compounding is explicitly excluded by the page and is not smuggled back in as an annual yield.',
  'The guardian names on a different card are not part of this schedule.',
 ],
 sources=[dict(label='SKR docs', url='https://docs.solanamobile.com/solana-mobile-stack/skr.md', note='HTTP 200 on 17 Nov 2026.')],
 related=['skr-inflation-starts-at-ten-percent-and-does-not-compound', 'three-cards-on-a-wallet-post-are-not-three-stories'],
)

R(
 title='The Fork Dropped High Leverage and Changed the Dollar',
 desk='money', desk_name='Money and markets', feature='Claim Check',
 desc='Velocity’s migration page drops high-leverage mode and names USDT, not USDC, as the quote. No account was funded.',
 deck='A fork that is sold as the next home of a perps engine also publishes a list of what it threw away. High leverage is on that list. The dollar it settles in is a different mint.',
 question='What does the migration page say a Drift integrator loses, and which token does it say will not be accepted as quote?',
 paragraphs=[
  'The page is a migration note, and its most expensive line is not the new programme id. “This is the single most money-relevant change. On Drift, spot market 0 (the cross-margin quote and collateral asset) is USDC. On Velocity mainnet-beta it is USDT.” Both tokens, the page says, have six decimals, “so notional amounts look identical and nothing type-checks differently.” A desk that keeps funding accounts the way it funded Drift “is depositing the wrong token: deposits, withdrawals, ATA derivation, collateral, and settlement all reference the USDT mint.” The page prints the mints. Drift’s USDC is EPjFWdd5AufqSSqeM2qN1xzybapC8G4wEGGkZwyTDt1v. Velocity mainnet-beta’s USDT is Es9vMFrzaCERmJfrF4H2FYD4KCoNkY11McCe8BenwNYB. Devnet is a third mint, a dUSDT placeholder, GqmEqYsy8EyvofDpmtFxK8zhYrgWgNokAtYoduQdL7v6. The instruction is to stop hardcoding and read getConfig().QUOTE_MINT_ADDRESS. The paper did not call that function. The warning is the page’s, and it is written for someone whose code will compile while moving the wrong dollar.',
  'The same page says what the fork refused to carry. High leverage mode is one refusal. “The five HLM instructions and their config-account subscribers are removed. The onchain MarginMode enum and the User.marginMode field are gone.” A TypeScript class called MarginMode “still exists in the SDK, reduced to DEFAULT only, so imports don’t break.” The name survives as a stub. The mode does not. Prediction markets are in the same table: initialize_prediction_market is removed, and ContractType.PREDICTION “is now DEPRECATED_PREDICTION.” Spot order-book trading is removed even though spot markets remain “for collateral and borrow-lend.” Trying to place a spot order “returns SpotDlobTradingDisabled (6350).” Serum, Phoenix, and OpenBook fulfillment are gone. A protected-maker mode is gone. Legacy Pyth pull and push instructions are gone, and “Pyth Lazer is the supported Pyth path.” Switchboard clients are removed and their oracle-source names are marked deprecated, with the old discriminants kept. Staking a governance token for a fee discount is gone. “Perp fee tier is now based on 30-day volume, floored by an admin-set promo tier.” Protocol-owned insurance-fund shares and the rebalance instructions are removed. None of those sentences was checked against a running programme. They are the changelog.',
  'Set beside a venue that advertises five hundred times leverage, the changelog is the other culture. Flash’s Degen Mode page, retrieved the same day, starts a slider at 125x and names 500x for SOL, BTC, and ETH. Velocity’s page, describing itself as a fork of Drift taken at SDK v2.163.0-beta.0, says the high-leverage instructions were dropped and the client class was renamed from DriftClient to VelocityClient with “no back-compat alias.” The programme ids are printed too. Drift’s is dRiftyHA39MWEi3m9aunc5MzRF1JYuBsbn6VPcn33UH. Velocity’s is vELoC1audYbSYVRXn1vPaV8Axoa9oU6BYmNGZZBDZ1P. The page also says “The Drift program is paused.” That sentence is the publisher’s. This paper did not query the programme. A reader who wants the wildest multiple will not find it in this migration note. A reader who wants to know which dollar a copied integration will silently miss will find it in the first table, in a mint address, next to a sentence that says the types will not save you.',
 ],
 says=[
  'Velocity mainnet-beta uses USDT as the quote and collateral asset. Drift’s spot market 0 uses USDC. Both are described as 6-decimal tokens, so a wrong mint can still type-check.',
  'The page prints the USDC mint, the USDT mint, a devnet placeholder mint, and both programme ids.',
  'High-leverage mode, prediction-market initialisation, spot order-book trading, and governance-token fee discounts are listed as removed. Spot markets remain for collateral and borrow-lend. A spot order attempt returns error 6350.',
  'Pyth Lazer is named as the supported Pyth path. The page says the Drift programme is paused. That claim was not queried here.',
 ],
 paid=[
  'Perp fee tier, on this page, follows 30-day volume and can be floored by an admin-set promo tier.',
  'A governance-token stake no longer buys a fee discount, because that path is listed as removed.',
 ],
 decides=[
  'The fork’s authors, as the page describes them, decided which Drift subsystems to drop and which quote mint to require.',
  'An integrator decides whether to read the config mint or to keep a hardcoded USDC address. The page says the second choice deposits the wrong token.',
 ],
 limits=[
  'No account was funded and no programme account was read. “Paused” remains the page’s word.',
  'The page’s later sentence about a new liquidity-pool module is not finished in this reading, because this reading does not rely on a line it cannot quote in full.',
  'Error 6350 is the page’s name for a removed instruction. It was not reproduced.',
 ],
 sources=[
  dict(label='Migrating from Drift', url='https://docs.velocity.exchange/developers/migrate-from-drift.md', note='HTTP 200 on 17 Nov 2026.'),
  dict(label='Degen Mode', url='https://docs.flash.trade/flash-trade/getting-started/degen-mode.md', note='HTTP 200 on 17 Nov 2026. Used only for the 125x and 500x figures the migration page does not share.'),
 ],
 related=['velocity-says-it-forked-drift-and-that-drift-is-paused', 'five-hundred-times-and-the-orders-turned-off'],
)

R(
 title='You Cannot Enter Degen Mode by Pulling Collateral',
 desk='culture', desk_name='Internet culture', feature='The Fine Print',
 desc='Degen Mode blocks one way in, allows a way out, and still charges open and close fees. No mode was switched.',
 deck='The mode that removes the stop-loss also publishes a door policy. You may leave. You may not arrive by thinning the position you already have. The fees the slogan calls zero are a different fee.',
 question='What does the Degen Mode page say about switching modes, and which fee does “zero” actually cancel?',
 paragraphs=[
  'The page’s transition rules are short and unequal. “Cannot transition from normal mode using remove collateral.” “Can transition from Degen Mode to normal mode without restrictions.” “Existing positions must be closed before mode switching.” The door into the higher multiple is not a slider dragged on a live ticket, and it is not the act of pulling margin until the remaining collateral implies a wilder leverage. The page says that particular path is closed. The door out is described as free of restrictions, with one prior condition that applies in both directions: the positions have to be closed first. A trader who is already inside, on this text, cannot glide back to ordinary rules while the ticket is open. They close, and then they switch. The paper did not switch.',
  '“Zero” is narrower than the headline. Under “Zero Trading Costs” the page says swap fees are “completely eliminated on all trades” and, in the next bullet, “Position Fees: Standard open/close fees still apply.” The fee schedule retrieved the same day prices those open and close fees by market, including 0.02 percent on majors, and it prices a spread on both the open and the close. Degen Mode’s own asset table is only SOL, BTC, and ETH, each with a 500 figure, a max position, and a max exposure whose unit the table does not name. A reader who hears “zero trading costs” and stops has missed the bullet that keeps the open and the close. A reader who hears “500x” and stops has missed the sentence that the mode is “currently limited to SOL, BTC, and ETH,” so the meme markets on the other fee table are not, on this page, inside the mode.',
  'The page also raises the toll at the door without stating the toll. “Minimum Position Size: Higher entry requirements than normal mode.” “Higher Minimums: Substantial capital requirements for entry.” No number is attached to “higher” or “substantial.” The maximums are numbered, in thousands, without a unit. The minimums are adjectives. That is a different kind of fine print from a missing stop-loss, and it belongs next to it. The mode that tells an expert they can be wiped out in seconds also tells them the small ticket may not qualify, and then does not say how large the ticket has to be. The order panel, elsewhere in these docs, is declared the authority for a live number. This reading does not open the panel. It prints the adjectives, and it prints the rule that you do not get there by removing collateral from a position you already hold.',
 ],
 says=[
  'The page says a trader cannot enter Degen Mode by removing collateral, can leave the mode without restrictions, and must close existing positions before switching.',
  'Swap fees are described as eliminated. Open and close position fees are described as still charged.',
  'The listed assets are SOL, BTC, and ETH. Minimum size is described as higher than normal mode, without a number.',
 ],
 paid=[
  'Open and close fees still apply inside the mode. The fee page prices majors at 0.02 percent, dated as a snapshot.',
  'Swap fees, on the Degen Mode page, are the cost that is removed.',
 ],
 decides=[
  'The mode’s rules, as written, decide that one transition path is closed and that open positions block a switch.',
  'The page does not give the trader a number for the higher minimum. It points, by the rest of the docs’ habit, at a panel this paper did not open.',
 ],
 limits=[
  'No mode was switched and no position was closed.',
  'The unit on the max-position figures is not stated on the asset table, so the figures are not converted into a currency.',
 ],
 sources=[
  dict(label='Degen Mode', url='https://docs.flash.trade/flash-trade/getting-started/degen-mode.md', note='HTTP 200 on 17 Nov 2026.'),
  dict(label='Flash fees', url='https://docs.flash.trade/flash-trade/flash-trade-protocol/perpetuals-specifications/fees.md', note='HTTP 200 on 17 Nov 2026.'),
 ],
 related=['degen-mode-starts-the-slider-at-125-times', 'five-hundred-times-and-the-orders-turned-off'],
)

R(
 title='A Code Buys Fifteen Minutes, Not the Principal',
 desk='money', desk_name='Money and markets', feature='The Fine Print',
 desc='A funded-wallet code starts a fifteen-minute clock on the first trade and does not pay out the starting balance. No code was used.',
 deck='The page that says the house funds the stack also says the clock starts late, the principal stays, and a ten-dollar balance can turn the safety orders off. Another page, about the mode this wallet includes, says those orders are off anyway.',
 question='What does a funded-wallet code actually buy, and where do the two Flash pages disagree about stop orders?',
 paragraphs=[
  'The mechanics are a code, a clock, and a split. “Access to a valid Funded Wallet code” is a prerequisite. “Each code grants access to one Funded Wallet session.” The clock is “15 minutes of active trading time,” and it “starts on your first trade, not when you claim the wallet.” Planning is supposed to happen before the first click, because the first click is the start. Profits are “100% of profits above starting balance.” The worked example is a 100 dollar start, a 150 dollar end, and 50 dollars kept. “Only profits above the initial funded amount are withdrawable.” “The initial capital belongs to Flash Trade.” If the balance falls below the start, “you simply don’t profit — but you don’t owe anything either.” The house can lose the stack it posted. The holder cannot take the stack home, and cannot be billed for losing it, on these sentences. “After the session ends, any balance above the starting amount is yours to withdraw.” The withdrawal “follows standard Flash Trade procedures,” which this page does not reproduce.',
  'Two pages then disagree about the tools, and the disagreement is the fine print. The funded-wallet FAQ asks “Can I use limit orders or TP/SL?” and answers “Yes. All standard order types are available during your Funded Wallet session.” A warning under that answer says that if the starting amount “is not greater than $10 you will not be able to use these features.” The Degen Mode page, which the funded-wallet page explicitly includes — “Degen Mode enabled (125x–500x leverage)” — says “No TP/SL Support: Take profit and stop loss orders unavailable” and “No Limit Orders: Market orders only.” A session under ten dollars loses the orders because of the warning. A session inside Degen Mode loses them because of the mode page, and the funded page says the mode is available. The paper will not decide which page the interface obeys. It will say the docs, read together, do not let a reader treat “yes, all standard order types” as a rule that survives the mode the same page is selling.',
  'One answer on the page is printed here without repair, because repairing it would be a finding about what the author meant. Asked whether a connected wallet is needed, the page says: “Yes. The Funded Wallet is fully abstracted — external wallet connection required but is not used for trading can create a social account through Privy.” The grammar does not resolve whether the connection is required, unused, or a way to make a social account. Earlier bullets say there is “no seed phrase” and “no transaction signing,” and that “Flash Trade controls the wallet infrastructure.” The broken sentence is not edited into one of those clearer lines. Codes, the page says, come from “promotions, partnerships, and community events,” and a support note says legitimate support “will never ask for your private keys, recovery phrase, or Funded Wallet codes.” The paper does not have a code. It did not ask Discord for one. Synthetic markets on the same page “include FX, metals, and commodities,” and “standard market hours apply” to them. The hours themselves are not listed. A fifteen-minute clock that starts on the first trade can, on this text, open onto a market that is shut, and the page does not say what the button does then.',
 ],
 says=[
  'A code grants one session. The fifteen-minute timer starts on the first trade, not on the claim. Only profit above the starting balance is withdrawable, and a loss below the start is not a debt.',
  'The FAQ says limit, take-profit, and stop orders are available, unless the starting amount is not greater than 10 dollars.',
  'The same page says Degen Mode is enabled. The Degen Mode page says those orders are unavailable inside the mode.',
  'The wallet-connection answer is ungrammatical on the page. It is quoted as printed. It names Privy.',
 ],
 paid=[
  'The holder is paid profits above the starting balance. The starting balance is described as Flash Trade’s.',
  'Transaction costs are described as handled by the platform. The fee schedule is not waived by that sentence.',
 ],
 decides=[
  'The holder decides when the first trade starts the clock. The page decides that the principal is not withdrawable.',
  'Which page governs stop orders inside a funded Degen Mode session is not decided by the docs as retrieved.',
 ],
 limits=[
  'No code was entered and no session was timed.',
  'Market hours are named and not listed. The paper does not invent the hours.',
  'The Privy sentence was not rewritten into a cleaner rule.',
 ],
 sources=[
  dict(label='Funded Wallet', url='https://docs.flash.trade/flash-trade/getting-started/funded-wallet.md', note='HTTP 200 on 17 Nov 2026.'),
  dict(label='Degen Mode', url='https://docs.flash.trade/flash-trade/getting-started/degen-mode.md', note='HTTP 200 on 17 Nov 2026.'),
 ],
 related=['a-funded-wallet-that-says-zero-risk-and-then-describes-the-keys', 'five-hundred-times-and-the-orders-turned-off'],
)

R(
 title='The Wide Band Is Counted Against the Trader',
 desk='chain-watch', desk_name='Chain Watch', feature='The Fine Print',
 desc='Flash’s margin page says a volatile oracle prices liabilities up and assets down. No confidence interval was read.',
 deck='A second pricing rule sits under the leverage table. It does not close the market. It moves the numbers a liquidation uses, and it moves them in the house’s direction.',
 question='What does the margin page say a confidence interval does to a long and to a short when volatility is extreme?',
 paragraphs=[
  'The leverage table is the part of the margin page that travels. Under it is a shorter rule with a larger effect on a live ticket. “During periods of extreme volatility, position pricing follows conservative principles: the oracle’s confidence interval is applied so that prices used for opening, closing, and liquidation calculations maximize liabilities and minimize assets for traders.” The direction is not neutral. Liabilities go up. Assets go down. The interval is not described as a warning printed beside the price. It is described as an input to the price the system uses.',
  'The page then splits the direction by side. For longs, “the lower bound of the oracle confidence interval values your collateral and PnL — both are discounted, so liquidation can arrive earlier than mid-price math suggests.” For shorts, “the upper bound of the confidence interval prices your position — reducing recognized profit while volatility is elevated.” A long is marked on the worse low. A short is marked on the worse high. In both cases the sentence that follows is about the trader’s number getting worse, not about the pool’s collateral getting a matching haircut in the trader’s favour. The practical line is blunt: “run lower leverage and keep collateral well above the minimum — conservative pricing means liquidation distance is shorter than it looks.”',
  'This is not the same mechanism as the pricing engine’s close-only flag, which is a different page and a different trigger. That page describes a gap between price and an exponential moving average, and a state in which opens can be refused while closes and liquidations continue. This page describes a band around an oracle, applied so that the calculations already under way use the harsher edge. A market can, on these two documents, be open for new risk and still be marking that risk against the trader, or be closed to new risk and still be willing to liquidate. The paper did not read an oracle confidence figure on 17 Nov 2026. It did not measure a band. The rule is the sentence. Anyone quoting “100x” from the table above it without the sentence underneath is quoting the cap and dropping the way the cap is measured when the oracle is least sure.',
 ],
 says=[
  'In extreme volatility the margin page applies the oracle confidence interval so that liabilities are maximized and assets are minimized for the trader.',
  'Longs are valued on the lower bound, and the page says liquidation can arrive earlier than mid-price math. Shorts are priced on the upper bound, which reduces recognized profit.',
  'The page tells the reader to run lower leverage because the distance to liquidation is shorter than it looks.',
 ],
 paid=['No fee rate is set by this rule. The rule changes the price at which a liquidation, an open, or a close is calculated.'],
 decides=[
  'The page states the direction of the adjustment. It does not say the trader can opt out of it.',
  'What counts as extreme volatility is not defined on this page. The pricing engine’s thresholds are a different document.',
 ],
 limits=[
  'No oracle confidence interval was read, and no liquidation was observed arriving early.',
  'The close-only flag is not this rule. The two pages are not merged into one trigger.',
 ],
 sources=[
  dict(label='Flash margin framework', url='https://docs.flash.trade/flash-trade/flash-trade-protocol/perpetuals-specifications/margin-framework.md', note='HTTP 200 on 17 Nov 2026.'),
  dict(label='Flash pricing engine', url='https://docs.flash.trade/flash-trade/flash-trade-protocol/technical-architecture/pricing-engine.md', note='HTTP 200 on 17 Nov 2026. Cited only to keep the close-only flag distinct.'),
 ],
 related=['a-volatility-flag-can-close-the-door', 'the-forex-line-is-the-wilder-number'],
)

R(
 title='A Short Only Caps When the Price Reaches Zero',
 desk='money', desk_name='Money and markets', feature='The Fine Print',
 desc='Flash says a 100 percent payoff on a short reaches a max-profit price of zero. No short was opened.',
 deck='The profit cap is a lock the pool sets aside at the open. On a fully capped short, the page says that lock only binds if the asset is worth nothing. On a major, the same machine binds almost at once.',
 question='What does the max-profit page say the pool locks, and when does it say a short’s cap actually binds?',
 paragraphs=[
  'The page separates the cap from the rest of the ticket. “Every position has a hard cap on how much profit it can realize. That cap is set when the position opens, based on how much collateral the pool sets aside to pay you out.” It is “separate from your leverage, your liquidation price, or your collateral.” The lock is a formula. locked_usd equals size times max_payoff_bps over 10,000, plus the collateral. The first term is “the maximum the pool will pay out as profit.” The second “ensures your own collateral is always fully covered.” At settlement, payout is the minimum of profit plus collateral, and that locked amount. Max profit, alone, is the first term. Past the max-profit price, “your position stops earning more profit even if the market keeps moving in your favor.” A take-profit order “cannot be placed past the max profit price.” The panel, again, is said to show the live price. The panel was not opened.',
  'The short is the case the page uses to show a cap that is hard to hit. “For shorts with a 100% max payoff, the max profit price effectively reaches $0 — the asset would need to go to zero for the cap to bind.” The formula above that sentence is entry price minus max profit over size. A payoff equal to the whole size, subtracted from the entry, lands on zero. The page calls that “effectively.” It does not show a worked short with fees taken out, so this reading does not invent a fee-adjusted zero. The contrast is the major. “Major crypto markets — BTC, ETH, SOL — cap profit at 25% of position size,” and “a 100x BTC long hits its max profit on a 0.25% favorable move.” Most alt, meme, and synthetic markets “cap at 50–100%.” A few “run higher on one side.” The short that needs a collapse to zero and the long that is finished after a quarter of a percent are the same formula with different payoff parameters. The culture talks about the multiple. The page talks about a lock that, at 100x on a major, is spent almost immediately in the trader’s favour, and that, on a fully capped short, is barely reachable.',
  'The reason the page gives is the pool’s collateral, not the trader’s ambition. “The cap is most relevant for synthetic markets — forex, commodities, and tokenized equities — where the pool is backed by USDC rather than the native asset, protecting the pool from outsized payouts.” A synthetic short or long is a claim on a USDC pool, and the lock is how large a claim the pool will pre-commit. The dates match the other snapshots: “as of 2026-07-03; tunable.” A 100 percent figure in that sentence is a parameter as of that day, on the markets the page calls “most” alts, memes, and synthetics, not a promise that every short is a bet the asset goes to zero. The zero is the arithmetic of a 100 percent payoff. Markets with a lower payoff bind sooner, and the page says some bind on one side only. Which side, and which market, is the panel’s. This reading stops at the formula and at the sentence that a short’s full cap is a price of zero.',
 ],
 says=[
  'The pool locks collateral plus a max profit equal to size times the payoff parameter. Settlement cannot pay more than the lock.',
  'A short with a 100 percent max payoff has a max-profit price that effectively reaches zero.',
  'Majors cap profit at 25 percent of size, so a 100x BTC long binds after a 0.25 percent favorable move. The page says a take-profit cannot be placed beyond the cap.',
  'The cap is described as protection for pools that are backed by USDC on synthetic markets.',
 ],
 paid=[
  'The trader’s profit is capped by what the pool locked at the open.',
  'The pool, on the page’s account, is the party protected from an outsized payout.',
 ],
 decides=[
  'The payoff parameter is a per-market setting, dated 2026-07-03 and described as tunable.',
  'The trader does not get to place a take-profit past the price the lock implies.',
 ],
 limits=[
  'No short was opened. Zero is the page’s description of the 100 percent case, not a forecast.',
  'The live max-profit price is attributed to a panel that was not opened.',
 ],
 sources=[dict(label='Flash max profit', url='https://docs.flash.trade/flash-trade/flash-trade-protocol/perpetuals-specifications/max-profit.md', note='HTTP 200 on 17 Nov 2026.')],
 related=['a-hundred-times-leverage-dies-on-a-quarter-of-a-percent', 'the-forex-line-is-the-wilder-number'],
)

R(
 title='The Cheap Deposit Is Not the Swap in the Menu',
 desk='money', desk_name='Money and markets', feature='Who Gets Paid?',
 desc='Flash says an underweight deposit draws a cheaper conversion fee, and that this swap is not the Jupiter route. No deposit was made.',
 deck='Two things on one fee page are both called a swap. One prices the act of posting collateral. The other is a different page in the app. USDC, meanwhile, is free to add and not free to remove.',
 question='Who does the fee page say is paid when collateral is converted, and which swap does it say that fee is not?',
 paragraphs=[
  'The page lists three costs of a trade and then a fourth that happens before the trade looks like a trade. Open and close fees are “a flat percentage of position size.” The spread is “applied on entry and exit,” so “a take-profit target needs to clear roughly two spreads before the position is net positive.” Margin fees accrue from pool utilization, linear below 72 percent, stepped up above it, with “a 90 percent utilization cap.” Then the collateral swap. “When your deposit is converted into a position’s backing asset, a pool swap fee applies, calculated from pool balance ratios — depositing an underweight asset is cheaper.” The formula is printed as symbols: a slope from a target fee and a minimum fee across a target ratio and a minimum ratio, and an intercept. The page does not print the target fee, the minimum fee, or the ratios. A reader can see the shape. A reader cannot compute a rate. This reading does not supply the missing numbers.',
  'The next sentence is the one that keeps two products apart. “This pool-level conversion is different from the Swap page in the app, which routes spot swaps through Jupiter.” A person who taps Swap is, on this page, in a different fee. A person who deposits the “wrong” asset relative to what the pool wants is in this fee, and is told that being on the light side of the pool is the cheaper side. Who receives the fee is not named in the paragraph. The fee-distribution page, a different document, splits trading fees between liquidity providers and the rest of a table by pool, with meme pools keeping a larger LP share. It does not, in the lines used here, say the collateral-conversion fee takes that same split. The paper will not paste the distribution table onto a fee the distribution page did not name.',
  'USDC has its own row, and the row is asymmetric. Adding or minting liquidity is 0 basis points. Removing or burning it is 15. Entry is free on that row. Exit is not. Combined with a utilization fee that rises as the pool fills, and a spread charged twice, the page is a stack of small tolls around a leverage slider that will get all of the attention. The order panel “is always the authority for your specific order,” and the snapshot is dated 2026-07-03. The asymmetry does not need the panel to be stated. Zero to get USDC in, 15 basis points to take it out, is on the page. Whether a particular deposit was underweight on a particular afternoon is not. No deposit was made.',
 ],
 says=[
  'A collateral conversion fee depends on pool balance ratios, and the page says depositing an underweight asset is cheaper. The formula’s target rates are not printed.',
  'That conversion is described as different from the app’s Swap page, which routes through Jupiter.',
  'USDC liquidity is 0 basis points to add and 15 basis points to remove. Utilization fees scale linearly below 72 percent, step up above it, and face a 90 percent cap. Spread is charged on the open and again on the close.',
 ],
 paid=[
  'The page does not name the recipient of the collateral-conversion fee.',
  'A trader pays spread twice, and pays 15 basis points to remove USDC liquidity. Adding it is listed at zero.',
 ],
 decides=[
  'Pool ratios decide which deposit is the cheap one. The page does not let the reader see the ratios without the panel.',
  'The distinction between the conversion and the Jupiter swap is the page’s. It is not a test of either route.',
 ],
 limits=[
  'No deposit was made and no ratio was read. The symbolic formula is not filled in.',
  'The fee-distribution split is not applied to a fee that page does not mention.',
 ],
 sources=[
  dict(label='Flash fees', url='https://docs.flash.trade/flash-trade/flash-trade-protocol/perpetuals-specifications/fees.md', note='HTTP 200 on 17 Nov 2026.'),
  dict(label='Flash fee distribution', url='https://docs.flash.trade/flash-trade/flash-trade-protocol/technical-architecture/fee-distribution.md', note='HTTP 200 on 17 Nov 2026. Cited to avoid borrowing its split for a fee it does not name.'),
 ],
 related=['meme-markets-pay-a-different-open-fee', 'the-page-that-says-the-oracle-removes-the-spread-and-the-page-that-charges-it-twice'],
)
