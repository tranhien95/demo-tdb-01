# Hướng Dẫn Margin/Leverage

## 📋 Margin/Leverage Là Gì?

**Margin** (hay **Leverage**) cho phép bạn trade với số tiền lớn hơn vốn thực tế.

### Ví Dụ:
- **Vốn thực tế**: $1,000
- **Margin 10x**: Có thể trade với $10,000
- **Lợi ích**: Lợi nhuận tăng 10 lần
- **Rủi ro**: Thua lỗ cũng tăng 10 lần!

## ⚠️ CẢNH BÁO: Leverage Rất Nguy Hiểm!

### Tại Sao Nguy Hiểm?

1. **Lỗi Nhanh Hơn**:
   ```
   Vốn: $1,000
   Leverage: 10x
   Position size: $10,000
   
   Nếu giá giảm 10%:
   - Không có leverage: Mất $100 (10% của $1,000)
   - Có leverage 10x: Mất $1,000 (100% vốn!) → Phá sản!
   ```

2. **Liquidation Risk**:
   - Với leverage cao, chỉ cần giá di chuyển nhỏ là có thể bị liquidation
   - Mất toàn bộ vốn, không có cơ hội phục hồi

3. **Tâm Lý Căng Thẳng**:
   - Mỗi biến động giá đều ảnh hưởng lớn đến vốn
   - Dễ đưa ra quyết định sai

## 📊 So Sánh Leverage Levels

| Leverage | Risk Level | Khuyến Nghị | Use Case |
|----------|------------|-------------|----------|
| 1x (No margin) | Rất thấp | ✅ **Khuyến nghị** | Người mới, conservative |
| 2-3x | Thấp | ✅ OK | Trader có kinh nghiệm |
| 5-10x | Trung bình | ⚠️ Cẩn thận | Trader chuyên nghiệp |
| 20-50x | Cao | ❌ Nguy hiểm | Chỉ cho scalping, rất rủi ro |
| 100x+ | Cực kỳ cao | ❌ **TRÁNH** | Gambling, không phải trading |

## 💡 Cách Tính Position Size Với Margin

### **Không Có Margin** (Leverage 1x):
```
Vốn: $1,000
Risk per trade: 2% = $20
Stop Loss: 3%
Position Size = $20 / 3% = $666.67
```

### **Có Margin 10x**:
```
Vốn: $1,000
Margin: 10x
Vốn có thể dùng: $1,000 × 10 = $10,000

Risk per trade: 2% của $1,000 = $20
Stop Loss: 3%
Position Size = $20 / 3% = $666.67

Nhưng với margin 10x, có thể mở position lớn hơn:
Position Size với margin = $666.67 × 10 = $6,666.67
```

**⚠️ Lưu ý**: Với margin, nếu giá di chuyển 1% ngược lại, bạn mất 10% vốn!

## 🎯 Khi Nào Nên Dùng Margin?

### ✅ **Nên Dùng**:
1. **Scalping**: Cần position size lớn, hold time ngắn
2. **High Win Rate Strategy**: Win rate >70%, có thể chấp nhận rủi ro
3. **Trader Chuyên Nghiệp**: Có kinh nghiệm quản lý rủi ro
4. **Backtesting**: Test strategy với margin để xem performance

### ❌ **Không Nên Dùng**:
1. **Người Mới**: Chưa có kinh nghiệm
2. **Swing Trading**: Hold lâu, rủi ro liquidation cao
3. **Low Win Rate**: Win rate <50%, dễ thua nhiều
4. **Live Trading Lần Đầu**: Nên test không margin trước

## 📈 Ví Dụ Thực Tế

### **Scenario 1: Conservative (Không Margin)**
```
Vốn: $1,000
Margin: Không (1x)
Risk per trade: 2%
Stop Loss: 3%

Position Size: $666.67
Nếu thua: Mất $20 (2% vốn)
Nếu thắng 3%: Lời $20 (2% vốn)
```

### **Scenario 2: Moderate (Margin 5x)**
```
Vốn: $1,000
Margin: 5x
Risk per trade: 2%
Stop Loss: 3%

Position Size: $3,333.33
Nếu thua: Mất $20 (2% vốn thực tế)
Nếu thắng 3%: Lời $100 (10% vốn thực tế)
⚠️ Nhưng nếu giá di chuyển 20% ngược lại: Phá sản!
```

### **Scenario 3: Aggressive (Margin 10x) - KHÔNG KHUYẾN NGHỊ**
```
Vốn: $1,000
Margin: 10x
Risk per trade: 2%
Stop Loss: 3%

Position Size: $6,666.67
Nếu thua: Mất $20 (2% vốn thực tế)
Nếu thắng 3%: Lời $200 (20% vốn thực tế)
⚠️ Nhưng nếu giá di chuyển 10% ngược lại: Phá sản!
```

## 🛡️ Best Practices

### **1. Bắt Đầu Không Margin**
- Test strategy với leverage 1x trước
- Đảm bảo strategy có lời ổn định
- Sau đó mới thử margin thấp (2-3x)

### **2. Kết Hợp Với Risk Management**
- **Risk per trade thấp hơn** khi dùng margin:
  - Không margin: Risk 2-5%
  - Margin 5x: Risk 1-2%
  - Margin 10x: Risk 0.5-1%

### **3. Stop Loss Chặt Hơn**
- Với margin cao, cần stop loss nhỏ hơn
- Margin 10x: Stop Loss 1-2% (thay vì 3-5%)

### **4. Không Bao Giờ**
- ❌ Dùng margin >20x cho live trading
- ❌ Dùng margin khi chưa test kỹ strategy
- ❌ Dùng margin với risk per trade cao (>5%)
- ❌ Dùng margin khi tâm lý không ổn định

## 🔧 Cấu Hình Khuyến Nghị

### **Cho Người Mới**:
```json
{
  "risk_management": {
    "capital": 1000,
    "risk_percent": 1.0,
    "reward_ratio": 2.0,
    "stop_loss_percent": 2.0,
    "margin": undefined  // Không dùng margin
  }
}
```

### **Cho Trader Có Kinh Nghiệm**:
```json
{
  "risk_management": {
    "capital": 5000,
    "risk_percent": 1.0,  // Giảm risk khi dùng margin
    "reward_ratio": 2.0,
    "stop_loss_percent": 1.5,  // Stop loss chặt hơn
    "margin": 5  // Margin 5x
  }
}
```

### **Cho Scalping (Rất Rủi Ro)**:
```json
{
  "risk_management": {
    "capital": 2000,
    "risk_percent": 0.5,  // Risk rất thấp
    "reward_ratio": 1.5,
    "stop_loss_percent": 1.0,  // Stop loss rất chặt
    "margin": 10  // Margin 10x
  }
}
```

## ⚠️ Kết Luận

**Margin/Leverage là con dao hai lưỡi:**
- ✅ Có thể tăng lợi nhuận nhanh
- ❌ Cũng có thể phá sản nhanh

**Khuyến nghị:**
- Bắt đầu **không margin** (để trống field)
- Chỉ dùng margin khi đã test kỹ và có kinh nghiệm
- Giới hạn margin **tối đa 5-10x** cho live trading
- **Không bao giờ** dùng margin >20x

**Nhớ**: "Những trader thành công nhất thường không dùng hoặc dùng margin rất thấp!"

