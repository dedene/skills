# Rails

Use for Ruby on Rails applications, engines, and in-repo packages, including the server side of Hotwire (Turbo, Stimulus) wiring. Apply the JavaScript/TypeScript profile to browser code beyond the markup and identifiers Rails renders.

## Establish the context

- Read `Gemfile.lock` (rails, zeitwerk, solid_queue, turbo-rails, packwerk), `.ruby-version`, binstubs, `bin/ci` with `config/ci.rb` when present, and CI. Identify Minitest or RSpec, the queue adapter per environment, `database.yml` connections, and engines without changing them.
- Read `config.load_defaults` and any `new_framework_defaults_*.rb`. Transaction callback ordering and similar semantics follow these flags, not the gem version alone.
- Note `config.eager_load` per environment. Recently generated test configs eager load only when `CI` is set, so constant and naming errors can stay hidden locally and appear in CI or production.
- Map the component boundaries the repo already uses: engines with `isolate_namespace`, `packs/` or `components/` with `package.yml`, and `lib/` under `config.autoload_lib`. MVC directories are not evidence of poor cohesion; do not add engines, packs, or service-object layers as cleanup.
- Trace each affected route through filters, controller, model/query, view/partial/serializer, mailers, broadcasts, and jobs. When persistence is involved, read `db/schema.rb` or `structure.sql` for constraints, defaults, and triggers.

## Trace more than imports

- **Convention wiring:** routes to actions, implicit rendering, partial lookup through `to_partial_path`, helpers, layouts, i18n keys derived from `model_name`, and host-app views that override engine views at the same path. Search strings and paths, not only constants, before calling a method or template unused.
- **Load-time wiring:** concerns and `included` blocks, callbacks, validations, scopes, association options (`dependent:`, `touch:`, `counter_cache:`), `ActiveSupport.on_load`, `config.to_prepare`, initializers, `ActiveSupport::Notifications` subscribers, and `class_eval` overrides of engine classes. Trace registration and inheritance order.
- **Names stored as data:** STI `type`, polymorphic `*_type` columns (including Active Storage attachments and Action Text), `delegated_type`, serialized columns, GlobalID and signed GlobalID, Active Job payloads (job class; `deliver_later` stores mailer class and method name as strings), Solid Queue `recurring.yml` `class:`/`command:` entries, concurrency keys built from record class names, and Turbo stream names. Stored and queued data outlives the deploy.
- **Ambient state:** `Current` attributes reset around every request and job and are not serialized into job arguments. Code that reads `Current` depends on where it runs.
- **Rendered JS identifiers:** `data-controller`, `data-*-target`, and `data-action` values map to Stimulus file paths (`admin/user_filter_controller.js` is `admin--user-filter`). `turbo_frame_tag` ids and `dom_id` values must match between the requesting page and the response, and Turbo Stream actions target DOM ids.
- **Boot paths:** web, `bin/jobs`, console, rake (`config.rake_eager_load` is false by default), and eager-loaded production load code differently. One path booting cleanly does not prove the others.

## Preserve these boundaries

- Keep transaction scope and side-effect timing. `after_commit` and `after_save` are not interchangeable. Transactions are per database connection: a separate queue database, another `connects_to` abstract class, or a replica sits outside `ApplicationRecord.transaction`.
- Nested `transaction` blocks join the parent unless `requires_new: true`; `ActiveRecord::Rollback` raised in a joined block rolls nothing back and is swallowed. Extracting a block into its own method does not change this.
- Keep job enqueue timing. `enqueue_after_transaction_commit` is a per-class attribute (default false) inherited from `ApplicationJob`. Solid Queue on the app database enqueues inside the surrounding transaction; on its own database (the Rails 8 default) it does not, and logic relying on the former silently loses it.
- Keep job argument shapes compatible with payloads already queued, and keep jobs idempotent where retries exist.
- Preserve association behavior, validation contexts, scopes, authorization, and query laziness. `update_column(s)`, `update_all`, `insert_all`, `upsert_all`, `delete_all`, and `touch_all` skip callbacks and validations; swapping them with `save`/`destroy` in either direction changes behavior.
- Keep Zeitwerk's path-to-constant mapping. Each autoload path is a root namespace (`app/services/billing/charge.rb` defines `Billing::Charge`), including `concerns` directories. Preserve inflection acronyms and `collapse`/`ignore` configuration.
- Initializers must not reference reloadable constants; wrap that code in `to_prepare`. Do not cache reloadable classes in middleware, config, or other long-lived objects.
- Respect engine isolation: `isolate_namespace` namespaces tables (`blorgh_articles`), routes (`main_app.` versus the engine proxy), helpers, and views. Engines should reference host classes by name string.
- Respect `package.yml` dependencies and privacy. Do not absorb new violations by editing `package_todo.yml` or running `bin/packwerk update-todo`.
- Do not rewrite applied migrations. Renaming a stored or queued name needs a compatibility plan (kept constant alias, `sti_name`/`polymorphic_name` override, data migration) within authorized scope.

