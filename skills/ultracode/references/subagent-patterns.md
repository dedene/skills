# Ultracode Subagent Patterns

## Table Of Contents

- Delegation rules
- Main thread boundary
- Worker roles
- Bookkeeper contract
- Prompt template
- Host mappings
- Conflict handling
- Anti-patterns

## Delegation Rules

Delegate work that is independent, bounded, and useful even if it returns imperfectly.

Keep local:

- User interaction, approvals, budget/resource decisions, user-facing progress reports, and final synthesis.
- Compact summaries needed to decide the next packet.
- Sensitive credentialed actions unless the user explicitly approves the exact tool use.

Delegate:

- Workflow artifact bookkeeping to one dedicated `bookkeeper` subagent.
- Independent codebase reconnaissance.
- Competing design proposals.
- Focused implementation slices with disjoint write scopes.
- Security, accessibility, or performance reviews.
- Test failure triage when logs and commands are self-contained.
- Post-change verification while the parent continues non-overlapping work.
- Browser, Docker, dev-server, long-running process, and other resource-heavy work.

## Main Thread Boundary

The main thread should preserve context for interaction with the user. Do not make it the place where raw research, long logs, broad browsing, or repeated test output accumulates. Put workflow detail into packet files, result files, or subagent final outputs.

When the host supports subagents, the main thread should supervise rather than execute: start the bookkeeper, spawn workers, report lifecycle events to the bookkeeper, resolve approvals, post progress reports, and synthesize compact results. If a task would fill the main context with details the user does not need to see, it should usually become a packet or a bookkeeper update.

Do not let multiple actors maintain `.workflow/`. After the bookkeeper starts, the parent and workers treat workflow artifacts as bookkeeper-owned.

## Worker Roles

Use these role labels in packet names when helpful:

- `bookkeeper`: maintain `.workflow/` artifacts and return compact supervisor briefs.
- `scout`: gather facts, source paths, call graphs, prior art.
- `planner`: propose decomposition or risk model.
- `worker`: make a bounded code/doc change in a disjoint write scope.
- `reviewer`: inspect changed code or artifacts for regressions.
- `security`: look for secrets, auth, data exposure, injection, or permission issues.
- `verifier`: run commands, browser checks, or reproduction steps.
- `synthesizer`: compare results and produce a compact decision memo.

## Bookkeeper Contract

Start one `bookkeeper` before writing workflow artifacts. Give it:

- Goal, root, mode, success criteria, non-goals, constraints, approvals, known risks, and host capabilities.
- Packet requests: title, role, read/write scope, dependencies, expected output, and risk notes.
- Worker lifecycle events: requested, spawned, running, complete, blocked, closed.
- Worker final outputs and verification results after the parent has reviewed them for obvious scope issues.
- Accepted, rejected, deferred, and follow-up decisions from the parent.
- Resource events: planned, active, idle, closed, released, stopped, removed, cleaned, leaked, or handed-off.

Allowed writes:

- `.workflow/ultracode/<run-id>/**` only.

Forbidden:

- Source edits, dependency changes, git staging, commits, `.gitignore` edits, destructive commands, credentialed tools, and product/safety/completion decisions.

After each update, the bookkeeper returns:

- Run directory.
- Current phase.
- Percent complete as a coarse estimate.
- ETA range and confidence.
- Done.
- Remaining.
- `green | yellow | red` status with one reason.
- Artifact consistency status.
- Missing packets, results, resources, or verification evidence.

If the host cannot keep a persistent bookkeeper alive, spawn a fresh bookkeeper with the run path and latest event. Do not compensate by having the parent manually edit `state.json` unless no subagent primitive exists.

## Prompt Template

### Bookkeeper

```text
You are the Ultracode bookkeeper.

Own the workflow artifacts under: <run-dir or requested root>
Allowed writes: .workflow/ultracode/<run-id>/** only.
Forbidden: source edits, dependency changes, git staging, commits, .gitignore edits, destructive commands, credentialed tools, and product/safety/completion decisions.

Record the parent-provided goal, constraints, packet requests, worker lifecycle events, accepted decisions, verification results, and resource changes.
Maintain plan.md, orchestration.md, state.json, packets/, results/, integration.md, and final-report.md as needed.

After each update, return a concise supervisor brief:
- run directory
- phase
- percent complete
- ETA and confidence
- done
- remaining
- green/yellow/red status with one reason
- artifact consistency status
- missing results, resources, or verification evidence

Progress percent is an estimate from phase maturity and accepted evidence, not packet count alone.
Do not make product, safety, or completion decisions. Record the parent's decisions.
```

### Packet Worker

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
- Spawn the bookkeeper first for workflow artifact maintenance when the task uses Workflow, Delegated, or Runner mode.
- Spawn concrete sidecar packets, then keep working locally on non-overlapping tasks.
- Use the parent thread for user-facing progress and coordination; use the bookkeeper for artifact updates and workers for workflow execution whenever possible.
- Do not set a different model unless the user asked or the packet clearly needs it.
- Wait for workers only when their result is needed to proceed.
- Close workers that are no longer needed.

### Claude Code

- If native `/workflows` is available and the user explicitly wants that surface, use it for large runner-style tasks.
- Native workflow scripts are JavaScript orchestration files. Reflect the same shape in Ultracode artifacts: named metadata, phases, logs, bounded agent calls, `parallel`/`pipeline` batches, structured outputs, and compact final returns.
- Have the bookkeeper mirror native workflow run identifiers and artifact paths into the portable Ultracode `state.json` when available; accepted outputs still belong in `results/`, `integration.md`, and `final-report.md`.
- If using Task/subagent tools, pass the packet file and run directory. Keep worker prompts short and bounded.
- Do not depend on Claude-only artifacts when the user wants the workflow reusable in Codex or other agents.

### Pi / Open Dynamic Workflow Style

- Use JavaScript workflow runners only when installed, trusted, and appropriate for scale.
- Keep policy outside worker prompts when possible: read/write scope, network, max workers, max tokens, and timeout.
- Persist worker outputs into the same `results/` contract so integration stays host-agnostic.

### Generic Skills CLI

- If no subagent primitive exists, prefer Direct mode for small tasks.
- For larger tasks, run packet mode sequentially and keep artifact edits mechanical because bookkeeper isolation is unavailable.
- Preserve isolation by clearing assumptions between packets: reread only the packet and cited artifacts, then produce a result.

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
- Letting parent, workers, and bookkeeper all edit `.workflow/`.
- Treating the bookkeeper as a decision-maker instead of a recorder.
- Letting resource-heavy workers return without resource status and cleanup notes.
- Assigning overlapping write scopes.
- Treating worker output as truth without checking evidence.
- Running many workers to avoid making a decision.
- Skipping final verification because workers reported success.
