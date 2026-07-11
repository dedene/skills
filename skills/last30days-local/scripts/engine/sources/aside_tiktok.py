from __future__ import annotations

import json
import re
from datetime import datetime, timezone
from pathlib import Path
from typing import Any
from urllib.parse import urljoin, urlparse

from ..backend import Backend, LoginRequired, get_backend
from ..model import Item, filter_recent_items, parse_metric_count, strip_tracking


VIDEO_ID_RE = re.compile(r"/video/(\d+)")
URL_HANDLE_RE = re.compile(r"/@([^/]+)/video/")


def build_search_js(query: str, scrolls: int = 3) -> str:
    template = (Path(__file__).parent / "js" / "tiktok_search.js").read_text(encoding="utf-8")
    return template.replace("__QUERY_JSON__", json.dumps(query)).replace("__SCROLLS__", str(int(scrolls)))


def _video_id(url: str | None) -> str | None:
    if not url:
        return None
    match = VIDEO_ID_RE.search(urlparse(url).path)
    return match.group(1) if match else None


def tiktok_id_timestamp(video_id: str) -> str | None:
    if not video_id.isdigit():
        return None
    seconds = int(video_id) >> 32
    return datetime.fromtimestamp(seconds, tz=timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def _handle(raw: dict[str, Any], url: str | None) -> str | None:
    author_handle = raw.get("author_handle")
    if isinstance(author_handle, str) and author_handle.strip():
        handle = author_handle.strip().lstrip("@")
        return f"@{handle}"
    if url:
        match = URL_HANDLE_RE.search(urlparse(url).path)
        if match:
            return f"@{match.group(1)}"
    return None


def _author_url(author_href: str | None, author: str | None) -> str | None:
    if isinstance(author_href, str) and author_href.strip():
        return strip_tracking(urljoin("https://www.tiktok.com", author_href.strip()))
    return f"https://www.tiktok.com/{author}" if author else None


def normalize_items(payload: dict[str, Any]) -> list[Item]:
    items: list[Item] = []
    for raw in payload.get("items", []):
        if not isinstance(raw, dict):
            continue
        url = strip_tracking(raw.get("url") if isinstance(raw.get("url"), str) else None)
        if not url:
            continue
        video_id = _video_id(url)
        author = _handle(raw, url)
        normalized_raw = dict(raw)
        normalized_raw["_derived"] = {"date_confidence": "approx_id"}
        items.append(
            Item(
                source="tiktok",
                id=video_id,
                url=url,
                author=author,
                author_url=_author_url(raw.get("author_href") if isinstance(raw.get("author_href"), str) else None, author),
                title=None,
                text=raw.get("caption") if isinstance(raw.get("caption"), str) else None,
                published_at=tiktok_id_timestamp(video_id) if video_id else None,
                engagement={"views": parse_metric_count(raw.get("views") if isinstance(raw.get("views"), str) else None)},
                relevance=None,
                raw=normalized_raw,
            )
        )
    return items


def search(query: str, days: int = 30, limit: int = 20, backend: Backend | None = None) -> list[Item]:
    backend = backend or get_backend("aside")
    payload = backend.run_js(build_search_js(query))
    if payload.get("login_required") is True:
        raise LoginRequired(str(payload.get("source") or "tiktok"))
    return filter_recent_items(normalize_items(payload), days)[:limit]
