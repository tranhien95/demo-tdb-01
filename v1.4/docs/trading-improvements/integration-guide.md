# 🔧 HƯỚNG DẪN TÍCH HỢP TRADING IMPROVEMENTS

## 📋 Tổng Quan

File này hướng dẫn cách tích hợp các cải tiến trading vào `live_trading_engine.py` và `strategy_engine.py`.

---

## 🚀 BƯỚC 1: Import Module

Thêm vào đầu file `live_trading_engine.py`:

```python
from trading_improvements import TradingImprovements
```

---

## 🎯 BƯỚC 2: Tích Hợp Trailing Stop Loss

### Trong method `_check_exit_conditions`:

```python
def _check_exit_conditions(self, current_price: float, signals: SignalWithConfidence):
    """Check exit conditions với trailing stop"""
    for position in self.state.open_positions[:]:
        # 1. Tính ATR cho trailing stop
        symbol = self.state.config.symbol
        candles = self.price_history.get(symbol, [])
        if len(candles) >= 14:
            atr = self._calculate_atr(candles, 14)
        else:
            atr = position.entry_price * 0.01  # Fallback: 1%
        
        # 2. Update trailing stop
        trailing_updated = TradingImprovements.update_trailing_stop(
            position, current_price, atr, trailing_multiplier=1.5
        )
        
        if trailing_updated:
            print(f"[Trailing] Updated SL for {position.side} @ {position.stoploss:.2f}")
        
        # 3. Check breakeven
        breakeven_set = TradingImprovements.check_breakeven_stop(
            position, current_price, breakeven_r=1.0, buffer_pct=0.1
        )
        
        if breakeven_set:
            print(f"[Breakeven] SL moved to breakeven @ {position.stoploss:.2f}")
        
        # 4. Check partial profit taking
        partial_rules = getattr(position, 'partial_rules', [
            {"r_level": 1.0, "close_pct": 0.5, "taken": False},
            {"r_level": 2.0, "close_pct": 0.25, "taken": False}
        ])
        
        close_pct = TradingImprovements.check_partial_profit_taking(
            position, current_price, partial_rules
        )
        
        if close_pct:
            self._close_partial_position(position, close_pct)
            position.partial_rules = partial_rules  # Save updated rules
        
        # 5. Check SL/TP (existing logic)
        exit_price = None
        exit_reason = None
        
        if position.side == "LONG":
            if current_price <= position.stoploss:
                exit_price = position.stoploss
                exit_reason = "SL"
            elif current_price >= position.takeprofit:
                exit_price = position.takeprofit
                exit_reason = "TP"
        else:  # SHORT
            if current_price >= position.stoploss:
                exit_price = position.stoploss
                exit_reason = "SL"
            elif current_price <= position.takeprofit:
                exit_price = position.takeprofit
                exit_reason = "TP"
        
        # 6. Check reversal signal
        if not exit_reason:
            if position.side == "LONG" and signals.type == SignalType.STRONG_SELL:
                exit_price = current_price
                exit_reason = "Reversal"
            elif position.side == "SHORT" and signals.type == SignalType.STRONG_BUY:
                exit_price = current_price
                exit_reason = "Reversal"
        
        if exit_price and exit_reason:
            self._close_position(position, exit_price, exit_reason, signals)
```

### Thêm helper method `_calculate_atr`:

```python
def _calculate_atr(self, candles: List[CandleData], period: int = 14) -> float:
    """Calculate ATR from candles"""
    if len(candles) < period + 1:
        return 0.0
    
    true_ranges = []
    for i in range(1, len(candles)):
        high = candles[i].high
        low = candles[i].low
        prev_close = candles[i-1].close
        
        tr = max(
            high - low,
            abs(high - prev_close),
            abs(low - prev_close)
        )
        true_ranges.append(tr)
    
    # ATR = SMA of True Ranges
    atr = sum(true_ranges[-period:]) / period
    return atr
```

### Thêm method `_close_partial_position`:

