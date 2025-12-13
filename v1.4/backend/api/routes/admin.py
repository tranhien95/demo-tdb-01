"""
Admin Routes
Admin panel endpoints for database management and monitoring
"""

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import func, desc
from typing import Dict, Any, List
from datetime import datetime, timedelta
from database.connection import get_db
from database.models import (
    Strategy, LiveTradingSession, Position, 
    ClosedTrade, BacktestResult
)
from api.exceptions import NotFoundException
from api.decorators import handle_exceptions
from utils.logger import get_logger

logger = get_logger(__name__)

router = APIRouter(prefix="/admin", tags=["admin"])


@router.get("/dashboard")
@handle_exceptions
async def get_dashboard(db: Session = Depends(get_db)) -> Dict[str, Any]:
    """Get admin dashboard statistics"""
    
    # Count strategies
    total_strategies = db.query(Strategy).count()
    
    # Count trading sessions
    total_sessions = db.query(LiveTradingSession).count()
    active_sessions = db.query(LiveTradingSession).filter(
        LiveTradingSession.status == "RUNNING"
    ).count()
    
    # Count trades
    total_trades = db.query(ClosedTrade).count()
    
    # Calculate win rate
    winning_trades = db.query(ClosedTrade).filter(
        ClosedTrade.profit > 0
    ).count()
    win_rate = (winning_trades / total_trades * 100) if total_trades > 0 else 0
    
    # Calculate total profit
    total_profit_result = db.query(func.sum(ClosedTrade.profit)).scalar()
    total_profit = float(total_profit_result) if total_profit_result else 0.0
    
    # Recent activity (last 7 days)
    seven_days_ago = datetime.utcnow() - timedelta(days=7)
    recent_trades = db.query(ClosedTrade).filter(
        ClosedTrade.exit_time >= seven_days_ago
    ).count()
    
    return {
        "statistics": {
            "total_strategies": total_strategies,
            "total_sessions": total_sessions,
            "active_sessions": active_sessions,
            "total_trades": total_trades,
            "win_rate": round(win_rate, 2),
            "total_profit": round(total_profit, 2),
            "recent_trades_7d": recent_trades
        },
        "timestamp": datetime.utcnow().isoformat()
    }


@router.get("/strategies")
@handle_exceptions
async def list_all_strategies(
    db: Session = Depends(get_db),
    limit: int = 100,
    offset: int = 0
) -> Dict[str, Any]:
    """List all strategies with details"""
    
    total = db.query(Strategy).count()
    strategies = db.query(Strategy).order_by(
        desc(Strategy.updated_at)
    ).offset(offset).limit(limit).all()
    
    result = []
    for strategy in strategies:
        # Count related sessions
        session_count = db.query(LiveTradingSession).filter(
            LiveTradingSession.strategy_id == strategy.id
        ).count()
        
        result.append({
            "id": strategy.id,
            "name": strategy.name,
            "description": strategy.description,
            "indicator_count": len(strategy.indicators),
            "session_count": session_count,
            "created_at": strategy.created_at.isoformat(),
            "updated_at": strategy.updated_at.isoformat()
        })
    
    return {
        "total": total,
        "limit": limit,
        "offset": offset,
        "strategies": result
    }


@router.get("/strategies/{strategy_id}")
@handle_exceptions
async def get_strategy_details(
    strategy_id: int,
    db: Session = Depends(get_db)
) -> Dict[str, Any]:
    """Get detailed strategy information"""
    
    strategy = db.query(Strategy).filter(Strategy.id == strategy_id).first()
    
    if not strategy:
        raise NotFoundException("Strategy", str(strategy_id))
    
    # Get related sessions
    sessions = db.query(LiveTradingSession).filter(
        LiveTradingSession.strategy_id == strategy_id
    ).all()
    
    # Get backtest results
    backtests = db.query(BacktestResult).filter(
        BacktestResult.strategy_id == strategy_id
    ).order_by(desc(BacktestResult.created_at)).limit(10).all()
    
    return {
        "id": strategy.id,
        "name": strategy.name,
        "description": strategy.description,
        "indicators": strategy.indicators,
        "signal_logic": strategy.signal_logic,
        "filters": strategy.filters,
        "risk_management": strategy.risk_management,
        "created_at": strategy.created_at.isoformat(),
        "updated_at": strategy.updated_at.isoformat(),
        "sessions": [
            {
                "id": s.id,
                "symbol": s.symbol,
                "timeframe": s.timeframe,
                "status": s.status,
                "created_at": s.created_at.isoformat()
            }
            for s in sessions
        ],
        "recent_backtests": [
            {
                "id": b.id,
                "symbol": b.symbol,
                "timeframe": b.timeframe,
                "win_rate": float(b.win_rate) if b.win_rate else None,
                "profit_pct": float(b.profit_pct) if b.profit_pct else None,
                "created_at": b.created_at.isoformat()
            }
            for b in backtests
        ]
    }


