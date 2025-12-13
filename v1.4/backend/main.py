#!/usr/bin/env python3
"""
Combo Optimizer v1.4 Backend
FastAPI server for indicator calculation and strategy backtesting
Port: 4000
"""

from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import StreamingResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, ValidationError
import json
from typing import List, Dict, Any, Optional
from itertools import combinations
from indicators import indicator_manager, get_all_signals, get_pine_script_code
from performance_metrics import PerformanceMetrics
from binance_fetcher import get_binance_fetcher

# Strategy imports
from strategy_models import (
    Strategy, BacktestRequest, StrategyListItem, 
    IndicatorConfig, SignalDetail
)
from strategy_engine import StrategyEngine
from strategy_storage import strategy_storage
from pine_script_generator import pine_script_generator

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
    limit: int = 200

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
    def _get_or_compute_signals(ohlcv_data: List[Dict]) -> List[Dict]:
        """Get cached signals or compute them once"""
        data_len = len(ohlcv_data)
        
        if BacktestEngine._signals_cache is not None and BacktestEngine._cache_data_len == data_len:
            return BacktestEngine._signals_cache
        
        print(f"[Cache] Computing signals for {data_len} candles...")
        all_signals = []
        for i in range(len(ohlcv_data)):
            signals = get_all_signals(ohlcv_data, i)
            all_signals.append(signals)
        
        BacktestEngine._signals_cache = all_signals
        BacktestEngine._cache_data_len = data_len
        print(f"[Cache] Signals cached successfully")
        return all_signals
    
    @staticmethod
    def backtest_combo(combo: List[str], ohlcv_data: List[Dict], threshold: int,
                      risk_pct: float, rr_ratio: float, sl_pct: float, filters: Dict, 
                      min_signal_ratio: int = 50, candle_confirmation: int = 2) -> Dict:
        """Backtest a single indicator combination"""
        
        if not ohlcv_data or len(ohlcv_data) < 50:
            return {
                'combo': '+'.join(combo),
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
        balance = 100
        max_balance = 100
        min_balance = 100
        wins = 0
        current_position = None
        
        last_signal = None
        signal_count = 0
        
        all_signals = BacktestEngine._get_or_compute_signals(ohlcv_data)
        
        # Dynamic indicator map from indicator_manager (same as Strategy Builder)
        available_indicators = indicator_manager.list_indicators()
        indicator_map = {ind: ind for ind in available_indicators}
        
        for i in range(50, len(ohlcv_data) - 1):
            all_candle_signals = all_signals[i]
            
            combo_signals = {}
            for indicator_name in combo:
                signal_key = indicator_map.get(indicator_name, indicator_name)
                if signal_key in all_candle_signals:
                    combo_signals[signal_key] = all_candle_signals[signal_key]
            
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
                
                trades_list.append({
                    'entry': round(entry, 2),
                    'exit': None,
                    'sl': round(sl, 2),
                    'tp': round(tp, 2),
                    'profit': None,
                    'profit_pct': None,
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
                # Risk is based on INITIAL capital (100), position = risk / SL%
                initial_capital = 100
                risk_amount = initial_capital * (risk_pct / 100)
                position_size = risk_amount / (sl_pct / 100)
                actual_profit_usd = position_size * (profit_pct / 100)
                
                last_trade['exit'] = round(current_close, 2)
                last_trade['exit_time'] = ohlcv_data[i].get('time', '')
                last_trade['profit'] = round(actual_profit_usd, 4)  # USD profit
                last_trade['profit_pct'] = round(profit_pct, 2)
                last_trade['exit_reason'] = 'Switch'
                
                if profit > 0:
                    wins += 1
                
                # Update balance
                balance += actual_profit_usd
                max_balance = max(max_balance, balance)
                min_balance = min(min_balance, balance)
                
                entry = current_close
                sl = entry * (1 - sl_pct / 100) if entry_type == 'LONG' else entry * (1 + sl_pct / 100)
                tp = entry + (entry - sl) * rr_ratio if entry_type == 'LONG' else entry - (sl - entry) * rr_ratio
                
                trades_list.append({
                    'entry': round(entry, 2),
                    'exit': None,
                    'sl': round(sl, 2),
                    'tp': round(tp, 2),
                    'profit': None,
                    'profit_pct': None,
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
                        
                        # Calculate actual USD profit
                        initial_capital = 100
                        risk_amount = initial_capital * (risk_pct / 100)
                        position_size = risk_amount / (sl_pct / 100)
                        actual_profit_usd = position_size * (profit_pct / 100)
                        
                        last_trade['exit'] = round(exit_price, 2)
                        last_trade['exit_time'] = ohlcv_data[i].get('time', '')
                        last_trade['profit'] = round(actual_profit_usd, 4)  # USD profit
                        last_trade['profit_pct'] = round(profit_pct, 2)
                        last_trade['exit_reason'] = exit_reason
                        
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
                
                # Calculate actual USD profit
                initial_capital = 100
                risk_amount = initial_capital * (risk_pct / 100)
                position_size = risk_amount / (sl_pct / 100)
                actual_profit_usd = position_size * (profit_pct / 100)
                
                last_trade['exit'] = round(exit_price, 2)
                last_trade['exit_time'] = ohlcv_data[-1].get('time', '')
                last_trade['profit'] = round(actual_profit_usd, 4)  # USD profit
                last_trade['profit_pct'] = round(profit_pct, 2)
                
                if profit > 0:
                    wins += 1
        
        completed_trades = [t for t in trades_list if t['exit'] is not None]
        total_trades = len(completed_trades)
        losses = total_trades - wins
        
        win_rate = (wins / total_trades * 100) if total_trades > 0 else 0
        
        # Calculate actual portfolio return (not sum of individual trades)
        total_profit = ((balance - 100) / 100) * 100  # ROI% from initial 100
        
        # Use standardized performance metrics
        profit_factor = PerformanceMetrics.calculate_profit_factor(completed_trades)
        
        # Calculate max drawdown from balance tracking
        draw_down = ((max_balance - min_balance) / max_balance * 100) if max_balance > 0 else 0
        
        # Calculate Sharpe ratio properly
        sharpe = PerformanceMetrics.calculate_sharpe_ratio(completed_trades)
        
        return {
            'combo': ' + '.join(combo),
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
    """Lấy OHLCV data từ Binance"""
    try:
        if not request.symbol or not request.timeframe:
            raise ValueError("symbol và timeframe không được để trống")
        
        if request.limit < 50 or request.limit > 10000:
            raise ValueError("limit phải từ 50 đến 10000")
        
        fetcher = get_binance_fetcher()
        
        # Validate symbol
        if not fetcher.validate_symbol(request.symbol):
            raise ValueError(f"Symbol không hợp lệ: {request.symbol}")
        
        # Fetch data
        ohlcv_data = fetcher.fetch_ohlcv(
            request.symbol,
            request.timeframe,
            request.limit
        )
        
        if not ohlcv_data:
            raise ValueError(f"Không thể lấy data cho {request.symbol}")
        
        from datetime import datetime
        
        response = {
            'status': 'success',
            'symbol': request.symbol,
            'timeframe': request.timeframe,
            'count': len(ohlcv_data),
            'ohlcv_data': ohlcv_data,
            'fetched_at': datetime.now().isoformat()
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
        
        params = OptimizationParams(**body)
    except ValidationError as e:
        print(f"[ERROR] Validation error: {e}")
        raise HTTPException(status_code=422, detail=str(e))
    except Exception as e:
        print(f"[ERROR] Parse error: {e}")
        raise HTTPException(status_code=400, detail=str(e))
    
    async def progress_generator():
        try:
            data = [d.dict() for d in params.ohlcv_data]
            
            # Use same indicator list as Strategy Builder (from indicator_manager)
            indicators = indicator_manager.list_indicators()
            
            combos = []
            for size in range(params.min_combo_size, params.max_combo_size + 1):
                for combo in combinations(indicators, size):
                    combos.append(list(combo))
            
            if params.max_combos > 0:
                combos = combos[:params.max_combos]
            total_combos = len(combos)
            
            BacktestEngine._get_or_compute_signals(data)
            
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
                    params.candle_confirmation
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
async def generate_pine_script(indicators: List[str]):
    """Generate Pine Script code from indicator list (full strategy with signal logic)"""
    try:
        from strategy_models import Strategy, IndicatorConfig, SignalLogic, FilterConfig, RiskManagement
        
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
        
        strategy = Strategy(
            name="Optimized Combo",
            description=f"Auto-generated from combo: {' + '.join(indicators)}",
            indicators=indicator_configs,
            signal_logic=SignalLogic(threshold_percent=70),
            filters=FilterConfig(),
            risk_management=RiskManagement(
                risk_percent=10.0,
                reward_ratio=1.0,
                stop_loss_percent=5.0,
                capital=1000
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
        
        # Convert data format
        data = [d if isinstance(d, dict) else d.dict() if hasattr(d, 'dict') else d for d in request.ohlcv_data]
        
        # Pre-compute signals (same as Combo Optimizer)
        BacktestEngine._get_or_compute_signals(data)
        
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
                    candle_confirmation=2  # Default
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