```python
def _close_partial_position(self, position: Position, close_pct: float):
    """Close một phần position"""
    if close_pct <= 0 or close_pct >= 1:
        return
    
    # Calculate partial quantity
    partial_quantity = position.quantity * close_pct
    remaining_quantity = position.quantity * (1 - close_pct)
    
    # Calculate P&L cho phần đóng
    current_price = self._get_current_price(position.symbol)
    if position.side == "LONG":
        profit = (current_price - position.entry_price) * partial_quantity
    else:
        profit = (position.entry_price - current_price) * partial_quantity
    
    # Update position
    position.quantity = remaining_quantity
    position.entry_value = position.entry_price * remaining_quantity
    
    # Update balance
    self.state.balance += profit
    
    # Log
    print(f"[Partial] Closed {close_pct*100:.0f}% of {position.side} position. Profit: ${profit:.2f}")
    
    # Nếu đóng hết (do rounding), remove position
    if remaining_quantity < 0.001:
        self.state.open_positions.remove(position)
```

---

## 🎯 BƯỚC 3: Tích Hợp Dynamic Position Sizing

### Trong method `_open_position`:

```python
def _open_position(self, entry_price: float, side: str, signals: SignalWithConfidence) -> Optional[Position]:
    """Open new position với dynamic sizing"""
    try:
        # 1. Tính volatility
        symbol = self.state.config.symbol
        candles = self.price_history.get(symbol, [])
        if len(candles) >= 14:
            atr = self._calculate_atr(candles, 14)
            volatility_pct = (atr / entry_price) * 100
        else:
            volatility_pct = 1.0  # Default
        
        # 2. Tính dynamic position size
        base_risk_pct = self.state.config.risk_percent
        confidence = signals.confidence
        
        adjusted_risk_pct = TradingImprovements.calculate_dynamic_position_size(
            base_risk_pct=base_risk_pct,
            confidence=confidence,
            volatility_pct=volatility_pct,
            max_multiplier=2.0
        )
        
        print(f"[Dynamic Sizing] Base: {base_risk_pct}% → Adjusted: {adjusted_risk_pct:.2f}% (Confidence: {confidence:.1f}%)")
        
        # 3. Calculate position size với adjusted risk
        risk_amount = self.state.balance * (adjusted_risk_pct / 100)
        sl_distance_pct = self.state.config.stoploss_percent / 100
        quantity = risk_amount / (entry_price * sl_distance_pct)
        
        # 4. Check margin
        position_cost = quantity * entry_price
        if position_cost > self.state.available_margin:
            print(f"[Warning] Insufficient margin. Need: ${position_cost:.2f}, Available: ${self.state.available_margin:.2f}")
            return None
        
        # 5. Calculate SL & TP (có thể dùng ATR-based)
        if self.state.config.use_atr_sl_tp:  # New config option
            sl_distance_pct, tp_distance_pct = TradingImprovements.calculate_atr_based_sl_tp(
                entry_price, atr, rr_ratio=self.state.config.reward_ratio
            )
        else:
            sl_distance_pct = self.state.config.stoploss_percent / 100
            tp_distance_pct = sl_distance_pct * 2  # 2:1 R:R
        
        if side == "LONG":
            stoploss = entry_price * (1 - sl_distance_pct)
            takeprofit = entry_price * (1 + tp_distance_pct)
        else:  # SHORT
            stoploss = entry_price * (1 + sl_distance_pct)
            takeprofit = entry_price * (1 - tp_distance_pct)
        
        # 6. Create position với partial rules
        position = Position(
            id=str(uuid.uuid4()),
            symbol=symbol,
            side=side,
            entry_price=entry_price,
            quantity=quantity,
            entry_time=datetime.now(),
            stoploss=stoploss,
            takeprofit=takeprofit,
            entry_signal=signals.type,
            entry_confidence=signals.confidence,
            partial_rules=[  # Initialize partial rules
                {"r_level": 1.0, "close_pct": 0.5, "taken": False},
                {"r_level": 2.0, "close_pct": 0.25, "taken": False}
            ]
        )
        
        # 7. Update state
        self.state.open_positions.append(position)
        self.state.used_margin += position_cost
        self.state.available_margin -= position_cost
        
        print(f"[Entry] {side} @ ${entry_price:.2f}, Size: {quantity:.4f}, SL: ${stoploss:.2f}, TP: ${takeprofit:.2f}")
        
        return position
        
    except Exception as e:
        print(f"Error opening position: {e}")
        import traceback
        traceback.print_exc()
        return None
```

