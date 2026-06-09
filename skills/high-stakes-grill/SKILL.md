---
name: high-stakes-grill
description: Use when stress-testing, speccing, or refining a plan where many details can be decided by the agent, but a few trajectory-setting decisions still need human judgment.
---

# High-Stakes Grill

Grill a plan with selective autonomy: resolve ordinary questions yourself, but stop for human judgment when an answer would materially change the direction, risk, or cost of the work.

## Start

1. Find the plan in the conversation, repo, issue, PRD, or named file. If none is clear, ask what to grill.
2. When file writes are allowed, create a scratch decision log:

   ```bash
   node <this-skill-dir>/scripts/new-high-stakes-grill-run.mjs "short plan title" --root .
   ```

   If the script is unavailable, manually create `.workflow/high-stakes-grill/<timestamp>-<slug>/decision-log.md` and ensure `.workflow/` is locally ignored. If the active host mode forbids file writes, keep the same context capsule and decision ledger in chat until writes are allowed.
3. Keep the log current after every decision. Update the context capsule near the top so the session can recover after compaction.

## Decision Loop

Repeat until no meaningful open questions remain:

1. Pick the most important unresolved question, respecting dependencies.
2. If the repo, docs, code, schema, tests, or external primary source can answer it, explore and use that answer.
3. Classify the question:
   - `auto`: convention-driven, reversible, low-risk, implementation-local, or answerable from evidence.
   - `human`: trajectory-setting, high-risk, expensive, irreversible, preference-heavy, or materially product-facing.
   - `skip`: cosmetic, premature, or unlikely to change the plan.
4. For `auto`, choose the recommendation yourself and record it.
5. For `human`, ask exactly one question with 2-3 concrete options, put the recommended option first, and wait. Use the host's structured ask-user mechanism when available.
6. Record the answer before moving on.

## Human Escalation Triggers

Ask the user when the answer affects any of these:

- Product direction, target audience, positioning, or user promise.
- Architecture, ownership boundaries, public APIs, schemas, data model, migrations, or compatibility.
- Security, privacy, permissions, credentials, compliance, billing, destructive operations, or production data.
- New dependencies, vendor lock-in, recurring cost, long-running work, broad refactors, or rollout strategy.
- Brand, legal, policy, or communication risk.
- A tradeoff where reasonable teams would choose differently and the downstream work depends on the choice.

Default to auto only when a wrong answer would be easy to reverse and would not waste much implementation effort.

## Question Format

For human questions:

```markdown
Question: <one concrete decision>

A. <recommended option> (Recommended) - <one-line reason>
B. <real alternative> - <tradeoff>
C. <real alternative, if useful> - <tradeoff>
```

Do not ask bundled questions. If two choices are dependent, ask the upstream one first.

## Log Format

Append after every decision:

```markdown
### Decision N: <question>

- Mode: auto | human
- Chosen answer: <A/B/C or short answer>
- Reason: <one-line rationale>
- Evidence: <repo path, command, source, or "user answer">
- Downstream implications: <what this unlocks or changes>
```

Maintain the context capsule:

- Goal
- Current state
- Constraints
- Accepted decisions
- Open high-stakes questions
- Assumptions and defaults

## Stop

Stop when remaining questions are trivial, cosmetic, or would not change the resolved plan. End with:

- `Decisions`: grouped into auto and human.
- `Resolved plan`: rewritten with decisions baked in.
- `Overrides`: specific decisions the user can flip, plus which downstream decisions would need re-resolution.

Do not invent a plan. Do not keep interviewing after decisions stop adding value.
