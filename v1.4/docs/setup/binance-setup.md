# 🚀 Setup Binance Live Data v1.4

## ✅ Cập Nhật Mới

v1.4 giờ đã có tính năng **lấy dữ liệu live từ Binance** với timeframe tùy chọn!

### Thành Phần Mới:
- **Backend**: `binance_fetcher.py` - Kết nối Binance API qua CCXT
- **API Endpoints**: 4 endpoints mới cho Binance
- **Frontend**: Component `BinanceDataFetcher` - UI để chọn symbol/timeframe
- **Library**: CCXT + Pandas

---

## 📦 Installation

### 1️⃣ Backend Setup

```bash
cd v1.4/backend

# Cài đặt dependencies mới
pip install -r requirements.txt

# Hoặc install riêng:
pip install ccxt==4.0.97 pandas==2.1.3
```

### 2️⃣ Frontend Setup

```bash
cd v1.4/frontend

# Nếu chưa install
pnpm install

# Hoặc
npm install
```

---

## 🎯 Sử Dụng

### **Bước 1: Chạy Backend**

```bash
cd v1.4/backend
python main.py
# hoặc
python -m uvicorn main:app --reload
```

Backend sẽ chạy ở `http://localhost:4000`

### **Bước 2: Chạy Frontend**

```bash
cd v1.4/frontend
pnpm dev
# hoặc
npm run dev
```

Frontend sẽ chạy ở `http://localhost:3000`

### **Bước 3: Lấy Live Data**

1. Mở trình duyệt: `http://localhost:3000`
2. Kéo xuống section **"📊 Lấy Data từ Binance"**
3. Chọn:
   - **Symbol**: BTC/USDT, ETH/USDT, v.v...
   - **Timeframe**: 1m, 5m, 15m, 30m, 1h, 4h, 1d, 1w
   - **Số Candles**: 50-1000 (mặc định 200)
4. Nhấn **"Tải Data"**
5. Data sẽ được load vào app tự động ✅

---

## 📊 Symbols Hỗ Trợ

### Major Cryptocurrencies:
- **BTC/USDT** - Bitcoin
- **ETH/USDT** - Ethereum
- **BNB/USDT** - Binance Coin
- **XRP/USDT** - Ripple
- **SOL/USDT** - Solana
- **ADA/USDT** - Cardano
- **DOGE/USDT** - Dogecoin
- **AVAX/USDT** - Avalanche
- **MATIC/USDT** - Polygon
- **LINK/USDT** - Chainlink
- Và 10+ symbols khác...

### Chế độ Sử Dụng:
- ✅ **Public API** (không cần API key)
- ✅ **Hoàn toàn miễn phí**
- ✅ **Tốc độ nhanh** (~1-2 giây)

---

## ⏱️ Timeframes Hỗ Trợ

| Timeframe | Ký Hiệu | Mô Tả |
|-----------|---------|-------|
| 1 phút | `1m` | 1 Minute |
| 5 phút | `5m` | 5 Minutes |
| 15 phút | `15m` | 15 Minutes |
| 30 phút | `30m` | 30 Minutes |
| 1 giờ | `1h` | 1 Hour |
| 4 giờ | `4h` | 4 Hours |
| 1 ngày | `1d` | 1 Day |
| 1 tuần | `1w` | 1 Week |

---

## 🔧 API Endpoints

### 1. **GET /api/binance/symbols**
Lấy danh sách symbol phổ biến

```bash
curl http://localhost:4000/api/binance/symbols
```

**Response:**
```json
{
  "status": "success",
  "symbols": ["BTC/USDT", "ETH/USDT", ...],
  "count": 20
}
```

### 2. **GET /api/binance/timeframes**
Lấy danh sách timeframe

```bash
curl http://localhost:4000/api/binance/timeframes
```

**Response:**
```json
{
  "status": "success",
  "timeframes": {
    "1": "1m",
    "5": "5m",
    "15": "15m",
    ...
  }
}
```

### 3. **POST /api/binance/fetch**
Lấy OHLCV data từ Binance

```bash
curl -X POST http://localhost:4000/api/binance/fetch \
  -H "Content-Type: application/json" \
  -d '{
    "symbol": "BTC/USDT",
    "timeframe": "15m",
    "limit": 200
  }'
```

