#!/usr/bin/env python3
"""Research topics inside a YouTube channel with yt-dlp and local transcripts."""

from __future__ import annotations

import argparse
import json
import math
import os
import re
import shutil
import subprocess
import sys
from pathlib import Path
from typing import Any


DATE_RE = re.compile(r"^\d{4}-?\d{2}-?\d{2}$")
TOKEN_RE = re.compile(r"[a-z0-9][a-z0-9'-]*")
DEFAULT_OUTPUT_DIR = "youtube-channel-research"


def fail(message: str, code: int = 1) -> None:
    print(f"error: {message}", file=sys.stderr)
    raise SystemExit(code)


def require_binary(name: str) -> str:
    path = shutil.which(name)
    if not path:
        fail(f"{name} is required")
    return path


def normalize_date(value: str | None) -> str | None:
    if not value:
        return None
    value = str(value).strip()
    if not DATE_RE.match(value):
        return None
    return value.replace("-", "")


def parse_ndjson(path: Path) -> list[dict[str, Any]]:
    if not path.exists():
        return []
    records: list[dict[str, Any]] = []
    for line in path.read_text(encoding="utf-8").splitlines():
        if line.strip():
            records.append(json.loads(line))
    return records


def write_json(path: Path, data: Any) -> None:
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def catalog_path(output_dir: Path, mode: str) -> Path:
    return output_dir / f"catalog-{mode}.ndjson"


def best_catalog(output_dir: Path) -> Path:
    full = catalog_path(output_dir, "full")
    flat = catalog_path(output_dir, "flat")
    if full.exists():
        return full
    if flat.exists():
        return flat
    fail(f"no catalog found in {output_dir}; run catalog first")


def run_yt_dlp_catalog(channel_url: str, output_path: Path, mode: str, limit: int | None) -> None:
    output_path.parent.mkdir(parents=True, exist_ok=True)
    command = [
        require_binary("yt-dlp"),
        "--no-update",
        "--quiet",
        "--skip-download",
        "--dump-json",
    ]
    if mode == "flat":
        command.insert(3, "--flat-playlist")
    if limit:
        command.extend(["--playlist-end", str(limit)])
    command.append(channel_url)

    with output_path.open("w", encoding="utf-8") as handle:
        try:
            result = subprocess.run(command, text=True, stdout=handle, stderr=subprocess.PIPE, check=False)
        except KeyboardInterrupt:
            print(f"interrupted; partial catalog may exist: {output_path}", file=sys.stderr)
            raise SystemExit(130)
    if result.returncode != 0:
        fail(result.stderr.strip() or f"yt-dlp exited with {result.returncode}")


def video_url(record: dict[str, Any]) -> str:
    return record.get("webpage_url") or record.get("url") or f"https://www.youtube.com/watch?v={record.get('id')}"


def tokenize(text: str) -> list[str]:
    return [token.lower().rstrip("s") for token in TOKEN_RE.findall(text.lower()) if len(token) > 1]


def query_terms(query: str) -> list[str]:
    terms = tokenize(query)
    extras: list[str] = []
    joined = " ".join(terms)
    phrase_pairs = [
        ("landing", "page"),
        ("home", "page"),
        ("story", "telling"),
        ("call", "action"),
        ("case", "study"),
    ]
    for left, right in phrase_pairs:
        if left in joined and right in joined:
            extras.append(f"{left} {right}")
    return list(dict.fromkeys(terms + extras))


def count_term(text: str, term: str) -> int:
    if " " in term:
        return text.count(term)
    return len(re.findall(rf"\b{re.escape(term)}[a-z]*\b", text))


def score_text(text: str, terms: list[str], *, weight: float = 1.0) -> float:
    lowered = text.lower()
    score = 0.0
    for term in terms:
        score += count_term(lowered, term) * weight * (3.0 if " " in term else 1.0)
    return score


def filter_records(
    records: list[dict[str, Any]],
    *,
    since: str | None = None,
    until: str | None = None,
) -> list[dict[str, Any]]:
    since_norm = normalize_date(since)
    until_norm = normalize_date(until)
    kept: list[dict[str, Any]] = []
    for record in records:
        date = normalize_date(record.get("upload_date"))
        if date:
            if since_norm and date < since_norm:
                continue
            if until_norm and date > until_norm:
                continue
        kept.append(record)
    return kept


