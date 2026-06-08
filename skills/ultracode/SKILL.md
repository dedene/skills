---
name: ultracode
description: "Use when the user asks for ultracode, dynamic workflows, Claude Code /workflows-style orchestration, subagent swarms, parallel agents, multi-agent fan-out, or complex codebase work such as migrations, audits, broad refactors, research-plus-implementation tracks, or high-risk changes that need independent verification."
---

# Ultracode

Run complex work as an explicit workflow: plan, fan out where useful, preserve evidence, integrate deliberately, and verify before handoff. The main thread is the control plane for user interaction, approvals, check-ins, and final synthesis; workflow execution belongs in bounded subagents whenever the host supports them.

This skill is host-portable. Use native workflow or subagent tools when the host provides them, but keep the artifact contract stable so the same process works in Codex, Claude Code, Pi-style workflow tools, or a generic skills-compatible agent.

## Mode Selection

Choose the lightest mode that can finish the task well.

| Mode | Use when | Action |
| --- | --- | --- |
| Direct | Small, obvious, one agent can safely finish | Do the work normally; no ultracode ceremony |
| Workflow | Multi-step, needs checkpoints, little parallelism | Create a run directory, packetize the work, execute in order, verify |
| Delegated | Independent research, review, implementation, or verification tracks exist | Create packets, spawn bounded subagents, integrate results |
| Runner | A trusted workflow runner exists and the task is large, repetitive, or long-running | Use the runner after confirming policy, budget, and observability |

Do not escalate just because the word "complex" appears. Escalate when parallel clean-room thinking, independent verification, or explicit artifact state materially reduces risk.

## Main Thread Discipline

Keep the main thread light and available to the user. It should hold the goal, decision log, current phase, approvals, check-in cadence, resource ledger, and compact result summaries. It should not load full exploratory context, browse widely, run long investigations, or perform broad implementation work when subagents are available.

Default to subagents for workflow work: discovery, implementation slices, verification, reviews, browser checks, Docker work, and resource-heavy tasks. If no subagent primitive exists, use sequential packet mode and keep raw details in artifacts instead of the main conversation.

## Operating Loop

1. **Preflight the goal**
   - State the goal, success criteria, non-goals, constraints, and known risks.
   - Confirm approval before destructive actions, production changes, large token spend, network-heavy research, credentialed tools, or more than 4 concurrent workers.
   - If the user explicitly asked for subagents or fan-out, bounded delegation is allowed; still ask before expensive or risky fan-out.
   - Treat `.workflow/` as local scratch state. It must be ignored by Git and never staged, committed, or added to version control.
   - Set check-in cadence to 10 minutes by default for long-running workflows. Tell the user the cadence and use phase-change updates when useful.

2. **Create the workflow run**
   - Prefer the scaffolder:
     ```bash
     python3 <skill-dir>/scripts/new-ultracode-run.py "short task title" --root .
     ```
   - The scaffolder adds `.workflow/` to local Git exclude when possible. If scripts are unavailable, ensure `.workflow/` is ignored before creating the same structure manually under `.workflow/ultracode/<timestamp>-<slug>/`.
   - See `references/workflow-contract.md` for the complete artifact schema.

3. **Plan before fanning out**
   - Write `plan.md` with success criteria and verification gates.
   - Write `orchestration.md` with mode, worker count, dependencies, packet ownership, and stop conditions.
   - Record the check-in cadence and expected resource use.
   - Keep user-facing decisions, approvals, and check-ins local. Delegate execution packets, including critical-path work, whenever subagents are available.

4. **Packetize work**
   - Create one file per packet in `packets/`.
   - Each packet must include objective, input context, allowed scope, explicit non-goals, required output, verification request, and risk notes.
   - Use disjoint write scopes for implementation workers.
   - Assign browser, Docker, dev-server, background-process, tmux, temp-dir, and port ownership explicitly.

5. **Delegate or simulate**
   - If native subagent tools exist, use them for packets that can run in parallel.
   - If no native subagent tool exists, execute packets one by one as isolated passes and still write `results/` files.
   - Do not invent tool names. Capability-detect the host first.
   - See `references/subagent-patterns.md` for prompts, worker roles, and host mappings.

6. **Integrate deliberately**
   - Read every result. Distinguish evidence from opinion.
   - Resolve conflicts against source files, tests, docs, or primary research.
   - Prefer an integrator/synthesizer subagent for bulky result comparison. Keep the main thread to compact summaries and final decisions.
   - Apply changes through assigned worker scopes when possible. Use the parent context only for small glue edits or when it is clearly the safest integration path.
   - Record accepted, rejected, and follow-up items in `integration.md`.

7. **Verify and close**
   - Run the relevant project gates: tests, lint, typecheck, build, browser checks, docs, or equivalent.
   - Before final handoff, close or explicitly hand off every live browser, Docker container, dev server, background job, tmux pane, temp directory, and port recorded in `state.json`.
   - Run the artifact validator:
     ```bash
     python3 <skill-dir>/scripts/verify-ultracode-run.py --strict .workflow/ultracode/<run-id>
     ```
   - Write `final-report.md` with outcome, files changed, verification evidence, resource cleanup, unresolved risks, and next steps.

## Check-Ins

For workflows expected to run more than 10 minutes, check in from the main thread every 10 minutes and at major phase changes. Keep updates short:

- current phase and active packets
- what workers are doing now
- latest evidence or meaningful progress
- resource status: browsers, containers, servers, jobs, ports
- next checkpoint or blocker

Do not wait until the end to report that the workflow drifted, blocked, or accumulated resources.

## Capability Detection

Check the host before choosing mechanics:

- **Codex with subagent tools**: use `spawn_agent` for bounded packets, keep the immediate blocker local, and `wait_agent` only when the result is needed.
- **Claude Code with native workflows**: if the user wants native `/workflows`, use that surface; otherwise run this artifact-based workflow with Task/subagent tools when available.
- **Pi/Open Dynamic Workflow-style tools**: use runner scripts only when installed and trusted. Keep worker policy explicit: scope, budget, read/write access, network, and secret handling.
- **Generic skills CLI or no subagents**: use packet mode. The workflow is still valuable because it preserves planning, evidence, integration, and verification.

## Risk And Cost Rules

Read `references/risk-and-cost-gates.md` when the task touches production, secrets, destructive operations, external APIs, broad file edits, dependency changes, or expensive parallelism.

Default budgets:

- 2-3 workers for normal delegated work.
- 4 workers for broad research or review.
- More than 4 workers only with explicit user approval and clear packet boundaries.

## References

- `references/workflow-contract.md` - run directory schema, state file, packet templates, result templates, and final report format.
- `references/subagent-patterns.md` - decomposition patterns, worker prompts, host-specific mappings, and conflict handling.
- `references/risk-and-cost-gates.md` - approval gates, safety constraints, cost controls, and verification standards.

## Scripts

- `scripts/new-ultracode-run.py` - creates `.workflow/ultracode/<run-id>/` with required files.
- `scripts/verify-ultracode-run.py` - validates that the run has the expected artifacts before handoff.

Do not use `git add .workflow`, `git add -f .workflow`, or include workflow artifacts in commits or PRs.
