# TradingView vs Python Backtest Discrepancy - Debug Checklist

## ⚠️ Vấn đề: Kết quả TradingView khác hoàn toàn với Python

Nếu kết quả khác nhau nhiều, hãy kiểm tra từng điểm sau:

---

## 🔍 1. TRADINGVIEW SETTINGS (Critical - thường là nguyên nhân chính)

### ✅ Settings → Properties:

1. **Kích thước lệnh mặc định (Default Order Size)**:
   - ❌ WRONG: `1` hoặc bất kỳ số nào > 0
   - ✅ CORRECT: `0` (zero) hoặc để trống
   
2. **Loại (Type)**:
   - ✅ CORRECT: "Fixed" hoặc "Số lượng"
   - ❌ WRONG: "Percentage" hoặc "% Vốn cổ phần"

3. **Vốn ban đầu (Initial Capital)**:
   - ✅ Phải khớp với Python: `1000` (hoặc giá trị bạn dùng)

4. **Hoa hồng (Commission)**:
   - ✅ Phải = `0%` (Python backtest không có commission)

5. **Trượt giá (Slippage)**:
   - ✅ Phải = `0 ticks` (Python backtest không có slippage)

6. **Kim tự tháp (Pyramiding)**:
   - ✅ Phải = `0 orders` (Python không cho phép nhiều position)

### ✅ Kiểm tra sau khi chạy backtest:

- Mở **Trade List** (danh sách trades)
- Xem cột **"Cỡ lệnh"**:
  - ❌ Nếu thấy `"1 hợp đồng"` hoặc `"1"` → **Settings SAI!**
  - ✅ Nếu thấy số như `0.62768`, `0.60111` → **Settings ĐÚNG!**

---

## 🔍 2. DATA PERIOD (Critical - thường bị bỏ qua)

### ✅ Kiểm tra date range:

1. **Python backtest dùng khoảng thời gian nào?**
   - Ví dụ: 2025-11-15 đến 2025-12-13

2. **TradingView đang dùng khoảng thời gian nào?**
   - Click vào chart → Xem date range ở góc dưới
   - ⚠️ TradingView mặc định có thể dùng data từ năm trước!

3. **Phải khớp hoàn toàn:**
   - Same start date
   - Same end date
   - Same timeframe (1h, 15m, etc.)

### ✅ Cách set đúng:

- TradingView → Right-click chart → "Settings" → "Inputs"
- Hoặc dùng date picker trên chart để set date range

---

## 🔍 3. SIGNAL LOGIC MISMATCH

### Kiểm tra Pine Script code có đúng logic không:

1. **Signal counting:**
   ```pine
   // Phải dùng entry_type_long/entry_type_short, KHÔNG phải raw signals
   entry_type_long = bullish_percent >= 70.0
   entry_type_short = bearish_percent >= 70.0
   ```

2. **Candle confirmation:**
   ```pine
   // Phải require 2 candles (hoặc số bạn config)
   long_signal_confirmed := long_signal_count >= 2
   ```

3. **Filter application:**
   ```pine
   // Filters phải apply SAU khi confirm signal
   long_signal := long_signal_confirmed and (filters...)
   ```

---

## 🔍 4. POSITION SIZING LOGIC

### Kiểm tra Pine Script có đúng không:

```pine
// Phải dùng calculate_qty function với initial_capital
calculate_qty(entry_price) =>
    risk_amount = initial_capital * risk_percent / 100
    position_size = risk_amount / (sl_percent / 100)
    qty = position_size / entry_price
    qty

// Phải dùng qty parameter trong strategy.entry()
qty_long = calculate_qty(close)
strategy.entry("Long", strategy.long, qty=qty_long)
```

---

## 🔍 5. ENTRY TIMING

### So sánh entry timing giữa Python và TradingView:

1. **Trade đầu tiên:**
   - Python: Entry vào thời điểm nào?
   - TradingView: Entry vào thời điểm nào?
   - ⚠️ Nếu khác nhau → Có thể do:
     - Signal counting logic khác
     - Candle confirmation khác
     - Filters blocking ở thời điểm khác

2. **Số lượng trades:**
   - Python: Bao nhiêu trades?
   - TradingView: Bao nhiêu trades?
   - ⚠️ Nếu khác nhiều → Có thể do:
     - Filters blocking nhiều hơn
     - Entry conditions khác
     - Position switching logic khác

---

