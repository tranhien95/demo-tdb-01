# 🚀 Combo Optimizer v1.1 - Hướng Dẫn Chạy

🔗 **GitHub**: https://github.com/tranhien95/demo-tdb-01.git

---

## 📋 Yêu Cầu
- **Browser**: Chrome, Firefox, Safari, Edge (bất kỳ)
- **Python**: 3.6+ (chạy HTTP server)
- **Files**: 
  - `combo-optimizer-v2.html` ✅
  - `OANDA_XAUUSD_15.csv` ✅
  - `REQUIREMENTS.md` (tham khảo)

---

## ⚡ Cách Chạy

### **Step 1: Mở PowerShell/Terminal**
```powershell
# Điều hướng đến thư mục
cd d:\Trade\Demo1\v1.1
```

### **Step 2: Khởi Động HTTP Server**
```powershell
# Option A: Python HTTP Server (khuyến nghị)
python -m http.server 8000

# Option B: Python3
python3 -m http.server 8000

# Option C: Node.js (nếu có)
npx http-server -p 8000
```

**Output sẽ hiển thị:**
```
Serving HTTP on 0.0.0.0 port 8000 (http://0.0.0.0:8000/) ...
```

### **Step 3: Mở Browser**
```
http://localhost:8000/combo-optimizer-v2.html
```

Hoặc copy-paste URL vào address bar.

---

## 🎯 Sử Dụng Tool

### **1️⃣ Upload CSV Data**
1. Click nút **"📂 Chọn File"**
2. Chọn file `OANDA_XAUUSD_15.csv`
3. Chờ message **"✅ Tải thành công: [số] candles"**

### **2️⃣ Cấu Hình Tối Ưu Hóa**

| Tham Số | Mặc Định | Mô Tả |
|---------|---------|-------|
| **Min Combo** | 2 | Số chỉ báo tối thiểu |
| **Max Combo** | 3 | Số chỉ báo tối đa |
| **Threshold** | 70 | % chỉ báo cần đồng ý |
| **Risk %** | 1 | % vốn mỗi trade |
| **RR Ratio** | 2 | TP = SL × RR |
| **SL %** | 1.5 | Distance SL từ entry |

**Ví dụ cấu hình:**
- Combo 2-3: Test tổ hợp 2-3 chỉ báo
- Threshold 70%: ≥70% chỉ báo phải đồng ý
- Risk 1%: Mỗi trade dùng 1% vốn
- SL 1.5%: Stop loss 1.5% từ entry

### **3️⃣ Chạy Optimization**
1. Đảm bảo CSV đã load ✅
2. Click **"▶️ Chạy Optimization"**
3. Chờ progress bar hoàn tất (5-30 phút tuỳ CSV size)

### **4️⃣ Xem Kết Quả**
1. Bảng **Top 100 Combos** hiển thị:
   - Trades: Số trade
   - Wins/Losses: Thắng/Thua
   - Win Rate: % thắng
   - Profit %: Lợi nhuận
   - Profit Factor: Chất lượng (>1 = lãi)
   - Drawdown: Mức giảm tối đa
   - Sharpe Ratio: Risk-adjusted return

2. **Search/Filter**: Dùng ô tìm kiếm để lọc combo

### **5️⃣ Chi Tiết Trade**
1. **Click vào combo** bất kỳ trong bảng
2. Xem **Chart** với:
   - 📈 Price line (Close, High, Low)
   - 🟢 Green ▲ = LONG entry
   - 🔴 Red ▼ = SHORT entry
   - ✅ Green circle = Exit lãi
   - ❌ Red circle = Exit lỗ

3. **Trade Stats**:
   - Total Trades
   - Wins / Losses
   - Total Profit %
   - Avg Win/Loss %

4. **Trades Table**:
   - #, Entry Time, Entry Price
   - Exit Time, Exit Price
   - SL, TP, Profit $, Profit %, Type

### **6️⃣ Export Trades**
1. Click **"📥 Tải CSV"** (trong trades table)
2. File `trades_[combo_name].csv` sẽ download

---

## 🔍 Hiểu Risk Management

