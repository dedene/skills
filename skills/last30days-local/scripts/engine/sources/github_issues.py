from __future__ import annotations

import json
import re
import shutil
import subprocess
from datetime import datetime, timedelta, timezone
from typing import Any
from urllib.parse import quote

from ..backend import BackendError
from ..model import Item, filter_recent_items


GH_HINT = "install/authenticate GitHub CLI: brew install gh && gh auth login"
ISSUE_NUMBER_RE = re.compile(r"/issues/(\d+)$|/pull/(\d+)$")
RAW_KEYS = {"title", "body", "html_url", "created_at", "comments", "state", "repository_url"}


def _iso_date(days: int, now: datetime | None = None) -> str:
    base = now or datetime.now(timezone.utc)
    if base.tzinfo is None:
        base = base.replace(tzinfo=timezone.utc)
    return (base.astimezone(timezone.utc) - timedelta(days=days)).date().isoformat()


def _issue_number(url: str | None) -> str | None:
    if not url:
        return None
    match = ISSUE_NUMBER_RE.search(url)
    if not match:
        return None
    return match.group(1) or match.group(2)


def _container(repository_url: str | None) -> str | None:
    if not repository_url or "/repos/" not in repository_url:
        return None
    return repository_url.split("/repos/", 1)[1].strip("/") or None


def _truncate(value: Any, limit: int = 500) -> str | None:
    if value is None:
        return None
    text = str(value)
    return text[:limit]


def normalize_issues(payload: dict[str, Any]) -> list[Item]:
    issues = payload.get("items")
    if not isinstance(issues, list):
        return []

    items: list[Item] = []
    for issue in issues:
        if not isinstance(issue, dict):
            continue
        user = issue.get("user") if isinstance(issue.get("user"), dict) else {}
        reactions = issue.get("reactions") if isinstance(issue.get("reactions"), dict) else {}
        raw = {key: issue.get(key) for key in RAW_KEYS if key in issue}
        raw["user"] = {"login": user.get("login")}
        raw["reactions"] = {"total_count": reactions.get("total_count")}
        raw["_derived"] = {"container": _container(issue.get("repository_url"))}
        items.append(
            Item(
                source="github",
                id=_issue_number(issue.get("html_url")),
                url=issue.get("html_url"),
                author=user.get("login"),
                author_url=None,
                title=issue.get("title"),
                text=_truncate(issue.get("body")),
                published_at=issue.get("created_at"),
                engagement={"reactions": reactions.get("total_count"), "comments": issue.get("comments")},
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
    now: datetime | None = None,
) -> list[Item]:
    del backend
    if shutil.which("gh") is None:
        raise BackendError(f"gh not found; {GH_HINT}")

    q = f"{quote(query, safe='')}+created:>{_iso_date(days, now=now)}"
    command = ["gh", "api", f"search/issues?q={q}&sort=reactions&per_page={min(limit * 2, 50)}"]
    try:
        result = subprocess.run(command, capture_output=True, text=True, timeout=60, check=False)
    except (FileNotFoundError, subprocess.TimeoutExpired) as exc:
        raise BackendError(f"gh api failed; {GH_HINT}") from exc

    if result.returncode != 0:
        raise BackendError(f"gh api failed with exit {result.returncode}; {GH_HINT}")

    payload = json.loads(result.stdout or "{}")
    return filter_recent_items(normalize_issues(payload), days, now=now)[:limit]
