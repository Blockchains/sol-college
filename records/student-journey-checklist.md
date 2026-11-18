# Student-journey checklist tracker

Track Release A–E against the consolidated learning-workflow redesign.
Do not mark an item complete because a screen exists — acceptance conditions must work.

Legend: `done` · `partial` · `todo`

## Release A — Correctness and clarity

| Item | Priority | Status | Implementation reference | Acceptance evidence |
|---|---|---|---|---|
| Public release identifier | P0 | done | `scripts/release_identity.py`, footer, `/releases/` | `/release.json` + footer `sc-release` |
| Deployment timestamp | P0 | done | `built_at` in release.json | ISO-8601 UTC on release page |
| App vs curriculum version | P0 | done | `app_release` ≠ `curriculum_version` digest | release.json fields |
| Release notes page | P0 | done | `/releases/` | User-visible change list |
| Public release endpoint | P0 | done | `/release.json` | Non-sensitive JSON only |
| Curriculum source of truth (counts) | P0 | done | inventory → landing + `/curriculum.json` | Homepage/catalogue agree |
| Counts / path / elective labels | P0 | done | #60 curriculum consistency | Tests in `test_curriculum_consistency.py` |
| Metadata rendering guards | P0 | done | `curriculum_copy.format_limit_text` | No raw array syntax |
| Beginner entrance | P1 | done | `#start` + learning_layer | `test_learning_layer.py` |
| Honest status labels | P0 | done | env-health panel + Picassol ui_check | Program flow vs hosted UI vs frontend/RPC |
| Picassol correctness (create/account) | P0 | partial | lesson JSON + live ui_check | Hosted create recorded; recolour observation/script until hosted UI lands |
| Canonical per-lesson schema (owner, content_version, …) | P0 | partial | `curriculum_schema.py` + backfill | Required fields complete for all live guided lessons; recommended fields still open on ~24 |
| Cache / old-tab update notice | P0 | done | `scripts/release-notice.js` | Banner when `/release.json` app/curriculum changes |

## Release B — One complete learning journey

| Item | Status | Notes |
|---|---|---|
| Front door → route selection | done | `#start` |
| Lesson preview / contract | partial | Picassol learning_loop |
| Preflight | done (Picassol) | observation + practical |
| Predict → Act → Inspect → Explain | done (Picassol) | workspace |
| Independent assessment | done (Picassol) | `/lessons/picassol-hackathon/assessment/` |
| Saved outcome + resume | done (Picassol) | content_version + predict lock restore + attempt recovery |
| Evidence provenance tags | done (Picassol) | route tag + optional signature + stale note |
| Pending / unclear tx recovery | done (Picassol) | Attempt recovery panel; no blind resubmit guidance |
| Failure routes observed with learners | todo | — |

## Later releases

- Release C: reusable workspace/preflight/evidence/help/assessment components — `partial` (shared `learning_layer.py`; Stage 1 complete; Stage 2: CipherVault + MandateKey + Trust Protocol; remaining Stage 2–3 open)
- Release D: Foundations migration + rubrics — foundations 001–007 RC exist; verification open
- Release E: AI tutor, personalisation, community — `todo` (P2)

## Definition of done (product)

A student can find a start, prepare safely, know the current task, inspect evidence, explain, recover, demonstrate on a fresh example, save, and return. **First milestone: one excellent vertical slice (Picassol), then scale.**
