# Astra instruction migration — 2026-09-13

Implemented the findings from the Eric Provencher audit across Peter's two maintained skill repositories, installed owned skills, personal and team AGENTS.md, and the Compound tool-map generator.

## Changes

- Consolidated authority, completion, questions, verification, browser, and delegation policies. Existing authorization carries through workers; external effects remain scoped to the user's request.
- Removed repeated confirmations, first-slice-only delivery, mandatory disagreements, blanket parent implementation bans, and unconditional repeated verification.
- Narrowed skill triggers and moved long operational procedures into conditional references. Architect loop, interview, and ultracode require explicit invocation in Codex.
- Reconciled five source/installation differences, preserving the Notion CLI-first route and portable Codex paths. Removed unsupported model taste scores and fixed productivity multipliers.
- Corrected uploads, review posting, CI, production submissions, and optional Notion publication boundaries. Kept the existing guarded Nimbu restore workflow.
- Corrected browser fallbacks, mcporter wrapper paths, Figma recovery assumptions and broken links, coverage revision caveats, and accessibility interpretation.
- Declared 36 canonical skill sources and added hash-checked installation synchronization. Existing destinations are synchronized; previously uninstalled skills remain uninstalled. Destination-only files are preserved.
- Disabled duplicate local Superpowers entries and broad upstream bootstraps through Codex configuration. Upstream skill bodies were not edited.

## Verification

- Six sync tests pass: planning is read-only, apply backs up files, repeated sync is idempotent, drift aborts before writes, extra files survive, and unsafe paths are rejected.
- Four ultracode ledger tests pass. Four focused Compound generator tests passed during staged validation.
- Changed skill frontmatter and local links were checked; the attachment skill retains its existing Claude-supported `argument-hint` field, which Codex's generic quick validator does not recognize.
- Changed Figma shell wrapper passes shell syntax validation. Both maintained repositories pass `git diff --check`.
- Installed synchronization reports zero changed files. Local Codex prompt rendering succeeds with the new configuration; excluded bootstraps and duplicate local Superpowers paths are absent.
- Four read-only instruction simulations covered upload auditing, review-only CI, public launch checks without credentials, and accessibility reporting without a browser. Residual reference contradictions found in those checks were corrected.

These checks do not establish model performance improvement. Repeated controlled Astra runs and live external API workflows were not executed. The broader Compound test attempt was limited by missing dependencies and temporary-directory permissions; its focused generator tests passed.

## Operational notes

Restart Codex to refresh skills and configuration in a new session. After plugin upgrades, recheck versioned paths in `disabled-upstream-skills.json`. Run the sync check after editing canonical skills; review a fresh plan before applying it.

No commits or pushes were made. Pre-existing edits were preserved. Migration backups:

- `/var/folders/ml/vv16b3nn2kjgn_gt7btb03_c0000gn/T/astra-migration-backup-15iretu_`
- `/private/var/folders/ml/vv16b3nn2kjgn_gt7btb03_c0000gn/T/skill-sync-backup-r2erial6`

## Portability correction — 2026-09-15

The initial migration incorrectly copied Peter's personal mcporter wrapper path into shared skills. Shared MCP examples and the Figma helper now select `MCPORTER_BIN`, falling back to the installed `mcporter` only when no host wrapper is required. Personal wrapper policy stays in the personal AGENTS.md. The older Aside backend now accepts `ASIDE_BIN` or resolves `aside` from PATH. Machine-specific sync manifests are explicitly documented as personal configuration.
