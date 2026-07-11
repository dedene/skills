from __future__ import annotations

import json
import re
from pathlib import Path
from typing import Any
from urllib.parse import urljoin, urlparse

from ..backend import Backend, LoginRequired, get_backend
from ..model import Item, filter_recent_items, strip_tracking


PIN_ID_RE = re.compile(r"/pin/(\d+)")


def build_search_js(query: str, scrolls: int = 3) -> str:
    template = (Path(__file__).parent / "js" / "pinterest_search.js").read_text(encoding="utf-8")
    return template.replace("__QUERY_JSON__", json.dumps(query)).replace("__SCROLLS__", str(int(scrolls)))


def _pin_id(href: str | None) -> str | None:
    if not href:
        return None
    match = PIN_ID_RE.search(urlparse(href).path)
    return match.group(1) if match else None


def normalize_items(payload: dict[str, Any]) -> list[Item]:
    items: list[Item] = []
    for raw in payload.get("items", []):
        if not isinstance(raw, dict):
            continue
        href = raw.get("href") if isinstance(raw.get("href"), str) else None
        if not href:
            continue
        text = raw.get("alt") if isinstance(raw.get("alt"), str) and raw.get("alt") else None
        if not text:
            text = raw.get("card_text") if isinstance(raw.get("card_text"), str) and raw.get("card_text") else None
        normalized_raw = dict(raw)
        normalized_raw["_derived"] = {"date_confidence": "none"}
        items.append(
            Item(
                source="pinterest",
                id=_pin_id(href),
                url=strip_tracking(urljoin("https://www.pinterest.com", href)),
                author=None,
                author_url=None,
                title=None,
                text=text,
                published_at=None,
                engagement={},
                relevance=None,
                raw=normalized_raw,
            )
        )
    return items


def search(query: str, days: int = 30, limit: int = 20, backend: Backend | None = None) -> list[Item]:
    backend = backend or get_backend("aside")
    payload = backend.run_js(build_search_js(query))
    if payload.get("login_required") is True:
        raise LoginRequired(str(payload.get("source") or "pinterest"))
    return filter_recent_items(normalize_items(payload), days)[:limit]
