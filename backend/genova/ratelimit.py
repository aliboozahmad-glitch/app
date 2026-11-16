import time
from collections import defaultdict, deque

from fastapi import HTTPException


class RateLimiter:
    """In-memory sliding window per key (single worker). Replace with Redis when scaling out."""

    def __init__(self, limit: int, window_s: int):
        self.limit, self.window = limit, window_s
        self.hits: dict = defaultdict(deque)

    def check(self, key: str) -> None:
        now = time.monotonic()
        q = self.hits[key]
        while q and now - q[0] > self.window:
            q.popleft()
        if len(q) >= self.limit:
            raise HTTPException(status_code=429, detail="Too many requests. Please wait a moment.")
        q.append(now)


analysis_limiter = RateLimiter(limit=30, window_s=60)
