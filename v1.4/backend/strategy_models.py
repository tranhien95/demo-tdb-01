"""
Strategy Models
Data models for custom strategy building
"""

from pydantic import BaseModel, Field, ConfigDict
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
    candle_confirmation: int = Field(default=1, ge=1, le=10, description="Candles needed to confirm entry signal")
    min_holding_candles: int = Field(default=3, ge=1, le=100, description="Minimum candles to hold position before allowing switch")
    switch_confirmation_candles: int = Field(default=2, ge=1, le=10, description="Candles needed to confirm switch signal")
    allow_position_switch: bool = Field(default=True, description="Enable/disable position switching")
    min_profit_r_to_switch: float = Field(default=-1.0, ge=-5.0, le=5.0, description="Minimum profit R to allow switch (-1 = only switch if losing to protect capital, 0 = always allow, 0.5 = need 0.5R profit)")
    enable_trailing_stop: bool = Field(default=True, description="Enable trailing stop loss in backtest")
    trailing_activation_r: float = Field(default=1.0, ge=0.0, le=5.0, description="Activate trailing when profit >= this R value")
    trailing_multiplier: float = Field(default=1.5, ge=0.5, le=5.0, description="ATR multiplier for trailing distance")
    enable_partial_tp_close: bool = Field(default=False, description="Enable partial TP close - close % of position at TP, keep remainder with trailing stop")
    tp_close_pct: float = Field(default=0.5, ge=0.0, le=1.0, description="Close % of position when TP hit (0.5 = 50%, 1.0 = 100%). Only used if enable_partial_tp_close is True")


class FilterConfig(BaseModel):
    """Trading filters configuration"""
    enable_adx: bool = Field(default=False, description="Enable ADX filter")
    adx_threshold: float = Field(default=25.0, ge=0, le=100, description="ADX threshold")
    
    enable_volume: bool = Field(default=False, description="Enable volume filter")
    volume_threshold: float = Field(default=1.5, ge=1.0, le=5.0, description="Volume multiplier threshold")
    
    enable_ma_filter: bool = Field(default=False, description="Enable MA trend filter")
    ma_period: int = Field(default=50, ge=10, le=500, description="MA period")
    
    enable_atr_filter: bool = Field(default=False, description="Enable ATR volatility filter")
    min_atr: float = Field(default=0.0005, ge=0.00001, le=10.0, description="Minimum ATR value")
    
    enable_trend_filter: bool = Field(default=False, description="Enable trend filter")
    trend_ma: int = Field(default=200, ge=50, le=500, description="Trend MA period")


class RiskManagement(BaseModel):
    """Risk management settings"""
    risk_percent: float = Field(default=10.0, ge=1.0, le=100.0, description="Risk per trade %")
    reward_ratio: float = Field(default=1.0, ge=0.5, le=10.0, description="Reward ratio (for TP calculation)")
    stop_loss_percent: float = Field(default=5.0, ge=0.1, le=10.0, description="Stop loss %")
    capital: float = Field(default=10000.0, ge=100.0, le=1000000.0, description="Initial capital")
    margin: Optional[float] = Field(default=None, description="Margin to use (if leveraged trading)")


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
    
    model_config = ConfigDict(populate_by_name=True)


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
    version: Optional[str] = "1.0.0"  # Strategy version
    backtest_info: Optional[Dict[str, Any]] = None  # Backtest results if available
