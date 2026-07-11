from __future__ import annotations

import unittest
from datetime import datetime, timezone

import tests  # noqa: F401
from engine.model import parse_relative_age, strip_tracking


class TextParsingTests(unittest.TestCase):
    def test_parse_relative_age_uses_fixed_now(self) -> None:
        now = datetime(2026, 7, 4, 12, 0, tzinfo=timezone.utc)
        cases = {
            "4m": "2026-07-04T11:56:00Z",
            "2h": "2026-07-04T10:00:00Z",
            "3d": "2026-07-01T12:00:00Z",
            "1w": "2026-06-27T12:00:00Z",
            "2mo": "2026-05-05T12:00:00Z",
            "1y": "2025-07-04T12:00:00Z",
            "3d •": "2026-07-01T12:00:00Z",
            "3 days ago": "2026-07-01T12:00:00Z",
        }

        for label, expected in cases.items():
            with self.subTest(label=label):
                self.assertEqual(parse_relative_age(label, now=now), expected)

    def test_parse_relative_age_returns_none_for_missing_or_unknown_labels(self) -> None:
        self.assertIsNone(parse_relative_age(None))
        self.assertIsNone(parse_relative_age("garbage"))

    def test_strip_tracking_removes_query_and_fragment(self) -> None:
        url = (
            "https://www.linkedin.com/posts/siddhartharoraisb_ai-product-manager-please-read-these-25-share-"
            "7479112436957130752-aY9H/?utm_source=share&utm_medium=member_desktop&rcm=ACoAAACp#frag"
        )

        stripped = strip_tracking(url)

        self.assertEqual(
            stripped,
            "https://www.linkedin.com/posts/siddhartharoraisb_ai-product-manager-please-read-these-25-share-"
            "7479112436957130752-aY9H/",
        )
        self.assertNotIn("rcm=", stripped or "")
        self.assertNotIn("utm_", stripped or "")


if __name__ == "__main__":
    unittest.main()