def rank_metadata(records: list[dict[str, Any]], query: str) -> list[dict[str, Any]]:
    terms = query_terms(query)
    ranked: list[dict[str, Any]] = []
    for record in records:
        title = record.get("title") or ""
        description = record.get("description") or ""
        score = score_text(title, terms, weight=8.0) + score_text(description, terms, weight=1.5)
        if all(term in (title + " " + description).lower() for term in tokenize(query)[:2]):
            score += 5
        if score <= 0:
            continue
        item = dict(record)
        item["score"] = round(score, 3)
        item["url"] = video_url(record)
        item["snippet"] = make_snippet(description or title, terms)
        ranked.append(item)
    ranked.sort(key=lambda item: (item["score"], item.get("upload_date") or ""), reverse=True)
    return ranked


def make_snippet(text: str, terms: list[str], width: int = 220) -> str:
    compact = re.sub(r"\s+", " ", text).strip()
    if len(compact) <= width:
        return compact
    lowered = compact.lower()
    positions = [lowered.find(term) for term in terms if lowered.find(term) >= 0]
    start = max(0, min(positions) - 60) if positions else 0
    end = min(len(compact), start + width)
    prefix = "..." if start > 0 else ""
    suffix = "..." if end < len(compact) else ""
    return prefix + compact[start:end].strip() + suffix


def transcript_records(output_dir: Path, catalog_records: list[dict[str, Any]]) -> list[dict[str, Any]]:
    by_id = {record.get("id"): record for record in catalog_records}
    root = output_dir / "transcripts"
    records: list[dict[str, Any]] = []
    if not root.exists():
        return records
    for transcript in root.glob("*/transcript.txt"):
        video_id = transcript.parent.name
        record = dict(by_id.get(video_id, {"id": video_id, "title": video_id}))
        record["transcript_text"] = transcript.read_text(encoding="utf-8", errors="replace")
        meta = transcript.parent / "metadata.compact.json"
        if meta.exists():
            metadata = json.loads(meta.read_text(encoding="utf-8"))
            record["title"] = metadata.get("title") or record.get("title")
            record["url"] = metadata.get("webpage_url") or video_url(record)
            record["duration"] = metadata.get("duration") or record.get("duration")
        records.append(record)
    return records


def rank_transcripts(records: list[dict[str, Any]], query: str) -> list[dict[str, Any]]:
    terms = query_terms(query)
    ranked: list[dict[str, Any]] = []
    for record in records:
        transcript = record.get("transcript_text") or ""
        title = record.get("title") or ""
        description = record.get("description") or ""
        transcript_score = score_text(transcript, terms, weight=1.0)
        metadata_score = score_text(title, terms, weight=8.0) + score_text(description, terms, weight=1.0)
        score = transcript_score + metadata_score
        if score <= 0:
            continue
        item = dict(record)
        item["score"] = round(score, 3)
        item["url"] = item.get("url") or video_url(record)
        item["snippet"] = make_snippet(transcript or description or title, terms, width=260)
        item.pop("transcript_text", None)
        ranked.append(item)
    ranked.sort(key=lambda item: (item["score"], item.get("upload_date") or ""), reverse=True)
    return ranked


def print_results(records: list[dict[str, Any]], *, top: int, include_snippets: bool = True) -> None:
    for index, record in enumerate(records[:top], start=1):
        date = normalize_date(record.get("upload_date")) or "unknown"
        duration = record.get("duration_string") or record.get("duration") or ""
        print(f"{index}. [{date}] {record.get('title')}")
        print(f"   score: {record.get('score')}  duration: {duration}  url: {record.get('url') or video_url(record)}")
        if include_snippets and record.get("snippet"):
            print(f"   {record['snippet']}")


def load_catalog(output_dir: Path) -> list[dict[str, Any]]:
    return parse_ndjson(best_catalog(output_dir))


def command_catalog(args: argparse.Namespace) -> None:
    output_dir = Path(args.output_dir)
    path = catalog_path(output_dir, args.mode)
    run_yt_dlp_catalog(args.channel_url, path, args.mode, args.limit)
    records = parse_ndjson(path)
    first_date = next((normalize_date(record.get("upload_date")) for record in records if record.get("upload_date")), None)
    last_date = next((normalize_date(record.get("upload_date")) for record in reversed(records) if record.get("upload_date")), None)
    print(f"catalog: {path}")
    print(f"mode: {args.mode}")
    print(f"records: {len(records)}")
    if first_date or last_date:
        print(f"date_range: {first_date or 'unknown'}..{last_date or 'unknown'}")


