# Combo Optimizer v1.4

🎯 **Tìm Tổ Hợp Chỉ Báo Tối Ưu với React + TypeScript + FastAPI**

## 🏗️ Kiến Trúc

### Frontend
- **React 18** + **TypeScript**
- **Zustand** - State management
- **Tailwind CSS** - Styling
- **Lightweight Charts** - Biểu đồ nến
- **Vite** - Build tool
- **Port**: 3000

### Backend
- **FastAPI** - Python web framework
- **Port**: 4000
- **Streaming API** - Real-time progress updates
- **20+ Technical Indicators**

## 📋 Yêu Cầu Hệ Thống

### Backend
- Python 3.8+
- pip

### Frontend
- Node.js 18+
- pnpm (hoặc npm/yarn)

## 🚀 Cài Đặt

### 1. Backend Setup

```bash
cd v1.4/backend

# Cài dependencies
pip install -r requirements.txt

# Chạy server
python main.py
# hoặc
run.bat
```

Server sẽ chạy tại: `http://localhost:4000`

### 2. Frontend Setup

```bash
cd v1.4/frontend

# Cài pnpm (nếu chưa có)
npm install -g pnpm

# Cài dependencies
pnpm install

# Chạy dev server
pnpm dev
```

Frontend sẽ chạy tại: `http://localhost:3000`

## 📝 Sử Dụng

1. **Upload CSV**: Kéo thả file CSV chứa dữ liệu OHLCV
2. **Cấu hình tham số**: 
   - Combo size: 2-3
   - Threshold: 70%
   - Stop Loss: 0.75%
   - Risk/Reward: 2.0
3. **Chạy Optimization**: Click "▶️ Chạy Optimization"
4. **Xem kết quả**: 
   - Bảng top 100 combos
   - Click vào row để xem chart với trade markers
   - Download Pine Script code

## 🎨 Tính Năng

### Frontend
✅ Modern React với TypeScript
✅ Zustand state management (lightweight alternative to Redux)
✅ Tailwind CSS với custom gradient theme
✅ Lightweight Charts - Professional candlestick charts
✅ Real-time progress tracking
✅ Interactive results table
✅ Trade visualization với entry/exit markers
✅ CSV export
✅ Pine Script code generation

### Backend
✅ FastAPI streaming responses
✅ 20+ technical indicators (RSI, MACD, EMA, Bollinger, etc.)
✅ Advanced backtesting engine
✅ Signal caching for performance
✅ Multiple entry filters (ADX, Volume, MA, Trend)
✅ Configurable risk management
✅ Pine Script synchronization

## 🔧 Configuration

### Backend Port
File: `backend/main.py`
```python
uvicorn.run(app, host="0.0.0.0", port=4000)
```

### Frontend API Endpoint
File: `frontend/src/services/api.ts`
```typescript
const API_BASE = 'http://localhost:4000'
```

## 📊 Recommended Settings

**Quick Test (EMA Pair)**:
- Combo Size: 2-2
- Threshold: 70%
- SL: 0.75%
- RR: 2.0
- Filters: Disabled
- Expected: 10 trades, 60% WR, +6% profit

## 🛠️ Development

### Frontend
```bash
pnpm dev          # Start dev server
pnpm build        # Build for production
pnpm preview      # Preview production build
```

### Backend
```bash
python main.py    # Start FastAPI server
```

## 📦 Dependencies

### Frontend
- react ^18.2.0
- zustand ^4.4.7
- lightweight-charts ^4.1.1
- tailwindcss ^3.4.0
- typescript ^5.3.3

### Backend
- fastapi ^0.104.1
- uvicorn ^0.24.0
- pydantic ^2.5.0

## 🐛 Troubleshooting

### Backend không start:
```bash
# Check Python version
python --version  # should be 3.8+

# Reinstall dependencies
pip install -r requirements.txt --force-reinstall
```

### Frontend không build:
```bash
# Clear node_modules
rm -rf node_modules
pnpm install

# Clear cache
rm -rf .vite
```

### CORS errors:
Backend đã cấu hình CORS cho `localhost:3000`. Nếu dùng port khác, update `backend/main.py`:
```python
allow_origins=["http://localhost:YOUR_PORT"]
```

## 📚 Documentation

Tất cả documentation đã được tổ chức trong thư mục `docs/`:

- **Trading Improvements**: `docs/trading-improvements/`
  - Trailing Stop Loss
  - Breakeven Stop
  - Integration guides
  
- **Live Trading**: `docs/live-trading/`
  - Setup & Quick Start
  - Implementation details
  
- **Indicators**: `docs/indicators/`
  - Quick Reference
  - Improvements & Summary
  
- **Setup**: `docs/setup/`
  - Installation guides
  - Binance configuration

Xem `docs/README.md` để biết cấu trúc đầy đủ.

## 📄 License

MIT

## 👨‍💻 Author

Combo Optimizer Team - v1.4 (React + TypeScript + FastAPI)
