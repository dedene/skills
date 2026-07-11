from __future__ import annotations

import unittest
from pathlib import Path
from unittest import mock

import tests  # noqa: F401
from engine.backend import BackendError
from engine.sources import youtube_ytdlp


FIXTURES = Path(__file__).resolve().parent / "fixtures"


class YouTubeYtDlpTests(unittest.TestCase):
    def test_parse_ytdlp_lines_skips_malformed_lines(self) -> None:
        text = '{"id": "ok"}\nnot-json\n[]\n{"id": "also-ok"}\n'

        objs = youtube_ytdlp.parse_ytdlp_lines(text)

        self.assertEqual(objs, [{"id": "ok"}, {"id": "also-ok"}])

    def test_normalize_videos_maps_ytdlp_fixture_to_items(self) -> None:
        text = (FIXTURES / "youtube_search_ytdlp.jsonl").read_text(encoding="utf-8")
        items = youtube_ytdlp.normalize_videos(youtube_ytdlp.parse_ytdlp_lines(text))

        self.assertEqual(len(items), 5)
        first = items[0]
        self.assertEqual(first.source, "youtube")
        self.assertEqual(first.id, "Nm-TkTQJN-Y")
        self.assertEqual(first.url, "https://www.youtube.com/watch?v=Nm-TkTQJN-Y")
        self.assertEqual(first.author, "Zinho Automates")
        self.assertEqual(first.published_at, "2026-07-03T14:21:19Z")
        self.assertEqual(first.engagement["views"], 14135)
        self.assertEqual(first.engagement["comments"], 12)
        self.assertEqual(first.raw["_derived"], {"date_confidence": "exact"})
        self.assertNotIn("formats", first.raw)

    def test_upload_date_falls_back_to_day_confidence(self) -> None:
        items = youtube_ytdlp.normalize_videos(
            [
                {
                    "id": "abc",
                    "title": "Title",
                    "upload_date": "20260703",
                    "webpage_url": "https://youtube.test/watch?v=abc",
                }
            ]
        )

        self.assertEqual(items[0].published_at, "2026-07-03")
        self.assertEqual(items[0].raw["_derived"], {"date_confidence": "day"})

    def test_search_missing_ytdlp_raises_install_hint(self) -> None:
        with mock.patch.object(youtube_ytdlp.shutil, "which", return_value=None):
            with self.assertRaises(BackendError) as raised:
                youtube_ytdlp.search("claude code")

        self.assertIn("brew install yt-dlp", str(raised.exception))


if __name__ == "__main__":
    unittest.main()
