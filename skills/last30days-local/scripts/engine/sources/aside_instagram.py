from __future__ import annotations

import json
import re
from datetime import datetime, timezone
from pathlib import Path
from typing import Any
from urllib.parse import urljoin, urlparse

from ..backend import Backend, LoginRequired, get_backend
from ..model import Item, filter_recent_items, parse_metric_count, strip_tracking


SHORTCODE_RE = re.compile(r"/(?:p|reel)/([^/?#]+)/?")
SHORTCODE_ALPHABET = "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789-_"
INSTAGRAM_EPOCH_MS = 1_314_220_021_721


def build_search_js(query: str, enrich: int = 4, scrolls: int = 2) -> str:
    template = (Path(__file__).parent / "js" / "instagram_search.js").read_text(encoding="utf-8")
    return (
        template.replace("__QUERY_JSON__", json.dumps(query))
        .replace("__ENRICH__", str(int(enrich)))
        .replace("__SCROLLS__", str(int(scrolls)))
    )


def _shortcode(href: str | None) -> str | None:
    if not href:
        return None
    match = SHORTCODE_RE.search(urlparse(href).path)
    return match.group(1) if match else None


def instagram_shortcode_timestamp(shortcode: str) -> str | None:
    if len(shortcode) > 11:
        return None
    media_id = 0
    for char in shortcode:
        index = SHORTCODE_ALPHABET.find(char)
        if index < 0:
            return None
        media_id = media_id * 64 + index
    unix_ms = (media_id >> 23) + INSTAGRAM_EPOCH_MS
    return datetime.fromtimestamp(unix_ms / 1000, tz=timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def _author(author_href: str | None) -> str | None:
    if not author_href:
        return None
    handle = author_href.strip().strip("/").split("/", 1)[0]
    return f"@{handle}" if handle else None


def _author_url(author_href: str | None) -> str | None:
    if not author_href:
        return None
    href = author_href.strip()
    return strip_tracking(urljoin("https://www.instagram.com", href)) if href else None


def normalize_items(payload: dict[str, Any]) -> list[Item]:
    items: list[Item] = []
    for raw in payload.get("items", []):
        if not isinstance(raw, dict):
            continue
        href = raw.get("href") if isinstance(raw.get("href"), str) else None
        alt = raw.get("alt") if isinstance(raw.get("alt"), str) and raw.get("alt") else None
        datetime_value = raw.get("datetime") if isinstance(raw.get("datetime"), str) else None
        if not href or (not alt and not datetime_value):
            continue
        shortcode = _shortcode(href)
        published_at = datetime_value or (instagram_shortcode_timestamp(shortcode) if shortcode else None)
        normalized_raw = dict(raw)
        normalized_raw["_derived"] = {"date_confidence": "exact" if datetime_value else "approx_id"}
        items.append(
            Item(
                source="instagram",
                id=shortcode,
                url=strip_tracking(urljoin("https://www.instagram.com", href)),
                author=_author(raw.get("author_href") if isinstance(raw.get("author_href"), str) else None),
                author_url=_author_url(raw.get("author_href") if isinstance(raw.get("author_href"), str) else None),
                title=None,
                text=alt,
                published_at=published_at,
                engagement={"likes": parse_metric_count(raw.get("like_text") if isinstance(raw.get("like_text"), str) else None)},
                relevance=None,
                raw=normalized_raw,
            )
        )
    return items


def search(query: str, days: int = 30, limit: int = 20, backend: Backend | None = None) -> list[Item]:
    backend = backend or get_backend("aside")
    payload = backend.run_js(build_search_js(query))
    if payload.get("login_required") is True:
        raise LoginRequired(str(payload.get("source") or "instagram"))
    return filter_recent_items(normalize_items(payload), days)[:limit]
