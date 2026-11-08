# Go

Use for Go services, CLIs, and libraries, in single modules or multi-module workspaces. Apply the matching profile to non-Go code reached through cgo, generated clients, or embedded frontends.

## Establish the context

- Read `go.mod` (`go`, `toolchain`, `tool`, `godebug`, `replace`, `retract`), any `go.work`, Makefile or task runner, and CI. The `go` line sets language semantics per module (per-iteration loop variables start at `go 1.22`); the main module's `go.mod`, or `go.work` in workspace mode, also sets default GODEBUG behavior.
- Distinguish one module from a workspace. Without `go.work`, `./...` at the root skips nested modules; CI may build each module with `GOWORK=off` against published versions of its siblings.
- Record supported GOOS/GOARCH, build tags, cgo, generated sources (`//go:generate`, protobuf, sqlc, `wire_gen.go`), and `//go:embed` assets before calling code unused or duplicated.
- Map package consumers, exported declarations, `internal/` boundaries, `main` packages, and whether other repositories import the module. A file boundary is not a package boundary.
- Use the pinned tools (`tool` directives run via `go tool`, `tools.go` blank imports, versions in Makefiles). Do not run `go mod tidy`, regenerate, or edit the `go`/`toolchain` lines to make the tree look cleaner. If a move needs a `require` change, make the minimal one and review the `go.mod`/`go.sum` diff.

## Trace more than imports

- Follow `init` functions and blank imports that write to global registries: `database/sql` drivers, `image` formats, `net/http/pprof` and `expvar` handlers on `DefaultServeMux`, package-level `flag` definitions, the Prometheus default registry, codec and plugin maps.
- Package initialization follows the import graph; since Go 1.21, independent packages initialize in import-path order. Code that depends on ordering not expressed by an import changes behavior when a package is renamed or moved.
- Follow links no import shows: implicit interface satisfaction, `var _ I = (*T)(nil)` assertions, type switches, `errors.As` targets, reflection, struct tags (`json`, `db`, `yaml`), marshaler methods, and `//go:linkname` references from other packages.
- For dependency injection, trace the graph, not call sites. Wire generates `wire_gen.go` from `wireinject`-tagged injectors: edit the injector and regenerate with the pinned version (upstream is archived since 2025). Fx calls constructors only when an invoke needs them, runs `OnStart` hooks in append order and `OnStop` hooks in reverse.
- Trace who starts each affected goroutine, who cancels it, who closes its channels, and who waits for it, including error and early-return paths.
- Follow ownership of `*sql.Tx`, `*sql.Conn`, `*sql.Rows`, response bodies, files, and locks through helpers. A `Tx` holds one connection until commit or rollback, and canceling its `BeginTx` context rolls it back.
- `//go:embed` patterns resolve relative to the package directory and cannot contain `..`. Moving the file moves or breaks the asset.
- Inspect build-tagged files, `_test.go` files (including `export_test.go` shims), and generated counterparts before consolidating apparent duplication; they may implement one contract for different environments.

## Preserve these boundaries

- Keep packages cohesive around a capability. Do not split per type, add `utils`/`common` hubs, or impose a layered service/repository layout on working code.
- Define interfaces at the consumer from what it uses. A one-implementation interface is neither automatically needed nor automatically redundant. Keep returning concrete types where the package already does.
- For packages importable outside the repo, preserve import paths, exported names, signatures (including assignability to function types), interface method sets, struct comparability, zero-value behavior, and error identity (sentinels, `%w` chains, `errors.Is`/`As` targets). Adding a method to an exported interface or a variadic parameter to an exported function breaks callers.
- When moving an exported type, leave an alias (`type T = newpkg.T`), not a defined type (`type T newpkg.T`), which drops methods and type identity. Forward functions and constants too. A `//go:fix inline` directive lets gopls or `go fix -inline` (Go 1.26+) migrate callers later, if the project's toolchain supports it.
- Keep `internal/` placement meaningful: moving a package changes which trees may import it.
- Pass the caller's `context.Context` through extracted code. Do not substitute `context.Background()` or store a request context in a struct that outlives the request. An incoming request's context is canceled when `ServeHTTP` returns, so work that outlives the handler needs its own owned context and shutdown path.
- Preserve middleware order and use `ResponseWriter` and `Request.Body` only within `ServeHTTP`.
- Preserve transaction scope. Code that takes `*sql.DB` runs outside a caller's `*sql.Tx`, possibly on another connection; a shared querier interface hides which one a helper received.
- Keep seams that isolate platform code, external systems, or distinct lifetimes when they serve a demonstrated purpose.

