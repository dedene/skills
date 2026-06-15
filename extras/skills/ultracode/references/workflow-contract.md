# Ultracode Workflow Contract

This contract describes the Durable Workflow ledger. Direct and Thin modes do not need these files.

## Run Directory

The ledger lives under the project root:

```text
.workflow/ultracode/<run-id>/
  workflow.md
  state.json
  journal.md
  packets/
    001-name.md
  results/
    001-name.md
  integration.md
  final-report.md
```

Use a timestamped slug for `<run-id>`, for example `20260615-113000-react-to-solid-migration`.

`.workflow/` is local scratch state. It must be ignored by Git and never committed. Prefer adding `.workflow/` to `.git/info/exclude` so the workflow does not create a tracked `.gitignore` change. Only edit `.gitignore` when the user explicitly wants the ignore rule committed.

## Ownership Model

The parent thread owns user interaction, approvals, budget/resource decisions, final decisions, and the final answer.

Artifact ownership depends on the run:

- With a real bookkeeper worker: the bookkeeper is the single writer for `.workflow/ultracode/<run-id>/**`.
- Without a real bookkeeper worker: the parent updates artifacts only at phase boundaries, integration decisions, verification results, and resource lifecycle events.
- Packet workers return results to the parent. They do not edit `.workflow/` unless their assigned role is `bookkeeper`.

Do not spawn fresh bookkeepers for routine lifecycle events in Codex. That costs more than it preserves.

## State File

`state.json` is the machine-readable index. Keep it small, current, and honest.

```json
{
  "title": "React to Solid migration",
  "runId": "20260615-113000-react-to-solid-migration",
  "createdAt": "2026-06-15T11:30:00Z",
  "updatedAt": "2026-06-15T11:35:00Z",
  "status": "running",
  "mode": "durable",
  "root": ".",
  "budget": {
    "maxConcurrentAgents": 4,
    "maxTotalAgents": 16,
    "timeLimitMinutes": 45,
    "network": false,
    "credentialedTools": false
  },
  "approval": {
    "status": "approved",
    "approvedAt": "2026-06-15T11:31:00Z",
    "writes": ["solid-migration/**"],
    "verification": ["typecheck", "tests", "migration report"]
  },
  "progress": {
    "percentComplete": 35,
    "eta": "20-40 min",
    "etaConfidence": "medium",
    "status": "yellow",
    "statusReason": "Infrastructure phase has one blocked test setup packet",
    "done": ["Inventory", "Pattern Analysis"],
    "remaining": ["Infrastructure", "Core Port", "App Port", "Verify"]
  },
  "phases": [
    {
      "id": "03",
      "name": "Infrastructure",
      "status": "running",
      "agentCount": 10,
      "completeAgents": 3,
      "startedAt": "2026-06-15T11:33:00Z",
      "completedAt": null,
      "elapsedMs": 120000,
      "summary": "Tooling and app shell in progress"
    }
  ],
  "agents": [
    {
      "id": "infra-package-json",
      "nickname": "infra:package.json",
      "phaseId": "03",
      "packet": "packets/003-infra-package-json.md",
      "result": "results/003-infra-package-json.md",
      "status": "complete",
      "tools": 9,
      "tokens": null,
      "startedAt": "2026-06-15T11:33:10Z",
      "completedAt": "2026-06-15T11:33:38Z",
      "summary": "Scripts and dependencies updated"
    }
  ],
  "resources": [],
  "verification": [],
  "nativeWorkflow": null
}
```

Allowed run `status`: `planning`, `approved`, `running`, `paused`, `integrating`, `verifying`, `complete`, `blocked`, `cancelled`.

Allowed phase and agent `status`: `pending`, `running`, `complete`, `blocked`, `failed`, `cancelled`, `closed`.

Allowed resource `status`: `planned`, `active`, `idle`, `closed`, `released`, `stopped`, `removed`, `cleaned`, `leaked`, `handed-off`, `unknown`.

Allowed `etaConfidence`: `low`, `medium`, `high`.

