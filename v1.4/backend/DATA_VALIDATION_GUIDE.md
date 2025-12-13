# Data Validation Guide

## Backtest Result Data Structure

Sau khi fix lỗi `AttributeError: 'SignalDetail' object has no attribute 'model_dump'`, cấu trúc dữ liệu backtest result như sau:

### Expected Structure

```json
{
  "status": "success",
  "total_trades": 10,
  "winning_trades": 6,
  "losing_trades": 4,
  "win_rate": 60.0,
  "profit_factor": 1.5,
  "total_profit": 150.25,
  "total_profit_pct": 1.5,
  "max_drawdown": 5.2,
  "sharpe_ratio": 1.2,
  "long_trades": 5,
  "short_trades": 5,
  "signals_found": 20,
  "long_signals": 12,
  "short_signals": 8,
  "equity_curve": [10000, 10050, 10100, ...],
  "trades": [
    {
      "entry": 50000.0,
      "exit": 50100.0,
      "sl": 49500.0,
      "tp": 51000.0,
      "profit": 50.0,
      "profit_pct": 0.1,
      "position_size": 1000.0,
      "position_percent": 10.0,
      "type": "LONG",
      "time": "2024-01-01T00:00:00",
      "exit_time": "2024-01-02T00:00:00",
      "exit_reason": "TP",
      "entry_signals": [
        {
          "indicator_type": "RSI",
          "indicator_id": "abc123",
          "bullish": true,
          "bearish": false,
          "value": 70.0,
          "weight": 1.0,
          "contribution_percent": 50.0,
          "enabled": true
        },
        {
          "indicator_type": "MACD",
          "indicator_id": "def456",
          "bullish": true,
          "bearish": false,
          "value": 0.5,
          "weight": 1.0,
          "contribution_percent": 50.0,
          "enabled": true
        }
      ]
    }
  ]
}
```

### Key Points

1. **entry_signals**: Mỗi trade có `entry_signals` là một array các signal details
2. **SignalDetail Structure**: Mỗi signal detail có các fields:
   - `indicator_type`: Loại indicator (RSI, MACD, EMA, etc.)
   - `indicator_id`: ID của indicator instance
   - `bullish`: Boolean - có signal bullish không
   - `bearish`: Boolean - có signal bearish không
   - `value`: Giá trị của indicator
   - `weight`: Trọng số của indicator
   - `contribution_percent`: Phần trăm đóng góp vào signal
   - `enabled`: Indicator có được bật không

3. **Serialization**: `SignalDetail` objects được serialize bằng method `.dict()` (sử dụng `asdict()` từ dataclasses)

## How to Validate Data

### Option 1: Use Validation Script

```bash
# From backend directory
python scripts/validate_backtest_data.py <your_data.json>
```

Hoặc paste JSON trực tiếp:
```bash
python scripts/validate_backtest_data.py
# Then paste your JSON and press Ctrl+D (Linux/Mac) or Ctrl+Z (Windows)
```

### Option 2: Manual Check

Kiểm tra các điểm sau:

1. ✅ `entry_signals` là một array
2. ✅ Mỗi signal trong `entry_signals` là một object/dict
3. ✅ Mỗi signal có đầy đủ các fields: `indicator_type`, `indicator_id`, `bullish`, `bearish`, `value`, `weight`, `contribution_percent`, `enabled`
4. ✅ Không có lỗi `AttributeError` khi serialize

### Option 3: Test with Python

```python
from strategy_models_simple import SignalDetail

# Create a test signal
signal = SignalDetail(
    indicator_type='RSI',
    indicator_id='1',
    bullish=True,
    bearish=False,
    value=70.0,
    weight=1.0,
    contribution_percent=50.0,
    enabled=True
)

# Serialize
result = signal.dict()
print(result)  # Should print a dict without errors
```

## Common Issues Fixed

1. ✅ **AttributeError: 'SignalDetail' object has no attribute 'model_dump'**
   - **Fix**: Changed import from `strategy_models` to `strategy_models_simple`
   - **Fix**: Use `.dict()` method instead of `.model_dump()`

2. ✅ **Serialization Logic**
   - Code now checks: `s.dict() if hasattr(s, 'dict') else (s.model_dump() if hasattr(s, 'model_dump') else s.__dict__)`
   - This handles both dataclass and Pydantic models gracefully

## Testing

Để test xem data có đúng format không:

1. Gửi backtest request qua API
2. Nhận response
3. Kiểm tra `trades[0].entry_signals` có đúng structure không
4. Verify không có lỗi serialization

## Next Steps

Nếu bạn có JSON payload cụ thể cần check:
1. Lưu vào file (ví dụ: `test_data.json`)
2. Chạy: `python scripts/validate_backtest_data.py test_data.json`
3. Hoặc paste JSON vào script và chạy