## Typical refactoring traps

- Moving `perform_later` or `deliver_later` from an `after_commit` callback into a service method called inside `transaction` lets the job run before the row is visible, or after a rollback. Keep it post-commit with `transaction.after_commit` or `ActiveRecord.after_all_transactions_commit` (7.2+), or the job's `enqueue_after_transaction_commit`. `ActionMailer::MailDeliveryJob` inherits from `ActiveJob::Base`, not `ApplicationJob`, so that setting on `ApplicationJob` does not cover mail.
- Consolidating callbacks into a concern as `after_create_commit :sync` plus `after_update_commit :sync` keeps only the last one, because both alias `after_commit` with the same method name. Use `after_commit :sync, on: [:create, :update]` or `after_save_commit`.
- Moving a `before_destroy` into a concern included after `has_many ..., dependent: :destroy` runs it after the children are gone. Keep declaration order or pass `prepend: true`.
- Renaming or namespacing a model changes `model_name`, which drives partial paths, `dom_id`, param keys, polymorphic route helpers, i18n keys, and Turbo stream names, and orphans the old name in STI, polymorphic, Active Storage, GlobalID, and queued-job data.
- Extracting synchronous model or controller work into a job drops `Current.user`, `Current.account`, and per-request `Time.zone`. Pass explicit arguments and keep authorization decisions where the actor is known.
- Renaming, reordering, or removing `step`s in a job that includes `ActiveJob::Continuable` (8.1+) makes interrupted jobs raise `InvalidStepError` on resume, because completed steps are serialized in the job data.

## Verification candidates

- Prefer `bin/ci` or the documented CI steps, then `bin/rails test`, `bin/rails test:system`, or `bundle exec rspec` against the repo's disposable database. Check what `bin/setup` and `db:prepare` touch before running them.
- `bin/rails zeitwerk:check` eager loads and reports path/constant mismatches. It boots the environment, runs initializers, lists directories it did not check, and proves nothing about names stored in tables or queues. Also run the suite with `CI=1` or eager loading on after moving constants.
- `bin/rails routes` (`-c`, `-g`) before and after shows route names and helpers; `--unused` (7.1+) only flags routes without a matching action or template. Neither proves rendering, constraints at runtime, or authorization.
- Request or integration tests prove route, partial, and response resolution; system tests prove Stimulus and Turbo wiring in a browser. Model tests prove neither.
- `assert_enqueued_with`, `assert_enqueued_jobs`, and `perform_enqueued_jobs` plus a rollback-path test cover enqueue timing. The test adapter does not prove Solid Queue concurrency controls, recurring schedules, or same-database transactional enqueue. `bin/jobs check` (recent Solid Queue) validates `queue.yml` and `recurring.yml` without running jobs.
- `assert_queries_count`/`assert_no_queries` (7.2+), `strict_loading`, or Bullet when the repo uses it show query counts and lazy loading, not result equivalence.
- `bin/packwerk check` and `validate` cover static constant references only; they ignore method calls and dynamic dispatch and report false positives with custom Zeitwerk inflections or collapsed directories. `bin/brakeman` and `bin/rubocop` do not establish behavior.

## Primary references

Use the guides for the repo's version (`https://guides.rubyonrails.org/vX.Y/...`); the unversioned guides track the latest release, which may not match.

- [Autoloading and reloading constants](https://guides.rubyonrails.org/autoloading_and_reloading_constants.html)
- [Active Record callbacks](https://guides.rubyonrails.org/active_record_callbacks.html)
- [Active Record transactions API](https://api.rubyonrails.org/classes/ActiveRecord/Transactions/ClassMethods.html)
- [Active Job basics: transactional integrity](https://guides.rubyonrails.org/active_job_basics.html#transactional-integrity-on-jobs)
- [Getting started with engines](https://guides.rubyonrails.org/engines.html)
