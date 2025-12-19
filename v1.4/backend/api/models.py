"""
API Models
Pydantic models for API requests/responses
"""

from pydantic import BaseModel, Field, ConfigDict
from typing import List, Dict, Any, Optional
from datetime import datetime


class OHLCV(BaseModel):
    """OHLCV data model"""
    time: str
    open: float
    high: float
    low: float
    close: float
    volume: int


class OptimizationParams(BaseModel):
    """Parameters for optimization endpoint"""
    model_config = ConfigDict(populate_by_name=True)  # Allow both snake_case and camelCase
    
    ohlcv_data: List[OHLCV]  # Required field, frontend sends as 'ohlcv_data'
    min_combo_size: int = Field(default=2, alias='minComboSize')
    max_combo_size: int = Field(default=3, alias='maxComboSize')
    threshold: int = 70
    risk_percent: float = Field(default=10.0, alias='riskPercent')
    rr_ratio: float = Field(default=2.0, alias='rrRatio')
    sl_percent: float = Field(default=0.75, alias='slPercent')
    filters: Dict[str, Any] = {}
    max_combos: int = Field(default=0, alias='maxCombos')
    min_signal_ratio: int = Field(default=70, alias='minSignalStrength')
    candle_confirmation: int = Field(default=2, alias='candleConfirmation')
    capital: float = 1000.0  # Initial capital
    
    # Additional Filters
    enable_adx_filter: bool = Field(default=False, alias='enableADXFilter')
    adx_threshold: float = Field(default=25.0, alias='adxThreshold')
    enable_volume_filter: bool = Field(default=False, alias='enableVolumeFilter')
    volume_ma_period: int = Field(default=20, alias='volumeThreshold')
    enable_ma_filter: bool = Field(default=False, alias='enableMAFilter')
    ma_period: int = Field(default=50, alias='maValue')
    enable_trend_filter: bool = Field(default=False, alias='enableTrendFilter')
    trend_ma: int = Field(default=200, alias='trendMA')
    enable_volatility_filter: bool = Field(default=False, alias='enableVolatilityFilter')
    min_atr: float = Field(default=0.5, alias='minATR')
    
    # Advanced Exit Settings
    enable_trailing_stop: bool = Field(default=True, alias='enableTrailingStop')
    trailing_activation_r: float = Field(default=1.0, alias='trailingActivationR')
    trailing_multiplier: float = Field(default=1.5, alias='trailingMultiplier')
    enable_partial_tp_close: bool = Field(default=False, alias='enablePartialTPClose')
    tp_close_pct: float = Field(default=0.5, alias='tpClosePct')
    
    # Additional fields from frontend that may not be used in backend
    min_win_rate: float = Field(default=50.0, alias='minWinRate', exclude=True)
    min_profit: float = Field(default=0.0, alias='minProfit', exclude=True)
    min_trades: int = Field(default=10, alias='minTrades', exclude=True)


class BacktestResult(BaseModel):
    """Backtest result model"""
    combo: str
    trades: int
    wins: int
    losses: int
    win_rate: float
    profit_pct: float
    profit_factor: float
    draw_down: float
    sharpe: float
    trades_list: List[Dict] = []


class BinanceRequest(BaseModel):
    """Binance API request model"""
    symbol: str
    timeframe: str
    limit: Optional[int] = None  # Optional if using date range
    start_date: Optional[str] = None  # Format: 'YYYY-MM-DD' or 'YYYY-MM-DD HH:MM:SS'
    end_date: Optional[str] = None  # Format: 'YYYY-MM-DD' or 'YYYY-MM-DD HH:MM:SS'


class BinanceResponse(BaseModel):
    """Binance API response model"""
    symbol: str
    timeframe: str
    count: int
    ohlcv_data: List[OHLCV]
    fetched_at: str


class VNStockRequest(BaseModel):
    """VNStock API request model"""
    symbol: str
    timeframe: str
    limit: Optional[int] = None  # Optional if using date range
    start_date: Optional[str] = None  # Format: 'YYYY-MM-DD' or 'YYYY-MM-DD HH:MM:SS'
    end_date: Optional[str] = None  # Format: 'YYYY-MM-DD' or 'YYYY-MM-DD HH:MM:SS'


class LiveTradingStartRequest(BaseModel):
    """Live trading start request model"""
    symbol: str
    timeframe: str
    strategy_name: str
    initial_balance: float
    risk_percent: float  # % vốn mỗi lệnh
    margin: float = 1.0  # Margin ratio
    stoploss_percent: float = 2.0  # Fixed SL %
    reversal_strength_threshold: float = 70.0
    max_positions: int = 1

