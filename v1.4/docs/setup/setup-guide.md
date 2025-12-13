# 🚀 Hướng Dẫn Cài Đặt Chi Tiết - Combo Optimizer v1.4

## Bước 1: Cài Đặt Python (nếu chưa có)

1. Tải Python 3.8+ từ: https://www.python.org/downloads/
2. **Quan trọng**: Tick ☑️ "Add Python to PATH" khi cài
3. Kiểm tra: Mở PowerShell/CMD và chạy:
   ```bash
   python --version
   ```
   Kết quả: `Python 3.x.x`

## Bước 2: Cài Đặt Node.js (nếu chưa có)

1. Tải Node.js 18+ LTS từ: https://nodejs.org/
2. Cài đặt với cấu hình mặc định
3. Kiểm tra: Mở PowerShell/CMD và chạy:
   ```bash
   node --version
   npm --version
   ```

## Bước 3: Cài Đặt pnpm

```bash
npm install -g pnpm
```

Kiểm tra:
```bash
pnpm --version
```

## Bước 4: Setup Backend

```bash
# Di chuyển vào thư mục backend
cd c:\Data\PineScript\demo-tdb-01\v1.4\backend

# Cài dependencies
pip install -r requirements.txt

# Chạy backend
python main.py
```

✅ Backend sẽ chạy tại: **http://localhost:4000**

**Giữ terminal này mở!**

## Bước 5: Setup Frontend (Terminal mới)

Mở PowerShell/CMD mới:

```bash
# Di chuyển vào thư mục frontend
cd c:\Data\PineScript\demo-tdb-01\v1.4\frontend

# Cài dependencies (lần đầu tiên hoặc khi có thay đổi)
pnpm install

# Chạy dev server
pnpm dev
```

✅ Frontend sẽ chạy tại: **http://localhost:3000**

**Giữ terminal này mở!**

## Bước 6: Sử Dụng

1. Mở trình duyệt và truy cập: **http://localhost:3000**
2. Upload file CSV (ví dụ: `OANDA_XAUUSD_15.csv`)
3. Cấu hình tham số
4. Click "▶️ Chạy Optimization"

## 🎯 Quick Start Script

### Cách 1: Dùng START.bat (Recommended)

Double-click file `START.bat` trong thư mục v1.4

File này sẽ:
- Kiểm tra Python & Node.js
- Tự động cài dependencies (nếu cần)
- Khởi động backend (port 4000)
- Khởi động frontend (port 3000)
- Mở browser tự động

### Cách 2: Manual Start

**Terminal 1 - Backend:**
```bash
cd c:\Data\PineScript\demo-tdb-01\v1.4\backend
python main.py
```

**Terminal 2 - Frontend:**
```bash
cd c:\Data\PineScript\demo-tdb-01\v1.4\frontend
pnpm dev
```

## ⚠️ Troubleshooting

### Lỗi: "pnpm is not recognized"

**Giải pháp:**
```bash
npm install -g pnpm
```

Hoặc dùng npm thay pnpm:
```bash
npm install
npm run dev
```

### Lỗi: "python is not recognized"

**Giải pháp:**
1. Cài Python từ python.org
2. Tick "Add Python to PATH"
3. Restart terminal/computer

### Lỗi: Backend không start (Port 4000 đang được dùng)

**Giải pháp 1**: Đổi port backend
- File: `backend/main.py` (dòng cuối)
- Thay `port=4000` thành `port=4001`
- File: `frontend/src/services/api.ts`
- Thay `http://localhost:4000` thành `http://localhost:4001`

**Giải pháp 2**: Tìm và tắt process đang dùng port 4000
```bash
# Windows
netstat -ano | findstr :4000
taskkill /PID <PID_NUMBER> /F
```

### Lỗi: Frontend không start (Port 3000 đang được dùng)

**Giải pháp**: Vite sẽ tự động đề xuất port khác (3001, 3002...)

### Lỗi: CORS khi call API

**Nguyên nhân**: Backend chưa chạy hoặc port sai

**Giải pháp**:
1. Kiểm tra backend đang chạy: http://localhost:4000/health
2. Kiểm tra port trong `frontend/src/services/api.ts`

### Lỗi: Module not found (Frontend)

**Giải pháp**:
```bash
cd frontend
rm -rf node_modules
rm pnpm-lock.yaml
pnpm install
```

### Lỗi: Python module not found (Backend)

**Giải pháp**:
```bash
cd backend
pip install -r requirements.txt --upgrade --force-reinstall
```

## 🔧 Kiểm Tra Kết Nối

### Test Backend:
Mở browser: http://localhost:4000/health

Kết quả mong đợi:
```json
{
  "status": "ok",
  "version": "1.4.0",
  "port": 4000,
  "frontend": "http://localhost:3000"
}
```

### Test Frontend:
Mở browser: http://localhost:3000

Thấy giao diện Combo Optimizer

## 📦 Cấu Trúc Project

```
v1.4/
├── backend/
│   ├── main.py              # FastAPI server
│   ├── indicators.py        # Technical indicators
│   ├── requirements.txt     # Python dependencies
│   └── run.bat             # Windows script
│
├── frontend/
│   ├── src/
│   │   ├── components/     # React components
│   │   ├── store/          # Zustand state
│   │   ├── services/       # API calls
│   │   ├── types/          # TypeScript types
│   │   ├── App.tsx         # Main app
│   │   └── main.tsx        # Entry point
│   ├── package.json
│   ├── tsconfig.json       # TypeScript config
│   ├── tailwind.config.js  # Tailwind config
│   └── vite.config.js      # Vite config
│
├── OANDA_XAUUSD_15.csv     # Sample data
├── START.bat                # Auto-start script
└── README.md
```

## 🎓 Tips

### 1. Development Mode
- Backend: Auto-reload khi sửa code Python (FastAPI built-in)
- Frontend: Hot Module Reload khi sửa code React (Vite built-in)

### 2. Build Production

**Frontend:**
```bash
cd frontend
pnpm build
```
Output: `frontend/dist/`

**Backend:**
Production với Gunicorn (Linux):
```bash
gunicorn -w 4 -k uvicorn.workers.UvicornWorker main:app
```

### 3. Recommended IDE Settings

**VSCode Extensions:**
- Python
- Pylance
- ESLint
- Prettier
- Tailwind CSS IntelliSense
- TypeScript Vue Plugin

### 4. Git Ignore

Thêm vào `.gitignore`:
```
# Backend
__pycache__/
*.pyc

# Frontend
node_modules/
dist/
.vite/

# Data
*.csv
```

## 📞 Support

Nếu gặp vấn đề, kiểm tra:
1. Backend logs (terminal chạy backend)
2. Frontend console (F12 trong browser)
3. Network tab (kiểm tra API calls)

Happy Optimizing! 🎯
