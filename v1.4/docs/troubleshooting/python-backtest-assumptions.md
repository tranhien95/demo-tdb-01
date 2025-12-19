# Python Backtest - Assumptions & Settings

## 🔍 CÁC ASSUMPTIONS TRONG PYTHON BACKTEST

### 1. **Order Execution Timing**

#### Python Backtest:
```python
# backend/main.py line 167-240
for i in range(50, len(ohlcv_data) - 1):
    # Check signal at candle i
    # Execute order at candle i's CLOSE price
    entry = ohlcv_data[i]['close']  # Uses CLOSE price
```

**Assumption:**
- Signal được check tại candle `i`
- Order được execute ngay tại **CLOSE price** của candle `i`
- Không có delay giữa signal và execution

#### TradingView:
```pine
// Pine Script
if long_signal and strategy.position_size == 0
    strategy.entry("Long", strategy.long, qty=qty_long)
```

**Behavior:**
- `calc_on_order_fills=false` → Order execute tại **bar close**
- `calc_on_order_fills=true` → Order execute tại **bar open** (next bar)

**Pine Script Generated:**
```pine
calc_on_order_fills=false  // Matches Python: execute at bar close
```

**✅ GIỐNG NHAU** - Cả 2 đều execute tại bar close

---

### 2. **Position Sizing**

#### Python Backtest:
```python
# backend/main.py line 246-247
risk_amount = capital * (risk_pct / 100)
position_size = risk_amount / (sl_pct / 100)
```

**Assumption:**
- Dùng **FIXED capital** (không thay đổi theo balance)
- Position size = Risk amount / SL distance
- Không dùng `balance` (current balance), luôn dùng `capital` (initial)

#### TradingView:
```pine
// Pine Script generated
calculate_qty(entry_price) =>
    risk_amount = initial_capital * risk_percent / 100
    position_size = risk_amount / (sl_percent / 100)
    qty = position_size / entry_price
    qty
```

**✅ GIỐNG NHAU** - Cả 2 đều dùng fixed initial capital

---

### 3. **Commission & Slippage**

#### Python Backtest:
```python
# NO commission/slippage in calculation
# Profit = position_size * (exit_price - entry_price) / entry_price
actual_profit_usd = position_size_old * (profit_pct / 100)
```

**Assumption:**
- Commission = **0%**
- Slippage = **0**
- No fees deducted

#### TradingView:
```pine
// Pine Script generated
commission_type=strategy.commission.percent,
commission_value=0.0,
slippage=0,
```

**✅ GIỐNG NHAU** - Cả 2 đều = 0

---

### 4. **Pyramiding (Multiple Positions)**

#### Python Backtest:
```python
# backend/main.py line 240
if should_enter and not current_position:
    # Only enter if NO current position
    # Cannot have multiple positions
```

**Assumption:**
- **Chỉ 1 position** tại một thời điểm
- Không cho phép pyramiding
- Nếu có position → Phải close trước khi enter mới

#### TradingView:
```pine
// Pine Script generated
pyramiding=0,  // No pyramiding
```

**✅ GIỐNG NHAU** - Cả 2 đều không cho phép pyramiding

---

### 5. **Signal Calculation Timing**

#### Python Backtest:
```python
# backend/main.py line 167-184
for i in range(50, len(ohlcv_data) - 1):
    all_candle_signals = all_signals[i]  # Signals at candle i
    # Calculate entry_type based on signals at candle i
    # Check if should enter at candle i
```

**Assumption:**
- Signals được tính tại candle `i`
- Entry decision được làm tại candle `i`
- Order execute tại **close của candle `i`**

#### TradingView:
```pine
// Pine Script
// Signals calculated on each bar
// Entry executed at bar close (calc_on_order_fills=false)
```

**✅ GIỐNG NHAU** - Cả 2 đều check signal và execute tại bar close

---

### 6. **Candle Confirmation Logic**

#### Python Backtest:
```python
# backend/main.py line 226-230
if entry_type and entry_type == last_signal:
    signal_count += 1
else:
    last_signal = entry_type
    signal_count = 1

should_enter = (entry_type and 
                filter_passed and
                signal_count >= candle_confirmation)
```

**Assumption:**
- `signal_count` tăng khi signal **giống nhau** liên tiếp
- Reset về 1 khi signal **thay đổi**
- Entry chỉ khi `signal_count >= candle_confirmation`

#### TradingView:
```pine
// Pine Script generated
if entry_type_long
    if last_signal_type == "LONG"
        long_signal_count := long_signal_count + 1
    else
        long_signal_count := 1
long_signal := long_signal_count >= candle_confirmation
```

**✅ GIỐNG NHAU** - Logic giống hệt

---

### 7. **Position Switching**

#### Python Backtest:
```python
# backend/main.py line 266-298
elif should_enter and current_position and current_position != entry_type:
    # Close current position at current_close
    # Enter new position at current_close (same candle)
    last_trade['exit'] = round(current_close, 2)
    # ... calculate profit ...
    # Then enter new position
    entry = current_close
```

**Assumption:**
- Close và Enter xảy ra tại **cùng một candle**
- Close price = Entry price (cho position mới)
- Profit được tính từ entry cũ đến close price

