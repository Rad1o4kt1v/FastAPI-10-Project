# app/rate_limiter.py
import time
import aioredis
from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.status import HTTP_429_TOO_MANY_REQUESTS


class RateLimiterMiddleware(BaseHTTPMiddleware):
    def __init__(self, app, redis_url: str, limit: int = 5, window_sec: int = 60):
        super().__init__(app)
        self.redis_url = redis_url
        self.limit = limit
        self.window = window_sec
        self.redis = None

    async def dispatch(self, request: Request, call_next):
        if self.redis is None:
            self.redis = aioredis.from_url(
                self.redis_url, encoding="utf-8", decode_responses=True
            )

        client_ip = request.client.host  # Или request.headers.get("X-Real-IP")
        window_id = int(time.time()) // self.window
        key = f"rate_limit:{client_ip}:{window_id}"

        count = await self.redis.incr(key)
        if count == 1:
            await self.redis.expire(key, self.window)

        if count > self.limit:
            return Response(
                content="⛔ Too Many Requests",
                status_code=HTTP_429_TOO_MANY_REQUESTS
            )

        return await call_next(request)
