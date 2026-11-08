# Rust

Use for Rust libraries, CLIs, services, and native components in mixed apps. For the consuming side of bindings (Swift, TypeScript via napi/wasm, Python via PyO3), also read that stack's profile.

## Establish the context

- Read the workspace and member manifests, `[workspace.dependencies]` and `[workspace.lints]`, `rust-toolchain.toml`, `rust-version`, `.cargo/config.toml` (aliases, targets, rustflags), lockfile policy, `build.rs` files, and CI.
- Record each crate's `edition`; it is per crate. Edition 2024 (stable since Rust 1.85) changes temporary drop scopes, return-position `impl Trait` lifetime capture, `unsafe extern` and `#[unsafe(...)]` attribute rules, and never-type fallback, so identical code can behave differently in two crates of one workspace.
- Record the resolver. It is workspace-wide and read only from the root manifest; `resolver = "3"` (default for edition 2024, Rust 1.84+) prefers dependency versions compatible with `rust-version`. Preserve the existing MSRV: do not use std APIs newer than it.
- Identify which crates are published or consumed outside the repo (crates.io, git dependencies, FFI, wasm, Python), plus binaries, proc macros, and generated code (bindgen, cbindgen, UniFFI, prost, sqlx offline data) with their inputs.
- Record supported targets and feature combinations from CI, including `--no-default-features`, `no_std`, and `cfg(target_os)` code. One default build does not cover conditional code.
- Inspect `build.rs` and proc macros before running unfamiliar builds: compilation executes project code and may need native toolchains or network access.

## Trace more than imports

- Public surface is set by reachability, not file layout. Follow `pub use` and glob re-exports, `pub(crate)` and `pub(super)`, `#[doc(hidden)] pub` items that macros depend on, and `#[macro_export]` macros, which always land at the crate root and reach helpers through `$crate::` paths.
- Follow trait and blanket impls, derive and proc-macro output (`cargo expand` when available), link-time registration (`inventory`, `linkme`), `#[no_mangle]` and `extern` symbols, and generated bindings consumed by other languages.
- Follow method resolution, not just names: which traits are in scope, `Deref` targets, and inherent methods decide which `foo()` is called. An inherent method with a trait method's name wins silently, and changing which traits a glob import brings into scope can switch or break the call.
- Integration tests in `tests/`, examples, and benches compile as separate crates against the public API, and `#[cfg(test)]` helpers exist only in unit-test builds. Check them before narrowing visibility or moving test-only code.
- Follow feature flow with `cargo tree -e features -i <crate>`. Features unify across every package in one build, so a crate can compile only because a sibling enables a feature it never declared. Resolver 2+ keeps build-dependency, proc-macro, and inactive-target features separate; dev-dependency features unify only when dev targets build.
- Trace ownership of guards, handles, transactions, buffers, and task state: where values move, borrow, or drop, including early returns, `?`, and panics. `let _ = m.lock()` drops the guard at once; `let _g = m.lock()` holds it to the end of scope.
- Follow async work through runtime entry points, `spawn`, `JoinHandle`, `select!`, timeouts, cancellation tokens, and shutdown. In Tokio, dropping a `JoinHandle` detaches the task rather than cancelling it, and running `spawn_blocking` work cannot be aborted.
- Read `unsafe` callers and callees together with their `// SAFETY:` comments. The invariants an unsafe block relies on often live in private fields and constructors, so module privacy is the soundness boundary.

## Preserve these boundaries

- Public paths and re-exports, trait contracts (including sealed traits), feature names, error variants, `#[non_exhaustive]` markers, `Display` and serde representations, and auto traits (`Send`, `Sync`, `Unpin`, `UnwindSafe`). Adding a private `Rc`, `RefCell`, or raw-pointer field silently removes `Send` or `Sync` for downstream users.
- Minimal visibility. Making a `pub(crate)` item `pub` so a split crate can reach it adds permanent API; prefer a private module with targeted `pub use`, or keep the code in one crate.
- Drop order: locals drop in reverse declaration order, struct fields in declaration order. Reordering fields or bindings, or extracting an expression into a helper, can change when a guard, connection, or temp file is released.
- Concrete types until variation is demonstrated. Do not add traits, generics, `dyn` objects, or builder layers for a single implementation, and do not erase useful types to shorten signatures.
- Ownership intent. Do not resolve borrow-checker friction with `.clone()`, `Arc<Mutex<_>>`, `'static` bounds, boxing, or `unsafe` until the intended owner is identified and the extraction is shown to cross a real lifetime boundary.
- Error contracts: the `From` impls that `?` relies on, `source()` chains, and variants callers match or log.
- Additive features. Do not move existing public code behind a new feature, add a feature to `default` that changes behavior, or pull `std` into a `no_std` path.
- FFI and unsafe contracts: `#[repr(C)]` and `#[repr(transparent)]` layout, public field order, symbol names, ABI, which side allocates and frees, thread affinity, and pinning. Since Rust 1.81 a panic escaping an `extern "C"` function aborts the process; unwinding requires `"C-unwind"` or `catch_unwind`.

