# Admin Panel Guide

## ✅ Admin Panel Đã Được Tạo!

### 📍 Endpoints Available

#### Dashboard
```
GET /admin/dashboard
```
Returns:
- Total strategies
- Total sessions
- Active sessions
- Total trades
- Win rate
- Total profit
- Recent trades (7 days)

#### Strategies
```
GET /admin/strategies
GET /admin/strategies?limit=50&offset=0
GET /admin/strategies/{strategy_id}
```

#### Trading Sessions
```
GET /admin/sessions
GET /admin/sessions?status=RUNNING
GET /admin/sessions?limit=50&offset=0
```

#### Trades
```
GET /admin/trades
GET /admin/trades?session_id=1
GET /admin/trades?limit=100&offset=0
```

#### Database Info
```
GET /admin/db-info
```
Returns:
- Database type (SQLite/PostgreSQL)
- File size
- Table counts
- Database location

#### Trading Statistics
```
GET /admin/stats/trading
GET /admin/stats/trading?days=30
```

---

## 🚀 Usage Examples

### Get Dashboard Stats
```bash
curl http://localhost:4000/admin/dashboard
```

### List All Strategies
```bash
curl http://localhost:4000/admin/strategies
```

### Get Strategy Details
```bash
curl http://localhost:4000/admin/strategies/1
```

### List Trading Sessions
```bash
curl http://localhost:4000/admin/sessions
```

### List Trades
```bash
curl http://localhost:4000/admin/trades
```

### Get Database Info
```bash
curl http://localhost:4000/admin/db-info
```

### Get Trading Statistics (Last 30 days)
```bash
curl http://localhost:4000/admin/stats/trading?days=30
```

---

## 🎨 Frontend Integration

### Option 1: Use Existing Frontend

Add admin pages to your React app:
- `/admin` - Dashboard
- `/admin/strategies` - Strategy list
- `/admin/sessions` - Trading sessions
- `/admin/trades` - Trade history

### Option 2: Simple HTML Page

Create a simple HTML page that calls these APIs and displays data.

### Option 3: Use SQLite Browser

For advanced users, use DB Browser for SQLite:
- Download: https://sqlitebrowser.org/
- Open: `backend/combo_optimizer.db`
- View all tables and data

---

## 📊 Response Examples

### Dashboard Response
```json
{
  "statistics": {
    "total_strategies": 4,
    "total_sessions": 2,
    "active_sessions": 1,
    "total_trades": 150,
    "win_rate": 65.5,
    "total_profit": 1250.50,
    "recent_trades_7d": 25
  },
  "timestamp": "2025-12-11T10:30:00"
}
```

### Database Info Response
```json
{
  "database_url": "./combo_optimizer.db",
  "database_type": "SQLite",
  "file_size_bytes": 245760,
  "file_size_mb": 0.23,
  "table_counts": {
    "strategies": 4,
    "sessions": 2,
    "positions": 0,
    "closed_trades": 150,
    "backtest_results": 10
  }
}
```

---

## 🔒 Security Note

**Important:** Admin endpoints are currently open. For production, add:
- Authentication
- Authorization (admin role)
- Rate limiting

Example:
```python
from fastapi import Depends, HTTPException
from fastapi.security import HTTPBearer

security = HTTPBearer()

@router.get("/admin/dashboard")
async def get_dashboard(
    token: str = Depends(security),
    db: Session = Depends(get_db)
):
    # Verify token and check admin role
    if not is_admin(token):
        raise HTTPException(403, "Admin access required")
    # ...
```

---

## 🎯 Next Steps

1. ✅ Admin API created
2. ⏳ Add authentication (optional)
3. ⏳ Create admin frontend (optional)
4. ⏳ Add export features (CSV/Excel)

---

**Status:** ✅ Admin API Ready  
**Endpoints:** 7 admin endpoints available  
**Next:** Use in frontend or test with curl/Postman

