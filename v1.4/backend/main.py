#!/usr/bin/env python3
"""
Combo Optimizer v1.4 Backend
FastAPI server for indicator calculation and strategy backtesting
Port: 4000
"""

from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import StreamingResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, ValidationError, Field, ConfigDict
import json
from typing import List, Dict, Any, Optional
from itertools import combinations
from indicators import indicator_manager, get_all_signals, get_pine_script_code
from indicators.config_variants import generate_indicator_with_configs, INDICATOR_CONFIG_VARIANTS
from performance_metrics import PerformanceMetrics
from utils.gpu_acceleration import gpu, GPU_AVAILABLE
from binance_fetcher import get_binance_fetcher
try:
    from vnstock_fetcher import get_vnstock_fetcher
    VNSTOCK_AVAILABLE = True
except (ImportError, UnicodeEncodeError, Exception) as e:
    VNSTOCK_AVAILABLE = False
    if isinstance(e, UnicodeEncodeError):
        print("⚠️ vnstock encoding error (Windows console issue). Library is installed but may have display issues.")
    elif isinstance(e, ImportError):
        print("⚠️ vnstock chưa được cài đặt. Chạy: pip install vnstock để sử dụng chứng khoán VN")
    else:
        print(f"⚠️ vnstock error: {str(e)}. Using fallback mode.")

try:
    from dnse_fetcher import get_dnse_fetcher
    DNSE_AVAILABLE = True
except ImportError:
    DNSE_AVAILABLE = False
    print("⚠️ dnse_fetcher có thể cần yfinance. Chạy: pip install yfinance để sử dụng")

# Strategy imports
from strategy_models import (
    Strategy, BacktestRequest, StrategyListItem, 
    IndicatorConfig, SignalDetail
)
from strategy_engine import StrategyEngine
from strategy_storage import strategy_storage
from pine_script_generator import pine_script_generator
from pine_script_parser import PineScriptParser

# Live Trading imports
from live_trading_engine import get_live_trading_engine
from live_trading_models import TradingConfig, TradeStatus

app = FastAPI(title="Combo Optimizer v1.4 Backend", version="1.4.0")

# Enable CORS for React frontend (port 5173 for Vite dev server)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://localhost:5173", "http://127.0.0.1:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ======================== MODELS ========================

class OHLCV(BaseModel):
    time: str
    open: float
    high: float
    low: float
    close: float
    volume: int

class OptimizationParams(BaseModel):
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

# ======================== BINANCE MODELS ========================

class BinanceRequest(BaseModel):
    symbol: str
    timeframe: str
    limit: Optional[int] = None  # Optional if using date range
    start_date: Optional[str] = None  # Format: 'YYYY-MM-DD' or 'YYYY-MM-DD HH:MM:SS'
    end_date: Optional[str] = None  # Format: 'YYYY-MM-DD' or 'YYYY-MM-DD HH:MM:SS'

class BinanceResponse(BaseModel):
    symbol: str
    timeframe: str
    count: int
    ohlcv_data: List[OHLCV]
    fetched_at: str

# ======================== BACKTESTING ========================

