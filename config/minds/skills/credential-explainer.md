# Skill playbook: Credential Explainer

Status: PLAYBOOK ONLY. Not built, not published to Bazaar, not equipped on any Mind.
Building, publishing or equipping requires operator approval (see docs/minds-setup.md). Private project
information must never be published to Bazaar; a published version of this Skill must be generic.

## Purpose
Explain what a Sol.College credential does and does not certify (one accepted contribution; not accreditation, not on-chain, not signed).

## Registry Offering (how it is found)
- Name: Sol.College Credential Explainer
- Listing visibility: private to Sol.College Minds unless the operator approves a generic public version.

## App Manifest (how it connects)
- Inputs arrive inside structured tasks (`sc-task/1`) sent by protected GitHub workflows.
- No direct GitHub write access. GitHub reads, if ever enabled, go through a supported HelloMinds Connection,
  restricted to the project's lab and upstream repositories and started read-only.

## Tool Schemas (what it can do)
- Read the task envelope (sources, evidence ids, context).
- Produce an `sc-task-response/1` JSON object. No other side effects.

## Skill Playbook (how it behaves)
1. Confirm the task's project and kind; refuse out-of-scope requests.
2. Cite only the provided source and evidence ids; separate facts from hypotheses.
3. Put open questions in `uncertainties`.
4. Never state that validation passed, that a contribution was accepted, or that a credential exists.
