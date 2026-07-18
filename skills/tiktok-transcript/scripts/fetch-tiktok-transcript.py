#!/usr/bin/env python3
"""Fetch and inspect TikTok transcripts with yt-dlp, with an mlx-whisper fallback.

The default fetch path writes transcript artifacts to disk and prints only
metadata plus a short preview so agents do not accidentally load long
transcripts into context. Videos without native captions fall back to local
Whisper transcription (mlx-whisper) on Apple Silicon.
"""

from __future__ import annotations

import argparse
import glob
import html
import json
import os
import platform
import re
import shutil
import subprocess
import sys
import textwrap
from pathlib import Path
from typing import Any


DEFAULT_OUTPUT_DIR = "tiktok-transcripts"
DEFAULT_LANGUAGES = "eng.*,en.*,all"
DEFAULT_WHISPER_MODEL = "mlx-community/whisper-large-v3-turbo"
COOKIES_ENV_VAR = "TIKTOK_TRANSCRIPT_COOKIES_FROM_BROWSER"


def fail(message: str, code: int = 1) -> None:
    print(f"error: {message}", file=sys.stderr)
    raise SystemExit(code)


def require_yt_dlp() -> str:
    path = shutil.which("yt-dlp")
    if not path:
        fail("yt-dlp is required. Install it with: brew install yt-dlp")
    return path


def run_command(args: list[str], *, quiet: bool = False) -> subprocess.CompletedProcess[str]:
    result = subprocess.run(args, text=True, capture_output=True, check=False)
    if result.returncode != 0 and not quiet:
        stderr = result.stderr.strip()
        stdout = result.stdout.strip()
        detail = stderr or stdout or f"exit code {result.returncode}"
        fail(detail)
    return result


def normalize_video_url(url: str) -> str:
    if re.fullmatch(r"\d{6,}", url):
        fail("bare TikTok video ids are ambiguous; pass a full video URL")
    return url


def normalize_channel_url(channel: str) -> str:
    channel = channel.strip()
    if channel.startswith("http"):
        return channel
    handle = channel.lstrip("@")
    if not re.fullmatch(r"[A-Za-z0-9._-]{2,}", handle):
        fail(f"invalid TikTok handle: {channel}")
    return f"https://www.tiktok.com/@{handle}"


def yt_dlp_base_args(args: argparse.Namespace) -> list[str]:
    command = [require_yt_dlp(), "--no-playlist"]
    cookies_from_browser = args.cookies_from_browser or os.environ.get(COOKIES_ENV_VAR)
    if cookies_from_browser:
        command.extend(["--cookies-from-browser", cookies_from_browser])
    if getattr(args, "cookies", None):
        command.extend(["--cookies", args.cookies])
    return command


def load_info(url: str, args: argparse.Namespace) -> dict[str, Any]:
    command = yt_dlp_base_args(args)
    command.extend(["--skip-download", "--dump-single-json", url])
    result = run_command(command)
    try:
        return json.loads(result.stdout)
    except json.JSONDecodeError as exc:
        fail(f"yt-dlp returned invalid JSON: {exc}")


def safe_video_id(info: dict[str, Any]) -> str:
    video_id = str(info.get("id") or "").strip()
    if not re.fullmatch(r"[A-Za-z0-9_-]{6,}", video_id):
        fail("could not determine a safe TikTok video id")
    return video_id


def compact_metadata(
    info: dict[str, Any],
    transcript_file: Path | None = None,
    plain_text_file: Path | None = None,
    transcript_source: str | None = None,
) -> dict[str, Any]:
    return {
        "id": info.get("id"),
        "title": info.get("title"),
        "uploader": info.get("uploader") or info.get("channel"),
        "uploader_id": info.get("uploader_id"),
        "duration": info.get("duration"),
        "upload_date": info.get("upload_date"),
        "webpage_url": info.get("webpage_url"),
        "language": info.get("language"),
        "transcript_source": transcript_source,
        "transcript_file": str(transcript_file) if transcript_file else None,
        "plain_text_file": str(plain_text_file) if plain_text_file else None,
        "subtitle_languages": sorted((info.get("subtitles") or {}).keys()),
        "automatic_caption_languages": sorted((info.get("automatic_captions") or {}).keys()),
    }