class BacktestEngine:
    """Backtest strategy combinations"""
    
    _signals_cache = None
    _cache_data_len = 0
    
    @staticmethod
    def _get_or_compute_signals(ohlcv_data: List[Dict], use_gpu: bool = None) -> List[Dict]:
        """
        Get cached signals or compute them once
        
        Args:
            ohlcv_data: OHLCV data
            use_gpu: Whether to use GPU acceleration (auto-detect if None)
        """
        data_len = len(ohlcv_data)
        
        if BacktestEngine._signals_cache is not None and BacktestEngine._cache_data_len == data_len:
            return BacktestEngine._signals_cache
        
        # Auto-detect GPU usage
        if use_gpu is None:
            use_gpu = GPU_AVAILABLE and gpu.use_gpu
        
        if use_gpu:
            print(f"[GPU Cache] Computing signals for {data_len} candles on GPU...")
        else:
            print(f"[Cache] Computing signals for {data_len} candles on CPU...")
        
        all_signals = []
        for i in range(len(ohlcv_data)):
            signals = get_all_signals(ohlcv_data, i)
            all_signals.append(signals)
        
        BacktestEngine._signals_cache = all_signals
        BacktestEngine._cache_data_len = data_len
        
        if use_gpu:
            print(f"[GPU Cache] Signals cached successfully (GPU accelerated)")
        else:
            print(f"[Cache] Signals cached successfully")
        
        return all_signals
    
    @staticmethod
    def backtest_combo(combo: List[Any], ohlcv_data: List[Dict], threshold: int,
                      risk_pct: float, rr_ratio: float, sl_pct: float, filters: Dict, 
                      min_signal_ratio: int = 50, candle_confirmation: int = 2, capital: float = 100,
                      enable_trailing_stop: bool = True, trailing_activation_r: float = 1.0,
                      trailing_multiplier: float = 1.5, enable_partial_tp_close: bool = False,
                      tp_close_pct: float = 0.5) -> Dict:
        """
        Backtest a single indicator combination
        
        Args:
            combo: List of indicator configs. Each can be:
                - str: indicator name (uses default config)
                - dict: {'indicator_name': str, 'config': dict, 'display_name': str}
        """
        
        # Normalize combo format
        normalized_combo = []
        combo_display_names = []
        for item in combo:
            if isinstance(item, str):
                normalized_combo.append({'indicator_name': item, 'config': {}, 'display_name': item})
                combo_display_names.append(item)
            elif isinstance(item, dict):
                normalized_combo.append(item)
                combo_display_names.append(item.get('display_name', item.get('indicator_name', 'Unknown')))
            else:
                # Fallback
                normalized_combo.append({'indicator_name': str(item), 'config': {}, 'display_name': str(item)})
                combo_display_names.append(str(item))
        
        combo_str = ' + '.join(combo_display_names)
        
        if not ohlcv_data or len(ohlcv_data) < 50:
            return {
                'combo': combo_str,
                'combo_config': normalized_combo,
                'trades': 0,
                'wins': 0,
                'losses': 0,
                'win_rate': 0,
                'profit_pct': 0,
                'profit_factor': 0,
                'draw_down': 0,
                'sharpe': 0,
                'trades_list': []
            }
        
        trades_list = []
        balance = capital
        max_balance = capital
        min_balance = capital
        wins = 0
        current_position = None
        
        last_signal = None
        signal_count = 0
        
        # Get default signals (for indicators without custom config)
        all_signals = BacktestEngine._get_or_compute_signals(ohlcv_data)
        
        # Calculate signals with custom configs
        available_indicators = indicator_manager.list_indicators()
        
        for i in range(50, len(ohlcv_data) - 1):
            combo_signals = {}
            
            # Calculate signals for each indicator in combo with its config
            for ind_config in normalized_combo:
                ind_name = ind_config['indicator_name']
                ind_custom_config = ind_config.get('config', {})
                
                if ind_name not in available_indicators:
                    continue
                
                # If custom config provided, calculate with it
                if ind_custom_config:
                    indicator = indicator_manager.get_indicator(ind_name)
                    if indicator:
                        signal = indicator.calculate_safe(ohlcv_data, i, **ind_custom_config)
                        combo_signals[ind_config['display_name']] = signal
                else:
                    # Use cached default signals
                    signal_key = ind_name
                    if signal_key in all_signals[i]:
                        combo_signals[ind_config['display_name']] = all_signals[i][signal_key]
            
            bullish_count = 0
            bearish_count = 0
            total_strength = 0
            
            for signal_key, signal_data in combo_signals.items():
                if isinstance(signal_data, dict):
                    if signal_data.get('bullish', False):
                        bullish_count += 1
                    if signal_data.get('bearish', False):
                        bearish_count += 1
                    total_strength += signal_data.get('strength', 0)
            
            total_signals = len(combo_signals)
            avg_strength = (total_strength / total_signals) if total_signals > 0 else 0
            
            bullish_pct = (bullish_count / total_signals * 100) if total_signals > 0 else 0
            bearish_pct = (bearish_count / total_signals * 100) if total_signals > 0 else 0
            
            entry_type = None
            if bullish_pct >= threshold:
                entry_type = 'LONG'
            elif bearish_pct >= threshold:
                entry_type = 'SHORT'
            
            filter_passed = True
            
            if entry_type:
                if filters.get('enable_adx_filter', False):
                    adx_val = all_candle_signals.get('ADX', {}).get('value', 0)
                    adx_threshold = filters.get('adx_threshold', 25)
                    if adx_val < adx_threshold:
                        filter_passed = False
                
                if filter_passed and filters.get('enable_volume_filter', False):
                    vol_ma_period = filters.get('volume_ma_period', 20)
                    if i >= vol_ma_period:
                        vol_ma = sum([ohlcv_data[j]['volume'] for j in range(i - vol_ma_period, i)]) / vol_ma_period
                        current_vol = ohlcv_data[i]['volume']
                        if current_vol < vol_ma:
                            filter_passed = False
                
                if filter_passed and filters.get('enable_ma_filter', False):
                    ma_period = filters.get('ma_period', 50)
                    if i >= ma_period:
                        ma_val = sum([ohlcv_data[j]['close'] for j in range(i - ma_period, i)]) / ma_period
                        current_price = ohlcv_data[i]['close']
                        if entry_type == 'LONG' and current_price <= ma_val:
                            filter_passed = False
                        elif entry_type == 'SHORT' and current_price >= ma_val:
                            filter_passed = False
            
            if entry_type and entry_type == last_signal:
                signal_count += 1
            else:
                last_signal = entry_type
                signal_count = 1
            
            should_enter = (
                entry_type and 
                filter_passed and
                signal_count >= candle_confirmation and
                (not current_position or current_position != entry_type)
            )
            
            if should_enter and not current_position:
                entry = ohlcv_data[i]['close']
                sl = entry * (1 - sl_pct / 100) if entry_type == 'LONG' else entry * (1 + sl_pct / 100)
                tp = entry + (entry - sl) * rr_ratio if entry_type == 'LONG' else entry - (sl - entry) * rr_ratio
                
                # Calculate position size based on capital parameter
                risk_amount = capital * (risk_pct / 100)
                position_size = risk_amount / (sl_pct / 100)
                position_percent = (position_size / balance) * 100
                
                trades_list.append({
                    'entry': round(entry, 2),
                    'exit': None,
                    'sl': round(sl, 2),
                    'tp': round(tp, 2),
                    'profit': None,
                    'profit_pct': None,
                    'position_size': round(position_size, 2),
                    'position_percent': round(position_percent, 2),
                    'balance_before': round(balance, 2),
                    'type': entry_type,
                    'time': ohlcv_data[i].get('time', ''),
                    'exit_time': None
                })
                current_position = entry_type
            
            elif should_enter and current_position and current_position != entry_type:
                last_trade = trades_list[-1]
                current_close = ohlcv_data[i]['close']
                
                profit = current_close - last_trade['entry'] if current_position == 'LONG' else last_trade['entry'] - current_close
                profit_pct = (profit / last_trade['entry']) * 100
                
                # Calculate actual USD profit: position size × profit%
                # Use stored position_size or calculate it
                if 'position_size' not in last_trade or last_trade.get('position_size') is None:
                    risk_amount = capital * (risk_pct / 100)
                    position_size_old = risk_amount / (sl_pct / 100)
                    last_trade['position_size'] = round(position_size_old, 2)
                else:
                    position_size_old = last_trade['position_size']
                
                actual_profit_usd = position_size_old * (profit_pct / 100)
                
                last_trade['exit'] = round(current_close, 2)
                last_trade['exit_time'] = ohlcv_data[i].get('time', '')
                last_trade['profit'] = round(actual_profit_usd, 4)  # USD profit
                last_trade['profit_pct'] = round(profit_pct, 2)
                last_trade['exit_reason'] = 'Switch'
                if 'balance_before' in last_trade:
                    last_trade['balance_after'] = round(last_trade['balance_before'] + actual_profit_usd, 2)
                
                if profit > 0:
                    wins += 1
                
                # Update balance
                balance += actual_profit_usd
                max_balance = max(max_balance, balance)
                min_balance = min(min_balance, balance)
                
                entry = current_close
                sl = entry * (1 - sl_pct / 100) if entry_type == 'LONG' else entry * (1 + sl_pct / 100)
                tp = entry + (entry - sl) * rr_ratio if entry_type == 'LONG' else entry - (sl - entry) * rr_ratio
                
                # Calculate position size for new trade
                risk_amount = capital * (risk_pct / 100)
                position_size = risk_amount / (sl_pct / 100)
                position_percent = (position_size / balance) * 100
                
                trades_list.append({
                    'entry': round(entry, 2),
                    'exit': None,
                    'sl': round(sl, 2),
                    'tp': round(tp, 2),
                    'profit': None,
                    'profit_pct': None,
                    'position_size': round(position_size, 2),
                    'position_percent': round(position_percent, 2),
                    'balance_before': round(balance, 2),
                    'type': entry_type,
                    'time': ohlcv_data[i].get('time', ''),
                    'exit_time': None
                })
                current_position = entry_type
            
            elif current_position and len(trades_list) > 0:
                last_trade = trades_list[-1]
                
                if last_trade.get('exit') is None:
                    current_high = ohlcv_data[i]['high']
                    current_low = ohlcv_data[i]['low']
                    current_close = ohlcv_data[i]['close']
                    
                    exit_price = None
                    exit_reason = None
                    
                    if current_position == 'LONG' and current_high >= last_trade['tp']:
                        exit_price = last_trade['tp']
                        exit_reason = 'TP'
                    elif current_position == 'SHORT' and current_low <= last_trade['tp']:
                        exit_price = last_trade['tp']
                        exit_reason = 'TP'
                    
                    if not exit_reason:
                        if current_position == 'LONG' and current_low <= last_trade['sl']:
                            exit_price = last_trade['sl']
                            exit_reason = 'SL'
                        elif current_position == 'SHORT' and current_high >= last_trade['sl']:
                            exit_price = last_trade['sl']
                            exit_reason = 'SL'
                    
                    if exit_price and exit_reason:
                        profit = exit_price - last_trade['entry'] if current_position == 'LONG' else last_trade['entry'] - exit_price
                        profit_pct = (profit / last_trade['entry']) * 100
                        
                        # Calculate actual USD profit using stored position_size or calculate it
                        if 'position_size' not in last_trade or last_trade.get('position_size') is None:
                            risk_amount = capital * (risk_pct / 100)
                            position_size = risk_amount / (sl_pct / 100)
                            last_trade['position_size'] = round(position_size, 2)
                        else:
                            position_size = last_trade['position_size']
                        
                        actual_profit_usd = position_size * (profit_pct / 100)
                        
                        last_trade['exit'] = round(exit_price, 2)
                        last_trade['exit_time'] = ohlcv_data[i].get('time', '')
                        last_trade['profit'] = round(actual_profit_usd, 4)  # USD profit
                        last_trade['profit_pct'] = round(profit_pct, 2)
                        last_trade['exit_reason'] = exit_reason
                        last_trade['balance_after'] = round(balance + actual_profit_usd, 2)
                        
                        if profit > 0:
                            wins += 1
                        
                        # Update balance
                        balance += actual_profit_usd
                        max_balance = max(max_balance, balance)
                        min_balance = min(min_balance, balance)
                        current_position = None
        
        if current_position and len(trades_list) > 0:
            last_trade = trades_list[-1]
            if last_trade.get('exit') is None:
                exit_price = ohlcv_data[-1]['close']
                profit = exit_price - last_trade['entry'] if current_position == 'LONG' else last_trade['entry'] - exit_price
                profit_pct = (profit / last_trade['entry']) * 100
                
                # Calculate actual USD profit using stored position_size or calculate it
                if 'position_size' not in last_trade or last_trade.get('position_size') is None:
                    risk_amount = capital * (risk_pct / 100)
                    position_size = risk_amount / (sl_pct / 100)
                    last_trade['position_size'] = round(position_size, 2)
                else:
                    position_size = last_trade['position_size']
                
                actual_profit_usd = position_size * (profit_pct / 100)
                
                last_trade['exit'] = round(exit_price, 2)
                last_trade['exit_time'] = ohlcv_data[-1].get('time', '')
                last_trade['profit'] = round(actual_profit_usd, 4)  # USD profit
                if 'balance_before' in last_trade:
                    last_trade['balance_after'] = round(last_trade['balance_before'] + actual_profit_usd, 2)
                last_trade['profit_pct'] = round(profit_pct, 2)
                
                if profit > 0:
                    wins += 1
        
        completed_trades = [t for t in trades_list if t['exit'] is not None]
        total_trades = len(completed_trades)
        losses = total_trades - wins
        
        win_rate = (wins / total_trades * 100) if total_trades > 0 else 0
        
        # Calculate actual portfolio return (not sum of individual trades)
        total_profit = ((balance - capital) / capital) * 100  # ROI% from initial capital
        
        # Use standardized performance metrics
        profit_factor = PerformanceMetrics.calculate_profit_factor(completed_trades)
        
        # Calculate max drawdown from balance tracking
        draw_down = ((max_balance - min_balance) / max_balance * 100) if max_balance > 0 else 0
        
        # Calculate Sharpe ratio properly
        sharpe = PerformanceMetrics.calculate_sharpe_ratio(completed_trades)
        
        return {
            'combo': combo_str,
            'combo_config': normalized_combo,  # Include config info
            'trades': total_trades,
            'wins': wins,
            'losses': losses,
            'win_rate': round(win_rate, 2),
            'profit_pct': round(total_profit, 2),
            'profit_factor': round(profit_factor, 2),
            'draw_down': round(draw_down, 2),
            'sharpe': round(total_profit / max(draw_down, 1), 2) if total_profit != 0 else 0,
            'trades_list': completed_trades[-200:]
        }

