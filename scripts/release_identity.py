"""Public release identity for Sol.College (app vs curriculum, no secrets).

Writes non-sensitive artifacts a reviewer can use to identify what they are
inspecting: /release.json, /curriculum.json, /releases/, and footer markup.
"""
from __future__ import annotations

import hashlib
import html
import json
import os
import subprocess
from datetime import datetime, timezone
from pathlib import Path

E = lambda s: html.escape(str(s), quote=True)

# User-visible release notes for this product line. Append a new entry when
# shipping learner-facing changes. Do not put secrets or infrastructure here.
RELEASE_NOTES = [
  {
    'id': '2026-11-19-release-c22',
    'title': 'Release C.22 — Debug laboratory track honesty',
    'summary': (
      'Ten partial-functional labs are retagged track=debug-laboratory so the catalogue '
      'does not present known-gap lessons as ordinary electives. Recommended curriculum '
      'fields are complete for live guided lessons.'
    ),
    'changes': [
      'Retag partial labs (Barn, UniProof, Friendstake, CS2 market, Web3 Splitter, PulseFund, stakes.wtf, Votara, DeVos, Agenc) as debug-laboratory.',
      'Checklist: recommended schema fields marked done (0 missing_recommended).',
      'Tests assert every non-full functional live lab uses debug-laboratory track.',
    ],
  },
  {
    'id': '2026-11-19-release-c21',
    'title': 'Release C.21 — Final catalogue learning loops (guided live complete)',
    'summary': (
      'PulseFund, stakes.wtf, Votara, and DeVos join the shared learning layer. '
      'Every guided live lesson JSON now has a learning_loop.'
    ),
    'changes': [
      'pulsefund-sol / stakes-main / votara / devos-decentralized-voting: track=elective, loops, rubrics.',
      'Loops cover wrong Contribute PDA, stale gov price, quorum-before-percentage, and missing finished election state.',
      'Test gate: all guided live lessons expose learning_loop.',
    ],
  },
  {
    'id': '2026-11-19-release-c20',
    'title': 'Release C.20 — Catalogue debug electives batch 5',
    'summary': (
      'Barn, UniProof, Friendstake, CS2 Prediction Market, and Web3 Splitter join the '
      'shared learning layer with diagnosis-focused loops (reject→accept bug, unconstrained '
      'sign, wrong payee, missing claim, claim seeds mismatch).'
    ),
    'changes': [
      'Five formerly untracked catalogue lessons gain track=elective, learning_loop, and rubrics.',
      'Loops emphasise diagnosing recorded bugs without claiming unproven production fixes.',
      'Remaining unwired guided catalogue: pulsefund, stakes-main, votara, devos.',
    ],
  },
  {
    'id': '2026-11-19-release-c19',
    'title': 'Release C.19 — Elective learning loops batch 4 (track=elective complete)',
    'summary': (
      'Final track=elective catalogue lessons join the shared learning layer: Atlantid, '
      'Covenant, Otomat, SolAgents Commerce, TrustRail Pipelines, and Veedor.'
    ),
    'changes': [
      'Six electives gain learning_loop + lab-specific criteria (owner vs cap, init co-signer, Ed25519, job PDA vault, staging delegation, MissingEd25519).',
      'All lessons with track=elective now have learning_loop and assessment criteria.',
      'Remaining unwired catalogue items are untracked/preview-style lessons outside track=elective.',
    ],
  },
  {
    'id': '2026-11-19-release-c18',
    'title': 'Release C.18 — Elective learning loops batch 3',
    'summary': (
      'Catalogue electives AgentEscrow, Pact Escrow, Lattice Escrow, EscrowAgent, '
      'Agent Court, and Allowance join the shared learning layer.'
    ),
    'changes': [
      'Six escrow/allowance electives gain learning_loop + lab-specific assessment criteria.',
      'Loops emphasise vault PDA bumps, authority-gated release, OracleCallback rejection, claim status, and OverRequestCap.',
      'Tests cover batch 3 predict answers and no Picassol leakage.',
    ],
  },
  {
    'id': '2026-11-19-release-c17',
    'title': 'Release C.17 — Elective learning loops batch 2',
    'summary': (
      'Apply-path electives Hydra, Agent Bazaar, AgentVault, Orrery, and Reddi Escrow '
      'join the shared learning layer with scoped loops and lab-specific rubrics.'
    ),
    'changes': [
      'hydra / agent-bazaar / agentvault / orrery / reddi-escrow: track=elective, learning_loop, assessment criteria.',
      'AgentVault loop emphasises explaining rejected complete_task rather than inventing payouts.',
      'Tests cover batch 2 predict answers and no Picassol leakage.',
    ],
  },
  {
    'id': '2026-11-19-release-c16',
    'title': 'Release C.16 — Elective learning loops batch 1',
    'summary': (
      'First five apply-path electives join the shared learning layer: Guild Protocol, '
      'QVAC Marketplace, AgentTrust, Agenc Protocol, and Forge Agent Bounty.'
    ),
    'changes': [
      'Each elective gains track=elective, student_outcome, learning_loop, and lab-specific assessment criteria.',
      'Workspace/preflight/assessment pages generate from the shared learning_layer.',
      'Tests assert predict answers and no Picassol criterion leakage.',
    ],
  },
  {
    'id': '2026-11-18-release-d3',
    'title': 'Release D.3 — Foundations → Stage 1 handoff + structural verification',
    'summary': (
      'Foundations 007 hands off to Picassol as Stage 1. Catalog records automated '
      'structural technical checks while learner testing remains open. Picassol prereqs '
      'recommend Foundations 001–007 for newcomers.'
    ),
    'changes': [
      'Lesson 007 next-step copy: Foundations sequence ends; Picassol is Stage 1 (future PDA lesson does not block).',
      'Catalog next_id / stage1_handoff / technical_checks; STATUS_ROWS technical line updated across 001–007.',
      'Picassol prereqs recommend Foundations 001–007; automated handoff tests added.',
    ],
  },
  {
    'id': '2026-11-18-release-d2',
    'title': 'Release D.2 — Foundations 001–007 shared learning loops',
    'summary': (
      'Every Foundations lesson now has a catalog learning_loop and the shared '
      'Predict→Act→Inspect workspace. Verification status remains release_candidate.'
    ),
    'changes': [
      'Catalog learning_loop entries for Lessons 002–007 (001 already present).',
      'Inject shared foundations workspace into all seven Foundations lesson pages.',
      'Rename Lesson 003 product-requirement section id to avoid colliding with #workspace.',
    ],
  },
  {
    'id': '2026-11-18-release-d1',
    'title': 'Release D.1 — Foundations in curriculum source of truth',
    'summary': (
      'Foundations Lessons 001–007 are registered in dapps/foundations/catalog.json '
      'and emitted on /curriculum.json. Lesson 001 gains the shared learning-loop workspace; '
      'all seven remain honest release candidates until verification completes.'
    ),
    'changes': [
      'Canonical foundations catalog with outcomes, prereqs, verification_status, and 001 learning_loop.',
      'curriculum_schema audit includes foundations track; curriculum.json lists them separately from live apps.',
      'Lesson 001 page injects Predict→Act→Inspect workspace from the catalog loop.',
    ],
  },
  {
    'id': '2026-11-18-release-c15',
    'title': 'Release C.15 — OrbOracle learning loop (path complete)',
    'summary': (
      'Stage 3 OrbOracle joins the shared learning layer. All staged path labs '
      '(1–16) now share preflight → Predict→Act→Inspect → assessment.'
    ),
    'changes': [
      'orboracle-solana gains learning_loop, lab-specific criteria, and path-aligned prereqs.',
      'Release C path migration for reusable learning components is complete; electives remain open.',
    ],
  },
  {
    'id': '2026-11-18-release-c14',
    'title': 'Release C.14 — Novengrid/colosseum learning loop',
    'summary': (
      'Stage 3 Novengrid SOL staking joins the shared learning layer with '
      'early-unstake refusal and per-second reward criteria.'
    ),
    'changes': [
      'colosseum gains learning_loop, lab-specific criteria, and path-aligned prereqs.',
      'Assessment requires honesty about 7-day UI lock vs script-verified unlock.',
    ],
  },
  {
    'id': '2026-11-18-release-c13',
    'title': 'Release C.13 — sentient.send Stage 3 learning loop',
    'summary': (
      'Stage 3 opens with sentient.send on the shared learning layer: '
      'winner-takes-all payout reasoning and 32-byte seed-limit criteria.'
    ),
    'changes': [
      'sentient-send gains learning_loop, lab-specific criteria, and path-aligned prereqs from Stage 2.',
      'Release C continues into Stage 3 after completing Stage 1–2 path labs.',
    ],
  },
  {
    'id': '2026-11-18-release-c12',
    'title': 'Release C.12 — NAIM learning loop (Stage 2 complete)',
    'summary': (
      'Stage 2 NAIM joins the shared learning layer. All Stage 2 path labs now '
      'share preflight → Predict→Act→Inspect → assessment.'
    ),
    'changes': [
      'naim gains learning_loop, lab-specific criteria, and path-aligned prereqs.',
      'Stage 2 path coverage for reusable learning components is complete.',
    ],
  },
  {
    'id': '2026-11-18-release-c11',
    'title': 'Release C.11 — AgentX learning loop',
    'summary': (
      'Stage 2 AgentX joins the shared learning layer with Active-status and '
      'oracle=authority criteria, keeping claim_reward out of required mastery.'
    ),
    'changes': [
      'agentx gains learning_loop, lab-specific criteria, and path-aligned prereqs.',
      'Assessment notes initialize_registry is a lab patch and claim_reward was unverified.',
    ],
  },
  {
    'id': '2026-11-18-release-c10',
    'title': 'Release C.10 — Oculus learning loop',
    'summary': (
      'Stage 2 Oculus joins the shared learning layer with pause/LimitBreached '
      'criteria and honesty that check_spend does not transfer tokens.'
    ),
    'changes': [
      'oculus gains learning_loop, lab-specific criteria, and path-aligned prereqs.',
      'Assessment requires honesty about window-reset and non-transferring check_spend.',
    ],
  },
  {
    'id': '2026-11-18-release-c9',
    'title': 'Release C.9 — ZeroAI learning loop',
    'summary': (
      'Stage 2 ZeroAI joins the shared learning layer with stale-Pyth zero-snapshot '
      'criteria so successful addgame is not mistaken for live oracle prices.'
    ),
    'changes': [
      'zeroai gains learning_loop, lab-specific criteria, and path-aligned prereqs.',
      'Assessment requires honesty about closegame and stale Devnet Pyth feeds.',
    ],
  },
  {
    'id': '2026-11-18-release-c8',
    'title': 'Release C.8 — Trust Protocol learning loop',
    'summary': (
      'Stage 2 Trust Protocol joins the shared learning layer with second-initialize '
      'and bond-vault-v2 criteria, keeping unverified dispute/insurance out of mastery claims.'
    ),
    'changes': [
      'trust-protocol gains learning_loop, lab-specific criteria, and path-aligned prereqs.',
      'Assessment requires honesty about contract/dispute/insurance not being on the verified path.',
    ],
  },
  {
    'id': '2026-11-18-release-c7',
    'title': 'Release C.7 — MandateKey learning loop',
    'summary': (
      'Stage 2 MandateKey joins the shared learning layer with create/revoke '
      'practice and honest coverage that pay was not hosted-verified.'
    ),
    'changes': [
      'mandatekey gains learning_loop, lab-specific criteria, and path-aligned prereqs.',
      'Assessment requires honesty about pay/vault prerequisites and unimplemented owner ixs.',
    ],
  },
  {
    'id': '2026-11-18-release-c6',
    'title': 'Release C.6 — CipherVault Stage 2 learning loop',
    'summary': (
      'Stage 2 opens with CipherVault on the shared learning layer: threshold '
      'multisig flow plus honest missing-constraint assessment criteria.'
    ),
    'changes': [
      'ciphervault gains learning_loop, lab-specific criteria, and path-aligned prereqs from Stage 1.',
      'Release C continues into Stage 2 after completing all six Stage 1 labs.',
    ],
  },
  {
    'id': '2026-11-18-release-c5',
    'title': 'Release C.5 — Gifter escrow learning loop (Stage 1 complete)',
    'summary': (
      'Stage 1 Gifter escrow joins the shared learning layer. All six Stage 1 '
      'path labs now share preflight → Predict→Act→Inspect → assessment.'
    ),
    'changes': [
      'gifter-escrow gains learning_loop, lab-specific criteria, and curriculum metadata.',
      'Stage 1 path coverage for reusable learning components is complete.',
    ],
  },
  {
    'id': '2026-11-18-release-c4',
    'title': 'Release C.4 — TrustLock learning loop',
    'summary': (
      'Stage 1 TrustLock joins the shared learning layer with Clock-deadline '
      'guards, claim/cancel criteria, and curriculum metadata.'
    ),
    'changes': [
      'trustlock gains learning_loop, lab-specific assessment criteria, and path-aligned prereqs.',
      'Five Stage 1 path labs now share reusable preflight → loop → assessment components.',
    ],
  },
  {
    'id': '2026-11-18-release-c3',
    'title': 'Release C.3 — gree NFT lab learning loop',
    'summary': (
      'Stage 1 lesson gree joins the shared preflight → Predict→Act→Inspect → '
      'assessment stack with Metaplex-specific criteria.'
    ),
    'changes': [
      'gree gains learning_loop, lab-specific assessment criteria, and curriculum metadata.',
      'Four Stage 1 path labs now share the reusable learning-layer components.',
    ],
  },
  {
    'id': '2026-11-18-release-c2',
    'title': 'Release C.2 — Proof of Estimate loop + lab-specific rubrics',
    'summary': (
      'Stage 1 lesson Proof of Estimate joins the shared learning loop. Assessment '
      'criteria are lab-specific so NameGen and POE no longer inherit Picassol wording.'
    ),
    'changes': [
      'poe-solana gains learning_loop, assessment criteria, and lab metadata.',
      'Picassol and NameGen store explicit criteria; assessment HTML fallback is generic.',
    ],
  },
  {
    'id': '2026-11-18-release-c',
    'title': 'Release C — second application lab learning loop (NameGen)',
    'summary': (
      'Stage 1 lesson NameGen now uses the same preflight → Predict→Act→Inspect → '
      'assessment → attempt-recovery components as Picassol.'
    ),
    'changes': [
      'c4-comets-todor-edward-andrei gains learning_loop, assessment rubric page, and lab metadata.',
      'Proves the learning-layer components reuse beyond Picassol without a shell redesign.',
    ],
  },
  {
    'id': '2026-11-18-release-a3',
    'title': 'Release A.3 — curriculum required-field backfill',
    'summary': (
      'All live guided lessons now carry objectives and prerequisites; the twelve former '
      'schema gaps also get student_outcome, content_version, and elective track labels.'
    ),
    'changes': [
      'curriculum_schema reports missing_required_lessons = 0 for the live inventory.',
      'Escrow/agent electives (AgentEscrow, Veedor, Otomat, Agent Court, and peers) have decision-ready outcomes.',
    ],
  },
  {
    'id': '2026-11-18-release-b2',
    'title': 'Release B.2 — pending-attempt recovery',
    'summary': (
      'Attempt recovery panel separates wallet rejection, unknown submission, pending, '
      'failure, and success — and tells learners not to blind-resubmit.'
    ),
    'changes': [
      'Stuck → transaction flow opens Attempt recovery with status-specific next steps.',
      'Attempt state persists in local lesson loop storage and surfaces in the evidence drawer.',
      'Explorer deep-link uses a recorded signature when present.',
    ],
  },
  {
    'id': '2026-11-18-release-b',
    'title': 'Release B — Picassol assessment and safer resume',
    'summary': (
      'Independent Picassol assessment rubric, content-version resume safety, '
      'restored prediction lock UI, and clearer evidence provenance tags.'
    ),
    'changes': [
      'Picassol ships /lessons/picassol-hackathon/assessment/ with criteria and honesty gates.',
      'Workspace stores content_version and warns when lesson content changes.',
      'Evidence drawer tags attempt route; optional public signature field; stale observation note on resume.',
    ],
  },
  {
    'id': '2026-11-18-release-a2',
    'title': 'Release A.2 — schema audit, update notice, Picassol honesty',
    'summary': (
      'Curriculum schema status on /curriculum.json, stale-tab reload notice from '
      '/release.json, and clearer Picassol hosted-UI vs script verification labels.'
    ),
    'changes': [
      'Curriculum export includes schema_status and missing-field lists per lesson.',
      'Open tabs that see a new app or curriculum version get a reload banner.',
      'Picassol states hosted create is verified; recolour remains observation/script until hosted UI is recorded.',
    ],
  },
  {
    'id': '2026-11-18-release-a',
    'title': 'Release A — correctness and clarity',
    'summary': (
      'Public release identity (app vs curriculum), curriculum summary endpoint, '
      'honest environment-status labels, and mobile horizontal-scroll containment.'
    ),
    'changes': [
      'Footer and /release.json expose app release, curriculum version, and build time.',
      'Homepage and catalogue counts continue to come from the live inventory.',
      'Environment health panels separate recorded flow from hosted-UI method notes.',
      'Mobile pages clip document overflow; closed nav menus no longer paint over content.',
    ],
  },
  {
    'id': '2026-11-18-learning-layer',
    'title': 'Learning-layer vertical slice (Picassol)',
    'summary': (
      'Front door route selection, Picassol preflight, Predict→Act→Inspect workspace, '
      'stuck help, and local resume.'
    ),
    'changes': [
      'Start learning opens an orientation section with beginner, developer, and investigate routes.',
      'Picassol exposes a learning_loop with observation and practical paths.',
    ],
  },
]


