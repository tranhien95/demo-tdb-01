"""
Live Trading Models
Data models for live trading system
"""

from dataclasses import dataclass, field, asdict
from typing import Dict, List, Optional, Any
from datetime import datetime
from enum import Enum
import json


class OrderStatus(str, Enum):
    PENDING = "pending"
    OPEN = "open"
    CLOSED = "closed"
    CANCELLED = "cancelled"


class TradeStatus(str, Enum):
    RUNNING = "running"
    STOPPED = "stopped"
    PAUSED = "paused"


class SignalType(str, Enum):
    STRONG_BUY = "STRONG_BUY"
    BUY = "BUY"
    NEUTRAL = "NEUTRAL"
    SELL = "SELL"
    STRONG_SELL = "STRONG_SELL"


@dataclass
class TradingConfig:
    """Trading configuration"""
    symbol: str
    timeframe: str
    strategy_name: str
    initial_balance: float
    risk_percent: float  # % vốn mỗi lệnh
    margin: float  # Margin ratio (1.0 = no margin, 2.0 = 2x leverage)
    stoploss_percent: float  # Fixed % SL
    reversal_strength_threshold: float = 70.0  # % để trigger reversal SL
    max_positions: int = 1
    # Trailing Stop Loss settings
    enable_trailing_stop: bool = True  # Enable trailing stop loss
    trailing_multiplier: float = 1.5  # ATR multiplier for trailing distance
    trailing_activation_r: float = 1.0  # Activate trailing when profit >= 1R
    # Breakeven Stop settings
    enable_breakeven_stop: bool = True  # Enable breakeven stop
    breakeven_activation_r: float = 1.0  # Move SL to breakeven when profit >= 1R
    breakeven_buffer_pct: float = 0.1  # Buffer % to avoid spread (default 0.1%)
    # Dynamic Position Sizing settings
    enable_dynamic_sizing: bool = True  # Enable dynamic position sizing
    dynamic_sizing_max_multiplier: float = 2.0  # Max multiplier for position size
    dynamic_sizing_use_volatility: bool = True  # Adjust size based on volatility
    # Partial Profit Taking settings
    enable_partial_profit: bool = True  # Enable partial profit taking
    partial_profit_rules: List[Dict] = field(default_factory=lambda: [
        {"r_level": 1.0, "close_pct": 0.5, "taken": False},
        {"r_level": 2.0, "close_pct": 0.25, "taken": False}
    ])  # Partial exit rules
    # Multi-timeframe settings
    enable_multi_timeframe: bool = True  # Enable multi-timeframe confirmation
    higher_timeframe: str = "1h"  # Higher timeframe for trend filter
    # Volatility-based SL/TP settings
    enable_atr_sl_tp: bool = False  # Use ATR-based SL/TP
    atr_sl_multiplier: float = 2.0  # ATR multiplier for SL
    atr_tp_multiplier: float = 4.0  # ATR multiplier for TP (2:1 R:R)
    # Time-based filter settings
    enable_time_filter: bool = True  # Enable time-based filters
    market_type: str = "crypto"  # "crypto", "forex", "stock"
    # Market regime detection
    enable_regime_detection: bool = False  # Enable market regime detection
    # Signal quality scoring
    enable_signal_quality: bool = True  # Enable signal quality scoring
    min_signal_quality: float = 70.0  # Minimum quality score to trade
    # Correlation filter
    enable_correlation_filter: bool = False  # Enable correlation filter
    max_correlation: float = 0.7  # Max correlation allowed
    created_at: datetime = field(default_factory=datetime.now)


