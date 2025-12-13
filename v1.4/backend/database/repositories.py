"""
Database Repositories
Repository pattern for database operations
"""

from typing import List, Optional
from sqlalchemy.orm import Session
from sqlalchemy import and_
from database.models import Strategy as StrategyModel, LiveTradingSession, Position, ClosedTrade
from strategy_models import Strategy as StrategyDomain, StrategyListItem
from datetime import datetime
from utils.logger import get_logger

logger = get_logger(__name__)


class StrategyRepository:
    """Repository for Strategy operations"""
    
    def __init__(self, db: Session):
        self.db = db
    
    def save(self, strategy: StrategyDomain) -> bool:
        """
        Save or update strategy
        
        Args:
            strategy: Strategy domain model
            
        Returns:
            True if successful
        """
        try:
            # Check if strategy exists
            db_strategy = self.db.query(StrategyModel).filter(
                StrategyModel.name == strategy.name
            ).first()
            
            now = datetime.utcnow()
            
            if db_strategy:
                # Update existing
                db_strategy.description = strategy.description
                db_strategy.indicators = [ind.model_dump() for ind in strategy.indicators]
                db_strategy.signal_logic = strategy.signal_logic.model_dump()
                db_strategy.filters = strategy.filters.model_dump()
                db_strategy.risk_management = strategy.risk_management.model_dump()
                db_strategy.updated_at = now
                logger.info(f"Strategy updated: {strategy.name}")
            else:
                # Create new
                db_strategy = StrategyModel(
                    name=strategy.name,
                    description=strategy.description,
                    indicators=[ind.model_dump() for ind in strategy.indicators],
                    signal_logic=strategy.signal_logic.model_dump(),
                    filters=strategy.filters.model_dump(),
                    risk_management=strategy.risk_management.model_dump(),
                    created_at=now,
                    updated_at=now
                )
                self.db.add(db_strategy)
                logger.info(f"Strategy created: {strategy.name}")
            
            self.db.commit()
            return True
            
        except Exception as e:
            self.db.rollback()
            logger.error(f"Error saving strategy '{strategy.name}': {e}", exc_info=True)
            return False
    
    def load(self, name: str) -> Optional[StrategyDomain]:
        """
        Load strategy by name
        
        Args:
            name: Strategy name
            
        Returns:
            Strategy domain model or None
        """
        try:
            db_strategy = self.db.query(StrategyModel).filter(
                StrategyModel.name == name
            ).first()
            
            if not db_strategy:
                return None
            
            # Convert to domain model
            from strategy_models import IndicatorConfig, SignalLogic, FilterConfig, RiskManagement
            
            strategy = StrategyDomain(
                name=db_strategy.name,
                description=db_strategy.description,
                indicators=[
                    IndicatorConfig(**ind) for ind in db_strategy.indicators
                ],
                signal_logic=SignalLogic(**db_strategy.signal_logic),
                filters=FilterConfig(**db_strategy.filters),
                risk_management=RiskManagement(**db_strategy.risk_management),
                created_at=db_strategy.created_at,
                updated_at=db_strategy.updated_at
            )
            
            logger.info(f"Strategy loaded: {name}")
            return strategy
            
        except Exception as e:
            logger.error(f"Error loading strategy '{name}': {e}", exc_info=True)
            return None
    
    def list_all(self) -> List[StrategyListItem]:
        """
        List all strategies
        
        Returns:
            List of strategy list items
        """
        try:
            db_strategies = self.db.query(StrategyModel).order_by(
                StrategyModel.updated_at.desc()
            ).all()
            
            strategies = []
            for db_strategy in db_strategies:
                strategies.append(StrategyListItem(
                    name=db_strategy.name,
                    description=db_strategy.description,
                    indicator_count=len(db_strategy.indicators),
                    created_at=db_strategy.created_at,
                    updated_at=db_strategy.updated_at
                ))
            
            return strategies
            
        except Exception as e:
            logger.error(f"Error listing strategies: {e}", exc_info=True)
            return []
    
    def delete(self, name: str) -> bool:
        """
        Delete strategy by name
        
        Args:
            name: Strategy name
            
        Returns:
            True if successful
        """
        try:
            db_strategy = self.db.query(StrategyModel).filter(
                StrategyModel.name == name
            ).first()
            
            if not db_strategy:
                return False
            
            self.db.delete(db_strategy)
            self.db.commit()
            
            logger.info(f"Strategy deleted: {name}")
            return True
            
        except Exception as e:
            self.db.rollback()
            logger.error(f"Error deleting strategy '{name}': {e}", exc_info=True)
            return False
    
    def exists(self, name: str) -> bool:
        """Check if strategy exists"""
        return self.db.query(StrategyModel).filter(
            StrategyModel.name == name
        ).first() is not None


class LiveTradingRepository:
    """Repository for Live Trading operations"""
    
    def __init__(self, db: Session):
        self.db = db
    
    def save_session(self, session_data: dict) -> Optional[int]:
        """
        Save live trading session
        
        Args:
            session_data: Session data dictionary
            
        Returns:
            Session ID or None
        """
        try:
            # Implementation for saving trading sessions
            # This would be called from live_trading_engine
            pass
        except Exception as e:
            logger.error(f"Error saving trading session: {e}", exc_info=True)
            return None
    
    def load_session(self, session_id: int) -> Optional[dict]:
        """Load trading session by ID"""
        try:
            # Implementation for loading sessions
            pass
        except Exception as e:
            logger.error(f"Error loading session {session_id}: {e}", exc_info=True)
            return None

