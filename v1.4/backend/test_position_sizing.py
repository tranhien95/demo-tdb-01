"""
Test Position Sizing Logic
Làm rõ khái niệm Risk% vs Position Size
"""

def test_position_sizing_concepts():
    """So sánh 2 cách hiểu Position Sizing"""
    
    print("=" * 80)
    print("POSITION SIZING - 2 CÁCH HIỂU")
    print("=" * 80)
    
    balance = 10000
    risk_pct = 10  # 10% risk per trade
    sl_pct = 0.75  # SL distance 0.75%
    entry_price = 1280
    
    print(f"\nSetup:")
    print(f"  Balance: ${balance:,.2f}")
    print(f"  Risk per trade: {risk_pct}%")
    print(f"  SL distance: {sl_pct}%")
    print(f"  Entry price: ${entry_price}")
    
    # ============================================
    # CÁCH 1: Position Size = Risk Amount (CODE HIỆN TẠI)
    # ============================================
    print("\n" + "=" * 80)
    print("CÁCH 1: POSITION SIZE = RISK AMOUNT (CODE HIỆN TẠI)")
    print("=" * 80)
    
    position_size_v1 = balance * (risk_pct / 100)
    
    print(f"\nLogic:")
    print(f"  position_size = balance × risk%")
    print(f"  position_size = ${balance:,.2f} × {risk_pct}% = ${position_size_v1:,.2f}")
    
    # Hit SL
    sl_price = entry_price * (1 + sl_pct / 100)  # SHORT
    price_loss_pct = (entry_price - sl_price) / entry_price * 100
    actual_loss_v1 = position_size_v1 * (price_loss_pct / 100)
    
    print(f"\nKhi hit SL:")
    print(f"  SL price: ${sl_price:.2f}")
    print(f"  Price loss: {price_loss_pct:.2f}%")
    print(f"  Actual loss: ${position_size_v1:,.2f} × {price_loss_pct:.2f}% = ${actual_loss_v1:,.2f}")
    print(f"  Loss % of balance: {(actual_loss_v1 / balance) * 100:.2f}%")
    
    # Hit TP (RR 2:1)
    tp_distance = sl_pct * 2
    tp_price = entry_price * (1 - tp_distance / 100)
    price_gain_pct = (entry_price - tp_price) / entry_price * 100
    actual_gain_v1 = position_size_v1 * (price_gain_pct / 100)
    
    print(f"\nKhi hit TP (RR 2:1):")
    print(f"  TP price: ${tp_price:.2f}")
    print(f"  Price gain: {price_gain_pct:.2f}%")
    print(f"  Actual gain: ${position_size_v1:,.2f} × {price_gain_pct:.2f}% = ${actual_gain_v1:,.2f}")
    print(f"  Gain % of balance: {(actual_gain_v1 / balance) * 100:.2f}%")
    
    print(f"\n⚠️  NHẬN XÉT:")
    print(f"  - Position size = ${position_size_v1:,.2f} (10% balance)")
    print(f"  - SL loss = ${actual_loss_v1:.2f} (0.075% balance) ← KHÔNG phải 10%!")
    print(f"  - Risk thực tế chỉ 0.075%, không phải 10%")
    
    # ============================================
    # CÁCH 2: Position Size dựa trên Risk/SL (THỰC TẾ)
    # ============================================
    print("\n" + "=" * 80)
    print("CÁCH 2: POSITION SIZE = RISK / SL DISTANCE (TRADING THỰC TẾ)")
    print("=" * 80)
    
    risk_amount = balance * (risk_pct / 100)  # $1000
    position_size_v2 = risk_amount / (sl_pct / 100)  # $1000 / 0.0075 = $133,333
    
    print(f"\nLogic:")
    print(f"  risk_amount = balance × risk% = ${risk_amount:,.2f}")
    print(f"  position_size = risk_amount / SL% = ${risk_amount:,.2f} / {sl_pct}%")
    print(f"  position_size = ${position_size_v2:,.2f}")
    
    # Hit SL
    actual_loss_v2 = position_size_v2 * (price_loss_pct / 100)
    
    print(f"\nKhi hit SL:")
    print(f"  SL price: ${sl_price:.2f}")
    print(f"  Price loss: {price_loss_pct:.2f}%")
    print(f"  Actual loss: ${position_size_v2:,.2f} × {price_loss_pct:.2f}% = ${actual_loss_v2:,.2f}")
    print(f"  Loss % of balance: {(actual_loss_v2 / balance) * 100:.2f}%")
    
    # Hit TP
    actual_gain_v2 = position_size_v2 * (price_gain_pct / 100)
    
    print(f"\nKhi hit TP (RR 2:1):")
    print(f"  TP price: ${tp_price:.2f}")
    print(f"  Price gain: {price_gain_pct:.2f}%")
    print(f"  Actual gain: ${position_size_v2:,.2f} × {price_gain_pct:.2f}% = ${actual_gain_v2:,.2f}")
    print(f"  Gain % of balance: {(actual_gain_v2 / balance) * 100:.2f}%")
    
    print(f"\n✅ NHẬN XÉT:")
    print(f"  - Position size = ${position_size_v2:,.2f}")
    print(f"  - SL loss = ${actual_loss_v2:.2f} (10% balance) ← ĐÚNG!")
    print(f"  - TP gain = ${actual_gain_v2:.2f} (20% balance với RR 2:1)")
    print(f"  - Đây là cách tính chuẩn trong trading")
    
    # ============================================
    # SO SÁNH
    # ============================================
    print("\n" + "=" * 80)
    print("SO SÁNH 2 CÁCH")
    print("=" * 80)
    
    print(f"\n{'Metric':<30} {'Cách 1 (Code)':<20} {'Cách 2 (Thực tế)':<20}")
    print("-" * 70)
    print(f"{'Position Size':<30} ${position_size_v1:<19,.2f} ${position_size_v2:<19,.2f}")
    print(f"{'SL Loss (USD)':<30} ${actual_loss_v1:<19.2f} ${actual_loss_v2:<19,.2f}")
    print(f"{'SL Loss (% balance)':<30} {(actual_loss_v1/balance)*100:<19.2f}% {(actual_loss_v2/balance)*100:<19.2f}%")
    print(f"{'TP Gain (USD)':<30} ${actual_gain_v1:<19.2f} ${actual_gain_v2:<19.2f}")
    print(f"{'TP Gain (% balance)':<30} {(actual_gain_v1/balance)*100:<19.2f}% {(actual_gain_v2/balance)*100:<19.2f}%")
    
    print("\n" + "=" * 80)
    print("KẾT LUẬN")
    print("=" * 80)
    print("\nCODE HIỆN TẠI đang dùng CÁCH 1:")
    print("✅ ĐÚNG nếu bạn muốn: 'Vào lệnh bằng 10% vốn'")
    print("   → Risk thực tế = 10% × 0.75% = 0.075% vốn khi SL")
    print("   → Win = 10% × 1.5% = 0.15% vốn khi TP (RR 2:1)")
    
    print("\n❌ SAI nếu bạn muốn: 'Risk 10% vốn mỗi lệnh'")
    print("   → Cần dùng CÁCH 2: position = risk / SL%")
    print("   → Position size sẽ lớn hơn nhiều!")
    
    print("\n🎯 CÂUHỎI CHO BẠN:")
    print("   'Risk 10%' có nghĩa là:")
    print("   A) Vào lệnh bằng 10% vốn (Cách 1 - code hiện tại)")
    print("   B) Chấp nhận mất tối đa 10% vốn nếu SL (Cách 2 - trading thực tế)")


