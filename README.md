# skills

Skills for designers, builders & engineers. Install them into Claude Code as a plugin, or into any agent with the `skills` CLI.

## What's inside

- **smooth-shadows** — generate layered, smooth `box-shadow` CSS (the shadows.brumm.af / Tobias Ahlin technique) for soft, realistic elevation. Outputs ready-to-paste CSS or Tailwind values.
- **ultracode** — run complex work through a Codex-friendly dynamic-workflow pattern: phase graph, approval card, visible progress table, bounded subagents when available, durable run ledger, result reduction, and verification before handoff. Ships as a separate opt-in plugin (`extras/`) since Claude Code has native ultracode workflows; still installs everywhere via the skills CLI.
- **autopilot-interview** — interview a plan on autopilot: auto-decide low-risk details, escalate only the high-stakes, hard-to-reverse choices to you, and keep a scratch decision log for long sessions.
- **architect-loop** — coordinate bounded builder slices, review evidence and objections, and carry existing permissions through implementation and handoff. Model selection follows the host configuration.
- **youtube-transcript** — fetch YouTube captions with `yt-dlp`, save cached transcript artifacts, and inspect previews/search results/excerpts without loading full transcripts into agent context.
- **youtube-channel-search** — research topics inside a known YouTube channel with `yt-dlp` catalogs, metadata ranking, transcript hydration, and local transcript ranking.
- **tiktok-transcript** — fetch TikTok captions with `yt-dlp` for a single video or a whole channel, save cached transcript artifacts, and fall back to local `mlx-whisper` transcription (Apple Silicon) when a video has no native captions.
- **idea-to-visual** — turn an idea, quote, or chapter into a simple explanatory visual: brainstorm text and visual elements, draft 10 concepts across visual types, filter them for clarity, then write or run the image prompt (Higgsfield via mcporter, Gemini / Nano Banana, ChatGPT image, or paste-ready prompts). Also does style transfer of rough sketches, tracing-friendly metaphor objects, caption brainstorms, and a reusable house style.
- **go-cli-builder** — scaffold or extend Go CLIs with explicit command, authentication, output, and verification contracts; scale research to the affected surface.
- **last30days-local** — research what people said about a topic in the last 30 days across X, Reddit, Hacker News, YouTube, LinkedIn, Threads, TikTok, Instagram, Bluesky, GitHub, Pinterest, Polymarket, and the web — no API keys, using the local logged-in browser (Aside) plus `yt-dlp`, `gh`, and keyless HTTP. Inspired by [mvanhorn/last30days-skill](https://github.com/mvanhorn/last30days-skill).
- **Conversion skills for service-business websites** — four skills that share one `.agents/business-context.md` file and a rule base distilled from 63 [Wes McDowell](https://www.youtube.com/@WesMcDowellInc) videos (2018–2026), with structure ideas adapted from [coreyhaines31/marketingskills](https://github.com/coreyhaines31/marketingskills) (MIT). Optional Belgium/EU layer for language, consent, reviews, and legal footer rules.
  - **site-brief** — draft the business context (ideal customer, the site's one job, primary CTA, transitional offer, proof inventory, locale) from an existing site or repo, then interview only for gaps.
  - **conversion-audit** — audit a homepage or landing page: 5-second test, then prioritized quick wins, high-impact changes, and test ideas, each citing a rule and evidence.
  - **page-copy** — write homepage, landing, services, about, or contact pages as wireframe plus copy per section, with headline/CTA alternatives and no invented proof.
  - **lead-offer** — design a transitional offer (lead magnet, quiz, micro-app), its opt-in and thank-you page, and a short nurture sequence.
- **claude-codex** — Claude/Fable bridge for bounded implementation and review through the Codex CLI, using the selected model and effort. Separate opt-in plugin (`claude-codex/`); not part of `dedene-skills`.

## Install

### As a Claude Code plugin

```
/plugin marketplace add dedene/skills
/plugin install dedene-skills@dedene
```

The skills are then available as `/dedene-skills:smooth-shadows`, `/dedene-skills:autopilot-interview`, `/dedene-skills:architect-loop`, `/dedene-skills:youtube-transcript`, `/dedene-skills:youtube-channel-search`, `/dedene-skills:tiktok-transcript`, `/dedene-skills:idea-to-visual`, `/dedene-skills:site-brief`, `/dedene-skills:conversion-audit`, `/dedene-skills:page-copy`, and `/dedene-skills:lead-offer`.

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
npx skills add dedene/skills --skill tiktok-transcript
npx skills add dedene/skills --skill idea-to-visual
npx skills add dedene/skills --skill site-brief
npx skills add dedene/skills --skill conversion-audit
npx skills add dedene/skills --skill page-copy
npx skills add dedene/skills --skill lead-offer
```

## Maintaining Peter's installations

`config/skill-sources.json` records the canonical source and existing installation targets for each owned skill across this repository and prompt-engineering-club. This repository owns smooth-shadows; its club copy is a sync target. Skills without targets remain uninstalled.

This manifest and `config/AGENTS.md` are Peter's machine-specific configuration, not team installation defaults. Teammates should supply their own source/target manifest with `--manifest <file>`. Shared MCP skills accept `MCPORTER_BIN` as an executable path; configure any host-required credential wrapper there, otherwise they use the installed `mcporter` command.

Run from this repository:

```sh
python3 scripts/sync-skills.py --check
python3 scripts/sync-skills.py --plan /tmp/skill-sync-plan.json
# Review the plan before applying it.
python3 scripts/sync-skills.py --apply /tmp/skill-sync-plan.json
```

Apply verifies source and destination hashes before writing, backs up replaced files, and preserves destination-only files. Reconcile unexpected drift in the canonical source before creating a new plan.

`config/AGENTS.md` is Peter's canonical personal instruction base; the Compound plugin appends its generated tool map when installed. `config/screenshots.md` holds the conditional screenshot recipe. The club maintains its separate team instruction base.

`config/disabled-upstream-skills.json` records excluded duplicate Superpowers entries and broad bootstrap skills. Their matching `[[skills.config]]` entries in `~/.codex/config.toml` use `enabled = false`; upstream bodies remain untouched. Recheck versioned plugin paths after upgrades and restart Codex after configuration changes. Re-enable a disabled entry deliberately when needed. Owned architect-loop, autopilot-interview, and ultracode instead use `allow_implicit_invocation: false`, retaining explicit invocation.

## License

MIT — see [LICENSE](LICENSE).
