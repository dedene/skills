# CLI Quality Loop

Phased loop for taking one CLI from research to shipped, with timeboxes and gates. Use the Fast Path for most builds; switch to the Managed Path when the work needs pause/resume or spans multiple sessions.

## Fast Path

| Phase | Timebox | What to do | Artifact |
| --- | --- | --- | --- |
| 0 Resolve + Reuse | 1-3 min | Find existing repo, docs, spec, WSDL, Postman collection, HAR, tokens, prior work, package manager, release path. | Source map |
| 1 Research Brief | 5-10 min | Identify API/product, primary users, real jobs, auth, rate limits, pagination, dangerous writes, data gravity, and "why this CLI should exist." | Brief |
| 2 Ecosystem Scan | 5-10 min | Inspect official CLIs, SDKs, MCPs, Postman examples, community wrappers, and Peter's closest local CLIs. Capture features to match or consciously skip. | Ecosystem notes |
| 3 Discovery Gate | 2-5 min | If docs are incomplete, capture HAR/browser traffic, WSDL metadata, sample XML/JSON responses, request headers, protection signals, rate-limit evidence. | `discovery/` notes |
| 4 Docs Parity Gate | 5-15 min | Build a command-to-doc matrix. Each planned command must trace to primary docs, a spec/WSDL operation, Postman request, HAR finding, or documented example. | `docs/docs-parity.md` |
| 5 Scaffold | 1-2 min | Create the smallest buildable slice proving binary name, auth/config shape, transport, one command, output, tests, Makefile. | Buildable repo |
| 6 Build The Useful CLI | 10-20 min per slice | Add commands that represent user workflows, not just endpoint wrappers. Include workflow commands once data shape is understood. | Command set |
| 7 Shipcheck | 3-8 min | Run fmt/lint/test/build, help/version smoke, doctor, output contract tests, and fixture/live read-only verification. | Proof block |
| 8 Live Smoke | 2-5 min | With credentials, run safe read-only commands at low limits. For writes, use `--dry-run` or sandbox accounts only. | Smoke log |

## Managed Path

For larger CLIs or work that must pause/resume: run the Fast Path phases above, but write each phase's artifact to disk (per Artifact Rules below) so any session can pick up where the last one stopped. Add these gates after the build phases:

1. **Enrich**: collect missing docs, sample payloads, fixtures, auth/rate-limit clarifications; then refactor/extend without losing hand-authored behavior.
2. **Review**: dogfood, verify, output review, command grammar review.
3. **Agent readiness**: JSON/no-input/read-only/compact/errors/completions.
4. **Comparative**: compare against the best existing way to perform the same job.
5. **Ship**: release config, Homebrew, README, install smoke.

## Docs Parity Gate

Build a command-to-doc matrix before accepting a command into the shipped surface:

```text
command | primary source | operation | auth/session | request fields | response fields | paging/rate limits | errors | proof
```

For each command:

- Link the exact primary source: docs URL/section, OpenAPI path, WSDL operation, Postman request, HAR evidence, or documented example.
- Verify method/path/SOAP action, namespace, envelope/body shape, headers, auth/session placement, required and optional params, pagination, rate limits, and documented error cases.
- Verify the implementation uses only documented response fields in table/JSON/plain output, or records why an observed field is provisional.
- Add fixture/golden tests for request payloads and output mapping when the examples are stable enough to encode.
- Record discrepancies when docs and live behavior disagree. Name which source is trusted for the shipped behavior.

The gate fails when a command cannot be traced to docs or discovery provenance.

## Artifact Rules

Artifacts matter only when they improve the next phase. Keep them short and factual:

- `docs/research/<date>-brief.md`: identity, jobs, auth, rate limits, scope.
- `docs/research/<date>-ecosystem.md`: features to match, skip, or defer.
- `docs/discovery/`: WSDL, Postman, HAR notes, sample responses, warnings.
- `docs/proofs/<date>-docs-parity.md`: command-to-doc matrix, discrepancies, provisional behavior.
- `docs/proofs/<date>-shipcheck.md`: commands run, results, gaps.

Do not create ceremony files for their own sake. A one-page brief beats a pile of stale documents.

## When The API Is SOAP

SOAP APIs often need more hand shaping than generators provide:

- Treat WSDL as source material, not a full product design.
- Test generated XML/envelopes with golden files.
- Keep session/auth ceremony hidden behind `internal/auth` and `internal/api`.
- Expose user concepts in commands, not SOAP method names.
- Add `doctor` early because credentials, TLS, domains/admin IDs, and permissions often fail before business logic.
