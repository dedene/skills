from __future__ import annotations

import json
import shutil
import subprocess
from datetime import datetime, timezone
from typing import Any

from ..backend import BackendError
from ..model import Item, filter_recent_items


RAW_KEYS = {
    "id",
    "title",
    "description",
    "channel",
    "channel_url",
    "upload_date",
    "timestamp",
    "view_count",
    "like_count",
    "comment_count",
    "duration",
    "webpage_url",
}


def parse_ytdlp_lines(text: str) -> list[dict[str, Any]]:
    objs: list[dict[str, Any]] = []
    for line in text.splitlines():
        line = line.strip()
        if not line:
            continue
        try:
            obj = json.loads(line)
        except json.JSONDecodeError:
            continue
        if isinstance(obj, dict):
            objs.append(obj)
    return objs


def _iso_from_timestamp(value: Any) -> str | None:
    if value is None:
        return None
    try:
        timestamp = int(value)
    except (TypeError, ValueError):
        return None
    return datetime.fromtimestamp(timestamp, tz=timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def _date_from_upload_date(value: Any) -> str | None:
    if not isinstance(value, str) or len(value) != 8 or not value.isdigit():
        return None
    try:
        return datetime.strptime(value, "%Y%m%d").date().isoformat()
    except ValueError:
        return None


def _small_raw(obj: dict[str, Any], date_confidence: str) -> dict[str, Any]:
    raw = {key: obj.get(key) for key in RAW_KEYS if key in obj}
    raw["_derived"] = {"date_confidence": date_confidence}
    return raw


def normalize_videos(objs: list[dict[str, Any]]) -> list[Item]:
    items: list[Item] = []
    for obj in objs:
        if not isinstance(obj, dict):
            continue
        published_at = _iso_from_timestamp(obj.get("timestamp"))
        date_confidence = "exact" if published_at else "day"
        if not published_at:
            published_at = _date_from_upload_date(obj.get("upload_date"))
        if not published_at:
            date_confidence = "none"

        items.append(
            Item(
                source="youtube",
                id=obj.get("id"),
                url=obj.get("webpage_url"),
                author=obj.get("channel"),
                author_url=obj.get("channel_url"),
                title=obj.get("title"),
                text=obj.get("description") or "",
                published_at=published_at,
                engagement={
                    "views": obj.get("view_count"),
                    "likes": obj.get("like_count"),
                    "comments": obj.get("comment_count"),
                },
                relevance=None,
                raw=_small_raw(obj, date_confidence),
            )
        )
    return items


def search(query: str, days: int = 30, limit: int = 20, backend: object | None = None) -> list[Item]:
    del backend
    if shutil.which("yt-dlp") is None:
        raise BackendError("yt-dlp not found; install it with: brew install yt-dlp")

    count = min(limit * 2, 40)
    command = [
        "yt-dlp",
        "--ignore-config",
        "--no-cookies-from-browser",
        f"ytsearch{count}:{query}",
        "--dump-json",
        "--no-download",
    ]
    try:
        result = subprocess.run(command, capture_output=True, text=True, timeout=120, check=False)
    except subprocess.TimeoutExpired as exc:
        raise BackendError(f"yt-dlp timeout after 120s; stderr_tail={(exc.stderr or '')[-500:]!r}") from exc

    if result.returncode != 0:
        raise BackendError(f"yt-dlp failed with exit {result.returncode}; stderr_tail={result.stderr[-500:]!r}")

    items = filter_recent_items(normalize_videos(parse_ytdlp_lines(result.stdout)), days)
    return items[:limit]
