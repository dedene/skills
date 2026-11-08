# JVM and Spring

Use for Java and Kotlin backend services, workers, and libraries, mainly Spring Boot, with short notes where Quarkus or Micronaut differ. Android apps need separate lifecycle guidance; a frontend in the same repository uses the JavaScript/TypeScript profile.

## Establish the context

- Read the Maven/Gradle wrappers, module layout, JDK toolchain, Kotlin compiler plugins (`kotlin-spring`, `kotlin-jpa`), BOM or platform versions, profiles, and CI tasks. Use the wrappers and pinned versions; a refactor does not upgrade Boot, Kotlin, or the JDK.
- Take the Spring generation from resolved dependencies, not memory, and read docs for that version. Boot 4 runs on Framework 7 (Jakarta EE 11, JSpecify nullability, Jackson 3, modular `spring-boot-<technology>` jars); Boot 3 runs on Framework 6.
- Identify the execution model per component: servlet on platform threads, servlet with `spring.threads.virtual.enabled`, WebFlux/Reactor, or Kotlin coroutines. Transaction binding and context propagation differ between them.
- Note whether the build runs Spring AOT or native images. AOT fixes the classpath, active profiles, and `@Conditional` outcomes at build time and relies on runtime hints for reflection, resources, and proxies.
- Separate a library's published API and supported JVM targets from the application's runtime. Check `@NullMarked` packages: Kotlin enforces JSpecify annotations as real nullability, so moving or dropping one changes Kotlin callers.
- Quarkus (ArC) and Micronaut resolve injection at build time. Quarkus removes unused beans during the build by default and supports intercepted self-invocation, so the Spring proxy rules below do not transfer unchanged.

## Trace more than imports

- **Registration:** follow component scanning from the `@SpringBootApplication` package, explicit `@ComponentScan` and `@Import`, `@Bean` methods, `BeanRegistrar` (Framework 7), post-processors, profiles, qualifiers, `@Primary`, and `ObjectProvider` or collection injection. A class with no callers can be live through any of these.
- **Auto-configuration:** read `META-INF/spring/org.springframework.boot.autoconfigure.AutoConfiguration.imports` and the `@ConditionalOnClass`, `@ConditionalOnBean`, `@ConditionalOnMissingBean`, and `@ConditionalOnProperty` conditions on affected types. A user bean of a matching type makes the auto-configured one back off; moving a dependency between modules changes class conditions.
- **Request path:** trace servlet filters and the security filter chain, interceptors, argument resolvers, validation, `@ControllerAdvice`, method security, transactions, persistence, and the events, jobs, or messages emitted.
- **Other entrypoints:** `@Scheduled`, `@KafkaListener`, `@RabbitListener`, `@JmsListener`, Spring Batch steps, `ApplicationRunner`, and actuator endpoints start work that no controller calls.
- **Proxied behavior:** `@Transactional`, `@Cacheable`, `@Async`, `@PreAuthorize`, `@Retryable`, and custom aspects apply only when a call crosses the proxy. Find each annotated method's callers and the bean reference they use.
- **Events:** list publishers and listeners together: `@EventListener`, `@TransactionalEventListener` and its phase, `@Async` listeners, Spring Modulith `@ApplicationModuleListener` (async, `REQUIRES_NEW`, after commit), and any custom `ApplicationEventMulticaster`.
- **Persistence:** follow entity scanning, Spring Data repository interfaces, derived query method names, `@Query`, entity graphs, fetch types, cascade and orphan-removal rules, and Flyway/Liquibase migrations. A repository method name is a query definition, and a missing implementation class is expected.
- **Reflection and metadata:** check `@ConfigurationProperties` bindings, serialized field and type names, `META-INF/services`, `spring.factories`, `aot.factories`, `RuntimeHintsRegistrar`, `@RegisterReflectionForBinding`, and annotation processors (MapStruct, Lombok, kapt/KSP). Change generator inputs and regenerate through the build.

## Preserve these boundaries

