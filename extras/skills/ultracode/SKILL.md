---
name: ultracode
description: "Use when the user asks for ultracode, dynamic workflows, Claude Code /workflows-style orchestration, subagent swarms, parallel agents, multi-agent fan-out, broad migrations, codebase-wide audits, high-risk plans, or complex work that needs independent verification."
---

# Ultracode

Ultracode is the Codex approximation of Claude Code dynamic workflows. It should feel like a workflow run, not like a longer chat: define phases, fan out bounded agents where useful, keep intermediate state outside the main conversation, show progress visibly, reduce and cross-check results, then return one coordinated answer.

Mimic the functional shape of dynamic workflows:

- A run has a goal, phase graph, worker budget, write scopes, approval envelope, and verification gate.
- The main thread stays responsive and user-facing.
- Intermediate state lives in a run ledger, not in the conversation.
- Agents work from bounded packets and return structured results.
- Results are checked before integration.
- Progress is visible as phases, agents, elapsed time, resources, and status.
- Completed work can be resumed or audited when durable artifacts exist.

Do not mimic dynamic workflows by adding ceremony to small work. If a normal Codex pass is faster and safer, use Direct mode and say why.

## Dynamic Workflow Semantics

Claude Code dynamic workflows move orchestration into a script and show it through `/workflows`: phases, agent counts, token/tool usage, elapsed time, pause/resume/stop/restart controls, drill-down into agents, and optional saved commands.

Codex does not have that native runner unless a concrete runner tool is present. In Codex, Ultracode emulates the behavior with:

- a phase plan and approval card in the main thread
- `multi_agent_v1.spawn_agent` workers when available and the user has opted into workflow/subagent work
- `multi_tool_use.parallel` for independent local reads and command checks
- `update_plan` as the live task panel
- `.workflow/ultracode/<run-id>/` as the durable run ledger when resumability or auditability is worth the cost
- concise progress tables in the main thread

Never pretend the main thread is multiple agents. If no real worker primitive exists, use Direct or Thin mode rather than roleplaying a workflow.

## Mode Selection

Choose the lightest mode that preserves the workflow value.

| Mode | Use when | Mechanics |
| --- | --- | --- |
| Direct | Small or tightly coupled work; one agent can finish faster than orchestration | No run ledger, no bookkeeper, normal implementation and verification |
| Thin Workflow | Multi-step work benefits from visible phases, but durable artifacts would slow it down | `update_plan`, main-thread progress table, optional sidecar workers, no `.workflow/` unless the run grows |
| Durable Workflow | User asked for ultracode/workflow, or the task needs resumability, auditability, multi-agent reduction, or cross-checking | Create `.workflow/ultracode/<run-id>/`, phase ledger, packets/results, progress dashboard, final report |
| Runner Workflow | A trusted workflow runner exists and the task is large, repeatable, or long-running | Use the runner after approval; mirror its state into the Ultracode ledger |

Escalate into Durable Workflow when any of these are true:

- explicit request: `ultracode`, `workflow`, `dynamic workflow`, subagent swarm, or broad fan-out
- 3+ independent workstreams with useful parallelism
- codebase-wide migration, audit, or review
- work may run past 15 minutes or resume after interruption
- findings need independent reviewers or adversarial verification
- user needs a reusable workflow command or audit trail

Stay Direct or Thin when:

- the next step is an immediate blocker the parent can do faster
- workers would read the same files for the same question
- artifacts would not reduce risk or preserve useful state
- the task is mostly one edit loop with one verification gate

## Initial Approval Card

Before a Durable or Runner workflow starts, show a compact run card and ask only for the meaningful approval. Do not ask again for routine worker events inside the approved envelope.

```text
Ultracode run: react-to-solid-migration
Goal: Non-destructive React to Solid.js port of Excalidraw into solid-migration/
Mode: Durable Workflow
Budget: 4 concurrent agents, 16 total agents, 45 min first pass
Writes: solid-migration/** only
Network: off
Verification: typecheck, tests, migration report

| Phase | Purpose | Agents | Output |
| --- | --- | ---: | --- |
| 1 Inventory | Map files and dependencies | 4 | source map |
| 2 Patterns | Identify migration patterns | 4 | pattern guide |
| 3 Infrastructure | Create Solid shell and tooling | 3 | buildable app |
| 4 Core Port | Port shared logic | 3 | changed files + tests |
| 5 App Port | Port UI flows | 1 | changed files + tests |
| 6 Verify | Run checks and review | 1 | final report |
```

