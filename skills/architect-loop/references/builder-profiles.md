# Builder profiles

Profiles supply invocation mechanics, not permissions. Every dispatch includes the allowed-actions field and worker contract from SKILL.md. Never infer publication authority from network or sandbox settings.

Reuse the requested or recorded builder/model. Otherwise use Codex with its configured model and reasoning effort; do not bake model generations or cost assumptions into this skill. Verify flags through installed help. Help documents flags, but does not necessarily enumerate available models; use the CLI's supported model discovery when a model choice actually needs resolving.

## Codex CLI

```bash
codex exec -s workspace-write - < docs/builder-block.md
```

Check `codex exec --help` first. Add `-C <root>` and an output file if needed. Omit model/effort overrides to inherit configuration; use the requested profile when specified. Capture the session identifier and resume that exact session for follow-ups; avoid `--last` when runs may overlap. Use read-only mode for review-only work. Network behavior depends on the host configuration, not merely the sandbox name. Do not weaken sandbox controls to work around a blocked action.

## Cursor CLI or other builders

Inspect the installed executable's help for noninteractive execution, prompt input, model selection, output capture, and resume support. For Cursor, start with `cursor-agent --help`; for Grok, start with `grok --help` if installed. Do not assume their flags or model lists match another CLI.

Record the verified command, chosen model/configuration, ownership, and evidence capture in the handoff. Use available background execution and session controls. Parallel agents are optional and must be both supported and authorized.

## New builder checklist

Confirm executable and authentication with status/help commands, supported read/write boundaries, prompt transport, final output capture, and cancellation/resume behavior. Carry the same allowed actions and acceptance criteria into the brief. A builder need not commit or raise an objection to complete its task.

If direct dispatch is unavailable, report the exact missing executable, authentication, or host capability. Provide a self-contained pasteable brief only as the fallback, while completing useful parent work within scope.
