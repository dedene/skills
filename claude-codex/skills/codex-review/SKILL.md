---
name: codex-review
description: Obtain an independent Codex CLI review of a diff or design and verify its findings.
---

# Codex Review

Get the configured Codex model's independent review and verify its findings. Keep the review subprocess read-only. When the user's broader request includes fixes, the parent completes confirmed fixes and verification without asking again.

## 1. Pick scope and mode

| Situation | Command |
|---|---|
| Dirty working tree (default when dirty) | `codex review --uncommitted` |
| Clean tree on a feature branch | `codex review --base <default-branch>` |
| A single commit | `codex review --commit <sha>` |
| Steered review | Check installed help for compatible scope/prompt flags; if they cannot combine, use read-only `codex exec` with an explicit scope and focus |
| Challenge a design or premise, not just the diff | adversarial mode — §3 |

Check scope before declaring nothing to review: `git status --short` and `git diff --shortstat` — untracked files count as reviewable work.

`codex review` has no `-C` and no `--skip-git-repo-check`: run it from the repo root of a git repository.

## 2. Dispatch

```bash
RUN_DIR="$(mktemp -d "${TMPDIR:-/tmp}/codex-review.XXXXXX")"
cd "$REPO_ROOT" && codex -s read-only review --uncommitted \
  > "$RUN_DIR/review.md" 2>"$RUN_DIR/review.err" </dev/null
```

- **Keep `RUN_DIR` outside the repo** (mktemp as shown). Artifacts redirected into the working tree become untracked files that Codex then reviews — self-referential noise findings.
- **Execution:** use the host's background/session mechanism for long reviews and remain responsive. Check `codex --help` and `codex review --help` for the installed version before first use.
- **Always `</dev/null`** — non-TTY stdin stalls the CLI otherwise.
- Inherit configured model and reasoning effort, including a GPT-6 Astra profile when configured. Override only for a requested model or documented host policy; no fixed generation or effort default belongs in this skill.
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
- Keep the reviewer read-only. If fixes are already authorized, the parent implements confirmed findings and verifies affected behavior before handoff. Otherwise report the findings.

## Troubleshooting

| Symptom | Fix |
|---|---|
| Trust/repo-check errors | a git repo is required, but untrusted dirs reviewed fine as of 0.142.5; if it ever blocks, fall back to `codex exec review` (check `codex exec review --help`) |
| Stalls on `Reading additional input from stdin...` | you dropped `</dev/null` |
| Killed around 2 minutes | use the host's background/session mechanism |
| Empty review output | check `review.err`; confirm there was something to review (`git status --short`) |
