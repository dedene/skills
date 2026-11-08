---
name: untangle-codebase
description: Audit or refactor a codebase or subsystem to reduce hidden coupling, scattered business rules, and unnecessary abstractions while preserving behavior and framework conventions. Use when asked to untangle, de-spaghetti, or reduce coupling in a codebase; when code is tangled or hard to change, tech debt has piled up, or one change needs edits in many places; or for an architecture cleanup or broad structural refactor. Not for incidental cleanup during an unrelated feature or a defect-only diff review.
---

# Untangle Codebase

Make future changes easier to locate, reason about, and verify. Improve boundaries where code demonstrates a problem; leave healthy structure alone. Fewer files, fewer branches, and more abstractions are not success criteria. Success looks like this: one rule has one owner, a change that used to touch five files now touches one, and a reader can find where a behavior lives without tracing callbacks across the tree.

## Scope and operating mode

Infer the mode from the request: an audit or assessment produces findings without changing application code; a request to untangle or refactor includes implementation and verification. A requested area limits the work. For a whole-codebase request, inventory the whole first-party system and work through its supported findings in coherent increments; report any areas not inspected deeply.

Carry existing authorization forward. Do not add an approval checkpoint for routine local refactoring. Ask only when an unresolved behavior or compatibility decision materially changes the outcome. Toolchain upgrades, architecture migrations, unrelated bug fixes, bulk comment/test deletion, publication, and production changes are not implied by this skill.

## 1. Discover the system and its boundaries

Read applicable repository instructions, status, manifests, build definitions, CI configuration, and relevant documentation. Identify:

- Languages, framework versions, runtime settings, build targets, and package/workspace boundaries.
- Application kinds: web service, UI application, CLI, library, worker, or data pipeline. A repository may contain several.
- Entrypoints, public contracts, persistence, external services, generated code, and runtime registration.
- Documented build/test commands and the disposable environments they require. Establish relevant baseline results before editing; distinguish existing failures from new ones.

Read only the profiles for the affected components:

| Component | Reference |
| --- | --- |
| Ruby on Rails | [Rails](references/rails.md) |
| Go services, CLIs, and libraries | [Go](references/go.md) |
| Swift macOS apps and packages | [Swift/macOS](references/swift-macos.md) |
| JavaScript/TypeScript frontends and backends | [JavaScript/TypeScript](references/javascript-typescript.md) |
| Python web apps, tools, and pipelines | [Python](references/python.md) |
| PHP applications and extensions | [PHP](references/php.md) |
| Java/Kotlin backend applications | [JVM/Spring](references/jvm-spring.md) |
| C#/.NET applications and workers | [.NET](references/dotnet.md) |
| Rust services, CLIs, and libraries | [Rust](references/rust.md) |

Profiles are conditional guidance, not instructions to migrate to their named frameworks. Use the general workflow for other stacks, consult version-matched primary documentation when necessary, and state what could not be verified.

Trace representative operations from entrypoint through state changes and effects. Use symbol navigation, targeted searches, and existing tooling before building new analyzers. Import graphs show only part of the system: also follow callbacks, events, reflection, generated bindings, schemas, queues, configuration, and process boundaries. If making an outline, do it in scratch space; never strip bodies from working source files.

On a large system where delegation is available and allowed, map components in parallel: give each agent one component and this section's questions, require file-level evidence, then combine the results yourself. Cross-component links are where the important findings usually are, so look for them in the combined map rather than in any single report.

## 2. Establish evidence of change friction

Ask one question of each relationship: should these pieces change together? A finding is a place where the code answers it wrong:

- **Hidden links:** pieces must change together, but nothing shows it. Copies of a rule, value, schema, or state transition; a module that reads state another module sets; one feature spread across layers or folders; a call order, convention, or resource ownership that callers must just know.
- **Needless links:** pieces are tied together but change for different reasons. Callers that depend on another component's internals; stable code importing volatile code; a general function with a parameter only one workflow understands; a shallow interface that changes whenever its internals do.
- **Surplus:** pieces with no reason of their own to change. Pass-through wrappers, extension points or configuration for variation that never occurs, code nothing uses. Removal must have a concrete benefit and lose no needed boundary.

Treat special cases (an `if` for one value, a parameter for one caller, a swallowed exception) as clues to a requirement the design never modeled. Name that requirement before deciding whether to keep, generalize, or remove the case.

Use recent Git history to test hypotheses about what changes together. This counts file pairs that co-changed in commits of at most 20 files; scope the pathspec to the area under review:

```sh
git log --since=12.months --no-merges --name-only --format=format:@ -- . |
awk 'function flush(){ if (n > 1 && n <= 20) for (i = 1; i < n; i++) for (j = i + 1; j <= n; j++) c[f[i] < f[j] ? f[i] "  " f[j] : f[j] "  " f[i]]++; n = 0 }
     /^@/ { flush(); next } NF { f[++n] = $0 }
     END { flush(); for (p in c) if (c[p] > 2) print c[p], p }' | sort -rn | head -30
```

Exclude lockfiles, generated files, mechanical renames, and formatting commits from the inference. Pairs across components with no visible dependency are the most interesting. Similar code or frequent co-change alone does not prove shared responsibility; a test and its subject, or a manifest and its README, are expected to move together.

For each proposed finding, record:

