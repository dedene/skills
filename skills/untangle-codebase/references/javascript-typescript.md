# JavaScript and TypeScript

Use for JS/TS frontends, backends, and packages: React/Next.js, Vue/Nuxt, Svelte/SvelteKit, Angular, Node services, and monorepos. For Electron, React Native, or another native host, this profile covers shared JS/TS only; check the host's lifecycle, process bridges, and permissions in its own docs, and do not claim a browser check verifies the native app.

## Establish the context

- Read `package.json` (`scripts`, `type`, `exports`, `imports`, `sideEffects`, `engines`), the lockfile, workspace config, every `tsconfig*.json` including `references` and `paths`, framework and bundler config, and CI. Use the pinned runtime and package manager.
- Identify the installed framework major and its opt-in modes from config, not memory: Next.js App or Pages Router and `cacheComponents`; Nuxt directory layout and compatibility flags; Svelte runes or legacy components; Angular zoneless or zone.js, standalone or NgModule; React Compiler on or off. Conventions differ sharply between these modes.
- Classify each affected module by where it runs: browser, server render, server-only, proxy/edge, worker, build or test tooling. Record which modules are already imported across that line.
- In a monorepo, separate private app code from published packages. A package's contract is its `exports` map, emitted types, and supported module formats, not its source tree.
- Use graph tooling the repo already has (`knip`, `dependency-cruiser`, `madge`, Nx or Turborepo graph) before tracing imports by hand. Do not install an analyzer to answer what targeted reads can.

## Trace more than imports

- File-based routing registers code by path and filename: Next.js `app/` segments (`page`, `layout`, `loading`, `error`, `route`) and `proxy.ts` (renamed from `middleware.ts` in Next.js 16); Nuxt `pages/`, `middleware/`, `server/`; SvelteKit `+page`, `+layout`, `+server`, `hooks.server`. A file with no importers may be a live route.
- Auto-imports and auto-registration hide edges: Nuxt `components/`, `composables/`, `utils/`, and top-level `plugins/` files (run in filename order, scoped by `.client`/`.server` suffix); Angular providers in route configs and `ApplicationConfig`; Vue and Angular plugins installed at bootstrap. Search config and naming conventions, not only import statements.
- Directives change where code runs and what it exposes: `'use client'` pulls the module and everything it imports into the client graph; a file-level `'use server'` makes every export a client-callable server endpoint; `'use cache'` gives a result a lifetime and keys it on its arguments and captured values.
- Side-effect imports (polyfills, CSS, registration modules, `server-only`) and barrel files carry evaluation order. `sideEffects` in `package.json`, `import type`, and `verbatimModuleSyntax` decide whether such an import survives the build.
- Follow non-static edges: computed `import()`, `import.meta.glob`, DI tokens, event emitters, message channels, and clients generated from OpenAPI, GraphQL, or ORM schemas. Change the generator input, not the output.
- Treat effects, subscriptions, timers, listeners, and in-flight requests as resources with an owner and cleanup path. Trace unmount, navigation, cancellation, HMR, and React Strict Mode double mounting.
- Trace data ownership separately from rendering: server caches, client query caches, URL state, form drafts, and persisted records have different lifetimes on purpose.

## Preserve these boundaries

- **React:** component type, tree position, and `key` define state identity. Keep hook order and effect cleanup intact. With React Compiler on, memoization follows the Rules of React; the React docs advise leaving existing `useMemo`/`useCallback` in place unless tested, because removing them changes compiled output and can make effects fire more or less often.
- **Next.js App Router:** keep secrets and DB clients in server-only modules (mark them with `import 'server-only'`); only `NEXT_PUBLIC_` env vars reach the client. Props passed into Client Components must be serializable. `cookies`, `headers`, `params`, and `searchParams` are async and request-scoped. Confirm which caching model is active (Cache Components or the previous model) before moving data access across a cached function or component.
- **Vue/Nuxt:** pass reactive sources across an extraction as refs or getters (`useX(() => prop)`), not unwrapped values. In SSR code never move `ref()` state to module scope; Nuxt warns it is shared across requests. Use `useState` or the existing store, and keep that state serializable.
- **Svelte/SvelteKit:** runes outside components belong in `.svelte.js`/`.svelte.ts` files, and a reassigned `$state` variable cannot be exported; export an object or accessor functions instead. Passing or destructuring `$state` copies the value. Keep `load` free of side effects and server data out of module-level variables. SvelteKit rejects public code that imports server-only modules (`.server` files, `server` directories, private env) even through a re-export.
- **Angular:** provider location sets instance scope: `providedIn: 'root'` and app config give one shared instance, route providers scope to that subtree, component `providers` create one instance per component. Preserve signal reads in templates and the `computed`/`effect` graph. In zoneless or OnPush code, state changed outside signals, the async pipe, or `markForCheck` does not re-render.
- **Node services:** keep middleware order, error propagation, startup and shutdown hooks, and request scope (`AsyncLocalStorage`, per-request DI). Module-level values live for the process; a helper must not cache one user's data or credentials.
- **Packages:** preserve `exports` subpaths and conditions (`types`, `import`, `require`, `module-sync`, `browser`, `default`), the `type` field, and emitted `.d.ts` paths. Adding or narrowing `exports` blocks every undeclared deep import, including `package.json`. Do not fold a CJS/ESM migration into a structural refactor.

