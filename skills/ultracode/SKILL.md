---
name: ultracode
description: "Use when the user asks for ultracode, dynamic workflows, Claude Code /workflows-style orchestration, subagent swarms, parallel agents, multi-agent fan-out, or complex codebase work such as migrations, audits, broad refactors, research-plus-implementation tracks, or high-risk changes that need independent verification."
---

# Ultracode

Run complex work as an explicit workflow: plan, fan out where useful, preserve evidence, integrate deliberately, and verify before handoff. The main thread is the supervisor for user interaction, approvals, worker coordination, progress reports, and final decisions. Workflow artifact bookkeeping belongs to one dedicated `bookkeeper` subagent whenever the host supports subagents.

This skill is host-portable. Use native workflow or subagent tools when the host provides them, but keep the artifact contract stable so the same process works in Codex, Claude Code, Pi-style workflow tools, or a generic skills-compatible agent.

## Mode Selection

Choose the lightest mode that can finish the task well.

| Mode | Use when | Action |
| --- | --- | --- |
| Direct | Small, obvious, one agent can safely finish | Do the work normally; no ultracode ceremony |
| Workflow | Multi-step, needs checkpoints, little parallelism | Start a bookkeeper, execute packets in order, verify |
| Delegated | Independent research, review, implementation, or verification tracks exist | Start a bookkeeper, spawn bounded workers, integrate results |
| Runner | A trusted workflow runner exists and the task is large, repetitive, or long-running | Start a bookkeeper, use the runner after confirming policy, budget, and observability |

Do not escalate just because the word "complex" appears. Escalate when parallel clean-room thinking, independent verification, or explicit artifact state materially reduces risk.

## Main Thread Discipline

Keep the main thread light and available to the user. It should hold the goal, current decision state, approvals, budget/resource decisions, worker lifecycle, compact progress, and final synthesis. It should not load full exploratory context, browse widely, run long investigations, perform broad implementation work, or manually maintain `.workflow/` artifacts when subagents are available.

Default to subagents for workflow work: bookkeeping, discovery, implementation slices, verification, reviews, browser checks, Docker work, and resource-heavy tasks. After the bookkeeper starts, it is the single writer for `.workflow/ultracode/<run-id>/**`. Workers return results to the main thread; the main thread forwards accepted lifecycle events and results to the bookkeeper.

If no subagent primitive exists, use Direct mode for small work or a minimal sequential workflow. In that fallback, keep artifact edits rare and mechanical, and say that the host cannot provide bookkeeper isolation.

## Operating Loop

1. **Preflight the goal**
   - State the goal, success criteria, non-goals, constraints, and known risks.
   - Confirm approval before destructive actions, production changes, large token spend, network-heavy research, credentialed tools, or more than 4 concurrent workers.
   - If the user explicitly asked for subagents or fan-out, bounded delegation is allowed; still ask before expensive or risky fan-out.
   - Treat `.workflow/` as local scratch state. It must be ignored by Git and never staged, committed, or added to version control.
   - Set progress cadence to 10 minutes by default for long-running workflows. Tell the user the cadence and use phase-change updates when useful.

2. **Start the bookkeeper**
   - Spawn one `bookkeeper` subagent before creating packets or writing workflow artifacts.
   - Give it the goal, root, mode, success criteria, non-goals, constraints, approvals, known risks, host capabilities, budget, and expected progress cadence.
   - Restrict its write scope to `.workflow/ultracode/<run-id>/**`. It may create the run directory itself or use `scripts/new-ultracode-run.mjs`; the main thread should not edit the files it owns.
   - If persistent subagents are unavailable, spawn a fresh bookkeeper for each lifecycle update with the run path and latest event. Preserve the single-writer rule.
   - See `references/workflow-contract.md` for the complete artifact schema and supervisor brief contract.

3. **Plan before fanning out**
   - Ask the bookkeeper to record `plan.md`, `orchestration.md`, and initial `state.json`.
   - Keep user-facing decisions, approvals, and budget/resource choices local.
   - The bookkeeper returns a compact supervisor brief with run path, current phase, percent complete, ETA, done, remaining, risk status, and missing artifacts or resources.

4. **Packetize work**
   - Ask the bookkeeper to create one packet file per packet in `packets/`.
   - Each packet must include objective, input context, allowed scope, explicit non-goals, required output, verification request, and risk notes.
   - Use disjoint write scopes for implementation workers.
   - Assign browser, Docker, dev-server, background-process, tmux, temp-dir, and port ownership explicitly.

