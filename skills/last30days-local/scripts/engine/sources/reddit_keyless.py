from __future__ import annotations

import html
import re
import time
import xml.etree.ElementTree as ET
from html.parser import HTMLParser
from typing import Any, Callable
from urllib.parse import quote_plus

from .. import httpget
from ..model import Item, filter_recent_items


ATOM = "{http://www.w3.org/2005/Atom}"
POST_ID_RE = re.compile(r"/comments/([A-Za-z0-9]+)")

_opener: Callable[..., bytes] | None = None


def set_http_hooks(
    *,
    opener: Callable[..., bytes] | None = None,
    clock: Callable[[], float] | None = None,
    sleep: Callable[[float], object] | None = None,
) -> None:
    global _opener
    _opener = opener
    httpget.set_http_hooks(clock=clock or time.monotonic, sleep=sleep or time.sleep)


def _get(url: str, accept: str) -> bytes:
    return httpget.get(url, accept=accept, opener=_opener)


class _TextExtractor(HTMLParser):
    def __init__(self) -> None:
        super().__init__(convert_charrefs=True)
        self.parts: list[str] = []

    def handle_data(self, data: str) -> None:
        if data.strip():
            self.parts.append(data)

    def text(self) -> str:
        return " ".join(" ".join(self.parts).split())


def _strip_html(value: str | None) -> str:
    if not value:
        return ""
    parser = _TextExtractor()
    parser.feed(value)
    return parser.text()


def _post_id_from_url(url: str | None) -> str | None:
    if not url:
        return None
    match = POST_ID_RE.search(url)
    return match.group(1) if match else None


def _entry_id(entry: ET.Element, url: str | None) -> str | None:
    post_id = _post_id_from_url(url)
    if post_id:
        return post_id
    id_el = entry.find(f"{ATOM}id")
    if id_el is not None and id_el.text:
        return id_el.text.strip()
    return None


def _subreddit_from(category: str | None, url: str | None) -> str | None:
    if category:
        return category.removeprefix("r/")
    if url and "/r/" in url:
        return url.split("/r/", 1)[1].split("/", 1)[0]
    return None


def _author_name(entry: ET.Element) -> str | None:
    author_el = entry.find(f"{ATOM}author/{ATOM}name")
    if author_el is None or not author_el.text:
        return None
    author = author_el.text.strip()
    return author.removeprefix("/u/").removeprefix("u/") or None


def _author_url(entry: ET.Element) -> str | None:
    uri_el = entry.find(f"{ATOM}author/{ATOM}uri")
    if uri_el is None or not uri_el.text:
        return None
    return uri_el.text.strip() or None


def parse_search_rss(xml_text: str) -> list[Item]:
    try:
        root = ET.fromstring(xml_text)
    except ET.ParseError:
        return []

    items: list[Item] = []
    for entry in root.iter(f"{ATOM}entry"):
        link_el = entry.find(f"{ATOM}link")
        url = (link_el.get("href") or "").strip() if link_el is not None else ""
        if not url:
            continue

        title_el = entry.find(f"{ATOM}title")
        published_el = entry.find(f"{ATOM}published")
        if published_el is None:
            published_el = entry.find(f"{ATOM}updated")
        category_el = entry.find(f"{ATOM}category")
        content_el = entry.find(f"{ATOM}content")

        subreddit = _subreddit_from(category_el.get("term") if category_el is not None else None, url)
        raw = {
            "_derived": {
                "container": f"r/{subreddit}" if subreddit else None,
                "date_confidence": "exact",
            }
        }
        items.append(
            Item(
                source="reddit",
                id=_entry_id(entry, url),
                url=url,
                author=_author_name(entry),
                author_url=_author_url(entry),
                title=(title_el.text or "").strip() if title_el is not None and title_el.text else None,
                text=_strip_html(content_el.text if content_el is not None else None),
                published_at=(published_el.text or "").strip() if published_el is not None and published_el.text else None,
                engagement={},
                relevance=None,
                raw=raw,
            )
        )
    return items