# ======================== BINANCE API ENDPOINTS ========================

@app.get("/api/binance/symbols")
async def get_binance_symbols():
    """Lấy danh sách symbol phổ biến từ Binance"""
    try:
        fetcher = get_binance_fetcher()
        symbols = fetcher.get_available_symbols()
        return {
            'status': 'success',
            'symbols': symbols,
            'count': len(symbols)
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/binance/timeframes")
async def get_binance_timeframes():
    """Lấy danh sách timeframe khả dụng"""
    try:
        fetcher = get_binance_fetcher()
        timeframes = fetcher.get_timeframes()
        return {
            'status': 'success',
            'timeframes': timeframes
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/binance/fetch")
async def fetch_binance_data(request: BinanceRequest):
    """Lấy OHLCV data từ Binance
    
    Can use either:
    - limit: Number of candles to fetch (50-10000)
    - start_date and end_date: Date range (format: 'YYYY-MM-DD' or 'YYYY-MM-DD HH:MM:SS')
    """
    try:
        if not request.symbol or not request.timeframe:
            raise ValueError("symbol và timeframe không được để trống")
        
        # Validate: must have either limit OR date range
        has_limit = request.limit is not None
        has_date_range = request.start_date is not None and request.end_date is not None
        
        if not has_limit and not has_date_range:
            raise ValueError("Either 'limit' or both 'start_date' and 'end_date' must be provided")
        
        if has_limit and (request.limit < 50 or request.limit > 10000):
            raise ValueError("limit phải từ 50 đến 10000")
        
        if has_date_range:
            # Validate that start_date is before end_date
            from datetime import datetime
            try:
                start_dt = datetime.strptime(request.start_date.split()[0], '%Y-%m-%d')
                end_dt = datetime.strptime(request.end_date.split()[0], '%Y-%m-%d')
                if start_dt >= end_dt:
                    raise ValueError("start_date phải trước end_date")
            except ValueError as e:
                raise ValueError(f"Invalid date format: {str(e)}")
        
        fetcher = get_binance_fetcher()
        
        # Validate symbol
        if not fetcher.validate_symbol(request.symbol):
            raise ValueError(f"Symbol không hợp lệ: {request.symbol}")
        
        # Fetch data - pass start_date and end_date if provided
        fetch_kwargs = {
            'symbol': request.symbol,
            'timeframe': request.timeframe,
        }
        
        # Only pass limit if provided (not None)
        if request.limit is not None:
            fetch_kwargs['limit'] = request.limit
        
        # Pass start_date and end_date if provided
        if request.start_date:
            fetch_kwargs['start_date'] = request.start_date
        if request.end_date:
            fetch_kwargs['end_date'] = request.end_date
        
        ohlcv_data = fetcher.fetch_ohlcv(**fetch_kwargs)
        
        if not ohlcv_data:
            raise ValueError(f"Không thể lấy data cho {request.symbol}")
        
        from datetime import datetime
        
        response = {
            'status': 'success',
            'symbol': request.symbol,
            'timeframe': request.timeframe,
            'count': len(ohlcv_data),
            'ohlcv_data': ohlcv_data,
            'fetched_at': datetime.now().isoformat(),
            'start_date': request.start_date,
            'end_date': request.end_date
        }
        
        return response
    
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/binance/symbol-info/{symbol}")
async def get_symbol_info(symbol: str):
    """Lấy thông tin symbol"""
    try:
        fetcher = get_binance_fetcher()
        info = fetcher.get_symbol_info(symbol)
        
        if not info:
            raise HTTPException(status_code=404, detail=f"Symbol không tìm thấy: {symbol}")
        
        return {
            'status': 'success',
            'data': info
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ======================== VNSTOCK ENDPOINTS ========================

@app.get("/api/vnstock/symbols")
async def get_vnstock_symbols(asset_type: str = 'stock'):
    """Lấy danh sách mã cổ phiếu hoặc phái sinh Việt Nam
    
    Args:
        asset_type: 'stock' (cổ phiếu) hoặc 'derivative' (phái sinh)
    """
    if not VNSTOCK_AVAILABLE:
        # Return fallback symbols instead of 503 error
        if asset_type == 'derivative':
            fallback_symbols = [
                'VN30F1M', 'VN30F2M', 'VN30F3M',
                'HNX30F1M', 'HNX30F2M', 'HNX30F3M',
                'VN30F2401', 'VN30F2402', 'VN30F2403',
            ]
        else:
            fallback_symbols = [
                'VCB', 'VIC', 'VHM', 'VRE', 'VNM', 'HPG', 'MSN', 'TCB',
                'BID', 'CTG', 'VPB', 'SSI', 'FPT', 'VJC', 'MWG', 'PNJ',
                'GAS', 'PLX', 'POW', 'GVR', 'VSH', 'VGC', 'VCI', 'VND',
                'ACB', 'TPB', 'STB', 'HDB', 'MBB', 'EIB', 'SHB', 'OCB'
            ]
        return {
            'status': 'warning',
            'symbols': fallback_symbols,
            'count': len(fallback_symbols),
            'asset_type': asset_type,
            'message': 'vnstock library chưa được cài đặt. Đang dùng danh sách mã mặc định. Để sử dụng đầy đủ, chạy: pip install vnstock'
        }
    
    try:
        fetcher = get_vnstock_fetcher()
        if asset_type == 'derivative':
            symbols = fetcher.get_derivatives_symbols()
        else:
            symbols = fetcher.get_available_symbols()
        return {
            'status': 'success',
            'symbols': symbols,
            'count': len(symbols),
            'asset_type': asset_type
        }
    except ImportError as e:
        # vnstock not available
        fallback_symbols = [
            'VCB', 'VIC', 'VHM', 'VRE', 'VNM', 'HPG', 'MSN', 'TCB',
            'BID', 'CTG', 'VPB', 'SSI', 'FPT', 'VJC', 'MWG', 'PNJ',
            'GAS', 'PLX', 'POW', 'GVR', 'VSH', 'VGC', 'VCI', 'VND',
            'ACB', 'TPB', 'STB', 'HDB', 'MBB', 'EIB', 'SHB', 'OCB'
        ]
        return {
            'status': 'warning',
            'symbols': fallback_symbols,
            'count': len(fallback_symbols),
            'message': f'vnstock error: {str(e)}. Using fallback symbols.'
        }
    except Exception as e:
        # Other errors (network, API issues, outside trading hours, etc.)
        import traceback
        error_detail = str(e)
        print(f"[VNStock Error] {error_detail}")
        traceback.print_exc()
        
        # Use fallback symbols on any error
        fallback_symbols = [
            'VCB', 'VIC', 'VHM', 'VRE', 'VNM', 'HPG', 'MSN', 'TCB',
            'BID', 'CTG', 'VPB', 'SSI', 'FPT', 'VJC', 'MWG', 'PNJ',
            'GAS', 'PLX', 'POW', 'GVR', 'VSH', 'VGC', 'VCI', 'VND',
            'ACB', 'TPB', 'STB', 'HDB', 'MBB', 'EIB', 'SHB', 'OCB'
        ]
        return {
            'status': 'warning',
            'symbols': fallback_symbols,
            'count': len(fallback_symbols),
            'message': f'Không thể tải từ vnstock API. Có thể do: (1) Không trong giờ giao dịch, (2) Lỗi mạng, (3) API tạm thời không khả dụng. Đang dùng danh sách mã mặc định. Lỗi: {error_detail}'
        }


@app.get("/api/vnstock/timeframes")
async def get_vnstock_timeframes():
    """Lấy danh sách timeframe khả dụng cho chứng khoán VN"""
    if not VNSTOCK_AVAILABLE:
        # Return fallback timeframes instead of 503 error
        fallback_timeframes = {
            '1': '1 phút',
            '5': '5 phút',
            '15': '15 phút',
            '30': '30 phút',
            '1h': '1 giờ',
            '1d': '1 ngày',
            '1w': '1 tuần',
            '1M': '1 tháng'
        }
        return {
            'status': 'warning',
            'timeframes': fallback_timeframes,
            'message': 'vnstock library chưa được cài đặt. Đang dùng danh sách timeframe mặc định. Để sử dụng đầy đủ, chạy: pip install vnstock'
        }
    
    try:
        fetcher = get_vnstock_fetcher()
        timeframes = fetcher.get_timeframes()
        return {
            'status': 'success',
            'timeframes': timeframes
        }
    except ImportError as e:
        # vnstock not available
        fallback_timeframes = {
            '1': '1 phút',
            '5': '5 phút',
            '15': '15 phút',
            '30': '30 phút',
            '1h': '1 giờ',
            '1d': '1 ngày',
            '1w': '1 tuần',
            '1M': '1 tháng'
        }
        return {
            'status': 'warning',
            'timeframes': fallback_timeframes,
            'message': f'vnstock error: {str(e)}. Using fallback timeframes.'
        }
    except Exception as e:
        # Other errors
        import traceback
        error_detail = str(e)
        print(f"[VNStock Error] {error_detail}")
        traceback.print_exc()
        
        fallback_timeframes = {
            '1': '1 phút',
            '5': '5 phút',
            '15': '15 phút',
            '30': '30 phút',
            '1h': '1 giờ',
            '1d': '1 ngày',
            '1w': '1 tuần',
            '1M': '1 tháng'
        }
        return {
            'status': 'warning',
            'timeframes': fallback_timeframes,
            'message': f'Không thể tải từ vnstock API. Có thể do: (1) Không trong giờ giao dịch, (2) Lỗi mạng, (3) API tạm thời không khả dụng. Đang dùng danh sách timeframe mặc định. Lỗi: {error_detail}'
        }


@app.post("/api/vnstock/fetch")
async def fetch_vnstock_data(request: BinanceRequest):
    """Lấy OHLCV data từ chứng khoán Việt Nam
    
    Can use either:
    - limit: Number of candles to fetch (50-10000)
    - start_date and end_date: Date range (format: 'YYYY-MM-DD' or 'YYYY-MM-DD HH:MM:SS')
    """
    # Debug: log request details
    print(f"[VNStock Fetch] Received request: symbol={request.symbol}, timeframe={request.timeframe}")
    print(f"[VNStock Fetch] limit={request.limit}, start_date={request.start_date}, end_date={request.end_date}")
    
    if not VNSTOCK_AVAILABLE:
        raise HTTPException(
            status_code=503, 
            detail="vnstock library chưa được cài đặt. Vui lòng chạy: pip install vnstock trong thư mục backend. Sau đó restart backend server."
        )
    
    try:
        # Validate required fields
        if not request.symbol or not request.timeframe:
            error_msg = f"symbol và timeframe không được để trống. Received: symbol={request.symbol}, timeframe={request.timeframe}"
            print(f"[VNStock Fetch] Validation error: {error_msg}")
            raise ValueError(error_msg)
        
        # Validate: must have either limit OR date range
        has_limit = request.limit is not None
        has_date_range = request.start_date is not None and request.end_date is not None
        
        if not has_limit and not has_date_range:
            error_msg = "Either 'limit' (50-10000) or both 'start_date' and 'end_date' must be provided"
            print(f"[VNStock Fetch] Validation error: {error_msg}")
            raise ValueError(error_msg)
        
        if has_limit and (request.limit < 50 or request.limit > 10000):
            error_msg = f"limit phải từ 50 đến 10000. Received: {request.limit}"
            print(f"[VNStock Fetch] Validation error: {error_msg}")
            raise ValueError(error_msg)
        
        if has_date_range:
            # Validate that start_date is before end_date
            from datetime import datetime
            try:
                start_dt = datetime.strptime(request.start_date.split()[0], '%Y-%m-%d')
                end_dt = datetime.strptime(request.end_date.split()[0], '%Y-%m-%d')
                if start_dt >= end_dt:
                    error_msg = f"start_date phải trước end_date. Received: start_date={request.start_date}, end_date={request.end_date}"
                    print(f"[VNStock Fetch] Validation error: {error_msg}")
                    raise ValueError(error_msg)
            except ValueError as e:
                error_msg = f"Invalid date format: {str(e)}. start_date={request.start_date}, end_date={request.end_date}"
                print(f"[VNStock Fetch] Validation error: {error_msg}")
                raise ValueError(error_msg)
        
        fetcher = get_vnstock_fetcher()
        
        # Validate symbol
        if not fetcher.validate_symbol(request.symbol):
            error_msg = f"Symbol không hợp lệ: {request.symbol}"
            print(f"[VNStock Fetch] Validation error: {error_msg}")
            raise ValueError(error_msg)
        
        # Fetch data - pass start_date and end_date if provided
        fetch_kwargs = {
            'symbol': request.symbol.upper(),  # Uppercase for Vietnam stocks
            'timeframe': request.timeframe,
        }
        
        # Only pass limit if provided (not None)
        if request.limit is not None:
            fetch_kwargs['limit'] = request.limit
        
        # Pass start_date and end_date if provided
        if request.start_date:
            fetch_kwargs['start_date'] = request.start_date
        if request.end_date:
            fetch_kwargs['end_date'] = request.end_date
        
        print(f"[VNStock Fetch] Calling fetcher.fetch_ohlcv with: {fetch_kwargs}")
        ohlcv_data = fetcher.fetch_ohlcv(**fetch_kwargs)
        
        if not ohlcv_data:
            error_msg = f"Không thể lấy data cho {request.symbol}. Có thể do: (1) Mã không tồn tại, (2) Không trong giờ giao dịch, (3) API tạm thời không khả dụng"
            print(f"[VNStock Fetch] Error: {error_msg}")
            raise ValueError(error_msg)
        
        from datetime import datetime
        
        response = {
            'status': 'success',
            'symbol': request.symbol,
            'timeframe': request.timeframe,
            'count': len(ohlcv_data),
            'ohlcv_data': ohlcv_data,
            'fetched_at': datetime.now().isoformat(),
            'start_date': request.start_date,
            'end_date': request.end_date
        }
        
        print(f"[VNStock Fetch] Success: fetched {len(ohlcv_data)} candles for {request.symbol}")
        return response
    
    except ValueError as e:
        error_detail = str(e)
        print(f"[VNStock Fetch] ValueError (400): {error_detail}")
        raise HTTPException(status_code=400, detail=error_detail)
    except Exception as e:
        import traceback
        error_detail = str(e)
        print(f"[VNStock Fetch] Exception (500): {error_detail}")
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"Internal server error: {error_detail}")


@app.get("/api/vnstock/derivatives/symbols")
async def get_vnstock_derivatives_symbols():
    """Lấy danh sách mã phái sinh Việt Nam"""
    if not VNSTOCK_AVAILABLE:
        # Return fallback derivatives symbols
        from datetime import datetime
        current_date = datetime.now()
        current_year = current_date.year % 100
        current_month = current_date.month
        
        fallback_derivatives = []
        for month_offset in range(0, 6):
            month = (current_month + month_offset - 1) % 12 + 1
            year = current_year + (current_month + month_offset - 1) // 12
            fallback_derivatives.append(f"VN30F{year:02d}{month:02d}")
            fallback_derivatives.append(f"HNX30F{year:02d}{month:02d}")
        
        return {
            'status': 'warning',
            'symbols': fallback_derivatives,
            'count': len(fallback_derivatives),
            'message': 'vnstock library chưa được cài đặt. Đang dùng danh sách phái sinh mặc định.'
        }
    
    try:
        fetcher = get_vnstock_fetcher()
        symbols = fetcher.get_derivatives_symbols()
        return {
            'status': 'success',
            'symbols': symbols,
            'count': len(symbols)
        }
    except Exception as e:
        import traceback
        error_detail = str(e)
        print(f"[VNStock Derivatives Error] {error_detail}")
        traceback.print_exc()
        
        # Fallback
        from datetime import datetime
        current_date = datetime.now()
        current_year = current_date.year % 100
        current_month = current_date.month
        
        fallback_derivatives = []
        for month_offset in range(0, 6):
            month = (current_month + month_offset - 1) % 12 + 1
            year = current_year + (current_month + month_offset - 1) // 12
            fallback_derivatives.append(f"VN30F{year:02d}{month:02d}")
            fallback_derivatives.append(f"HNX30F{year:02d}{month:02d}")
        
        return {
            'status': 'warning',
            'symbols': fallback_derivatives,
            'count': len(fallback_derivatives),
            'message': f'Không thể tải từ vnstock API. Đang dùng danh sách phái sinh mặc định. Lỗi: {error_detail}'
        }


@app.get("/api/vnstock/symbol-info/{symbol}")
async def get_vnstock_symbol_info(symbol: str):
    """Lấy thông tin mã cổ phiếu Việt Nam"""
    if not VNSTOCK_AVAILABLE:
        # Return basic info instead of 503
        return {
            'status': 'warning',
            'data': {
                'symbol': symbol.upper(),
                'name': '',
                'exchange': '',
                'sector': ''
            },
            'message': 'vnstock library chưa được cài đặt. Để lấy thông tin đầy đủ, chạy: pip install vnstock'
        }
    
    try:
        fetcher = get_vnstock_fetcher()
        info = fetcher.get_symbol_info(symbol.upper())
        
        if not info:
            raise HTTPException(status_code=404, detail=f"Symbol không tìm thấy: {symbol}")
        
        return {
            'status': 'success',
            'data': info
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ======================== DNSE/YFINANCE ENDPOINTS ========================

@app.get("/api/dnse/symbols")
async def get_dnse_symbols():
    """Lấy danh sách mã cổ phiếu Việt Nam (DNSE/yfinance)"""
    try:
        fetcher = get_dnse_fetcher()
        symbols = fetcher.get_available_symbols()
        return {
            'status': 'success',
            'symbols': symbols,
            'count': len(symbols)
        }
    except Exception as e:
        import traceback
        error_detail = str(e)
        print(f"[DNSE Error] {error_detail}")
        traceback.print_exc()
        
        fallback_symbols = [
            'VCB', 'VIC', 'VHM', 'VRE', 'VNM', 'HPG', 'MSN', 'TCB',
            'BID', 'CTG', 'VPB', 'SSI', 'FPT', 'VJC', 'MWG', 'PNJ',
            'GAS', 'PLX', 'POW', 'GVR', 'VSH', 'VGC', 'VCI', 'VND',
            'ACB', 'TPB', 'STB', 'HDB', 'MBB', 'EIB', 'SHB', 'OCB'
        ]
        return {
            'status': 'warning',
            'symbols': fallback_symbols,
            'count': len(fallback_symbols),
            'message': f'Không thể tải từ DNSE/yfinance. Đang dùng danh sách mã mặc định. Lỗi: {error_detail}'
        }


@app.get("/api/dnse/timeframes")
async def get_dnse_timeframes():
    """Lấy danh sách timeframe khả dụng cho DNSE/yfinance"""
    try:
        fetcher = get_dnse_fetcher()
        timeframes = fetcher.get_timeframes()
        return {
            'status': 'success',
            'timeframes': timeframes
        }
    except Exception as e:
        import traceback
        error_detail = str(e)
        print(f"[DNSE Error] {error_detail}")
        traceback.print_exc()
        
        fallback_timeframes = {
            '1': '1 phút',
            '5': '5 phút',
            '15': '15 phút',
            '30': '30 phút',
            '1h': '1 giờ',
            '1d': '1 ngày',
            '1w': '1 tuần',
            '1M': '1 tháng'
        }
        return {
            'status': 'warning',
            'timeframes': fallback_timeframes,
            'message': f'Không thể tải từ DNSE/yfinance. Đang dùng danh sách timeframe mặc định. Lỗi: {error_detail}'
        }


@app.post("/api/dnse/fetch")
async def fetch_dnse_data(request: BinanceRequest):
    """Lấy OHLCV data từ DNSE/yfinance"""
    try:
        fetcher = get_dnse_fetcher()
        
        symbol = request.symbol.upper()
        timeframe = request.timeframe
        
        # Validate symbol
        if not fetcher.validate_symbol(symbol):
            raise HTTPException(status_code=400, detail=f"Invalid symbol: {symbol}")
        
        # Fetch data
        if request.start_date and request.end_date:
            ohlcv_data = fetcher.fetch_ohlcv(
                symbol, timeframe,
                start_date=request.start_date,
                end_date=request.end_date
            )
        elif request.limit:
            ohlcv_data = fetcher.fetch_ohlcv(
                symbol, timeframe,
                limit=request.limit
            )
        else:
            ohlcv_data = fetcher.fetch_ohlcv(symbol, timeframe, limit=200)
        
        if not ohlcv_data:
            raise HTTPException(
                status_code=404,
                detail=f"Không tìm thấy data cho {symbol}. Có thể mã này không được hỗ trợ bởi yfinance hoặc cần thêm .VN suffix."
            )
        
        return {
            'status': 'success',
            'symbol': symbol,
            'timeframe': timeframe,
            'count': len(ohlcv_data),
            'ohlcv_data': ohlcv_data,
            'fetched_at': datetime.now().isoformat()
        }
    except HTTPException:
        raise
    except Exception as e:
        import traceback
        error_detail = str(e)
        print(f"[DNSE Fetch Error] {error_detail}")
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"Error fetching data: {error_detail}")


@app.get("/api/dnse/symbol-info/{symbol}")
async def get_dnse_symbol_info(symbol: str):
    """Lấy thông tin chi tiết mã cổ phiếu (DNSE/yfinance)"""
    try:
        fetcher = get_dnse_fetcher()
        info = fetcher.get_symbol_info(symbol)
        return {
            'status': 'success',
            **info
        }
    except Exception as e:
        return {
            'status': 'error',
            'symbol': symbol.upper(),
            'name': '',
            'exchange': '',
            'sector': '',
            'error': str(e)
        }


# ======================== API ENDPOINTS ========================

@app.get("/")
async def root():
    return {"message": "Combo Optimizer v1.4 Backend", "status": "running"}

@app.get("/health")
async def health_check():
    return {
        'status': 'ok',
        'version': '1.4.0',
        'port': 4000,
        'frontend': 'http://localhost:3000'
    }

@app.post("/optimize-stream")
async def optimize_stream(request: Request):
    """Run optimization with streaming progress updates"""
    try:
        body = await request.json()
        print(f"[DEBUG] Request body keys: {body.keys()}")
        print(f"[DEBUG] Full request: {json.dumps(body, indent=2)[:500]}")
        
        # Print to console for debugging (always visible)
        min_combo = body.get('minComboSize', body.get('min_combo_size', 'NOT PROVIDED'))
        max_combo = body.get('maxComboSize', body.get('max_combo_size', 'NOT PROVIDED'))
        print(f"[OPTIMIZATION] Received - minComboSize: {min_combo}, maxComboSize: {max_combo}")
        
        params = OptimizationParams(**body)
        print(f"[OPTIMIZATION] Parsed - min_combo_size: {params.min_combo_size}, max_combo_size: {params.max_combo_size}")
    except ValidationError as e:
        print(f"[ERROR] Validation error: {e}")
        raise HTTPException(status_code=422, detail=str(e))
    except Exception as e:
        print(f"[ERROR] Parse error: {e}")
        raise HTTPException(status_code=400, detail=str(e))
    
    async def progress_generator():
        try:
            data = [d.model_dump() for d in params.ohlcv_data]
            
            # Generate indicator variants (with multiple configs)
            base_indicators = indicator_manager.list_indicators()
            indicator_variants = []
            
            for ind_name in base_indicators:
                variants = generate_indicator_with_configs(ind_name)
                indicator_variants.extend(variants)
            
            print(f"[OPTIMIZATION] Generated {len(indicator_variants)} indicator variants from {len(base_indicators)} base indicators")
            
            # Generate combos from variants
            combos = []
            print(f"[OPTIMIZATION] Generating combos from size {params.min_combo_size} to {params.max_combo_size}")
            for size in range(params.min_combo_size, params.max_combo_size + 1):
                # Generate combinations of indicator variants
                size_combos = list(combinations(indicator_variants, size))
                
                # Filter: Don't allow same indicator with different configs in same combo
                filtered_combos = []
                for combo in size_combos:
                    combo_list = list(combo)
                    # Check if combo has duplicate base indicator names
                    base_names = [item['indicator_name'] for item in combo_list]
                    if len(base_names) == len(set(base_names)):  # No duplicates
                        filtered_combos.append(combo_list)
                
                combos.extend(filtered_combos)
                print(f"[OPTIMIZATION] Generated {len(filtered_combos)} combos of size {size} (filtered from {len(size_combos)})")
            
            if params.max_combos > 0:
                combos = combos[:params.max_combos]
            total_combos = len(combos)
            print(f"[OPTIMIZATION] Total combos to test: {total_combos} (size range: {params.min_combo_size} to {params.max_combo_size})")
            
            # Check GPU availability
            use_gpu = GPU_AVAILABLE and gpu.use_gpu
            if use_gpu:
                print(f"[OPTIMIZATION] GPU acceleration: ENABLED ({gpu.gpu_library})")
            else:
                print(f"[OPTIMIZATION] GPU acceleration: DISABLED (using CPU)")
            
            BacktestEngine._get_or_compute_signals(data, use_gpu=use_gpu)
            
            results = []
            for idx, combo in enumerate(combos):
                result = BacktestEngine.backtest_combo(
                    combo,
                    data,
                    params.threshold,
                    params.risk_percent,
                    params.rr_ratio,
                    params.sl_percent,
                    params.filters,
                    params.min_signal_ratio,
                    params.candle_confirmation,
                    params.capital,
                    params.enable_trailing_stop,
                    params.trailing_activation_r,
                    params.trailing_multiplier,
                    params.enable_partial_tp_close,
                    params.tp_close_pct
                )
                if result['trades'] > 0:
                    results.append(result)
                
                if (idx + 1) % 5 == 0 or idx == total_combos - 1:
                    progress = round(((idx + 1) / total_combos) * 100, 1)
                    yield f'data: {{"progress": {progress}, "tested": {idx + 1}, "with_trades": {len(results)}}}\n\n'
            
            results.sort(key=lambda x: x['profit_pct'], reverse=True)
            
            final_data = {
                'results': results[:100],
                'total_tested': total_combos,
                'total_with_trades': len(results),
                'progress': 100
            }
            yield f'data: {{"final": true, "data": {json.dumps(final_data)}}}\n\n'
        
        except Exception as e:
            import traceback
            traceback.print_exc()
            yield f'data: {{"error": "{str(e)}"}}\n\n'
    
    return StreamingResponse(progress_generator(), media_type="text/event-stream")

@app.post("/generate-pine-script")
async def generate_pine_script(request: Request):
    """Generate Pine Script code from indicator list (full strategy with signal logic)"""
    try:
        from strategy_models import Strategy, IndicatorConfig, SignalLogic, FilterConfig, RiskManagement
        
        # Parse request body - can be List[str] (old format) or dict with filters (new format)
        body = await request.json()
        
        # Handle both old format (list) and new format (dict)
        if isinstance(body, list):
            indicators = body
            filters_data = {}
        elif isinstance(body, dict):
            indicators = body.get('indicators', [])
            filters_data = body.get('filters', {})
        else:
            raise ValueError("Invalid request format. Expected list of indicators or dict with 'indicators' and 'filters'")
        
        # Create a temporary strategy from indicators
        indicator_configs = [
            IndicatorConfig(
                type=ind,
                config={},
                weight=1.0,
                enabled=True
            )
            for ind in indicators
        ]
        
        # Create FilterConfig from provided filters or use defaults
        filter_config = FilterConfig(
            enable_adx=filters_data.get('enable_adx', False),
            adx_threshold=filters_data.get('adx_threshold', 25.0),
            enable_volume=filters_data.get('enable_volume', False),
            volume_threshold=filters_data.get('volume_threshold', 1.5),
            enable_ma_filter=filters_data.get('enable_ma_filter', False),
            ma_period=filters_data.get('ma_period', 50),
            enable_atr_filter=filters_data.get('enable_atr_filter', False),
            min_atr=filters_data.get('min_atr', 0.0005),
            enable_trend_filter=filters_data.get('enable_trend_filter', False),
            trend_ma=filters_data.get('trend_ma', 200)
        )
        
        strategy = Strategy(
            name="Optimized Combo",
            description=f"Auto-generated from combo: {' + '.join(indicators)}",
            indicators=indicator_configs,
            signal_logic=SignalLogic(
                threshold_percent=filters_data.get('threshold', 70),
                candle_confirmation=filters_data.get('candle_confirmation', 2)  # Match combo optimizer default
            ),
            filters=filter_config,
            risk_management=RiskManagement(
                risk_percent=filters_data.get('risk_percent', 10.0),
                reward_ratio=filters_data.get('rr_ratio', 1.0),
                stop_loss_percent=filters_data.get('sl_percent', 5.0),
                capital=filters_data.get('capital', 1000)
            )
        )
        
        # Generate full strategy code
        result = pine_script_generator.generate(strategy)
        
        print(f"[generate-pine-script] Generated full strategy code for {len(indicators)} indicators")
        print(f"[generate-pine-script] Code length: {len(result.code)} characters")
        
        return {
            'status': 'success',
            'code': result.code,
            'indicators': indicators,
            'strategy_name': result.strategy_name
        }
    except Exception as e:
        import traceback
        error_msg = f"Error generating Pine Script: {str(e)}"
        print(f"[generate-pine-script] ERROR: {error_msg}")
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=error_msg)


# ======================== STRATEGY BUILDER ENDPOINTS ========================

@app.get("/api/indicators/list")
async def list_indicators():
    """List all available indicators with their configs"""
    try:
        indicators = indicator_manager.list_indicators()
        result = []
        
        for ind_name in indicators:
            config = indicator_manager.get_indicator_config(ind_name)
            result.append({
                'type': ind_name,
                'description': config.get('description', ''),
                'default_config': config
            })
        
        return {'indicators': result}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/strategy/validate")
async def validate_strategy(strategy: Strategy):
    """Validate strategy configuration"""
    try:
        # Basic validation
        if not strategy.indicators:
            raise ValueError("Strategy must have at least one indicator")
        
        enabled_count = sum(1 for ind in strategy.indicators if ind.enabled)
        if enabled_count == 0:
            raise ValueError("Strategy must have at least one enabled indicator")
        
        # Check indicator types are valid
        available = indicator_manager.list_indicators()
        for ind in strategy.indicators:
            if ind.type not in available:
                raise ValueError(f"Invalid indicator type: {ind.type}")
        
        return {'valid': True, 'message': 'Strategy is valid'}
    except Exception as e:
        return {'valid': False, 'message': str(e)}


@app.post("/api/strategy/preview")
async def preview_strategy_signals(request: BacktestRequest):
    """Preview signal count without full backtest"""
    try:
        data = [d.dict() if hasattr(d, 'dict') else d for d in request.ohlcv_data]
        strategy = request.strategy
        
        total_signals = 0
        long_signals = 0
        short_signals = 0
        
        # Quick loop to count signals
        for i in range(50, len(data)):
            direction, bull_pct, bear_pct, _ = StrategyEngine.calculate_signal(
                strategy, data, i
            )
            
            if direction:
                if StrategyEngine.apply_filters(strategy, data, i, direction):
                    total_signals += 1
                    if direction == 'LONG':
                        long_signals += 1
                    else:
                        short_signals += 1
        
        return {
            'total_signals': total_signals,
            'long_signals': long_signals,
            'short_signals': short_signals,
            'total_candles': len(data) - 50
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/strategy/backtest")
async def backtest_strategy(request: BacktestRequest):
    """Run full backtest on custom strategy"""
    try:
        data = request.ohlcv_data
        strategy = request.strategy
        
        # DEBUG: Log received parameters
        print("\n" + "="*70)
        print("BACKTEST REQUEST RECEIVED")
        print("="*70)
        print(f"Strategy: {strategy.name}")
        print(f"Risk Percent: {strategy.risk_management.risk_percent}%")
        print(f"Reward Ratio: {strategy.risk_management.reward_ratio}:1")
        print(f"Stop Loss: {strategy.risk_management.stop_loss_percent}%")
        print(f"Capital: ${strategy.risk_management.capital:,.2f}")
        print(f"Margin: {strategy.risk_management.margin}")
        print(f"OHLCV Data Points: {len(data)}")
        print("="*70 + "\n")
        
        # Run backtest
        result = StrategyEngine.backtest_strategy(strategy, data)
        
        # Result is already a dict from the engine
        return result
    except Exception as e:
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/strategy/save")
async def save_strategy(strategy: Strategy):
    """Save strategy to disk"""
    try:
        success = strategy_storage.save_strategy(strategy)
        if success:
            return {'status': 'success', 'message': f'Strategy "{strategy.name}" saved'}
        else:
            raise HTTPException(status_code=500, detail="Failed to save strategy")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/strategy/list")
async def list_strategies():
    """List all saved strategies"""
    try:
        strategies = strategy_storage.list_strategies()
        return {'strategies': [s.model_dump() for s in strategies]}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/strategy/upload")
async def upload_strategy(request: Request):
    """Upload strategy from JSON body"""
    try:
        data = await request.json()
        
        if 'name' not in data:
            raise HTTPException(status_code=400, detail='Strategy name required')
        
        strategy_name = data['name']
        
        # Create strategy model and save using Strategy model
        strategy = Strategy(
            name=strategy_name,
            description=data.get('description', ''),
            indicators=data.get('indicators', []),
            signal_logic=data.get('signal_logic', {}),
            filters=data.get('filters', {}),
            risk_management=data.get('risk_management', {})
        )
        success = strategy_storage.save_strategy(strategy)
        
        if success:
            return {
                'status': 'success',
                'strategy_name': strategy_name,
                'message': f'Strategy "{strategy_name}" uploaded'
            }
        else:
            raise HTTPException(status_code=500, detail='Failed to save strategy')
            
    except ValidationError as e:
        raise HTTPException(status_code=400, detail=f'Invalid strategy format: {str(e)}')
    except Exception as e:
        raise HTTPException(status_code=500, detail=f'Error uploading strategy: {str(e)}')


@app.get("/api/strategy/load/{name}")
async def load_strategy(name: str):
    """Load strategy by name"""
    try:
        strategy = strategy_storage.load_strategy(name)
        if strategy:
            return strategy.model_dump()
        else:
            raise HTTPException(status_code=404, detail=f'Strategy "{name}" not found')
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.delete("/api/strategy/delete/{name}")
async def delete_strategy(name: str):
    """Delete strategy by name"""
    try:
        success = strategy_storage.delete_strategy(name)
        if success:
            return {'status': 'success', 'message': f'Strategy "{name}" deleted'}
        else:
            raise HTTPException(status_code=404, detail=f'Strategy "{name}" not found')
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/strategy/export-pine")
async def export_pine_script(
    strategy: Strategy,
    backtest_result: Optional[Dict[str, Any]] = None,
    version: Optional[str] = None
):
    """Export strategy to Pine Script with optional backtest results and version"""
    try:
        result = pine_script_generator.generate(strategy, backtest_result, version)
        return result.model_dump()
    except Exception as e:
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))


