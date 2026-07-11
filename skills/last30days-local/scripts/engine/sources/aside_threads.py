from __future__ import annotations

import json
import re
from pathlib import Path
from typing import Any
from urllib.parse import urljoin, urlparse

from ..backend import Backend, LoginRequired, get_backend
from ..model import Item, filter_recent_items, parse_metric_count, strip_tracking


POST_ID_RE = re.compile(r"/post/([^/?#]+)")
BARE_COUNT_RE = re.compile(r"^\d[\d.,]*$")
PAGE_MARKER_RE = re.compile(r"^(?:/|\d+\s*/\s*\d+)$")
RELATIVE_AGE_LINE_RE = re.compile(r"^\d+\s*[a-zA-Z]{1,3}\.?$")
TRANSLATION_LINES = {"Vertalen", "Translate"}


def build_search_js(query: str, scrolls: int = 3) -> str:
    template = (Path(__file__).parent / "js" / "threads_search.js").read_text(encoding="utf-8")
    return template.replace("__QUERY_JSON__", json.dumps(query)).replace("__SCROLLS__", str(int(scrolls)))


def _post_id(post_href: str | None) -> str | None:
    if not post_href:
        return None
    match = POST_ID_RE.search(urlparse(post_href).path)
    return match.group(1) if match else None


def _author(author_href: str | None) -> str | None:
    if not author_href:
        return None
    handle = author_href.strip().strip("/").split("/", 1)[0]
    return handle if handle.startswith("@") else f"@{handle}" if handle else None


def _author_url(author_href: str | None) -> str | None:
    author = _author(author_href)
    return f"https://www.threads.com/{author}" if author else None


def _clean_text(text: str | None, author: str | None = None) -> str | None:
    if not isinstance(text, str):
        return None
    author_tokens = {author} if author else set()
    if author and author.startswith("@"):
        author_tokens.add(author[1:])
    elif author:
        author_tokens.add(f"@{author}")
    kept: list[str] = []
    content_started = False
    for line in text.splitlines()[2:]:
        stripped = line.strip().strip("\u200b").strip()
        if not stripped:
            continue
        if not content_started and _is_leading_context_line(stripped, author_tokens):
            continue
        if stripped in TRANSLATION_LINES:
            continue
        if BARE_COUNT_RE.match(stripped):
            continue
        if PAGE_MARKER_RE.match(stripped):
            continue
        content_started = True
        kept.append(stripped)
    return "\n".join(kept).strip() or None


def _is_leading_context_line(line: str, author_tokens: set[str]) -> bool:
    if RELATIVE_AGE_LINE_RE.match(line):
        return True
    if line in author_tokens:
        return True
    return line.startswith("Je beantwoordt") or line.startswith("Replying to")


def _engagement(actions: Any) -> dict[str, int | None]:
    rows = actions if isinstance(actions, list) else []
    counts: list[str | None] = []
    for action in rows[-4:]:
        counts.append(action.get("count") if isinstance(action, dict) else None)
    counts = (counts + [None, None, None, None])[:4]
    return {
        "likes": parse_metric_count(counts[0]),
        "replies": parse_metric_count(counts[1]),
        "reposts": parse_metric_count(counts[2]),
        "shares": parse_metric_count(counts[3]),
    }


def normalize_items(payload: dict[str, Any]) -> list[Item]:
    items: list[Item] = []
    for raw in payload.get("items", []):
        if not isinstance(raw, dict):
            continue
        post_href = raw.get("post_href") if isinstance(raw.get("post_href"), str) else None
        if not post_href:
            continue
        normalized_raw = dict(raw)
        normalized_raw["_derived"] = {"date_confidence": "exact"}
        items.append(
            Item(
                source="threads",
                id=_post_id(post_href),
                url=strip_tracking(urljoin("https://www.threads.com", post_href)),
                author=_author(raw.get("author_href") if isinstance(raw.get("author_href"), str) else None),
                author_url=_author_url(raw.get("author_href") if isinstance(raw.get("author_href"), str) else None),
                title=None,
                text=_clean_text(
                    raw.get("text") if isinstance(raw.get("text"), str) else None,
                    _author(raw.get("author_href") if isinstance(raw.get("author_href"), str) else None),
                ),
                published_at=raw.get("datetime") if isinstance(raw.get("datetime"), str) else None,
                engagement=_engagement(raw.get("actions")),
                relevance=None,
                raw=normalized_raw,
            )
        )
    return items


def search(query: str, days: int = 30, limit: int = 20, backend: Backend | None = None) -> list[Item]:
    backend = backend or get_backend("aside")
    payload = backend.run_js(build_search_js(query))
    if payload.get("login_required") is True:
        raise LoginRequired(str(payload.get("source") or "threads"))
    return filter_recent_items(normalize_items(payload), days)[:limit]
