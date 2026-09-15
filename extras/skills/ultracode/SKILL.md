---
name: ultracode
description: Coordinate an explicitly requested Ultracode or durable multi-agent workflow with scoped workers and resumable state.
---

# Ultracode

Choose the lightest workflow that completes the requested outcome. Explicit invocation permits this coordination workflow, but does not expand permission for external effects or override host delegation limits.

## Choose a mode

- **Direct:** tightly coupled or small work; normal implementation and verification.
- **Thin:** visible phases and optional independent workers; no durable ledger needed.
- **Durable:** resumability, an audit trail, or multi-agent integration needs saved state.
- **Runner:** a detected, trusted runner materially helps repeatable work and its actions fit existing authorization.

An Ultracode request, task category, or elapsed timer alone does not require durable artifacts. No real worker capability means Direct or Thin; never simulate multiple agents with personas.

## Establish scope and capability

State the outcome, ownership, acceptance checks, useful phases, and any user-specified resource limits. Use the actual host's available spawn, message, wait, background execution, and progress tools; do not assume a tool namespace. Batch independent read operations with the available parallel call mechanism.

Check existing authorization before asking. Routine credentialed reads, required dependencies, local dev servers, or 15 minutes of authorized work do not by themselves require another permission question. Ask only about unresolved consequential choices, missing authority, or exceeding an explicit user/host limit. Prepare the concrete action first and pause only dependent work. See [references/risk-and-cost-gates.md](references/risk-and-cost-gates.md).

Start with 1–2 useful independent workers, or 2–4 for broader phases, within host capacity. These are sizing suggestions, not automatic approval gates. Count every worker, including bookkeeping, against actual limits. More workers must have distinct useful work; avoid idle fan-out.

## Execute

1. Inspect the relevant state and define disjoint worker ownership. Keep immediate dependent blockers and small integration fixes local.
2. For Durable/Runner mode, read [references/workflow-contract.md](references/workflow-contract.md). Create the ledger with `node <this-skill-dir>/scripts/new-ultracode-run.mjs --help` and the documented arguments. Keep `.workflow/` locally ignored; never stage or publish scratch artifacts.
3. Record the authority basis, including instructions already granting it, in the run's approval fields. A pending scaffold field is not a new requirement to ask the user. Do not mark missing authority approved.
4. Dispatch bounded packets using [references/subagent-patterns.md](references/subagent-patterns.md). Every packet carries allowed actions, paths, acceptance evidence, and resource cleanup ownership. Preserve others' edits.
5. Review each result against source files, diffs, logs, tests, or primary sources. Resolve conflicting claims with evidence. Use independent review where risk warrants it.
6. Integrate changes and verify the affected behavior. Trust recorded checks only when command, checked tree/revision, environment, and result match the integrated state. Repeat after relevant changes, failures, or incomplete evidence, not simply because a worker ran them.
7. Clean up resources created by this run or explicitly hand them off. Finish authorized follow-through; report any concrete external blocker and complete independent work.

Keep the user informed at meaningful milestones and within the host's update cadence. Report known counts and evidence; do not invent token usage or ETA. Update durable state at phase boundaries, decisions, blockers, integrations, and cleanup rather than every tool call.

## Resume and complete

Read the latest incomplete run's workflow, state, journal, integration decisions, results, and resource records. Reconcile them with the actual tree and live processes. Missing or stale ledger entries do not erase completed work. Reconstruct evidence and continue from the next unblocked phase; collapse to Direct mode if the ledger no longer helps.

When a durable run finishes, write the final report and run `scripts/verify-ultracode-run.mjs` using its documented CLI. Artifact validity supplements behavioral verification; it does not prove the task succeeded. Report changed files, verification, unresolved limitations, and resource handoff. Do not stop after a first pass when the requested result remains achievable within scope.
