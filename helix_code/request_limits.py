"""[FACT] Shared in-memory rate limiting helpers for operational ingress."""

from __future__ import annotations

import time
from collections import defaultdict, deque
from collections.abc import Callable
from threading import Lock


class SlidingWindowRateLimiter:
    """[FACT] Track per-key events inside a bounded sliding window."""

    def __init__(self, now_fn: Callable[[], float] | None = None) -> None:
        self._events: dict[str, deque[float]] = defaultdict(deque)
        self._lock = Lock()
        self._now_fn = now_fn or time.monotonic

    def allow(self, key: str, limit: int, window_seconds: float) -> tuple[bool, float]:
        """[FACT] Return allow/deny plus a retry-after estimate in seconds."""
        if limit <= 0 or window_seconds <= 0:
            return True, 0.0

        now = self._now_fn()
        cutoff = now - window_seconds

        with self._lock:
            bucket = self._events[key]
            while bucket and bucket[0] <= cutoff:
                bucket.popleft()

            if len(bucket) >= limit:
                retry_after = max(window_seconds - (now - bucket[0]), 0.0)
                return False, retry_after

            bucket.append(now)
            return True, 0.0
