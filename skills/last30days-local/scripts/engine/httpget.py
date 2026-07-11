from __future__ import annotations

import socket
import time
import urllib.error
import urllib.request
from typing import Callable

from .backend import BackendError


USER_AGENT = (
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
    "AppleWebKit/537.36 (KHTML, like Gecko) "
    "Chrome/124.0.0.0 Safari/537.36"
)
ACCEPT_LANGUAGE = "en-US,en;q=0.9"
MIN_REQUEST_INTERVAL = 0.25

_clock: Callable[[], float] = time.monotonic
_sleep: Callable[[float], object] = time.sleep
_last_request_at: float | None = None


def set_http_hooks(
    *,
    clock: Callable[[], float] | None = None,
    sleep: Callable[[float], object] | None = None,
) -> None:
    global _clock, _sleep, _last_request_at
    _clock = clock or time.monotonic
    _sleep = sleep or time.sleep
    _last_request_at = None


def headers(accept: str) -> dict[str, str]:
    return {
        "User-Agent": USER_AGENT,
        "Accept-Language": ACCEPT_LANGUAGE,
        "Accept": accept,
    }


def get(url: str, accept: str = "application/json", opener: Callable[..., bytes] | None = None) -> bytes:
    global _last_request_at
    now = _clock()
    if _last_request_at is not None:
        elapsed = now - _last_request_at
        if elapsed < MIN_REQUEST_INTERVAL:
            _sleep(MIN_REQUEST_INTERVAL - elapsed)
            now = _clock()
    _last_request_at = now

    request_headers = headers(accept)
    try:
        if opener is not None:
            try:
                return opener(url, request_headers)
            except TypeError:
                return opener(url)

        request = urllib.request.Request(url, headers=request_headers)
        with urllib.request.urlopen(request, timeout=30) as response:
            return response.read()
    except (urllib.error.HTTPError, urllib.error.URLError, TimeoutError, socket.timeout) as exc:
        raise BackendError(_error_message(url, exc)) from exc


def _error_message(url: str, exc: BaseException) -> str:
    if isinstance(exc, urllib.error.HTTPError):
        return f"request failed: url={url!r}; status={exc.code}; reason={exc.reason}"
    if isinstance(exc, urllib.error.URLError):
        return f"request failed: url={url!r}; reason={exc.reason}"
    return f"request failed: url={url!r}; reason={exc}"