class BacktestPineScriptRequest(BaseModel):
    """Request to backtest Pine Script code"""
    pine_code: str
    ohlcv_data: List[Dict[str, Any]]


@app.post("/api/strategy/backtest-pine")
async def backtest_pine_script(request: BacktestPineScriptRequest):
    """
    Parse Pine Script code and run backtest
    
    This endpoint:
    1. Parses Pine Script code to extract strategy parameters
    2. Converts to Strategy object
    3. Runs backtest using Python engine
    
    Note: This is a simplified parser. For full accuracy, you may need
    to manually verify the extracted parameters.
    """
    try:
        print("[backtest-pine] Parsing Pine Script code for backtesting...")
        
        # Parse Pine Script to Strategy
        strategy = PineScriptParser.parse_to_strategy(request.pine_code)
        
        print(f"[backtest-pine] Parsed strategy: {strategy.name}")
        print(f"[backtest-pine] Indicators: {[ind.type for ind in strategy.indicators]}")
        print(f"[backtest-pine] Threshold: {strategy.signal_logic.threshold_percent}%")
        print(f"[backtest-pine] Candle confirmation: {strategy.signal_logic.candle_confirmation}")
        
        # Convert ohlcv_data to list of dicts
        data = [d.dict() if hasattr(d, 'dict') else d for d in request.ohlcv_data]
        
        # Run backtest
        result = StrategyEngine.backtest_strategy(strategy, data)
        
        # StrategyEngine.backtest_strategy returns a dict, not a model
        # Just return it directly
        return {
            "status": "success",
            "strategy_name": strategy.name,
            "parsed_indicators": [ind.type for ind in strategy.indicators],
            "backtest_result": result
        }
        
    except Exception as e:
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"Failed to backtest Pine Script: {str(e)}")


