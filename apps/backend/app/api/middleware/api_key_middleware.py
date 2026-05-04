from fastapi import FastAPI
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import JSONResponse


class APIKeyMiddleware(BaseHTTPMiddleware):
    DEFAULT_EXEMPT_PREFIXES = ("/api/workflows/", "/api/integrations/")

    async def dispatch(self, request, call_next):
        if request.url.path.startswith("/third-party"):
            api_key = request.headers.get("x-api-key")

            if not api_key or api_key != "your-secret-key":
                return JSONResponse({"detail": "Invalid API Key"}, status_code=403)

        return await call_next(request)


def add_api_key_middleware(app: FastAPI) -> None:
    """Utility to add the API KEY middleware to the FastAPI app."""
    app.add_middleware(APIKeyMiddleware)
