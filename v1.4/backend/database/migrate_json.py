"""
Migration Script
Migrate data from JSON files to database
"""

import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from database.connection import init_db, get_db_session
from database.repositories import StrategyRepository
from strategy_storage import strategy_storage
from utils.logger import get_logger

logger = get_logger(__name__)


def migrate_strategies():
    """Migrate strategies from JSON files to database"""
    logger.info("Starting strategy migration from JSON to database...")
    
    # Initialize database
    try:
        init_db()
        logger.info("Database initialized")
    except Exception as e:
        logger.error(f"Failed to initialize database: {e}", exc_info=True)
        return False
    
    # Get database session
    db = get_db_session()
    repo = StrategyRepository(db)
    
    try:
        # Load all strategies from JSON files
        strategy_items = strategy_storage.list_strategies()
        
        if not strategy_items:
            logger.info("No strategies found in JSON files")
            return True
        
        logger.info(f"Found {len(strategy_items)} strategies to migrate")
        
        migrated = 0
        skipped = 0
        errors = 0
        
        for item in strategy_items:
            try:
                # Check if already exists in database
                if repo.exists(item.name):
                    logger.warning(f"Strategy '{item.name}' already exists in database, skipping")
                    skipped += 1
                    continue
                
                # Load from JSON
                strategy = strategy_storage.load_strategy(item.name)
                
                if not strategy:
                    logger.warning(f"Could not load strategy '{item.name}' from JSON")
                    errors += 1
                    continue
                
                # Save to database
                if repo.save(strategy):
                    migrated += 1
                    logger.info(f"Migrated: {item.name}")
                else:
                    errors += 1
                    logger.error(f"Failed to migrate: {item.name}")
                    
            except Exception as e:
                logger.error(f"Error migrating strategy '{item.name}': {e}", exc_info=True)
                errors += 1
        
        logger.info(f"Migration complete: {migrated} migrated, {skipped} skipped, {errors} errors")
        return errors == 0
        
    except Exception as e:
        logger.error(f"Migration failed: {e}", exc_info=True)
        return False
    finally:
        db.close()


def verify_migration():
    """Verify migration by comparing counts"""
    logger.info("Verifying migration...")
    
    # Count JSON strategies
    json_strategies = strategy_storage.list_strategies()
    json_count = len(json_strategies)
    
    # Count database strategies
    db = get_db_session()
    repo = StrategyRepository(db)
    
    try:
        db_strategies = repo.list_all()
        db_count = len(db_strategies)
        
        logger.info(f"JSON strategies: {json_count}")
        logger.info(f"Database strategies: {db_count}")
        
        if json_count == db_count:
            logger.info("✅ Migration verified: Counts match")
            return True
        else:
            logger.warning(f"⚠️ Migration mismatch: JSON={json_count}, DB={db_count}")
            return False
    finally:
        db.close()


if __name__ == "__main__":
    print("=" * 60)
    print("JSON to Database Migration")
    print("=" * 60)
    
    # Run migration
    success = migrate_strategies()
    
    if success:
        # Verify
        verify_migration()
        print("\n✅ Migration completed successfully!")
        print("\nNext steps:")
        print("1. Test the application with database")
        print("2. Update strategy_storage.py to use database")
        print("3. Backup JSON files before removing")
    else:
        print("\n❌ Migration failed. Check logs for details.")

