# Database Recommendations

## 📊 Current State

### Data Storage
- **Strategies**: JSON files in `backend/saved_strategies/`
- **Live Trading State**: JSON files in `backend/trading_data/`
- **No database**: File-based storage only

### Limitations
❌ No transaction support
❌ No query capabilities (search, filter, sort)
❌ No relationships between data
❌ No indexing (slow for large datasets)
❌ No concurrent access control
❌ Not production-ready
❌ Difficult to backup/restore
❌ No data integrity constraints

---

## 🎯 Recommendations

### Option 1: SQLite (Recommended for Start)

**Best for:**
- Development
- Small to medium scale
- Single user or small team
- Quick implementation
- No server setup needed

**Pros:**
✅ Zero configuration
✅ File-based (easy backup)
✅ ACID transactions
✅ SQL queries
✅ Good performance for small datasets
✅ Built into Python

**Cons:**
❌ Limited concurrent writes
❌ Not ideal for high traffic
❌ No network access

**Implementation:**
```python
# requirements.txt
sqlalchemy==2.0.23
alembic==1.12.1  # For migrations

# Database URL
DATABASE_URL = "sqlite:///./combo_optimizer.db"
```

**When to use:**
- MVP/Prototype
- Personal projects
- Development environment
- < 1000 strategies
- < 10 concurrent users

---

### Option 2: PostgreSQL (Recommended for Production)

**Best for:**
- Production deployments
- Multiple users
- High traffic
- Complex queries
- Data relationships

**Pros:**
✅ Production-ready
✅ Excellent performance
✅ Advanced features (JSONB, full-text search)
✅ Strong data integrity
✅ Concurrent access
✅ Scalable
✅ Network accessible

**Cons:**
❌ Requires server setup
❌ More complex configuration
❌ Higher resource usage

**Implementation:**
```python
# requirements.txt
sqlalchemy==2.0.23
alembic==1.12.1
psycopg2-binary==2.9.9  # PostgreSQL driver

# Database URL
DATABASE_URL = "postgresql://user:password@localhost/combo_optimizer"
```

**When to use:**
- Production environment
- Multiple users
- High traffic
- Need for complex queries
- Team collaboration

---

### Option 3: Hybrid Approach

**Best for:**
- Gradual migration
- Development + Production

**Strategy:**
1. Start with SQLite for development
2. Migrate to PostgreSQL for production
3. Use environment variable to switch

```python
import os
from sqlalchemy import create_engine

# Environment-based database selection
if os.getenv("ENVIRONMENT") == "production":
    DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://...")
else:
    DATABASE_URL = "sqlite:///./combo_optimizer.db"

engine = create_engine(DATABASE_URL)
```

---

## 📋 Database Schema Design

### Tables Needed

#### 1. `strategies`
```sql
CREATE TABLE strategies (
    id SERIAL PRIMARY KEY,
    name VARCHAR(100) UNIQUE NOT NULL,
    description TEXT,
    indicators JSONB NOT NULL,
    signal_logic JSONB NOT NULL,
    filters JSONB NOT NULL,
    risk_management JSONB NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_strategies_name ON strategies(name);
CREATE INDEX idx_strategies_created_at ON strategies(created_at);
```

#### 2. `live_trading_sessions`
```sql
CREATE TABLE live_trading_sessions (
    id SERIAL PRIMARY KEY,
    symbol VARCHAR(20) NOT NULL,
    timeframe VARCHAR(10) NOT NULL,
    strategy_id INTEGER REFERENCES strategies(id),
    status VARCHAR(20) NOT NULL,
    initial_balance DECIMAL(15, 2) NOT NULL,
    current_balance DECIMAL(15, 2) NOT NULL,
    equity DECIMAL(15, 2) NOT NULL,
    config JSONB NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_sessions_strategy ON live_trading_sessions(strategy_id);
CREATE INDEX idx_sessions_status ON live_trading_sessions(status);
```

#### 3. `positions`
```sql
CREATE TABLE positions (
    id SERIAL PRIMARY KEY,
    session_id INTEGER REFERENCES live_trading_sessions(id),
    symbol VARCHAR(20) NOT NULL,
    direction VARCHAR(10) NOT NULL,  -- LONG or SHORT
    entry_price DECIMAL(15, 8) NOT NULL,
    current_price DECIMAL(15, 8),
    stop_loss DECIMAL(15, 8),
    take_profit DECIMAL(15, 8),
    size DECIMAL(15, 8) NOT NULL,
    pnl DECIMAL(15, 2) DEFAULT 0,
    status VARCHAR(20) NOT NULL,  -- OPEN, CLOSED
    opened_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    closed_at TIMESTAMP
);

CREATE INDEX idx_positions_session ON positions(session_id);
CREATE INDEX idx_positions_status ON positions(status);
```

#### 4. `closed_trades`
```sql
CREATE TABLE closed_trades (
    id SERIAL PRIMARY KEY,
    session_id INTEGER REFERENCES live_trading_sessions(id),
    symbol VARCHAR(20) NOT NULL,
    direction VARCHAR(10) NOT NULL,
    entry_price DECIMAL(15, 8) NOT NULL,
    exit_price DECIMAL(15, 8) NOT NULL,
    entry_time TIMESTAMP NOT NULL,
    exit_time TIMESTAMP NOT NULL,
    profit DECIMAL(15, 2) NOT NULL,
    profit_pct DECIMAL(10, 4) NOT NULL,
    exit_reason VARCHAR(50),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_trades_session ON closed_trades(session_id);
CREATE INDEX idx_trades_exit_time ON closed_trades(exit_time);
```

