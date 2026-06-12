# Builder profiles

A profile adapts the paste-ready block's **invocation header**, names the **model-discovery command**, and notes the harness's capabilities. Profiles never change the `=== RULES ===` half, the slice-spec contract, or the HANDOFF format — those are loop-invariant. Record the active builder and model as a `Builder:` line in `docs/HANDOFF.md` (e.g. `Builder: codex (gpt-5.5 high)`) so every future architect session picks the right profile without asking.

**Default:** when no builder is recorded or named, use **codex with `gpt-5.5-codex` at high reasoning effort** — no confirmation question needed. When a builder *is* specified, discover its available models with the command below (never from memory — fast models churn) and confirm the choice with the user via one structured question, recommended model first.

## codex (GPT-5.x Codex) — default

- **Invocation header:** `/goal: execute the architect spec below.`
- **Model discovery:** `codex --help` (model via `codex -m <model>`; reasoning effort via `codex -c model_reasoning_effort=high` or the config file). Verify flags against the installed version — they change.
- **Default model:** `gpt-5.5-codex` at high reasoning effort.
- **Parallelism:** supports spawning agents — Phase 2 runs max 3–4 lane agents + one reviewer agent.
- **Notes:** strong at long unattended runs; keep the spec's verify-first list sharp so it reads truth from the repo instead of guessing.

## cursor (Cursor CLI / Composer)

- **Invocation header:** none — paste the block as the prompt in a Cursor CLI (`cursor-agent`) session running a Composer model. Start the first line at `=== SLICE SPEC ===` and prepend one plain sentence: `Execute the architect spec below.`
- **Model discovery:** `cursor-agent --help` and, if the installed version has one, its model-listing subcommand (model via `cursor-agent -m <model>`). Verify against the installed version.
- **Parallelism:** if the session can run parallel agents, use lanes as written; otherwise Phase 2's sequential fallback applies — lanes run one after another, reviewer pass still mandatory and still writes no feature code.
- **Notes:** the common pairing for UI-heavy slices. The architect acts as creative director: always include the **Design direction** spec field, and make at least one frozen gate produce committable visual evidence (e.g. screenshots saved under `docs/evidence/<slice-id>/`, an a11y or Lighthouse score). The builder commits the evidence; it never grades it.

## grok (Grok CLI / Grok Build)

- **Invocation header:** none — paste the block as the prompt in a `grok` session. Start the first line at `=== SLICE SPEC ===` and prepend one plain sentence: `Execute the architect spec below.`
- **Model discovery:** `grok --help` and, if the installed version has one, its model-listing subcommand or settings. Verify against the installed version.
- **Parallelism:** check the installed version's agent/subtask support; if absent, Phase 2's sequential fallback applies — reviewer pass still mandatory.
- **Notes:** fast and cheap on a sub, good for high-volume mechanical slices. Lean harder on Phase 0 (it must cite real repo files in its plan) and keep frozen gates strictly numeric — fast builders are the most tempted to narrate.

## New or future builder (checklist)

Any agent qualifies if it can read a spec, push back with reasons, commit, and write numbers to a file. To onboard one, answer these and add a profile entry above:

1. **Invocation** — how does a pasted block reach it (slash command, plain prompt, CLI flag)? That becomes the header.
2. **Models** — what is the model-discovery command (`--help`, a models subcommand, a config file)? Which flag selects the model? Discover, then confirm with the user.
3. **Parallelism** — can it run subagents/parallel lanes? If not, Phase 2's sequential fallback applies automatically; nothing else changes.
4. **Git** — can it commit + push itself? If not, instruct it to stop after each slice and ask the human to commit; results still go in `docs/HANDOFF.md` first.
5. **Evidence** — can it run tests, capture screenshots, or run a browser? Shape the frozen gates around what it can actually measure and commit.
6. **Discipline** — does it respect "read-only after freeze"? If it tends to edit frozen docs, add one line to the header: "Files listed under Frozen contracts in docs/HANDOFF.md are read-only."

If a builder cannot satisfy 1–5 even with workarounds, it is not a fit for the loop — say so rather than weakening the rules.