def _git_sha(root: Path) -> str:
  env = os.environ.get('GITHUB_SHA') or os.environ.get('COMMIT_SHA') or ''
  if env.strip():
    return env.strip()[:40]
  try:
    out = subprocess.check_output(
      ['git', 'rev-parse', 'HEAD'],
      cwd=str(root),
      stderr=subprocess.DEVNULL,
      timeout=5,
    )
    return out.decode().strip()[:40]
  except Exception:
    return 'unknown'


def _file_digest(paths: list[Path]) -> str:
  h = hashlib.sha256()
  for p in sorted(paths, key=lambda x: str(x)):
    if not p.is_file():
      continue
    h.update(p.as_posix().encode())
    h.update(b'\0')
    h.update(p.read_bytes())
    h.update(b'\0')
  return h.hexdigest()[:16]


def curriculum_snapshot(root: Path) -> dict:
  """Counts and digest from the same inventory the public pages use."""
  live_path = root / 'dapps' / 'live.json'
  path_path = root / 'dapps' / 'lessons' / 'path.json'
  lessons_dir = root / 'dapps' / 'lessons'
  live = json.loads(live_path.read_text(encoding='utf-8')) if live_path.is_file() else []
  path = json.loads(path_path.read_text(encoding='utf-8')) if path_path.is_file() else {}
  staged_ids = {st.get('id') for st in path.get('stages', []) if st.get('id') is not None}

  guided = 0
  challenges = 0
  previews = 0
  staged = 0
  electives = 0
  records = []

  for row in live:
    slug = row.get('slug') or ''
    functional = str(row.get('functional') or '').lower()
    full = functional in ('', 'full', 'fully working', 'fully_working', 'fully-functional', 'fully functional')
    if full:
      guided += 1
      kind = 'lesson'
    else:
      challenges += 1
      kind = 'challenge'
    lesson_fp = lessons_dir / f'{slug}.json'
    L = {}
    if lesson_fp.is_file():
      try:
        L = json.loads(lesson_fp.read_text(encoding='utf-8'))
      except Exception:
        L = {}
    stage = L.get('path_stage')
    track = L.get('track') or (
      'core-path' if stage in staged_ids else (
        'elective' if full else 'debug-laboratory'
      )
    )
    if full:
      if stage in staged_ids:
        staged += 1
      else:
        electives += 1
    ui = row.get('ui_check') or ''
    records.append({
      'id': slug,
      'title': L.get('title') or row.get('name') or slug,
      'resource_type': kind if full else 'challenge',
      'track': track,
      'path_stage': stage,
      'path_order': L.get('path_order'),
      'time': L.get('time') or '',
      'verified': row.get('verified') or '',
      'functional': 'full' if full else (row.get('functional') or 'partial'),
      'ui_check': ui,
      'status': {
        'program_flow': 'recorded' if row.get('ran') or row.get('steps') else 'unknown',
        'hosted_ui': 'noted' if ui else 'unspecified',
        'content_review': L.get('content_review') or '',
      },
      'prereqs': L.get('prereqs') or [],
      'student_outcome': L.get('student_outcome') or '',
      'content_version': L.get('content_version') or L.get('version') or '',
    })

  digest_files = [live_path, path_path]
  digest_files.extend(sorted(lessons_dir.glob('*.json')))
  return {
    'guided_lessons': guided,
    'debug_challenges': challenges,
    'project_previews': previews,
    'core_path_lessons': staged,
    'electives': electives,
    'live_apps': len(live),
    'learning_activities': len(live),
    'curriculum_digest': _file_digest([p for p in digest_files if p.is_file()]),
    'lessons': records,
  }


