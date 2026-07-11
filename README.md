# skills

Skills for designers, builders & engineers. Install them into Claude Code as a plugin, or into any agent with the `skills` CLI.

## What's inside

- **smooth-shadows** — generate layered, smooth `box-shadow` CSS (the shadows.brumm.af / Tobias Ahlin technique) for soft, realistic elevation. Outputs ready-to-paste CSS or Tailwind values.
- **ultracode** — run complex work through a Codex-friendly dynamic-workflow pattern: phase graph, approval card, visible progress table, bounded subagents when available, durable run ledger, result reduction, and verification before handoff. Ships as a separate opt-in plugin (`extras/`) since Claude Code has native ultracode workflows; still installs everywhere via the skills CLI.
- **autopilot-interview** — interview a plan on autopilot: auto-decide low-risk details, escalate only the high-stakes, hard-to-reverse choices to you, and keep a scratch decision log for long sessions.
- **architect-loop** — act as the architect (and creative director for UI work) over any fast builder — GPT-5.5 Codex, Cursor Composer, Grok, or whatever comes next: read `docs/HANDOFF.md`, rule on the builder's disagreements, judge raw results against frozen gates, and write the next one-PR slice spec. The repo is the memory; the human owns the gate calls.
- **youtube-transcript** — fetch YouTube captions with `yt-dlp`, save cached transcript artifacts, and inspect previews/search results/excerpts without loading full transcripts into agent context.
- **youtube-channel-search** — research topics inside a known YouTube channel with `yt-dlp` catalogs, metadata ranking, transcript hydration, and local transcript ranking.
- **go-cli-builder** — scaffold and iterate on small, well-tested local Go CLIs, with a quality loop that leans on GPT-5.5 (via Codex) for the mechanical build work.
- **last30days-local** — research what people said about a topic in the last 30 days across X, Reddit, Hacker News, YouTube, LinkedIn, Threads, TikTok, Instagram, Bluesky, GitHub, Pinterest, Polymarket, and the web — no API keys, using the local logged-in browser (Aside) plus `yt-dlp`, `gh`, and keyless HTTP. Inspired by [mvanhorn/last30days-skill](https://github.com/mvanhorn/last30days-skill).
- **claude-codex** — Claude/Fable-only bridge for sending bounded implementation and review work to GPT-5.5 through the Codex CLI. Separate opt-in plugin (`claude-codex/`); not part of `dedene-skills`.

## Install

### As a Claude Code plugin

```
/plugin marketplace add dedene/skills
/plugin install dedene-skills@dedene
```

The skills are then available as `/dedene-skills:smooth-shadows`, `/dedene-skills:autopilot-interview`, `/dedene-skills:architect-loop`, `/dedene-skills:youtube-transcript`, and `/dedene-skills:youtube-channel-search`.

The ultracode skill is intentionally not part of `dedene-skills` — Claude Code ships native ultracode workflows. For other hosts, it is available as a separate plugin:

```
/plugin install ultracode@dedene
```

The Codex delegation/review bridge is intentionally Claude/Fable-only for now:

```
/plugin install claude-codex@dedene
```

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
npx skills add dedene/skills --skill youtube-transcript
npx skills add dedene/skills --skill youtube-channel-search
```

## License

MIT — see [LICENSE](LICENSE).
