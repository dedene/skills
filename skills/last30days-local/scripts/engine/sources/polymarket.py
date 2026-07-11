from __future__ import annotations

import json
from typing import Any, Callable
from urllib.parse import quote_plus

from .. import httpget
from ..model import Item


RAW_KEYS = {"title", "slug", "volume", "liquidity"}


def _int_or_none(value: Any) -> int | None:
    if value is None:
        return None
    try:
        return int(float(value))
    except (TypeError, ValueError):
        return None


def normalize_events(payload: dict[str, Any]) -> list[Item]:
    events = payload.get("events")
    if not isinstance(events, list):
        return []

    items: list[Item] = []
    for event in events:
        if not isinstance(event, dict):
            continue
        slug = event.get("slug")
        if not slug:
            continue
        raw = {key: event.get(key) for key in RAW_KEYS if key in event}
        raw["_derived"] = {"endDate": event.get("endDate")}
        engagement = {
            "volume": _int_or_none(event.get("volume")),
            "liquidity": _int_or_none(event.get("liquidity")),
        }
        items.append(
            Item(
                source="polymarket",
                id=slug,
                url=f"https://polymarket.com/event/{slug}",
                author=None,
                author_url=None,
                title=event.get("title"),
                text=None,
                published_at=None,
                engagement={key: value for key, value in engagement.items() if value is not None},
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
) -> list[Item]:
    del backend, days
    url = f"https://gamma-api.polymarket.com/public-search?q={quote_plus(query)}&limit_per_type=10"
    payload = json.loads(httpget.get(url, opener=opener).decode("utf-8", errors="replace"))
    return normalize_events(payload)[:limit]
