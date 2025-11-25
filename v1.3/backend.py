#!/usr/bin/env python3
"""
Combo Optimizer v1.3 Backend
FastAPI server for indicator calculation and strategy backtesting
"""

from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.responses import JSONResponse, StreamingResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import csv
import io
import json
from typing import List, Dict, Any, Optional
from datetime import datetime
import asyncio
from itertools import combinations
from indicators_improved import IndicatorCalculator, get_pine_script_code

app = FastAPI(title="Combo Optimizer v1.3 - IMPROVED", version="1.3.1")

# Enable CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
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
    risk_percent: float = 10.0  # 10% aggressive
    rr_ratio: float = 2.0  # ✅ OPTIMIZED: 4.0 → 2.0 (EMA pair works best at 2:1 ratio = +6% profit)
    sl_percent: float = 0.75  # ✅ OPTIMIZED: 2.0 → 0.75 (Tighter SL for EMA signals = +6% profit)
    filters: Dict[str, Any] = {}
    max_combos: int = 0  # 0 = test all, >0 = limit combos
    min_signal_ratio: int = 70  # Moderate signal quality threshold
    candle_confirmation: int = 2  # ✅ CC=2 is optimal (55.6% WR, +6% profit vs CC=1 which gives -2%)
    
    # Additional Filters - DISABLED (too restrictive, reduce signal count without profit gain)
    enable_adx_filter: bool = False
    adx_threshold: float = 25.0
    
    enable_volume_filter: bool = False  # Only entry when Volume > MA(20)
    volume_ma_period: int = 20
    
    enable_ma_filter: bool = False
    ma_period: int = 50
    
    # NEW: Improved Indicator System
    use_convergence_score: bool = True  # NEW: Use improved convergence detection
    convergence_confidence_min: str = 'MEDIUM'  # NEW: 'WEAK', 'MEDIUM', 'STRONG'

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

# ======================== INDICATORS ========================


# ======================== BACKTESTING ========================

