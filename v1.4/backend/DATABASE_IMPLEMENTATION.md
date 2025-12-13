# Database Implementation Guide

## ✅ Implementation Complete

### Files Created

1. **`database/models.py`** - SQLAlchemy models
   - Strategy, LiveTradingSession, Position, ClosedTrade, BacktestResult

2. **`database/connection.py`** - Database connection & session management
   - SQLite default, PostgreSQL support via env var

3. **`database/repositories.py`** - Repository pattern
   - StrategyRepository for strategy operations

4. **`database/migrate_json.py`** - Migration script
   - Migrates JSON files to database

5. **`database/init_database.py`** - Database initialization
   - Creates all tables

6. **`strategy_storage_db.py`** - Database-backed storage
   - Drop-in replacement for JSON storage

---

## 🚀 Quick Start

### Step 1: Install Dependencies

```bash
cd backend
pip install -r requirements.txt
```

This installs:
- `sqlalchemy==2.0.23`
- `alembic==1.12.1`

### Step 2: Initialize Database

```bash
python database/init_database.py
```

This creates:
- `combo_optimizer.db` (SQLite database file)
- All required tables

### Step 3: Migrate Existing Data

```bash
python database/migrate_json.py
```

This migrates:
- All strategies from `saved_strategies/*.json` to database
- Verifies migration success

### Step 4: Switch to Database Storage

**Option A: Replace storage (Recommended)**

```python
# In api/routes/strategy.py and other files
# Change from:
from strategy_storage import strategy_storage

# To:
from strategy_storage_db import strategy_storage
```

**Option B: Use environment variable**

```python
import os

if os.getenv("USE_DATABASE", "false").lower() == "true":
    from strategy_storage_db import strategy_storage
else:
    from strategy_storage import strategy_storage
```

---

## 📊 Database Schema

### Tables Created

1. **strategies**
   - id, name, description
   - indicators (JSONB)
   - signal_logic, filters, risk_management (JSONB)
   - created_at, updated_at

2. **live_trading_sessions**
   - id, strategy_id, symbol, timeframe
   - status, balance, equity
   - config (JSONB)
   - created_at, last_updated

3. **positions**
   - id, session_id, symbol, direction
   - entry_price, current_price, stop_loss, take_profit
   - size, pnl, status
   - opened_at, closed_at

4. **closed_trades**
   - id, session_id, symbol, direction
   - entry_price, exit_price
   - profit, profit_pct, exit_reason
   - entry_time, exit_time

5. **backtest_results**
   - id, strategy_id, symbol, timeframe
   - total_trades, win_rate, profit_pct
   - sharpe_ratio, max_drawdown
   - results (JSONB)

---

## 🔄 Migration Process

### Before Migration

```
backend/
├── saved_strategies/
│   ├── RSI_Strategy.json
│   ├── MACD_Strategy.json
│   └── ...
```

### After Migration

```
backend/
├── combo_optimizer.db  (SQLite database)
├── saved_strategies/   (backup - can be removed)
└── database/
    ├── models.py
    ├── connection.py
    └── repositories.py
```

### Migration Steps

1. **Backup JSON files** (optional but recommended)
   ```bash
   cp -r saved_strategies saved_strategies_backup
   ```

2. **Run migration**
   ```bash
   python database/migrate_json.py
   ```

3. **Verify migration**
   - Check migration output
   - Verify counts match
   - Test loading strategies

4. **Switch to database**
   - Update imports
   - Test thoroughly
   - Keep JSON files as backup

---

## 🔧 Configuration

### SQLite (Default)

No configuration needed. Database file created automatically:
- Location: `backend/combo_optimizer.db`
- File-based, easy to backup

### PostgreSQL (Production)

Set environment variable:
```bash
export DATABASE_URL="postgresql://user:password@localhost/combo_optimizer"
```

Or in `.env`:
```
DATABASE_URL=postgresql://user:password@localhost/combo_optimizer
```

### Enable SQL Debugging

```bash
export SQL_DEBUG=true
```

Shows all SQL queries in logs.

---

## 📝 Usage Examples

### Save Strategy

```python
from strategy_storage_db import strategy_storage
from strategy_models import Strategy, IndicatorConfig

strategy = Strategy(
    name="My Strategy",
    indicators=[IndicatorConfig(type="RSI", config={"period": 14})],
    # ... other fields
)

success = strategy_storage.save_strategy(strategy)
```

### Load Strategy

```python
strategy = strategy_storage.load_strategy("My Strategy")
```

### List Strategies

```python
strategies = strategy_storage.list_strategies()
for item in strategies:
    print(f"{item.name} - {item.indicator_count} indicators")
```

### Delete Strategy

```python
success = strategy_storage.delete_strategy("My Strategy")
```

---

## 🧪 Testing

### Test Database Connection

```python
from database.connection import get_db_session
from database.models import Strategy

db = get_db_session()
try:
    count = db.query(Strategy).count()
    print(f"Strategies in database: {count}")
finally:
    db.close()
```

### Test Migration

```python
from database.migrate_json import migrate_strategies, verify_migration

# Run migration
migrate_strategies()

# Verify
verify_migration()
```

---

## 🔄 Rollback Plan

If you need to rollback to JSON storage:

1. **Keep JSON files** (don't delete immediately)
2. **Revert imports** to use `strategy_storage` instead of `strategy_storage_db`
3. **Database file** can be kept or deleted

---

## 📈 Next Steps

1. ✅ Database models created
2. ✅ Migration script ready
3. ✅ Repository layer implemented
4. ⏳ Run migration
5. ⏳ Update imports to use database
6. ⏳ Test thoroughly
7. ⏳ Add Alembic for future migrations
8. ⏳ Consider adding indexes for performance

---

## 🎯 Benefits Achieved

✅ **Transactions** - Data integrity guaranteed
✅ **Queries** - Search, filter, sort capabilities
✅ **Relationships** - Link strategies with trades
✅ **Performance** - Indexed queries
✅ **Scalability** - Ready for production
✅ **Backup** - Easy database backup

---

**Status:** ✅ Ready to Use  
**Next:** Run `python database/init_database.py` then `python database/migrate_json.py`

