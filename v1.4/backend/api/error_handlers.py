"""
Error Handlers
Centralized error handling for FastAPI
"""

from fastapi import Request, HTTPException
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from pydantic import ValidationError
from api.exceptions import APIException
from utils.logger import get_logger

logger = get_logger(__name__)


async def api_exception_handler(request: Request, exc: APIException) -> JSONResponse:
    """Handle custom API exceptions"""
    logger.error(
        f"API Exception: {exc.error_code} - {exc.message}",
        extra={
            "status_code": exc.status_code,
            "error_code": exc.error_code,
            "details": exc.details,
            "path": request.url.path
        }
    )
    
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "error": {
                "code": exc.error_code,
                "message": exc.message,
                "details": exc.details,
                "path": request.url.path
            }
        }
    )


async def http_exception_handler(request: Request, exc: HTTPException) -> JSONResponse:
    """Handle FastAPI HTTPException"""
    status_code = exc.status_code
    detail = exc.detail
    
    # Map status codes to error codes
    error_code_map = {
        400: "BAD_REQUEST",
        401: "UNAUTHORIZED",
        403: "FORBIDDEN",
        404: "NOT_FOUND",
        409: "CONFLICT",
        422: "VALIDATION_ERROR",
        500: "INTERNAL_ERROR",
        502: "BAD_GATEWAY",
        503: "SERVICE_UNAVAILABLE"
    }
    
    error_code = error_code_map.get(status_code, "HTTP_ERROR")
    
    # Log based on status code
    if status_code >= 500:
        logger.error(
            f"HTTP Exception: {error_code} - {detail}",
            extra={"status_code": status_code, "path": request.url.path},
            exc_info=True
        )
    elif status_code >= 400:
        logger.warning(
            f"HTTP Exception: {error_code} - {detail}",
            extra={"status_code": status_code, "path": request.url.path}
        )
    
    return JSONResponse(
        status_code=status_code,
        content={
            "error": {
                "code": error_code,
                "message": str(detail),
                "path": request.url.path
            }
        }
    )


async def validation_exception_handler(request: Request, exc: RequestValidationError) -> JSONResponse:
    """Handle Pydantic validation errors"""
    errors = exc.errors()
    error_messages = []
    
    for error in errors:
        field = ".".join(str(loc) for loc in error.get("loc", []))
        message = error.get("msg", "Validation error")
        error_messages.append(f"{field}: {message}")
    
    error_message = "; ".join(error_messages)
    
    logger.warning(
        f"Validation error: {error_message}",
        extra={"path": request.url.path, "errors": errors}
    )
    
    return JSONResponse(
        status_code=422,
        content={
            "error": {
                "code": "VALIDATION_ERROR",
                "message": "Request validation failed",
                "details": {
                    "errors": errors,
                    "messages": error_messages
                },
                "path": request.url.path
            }
        }
    )


async def value_error_handler(request: Request, exc: ValueError) -> JSONResponse:
    """Handle ValueError exceptions"""
    logger.warning(
        f"Value error: {str(exc)}",
        extra={"path": request.url.path}
    )
    
    return JSONResponse(
        status_code=400,
        content={
            "error": {
                "code": "VALIDATION_ERROR",
                "message": str(exc),
                "path": request.url.path
            }
        }
    )


async def generic_exception_handler(request: Request, exc: Exception) -> JSONResponse:
    """Handle all other unhandled exceptions"""
    logger.error(
        f"Unhandled exception: {type(exc).__name__} - {str(exc)}",
        extra={"path": request.url.path},
        exc_info=True
    )
    
    return JSONResponse(
        status_code=500,
        content={
            "error": {
                "code": "INTERNAL_ERROR",
                "message": "An unexpected error occurred",
                "path": request.url.path
            }
        }
    )

