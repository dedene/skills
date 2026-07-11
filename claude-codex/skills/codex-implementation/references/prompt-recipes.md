# Codex Prompt Recipes

Adapted from openai/codex-plugin-cc (Apache-2.0), tuned for gpt-5.5.
Copy the smallest recipe that fits, fill the angle-bracket slots, trim what
you don't need. One task per run — unrelated asks get separate runs.
Blocks are defined in [prompt-blocks.md](prompt-blocks.md).

## Implementation (the default brief)

```xml
<task>
In <repo-root>, implement <feature/fix> in <files or subsystem>.
Context: <the 3-5 facts Codex needs: current behavior, why it changes, constraints>.
Follow these conventions: <only the repo conventions that matter for this change>.
Done means: <concrete acceptance criteria>.
</task>

<completeness_contract>
Resolve the task fully before stopping. Do not stop at the first plausible version.
</completeness_contract>

<verification_loop>
Run `<gate command>` and fix failures until it passes. Report the final output.
</verification_loop>

<action_safety>
Keep changes tightly scoped to the stated task.
No unrelated refactors, renames, or cleanup.
</action_safety>

<structured_output_contract>
Return:
1. summary of the change
2. touched files
3. verification performed and its result
4. residual risks or follow-ups
</structured_output_contract>
```

## Diagnosis (read-only investigation)

```xml
<task>
Diagnose why <failing test/command/behavior> is breaking in <repo-root>.
Reproduce with: <command>. Observed: <error/output>.
</task>

<compact_output_contract>
Return: 1. most likely root cause  2. evidence  3. smallest safe next step.
</compact_output_contract>

<default_follow_through_policy>
Keep going until you have enough evidence to identify the root cause confidently.
</default_follow_through_policy>

<missing_context_gating>
Do not guess missing repository facts. State exactly what remains unknown.
</missing_context_gating>
```

Dispatch diagnosis with `-s read-only`.

## Propose-mode diff (review before anything is written)

```xml
<task>
In <repo-root>, design the smallest safe change that <goal>, but DO NOT modify any files.
</task>

<structured_output_contract>
Return:
1. a complete unified diff (git apply compatible, correct paths from the repo root)
2. why this approach
3. risks
</structured_output_contract>

<verification_loop>
Before finalizing, re-read every hunk against the current file contents so the diff applies cleanly.
</verification_loop>
```

Dispatch with `-s read-only`; after your review: `git apply <diff-file>`.

## Follow-up delta (same Codex session)

```bash
codex exec resume --last "<delta instruction only>" </dev/null
```

Send only what changed — "also handle the empty-list case in average() and add a test for it" — not a restatement of the whole brief. Restate the brief only when direction changed materially.

## Research / recommendation

```xml
<task>
Research <question> and recommend the best path for <context>.
</task>

<structured_output_contract>
Return: 1. observed facts  2. recommendation  3. tradeoffs  4. open questions.
</structured_output_contract>

<research_mode>
Separate observed facts, reasoned inferences, and open questions.
</research_mode>

<citation_rules>
Back important claims with references to inspected sources. Prefer primary sources.
</citation_rules>
```

Dispatch with `-s read-only` (config allows network, so web research works).
