from __future__ import annotations

import contextlib
import io
import json
import unittest
from argparse import Namespace
from pathlib import Path

import tests  # noqa: F401
from engine.backend import LoginRequired, extract_payload
from engine.sources import aside_instagram, aside_pinterest, aside_threads, aside_tiktok
from last30days import run_search


FIXTURES = Path(__file__).resolve().parent / "fixtures"


def load_payload(name: str) -> dict:
    return json.loads((FIXTURES / f"{name}_search_payload.json").read_text(encoding="utf-8"))


class FakeBackend:
    def __init__(self, payload: dict) -> None:
        self.payload = payload
        self.js: str | None = None

    def run_js(self, js: str) -> dict:
        self.js = js
        return self.payload


class NewAsideSourceTests(unittest.TestCase):
    def test_extracts_payloads_from_noisy_aside_stdout(self) -> None:
        expected = {"threads": 5, "tiktok": 14, "instagram": 56, "pinterest": 24}

        for source, count in expected.items():
            with self.subTest(source=source):
                stdout = (FIXTURES / f"{source}_search_stdout.txt").read_text(encoding="utf-8")

                payload = extract_payload(stdout)

                self.assertEqual(payload["count"], count)
                self.assertEqual(len(payload["items"]), count)

    def test_threads_normalize_items_maps_fixture_rows_to_items(self) -> None:
        items = aside_threads.normalize_items(load_payload("threads"))

        self.assertEqual(len(items), 5)
        first = items[0]
        self.assertEqual(first.source, "threads")
        self.assertEqual(first.id, "DaXebZHAeW8")
        self.assertEqual(first.url, "https://www.threads.com/@aiposthub/post/DaXebZHAeW8")
        self.assertEqual(first.author, "@aiposthub")
        self.assertEqual(first.author_url, "https://www.threads.com/@aiposthub")
        self.assertEqual(first.published_at, "2026-07-04T09:59:22.000Z")
        self.assertEqual(first.engagement, {"likes": None, "replies": 1, "reposts": None, "shares": None})
        self.assertEqual(first.raw["_derived"], {"date_confidence": "exact"})
        self.assertNotIn("aiposthub\n7 m", first.text or "")
        self.assertNotIn("Vertalen", first.text or "")
        self.assertFalse((first.text or "").endswith("\n1"))

    def test_threads_drops_leading_reply_context_after_initial_lines(self) -> None:
        payload = {
            "items": [
                {
                    "post_href": "/@handle/post/DaSynthetic",
                    "author_href": "/@handle",
                    "datetime": "2026-07-04T09:59:22.000Z",
                    "text": "handle\n10 m\nJe beantwoordt @x\nActual content line",
                    "actions": [],
                }
            ]
        }

        item = aside_threads.normalize_items(payload)[0]

        self.assertEqual(item.text, "Actual content line")

    def test_tiktok_normalize_items_maps_fixture_rows_to_items(self) -> None:
        items = aside_tiktok.normalize_items(load_payload("tiktok"))

        self.assertEqual(len(items), 12)
        first = items[0]
        self.assertEqual(first.source, "tiktok")
        self.assertEqual(first.id, "7657180977130687758")
        self.assertEqual(first.url, "https://www.tiktok.com/@brockmesarich/video/7657180977130687758")
        self.assertEqual(first.author, "@brockmesarich")
        self.assertEqual(first.author_url, "https://www.tiktok.com/@brockmesarich")
        self.assertEqual(first.published_at, "2026-06-30T13:32:55Z")
        self.assertEqual(
            first.text,
            "There's a single file on GitHub with 170,000 stars that makes Claude noticeably smarter the second you install it.",
        )
        self.assertEqual(first.engagement, {"views": 23600})
        self.assertEqual(first.raw["_derived"], {"date_confidence": "approx_id"})

    def test_instagram_normalize_items_maps_fixture_rows_to_items(self) -> None:
        items = aside_instagram.normalize_items(load_payload("instagram"))

        self.assertEqual(len(items), 45)
        second = items[1]
        self.assertEqual(second.source, "instagram")
        self.assertEqual(second.id, "DaSw3YwlC3s")
        self.assertEqual(second.url, "https://www.instagram.com/p/DaSw3YwlC3s/")
        self.assertEqual(second.author, "@fullstackparody")
        self.assertEqual(second.author_url, "https://www.instagram.com/fullstackparody/")
        self.assertEqual(second.published_at, "2026-07-02T14:04:18.000Z")
        self.assertTrue((second.text or "").startswith("Claude Code has 65+ features."))
        self.assertEqual(second.engagement, {"likes": 1})
        self.assertEqual(second.raw["_derived"], {"date_confidence": "exact"})

        non_enriched = items[4]
        self.assertEqual(non_enriched.id, "DZyLyIUGo_G")
        self.assertEqual(non_enriched.published_at, "2026-06-19T22:24:32Z")
        self.assertEqual(non_enriched.raw["_derived"], {"date_confidence": "approx_id"})

    def test_pinterest_normalize_items_maps_fixture_rows_to_items(self) -> None:
        items = aside_pinterest.normalize_items(load_payload("pinterest"))

        self.assertEqual(len(items), 24)
        first = items[0]
        self.assertEqual(first.source, "pinterest")
        self.assertEqual(first.id, "71705819063263974")
        self.assertEqual(first.url, "https://www.pinterest.com/pin/71705819063263974/")
        self.assertIsNone(first.author)
        self.assertIsNone(first.author_url)
        self.assertIsNone(first.published_at)
        self.assertEqual(first.text, "a hand holding a pen over a white sheet of paper with the words claude code workflow sheetsheet on it")
        self.assertEqual(first.engagement, {})
        self.assertEqual(first.raw["_derived"], {"date_confidence": "none"})

    def test_timestamp_helpers(self) -> None:
        self.assertEqual(aside_tiktok.tiktok_id_timestamp("7657180977130687758"), "2026-06-30T13:32:55Z")
        self.assertIsNone(aside_tiktok.tiktok_id_timestamp("not-numeric"))
        self.assertTrue((aside_instagram.instagram_shortcode_timestamp("DaSw3YwlC3s") or "").startswith("2026-07-02"))
        self.assertIsNone(aside_instagram.instagram_shortcode_timestamp("DaSw3YwlC3s!"))
        self.assertIsNone(aside_instagram.instagram_shortcode_timestamp("DaSw3YwlC3sTooLong"))

    def test_search_raises_login_required_for_new_sources(self) -> None:
        cases = {
            "threads": aside_threads.search,
            "tiktok": aside_tiktok.search,
            "instagram": aside_instagram.search,
            "pinterest": aside_pinterest.search,
        }

        for source, search in cases.items():
            with self.subTest(source=source):
                backend = FakeBackend({"login_required": True, "source": source, "items": []})

                with self.assertRaises(LoginRequired) as raised:
                    search("claude code", backend=backend)

                self.assertEqual(raised.exception.source, source)

    def test_build_search_js_injects_values_and_clears_placeholders(self) -> None:
        query = "claude's \"code\" / 日本語"
        cases = [
            (aside_threads.build_search_js(query, scrolls=2), ["const q = " + json.dumps(query), "for (let i = 0; i < 2; i++)"]),
            (aside_tiktok.build_search_js(query, scrolls=2), ["const q = " + json.dumps(query), "for (let i = 0; i < 2; i++)"]),
            (aside_instagram.build_search_js(query, enrich=3, scrolls=2), ["const q = " + json.dumps(query), "const ENRICH = 3;", "for (let i = 0; i < 2; i++)"]),
            (aside_pinterest.build_search_js(query, scrolls=2), ["const q = " + json.dumps(query), "for (let i = 0; i < 2; i++)"]),
        ]

        for js, expected_snippets in cases:
            with self.subTest(snippet=expected_snippets[0]):
                for snippet in expected_snippets:
                    self.assertIn(snippet, js)
                self.assertNotIn("__QUERY_JSON__", js)
                self.assertNotIn("__SCROLLS__", js)
                self.assertNotIn("__LIMIT__", js)
                self.assertNotIn("__ENRICH__", js)

    def test_unknown_source_error_lists_all_sources(self) -> None:
        stderr = io.StringIO()
        args = Namespace(
            source="nosuchsource",
            query="claude code",
            days=30,
            limit=20,
            backend="aside",
            wait_login=False,
            json=False,
        )

        with contextlib.redirect_stderr(stderr):
            code = run_search(args)

        self.assertEqual(code, 2)
        self.assertIn(
            "available sources: bluesky, github, hackernews, instagram, linkedin, pinterest, polymarket, reddit, threads, tiktok, web, x, youtube",
            stderr.getvalue(),
        )


if __name__ == "__main__":
    unittest.main()
