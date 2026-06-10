# Ultracode Workflow Contract

## Table Of Contents

- Run directory
- Ownership model
- State file
- Native workflow mirror
- Plan template
- Orchestration template
- Supervisor brief contract
- Resource ledger
- Packet template
- Result template
- Integration template
- Final report template

## Run Directory

The bookkeeper creates and maintains one run directory per user task:

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

## Ownership Model

Use a single writer for workflow artifacts.

- The `bookkeeper` subagent owns every file under `.workflow/ultracode/<run-id>/**`.
- The main thread owns user interaction, approvals, budget/resource decisions, worker lifecycle, progress reports, and final synthesis.
- Workers return results to the main thread. They do not edit `.workflow/`.
- The main thread forwards accepted events, decisions, worker outputs, verification results, and resource changes to the bookkeeper.
- The bookkeeper records facts and returns supervisor briefs. It does not make product, safety, or completion decisions.

If the host cannot keep one persistent bookkeeper alive, spawn a fresh bookkeeper with the run path and latest lifecycle event. Preserve single-writer ownership: do not let the parent, workers, and bookkeeper edit the same artifact set.

## State File

`state.json` is the machine-readable index. The bookkeeper keeps it small and current.

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
  "progress": {
    "percentComplete": 5,
    "eta": "unknown",
    "etaConfidence": "low",
    "done": [],
    "remaining": ["Write packets", "Run workers", "Verify"],
    "status": "green",
    "statusReason": "Workflow initialized"
  },
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

`progress.percentComplete` is a coarse estimate, not fake precision. Use task maturity and accepted evidence, not packet count alone. Default phase weights:

| Phase | Weight |
| --- | ---: |
| Planning and packetization | 5% |
| Scouts and design discovery | 15% |
| Implementation | 40% |
| Review and fixes | 25% |
| Final verification and handoff | 15% |

Use `etaConfidence` values `low`, `medium`, or `high`. Use `status` values `green`, `yellow`, or `red`.

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

## Artifact Ownership

- Bookkeeper:
- Run directory:
- Parent responsibilities:
- Worker artifact rule: workers return results; they do not edit `.workflow/`.

## Work Packets

| Packet | Owner | Scope | Dependencies | Expected result |
| --- | --- | --- | --- | --- |

## Progress Cadence

- Interval: 10 minutes
- Last progress report:
- Next progress report:
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

## Supervisor Brief Contract

The bookkeeper owns check-in records and returns a supervisor brief. The main thread posts the brief to the user every 10 minutes for long-running workflows and at major phase changes.

```json
{
  "at": "2026-06-08T14:25:30Z",
  "phase": "delegating",
  "percentComplete": 35,
  "eta": "20-40 min",
  "etaConfidence": "medium",
  "done": ["Plan recorded", "Two scouts running"],
  "remaining": ["Integrate scout results", "Run verifier", "Apply fix"],
  "status": "yellow",
  "statusReason": "Waiting on one critical scout result",
  "activePackets": ["001-trace-auth-flow", "002-repro-race"],
  "resources": ["browser:playwright-auth-repro"],
  "next": "Integrate findings after scout results return.",
  "artifactStatus": "current",
  "missing": []
}
```

User-facing form:

```text
35% complete, ETA 20-40 min. Done: plan recorded, two scouts running. Remaining: integrate scout results, run verifier, apply fix. Status: yellow, waiting on one critical scout result.
```

## Resource Ledger

The bookkeeper tracks resource-heavy work in `state.json` as soon as the main thread reports that it is planned or created. The main thread still owns the decision to start, close, release, or hand off resources.

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