def build_release(root: str | Path = '.') -> dict:
  root = Path(root)
  sha = _git_sha(root)
  built = datetime.now(timezone.utc).strftime('%Y-%m-%dT%H:%M:%SZ')
  snap = curriculum_snapshot(root)
  notes = RELEASE_NOTES[0] if RELEASE_NOTES else {}
  app_release = notes.get('id') or f'git-{sha[:12]}'
  return {
    'schema': 'sol.college.release/v1',
    'app_release': app_release,
    'app_release_title': notes.get('title') or app_release,
    'curriculum_version': snap['curriculum_digest'],
    'built_at': built,
    'git_sha': sha,
    'git_sha_short': sha[:12] if sha != 'unknown' else 'unknown',
    'site': 'https://sol.college',
    'counts': {
      'live_apps': snap['live_apps'],
      'guided_lessons': snap['guided_lessons'],
      'debug_challenges': snap['debug_challenges'],
      'core_path_lessons': snap['core_path_lessons'],
      'electives': snap['electives'],
      'learning_activities': snap['learning_activities'],
    },
    'notes_url': '/releases/',
    'curriculum_url': '/curriculum.json',
    'release_url': '/release.json',
    'current_notes': notes,
    'sensitive': False,
  }


def footer_html(rel: dict) -> str:
  return (
    f'<p class="sc-release" id="sc-release">'
    f'<a href="/releases/">Release {E(rel["app_release"])}</a>'
    f' · app <code>{E(rel["git_sha_short"])}</code>'
    f' · curriculum <code>{E(rel["curriculum_version"])}</code>'
    f' · built {E(rel["built_at"])}'
    f' · <a href="/release.json">release.json</a>'
    f'</p>'
  )


