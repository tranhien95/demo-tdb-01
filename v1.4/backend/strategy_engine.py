"""
Strategy Engine
Execute custom strategies with weighted indicators
"""

from typing import List, Dict, Any, Tuple
from strategy_models import (
    Strategy, BacktestResult, BacktestTrade, 
    SignalDetail, TradeSignal, IndicatorConfig
)
from indicators import indicator_manager
from indicators.base import HelperFunctions
import uuid


class StrategyEngine:
    """Execute and backtest custom strategies"""
    
    @staticmethod
    def calculate_signal(
        strategy: Strategy,
        data: List[Dict],
        index: int
    ) -> Tuple[str, float, float, List[SignalDetail]]:
        """
        Calculate signal for a candle
        
        Returns:
            (direction, bullish_percent, bearish_percent, signals_detail)
        """
        signals_detail = []
        total_weight = 0
        bullish_weight = 0
        bearish_weight = 0
        
        # Calculate each indicator
        for ind_config in strategy.indicators:
            if not ind_config.enabled:
                continue
            
            # Get indicator signal
            signal = indicator_manager.calculate_indicator(
                ind_config.type,
                data,
                index,
                **ind_config.config
            )
            
            # Handle None values - convert to False for boolean fields
            bullish = signal.get('bullish', False)
            bearish = signal.get('bearish', False)
            value = signal.get('value', 0)
            
            if bullish is None:
                bullish = False
            if bearish is None:
                bearish = False
            if value is None:
                value = 0
            
            # Calculate contribution
            weight = ind_config.weight
            total_weight += weight
            
            if bullish:
                bullish_weight += weight
            if bearish:
                bearish_weight += weight
            
            # Store detail
            signals_detail.append(SignalDetail(
                indicator_type=ind_config.type,
                indicator_id=ind_config.id,
                bullish=bullish,
                bearish=bearish,
                value=value,
                weight=weight,
                contribution_percent=(weight / total_weight * 100) if total_weight > 0 else 0,
                enabled=ind_config.enabled
            ))
        
        # Calculate percentages
        bullish_percent = (bullish_weight / total_weight * 100) if total_weight > 0 else 0
        bearish_percent = (bearish_weight / total_weight * 100) if total_weight > 0 else 0
        
        # Determine direction based on threshold
        threshold = strategy.signal_logic.threshold_percent
        
        if bullish_percent >= threshold:
            direction = 'LONG'
        elif bearish_percent >= threshold:
            direction = 'SHORT'
        else:
            direction = None
        
        return direction, bullish_percent, bearish_percent, signals_detail
    
    @staticmethod
    def apply_filters(
        strategy: Strategy,
        data: List[Dict],
        index: int,
        direction: str
    ) -> bool:
        """
        Apply filters to signal
        
        Returns:
            True if all enabled filters pass
        """
        filters = strategy.filters
        
        # ADX Filter
        if filters.enable_adx_filter:
            adx_signal = indicator_manager.calculate_indicator('ADX', data, index, period=14)
            if adx_signal.get('value', 0) < filters.adx_threshold:
                return False
        
        # Volume Filter
        if filters.enable_volume_filter:
            if index >= filters.volume_ma_period:
                vol_ma = sum([data[j]['volume'] for j in range(index - filters.volume_ma_period, index)]) / filters.volume_ma_period
                current_vol = data[index]['volume']
                if current_vol < vol_ma * filters.volume_multiplier:
                    return False
        
        # MA Trend Filter
        if filters.enable_ma_filter:
            if index >= filters.ma_period:
                ma_val = sum([data[j]['close'] for j in range(index - filters.ma_period, index)]) / filters.ma_period
                current_price = data[index]['close']
                if direction == 'LONG' and current_price <= ma_val:
                    return False
                elif direction == 'SHORT' and current_price >= ma_val:
                    return False
        
        # ATR Filter
        if filters.enable_atr_filter:
            atr_val = HelperFunctions.atr(data, index, filters.atr_period)
            if atr_val < filters.atr_min:
                return False
        
        # Trend Filter (EMA200)
        if filters.enable_trend_filter:
            if index >= filters.trend_ema_period:
                closes = [d['close'] for d in data[:index + 1]]
                ema_vals = HelperFunctions.ema(closes, filters.trend_ema_period)
                ema_val = ema_vals[index] if ema_vals[index] is not None else data[index]['close']
                
                if direction == 'LONG' and data[index]['close'] <= ema_val:
                    return False
                elif direction == 'SHORT' and data[index]['close'] >= ema_val:
                    return False
        
        return True
    
    @staticmethod
    def backtest_strategy(
        strategy: Strategy,
        ohlcv_data: List[Dict]
    ) -> BacktestResult:
        """
        Backtest a custom strategy
        
        Returns:
            BacktestResult with full details
        """
        data = ohlcv_data
        risk_pct = strategy.risk_management.risk_percent
        rr_ratio = strategy.risk_management.rr_ratio
        sl_pct = strategy.risk_management.sl_percent
        candle_confirmation = strategy.risk_management.candle_confirmation
        capital = strategy.risk_management.capital
        
        trades_list = []
        balance = capital
        max_balance = capital
        min_balance = capital
        wins = 0
        long_trades = 0
        short_trades = 0
        current_position = None
        
        last_signal = None
        signal_count = 0
        
        total_signals = 0
        long_signals = 0
        short_signals = 0
        equity_curve = [capital]  # Start with initial capital
        
        # Backtest loop
        for i in range(50, len(data) - 1):
            # Calculate signal
            direction, bull_pct, bear_pct, signals_detail = StrategyEngine.calculate_signal(
                strategy, data, i
            )
            
            # Count signals
            if direction:
                total_signals += 1
                if direction == 'LONG':
                    long_signals += 1
                else:
                    short_signals += 1
            
            # Apply filters
            if direction:
                filter_passed = StrategyEngine.apply_filters(strategy, data, i, direction)
                if not filter_passed:
                    direction = None
            
            # Candle confirmation
            if direction and direction == last_signal:
                signal_count += 1
            else:
                last_signal = direction
                signal_count = 1
            
            should_enter = (
                direction and
                signal_count >= candle_confirmation and
                (not current_position or current_position != direction)
            )
            
            # Enter trade
            if should_enter and not current_position:
                entry = data[i]['close']
                sl = entry * (1 - sl_pct / 100) if direction == 'LONG' else entry * (1 + sl_pct / 100)
                tp = entry + (entry - sl) * rr_ratio if direction == 'LONG' else entry - (sl - entry) * rr_ratio
                
                # Calculate position size
                risk_amount = balance * (risk_pct / 100)
                position_size = risk_amount
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
                    'type': direction,
                    'time': data[i].get('time', ''),
                    'exit_time': None,
                    'entry_signals': [s.dict() for s in signals_detail]
                })
                current_position = direction
                if direction == 'LONG':
                    long_trades += 1
                else:
                    short_trades += 1
            
            # Switch position
            elif should_enter and current_position and current_position != direction:
                last_trade = trades_list[-1]
                current_close = data[i]['close']
                
                profit = current_close - last_trade['entry'] if current_position == 'LONG' else last_trade['entry'] - current_close
                profit_pct = (profit / last_trade['entry']) * 100
                
                last_trade['exit'] = round(current_close, 2)
                last_trade['exit_time'] = data[i].get('time', '')
                last_trade['profit'] = round(profit, 4)
                last_trade['profit_pct'] = round(profit_pct, 2)
                last_trade['exit_reason'] = 'Switch'
                
                if profit > 0:
                    wins += 1
                
                balance += (profit_pct / 100) * (balance * risk_pct / 100)
                max_balance = max(max_balance, balance)
                min_balance = min(min_balance, balance)
                equity_curve.append(round(balance, 2))
                
                # Enter new position
                entry = current_close
                sl = entry * (1 - sl_pct / 100) if direction == 'LONG' else entry * (1 + sl_pct / 100)
                tp = entry + (entry - sl) * rr_ratio if direction == 'LONG' else entry - (sl - entry) * rr_ratio
                
                # Calculate position size
                risk_amount = balance * (risk_pct / 100)
                position_size = risk_amount
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
                    'type': direction,
                    'time': data[i].get('time', ''),
                    'exit_time': None,
                    'entry_signals': [s.dict() for s in signals_detail]
                })
                current_position = direction
            
            # Check SL/TP
            elif current_position and len(trades_list) > 0:
                last_trade = trades_list[-1]
                
                if last_trade.get('exit') is None:
                    current_high = data[i]['high']
                    current_low = data[i]['low']
                    
                    exit_price = None
                    exit_reason = None
                    
                    # Check TP
                    if current_position == 'LONG' and current_high >= last_trade['tp']:
                        exit_price = last_trade['tp']
                        exit_reason = 'TP'
                    elif current_position == 'SHORT' and current_low <= last_trade['tp']:
                        exit_price = last_trade['tp']
                        exit_reason = 'TP'
                    
                    # Check SL
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
                        
                        last_trade['exit'] = round(exit_price, 2)
                        last_trade['exit_time'] = data[i].get('time', '')
                        last_trade['profit'] = round(profit, 4)
                        last_trade['profit_pct'] = round(profit_pct, 2)
                        last_trade['exit_reason'] = exit_reason
                        
                        if profit > 0:
                            wins += 1
                        
                        balance += (profit_pct / 100) * (balance * risk_pct / 100)
                        max_balance = max(max_balance, balance)
                        min_balance = min(min_balance, balance)
                        equity_curve.append(round(balance, 2))
                        current_position = None
        
        # Close last trade if open
        if current_position and len(trades_list) > 0:
            last_trade = trades_list[-1]
            if last_trade.get('exit') is None:
                exit_price = data[-1]['close']
                profit = exit_price - last_trade['entry'] if current_position == 'LONG' else last_trade['entry'] - exit_price
                profit_pct = (profit / last_trade['entry']) * 100
                
                last_trade['exit'] = round(exit_price, 2)
                last_trade['exit_time'] = data[-1].get('time', '')
                last_trade['profit'] = round(profit, 4)
                last_trade['profit_pct'] = round(profit_pct, 2)
                last_trade['exit_reason'] = 'Close'
                
                if profit > 0:
                    wins += 1
        
        # Calculate stats
        completed_trades = [t for t in trades_list if t['exit'] is not None]
        total_trades = len(completed_trades)
        losses = total_trades - wins
        
        # Calculate profit factor correctly
        gross_profit = sum([t.get('profit', 0) for t in completed_trades if t.get('profit', 0) > 0])
        gross_loss = abs(sum([t.get('profit', 0) for t in completed_trades if t.get('profit', 0) < 0]))
        profit_factor = (gross_profit / gross_loss) if gross_loss > 0 else (gross_profit if gross_profit > 0 else 0)
        
        win_rate = (wins / total_trades * 100) if total_trades > 0 else 0
        draw_down = ((max_balance - min_balance) / max_balance * 100) if max_balance > 0 else 0
        total_profit_pct = sum([t.get('profit_pct', 0) or 0 for t in completed_trades])
        total_profit_usd = sum([t.get('profit', 0) or 0 for t in completed_trades])  # Sum all profits
        sharpe = round(total_profit_pct / max(draw_down, 1), 2) if total_profit_pct != 0 else 0
        
        return BacktestResult(
            strategy_name=strategy.name,
            total_trades=total_trades,
            wins=wins,
            losses=losses,
            win_rate=round(win_rate, 2),
            profit_pct=round(total_profit_pct, 2),
            total_profit_usd=round(total_profit_usd, 2),
            profit_factor=round(profit_factor, 2),
            draw_down=round(draw_down, 2),
            sharpe=sharpe,
            trades=[BacktestTrade(**t) for t in completed_trades[-200:]],
            total_signals=total_signals,
            long_signals=long_signals,
            short_signals=short_signals,
            long_trades=long_trades,
            short_trades=short_trades,
            equity_curve=equity_curve
        )