def write_json(path: Path, data: Any) -> None:
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def language_patterns(languages: str) -> list[str]:
    return [item.strip() for item in languages.split(",") if item.strip()]


def find_vtt_file(video_dir: Path, video_id: str, languages: str) -> Path | None:
    candidates = [Path(path) for path in glob.glob(str(video_dir / f"{video_id}*.vtt"))]
    candidates = [path for path in candidates if path.name != "transcript.whisper.vtt"]
    if not candidates:
        return None

    for pattern in language_patterns(languages):
        prefix = pattern.rstrip("*").rstrip(".")
        if not prefix or prefix == "all":
            continue
        for path in sorted(candidates):
            parts = path.name.split(".")
            file_lang = ".".join(parts[1:-1]) if len(parts) > 2 else ""
            if file_lang == prefix or file_lang.startswith(prefix):
                return path
    return sorted(candidates)[0]


def parse_time(value: str) -> float:
    value = value.strip().replace(",", ".")
    parts = value.split(":")
    try:
        if len(parts) == 3:
            return int(parts[0]) * 3600 + int(parts[1]) * 60 + float(parts[2])
        if len(parts) == 2:
            return int(parts[0]) * 60 + float(parts[1])
    except ValueError:
        pass
    fail(f"invalid timestamp: {value}")


def parse_time_arg(value: str) -> float:
    if re.fullmatch(r"\d+(\.\d+)?", value):
        return float(value)
    return parse_time(value)


def format_time(seconds: float) -> str:
    seconds = max(0.0, seconds)
    whole = int(seconds)
    millis = int(round((seconds - whole) * 1000))
    if millis == 1000:
        whole += 1
        millis = 0
    hours = whole // 3600
    minutes = (whole % 3600) // 60
    secs = whole % 60
    return f"{hours:02d}:{minutes:02d}:{secs:02d}.{millis:03d}"


def strip_vtt_markup(text: str) -> str:
    text = re.sub(r"<\d{2}:\d{2}:\d{2}\.\d{3}>", "", text)
    text = re.sub(r"<[^>]+>", "", text)
    text = html.unescape(text)
    text = re.sub(r"\s+", " ", text)
    return text.strip()


def parse_vtt(path: Path) -> list[dict[str, Any]]:
    cues: list[dict[str, Any]] = []
    lines = path.read_text(encoding="utf-8", errors="replace").splitlines()
    index = 0
    while index < len(lines):
        line = lines[index].strip("﻿ ")
        if not line or line == "WEBVTT" or line.startswith(("Kind:", "Language:", "NOTE", "STYLE")):
            index += 1
            continue
        if "-->" not in line and index + 1 < len(lines) and "-->" in lines[index + 1]:
            index += 1
            line = lines[index].strip()
        if "-->" not in line:
            index += 1
            continue

        start_raw, end_raw = line.split("-->", 1)
        end_raw = end_raw.strip().split()[0]
        start = parse_time(start_raw)
        end = parse_time(end_raw)
        index += 1

        text_lines: list[str] = []
        while index < len(lines) and lines[index].strip():
            text_lines.append(lines[index].strip())
            index += 1

        text = strip_vtt_markup(" ".join(text_lines))
        if text and (not cues or cues[-1]["text"] != text):
            cues.append(
                {
                    "start": round(start, 3),
                    "end": round(end, 3),
                    "start_time": format_time(start),
                    "end_time": format_time(end),
                    "text": text,
                }
            )
    return cues


