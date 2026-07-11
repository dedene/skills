---
name: go-cli-builder
description: Use when building, scaffolding, or substantially expanding Go CLIs for APIs, SaaS products, SOAP/OpenAPI/Postman/HAR-backed integrations, Homebrew-distributed tools, or Kong-based command surfaces, following a phased research-to-ship quality loop.
---

# Go CLI Builder

Build production-grade Go CLIs in Peter's house style: useful vertical slices first, agent-friendly command contracts, strong auth/config/output boundaries, and shippable Homebrew distribution.

## Start Here

1. Read local context before design:
   - Existing repo: `go.mod`, `Makefile`, `.goreleaser.yaml`, `README.md`, `cmd/`, `internal/`, tests, docs, current command grammar.
   - New repo: inspect `~/Development/Personal/go-cli-development-guide.md`, then sample the closest existing CLIs: `nimbu-go-cli`, `frontapp-cli`, `harvest-cli`, `raindrop-cli`.
2. If the target API facts may have changed, verify current primary docs before designing auth, rate limits, endpoint scope, or dependency versions.
3. Make docs parity a gate: before implementation, create a command-to-doc matrix that traces each planned command to the primary operation, method/path or SOAP action, auth/session rule, required fields, response fields, pagination/rate limits, and documented errors.
4. Read `references/cli-quality-loop.md` when shaping scope, phases, artifacts, or verification gates.
5. Read `references/local-go-cli-patterns.md` before scaffolding, changing command grammar, auth/config/output, release setup, or tests.

## Default Shape

Prefer a hand-shaped Go CLI over generated breadth. Start with one valuable vertical slice that proves auth, transport, output, errors, tests, and release shape.

Use this package layout unless the repo already has stronger conventions:

```text
cmd/<binary>/main.go
internal/api/       # clients, transport, typed API errors, resource methods
internal/auth/      # login/token/session/keyring/env handling
internal/config/    # config files, profiles/accounts, paths
internal/cmd/       # Kong commands and command wiring
internal/output/    # table/json/plain, colors, terminal helpers
internal/errfmt/    # actionable user-facing errors
internal/ui/        # optional TUI/wizards/spinners only when useful
```

Use Kong for new CLIs, matching `nimbu`, `frontcli`, `harvest`, and `raindrop`. Use Cobra only when the existing repo already uses Cobra or interoperability demands it.

## Fast Path

| Phase | Purpose | Output |
| --- | --- | --- |
| 0 Resolve + Reuse | Existing repo, docs/spec/HAR/Postman/WSDL, tokens, prior CLIs | source map + constraints |
| 1 Research Brief | API identity, user jobs, auth, rate limits, product thesis | short brief |
| 2 Ecosystem Scan | Existing CLIs/MCPs/SDKs, Nimbu/frontcli/harvest patterns | ecosystem notes |
| 3 Discovery Gate | API quirks, sampled responses, SOAP/XML/HAR provenance | discovery notes |
| 4 Docs Parity Gate | planned commands checked against primary docs/spec/WSDL/Postman/HAR evidence | command-to-doc matrix |
| 5 Scaffold Slice | Small working CLI slice | buildable repo |
| 6 Build Useful CLI | workflow commands, safe mutations, output contracts | real commands |
| 7 Shipcheck | fmt/lint/test, help/version, doctor, read-only smoke | proof block |
| 8 Distribution | GoReleaser, Homebrew tap, install docs | releasable binary |

Build one excellent CLI; add catalog or marketplace machinery only if the user explicitly asks for a family of CLIs.

## Command Contract

- Keep identity in flags, payload last: `tool invoices get --invoice 123 --json`, not hidden positional ID chains.
- Prefer explicit resource words over generic wrappers. Add raw API escape hatches only after core workflows are stable.
- For create/update, support `--file` or clear inline assignments; make them mutually exclusive.
- Default to human table output; always support structured `--json`. Add `--plain`/TSV when shell pipelines matter.
- Add `--no-input`, `--readonly` or env equivalent, `--dry-run` for mutating previews, and `--force` for destructive actions.
- Errors must name the failed command/flag/resource and the next corrective command when possible.

## Verification Bar

Before handoff, run the repo gate: usually `make ci` or `make fmt-check lint test`. Also smoke:

```bash
make build
./bin/<binary> --help
./bin/<binary> version 2>/dev/null || ./bin/<binary> --version
./bin/<binary> auth doctor 2>/dev/null || true
```

For bug fixes or durable behavior, add regression tests. For API integrations, prefer read-only live smoke when credentials are available; otherwise use fixture servers, golden SOAP/XML payloads, or recorded responses.

Docs parity is a release gate, not a research note:

- Every shipped command must link to a primary source section, WSDL operation, OpenAPI path, Postman request, HAR finding, or documented example.
- Verify method/path/SOAP action, auth/session placement, required and optional params, request body/XML, response fields used by output, pagination/rate limits, and error cases.
- Cover request builders and output mappers with fixtures or goldens based on documented examples when practical.
- Commands based only on observed behavior must be marked provisional with provenance and warnings.

## Common Mistakes

- Starting with every endpoint instead of a useful slice.
- Putting secrets in config files instead of OS keyring/env.
- Making JSON a separate afterthought instead of a first-class output contract.
- Treating docs parity as optional research instead of a release gate.
- Letting command grammar drift between examples, README, tests, completion, and GoReleaser binary name.
