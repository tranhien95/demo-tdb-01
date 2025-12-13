# Chuyển Sang Dùng Database

## ✅ Database Đã Sẵn Sàng!

Database đã được setup và migrate data từ JSON. Bây giờ cần chuyển code sang dùng database.

---

## 🔄 Cách Chuyển

### Option 1: Thay Đổi Import (Recommended)

Tìm và thay đổi trong các files:

**Files cần update:**
1. `backend/api/routes/strategy.py`
2. `backend/live_trading_engine.py`

**Thay đổi:**
```python
# Từ:
from strategy_storage import strategy_storage

# Sang:
from strategy_storage_db import strategy_storage
```

### Option 2: Environment Variable (Flexible)

Tạo file `backend/config.py`:
```python
import os

USE_DATABASE = os.getenv("USE_DATABASE", "true").lower() == "true"

if USE_DATABASE:
    from strategy_storage_db import strategy_storage
else:
    from strategy_storage import strategy_storage
```

Rồi import từ config:
```python
from config import strategy_storage
```

---

## 📝 Files Cần Update

### 1. `backend/api/routes/strategy.py`
Line 11:
```python
# Change from:
from strategy_storage import strategy_storage

# To:
from strategy_storage_db import strategy_storage
```

### 2. `backend/live_trading_engine.py`
Line 14:
```python
# Change from:
from strategy_storage import strategy_storage

# To:
from strategy_storage_db import strategy_storage
```

---

## ✅ Verify

Sau khi update, test:

```bash
# Start server
python main.py

# Test endpoint
curl http://localhost:4000/api/strategy/list
```

Nếu thấy strategies → ✅ Database đang hoạt động!

---

## 🔙 Rollback (Nếu Cần)

Nếu có vấn đề, có thể rollback về JSON:

```python
# Change back to:
from strategy_storage import strategy_storage
```

Database vẫn giữ nguyên, có thể dùng lại sau.

---

**Status:** ✅ Ready to switch  
**Next:** Update imports in strategy.py and live_trading_engine.py

