# Core lessons (one per app that is live on devnet)

`scripts/core_lessons.py` runs after `scripts/live_devnet.py` on every build. For every entry in `dapps/live.json` it writes
`/lessons/<slug>/` (canonical) and the same page at `/explore/<slug>/`, the `/lessons/` index, the `/lessons/path/` learning
path (beginner to advanced, by concept), the `/lessons/glossary/`, the homepage hero and path, the main nav, and the
"Source library (not yet live)" labels on every walkthrough that is not live.

Every full lesson has the same structure:

0. At the top: difficulty, time estimate, path stage, **learning objectives**, **prerequisites**, and **concepts you'll meet** (each linked to the glossary).
1. What the app does (+ live app, program, explorer)
2. Try it yourself (Phantom on devnet, numbered steps with what you should see)
3. How it works (diagram, accounts table, each instruction with real code at the pinned commit)
4. The key idea
5. Frontend wiring
6. Proof (signatures and rejections from `dapps/live.json`; we never invent these)
7. Exercises (bugs as exercises where we found them; each has a hint and a folded reference approach — described, not invented outputs)
8. Build it yourself locally (exact `git checkout` + `anchor build` commands; we only claim a result we have actually produced)

**New live app = lesson automatically.** If `dapps/lessons/<slug>.json` does not exist, the lesson is generated from the app's
`live.json` entry (summary, source refs, proof) and marked as a draft. Add `dapps/lessons/<slug>.json` to replace it with the full lesson.

## `dapps/lessons/<slug>.json`

```json
{
 "title": "…", "summary": "one line for cards", "what": "one paragraph", "app_note": "what we changed to host it",
 "difficulty": "Beginner|Intermediate|Advanced", "time": "30 min",
 "path_order": 1, "path_stage": 1,
 "objectives": ["what you will be able to do"],
 "prereqs": ["wallet, earlier lessons — markdown allowed"],
 "concepts": ["pda", "cpi"],
 "try_steps": [{"do": "…", "see": "…"}],
 "diagram": "plain-text diagram", "accounts": [["Account", "Address (seeds)", "Holds"]],
 "instructions": [{"name": "`ix`: …", "refs": [{"path": "file in the fork", "a": 10, "b": 20, "note": "optional"}], "steps": ["…"]}],
 "innovation": {"title": "…", "text": "…", "refs": [ … ], "more": ["…"]},
 "frontend": [{"title": "…", "refs": [ … ], "steps": ["…"]}],
 "exercises": [{"title": "…", "steps": ["…"], "expect": "…", "hint": "…", "approach": "…"}],
 "build": {"dir": "programs/…", "anchor": "0.30.1", "test": "anchor test", "note": "…", "ran": "what we actually ran"}
}
```

`path_order` and `path_stage` place the lesson on `/lessons/path/`. Stage names live in `dapps/lessons/path.json`.
Concept ids must exist in `dapps/lessons/glossary.json`.

Code is never typed into the JSON: a ref is a path and line range at the fork commit pinned in `live.json` (or `"repo"`/`"ref"` for
another repo at a pinned commit, e.g. our own patch). The lines are fetched from GitHub and cached in `excerpts.json`.
Text supports `` `code` ``, `**bold**` and `[text](url)`. Proof is never written here: it comes from the recorded runs in `live.json`.