class OptimizeStrategyRequest(BaseModel):
    """Request for strategy optimization"""
    ohlcv_data: List[Dict[str, Any]]
    combo_size: int = 2
    max_combos: Optional[int] = None
    # Use filters and risk management from base strategy
    filters: Dict[str, Any] = {}
    risk_management: Dict[str, Any] = {}


@app.post("/api/strategy/optimize")
async def optimize_strategy(request: OptimizeStrategyRequest):
    """Optimize strategy by testing all indicator combinations - similar to Combo Optimizer"""
    try:
        # Use same indicator list as Strategy Builder (from indicator_manager)
        indicators = indicator_manager.list_indicators()
        
        print(f"[STRATEGY OPTIMIZE] Testing with {len(indicators)} indicators, combo_size={request.combo_size}")
        
        # Generate all combinations
        from itertools import combinations
        all_combos = []
        for combo_tuple in combinations(indicators, request.combo_size):
            all_combos.append(list(combo_tuple))
        
        total_combos = len(all_combos)
        print(f"[STRATEGY OPTIMIZE] Total combinations: {total_combos}")
        
        # Limit combos if specified
        if request.max_combos and request.max_combos > 0:
            all_combos = all_combos[:request.max_combos]
            print(f"[STRATEGY OPTIMIZE] Limited to {len(all_combos)} combos")
        
        # Parse filters and risk from request
        filters_dict = request.filters if request.filters else {}
        risk_dict = request.risk_management if request.risk_management else {}
        
        # Extract parameters
        threshold = 70  # Default threshold
        risk_percent = risk_dict.get('risk_percent', 10.0)
        rr_ratio = risk_dict.get('reward_ratio', 1.0)
        sl_percent = risk_dict.get('stop_loss_percent', 5.0)
        capital = risk_dict.get('capital', 1000.0)
        
        # Convert data format
        data = [d if isinstance(d, dict) else d.dict() if hasattr(d, 'dict') else d for d in request.ohlcv_data]
        
        # Pre-compute signals (same as Combo Optimizer)
        use_gpu = GPU_AVAILABLE and gpu.use_gpu
        BacktestEngine._get_or_compute_signals(data, use_gpu=use_gpu)
        
        # Test multiple thresholds (like testing different configs)
        thresholds = [50, 55, 60, 65, 70, 75, 80]
        
        results = []
        tested = 0
        
        for combo_idx, combo in enumerate(all_combos):
            for threshold in thresholds:
                tested += 1
                
                # Use same backtest logic as Combo Optimizer
                result = BacktestEngine.backtest_combo(
                    combo,
                    data,
                    threshold,
                    risk_percent,
                    rr_ratio,
                    sl_percent,
                    filters_dict,
                    min_signal_ratio=50,  # Default
                    candle_confirmation=2,  # Default
                    capital=capital,
                    enable_trailing_stop=True,  # Default
                    trailing_activation_r=1.0,  # Default
                    trailing_multiplier=1.5,  # Default
                    enable_partial_tp_close=False,  # Default
                    tp_close_pct=0.5  # Default
                )
                
                if result['trades'] > 0:
                    results.append({
                        'combo': '+'.join(combo),  # Same format as Combo Optimizer
                        'combo_name': '+'.join(combo),
                        'indicators': [
                            {'type': ind, 'config': {}, 'weight': 1.0}
                            for ind in combo
                        ],
                        'threshold': threshold,
                        'trades': result['trades'],
                        'wins': result['wins'],
                        'losses': result['losses'],
                        'win_rate': result['win_rate'],
                        'profit_pct': result['profit_pct'],
                        'profit_factor': result['profit_factor'],
                        'draw_down': result['draw_down'],
                        'sharpe': result['sharpe'],
                        # For compatibility
                        'total_trades': result['trades'],
                        'sharpe_ratio': result['sharpe'],
                        'max_drawdown': result['draw_down']
                    })
            
            # Progress update
            if (combo_idx + 1) % 10 == 0:
                print(f"[STRATEGY OPTIMIZE] Progress: {combo_idx+1}/{len(all_combos)} combos, {tested} tests, {len(results)} results")
        
        print(f"[STRATEGY OPTIMIZE] Completed: {tested} tests, {len(results)} results")
        
        # Sort by profit
        results.sort(key=lambda x: x['profit_pct'], reverse=True)
        
        return {
            'total_results': len(results),
            'total_tested': tested,
            'top_combos': results[:10]  # Top 10
        }
        
    except Exception as e:
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))


