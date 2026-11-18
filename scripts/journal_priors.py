"""Documentary priors for Journal protocols and sketches.

Each entry cites library paper slugs already retrieved on 17 Nov 2026.
A prior is a document pointer, not a finding, not a re-run, and not peer review.
"""
from __future__ import annotations

# protocol/sketch slug -> list of (paper_slug, how_to_cite)
PRIORS = {
 'submitted-is-not-settled': [
  ('solana-commitment-status', 'Defines commitment labels as the file’s process language. Not a client-state study.'),
  ('optimistic-confirmation', 'A design note on confirmation signalling. Not an application classification result.'),
  ('optimistic-confirmation-and-slashing', 'Pairs confirmation language with slashing design text. Not a harness log.'),
  ('transaction-receipts', 'Names receipt-shaped records. Not a comparison of UI labels to cluster responses.'),
  ('durable-transaction-nonces', 'Durable nonce design text. Not a measured expiry recovery.'),
  ('block-confirmation', 'Block confirmation wording in a design note. Not an observed confirmation column.'),
  ('handle-duplicate-block', 'Duplicate-block handling design. Not a stored application label.'),
  ('optimistic-transaction-propagation-signal', 'Propagation signal design. Not a settlement classification.'),
 ],
 'retry-without-double-execution': [
  ('durable-transaction-nonces', 'Nonce reuse and identity language in the file. Not a double-fulfilment score.'),
  ('relax-invalid-nonced-transactions-constraint', 'Constraint change proposal. Not a fault-injection result.'),
  ('prohibit-nonce-account-self-withdrawals', 'A safety constraint proposal. Not a merchant retry study.'),
  ('optimistic-transaction-propagation-signal', 'Propagation signalling design. Not an idempotency test.'),
  ('transaction-receipts', 'Receipt wording that a recovery design might cite. Not a fulfilment invariant check.'),
 ],
 'who-can-move-the-funds': [
  ('vote-account-v5', 'Vote account authority fields as stored in the file. Not a fixture review.'),
  ('secure-vote-signing', 'Signing design text. Not a detection-rate result.'),
  ('loader-v3-reclaim-closed-program', 'Loader/program reclaim design. Not an authority-graph evaluation.'),
  ('core-bpf-upgrade-procedure', 'Upgrade procedure wording. Not a human-review experiment.'),
  ('hash-validation-in-program-upgrades', 'Upgrade hash-check proposal. Not a false-positive study.'),
  ('prohibit-vote-account-self-withdrawals', 'Self-withdrawal prohibition design. Not a reviewed fixture.'),
  ('bls-pubkey-management-in-vote-account', 'BLS pubkey management design. Not an authority-graph score.'),
 ],
 'sponsorship-without-arbitrary-signing': [
  ('deterministic-transaction-fees', 'Fee determinism design language. Not a sponsor policy corpus.'),
  ('comprehensive-compute-fees', 'Compute fee design text. Not a merchant policy test.'),
  ('fee-transaction-priority', 'Priority fee proposal wording. Not a residual-risk inventory.'),
  ('base-inclusion-and-resource-based-fee', 'Inclusion and fee resource design. Not a signed-byte audit.'),
  ('relax-fee-payer-constraint', 'Fee-payer constraint proposal. Not a built sponsor.'),
 ],
 'one-token-api': [
  ('p-token-efficient-token-program', 'Token program design note. Not a compatibility matrix cell.'),
  ('p-ata-cu-optimized-ata-program', 'ATA program design. Not an account-creation fixture.'),
  ('token-bridge', 'Wormhole token-bridge design reading. Not a transfer matrix row.'),
  ('transfer-verifier', 'Transfer verification design. Not observed error handling.'),
  ('solana-zk-token-proof-program', 'ZK token proof program design. Not an unsupported-cell claim.'),
 ],
 'can-learners-explain': [
  ('solana-a-new-architecture-for-a-high-performance-blockchain', 'Architecture white paper as a teaching source document. Not a learner study.'),
  ('instruction-introspection', 'Instruction introspection design. Not a comprehension score.'),
  ('transaction-receipts', 'Receipt-shaped records a lesson might ask a learner to read. Not an assessment result.'),
 ],
 'finality-under-named-rules': [
  ('solana-a-new-architecture-for-a-high-performance-blockchain', 'Proof of History and Tower wording in the white paper. Not a finality measurement.'),
  ('solana-alpenglow-consensus-v1-2', 'Alpenglow consensus PDF reading. Not a cluster observation.'),
  ('solana-alpenglow-consensus-v1-1', 'Earlier Alpenglow version on the shelf. Version discipline only.'),
  ('solana-alpenglow-consensus-v1', 'First Alpenglow shelf version. Not “the live network”.'),
  ('simd-0326-alpenglow', 'SIMD-0326 companion proposal. Status label is the file’s, not a journal review.'),
  ('tower-bft', 'Tower BFT design note. Not a vote-log study.'),
  ('alpenglow-migration', 'Migration design text. Not an activation reading from a cluster.'),
  ('markers-for-alpenglow-fast-leader-handover', 'Leader-handover markers proposal. Not a timed handover.'),
  ('optimistic-confirmation-and-slashing', 'Optimistic confirmation design. Not a slash event.'),
  ('alpenglow-validator-admission-ticket', 'Admission-ticket design text. Not a validator-set census.'),
  ('reliable-vote-transmission', 'Vote transmission design. Not a measured vote arrival.'),
  ('synchronization', 'Cluster synchronization design note. Not a fork observation.'),
  ('validate-chained-block-id', 'Chained block id validation proposal. Not a stored fork choice.'),
 ],
 'fee-and-rent-observation': [
  ('storage-rent-economics', 'Rent economics design. Not a remeasured rent schedule.'),
  ('economic-sustainability', 'Economic sustainability note. Not a scored payment workflow.'),
  ('cluster-economics', 'Cluster economics design. Not a balance-change table.'),
  ('staking-rewards', 'Staking rewards design. Not a payment-cost study.'),
  ('comprehensive-compute-fees', 'Compute fees design. Not an omitted-cost inventory.'),
  ('deterministic-transaction-fees', 'Deterministic fees design. Not a displayed-fee comparison.'),
  ('fee-transaction-priority', 'Priority fee proposal. Not a workflow cost walk.'),
  ('base-inclusion-and-resource-based-fee', 'Resource-based fee design. Not a product UI audit.'),
 ],
 'upgrade-bytes-and-disclosure': [
  ('core-bpf-upgrade-procedure', 'Upgrade procedure document. Not a user-facing disclosure score.'),
  ('hash-validation-in-program-upgrades', 'Hash validation proposal. Not an inspected deployment.'),
  ('enable-core-bpf-programs', 'Core BPF enablement proposal. Not an authority read.'),
  ('loader-v3-set-program-data-to-elf-length', 'Loader program-data length proposal. Not a public-statement audit.'),
  ('loader-v3-reclaim-closed-program', 'Closed-program reclaim design. Not a disclosure pair.'),
 ],
 # Sketches
 'rpc-observation-under-failure': [
  ('solana-commitment-status', 'Commitment labels a client might mis-map after a timeout. Not a provider-failure study.'),
  ('transaction-receipts', 'Receipt wording. Not a stored timeout classification.'),
 ],
 'shared-writable-state': [
  ('solana-a-new-architecture-for-a-high-performance-blockchain', 'Parallelism and account wording in the white paper. Not a contention workload.'),
  ('loaded-transaction-data-size-specification', 'Loaded data size specification. Not an overlap log.'),
 ],
 'the-cost-of-a-payment': [
  ('storage-rent-economics', 'Rent economics design. Cite beside the fee-and-rent protocol for the full workflow walk.'),
  ('comprehensive-compute-fees', 'Compute fee design. Not a displayed-fee audit.'),
  ('deterministic-transaction-fees', 'Deterministic fee language. Not a balance-change set.'),
 ],
 'reproducible-solana-builds': [
  ('core-bpf-upgrade-procedure', 'Upgrade procedure that assumes identifiable bytes. Not a second-party rebuild.'),
  ('hash-validation-in-program-upgrades', 'Hash validation proposal. Not a reproduction log.'),
 ],
 'indexer-recovery': [
  ('ledger-replication', 'Ledger replication design. Not a gap-fill measurement.'),
  ('synchronization', 'Synchronization design note. Not an ingest recovery table.'),
 ],
 'stale-frontend-state': [
  ('solana-commitment-status', 'Commitment labels a UI might cache. Not a frontend timing study.'),
  ('optimistic-confirmation', 'Optimistic confirmation wording. Not a displayed-label pair.'),
 ],
 'upgrade-authority': [
  ('core-bpf-upgrade-procedure', 'Upgrade procedure document. Prefer the upgrade-bytes protocol for a full study design.'),
  ('hash-validation-in-program-upgrades', 'Hash validation proposal. Not a disclosure score.'),
 ],
 'generated-patches': [
  ('hash-validation-in-program-upgrades', 'Hash-check design a patch review might cite. Not a model-patch trial.'),
  ('secure-vote-signing', 'Signing design text as an example of a check that must not be deleted. Not an AI evaluation.'),
 ],
 'benchmarking-benchmarks': [
  ('solana-a-new-architecture-for-a-high-performance-blockchain', 'White-paper performance figures as document claims only. Not a scored benchmark corpus.'),
  ('solayer-chain-infinitely-scalable-hardware-accelerated-svm-network', 'Hardware-accelerated SVM design reading. Not a workload measurement.'),
 ],
 'evidence-quality': [
  ('slashable-event-verification', 'Slashable event verification design. Not a scored security write-up.'),
  ('slashing-rules', 'Slashing rules design. Not a suspected/reproduced/fixed/deployed score.'),
  ('optimistic-confirmation-and-slashing', 'Confirmation-and-slashing proposal. Process language only.'),
 ],
 'wallet-preview': [
  ('instruction-introspection', 'Introspection design a preview might surface. Not a comprehension trial.'),
  ('transfer-verifier', 'Transfer verification design. Not a wallet UI study.'),
 ],
 'application-retirement': [
  ('core-bpf-upgrade-procedure', 'Upgrade procedure that can outlive an operator’s marketing. Not a retirement audit.'),
  ('loader-v3-reclaim-closed-program', 'Closed-program reclaim design. Not a remaining-duty inventory.'),
 ],
 'vote-credits-and-schedule': [
  ('timely-vote-credits', 'Timely vote credits design. Not a before/after credit table.'),
  ('timely-vote-credits-2', 'Later timely-vote-credits shelf entry. Version discipline only.'),
  ('vote-account-address-keyed-leader-schedule', 'Address-keyed leader schedule proposal. Not a schedule observation.'),
  ('vote-account-v4', 'Vote account v4 design. Not a cluster field read.'),
  ('vote-account-v5', 'Vote account v5 design. Not an epoch credit measurement.'),
  ('syscall-get-epoch-stake', 'Epoch stake syscall design. Not a stake census.'),
  ('stop-special-casing-of-vote-cu-cost', 'Vote CU cost proposal. Not a CU observation.'),
  ('deprecate-legacy-vote-instructions', 'Legacy vote deprecation design. Not an instruction-mix measurement.'),
 ],
 'slashable-evidence-records': [
  ('slashable-event-verification', 'Slashable event verification design. Not a verified evidence object.'),
  ('slashing-rules', 'Slashing rules design note. Not an acted-on stake change.'),
  ('optimistic-confirmation-and-slashing', 'Confirmation-and-slashing proposal. Keeps states separate only as wording.'),
  ('secure-vote-signing', 'Secure vote signing design. Not a slash reproduction.'),
  ('secure-vote-signing-2', 'Later secure-vote-signing shelf entry. Not a verification log.'),
 ],
 'commitment-across-providers': [
  ('solana-commitment-status', 'Commitment status design language. Not a multi-provider poll.'),
  ('optimistic-confirmation', 'Optimistic confirmation design. Not a provider disagreement table.'),
  ('block-confirmation', 'Block confirmation wording. Not a polling-rule result.'),
  ('optimistic-transaction-propagation-signal', 'Propagation signal design. Not an RPC comparison.'),
 ],
 'tower-alpenglow-document-delta': [
  ('tower-bft', 'Tower BFT design note as one side of a documentary delta. Not a migration.'),
  ('solana-alpenglow-consensus-v1-2', 'Latest Alpenglow shelf PDF in this catalogue. Not activation.'),
  ('solana-alpenglow-consensus-v1-1', 'Intermediate Alpenglow version. Keep pinned separately.'),
  ('solana-alpenglow-consensus-v1', 'First Alpenglow shelf version. Keep pinned separately.'),
  ('simd-0326-alpenglow', 'SIMD-0326 companion. Status is the file’s label.'),
  ('alpenglow-migration', 'Migration design text. Documentary only until a cluster arm exists.'),
  ('solana-a-new-architecture-for-a-high-performance-blockchain', 'White-paper PoH/Tower wording as the older document set.'),
 ],
 'rent-exemption-paths': [
  ('storage-rent-economics', 'Rent economics design. Not a product path walk.'),
  ('cluster-economics', 'Cluster economics design. Not an unnamed-transfer inventory.'),
  ('economic-sustainability', 'Economic sustainability note. Not a UI fee sentence audit.'),
  ('p-ata-cu-optimized-ata-program', 'ATA program design that account-creation paths may touch. Not a rent observation.'),
 ],
 'stake-delegation-disclosure': [
  ('stake-delegation-and-rewards', 'Stake delegation and rewards design. Not a UI disclosure pair.'),
  ('staking-rewards', 'Staking rewards design. Not a vote-account field read.'),
  ('vote-account-v5', 'Vote account fields a disclosure study would have to name. Not a pool UI audit.'),
  ('vote-account-initialize-v2', 'Vote account initialize design. Not a delegator comprehension study.'),
  ('deactivatedelinquent-for-closed-vote-accounts', 'Closed vote-account delinquency design. Not a disclosure score.'),
  ('block-revenue-sharing', 'Block revenue sharing design. Not a stake-account statement check.'),
 ],
}


