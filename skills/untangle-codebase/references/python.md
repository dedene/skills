# Python

Use for Django, FastAPI and Flask services, installable packages, CLIs, data pipelines and Celery-style workers. Apply the JavaScript/TypeScript profile to frontend code bundled in the same repository.

## Establish the context

- Read `pyproject.toml`, the lockfile (`uv.lock`, `poetry.lock`, `requirements*.txt`), `requires-python`, tool sections (`[tool.pytest.ini_options]`, mypy/pyright, ruff, `[tool.importlinter]`), `tox.ini` or `noxfile.py`, and CI. Use the existing runner and environment; do not add a package manager, type checker or linter for the refactor.
- Take framework versions from the lockfile, not memory. FastAPI yield cleanup, Django async support and Celery transaction helpers changed between releases.
- Inventory entry points that never appear as imports: `[project.scripts]` and `[project.entry-points]`, management commands, WSGI/ASGI modules, worker and beat processes, pipeline or DAG definitions, notebooks, and plugins loaded through `importlib.metadata.entry_points()`.
- Check which settings and configuration each process loads (`DJANGO_SETTINGS_MODULE`, env-driven config objects, worker `-A` app). Web, worker, CLI and test processes may import different modules and wire different registrations.
- Separate the public surface from internals: `__init__.py` re-exports, `__all__`, documented import paths, and names that consumers reference as strings. A module with no in-repo caller can still be load-bearing.

## Trace more than imports

- Import-time side effects register behavior: decorators (`@app.get`, `@receiver`, `@shared_task`, `@admin.register`, `@click.command`), metaclasses, `__init_subclass__` registries and module-level `connect()` calls run only if something imports the module. Removing or moving an import can silently unregister a route, task or receiver.
- Strings are references: Django settings (`INSTALLED_APPS`, `MIDDLEWARE`, `AUTH_USER_MODEL`, `ROOT_URLCONF`, storage and logging backends), `include("app.urls")`, `"app_label.Model"` relations, Celery task names and beat schedules, entry point `module:attr` values, `importlib.import_module()` calls, and `mock.patch("pkg.mod.name")` targets in tests.
- **Django:** `django.setup()` imports each app config, then each app's `models`, then runs `AppConfig.ready()`, all in `INSTALLED_APPS` order. Importing models from an app's root package or `apps.py` breaks this, and receivers wired in `ready()` exist only because of that import. App order also decides which templates, static files and management commands win.
- **Django:** signal receivers run inline in the sender's thread, inside whatever transaction the sender holds; a receiver that raises inside `atomic()` leaves the block unusable (`TransactionManagementError`). Also trace managers, custom querysets, `save()` overrides, middleware order, context processors and template tags.
- **FastAPI:** dependencies form a per-request graph; a dependency required twice in one request runs once and is cached unless `use_cache=False`. Follow `include_router()` prefixes, dependencies and tags, `app.state`/`request.state`, and the `lifespan` context: it runs only for the main app, not mounted sub-apps, and passing `lifespan` disables `on_event` handlers.
- **FastAPI:** a return annotation or `response_model` validates, filters and documents the output. Changing an endpoint's return type changes the response body and OpenAPI schema, not just typing.
- **Flask:** routes, `before_request` hooks, error handlers and CLI commands attach at app or blueprint registration; extensions bind in `init_app()`. `current_app`, `g`, `request` and `session` are context-local proxies that usually live for one request or CLI command.
- **Workers and serialized state:** Celery derives the default task name from the defining module and function name, and that name travels in queued messages, result backends and beat schedules. Pickle (task serializer, caches, joblib or model artifacts, `multiprocessing`) stores classes and functions by fully qualified name, so the old path must import at load time.
- **Autodiscovery:** Celery `app.autodiscover_tasks()` imports only the `tasks` module of each listed package by default, and admin autodiscovery imports each app's `admin` module. A task or registration moved to a differently named module is no longer found by workers.

## Preserve these boundaries

