from __future__ import annotations

import json
from datetime import datetime, timezone
from html.parser import HTMLParser
from typing import Any, Callable
from urllib.parse import quote_plus

from .. import httpget
from ..model import Item, filter_recent_items


USED_KEYS = {"author", "created_at", "created_at_i", "num_comments", "objectID", "points", "story_text", "title", "url"}


class _TextExtractor(HTMLParser):
    def __init__(self) -> None:
        super().__init__(convert_charrefs=True)
        self.parts: list[str] = []

    def handle_data(self, data: str) -> None:
        if data.strip():
            self.parts.append(data)

    def text(self) -> str:
        return " ".join(" ".join(self.parts).split())


def strip_html(value: str | None) -> str | None:
    if not value:
        return None
    parser = _TextExtractor()
    parser.feed(value)
    return parser.text() or None


def cutoff_epoch(days: int, now: datetime | None = None) -> int:
    base = now or datetime.now(timezone.utc)
    if base.tzinfo is None:
        base = base.replace(tzinfo=timezone.utc)
    return int(base.timestamp() - days * 86400)


def normalize_hits(payload: dict[str, Any]) -> list[Item]:
    hits = payload.get("hits")
    if not isinstance(hits, list):
        return []

    items: list[Item] = []
    for hit in hits:
        if not isinstance(hit, dict):
            continue
        object_id = str(hit.get("objectID") or "")
        if not object_id:
            continue
        hn_url = f"https://news.ycombinator.com/item?id={object_id}"
        raw = {key: hit.get(key) for key in USED_KEYS if key in hit}
        raw["hn_url"] = hn_url
        items.append(
            Item(
                source="hackernews",
                id=object_id,
                url=hit.get("url") or hn_url,
                author=hit.get("author"),
                author_url=None,
                title=hit.get("title"),
                text=strip_html(hit.get("story_text")),
                published_at=hit.get("created_at"),
                engagement={"points": hit.get("points"), "comments": hit.get("num_comments")},
                relevance=None,
                raw=raw,
            )
        )
    return items


def search(
    query: str,
    days: int = 30,
    limit: int = 20,
    backend: object | None = None,
    *,
    opener: Callable[..., bytes] | None = None,
    now: datetime | None = None,
) -> list[Item]:
    del backend
    cutoff = cutoff_epoch(days, now=now)
    url = (
        "https://hn.algolia.com/api/v1/search_by_date?"
        f"query={quote_plus(query)}&tags=story&numericFilters=created_at_i>{cutoff}"
    )
    payload = json.loads(httpget.get(url, opener=opener).decode("utf-8", errors="replace"))
    items = filter_recent_items(normalize_hits(payload), days, now=now)
    return items[:limit]


def fetch_comments(item_id: str, limit: int = 5, opener: Callable[..., bytes] | None = None) -> list[dict[str, str | None]]:
    url = f"https://hn.algolia.com/api/v1/items/{quote_plus(str(item_id))}"
    payload = json.loads(httpget.get(url, opener=opener).decode("utf-8", errors="replace"))
    children = payload.get("children") if isinstance(payload, dict) else None
    if not isinstance(children, list):
        return []

    comments: list[dict[str, str | None]] = []
    for child in children:
        if not isinstance(child, dict):
            continue
        text = strip_html(child.get("text"))
        if not text:
            continue
        comments.append({"author": child.get("author"), "text": text})
        if len(comments) >= limit:
            break
    return comments
