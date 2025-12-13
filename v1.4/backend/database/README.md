# Database Setup

## Quick Start with SQLite

### 1. Install Dependencies

```bash
pip install sqlalchemy alembic
```

### 2. Initialize Database

```python
from database.connection import init_db

# Create all tables
init_db()
```

### 3. Use in FastAPI

```python
from fastapi import Depends
from sqlalchemy.orm import Session
from database.connection import get_db

@app.get("/strategies")
async def list_strategies(db: Session = Depends(get_db)):
    strategies = db.query(Strategy).all()
    return strategies
```

## Migration from JSON

See `DATABASE_RECOMMENDATIONS.md` for migration plan.

## Switch to PostgreSQL

Set environment variable:
```bash
export DATABASE_URL="postgresql://user:password@localhost/combo_optimizer"
```

## Alembic Migrations

```bash
# Initialize (first time only)
alembic init alembic

# Create migration
alembic revision --autogenerate -m "Initial schema"

# Apply migration
alembic upgrade head
```

