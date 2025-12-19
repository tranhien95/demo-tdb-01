# 📊 Pine Script Testing Guide - Combo Optimizer

## ✅ Checklist trước khi test trên TradingView

### 1. **Settings trong Pine Script Code (đã được set trong code)**
- ✅ `default_qty_type=strategy.fixed` - Sử dụng fixed quantity
- ✅ `commission_value=0.0` - Không có commission
- ✅ `slippage=0` - Không có slippage  
- ✅ `pyramiding=0` - Không cho phép multiple positions
- ✅ `calc_on_order_fills=false` - Tính toán trên bar close
- ✅ `close_entries_rule="ANY"` - Đóng position khi có exit signal

### 2. **Settings trong TradingView UI (PHẢI KIỂM TRA THỦ CÔNG)**

#### ⚠️ QUAN TRỌNG NHẤT: Order Size
1. Click icon **⚙️ Settings** (góc trên bên phải chart)
2. Vào tab **"Properties"** hoặc **"Strategy Properties"**
3. Tìm **"Order Size"** section
4. **Type** phải là **"Fixed"** (KHÔNG phải "Contracts" hay "Percentage")
5. Value có thể để trống hoặc bất kỳ (code sẽ override bằng `qty=` parameter)

#### Kiểm tra các settings khác:
- **Initial Capital**: Phải = 1000 (hoặc giá trị bạn đã set trong combo optimizer)
- **Commission**: Nên set = 0% (code đã set nhưng UI có thể override)
- **Slippage**: Nên set = 0 ticks (code đã set nhưng UI có thể override)

### 3. **Data Period (Phải giống Python)**
1. Đảm bảo chart hiển thị đúng symbol (ví dụ: BINANCE:ETHUSDT)
2. Đảm bảo timeframe đúng (ví dụ: 1h)
3. Set vùng backtest trong TradingView:
   - Click **"Strategy Tester"** tab (bên dưới chart)
   - Set **"From"** và **"To"** dates giống với Python backtest
   - Ví dụ: From: 2025-11-13, To: 2025-12-13

### 4. **So sánh kết quả**

#### Metrics cần so sánh:
- ✅ **Tổng số trades**: Python vs TradingView
- ✅ **Entry timing**: Ngày giờ entry đầu tiên
- ✅ **Position size**: Quy mô vị thế (số lượng và giá trị)
- ✅ **P&L**: Lợi nhuận ròng và %

#### Nếu vẫn lệch:
1. **Kiểm tra lại Settings** (đặc biệt Order Size)
2. **Kiểm tra data period** có match không
3. **Kiểm tra indicator signals** bằng cách plot trên chart:
   ```pine
   plotshape(long_signal, "Long", shape.triangleup)
   plotshape(short_signal, "Short", shape.triangledown)
   plot(bullish_percent, "Bullish %")
   plot(bearish_percent, "Bearish %")
   ```
4. So sánh signals giữa Python và TradingView ở cùng timestamp

---

## 🐛 Debug Tips

### Plot để debug:
1. Plot bullish/bearish percentages để xem signal generation
2. Plot long_signal/short_signal để xem entry signals
3. Plot raw_long_signal/raw_short_signal để xem trước confirmation
4. Plot signal counts để xem candle confirmation

### Common Issues:

#### Issue 1: Position Size = "1 hợp đồng"
- **Nguyên nhân**: TradingView Settings → Order Size → Type = "Contracts"
- **Fix**: Đổi thành "Fixed"

#### Issue 2: Số trades khác nhau (ít hơn Python)
- **Nguyên nhân**: Entry timing khác do signal generation hoặc filters
- **Debug**: Plot signals và so sánh với Python ở cùng timestamp

#### Issue 3: P&L khác nhau
- **Nguyên nhân**: Position size khác (do settings) hoặc entry/exit timing khác
- **Debug**: Check position size trong trade list, so sánh với Python

---

## ✅ Best Practice

1. **Luôn test Pine Script trên TradingView** sau khi generate
2. **Kiểm tra Settings TRƯỚC khi chạy backtest**
3. **So sánh trade-by-trade** giữa Python và TradingView
4. **Report discrepancies** với:
   - Settings hiện tại
   - Entry timing khác nhau
   - Position size khác nhau