class BacktestEngine:
    """Backtest strategy combinations"""
    
    # Cache for pre-calculated signals
    _signals_cache = None
    _cache_data_len = 0
    
    @staticmethod
    def _get_or_compute_signals(ohlcv_data: List[Dict]) -> List[Dict]:
        """Get cached signals or compute them once"""
        data_len = len(ohlcv_data)
        
        # If cache is valid, return it
        if BacktestEngine._signals_cache is not None and BacktestEngine._cache_data_len == data_len:
            return BacktestEngine._signals_cache
        
        # Otherwise compute all signals once
        print(f"[Cache] Computing signals for {data_len} candles...")
        all_signals = []
        for i in range(len(ohlcv_data)):
            signals = IndicatorCalculator.get_all_signals(ohlcv_data, i)
            all_signals.append(signals)
        
        BacktestEngine._signals_cache = all_signals
        BacktestEngine._cache_data_len = data_len
        print(f"[Cache] Signals cached successfully")
        return all_signals
    
    @staticmethod
    def backtest_combo(combo: List[str], ohlcv_data: List[Dict], threshold: int,
                      risk_pct: float, rr_ratio: float, sl_pct: float, filters: Dict, 
                      min_signal_ratio: int = 50, candle_confirmation: int = 2,
                      use_convergence_score: bool = True, convergence_confidence_min: str = 'MEDIUM') -> Dict:
        """Backtest a single indicator combination
        
        Args:
            combo: List of indicator names to use (e.g., ['RSI', 'MACD', 'Stochastic'])
            min_signal_ratio: Minimum % of signals needed to enter (50=50%, 100=100%)
            candle_confirmation: Number of consecutive candles with same signal to entry (1=sensitive, 2-3=normal, 4+=safe)
            use_convergence_score: NEW - Use improved convergence detection instead of simple counting
            convergence_confidence_min: NEW - Minimum confidence level for entry ('WEAK', 'MEDIUM', 'STRONG')
        """
        
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
        
        # Track consecutive signals for candle confirmation
        last_signal = None
        signal_count = 0
        
        # Get pre-calculated signals
        all_signals = BacktestEngine._get_or_compute_signals(ohlcv_data)
        
        # Map indicator names in combo to signal keys
        indicator_map = {
            'RSI': 'RSI',
            'MACD': 'MACD',
            'Stochastic': 'Stochastic',
            'BB_Upper': 'Bollinger_Bands',
            'BB_Lower': 'Bollinger_Bands',
            'Vol_MA': 'Volume_MA',
            'EMA_50': 'EMA_50',
            'EMA_200': 'EMA_200',
            'ADX': 'ADX',
            'CCI': 'CCI',
            'MFI': 'MFI',
            'ROC': 'ROC',
            'VROC': 'VROC',
            'RVI': 'RVI',
            'Donchian': 'Donchian',
            'AO': 'Awesome_Oscillator',
            'Momentum': 'Momentum',
            'ATR': 'ATR',
            'Pivot_R1': 'Pivot_Points',
            'OBV': 'OBV',
            'SuperTrend': 'SuperTrend'
        }
        
        for i in range(50, len(ohlcv_data) - 1):
            # Use cached signals instead of recalculating
            all_candle_signals = all_signals[i]
            
            # ==================== FILTER SIGNALS BY COMBO ====================
            # Only use signals from indicators in this combo
            combo_signals = {}
            for indicator_name in combo:
                signal_key = indicator_map.get(indicator_name, indicator_name)
                if signal_key in all_candle_signals:
                    combo_signals[signal_key] = all_candle_signals[signal_key]
            
            # ==================== IMPROVED SIGNAL DETECTION ====================
            # Count bullish vs bearish signals in the combo
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
            
            # Determine entry signal based on threshold
            entry_type = None
            if bullish_pct >= threshold:
                entry_type = 'LONG'
            elif bearish_pct >= threshold:
                entry_type = 'SHORT'
            
            # Check Additional Filters (ADX, Volume, MA)
            filter_passed = True
            
            if entry_type:
                # ADX Filter - only enter when trend is strong
                if filters.get('enable_adx_filter', False):
                    adx_val = all_candle_signals.get('ADX', {}).get('value', 0)
                    adx_threshold = filters.get('adx_threshold', 25)
                    if adx_val < adx_threshold:
                        filter_passed = False
                
                # Volume Filter - only enter when volume is high
                if filter_passed and filters.get('enable_volume_filter', False):
                    vol_ma_period = filters.get('volume_ma_period', 20)
                    if i >= vol_ma_period:
                        vol_ma = sum([ohlcv_data[j]['volume'] for j in range(i - vol_ma_period, i)]) / vol_ma_period
                        current_vol = ohlcv_data[i]['volume']
                        if current_vol < vol_ma:
                            filter_passed = False
                
                # MA Filter - price > MA for LONG, price < MA for SHORT
                if filter_passed and filters.get('enable_ma_filter', False):
                    ma_period = filters.get('ma_period', 50)
                    if i >= ma_period:
                        ma_val = sum([ohlcv_data[j]['close'] for j in range(i - ma_period, i)]) / ma_period
                        current_price = ohlcv_data[i]['close']
                        if entry_type == 'LONG' and current_price <= ma_val:
                            filter_passed = False
                        elif entry_type == 'SHORT' and current_price >= ma_val:
                            filter_passed = False
            
            # Track consecutive signals for candle confirmation filter
            if entry_type and entry_type == last_signal:
                signal_count += 1
            else:
                last_signal = entry_type
                signal_count = 1
            
            # Entry logic - only enter if candle_confirmation criteria met AND not same type as current AND filters passed
            # Prevent: LONG → LONG again, or SHORT → SHORT again
            # Allow: No position, or switch (LONG → SHORT or SHORT → LONG)
            should_enter = (
                entry_type and 
                filter_passed and
                signal_count >= candle_confirmation and
                (not current_position or current_position != entry_type)  # Allow switch
            )
            
            if should_enter and not current_position:
                # Normal entry (no existing position)
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
                # Switch position (exit current, enter new opposite)
                last_trade = trades_list[-1]
                current_close = ohlcv_data[i]['close']
                
                # Exit previous position at market price
                profit = current_close - last_trade['entry'] if current_position == 'LONG' else last_trade['entry'] - current_close
                profit_pct = (profit / last_trade['entry']) * 100
                
                last_trade['exit'] = round(current_close, 2)
                last_trade['exit_time'] = ohlcv_data[i].get('time', '')
                last_trade['profit'] = round(profit, 4)
                last_trade['profit_pct'] = round(profit_pct, 2)
                last_trade['exit_reason'] = 'Switch'  # Mark as position switch
                
                if profit > 0:
                    wins += 1
                
                balance += (profit_pct / 100) * (balance * risk_pct / 100)
                max_balance = max(max_balance, balance)
                min_balance = min(min_balance, balance)
                
                # Enter new opposite position
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
            
            # Exit logic - Priority: TP/SL > Signal reversal (Switch handled in entry)
            # IMPORTANT: Each trade exits ONLY ONCE. No double-exit.
            elif current_position and len(trades_list) > 0:
                last_trade = trades_list[-1]
                
                # Only process exit if trade has not been exited yet
                if last_trade.get('exit') is None:
                    current_high = ohlcv_data[i]['high']
                    current_low = ohlcv_data[i]['low']
                    current_close = ohlcv_data[i]['close']
                    
                    exit_price = None
                    exit_reason = None
                    
                    # Priority 1: Check TP hit FIRST (high reached for LONG, low reached for SHORT)
                    if current_position == 'LONG' and current_high >= last_trade['tp']:
                        exit_price = last_trade['tp']
                        exit_reason = 'TP'
                    elif current_position == 'SHORT' and current_low <= last_trade['tp']:
                        exit_price = last_trade['tp']
                        exit_reason = 'TP'
                    
                    # Priority 2: Check SL hit SECOND (low reached for LONG, high reached for SHORT)
                    # Only check if TP was not hit
                    if not exit_reason:
                        if current_position == 'LONG' and current_low <= last_trade['sl']:
                            exit_price = last_trade['sl']
                            exit_reason = 'SL'
                        elif current_position == 'SHORT' and current_high >= last_trade['sl']:
                            exit_price = last_trade['sl']
                            exit_reason = 'SL'
                    
                    # Execute exit if any condition met
                    # After exit, position is closed - Switch logic handles new entry
                    if exit_price and exit_reason:
                        profit = exit_price - last_trade['entry'] if current_position == 'LONG' else last_trade['entry'] - exit_price
                        profit_pct = (profit / last_trade['entry']) * 100
                        
                        last_trade['exit'] = round(exit_price, 2)
                        last_trade['exit_time'] = ohlcv_data[i].get('time', '')
                        last_trade['profit'] = round(profit, 4)
                        last_trade['profit_pct'] = round(profit_pct, 2)
                        last_trade['exit_reason'] = exit_reason
                        
                        if profit > 0:
                            wins += 1
                        
                        balance += (profit_pct / 100) * (balance * risk_pct / 100)
                        max_balance = max(max_balance, balance)
                        min_balance = min(min_balance, balance)
                        current_position = None  # Close position after exit
        
        # Close remaining position
        if current_position and len(trades_list) > 0:
            last_trade = trades_list[-1]
            exit_price = ohlcv_data[-1]['close']
            profit = exit_price - last_trade['entry'] if current_position == 'LONG' else last_trade['entry'] - exit_price
            profit_pct = (profit / last_trade['entry']) * 100
            
            last_trade['exit'] = round(exit_price, 2)
            last_trade['exit_time'] = ohlcv_data[-1].get('time', '')
            last_trade['profit'] = round(profit, 4)
            last_trade['profit_pct'] = round(profit_pct, 2)
            
            if profit > 0:
                wins += 1
        
        completed_trades = [t for t in trades_list if t['exit'] is not None]
        total_trades = len(completed_trades)
        losses = total_trades - wins
        
        win_rate = (wins / total_trades * 100) if total_trades > 0 else 0
        profit_factor = (wins / (losses or 1)) if losses > 0 else (wins if wins > 0 else 0)
        draw_down = ((max_balance - min_balance) / max_balance * 100) if max_balance > 0 else 0
        
        # Calculate total profit - ensure profit_pct is never None
        total_profit = sum([t.get('profit_pct', 0) or 0 for t in completed_trades])
        
        return {
            'combo': '+'.join(combo),
            'trades': total_trades,
            'wins': wins,
            'losses': losses,
            'win_rate': round(win_rate, 2),
            'profit_pct': round(total_profit, 2),
            'profit_factor': round(profit_factor, 2),
            'draw_down': round(draw_down, 2),
            'sharpe': round(total_profit / max(draw_down, 1), 2) if total_profit != 0 else 0,
            'trades_list': completed_trades[-200:]  # Limit to last 200 trades
        }