def write_markdown(path: Path, info: dict[str, Any], cues: list[dict[str, Any]], source: str) -> None:
    title = info.get("title") or info.get("id") or "TikTok transcript"
    lines = [
        f"# {title}",
        "",
        f"- Source: {info.get('webpage_url') or ''}",
        f"- Creator: {info.get('uploader') or info.get('channel') or ''}",
        f"- Duration: {info.get('duration') or ''}",
        f"- Transcript source: {source}",
        "",
        "## Transcript",
        "",
    ]
    for cue in cues:
        lines.append(f"[{cue['start_time']} -> {cue['end_time']}] {cue['text']}")
    path.write_text("\n".join(lines).strip() + "\n", encoding="utf-8")


def plain_text_from_cues(cues: list[dict[str, Any]], *, wrap_width: int = 0) -> str:
    paragraphs: list[str] = []
    current: list[str] = []
    previous_end: float | None = None

    for cue in cues:
        text = cue["text"].strip()
        if not text:
            continue
        if previous_end is not None and cue["start"] - previous_end > 4 and current:
            paragraphs.append(" ".join(current))
            current = []
        current.append(text)
        previous_end = cue["end"]

    if current:
        paragraphs.append(" ".join(current))

    if wrap_width > 0:
        paragraphs = [
            textwrap.fill(paragraph, width=wrap_width, break_long_words=False)
            for paragraph in paragraphs
        ]
    return "\n\n".join(paragraphs).strip() + "\n"


# --- Whisper fallback -------------------------------------------------------


def whisper_available() -> bool:
    return bool(shutil.which("mlx_whisper") or shutil.which("uvx"))


def require_apple_silicon() -> None:
    if sys.platform != "darwin" or platform.machine() != "arm64":
        fail(
            "the whisper fallback uses mlx-whisper, which needs Apple Silicon. "
            "Rerun with --whisper never, or transcribe the audio with faster-whisper."
        )


def whisper_command() -> list[str]:
    if shutil.which("mlx_whisper"):
        return ["mlx_whisper"]
    if shutil.which("uvx"):
        return ["uvx", "--from", "mlx-whisper", "mlx_whisper"]
    fail("mlx-whisper is not available. Install uv (brew install uv) or pip install mlx-whisper")


def download_audio(url: str, video_dir: Path, video_id: str, args: argparse.Namespace) -> Path:
    existing = sorted(video_dir.glob(f"{video_id}.audio.*"))
    if existing and not args.refresh:
        return existing[0]
    command = yt_dlp_base_args(args)
    command.extend(
        [
            "-f",
            "bestaudio/best",
            "-x",
            "--audio-format",
            "m4a",
            "-o",
            str(video_dir / f"{video_id}.audio.%(ext)s"),
            url,
        ]
    )
    run_command(command)
    downloaded = sorted(video_dir.glob(f"{video_id}.audio.*"))
    if not downloaded:
        fail(f"audio download produced no file in {video_dir}")
    return downloaded[0]


def transcribe_with_whisper(
    audio_file: Path, video_dir: Path, args: argparse.Namespace
) -> Path:
    vtt_path = video_dir / "transcript.whisper.vtt"
    if vtt_path.exists() and not args.refresh:
        return vtt_path
    require_apple_silicon()
    # mlx_whisper truncates --output-name at the first dot, so use a dot-free
    # name and rename afterwards.
    command = whisper_command() + [
        str(audio_file),
        "--model",
        args.whisper_model,
        "--output-format",
        "vtt",
        "--output-dir",
        str(video_dir),
        "--output-name",
        "whisper-output",
    ]
    if args.whisper_language:
        command.extend(["--language", args.whisper_language])
    result = subprocess.run(command, text=True, capture_output=True, check=False)
    raw_path = video_dir / "whisper-output.vtt"
    if result.returncode != 0 or not raw_path.exists():
        detail = (result.stderr or result.stdout or "").strip()
        fail(f"mlx-whisper transcription failed: {detail[-2000:]}")
    raw_path.replace(vtt_path)
    return vtt_path


# --- Artifact helpers -------------------------------------------------------


def resolve_artifact_dir(path: str) -> Path:
    candidate = Path(path)
    if candidate.is_file():
        return candidate.parent
    if candidate.is_dir():
        return candidate
    fail(f"artifact path does not exist: {path}")


