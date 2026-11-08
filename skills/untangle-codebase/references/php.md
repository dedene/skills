# PHP

Use for Laravel, Symfony, WordPress, and plain PHP applications, packages, plugins, and themes, including long-running servers and workers. Apply the JavaScript/TypeScript profile to bundled frontend code and block-editor scripts in the same flow.

## Establish the context

- Identify the framework from installed packages and bootstrap files (`artisan` and `bootstrap/app.php`, `bin/console` and `config/bundles.php`, a plugin header or `wp-config.php`), not from Composer usage alone. Read versions from `composer.lock`, not the constraint in `composer.json`.
- Read the `php` constraint under `require`, `config.platform`, `autoload`/`autoload-dev` (PSR-4, `classmap`, `files`), Composer scripts, and CI. Identify PHPUnit or Pest and any configured PHPStan, Psalm, Deptrac, Rector, or PHPCS without adding or upgrading them.
- Match conventions to the installed version: Laravel 11+ registers providers in `bootstrap/providers.php` and middleware/exceptions in `bootstrap/app.php`; older apps use `config/app.php` and `app/Http/Kernel.php`. Symfony config may be YAML, PHP, or attributes; follow what the repository uses.
- List every entry point: web front controller, console commands, scheduler, queue workers (`queue:work`, `messenger:consume`), WP-Cron, WP-CLI, REST and `admin-ajax` handlers, and plugin activation hooks.
- Detect long-running modes: Laravel Octane, FrankenPHP worker mode, RoadRunner, Swoole, and every queue or Messenger worker. One booted application serves many requests or jobs; static properties, singletons, and in-memory caches persist between them.
- Treat `bootstrap/cache/*.php`, `var/cache/` (compiled container, routes), Doctrine proxies, and `vendor/composer/autoload_*` as generated. Change their sources and regenerate in a test environment.

## Trace more than imports

- **Laravel:** service providers (`register` only binds; `boot` wires listeners, routes, gates, macros, observers), deferred providers and their `provides()` list, package auto-discovery via `extra.laravel` in dependency `composer.json` files.
- **Laravel:** container attributes (`#[Bind]`, `#[Singleton]`, `#[Scoped]`, contextual `#[Config]`, `#[Give]`, `#[Tag]`), zero-configuration resolution of concrete classes, facades, and real-time facades (`Facades\App\...` imports point at no file).
- **Laravel:** event discovery scans listener directories and registers `handle`/`__invoke` methods by their type-hinted event; policies are discovered by model and policy naming; observers attach via `#[ObservedBy]` or `observe()`; global scopes, casts, and route model binding run without explicit calls.
- **Symfony:** `services.yaml` `resource`/`exclude` globs, autoconfiguration that adds tags from interfaces and attributes (`#[AsEventListener]`, `#[AsMessageHandler]`, `#[AsCommand]`, `#[AutoconfigureTag]`, `#[AsDecorator]`, `#[AsAlias]`, `#[When]`, `#[Autowire]`), compiler passes, and tagged iterators with priorities.
- **Symfony:** Messenger `routing` keyed by message class or interface, Doctrine mapping by directory and namespace prefix, `#[AsEntityListener]`/`#[AsDoctrineListener]` registrations, route names, Twig template paths, and serializer groups or `#[SerializedName]`.
- **WordPress:** `add_action`/`add_filter` with priority and accepted argument count, dynamic hook names (`save_post_{$post_type}`, `wp_ajax_{$action}`), shortcodes, REST routes, `block.json`, pluggable functions behind `function_exists`, template hierarchy and child-theme overrides, and hook names stored in the `cron` option.
- **Plain PHP:** `require`/`include` chains, Composer `files` autoload, globals, string callables (`call_user_func`, `new $class`), and magic methods (`__call`, `__get`) that hide the real receiver.
- Follow class names stored outside code: queued job and message payloads, Eloquent polymorphic `*_type` columns (FQCN unless a morph map is enforced), Doctrine discriminator maps, database notifications, and cached or session-serialized objects.

## Preserve these boundaries