@dataclass
class Position:
    """Open trading position"""
    id: str
    symbol: str
    entry_price: float
    entry_time: datetime
    quantity: float  # Number of coins/stocks
    side: str  # "LONG" or "SHORT"
    
    # SL & TP
    stoploss: float
    takeprofit: float
    
    # Entry signal info
    entry_signal: str  # STRONG_BUY, BUY, etc.
    entry_confidence: float  # 0-100
    
    # Tracking
    current_price: float = 0.0
    current_pnl: float = 0.0
    current_pnl_percent: float = 0.0
    highest_price: float = 0.0  # For trailing SL
    lowest_price: float = 0.0   # For trailing SL
    
    # Trailing Stop Loss
    initial_stoploss: float = 0.0  # Original SL for R calculation
    trailing_activated: bool = False  # Whether trailing is active
    # Breakeven Stop
    breakeven_set: bool = False  # Whether breakeven has been set
    # Partial Profit Taking
    partial_profit_rules: List[Dict] = field(default_factory=lambda: [
        {"r_level": 1.0, "close_pct": 0.5, "taken": False},
        {"r_level": 2.0, "close_pct": 0.25, "taken": False}
    ])  # Partial exit rules
    
    def update_price(self, price: float):
        """Update current price and calculate P&L"""
        self.current_price = price
        
        if self.side == "LONG":
            self.current_pnl = (price - self.entry_price) * self.quantity
            self.current_pnl_percent = ((price - self.entry_price) / self.entry_price) * 100
            if price > self.highest_price:
                self.highest_price = price
        else:  # SHORT
            self.current_pnl = (self.entry_price - price) * self.quantity
            self.current_pnl_percent = ((self.entry_price - price) / self.entry_price) * 100
            if price < self.lowest_price:
                self.lowest_price = price
    
    def to_dict(self) -> Dict:
        """Convert to dictionary"""
        return {
            "id": self.id,
            "symbol": self.symbol,
            "entry_price": self.entry_price,
            "entry_time": self.entry_time.isoformat(),
            "quantity": self.quantity,
            "side": self.side,
            "stoploss": self.stoploss,
            "takeprofit": self.takeprofit,
            "entry_signal": self.entry_signal,
            "entry_confidence": self.entry_confidence,
            "current_price": self.current_price,
            "current_pnl": self.current_pnl,
            "current_pnl_percent": self.current_pnl_percent,
            "initial_stoploss": self.initial_stoploss,
            "trailing_activated": self.trailing_activated,
            "breakeven_set": self.breakeven_set,
        }


@dataclass
class ClosedTrade:
    """Completed trade"""
    id: str
    symbol: str
    entry_price: float
    entry_time: datetime
    exit_price: float
    exit_time: datetime
    quantity: float
    side: str
    pnl: float
    pnl_percent: float
    win: bool
    exit_reason: str  # "TP_HIT", "SL_HIT", "REVERSAL_SIGNAL", "MANUAL"
    entry_signal: str
    exit_signal: Optional[str]
    entry_confidence: float
    
    def to_dict(self) -> Dict:
        """Convert to dictionary"""
        return {
            "id": self.id,
            "symbol": self.symbol,
            "entry_price": self.entry_price,
            "entry_time": self.entry_time.isoformat(),
            "exit_price": self.exit_price,
            "exit_time": self.exit_time.isoformat(),
            "quantity": self.quantity,
            "side": self.side,
            "pnl": self.pnl,
            "pnl_percent": self.pnl_percent,
            "win": self.win,
            "exit_reason": self.exit_reason,
            "entry_signal": self.entry_signal,
            "exit_signal": self.exit_signal,
            "entry_confidence": self.entry_confidence,
        }


@dataclass
class LiveTradingState:
    """Overall live trading state"""
    status: TradeStatus
    config: TradingConfig
    
    # Account
    balance: float  # Current balance
    equity: float  # Balance + open positions P&L
    used_margin: float
    available_margin: float
    
    # Positions
    open_positions: List[Position] = field(default_factory=list)
    closed_trades: List[ClosedTrade] = field(default_factory=list)
    
    # Chart data
    candles: List[Dict[str, Any]] = field(default_factory=list)
    
    # Performance metrics
    total_trades: int = 0
    winning_trades: int = 0
    losing_trades: int = 0
    win_rate: float = 0.0
    total_profit: float = 0.0
    total_loss: float = 0.0
    profit_factor: float = 0.0
    max_drawdown: float = 0.0
    daily_pnl: float = 0.0
    
    # Tracking
    created_at: datetime = field(default_factory=datetime.now)
    last_updated: datetime = field(default_factory=datetime.now)
    
    def to_dict(self) -> Dict:
        """Convert to dictionary"""
        return {
            "status": self.status.value,
            "config": asdict(self.config),
            "balance": self.balance,
            "equity": self.equity,
            "used_margin": self.used_margin,
            "available_margin": self.available_margin,
            "open_positions": [p.to_dict() for p in self.open_positions],
            "closed_trades": [t.to_dict() for t in self.closed_trades],
            "candles": self.candles,
            "total_trades": self.total_trades,
            "winning_trades": self.winning_trades,
            "losing_trades": self.losing_trades,
            "win_rate": self.win_rate,
            "total_profit": self.total_profit,
            "total_loss": self.total_loss,
            "profit_factor": self.profit_factor,
            "max_drawdown": self.max_drawdown,
            "daily_pnl": self.daily_pnl,
            "created_at": self.created_at.isoformat(),
            "last_updated": self.last_updated.isoformat(),
        }


@dataclass
class SignalWithConfidence:
    """Signal from indicator with confidence"""
    type: SignalType
    confidence: float  # 0-100
    reversal_strength: float  # 0-100 for reversal signals
    divergence: bool
    supporting_signals: List[str] = field(default_factory=list)


@dataclass
class CandleData:
    """Single candle OHLCV data"""
    time: datetime
    open: float
    high: float
    low: float
    close: float
    volume: float
