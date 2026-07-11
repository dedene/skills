from __future__ import annotations

import json
import re
from datetime import datetime
from pathlib import Path
from typing import Any
from urllib.parse import urlparse

from ..backend import Backend, LoginRequired, get_backend
from ..model import Item, filter_recent_items, parse_metric_count


STATUS_ID_RE = re.compile(r"/status/(\d+)")


def build_search_js(query: str, scrolls: int = 3) -> str:
    template = (Path(__file__).parent / "js" / "x_search.js").read_text(encoding="utf-8")
    return template.replace("__QUERY_JSON__", json.dumps(query)).replace("__SCROLLS__", str(int(scrolls)))


def _status_id(url: str | None) -> str | None:
    if not url:
        return None
    match = STATUS_ID_RE.search(urlparse(url).path)
    return match.group(1) if match else None


def _handle_from_href(author_href: str | None) -> str | None:
    if not author_href:
        return None
    handle = author_href.strip().strip("/").split("/", 1)[0]
    return f"@{handle}" if handle else None


def _author_url(author_href: str | None) -> str | None:
    if not author_href:
        return None
    href = author_href.strip()
    if not href:
        return None
    if href.startswith("http://") or href.startswith("https://"):
        return href
    return "https://x.com" + (href if href.startswith("/") else f"/{href}")


def _display_name(author_name: str | None) -> str | None:
    if not author_name:
        return None
    for line in author_name.splitlines():
        line = line.strip()
        if line:
            return line
    compact = author_name.strip()
    return compact or None


def _author(author_name: str | None, author_href: str | None) -> str | None:
    handle = _handle_from_href(author_href)
    display = _display_name(author_name)
    if display and handle:
        if display == handle or display.endswith(handle):
            return display
        return f"{display} ({handle})"
    return display or handle


def normalize_items(payload: dict[str, Any]) -> list[Item]:
    items: list[Item] = []
    for raw in payload.get("items", []):
        if not isinstance(raw, dict):
            continue
        url = raw.get("url")
        if not url:
            continue
        metrics = raw.get("metrics") if isinstance(raw.get("metrics"), dict) else {}
        items.append(
            Item(
                source="x",
                id=_status_id(url),
                url=url,
                author=_author(raw.get("author_name"), raw.get("author_href")),
                author_url=_author_url(raw.get("author_href")),
                title=None,
                text=raw.get("text"),
                published_at=raw.get("datetime"),
                engagement={
                    "replies": parse_metric_count(metrics.get("reply")),
                    "reposts": parse_metric_count(metrics.get("retweet")),
                    "likes": parse_metric_count(metrics.get("like")),
                    "views": parse_metric_count(metrics.get("views")),
                },
                relevance=None,
                raw=raw,
            )
        )
    return items


def filter_recent(items: list[Item], days: int, now: datetime | None = None) -> list[Item]:
    return filter_recent_items(items, days, now=now)


def search(query: str, days: int = 30, limit: int = 20, backend: Backend | None = None) -> list[Item]:
    backend = backend or get_backend("aside")
    payload = backend.run_js(build_search_js(query))
    if payload.get("login_required") is True:
        raise LoginRequired(str(payload.get("source") or "x"))
    items = filter_recent(normalize_items(payload), days)
    return items[:limit]
