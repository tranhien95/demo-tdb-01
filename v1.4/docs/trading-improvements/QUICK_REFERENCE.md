# ⚡ QUICK REFERENCE - TẤT CẢ FEATURES

## 🚀 ENABLE ALL FEATURES

```python
config = TradingConfig(
    # Basic
    symbol="BTCUSDT",
    timeframe="M5",
    strategy_name="MyStrategy",
    initial_balance=10000.0,
    risk_percent=2.0,
    margin=1.0,
    stoploss_percent=1.0,
    
    # ✅ Trailing Stop
    enable_trailing_stop=True,
    trailing_multiplier=1.5,
    trailing_activation_r=1.0,
    
    # ✅ Breakeven Stop
    enable_breakeven_stop=True,
    breakeven_activation_r=1.0,
    breakeven_buffer_pct=0.1,
    
    # ✅ Dynamic Sizing
    enable_dynamic_sizing=True,
    dynamic_sizing_max_multiplier=2.0,
    dynamic_sizing_use_volatility=True,
    
    # ✅ Partial Profit
    enable_partial_profit=True,
    partial_profit_rules=[
        {"r_level": 1.0, "close_pct": 0.5, "taken": False},
        {"r_level": 2.0, "close_pct": 0.25, "taken": False}
    ],
    
    # ✅ Multi-timeframe
    enable_multi_timeframe=True,
    higher_timeframe="1h",
    
    # ✅ Volatility SL/TP (optional)
    enable_atr_sl_tp=False,
    atr_sl_multiplier=2.0,
    atr_tp_multiplier=4.0,
    
    # ✅ Time Filter
    enable_time_filter=True,
    market_type="crypto",
    
    # ✅ Signal Quality
    enable_signal_quality=True,
    min_signal_quality=70.0,
    
    # ✅ Correlation (optional)
    enable_correlation_filter=False,
    max_correlation=0.7,
)
```

---

## 📊 FEATURES SUMMARY

| # | Feature | Status | Config |
|---|---------|--------|--------|
| 1 | Trailing Stop | ✅ | `enable_trailing_stop` |
| 2 | Partial Profit | ✅ | `enable_partial_profit` |
| 3 | Dynamic Sizing | ✅ | `enable_dynamic_sizing` |
| 4 | Multi-timeframe | ✅ | `enable_multi_timeframe` |
| 5 | Volatility SL/TP | ✅ | `enable_atr_sl_tp` |
| 6 | Time Filter | ✅ | `enable_time_filter` |
| 7 | Market Regime | ✅ | `enable_regime_detection` |
| 8 | Breakeven Stop | ✅ | `enable_breakeven_stop` |
| 9 | Correlation | ✅ | `enable_correlation_filter` |
| 10 | Signal Quality | ✅ | `enable_signal_quality` |

---

## 🎯 RECOMMENDED SETTINGS

### Conservative (An toàn):
```python
# Risk Management
enable_trailing_stop=True
enable_breakeven_stop=True
enable_partial_profit=True
enable_dynamic_sizing=True

# Filters
enable_multi_timeframe=True
enable_time_filter=True
enable_signal_quality=True
min_signal_quality=75.0  # Higher threshold
```

### Aggressive (Tối đa profit):
```python
# Risk Management
enable_trailing_stop=True
trailing_multiplier=2.0  # Loose trailing
enable_breakeven_stop=True
breakeven_activation_r=1.5  # Later activation
enable_partial_profit=False  # Hold to TP
enable_dynamic_sizing=True
dynamic_sizing_max_multiplier=3.0  # Higher max

# Filters
enable_multi_timeframe=True
enable_signal_quality=True
min_signal_quality=65.0  # Lower threshold
```

---

## 📚 DOCUMENTATION LINKS

- **Overview**: `overview.md`
- **Implementation Complete**: `IMPLEMENTATION_COMPLETE.md`
- **Integration Guide**: `integration-guide.md`
- **Quick Reference**: `QUICK_REFERENCE.md` (file này)

---

**Tất cả features đã sẵn sàng! 🚀**