def load_cues(path: str) -> tuple[Path, list[dict[str, Any]]]:
    artifact_dir = resolve_artifact_dir(path)
    transcript_json = artifact_dir / "transcript.json"
    if not transcript_json.exists():
        fail(f"missing transcript.json in {artifact_dir}")
    return artifact_dir, json.loads(transcript_json.read_text(encoding="utf-8"))


def print_cues(cues: list[dict[str, Any]]) -> None:
    for cue in cues:
        print(f"[{cue['start_time']} -> {cue['end_time']}] {cue['text']}")


# --- Fetch core -------------------------------------------------------------


def fetch_video(url: str, args: argparse.Namespace, *, quiet: bool = False) -> dict[str, Any]:
    """Fetch one video's transcript. Returns a summary dict for channel mode."""
    info = load_info(url, args)
    video_id = safe_video_id(info)
    video_dir = Path(args.output_dir) / video_id
    video_dir.mkdir(parents=True, exist_ok=True)

    info_path = video_dir / "source.info.json"
    if args.refresh or not info_path.exists():
        write_json(info_path, info)

    subtitle_file = find_vtt_file(video_dir, video_id, args.languages)
    if args.refresh or not subtitle_file:
        command = yt_dlp_base_args(args)
        command.extend(
            [
                "--skip-download",
                "--write-subs",
                "--write-auto-subs",
                "--sub-format",
                "vtt",
                "--sub-langs",
                args.languages,
                "-o",
                str(video_dir / "%(id)s.%(ext)s"),
                url,
            ]
        )
        run_command(command)
        subtitle_file = find_vtt_file(video_dir, video_id, args.languages)

    transcript_source = "tiktok-captions"
    if args.whisper == "always" or (not subtitle_file and args.whisper == "auto"):
        audio_file = download_audio(url, video_dir, video_id, args)
        subtitle_file = transcribe_with_whisper(audio_file, video_dir, args)
        transcript_source = f"mlx-whisper:{args.whisper_model}"

    if not subtitle_file:
        write_json(video_dir / "metadata.compact.json", compact_metadata(info))
        return {
            "id": video_id,
            "title": info.get("title"),
            "status": "no-captions",
            "artifact_dir": str(video_dir),
        }

    cues = parse_vtt(subtitle_file)
    if not cues:
        fail(f"subtitle file contained no cues: {subtitle_file}")

    transcript_vtt = video_dir / "transcript.vtt"
    if subtitle_file.resolve() != transcript_vtt.resolve():
        transcript_vtt.write_text(
            subtitle_file.read_text(encoding="utf-8", errors="replace"), encoding="utf-8"
        )

    transcript_json = video_dir / "transcript.json"
    transcript_md = video_dir / "transcript.md"
    transcript_txt = video_dir / "transcript.txt"
    write_json(transcript_json, cues)
    write_markdown(transcript_md, info, cues, transcript_source)
    transcript_txt.write_text(plain_text_from_cues(cues), encoding="utf-8")
    write_json(
        video_dir / "metadata.compact.json",
        compact_metadata(
            info,
            transcript_file=transcript_md,
            plain_text_file=transcript_txt,
            transcript_source=transcript_source,
        ),
    )

    if not quiet:
        print(f"video_id: {video_id}")
        print(f"title: {info.get('title') or ''}")
        print(f"creator: {info.get('uploader') or info.get('channel') or ''}")
        print(f"duration_seconds: {info.get('duration') or ''}")
        print(f"transcript_source: {transcript_source}")
        print(f"cue_count: {len(cues)}")
        print(f"artifact_dir: {video_dir}")
        print(f"transcript_txt: {transcript_txt}")
        print("")
        print("preview:")
        print_cues(cues[: args.preview_lines])

    return {
        "id": video_id,
        "title": info.get("title"),
        "status": transcript_source,
        "cue_count": len(cues),
        "artifact_dir": str(video_dir),
    }


# --- Commands ---------------------------------------------------------------


