"""
API Models
Pydantic models for API requests/responses
"""

from pydantic import BaseModel
from typing import List, Dict, Any


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
    ohlcv_data: List[OHLCV]
    min_combo_size: int = 2
    max_combo_size: int = 3
    threshold: int = 70
    risk_percent: float = 10.0
    rr_ratio: float = 2.0
    sl_percent: float = 0.75
    filters: Dict[str, Any] = {}
    max_combos: int = 0
    min_signal_ratio: int = 70
    candle_confirmation: int = 2
    
    # Additional Filters
    enable_adx_filter: bool = False
    adx_threshold: float = 25.0
    enable_volume_filter: bool = False
    volume_ma_period: int = 20
    enable_ma_filter: bool = False
    ma_period: int = 50


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
    limit: int = 200


class BinanceResponse(BaseModel):
    """Binance API response model"""
    symbol: str
    timeframe: str
    count: int
    ohlcv_data: List[OHLCV]
    fetched_at: str


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

