"""
Initialize Database
Script to initialize database and create tables
"""

import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from database.connection import init_db, engine
from database.models import Base
from utils.logger import get_logger

logger = get_logger(__name__)


def main():
    """Initialize database"""
    print("=" * 60)
    print("Database Initialization")
    print("=" * 60)
    
    try:
        # Create all tables
        logger.info("Creating database tables...")
        init_db()
        
        # Verify tables were created
        inspector = engine.dialect.inspector(engine)
        tables = inspector.get_table_names()
        
        print(f"\n✅ Database initialized successfully!")
        print(f"\nCreated tables: {', '.join(tables)}")
        print("\nNext steps:")
        print("1. Run migration: python database/migrate_json.py")
        print("2. Update strategy_storage to use database")
        
    except Exception as e:
        logger.error(f"Failed to initialize database: {e}", exc_info=True)
        print(f"\n❌ Error: {e}")
        return False
    
    return True


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)

