# Operations

## Minds CLI (`cd pilot && npx tsx src/minds/cli.ts …`) and the `minds-admin` workflow
| Command | Class | Approval |
| --- | --- | --- |
| `inventory` | read | none (environment `minds`) |
| `project <slug>`, `reconcile <slug>`, `telemetry <slug>`, `capabilities <slug>` | read | none; requires an approved project->Mind mapping |
| `provision <slug> --name N --archetype A` | mutation | `minds-admin` reviewer; idempotent state machine |
| `equip <slug> --skills id,…` / `--apps id,…` | mutation | reviewer; result + final state checked; partial success exits 2 |
| `circle <slug> --add … --remove …` | mutation | reviewer; only `SC_CIRCLE_APPROVED_MEMBERS`; stewards never removed |
| `pause <slug>` / `resume <slug>` | mutation | reviewer; targets one project's Mind only |
| `smoke-test --mind-name N [--allow-message]` | read (+1 message) | message only for a designated test Mind, with approval |

## Provisioning states
`requested -> creation-intent -> (mind-confirmed | creation-uncertain) -> mapping-recorded -> conversation-configured -> verified`.
An ambiguous `awakenMind` outcome becomes `creation-uncertain`; the next run reconciles and lists same-name Minds
but never adopts by name and never awakens again. Resolve with `resolveUncertainProvision` (operator confirms the
Mind ID or that none was created).

## Structured tasks
`queued -> dispatch-intent -> dispatched -> (response-received -> validated -> completed | uncertain | operator-review)`.
One conversation alias per task (`<prefix>-<kind>-<taskId>`). Duplicate requests return the stored record.
Timeouts and failed sends become `uncertain`; `reconcileTask` reads newest-first history for the exact sent text and
a later reply naming the taskId. Nothing is resent automatically. Concurrency: a per-task lock file plus workflow
`concurrency` groups. GitHub Actions concurrency is not exactly-once delivery; the lock and the persisted intent are
what prevent double sends, and they only hold within one records store.

## Rerun policy (validation)
The newest run (highest run id) of `candidate-validation.yml` for the exact candidate decides, at its latest attempt.
An older pass never hides a newer failure. Re-running a failed run produces a new attempt of the same run; a passing
re-attempt is recorded with its attempt number.

## Upstream
`upstream-reconcile` (every 6 hours or manual) reads the actual upstream head, compares with the recorded head through
GitHub compare, refuses to rewind on out-of-order observations, flags force-pushed (diverged) upstreams for operator
review, and lists experiments needing rebase/retest.

## Evidence retention
Actions artifacts expire (90 days here). Durable evidence = the adoption manifest in `records/public/adoption/`
(run id, attempt, jobs, artifact digests, canonical bytes hashed with sha256). Confidential artifacts belong in the
private control repo. Repository administrators can still rewrite history; GitHub does not make records tamper-proof.

## Pausing
`minds-admin` with action `pause` and a project slug disables only that project's Mind. Never disable the whole account automatically.