def meta_html(rel: dict) -> str:
  return (
    f'<meta name="sc-app-release" content="{E(rel["app_release"])}">'
    f'<meta name="sc-curriculum-version" content="{E(rel["curriculum_version"])}">'
    f'<meta name="sc-built-at" content="{E(rel["built_at"])}">'
    f'<meta name="sc-git-sha" content="{E(rel["git_sha_short"])}">'
  )


def releases_page_html(rel: dict) -> str:
  items = []
  for note in RELEASE_NOTES:
    current = ' aria-current="page"' if note.get('id') == rel.get('app_release') else ''
    lis = ''.join(f'<li>{E(c)}</li>' for c in note.get('changes') or [])
    items.append(
      f'<article class="release-note"{current}>'
      f'<h2 id="{E(note["id"])}">{E(note["title"])}</h2>'
      f'<p class="meta"><code>{E(note["id"])}</code></p>'
      f'<p>{E(note.get("summary") or "")}</p>'
      f'<ul>{lis}</ul></article>'
    )
  body = '\n'.join(items)
  return f'''<!doctype html>
<html lang="en"><head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Release notes | Sol.College</title>
<meta name="description" content="Sol.College application and curriculum release notes. Identifies what a reviewer is inspecting.">
<link rel="canonical" href="https://sol.college/releases/">
{meta_html(rel)}
<style>
body{{font-family:ui-sans-serif,system-ui,sans-serif;margin:0;background:#0b0a14;color:#eee;line-height:1.55}}
main{{max-width:42rem;margin:0 auto;padding:24px 16px 64px}}
a{{color:#7dffb3}} .meta{{color:#9a94b8;font-size:.92rem}}
.release-note{{border-top:1px solid #2a2740;padding:20px 0}}
h1{{font-size:1.8rem}} h2{{font-size:1.2rem;margin:0 0 6px}}
code{{font-size:.9em}}
.sc-release{{margin-top:32px;font-size:.85rem;color:#9a94b8}}
</style>
</head><body>
<main id="main">
<nav class="crumbs" aria-label="Breadcrumb"><a href="/">Home</a> / <span>Releases</span></nav>
<h1>Release notes</h1>
<p class="lead">Application release and curriculum version are separate. The application release names the learner-facing product build; the curriculum version is a digest of the lesson inventory.</p>
<p class="meta">This page: app <code>{E(rel["app_release"])}</code> · git <code>{E(rel["git_sha_short"])}</code> · curriculum <code>{E(rel["curriculum_version"])}</code> · built {E(rel["built_at"])}</p>
<p><a href="/release.json">Machine-readable release.json</a> · <a href="/curriculum.json">curriculum.json</a></p>
{body}
{footer_html(rel)}
</main>
</body></html>
'''