Ask before starting if the workflow exceeds the default budget, uses credentials, writes outside the repo, adds dependencies, starts long-running resources, or uses network-heavy research.

## Progress Surface

For Dynamic Workflow mode, keep a visible status surface in the main thread. Use a Markdown table in normal chat; use a compact text table if Markdown would wrap badly.

Recommended main-thread update:

```text
Ultracode: react-to-solid-migration
10/16 agents complete | elapsed 5m30s | status yellow: infra fix in progress

| Phase | State | Agents | Elapsed | Evidence | Next |
| --- | --- | ---: | ---: | --- | --- |
| Inventory | done | 4/4 | 1m20s | results/001-* | accepted |
| Pattern Analysis | done | 4/4 | 2m45s | results/002-* | accepted |
| Infrastructure | running | 2/3 | 5m30s | 2 files changed | finish tooling |
| Migrate Core | pending | 0/3 | - | - | after infra |
```

Agent drill-down, when useful:

```text
| Agent | Phase | State | Scope | Tools | Result |
| --- | --- | --- | --- | ---: | --- |
| infra:package.json | Infrastructure | done | package.json | 9 | scripts updated |
| infra:vite.config.ts | Infrastructure | running | vite.config.ts | 8 | checking aliases |
| infra:setupTests.ts | Infrastructure | blocked | test setup | 5 | needs jsdom choice |
```

Rules:

- Report phase changes immediately.
- For workflows expected to run over 10 minutes, report at least every 10 minutes.
- Show counts only when they are known. Use `unknown` instead of inventing tokens or tool counts.
- Include active resources and cleanup status when browsers, servers, containers, ports, tmux panes, or watchers are involved.
- Do not flood the user with every packet result. Surface decisions, blockers, and verified progress.

## Codex Execution Loop

1. **Preflight and capability detection**
   - State goal, success criteria, non-goals, constraints, risks, expected verification, and default budget.
   - Check whether `multi_agent_v1.spawn_agent`, `wait_agent`, `send_input`, and `close_agent` are available before promising agent orchestration.
   - Use `tool_search` only when the tools are not already visible.
   - If no real subagent tool exists, do not simulate workers. Use Direct, Thin, or Runner if an external runner exists.

2. **Draft the phase graph**
   - Define phases as data: id, name, objective, dependencies, max agents, read scope, write scope, expected output, verification.
   - Keep phase count small. Most runs need 3-6 phases.
   - Split implementation by disjoint write scopes. Split research by distinct questions.
   - Keep the immediate critical-path blocker local unless a worker can progress without blocking the parent.

3. **Create the run ledger for Durable/Runner**
   - Create `.workflow/ultracode/<run-id>/` with `workflow.md`, `state.json`, `journal.md`, `packets/`, `results/`, `integration.md`, and `final-report.md`.
   - Add `.workflow/` to local Git exclude, not tracked `.gitignore`, unless the user explicitly wants the ignore rule committed.
   - The ledger is scratch state. Never stage, commit, or publish it.

4. **Get approval once**
   - Show the approval card with phases, worker budget, write scopes, network/resource policy, and verification gates.
   - Approval covers routine worker lifecycle events inside that envelope.
   - Ask again only if the run exceeds the envelope or discovers materially higher risk.

5. **Run phases dynamically**
   - Spawn sidecar agents for independent packets only.
   - Use `multi_tool_use.parallel` for independent file reads and safe local commands.
   - Use background `exec_command` sessions for long-running commands only when the user approved the resource.
   - Wait for workers only when their result is needed for the next critical-path decision.
   - Close completed workers after their result is reviewed.
   - Update `state.json` and `journal.md` at phase boundaries, blockers, integrations, verification results, and resource changes. Avoid per-tool-call bookkeeping.

6. **Reduce and cross-check**
   - Read every worker result before accepting it.
   - Distinguish evidence from opinion.
   - Resolve conflicts against source files, tests, logs, docs, or primary research.
   - For high-risk findings, assign at least one independent reviewer or verifier before reporting it as true.
   - Record accepted, rejected, deferred, and follow-up decisions in `integration.md`.

7. **Integrate and verify**
   - Apply edits through disjoint worker scopes when possible.
   - Parent may make small glue edits or integration fixes when that is safer than another worker round.
   - Run the relevant project gates: tests, lint, typecheck, build, browser checks, docs, or equivalent.
   - Clean up or explicitly hand off every resource.
   - Write `final-report.md` and run the artifact validator when a ledger exists.

## Worker Budget

Defaults for Codex:

