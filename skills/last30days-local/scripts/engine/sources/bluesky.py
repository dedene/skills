from __future__ import annotations

import json
from datetime import datetime
from typing import Any, Callable
from urllib.parse import quote_plus

from .. import httpget
from ..model import Item, filter_recent_items


def _rkey(uri: str | None) -> str | None:
    if not uri:
        return None
    return uri.rstrip("/").split("/")[-1] or None


def _author(author: dict[str, Any]) -> tuple[str | None, str | None]:
    handle = author.get("handle")
    display_name = author.get("displayName")
    if display_name and handle:
        name = f"{display_name} (@{handle})"
    elif handle:
        name = f"@{handle}"
    else:
        name = display_name
    return name, f"https://bsky.app/profile/{handle}" if handle else None


def normalize_posts(payload: dict[str, Any], days: int = 30, now: datetime | None = None) -> list[Item]:
    posts = payload.get("posts")
    if not isinstance(posts, list):
        return []

    items: list[Item] = []
    for post in posts:
        if not isinstance(post, dict):
            continue
        record = post.get("record") if isinstance(post.get("record"), dict) else {}
        author_obj = post.get("author") if isinstance(post.get("author"), dict) else {}
        rkey = _rkey(post.get("uri"))
        handle = author_obj.get("handle")
        author, author_url = _author(author_obj)
        items.append(
            Item(
                source="bluesky",
                id=rkey,
                url=f"https://bsky.app/profile/{handle}/post/{rkey}" if handle and rkey else None,
                author=author,
                author_url=author_url,
                title=None,
                text=record.get("text"),
                published_at=record.get("createdAt"),
                engagement={
                    "likes": post.get("likeCount"),
                    "reposts": post.get("repostCount"),
                    "replies": post.get("replyCount"),
                    "quotes": post.get("quoteCount"),
                },
                relevance=None,
                raw={
                    "uri": post.get("uri"),
                    "author": {"handle": handle, "displayName": author_obj.get("displayName")},
                    "record": {"text": record.get("text"), "createdAt": record.get("createdAt")},
                    "likeCount": post.get("likeCount"),
                    "repostCount": post.get("repostCount"),
                    "replyCount": post.get("replyCount"),
                    "quoteCount": post.get("quoteCount"),
                },
            )
        )
    return filter_recent_items(items, days, now=now)


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
    count = min(limit * 2, 100)
    url = f"https://api.bsky.app/xrpc/app.bsky.feed.searchPosts?q={quote_plus(query)}&sort=latest&limit={count}"
    payload = json.loads(httpget.get(url, opener=opener).decode("utf-8", errors="replace"))
    return normalize_posts(payload, days=days, now=now)[:limit]