### Ví Dụ Thực Tế
```
Balance: 100 USD
Risk %: 1%
Risk Amount: 100 × 1% = 1 USD

Entry: 4050
SL %: 1.5%
SL Price: 4050 × 0.985 = 3988.25

RR Ratio: 2.0
TP Price: 4050 + (4050-3988.25)×2 = 4173.5

📊 Nếu Exit = 4100 (thắng):
- Profit = 4100 - 4050 = 50
- Profit % = 50/4050 = 1.23%
- P&L = Risk × Profit% / SL% = 1 × 1.23 / 1.5 = 0.82 USD
- Balance mới = 100.82 USD
```

---

## ⚙️ Cấu Hình Mặc Định Khuyến Nghị

### **Đối với Beginner:**
- Combo: 2-2 (chỉ 2 chỉ báo)
- Threshold: 70%
- Risk: 0.5% (an toàn hơn)
- SL: 2%

### **Đối với Intermediate:**
- Combo: 2-4
- Threshold: 70%
- Risk: 1%
- SL: 1.5%

### **Đối với Advanced:**
- Combo: 3-5
- Threshold: 60% (mở rộng hơn)
- Risk: 1-2%
- SL: 1-1.5%

---

## 🐛 Troubleshooting

### **Server không chạy**
```powershell
# Kiểm tra port 8000 có occupied không
netstat -ano | findstr :8000

# Dùng port khác
python -m http.server 8001
# Rồi mở: http://localhost:8001/combo-optimizer-v2.html
```

### **CSV không load được**
1. Kiểm tra format CSV:
   - Cần cột: `time, open, high, low, close`
   - Optional: `volume`
2. Encoding: UTF-8 (không ANSI)
3. File size: <50MB

### **Browser chậm/lag**
- Giảm combo size (2-2 thay 2-5)
- Giảm CSV data (dùng 1000 candles đầu)
- Dùng browser khác (Chrome thường nhanh nhất)

### **Chart không hiển thị**
1. Reload page (Ctrl+R)
2. Clear cache (Ctrl+Shift+Delete)
3. Kiểm tra console (F12) có error không

---

## 📊 Output Files

### Export CSV Trades
```
Format:
#,Entry Time,Entry Price,Exit Time,Exit Price,SL,TP,Profit $,Profit %,Type

Ví dụ:
1,18:00,4050.00,18:15,4100.00,3988.25,4173.50,0.82,1.23,LONG
2,18:30,4095.00,18:45,4050.00,4143.28,3989.97,-0.82,-1.23,SHORT
```

---

## 🎓 Hiểu Chiến Lược

### Consensus Logic
```
Nếu Combo = [RSI, MACD, EMA]:
  - Bullish count = 3 → LONG
  - Bearish count = 3 → SHORT
  - Mixed (1 bullish, 2 bearish) → SHORT

Nếu Combo = [RSI, MACD, EMA, Bollinger, ADX]:
  - Bullish % = 70% → LONG
  - Bearish % = 70% → SHORT
  - Khác → bỏ qua
```

### Position Management
```
Đang LONG:
  - Nhận LONG signal → bỏ qua
  - Nhận SHORT signal → exit LONG, vào SHORT
  - Cuối data → exit với close cuối

Chỉ 1 vị thế tại 1 lúc (không 2 LONG liên tiếp)
```

---

## 💡 Tips & Tricks

1. **Test trên 1000 candles đầu** trước khi full 2875
2. **Combo 2-2 thường tốt nhất** (chỉ báo chất lượng cao)
3. **Win rate >50%** = chiến lược tốt
4. **Profit Factor >1.5** = rất tốt
5. **Giảm Risk %** nếu Drawdown cao

---

## 🔗 Files Tham Khảo

- `REQUIREMENTS.md` - Chi tiết kỹ thuật & tính năng
- `OANDA_XAUUSD_15.csv` - Data gốc XAUUSD 15-min

---

## 📞 Support

Nếu có lỗi:
1. Kiểm tra console (F12)
2. Reload page
3. Kiểm tra CSV format
4. Khởi động lại server Python

---

**Version**: 1.1
**Last Updated**: 23 Nov 2025
**Status**: ✅ Ready to Use