1. **Evidence:** locations and a concrete change or failure scenario exposing the problem.
2. **Consequence:** duplicated decisions, surprising effects, fragile sequencing, or excessive unrelated edits.
3. **Correction:** the smallest coherent boundary or ownership change, including its tradeoff.
4. **Preservation:** behavior/contracts that must remain and how to verify them.

Example:

```markdown
### Refund eligibility is decided in three places
- **Evidence:** `app/models/order.rb:88` (`refundable?`, 30 days), `app/controllers/refunds_controller.rb:24` (inline 30-day check), `app/jobs/auto_refund_job.rb:12` (31-day check). Commits `a1b2c3d` and `e4f5a6b` changed the window in two of the three.
- **Consequence:** changing the refund window takes three coordinated edits; the job already disagrees by a day.
- **Correction:** make `Order#refundable?` the owner and call it from the controller and job. Tradeoff: the job loads each order instead of filtering in one query.
- **Preservation:** refund responses and job results for orders aged 29, 30, and 31 days. Add characterization tests first; ask whether day 31 is intended before choosing which behavior survives.
```

Rank by demonstrated impact and frequency, confidence, and change risk. Separate supported findings from questions. A long file, a one-implementation interface, a retry, or a framework convention is not a finding by itself.

## 3. Choose corrections that fit the project

Prefer an existing idiomatic boundary over introducing a new architecture. Bring one rule under one owner where that reduces coordination; keep distinct rules separate even when their code currently matches. Logical ownership can span conventional folders. Do not force every feature into a single directory or every dependency behind an interface.

Group findings when one correction removes their shared cause. Explain which relationships it fixes and verify each affected consumer; avoid separate patches that preserve the same underlying coordination problem.

Before removing an apparent exception, identify the requirement it serves: retries, compatibility branches, locks, caches, availability checks, and adapters may be essential. Before removing apparently unused code, check exports, reflection, framework discovery, configuration, generated callers, platform variants, and consumers outside the repository. An empty search result is insufficient evidence.

Preserve contracts appropriate to the application:

| Application | Contracts to trace through a refactor |
| --- | --- |
| Libraries/SDKs | Public symbols, import paths, serialization, error behavior, supported versions, external consumers |
| CLIs/automation | Flags, stdout/stderr, exit codes, configuration precedence, signals, cleanup |
| Web/services | Routes, authorization, middleware order, transaction boundaries, response/event schemas |
| UI/native apps | State identity, lifecycle, focus, navigation, accessibility, thread/actor and process boundaries |
| Workers/pipelines | Ordering, delivery semantics, idempotency, retries, cancellation, checkpoints, data formats |

For mixed stacks, follow contracts across the boundary: a Rails endpoint and its TS caller, or a Rust component and its Swift consumer, belong in the same analysis when the change crosses them. Update generators and their inputs rather than editing generated output as the source of truth.

Keep decisions beside findings in the conversation or the repository's existing task document. Use scratch space for temporary inventories and tool output. Do not invent a persistent ledger or add repository documentation unless the task needs it.

## 4. Implement and verify incrementally

In audit mode, stop with the ranked findings, proposed corrections, and coverage limits. In refactor mode, complete the supported in-scope corrections:

- Make one coherent structural change at a time; inspect affected callers and registration paths.
- Keep each correction separately revertible: one commit per correction when the repository workflow permits, so a later regression can be bisected and backed out without unwinding unrelated work.
- Where coverage is missing, add a focused behavioral or characterization test before a risky move. Do not encode an accidental bug as desired behavior; clarify intent if preserving and correcting it would produce different contracts.
- Preserve tests as the regression safety net. Adapt tests coupled to changed internals when necessary, retaining their behavioral assertions. Shared setup or similar assertions at different boundaries do not justify deleting tests.
- Retain comments that explain contracts, invariants, compatibility, or operational constraints. Avoid a separate comment-cleanup campaign.
- Run checks that exercise the affected behavior after each increment, then complete the relevant repository gates. Include rollback/failure, cancellation, lifecycle, or platform configurations when the change affects them. Compilation alone does not establish behavioral equivalence.
- Exercise changed UI flows with the appropriate browser or native tooling. Use disposable data and safe service substitutes; a test environment variable alone does not prove isolation.

Fix regressions introduced by the refactor. Record unrelated baseline failures without expanding scope. If a required check is unavailable, continue independent safe work, state the exact blocker, and do not claim the affected behavior is verified. Do not run an unverified high-risk transformation through the rest of the codebase.

## 5. Finish against evidence

Review the final diff against the findings and preservation requirements. Revisit affected dependency and registration paths, and check whether the proposed correction actually reduced the original coordination burden. Do not replace a small problem with a general framework.

For broad changes, an independent review can help when delegation is available and allowed. Give reviewers bounded areas and require file-level evidence; review their findings rather than treating consensus as proof. A single-agent run remains valid.

Finish when supported findings within scope are resolved or explicitly deferred with reasons, required relevant checks have passed or their concrete blockers are reported, and no regression introduced by the work remains unexplained. Do not search indefinitely for architectural perfection or silently declare a partially inspected repository clean.

Report what became easier to change, the key corrections with file references, actual verification results, and retained exceptions or limitations. For an audit with no supported findings, say so without inventing work.

Adapted from [caldoai/skills: untangle-codebase](https://github.com/caldoai/skills/blob/main/skills/untangle-codebase/SKILL.md) (MIT).
