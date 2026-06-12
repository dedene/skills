# Builder profiles

A profile defines the **dispatch command** (how the architect invokes the builder non-interactively from a shell), names the **model-discovery command**, and notes the harness's capabilities. Profiles never change the `=== RULES ===` half, the slice-spec contract, or the HANDOFF format — those are loop-invariant. Record the active builder and model as a `Builder:` line in `docs/HANDOFF.md` (e.g. `Builder: codex (gpt-5.5 high)`) so every future architect session picks the right profile without asking.

**Default:** when no builder is recorded or named, use **the `codex` CLI running `gpt-5.5` at high reasoning effort** — no confirmation question needed. When a builder *is* specified, discover its available models with the command below (never from memory — fast models churn) and confirm the choice with the user via one structured question, recommended model first.

**Dispatch is the architect's job.** Always verify the dispatch flags against the installed version (`<cli> --help`) before the first run of a session — these CLIs change fast. Run dispatches in a background shell and feed the block from `docs/builder-block.md`. The paste fallback exists only for builders with no shell-reachable mode (or when the CLI is missing/unauthenticated); using it for any other reason is a defect.

## codex (Codex CLI) — default

- **Dispatch command:**
  ```bash
  codex exec -s workspace-write -m gpt-5.5 -c model_reasoning_effort=high - < docs/builder-block.md
  ```
  `codex exec` runs non-interactively; `-` reads the block from stdin. Useful extras: `-C <dir>` to set the working root, `-o <file>` to capture the builder's final message, `exec resume --last` to continue a session (use it for a two-turn Phase 0 checkpoint when warranted).
- **Model discovery:** `codex --help` (model via `-m`; reasoning effort via `-c model_reasoning_effort=high` or the config file). Verify flags against the installed version — they change.
- **Default model:** `gpt-5.5` at high reasoning effort.
- **Parallelism:** supports spawning agents — Phase 2 runs max 3–4 lane agents + one reviewer agent.
- **Sandbox/network:** `workspace-write` blocks network, so `git push` fails inside the run — the builder commits locally and records the sha in `docs/HANDOFF.md` (the RULES block already allows this). Only escalate to `-s danger-full-access` if the human explicitly approves it.
- **Paste fallback header:** `/goal: execute the architect spec below.` (interactive Codex session).
- **Notes:** strong at long unattended runs; keep the spec's verify-first list sharp so it reads truth from the repo instead of guessing.

## cursor (Cursor CLI / Composer)

- **Dispatch command:**
  ```bash
  cursor-agent -p --model <model> "$(cat docs/builder-block.md)"
  ```
  `-p/--print` is the non-interactive mode with full tool access (write + shell). `--output-format text` is the default; use `stream-json` if you want to watch progress.
- **Model discovery:** `cursor-agent --help` and, if the installed version has one, its model-listing subcommand (model via `--model`). Verify against the installed version.
- **Parallelism:** if the session can run parallel agents, use lanes as written; otherwise Phase 2's sequential fallback applies — lanes run one after another, reviewer pass still mandatory and still writes no feature code.
- **Paste fallback:** Composer inside the Cursor IDE is not shell-reachable — that is the one legitimate paste case for this builder. Prepend one plain sentence: `Execute the architect spec below.`
- **Notes:** the common pairing for UI-heavy slices. The architect acts as creative director: always include the **Design direction** spec field, and make at least one frozen gate produce visual evidence on disk (e.g. screenshots saved under `docs/evidence/<slice-id>/`, an a11y or Lighthouse score). The builder saves the evidence; it never grades it.

## grok (Grok CLI / Grok Build)

- **Dispatch command:** check `grok --help` on the installed version for a non-interactive/print/prompt flag and use it with the block from `docs/builder-block.md`. If the installed version has no such mode, use the paste fallback and say so.
- **Model discovery:** `grok --help` and, if the installed version has one, its model-listing subcommand or settings. Verify against the installed version.
- **Parallelism:** check the installed version's agent/subtask support; if absent, Phase 2's sequential fallback applies — reviewer pass still mandatory.
- **Paste fallback:** prepend one plain sentence: `Execute the architect spec below.`
- **Notes:** fast and cheap on a sub, good for high-volume mechanical slices. Lean harder on Phase 0 (it must cite real repo files in its plan) and keep frozen gates strictly numeric — fast builders are the most tempted to narrate.

## New or future builder (checklist)

Any agent qualifies if it can read a spec, push back with reasons, commit, and write numbers to a file. To onboard one, answer these and add a profile entry above:

1. **Dispatch** — does it have a non-interactive exec/print mode the architect can call from a shell (an `exec` subcommand, a `-p` flag, a stdin mode)? That command becomes the dispatch command. No such mode → paste fallback through the human, stated explicitly in the profile.
2. **Models** — what is the model-discovery command (`--help`, a models subcommand, a config file)? Which flag selects the model? Discover, then confirm with the user.
3. **Parallelism** — can it run subagents/parallel lanes? If not, Phase 2's sequential fallback applies automatically; nothing else changes.
4. **Git** — can it commit itself, and does its sandbox allow pushing? If it cannot commit, instruct it to stop after each slice and ask the human to commit; results still go in `docs/HANDOFF.md` first. If only the push is blocked, the RULES block already covers it — record the sha.
5. **Evidence** — can it run tests, capture screenshots, or run a browser? Shape the frozen gates around what it can actually measure and commit.
6. **Discipline** — does it respect "read-only after freeze"? If it tends to edit frozen docs, add one line to the block: "Files listed under Frozen contracts in docs/HANDOFF.md are read-only."

If a builder cannot satisfy 1–5 even with workarounds, it is not a fit for the loop — say so rather than weakening the rules.