## Typical refactoring traps

- Moving code between a 2021 and a 2024 crate changes temporary scope: in 2024, tail-expression temporaries drop before locals and `if let` scrutinee temporaries drop before `else`. A `MutexGuard` or `RefCell` borrow held into an `else` branch now releases earlier, while `match` scrutinee temporaries still live through every arm.
- Extracting a block that holds a `std::sync::MutexGuard` or `RefCell` borrow into an async helper can keep it across `.await`, making the future `!Send` or deadlocking; inlining a helper can widen a guard's scope the same way.
- Splitting a crate breaks coherence (an impl of a foreign trait for a type now in another crate violates the orphan rule; inherent impls must stay with the type), turns `pub(crate)` items into public API, and gives each new crate its own feature set. Moving a helper behind an exported macro breaks its `$crate::` path for downstream users.
- Wrapping an operation in a `select!` branch or `tokio::time::timeout` drops the losing future mid-progress. Tokio documents `read_exact`, `write_all`, `Mutex::lock`, and `Semaphore::acquire` as not cancellation-safe: partial data or queue position is lost.
- Consolidating feature-gated or `cfg(target_os)` implementations can make a crate rely on a feature only a sibling enables, or hide code a non-default target needs; `cargo build --workspace` passes while `cargo build -p <crate>` fails.
- Changing an error enum, adding a variant to an exhaustive enum, or replacing a concrete error with `Box<dyn Error>` or `anyhow::Error` breaks callers' `match` arms and `?` conversions even when `Display` output is identical.

## Verification candidates

- Prefer the repo's own cargo aliases, `just`/`make`/`xtask` targets, and CI matrix, with its exact feature, target, and toolchain flags.
- `cargo fmt --check`, `cargo clippy --all-targets` with the repo's lint config, `cargo test -p <crate>`, then the workspace gate. Compiling and lint-clean code proves nothing about drop timing, cancellation, or runtime behavior.
- `cargo nextest run` isolates each test in its own process but does not run doctests; pair it with `cargo test --doc`.
- `cargo hack check --each-feature` or `--feature-powerset --depth 2` runs packages one at a time, exposing features borrowed from siblings; `--no-dev-deps` catches dev-dependency feature leakage and `--rust-version` checks the declared MSRV. Do not default to `--all-features`: it can combine incompatible features and skips the no-default build consumers use.
- For published crates, `cargo semver-checks` compares against the crates.io release or `--baseline-rev`. It catches removed or moved items and many auto-trait and `non_exhaustive` changes, but not every type, generic, or lifetime change, feature-subset breakage, or behavior change.
- For unsafe or concurrency changes, use existing Miri (`cargo +nightly miri test`; it cannot run most foreign calls), sanitizers, or loom models, plus tests for release, cancellation, shutdown, and partial failure.
- For mixed apps, regenerate bindings from their sources and run the consumer's build and tests, not only the Rust crate.
- Keep toolchain, edition, resolver, and dependency upgrades out of a structural refactor; `cargo fix --edition` is a migration.

## Primary references

- [Cargo SemVer compatibility](https://doc.rust-lang.org/cargo/reference/semver.html)
- [Cargo features and feature unification](https://doc.rust-lang.org/cargo/reference/features.html)
- [Rust Reference: destructors and temporary scopes](https://doc.rust-lang.org/reference/destructors.html)
- [Rust 2024 edition guide](https://doc.rust-lang.org/edition-guide/rust-2024/index.html)
- [Tokio `select!` cancellation safety](https://docs.rs/tokio/latest/tokio/macro.select.html)
