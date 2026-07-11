from __future__ import annotations

import json
import re
from pathlib import Path
from typing import Any
from urllib.parse import urljoin, urlparse

from ..backend import Backend, LoginRequired, get_backend
from ..model import Item, filter_recent_items, parse_metric_count, parse_relative_age, strip_tracking


POST_ID_RE = re.compile(r"-(\d{15,})-|(\d{15,})/?$")
AGE_RE = re.compile(r"(\d+)\s*(m|h|d|w|mo|y)\s*•", re.IGNORECASE)
COMMENT_RE = re.compile(r"(\d[\d,.]*[KkMm]?)\s+comments?", re.IGNORECASE)
REPOST_RE = re.compile(r"(\d[\d,.]*[KkMm]?)\s+reposts?", re.IGNORECASE)
BARE_COUNT_RE = re.compile(r"^\s*(\d[\d,.]*[KkMm]?)\s*$")


def build_search_js(query: str, limit: int = 20, scrolls: int = 3) -> str:
    template = (Path(__file__).parent / "js" / "linkedin_search.js").read_text(encoding="utf-8")
    return (
        template.replace("__QUERY_JSON__", json.dumps(query))
        .replace("__LIMIT__", str(int(limit)))
        .replace("__SCROLLS__", str(int(scrolls)))
    )


def _post_id(url: str | None) -> str | None:
    if not url:
        return None
    path = urlparse(url).path
    match = POST_ID_RE.search(path)
    if not match:
        return None
    return match.group(1) or match.group(2)


def _display_name(raw: dict[str, Any]) -> str | None:
    head = raw.get("container_head")
    if isinstance(head, str):
        lines = [line.strip() for line in head.splitlines() if line.strip()]
        if lines and lines[0] == "Feed post" and len(lines) > 1:
            return lines[1]
    author_name = raw.get("author_name")
    if isinstance(author_name, str):
        for line in author_name.splitlines():
            line = line.strip()
            if line:
                return line
    return None


def _author_url(author_href: str | None) -> str | None:
    if not author_href:
        return None
    href = author_href.strip()
    if not href:
        return None
    return strip_tracking(urljoin("https://www.linkedin.com", href))


def _age_label(container_head: str | None) -> str | None:
    if not container_head:
        return None
    if re.search(r"\bnow\s*•", container_head, re.IGNORECASE):
        return "now"
    match = AGE_RE.search(container_head)
    if match:
        return f"{match.group(1)}{match.group(2).lower()}"
    return None


def _metric(pattern: re.Pattern[str], value: str | None) -> int | None:
    if not value:
        return None
    match = pattern.search(value)
    if not match:
        return None
    return parse_metric_count(match.group(1))


def _bare_reactions(container_tail: str | None) -> int | None:
    if not container_tail:
        return None
    for line in reversed(container_tail.splitlines()):
        text = line.strip().strip("\u200b").strip()
        if not text:
            continue
        match = BARE_COUNT_RE.match(text)
        if match:
            return parse_metric_count(match.group(1))
    return None


def _engagement(container_tail: str | None) -> dict[str, int | None]:
    return {
        "reactions": _bare_reactions(container_tail),
        "comments": _metric(COMMENT_RE, container_tail),
        "reposts": _metric(REPOST_RE, container_tail),
    }


def normalize_items(payload: dict[str, Any]) -> list[Item]:
    items: list[Item] = []
    for raw in payload.get("items", []):
        if not isinstance(raw, dict):
            continue
        text = raw.get("text") if isinstance(raw.get("text"), str) else None
        url = strip_tracking(raw.get("url") if isinstance(raw.get("url"), str) else None)
        if not text and not url:
            continue

        age_label = _age_label(raw.get("container_head") if isinstance(raw.get("container_head"), str) else None)
        derived = {"age_label": age_label, "date_confidence": "approx_relative"}
        normalized_raw = dict(raw)
        normalized_raw["_derived"] = derived

        items.append(
            Item(
                source="linkedin",
                id=_post_id(url),
                url=url,
                author=_display_name(raw),
                author_url=_author_url(raw.get("author_href") if isinstance(raw.get("author_href"), str) else None),
                title=None,
                text=text,
                published_at=parse_relative_age(age_label),
                engagement=_engagement(raw.get("container_tail") if isinstance(raw.get("container_tail"), str) else None),
                relevance=None,
                raw=normalized_raw,
            )
        )
    return items


def search(query: str, days: int = 30, limit: int = 20, backend: Backend | None = None) -> list[Item]:
    backend = backend or get_backend("aside")
    payload = backend.run_js(build_search_js(query, limit=limit))
    if payload.get("login_required") is True:
        raise LoginRequired(str(payload.get("source") or "linkedin"))
    return filter_recent_items(normalize_items(payload), days)[:limit]
