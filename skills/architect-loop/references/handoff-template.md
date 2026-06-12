# HANDOFF — <project>

> The repo is the brain. If it isn't in this file, it didn't happen.
> Builder writes **raw results only** — tables and numbers, no interpretation, no "promising."
> Verdicts and rulings belong to the architect and the human.
> Local-only: this file, `docs/contracts/`, `docs/evidence/`, and `docs/builder-block.md` are git-excluded — never commit them (see the skill's "Keep the loop files out of git").

<!-- All <angle-bracket> rows below are placeholders — replace or delete them on first real use; do not leave them behind. -->

Builder: <name (model) — e.g. codex (gpt-5.5 high), cursor (composer), grok (…) — see the skill's builder-profiles reference>

## Current slice

`<slice-id>` — <one-line goal>

## Frozen contracts (read-only after freeze)

Schemas and interfaces frozen in Phase 1. Do not edit after the freeze date — supersede with a new slice instead.

- `<path>` — <what it defines> — frozen <YYYY-MM-DD>

## Frozen gates (set before results, never edited)

| Gate | Target | How measured |
| --- | --- | --- |
| <gate> | <target> | <command / metric / check> |

## Raw results (latest first — builder fills, no interpretation)

<!-- Numbers only. No pass/fail, no narrative — verdicts belong to the architect's rulings below. -->

### `<slice-id>` — <YYYY-MM-DD>

| Gate | Target | Actual |
| --- | --- | --- |
| <gate> | <target> | <raw number> |

- Commit / PR: <link or sha>
- Reviewer agent: APPROVE / defect list ref
- Evidence: <paths under docs/evidence/<slice-id>/ — screenshots, logs, score reports — or "—">

## Decisions (what + why) — architect-owned

- <decision> — <why> — <YYYY-MM-DD>

## Open disagreements (builder → architect) — architect rules on these

- [ ] <disagreement> — raised by builder — <reason / cited file>

## Rulings (architect → builder)

- <disagreement> → ACCEPT | REJECT | MODIFY — <one line why> — <YYYY-MM-DD>

## Next slice — architect-owned

<one-line goal of the next slice>

## Session log (boundaries)

- <YYYY-MM-DD> — built: <…> / decided: <…> / next: <…>
