from __future__ import annotations

import time
from collections import defaultdict, deque

from fastapi import HTTPException, Request, status


class InMemoryRateLimiter:
    """Simple sliding-window limiter keyed by client IP.

    Good enough to blunt brute-force login/refresh attempts from a single
    process; a multi-process deployment needs a shared store (Redis) instead
    -- tracked in the roadmap.
    """

    def __init__(self, max_requests: int, window_seconds: float) -> None:
        self.max_requests = max_requests
        self.window_seconds = window_seconds
        self._hits: dict[str, deque[float]] = defaultdict(deque)

    def __call__(self, request: Request) -> None:
        client_ip = request.client.host if request.client else "unknown"
        now = time.monotonic()
        hits = self._hits[client_ip]
        while hits and now - hits[0] > self.window_seconds:
            hits.popleft()
        if len(hits) >= self.max_requests:
            raise HTTPException(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                detail="Too many attempts. Please wait before trying again.",
            )
        hits.append(now)


login_rate_limiter = InMemoryRateLimiter(max_requests=10, window_seconds=60.0)
refresh_rate_limiter = InMemoryRateLimiter(max_requests=30, window_seconds=60.0)
