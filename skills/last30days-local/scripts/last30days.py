#!/usr/bin/env python3
"""Search recent social posts through local source adapters."""

from __future__ import annotations

import argparse
import json
import sys
import time
from collections.abc import Callable
from typing import TypeVar

from engine.backend import BackendError, LoginRequired, get_backend
from engine.sources import SOURCES, hackernews, reddit_keyless


T = TypeVar("T")


def retry_until_login(
    fn: Callable[[], T],
    *,
    attempts: int,
    delay: int,
    sleep: Callable[[int], object] = time.sleep,
) -> T:
    last_error: LoginRequired | None = None
    for attempt in range(attempts):
        try:
            return fn()
        except LoginRequired as exc:
            last_error = exc
            if attempt == attempts - 1:
                break
            sleep(delay)
    if last_error is not None:
        raise last_error
    raise RuntimeError("retry_until_login called with no attempts")


def engagement_summary(engagement: dict[str, int | None]) -> str:
    parts = [f"{key}={value}" for key, value in engagement.items() if value is not None]
    return " ".join(parts) if parts else "engagement=n/a"


def compact_text(value: str | None, width: int = 120) -> str:
    if not value:
        return ""
    compact = " ".join(value.split())
    if len(compact) <= width:
        return compact
    return compact[: width - 3].rstrip() + "..."


def run_search(args: argparse.Namespace) -> int:
    if args.source not in SOURCES:
        available = ", ".join(sorted(SOURCES))
        print(f"error: unknown source {args.source!r}; available sources: {available}", file=sys.stderr)
        return 2

    try:
        backend = None if args.source in {"bluesky", "github", "hackernews", "polymarket", "reddit", "web", "youtube"} else get_backend(args.backend)
        search = lambda: SOURCES[args.source](args.query, days=args.days, limit=args.limit, backend=backend)
        if args.wait_login:
            try:
                items = retry_until_login(
                    search,
                    attempts=31,
                    delay=20,
                    sleep=lambda seconds: (print(f"Waiting for login to {args.source}... (Ctrl-C to abort)", file=sys.stderr), time.sleep(seconds))[1],
                )
            except KeyboardInterrupt:
                print("aborted", file=sys.stderr)
                return 130
        else:
            items = search()
    except ValueError as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 2
    except LoginRequired as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 3
    except BackendError as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 1

    if args.json:
        print(json.dumps([item.to_dict() for item in items], ensure_ascii=False, indent=2))
        return 0

    for item in items:
        date = item.published_at or "unknown-date"
        author = item.author or "unknown-author"
        text = compact_text(item.text or item.title)
        print(f"{date} | {author} | {engagement_summary(item.engagement)} | {text} | {item.url}")
    return 0


def run_comments(args: argparse.Namespace) -> int:
    if args.source not in {"reddit", "hackernews"}:
        print("error: comments only supports sources: hackernews, reddit", file=sys.stderr)
        return 2

    try:
        if args.source == "reddit":
            if not args.post_id:
                print("error: reddit comments requires subreddit and post_id", file=sys.stderr)
                return 2
            comments = reddit_keyless.fetch_comments(args.item_id, args.post_id, sort=args.sort, limit=args.limit)
        else:
            comments = hackernews.fetch_comments(args.item_id, limit=args.limit)
    except BackendError as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 1

    if args.json:
        print(json.dumps(comments, ensure_ascii=False, indent=2))
        return 0

    for comment in comments:
        author = comment.get("author") or "unknown-author"
        score = comment.get("score")
        text = compact_text(comment.get("text"))
        if args.source == "reddit":
            print(f"{score} | {author} | {text} | {comment.get('permalink')}")
        else:
            print(f"{author} | {text}")
    return 0


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="last30days")
    subparsers = parser.add_subparsers(dest="command", required=True)

    search_parser = subparsers.add_parser("search", help="search a recent-post source")
    search_parser.add_argument("source", help="source adapter, e.g. x")
    search_parser.add_argument("query", help="search query")
    search_parser.add_argument("--days", type=int, default=30, help="keep items from this many days back")
    search_parser.add_argument("--limit", type=int, default=20, help="maximum items to print")
    search_parser.add_argument("--backend", default="aside", help="browser backend to use, e.g. aside")
    search_parser.add_argument("--wait-login", action="store_true", help="wait and retry when a source requires login")
    search_parser.add_argument("--json", action="store_true", help="print normalized items as JSON")
    search_parser.set_defaults(func=run_search)

    comments_parser = subparsers.add_parser("comments", help="fetch comments for a source item")
    comments_parser.add_argument("source", help="comment source; reddit or hackernews")
    comments_parser.add_argument("item_id", help="Hacker News item id, or subreddit name for reddit")
    comments_parser.add_argument("post_id", nargs="?", help="Reddit post id, with or without t3_ prefix")
    comments_parser.add_argument("--sort", default="top", help="comment sort to request")
    comments_parser.add_argument("--limit", type=int, default=5, help="maximum comments to print")
    comments_parser.add_argument("--json", action="store_true", help="print comments as JSON")
    comments_parser.set_defaults(func=run_comments)
    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    return args.func(args)


if __name__ == "__main__":
    raise SystemExit(main())