- Keep container lifetimes. Laravel `scoped` instances are flushed per Octane request and queue job; `singleton` instances are not. Symfony shared services persist in a worker unless they implement `ResetInterface` or carry the `kernel.reset` tag.
- Keep request, user, tenant, locale, and config values out of singleton constructors and static properties. Octane docs warn that an injected container, request, or config repository goes stale on later requests; pass the value to the method instead.
- Keep transaction and dispatch timing: Laravel `after_commit`, `afterCommit()`/`beforeCommit()`, `ShouldDispatchAfterCommit`, `ShouldQueueAfterCommit`, `ShouldHandleEventsAfterCommit`; Symfony `doctrine_transaction` middleware and `DispatchAfterCurrentBusStamp`.
- Keep middleware order, listener priorities, and tagged-service order. Symfony runs same-priority listeners in registration order.
- Keep names used outside PHP calls: route names, service IDs and aliases, event and hook names, config and option keys, template names, morph map values, cron hooks, and job or message class names. Rename through a compatibility path (service alias, morph map, `class_alias`, `do_action_deprecated`/`apply_filters_deprecated`) and keep old classes until queues drain.
- In Laravel, call `env()` only from config files. Moved into application code, it stops seeing `.env` values once `config:cache` runs and returns only system environment variables.
- Treat WordPress hooks, public functions, and package classes as extension APIs for code outside the repository. Do not add repositories over every model, a custom container, or syntax modernization; keep supported PHP versions and required extensions.

## Typical refactoring traps

- Moving a job dispatch or event into code that runs inside `DB::transaction()` lets a worker start before the commit and miss the row, or keeps work from a rolled-back transaction when `after_commit` is off. Wrapping existing code in a new transaction delays after-commit events and observers.
- Replacing a per-model save loop with an Eloquent mass update, `DB::table()`, or Doctrine DQL `UPDATE`/`DELETE` skips model events, observers, `preUpdate`/`preRemove`, and entity listeners, and leaves Doctrine's managed entities stale.
- Renaming or moving a job, message, model, or listener class breaks payloads already queued, polymorphic rows storing the old FQCN, Messenger routing keyed by the old class (the message then runs synchronously in the request), and Laravel event or policy discovery tied to directory and naming conventions.
- Hoisting request-derived state into a singleton or static cache passes tests and PHP-FPM, which boot fresh, but leaks between requests under Octane, FrankenPHP, or RoadRunner and between jobs in a long-lived worker.
- Extracting an interface with a second implementation makes Symfony autowiring ambiguous or picks the wrong service; moving a class into an `exclude`d path drops its service and tags; moving listener files can reorder same-priority listeners.
- Changing a WordPress callback from a named function or `Class::method` to a closure or a different instance, or changing its priority, breaks third-party `remove_action`/`remove_filter` without a warning. A renamed hook silently stops existing extensions, and a renamed cron hook orphans scheduled events.

## Verification candidates

- Run the repository's Composer scripts, Makefile, or CI commands first, with disposable databases, queues, and caches. Run targeted PHPUnit or Pest tests on public entry points and error paths of changed orchestration.
- PHPStan or Psalm with configured extensions (Larastan, phpstan-symfony, phpstan-doctrine, phpstan-wordpress) checks types and resolvable calls. It does not prove container wiring, hook registration, or class names referenced from config, payloads, or the database.
- Deptrac, if configured, enforces layer rules on class references; it misses container lookups, hooks, and string-based dispatch. Run Rector only as `--dry-run` analysis when the repository already configures it.
- Symfony: `lint:container` checks compiled argument types and aliases, not runtime behavior. Diff `debug:container`, `debug:autowiring`, `debug:event-dispatcher`, `debug:messenger`, and `debug:router` output before and after the change.
- Laravel: diff `route:list` and `event:list` before and after. If production caches config, run the affected tests with cached config in the test environment; never run cache or optimize commands against an unspecified environment.
- `Queue::fake()` and `Bus::fake()` record dispatches without serializing them. Prove payload round-trips through a real queue driver or Symfony's `in-memory` transport with its `serialize` option enabled, and process at least two jobs in one worker when shared-state lifetime changed.
- For long-running HTTP, send repeated requests through one kernel (Symfony `KernelBrowser::disableReboot()`, or one Octane or FrankenPHP worker with low worker and high max-request counts). A default max-requests restart can hide leaks.
- WordPress: use the repository's WordPress PHPUnit harness or `wp-env` in a disposable install; assert registration and priority with `has_action`/`has_filter`, filter return values, removal by third-party code, and activation behavior.

## Primary references

- [Laravel 13 queues](https://laravel.com/framework/docs/13.x/queues)
- [Laravel 13 Octane: dependency injection](https://laravel.com/framework/docs/13.x/octane#dependency-injection-and-octane)
- [Symfony service container (current)](https://symfony.com/doc/current/service_container.html)
- [Doctrine ORM events](https://www.doctrine-project.org/projects/doctrine-orm/en/current/reference/events.html)
- [WordPress Plugin Handbook: hooks](https://developer.wordpress.org/plugins/hooks/)