def write_artifacts(site: str | Path, root: str | Path = '.') -> dict:
  site = Path(site)
  site.mkdir(parents=True, exist_ok=True)
  rel = build_release(root)
  snap = curriculum_snapshot(Path(root))
  try:
    import curriculum_schema as _schema
    audit = _schema.audit_inventory(root)
    by_id = {r['id']: r for r in audit['lessons']}
  except Exception:
    audit = {'summary': {}}
    by_id = {}
  foundations_rows = audit.get('foundations') or []
  public_curriculum = {
    'schema': 'sol.college.curriculum/v1',
    'curriculum_version': snap['curriculum_digest'],
    'generated_from': 'dapps/live.json + dapps/lessons/*.json + dapps/foundations/catalog.json',
    'counts': {
      'live_apps': snap['live_apps'],
      'guided_lessons': snap['guided_lessons'],
      'debug_challenges': snap['debug_challenges'],
      'core_path_lessons': snap['core_path_lessons'],
      'electives': snap['electives'],
      'learning_activities': snap['learning_activities'],
      'foundations': len(foundations_rows),
    },
    'schema_summary': audit.get('summary') or {},
    'foundations': [
      {
        'id': r['id'],
        'title': r['title'],
        'resource_type': r['resource_type'],
        'track': 'foundations',
        'number': r.get('path_order'),
        'time': r.get('time') or '',
        'student_outcome': r.get('student_outcome') or '',
        'content_version': r.get('content_version') or '',
        'verification_status': r.get('verified') or 'release_candidate',
        'assessment_available': bool(r.get('assessment_available')),
        'has_learning_loop': bool(r.get('has_learning_loop')),
        'schema_status': r.get('schema_status') or 'unknown',
        'missing_required': r.get('missing_required') or [],
        'missing_recommended': r.get('missing_recommended') or [],
      }
      for r in foundations_rows
    ],
    'lessons': [
      {
        'id': r['id'],
        'title': r['title'],
        'resource_type': r['resource_type'],
        'track': r['track'],
        'path_stage': r['path_stage'],
        'path_order': r['path_order'],
        'time': r['time'],
        'verified': r['verified'],
        'status': r['status'],
        'student_outcome': r['student_outcome'] or (by_id.get(r['id']) or {}).get('student_outcome') or '',
        'content_version': r['content_version'] or (by_id.get(r['id']) or {}).get('content_version') or '',
        'schema_status': (by_id.get(r['id']) or {}).get('schema_status') or 'unknown',
        'missing_required': (by_id.get(r['id']) or {}).get('missing_required') or [],
        'missing_recommended': (by_id.get(r['id']) or {}).get('missing_recommended') or [],
      }
      for r in snap['lessons']
    ],
  }
  (site / 'release.json').write_text(json.dumps(rel, indent=2) + '\n', encoding='utf-8')
  (site / 'curriculum.json').write_text(json.dumps(public_curriculum, indent=2) + '\n', encoding='utf-8')
  releases = site / 'releases'
  releases.mkdir(exist_ok=True)
  (releases / 'index.html').write_text(releases_page_html(rel), encoding='utf-8')
  return rel


def inject_into_html(text: str, rel: dict) -> str:
  """Idempotently add release meta + footer line to an HTML document."""
  if 'name="sc-app-release"' not in text and '</head>' in text:
    text = text.replace('</head>', meta_html(rel) + '</head>', 1)
  foot = footer_html(rel)
  if 'id="sc-release"' in text or "id='sc-release'" in text:
    text = __import__('re').sub(
      r'<p class="sc-release"[^>]*>.*?</p>',
      foot,
      text,
      count=1,
      flags=__import__('re').S,
    )
  elif '</footer>' in text:
    text = text.replace('</footer>', foot + '</footer>', 1)
  elif '</body>' in text:
    text = text.replace('</body>', f'<footer>{foot}</footer></body>', 1)
  return text
