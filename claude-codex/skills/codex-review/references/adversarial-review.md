# Adversarial Review Prompt Template

Adapted from openai/codex-plugin-cc (Apache-2.0). Use for pressure-testing a
design or premise, not for routine diff review (that's `codex review`).

Fill `<TARGET>` (e.g. "uncommitted changes in this repo", "the diff vs main",
"the migration plan in docs/plan.md") and `<USER_FOCUS>` (the specific risk or
decision to challenge; write "none" if absent). Keep every other block intact —
the skeptical stance is the value.

Dispatch (read-only, always):

```bash
RUN_DIR="$(mktemp -d "${TMPDIR:-/tmp}/codex-adv.XXXXXX")"
# write the filled template to "$RUN_DIR/brief.md", then:
codex exec -s read-only -C "$REPO_ROOT" --skip-git-repo-check \
  -o "$RUN_DIR/adversarial.md" \
  "$(command cat "$RUN_DIR/brief.md")" </dev/null
```

For machine-readable output add:
`--output-schema <path-to-this-skill>/references/review-findings.schema.json`
Resolve `<path-to-this-skill>` to the installed `codex-review` skill directory; the `-o` file then contains JSON matching the schema.

## Template

```xml
<role>
You are performing an adversarial software review.
Your job is to break confidence in the change, not to validate it.
</role>

<task>
Review as if finding the strongest reasons this should not ship yet.
Target: <TARGET>
User focus: <USER_FOCUS>
Gather the context yourself: inspect the repository with git (e.g. `git diff`,
`git diff <base>...HEAD`, `git show <sha>`) and read the relevant files.
</task>

<operating_stance>
Default to skepticism.
Assume the change can fail in subtle, high-cost, or user-visible ways until the evidence says otherwise.
No credit for good intent, partial fixes, or likely follow-up work.
Happy-path-only behavior is a real weakness.
</operating_stance>

<attack_surface>
Prioritize expensive, dangerous, or hard-to-detect failures:
- auth, permissions, tenant isolation, trust boundaries
- data loss, corruption, duplication, irreversible state changes
- rollback safety, retries, partial failure, idempotency gaps
- race conditions, ordering assumptions, stale state, re-entrancy
- empty-state, null, timeout, degraded dependency behavior
- version skew, schema drift, migration hazards, compatibility regressions
- observability gaps that would hide failure or block recovery
</attack_surface>

<review_method>
Actively try to disprove the change.
Hunt violated invariants, missing guards, unhandled failure paths, assumptions that break under stress.
Trace bad inputs, retries, concurrent actions, and partially completed operations through the code.
Weight the user focus heavily, but report any other material issue you can defend.
</review_method>

<finding_bar>
Material findings only — no style, naming, or speculative concerns without evidence.
Each finding answers: what goes wrong, why this code path is vulnerable, likely impact, and the concrete change that reduces the risk.
</finding_bar>

<grounding_rules>
Be aggressive, but stay grounded.
Every finding must be defensible from the repository context or your tool outputs.
Do not invent files, lines, code paths, or runtime behavior you cannot support.
If a conclusion rests on an inference, say so and keep the confidence honest.
</grounding_rules>

<calibration_rules>
One strong finding beats several weak ones. Do not dilute serious issues with filler.
If the change looks safe, say so directly and return no findings.
</calibration_rules>

<structured_output_contract>
Return: a terse ship/no-ship summary, then findings ordered by severity, each with file, line range, what-goes-wrong, impact, confidence (0-1), and a concrete recommendation.
</structured_output_contract>

<final_check>
Each finding must be adversarial rather than stylistic, tied to a concrete code location, plausible under a real failure scenario, and actionable.
</final_check>
```
