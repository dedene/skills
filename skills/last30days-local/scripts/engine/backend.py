from __future__ import annotations

import json
import subprocess
from typing import Any, Protocol


JSON_START = "<<<JSON_START>>>"
JSON_END = "<<<JSON_END>>>"


class BackendError(RuntimeError):
    """Raised when the browser backend cannot return a valid payload."""


class LoginRequired(RuntimeError):
    """Raised when a source reports that the browser is not logged in."""

    LOGIN_URLS = {
        "x": "https://x.com/login",
        "linkedin": "https://www.linkedin.com/login",
        "threads": "https://www.threads.com/login",
        "tiktok": "https://www.tiktok.com/login",
        "instagram": "https://www.instagram.com/accounts/login/",
        "pinterest": "https://www.pinterest.com/login/",
    }

    def __init__(self, source: str) -> None:
        self.source = source
        url = self.LOGIN_URLS.get(source, source)
        super().__init__(f"login required for {source}: open {url} in the Aside browser and log in, then retry")


class Backend(Protocol):
    def run_js(self, js: str) -> dict[str, Any]:
        ...


def _tail(value: str | bytes | None, limit: int = 500) -> str:
    if value is None:
        return ""
    if isinstance(value, bytes):
        value = value.decode("utf-8", errors="replace")
    return value[-limit:]


def _diagnostic(reason: str, *, exit_code: int | str | None, stdout: str | bytes | None, stderr: str | bytes | None) -> str:
    return (
        f"{reason}; exit_code={exit_code if exit_code is not None else 'n/a'}; "
        f"stdout_tail={_tail(stdout)!r}; stderr_tail={_tail(stderr)!r}"
    )


def extract_payload(stdout: str) -> dict[str, Any]:
    start = stdout.find(JSON_START)
    end = stdout.find(JSON_END, start + len(JSON_START))
    if start < 0 or end < 0:
        raise BackendError(_diagnostic("sentinels missing", exit_code=None, stdout=stdout, stderr=""))

    raw = stdout[start + len(JSON_START) : end].strip()
    try:
        payload = json.loads(raw)
    except json.JSONDecodeError as exc:
        raise BackendError(_diagnostic(f"JSON parse error: {exc}", exit_code=None, stdout=stdout, stderr="")) from exc
    if not isinstance(payload, dict):
        raise BackendError(_diagnostic("JSON payload was not an object", exit_code=None, stdout=stdout, stderr=""))
    return payload


class AsideBackend:
    def __init__(self, aside_bin: str = "/Users/peter/.local/bin/aside", timeout: int = 90) -> None:
        self.aside_bin = aside_bin
        self.timeout = timeout

    def run_js(self, js: str) -> dict[str, Any]:
        command = [self.aside_bin, "repl", js]
        try:
            result = subprocess.run(
                command,
                capture_output=True,
                text=True,
                timeout=self.timeout,
                check=False,
            )
        except subprocess.TimeoutExpired as exc:
            raise BackendError(
                _diagnostic(
                    f"timeout after {self.timeout}s",
                    exit_code="timeout",
                    stdout=exc.stdout,
                    stderr=exc.stderr,
                )
            ) from exc

        if result.returncode != 0:
            raise BackendError(
                _diagnostic(
                    "nonzero exit",
                    exit_code=result.returncode,
                    stdout=result.stdout,
                    stderr=result.stderr,
                )
            )

        try:
            return extract_payload(result.stdout)
        except BackendError as exc:
            raise BackendError(
                _diagnostic(
                    str(exc).split(";", 1)[0],
                    exit_code=result.returncode,
                    stdout=result.stdout,
                    stderr=result.stderr,
                )
            ) from exc


BACKENDS = {"aside": AsideBackend}


def get_backend(name: str = "aside") -> Backend:
    try:
        backend_cls = BACKENDS[name]
    except KeyError as exc:
        available = ", ".join(sorted(BACKENDS))
        raise ValueError(f"unknown backend {name!r}; available backends: {available}") from exc
    return backend_cls()
