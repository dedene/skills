---
name: tiktok-transcript
description: Fetch TikTok transcripts/captions into cached local files, for a single video or all videos of a channel/user, falling back to local mlx-whisper transcription when a video has no native captions. Use when the user provides a TikTok URL, video ID, or @handle and asks to get, fetch, download, search, excerpt, summarize, or otherwise use TikTok transcripts/captions/subtitles.
---

# TikTok Transcript

Fetch TikTok captions with `yt-dlp`, save durable transcript artifacts, and keep the full transcript out of context unless the user explicitly asks to inspect it. Videos without native captions are transcribed locally with `mlx-whisper` (Apple Silicon).

This skill mirrors the workflow shape of the sibling `youtube-transcript` skill.

## Workflow

1. Resolve this skill directory and run the bundled script. Always single-quote TikTok URLs in zsh because `?` can be treated as a glob.
2. Fetch to local artifacts with `fetch` (one video) or `channel` (a user's videos). Do not read `transcript.md` or `transcript.json` into context by default.
3. Use `transcript.txt` for summaries or other content-only work; it removes timestamps and is cheaper to read than `transcript.md`.
4. Use `preview`, `search`, `excerpt`, or bounded `text` output when later work needs only a small portion.
5. Read the full transcript only when the task truly requires full-document reasoning and no smaller excerpt/search path is enough.

## Commands

```bash
python3 <this-skill-dir>/scripts/fetch-tiktok-transcript.py list 'https://www.tiktok.com/@user/video/VIDEO_ID'

python3 <this-skill-dir>/scripts/fetch-tiktok-transcript.py fetch 'https://www.tiktok.com/@user/video/VIDEO_ID' \
  --output-dir tiktok-transcripts

# All (or the N most recent) videos of a channel:
python3 <this-skill-dir>/scripts/fetch-tiktok-transcript.py channel @user --limit 20

python3 <this-skill-dir>/scripts/fetch-tiktok-transcript.py preview tiktok-transcripts/VIDEO_ID

python3 <this-skill-dir>/scripts/fetch-tiktok-transcript.py search tiktok-transcripts/VIDEO_ID 'topic or phrase'

python3 <this-skill-dir>/scripts/fetch-tiktok-transcript.py excerpt tiktok-transcripts/VIDEO_ID \
  --start 00:00:30 \
  --end 00:01:10

python3 <this-skill-dir>/scripts/fetch-tiktok-transcript.py text tiktok-transcripts/VIDEO_ID --max-chars 4000
```

The `fetch` command prints a compact result with the video title, transcript source, cue count, and a short preview. It intentionally does not print the full transcript. The `channel` command prints one status line per video plus a summary, and writes `channel.index.json`.

## Whisper fallback

- Not every TikTok video has captions; it depends on whether the creator enabled them.
- `--whisper auto` (default) transcribes locally with `mlx-whisper` only when no native captions exist: audio is downloaded via `yt-dlp -x` and transcribed on-device. `--whisper always` forces Whisper even when captions exist; `--whisper never` skips it (caption-less videos are then reported as `no-captions`).
- Requires Apple Silicon. The script uses an installed `mlx_whisper` binary or falls back to `uvx --from mlx-whisper mlx_whisper` (needs `uv`).
- Default model is `mlx-community/whisper-large-v3-turbo` (good speed/quality; ~1.5 GB download on first use). Override with `--whisper-model`, e.g. `mlx-community/whisper-tiny` for quick tests. Use `--whisper-language nl` etc. when autodetection picks wrong.
- For bulk channel runs, a cheap first pass is `channel @user --whisper never`, then rerun with `--whisper auto` to fill in only the caption-less videos (artifacts are cached; nothing is re-fetched).
- `transcript_source` in `metadata.compact.json` and the fetch output records whether the transcript came from `tiktok-captions` or `mlx-whisper:<model>`.

## Artifacts

Default output:

```text
tiktok-transcripts/
├── channel.index.json        # channel mode only: per-video status
└── VIDEO_ID/
    ├── metadata.compact.json
    ├── source.info.json
    ├── VIDEO_ID.audio.m4a    # whisper fallback only
    ├── transcript.whisper.vtt  # whisper fallback only
    ├── transcript.json
    ├── transcript.md
    ├── transcript.txt
    └── transcript.vtt
```

- `transcript.json` contains timestamped cue objects for programmatic search/excerpt.
- `transcript.txt` contains timestamp-free plain text for summarization and other content-only tasks.
- `metadata.compact.json` is the small metadata file to read into context when needed.

## Fallbacks

If yt-dlp reports rate limiting, bot detection, login walls, or region errors:

1. Retry with browser cookies (Peter is logged in to TikTok in his browsers):

   ```bash
   python3 <this-skill-dir>/scripts/fetch-tiktok-transcript.py fetch 'URL' --cookies-from-browser chrome
   ```

   `chrome`, `chrome:Profile 1`, `firefox`, and `safari` are common values. The script also honors `TIKTOK_TRANSCRIPT_COOKIES_FROM_BROWSER`.

2. If yt-dlp warns about impersonation and requests start failing, install the impersonation dependency it suggests (curl_cffi) per https://github.com/yt-dlp/yt-dlp#impersonation.

3. If `channel` undercounts a large profile (known yt-dlp TikTok pagination flakiness), harvest video links by scrolling the profile page in a real logged-in browser session (Aside or agent-browser), then `fetch` each URL individually.

## Notes

- `yt-dlp` is the only required external binary for captioned videos; `uv` (or `pip install mlx-whisper`) enables the Whisper fallback.
- TikTok caption info is missing from yt-dlp's JSON metadata even when captions exist — only `list`/`fetch` (which use `--list-subs`/`--write-subs`) can see them. Do not conclude "no captions" from `source.info.json`.
- Use `--refresh` to re-download captions/audio and re-transcribe.
- Private accounts fail even with valid cookies (open yt-dlp issue as of 2026).
