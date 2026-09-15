---
name: autopilot-interview
description: Interview or stress-test a plan when the user requests it. Resolve routine choices and surface consequential unresolved decisions.
---

# Autopilot Interview

Interview a plan by default through deep auto-interviewing with selective autonomy. Build a broad question map, resolve ordinary questions yourself, and stop for human judgment when an answer would materially change direction, risk, cost, UX, architecture, or the final spec/plan.

When the user asks to be interviewed or grilled in detail, use the same default workflow at full intensity: surface non-obvious questions across product, technical implementation, UI/UX, concerns, tradeoffs, risks, rollout, and acceptance criteria until the requested spec, plan, or next artifact is complete enough to write.

## Start

1. Find the plan in the conversation, repo, issue, PRD, or named file. If none is clear, ask what to interview.
2. Capture the completion target if the user gave one: write a spec to a file, produce an implementation plan, proceed to implementation, or return a resolved plan in chat.
3. When resumability or a substantial decision history warrants it and file writes are allowed, create a scratch decision log. Keep short interviews in conversation:

   ```bash
   node <this-skill-dir>/scripts/new-autopilot-interview-run.mjs "short plan title" --root .
   ```

   If the script is unavailable, manually create `.workflow/autopilot-interview/<timestamp>-<slug>/decision-log.md` and ensure `.workflow/` is locally ignored. If the active host mode forbids file writes, keep the same context capsule and decision ledger in chat until writes are allowed.
4. Keep the log current after every decision. Update the context capsule near the top so the session can recover after compaction.

## Default Auto-Interview

Use this for explicitly requested interviews or stress-tests. For quick stress-tests, still build the map internally but ask only the highest-stakes questions. For explicit interview requests, run the map at full intensity.

Before asking questions, build a question map across all relevant domains:

- Product promise, target users, jobs-to-be-done, scope boundaries, and non-goals.
- Technical implementation, architecture, ownership boundaries, data model, APIs, schemas, migrations, compatibility, and dependencies.
- UI/UX, navigation, core flows, edge flows, empty/loading/error states, permissions, responsiveness, accessibility, and copy tone.
- Concerns, tradeoffs, risks, security, privacy, abuse cases, observability, operations, rollout, and support.
- Testing, acceptance criteria, success metrics, performance, failure modes, and documentation.

Question quality rules:

- Ask non-obvious questions whose answers change the shape of the spec, plan, UI, architecture, risk, or cost.
- Convert obvious questions into sharper hidden-fork questions. Prefer "which tradeoff should win?" over "do you want X?"
- Always provide a recommended answer first, with the rationale and the cost of the alternatives.
- Continue until every material domain is either decided, auto-decided, explicitly skipped, or recorded as an assumption.
- If the user said "then proceed to..." complete that target after the interview rather than stopping at the decision list.

## Decision Loop

Repeat until no meaningful open questions remain:

1. Pick the most important unresolved question from the plan and auto-interview map, respecting dependencies.
2. If the repo, docs, code, schema, tests, or external primary source can answer it, explore and use that answer.
3. Classify the question:
   - `auto`: a two-way door with a valid smart answer: evidence-backed, convention-driven, easy to reverse, low-risk, or implementation-local.
   - `human`: a one-way door: hard to reverse, expensive to unwind, preference-defining, or likely to shape product direction, architecture, cost, risk, or user promise.
   - `skip`: cosmetic, premature, or unlikely to change the plan.
4. For `auto`, choose the recommendation yourself and record it.
5. For `human`, first check whether the brief or prior answers already settle it. If unresolved, ask one concrete question with the recommendation and tradeoffs. Use the host's structured question mechanism when supported for this question type. Pause only dependent work; continue independent work while waiting.
6. Record the exact decision question, options, and answer before moving on.

Do not stop just because the current plan has no obvious holes. Re-scan the auto-interview map for hidden forks, edge states, and downstream tradeoffs before ending.

## Escalation Rule

Resolve routine choices from evidence, conventions, and established preferences. A choice affecting architecture, UX, or cost does not automatically need a question. Disagreement between reasonable teams is not enough either.

Ask when a decision remains unresolved and materially changes the requested outcome, crosses authority, or creates costly rework. Reuse decisions and authorization already supplied. Explain the relevant findings, recommendation, and downstream effect so the user can answer without reading tool output. Continue independent work while the answer is pending.

## Question Format

For human questions:

```markdown
Question: <one concrete decision>

A. <recommended option> (Recommended) - <one-line reason>
B. <real alternative> - <tradeoff>
C. <real alternative, if useful> - <tradeoff>
```

Do not ask bundled questions. If two choices are dependent, ask the upstream one first.

When recording a human decision, copy the `Question:` line and the option labels exactly as shown to the user.

## Log Format

Append after every decision:

```markdown
### Decision N: <short decision topic>

- Mode: auto | human
- Question asked: <exact human prompt or internal decision question>
- Options presented: <A/B/C options shown, or "not presented; auto-decided">
- Chosen answer: <A/B/C plus option label, or short answer>
- Reason: <one-line rationale>
- Evidence: <repo path, command, source, or "user answer">
- Downstream implications: <what this unlocks or changes>
```

Maintain the context capsule:

- Goal
- Current state
- Constraints
- Completion target
- Accepted decisions
- Open high-stakes questions
- Assumptions and defaults

## Stop

Stop when remaining questions are trivial, cosmetic, or would not change the resolved plan, spec, UI, architecture, risk profile, or implementation path.

If the user requested a follow-on target, complete it:

- Spec target: write the resolved spec to the requested file, or choose a conventional project path if obvious.
- Planning target: produce the implementation plan with decisions baked in.
- Implementation target: proceed only if the remaining work is clear and allowed in the active host mode.

Otherwise end with:

- `Decisions`: grouped into auto and human.
- `Resolved plan`: rewritten with decisions baked in.
- `Overrides`: specific decisions the user can flip, plus which downstream decisions would need re-resolution.

Do not invent a plan. Do not keep interviewing after decisions stop adding value.
