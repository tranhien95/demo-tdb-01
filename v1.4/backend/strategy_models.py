"""
Strategy Models
Data models for custom strategy building
"""

from pydantic import BaseModel, Field
from typing import List, Dict, Optional, Any
from datetime import datetime


class IndicatorConfig(BaseModel):
    """Configuration for a single indicator instance"""
    type: str = Field(..., description="Indicator type (RSI, MACD, etc)")
    config: Dict[str, Any] = Field(default_factory=dict, description="Indicator parameters")
    weight: float = Field(default=1.0, ge=0.1, le=10.0, description="Indicator weight for signal calculation")
    enabled: bool = Field(default=True, description="Whether indicator is active")
    id: Optional[str] = Field(None, description="Unique ID for this instance")


class SignalLogic(BaseModel):
    """Signal confirmation logic"""
    threshold_percent: float = Field(default=70.0, ge=0, le=100, description="Minimum % of weighted agreement needed")


class FilterConfig(BaseModel):
    """Trading filters configuration"""
    # ADX Filter
    enable_adx_filter: bool = Field(default=False)
    adx_threshold: float = Field(default=25.0, ge=0, le=100)
    
    # Volume Filter
    enable_volume_filter: bool = Field(default=False)
    volume_ma_period: int = Field(default=20, ge=5, le=200)
    volume_multiplier: float = Field(default=1.5, ge=1.0, le=5.0)
    
    # MA Trend Filter
    enable_ma_filter: bool = Field(default=False)
    ma_period: int = Field(default=50, ge=10, le=500)
    
    # ATR Volatility Filter
    enable_atr_filter: bool = Field(default=False)
    atr_period: int = Field(default=14, ge=5, le=50)
    atr_min: float = Field(default=0.5, ge=0.1, le=10.0)
    
    # Trend Filter (Price vs EMA200)
    enable_trend_filter: bool = Field(default=False)
    trend_ema_period: int = Field(default=200, ge=50, le=500)


class RiskManagement(BaseModel):
    """Risk management settings"""
    risk_percent: float = Field(default=10.0, ge=1.0, le=100.0, description="Risk per trade %")
    rr_ratio: float = Field(default=2.0, ge=0.5, le=10.0, description="Risk:Reward ratio")
    sl_percent: float = Field(default=0.75, ge=0.1, le=10.0, description="Stop loss %")
    candle_confirmation: int = Field(default=2, ge=1, le=10, description="Candles to confirm signal")
    capital: float = Field(default=10000.0, ge=100.0, le=1000000.0, description="Initial capital")


class Strategy(BaseModel):
    """Complete trading strategy definition"""
    name: str = Field(..., min_length=1, max_length=100)
    description: Optional[str] = Field(None, max_length=500)
    
    indicators: List[IndicatorConfig] = Field(..., min_items=1, max_items=20)
    signal_logic: SignalLogic = Field(default_factory=SignalLogic)
    filters: FilterConfig = Field(default_factory=FilterConfig)
    risk_management: RiskManagement = Field(default_factory=RiskManagement)
    
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None


class BacktestRequest(BaseModel):
    """Request to backtest a strategy"""
    strategy: Strategy
    ohlcv_data: List[Dict[str, Any]]


class SignalDetail(BaseModel):
    """Details of a signal calculation"""
    indicator_type: str
    indicator_id: Optional[str]
    bullish: Optional[bool] = False
    bearish: Optional[bool] = False
    value: Any = None  # Can be float, dict, or any complex value from indicators
    weight: float
    contribution_percent: float
    enabled: bool


class TradeSignal(BaseModel):
    """Signal with full details"""
    index: int
    time: str
    direction: str  # LONG or SHORT
    total_weight: float
    bullish_weight: float
    bearish_weight: float
    bullish_percent: float
    bearish_percent: float
    threshold_met: bool
    signals_detail: List[SignalDetail]


class BacktestTrade(BaseModel):
    """Individual trade result"""
    entry: float
    exit: Optional[float]
    sl: float
    tp: float
    profit: Optional[float]
    profit_pct: Optional[float]
    position_size: Optional[float]  # Amount of money in trade
    position_percent: Optional[float]  # Percent of capital used
    type: str  # LONG or SHORT
    time: str
    exit_time: Optional[str]
    exit_reason: Optional[str]
    entry_signals: List[SignalDetail]


class BacktestResult(BaseModel):
    """Backtest results with full details"""
    strategy_name: str
    
    # Stats
    total_trades: int
    winning_trades: int = Field(..., alias='wins')
    losing_trades: int = Field(..., alias='losses')
    win_rate: float
    profit_pct: float
    total_profit_usd: float
    long_trades: int
    short_trades: int
    profit_factor: float
    max_drawdown: float = Field(..., alias='draw_down')
    sharpe_ratio: float = Field(..., alias='sharpe')
    
    # Advanced Metrics (New)
    sortino_ratio: Optional[float] = 0.0
    calmar_ratio: Optional[float] = 0.0
    recovery_factor: Optional[float] = 0.0
    expectancy: Optional[float] = 0.0
    max_consecutive_losses: Optional[int] = 0
    max_consecutive_wins: Optional[int] = 0
    profit_per_trade: Optional[float] = 0.0
    avg_win: Optional[float] = 0.0
    avg_loss: Optional[float] = 0.0
    avg_win_pct: Optional[float] = 0.0
    avg_loss_pct: Optional[float] = 0.0
    largest_win: Optional[float] = 0.0
    largest_loss: Optional[float] = 0.0
    max_drawdown_value: Optional[float] = 0.0
    drawdown_duration: Optional[int] = 0
    recovery_duration: Optional[int] = 0
    
    # Trades
    trades: List[BacktestTrade]
    
    # Equity curve
    equity_curve: List[float]
    
    # Signal preview
    total_signals: int
    long_signals: int
    short_signals: int
    
    class Config:
        populate_by_name = True


class StrategyListItem(BaseModel):
    """Strategy list item for UI"""
    name: str
    description: Optional[str]
    indicator_count: int
    created_at: datetime
    updated_at: datetime


class PineScriptExport(BaseModel):
    """Pine Script export result"""
    code: str
    strategy_name: str
    indicators_used: List[str]
