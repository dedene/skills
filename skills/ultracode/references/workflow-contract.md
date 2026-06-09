# Ultracode Workflow Contract

## Table Of Contents

- Run directory
- State file
- Native workflow mirror
- Plan template
- Orchestration template
- Check-in contract
- Resource ledger
- Packet template
- Result template
- Integration template
- Final report template

## Run Directory

Create one run directory per user task:

```text
.workflow/ultracode/<run-id>/
  plan.md
  orchestration.md
  state.json
  packets/
    001-name.md
  results/
    001-name.md
  integration.md
  final-report.md
```

Use a timestamped slug for `<run-id>`, for example `20260608-141530-fix-auth-race`.

`.workflow/` is local scratch state. It must be ignored by Git and never committed. Prefer adding `.workflow/` to `.git/info/exclude` so the workflow does not create a tracked `.gitignore` change. Only edit `.gitignore` if the user explicitly wants the ignore rule committed.

## State File

`state.json` is the machine-readable index. Keep it small and current.

```json
{
  "title": "Fix auth race",
  "runId": "20260608-141530-fix-auth-race",
  "createdAt": "2026-06-08T14:15:30Z",
  "status": "planning",
  "mode": "delegated",
  "root": ".",
  "checkInIntervalMinutes": 10,
  "lastCheckInAt": null,
  "nextCheckInDueAt": "2026-06-08T14:25:30Z",
  "checkIns": [],
  "resources": [],
  "nativeWorkflow": null,
  "packets": [
    {
      "id": "001",
      "name": "trace-auth-flow",
      "status": "pending",
      "owner": "subagent",
      "packet": "packets/001-trace-auth-flow.md",
      "result": "results/001-trace-auth-flow.md"
    }
  ],
  "approvals": [],
  "verification": []
}
```

Allowed `status`: `planning`, `delegating`, `integrating`, `verifying`, `complete`, `blocked`, `cancelled`.

Allowed packet `status`: `pending`, `running`, `complete`, `blocked`, `rejected`.

Allowed resource `status`: `planned`, `active`, `idle`, `closed`, `released`, `stopped`, `removed`, `cleaned`, `leaked`, `handed-off`.

## Native Workflow Mirror

When the host provides a native workflow runner, keep using this portable run directory and record a pointer to the native run in `state.json`.

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

## Plan Template

```markdown
# Plan

## Goal

## Success Criteria

- [ ]

## Non-Goals

- 

## Constraints

- 

## Risks

- 

## Verification Gates

- [ ] 
```

## Orchestration Template

```markdown
# Orchestration

## Mode

Direct | Workflow | Delegated | Runner

## Host Capabilities

- Native subagents:
- Runner:
- Network:
- Write access:

## Work Packets

| Packet | Owner | Scope | Dependencies | Expected result |
| --- | --- | --- | --- | --- |

## Check-In Cadence

- Interval: 10 minutes
- Last check-in:
- Next check-in:
- Phase-change updates:

## Resource Plan

| Resource | Owner | Purpose | Cleanup |
| --- | --- | --- | --- |

## Stop Conditions

- 

## Budget

- Workers:
- Time:
- Token/cost limit:
```

## Check-In Contract

The main thread owns check-ins. For long-running workflows, add entries to `state.json` and post a short user-facing update every 10 minutes or at phase changes.

```json
{
  "at": "2026-06-08T14:25:30Z",
  "phase": "delegating",
  "summary": "Two scouts are tracing auth flow; verifier is preparing repro command.",
  "activePackets": ["001-trace-auth-flow", "002-repro-race"],
  "resources": ["browser:playwright-auth-repro"],
  "next": "Integrate findings after scout results return."
}
```

## Resource Ledger

Track resource-heavy work in `state.json` as soon as it is planned or created. Update status when closed, released, or handed off.

```json
{
  "id": "browser:auth-repro",
  "type": "browser",
  "owner": "packet-002",
  "purpose": "Reproduce auth redirect race",
  "status": "active",
  "createdAt": "2026-06-08T14:18:00Z",
  "cleanup": "close Playwright browser/context",
  "notes": "Headless Chromium"
}
```

Track at least: browsers, Docker containers, dev servers, background processes, tmux panes, temp directories, open ports, simulators, and long-running test watchers.

## Packet Template

```markdown
# Packet 001: Short Name

## Objective

## Context

Only include the minimum source paths, facts, screenshots, links, or logs needed.

## Allowed Scope

- Read:
- Write:
- Tools:
- Resources:
- Cleanup:

## Non-Goals

- 

## Required Output

- Findings:
- Evidence:
- Changed files, if any:
- Verification run, if any:

## Risk Notes

- 
```

## Result Template

```markdown
# Result 001: Short Name

## Status

complete | blocked | partial

## Summary

## Evidence

- 

## Changes

- 

## Verification

- Command:
- Result:

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
