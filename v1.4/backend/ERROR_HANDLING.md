# Error Handling System

## ✅ Implementation Complete

### Problem
- Inconsistent error handling across endpoints
- Mixed error messages (English/Vietnamese)
- No standardized error response format
- Some endpoints missing error handling
- Inconsistent logging

### Solution
Created comprehensive error handling system:

## 1. Custom Exceptions (`api/exceptions.py`)

### Base Exception
- `APIException` - Base class for all API exceptions

### Specific Exceptions
- `ValidationException` (400) - Input validation errors
- `NotFoundException` (404) - Resource not found
- `ConflictException` (409) - Resource conflicts
- `UnauthorizedException` (401) - Authentication required
- `ForbiddenException` (403) - Access denied
- `InternalServerException` (500) - Server errors
- `ExternalServiceException` (502) - External service failures
- `BadGatewayException` (502) - Gateway errors
- `ServiceUnavailableException` (503) - Service unavailable

### Usage
```python
from api.exceptions import ValidationException, NotFoundException

# Validation error
if not symbol:
    raise ValidationException("Symbol is required")

# Not found
if not strategy:
    raise NotFoundException("Strategy", name)
```

## 2. Error Handlers (`api/error_handlers.py`)

Centralized error handlers registered in `main.py`:

- `api_exception_handler` - Handles custom API exceptions
- `http_exception_handler` - Handles FastAPI HTTPException
- `validation_exception_handler` - Handles Pydantic validation errors
- `value_error_handler` - Handles ValueError
- `generic_exception_handler` - Catches all unhandled exceptions

### Error Response Format
```json
{
  "error": {
    "code": "ERROR_CODE",
    "message": "Human-readable message",
    "details": {},
    "path": "/api/endpoint"
  }
}
```

## 3. Decorators (`api/decorators.py`)

### `@handle_exceptions`
Automatically handles common exceptions:
- `ValueError` → `ValidationException`
- `KeyError` → `NotFoundException`
- Other exceptions → `InternalServerException`

### Usage
```python
from api.decorators import handle_exceptions

@router.get("/endpoint")
@handle_exceptions
async def my_endpoint():
    # No try-except needed
    return {"data": "result"}
```

## 4. Updated Routes

All routes updated to use new error handling:

### Binance Routes
- ✅ `/api/binance/symbols`
- ✅ `/api/binance/timeframes`
- ✅ `/api/binance/fetch`
- ✅ `/api/binance/symbol-info/{symbol}`

### Strategy Routes
- ✅ `/api/strategy/indicators/list`
- ✅ `/api/strategy/validate`
- ✅ `/api/strategy/preview`
- ✅ `/api/strategy/backtest`
- ✅ `/api/strategy/save`
- ✅ `/api/strategy/list`
- ✅ `/api/strategy/upload`
- ✅ `/api/strategy/load/{name}`
- ✅ `/api/strategy/delete/{name}`
- ✅ `/api/strategy/export-pine`

### Live Trading Routes
- ✅ `/api/live-trading/start`
- ✅ `/api/live-trading/status`
- ✅ `/api/live-trading/update`
- ✅ `/api/live-trading/stop`
- ✅ `/api/live-trading/pause`
- ✅ `/api/live-trading/resume`
- ✅ `/api/live-trading/close-all`

### Optimization Routes
- ✅ `/optimize-stream`
- ✅ `/generate-pine-script`

## Benefits

✅ **Consistency:**
- All errors follow same format
- Consistent status codes
- Standardized error messages

✅ **Maintainability:**
- Centralized error handling
- Easy to add new error types
- Clear error codes

✅ **Debugging:**
- All errors logged with context
- Stack traces for server errors
- Request path included

✅ **User Experience:**
- Clear error messages
- Helpful error codes
- Consistent API responses

## Error Codes

| Code | Status | Description |
|------|--------|-------------|
| `VALIDATION_ERROR` | 400 | Input validation failed |
| `UNAUTHORIZED` | 401 | Authentication required |
| `FORBIDDEN` | 403 | Access denied |
| `NOT_FOUND` | 404 | Resource not found |
| `CONFLICT` | 409 | Resource conflict |
| `INTERNAL_ERROR` | 500 | Server error |
| `EXTERNAL_SERVICE_ERROR` | 502 | External service failure |
| `BAD_GATEWAY` | 502 | Gateway error |
| `SERVICE_UNAVAILABLE` | 503 | Service unavailable |

## Examples

### Before
```python
try:
    # code
except Exception as e:
    logger.error(f"Error: {e}", exc_info=True)
    raise HTTPException(status_code=500, detail=str(e))
```

### After
```python
@handle_exceptions
async def endpoint():
    # code - exceptions handled automatically
    return result
```

Or with specific exceptions:
```python
if not resource:
    raise NotFoundException("Resource", identifier)
```

---

**Status:** ✅ Complete  
**Date:** 2025-12-11

