from __future__ import annotations

import json
import urllib.error
import unittest
from io import BytesIO
from pathlib import Path

import tests  # noqa: F401
from engine.backend import BackendError
from engine.sources import reddit_keyless


FIXTURES = Path(__file__).resolve().parent / "fixtures"


class FakeClock:
    def __init__(self) -> None:
        self.now = 100.0
        self.sleeps: list[float] = []

    def monotonic(self) -> float:
        return self.now

    def sleep(self, seconds: float) -> None:
        self.sleeps.append(seconds)
        self.now += seconds


class RedditKeylessTests(unittest.TestCase):
    def tearDown(self) -> None:
        reddit_keyless.set_http_hooks()

    def test_days_to_timeframe_mapping(self) -> None:
        self.assertEqual(reddit_keyless.days_to_timeframe(1), "week")
        self.assertEqual(reddit_keyless.days_to_timeframe(7), "week")
        self.assertEqual(reddit_keyless.days_to_timeframe(8), "month")
        self.assertEqual(reddit_keyless.days_to_timeframe(31), "month")
        self.assertEqual(reddit_keyless.days_to_timeframe(32), "year")

    def test_parse_search_rss_fixture(self) -> None:
        xml = (FIXTURES / "reddit_search_rss.xml").read_text(encoding="utf-8")
        items = reddit_keyless.parse_search_rss(xml)

        self.assertEqual(len(items), 25)
        first = items[0]
        self.assertEqual(first.source, "reddit")
        self.assertEqual(first.id, "t5_dp6k3k")
        self.assertEqual(first.url, "https://www.reddit.com/r/ClaudeCode/")
        self.assertEqual(first.author, "IndraVahan")
        self.assertEqual(first.raw["_derived"]["container"], "r/ClaudeCode")
        self.assertEqual(first.published_at, "2025-02-24T19:29:29+00:00")
        self.assertEqual(first.raw["_derived"]["date_confidence"], "exact")

    def test_parse_shreddit_listing_fixture(self) -> None:
        html = (FIXTURES / "reddit_shreddit_listing.html").read_text(encoding="utf-8")
        posts = reddit_keyless.parse_shreddit_posts(html)

        self.assertEqual(len(posts), 24)
        self.assertTrue(all(isinstance(post["score"], int) for post in posts))
        self.assertTrue(all(post["permalink"].startswith("/r/") for post in posts))
        self.assertIn("t3_1un59on", {post["post_id"] for post in posts})

    def test_parse_shreddit_comments_fixture(self) -> None:
        html = (FIXTURES / "reddit_shreddit_comments.html").read_text(encoding="utf-8")
        comments = reddit_keyless.parse_shreddit_comments(html)

        self.assertEqual(len(comments), 1)
        for comment in comments:
            self.assertTrue(comment["author"])
            self.assertIsInstance(comment["score"], int)
            self.assertTrue(comment["text"])

    def test_fetch_functions_use_injected_opener(self) -> None:
        listing = (FIXTURES / "reddit_shreddit_listing.html").read_bytes()
        comments = (FIXTURES / "reddit_shreddit_comments.html").read_bytes()
        urls: list[tuple[str, str]] = []

        def opener(url: str, headers: dict[str, str]) -> bytes:
            urls.append((url, headers["Accept"]))
            if "community-more-posts" in url:
                return listing
            if "/svc/shreddit/comments/" in url:
                return comments
            raise AssertionError(url)

        reddit_keyless.set_http_hooks(opener=opener)

        posts = reddit_keyless.fetch_subreddit_posts("ClaudeAI", sort="new", t="month")
        top_comments = reddit_keyless.fetch_comments("ClaudeAI", "t3_1un59on", limit=1)

        self.assertEqual(len(posts), 24)
        self.assertEqual(len(top_comments), 1)
        self.assertIn("name=ClaudeAI", urls[0][0])
        self.assertEqual(urls[0][1], "text/html")
        self.assertEqual(urls[1][1], "text/html")

    def test_search_uses_rss_timeframe_and_limit(self) -> None:
        xml = (FIXTURES / "reddit_search_rss.xml").read_bytes()
        requested: list[str] = []

        def opener(url: str, headers: dict[str, str]) -> bytes:
            requested.append(url)
            self.assertEqual(headers["Accept"], "application/atom+xml")
            return xml

        reddit_keyless.set_http_hooks(opener=opener)

        items = reddit_keyless.search("claude code", days=7, limit=3, backend=object())

        self.assertEqual(len(items), 3)
        self.assertIn("sort=new", requested[0])
        self.assertIn("t=week", requested[0])

    def test_search_wraps_http_error_without_response_body(self) -> None:
        def opener(url: str, headers: dict[str, str]) -> bytes:
            raise urllib.error.HTTPError(url, 429, "Too Many Requests", {}, BytesIO(b"private response body"))

        reddit_keyless.set_http_hooks(opener=opener)

        with self.assertRaises(BackendError) as raised:
            reddit_keyless.search("claude code")

        message = str(raised.exception)
        self.assertIn("https://www.reddit.com/search.rss", message)
        self.assertIn("status=429", message)
        self.assertIn("reason=Too Many Requests", message)
        self.assertNotIn("private response body", message)

    def test_rate_limiter_uses_injected_clock(self) -> None:
        clock = FakeClock()
        calls = 0

        def opener(url: str, headers: dict[str, str]) -> bytes:
            nonlocal calls
            calls += 1
            return b"ok"

        reddit_keyless.set_http_hooks(opener=opener, clock=clock.monotonic, sleep=clock.sleep)

        reddit_keyless._get("https://reddit.test/one", "text/html")
        reddit_keyless._get("https://reddit.test/two", "text/html")

        self.assertEqual(calls, 2)
        self.assertEqual(clock.sleeps, [0.25])

    def test_comments_cli_json_shape_helper(self) -> None:
        comments = reddit_keyless.parse_shreddit_comments(
            (FIXTURES / "reddit_shreddit_comments.html").read_text(encoding="utf-8")
        )[:1]

        encoded = json.dumps(comments)

        self.assertIn("StrobeWafel_404", encoded)

    def test_shreddit_html_fixtures_do_not_contain_tracking_identifiers(self) -> None:
        for fixture in ("reddit_shreddit_listing.html", "reddit_shreddit_comments.html"):
            with self.subTest(fixture=fixture):
                html = (FIXTURES / fixture).read_text(encoding="utf-8")
                self.assertNotRegex(html, r"(?i)loid|user_session|session-tracker|correlation")


if __name__ == "__main__":
    unittest.main()
