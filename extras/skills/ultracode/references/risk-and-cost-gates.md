# Ultracode authority, resources, and verification

Skills do not grant authority. Reuse the user's instructions and host policy; do not ask again for work already authorized.

## Decision boundaries

Ask only for missing authority or an unresolved choice that materially changes the outcome, incurs meaningful cost, or creates costly rework. Prepare the concrete action and explain the boundary; pause only dependent work.

Commit, push, publish, message others, perform destructive operations, or change production only within explicit authorization. Credentials and network access never grant permission. Keep secrets out of prompts and artifacts; delegate only the minimum relevant private context to an authorized worker surface.

Routine authenticated reads, task-required research, local development resources, and elapsed time alone do not create approval gates. Follow actual user budgets, host limits, and repository dependency policies. If a requested action exceeds them, ask about that concrete excess.

## Resource sizing and ownership

Start with 1–2 independent workers for focused work or 2–4 for broad phases. These are sizing suggestions, not fixed permission thresholds. Include bookkeepers in actual worker limits. Do not create duplicate workers without a distinct task or a useful independent review.

For each browser, container, dev server, watcher, session, or port, record owner, purpose, identifier, and cleanup plan. Reuse an existing task-owned resource when appropriate. Clean up only resources owned by this run; do not sweep unrelated sessions. Before handoff close or explicitly hand off each resource and record evidence.

Resource statuses: `planned`, `active`, `idle`, `closed`, `released`, `stopped`, `removed`, `cleaned`, `leaked`, `handed-off`, `unknown`.

## Runner and ledger policy

Verify the runner executable, allowed writes, network behavior, resource limits, stop command, and resume semantics before use. Apply existing authorization to its concrete actions; request only missing permission. Keep workflow scratch artifacts local and ignored.

The ledger's `approval` object records authority already granted as well as new answers. Set `approved` only when instructions actually cover the actions, describe that basis in workflow/journal, and leave unresolved actions pending. Scaffold defaults and illustrative time budgets are not user-imposed limits.

## Evidence and stopping

Require source paths, command results, tests, primary-source links, screenshots, or inspected observations appropriate to the claim. Label opinion and uncertainty. Check recorded command, tree/revision, environment, and result before relying on worker verification. Rerun affected checks after edits or when evidence is incomplete; do not repeat unchanged valid checks by ritual.

Finish all authorized work. For environmental outages, missing access, or unrelated failures, report exact evidence and complete independent work. A durable artifact validator checks records, not behavioral success.