---

## 🎯 BƯỚC 4: Tích Hợp Multi-Timeframe Confirmation

### Trong method `_check_entry_conditions`:

```python
def _check_entry_conditions(self, current_price: float, signals: SignalWithConfidence):
    """Check entry conditions với multi-timeframe confirmation"""
    # 1. Check signal quality score
    symbol = self.state.config.symbol
    candles = self.price_history.get(symbol, [])
    
    if len(candles) < 50:
        return
    
    # Calculate volume ratio
    current_vol = candles[-1].volume
    avg_vol = sum([c.volume for c in candles[-20:]]) / 20
    volume_ratio = current_vol / avg_vol if avg_vol > 0 else 1.0
    
    # Check trend alignment
    ema_50 = HelperFunctions.ema([c.close for c in candles], 50)
    ema_200 = HelperFunctions.ema([c.close for c in candles], 200)
    trend_aligned = False
    
    if ema_50[-1] and ema_200[-1]:
        if signals.type == SignalType.STRONG_BUY and current_price > ema_50[-1] > ema_200[-1]:
            trend_aligned = True
        elif signals.type == SignalType.STRONG_SELL and current_price < ema_50[-1] < ema_200[-1]:
            trend_aligned = True
    
    # Check volatility
    atr = self._calculate_atr(candles, 14)
    atr_pct = (atr / current_price) * 100
    volatility_optimal = 0.5 <= atr_pct <= 1.5
    
    # Check time
    time_optimal = TradingImprovements.is_tradeable_time(
        datetime.now(), market_type="crypto"
    )
    
    # Calculate quality score
    quality_score = TradingImprovements.calculate_signal_quality_score(
        confidence=signals.confidence,
        volume_ratio=volume_ratio,
        trend_aligned=trend_aligned,
        volatility_optimal=volatility_optimal,
        time_optimal=time_optimal
    )
    
    print(f"[Signal Quality] Score: {quality_score:.1f}/100 (Confidence: {signals.confidence:.1f}%)")
    
    # Chỉ trade khi quality score >= 70
    if quality_score < 70:
        print(f"[Skip] Signal quality too low: {quality_score:.1f} < 70")
        return
    
    # 2. Multi-timeframe confirmation
    primary_tf = self.state.config.timeframe
    higher_tf_map = {
        "M1": "M5", "M5": "M15", "M15": "H1",
        "H1": "H4", "H4": "D", "D": "D"
    }
    higher_tf = higher_tf_map.get(primary_tf, "H1")
    
    # Fetch higher timeframe data
    tf_map = {
        "M1": "1m", "M5": "5m", "M15": "15m",
        "H1": "1h", "H4": "4h", "D": "1d"
    }
    binance_tf = tf_map.get(higher_tf, "1h")
    binance_symbol = symbol.replace("USDT", "/USDT") if "/" not in symbol else symbol
    
    higher_data = self.binance_fetcher.fetch_ohlcv(
        binance_symbol, binance_tf, 200
    )
    
    if higher_data:
        higher_trend = TradingImprovements.check_multi_timeframe_trend(
            higher_data, current_price
        )
        
        # Check alignment
        if signals.type == SignalType.STRONG_BUY and higher_trend != "UPTREND":
            print(f"[Skip] Higher TF ({higher_tf}) trend: {higher_trend}, but signal is LONG")
            return
        elif signals.type == SignalType.STRONG_SELL and higher_trend != "DOWNTREND":
            print(f"[Skip] Higher TF ({higher_tf}) trend: {higher_trend}, but signal is SHORT")
            return
        
        print(f"[MTF] Higher TF ({higher_tf}) trend: {higher_trend} ✓")
    
    # 3. Original entry logic
    min_confidence = 65.0
    
    if signals.type == SignalType.STRONG_BUY and signals.confidence >= min_confidence:
        if len(self.state.open_positions) < self.state.config.max_positions:
            self._open_position(current_price, "LONG", signals)
    elif signals.type == SignalType.STRONG_SELL and signals.confidence >= min_confidence:
        if len(self.state.open_positions) < self.state.config.max_positions:
            self._open_position(current_price, "SHORT", signals)
```

