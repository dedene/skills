# Ultracode Subagent Patterns

## Table Of Contents

- Delegation rules
- Main thread boundary
- Worker roles
- Prompt template
- Host mappings
- Conflict handling
- Anti-patterns

## Delegation Rules

Delegate work that is independent, bounded, and useful even if it returns imperfectly.

Keep local:

- User interaction, approvals, check-ins, budget/resource decisions, and final synthesis.
- Compact summaries needed to decide the next packet.
- Sensitive credentialed actions unless the user explicitly approves the exact tool use.

Delegate:

- Independent codebase reconnaissance.
- Competing design proposals.
- Focused implementation slices with disjoint write scopes.
- Security, accessibility, or performance reviews.
- Test failure triage when logs and commands are self-contained.
- Post-change verification while the parent continues non-overlapping work.
- Browser, Docker, dev-server, long-running process, and other resource-heavy work.

## Main Thread Boundary

The main thread should preserve context for interaction with the user. Do not make it the place where raw research, long logs, broad browsing, or repeated test output accumulates. Put workflow detail into packet files, result files, or subagent final outputs.

When the host supports subagents, the main thread should coordinate rather than execute: create packets, spawn workers, track resources, post check-ins, resolve approvals, and synthesize compact results. If a task would fill the main context with details the user does not need to see, it should usually become a packet.

## Worker Roles

Use these role labels in packet names when helpful:

- `scout`: gather facts, source paths, call graphs, prior art.
- `planner`: propose decomposition or risk model.
- `worker`: make a bounded code/doc change in a disjoint write scope.
- `reviewer`: inspect changed code or artifacts for regressions.
- `security`: look for secrets, auth, data exposure, injection, or permission issues.
- `verifier`: run commands, browser checks, or reproduction steps.
- `synthesizer`: compare results and produce a compact decision memo.

## Prompt Template

```text
You are working on one Ultracode packet.

Run directory: <path>
Packet file: <path>

Read the packet first. Stay inside its allowed scope. Do not revert unrelated changes.
If editing code, touch only the allowed write paths and list every changed file.
Track any browser, Docker container, dev server, background process, tmux pane, temp directory, or port you open. Close it before returning unless the packet says to hand it off.
Return a concise result using the Result template. Include evidence and verification.
If blocked, say exactly what is missing.
```

For read-only packets, add:

```text
Do not modify files. Write no artifacts except your final result.
```

For implementation packets, add:

```text
You may edit files only in the packet's write scope. Add or update focused tests when practical.
```

For resource-heavy packets, add:

```text
Record every resource you start, including type, purpose, identifier, and cleanup action. Do not leave browsers, containers, servers, watchers, tmux panes, or ports running unless explicitly instructed.
```

## Host Mappings

### Codex

- Use native `spawn_agent` only when available and the user asked for subagents, delegation, or parallel work.
- Spawn concrete sidecar packets, then keep working locally on non-overlapping tasks.
- Use the parent thread for user check-ins and coordination; use workers for workflow execution whenever possible.
- Do not set a different model unless the user asked or the packet clearly needs it.
- Wait for workers only when their result is needed to proceed.
- Close workers that are no longer needed.

### Claude Code

- If native `/workflows` is available and the user explicitly wants that surface, use it for large runner-style tasks.
- Native workflow scripts are JavaScript orchestration files. Reflect the same shape in Ultracode artifacts: named metadata, phases, logs, bounded agent calls, `parallel`/`pipeline` batches, structured outputs, and compact final returns.
- Mirror native workflow run identifiers and artifact paths into the portable Ultracode `state.json` when available; accepted outputs still belong in `results/`, `integration.md`, and `final-report.md`.
- If using Task/subagent tools, pass the packet file and run directory. Keep worker prompts short and bounded.
- Do not depend on Claude-only artifacts when the user wants the workflow reusable in Codex or other agents.

### Pi / Open Dynamic Workflow Style

- Use JavaScript workflow runners only when installed, trusted, and appropriate for scale.
- Keep policy outside worker prompts when possible: read/write scope, network, max workers, max tokens, and timeout.
- Persist worker outputs into the same `results/` contract so integration stays host-agnostic.

### Generic Skills CLI

- If no subagent primitive exists, run packet mode sequentially.
- Preserve isolation by clearing assumptions between packets: reread only the packet and cited artifacts, then write a result.

## Conflict Handling

When workers disagree:

1. Identify the claim, not the person or worker role.
2. Check primary evidence: source files, tests, docs, logs, official references.
3. Prefer reproducible verification over plausibility.
4. Record the accepted and rejected claims in `integration.md`.
5. Spawn a verifier only if the conflict materially affects the outcome and can be tested independently.

## Anti-Patterns

- Spawning workers before writing success criteria.
- Giving every worker the full conversation when a packet would do.
- Doing broad workflow execution in the main thread when subagents are available.
- Letting resource-heavy workers return without resource status and cleanup notes.
- Assigning overlapping write scopes.
- Treating worker output as truth without checking evidence.
- Running many workers to avoid making a decision.
- Skipping final verification because workers reported success.
