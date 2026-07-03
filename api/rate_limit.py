"""Small in-memory rate limiter for lightweight API deployments."""
import time
from collections import defaultdict, deque
from typing import Deque, Dict, Set

from fastapi import Request


class InMemoryRateLimiter:
    """Track request timestamps by client/path in this process."""

    def __init__(self, per_minute: int, exempt_paths: Set[str]):
        self.per_minute = per_minute
        self.exempt_paths = exempt_paths
        self._window: Dict[str, Deque[float]] = defaultdict(deque)

    def clear(self) -> None:
        self._window.clear()

    def is_allowed(self, request: Request) -> bool:
        if self.per_minute <= 0 or request.url.path in self.exempt_paths:
            return True

        key = f"{self._client_host(request)}:{request.url.path}"
        now = time.monotonic()
        request_times = self._window[key]

        while request_times and now - request_times[0] > 60:
            request_times.popleft()

        if len(request_times) >= self.per_minute:
            return False

        request_times.append(now)
        return True

    @staticmethod
    def _client_host(request: Request) -> str:
        forwarded_for = request.headers.get("x-forwarded-for", "")
        client_host = forwarded_for.split(",", 1)[0].strip() if forwarded_for else None
        if client_host:
            return client_host
        return request.client.host if request.client else "unknown"
