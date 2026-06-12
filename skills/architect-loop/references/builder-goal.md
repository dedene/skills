# Builder /goal block — why each phase exists

The canonical Phase 0–2 block lives in SKILL.md ("Output: the paste-ready builder block") — that is the only copy to reproduce. This file explains the intent behind each phase, for when a builder pushes back on the rules or the architect needs to defend them.

- **Phase 0 forces disagreement.** A builder that silently complies hides its judgment; the architect needs the builder's objections surfaced with reasons and real file citations before committing to a plan. Silent scope additions are how a one-PR slice becomes a three-day detour.
- **Phase 1 freezes contracts first.** Lanes can only run in parallel safely if the shared schemas/interfaces are locked. Freeze them in `docs/`, then no lane can drift the contract under another.
- **Phase 2 separates building from grading.** Lane agents build modules that don't import each other (or run sequentially on harnesses without parallel agents — the separation matters, not the concurrency); one reviewer pass that never writes feature code is the only thing that can say APPROVE. Raw results go to `docs/HANDOFF.md` as numbers and committed evidence paths, never as narrative — because the verdict is the architect's and the human's to make, not the builder's.