5. **Delegate or simulate**
   - If native subagent tools exist, use them for packets that can run in parallel.
   - When workers start, finish, block, or close, send the lifecycle event to the bookkeeper.
   - Send worker final outputs to the bookkeeper so it can write normalized `results/` files.
   - If no native subagent tool exists, execute packets one by one as isolated passes and keep raw details out of the main conversation.
   - Do not invent tool names. Capability-detect the host first.
   - See `references/subagent-patterns.md` for prompts, worker roles, and host mappings.

6. **Integrate deliberately**
   - Read every result. Distinguish evidence from opinion.
   - Resolve conflicts against source files, tests, docs, or primary research.
   - Prefer an integrator/synthesizer subagent for bulky result comparison. Keep the main thread to compact summaries and final decisions.
   - Apply changes through assigned worker scopes when possible. Use the parent context only for small glue edits or when it is clearly the safest integration path.
   - Tell the bookkeeper which findings are accepted, rejected, or deferred so it can update `integration.md`.

7. **Verify and close**
   - Run the relevant project gates: tests, lint, typecheck, build, browser checks, docs, or equivalent.
   - Before final handoff, close or explicitly hand off every live browser, Docker container, dev server, background job, tmux pane, temp directory, and port reported by the bookkeeper.
   - Ask the bookkeeper to write `final-report.md` with outcome, files changed, verification evidence, resource cleanup, unresolved risks, and next steps.
   - Run the artifact validator when workflow artifacts exist and the host can access them:
     ```bash
     node <skill-dir>/scripts/verify-ultracode-run.mjs --strict .workflow/ultracode/<run-id>
     ```
   - Parent owns the final answer. The bookkeeper provides evidence and artifact consistency status; it does not decide whether the work is done.

## Progress Reports

For workflows expected to run more than 10 minutes, report progress from the main thread every 10 minutes and at major phase changes. Use the bookkeeper's supervisor brief instead of editing `.workflow/` directly.

Each report should include:

- percent complete as a coarse estimate
- ETA as a range with confidence when possible
- done
- remaining
- status: `green`, `yellow`, or `red`, with one reason

Example:

```text
74% complete, ETA 35-60 min. Done: suspend API/CLI, state primitives, runtime primitives. Remaining: review fixes, lazy restore, final verification. Status: yellow, correctness fix in progress.
```

Do not wait until the end to report that the workflow drifted, blocked, or accumulated resources.

## Capability Detection

Check the host before choosing mechanics:

- **Codex with subagent tools**: use `spawn_agent` for bounded packets, keep the immediate blocker local, and `wait_agent` only when the result is needed.
- **Claude Code with native workflows**: if the user wants native `/workflows`, use that surface; otherwise run this artifact-based workflow with Task/subagent tools when available.
- **Pi/Open Dynamic Workflow-style tools**: use runner scripts only when installed and trusted. Keep worker policy explicit: scope, budget, read/write access, network, and secret handling.
- **Generic skills CLI or no subagents**: use Direct mode where possible. For larger work, use minimal sequential packet mode and keep artifact edits mechanical because bookkeeper isolation is unavailable.

## Risk And Cost Rules

Read `references/risk-and-cost-gates.md` when the task touches production, secrets, destructive operations, external APIs, broad file edits, dependency changes, or expensive parallelism.

Default budgets:

- 2-3 workers for normal delegated work.
- 4 workers for broad research or review.
- More than 4 workers only with explicit user approval and clear packet boundaries.

## References

- `references/workflow-contract.md` - run directory schema, state file, packet templates, result templates, and final report format.
- `references/subagent-patterns.md` - bookkeeper contract, decomposition patterns, worker prompts, host-specific mappings, and conflict handling.
- `references/risk-and-cost-gates.md` - approval gates, safety constraints, cost controls, and verification standards.

## Scripts

- `scripts/new-ultracode-run.mjs` - optional helper that creates `.workflow/ultracode/<run-id>/` with required files.
- `scripts/verify-ultracode-run.mjs` - optional diagnostic that validates expected artifacts before handoff.

Do not use `git add .workflow`, `git add -f .workflow`, or include workflow artifacts in commits or PRs.
