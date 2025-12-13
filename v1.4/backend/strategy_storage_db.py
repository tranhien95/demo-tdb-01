"""
Strategy Storage - Database Backend
Database-backed strategy storage using SQLAlchemy
"""

from typing import List, Optional
from datetime import datetime
from strategy_models import Strategy, StrategyListItem
from database.connection import get_db_session
from database.repositories import StrategyRepository
from utils.logger import get_logger

logger = get_logger(__name__)


class StrategyStorage:
    """Handle strategy persistence using database"""
    
    def save_strategy(self, strategy: Strategy) -> bool:
        """
        Save strategy to database
        
        Returns:
            True if successful
        """
        db = get_db_session()
        try:
            repo = StrategyRepository(db)
            return repo.save(strategy)
        finally:
            db.close()
    
    def load_strategy(self, name: str) -> Optional[Strategy]:
        """
        Load strategy from database
        
        Args:
            name: Strategy name
            
        Returns:
            Strategy object or None if not found
        """
        db = get_db_session()
        try:
            repo = StrategyRepository(db)
            return repo.load(name)
        finally:
            db.close()
    
    def list_strategies(self) -> List[StrategyListItem]:
        """
        List all saved strategies
        
        Returns:
            List of strategy metadata
        """
        db = get_db_session()
        try:
            repo = StrategyRepository(db)
            return repo.list_all()
        finally:
            db.close()
    
    def delete_strategy(self, name: str) -> bool:
        """
        Delete a strategy
        
        Args:
            name: Strategy name
            
        Returns:
            True if successful
        """
        db = get_db_session()
        try:
            repo = StrategyRepository(db)
            return repo.delete(name)
        finally:
            db.close()


# Global instance
strategy_storage = StrategyStorage()

