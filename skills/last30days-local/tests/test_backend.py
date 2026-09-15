from __future__ import annotations

import unittest
from unittest.mock import patch
from pathlib import Path

import tests  # noqa: F401
from engine.backend import AsideBackend, BackendError, extract_payload


FIXTURES = Path(__file__).resolve().parent / "fixtures"


class ExecutableTests(unittest.TestCase):
    def test_resolves_executable_without_a_personal_home_path(self) -> None:
        with patch.dict("os.environ", {}, clear=True):
            self.assertEqual(AsideBackend().aside_bin, "aside")
        with patch.dict("os.environ", {"ASIDE_BIN": "/opt/team tools/aside"}):
            self.assertEqual(AsideBackend().aside_bin, "/opt/team tools/aside")
            self.assertEqual(AsideBackend("/custom/aside").aside_bin, "/custom/aside")


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