def command_list(args: argparse.Namespace) -> None:
    # TikTok caption info is missing from yt-dlp's JSON dump even when captions
    # exist, so ask --list-subs directly.
    command = yt_dlp_base_args(args)
    command.extend(["--skip-download", "--list-subs", normalize_video_url(args.url)])
    result = run_command(command)
    for line in result.stdout.splitlines():
        if line.startswith(("[info]", "Language")) or re.match(r"^\S+\s+vtt", line):
            print(line)
    if "Available subtitles" not in result.stdout:
        print("no native captions (fetch will fall back to mlx-whisper)")


def command_fetch(args: argparse.Namespace) -> None:
    fetch_video(normalize_video_url(args.url), args)


def command_channel(args: argparse.Namespace) -> None:
    channel_url = normalize_channel_url(args.channel)
    command = yt_dlp_base_args(args)
    command.remove("--no-playlist")
    command.extend(["--flat-playlist", "--print", "%(url)s"])
    if args.limit:
        command.extend(["--playlist-end", str(args.limit)])
    command.append(channel_url)
    result = run_command(command)
    urls = [line.strip() for line in result.stdout.splitlines() if line.strip()]
    if not urls:
        fail(f"no videos found for {channel_url}")

    print(f"channel: {channel_url}")
    print(f"video_count: {len(urls)}")
    print("")

    summaries: list[dict[str, Any]] = []
    for index, url in enumerate(urls, start=1):
        try:
            summary = fetch_video(url, args, quiet=True)
        except SystemExit:
            summary = {"id": url, "title": None, "status": "failed", "artifact_dir": None}
        summaries.append(summary)
        title = (summary.get("title") or "")[:60]
        print(f"[{index}/{len(urls)}] {summary['id']} | {summary['status']} | {title}")

    ok = [s for s in summaries if s["status"] not in ("no-captions", "failed")]
    missing = [s for s in summaries if s["status"] == "no-captions"]
    failed = [s for s in summaries if s["status"] == "failed"]
    index_path = Path(args.output_dir) / "channel.index.json"
    write_json(index_path, {"channel": channel_url, "videos": summaries})

    print("")
    print(f"transcribed: {len(ok)}")
    print(f"no_captions: {len(missing)}")
    print(f"failed: {len(failed)}")
    print(f"index: {index_path}")
    if missing and args.whisper == "never":
        print("hint: rerun with --whisper auto to transcribe the caption-less videos locally")


def command_preview(args: argparse.Namespace) -> None:
    _, cues = load_cues(args.artifact)
    print_cues(cues[: args.lines])


def command_search(args: argparse.Namespace) -> None:
    _, cues = load_cues(args.artifact)
    query = args.query.lower()
    matches: list[dict[str, Any]] = []
    for index, cue in enumerate(cues):
        if query in cue["text"].lower():
            start = max(0, index - args.context)
            end = min(len(cues), index + args.context + 1)
            matches.extend(cues[start:end])
            if len(matches) >= args.max_cues:
                break
    if not matches:
        print("no matches")
        return
    deduped: list[dict[str, Any]] = []
    seen: set[tuple[float, str]] = set()
    for cue in matches:
        key = (cue["start"], cue["text"])
        if key not in seen:
            deduped.append(cue)
            seen.add(key)
    print_cues(deduped[: args.max_cues])


def command_excerpt(args: argparse.Namespace) -> None:
    _, cues = load_cues(args.artifact)
    start = parse_time_arg(args.start)
    end = parse_time_arg(args.end)
    if end <= start:
        fail("--end must be after --start")
    print_cues([cue for cue in cues if cue["end"] >= start and cue["start"] <= end])


