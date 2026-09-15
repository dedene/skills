# HANDOFF — <project>

> Reconcile this record with the working tree and logs; missing entries mean missing records.
> Builder records inspectable results: commands, observations, screenshots, and uncertainty.
> Verdicts and rulings belong to the architect and the human.
> Local-only: this file, `docs/contracts/`, `docs/evidence/`, and `docs/builder-block.md` are git-excluded — never commit them unless the user or repository explicitly requires tracked artifacts.

<!-- All <angle-bracket> rows below are placeholders — replace or delete them on first real use; do not leave them behind. -->

Builder: <name and requested/recorded model or configured default>
Allowed actions: <explicit grants; default local edits and verification only, no commit, push, publication, messages, destructive operations, or production changes>

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

<!-- Record command, checked tree/revision, environment, result, and qualitative/visual evidence as relevant. -->

### `<slice-id>` — <YYYY-MM-DD>

| Gate | Target | Actual |
| --- | --- | --- |
| <gate> | <target> | <observed result or evidence path> |

- Checked tree/revision: <sha plus uncommitted diff or tree identity>
- Commit / PR: <only if explicitly authorized and created; otherwise "not requested">
- Review: <no objections / defect list with evidence / not needed for this risk>
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