#### 5. `backtest_results` (Optional - for history)
```sql
CREATE TABLE backtest_results (
    id SERIAL PRIMARY KEY,
    strategy_id INTEGER REFERENCES strategies(id),
    symbol VARCHAR(20),
    timeframe VARCHAR(10),
    start_date TIMESTAMP,
    end_date TIMESTAMP,
    total_trades INTEGER,
    win_rate DECIMAL(5, 2),
    profit_pct DECIMAL(10, 2),
    sharpe_ratio DECIMAL(10, 4),
    max_drawdown DECIMAL(10, 2),
    results JSONB,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_backtest_strategy ON backtest_results(strategy_id);
CREATE INDEX idx_backtest_created ON backtest_results(created_at);
```

---

## 🚀 Implementation Plan

### Phase 1: Setup SQLite (Quick Start)

1. **Install dependencies:**
```bash
pip install sqlalchemy alembic
```

2. **Create database models:**
```python
# backend/database/models.py
from sqlalchemy import Column, Integer, String, Text, DateTime, DECIMAL, ForeignKey, JSON
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from datetime import datetime

Base = declarative_base()

class Strategy(Base):
    __tablename__ = "strategies"
    
    id = Column(Integer, primary_key=True)
    name = Column(String(100), unique=True, nullable=False)
    description = Column(Text)
    indicators = Column(JSON, nullable=False)
    signal_logic = Column(JSON, nullable=False)
    filters = Column(JSON, nullable=False)
    risk_management = Column(JSON, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
```

3. **Create database connection:**
```python
# backend/database/connection.py
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
import os

DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./combo_optimizer.db")
engine = create_engine(DATABASE_URL, echo=True)
SessionLocal = sessionmaker(bind=engine)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
```

4. **Migrate existing JSON data:**
```python
# backend/database/migrate_json.py
from strategy_storage import strategy_storage
from database.models import Strategy
from database.connection import SessionLocal

def migrate_strategies():
    db = SessionLocal()
    try:
        strategies = strategy_storage.list_strategies()
        for strategy_item in strategies:
            strategy = strategy_storage.load_strategy(strategy_item.name)
            if strategy:
                db_strategy = Strategy(
                    name=strategy.name,
                    description=strategy.description,
                    indicators=[ind.model_dump() for ind in strategy.indicators],
                    signal_logic=strategy.signal_logic.model_dump(),
                    filters=strategy.filters.model_dump(),
                    risk_management=strategy.risk_management.model_dump()
                )
                db.add(db_strategy)
        db.commit()
    finally:
        db.close()
```

### Phase 2: Update Storage Layer

Replace `strategy_storage.py` with database-backed storage:

```python
# backend/database/strategy_repository.py
from sqlalchemy.orm import Session
from database.models import Strategy
from strategy_models import Strategy as StrategyModel

class StrategyRepository:
    def __init__(self, db: Session):
        self.db = db
    
    def save(self, strategy: StrategyModel) -> bool:
        # Implementation
        pass
    
    def load(self, name: str) -> StrategyModel:
        # Implementation
        pass
    
    def list_all(self) -> List[StrategyModel]:
        # Implementation
        pass
    
    def delete(self, name: str) -> bool:
        # Implementation
        pass
```

### Phase 3: Add Migrations (Alembic)

```bash
# Initialize Alembic
alembic init alembic

# Create migration
alembic revision --autogenerate -m "Initial schema"

# Apply migration
alembic upgrade head
```

---

## 📊 Comparison Table

| Feature | JSON Files | SQLite | PostgreSQL |
|---------|------------|--------|------------|
| Setup Complexity | ⭐ Easy | ⭐⭐ Medium | ⭐⭐⭐ Complex |
| Performance | ⭐⭐ Slow | ⭐⭐⭐ Good | ⭐⭐⭐⭐ Excellent |
| Scalability | ❌ No | ⭐⭐ Limited | ⭐⭐⭐⭐ Yes |
| Transactions | ❌ No | ✅ Yes | ✅ Yes |
| Queries | ❌ No | ✅ Yes | ✅ Yes |
| Concurrent Access | ❌ No | ⭐ Limited | ✅ Yes |
| Production Ready | ❌ No | ⭐⭐ Maybe | ✅ Yes |
| Backup | ⭐ Manual | ⭐⭐ File copy | ⭐⭐⭐⭐ pg_dump |

---

## 🎯 Recommendation

### For Your Project:

**Start with SQLite** because:
1. ✅ Quick to implement (1-2 days)
2. ✅ No server setup needed
3. ✅ Easy migration path to PostgreSQL later
4. ✅ Good for current scale
5. ✅ All SQL features available

**Migrate to PostgreSQL when:**
- Multiple users need access
- High traffic expected
- Need advanced features
- Production deployment

---

## 📝 Next Steps

1. **Decide on database** (SQLite recommended)
2. **Create database models** (see schema above)
3. **Set up SQLAlchemy** (connection, session)
4. **Create migration script** (JSON → Database)
5. **Update storage layer** (replace JSON with DB)
6. **Add Alembic** (for future migrations)
7. **Test thoroughly** (ensure data integrity)

---

**Status:** 📋 Recommendations Ready  
**Priority:** Medium (can start with SQLite)  
**Estimated Time:** 2-3 days for SQLite implementation

