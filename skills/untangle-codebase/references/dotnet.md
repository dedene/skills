# C# and .NET

Use for ASP.NET Core (minimal APIs, controllers, Razor Pages), Generic Host workers, and class libraries or NuGet packages. Treat Blazor and WPF/WinForms/MAUI as pointers only: their scopes follow circuits, components, or windows, so read their own lifetime docs before applying request-scoped guidance.

## Establish the context

- Read `global.json` (SDK pin, `rollForward`, `test.runner`), `.sln`/`.slnx`, `Directory.Build.props`/`.targets`, `Directory.Packages.props` (central package management), and each project's `TargetFramework(s)`, `Nullable`, `TreatWarningsAsErrors`, analyzers, and `InternalsVisibleTo`. Shared props decide what a moved file compiles under.
- Record the target-framework matrix and keep it. Behavior is version-specific: since .NET 10, all of `BackgroundService.ExecuteAsync` runs off the startup path, while earlier its synchronous prefix blocked other hosted services from starting. Do not retarget during a refactor, even when a target framework is near end of support.
- Identify the host behind each entry point: `WebApplication`, `Host.CreateApplicationBuilder` worker, test host, or a library with no host. "Scoped" means something different in each.
- Treat a project as a published contract when it has `IsPackable`, `EnablePackageValidation`/`PackageValidationBaselineVersion`, `PublicAPI.Shipped.txt`/`PublicAPI.Unshipped.txt`, or `IsTrimmable`/`IsAotCompatible`.
- List source generators in use: System.Text.Json `JsonSerializerContext`, `[LoggerMessage]`, `[GeneratedRegex]`, the configuration binding generator, the minimal API request delegate generator, EF compiled models (`dotnet ef dbcontext optimize`). Their inputs are the source of truth; `obj/` output is not.

## Trace more than imports

- **Registration:** Follow every `Add*` extension method, `TryAdd*`, `Replace`, `TryAddEnumerable`, keyed registrations (`AddKeyed*`, `[FromKeyedServices]`), factory lambdas, and assembly scanning (Scrutor, MediatR, `ApplyConfigurationsFromAssembly`, MVC application parts). The last `Add` wins for single resolution, all appear in `IEnumerable<T>`, and `TryAdd` keeps the first.
- **Lifetimes:** For each moved type, record its lifetime, its consumers' lifetimes, and who disposes it. Factory lambdas and `IServiceProvider.GetService` calls hide dependency edges from scope validation.
- **Pipeline:** Read `Program.cs` order: exception handling, HTTPS/static files, `UseRouting`, `UseCors`, `UseAuthentication`, `UseAuthorization`, rate limiting, antiforgery, endpoints. `WebApplication` adds `UseRouting`, authentication, and authorization implicitly when they are not called. Then trace endpoint metadata: `MapGroup` conventions, `RequireAuthorization`, endpoint filters (FIFO before `next`, reverse after, running after parameter binding), MVC filters, and `[ApiController]` behaviors.
- **Configuration:** Trace each options type from its section key through `Bind`/`Configure`/`PostConfigure`, validation (`ValidateDataAnnotations`, `IValidateOptions`, `ValidateOnStart`), and its accessor: `IOptions` (singleton, never reloads), `IOptionsSnapshot` (scoped, recomputed per scope), `IOptionsMonitor` (singleton, change notifications). Section keys are strings; renaming one does not break the build, and validation without `ValidateOnStart` runs only on first access.
- **EF Core:** Follow `OnModelCreating`, `IEntityTypeConfiguration` discovery, conventions, value converters, global query filters, interceptors, `SaveChanges` overrides, and the migrations snapshot. Mark where `IQueryable` crosses method boundaries and where it materializes.
- **Names as data:** Search for type, namespace, and member names used at runtime: System.Text.Json polymorphism and source-gen context type lists, message contracts keyed by full type name, `Type.GetType` strings, SignalR hub method names, and properties serialized without `[JsonPropertyName]`.
- **Async and shutdown:** Trace `CancellationToken` from `HttpContext.RequestAborted` or `stoppingToken` through every call, plus `IHostApplicationLifetime`, `HostOptions.ShutdownTimeout`, and `BackgroundServiceExceptionBehavior` (`StopHost` by default since .NET 6).

## Preserve these boundaries

