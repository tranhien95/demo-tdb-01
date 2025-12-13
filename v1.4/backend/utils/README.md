# Utilities

Utility modules for Combo Optimizer v1.4

## Modules

### logger.py
Centralized logging configuration and setup.

**Usage:**
```python
from utils.logger import get_logger

logger = get_logger(__name__)
logger.info("Message")
logger.error("Error", exc_info=True)
```

**Features:**
- Automatic log rotation (10MB, 5 backups)
- Separate error log file
- Console and file output
- Configurable log levels

See `LOGGING_SETUP.md` for detailed documentation.

