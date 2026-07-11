from __future__ import annotations

from html.parser import HTMLParser
from typing import Any, Callable
from urllib.parse import parse_qs, quote_plus, unquote, urlparse

from .. import httpget
from ..model import Item


class _DDGParser(HTMLParser):
    def __init__(self) -> None:
        super().__init__(convert_charrefs=True)
        self.results: list[dict[str, str | None]] = []
        self.current: dict[str, str | None] | None = None
        self.collect_title = False
        self.collect_snippet = False
        self.parts: list[str] = []

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        data = {key: value or "" for key, value in attrs}
        classes = set(data.get("class", "").split())
        if tag == "a" and "result__a" in classes:
            self._finish_current()
            self.current = {"href": data.get("href"), "title": None, "snippet": None}
            self.collect_title = True
            self.parts = []
        elif self.current is not None and "result__snippet" in classes:
            self.collect_snippet = True
            self.parts = []

    def handle_endtag(self, tag: str) -> None:
        if self.collect_title and tag == "a":
            if self.current is not None:
                self.current["title"] = _compact(self.parts)
            self.collect_title = False
            self.parts = []
        elif self.collect_snippet:
            if self.current is not None:
                self.current["snippet"] = _compact(self.parts)
            self.collect_snippet = False
            self.parts = []

    def handle_data(self, data: str) -> None:
        if self.collect_title or self.collect_snippet:
            self.parts.append(data)

    def close(self) -> None:
        super().close()
        self._finish_current()

    def _finish_current(self) -> None:
        if self.current is not None and self.current.get("href"):
            self.results.append(self.current)
        self.current = None


def _compact(parts: list[str]) -> str:
    return " ".join("".join(parts).split())


def decode_ddg_href(href: str | None) -> str | None:
    if not href:
        return None
    parsed = urlparse(href)
    if parsed.path == "/l/" or parsed.path.endswith("/l/"):
        uddg = parse_qs(parsed.query).get("uddg", [None])[0]
        return unquote(uddg) if uddg else href
    return href


def normalize_html(html_text: str) -> list[Item]:
    parser = _DDGParser()
    parser.feed(html_text)
    parser.close()

    seen: set[str] = set()
    items: list[Item] = []
    for result in parser.results:
        url = decode_ddg_href(result.get("href"))
        if not url or url in seen:
            continue
        seen.add(url)
        items.append(
            Item(
                source="web",
                id=None,
                url=url,
                author=None,
                author_url=None,
                title=result.get("title"),
                text=result.get("snippet"),
                published_at=None,
                engagement={},
                relevance=None,
                raw={"href": result.get("href"), "_derived": {"date_confidence": "none"}},
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
    del backend
    df = "w" if days <= 7 else "m"
    url = f"https://html.duckduckgo.com/html/?q={quote_plus(query)}&df={df}"
    html_text = httpget.get(url, accept="text/html", opener=opener).decode("utf-8", errors="replace")
    return normalize_html(html_text)[:limit]
