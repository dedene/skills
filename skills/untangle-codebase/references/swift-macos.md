# Swift and macOS

Use for Swift packages and macOS apps built with SwiftUI, AppKit, or both, including Observation, SwiftData/Core Data, and Swift concurrency. Treat other Apple platforms in the same repository as separate targets with their own lifecycle and test needs.

## Establish the context

- Read `Package.swift`, `Package.resolved`, Xcode projects/workspaces, shared schemes, test plans, `.xcconfig` files, and CI. If XcodeGen, Tuist, or another generator owns the project, edit its inputs, not the generated `.pbxproj`.
- Record the toolchain the repo pins (`.xcode-version`, CI image, `swift-tools-version`) and use it. SwiftUI semantics can differ by Xcode release, not only by deployment target.
- Per target, read the effective concurrency settings: Swift language mode, strict-concurrency level, `SWIFT_DEFAULT_ACTOR_ISOLATION`, `SWIFT_APPROACHABLE_CONCURRENCY`, and enabled upcoming features. In packages, read each target's `swiftSettings` (`.defaultIsolation(MainActor.self)`, `.enableUpcomingFeature(...)`, `swiftLanguageModes`). `xcodebuild -showBuildSettings -scheme <S>` shows resolved values.
- Default isolation is per module: unset means `nonisolated`, and imported modules are unaffected by the current module's choice. An app target and its local packages often run under different defaults.
- Map app, library, extension, XPC service, helper, login item, and test targets with source and resource membership. With Xcode buildable (synchronized) folders, a file's folder and any membership exceptions decide which target compiles it.
- Identify scene/window/document ownership and every persistence, XPC, sandbox, entitlement, App Group, and Objective-C boundary the change touches.

## Trace more than imports

- **AppKit:** follow nib/storyboard outlets, actions, and custom classes (bound by string name and module), Cocoa bindings and KVO key paths, `@objc` selectors, target/action with nil targets, responder-chain commands, `validateMenuItem`/`NSMenuItemValidation`, delegates, and `NotificationCenter` observers. No direct Swift caller does not mean unused.
- **Info.plist and entitlements:** `NSPrincipalClass`, `NSMainStoryboardFile`, extension principal classes, document types, URL schemes, and service names point at code by string. So do `NSApplicationDelegateAdaptor`, `@main`, and `SMAppService` bundle identifiers.
- **SwiftUI:** trace `WindowGroup(id:)`/`openWindow`, `.commands` with `@FocusedValue`/`focusedSceneValue`, `.environment(_:)` injection read by `@Environment(Type.self)`, `@SceneStorage` and `@AppStorage` string keys, and `.task`/`.onChange` side effects.
- **Observation:** a view updates only for `@Observable` properties its `body` reads. Trace which view reads which property, `@ObservationIgnored` fields, and any remaining `ObservableObject`/`@Published` paths, which track differently.
- **Persistence:** for SwiftData, trace `.modelContainer` placement, `@Query` consumers, `@ModelActor` types, and `VersionedSchema`/`SchemaMigrationPlan`. For Core Data, trace the `.xcdatamodeld`, `representedClassName`, codegen mode, and which contexts each thread or actor uses.
- **Concurrency:** mark the isolation of every affected declaration and each `await`. Actor-isolated state can change across a suspension (reentrancy). `Task {}` inherits the enclosing isolation, `Task.detached` does not, and `.task` is cancelled when its view disappears.
- Follow ownership of windows, controllers, observers, tasks, and closures; inspect strong/weak captures, cancellation, and teardown together.

## Preserve these boundaries

