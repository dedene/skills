---
name: codex-implementation
description: Delegate a bounded implementation task through the Codex CLI when cross-agent execution is requested or useful.
---

# Codex Implementation

Delegate implementation to the configured Codex model through `codex exec`. You own the outcome: you write the brief, Codex writes the code, you verify, judge, and report.

## 1. Delegate or not

Delegate when all three hold:

1. **Clear spec** — a skilled dev could start without follow-up questions. If not, tighten the spec first (files, constraints, acceptance criteria, gate command). Never forward vagueness.
2. **Bounded** — you can name the files or subsystem it touches.
3. **Useful independence** — delegation allows useful parallel work or an independently scoped implementation. UI, copy, and API design can be delegated with clear references, acceptance criteria, and appropriate review.

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
  "$(command cat "$RUN_DIR/brief.md")" </dev/null
```

Friction rules — each one earned:

- **Always end with `</dev/null`.** Without a TTY, codex waits on piped stdin ("Reading additional input from stdin...").
- **Brief in a file**, expanded with `$(command cat ...)` — long inline prompts break on shell quoting.
- **Read `$RUN_DIR/result.md`**, not stdout — stdout mixes transcript and token stats; `-o` is the clean final message.
- **Sandbox:** `workspace-write` for implementation, `read-only` for diagnosis/propose mode. Never `danger-full-access` or `--dangerously-bypass-approvals-and-sandbox` unless Peter explicitly asks.
- **Model and effort:** inherit CLI configuration, including a GPT-6 Astra profile when configured. Override only for a requested model or documented host policy; do not assume a fixed default, capability score, or free usage.
- **Foreground vs background:** use the host's background/session mechanism for long runs. Stay responsive, read the result and exit code on completion, and avoid busy polling.
- **Long or risky runs:** add `--json` to the dispatch and watch the run — see §5 "Watch and steer".
- **Follow-ups:** `codex exec resume <session-id> "<delta>" </dev/null` — same session keeps its context; send only the delta (see the Follow-up recipe).
- **Multiple roots:** writes outside `$REPO_ROOT` need `--add-dir <path>`.
- The CLI ships weekly: when a flag misbehaves, trust `codex exec --help` over this file.

## 3. Compose the brief

Codex sees none of your conversation. The brief must stand alone: repo root, exact files, the relevant AGENTS.md conventions, allowed actions, the gate command, and acceptance criteria. Explicitly state whether commits, pushes, publication, messages, destructive operations, and production changes are authorized; absent a grant, forbid them. Tell the worker it is not alone and must preserve others' edits.

Structure it with XML blocks — library in [references/prompt-blocks.md](references/prompt-blocks.md), fill-in templates in [references/prompt-recipes.md](references/prompt-recipes.md). The Implementation recipe is the default; one task per run.

## 4. Modes

| Mode | When | How |
|---|---|---|
| **In-place** (default) | normal delegation | `-s workspace-write` in the current worktree |
| **Worktree** | you're editing in parallel, or churn is risky | Use an isolated worktree only within the user's branch/worktree policy; point `-C` at it and integrate authorized changes after verification |
| **Propose** | risky area; review before anything is written | Propose-mode recipe: `-s read-only`, Codex returns a unified diff, you review then `git apply` |

## 5. Watch and steer (long runs)

For long or risky delegations, inspect progress and steer when needed:

1. **Dispatch in background with `--json` added.** Events stream as JSONL to the task's output file: `item.started`/`item.completed` with every command, its output, and Codex's own narration.
2. **Check at natural checkpoints** (not on a timer), and read cheaply — never Read the raw stream (its `aggregated_output` fields embed whole file dumps and would flood your context). Glance with a filter:

   ```bash
   tail -c 60000 "<task-output-file>" | grep '^{' | jq -r \
     'select(.type=="item.completed") | .item
      | select(.type=="agent_message" or .type=="command_execution")
      | (.command // .text) | .[0:160]' | tail -20
   ```

   That yields commands + Codex's narration only (~10x smaller than raw). Is Codex touching the right files? In scope? Not looping?
3. **Off the rails → stop the background task, then steer:** `codex exec resume <session-id> "<corrective delta>" </dev/null`. Capture the run's exact session ID and confirm resume support through installed help. Avoid `--last` when other runs may overlap.
4. **Steer with deltas, not restarts:** say what to stop and what to do instead ("STOP X. Change of plan: do Y."). Re-dispatch fresh only when direction changed so much that the old session context would hurt.

## 6. Verify — non-negotiable

1. `git status` and `git diff` in the repo. Read every change Codex made — inspect the diff alongside recorded evidence.
2. Inspect recorded gate commands, checked tree/revision, environment, and results. Rerun affected checks after integration edits, failures, or incomplete evidence; do not duplicate a valid unchanged gate solely because a worker ran it.
3. Exercise the behavior end-to-end when practical.

## 7. Judge and escalate

- Below the bar → one or two targeted resume deltas with sharper, more specific instructions.
- Still below → investigate the remaining gap and take over or adjust the brief within the existing model and resource policy.

## 8. Report

What Codex did (summary + touched files), what you verified and the results, anything you fixed or rejected. Failing tests are reported as failing, with output.

## From workflows and subagents

Use the host's actual agent capabilities and model policy. If it cannot select the requested Codex model natively, a bounded CLI wrapper may read this installed skill, compose the brief, dispatch it, and return the result plus verification evidence. Resolve the skill path through the active installation; do not hard-code a user's home directory. Do not add a wrapper when the parent can dispatch directly without losing useful parallel work.

## Troubleshooting

| Symptom | Fix |
|---|---|
| `Not inside a trusted directory` | keep `--skip-git-repo-check`, or run from a trusted project root |
| Hangs printing `Reading additional input from stdin...` | you dropped `</dev/null` |
| Killed around 2 minutes | foreground Bash timeout — use the host's background/session mechanism |
| Codex reports sandbox-blocked writes | target is outside the workspace: `--add-dir <path>`, or reconsider scope |
| Empty `result.md` | the run died before a final message — read the Bash call's stdout/stderr |
