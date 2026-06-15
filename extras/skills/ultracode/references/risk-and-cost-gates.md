# Ultracode Risk And Cost Gates

Use these gates for Durable and Runner workflows. Direct and Thin modes still follow normal repo and user instructions.

## Approval Gates

Ask before starting a workflow when it involves:

- destructive file or git operations
- staging, committing, force-adding, copying, publishing, or sharing `.workflow/` artifacts
- production, customer, billing, security, or credentialed changes
- external API writes, purchases, messages, deploys, or data exports
- new dependencies or unfamiliar install scripts
- more than 4 concurrent agents
- more than 16 total Codex agents
- more than 15 minutes unattended
- network-heavy research not directly required by the task
- credentialed connectors or private customer data in worker prompts
- writes outside the repo or outside the stated write scope
- starting a browser, Docker container, dev server, simulator, watcher, tmux pane, background job, or open port
- starting a second live resource of the same type

Ask with one concrete sentence. State the exact action, risk, and limit.

Example:

```text
This workflow would run 6 concurrent agents across the migration tree for up to 45 minutes and write only under solid-migration/**. Approve that budget?
```

Approval covers routine worker lifecycle events inside the stated envelope. Ask again only when the envelope changes.

## Default Budgets

| Task shape | Concurrent agents | Total agents | Notes |
| --- | ---: | ---: | --- |
| Focused investigation | 1-2 | 2-4 | Usually Thin mode |
| Normal Durable Workflow phase | 2-4 | 4-16 | Ask before exceeding |
| Broad audit or migration | 4 | 16 | Use phases and reducers |
| Adversarial verification | 1-2 | 2-4 | After integration |
| Runner workflow | explicit approval | explicit approval | Must name runner and timeout |

The bookkeeper does not count as an execution worker, but it still consumes resources. Use at most one active bookkeeper per run.

## Safety Policy

Default to:

- read-only scouts before write workers
- disjoint write scopes for implementation workers
- `.workflow/` as local scratch only
- no secrets in prompts, packets, results, or artifacts
- no connector or credential use inside workers unless explicitly approved
- no broad write access
- no destructive commands
- no network unless needed for current facts or explicitly approved
- parent-owned final decisions and final answer

If a worker needs sensitive context, pass only the minimum metadata required. Do not put secrets, tokens, private logs, or customer data into packet files.

## Resource Policy

Before starting a resource-heavy action:

- record owner, purpose, identifier when known, expected cleanup, and approval basis
- prefer assigning resource-heavy work to a bounded packet
- check whether an existing resource can be reused safely
- avoid stacking browsers, containers, dev servers, watchers, and ports

During the run:

- include active resources in progress updates
- close idle resources before spawning more
- mark unknown or stale resources during resume

Before handoff:

- close, stop, remove, release, or explicitly hand off every resource
- record cleanup evidence in `final-report.md`
- run the artifact validator when a Durable ledger exists and the environment can access it

Resource statuses: `planned`, `active`, `idle`, `closed`, `released`, `stopped`, `removed`, `cleaned`, `leaked`, `handed-off`, `unknown`.

## Runner Policy

Runner mode needs explicit policy before execution:

```json
{
  "runner": "name-or-command",
  "maxConcurrentAgents": 4,
  "maxTotalAgents": 16,
  "timeLimitMinutes": 45,
  "network": false,
  "write": ["specific/path/or/prefix"],
  "secrets": "metadata-only",
  "resume": "documented behavior",
  "stop": "documented command"
}
```

Do not use Runner mode until a named executable or native workflow tool is detected and trusted.

## Evidence Standards

Every accepted result should include at least one of:

- file paths and line references
- command and output summary
- test failure or pass evidence
- source URL for external research
- screenshot path or browser observation
- resource cleanup status
- explicit statement that the result is opinion-only

Do not accept:

- "looks good" with no evidence
- claims about current facts without source checks
- security conclusions without concrete reviewed surfaces
- verification claims without command names or observed result
- resource-heavy results without cleanup status

## Stop Conditions

Stop and ask the user when:

- the task goal changes materially
- the workflow exceeds the approved budget
- workers uncover higher risk than the approval card covered
- required credentials or production authority are missing
- resource usage is stacking up and ownership is unclear
- results conflict and cannot be resolved from available evidence
- verification is blocked by missing environment, failing unrelated tests, or external outage
- the workflow ledger and real workspace state disagree after resume