- **DI scopes:** Keep scoped state inside a scope. Hosted services and singletons inject `IServiceScopeFactory` and create one scope per unit of work; never resolve scoped services from the root provider. Convention-based middleware is constructed once, so scoped services belong in `InvokeAsync` parameters, not its constructor.
- **Disposal ownership:** The container disposes what it creates. Instances passed to `AddSingleton(instance)` and contexts from `IDbContextFactory` belong to the caller. Moving creation across that line changes who disposes.
- **EF Core unit of work:** One `DbContext` per unit of work, never used concurrently; await each operation before starting the next. Keep `SaveChanges` and explicit transaction boundaries where they are. `AddDbContextPool` reuses instances like singletons: `OnConfiguring` runs once, so per-request state such as a tenant ID must come through a scoped factory. Keep the tracking behavior (`AsNoTracking`, identity resolution) that update paths rely on.
- **HTTP contract:** Preserve route templates, binding sources, status codes, `ProblemDetails` shape, JSON naming policy, authorization policies, and endpoint metadata. A helper shared across endpoints must not bypass an endpoint's authorization or filters, or hold `HttpContext` past the request. Do not convert between controllers and minimal APIs as cleanup: `[ApiController]` adds automatic 400 responses and binding-source inference, and MVC filters do not run on minimal endpoints.
- **Library surface:** Keep public and protected members, namespaces, assembly identity, default parameter values and constants (compiled into callers), `InternalsVisibleTo`, and trimming/AOT annotations (`[DynamicallyAccessedMembers]`, `[RequiresUnreferencedCode]`). Moving a public type to another assembly breaks binary consumers unless `[TypeForwardedTo]` remains.
- **Generated code:** Change generator inputs (partial declarations, attributes, context type lists) and rebuild; never hand-edit `obj/` or `*.g.cs`. Regenerate EF compiled models when the model changes.
- **Abstractions and async:** Judge an existing interface by the lifetime, test seam, or public contract it carries, not by implementation count. Do not add repository/unit-of-work wrappers over `DbContext`, generic handlers, or mediator pipelines by default. Do not introduce `.Result`/`.Wait()`, `async void`, or fire-and-forget tasks that outlive their scope.

## Typical refactoring traps

- Merging a scoped service into a singleton helper, or caching it in a static or `Lazy<T>`, turns per-request state (current user, tenant, `DbContext`) into state shared across requests and threads. Scope validation catches only the constructor-injected case, and only where it is enabled.
- Changing a helper's parameter or return type from `IQueryable<T>` to `IEnumerable<T>` moves `Where`/`OrderBy`/`Take` from SQL into memory and loads whole tables; the reverse can surface translation exceptions at runtime, since EF evaluates on the client only in the final `Select`. Returning an unenumerated query from a method that disposes its context fails later at the caller.
- Wrapping calls that share one `DbContext` or scope in `Task.WhenAll` or `Parallel.ForEachAsync` throws "A second operation started on this context before a previous operation completed" or corrupts tracking state. Parallel work needs separate contexts from `IDbContextFactory` or separate scopes.
- Renaming an entity property or moving entity configuration yields a drop-and-add migration that loses data, or silently drops configuration when `ApplyConfigurationsFromAssembly` no longer scans that assembly. Inspect every generated migration and run `dotnet ef migrations has-pending-model-changes`.
- Reordering middleware or folding `Program.cs` registrations into extension methods changes which registration wins and whether CORS, authentication, authorization, or exception handling still wrap the endpoint. An explicit `UseRouting` added where it was implicit changes what runs before route matching.
- Moving a typed `HttpClient` into a singleton pins its handler so it misses DNS changes. `DelegatingHandler`s resolve scoped services from their own handler scope, not the request scope, so moving request-context logic into a handler leaks it between requests or loses it.

## Verification candidates

Prefer the repository's documented build, test, and format commands with its pinned SDK and configurations.

- `dotnet build` for every affected target framework, with `-warnaserror` if CI uses it. Compilation does not prove that DI graphs, configuration binding, or EF query translation still work.
- `dotnet test` for affected projects. When `global.json` sets `"test": { "runner": "Microsoft.Testing.Platform" }` (.NET 10 SDK or later), argument syntax differs from VSTest; copy the CI invocation.
- Build the host with `ValidateScopes` and `ValidateOnBuild` (on by default in Development for the Generic Host and `WebApplication`) and resolve affected services from two separate scopes. This catches missing registrations and constructor-captured scoped services; it misses factory lambdas, service-locator calls, and statics.
- Integration tests through `WebApplicationFactory<Program>` exercise the real middleware order and endpoint metadata; assert status codes, auth failures, and response bodies, not only happy paths. `ConfigureTestServices` replacements can hide the registration you changed.
- Run EF-related tests against the real provider (Testcontainers or the repository's disposable database). The in-memory provider uses LINQ to Objects and ignores transactions and relational constraints, so it cannot show query equivalence. Compare `ToQueryString()` or logged SQL before and after.
- For libraries: `dotnet pack` with package validation against the last shipped baseline, and PublicApiAnalyzers (RS0016/RS0017) where configured. Both catch signature and surface breaks, not behavioral changes. Run trim/AOT analysis where `IsTrimmable`/`IsAotCompatible` is set; a clean library build does not show warnings that a trimmed consuming app would get.
- `dotnet format --verify-no-changes` where CI runs it; it checks style and analyzer fixes, not behavior.
- Exercise cancellation and graceful shutdown (request abort, `StopAsync`, host stop) for moved hosted-service, streaming, or long-running code.

## Primary references

- [Dependency injection in .NET: scope validation, hosted-service scopes, keyed services](https://learn.microsoft.com/en-us/dotnet/core/extensions/dependency-injection/overview)
- [Options pattern: accessor lifetimes and validation](https://learn.microsoft.com/en-us/dotnet/core/extensions/options)
- [ASP.NET Core middleware order and implicit middleware](https://learn.microsoft.com/en-us/aspnet/core/fundamentals/middleware/?view=aspnetcore-10.0)
- [EF Core DbContext lifetime, factories, and threading](https://learn.microsoft.com/en-us/ef/core/dbcontext-configuration/)
- [.NET package validation](https://learn.microsoft.com/en-us/dotnet/fundamentals/apicompat/package-validation/overview)