# Global variable to store OHLCV data
ohlcv_data = []

# ======================== API ENDPOINTS ========================

@app.post("/upload")
async def upload_csv(file: UploadFile = File(...)):
    """Upload and parse CSV file"""
    global ohlcv_data
    
    try:
        contents = await file.read()
        decoded = contents.decode('utf-8')
        reader = csv.DictReader(io.StringIO(decoded))
        
        ohlcv_data = []
        for row in reader:
            try:
                ohlcv_data.append({
                    'time': row.get('Date', row.get('time', '')),
                    'open': float(row.get('Open', row.get('open', 0))),
                    'high': float(row.get('High', row.get('high', 0))),
                    'low': float(row.get('Low', row.get('low', 0))),
                    'close': float(row.get('Close', row.get('close', 0))),
                    'volume': float(row.get('Volume', row.get('volume', 0)))
                })
            except (ValueError, KeyError):
                continue
        
        # Reset signal cache when new data is uploaded
        BacktestEngine._signals_cache = None
        BacktestEngine._cache_data_len = 0
        
        return {
            'status': 'success',
            'message': f'Loaded {len(ohlcv_data)} candles',
            'candles': len(ohlcv_data)
        }
    
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.post("/backtest")
async def backtest(params: OptimizationParams):
    """Run backtest on a combo"""
    global ohlcv_data
    
    if not ohlcv_data:
        raise HTTPException(status_code=400, detail="No data loaded. Upload CSV first.")
    
    try:
        # For now, just test with RSI + MACD
        test_combo = ['RSI', 'MACD']
        result = BacktestEngine.backtest_combo(
            test_combo,
            ohlcv_data,
            params.threshold,
            params.risk_pct,
            params.rr_ratio,
            params.sl_pct,
            params.filters
        )
        
        return result
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/optimize")
async def optimize(params: OptimizationParams):
    """Run full optimization with provided OHLCV data"""
    try:
        # Convert OHLCV objects to dict format for backtest engine
        data = [d.dict() for d in params.ohlcv_data]
        
        # All available indicators
        indicators = [
            'RSI', 'MACD', 'Stochastic', 'BB_Upper', 'BB_Lower',
            'Vol_MA', 'EMA_50', 'EMA_200', 'ADX', 'CCI',
            'MFI', 'ROC', 'VROC', 'RVI', 'Donchian',
            'AO', 'Momentum', 'ATR', 'Pivot_R1', 'OBV'
        ]
        
        # Generate combinations based on min/max size
        combos = []
        for size in range(params.min_combo_size, params.max_combo_size + 1):
            for combo in combinations(indicators, size):
                combos.append(list(combo))
        
        # Limit combos based on parameter (0 = test tất cả)
        if params.max_combos > 0:
            combos = combos[:params.max_combos]
        
        # Pre-calculate all signals once
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
                params.candle_confirmation,
                params.use_convergence_score,
                params.convergence_confidence_min
            )
            if result['trades'] > 0:  # Only keep combos with trades
                results.append(result)
        
        # Sort by win rate
        results.sort(key=lambda x: x['win_rate'], reverse=True)
        
        return {
            'results': results[:100],  # Top 100
            'total_tested': len(combos),
            'total_with_trades': len(results)
        }
    
    except Exception as e:
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"Optimization error: {str(e)}")

