# Ultracode Risk And Cost Gates

## Table Of Contents

- Approval gates
- Worker budget
- Safety policy
- Resource policy
- Evidence standards
- Stop conditions

## Approval Gates

Ask the user before:

- Destructive file or git operations.
- Staging, committing, force-adding, copying, or publishing `.workflow/` artifacts.
- Production, customer, billing, security, or credentialed changes.
- External API writes, purchases, messages, deploys, or data exports.
- Adding new dependencies or running unfamiliar install scripts.
- More than 4 concurrent workers.
- Network-heavy research or long-running runner workflows.
- Starting resource-heavy work that may linger: browsers, Docker containers, dev servers, background jobs, tmux panes, simulators, file watchers, or open ports.
- Passing sensitive files, secrets, private logs, or customer data to subagents.

Use a short concrete question. State the exact action, risk, and limit.

## Worker Budget

The bookkeeper is orchestration overhead, not an execution worker. Start at most one active bookkeeper per run.

Default worker counts:

| Task shape | Workers |
| --- | --- |
| Focused investigation | 1-2 |
| Multi-slice implementation | 2-3 |
| Broad code review or research | 3-4 |
| Migration across many modules | Ask before 5+ |
| Adversarial verification | 1-2 reviewers after integration |

Each worker should have a clear expected value. If two workers would read the same files for the same question, merge the packet.

## Safety Policy

Default to:

- Read-only scouts.
- `.workflow/` artifacts as local scratch state only; keep them Git-ignored and out of commits.
- Main thread as supervisor only; delegate workflow artifact maintenance to one bookkeeper and workflow execution to subagents when available.
- Single-writer bookkeeping: after the bookkeeper starts, parent and workers do not edit `.workflow/ultracode/<run-id>/**`.
- No network unless the packet needs current or external facts.
- No secrets in prompts or result files.
- No connector or credential use inside workers unless explicitly approved.
- No broad write access.
- No destructive commands.
- Parent agent owns final decisions and final answer; the bookkeeper records decisions but does not make them. Delegate bulky integration and verification work when available, then verify the evidence before handoff.

## Resource Policy

Before starting resource-heavy work:

- Send a resource event to the bookkeeper with owner, purpose, status, and cleanup action.
- Prefer assigning the work to a subagent packet so the main thread stays clear for user interaction.
- Check existing resources before starting another browser, container, dev server, watcher, or long-running job.
- Reuse a running resource only when its owner and state are clear.

During long workflows:

- Include resource status in each 10-minute progress brief.
- Watch for stacking browsers, Docker containers, test watchers, ports, and background jobs.
- Stop and clean up idle or stale resources before spawning more.

Before final handoff:

- Close, stop, or explicitly hand off every resource.
- Ask the bookkeeper to record cleanup evidence in `final-report.md`.
- Run the artifact verifier in strict mode when artifacts exist and the host can access them.

For runner mode, write policy before execution:

```json
{
  "maxWorkers": 4,
  "maxTokens": "bounded by host",
  "network": false,
  "write": ["specific/path/or/prefix"],
  "secrets": "metadata-only",
  "timeoutMinutes": 30
}
```

## Evidence Standards

Every result should include at least one of:

- File paths and line references.
- Command and output summary.
- Test failure or pass evidence.
- Source URL for external research.
- Screenshot path or browser observation.
- Resource cleanup status when the packet opened anything.
- Explicit statement that the packet is opinion-only.

Do not accept:

- "Looks good" with no evidence.
- Claims about current facts without source checks.
- Security conclusions without concrete reviewed surfaces.
- Verification claims without command names or observed result.
- Resource-heavy packet results without cleanup status.

## Stop Conditions

Stop and ask the user when:

- The task goal changes materially.
- Workers uncover a higher-risk path than the original request implied.
- Required credentials or production authority are missing.
- Resource usage is stacking up, memory pressure appears, or the agent cannot identify what is still running.
- The workflow exceeds the approved budget.
- Results conflict and cannot be resolved from available evidence.
- Verification is blocked by missing environment, failing unrelated tests, or external outage.