- 1-2 sidecar agents for focused investigation or verification.
- 2-4 sidecar agents for normal Durable Workflow phases.
- Ask before more than 4 concurrent agents.
- Ask before more than 16 total agents in a Codex run.
- Ask before more than 15 minutes unattended, credentialed connectors, new dependencies, network-heavy research, or a second live resource of the same type.

Claude Code may support much larger workflow runs, but Codex should start smaller because the parent still owns coordination and user-facing output.

## Artifact Budget

Use artifacts because they preserve state, not because the skill says "workflow."

| Level | Files | Use when |
| --- | --- | --- |
| None | none | Direct mode |
| Thin | `update_plan` only | visible progress is enough |
| Durable | `workflow.md`, `state.json`, `journal.md`, `packets/`, `results/`, `integration.md`, `final-report.md` | resumability, audit trail, multi-agent reduction |
| Runner Mirror | Durable files plus runner script/path/snapshot metadata | external runner or native workflow exists |

In Durable mode, update artifacts at meaningful lifecycle points only:

- run created
- phase started/completed/blocked
- worker spawned/completed/blocked/closed
- integration decision made
- verification completed
- resource created/closed/handed off
- run completed/blocked/cancelled

Avoid bookkeeping every command, file read, or intermediate thought.

## Resume Protocol

When resuming an Ultracode run:

1. Find the latest incomplete `.workflow/ultracode/*/state.json`.
2. Read `workflow.md`, `state.json`, `journal.md`, `integration.md`, latest `results/`, and resource ledger.
3. Verify reality: `git status`, relevant process/session checks, live browser/server/container state when applicable.
4. Mark stale resources as closed, leaked, or unknown.
5. Continue from the next unblocked phase or collapse to Direct mode if the ledger is stale and no longer useful.
6. Tell the user what was resumed, what was already complete, and what evidence was rechecked.

## Bookkeeper Policy

A bookkeeper is optional in Codex and only useful when it is a real independent worker that can maintain Durable artifacts while the parent continues execution.

Use a bookkeeper when:

- the run has 4+ packets or multiple active phases
- artifact updates would distract the parent from critical-path work
- a persistent worker can own `.workflow/ultracode/<run-id>/**`

Do not use a bookkeeper when:

- no real subagent tool exists
- the host cannot keep worker context alive and would require fresh bookkeepers for routine events
- artifact maintenance costs more than it preserves

If no bookkeeper is used, the parent owns compact artifact updates at phase boundaries. Workers never edit `.workflow/` unless the packet explicitly assigns bookkeeper responsibility.

## Evidence Standards

Every accepted result should include at least one of:

- file paths and line references
- command and output summary
- test failure or pass evidence
- source URL for external research
- screenshot path or browser observation
- changed files list
- resource cleanup status

Do not accept:

- "looks good" with no evidence
- current factual claims without source checks
- security conclusions without reviewed surfaces
- verification claims without command names or observed results
- resource-heavy packet results without cleanup status

## Stop Conditions

Stop and ask when:

- the goal changes materially
- the run exceeds the approved worker, time, network, or resource budget
- workers uncover higher risk than the approval card covered
- required credentials or production authority are missing
- results conflict and cannot be resolved from evidence
- verification is blocked by environment, unrelated failures, or external outage
- resource usage is stacking up and ownership is unclear

## Host Mappings

Read `references/subagent-patterns.md` for packet prompts and role details.

- **Codex with `multi_agent_v1`**: use `spawn_agent` for bounded sidecars after user opt-in; use `wait_agent` sparingly; use `close_agent` after review; keep critical path local.
- **Codex without subagents**: Direct or Thin mode; no fake worker personas.
- **Claude Code with native workflows**: use native `/workflows` when the user wants that surface; mirror durable run facts only if cross-host portability matters.
- **External runner**: use only after detecting a named trusted executable and getting approval for policy, budget, and observability.

## References

- `references/workflow-contract.md` - durable ledger schema, state file, dashboard templates, packet/result templates, and final report format.
- `references/subagent-patterns.md` - Codex subagent prompts, dynamic phase patterns, bookkeeper rules, and conflict handling.
- `references/risk-and-cost-gates.md` - approval gates, budgets, safety constraints, resource cleanup, and verification standards.

## Scripts

- `scripts/new-ultracode-run.mjs` - optional helper that creates `.workflow/ultracode/<run-id>/`.
- `scripts/verify-ultracode-run.mjs` - validates expected artifacts before handoff.

Do not use `git add .workflow`, `git add -f .workflow`, or include workflow artifacts in commits or PRs.
