"""
Custom Exceptions
Standardized exceptions for API error handling
"""

from typing import Optional, Dict, Any


class APIException(Exception):
    """Base exception for API errors"""
    def __init__(
        self,
        message: str,
        status_code: int = 500,
        error_code: Optional[str] = None,
        details: Optional[Dict[str, Any]] = None
    ):
        self.message = message
        self.status_code = status_code
        self.error_code = error_code or f"ERR_{status_code}"
        self.details = details or {}
        super().__init__(self.message)


class ValidationException(APIException):
    """Validation error (400)"""
    def __init__(self, message: str, details: Optional[Dict[str, Any]] = None):
        super().__init__(
            message=message,
            status_code=400,
            error_code="VALIDATION_ERROR",
            details=details
        )


class NotFoundException(APIException):
    """Resource not found (404)"""
    def __init__(self, resource: str, identifier: Optional[str] = None):
        message = f"{resource} not found"
        if identifier:
            message = f"{resource} '{identifier}' not found"
        super().__init__(
            message=message,
            status_code=404,
            error_code="NOT_FOUND",
            details={"resource": resource, "identifier": identifier}
        )


class ConflictException(APIException):
    """Resource conflict (409)"""
    def __init__(self, message: str, details: Optional[Dict[str, Any]] = None):
        super().__init__(
            message=message,
            status_code=409,
            error_code="CONFLICT",
            details=details
        )


class UnauthorizedException(APIException):
    """Unauthorized access (401)"""
    def __init__(self, message: str = "Unauthorized"):
        super().__init__(
            message=message,
            status_code=401,
            error_code="UNAUTHORIZED"
        )


class ForbiddenException(APIException):
    """Forbidden access (403)"""
    def __init__(self, message: str = "Forbidden"):
        super().__init__(
            message=message,
            status_code=403,
            error_code="FORBIDDEN"
        )


class InternalServerException(APIException):
    """Internal server error (500)"""
    def __init__(self, message: str = "Internal server error", details: Optional[Dict[str, Any]] = None):
        super().__init__(
            message=message,
            status_code=500,
            error_code="INTERNAL_ERROR",
            details=details
        )


class ExternalServiceException(APIException):
    """External service error (502)"""
    def __init__(self, service: str, message: Optional[str] = None):
        msg = message or f"Error connecting to {service}"
        super().__init__(
            message=msg,
            status_code=502,
            error_code="EXTERNAL_SERVICE_ERROR",
            details={"service": service}
        )


class BadGatewayException(APIException):
    """Bad gateway error (502)"""
    def __init__(self, message: str = "Bad gateway"):
        super().__init__(
            message=message,
            status_code=502,
            error_code="BAD_GATEWAY"
        )


class ServiceUnavailableException(APIException):
    """Service unavailable (503)"""
    def __init__(self, message: str = "Service unavailable"):
        super().__init__(
            message=message,
            status_code=503,
            error_code="SERVICE_UNAVAILABLE"
        )

