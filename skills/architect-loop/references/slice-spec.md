# Slice spec contract

A slice spec defines a bounded deliverable, ideally reviewable as one PR. Include applicable fields below; mark genuinely inapplicable contracts or discovery items rather than inventing work.

## Required fields

- **Goal** — one sentence describing the bounded result.
- **Ownership and allowed actions** — assigned paths; whether commits, pushes, publication, messages, destructive operations, or production changes are explicitly authorized. Default to local edits and verification only.
- **In scope** — the concrete change this one PR makes. Bullet list, not prose.
- **Out of scope** — explicit. Name the adjacent work the builder will be tempted to pull in, and forbid it. This is the primary defense against scope creep.
- **Design direction** *(required only when the slice has a user-facing surface)* — the architect's creative-director call: visual references, the design system/tokens to follow, and the interaction quality bar (motion, states, empty/loading/error). Vague taste words ("clean", "modern") are not direction — point at something concrete. Every design intent must be backed by a frozen gate that produces evidence on disk: screenshots saved to a repo path (e.g. `docs/evidence/<slice-id>/` — git-excluded, like all loop files), an a11y score, a Lighthouse number. The builder saves the evidence; the architect and human judge it.
- **Frozen gates** — the hard acceptance criteria, written now, before any result exists. Each gate is measurable and states how it is measured (a command, a metric, a check). Record any justified change as a superseding decision; never silently change targets to fit results.
- **Contracts to freeze** — shared schemas/interfaces needing coordination. Stabilize them before dependent work; record and communicate a superseding decision when a change is needed.
- **Verify-first** — the APIs, formats, versions, signatures, and assumptions the builder must confirm against reality (real files, real docs, real responses) before writing code. This is what lets a short builder session replace hours of back-and-forth: the builder reads truth instead of asking.

## Quality bar

- Criteria need inspectable evidence: command results, code inspection, behavioral observations, or visual comparisons. Do not force visual quality into a numeric score.
- "Refactor X while you're there" is scope creep — put it in Out of scope or its own slice.
- Include verify-first items when an uncertain API, format, or repository fact affects implementation; do not invent a quota.
- For UI slices, "looks good" is the builder grading its own work. The gate is the saved screenshot or score; the verdict comes later, from the architect and the human.

## Example

```
=== SLICE SPEC ===

Ownership: payment handler and focused tests.
Allowed actions: local edits and verification only; no commit, push, publication, messages, destructive operations, or production changes.

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
