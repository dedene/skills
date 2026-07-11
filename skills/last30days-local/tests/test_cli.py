from __future__ import annotations

import unittest
import contextlib
import io
import json
from argparse import Namespace
from unittest import mock

import tests  # noqa: F401
from engine.backend import LoginRequired
from engine.model import Item
from last30days import engagement_summary, retry_until_login, run_comments, run_search


class RetryUntilLoginTests(unittest.TestCase):
    def test_engagement_summary_prints_all_non_none_keys(self) -> None:
        summary = engagement_summary(
            {
                "points": 2,
                "comments": 1,
                "reactions": 651,
                "volume": 10371,
                "liquidity": 9928,
                "quotes": 0,
                "shares": None,
            }
        )

        self.assertEqual(summary, "points=2 comments=1 reactions=651 volume=10371 liquidity=9928 quotes=0")

    def test_search_human_output_falls_back_to_title_when_text_empty(self) -> None:
        item = Item(
            source="polymarket",
            id="market-1",
            url="https://polymarket.com/event/market-1",
            author=None,
            author_url=None,
            title="US Government removes public access to another Anthropic AI model in 2026?",
            text=None,
            published_at=None,
            engagement={"volume": 10371, "liquidity": 9928},
            relevance=None,
            raw={},
        )
        args = Namespace(
            source="polymarket",
            query="anthropic",
            days=30,
            limit=20,
            backend="aside",
            wait_login=False,
            json=False,
        )
        stdout = io.StringIO()

        with mock.patch.dict("last30days.SOURCES", {"polymarket": lambda *args, **kwargs: [item]}):
            with contextlib.redirect_stdout(stdout):
                code = run_search(args)

        self.assertEqual(code, 0)
        line = stdout.getvalue()
        self.assertIn("volume=10371 liquidity=9928", line)
        self.assertIn("US Government removes public access to another Anthropic AI model in 2026?", line)

    def test_retries_until_login_wall_clears(self) -> None:
        calls = 0
        sleeps: list[int] = []

        def fn() -> str:
            nonlocal calls
            calls += 1
            if calls < 3:
                raise LoginRequired("linkedin")
            return "ok"

        result = retry_until_login(fn, attempts=5, delay=20, sleep=sleeps.append)

        self.assertEqual(result, "ok")
        self.assertEqual(calls, 3)
        self.assertEqual(sleeps, [20, 20])

    def test_hackernews_comments_cli_dispatches_by_item_id(self) -> None:
        stdout = io.StringIO()
        args = Namespace(source="hackernews", item_id="48784250", post_id=None, sort="top", limit=2, json=True)

        with mock.patch("last30days.hackernews.fetch_comments", return_value=[{"author": "alice", "text": "useful"}]) as fetch:
            with contextlib.redirect_stdout(stdout):
                code = run_comments(args)

        self.assertEqual(code, 0)
        fetch.assert_called_once_with("48784250", limit=2)
        self.assertEqual(json.loads(stdout.getvalue()), [{"author": "alice", "text": "useful"}])

    def test_gives_up_after_attempts(self) -> None:
        calls = 0
        sleeps: list[int] = []

        def fn() -> str:
            nonlocal calls
            calls += 1
            raise LoginRequired("x")

        with self.assertRaises(LoginRequired):
            retry_until_login(fn, attempts=3, delay=20, sleep=sleeps.append)

        self.assertEqual(calls, 3)
        self.assertEqual(sleeps, [20, 20])


if __name__ == "__main__":
    unittest.main()
