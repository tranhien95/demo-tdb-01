"""
Strategy Engine
Execute custom strategies with weighted indicators
"""

from typing import List, Dict, Any, Tuple
from strategy_models_simple import (
    Strategy, BacktestResult, BacktestTrade, 
    SignalDetail, SignalLogic, IndicatorConfig
)
from indicators import indicator_manager
from indicators.base import HelperFunctions
from performance_metrics import PerformanceMetrics
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
        if filters.enable_adx:
            adx_signal = indicator_manager.calculate_indicator('ADX', data, index, period=14)
            if adx_signal.get('value', 0) < filters.adx_threshold:
                return False
        
        # Volume Filter
        if filters.enable_volume:
            if index >= 20:
                vol_ma = sum([data[j]['volume'] for j in range(index - 20, index)]) / 20
                current_vol = data[index]['volume']
                if current_vol < vol_ma * filters.volume_threshold:
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
            atr_val = HelperFunctions.atr(data, index, 14)
            if atr_val < filters.min_atr:
                return False
        
        # Trend Filter (EMA200)
        if filters.enable_trend_filter:
            if index >= filters.trend_ma:
                closes = [d['close'] for d in data[:index + 1]]
                ema_vals = HelperFunctions.ema(closes, filters.trend_ma)
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
        rr_ratio = strategy.risk_management.reward_ratio
        sl_pct = strategy.risk_management.stop_loss_percent
        capital = strategy.risk_management.capital
        margin = strategy.risk_management.margin
        
        trades_list = []
        balance = capital
        max_balance = capital
        min_balance = capital
        wins = 0
        long_trades = 0
        short_trades = 0
        current_position = None
        entry_candle_index = None  # Track when position was entered
        
        last_signal = None
        signal_count = 0
        switch_signal_count = 0  # Track confirmation for switch signals
        last_switch_signal = None
        
        total_signals = 0
        long_signals = 0
        short_signals = 0
        equity_curve = [capital]  # Start with initial capital
        
        # Get switching controls from strategy
        allow_switch = strategy.signal_logic.allow_position_switch
        min_holding = strategy.signal_logic.min_holding_candles
        switch_confirmation = strategy.signal_logic.switch_confirmation_candles
        
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
            
            # Candle confirmation for entry
            if direction and direction == last_signal:
                signal_count += 1
            else:
                last_signal = direction
                signal_count = 1
            
            # Track switch signal confirmation separately
            if current_position and direction and direction != current_position:
                # This is a potential switch signal
                if direction == last_switch_signal:
                    switch_signal_count += 1
                else:
                    last_switch_signal = direction
                    switch_signal_count = 1
            else:
                # Reset switch signal tracking if not a switch scenario
                last_switch_signal = None
                switch_signal_count = 0
            
            # Determine if we should enter (new position or switch)
            should_enter_new = (
                direction and
                signal_count >= 1 and
                not current_position
            )
            
            # Determine if we should switch (with all checks)
            should_switch = False
            if allow_switch and current_position and direction and direction != current_position:
                # Check minimum holding time
                holding_time_ok = (entry_candle_index is None) or (i - entry_candle_index >= min_holding)
                # Check switch confirmation
                confirmation_ok = switch_signal_count >= switch_confirmation
                should_switch = holding_time_ok and confirmation_ok
            
            # Enter new trade
            if should_enter_new:
                entry = data[i]['close']
                sl = entry * (1 - sl_pct / 100) if direction == 'LONG' else entry * (1 + sl_pct / 100)
                tp = entry + (entry - sl) * rr_ratio if direction == 'LONG' else entry - (sl - entry) * rr_ratio
                
                # Calculate position size
                # Risk based on INITIAL capital, not current balance
                risk_amount = capital * (risk_pct / 100)
                # Position size = Risk / SL% (standard trading formula)
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
                    'type': direction,
                    'time': data[i].get('time', ''),
                    'exit_time': None,
                    'entry_signals': [s.dict() if hasattr(s, 'dict') else (s.model_dump() if hasattr(s, 'model_dump') else s.__dict__) for s in signals_detail]
                })
                current_position = direction
                entry_candle_index = i  # Track when position was entered
                if direction == 'LONG':
                    long_trades += 1
                else:
                    short_trades += 1
            
            # Switch position (only if allowed and conditions met)
            elif should_switch:
                last_trade = trades_list[-1]
                current_close = data[i]['close']
                
                profit = current_close - last_trade['entry'] if current_position == 'LONG' else last_trade['entry'] - current_close
                profit_pct = (profit / last_trade['entry']) * 100
                
                # Calculate actual USD profit based on position size
                position_size = last_trade['position_size']
                actual_profit_usd = position_size * (profit_pct / 100)
                
                last_trade['exit'] = round(current_close, 2)
                last_trade['exit_time'] = data[i].get('time', '')
                last_trade['profit'] = round(actual_profit_usd, 4)  # USD profit, not price diff
                last_trade['profit_pct'] = round(profit_pct, 2)
                last_trade['exit_reason'] = 'Switch'
                
                if profit > 0:
                    wins += 1
                
                # Update balance with actual profit
                balance += actual_profit_usd
                last_trade['balance_after'] = round(balance, 2)  # Balance after closing trade
                max_balance = max(max_balance, balance)
                min_balance = min(min_balance, balance)
                equity_curve.append(round(balance, 2))
                
                # Enter new position
                entry = current_close
                sl = entry * (1 - sl_pct / 100) if direction == 'LONG' else entry * (1 + sl_pct / 100)
                tp = entry + (entry - sl) * rr_ratio if direction == 'LONG' else entry - (sl - entry) * rr_ratio
                
                # Calculate position size
                # Risk based on INITIAL capital, not current balance
                risk_amount = capital * (risk_pct / 100)
                # Position size = Risk / SL% (standard trading formula)
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
                    'type': direction,
                    'time': data[i].get('time', ''),
                    'exit_time': None,
                    'balance_before': round(balance, 2),  # Balance before new trade after switch
                    'balance_after': None,  # Will be set when trade closes
                    'entry_signals': [s.dict() if hasattr(s, 'dict') else (s.model_dump() if hasattr(s, 'model_dump') else s.__dict__) for s in signals_detail]
                })
                current_position = direction
                entry_candle_index = i  # Track when new position was entered after switch
            
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
                        
                        # Calculate actual USD profit based on position size
                        position_size = last_trade['position_size']
                        actual_profit_usd = position_size * (profit_pct / 100)
                        
                        last_trade['exit'] = round(exit_price, 2)
                        last_trade['exit_time'] = data[i].get('time', '')
                        last_trade['profit'] = round(actual_profit_usd, 4)  # USD profit, not price diff
                        last_trade['profit_pct'] = round(profit_pct, 2)
                        last_trade['exit_reason'] = exit_reason
                        
                        if profit > 0:
                            wins += 1
                        
                        # Update balance with actual profit
                        balance += actual_profit_usd
                        last_trade['balance_after'] = round(balance, 2)  # Balance after closing trade
                        max_balance = max(max_balance, balance)
                        min_balance = min(min_balance, balance)
                        equity_curve.append(round(balance, 2))
                        current_position = None
                        entry_candle_index = None  # Reset entry tracking
        
        # Close last trade if open
        if current_position and len(trades_list) > 0:
            last_trade = trades_list[-1]
            if last_trade.get('exit') is None:
                exit_price = data[-1]['close']
                profit = exit_price - last_trade['entry'] if current_position == 'LONG' else last_trade['entry'] - exit_price
                profit_pct = (profit / last_trade['entry']) * 100
                
                # Calculate actual USD profit based on position size
                position_size = last_trade['position_size']
                actual_profit_usd = position_size * (profit_pct / 100)
                
                last_trade['exit'] = round(exit_price, 2)
                last_trade['exit_time'] = data[-1].get('time', '')
                last_trade['profit'] = round(actual_profit_usd, 4)  # USD profit, not price diff
                last_trade['profit_pct'] = round(profit_pct, 2)
                last_trade['exit_reason'] = 'Close'
                
                if profit > 0:
                    wins += 1
                
                # Update balance and set balance_after
                balance += actual_profit_usd
                last_trade['balance_after'] = round(balance, 2)
        
        # Calculate stats
        completed_trades = [t for t in trades_list if t['exit'] is not None]
        total_trades = len(completed_trades)
        losses = total_trades - wins
        
        win_rate = (wins / total_trades * 100) if total_trades > 0 else 0
        
        # Calculate actual portfolio return
        final_balance = equity_curve[-1] if equity_curve else capital
        total_profit_pct = ((final_balance - capital) / capital) * 100
        total_profit_usd = final_balance - capital
        
        # Calculate all performance metrics using standardized calculator
        all_metrics = PerformanceMetrics.calculate_all_metrics(
            trades=completed_trades,
            equity_curve=equity_curve,
            initial_capital=capital
        )
        
        # Prepare result - skip BacktestResult dataclass conversion for simplicity
        result = {
            'status': 'success',
            'total_trades': total_trades,
            'winning_trades': wins,
            'losing_trades': losses,
            'win_rate': round(win_rate, 2),
            'profit_factor': all_metrics['profit_factor'],
            'total_profit': round(total_profit_usd, 2),
            'total_profit_pct': round(total_profit_pct, 2),
            'max_drawdown': all_metrics['max_drawdown_pct'],
            'sharpe_ratio': all_metrics['sharpe_ratio'],
            'trades': completed_trades[-200:],  # Keep trades as plain dicts
            'long_trades': long_trades,
            'short_trades': short_trades,
            'signals_found': total_signals,
            'long_signals': long_signals,
            'short_signals': short_signals,
            'equity_curve': equity_curve
        }
        
        return result
