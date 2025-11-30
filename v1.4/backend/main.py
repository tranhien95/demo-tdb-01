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

# Strategy imports
from strategy_models import (
    Strategy, BacktestRequest, StrategyListItem, 
    IndicatorConfig, SignalDetail
)
from strategy_engine import StrategyEngine
from strategy_storage import strategy_storage
from pine_script_generator import pine_script_generator

app = FastAPI(title="Combo Optimizer v1.4 Backend", version="1.4.0")

# Enable CORS for React frontend (port 3000)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
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
        
        indicator_map = {
            'RSI': 'RSI',
            'MACD': 'MACD',
            'Stochastic': 'Stochastic',
            'Bollinger_Bands': 'Bollinger_Bands',
            'Volume_MA': 'Volume_MA',
            'EMA_50': 'EMA_50',
            'EMA_200': 'EMA_200',
            'EMA_12': 'EMA_12',
            'EMA_26': 'EMA_26',
            'ADX': 'ADX',
            'CCI': 'CCI',
            'MFI': 'MFI',
            'ROC': 'ROC',
            'VROC': 'VROC',
            'RVI': 'RVI',
            'Donchian': 'Donchian',
            'Awesome_Oscillator': 'Awesome_Oscillator',
            'Momentum': 'Momentum',
            'ATR': 'ATR',
            'Pivot_Points': 'Pivot_Points',
            'OBV': 'OBV',
            'SuperTrend': 'SuperTrend'
        }
        
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
            
            indicators = [
                'RSI', 'MACD', 'Stochastic', 'Bollinger_Bands',
                'Volume_MA', 'EMA_50', 'EMA_200', 'EMA_12', 'EMA_26',
                'ADX', 'CCI', 'MFI', 'ROC', 'VROC', 'RVI', 'Donchian',
                'Awesome_Oscillator', 'Momentum', 'ATR', 'Pivot_Points', 'OBV', 'SuperTrend'
            ]
            
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
    """Generate Pine Script code from indicator list"""
    try:
        code = get_pine_script_code(indicators)
        return {
            'status': 'success',
            'code': code,
            'indicators': indicators
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


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
        data = [d.dict() if hasattr(d, 'dict') else d for d in request.ohlcv_data]
        strategy = request.strategy
        
        # Run backtest
        result = StrategyEngine.backtest_strategy(strategy, data)
        
        return result.dict()
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
        return {'strategies': [s.dict() for s in strategies]}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/strategy/load/{name}")
async def load_strategy(name: str):
    """Load strategy by name"""
    try:
        strategy = strategy_storage.load_strategy(name)
        if strategy:
            return strategy.dict()
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
async def export_pine_script(strategy: Strategy):
    """Export strategy to Pine Script"""
    try:
        result = pine_script_generator.generate(strategy)
        return result.dict()
    except Exception as e:
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=4000)