- **State identity and ownership:** keep the view that owns `@State`/`@StateObject` and its structural identity stable. Changing branch structure, `.id(_:)`, or wrapping in `AnyView` can reset state and restart `.task`. Keep per-window state per window.
- **Isolation:** keep each declaration's effective isolation, task lifetime, cancellation propagation, and error delivery. Do not add broad `@MainActor`, `nonisolated`, `@unchecked Sendable`, `@preconcurrency`, or build-setting changes to make an extraction compile; fix the ownership boundary within the project's settings.
- **AppKit contracts:** framework-defined method signatures, `@IBAction`/`@objc` selectors, responder routing, main-thread requirements, undo registration, and restoration identifiers are interfaces.
- **Runtime names:** Objective-C runtime class names (module-qualified unless `@objc(Name)`) are stored in nibs, `NSKeyedArchiver`/`NSSecureCoding` archives, Core Data models, and XPC interfaces. SwiftData entity names and property names are the store schema.
- **Public contract:** `public`/`open` symbols, `package` access, products, resources reached via `Bundle.module`, `@available` ranges, and with library evolution enabled, `@frozen`/`@inlinable` bodies that clients compile into themselves.
- **Persisted keys:** `UserDefaults`/`@AppStorage` keys, `@SceneStorage` keys, bundle identifiers, App Group and keychain access groups, and file locations.
- **Idiomatic boundaries:** SwiftUI views composing small views, AppKit controllers per window, and packages as module boundaries are the native shape. Add a view model, coordinator, protocol, or package only for a demonstrated ownership or dependency problem.

## Typical refactoring traps

- Moving a type from an app target into a package (or the reverse) can flip unannotated declarations between `@MainActor` and `nonisolated`, and with `NonisolatedNonsendingByDefault` on one side only, change whether `nonisolated async` functions run on the caller's actor or off it. It also changes access control, `Bundle.module` resource lookup, and the module-qualified runtime class name used by nibs, archives, and Core Data.
- Extracting stored properties from an `@Observable` model into a plain helper class compiles but stops view updates. Swapping `@StateObject` for `@ObservedObject`, or moving model creation to a parent, changes who owns the instance and when it is recreated.
- Moving object creation into a `@State` default value has toolchain-dependent cost: through Xcode 26 the default is instantiated on every view initialization, while from Xcode 27 the `@State` macro instantiates it only the first time. Move work into `.task` if it must run once on both.
- Replacing `.task { }` with `onAppear { Task { } }`, or a callback with a detached task, drops automatic cancellation and changes which actor the work runs on and how long its owner lives.
- Merging similar menu, toolbar, and `.commands` handlers can remove differences in responder routing, focused-scene targeting, validation, or undo registration. Consolidating per-window or per-document models into a singleton breaks multiple windows, reopening, and restoration.
- Renaming a SwiftData `@Model` property or class, or a Core Data entity, without `@Attribute(originalName:)` or a mapping/migration stage changes the store schema and can lose data.

## Verification candidates

Use the repository's documented schemes, destinations, test plans, and scripts first.

- `swift build` and `swift test` for package targets; `swift test` runs XCTest and Swift Testing. Passing package tests does not prove app integration, resource bundling, or nib/plist wiring.
- `xcodebuild build`/`test -scheme <S> -destination 'platform=macOS' [-testPlan <P>]` for app targets. Do not change signing or entitlements to work around a local failure; report it.
- Swift Testing runs tests in parallel by default. New shared singletons or stores can surface as flaky tests rather than compile errors.
- `swift test --sanitize=thread` or `-enableThreadSanitizer YES` for changed concurrency paths. TSan finds races only on exercised paths; it does not verify actor isolation design or reentrancy logic.
- `swift package diagnose-api-breaking-changes <baseline>` for library public API. It does not cover Objective-C runtime names, resources, or behavior.
- Unused-code tools such as Periphery are candidates for leads only; they miss string-based entry points from nibs, plists, selectors, and archives.
- Run the app for changed UI: open and close multiple windows, menu and keyboard commands, focus changes, undo, restoration, and relaunch with existing data. Use disposable stores and a copy of a real store when model code moved.
- Name any scheme, OS version, entitlement, or signed-only scenario you could not run.

## Primary references

- [Swift data race safety](https://www.swift.org/migration/documentation/swift-6-concurrency-migration-guide/dataracesafety/)
- [SE-0466: Control default actor isolation inference](https://github.com/swiftlang/swift-evolution/blob/main/proposals/0466-control-default-actor-isolation.md)
- [SE-0461: Run nonisolated async functions on the caller's actor by default](https://github.com/swiftlang/swift-evolution/blob/main/proposals/0461-async-function-isolation.md)
- [SwiftUI: Managing model data in your app](https://developer.apple.com/documentation/swiftui/managing-model-data-in-your-app)
- [AppKit: NSResponder](https://developer.apple.com/documentation/appkit/nsresponder)
