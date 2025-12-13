# Logging System Setup

## ✅ Implementation Complete

### 1. Logger Module Created
- **Location:** `backend/utils/logger.py`
- **Features:**
  - File logging with rotation (10MB per file, 5 backups)
  - Separate error log file
  - Console output (optional)
  - Configurable log levels
  - Automatic log directory creation

### 2. Log Files Structure
```
backend/logs/
├── app.log          # All logs (INFO, WARNING, ERROR, etc.)
├── app.log.1        # Rotated backups
├── error.log        # Only ERROR and CRITICAL
└── error.log.1      # Rotated backups
```

### 3. Code Updates

#### Files Updated:
- ✅ `backend/main.py` - Replaced all print() with logger
- ✅ `backend/strategy_storage.py` - Replaced all print() with logger
- ✅ `backend/indicators/base.py` - Replaced print() with logger

#### Changes Made:
- Removed DEBUG print statements
- Replaced error print() with logger.error()
- Replaced info print() with logger.info()
- Added proper exception logging with exc_info=True

### 4. Usage

#### Basic Usage:
```python
from utils.logger import get_logger

logger = get_logger(__name__)

# Log levels
logger.debug("Debug message")
logger.info("Info message")
logger.warning("Warning message")
logger.error("Error message")
logger.critical("Critical message")

# With exception info
try:
    # code
except Exception as e:
    logger.error(f"Error occurred: {e}", exc_info=True)
```

#### In Different Modules:
```python
# Each module gets its own logger
from utils.logger import get_logger

logger = get_logger(__name__)  # Uses module name automatically

logger.info("Module-specific log message")
```

### 5. Log Levels

| Level | Usage | Example |
|-------|-------|---------|
| DEBUG | Detailed debugging info | Request body details |
| INFO | General information | Strategy saved, backtest started |
| WARNING | Warning messages | Invalid file format |
| ERROR | Error messages | Failed to save strategy |
| CRITICAL | Critical errors | System failure |

### 6. Configuration

#### Default Settings:
- **Log Level:** INFO
- **Console Output:** Enabled
- **Log Directory:** `backend/logs/`
- **Max File Size:** 10MB
- **Backup Count:** 5

#### Custom Configuration:
```python
from utils.logger import setup_logger
from pathlib import Path

# Custom logger
logger = setup_logger(
    name="my_module",
    log_level="DEBUG",  # More verbose
    log_dir=Path("custom/logs"),
    console_output=False  # No console output
)
```

### 7. Environment Variables (Future)

Can be extended to use environment variables:
```python
import os
log_level = os.getenv("LOG_LEVEL", "INFO")
console_output = os.getenv("LOG_CONSOLE", "true").lower() == "true"
```

### 8. Log Rotation

Logs automatically rotate when they reach 10MB:
- `app.log` → `app.log.1` → `app.log.2` → ... → `app.log.5`
- Oldest logs are deleted when limit reached

### 9. Benefits

✅ **Production Ready:**
- No more print() statements in production
- Proper log levels for filtering
- Log rotation prevents disk fill

✅ **Debugging:**
- Stack traces with exc_info=True
- Timestamps and function names
- Separate error log for quick access

✅ **Monitoring:**
- Can integrate with log aggregation tools
- Structured logging ready
- Easy to parse and analyze

### 10. Next Steps (Optional)

1. **Add structured logging:**
   ```python
   import json
   logger.info("Event", extra={"event_type": "backtest", "strategy": "RSI"})
   ```

2. **Add log aggregation:**
   - Send logs to external service (e.g., ELK, Splunk)
   - Use logging handlers for remote logging

3. **Add request ID tracking:**
   ```python
   # Add request ID to all logs in a request
   logger = get_logger(__name__)
   logger = logger.bind(request_id=request_id)
   ```

---

**Status:** ✅ Complete  
**Date:** 2025-12-11