**Response:**
```json
{
  "status": "success",
  "symbol": "BTC/USDT",
  "timeframe": "15m",
  "count": 200,
  "ohlcv_data": [
    {
      "time": "2024-12-05 10:00:00",
      "open": 42500.50,
      "high": 42600.00,
      "low": 42400.00,
      "close": 42550.00,
      "volume": 250000
    },
    ...
  ],
  "fetched_at": "2024-12-05T10:05:00.123456"
}
```

### 4. **GET /api/binance/symbol-info/{symbol}**
Lấy thông tin chi tiết symbol

```bash
curl http://localhost:4000/api/binance/symbol-info/BTC%2FUSDT
```

---

## 🛠️ Troubleshooting

### ❌ **"Cannot import ccxt"**
```bash
pip install ccxt
```

### ❌ **"Connection timeout"**
- Kiểm tra kết nối internet
- Binance API có thể bị chậm, chờ 5 giây rồi thử lại

### ❌ **"Invalid symbol"**
- Đảm bảo symbol đúng format: `BTC/USDT` (có `/`)
- Chọn từ danh sách dropdown có sẵn

### ❌ **"Limit must be 50-1000"**
- Giới hạn: minimum 50, maximum 1000 candles

---

## 💡 Tips & Tricks

### 1. **Thử Nhiều Timeframes**
Dữ liệu 1h sẽ khác 4h, hãy test cả hai để tìm strategy tốt nhất

### 2. **Lấy Nhiều Data = Backtest Tốt Hơn**
- 200 candles ≈ ~3 ngày (15m)
- 500 candles ≈ ~8 ngày (15m)
- 1000 candles ≈ ~16 ngày (15m)

### 3. **Kết Hợp Với Optimizer**
1. Lấy data từ Binance
2. Chạy Combo Optimizer
3. Export winner strategy ra Pine Script
4. Chạy trên TradingView

### 4. **Check Symbol Trước**
Tất cả symbols từ dropdown đều khả dụng 100%

---

## 📊 Workflow Hoàn Chỉnh

```
1. Chạy Backend (port 4000)
   ↓
2. Chạy Frontend (port 3000)
   ↓
3. Chọn Symbol + Timeframe
   ↓
4. Nhấn "Tải Data"
   ↓
5. Data được load → Chạy Optimizer
   ↓
6. Xem kết quả → Export Pine Script
   ↓
7. Chạy trên TradingView/Binance Trading Bot
```

---

## 🔐 Security Notes

- ✅ Chỉ dùng **Public API** (không cần credentials)
- ✅ **Không lưu** bất kỳ API key nào
- ✅ **Không** có phí sử dụng
- ✅ Rate limit: ~1200 requests/minute (rất rộng)

---

## 📈 Ví Dụ Sử Dụng

### Scenario 1: Lấy BTC 15 phút
```
Symbol: BTC/USDT
Timeframe: 15m
Limit: 500
```

→ Sẽ lấy ~8 ngày dữ liệu BTC (15m candles)

### Scenario 2: Lấy ETH 1 giờ
```
Symbol: ETH/USDT
Timeframe: 1h
Limit: 240
```

→ Sẽ lấy ~10 ngày dữ liệu ETH (1h candles)

### Scenario 3: Lấy Altcoin daily
```
Symbol: SOLANA/USDT
Timeframe: 1d
Limit: 365
```

→ Sẽ lấy 1 năm dữ liệu Solana

---

## 🚀 Production Ready?

Để chạy production:

### Backend:
```bash
gunicorn -w 4 -b 0.0.0.0:4000 main:app
```

### Frontend:
```bash
npm run build
npm run preview
```

---

## 📝 Changelog v1.4

- ✨ **NEW**: Binance live data fetcher
- ✨ **NEW**: BinanceDataFetcher component
- ✨ **NEW**: 4 new API endpoints for Binance
- 🔄 **UPDATED**: UI integration
- 📦 **ADDED**: CCXT + Pandas dependencies

---

**Version**: 1.4.0  
**Last Updated**: December 5, 2024  
**Status**: ✅ Ready to Use
