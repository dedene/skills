# Ultracode Subagent Patterns

Use subagents to make a workflow faster or more reliable. Do not use them to create the appearance of a workflow.

## Delegation Rules

Delegate work that is independent, bounded, and useful even if it returns imperfectly.

Keep local:

- user interaction, approvals, budget/resource decisions, and final synthesis
- the immediate critical-path blocker
- small glue edits where context switching would cost more than the edit
- sensitive credentialed actions unless the user explicitly approves the exact tool use
- final decision-making about accepted results and completion

Delegate:

- independent codebase reconnaissance
- distinct research questions
- implementation slices with disjoint write scopes
- focused review, security, accessibility, or performance checks
- verification that can run while the parent does non-overlapping work
- browser, Docker, dev-server, simulator, or long-running process work when approved
- durable artifact bookkeeping when a real worker can own it without slowing the run

Do not delegate two workers to answer the same question from the same files unless the goal is adversarial cross-checking.

## Codex Tool Mapping

When `multi_agent_v1` is available:

- `spawn_agent`: start a bounded sidecar after the user has opted into workflow, subagent, delegation, or parallel agent work.
- `wait_agent`: wait only when the next parent decision is blocked on that result. Prefer long waits over busy polling.
- `send_input`: reuse an existing agent only when the follow-up depends on that agent's context.
- `close_agent`: close completed or abandoned agents after reviewing their results.

Do not set a model override unless the user asked or the packet has a clear model-specific reason.

When `multi_agent_v1` is not available:

- do not simulate workers with personas in the main thread
- use Direct or Thin mode
- use `multi_tool_use.parallel` for independent file reads and safe local commands
- use background `exec_command` sessions only for approved long-running work

## Dynamic Phase Patterns

### Map -> Reduce -> Verify

Use for audits, migrations, and broad reviews.

1. Map: independent scouts inspect disjoint areas or questions.
2. Reduce: parent or synthesizer groups evidence, removes duplicates, and identifies conflicts.
3. Verify: independent reviewers test high-risk findings before integration.

### Pipeline

Use when phases depend on each other.

1. Discovery defines constraints and target files.
2. Implementation workers edit disjoint scopes.
3. Integration resolves conflicts and glue.
4. Verification runs project gates.

### Tournament

Use for high-risk plans or ambiguous architecture.

1. Several planners propose approaches independently.
2. A reviewer challenges assumptions and failure modes.
3. Parent chooses one plan and records rejected alternatives.

### Fix Loop

Use after a build or test gate fails.

1. Parent captures exact failure output.
2. One worker fixes the narrow failure scope.
3. A separate verifier reruns the gate if it can run in parallel with parent cleanup.
4. Repeat until the gate passes or a blocker is real.

## Worker Roles

Use role labels in packet names and progress tables when helpful:

- `bookkeeper`: maintain Durable Workflow artifacts and return compact dashboard updates
- `scout`: gather facts, file paths, call graphs, and prior art
- `planner`: propose a decomposition, phase graph, or risk model
- `worker`: make a bounded code/doc change in a disjoint write scope
- `reviewer`: inspect changed code or artifacts for regressions
- `security`: inspect auth, data exposure, injection, secrets, and permissions
- `verifier`: run commands, browser checks, or reproduction steps
- `synthesizer`: compare results and produce a compact decision memo

## Bookkeeper Contract

A bookkeeper is optional in Codex. Use one only when a real independent worker can keep artifacts current while the parent continues execution.

Give the bookkeeper:

- run directory
- goal, success criteria, non-goals, constraints, known risks
- approval envelope: worker budget, write scopes, network/resource policy, verification gates
- phase graph
- packet requests
- worker lifecycle events
- accepted/rejected/deferred decisions
- verification and resource events

Allowed writes:

- `.workflow/ultracode/<run-id>/**` only

Forbidden:

- source edits
- dependency changes
- git staging or commits
- `.gitignore` edits
- destructive commands
- credentialed tools
- product, safety, budget, or completion decisions

After each meaningful update, the bookkeeper returns:

- run directory
- phase
- percent complete
- ETA and confidence
- done
- remaining
- `green | yellow | red` status with one reason
- active agents and resources
- missing results, resource cleanup, or verification evidence

Do not use a bookkeeper for every lifecycle event if the host cannot keep that worker alive. The parent can update `state.json` and `journal.md` at phase boundaries instead.

## Prompt Templates

### Bookkeeper

```text
You are the Ultracode bookkeeper.

Own the workflow artifacts under: <run-dir>
Allowed writes: .workflow/ultracode/<run-id>/** only.
Forbidden: source edits, dependency changes, git staging, commits, .gitignore edits, destructive commands, credentialed tools, and product/safety/completion decisions.

Record only parent-provided facts: goal, approval envelope, phase graph, packet requests, worker lifecycle events, accepted decisions, verification results, and resource changes.
Maintain workflow.md, state.json, journal.md, packets/, results/, integration.md, and final-report.md as needed.

After each update, return a concise dashboard:
- run directory
- phase
- percent complete
- ETA and confidence
- done
- remaining
- green/yellow/red status with one reason
- active agents and resources
- artifact consistency status
- missing results, resources, or verification evidence

Progress percent is an estimate from phase maturity and accepted evidence, not packet count alone.
Do not make product, safety, budget, or completion decisions.
```

### Packet Worker

```text
You are working on one Ultracode packet.

Run directory: <path>
Packet file: <path>
Phase: <phase id/name>

Read the packet first. Stay inside its allowed scope. Do not revert unrelated changes.
You are not alone in the codebase; other workers or the parent may be editing different scopes.
If editing, touch only the allowed write paths and list every changed file.
Track any browser, Docker container, dev server, background process, tmux pane, temp directory, simulator, or port you open.
Close resources before returning unless the packet explicitly says to hand them off.

Return a concise result:
- status: complete | blocked | partial | failed
- summary
- evidence
- changed files, if any
- verification run, if any
- resources started and cleaned up
- open questions or blockers
```

For read-only packets, add:

```text
Do not modify files. Write no artifacts except your final result.
```

For implementation packets, add:

```text
You may edit files only in the packet's write scope. Add or update focused tests when practical.
```

For verifier packets, add:

```text
Run only the requested verification. Quote the command and summarize the observed result. If the gate fails, preserve the key failure lines.
```

## Conflict Handling

When workers disagree:

1. Identify the claim, not the worker.
2. Check primary evidence: source files, tests, docs, logs, or official references.
3. Prefer reproducible verification over plausibility.
4. Record accepted and rejected claims in `integration.md`.
5. Spawn a verifier only if the conflict materially affects the outcome and can be tested independently.

## Anti-Patterns

- spawning workers before success criteria and write scopes are known
- handing the immediate blocker to a worker and then waiting idly
- giving every worker the full conversation instead of a packet
- using workers to produce generic opinions
- overlapping write scopes without an integration plan
- treating worker output as truth without evidence
- using a bookkeeper when it serializes the run
- manually roleplaying subagents in the parent thread
- skipping final verification because workers reported success
- leaving completed agents open after review