# ======================== LIVE TRADING ENDPOINTS ========================

class LiveTradingStartRequest(BaseModel):
    symbol: str
    timeframe: str
    strategy_name: str
    initial_balance: float
    risk_percent: float  # % vốn mỗi lệnh
    margin: float = 1.0  # Margin ratio
    stoploss_percent: float = 2.0  # Fixed SL %
    reversal_strength_threshold: float = 70.0
    max_positions: int = 1


class LiveTradingStartPineRequest(BaseModel):
    """Request to start live trading with Pine Script code"""
    symbol: str
    timeframe: str
    pine_code: str
    initial_balance: float
    risk_percent: float = 10.0  # % vốn mỗi lệnh
    margin: float = 1.0  # Margin ratio
    stoploss_percent: float = 2.0  # Fixed SL %
    reversal_strength_threshold: float = 70.0
    max_positions: int = 1


@app.post("/api/live-trading/start")
async def start_live_trading(request: LiveTradingStartRequest):
    """Start live trading session"""
    try:
        engine = get_live_trading_engine()
        
        config = TradingConfig(
            symbol=request.symbol,
            timeframe=request.timeframe,
            strategy_name=request.strategy_name,
            initial_balance=request.initial_balance,
            risk_percent=request.risk_percent,
            margin=request.margin,
            stoploss_percent=request.stoploss_percent,
            reversal_strength_threshold=request.reversal_strength_threshold,
            max_positions=request.max_positions,
        )
        
        success = engine.initialize(config)
        if success:
            state_dict = engine.get_state()
            return {"status": "started", "state": state_dict}
        else:
            raise HTTPException(status_code=400, detail="Failed to initialize trading engine")
    
    except HTTPException:
        raise
    except Exception as e:
        print(f"Error in start_live_trading: {e}")
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/live-trading/start-pine")
async def start_live_trading_pine(request: LiveTradingStartPineRequest):
    """Start live trading session with Pine Script code"""
    try:
        print("[start-pine] Parsing Pine Script code for live trading...")
        
        # Parse Pine Script to Strategy
        strategy = PineScriptParser.parse_to_strategy(request.pine_code)
        
        print(f"[start-pine] Parsed strategy: {strategy.name}")
        print(f"[start-pine] Indicators: {[ind.type for ind in strategy.indicators]}")
        print(f"[start-pine] Threshold: {strategy.signal_logic.threshold_percent}%")
        
        # Initialize engine with strategy
        engine = get_live_trading_engine()
        
        # Use strategy's risk management if available, otherwise use request params
        risk_pct = request.risk_percent if request.risk_percent else strategy.risk_management.risk_percent
        sl_pct = request.stoploss_percent if request.stoploss_percent else strategy.risk_management.stop_loss_percent
        
        config = TradingConfig(
            symbol=request.symbol,
            timeframe=request.timeframe,
            strategy_name=strategy.name,  # Use parsed strategy name
            initial_balance=request.initial_balance,
            risk_percent=risk_pct,
            margin=request.margin,
            stoploss_percent=sl_pct,
            reversal_strength_threshold=request.reversal_strength_threshold,
            max_positions=request.max_positions,
        )
        
        # Initialize with strategy object directly
        success = engine.initialize(config, strategy=strategy)
        if success:
            state_dict = engine.get_state()
            return {
                "status": "started",
                "state": state_dict,
                "strategy_name": strategy.name,
                "parsed_indicators": [ind.type for ind in strategy.indicators]
            }
        else:
            raise HTTPException(status_code=400, detail="Failed to initialize trading engine")
    
    except HTTPException:
        raise
    except Exception as e:
        print(f"Error in start_live_trading_pine: {e}")
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"Failed to start live trading with Pine Script: {str(e)}")


