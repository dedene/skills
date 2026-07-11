from __future__ import annotations

import re
from dataclasses import asdict, dataclass
from datetime import datetime, timedelta, timezone
from typing import Any
from urllib.parse import urlparse, urlunparse


METRIC_RE = re.compile(r"^\s*(\d+(?:,\d{3})*(?:\.\d+)?|\d+(?:\.\d+)?)([KkMm])?\b")
RELATIVE_AGE_RE = re.compile(
    r"^\s*(?P<count>\d+)\s*(?P<unit>m|min|mins|minute|minutes|h|hr|hrs|hour|hours|d|day|days|w|wk|wks|week|weeks|mo|mon|month|months|y|yr|yrs|year|years)\b",
    re.IGNORECASE,
)


@dataclass
class Item:
    source: str
    id: str | None
    url: str | None
    author: str | None
    author_url: str | None
    title: str | None
    text: str | None
    published_at: str | None
    engagement: dict[str, int | None]
    relevance: float | None
    raw: dict[str, Any]

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


def parse_metric_count(label: str | None) -> int | None:
    if not label:
        return None
    match = METRIC_RE.match(label)
    if not match:
        return None

    number, suffix = match.groups()
    value = float(number.replace(",", ""))
    multiplier = 1
    if suffix and suffix.lower() == "k":
        multiplier = 1_000
    elif suffix and suffix.lower() == "m":
        multiplier = 1_000_000
    return int(value * multiplier)


def parse_relative_age(label: str | None, now: datetime | None = None) -> str | None:
    if not label:
        return None
    text = label.strip().lower()
    if not text or text == "now" or text.startswith("now "):
        delta = timedelta()
    else:
        match = RELATIVE_AGE_RE.match(text)
        if not match:
            return None
        count = int(match.group("count"))
        unit = match.group("unit").lower()
        if unit in {"m", "min", "mins", "minute", "minutes"}:
            delta = timedelta(minutes=count)
        elif unit in {"h", "hr", "hrs", "hour", "hours"}:
            delta = timedelta(hours=count)
        elif unit in {"d", "day", "days"}:
            delta = timedelta(days=count)
        elif unit in {"w", "wk", "wks", "week", "weeks"}:
            delta = timedelta(weeks=count)
        elif unit in {"mo", "mon", "month", "months"}:
            delta = timedelta(days=30 * count)
        elif unit in {"y", "yr", "yrs", "year", "years"}:
            delta = timedelta(days=365 * count)
        else:
            return None

    base = now or datetime.now(timezone.utc)
    if base.tzinfo is None:
        base = base.replace(tzinfo=timezone.utc)
    published = base.astimezone(timezone.utc) - delta
    return published.replace(microsecond=0).isoformat().replace("+00:00", "Z")


def strip_tracking(url: str | None) -> str | None:
    if not url:
        return None
    parsed = urlparse(url)
    return urlunparse((parsed.scheme, parsed.netloc, parsed.path, "", "", ""))


def _parse_datetime(value: str | None) -> datetime | None:
    if not value:
        return None
    try:
        parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
    except ValueError:
        return None
    if parsed.tzinfo is None:
        return parsed.replace(tzinfo=timezone.utc)
    return parsed.astimezone(timezone.utc)


def filter_recent_items(items: list[Item], days: int, now: datetime | None = None) -> list[Item]:
    now = now or datetime.now(timezone.utc)
    if now.tzinfo is None:
        now = now.replace(tzinfo=timezone.utc)
    cutoff_seconds = max(days, 0) * 24 * 60 * 60
    kept: list[Item] = []
    for item in items:
        published = _parse_datetime(item.published_at)
        if published is None:
            kept.append(item)
            continue
        age_seconds = (now.astimezone(timezone.utc) - published).total_seconds()
        if age_seconds <= cutoff_seconds:
            kept.append(item)
    return kept