- Public import paths, signatures, exception types and generator laziness. A decorator or wrapper may supply registration, transactions, authorization, caching or retries; identify its effect before inlining it. When a public symbol moves, keep a re-export at the old path.
- Django persisted identity: `AppConfig.label` and model names appear in table names, migration dependencies, content types and permissions. Migrations import custom fields, model base classes, `upload_to` and `limit_choices_to` callables, and `use_in_migrations` managers by path; keep them importable while any migration references them.
- Transaction boundaries: `atomic()` blocks, `ATOMIC_REQUESTS` (wraps the view only, not middleware or streaming response generation) and `transaction.on_commit()`, whose callbacks run after the outermost commit, are discarded on rollback, and run immediately when no transaction is open.
- Execution context: in FastAPI a plain `def` endpoint or dependency runs in a threadpool, while `async def` runs on the event loop. In Django the sync ORM raises `SynchronousOnlyOperation` from async code and transactions do not work in async mode; keep the atomic unit in one sync function called through `sync_to_async()`. Preserve cleanup, cancellation and task ownership, not just call syntax.
- Resource lifetime: FastAPI yield dependencies and `lifespan` resources, Flask `teardown_appcontext` handlers, and context managers. Never let a refactor capture a request-scoped session or a Flask proxy in module state, a thread or a background job; pass the real object (`_get_current_object()`) or an ID.
- Flask factory split: setup belongs in the application factory, request work in views and blueprints. Moving a module-level `app`, `db` or client into a factory, or the reverse, changes when extensions bind and breaks modules that import the global.
- CLI contract: arguments, stdout/stderr, exit codes, configuration precedence and import cost. Do not move work to import time that the old entry point deferred.
- Pipeline contract: schemas, dtypes, ordering, partitioning, checkpoints, retry and idempotency semantics, and numeric tolerances. Do not infer notebook reproducibility from saved outputs.

## Typical refactoring traps

- Moving a Celery task function to another module changes its generated name, so queued messages, beat entries and `send_task("old.name")` callers hit an unregistered task. Pin `name=` to the old value, or register both names until queues drain.
- Moving a model, custom field or field-option callable breaks historical migrations that import it, and moving a model between apps changes its label, table and content type. That is a schema migration, not a module move.
- Extracting "save, then notify" into a service changes semantics when the service runs inside `atomic()`: a direct `.delay()` or Django 6.0+ `.enqueue()` can reach a worker before commit and miss the row. Keep side effects in `transaction.on_commit()` (Celery 5.4+ has `delay_on_commit()`) and pass primary keys, not model instances.
- Moving blocking I/O from a `def` endpoint or dependency into an `async def` helper blocks the event loop for every request; turning a Django view async while it still calls the sync ORM raises `SynchronousOnlyOperation`.
- Relocating code around a FastAPI yield dependency is version-sensitive: 0.106.0 ran exit code before the response was sent, 0.118.0 moved it back to after, and 0.121.0 added `Depends(scope="function")` for pre-response cleanup. A session relied on during a `StreamingResponse` or `BackgroundTasks` may already be closed; background work should open its own resources. Since 0.110.0, catching an exception after `yield` without re-raising swallows it.
- Breaking an import cycle by moving code into `utils`, adding function-local imports or Python 3.15 `lazy import` defers the cycle and its side effects instead of removing it; registration that ran at import may stop running. Find which module owns the shared policy first.

## Verification candidates

- Run the repository's own commands first (`make test`, `tox`, `nox`, `uv run pytest`, `poetry run pytest`, CI scripts) against a baseline recorded before editing.
- Diff registrations before and after: Django `manage.py check` and `manage.py makemigrations --check --dry-run`, `celery -A <app> inspect registered` or the app's task registry, FastAPI `app.openapi()` or the route list, `flask routes`. These prove wiring survived, not behavior.
- Exercise lifecycles in tests: `with TestClient(app)` runs `lifespan`; Django `TestCase` never fires `on_commit`, so use `captureOnCommitCallbacks(execute=True)` or `TransactionTestCase`. Mocks patched at an old import path can keep tests green over a broken move.
- Celery eager mode (`task_always_eager`) runs tasks in-process and bypasses the broker and routing; it checks task logic, not task names, queue routing or message payloads. Use the project's worker-based integration setup for those.
- Package surface: build with the configured backend, install into a clean environment and import from outside the source tree; working-directory imports hide missing package data and broken re-exports. `griffe check` compares public signatures between Git refs but not return types or runtime behavior.
- Existing static gates only: mypy or pyright, ruff, and `lint-imports` when import-linter contracts are configured. None of them see string references, dynamic imports or registration side effects.
- `python -X importtime -c "import pkg"` shows whether import cost or import-time work moved. For pipelines, compare small deterministic fixtures against expected schema and output within the project's established tolerance.

## Primary references

- [Django: Applications and `AppConfig.ready()`](https://docs.djangoproject.com/en/stable/ref/applications/)
- [Django: Database transactions and `on_commit()`](https://docs.djangoproject.com/en/stable/topics/db/transactions/)
- [FastAPI: Dependencies with yield, version changes and scope](https://fastapi.tiangolo.com/advanced/advanced-dependencies/)
- [Flask: The application context](https://flask.palletsprojects.com/en/stable/appcontext/)
- [Celery: Tasks, names and transactions](https://docs.celeryq.dev/en/stable/userguide/tasks.html)