def priors_for(slug):
  return list(PRIORS.get(slug) or [])


def priors_html(E, slug):
  """HTML block listing documentary priors. Safe when a slug is missing from the library."""
  import library_papers as papers
  by = {r['slug']: r for r in papers.papers()}
  rows = priors_for(slug)
  if not rows:
    return (
      '<h2>Documentary priors from the library</h2>'
      '<p>No retrieved shelf document is wired to this page yet as a prior. '
      'A later edit may add catalogue pointers. Absence of a list is not a survey.</p>'
    )
  lis = []
  for paper_slug, note in rows:
    if paper_slug is None or note is None:
      continue
    row = by.get(paper_slug)
    if not row:
      continue
    title = row['title']
    href = '/library/papers/' + paper_slug + '/'
    lis.append(
      f'<li><a href="{E(href)}">{E(title)}</a> — {E(note)} '
      f'Catalogue id <code>{E(row["id"])}</code>. Appraisal: '
      f'<a href="/journal/notes/{E(paper_slug)}/">source appraisal</a>.</li>'
    )
  if not lis:
    return (
      '<h2>Documentary priors from the library</h2>'
      '<p>Priors were configured, but no matching catalogue row was found. '
      'That is a wiring error to fix, not a finding.</p>'
    )
  return (
    '<h2>Documentary priors from the library</h2>'
    '<p>These are retrieved documents on the Solana Library shelf. '
    'Each line is a citation filter for a later study, not a result of this protocol. '
    'No file was re-read line by line for this block beyond the catalogue fields already stored. '
    'No observation was collected.</p>'
    f'<ul>{"".join(lis)}</ul>'
  )
