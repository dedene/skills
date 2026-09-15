---
name: architect-loop
description: Run an explicitly requested architect/builder loop using a project handoff and user-defined acceptance gates.
---

# Architect Loop

Coordinate bounded builder work, inspect its evidence, and finish the authorized slice. Use this workflow when requested; ordinary implementation does not need an architect loop.

## Authority and roles

The parent owns scope, integration, evidence review, and communication. Builders own assigned files and verification. The parent may make small integration fixes when another dispatch would add cost without useful independence.

Pass the user's allowed actions to every builder. Tool access, credentials, network availability, and a passing review do not authorize commits, pushes, publication, messages, destructive operations, or production changes. Perform those only when explicitly authorized. Reuse existing authorization; ask only about unresolved consequential decisions or actions outside it. Continue independent work while awaiting an answer.

## Establish the slice

Read `docs/HANDOFF.md` if present, then inspect the current tree and relevant logs. Missing ledger entries mean missing records, not nonexistent work. Reconstruct evidence before redispatching; never invent past results.

For a new loop, use [references/handoff-template.md](references/handoff-template.md). Keep scratch handoff, builder block, contracts, and evidence local unless the user or repository explicitly wants tracked artifacts. Resolve the local exclude with `git rev-parse --git-path info/exclude`; add only this loop's untracked scratch paths. Preserve already tracked project files; do not untrack them.

Use the requested or recorded builder/model; otherwise use the configured Codex CLI defaults. See [references/builder-profiles.md](references/builder-profiles.md) for dispatch. Check installed CLI help before first use. Ask about a model only when the selected model is unavailable or a material unresolved tradeoff requires a choice.

Write a bounded spec using [references/slice-spec.md](references/slice-spec.md): goal, ownership, scope, allowed actions, acceptance evidence, relevant contracts, and facts to verify. Include design references and screenshots for user-facing work. Agree on criteria before judging results; record changed criteria as a superseding decision with its reason, never silently lower them to match results.

## Dispatch and inspect

Write the spec plus this worker contract to `docs/builder-block.md`, then invoke the selected builder. Use the host's background/session facilities for long runs and remain responsive.

```text
Execute the attached slice within its ownership and allowed actions.
You are not alone in the codebase. Preserve others' changes.
Review the plan and relevant files first. Raise concrete objections with evidence; "no objections" is valid after review. Do not invent disagreement or add scope silently.
Resolve routine choices from evidence. Pause dependent work only for an unresolved consequential choice or missing authority; continue independent work.
Stabilize shared contracts before concurrent implementation when needed. Coordinate changes that affect another owner's interface.
Use independent workers only when the host and task authorize delegation and useful disjoint work exists. Prefer a focused reviewer for high-risk changes.
Complete implementation and the relevant verification. Fix failures caused by the change. Report unrelated failures precisely.
Do not commit, push, publish, message others, perform destructive operations, or change production unless the allowed-actions field explicitly grants that action. Network access is not permission.
Record changed files, commands, checked revision/tree state, environment, results, and evidence paths in docs/HANDOFF.md. Include screenshots or observations for visual criteria. Report uncertainty and blockers honestly.
Keep loop scratch artifacts local; never force-add them.
```

Read the builder's diff, objections, command results, and visual evidence. Rule on actual objections with ACCEPT / REJECT / MODIFY and a reason. A clean review needs no invented objections. If output or handoff is missing, inspect the working tree and transcript and recover usable evidence before requesting more work.

## Verify and finish

Judge each criterion as PASS, FAIL, or UNVERIFIED with supporting evidence. Screenshots, behavioral observations, and code inspection can support criteria alongside numbers. Missing evidence is UNVERIFIED until checked; it is not proof the implementation failed.

Review recorded verification against the actual changed tree and environment. Rerun affected checks after edits, failures, or incomplete evidence; do not duplicate a valid unchanged gate solely because a worker ran it.

Continue iterations within the authorized scope. Stop dispatching when repeated attempts produce no useful progress; investigate the blocker or ask about a concrete rescope. Once the requested local slice and verification are complete, return the verified diff and recommendation. A SHIP recommendation does not itself authorize publication. Perform already authorized follow-through; ask only for missing authority or a consequential unresolved gate.

Keep the handoff current at integration and decision boundaries so another session can resume. For phase rationale, see [references/builder-goal.md](references/builder-goal.md).