class _PostParser(HTMLParser):
    def __init__(self) -> None:
        super().__init__(convert_charrefs=True)
        self.posts: list[dict[str, Any]] = []

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        if tag != "shreddit-post":
            return
        data = {key: value or "" for key, value in attrs}
        permalink = data.get("permalink", "")
        if "/comments/" not in permalink:
            return
        subreddit = data.get("subreddit-prefixed-name") or data.get("subreddit-name") or ""
        if subreddit and not subreddit.startswith("r/"):
            subreddit = f"r/{subreddit}"
        self.posts.append(
            {
                "title": data.get("post-title", ""),
                "permalink": permalink,
                "author": data.get("author", ""),
                "subreddit": subreddit,
                "created_timestamp": data.get("created-timestamp", ""),
                "score": _int_or_zero(data.get("score")),
                "comment_count": _int_or_zero(data.get("comment-count")),
                "post_id": data.get("id") or f"t3_{_post_id_from_url(permalink) or ''}",
                "content_href": data.get("content-href", ""),
            }
        )


def _int_or_zero(value: Any) -> int:
    try:
        return int(value)
    except (TypeError, ValueError):
        return 0


def parse_shreddit_posts(html_text: str) -> list[dict[str, Any]]:
    parser = _PostParser()
    parser.feed(html_text)
    return parser.posts


class _CommentParser(HTMLParser):
    def __init__(self) -> None:
        super().__init__(convert_charrefs=True)
        self.comments: list[dict[str, Any]] = []
        self.current: dict[str, Any] | None = None
        self.collect_depth = 0
        self.text_parts: list[str] = []

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        data = {key: value or "" for key, value in attrs}
        if tag == "shreddit-comment":
            self.current = {
                "author": data.get("author", ""),
                "score": _int_or_zero(data.get("score")),
                "permalink": data.get("permalink", ""),
            }
            self.collect_depth = 0
            self.text_parts = []
            return

        if self.current is None:
            return
        if self.collect_depth:
            self.collect_depth += 1
        elif tag == "div" and data.get("slot") == "comment":
            self.collect_depth = 1

    def handle_endtag(self, tag: str) -> None:
        if self.current is None:
            return
        if self.collect_depth:
            self.collect_depth -= 1
        if tag == "shreddit-comment":
            text = " ".join(" ".join(self.text_parts).split())
            if text:
                self.comments.append({**self.current, "text": html.unescape(text)})
            self.current = None
            self.collect_depth = 0
            self.text_parts = []

    def handle_data(self, data: str) -> None:
        if self.current is not None and self.collect_depth and data.strip():
            self.text_parts.append(data)


def parse_shreddit_comments(html_text: str, limit: int | None = None) -> list[dict[str, Any]]:
    parser = _CommentParser()
    parser.feed(html_text)
    comments = sorted(parser.comments, key=lambda comment: comment.get("score", 0), reverse=True)
    return comments[:limit] if limit is not None else comments


def days_to_timeframe(days: int) -> str:
    if days <= 7:
        return "week"
    if days <= 31:
        return "month"
    return "year"


def search(query: str, days: int = 30, limit: int = 20, backend: object | None = None, include_comments: bool = False) -> list[Item]:
    del backend, include_comments
    t = days_to_timeframe(days)
    url = f"https://www.reddit.com/search.rss?q={quote_plus(query)}&sort=new&t={t}"
    xml_text = _get(url, "application/atom+xml").decode("utf-8", errors="replace")
    return filter_recent_items(parse_search_rss(xml_text), days)[:limit]


def fetch_subreddit_posts(subreddit: str, sort: str = "new", t: str = "month") -> list[dict[str, Any]]:
    sub = subreddit.removeprefix("r/").strip()
    url = f"https://www.reddit.com/svc/shreddit/community-more-posts/{quote_plus(sort)}/?name={quote_plus(sub)}&t={quote_plus(t)}"
    return parse_shreddit_posts(_get(url, "text/html").decode("utf-8", errors="replace"))


def fetch_comments(subreddit: str, post_id: str, sort: str = "top", limit: int = 5) -> list[dict[str, Any]]:
    sub = subreddit.removeprefix("r/").strip()
    pid = post_id.removeprefix("t3_")
    url = f"https://www.reddit.com/svc/shreddit/comments/r/{quote_plus(sub)}/t3_{quote_plus(pid)}?sort={quote_plus(sort)}"
    return parse_shreddit_comments(_get(url, "text/html").decode("utf-8", errors="replace"), limit=limit)
