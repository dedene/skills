---
name: codex-implementation
description: Delegate a bounded, well-specified coding task to GPT-5.5 via the Codex CLI (codex exec) and verify the result. Use for bulk or mechanical work routed to gpt-5.5 per the model policy — clear-spec implementation, migrations, repetitive refactors, test backfills, data transforms — or when the user says "ask codex", "let codex build/fix this", "delegate to gpt-5.5", or "codex exec". Not for taste-critical UI, copy, or public API design.
---

# Codex Implementation

Delegate implementation to GPT-5.5 through `codex exec`. You own the outcome: you write the brief, Codex writes the code, you verify, judge, and report.

## 1. Delegate or not

Delegate when all three hold:

1. **Clear spec** — a skilled dev could start without follow-up questions. If not, tighten the spec first (files, constraints, acceptance criteria, gate command). Never forward vagueness.
2. **Bounded** — you can name the files or subsystem it touches.
3. **Taste is not the bottleneck** — gpt-5.5 codes fast but has taste 5. UI, copy, and public API design need taste ≥ 7: do those yourself, or hand Codex a spec so exact that no taste decisions remain.

For multi-slice projects with human gates, use the architect-loop skill; this skill is the single-task primitive.

## 2. Dispatch contract

```bash
RUN_DIR="$(mktemp -d "${TMPDIR:-/tmp}/codex-run.XXXXXX")"
# 1) write the brief (§3) to "$RUN_DIR/brief.md" with the Write tool
# 2) dispatch:
codex exec \
  -s workspace-write \
  -C "$REPO_ROOT" \
  --skip-git-repo-check \
  -o "$RUN_DIR/result.md" \
  -c model_reasoning_effort="medium" \
  "$(command cat "$RUN_DIR/brief.md")" </dev/null
```

Friction rules — each one earned:

- **Always end with `</dev/null`.** Without a TTY, codex waits on piped stdin ("Reading additional input from stdin...").
- **Brief in a file**, expanded with `$(command cat ...)` — long inline prompts break on shell quoting.
- **Read `$RUN_DIR/result.md`**, not stdout — stdout mixes transcript and token stats; `-o` is the clean final message.
- **Sandbox:** `workspace-write` for implementation, `read-only` for diagnosis/propose mode. Never `danger-full-access` or `--dangerously-bypass-approvals-and-sandbox` unless Peter explicitly asks.
- **Effort:** `low` for probes, `medium` for mechanical work, `high` for real problems; omit the `-c` override to use the config default (currently `xhigh`). Choose for latency, not price — Codex usage is effectively free.
- **Model:** leave unset (config default = gpt-5.5). Pass `-m` only when the user names a model.
- **Foreground vs background:** foreground with `timeout: 600000` only for clearly small tasks; everything else `run_in_background: true`. Don't poll — the harness notifies on exit; then read `result.md` and the exit code.
- **Long or risky runs:** add `--json` to the dispatch and watch the run — see §5 "Watch and steer".
- **Follow-ups:** `codex exec resume --last "<delta>" </dev/null` — same session keeps its context; send only the delta (see the Follow-up recipe).
- **Multiple roots:** writes outside `$REPO_ROOT` need `--add-dir <path>`.
- The CLI ships weekly: when a flag misbehaves, trust `codex exec --help` over this file.

## 3. Compose the brief

Codex sees none of your conversation. The brief must stand alone: repo root, exact files, the project conventions that matter (pull specific lines from the repo's CLAUDE.md/AGENTS.md), the gate command, acceptance criteria.

Structure it with XML blocks — library in [references/prompt-blocks.md](references/prompt-blocks.md), fill-in templates in [references/prompt-recipes.md](references/prompt-recipes.md). The Implementation recipe is the default; one task per run.

## 4. Modes

| Mode | When | How |
|---|---|---|
| **In-place** (default) | normal delegation | `-s workspace-write` in the current worktree |
| **Worktree** | you're editing in parallel, or churn is risky | `git worktree add`, point `-C` at it, merge after verification |
| **Propose** | risky area; review before anything is written | Propose-mode recipe: `-s read-only`, Codex returns a unified diff, you review then `git apply` |

## 5. Watch and steer (long runs)

GPT-5.5 is highly steerable mid-task — for long or risky delegations, don't fire-and-forget:

1. **Dispatch in background with `--json` added.** Events stream as JSONL to the task's output file: `item.started`/`item.completed` with every command, its output, and Codex's own narration.
2. **Check at natural checkpoints** (not on a timer), and read cheaply — never Read the raw stream (its `aggregated_output` fields embed whole file dumps and would flood your context). Glance with a filter:

   ```bash
   tail -c 60000 "<task-output-file>" | grep '^{' | jq -r \
     'select(.type=="item.completed") | .item
      | select(.type=="agent_message" or .type=="command_execution")
      | (.command // .text) | .[0:160]' | tail -20
   ```

   That yields commands + Codex's narration only (~10x smaller than raw). Is Codex touching the right files? In scope? Not looping?
3. **Off the rails → stop the background task, then steer:** `codex exec resume --last "<corrective delta>" </dev/null`. Killed sessions stay resumable — Codex persists the session incrementally, so the correction lands with full context (verified on 0.142.5).
4. **Steer with deltas, not restarts:** say what to stop and what to do instead ("STOP X. Change of plan: do Y."). Re-dispatch fresh only when direction changed so much that the old session context would hurt.

## 6. Verify — non-negotiable

1. `git status` and `git diff` in the repo. Read every change Codex made — its summary is a claim, not evidence.
2. Run the project gate yourself (lint, typecheck, tests) even if Codex says it did.
3. Exercise the behavior end-to-end when practical.

## 7. Judge and escalate

- Below the bar → one or two `resume --last` deltas with sharper, more specific instructions.
- Still below → take over yourself or redo with a smarter model. Standing permission: judge the output, not the price tag.

## 8. Report

What Codex did (summary + touched files), what you verified and the results, anything you fixed or rejected. Failing tests are reported as failing, with output.

## From workflows and subagents

Agent/Workflow `model` params accept only Claude models. To use gpt-5.5 there, spawn a thin wrapper — a `model: 'sonnet', effort: 'low'` agent whose prompt says: "Use the installed `codex-implementation` skill from the `claude-codex` plugin. Compose a self-contained brief for <task> per §3, dispatch it per §2 via Bash, and return the contents of result.md verbatim."

## Troubleshooting

| Symptom | Fix |
|---|---|
| `Not inside a trusted directory` | keep `--skip-git-repo-check`, or run from a trusted project root |
| Hangs printing `Reading additional input from stdin...` | you dropped `</dev/null` |
| Killed around 2 minutes | foreground Bash timeout — use `run_in_background` or raise `timeout` |
| Codex reports sandbox-blocked writes | target is outside the workspace: `--add-dir <path>`, or reconsider scope |
| Empty `result.md` | the run died before a final message — read the Bash call's stdout/stderr |
