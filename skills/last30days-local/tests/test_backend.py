from __future__ import annotations

import unittest
from pathlib import Path

import tests  # noqa: F401
from engine.backend import BackendError, extract_payload


FIXTURES = Path(__file__).resolve().parent / "fixtures"


class ExtractPayloadTests(unittest.TestCase):
    def test_extracts_payload_from_noisy_aside_stdout(self) -> None:
        stdout = (FIXTURES / "x_search_stdout.txt").read_text(encoding="utf-8")

        payload = extract_payload(stdout)

        self.assertEqual(payload["count"], 13)
        self.assertEqual(len(payload["items"]), 13)

    def test_missing_sentinels_raise_backend_error(self) -> None:
        with self.assertRaisesRegex(BackendError, "sentinels missing"):
            extract_payload("no json here")

    def test_malformed_json_raises_backend_error(self) -> None:
        stdout = "<<<JSON_START>>>\n{not json}\n<<<JSON_END>>>"

        with self.assertRaisesRegex(BackendError, "JSON parse error"):
            extract_payload(stdout)


if __name__ == "__main__":
    unittest.main()
