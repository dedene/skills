# Prompt Blocks for GPT-5.5 / Codex

Adapted from openai/codex-plugin-cc (Apache-2.0), tuned for gpt-5.5.

Prompt Codex like an operator, not a collaborator: state the task, the output
contract, the follow-through default, and only the constraints that matter.
Wrap each block in the XML tag shown. Use the smallest set that fits and
delete redundant lines before sending. Prefer a better contract over asking
the model to "think harder".

## Core

### `task` — use in every prompt

```xml
<task>
The concrete job, the repository or failure context, and what done looks like.
</task>
```

## Output shape

### `structured_output_contract` — when the response shape matters

```xml
<structured_output_contract>
Return exactly the requested output shape and nothing else.
Keep the answer compact. Highest-value findings or decisions first.
</structured_output_contract>
```

### `compact_output_contract` — concise prose instead of a shape

```xml
<compact_output_contract>
Keep the final answer compact and structured.
No scene-setting, no repeated recap.
</compact_output_contract>
```

## Follow-through

### `default_follow_through_policy` — act without routine questions

```xml
<default_follow_through_policy>
Default to the most reasonable low-risk interpretation and keep going.
Only stop to ask when a missing detail changes correctness, safety, or an irreversible action.
</default_follow_through_policy>
```

### `completeness_contract` — multi-step work that must not stop early

```xml
<completeness_contract>
Resolve the task fully before stopping.
Do not stop at the first plausible answer.
Check for follow-on fixes, edge cases, and cleanup needed for a correct result.
</completeness_contract>
```

### `verification_loop` — when correctness matters

```xml
<verification_loop>
Before finalizing, verify the result against the task requirements and the changed files or tool outputs.
If a check fails, revise instead of reporting the first draft.
</verification_loop>
```

## Grounding

### `missing_context_gating` — when the model might guess

```xml
<missing_context_gating>
Do not guess missing repository facts.
If required context is absent, retrieve it with tools or state exactly what remains unknown.
</missing_context_gating>
```

### `grounding_rules` — review, research, root-cause analysis

```xml
<grounding_rules>
Ground every claim in the provided context or your tool outputs.
Do not present inferences as facts. Label hypotheses clearly.
</grounding_rules>
```

### `citation_rules` — external research

```xml
<citation_rules>
Back important claims with citations or explicit references to inspected sources.
Prefer primary sources.
</citation_rules>
```

## Safety and scope

### `action_safety` — write-capable tasks

```xml
<action_safety>
Keep changes tightly scoped to the stated task.
No unrelated refactors, renames, or cleanup unless required for correctness.
Call out any risky or irreversible action before taking it.
</action_safety>
```

### `tool_persistence_rules` — long tool-heavy tasks

```xml
<tool_persistence_rules>
Keep using tools until you have enough evidence to finish confidently.
Do not abandon the workflow after a partial read when another targeted check would change the answer.
</tool_persistence_rules>
```

## Task-specific

### `research_mode` — exploration and recommendations

```xml
<research_mode>
Separate observed facts, reasoned inferences, and open questions.
Breadth first, then depth only where evidence changes the recommendation.
</research_mode>
```

### `dig_deeper_nudge` — review and adversarial inspection

```xml
<dig_deeper_nudge>
After the first plausible issue, check second-order failures, empty-state behavior, retries, stale state, and rollback paths before finalizing.
</dig_deeper_nudge>
```

### `progress_updates` — long runs

```xml
<progress_updates>
Keep progress updates brief and outcome-based: major phase changes or blockers only.
</progress_updates>
```

## Choosing blocks by task type

- Implementation or bugfix: `completeness_contract`, `verification_loop`, `action_safety`, `missing_context_gating`.
- Review / adversarial review: `grounding_rules`, `structured_output_contract`, `dig_deeper_nudge`.
- Research / recommendation: `research_mode`, `citation_rules`.
- Anything write-capable: always `action_safety`.
