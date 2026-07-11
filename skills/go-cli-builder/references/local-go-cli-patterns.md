# Peter's Go CLI Patterns

These patterns come from `nimbu-go-cli`, `frontapp-cli`, `harvest-cli`, `raindrop-cli`, and `~/Development/Personal/go-cli-development-guide.md`.

## Framework And Dependencies

- Prefer **Kong** for command parsing in new CLIs.
- Use `github.com/99designs/keyring` for OS credential storage.
- Use `gofumpt`, `goimports`, `golangci-lint`, `go test ./...` gates.
- Use GoReleaser for GitHub releases and Homebrew formula updates.
- Use CGO on Darwin when keychain support requires it; keep Linux/Windows CGO off where possible.

## Project Layout

```text
cmd/<binary>/main.go
internal/api/
internal/auth/
internal/cmd/
internal/config/
internal/errfmt/
internal/output/
internal/ui/        # only for dashboards, wizards, spinners, pickers
```

Nimbu adds domain packages when the CLI has real subsystems: `themes`, `notifications`, `devserver`, `devproxy`, `apps`, `updatecheck`. Add such packages only when they hide real complexity from `internal/cmd`.

## Makefile Pattern

Expected targets:

- `build`: compile to `bin/<binary>` with version/commit/date ldflags.
- `run`: build then run, forwarding args after `make run -- ...`.
- `tools`: install pinned local tools into `.tools/`.
- `fmt`: goimports + gofumpt.
- `fmt-check`: format then require clean diff, or report needed formatting.
- `lint`: golangci-lint.
- `test`: `go test ./...`.
- `ci`: fmt-check + lint + test.

## Release Pattern

Use `.goreleaser.yaml` v2:

- Set `project_name`.
- Build Darwin separately with `CGO_ENABLED=1` when keyring needs it.
- Build Linux/Windows with `CGO_ENABLED=0`.
- Inject version/commit/date into `internal/cmd`.
- Archive as `tar.gz`, Windows as `zip`.
- Generate checksums.
- Configure `brews` against the correct tap, with `bin.install "<binary>"` and a minimal version/help test.

## Auth And Config

- Prefer browser OAuth or API key/session login commands that store long-lived secrets in OS keyring.
- Allow env-token escape hatches for CI and agents.
- Do not create keyring directories before opening the backend; that can force file backend on macOS.
- Keep config non-secret: default site/account/domain/admin IDs, output defaults, base URL.
- Include `auth status`, `auth logout`, and preferably `auth doctor`.

## Agent And CI Controls

Good global flags/envs:

- `--json`, `--plain` or TSV, optional `--fields`/`--select`.
- `--no-input` or env equivalent.
- `--readonly` for agent sessions.
- `--no-progress` for CI.
- `--debug` for HTTP traces, with secrets redacted.
- `--force` for destructive operations.
- `--dry-run` for write previews.

## Command Grammar

Use flag-first resource identity:

```bash
nimbu channels entries update --channel blog --entry welcome title="Welcome" published:=true
```

Avoid older positional forms:

```bash
nimbu channels entries update blog welcome title=Welcome
```

Payload rules:

- `key=value`: string.
- `key:=json`: typed JSON.
- `key=@file.txt`: raw file content string.
- `key:=@file.json`: parse JSON from file.
- Dot paths are okay for shallow nesting.
- `--file` and inline assignments are mutually exclusive.

## Output Contracts

- Human table output by default.
- JSON must be stable enough for agents and scripts.
- Plain/TSV is useful for shell pipelines.
- Preserve full URLs or IDs in structured output even when table output truncates.
- Add list footers or hints when output is bounded.

## Testing Focus

High-value tests:

- Command grammar and help examples.
- Auth storage and logout/status edge cases.
- Error contract and exit codes.
- Output formatting, table width, time/date formatting.
- Inline assignment parsing and `--file` mutual exclusion.
- API transport retries, rate-limit handling, pagination.
- Golden XML/SOAP payloads or JSON request payloads.
- Docs parity matrix for command-to-operation coverage.
- Fixture tests that prove request fields and output fields match documented examples.
- README/help examples kept in sync with documented API names and constraints.
- Release binary name consistency.

## Binary Name Consistency

Verify the same binary name across:

- `cmd/<binary>/`
- `Makefile` `BIN` and `CMD`
- Kong `Name`
- README examples
- error messages
- User-Agent
- `.goreleaser.yaml`
- Homebrew formula test
- config directory and env var prefix