## Typical refactoring traps

- Moving a `main` package or splitting a module changes which `go.mod` or `go.work` sets GODEBUG defaults (for example `httpmuxgo121` routing), and moving code into a module with an older `go` line changes loop-variable semantics. Compare `go list -f '{{.DefaultGODEBUG}}' ./cmd/<name>` before and after.
- Moving a blank import or registration into a shared package registers drivers, metrics, flags, or pprof handlers in every binary that imports it. Moving it out silently disables them in binaries that relied on the transitive import.
- Moving a `defer` into a helper closes the resource before the caller finishes. Hoisting it out of a loop holds connections, transactions, or files for the whole loop.
- Extracting a helper that returns a concrete `*MyError` as `error` turns a nil result into a non-nil interface. Rewrapping with `%v` instead of `%w`, or adding a wrapper type, breaks `errors.Is`/`As` in callers.
- Folding fields into an embedded struct changes promoted methods, interface satisfaction, and JSON shape; turning nil slices into empty ones changes `null` to `[]`. Switching value and pointer receivers changes method sets, and copying a struct that holds a `sync.Mutex` splits the lock.
- Merging workers or pipelines changes channel backpressure, shutdown order, and which error reaches the caller. `errgroup.WithContext` cancels siblings on the first error; a plain `sync.WaitGroup` does not.

## Verification candidates

Prefer the repository's documented commands, make targets, and CI matrix.

- `gofmt` and `go vet`, or the configured `golangci-lint`/`staticcheck`, on affected packages. Vet catches copied locks, `%w` misuse, and misplaced `WaitGroup.Add`; it proves nothing about behavior.
- `go build ./...` and `go test ./...` per module. In workspaces add `go test work` (Go 1.25+) or run each module with `GOWORK=off` to see what consumers see. Include external `_test` packages and examples when exported APIs move.
- Build and vet each supported GOOS/GOARCH and tag combination. Cross-compilation proves compilation, not runtime behavior on that platform.
- `go test -race` where the platform supports it, with `-count=1 -shuffle=on` to expose order-dependent tests. The race detector reports only races on executed paths; it does not find deadlocks or goroutine leaks. Use `testing/synctest` (Go 1.25+) for cancellation and timeout tests if the project's Go version allows it.
- gopls rename, extract, inline, and parameter moves. Rename and inline are type-checked and conservative; extract is less rigorous; all can drop comments; files outside the active build tags and GOOS are not checked.
- `apidiff` or `gorelease` (golang.org/x/exp, untagged) between base and head of a library. They report compile-level breaks only, not behavioral changes or every downstream break.
- `deadcode` (golang.org/x/tools/cmd/deadcode) for functions unreachable from `main`, with `-test` to include tests. It analyzes one build configuration and misses callers in assembly or via `//go:linkname`; do not treat its output alone as proof for exported library code.
- `go list -deps`, `go mod why`, and `go mod graph` to confirm package and module edges before and after a move.
- Run integration tests only against the documented disposable services and data.

## Primary references

- [Go Modules Reference: go.mod, go.work, version lines, package patterns](https://go.dev/ref/mod)
- [Keeping Your Modules Compatible](https://go.dev/blog/module-compatibility)
- [Go, Backwards Compatibility, and GODEBUG](https://go.dev/doc/godebug)
- [gopls refactorings and their limits](https://go.dev/gopls/features/transformation)
- [Go Code Review Comments: interfaces, contexts, goroutine lifetimes](https://go.dev/wiki/CodeReviewComments)