@app.post("/optimize-stream")
async def optimize_stream(params: OptimizationParams):
    """Run optimization with streaming progress updates"""
    async def progress_generator():
        try:
            # Convert OHLCV objects to dict format
            data = [d.dict() for d in params.ohlcv_data]
            
            # All available indicators
            indicators = [
                'RSI', 'MACD', 'Stochastic', 'BB_Upper', 'BB_Lower',
                'Vol_MA', 'EMA_50', 'EMA_200', 'ADX', 'CCI',
                'MFI', 'ROC', 'VROC', 'RVI', 'Donchian',
                'AO', 'Momentum', 'ATR', 'Pivot_R1', 'OBV'
            ]
            
            # Generate combinations
            combos = []
            for size in range(params.min_combo_size, params.max_combo_size + 1):
                for combo in combinations(indicators, size):
                    combos.append(list(combo))
            
            # Limit combos based on parameter (0 = test tất cả)
            if params.max_combos > 0:
                combos = combos[:params.max_combos]
            total_combos = len(combos)
            
            # Pre-calculate all signals once
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
                    params.candle_confirmation,
                    params.use_convergence_score,
                    params.convergence_confidence_min
                )
                if result['trades'] > 0:
                    results.append(result)
                
                # Send progress update every 2 combos
                if (idx + 1) % 2 == 0 or idx == total_combos - 1:
                    progress = round(((idx + 1) / total_combos) * 100, 1)
                    yield f'data: {{"progress": {progress}, "tested": {idx + 1}, "with_trades": {len(results)}}}\n\n'
            
            # Sort by win rate
            results.sort(key=lambda x: x['win_rate'], reverse=True)
            
            # Send final results
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
    """Generate Pine Script code from indicator list - synchronized with Python"""
    try:
        code = get_pine_script_code(indicators)
        return {
            'status': 'success',
            'code': code,
            'indicators': indicators,
            'note': 'Generated from Python indicators - synchronized with backtest engine'
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        'status': 'ok',
        'version': '1.3.1-improved',
        'features': [
            'Strength Score Indicators',
            'Convergence Detection',
            'Signal Caching',
            'Multiple Filters'
        ],
        'data_loaded': len(ohlcv_data) > 0,
        'candles': len(ohlcv_data)
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