#### TradingView:
```pine
// Pine Script generated
// Position Switch - Short to Long
if long_signal and strategy.position_size < 0
    strategy.close("Short")  // Close SHORT
    strategy.entry("Long", strategy.long, qty=qty_long)  // Enter LONG
```

**⚠️ CÓ THỂ KHÁC:**
- TradingView có thể close và enter tại **cùng bar close**
- Nhưng execution order có thể khác (close trước, enter sau)
- Price có thể khác một chút nếu TradingView dùng different execution model

---

### 8. **Stop Loss & Take Profit Execution**

#### Python Backtest:
```python
# backend/main.py line 242-243
sl = entry * (1 - sl_pct / 100) if entry_type == 'LONG' else entry * (1 + sl_pct / 100)
tp = entry + (entry - sl) * rr_ratio if entry_type == 'LONG' else entry - (sl - entry) * rr_ratio

# Check if SL/TP hit at next candle
# Uses high/low of next candle to check
```

**Assumption:**
- SL/TP được check tại **candle tiếp theo** (i+1)
- Dùng `high` và `low` của candle để check
- Nếu `low <= SL` (LONG) → Exit at SL
- Nếu `high >= TP` (LONG) → Exit at TP

#### TradingView:
```pine
// Pine Script generated
strategy.exit("Long Exit", "Long", stop=long_sl, limit=long_tp)
```

**⚠️ CÓ THỂ KHÁC:**
- TradingView check SL/TP **trong real-time** (intra-bar)
- Python chỉ check tại **bar close**
- Nếu SL/TP hit trong bar → TradingView exit sớm hơn Python

---

## 🎯 TÓM TẮT ASSUMPTIONS

| Setting | Python Backtest | TradingView (Generated) | Match? |
|---------|----------------|------------------------|--------|
| **Order Execution** | Bar close | Bar close (`calc_on_order_fills=false`) | ✅ |
| **Position Sizing** | Fixed capital | Fixed initial_capital | ✅ |
| **Commission** | 0% | 0% | ✅ |
| **Slippage** | 0 | 0 | ✅ |
| **Pyramiding** | 0 (single position) | 0 | ✅ |
| **Signal Timing** | Bar close | Bar close | ✅ |
| **Candle Confirmation** | Count-based | Count-based | ✅ |
| **Position Switch** | Same candle | Same bar | ⚠️ Có thể khác |
| **SL/TP Check** | Next candle (high/low) | Intra-bar (real-time) | ⚠️ Có thể khác |

---

## ⚠️ CÁC ĐIỂM CÓ THỂ KHÁC

### 1. **SL/TP Execution Timing**

**Python:**
- Check SL/TP tại **candle close** (i+1)
- Dùng `high`/`low` của candle
- Nếu `low <= SL` → Exit at SL price

**TradingView:**
- Check SL/TP **intra-bar** (real-time)
- Có thể exit **sớm hơn** nếu SL/TP hit trong bar
- Exit price có thể khác (closer to SL/TP)

**Impact:**
- TradingView có thể exit **sớm hơn** → Profit/Loss khác một chút
- Nếu SL tight → TradingView có thể avoid một số losses mà Python không

### 2. **Position Switching Execution**

**Python:**
- Close và Enter tại **cùng candle**
- Close price = Entry price (theoretical)
- Profit được tính từ entry cũ đến close price

**TradingView:**
- Close và Enter tại **cùng bar**
- Execution order: Close trước, Enter sau
- Price có thể khác một chút (spread, execution model)

**Impact:**
- Nếu spread lớn → Profit/Loss khác một chút
- Nếu execution model khác → Timing khác

---

## 🔧 CÁCH VERIFY ASSUMPTIONS

### 1. **Check Order Execution Timing**

**Python:**
```python
# Entry at candle i's close
entry = ohlcv_data[i]['close']
entry_time = ohlcv_data[i]['time']
```

**TradingView:**
- Check Trade List → Entry time
- Phải khớp với Python entry time

### 2. **Check SL/TP Execution**

**Python:**
```python
# Check at next candle (i+1)
if ohlcv_data[i+1]['low'] <= sl:
    exit_price = sl
```

**TradingView:**
- Check Trade List → Exit time
- Nếu exit **sớm hơn** Python → TradingView exit intra-bar
- Nếu exit **giống** Python → Cả 2 exit tại bar close

### 3. **Check Position Size**

**Python:**
```python
position_size = risk_amount / (sl_pct / 100)
# Example: 100 / 0.05 = 2000
```

**TradingView:**
- Check Trade List → Position size
- Phải khớp với Python position size

---

## ✅ KẾT LUẬN

**Python Backtest Assumptions:**
- ✅ Order execution tại bar close
- ✅ Fixed capital cho position sizing
- ✅ No commission/slippage
- ✅ Single position (no pyramiding)
- ✅ Signal check và execute tại cùng bar
- ⚠️ SL/TP check tại next candle (có thể khác TradingView)
- ⚠️ Position switch tại cùng candle (có thể khác execution model)

**TradingView Match:**
- ✅ Most settings match
- ⚠️ SL/TP execution có thể khác (intra-bar vs next candle)
- ⚠️ Position switch execution có thể khác (execution model)

**Nếu kết quả khác:**
- **10-20% khác** → Có thể do SL/TP execution timing
- **Hoàn toàn khác** → Có thể do Settings override hoặc date range

