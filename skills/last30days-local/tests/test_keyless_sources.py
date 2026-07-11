from __future__ import annotations

import json
import shutil
import subprocess
import urllib.error
import unittest
from datetime import datetime, timezone
from io import BytesIO
from pathlib import Path
from unittest import mock

import tests  # noqa: F401
from engine.backend import BackendError
from engine.sources import bluesky, github_issues, hackernews, polymarket, web_ddg


FIXTURES = Path(__file__).resolve().parent / "fixtures"


def load_json(name: str) -> dict:
    return json.loads((FIXTURES / name).read_text(encoding="utf-8"))


class FakeClock:
    def __init__(self) -> None:
        self.now = 100.0
        self.sleeps: list[float] = []

    def monotonic(self) -> float:
        return self.now

    def sleep(self, seconds: float) -> None:
        self.sleeps.append(seconds)
        self.now += seconds


class KeylessSourceTests(unittest.TestCase):
    def test_hackernews_normalizes_fixture_and_computes_cutoff(self) -> None:
        items = hackernews.normalize_hits(load_json("hn_search.json"))

        self.assertEqual(len(items), 20)
        first = items[0]
        self.assertEqual(first.source, "hackernews")
        self.assertEqual(first.id, "48784250")
        self.assertEqual(first.url, "https://www.lockinmcp.com")
        self.assertEqual(first.title, "Show HN: An MCP server that gives your AI assistant write access to /etc./hosts")
        self.assertEqual(first.author, "Kiog-Aser")
        self.assertEqual(first.published_at, "2026-07-04T10:09:17Z")
        self.assertEqual(first.engagement, {"points": 2, "comments": 1})
        self.assertIn("LockIn lets AI assistants", first.text or "")
        self.assertEqual(first.raw["hn_url"], "https://news.ycombinator.com/item?id=48784250")

        cutoff = hackernews.cutoff_epoch(days=7, now=datetime(2026, 7, 4, 12, 0, tzinfo=timezone.utc))
        self.assertEqual(cutoff, 1782561600)

    def test_hackernews_fetch_comments_walks_top_level_children(self) -> None:
        payload = {
            "children": [
                {"author": "alice", "text": "First <p>comment", "children": [{"author": "nested", "text": "skip"}]},
                {"author": "bob", "text": "Second &amp; useful"},
                {"author": "empty", "text": ""},
            ]
        }
        requested: list[tuple[str, str]] = []

        def opener(url: str, headers: dict[str, str]) -> bytes:
            requested.append((url, headers["Accept"]))
            return json.dumps(payload).encode()

        comments = hackernews.fetch_comments("48784250", limit=2, opener=opener)

        self.assertEqual(requested, [("https://hn.algolia.com/api/v1/items/48784250", "application/json")])
        self.assertEqual(comments, [{"author": "alice", "text": "First comment"}, {"author": "bob", "text": "Second & useful"}])

    def test_bluesky_normalizes_fixture_and_builds_post_url(self) -> None:
        items = bluesky.normalize_posts(load_json("bluesky_search.json"), days=30, now=datetime(2026, 7, 4, 12, 0, tzinfo=timezone.utc))

        self.assertEqual(len(items), 25)
        first = items[0]
        self.assertEqual(first.source, "bluesky")
        self.assertEqual(first.id, "3mpstlxwoo22q")
        self.assertEqual(first.url, "https://bsky.app/profile/respo119.bsky.social/post/3mpstlxwoo22q")
        self.assertEqual(first.author, "レスポ (@respo119.bsky.social)")
        self.assertEqual(first.author_url, "https://bsky.app/profile/respo119.bsky.social")
        self.assertEqual(first.published_at, "2026-07-04T10:20:27.663Z")
        self.assertEqual(first.engagement, {"likes": 0, "reposts": 0, "replies": 0, "quotes": 0})

    def test_github_normalizes_fixture_and_missing_binary_has_auth_hint(self) -> None:
        items = github_issues.normalize_issues(load_json("github_search.json"))

        self.assertEqual(len(items), 25)
        first = items[0]
        self.assertEqual(first.source, "github")
        self.assertEqual(first.id, "65697")
        self.assertEqual(first.url, "https://github.com/anthropics/claude-code/issues/65697")
        self.assertEqual(first.title, "[FEATURE] Official Claude Desktop build for Linux (Ubuntu LTS / Debian)")
        self.assertEqual(first.author, "powell-clark")
        self.assertEqual(first.published_at, "2026-06-05T17:48:57Z")
        self.assertEqual(first.engagement, {"reactions": 651, "comments": 51})
        self.assertEqual(len(first.text or ""), 500)
        self.assertEqual(first.raw["_derived"]["container"], "anthropics/claude-code")

        with mock.patch.object(shutil, "which", return_value=None), self.assertRaises(BackendError) as raised:
            github_issues.search("claude code")
        self.assertIn("install/authenticate GitHub CLI: brew install gh && gh auth login", str(raised.exception))

    def test_github_search_builds_safe_gh_query(self) -> None:
        captured: list[list[str]] = []

        def fake_run(command: list[str], **kwargs: object) -> subprocess.CompletedProcess[str]:
            captured.append(command)
            return subprocess.CompletedProcess(command, 0, stdout=json.dumps({"items": []}), stderr="")

        with mock.patch.object(shutil, "which", return_value="/opt/homebrew/bin/gh"), mock.patch.object(subprocess, "run", side_effect=fake_run):
            github_issues.search("claude code / ai", days=3, limit=2, now=datetime(2026, 7, 4, tzinfo=timezone.utc))

        self.assertEqual(
            captured[0],
            ["gh", "api", "search/issues?q=claude%20code%20%2F%20ai+created:>2026-07-01&sort=reactions&per_page=4"],
        )

    def test_web_ddg_decodes_redirects_and_dedupes_urls(self) -> None:
        html = (FIXTURES / "web_ddg_search.html").read_text(encoding="utf-8")
        items = web_ddg.normalize_html(html + html)

        self.assertEqual(len(items), 10)
        first = items[0]
        self.assertEqual(first.source, "web")
        self.assertIsNone(first.id)
        self.assertEqual(first.url, "https://support.claude.com/en/articles/14554000-claude-code-power-user-tips")
        self.assertEqual(first.title, "Claude Code power user tips | Claude Help Center")
        self.assertEqual(first.text, "This article collects workflow tips from the Claude")
        self.assertEqual(first.engagement, {})
        self.assertEqual(first.raw["_derived"]["date_confidence"], "none")

    def test_polymarket_normalizes_events_and_coerces_engagement(self) -> None:
        items = polymarket.normalize_events(load_json("polymarket_search.json"))

        self.assertEqual(len(items), 10)
        first = items[0]
        self.assertEqual(first.source, "polymarket")
        self.assertEqual(first.id, "us-government-removes-public-access-to-another-anthropic-ai-model-in-2026-20260703203121674")
        self.assertEqual(
            first.url,
            "https://polymarket.com/event/us-government-removes-public-access-to-another-anthropic-ai-model-in-2026-20260703203121674",
        )
        self.assertEqual(first.title, "US Government removes public access to another Anthropic AI model in 2026?")
        self.assertIsNone(first.published_at)
        self.assertEqual(first.engagement, {"volume": 10371, "liquidity": 9928})
        self.assertEqual(first.raw["_derived"]["endDate"], "2026-12-31T23:59:00Z")

    def test_shared_http_helper_wraps_errors_without_response_body(self) -> None:
        from engine import httpget

        def opener(url: str, headers: dict[str, str]) -> bytes:
            raise urllib.error.HTTPError(url, 503, "Service Unavailable", {}, BytesIO(b"secret body"))

        with self.assertRaises(BackendError) as raised:
            httpget.get("https://example.test/search", opener=opener)

        message = str(raised.exception)
        self.assertIn("url='https://example.test/search'", message)
        self.assertIn("status=503", message)
        self.assertIn("reason=Service Unavailable", message)
        self.assertNotIn("secret body", message)

    def test_shared_http_helper_rate_limiter_uses_injected_clock(self) -> None:
        from engine import httpget

        clock = FakeClock()
        calls = 0

        def opener(url: str, headers: dict[str, str]) -> bytes:
            nonlocal calls
            calls += 1
            return b"ok"

        httpget.set_http_hooks(clock=clock.monotonic, sleep=clock.sleep)
        try:
            httpget.get("https://example.test/one", opener=opener)
            httpget.get("https://example.test/two", opener=opener)
        finally:
            httpget.set_http_hooks()

        self.assertEqual(calls, 2)
        self.assertEqual(clock.sleeps, [0.25])


if __name__ == "__main__":
    unittest.main()
