# skills

Skills for designers, builders & engineers. Install them into Claude Code as a plugin, or into any agent with the `skills` CLI.

## What's inside

- **smooth-shadows** — generate layered, smooth `box-shadow` CSS (the shadows.brumm.af / Tobias Ahlin technique) for soft, realistic elevation. Outputs ready-to-paste CSS or Tailwind values.
- **ultracode** — run complex work through a portable dynamic-workflow pattern: plan, fan out to subagents when available, preserve artifacts, integrate results, and verify before handoff.
- **high-stakes-grill** — stress-test plans with selective autonomy: auto-decide low-risk details, ask for trajectory-setting choices, and keep a scratch decision log for long sessions.

## Install

### As a Claude Code plugin

```
/plugin marketplace add dedene/skills
/plugin install dedene-skills@dedene
```

The skills are then available as `/dedene-skills:smooth-shadows`, `/dedene-skills:ultracode`, and `/dedene-skills:high-stakes-grill`.

### With the skills CLI

Works with Claude Code, Cursor, Codex, and other agents via [vercel-labs/skills](https://github.com/vercel-labs/skills):

```
npx skills add dedene/skills
```

To grab just one skill:

```
npx skills add dedene/skills --skill smooth-shadows
npx skills add dedene/skills --skill ultracode
npx skills add dedene/skills --skill high-stakes-grill
```

## License

MIT — see [LICENSE](LICENSE).