def test_current_code_behavior():
    """Test xem code hiện tại hoạt động như thế nào"""
    
    print("\n\n" + "=" * 80)
    print("TEST CODE HIỆN TẠI")
    print("=" * 80)
    
    balance = 10000
    risk_pct = 10
    
    # Scenario: 1 trade SL -0.75%
    position_size = balance * (risk_pct / 100)  # $1000
    profit_pct = -0.75
    
    # Theo line 345: actual_profit_usd = position_size × profit_pct / 100
    profit_method1 = position_size * (profit_pct / 100)
    
    # Theo line 357: balance change = balance × risk_pct/100 × profit_pct/100  
    profit_method2 = balance * (risk_pct / 100) * (profit_pct / 100)
    
    new_balance = balance * (1 + (risk_pct / 100) * (profit_pct / 100))
    
    print(f"\nScenario: 1 trade hit SL -0.75%")
    print(f"  Balance: ${balance:,.2f}")
    print(f"  Risk: {risk_pct}%")
    print(f"  Position: ${position_size:,.2f}")
    
    print(f"\nProfit calculation:")
    print(f"  Method 1 (line 345): ${profit_method1:.2f}")
    print(f"  Method 2 (line 357): ${profit_method2:.2f}")
    print(f"  ✅ Cả 2 đều = ${profit_method1:.2f}")
    
    print(f"\nBalance change:")
    print(f"  New balance: ${new_balance:,.2f}")
    print(f"  Loss: ${balance - new_balance:.2f}")
    print(f"  Loss %: {((balance - new_balance) / balance) * 100:.4f}%")
    
    print(f"\n💡 KẾT LUẬN:")
    print(f"  Code hiện tại nhất quán: position_size = risk_amount")
    print(f"  Nghĩa là: 'Vào lệnh 10% vốn', không phải 'Risk 10% vốn'")
    print(f"  Risk thực tế = 10% × 0.75% = 0.075% vốn")


if __name__ == "__main__":
    test_position_sizing_concepts()
    test_current_code_behavior()