def command_text(args: argparse.Namespace) -> None:
    _, cues = load_cues(args.artifact)
    text = plain_text_from_cues(cues, wrap_width=args.wrap)
    if args.max_chars is not None and len(text) > args.max_chars:
        print(text[: args.max_chars].rstrip())
        print(f"\n[truncated: omit --max-chars to print {len(text)} characters]")
        return
    print(text, end="")


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Fetch and inspect TikTok transcripts.")
    subparsers = parser.add_subparsers(dest="command", required=True)

    def add_cookie_args(command: argparse.ArgumentParser) -> None:
        command.add_argument("--cookies-from-browser", help="Passed to yt-dlp, e.g. safari or chrome:Profile 1")
        command.add_argument("--cookies", help="Path to a Netscape cookies.txt file")

    def add_fetch_args(command: argparse.ArgumentParser) -> None:
        command.add_argument("--languages", default=DEFAULT_LANGUAGES, help=f"yt-dlp sub language spec. Default: {DEFAULT_LANGUAGES}")
        command.add_argument("--output-dir", default=DEFAULT_OUTPUT_DIR, help=f"Output root. Default: {DEFAULT_OUTPUT_DIR}")
        command.add_argument("--refresh", action="store_true", help="Re-download subtitles/audio even when cached.")
        command.add_argument("--whisper", choices=["auto", "always", "never"], default="auto", help="Whisper fallback mode. auto = only when no native captions. Default: auto")
        command.add_argument("--whisper-model", default=DEFAULT_WHISPER_MODEL, help=f"mlx-whisper model repo. Default: {DEFAULT_WHISPER_MODEL}")
        command.add_argument("--whisper-language", help="Force the spoken language, e.g. en or nl. Default: autodetect")
        command.add_argument("--preview-lines", type=int, default=5, help="Number of cues to print after fetch.")
        add_cookie_args(command)

    list_parser = subparsers.add_parser("list", help="List available subtitle languages for a video.")
    list_parser.add_argument("url", help="TikTok video URL")
    add_cookie_args(list_parser)
    list_parser.set_defaults(func=command_list)

    fetch_parser = subparsers.add_parser("fetch", help="Fetch one video's transcript and write artifacts.")
    fetch_parser.add_argument("url", help="TikTok video URL")
    add_fetch_args(fetch_parser)
    fetch_parser.set_defaults(func=command_fetch)

    channel_parser = subparsers.add_parser("channel", help="Fetch transcripts for a user's videos.")
    channel_parser.add_argument("channel", help="TikTok handle (@user) or profile URL")
    channel_parser.add_argument("--limit", type=int, help="Only process the N most recent videos.")
    add_fetch_args(channel_parser)
    channel_parser.set_defaults(func=command_channel)

    preview_parser = subparsers.add_parser("preview", help="Print the first few transcript cues.")
    preview_parser.add_argument("artifact", help="Artifact directory or transcript.json path")
    preview_parser.add_argument("--lines", type=int, default=8)
    preview_parser.set_defaults(func=command_preview)

    search_parser = subparsers.add_parser("search", help="Search a saved transcript and print matching cues.")
    search_parser.add_argument("artifact", help="Artifact directory or transcript.json path")
    search_parser.add_argument("query")
    search_parser.add_argument("--context", type=int, default=1, help="Neighboring cues to include around each match.")
    search_parser.add_argument("--max-cues", type=int, default=12)
    search_parser.set_defaults(func=command_search)

    excerpt_parser = subparsers.add_parser("excerpt", help="Print cues in a time range.")
    excerpt_parser.add_argument("artifact", help="Artifact directory or transcript.json path")
    excerpt_parser.add_argument("--start", required=True, help="Start time, e.g. 00:00:30 or seconds.")
    excerpt_parser.add_argument("--end", required=True, help="End time, e.g. 00:01:10 or seconds.")
    excerpt_parser.set_defaults(func=command_excerpt)

    text_parser = subparsers.add_parser("text", help="Print timestamp-free transcript text.")
    text_parser.add_argument("artifact", help="Artifact directory or transcript.json path")
    text_parser.add_argument("--max-chars", type=int, help="Optional preview character limit.")
    text_parser.add_argument("--wrap", type=int, default=0, help="Optional text wrap width. Default: no wrapping.")
    text_parser.set_defaults(func=command_text)

    return parser


def main() -> None:
    parser = build_parser()
    args = parser.parse_args()
    args.func(args)


if __name__ == "__main__":
    main()