- **Transactions and proxies:** in the default proxy mode a self-call skips the interceptor, so the annotation can stay while the transaction, cache, async hop, or security check disappears. Preserve propagation, isolation, read-only flags, rollback rules (checked exceptions, including ones thrown from Kotlin, do not roll back by default), and where external effects happen relative to commit. Proxied behavior is not available in `@PostConstruct`.
- **Event timing:** `@TransactionalEventListener` defaults to `AFTER_COMMIT` and is skipped when no transaction is active unless `fallbackExecution = true`. Data access in an after-completion phase joins the finished transaction and is not committed; since 6.1, a `@Transactional` listener must use `REQUIRES_NEW` or `NOT_SUPPORTED`. A plain `@EventListener` runs synchronously inside the publisher's transaction, and its exception rolls the publisher back.
- **Bean identity and lifecycle:** preserve bean names (string qualifiers, `@DependsOn`, `@Async("name")`, `applicationTaskExecutor`), scope, init and destroy order, and `@Primary` resolution. Constructing a formerly managed class with `new` bypasses injection, proxies, and lifecycle callbacks.
- **Persistence context:** preserve transaction and session lifetime, flush timing, lazy loading, optimistic locking, and query counts where they matter. Boot registers Open EntityManager in View for web apps unless `spring.jpa.open-in-view=false`, so lazy access in controllers or serialization may work only because of it.
- **Threads and context:** thread-bound state (transactions, security context, MDC, request scope, observations) does not follow work onto another platform or virtual thread. It crosses only through configured decorators (`ContextPropagatingTaskDecorator`, Spring Security delegating executors) or the Reactor and coroutine context.
- **Declared module boundaries:** where Spring Modulith or ArchUnit rules exist, treat module API packages and allowed dependencies as contracts and fix the dependency rather than the rule.
- **Published APIs:** keep binary compatibility, Kotlin/Java interop (`@JvmStatic`, `@JvmOverloads`, default arguments, `internal` name mangling), JSpecify nullability, and configuration property keys for external consumers.
- **Structure:** keep an idiomatic layered or feature-package structure unless a concrete workflow shows needless coordination. Do not add hexagonal ports, CQRS, or an interface per class by default. A thin service may still own the transaction or authorization boundary.

## Typical refactoring traps

- Inlining a `@Transactional` or `@Cacheable` method into a caller on the same bean removes the transaction or cache at runtime. Extracting it into a new bean adds one, possibly with a different propagation, rollback scope, or cache key (default keys derive from the method parameters).
- Replacing a direct call with an event, or swapping `@TransactionalEventListener` and `@EventListener`, moves the side effect across the commit: messages go out for rolled-back work, or never fire when the publisher had no transaction.
- Moving entity access into an `@Async` method, scheduled job, message listener, or past the end of the service transaction causes `LazyInitializationException` or extra queries. Moving a `JdbcTemplate` read next to unflushed entity changes reads stale rows, because it does not trigger the persistence-context flush.
- Moving a class out of the scanned base package, or into one that a slice, `@EntityScan`, or auto-configuration package covers, changes which beans exist. Declaring a new `@Bean` of a type such as `Executor`, a Jackson mapper, or `DataSource` makes the matching auto-configuration back off; a custom `Executor` also takes over `@Async`.
- In Kotlin, moving a `@Transactional` method onto a class registered through a `@Bean` method or lacking a Spring stereotype leaves the class `final`, because `kotlin-spring` opens only annotated classes; CGLIB cannot proxy it and final methods are not advised.
- Renaming an event type, `@ConfigurationProperties` field, or serialized DTO breaks state outside the code: Spring Modulith stores incomplete publications as serialized events, externalized events route by type name unless `@Externalized` fixes the target, and deployed config uses the old property keys.

## Verification candidates

- Run targeted tests through `./mvnw` or `./gradlew`, then the module, consumer, and integration tasks CI runs. Unit tests on objects built with `new` prove nothing about proxying, scanning, or conditions.
- Start the application context under each affected profile with the existing `@SpringBootTest` or smoke test. For registration changes, compare the condition evaluation report (`--debug` or actuator `conditions`) and the `beans` endpoint before and after; a clean start does not prove runtime behavior.
- Test conditional and auto-configured beans with `ApplicationContextRunner`. It proves bean presence for the inputs given, not for production property sources.
- Exercise rollback and event timing through the real bean with a committing transaction. `@Transactional` tests and `@DataJpaTest` roll back by default, so `AFTER_COMMIT` listeners never fire, and a `RANDOM_PORT` server or `@Async` thread runs outside the test transaction. Use `TestTransaction`, non-transactional tests, and explicit `flush()` to avoid false positives.
- Use Testcontainers (often via `@ServiceConnection`) with the documented disposable databases and brokers; H2 does not prove dialect, locking, or migration behavior. Back query-count claims with Hibernate statistics or a query-counting datasource proxy.
- Where present, run Spring Modulith `ApplicationModules.of(App.class).verify()` or ArchUnit rules. They check static dependencies, not runtime wiring or transaction semantics.
- If CI builds AOT or native, run `processAot` or `spring-boot:process-aot` and the native test task; JVM tests do not exercise missing hints. For published libraries, run the repository's API compatibility check (japicmp, Kotlin ABI validation) and representative consumers.

## Primary references

- [Spring Framework: `@Transactional` proxy and visibility semantics](https://docs.spring.io/spring-framework/reference/data-access/transaction/declarative/annotations.html)
- [Spring Framework: transaction-bound events](https://docs.spring.io/spring-framework/reference/data-access/transaction/event.html)
- [Spring Boot: auto-configuration registration and conditions](https://docs.spring.io/spring-boot/reference/features/developing-auto-configuration.html)
- [Spring Framework: AOT restrictions and runtime hints](https://docs.spring.io/spring-framework/reference/core/aot.html)
- [Spring Framework: test-managed transactions and flush false positives](https://docs.spring.io/spring-framework/reference/testing/testcontext-framework/tx.html)
