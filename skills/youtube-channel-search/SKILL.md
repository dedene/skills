---
name: youtube-channel-search
description: Research topics inside a known YouTube channel without a YouTube Data API key. Use when the user provides a YouTube channel URL/handle and wants to find, rank, shortlist, or investigate videos relevant to a topic using channel metadata and optional transcript text.
---

# YouTube Channel Search

Search inside a known YouTube channel with a reproducible local workflow:

1. Build a channel catalog with `yt-dlp`.
2. Rank likely videos from metadata.
3. Fetch transcripts only for the shortlist.
4. Rank transcript text for the final answer.

Prefer this over browser automation. Use `agent-browser` only for manual UI checks or auth/consent fallbacks.

## Quick Start

```bash
python3 <this-skill-dir>/scripts/youtube-channel-search.py catalog \
  'https://www.youtube.com/@CHANNEL/videos' \
  --output-dir /tmp/channel-research \
  --mode flat \
  --limit 300

python3 <this-skill-dir>/scripts/youtube-channel-search.py catalog \
  'https://www.youtube.com/@CHANNEL/videos' \
  --output-dir /tmp/channel-research \
  --mode full \
  --limit 140

python3 <this-skill-dir>/scripts/youtube-channel-search.py search \
  /tmp/channel-research \
  'landing pages storytelling websites' \
  --since 2024-06-17 \
  --top 20

python3 <this-skill-dir>/scripts/youtube-channel-search.py fetch-transcripts \
  /tmp/channel-research \
  'landing pages storytelling websites' \
  --since 2024-06-17 \
  --top 15

python3 <this-skill-dir>/scripts/youtube-channel-search.py rank-transcripts \
  /tmp/channel-research \
  'landing pages storytelling websites' \
  --top 10
```

## Workflow

- Start with `catalog --mode flat` for a fast title-only index.
- Use `catalog --mode full --limit N` when dates/descriptions matter. Full mode is slower because it visits each video page, but it enables `--since` and better ranking.
- Use `search` for the metadata shortlist. This prints compact ranked results and stores `search-results.json`.
- Use `fetch-transcripts` only for likely candidates. It calls the sibling `youtube-transcript` skill and writes transcript artifacts under `transcripts/`.
- Use `rank-transcripts` for the final list. It reads `transcript.txt`, scores local content, and prints snippets.

## Files

Default output directory:

```text
channel-research/
├── catalog-flat.ndjson
├── catalog-full.ndjson
├── search-results.json
└── transcripts/
    └── VIDEO_ID/
        ├── metadata.compact.json
        ├── transcript.json
        ├── transcript.md
        └── transcript.txt
```

## Notes

- `yt-dlp` is required.
- Date filters use `YYYY-MM-DD` or `YYYYMMDD`. Records with no date are kept, not discarded, because flat catalogs usually omit upload dates.
- The search ranking is lexical, not embedding-based. For broad conceptual research, fetch more transcripts and let the final agent reasoning judge the shortlist.
- Keep large channel artifacts in `/tmp` unless the user asks to persist them in the repo.
