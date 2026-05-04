"""CSRF protection middleware."""

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from fastapi_csrf_protect import CsrfProtect
from starlette.middleware.base import BaseHTTPMiddleware

from app.api.shared_schemas.common import ErrorResponse
from app.config.settings import Settings
from app.shared.constants.error_codes import ErrorCodes

# Paths that are exempt from CSRF validation (integration, workflow, process-now, health APIs)
CSRF_EXEMPT_PREFIXES: tuple[str, ...] = (
    "/api/health",
    "/api/auth/login",
    "/api/auth/refresh",
    "/api/auth/forgot-password",
    "/api/auth/reset-password",
    "/api/integrations",
    "/api/workflows",
    "/api/process-now",
)

CSRF_PROTECTED_METHODS: frozenset[str] = frozenset({"POST", "PUT", "DELETE", "PATCH"})

CSRF_HEADER_NAME: str = "X-CSRF-Token"


def configure_csrf(settings: Settings) -> None:
    """Load CSRF configuration from application settings."""
    is_dev = settings.mode.lower() in ("development", "local")

    @CsrfProtect.load_config
    def get_csrf_config():
        config = [
            ("secret_key", settings.csrf_secret_key),
            ("httponly", True),
            ("max_age", settings.csrf_expiry_seconds),
        ]
        if is_dev:
            config += [
                ("cookie_samesite", "none"),
                ("cookie_secure", True),
            ]
        else:
            config += [
                ("cookie_samesite", "strict"),
                ("cookie_secure", True),
            ]
        return config


class CsrfMiddleware(BaseHTTPMiddleware):
    """Middleware that enforces session-bound CSRF validation on state-changing requests.
    """

    def __init__(
        self,
        app,
        settings: Settings,
        exempt_prefixes: tuple[str, ...] = CSRF_EXEMPT_PREFIXES,
    ) -> None:
        super().__init__(app)
        self._exempt = exempt_prefixes
        self._settings = settings

    async def dispatch(self, request: Request, call_next):
        if request.method in CSRF_PROTECTED_METHODS:
            path = request.url.path
            if not any(path.startswith(prefix) for prefix in self._exempt):
                csrf = CsrfProtect()
                try:
                    await csrf.validate_csrf(request)
                except Exception as e:
                    return self._reject(403, request, f"CSRF validation failed: {str(e)}")

        return await call_next(request)

    def _reject(self, status_code: int, request: Request, message: str) -> JSONResponse:
        response =  JSONResponse(
            status_code=status_code,
            content=ErrorResponse(
                status_code=status_code,
                error_code=ErrorCodes.CSRF_TOKEN_INVALID,
                message=message,
                path=request.url.path,
            ).model_dump(mode="json"),
        )
        response.headers["Access-Control-Allow-Origin"] = request.headers.get("origin")
        response.headers["Access-Control-Allow-Credentials"] = "true"
        response.headers["Access-Control-Allow-Methods"] = ",".join(CSRF_PROTECTED_METHODS)
        response.headers["Access-Control-Allow-Headers"] = "Content-Type,X-CSRF-Token,Authorization"
        return response

def add_csrf_middleware(app: FastAPI) -> None:
    """Configure CSRF protection and register the middleware."""
    settings = Settings.initialize()
    configure_csrf(settings)
    app.add_middleware(CsrfMiddleware, settings=settings)