@router.get("/sessions")
@handle_exceptions
async def list_sessions(
    db: Session = Depends(get_db),
    status: str = None,
    limit: int = 50,
    offset: int = 0
) -> Dict[str, Any]:
    """List trading sessions"""
    
    query = db.query(LiveTradingSession)
    
    if status:
        query = query.filter(LiveTradingSession.status == status)
    
    total = query.count()
    sessions = query.order_by(
        desc(LiveTradingSession.created_at)
    ).offset(offset).limit(limit).all()
    
    result = []
    for session in sessions:
        # Get strategy name
        strategy = db.query(Strategy).filter(
            Strategy.id == session.strategy_id
        ).first()
        
        # Count positions and trades
        open_positions = db.query(Position).filter(
            Position.session_id == session.id,
            Position.status == "OPEN"
        ).count()
        
        closed_trades_count = db.query(ClosedTrade).filter(
            ClosedTrade.session_id == session.id
        ).count()
        
        result.append({
            "id": session.id,
            "strategy_name": strategy.name if strategy else "Unknown",
            "symbol": session.symbol,
            "timeframe": session.timeframe,
            "status": session.status,
            "initial_balance": float(session.initial_balance),
            "current_balance": float(session.current_balance),
            "equity": float(session.equity),
            "open_positions": open_positions,
            "closed_trades": closed_trades_count,
            "created_at": session.created_at.isoformat(),
            "last_updated": session.last_updated.isoformat()
        })
    
    return {
        "total": total,
        "limit": limit,
        "offset": offset,
        "sessions": result
    }


@router.get("/trades")
@handle_exceptions
async def list_trades(
    db: Session = Depends(get_db),
    session_id: int = None,
    limit: int = 100,
    offset: int = 0
) -> Dict[str, Any]:
    """List closed trades"""
    
    query = db.query(ClosedTrade)
    
    if session_id:
        query = query.filter(ClosedTrade.session_id == session_id)
    
    total = query.count()
    trades = query.order_by(
        desc(ClosedTrade.exit_time)
    ).offset(offset).limit(limit).all()
    
    result = []
    for trade in trades:
        # Get session info
        session = db.query(LiveTradingSession).filter(
            LiveTradingSession.id == trade.session_id
        ).first()
        
        result.append({
            "id": trade.id,
            "session_id": trade.session_id,
            "symbol": trade.symbol,
            "direction": trade.direction,
            "entry_price": float(trade.entry_price),
            "exit_price": float(trade.exit_price),
            "profit": float(trade.profit),
            "profit_pct": float(trade.profit_pct),
            "exit_reason": trade.exit_reason,
            "entry_time": trade.entry_time.isoformat(),
            "exit_time": trade.exit_time.isoformat(),
            "session_symbol": session.symbol if session else None
        })
    
    return {
        "total": total,
        "limit": limit,
        "offset": offset,
        "trades": result
    }


@router.get("/db-info")
@handle_exceptions
async def get_database_info(db: Session = Depends(get_db)) -> Dict[str, Any]:
    """Get database information and statistics"""
    
    import os
    from pathlib import Path
    
    # Get database file info
    db_path = Path(__file__).parent.parent.parent / "combo_optimizer.db"
    db_size = db_path.stat().st_size if db_path.exists() else 0
    
    # Count records in each table
    counts = {
        "strategies": db.query(Strategy).count(),
        "sessions": db.query(LiveTradingSession).count(),
        "positions": db.query(Position).count(),
        "closed_trades": db.query(ClosedTrade).count(),
        "backtest_results": db.query(BacktestResult).count()
    }
    
    # Get database URL
    from database.connection import DATABASE_URL
    
    return {
        "database_url": DATABASE_URL.split("@")[-1] if "@" in DATABASE_URL else DATABASE_URL,
        "database_type": "SQLite" if "sqlite" in DATABASE_URL else "PostgreSQL",
        "file_size_bytes": db_size,
        "file_size_mb": round(db_size / (1024 * 1024), 2),
        "table_counts": counts,
        "timestamp": datetime.utcnow().isoformat()
    }


@router.get("/stats/trading")
@handle_exceptions
async def get_trading_statistics(
    db: Session = Depends(get_db),
    days: int = 30
) -> Dict[str, Any]:
    """Get trading statistics for last N days"""
    
    start_date = datetime.utcnow() - timedelta(days=days)
    
    # Trades in period
    trades = db.query(ClosedTrade).filter(
        ClosedTrade.exit_time >= start_date
    ).all()
    
    if not trades:
        return {
            "period_days": days,
            "total_trades": 0,
            "statistics": {}
        }
    
    winning = [t for t in trades if t.profit > 0]
    losing = [t for t in trades if t.profit <= 0]
    
    total_profit = sum(float(t.profit) for t in trades)
    total_profit_pct = sum(float(t.profit_pct) for t in trades)
    
    avg_profit = total_profit / len(trades) if trades else 0
    avg_profit_pct = total_profit_pct / len(trades) if trades else 0
    
    return {
        "period_days": days,
        "total_trades": len(trades),
        "winning_trades": len(winning),
        "losing_trades": len(losing),
        "win_rate": round(len(winning) / len(trades) * 100, 2) if trades else 0,
        "total_profit": round(total_profit, 2),
        "total_profit_pct": round(total_profit_pct, 2),
        "avg_profit_per_trade": round(avg_profit, 2),
        "avg_profit_pct_per_trade": round(avg_profit_pct, 2),
        "largest_win": round(max((float(t.profit) for t in trades), default=0), 2),
        "largest_loss": round(min((float(t.profit) for t in trades), default=0), 2)
    }

