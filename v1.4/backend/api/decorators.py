"""
API Decorators
Decorators for common API patterns
"""

from functools import wraps
from typing import Callable, Any
from fastapi import HTTPException
from api.exceptions import (
    APIException,
    ValidationException,
    NotFoundException,
    InternalServerException,
    ExternalServiceException
)
from utils.logger import get_logger

logger = get_logger(__name__)


def handle_exceptions(func: Callable) -> Callable:
    """
    Decorator to handle exceptions consistently
    
    Usage:
        @handle_exceptions
        async def my_endpoint():
            ...
    """
    @wraps(func)
    async def wrapper(*args, **kwargs):
        try:
            return await func(*args, **kwargs)
        except APIException:
            # Re-raise API exceptions (they're already handled)
            raise
        except HTTPException:
            # Re-raise HTTP exceptions (they're already handled)
            raise
        except ValueError as e:
            # Convert ValueError to ValidationException
            raise ValidationException(str(e))
        except KeyError as e:
            raise NotFoundException("Resource", str(e))
        except Exception as e:
            # Log unexpected errors
            logger.error(
                f"Unexpected error in {func.__name__}: {e}",
                exc_info=True
            )
            raise InternalServerException(
                f"An unexpected error occurred: {str(e)}"
            )
    
    return wrapper


def validate_input(validator: Callable[[Any], bool], error_message: str = "Invalid input"):
    """
    Decorator to validate function input
    
    Usage:
        @validate_input(lambda x: x > 0, "Value must be positive")
        async def my_endpoint(value: int):
            ...
    """
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        async def wrapper(*args, **kwargs):
            # Validate all arguments
            for arg in args:
                if not validator(arg):
                    raise ValidationException(error_message)
            for value in kwargs.values():
                if not validator(value):
                    raise ValidationException(error_message)
            return await func(*args, **kwargs)
        return wrapper
    return decorator

