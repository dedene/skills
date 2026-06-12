# Slice spec contract

A slice spec is the architect's single deliverable to the builder each loop. It must be small enough to land in one PR, and every field below is required. A missing field is a defect — the builder will fill the gap with its own assumptions, which defeats the loop.

## Required fields

- **Goal** — one sentence. If it needs "and", it is probably two slices.
- **In scope** — the concrete change this one PR makes. Bullet list, not prose.
- **Out of scope** — explicit. Name the adjacent work the builder will be tempted to pull in, and forbid it. This is the primary defense against scope creep.
- **Design direction** *(required only when the slice has a user-facing surface)* — the architect's creative-director call: visual references, the design system/tokens to follow, and the interaction quality bar (motion, states, empty/loading/error). Vague taste words ("clean", "modern") are not direction — point at something concrete. Every design intent must be backed by a frozen gate that produces evidence on disk: screenshots saved to a repo path (e.g. `docs/evidence/<slice-id>/` — git-excluded, like all loop files), an a11y score, a Lighthouse number. The builder saves the evidence; the architect and human judge it.
- **Frozen gates** — the hard acceptance criteria, written now, before any result exists. Each gate is measurable and states how it is measured (a command, a metric, a check). Never edited once results land.
- **Contracts to freeze** — the schemas/interfaces the builder freezes in Phase 1. After freeze they are read-only in `docs/` for everyone, including the builder and the architect.
- **Verify-first** — the APIs, formats, versions, signatures, and assumptions the builder must confirm against reality (real files, real docs, real responses) before writing code. This is what lets a short builder session replace hours of back-and-forth: the builder reads truth instead of asking.

## Quality bar

- A gate that cannot be measured is not a gate — make it measurable or cut it.
- "Refactor X while you're there" is scope creep — put it in Out of scope or its own slice.
- If the spec does not force verification of anything, the builder will guess. Always include at least one verify-first item.
- For UI slices, "looks good" is the builder grading its own work. The gate is the saved screenshot or score; the verdict comes later, from the architect and the human.

## Example

```
=== SLICE SPEC ===

Goal: Add idempotency keys to POST /payments so retries never double-charge.

In scope:
- Accept an `Idempotency-Key` header on POST /payments.
- Persist (key, request_hash, response) and replay the stored response on repeat.
- Return 409 on same key + different body.

Out of scope:
- Idempotency on any other endpoint.
- Changing the payments provider integration.
- Cleanup/expiry of stored keys (separate slice).

Frozen gates:
- Same key + same body twice → exactly one provider charge. Measured: integration test asserts provider mock called once.
- Same key + different body → HTTP 409. Measured: request test.
- Key store write is in the same DB transaction as the charge. Measured: code review of the txn boundary + test that a mid-flight failure leaves no orphan key.

Contracts to freeze:
- docs/contracts/idempotency.md — header name, storage row shape, 409 semantics.

Verify-first (confirm against the repo before coding):
- The exact payments provider client method + its retry behavior (cite the file).
- Whether the ORM exposes the transaction boundary you need (cite it).
- The project's existing error-response shape for 4xx (match it, don't invent one).
```