## Typical refactoring traps

- Moving a shared helper into a module that a `'use client'` file imports drags the helper's whole import graph into the client bundle; with a DB client or secret in that graph, the build fails or ships server code. Moving it into a `'use server'` file instead publishes it as an endpoint that takes untrusted arguments.
- Moving a Server Function to another route or narrowing the `proxy.ts` matcher silently removes Proxy auth coverage, because Server Functions are POSTs to the route that uses them. Keep authorization inside each Server Function.
- Inserting a wrapper element, swapping between two component types at the same position, or generating keys during render resets component state; dropping a stable `key` when extracting a list item makes items share state.
- Collapsing a barrel or converting imports to `import type` drops side-effect registration or reorders module evaluation; a circular import that happened to work through the barrel can then throw a TDZ `ReferenceError` at load.
- Moving per-request data into a module-level cache, a module-scope Vue/Svelte store, or an Angular root service leaks one user's data into another request. The reverse, moving a root provider into component `providers`, silently creates multiple instances.
- Adding top-level `await` to an ESM module, or to anything in its import graph, breaks CommonJS consumers that `require()` it with `ERR_REQUIRE_ASYNC_MODULE`, while types and ESM tests still pass.

## Verification candidates

- Prefer the repository's scripts and CI jobs for typecheck, lint, unit, e2e, and build. Run them for each affected workspace and for every consumer of a changed package.
- Typecheck with `tsc -b` or the repo's script when project references exist; `tsc --noEmit` against a solution-style root `tsconfig.json` with `"files": []` checks nothing. Passing types do not prove runtime resolution, bundling, or server/client placement.
- Run the production build (`next build`, `nuxt build`, `vite build`, `ng build`). It catches server-only import leaks, serialization errors, prerender and caching errors, and route conflicts that dev mode and unit tests miss. It does not exercise request scope or authorization.
- Framework checks where configured: `eslint-plugin-react-hooks` (its recommended presets include the React Compiler rules), `vue-tsc`, `svelte-check`, Angular strict templates. They catch rule violations, not behavior changes.
- If present: `knip` for unused files, exports, and dependencies (misses convention-based, string, and dynamic references unless its framework plugins are configured); `dependency-cruiser` or `madge` for cycles and forbidden edges (static imports only). Treat "unused" output as leads, not proof of dead code.
- For published packages: `npm pack --dry-run` to list shipped files, and `publint` or `@arethetypeswrong/cli` when available to check `exports` and type resolution under `import`, `require`, and different `moduleResolution` modes. Then install the packed tarball in a real consumer.
- For UI moves, drive the affected route in a browser: state retention and reset, back/forward, loading and error boundaries, focus and keyboard. For async ownership, unmount mid-request and remount repeatedly without duplicate listeners. For request scope, run two concurrent sessions as different users.

## Primary references

Use the docs for the installed version when behavior differs.

- [React: preserving and resetting state](https://react.dev/learn/preserving-and-resetting-state)
- [Next.js: server and client components](https://nextjs.org/docs/app/getting-started/server-and-client-components)
- [SvelteKit: state management](https://svelte.dev/docs/kit/state-management)
- [Angular: hierarchical dependency injection](https://angular.dev/guide/di/hierarchical-dependency-injection)
- [Node.js: packages and module systems](https://nodejs.org/api/packages.html)