@app.get("/api/live-trading/status")
async def get_live_trading_status():
    """Get current trading status"""
    try:
        engine = get_live_trading_engine()
        state = engine.get_state()
        if not state:
            return {"status": "not_started"}
        return {"status": "running", "state": state}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/live-trading/update")
async def update_live_trading():
    """Update trading (fetch latest data, check signals, execute trades)"""
    try:
        engine = get_live_trading_engine()
        result = engine.update()
        return {"status": "success", "result": result, "state": engine.get_state()}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/live-trading/stop")
async def stop_live_trading():
    """Stop live trading"""
    try:
        engine = get_live_trading_engine()
        engine.stop()
        return {"status": "stopped", "state": engine.get_state()}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/live-trading/pause")
async def pause_live_trading():
    """Pause live trading"""
    try:
        engine = get_live_trading_engine()
        engine.pause()
        return {"status": "paused", "state": engine.get_state()}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/live-trading/resume")
async def resume_live_trading():
    """Resume live trading"""
    try:
        engine = get_live_trading_engine()
        engine.resume()
        return {"status": "resumed", "state": engine.get_state()}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/live-trading/close-all")
async def close_all_live_positions():
    """Close all open positions"""
    try:
        engine = get_live_trading_engine()
        state = engine.get_state()
        
        if not state or not state.get("open_positions"):
            return {"status": "no_positions", "state": state}
        
        # Get current price (last closed price)
        current_price = state.get("state", {}).get("open_positions", [{}])[0].get("current_price", 0)
        if current_price == 0:
            raise HTTPException(status_code=400, detail="Cannot determine current price")
        
        engine.close_all_positions(current_price)
        return {"status": "all_closed", "state": engine.get_state()}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=4000)
