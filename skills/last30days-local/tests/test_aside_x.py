from __future__ import annotations

import json
import unittest
from datetime import datetime, timezone
from pathlib import Path

import tests  # noqa: F401
from engine.model import Item, parse_metric_count
from engine.sources.aside_x import build_search_js, filter_recent, normalize_items, search


FIXTURES = Path(__file__).resolve().parent / "fixtures"


def load_payload() -> dict:
    return json.loads((FIXTURES / "x_search_payload.json").read_text(encoding="utf-8"))


class FakeBackend:
    def __init__(self, payload: dict) -> None:
        self.payload = payload
        self.js: str | None = None

    def run_js(self, js: str) -> dict:
        self.js = js
        return self.payload


class AsideXTests(unittest.TestCase):
    def test_normalize_items_maps_fixture_rows_to_stable_item_shape(self) -> None:
        items = normalize_items(load_payload())

        self.assertEqual(len(items), 13)
        first = items[0]
        self.assertEqual(first.source, "x")
        self.assertEqual(first.id, "2073339050056946133")
        self.assertEqual(first.url, "https://x.com/0xMortyx/status/2073339050056946133")
        self.assertEqual(first.author_url, "https://x.com/0xMortyx")
        self.assertEqual(first.author, "Morty (@0xMortyx)")
        self.assertEqual(first.published_at, "2026-07-04T09:32:04.000Z")
        self.assertEqual(first.engagement, {"replies": 2, "reposts": 0, "likes": 7, "views": 39})

    def test_parse_metric_count_handles_x_labels(self) -> None:
        cases = {
            "2 Replies. Reply": 2,
            "1.2K Likes": 1200,
            "3M views": 3000000,
            "1,234 reposts": 1234,
            None: None,
            "": None,
            "Reply": None,
        }

        for label, expected in cases.items():
            with self.subTest(label=label):
                self.assertEqual(parse_metric_count(label), expected)

    def test_build_search_js_injects_query_as_json_literal(self) -> None:
        query = "claude's \"code\""

        js = build_search_js(query, scrolls=2)

        self.assertIn(json.dumps(query), js)
        self.assertIn("const q = " + json.dumps(query), js)
        self.assertIn("for (let i = 0; i < 2; i++)", js)
        self.assertNotIn("__QUERY_JSON__", js)
        self.assertNotIn("__SCROLLS__", js)

    def test_filter_recent_uses_fixed_now_and_keeps_missing_dates(self) -> None:
        now = datetime(2026, 7, 4, 12, 0, tzinfo=timezone.utc)
        items = [
            Item("x", "new", "https://x.com/a/status/1", None, None, None, "new", "2026-07-04T09:00:00.000Z", {}, None, {}),
            Item("x", "old", "https://x.com/a/status/2", None, None, None, "old", "2026-06-01T09:00:00.000Z", {}, None, {}),
            Item("x", "missing", "https://x.com/a/status/3", None, None, None, "missing", None, {}, None, {}),
        ]

        recent = filter_recent(items, days=30, now=now)

        self.assertEqual([item.id for item in recent], ["new", "missing"])

    def test_search_uses_injected_backend_and_applies_limit(self) -> None:
        backend = FakeBackend(load_payload())

        items = search("claude code", days=30, limit=2, backend=backend)

        self.assertEqual(len(items), 2)
        self.assertIsNotNone(backend.js)
        self.assertIn(json.dumps("claude code"), backend.js or "")

    def test_search_normalizes_empty_no_results_payload(self) -> None:
        backend = FakeBackend({"query": "nothing", "count": 0, "items": [], "note": "no results or unrecognized page"})

        items = search("nothing", backend=backend)

        self.assertEqual(items, [])

    def test_build_search_js_emits_empty_payload_for_no_results_page(self) -> None:
        js = build_search_js("nothing")

        self.assertIn("no results or unrecognized page", js)
        self.assertNotIn("No tweets found and no login marker detected", js)


if __name__ == "__main__":
    unittest.main()