## 🔍 6. DEBUG STEPS

### Step 1: Verify Settings
```
✅ Order Size = 0
✅ Initial Capital = 1000
✅ Commission = 0%
✅ Slippage = 0
✅ Pyramiding = 0
```

### Step 2: Verify Data
```
✅ Same start date
✅ Same end date
✅ Same timeframe
✅ Same symbol
```

### Step 3: Compare First Entry
```
Python CSV:
- Trade #1 entry time: ???
- Entry price: ???
- Position size: ???

TradingView:
- Trade #1 entry time: ???
- Entry price: ???
- Position size (qty): ???
```

### Step 4: Add Debug Output in Pine Script

Thêm vào Pine Script để debug:

```pine
// Debug: Print signal info
if long_signal or short_signal
    var table debugTable = table.new(position.top_right, 2, 4, bgcolor=color.white, border_width=1)
    table.cell(debugTable, 0, 0, "Time", text_color=color.black)
    table.cell(debugTable, 1, 0, str.tostring(time), text_color=color.black)
    table.cell(debugTable, 0, 1, "Bullish %", text_color=color.black)
    table.cell(debugTable, 1, 1, str.tostring(bullish_percent), text_color=color.black)
    table.cell(debugTable, 0, 2, "Signal Count", text_color=color.black)
    table.cell(debugTable, 1, 2, str.tostring(long_signal_count), text_color=color.black)
    table.cell(debugTable, 0, 3, "Qty", text_color=color.black)
    table.cell(debugTable, 1, 3, str.tostring(qty_long), text_color=color.black)
```

---

## 🎯 COMMON ISSUES & SOLUTIONS

### Issue 1: "Kết quả khác 10-20%"
- **Nguyên nhân:** Position sizing hoặc commission/slippage
- **Giải pháp:** Check Settings → Order Size = 0

### Issue 2: "Kết quả khác hoàn toàn, số trades khác nhau"
- **Nguyên nhân:** Entry timing hoặc signal logic khác
- **Giải pháp:** Check date range và signal counting logic

### Issue 3: "Trade đầu tiên khác thời gian"
- **Nguyên nhân:** Candle confirmation hoặc filters blocking
- **Giải pháp:** Check candle_confirmation và filter logic

### Issue 4: "Position size là 1 thay vì calculated qty"
- **Nguyên nhân:** TradingView Settings override
- **Giải pháp:** Set Order Size = 0 trong Settings

---

## 📝 DEBUG TEMPLATE

Copy và điền thông tin:

```
=== PYTHON BACKTEST ===
Date Range: ____ to ____
Timeframe: ____
Initial Capital: ____
Total Trades: ____
First Entry: Time=____, Price=____, Qty=____
Final Profit: ____%

=== TRADINGVIEW BACKTEST ===
Date Range: ____ to ____
Timeframe: ____
Initial Capital: ____
Order Size Setting: ____ (phải là 0!)
Total Trades: ____
First Entry: Time=____, Price=____, Qty=____ (check trong trade list!)
Final Profit: ____%

=== COMPARISON ===
Date Match: [ ] Yes [ ] No
Trades Count Match: [ ] Yes [ ] No
First Entry Match: [ ] Yes [ ] No
Profit Match: [ ] Yes [ ] No
```

---

## 🔧 QUICK FIX CHECKLIST

Trước khi test lại, đảm bảo:

- [ ] TradingView Settings → Order Size = **0**
- [ ] TradingView Settings → Commission = **0%**
- [ ] TradingView Settings → Slippage = **0 ticks**
- [ ] Date range trong TradingView **khớp** với Python
- [ ] Initial Capital trong TradingView **khớp** với Python
- [ ] Check trade list → Position size phải là số như `0.62768`, không phải `1`
- [ ] Regenerate Pine Script sau khi fix Python code
- [ ] Clear TradingView chart và load lại script

---

## 📞 NEXT STEPS

Nếu vẫn khác nhau sau khi check tất cả:

1. **Export Pine Script** từ app
2. **Copy code** và paste vào TradingView
3. **Check Settings** theo checklist trên
4. **Run backtest** với đúng date range
5. **Compare** trade-by-trade với Python CSV
6. **Tìm trade đầu tiên khác nhau** → Đó là điểm bắt đầu debug

Nếu trade đầu tiên đã khác → Có thể do:
- Signal calculation khác
- Indicator values khác
- Filter application khác
- Candle confirmation timing khác

