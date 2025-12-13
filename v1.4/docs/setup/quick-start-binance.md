# 🚀 Quick Start - Binance Live Data v1.4

## ⚡ Setup Nhanh (5 phút)

### 1️⃣ Cài Dependencies (Terminal 1)

```bash
cd v1.4\backend
pip install -r requirements.txt
```

**Kết quả:** Tất cả libraries được cài, bao gồm CCXT cho Binance

### 2️⃣ Chạy Backend (Terminal 1)

```bash
cd v1.4\backend
python main.py
```

**Output:**
```
INFO:     Uvicorn running on http://127.0.0.1:4000
INFO:     Application startup complete
```

Backend sẽ chạy ở `http://localhost:4000`

### 3️⃣ Chạy Frontend (Terminal 2)

```bash
cd v1.4\frontend
pnpm dev
# Hoặc: npm run dev
```

**Output:**
```
VITE v4.x.x built in xxx ms

➜ Local:   http://localhost:3000
```

Frontend sẽ chạy ở `http://localhost:3000`

### 4️⃣ Lấy Live Data

1. Mở: `http://localhost:3000`
2. Kéo xuống tìm section **"📊 Lấy Data từ Binance"**
3. Chọn:
   - **Symbol**: BTC/USDT (hoặc ETH, BNB, v.v...)
   - **Timeframe**: 15m (hoặc 1h, 4h, 1d, v.v...)
   - **Số Candles**: 200 (mặc định)
4. Nhấn **"Tải Data"**

✅ Data sẽ load ngay! Bạn có thể:
- Chạy Combo Optimizer
- Xây dựng Strategy tùy chỉnh
- Export ra Pine Script

---

## 🎯 Ví Dụ Sử Dụng

### Scenario 1: Backtest BTC 15m
```
Symbol: BTC/USDT
Timeframe: 15m
Limit: 500
→ ~8 ngày dữ liệu
```

### Scenario 2: Lấy ETH 1h
```
Symbol: ETH/USDT
Timeframe: 1h
Limit: 240
→ ~10 ngày dữ liệu
```

### Scenario 3: Altcoin daily
```
Symbol: SOL/USDT
Timeframe: 1d
Limit: 365
→ 1 năm dữ liệu
```

---

## 📊 Symbols Hỗ Trợ

**Major Cryptos:**
- BTC/USDT - Bitcoin
- ETH/USDT - Ethereum
- BNB/USDT - Binance Coin
- XRP/USDT - Ripple
- SOL/USDT - Solana
- ADA/USDT - Cardano
- DOGE/USDT - Dogecoin
- AVAX/USDT - Avalanche
- MATIC/USDT - Polygon
- LINK/USDT - Chainlink
- Và 10+ symbols khác...

---

## ⏱️ Timeframes Hỗ Trợ

| Ký Hiệu | Mô Tả |
|---------|-------|
| `1m` | 1 Minute |
| `5m` | 5 Minutes |
| `15m` | 15 Minutes |
| `30m` | 30 Minutes |
| `1h` | 1 Hour |
| `4h` | 4 Hours |
| `1d` | 1 Day |
| `1w` | 1 Week |

---

## 🔧 Troubleshooting

### ❌ "Cannot connect to backend"
```bash
# Kiểm tra backend chạy không
curl http://localhost:4000/health
```
→ Nếu không được, chạy `python main.py` ở terminal 1

### ❌ "Symbol not found"
- Chọn từ dropdown list có sẵn
- Tất cả symbols từ dropdown đều hoạt động 100%

### ❌ "Fetch timeout"
- Binance API có thể chậm
- Chờ 5-10 giây rồi thử lại

### ❌ "Module not found"
```bash
pip install ccxt
```

---

## 📚 Files Quan Trọng

```
v1.4/
├── backend/
│   ├── main.py                  # Backend chính
│   ├── binance_fetcher.py       # NEW: Kết nối Binance
│   ├── test_binance_fetcher.py  # TEST script
│   └── requirements.txt         # Dependencies
│
├── frontend/
│   ├── src/
│   │   ├── components/
│   │   │   └── BinanceDataFetcher.tsx  # NEW: UI component
│   │   └── services/
│   │       └── api.ts                   # NEW: API calls
│   └── package.json
│
└── BINANCE_SETUP.md             # Detailed guide
```

---

## ✅ Verification

Chạy test:
```bash
cd v1.4/backend
python test_binance_fetcher.py
```

**Expected output:**
```
✅ ALL TESTS PASSED!
```

---

## 🎓 Workflow Hoàn Chỉnh

```
1. Chạy Backend + Frontend
   ↓
2. Lấy Data từ Binance
   ↓
3. Data được load vào App
   ↓
4. Chạy Combo Optimizer
   ↓
5. Xem Results + Export Pine Script
   ↓
6. Run trên TradingView
```

---

## 🚀 API Endpoints (Advanced)

### Lấy danh sách symbols
```bash
curl http://localhost:4000/api/binance/symbols
```

### Lấy OHLCV data
```bash
curl -X POST http://localhost:4000/api/binance/fetch \
  -H "Content-Type: application/json" \
  -d '{
    "symbol": "BTC/USDT",
    "timeframe": "15m",
    "limit": 200
  }'
```

---

## 💡 Tips

1. **Test nhiều timeframes** → tìm cái tốt nhất
2. **500+ candles = backtest tốt hơn**
3. **Kết hợp Optimizer + Pine Script** → Run production
4. **Check health:** `http://localhost:4000/health`

---

**Version**: 1.4.0  
**Status**: ✅ Ready to Use  
**Last Updated**: December 5, 2024