Allowed progress `status`: `green`, `yellow`, `red`.

Use `null` for token or tool counts that the host does not report. Do not invent cost data.

## Workflow File

`workflow.md` is the readable orchestration script. It is not executable unless a real runner consumes it, but it should be structured enough to rerun manually.

```markdown
# Workflow

## Goal

## Args

## Approval Envelope

- Mode:
- Max concurrent agents:
- Max total agents:
- Time limit:
- Write scopes:
- Network:
- Credentialed tools:
- Verification gates:

## Phase Graph

| Phase | Depends On | Max Agents | Read Scope | Write Scope | Output |
| --- | --- | ---: | --- | --- | --- |

## Execution Rules

- Parent critical path:
- Worker packet rule:
- Reducer rule:
- Reviewer rule:
- Stop conditions:
```

## Journal

`journal.md` is the concise event stream. Write only meaningful lifecycle events.

```markdown
# Journal

## 2026-06-15T11:31:00Z

- Approved Durable Workflow. Budget: 4 concurrent agents, 16 total agents.

## 2026-06-15T11:33:00Z

- Phase 03 Infrastructure started. Spawned 3 of 10 planned agents.
```

Do not journal every command, tool call, thought, or file read.

## Progress Dashboard

The dashboard appears in the main thread and can also be copied into `journal.md` at check-ins.

```text
Ultracode: <run-id>
<complete>/<total> agents complete | elapsed <duration> | status <green|yellow|red>: <reason>

| Phase | State | Agents | Elapsed | Evidence | Next |
| --- | --- | ---: | ---: | --- | --- |
| 01 Inventory | done | 4/4 | 1m20s | results/001-* | accepted |
| 02 Patterns | done | 4/4 | 2m45s | results/002-* | accepted |
| 03 Infrastructure | running | 2/3 | 5m30s | 2 files changed | finish tooling |
```

Agent drill-down:

```text
| Agent | Phase | State | Scope | Tools | Result |
| --- | --- | --- | --- | ---: | --- |
| infra:package.json | Infrastructure | done | package.json | 9 | scripts updated |
| infra:vite.config.ts | Infrastructure | running | vite.config.ts | 8 | checking aliases |
```

## Packet Template

```markdown
# Packet 001: Short Name

## Phase

## Objective

## Context

Only include the minimum source paths, facts, screenshots, links, or logs needed.

## Allowed Scope

- Read:
- Write:
- Tools:
- Network:
- Resources:
- Cleanup:

## Non-Goals

-

## Required Output

- Findings:
- Evidence:
- Changed files, if any:
- Verification run, if any:
- Resource cleanup:

## Risk Notes

-
```

## Result Template

```markdown
# Result 001: Short Name

## Status

complete | blocked | partial | failed

## Summary

## Evidence

-

## Changes

-

## Verification

- Command:
- Result:

## Resources

- Started:
- Closed:
- Handed off:

## Open Questions

-
```

## Integration Template

```markdown
# Integration

## Results Reviewed

-

## Accepted

-

## Rejected

-

## Conflicts Resolved

-

## Integrated Changes

-

## Deferred

-
```

## Final Report Template

```markdown
# Final Report

## Outcome

## Files Changed

-

## Verification Evidence

-

## Resource Cleanup

-

## Remaining Risks

-

## Follow-Ups

-
```

## Native Workflow Mirror

When a host provides a real native workflow runner, keep the durable ledger and record a pointer to the native run:

```json
{
  "nativeWorkflow": {
    "host": "claude-code",
    "runId": "wf_abc123",
    "workflowName": "migration-audit",
    "scriptPath": "<native workflow script path>",
    "snapshotPath": "<native wf_*.json path>",
    "agentLogDir": "<native subagents/workflows/wf_* path>",
    "totalTokens": 123456,
    "totalToolCalls": 42,
    "durationMs": 600000
  }
}
```

Native artifacts are evidence, not the portable contract. Summarize accepted outputs into `results/`, `integration.md`, and `final-report.md`.
