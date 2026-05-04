"""Rate limiting / network throttling middleware."""

import asyncio
import time
import uuid
from typing import Any

from fastapi import FastAPI, Request
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import JSONResponse

from app.config.settings import Settings
from app.logger import logger

_SLIDING_WINDOW_LUA = r"""
redis.call('ZREMRANGEBYSCORE', KEYS[1], '-inf', tostring(tonumber(ARGV[1]) - tonumber(ARGV[2])) )
local count = redis.call('ZCARD', KEYS[1])

if tonumber(count) >= tonumber(ARGV[3]) then
  return {0, count}
end

redis.call('ZADD', KEYS[1], ARGV[1], ARGV[4])
count = count + 1

redis.call('PEXPIRE', KEYS[1], ARGV[2])

return {1, count}
"""


class RateLimitMiddleware(BaseHTTPMiddleware):
    def __init__(
        self, app: FastAPI, settings: Settings, redis_client: Any | None = None
    ):
        super().__init__(app)

        self.settings = settings
        self.enabled = bool(getattr(settings, "rate_limit_enabled", False))
        self.max_requests = int(getattr(settings, "rate_limit_requests", 500))
        self.window = int(getattr(settings, "rate_limit_window_seconds", 60))

        whitelist_raw = getattr(settings, "rate_limit_whitelist", "") or ""
        self.whitelist: set[str] = {
            ip.strip() for ip in whitelist_raw.split(",") if ip.strip()
        }

        # ✅ Overrides parsing
        overrides_raw = getattr(settings, "rate_limit_overrides", "") or ""
        self.overrides: dict[str, int] = {}

        for entry in (p.strip() for p in overrides_raw.split(",") if p.strip()):
            if ":" not in entry:
                logger.warning("Invalid override format", entry=entry)
                continue

            path, val = entry.split(":", 1)
            path = path.rstrip("/") or "/"

            try:
                self.overrides[path] = int(val)
            except Exception:
                logger.warning("Invalid override value", entry=entry)

        # In-memory fallback
        self._counters: dict[str, tuple[int, int]] = {}
        self._lock = asyncio.Lock()

        # Redis
        self.redis = redis_client
        self.backend = getattr(settings, "rate_limit_backend", "memory")

        self._lua_sha: str | None = None

        if self.backend == "redis" and self.redis:
            try:
                loop = asyncio.get_event_loop()

                async def _register():
                    return await self.redis.script_load(_SLIDING_WINDOW_LUA)

                self._register_task = loop.create_task(_register())
            except Exception:
                logger.exception("Failed to register Lua script")

    # ✅ Device/IP identifier
    def _get_identifier(self, request: Request) -> str:
        forwarded = request.headers.get("x-forwarded-for")

        if forwarded:
            client_ip = forwarded.split(",")[0].strip()
        elif request.client:
            client_ip = request.client.host
        else:
            client_ip = "unknown"

        return (
            request.headers.get("x-device-id")
            or request.headers.get("authorization")
            or client_ip
        )

    # ✅ Redis logic
    async def _redis_allowed(self, key: str, limit: int) -> tuple[bool, int]:
        if not self.redis:
            return True, 0

        now_ms = int(time.time() * 1000)
        window_ms = int(self.window * 1000)
        member = f"{now_ms}-{uuid.uuid4().hex}"

        try:
            sha = getattr(self, "_lua_sha", None)

            if sha is None and hasattr(self, "_register_task"):
                task = getattr(self, "_register_task")
                if task.done() and not task.cancelled() and task.exception() is None:
                    sha = task.result()
                    self._lua_sha = sha

            if sha:
                result = await self.redis.evalsha(
                    sha, 1, key, now_ms, window_ms, limit, member
                )
            else:
                result = await self.redis.eval(
                    _SLIDING_WINDOW_LUA, 1, key, now_ms, window_ms, limit, member
                )

            allowed = bool(result[0])
            count = int(result[1])  # ✅ post-add count

            return allowed, count

        except Exception:
            logger.exception("Redis failed, allowing request")
            return True, 0  # ✅ fail-open

    async def dispatch(self, request: Request, call_next):
        if not self.enabled:
            return await call_next(request)

        identifier = self._get_identifier(request)

        if identifier in self.whitelist:
            return await call_next(request)

        route_path = (request.url.path or "/").rstrip("/") or "/"
        matched_override = None
        for k in self.overrides:
            if route_path == k or route_path.startswith(f"{k}/"):
                if matched_override is None or len(k) > len(matched_override):
                    matched_override = k

        effective_max = (
            self.max_requests
            if matched_override is None
            else self.overrides[matched_override]
        )

        headers = {
            "X-RateLimit-Limit": str(effective_max),
            "X-RateLimit-Remaining": "0",
            "X-RateLimit-Reset": "0",
        }

        # ✅ REDIS PATH
        if self.backend == "redis" and self.redis:
            key = f"{getattr(self.settings, 'rate_limit_redis_prefix', 'rate_limit:')}{identifier}:{route_path}"

            allowed, count = await self._redis_allowed(key, effective_max)

            remaining = max(effective_max - count, 0)
            reset_ts = int(time.time()) + self.window

            headers["X-RateLimit-Remaining"] = str(remaining)
            headers["X-RateLimit-Reset"] = str(reset_ts)

            if not allowed:
                logger.warning(
                    "Rate limit exceeded (redis)",
                    identifier=identifier,
                    count=count,
                    limit=effective_max,
                )
                return JSONResponse(
                    {"detail": "Rate limit exceeded."},
                    status_code=429,
                    headers=headers,
                )

            response = await call_next(request)

            for k, v in headers.items():
                response.headers.setdefault(k, v)

            return response

        # ✅ IN-MEMORY FALLBACK
        now = int(time.time())

        async with self._lock:
            counter_key = f"{identifier}:{route_path}"
            count, start = self._counters.get(counter_key, (0, now))

            if now - start >= self.window:
                start = now
                count = 0

            count += 1

            self._counters[counter_key] = (count, start)

            remaining = max(effective_max - count, 0)
            reset_ts = start + self.window

            headers["X-RateLimit-Remaining"] = str(remaining)
            headers["X-RateLimit-Reset"] = str(reset_ts)

            if count > effective_max:
                logger.warning(
                    "Rate limit exceeded",
                    identifier=identifier,
                    count=count,
                    limit=effective_max,
                )
                return JSONResponse(
                    {"detail": "Rate limit exceeded."},
                    status_code=429,
                    headers=headers,
                )

        response = await call_next(request)

        for k, v in headers.items():
            response.headers.setdefault(k, v)

        return response


def add_rate_limit_middleware(app: FastAPI) -> None:
    settings = Settings.initialize()

    redis_client = None

    if getattr(settings, "rate_limit_backend", "memory") == "redis":
        try:
            import redis.asyncio as aioredis

            if settings.rate_limit_redis_url:
                redis_client = aioredis.from_url(settings.rate_limit_redis_url)

                async def _close_redis():
                    try:
                        await redis_client.close()
                        await redis_client.connection_pool.disconnect()
                    except Exception:
                        logger.exception("Error closing Redis")

                app.add_event_handler(
                    "shutdown", lambda: asyncio.create_task(_close_redis())
                )

        except Exception:
            logger.exception("Redis init failed, fallback to memory")
            redis_client = None

    app.add_middleware(
        RateLimitMiddleware,
        settings=settings,
        redis_client=redis_client,
    )
