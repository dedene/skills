---
name: codex-review
description: Independent GPT-5.5 code review via the Codex CLI — codex review for uncommitted changes, a branch diff, or a commit; adversarial exec mode for challenging a design or premise. Use when the user asks for a codex or gpt review, a second opinion on a diff or plan, or when adding gpt-5.5 as an extra review perspective alongside Claude reviews. Verifies findings against the code before reporting; never auto-fixes.
---

# Codex Review

Get GPT-5.5's independent read on a change, verify its findings yourself, then report. This skill never fixes code — fixing is a separate decision afterwards (often a codex-implementation dispatch).

## 1. Pick scope and mode

| Situation | Command |
|---|---|
| Dirty working tree (default when dirty) | `codex review --uncommitted` |
| Clean tree on a feature branch | `codex review --base <default-branch>` |
| A single commit | `codex review --commit <sha>` |
| Steered review | append instructions: `codex review --uncommitted "focus on the migration rollback path"` |
| Challenge a design or premise, not just the diff | adversarial mode — §3 |

Check scope before declaring nothing to review: `git status --short` and `git diff --shortstat` — untracked files count as reviewable work.

`codex review` has no `-C` and no `--skip-git-repo-check`: run it from the repo root of a git repository.

## 2. Dispatch

```bash
RUN_DIR="$(mktemp -d "${TMPDIR:-/tmp}/codex-review.XXXXXX")"
cd "$REPO_ROOT" && codex review --uncommitted \
  > "$RUN_DIR/review.md" 2>"$RUN_DIR/review.err" </dev/null
```

- **Keep `RUN_DIR` outside the repo** (mktemp as shown). Artifacts redirected into the working tree become untracked files that Codex then reviews — self-referential noise findings.
- **Background by default** (`run_in_background: true`): multi-file reviews at xhigh take minutes. Foreground (with `timeout: 600000`) only for 1-2 file diffs.
- **Always `</dev/null`** — non-TTY stdin stalls the CLI otherwise.
- Optional effort override: `-c model_reasoning_effort="high"`. Leave the model unset (config default gpt-5.5).
- On completion, read `review.md`; if it's empty, read `review.err` and the exit code before concluding anything.

## 3. Adversarial mode

For pressure-testing a decision ("was this caching design right?", "poke holes in this migration plan"): use the template in [references/adversarial-review.md](references/adversarial-review.md) — fill in target and focus, keep the skeptical-stance blocks intact, dispatch via `codex exec -s read-only` as shown there. Add `--output-schema <path-to-this-skill>/references/review-findings.schema.json` when you want machine-readable findings. Resolve `<path-to-this-skill>` to the installed `codex-review` skill directory; do not assume a user-skill install path.

## 4. Verify findings — the whole point

Codex findings are leads, not conclusions:

1. Read the cited lines yourself (Read tool, actual files) for every finding.
2. Confirm or refute each one against the code. Style nits and speculation without evidence: drop.
3. Anything you cannot confirm or refute cheaply: mark it "plausible, unverified" — don't silently drop or promote it.

## 5. Report

- Confirmed findings ranked by severity, each with `file:line` and a one-sentence concrete failure scenario.
- Rejected findings, one line each: what Codex claimed, why it's wrong.
- Plausible-unverified findings listed last, labeled.
- Point at the raw output: `Raw Codex review: <RUN_DIR>/review.md`.
- Nothing survives verification → say so plainly. Don't invent issues to seem useful.
- Never fix anything from this skill, even trivial confirmed findings.

## Troubleshooting

| Symptom | Fix |
|---|---|
| Trust/repo-check errors | a git repo is required, but untrusted dirs reviewed fine as of 0.142.5; if it ever blocks, fall back to `codex exec review` (check `codex exec review --help`) |
| Stalls on `Reading additional input from stdin...` | you dropped `</dev/null` |
| Killed around 2 minutes | use `run_in_background` |
| Empty review output | check `review.err`; confirm there was something to review (`git status --short`) |
