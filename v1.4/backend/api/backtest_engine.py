"""
Backtest Engine
Backtest strategy combinations for optimization
"""

from typing import List, Dict
from indicators import get_all_signals
from performance_metrics import PerformanceMetrics
from utils.logger import get_logger

logger = get_logger(__name__)


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
        
        logger.info(f"Computing signals for {data_len} candles...")
        all_signals = []
        for i in range(len(ohlcv_data)):
            signals = get_all_signals(ohlcv_data, i)
            all_signals.append(signals)
        
        BacktestEngine._signals_cache = all_signals
        BacktestEngine._cache_data_len = data_len
        logger.info(f"Signals cached successfully for {data_len} candles")
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

