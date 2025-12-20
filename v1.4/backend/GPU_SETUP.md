# 🚀 GPU Acceleration Setup Guide

Backend hiện hỗ trợ **GPU acceleration** để tăng tốc tính toán indicators và backtesting!

## 📋 Yêu Cầu

### 1. NVIDIA GPU với CUDA
- GPU: NVIDIA GPU (GTX 1050 trở lên, hoặc bất kỳ GPU hỗ trợ CUDA)
- CUDA Toolkit: Version 10.x, 11.x, hoặc 12.x
- Driver: NVIDIA Driver tương thích

### 2. Kiểm Tra GPU

**Windows:**
```powershell
nvidia-smi
```

**Linux/Mac:**
```bash
nvidia-smi
```

Nếu không có GPU hoặc không thấy output, backend sẽ tự động fallback về CPU (NumPy).

## 🔧 Cài Đặt

### Bước 1: Xác định CUDA Version

Chạy `nvidia-smi` và xem CUDA Version ở dòng đầu tiên:
```
CUDA Version: 12.1
```

### Bước 2: Cài Đặt cuPy

**Cho CUDA 12.x:**
```bash
pip install cupy-cuda12x
```

**Cho CUDA 11.x:**
```bash
pip install cupy-cuda11x
```

**Cho CUDA 10.x:**
```bash
pip install cupy-cuda10x
```

### Bước 3: Kiểm Tra

Chạy backend và kiểm tra log:
```bash
cd backend
python main.py
```

Bạn sẽ thấy:
- `✅ GPU acceleration enabled (cuPy)` - GPU hoạt động
- `⚠️ cuPy installed but no CUDA devices found` - cuPy có nhưng không có GPU
- `ℹ️ Using CPU (NumPy) - no GPU acceleration` - Không có GPU, dùng CPU

## ⚙️ Cấu Hình

### Bật/Tắt GPU

**Mặc định:** GPU tự động bật nếu có

**Tắt GPU (force CPU):**
```bash
# Windows PowerShell
$env:USE_GPU="false"
python main.py

# Linux/Mac
export USE_GPU=false
python main.py
```

## 📊 Hiệu Năng

### So Sánh (ước tính):

**CPU (NumPy):**
- 1000 candles × 33 indicators: ~2-5 giây
- 100 combos backtest: ~10-30 giây

**GPU (cuPy):**
- 1000 candles × 33 indicators: ~0.5-1 giây (5-10x nhanh hơn)
- 100 combos backtest: ~2-5 giây (5-10x nhanh hơn)

### Lưu Ý:
- GPU chỉ có lợi khi xử lý **lượng lớn data** (hàng nghìn candles)
- Với data nhỏ (< 500 candles), CPU có thể nhanh hơn do overhead
- GPU memory giới hạn, không phù hợp với data cực lớn (>100k candles)

## 🐛 Troubleshooting

### Lỗi: "cupy not found"
```bash
# Kiểm tra CUDA version
nvidia-smi

# Cài đúng cuPy version
pip install cupy-cuda12x  # hoặc 11x, 10x
```

### Lỗi: "CUDA out of memory"
- Giảm số lượng combos test cùng lúc
- Giảm số candles trong data
- Tắt GPU: `USE_GPU=false`

### GPU không được sử dụng
- Kiểm tra: `nvidia-smi` có hoạt động không
- Kiểm tra log backend có hiển thị "GPU acceleration enabled"
- Đảm bảo cuPy đã cài đúng version

## 🔄 Fallback Tự Động

Backend tự động fallback về CPU nếu:
- Không có GPU
- cuPy chưa được cài
- GPU không khả dụng
- CUDA error xảy ra

**Không cần lo lắng** - backend vẫn hoạt động bình thường trên CPU!