def command_search(args: argparse.Namespace) -> None:
    output_dir = Path(args.catalog_dir)
    records = filter_records(load_catalog(output_dir), since=args.since, until=args.until)
    ranked = rank_metadata(records, args.query)
    write_json(output_dir / "search-results.json", ranked[: args.save_top])
    print_results(ranked, top=args.top)
    print(f"saved: {output_dir / 'search-results.json'}")


def find_transcript_script(script_arg: str | None) -> Path:
    if script_arg:
        path = Path(script_arg)
        if path.exists():
            return path
        fail(f"transcript script not found: {path}")
    current = Path(__file__).resolve()
    sibling = current.parents[2] / "youtube-transcript" / "scripts" / "fetch-youtube-transcript.py"
    if sibling.exists():
        return sibling
    fail("could not find sibling youtube-transcript script; pass --transcript-script")


def command_fetch_transcripts(args: argparse.Namespace) -> None:
    output_dir = Path(args.catalog_dir)
    records = filter_records(load_catalog(output_dir), since=args.since, until=args.until)
    ranked = rank_metadata(records, args.query)[: args.top]
    transcript_script = find_transcript_script(args.transcript_script)
    transcript_root = output_dir / "transcripts"
    transcript_root.mkdir(parents=True, exist_ok=True)
    for record in ranked:
        video_id = record.get("id")
        if not video_id:
            continue
        transcript_file = transcript_root / video_id / "transcript.txt"
        if transcript_file.exists() and not args.refresh:
            print(f"skip existing: {video_id}")
            continue
        print(f"fetch: {video_id} {record.get('title')}")
        command = [
            sys.executable,
            str(transcript_script),
            "fetch",
            video_url(record),
            "--languages",
            args.languages,
            "--output-dir",
            str(transcript_root),
            "--preview-lines",
            "0",
        ]
        if args.refresh:
            command.append("--refresh")
        result = subprocess.run(command, text=True, capture_output=True, check=False)
        if result.returncode != 0:
            print(result.stderr.strip() or result.stdout.strip(), file=sys.stderr)
    print(f"transcripts: {transcript_root}")


def command_rank_transcripts(args: argparse.Namespace) -> None:
    output_dir = Path(args.catalog_dir)
    records = transcript_records(output_dir, load_catalog(output_dir))
    ranked = rank_transcripts(records, args.query)
    write_json(output_dir / "transcript-results.json", ranked[: args.save_top])
    print_results(ranked, top=args.top)
    print(f"saved: {output_dir / 'transcript-results.json'}")


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Search topics inside a YouTube channel.")
    subparsers = parser.add_subparsers(dest="command", required=True)

    catalog = subparsers.add_parser("catalog", help="Build a channel catalog with yt-dlp.")
    catalog.add_argument("channel_url")
    catalog.add_argument("--output-dir", default=DEFAULT_OUTPUT_DIR)
    catalog.add_argument("--mode", choices=["flat", "full"], default="flat")
    catalog.add_argument("--limit", type=int, help="Maximum videos to scan.")
    catalog.set_defaults(func=command_catalog)

    search = subparsers.add_parser("search", help="Rank catalog metadata for a topic.")
    search.add_argument("catalog_dir")
    search.add_argument("query")
    search.add_argument("--since")
    search.add_argument("--until")
    search.add_argument("--top", type=int, default=20)
    search.add_argument("--save-top", type=int, default=100)
    search.set_defaults(func=command_search)

    fetch = subparsers.add_parser("fetch-transcripts", help="Fetch transcripts for top metadata matches.")
    fetch.add_argument("catalog_dir")
    fetch.add_argument("query")
    fetch.add_argument("--since")
    fetch.add_argument("--until")
    fetch.add_argument("--top", type=int, default=15)
    fetch.add_argument("--languages", default="en,en-US,en-GB")
    fetch.add_argument("--refresh", action="store_true")
    fetch.add_argument("--transcript-script")
    fetch.set_defaults(func=command_fetch_transcripts)

    rank = subparsers.add_parser("rank-transcripts", help="Rank fetched transcript text for a topic.")
    rank.add_argument("catalog_dir")
    rank.add_argument("query")
    rank.add_argument("--top", type=int, default=10)
    rank.add_argument("--save-top", type=int, default=100)
    rank.set_defaults(func=command_rank_transcripts)

    return parser


def main() -> None:
    parser = build_parser()
    args = parser.parse_args()
    args.func(args)


if __name__ == "__main__":
    main()