---

## 🎯 BƯỚC 5: Update Models

Thêm vào `live_trading_models.py`:

```python
class Position(BaseModel):
    # ... existing fields ...
    
    # New fields for improvements
    trailing_activated: bool = False
    breakeven_set: bool = False
    partial_rules: List[Dict] = Field(default_factory=lambda: [
        {"r_level": 1.0, "close_pct": 0.5, "taken": False},
        {"r_level": 2.0, "close_pct": 0.25, "taken": False}
    ])

class TradingConfig(BaseModel):
    # ... existing fields ...
    
    # New config options
    use_atr_sl_tp: bool = Field(default=False, description="Use ATR-based SL/TP")
    enable_trailing_stop: bool = Field(default=True, description="Enable trailing stop")
    enable_breakeven: bool = Field(default=True, description="Enable breakeven stop")
    enable_partial_profit: bool = Field(default=True, description="Enable partial profit taking")
    enable_multi_timeframe: bool = Field(default=True, description="Enable multi-timeframe confirmation")
    min_signal_quality: float = Field(default=70.0, description="Minimum signal quality score")
```

---

## ✅ TESTING

### 1. Test Trailing Stop:
```python
# Tạo test position
position = Position(
    entry_price=100.0,
    stoploss=99.0,  # 1% SL
    side="LONG"
)

# Simulate price movement
prices = [100, 101, 102, 103, 102, 101]  # Price tăng rồi giảm
atr = 0.5

for price in prices:
    updated = TradingImprovements.update_trailing_stop(position, price, atr)
    print(f"Price: {price}, SL: {position.stoploss}, Updated: {updated}")
```

### 2. Test Breakeven:
```python
position = Position(
    entry_price=100.0,
    stoploss=99.0,  # 1% SL
    side="LONG"
)

# Price tăng 1.5% (1.5R)
updated = TradingImprovements.check_breakeven_stop(position, 101.5, breakeven_r=1.0)
print(f"Breakeven set: {updated}, SL: {position.stoploss}")
```

### 3. Test Dynamic Sizing:
```python
base_risk = 2.0  # 2%
sizes = []
for confidence in [60, 70, 80, 90, 95]:
    size = TradingImprovements.calculate_dynamic_position_size(
        base_risk, confidence, volatility_pct=1.0
    )
    sizes.append((confidence, size))
    print(f"Confidence: {confidence}% → Risk: {size:.2f}%")
```

---

## 📊 MONITORING

Thêm logging để track performance:

```python
# Trong _check_exit_conditions
if trailing_updated:
    self._log_trade_event({
        "type": "trailing_stop",
        "position_id": position.id,
        "new_sl": position.stoploss,
        "current_price": current_price
    })

if breakeven_set:
    self._log_trade_event({
        "type": "breakeven",
        "position_id": position.id,
        "new_sl": position.stoploss
    })
```

---

## 🎯 NEXT STEPS

1. ✅ Implement từng feature một
2. ✅ Backtest với historical data
3. ✅ Paper trading 1-2 tuần
4. ✅ Monitor performance metrics
5. ✅ Adjust parameters nếu cần
6. ✅ Deploy từng bước

---

**Good luck! 🚀**


