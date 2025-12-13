"""
Database Models
SQLAlchemy models for Combo Optimizer
"""

from sqlalchemy import Column, Integer, String, Text, DateTime, DECIMAL, ForeignKey, JSON, Index
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from datetime import datetime

Base = declarative_base()


class Strategy(Base):
    """Strategy table"""
    __tablename__ = "strategies"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), unique=True, nullable=False, index=True)
    description = Column(Text)
    indicators = Column(JSON, nullable=False)
    signal_logic = Column(JSON, nullable=False)
    filters = Column(JSON, nullable=False)
    risk_management = Column(JSON, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    
    # Relationships
    trading_sessions = relationship("LiveTradingSession", back_populates="strategy")
    backtest_results = relationship("BacktestResult", back_populates="strategy")
    
    __table_args__ = (
        Index('idx_strategies_created_at', 'created_at'),
        Index('idx_strategies_updated_at', 'updated_at'),
    )


class LiveTradingSession(Base):
    """Live trading session table"""
    __tablename__ = "live_trading_sessions"
    
    id = Column(Integer, primary_key=True, index=True)
    strategy_id = Column(Integer, ForeignKey("strategies.id"), nullable=False)
    symbol = Column(String(20), nullable=False, index=True)
    timeframe = Column(String(10), nullable=False)
    status = Column(String(20), nullable=False, index=True)  # RUNNING, PAUSED, STOPPED
    initial_balance = Column(DECIMAL(15, 2), nullable=False)
    current_balance = Column(DECIMAL(15, 2), nullable=False)
    equity = Column(DECIMAL(15, 2), nullable=False)
    config = Column(JSON, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    last_updated = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    
    # Relationships
    strategy = relationship("Strategy", back_populates="trading_sessions")
    positions = relationship("Position", back_populates="session", cascade="all, delete-orphan")
    closed_trades = relationship("ClosedTrade", back_populates="session", cascade="all, delete-orphan")
    
    __table_args__ = (
        Index('idx_sessions_strategy', 'strategy_id'),
        Index('idx_sessions_status', 'status'),
        Index('idx_sessions_created', 'created_at'),
    )


class Position(Base):
    """Open position table"""
    __tablename__ = "positions"
    
    id = Column(Integer, primary_key=True, index=True)
    session_id = Column(Integer, ForeignKey("live_trading_sessions.id"), nullable=False)
    symbol = Column(String(20), nullable=False)
    direction = Column(String(10), nullable=False)  # LONG or SHORT
    entry_price = Column(DECIMAL(15, 8), nullable=False)
    current_price = Column(DECIMAL(15, 8))
    stop_loss = Column(DECIMAL(15, 8))
    take_profit = Column(DECIMAL(15, 8))
    size = Column(DECIMAL(15, 8), nullable=False)
    pnl = Column(DECIMAL(15, 2), default=0)
    status = Column(String(20), nullable=False, index=True)  # OPEN, CLOSED
    opened_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    closed_at = Column(DateTime)
    
    # Relationships
    session = relationship("LiveTradingSession", back_populates="positions")
    
    __table_args__ = (
        Index('idx_positions_session', 'session_id'),
        Index('idx_positions_status', 'status'),
    )


class ClosedTrade(Base):
    """Closed trade history table"""
    __tablename__ = "closed_trades"
    
    id = Column(Integer, primary_key=True, index=True)
    session_id = Column(Integer, ForeignKey("live_trading_sessions.id"), nullable=False)
    symbol = Column(String(20), nullable=False)
    direction = Column(String(10), nullable=False)
    entry_price = Column(DECIMAL(15, 8), nullable=False)
    exit_price = Column(DECIMAL(15, 8), nullable=False)
    entry_time = Column(DateTime, nullable=False)
    exit_time = Column(DateTime, nullable=False, index=True)
    profit = Column(DECIMAL(15, 2), nullable=False)
    profit_pct = Column(DECIMAL(10, 4), nullable=False)
    exit_reason = Column(String(50))
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    
    # Relationships
    session = relationship("LiveTradingSession", back_populates="closed_trades")
    
    __table_args__ = (
        Index('idx_trades_session', 'session_id'),
        Index('idx_trades_exit_time', 'exit_time'),
    )


class BacktestResult(Base):
    """Backtest result history table"""
    __tablename__ = "backtest_results"
    
    id = Column(Integer, primary_key=True, index=True)
    strategy_id = Column(Integer, ForeignKey("strategies.id"), nullable=False)
    symbol = Column(String(20))
    timeframe = Column(String(10))
    start_date = Column(DateTime)
    end_date = Column(DateTime)
    total_trades = Column(Integer)
    win_rate = Column(DECIMAL(5, 2))
    profit_pct = Column(DECIMAL(10, 2))
    sharpe_ratio = Column(DECIMAL(10, 4))
    max_drawdown = Column(DECIMAL(10, 2))
    results = Column(JSON)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False, index=True)
    
    # Relationships
    strategy = relationship("Strategy", back_populates="backtest_results")
    
    __table_args__ = (
        Index('idx_backtest_strategy', 'strategy_id'),
        Index('idx_backtest_created', 'created_at'),
    )

