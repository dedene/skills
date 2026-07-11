from __future__ import annotations

import json
import unittest
from pathlib import Path

import tests  # noqa: F401
from engine.backend import LoginRequired, extract_payload
from engine.sources.aside_linkedin import build_search_js, normalize_items, search


FIXTURES = Path(__file__).resolve().parent / "fixtures"


def load_payload() -> dict:
    return json.loads((FIXTURES / "linkedin_search_payload.json").read_text(encoding="utf-8"))


class FakeBackend:
    def __init__(self, payload: dict) -> None:
        self.payload = payload
        self.js: str | None = None

    def run_js(self, js: str) -> dict:
        self.js = js
        return self.payload


class LinkedInTests(unittest.TestCase):
    def test_extracts_payload_from_noisy_aside_stdout(self) -> None:
        stdout = (FIXTURES / "linkedin_search_stdout.txt").read_text(encoding="utf-8")

        payload = extract_payload(stdout)

        self.assertEqual(payload["count"], 6)
        self.assertEqual(len(payload["items"]), 6)

    def test_normalize_items_maps_fixture_rows_to_items(self) -> None:
        items = normalize_items(load_payload())

        self.assertEqual(len(items), 6)
        first = items[0]
        self.assertEqual(first.source, "linkedin")
        self.assertEqual(first.id, "7479112436957130752")
        self.assertEqual(
            first.url,
            "https://www.linkedin.com/posts/siddhartharoraisb_ai-product-manager-please-read-these-25-share-"
            "7479112436957130752-aY9H/",
        )
        self.assertNotIn("rcm=", first.url or "")
        self.assertEqual(first.author, "Sid Arora")
        self.assertEqual(first.author_url, "https://www.linkedin.com/in/siddhartharoraisb/")
        self.assertIsNotNone(first.published_at)
        self.assertEqual(first.engagement, {"reactions": None, "comments": None, "reposts": None})
        self.assertEqual(first.raw["_derived"]["age_label"], "now")
        self.assertEqual(first.raw["_derived"]["date_confidence"], "approx_relative")

        second = items[1]
        self.assertEqual(second.author, "Darren Coxon")
        self.assertEqual(second.engagement["reactions"], 1)

    def test_normalize_items_handles_abbreviated_engagement_counts(self) -> None:
        payload = {
            "items": [
                {
                    "url": "https://www.linkedin.com/posts/example-123456789012345/",
                    "text": "Example post",
                    "container_tail": "10K\n1.2K comments\n3M reposts",
                }
            ]
        }

        item = normalize_items(payload)[0]

        self.assertEqual(item.engagement, {"reactions": 10000, "comments": 1200, "reposts": 3000000})

    def test_build_search_js_injects_query_limit_and_scrolls(self) -> None:
        js = build_search_js("claude's \"code\"", limit=7, scrolls=2)

        self.assertIn(json.dumps("claude's \"code\""), js)
        self.assertIn("const LIMIT = 7;", js)
        self.assertIn("for (let i = 0; i < 2; i++)", js)
        self.assertNotIn("__QUERY_JSON__", js)
        self.assertNotIn("__LIMIT__", js)
        self.assertNotIn("__SCROLLS__", js)

    def test_search_raises_login_required_when_backend_reports_login_wall(self) -> None:
        backend = FakeBackend({"login_required": True, "source": "linkedin", "items": []})

        with self.assertRaises(LoginRequired) as raised:
            search("claude code", backend=backend)

        self.assertEqual(raised.exception.source, "linkedin")


if __name__ == "__main__":
    unittest.main()
