# skills

Skills for designers, builders & engineers. Install them into Claude Code as a plugin, or into any agent with the `skills` CLI.

## What's inside

- **smooth-shadows** — generate layered, smooth `box-shadow` CSS (the shadows.brumm.af / Tobias Ahlin technique) for soft, realistic elevation. Outputs ready-to-paste CSS or Tailwind values.
- **ultracode** — run complex work through a portable dynamic-workflow pattern: plan, fan out to subagents when available, preserve artifacts, integrate results, and verify before handoff.
- **autopilot-interview** — interview a plan on autopilot: auto-decide low-risk details, escalate only the high-stakes, hard-to-reverse choices to you, and keep a scratch decision log for long sessions.
- **architect-loop** — act as the architect (and creative director for UI work) over any fast builder — GPT-5.5 Codex, Cursor Composer, Grok, or whatever comes next: read `docs/HANDOFF.md`, rule on the builder's disagreements, judge raw results against frozen gates, and write the next one-PR slice spec. The repo is the memory; the human owns the gate calls.

## Install

### As a Claude Code plugin

```
/plugin marketplace add dedene/skills
/plugin install dedene-skills@dedene
```

The skills are then available as `/dedene-skills:smooth-shadows`, `/dedene-skills:ultracode`, `/dedene-skills:autopilot-interview`, and `/dedene-skills:architect-loop`.

### With the skills CLI

Works with Claude Code, Cursor, Codex, and other agents via [vercel-labs/skills](https://github.com/vercel-labs/skills):

```
npx skills add dedene/skills
```

To grab just one skill:

```
npx skills add dedene/skills --skill smooth-shadows
npx skills add dedene/skills --skill ultracode
npx skills add dedene/skills --skill autopilot-interview
npx skills add dedene/skills --skill architect-loop
```

## License

MIT — see [LICENSE](LICENSE).
