"""
Live Trading Engine
Core trading logic with paper trading simulation
"""

import uuid
from datetime import datetime
from typing import List, Dict, Tuple, Optional
from live_trading_models import (
    Position, ClosedTrade, LiveTradingState, TradingConfig,
    SignalType, TradeStatus, SignalWithConfidence, CandleData
)
from strategy_engine import StrategyEngine
# Use database storage instead of JSON
from strategy_storage_db import strategy_storage
from binance_fetcher import get_binance_fetcher
from trading_improvements import TradingImprovements
import json
from pathlib import Path


class LiveTradingEngine:
    """Execute live trading with paper trading simulation"""
    
    DB_DIR = Path(__file__).parent / "trading_data"
    
    def __init__(self):
        self.DB_DIR.mkdir(exist_ok=True)
        self.state: Optional[LiveTradingState] = None
        self.price_history: Dict[str, List[CandleData]] = {}
        self.binance_fetcher = get_binance_fetcher()
    
    # ===================== INIT & CONFIG =====================
    
    def initialize(self, config: TradingConfig) -> bool:
        """
        Initialize live trading session
        
        Args:
            config: Trading configuration
            
        Returns:
            True if successful
        """
        try:
            # Load strategy
            strategy = strategy_storage.load_strategy(config.strategy_name)
            if not strategy:
                print(f"Strategy '{config.strategy_name}' not found")
                return False
            
            # Create initial state
            self.state = LiveTradingState(
                status=TradeStatus.RUNNING,
                config=config,
                balance=config.initial_balance,
                equity=config.initial_balance,
                used_margin=0.0,
                available_margin=config.initial_balance * config.margin
            )
            
            # Fetch initial data
            if not self._fetch_market_data():
                return False
            
            self._save_state()
            return True
            
        except Exception as e:
            print(f"Error initializing trading engine: {e}")
            return False
    
    def _fetch_market_data(self) -> bool:
        """Fetch market data from Binance"""
        try:
            symbol = self.state.config.symbol
            timeframe = self.state.config.timeframe
            limit = 1000  # Get up to 1000 candles for chart
            
            # Convert timeframe to Binance format
            tf_map = {
                "M1": "1m", "M5": "5m", "M15": "15m",
                "H1": "1h", "H4": "4h", "D": "1d"
            }
            binance_tf = tf_map.get(timeframe, "5m")
            
            # Binance symbol format is with slash (BTC/USDT)
            binance_symbol = symbol.replace("USDT", "/USDT") if "/" not in symbol else symbol
            
            ohlcv_data = self.binance_fetcher.fetch_ohlcv(
                binance_symbol, binance_tf, limit
            )
            
            if not ohlcv_data:
                print(f"No OHLCV data for {binance_symbol}")
                return False
            
            # Convert to CandleData and store chart data
            candles = []
            chart_data = []
            
            for item in ohlcv_data:
                try:
                    # Handle both dict and tuple formats
                    if isinstance(item, dict):
                        # Parse time string flexibly
                        time_str = item['time']
                        try:
                            dt = datetime.strptime(time_str, '%Y-%m-%d %H:%M:%S')
                        except:
                            # Try ISO format if standard format fails
                            dt = datetime.fromisoformat(time_str.replace('Z', '+00:00'))
                        
                        candle_dict = {
                            'time': item['time'],
                            'open': float(item['open']),
                            'high': float(item['high']),
                            'low': float(item['low']),
                            'close': float(item['close']),
                            'volume': float(item['volume'])
                        }
                        candle = CandleData(
                            time=dt,
                            open=float(item['open']),
                            high=float(item['high']),
                            low=float(item['low']),
                            close=float(item['close']),
                            volume=float(item['volume'])
                        )
                    else:
                        # Legacy tuple format
                        candle = CandleData(
                            time=datetime.fromtimestamp(item[0] / 1000),
                            open=float(item[1]),
                            high=float(item[2]),
                            low=float(item[3]),
                            close=float(item[4]),
                            volume=float(item[5])
                        )
                        candle_dict = {
                            'time': candle.time.isoformat(),
                            'open': float(item[1]),
                            'high': float(item[2]),
                            'low': float(item[3]),
                            'close': float(item[4]),
                            'volume': float(item[5])
                        }
                    
                    candles.append(candle)
                    chart_data.append(candle_dict)
                    
                except Exception as e:
                    print(f"Error converting candle: {e}, item: {item}")
                    import traceback
                    traceback.print_exc()
                    continue
            
            if not candles:
                print("No valid candles after conversion")
                return False
            
            self.price_history[symbol] = candles
            # Store chart data in state (last 500 for performance)
            self.state.candles = chart_data[-500:] if len(chart_data) > 500 else chart_data
            
            return True
            
        except Exception as e:
            print(f"Error fetching market data: {e}")
            import traceback
            traceback.print_exc()
            return False
    
    # ===================== TRADING LOGIC =====================
    
    def update(self) -> Dict:
        """
        Update trading state with latest candle
        
        Returns:
            State update dict
        """
        if not self.state or self.state.status != TradeStatus.RUNNING:
            return {"status": "not_running"}
        
        try:
            # Fetch latest data
            if not self._fetch_market_data():
                return {"error": "Failed to fetch market data"}
            
            symbol = self.state.config.symbol
            candles = self.price_history.get(symbol, [])
            
            if len(candles) < 50:  # Need minimum data for indicators
                return {"status": "insufficient_data"}
            
            # Get current price
            current_price = candles[-1].close
            
            # Load strategy
            strategy = strategy_storage.load_strategy(
                self.state.config.strategy_name
            )
            
            # Calculate signals
            signals = self._get_signals(strategy, candles)
            
            # Update positions with current price
            self._update_positions(current_price)
            
            # Check exit conditions
            self._check_exit_conditions(current_price, signals)
            
            # Check entry conditions
            if len(self.state.open_positions) < self.state.config.max_positions:
                self._check_entry_conditions(current_price, signals)
            
            # Update equity
            self._update_equity(current_price)
            
            # Update metrics
            self._update_metrics()
            
            self.state.last_updated = datetime.now()
            self._save_state()
            
            return {
                "status": "updated",
                "current_price": current_price,
                "signal": signals,
                "open_positions": len(self.state.open_positions),
                "balance": self.state.balance,
                "equity": self.state.equity,
            }
            
        except Exception as e:
            print(f"Error updating trading engine: {e}")
            return {"error": str(e)}
    
    def _get_signals(self, strategy, candles: List[CandleData]) -> SignalWithConfidence:
        """Get trading signals from strategy"""
        try:
            # Convert candles to dict format expected by StrategyEngine
            data = [
                {
                    "time": c.time.isoformat(),
                    "open": c.open,
                    "high": c.high,
                    "low": c.low,
                    "close": c.close,
                    "volume": c.volume
                }
                for c in candles
            ]
            
            # Calculate signal at last candle
            index = len(data) - 1
            direction, bullish_pct, bearish_pct, signals_detail = (
                StrategyEngine.calculate_signal(strategy, data, index)
            )
            
            # Convert to signal type
            if direction == "BULLISH":
                if bullish_pct >= 80:
                    signal_type = SignalType.STRONG_BUY
                else:
                    signal_type = SignalType.BUY
                confidence = bullish_pct
            elif direction == "BEARISH":
                if bearish_pct >= 80:
                    signal_type = SignalType.STRONG_SELL
                else:
                    signal_type = SignalType.SELL
                confidence = bearish_pct
            else:
                signal_type = SignalType.NEUTRAL
                confidence = 50.0
            
            # Get reversal signals (check for divergence in signals_detail)
            reversal_strength = 0.0
            has_divergence = False
            
            # signals_detail is a list of SignalDetail objects
            for sig in signals_detail:
                try:
                    # Handle both dict and object attributes
                    if hasattr(sig, 'divergence'):
                        has_divergence = has_divergence or sig.divergence
                    if hasattr(sig, 'contribution_percent'):
                        reversal_strength = max(reversal_strength, sig.contribution_percent)
                except:
                    pass
            
            return SignalWithConfidence(
                type=signal_type,
                confidence=confidence,
                reversal_strength=reversal_strength,
                divergence=has_divergence,
                supporting_signals=[getattr(s, 'indicator_type', '')[:30] for s in signals_detail[:3]]
            )
            
        except Exception as e:
            print(f"Error calculating signals: {e}")
            import traceback
            traceback.print_exc()
            return SignalWithConfidence(
                type=SignalType.NEUTRAL,
                confidence=0.0,
                reversal_strength=0.0,
                divergence=False
            )
    
    def _update_positions(self, current_price: float):
        """Update all open positions with current price"""
        for position in self.state.open_positions:
            position.update_price(current_price)
    
    def _check_exit_conditions(self, current_price: float, signals: SignalWithConfidence):
        """Check if any positions should be closed"""
        positions_to_close = []
        
        for position in self.state.open_positions:
            # Check partial profit taking (if enabled) - Check FIRST
            if self.state.config.enable_partial_profit:
                self._check_partial_profit_taking(position, current_price)
            
            # Check breakeven stop (if enabled) - Check BEFORE trailing
            if self.state.config.enable_breakeven_stop:
                self._check_breakeven_stop(position, current_price)
            
            # Update trailing stop loss (if enabled)
            if self.state.config.enable_trailing_stop:
                self._update_trailing_stop(position, current_price)
            
            exit_reason = None
            
            # Check SL hit
            if position.side == "LONG":
                if current_price <= position.stoploss:
                    exit_reason = "SL_HIT" if not position.trailing_activated else "TRAILING_SL_HIT"
                elif current_price >= position.takeprofit:
                    exit_reason = "TP_HIT"
            else:  # SHORT
                if current_price >= position.stoploss:
                    exit_reason = "SL_HIT" if not position.trailing_activated else "TRAILING_SL_HIT"
                elif current_price <= position.takeprofit:
                    exit_reason = "TP_HIT"
            
            # Check reversal signal
            if not exit_reason:
                if position.side == "LONG" and signals.type in [SignalType.STRONG_SELL, SignalType.SELL]:
                    if signals.reversal_strength >= self.state.config.reversal_strength_threshold:
                        exit_reason = "REVERSAL_SIGNAL"
                elif position.side == "SHORT" and signals.type in [SignalType.STRONG_BUY, SignalType.BUY]:
                    if signals.reversal_strength >= self.state.config.reversal_strength_threshold:
                        exit_reason = "REVERSAL_SIGNAL"
            
            if exit_reason:
                positions_to_close.append((position, exit_reason, current_price, signals.type))
        
        # Close positions
        for position, exit_reason, exit_price, exit_signal in positions_to_close:
            self._close_position(position, exit_price, exit_reason, exit_signal)
    
    def _check_entry_conditions(self, current_price: float, signals: SignalWithConfidence):
        """Check if should open new position với filters"""
        # 1. Signal Quality Scoring (if enabled)
        if self.state.config.enable_signal_quality:
            symbol = self.state.config.symbol
            candles = self.price_history.get(symbol, [])
            
            if len(candles) >= 50:
                data = [
                    {
                        "time": c.time.isoformat(),
                        "open": c.open,
                        "high": c.high,
                        "low": c.low,
                        "close": c.close,
                        "volume": c.volume
                    }
                    for c in candles
                ]
                
                quality_score = self._calculate_signal_quality_score(
                    signals, data, len(data) - 1
                )
                
                if quality_score < self.state.config.min_signal_quality:
                    print(f"[Signal Quality] Score too low: {quality_score:.1f} < {self.state.config.min_signal_quality}")
                    return  # Skip trade
        
        # 2. Time-based Filter (if enabled)
        if self.state.config.enable_time_filter:
            if not TradingImprovements.is_tradeable_time(
                datetime.now(), market_type=self.state.config.market_type
            ):
                print(f"[Time Filter] Current time not tradeable")
                return  # Skip trade
        
        # 3. Multi-timeframe Confirmation (if enabled)
        if self.state.config.enable_multi_timeframe:
            symbol = self.state.config.symbol
            primary_tf = self.state.config.timeframe
            higher_tf = self.state.config.higher_timeframe
            
            higher_trend = self._check_multi_timeframe_trend(symbol, primary_tf, higher_tf)
            
            if signals.type == SignalType.STRONG_BUY and higher_trend != "UPTREND":
                print(f"[MTF] Higher TF ({higher_tf}) trend: {higher_trend}, but signal is LONG - Skip")
                return
            elif signals.type == SignalType.STRONG_SELL and higher_trend != "DOWNTREND":
                print(f"[MTF] Higher TF ({higher_tf}) trend: {higher_trend}, but signal is SHORT - Skip")
                return
            
            if higher_trend != "SIDEWAYS":
                print(f"[MTF] Higher TF ({higher_tf}) trend: {higher_trend} ✓")
        
        # 4. Correlation Filter (if enabled and multiple positions)
        if self.state.config.enable_correlation_filter and len(self.state.open_positions) > 0:
            symbol = self.state.config.symbol
            max_corr = self._check_correlation(symbol, self.state.open_positions)
            
            if max_corr > self.state.config.max_correlation:
                print(f"[Correlation] Max correlation {max_corr:.2f} > {self.state.config.max_correlation} - Skip")
                return
        
        # 5. Original entry logic
        min_confidence = 65.0
        
        if signals.type == SignalType.STRONG_BUY and signals.confidence >= min_confidence:
            self._open_position(current_price, "LONG", signals)
        elif signals.type == SignalType.STRONG_SELL and signals.confidence >= min_confidence:
            self._open_position(current_price, "SHORT", signals)
    
    def _open_position(self, entry_price: float, side: str, signals: SignalWithConfidence) -> Optional[Position]:
        """Open new position với dynamic position sizing"""
        try:
            # Calculate base risk amount
            base_risk_pct = self.state.config.risk_percent
            
            # Dynamic position sizing (if enabled)
            if self.state.config.enable_dynamic_sizing:
                # Calculate volatility (ATR as % of price)
                symbol = self.state.config.symbol
                candles = self.price_history.get(symbol, [])
                
                if len(candles) >= 14 and self.state.config.dynamic_sizing_use_volatility:
                    atr = self._calculate_atr(candles, 14)
                    volatility_pct = (atr / entry_price) * 100
                else:
                    volatility_pct = 1.0  # Default volatility
                
                # Calculate dynamic risk %
                adjusted_risk_pct = TradingImprovements.calculate_dynamic_position_size(
                    base_risk_pct=base_risk_pct,
                    confidence=signals.confidence,
                    volatility_pct=volatility_pct,
                    max_multiplier=self.state.config.dynamic_sizing_max_multiplier
                )
                
                print(f"[Dynamic Sizing] Base: {base_risk_pct}% → Adjusted: {adjusted_risk_pct:.2f}% (Confidence: {signals.confidence:.1f}%, Volatility: {volatility_pct:.2f}%)")
            else:
                adjusted_risk_pct = base_risk_pct
            
            # Calculate position size với adjusted risk
            risk_amount = self.state.balance * (adjusted_risk_pct / 100)
            
            # SL distance in %
            sl_distance_pct = self.state.config.stoploss_percent / 100
            
            # Position size = risk / sl_distance
            quantity = risk_amount / (entry_price * sl_distance_pct)
            
            # Check margin
            position_cost = quantity * entry_price
            if position_cost > self.state.available_margin:
                return None
            
            # Calculate SL & TP (ATR-based or fixed)
            if self.state.config.enable_atr_sl_tp:
                # Use ATR-based SL/TP
                atr = self._calculate_atr(candles, 14) if len(candles) >= 14 else entry_price * 0.01
                sl_distance_pct, tp_distance_pct = TradingImprovements.calculate_atr_based_sl_tp(
                    entry_price, atr, rr_ratio=2.0
                )
                sl_distance_pct = sl_distance_pct / 100  # Convert to decimal
                tp_distance_pct = tp_distance_pct / 100
            else:
                # Use fixed SL/TP
                tp_distance_pct = sl_distance_pct * 2  # 2:1 R:R
            
            if side == "LONG":
                stoploss = entry_price * (1 - sl_distance_pct)
                takeprofit = entry_price * (1 + tp_distance_pct) if self.state.config.enable_atr_sl_tp else entry_price * (1 + sl_distance_pct * 2)
            else:  # SHORT
                stoploss = entry_price * (1 + sl_distance_pct)
                takeprofit = entry_price * (1 - tp_distance_pct) if self.state.config.enable_atr_sl_tp else entry_price * (1 - sl_distance_pct * 2)
            
            # Create position
            position = Position(
                id=str(uuid.uuid4()),
                symbol=self.state.config.symbol,
                entry_price=entry_price,
                entry_time=datetime.now(),
                quantity=quantity,
                side=side,
                stoploss=stoploss,
                takeprofit=takeprofit,
                entry_signal=signals.type.value,
                entry_confidence=signals.confidence,
                highest_price=entry_price if side == "LONG" else float('inf'),
                lowest_price=entry_price if side == "SHORT" else 0.0,
                initial_stoploss=stoploss,  # Store original SL for R calculation
                trailing_activated=False,
                breakeven_set=False,
                partial_profit_rules=self.state.config.partial_profit_rules.copy() if self.state.config.enable_partial_profit else [],
            )
            
            position.update_price(entry_price)
            self.state.open_positions.append(position)
            
            # Update margin
            self.state.used_margin += position_cost
            self.state.available_margin -= position_cost
            
            return position
            
        except Exception as e:
            print(f"Error opening position: {e}")
            return None
    
    def _close_position(
        self, position: Position, exit_price: float,
        exit_reason: str, exit_signal: Optional[SignalType] = None
    ) -> Optional[ClosedTrade]:
        """Close position and record trade"""
        try:
            # Calculate P&L
            if position.side == "LONG":
                pnl = (exit_price - position.entry_price) * position.quantity
            else:
                pnl = (position.entry_price - exit_price) * position.quantity
            
            pnl_percent = (pnl / (position.entry_price * position.quantity)) * 100
            
            # Create closed trade record
            trade = ClosedTrade(
                id=position.id,
                symbol=position.symbol,
                entry_price=position.entry_price,
                entry_time=position.entry_time,
                exit_price=exit_price,
                exit_time=datetime.now(),
                quantity=position.quantity,
                side=position.side,
                pnl=pnl,
                pnl_percent=pnl_percent,
                win=pnl > 0,
                exit_reason=exit_reason,
                entry_signal=position.entry_signal,
                exit_signal=exit_signal.value if exit_signal else None,
                entry_confidence=position.entry_confidence,
            )
            
            # Update state
            self.state.closed_trades.append(trade)
            self.state.balance += pnl
            self.state.total_trades += 1
            
            if trade.win:
                self.state.winning_trades += 1
                self.state.total_profit += pnl
            else:
                self.state.losing_trades += 1
                self.state.total_loss += abs(pnl)
            
            # Update margin
            position_cost = position.quantity * position.entry_price
            self.state.used_margin -= position_cost
            self.state.available_margin += position_cost
            
            # Remove from open positions
            self.state.open_positions.remove(position)
            
            return trade
            
        except Exception as e:
            print(f"Error closing position: {e}")
            return None
    
    def _calculate_atr(self, candles: List[CandleData], period: int = 14) -> float:
        """
        Calculate Average True Range (ATR) from candles
        
        Args:
            candles: List of CandleData
            period: ATR period (default 14)
            
        Returns:
            ATR value
        """
        if len(candles) < period + 1:
            # Fallback: return 1% of current price if not enough data
            if candles:
                return candles[-1].close * 0.01
            return 0.0
        
        true_ranges = []
        for i in range(1, len(candles)):
            high = candles[i].high
            low = candles[i].low
            prev_close = candles[i-1].close
            
            # True Range = max of:
            # 1. High - Low
            # 2. |High - Previous Close|
            # 3. |Low - Previous Close|
            tr = max(
                high - low,
                abs(high - prev_close),
                abs(low - prev_close)
            )
            true_ranges.append(tr)
        
        # ATR = Simple Moving Average of True Ranges
        atr = sum(true_ranges[-period:]) / period
        return atr
    
    def _update_trailing_stop(self, position: Position, current_price: float):
        """
        Update trailing stop loss for position
        
        Args:
            position: Position to update
            current_price: Current market price
        """
        if not position or not position.initial_stoploss:
            return
        
        # Calculate ATR
        symbol = position.symbol
        candles = self.price_history.get(symbol, [])
        
        if len(candles) < 14:
            return  # Not enough data
        
        atr = self._calculate_atr(candles, 14)
        
        # Calculate profit in R units
        entry = position.entry_price
        initial_sl_distance = abs(entry - position.initial_stoploss)
        
        if initial_sl_distance == 0:
            return  # Invalid SL
        
        # Calculate profit percentage
        if position.side == "LONG":
            profit = current_price - entry
            profit_pct = (profit / entry) * 100
        else:  # SHORT
            profit = entry - current_price
            profit_pct = (profit / entry) * 100
        
        # Calculate profit in R units
        sl_distance_pct = (initial_sl_distance / entry) * 100
        profit_r = profit_pct / sl_distance_pct if sl_distance_pct > 0 else 0
        
        # Only activate trailing when profit >= activation R
        activation_r = self.state.config.trailing_activation_r
        if profit_r < activation_r:
            return  # Not enough profit yet
        
        # Calculate trailing distance
        trailing_multiplier = self.state.config.trailing_multiplier
        trailing_distance = atr * trailing_multiplier
        
        # Update trailing stop
        if position.side == "LONG":
            new_sl = current_price - trailing_distance
            # Only move SL up, never down
            if new_sl > position.stoploss:
                old_sl = position.stoploss
                position.stoploss = new_sl
                if not position.trailing_activated:
                    position.trailing_activated = True
                    print(f"[Trailing] Activated for {position.side} position @ {current_price:.2f}, SL: {old_sl:.2f} → {new_sl:.2f}")
                else:
                    print(f"[Trailing] Updated {position.side} SL: {old_sl:.2f} → {new_sl:.2f} (Price: {current_price:.2f})")
        else:  # SHORT
            new_sl = current_price + trailing_distance
            # Only move SL down, never up
            if new_sl < position.stoploss:
                old_sl = position.stoploss
                position.stoploss = new_sl
                if not position.trailing_activated:
                    position.trailing_activated = True
                    print(f"[Trailing] Activated for {position.side} position @ {current_price:.2f}, SL: {old_sl:.2f} → {new_sl:.2f}")
                else:
                    print(f"[Trailing] Updated {position.side} SL: {old_sl:.2f} → {new_sl:.2f} (Price: {current_price:.2f})")
    
    def _check_partial_profit_taking(self, position: Position, current_price: float):
        """
        Check và thực hiện partial profit taking
        
        Args:
            position: Position to check
            current_price: Current market price
        """
        if not position or not position.initial_stoploss:
            return
        
        # Get partial rules từ position hoặc config
        if hasattr(position, 'partial_profit_rules') and position.partial_profit_rules:
            partial_rules = position.partial_profit_rules
        else:
            partial_rules = self.state.config.partial_profit_rules.copy()
        
        if not partial_rules:
            return
        
        entry = position.entry_price
        initial_sl_distance = abs(entry - position.initial_stoploss)
        
        if initial_sl_distance == 0:
            return
        
        # Calculate profit in R units
        if position.side == "LONG":
            profit = current_price - entry
            profit_pct = (profit / entry) * 100
        else:  # SHORT
            profit = entry - current_price
            profit_pct = (profit / entry) * 100
        
        # Calculate profit R
        sl_distance_pct = (initial_sl_distance / entry) * 100
        profit_r = profit_pct / sl_distance_pct if sl_distance_pct > 0 else 0
        
        # Check each rule
        for rule in partial_rules:
            r_level = rule.get('r_level', 0)
            close_pct = rule.get('close_pct', 0)
            taken = rule.get('taken', False)
            
            if profit_r >= r_level and not taken:
                # Close partial position
                self._close_partial_position(position, close_pct, f"Partial {r_level}R")
                rule['taken'] = True
                print(f"[Partial Profit] Closed {close_pct*100:.0f}% @ {r_level}R (Profit: {profit_r:.2f}R)")
                
                # Update position rules
                if not hasattr(position, 'partial_profit_rules'):
                    position.partial_profit_rules = []
                position.partial_profit_rules = partial_rules
                break  # Only close one level at a time
    
    def _close_partial_position(self, position: Position, close_pct: float, reason: str):
        """
        Close một phần position
        
        Args:
            position: Position to close partially
            close_pct: Percentage to close (0.0 - 1.0)
            reason: Reason for closing
        """
        if close_pct <= 0 or close_pct >= 1:
            return
        
        if position.quantity <= 0:
            return
        
        # Calculate partial quantity
        partial_quantity = position.quantity * close_pct
        remaining_quantity = position.quantity * (1 - close_pct)
        
        # Calculate P&L cho phần đóng
        current_price = position.current_price
        if position.side == "LONG":
            profit = (current_price - position.entry_price) * partial_quantity
        else:  # SHORT
            profit = (position.entry_price - current_price) * partial_quantity
        
        # Update position
        position.quantity = remaining_quantity
        
        # Update balance
        self.state.balance += profit
        
        # Create closed trade record for partial exit
        from live_trading_models import ClosedTrade
        partial_trade = ClosedTrade(
            id=f"{position.id}_partial_{reason}",
            symbol=position.symbol,
            entry_price=position.entry_price,
            entry_time=position.entry_time,
            exit_price=current_price,
            exit_time=datetime.now(),
            quantity=partial_quantity,
            side=position.side,
            pnl=profit,
            pnl_percent=(profit / (position.entry_price * partial_quantity)) * 100 if partial_quantity > 0 else 0,
            win=profit > 0,
            exit_reason=reason,
            entry_signal=position.entry_signal,
            exit_signal=None,
            entry_confidence=position.entry_confidence,
        )
        
        self.state.closed_trades.append(partial_trade)
        self.state.total_trades += 1
        
        if profit > 0:
            self.state.winning_trades += 1
            self.state.total_profit += profit
        else:
            self.state.losing_trades += 1
            self.state.total_loss += abs(profit)
        
        # Update margin (reduce used margin)
        partial_cost = partial_quantity * position.entry_price
        self.state.used_margin -= partial_cost
        self.state.available_margin += partial_cost
        
        # If position fully closed (due to rounding), remove it
        if remaining_quantity < 0.001:
            self.state.open_positions.remove(position)
            print(f"[Partial Profit] Position fully closed after partial exit")
    
    def _check_breakeven_stop(self, position: Position, current_price: float):
        """
        Move stop loss to breakeven when profit >= activation R
        
        Args:
            position: Position to check
            current_price: Current market price
        """
        if not position or not position.initial_stoploss:
            return
        
        # Check if breakeven already set
        if position.breakeven_set:
            return  # Already set, no need to check again
        
        entry = position.entry_price
        initial_sl_distance = abs(entry - position.initial_stoploss)
        
        if initial_sl_distance == 0:
            return  # Invalid SL
        
        # Calculate profit in R units
        if position.side == "LONG":
            profit = current_price - entry
            profit_pct = (profit / entry) * 100
        else:  # SHORT
            profit = entry - current_price
            profit_pct = (profit / entry) * 100
        
        # Calculate profit R
        sl_distance_pct = (initial_sl_distance / entry) * 100
        profit_r = profit_pct / sl_distance_pct if sl_distance_pct > 0 else 0
        
        # Check if should set breakeven
        activation_r = self.state.config.breakeven_activation_r
        if profit_r >= activation_r:
            buffer_pct = self.state.config.breakeven_buffer_pct
            
            if position.side == "LONG":
                # Entry + buffer to avoid spread
                new_sl = entry * (1 + buffer_pct / 100)
                # Only move if new SL is better than current SL
                if new_sl > position.stoploss:
                    old_sl = position.stoploss
                    position.stoploss = new_sl
                    position.breakeven_set = True
                    print(f"[Breakeven] {position.side} SL moved to breakeven: ${old_sl:.2f} → ${new_sl:.2f} (Entry: ${entry:.2f} + {buffer_pct}% buffer)")
            else:  # SHORT
                # Entry - buffer to avoid spread
                new_sl = entry * (1 - buffer_pct / 100)
                # Only move if new SL is better than current SL
                if new_sl < position.stoploss:
                    old_sl = position.stoploss
                    position.stoploss = new_sl
                    position.breakeven_set = True
                    print(f"[Breakeven] {position.side} SL moved to breakeven: ${old_sl:.2f} → ${new_sl:.2f} (Entry: ${entry:.2f} - {buffer_pct}% buffer)")
    
    def _calculate_signal_quality_score(
        self,
        signals: SignalWithConfidence,
        data: List[Dict],
        index: int
    ) -> float:
        """Calculate signal quality score (0-100)"""
        score = 0.0
        
        # 1. Indicator alignment (30 points)
        if signals.confidence >= 90:
            score += 30
        elif signals.confidence >= 80:
            score += 25
        elif signals.confidence >= 70:
            score += 20
        elif signals.confidence >= 60:
            score += 10
        
        # 2. Volume confirmation (20 points)
        if index >= 20:
            current_vol = data[index]['volume']
            avg_vol = sum([d['volume'] for d in data[index-20:index]]) / 20
            volume_ratio = current_vol / avg_vol if avg_vol > 0 else 1.0
            
            if volume_ratio >= 1.5:
                score += 20
            elif volume_ratio >= 1.2:
                score += 15
            elif volume_ratio >= 1.0:
                score += 10
        
        # 3. Trend confirmation (20 points)
        if index >= 200:
            from indicators.base import HelperFunctions
            closes = [d['close'] for d in data]
            ema_50 = HelperFunctions.ema(closes, 50)
            ema_200 = HelperFunctions.ema(closes, 200)
            
            if ema_50[index] and ema_200[index]:
                current_price = data[index]['close']
                if signals.type == SignalType.STRONG_BUY and current_price > ema_50[index] > ema_200[index]:
                    score += 20
                elif signals.type == SignalType.STRONG_SELL and current_price < ema_50[index] < ema_200[index]:
                    score += 20
        
        # 4. Volatility (15 points)
        if index >= 14:
            atr = self._calculate_atr_from_dict(data, 14, index)
            current_price = data[index]['close']
            atr_pct = (atr / current_price) * 100 if current_price > 0 else 0
            
            if 0.5 <= atr_pct <= 1.5:  # Optimal volatility
                score += 15
            elif 0.3 <= atr_pct <= 2.0:
                score += 10
        
        # 5. Time filter (15 points)
        if TradingImprovements.is_tradeable_time(
            datetime.now(), market_type=self.state.config.market_type
        ):
            score += 15
        
        return min(score, 100.0)
    
    def _calculate_atr_from_dict(self, data: List[Dict], period: int, index: int) -> float:
        """Calculate ATR from dict data"""
        if index < period:
            return data[index]['close'] * 0.01  # Fallback
        
        true_ranges = []
        for i in range(max(1, index - period + 1), index + 1):
            high = data[i]['high']
            low = data[i]['low']
            prev_close = data[i-1]['close']
            
            tr = max(
                high - low,
                abs(high - prev_close),
                abs(low - prev_close)
            )
            true_ranges.append(tr)
        
        return sum(true_ranges) / len(true_ranges) if true_ranges else 0.0
    
    def _check_multi_timeframe_trend(
        self,
        symbol: str,
        primary_tf: str,
        higher_tf: str
    ) -> str:
        """Check trend on higher timeframe"""
        try:
            # Convert timeframe
            tf_map = {
                "M1": "1m", "M5": "5m", "M15": "15m",
                "H1": "1h", "H4": "4h", "D": "1d"
            }
            binance_tf = tf_map.get(higher_tf, "1h")
            binance_symbol = symbol.replace("USDT", "/USDT") if "/" not in symbol else symbol
            
            # Fetch higher timeframe data
            higher_data = self.binance_fetcher.fetch_ohlcv(
                binance_symbol, binance_tf, 200
            )
            
            if not higher_data or len(higher_data) < 200:
                return "SIDEWAYS"  # Not enough data
            
            # Convert to dict format
            data = [
                {
                    "time": item.get('time', ''),
                    "open": float(item.get('open', 0)),
                    "high": float(item.get('high', 0)),
                    "low": float(item.get('low', 0)),
                    "close": float(item.get('close', 0)),
                    "volume": float(item.get('volume', 0))
                }
                for item in higher_data
            ]
            
            # Calculate trend
            return TradingImprovements.check_multi_timeframe_trend(
                data, data[-1]['close']
            )
        except Exception as e:
            print(f"Error checking multi-timeframe trend: {e}")
            return "SIDEWAYS"
    
    def _check_correlation(
        self,
        new_symbol: str,
        existing_positions: List[Position]
    ) -> float:
        """Check correlation with existing positions"""
        if not existing_positions:
            return 0.0
        
        try:
            # For now, return 0 (no correlation check)
            # Full implementation would require price history for all symbols
            # This is a placeholder - can be enhanced later
            return 0.0
        except Exception as e:
            print(f"Error checking correlation: {e}")
            return 0.0
    
    def _update_equity(self, current_price: float):
        """Update equity = balance + open P&L"""
        open_pnl = sum(p.current_pnl for p in self.state.open_positions)
        self.state.equity = self.state.balance + open_pnl
    
    def _update_metrics(self):
        """Update performance metrics"""
        if self.state.total_trades > 0:
            self.state.win_rate = (
                self.state.winning_trades / self.state.total_trades * 100
            )
        
        if self.state.total_loss > 0:
            self.state.profit_factor = (
                self.state.total_profit / self.state.total_loss
            )
        else:
            self.state.profit_factor = float('inf') if self.state.total_profit > 0 else 0.0
        
        # Max drawdown calculation
        if self.state.closed_trades:
            cumulative_pnl = self.state.config.initial_balance
            max_equity = cumulative_pnl
            max_dd = 0.0
            
            for trade in self.state.closed_trades:
                cumulative_pnl += trade.pnl
                if cumulative_pnl > max_equity:
                    max_equity = cumulative_pnl
                else:
                    dd = ((max_equity - cumulative_pnl) / max_equity) * 100
                    max_dd = max(max_dd, dd)
            
            self.state.max_drawdown = max_dd
        
        # Daily PnL
        today = datetime.now().date()
        self.state.daily_pnl = sum(
            t.pnl for t in self.state.closed_trades
            if t.exit_time.date() == today
        )
    
    # ===================== STATE MANAGEMENT =====================
    
    def get_state(self) -> Dict:
        """Get current state"""
        if not self.state:
            return {}
        return self.state.to_dict()
    
    def stop(self):
        """Stop trading"""
        if self.state:
            self.state.status = TradeStatus.STOPPED
            self._save_state()
    
    def pause(self):
        """Pause trading"""
        if self.state:
            self.state.status = TradeStatus.PAUSED
            self._save_state()
    
    def resume(self):
        """Resume trading"""
        if self.state:
            self.state.status = TradeStatus.RUNNING
            self._save_state()
    
    def _save_state(self):
        """Save state to file"""
        try:
            if not self.state:
                return
            
            # Use timestamp without colons for Windows filename compatibility
            timestamp = self.state.created_at.strftime('%Y%m%d_%H%M%S')
            filepath = self.DB_DIR / f"{self.state.config.symbol}_{timestamp}.json"
            
            with open(filepath, 'w') as f:
                json.dump(self.state.to_dict(), f, indent=2, default=str)
                
        except Exception as e:
            print(f"Error saving state: {e}")

    
    def close_all_positions(self, current_price: float):
        """Close all open positions"""
        positions = self.state.open_positions.copy()
        for position in positions:
            self._close_position(position, current_price, "MANUAL", None)


# Global instance
_trading_engine = None


def get_live_trading_engine() -> LiveTradingEngine:
    """Get global trading engine instance"""
    global _trading_engine
    if _trading_engine is None:
        _trading_engine = LiveTradingEngine()
    return _trading_engine
