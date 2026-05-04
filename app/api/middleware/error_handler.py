"""Global exception handlers for the API."""

from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse

from app.api.shared_schemas.common import ErrorResponse
from app.logger import logger
from app.shared.constants.error_codes import ErrorCodes
from app.shared.constants.error_messages import ErrorMessages
from app.shared.constants.http_status import HTTPStatus
from app.shared.exceptions.base import AppException


def app_exception_handler(request: Request, exc: AppException) -> JSONResponse:
    """
    Handle custom application exceptions.

    Args:
        request: FastAPI request object
        exc: Application exception

    Returns:
        JSON response with error details
    """
    logger.error(
        f"Application error: {exc.error_code}",
        error_message=exc.message,
        detail=exc.detail,
        path=request.url.path,
        method=request.method,
    )

    response = ErrorResponse(
        status_code=exc.status_code,
        error_code=exc.error_code,
        message=exc.message,
        path=request.url.path,
        detail=exc.detail,
    )

    return JSONResponse(
        status_code=exc.status_code,
        content=response.model_dump(mode="json"),
    )


def generic_exception_handler(request: Request, exc: Exception) -> JSONResponse:
    """
    Handle unexpected exceptions.

    Args:
        request: FastAPI request object
        exc: Generic exception

    Returns:
        JSON response with generic error message
    """
    logger.error(
        f"Unhandled exception: {type(exc).__name__}",
        error=str(exc),
        path=request.url.path,
        method=request.method,
    )

    response = ErrorResponse(
        status_code=HTTPStatus.INTERNAL_SERVER_ERROR,
        error_code=ErrorCodes.INTERNAL_ERROR,
        message=ErrorMessages.INTERNAL_ERROR,
        detail=str(exc),
        path=request.url.path,
    )

    return JSONResponse(
        status_code=HTTPStatus.INTERNAL_SERVER_ERROR,
        content=response.model_dump(mode="json"),
    )


def validation_exception_handler(
    request: Request,
    exc: RequestValidationError,
) -> JSONResponse:
    """
    Handle Pydantic validation errors.

    Args:
        request: FastAPI request object
        exc: Pydantic validation exception

    Returns:
        JSON response with grouped validation errors by field
    """
    errors = parse_validation_errors(exc)
    response = {
        "errors": errors,
    }

    return JSONResponse(
        status_code=422,
        content=response,
    )


def parse_validation_errors(exc: RequestValidationError) -> dict:
    errors = exc.errors()
    _errors = {}

    for error in errors:
        error_location = error["loc"]
        error_key = error_location[-1] if len(error_location) > 1 else error_location[0]

        message = error["msg"]

        _errors[error_key] = message
    return _errors


def register_exception_handlers(app: FastAPI):
    """
    Register all exception handlers with the FastAPI app.

    Args:
        app: FastAPI application instance
    """
    app.add_exception_handler(RequestValidationError, validation_exception_handler)
    app.add_exception_handler(AppException, app_exception_handler)
    app.add_exception_handler(Exception, generic_exception_handler)
