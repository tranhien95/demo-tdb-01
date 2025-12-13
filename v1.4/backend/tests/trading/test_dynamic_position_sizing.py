"""
Test Dynamic Position Sizing Implementation
Demo cách dynamic sizing hoạt động
"""
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))

from trading_improvements import TradingImprovements


def test_dynamic_sizing_scenarios():
    """Test dynamic sizing với different scenarios"""
    
    print("=" * 80)
    print("TEST DYNAMIC POSITION SIZING")
    print("=" * 80)
    
    base_risk = 2.0  # 2% base risk
    max_multiplier = 2.0
    
    scenarios = [
        {
            "name": "High Confidence, Normal Volatility",
            "confidence": 95.0,
            "volatility": 1.0,
            "expected_mult": 2.0
        },
        {
            "name": "Low Confidence, High Volatility",
            "confidence": 65.0,
            "volatility": 2.5,
            "expected_mult": 0.25
        },
        {
            "name": "Medium Confidence, Normal Volatility",
            "confidence": 85.0,
            "volatility": 1.0,
            "expected_mult": 1.0
        },
        {
            "name": "High Confidence, High Volatility",
            "confidence": 95.0,
            "volatility": 2.5,
            "expected_mult": 1.0
        },
        {
            "name": "Low Confidence, Low Volatility",
            "confidence": 65.0,
            "volatility": 0.2,
            "expected_mult": 0.375
        },
        {
            "name": "Very High Confidence, Low Volatility",
            "confidence": 98.0,
            "volatility": 0.5,
            "expected_mult": 1.5
        },
    ]
    
    print(f"\nBase Risk: {base_risk}%")
    print(f"Max Multiplier: {max_multiplier}x")
    print(f"\n{'='*80}")
    print("SCENARIOS")
    print("="*80)
    
    for i, scenario in enumerate(scenarios, 1):
        print(f"\n--- Scenario {i}: {scenario['name']} ---")
        print(f"  Confidence: {scenario['confidence']}%")
        print(f"  Volatility: {scenario['volatility']}%")
        
        adjusted_risk = TradingImprovements.calculate_dynamic_position_size(
            base_risk_pct=base_risk,
            confidence=scenario['confidence'],
            volatility_pct=scenario['volatility'],
            max_multiplier=max_multiplier
        )
        
        multiplier = adjusted_risk / base_risk
        print(f"  Adjusted Risk: {adjusted_risk:.2f}%")
        print(f"  Multiplier: {multiplier:.2f}x")
        print(f"  Expected: {scenario['expected_mult']:.2f}x")
        
        if abs(multiplier - scenario['expected_mult']) < 0.1:
            print(f"  ✅ Match!")
        else:
            print(f"  ⚠️  Difference: {abs(multiplier - scenario['expected_mult']):.2f}x")


def test_position_size_calculation():
    """Test tính position size với dynamic sizing"""
    
    print("\n" + "=" * 80)
    print("POSITION SIZE CALCULATION")
    print("=" * 80)
    
    balance = 10000.0
    base_risk = 2.0
    entry_price = 100.0
    sl_distance_pct = 1.0  # 1% SL
    
    scenarios = [
        {"confidence": 95.0, "volatility": 1.0, "name": "Strong Signal"},
        {"confidence": 65.0, "volatility": 2.5, "name": "Weak Signal"},
        {"confidence": 85.0, "volatility": 1.0, "name": "Normal Signal"},
    ]
    
    print(f"\nSetup:")
    print(f"  Balance: ${balance:,.2f}")
    print(f"  Base Risk: {base_risk}%")
    print(f"  Entry Price: ${entry_price:.2f}")
    print(f"  SL Distance: {sl_distance_pct}%")
    
    print(f"\n{'='*80}")
    print("COMPARISON: Fixed vs Dynamic")
    print("="*80)
    
    # Fixed sizing
    fixed_risk_amount = balance * (base_risk / 100)
    fixed_position_size = fixed_risk_amount / (entry_price * sl_distance_pct / 100)
    
    print(f"\nFIXED SIZING:")
    print(f"  Risk Amount: ${fixed_risk_amount:.2f}")
    print(f"  Position Size: {fixed_position_size:.2f} units")
    print(f"  Position Value: ${fixed_position_size * entry_price:,.2f}")
    
    print(f"\nDYNAMIC SIZING:")
    for scenario in scenarios:
        adjusted_risk = TradingImprovements.calculate_dynamic_position_size(
            base_risk_pct=base_risk,
            confidence=scenario['confidence'],
            volatility_pct=scenario['volatility'],
            max_multiplier=2.0
        )
        
        risk_amount = balance * (adjusted_risk / 100)
        position_size = risk_amount / (entry_price * sl_distance_pct / 100)
        
        print(f"\n  {scenario['name']}:")
        print(f"    Confidence: {scenario['confidence']}%, Volatility: {scenario['volatility']}%")
        print(f"    Adjusted Risk: {adjusted_risk:.2f}%")
        print(f"    Risk Amount: ${risk_amount:.2f}")
        print(f"    Position Size: {position_size:.2f} units")
        print(f"    Position Value: ${position_size * entry_price:,.2f}")
        print(f"    vs Fixed: {((position_size / fixed_position_size - 1) * 100):+.1f}%")


def test_multiplier_table():
    """Test multiplier table cho confidence và volatility"""
    
    print("\n" + "=" * 80)
    print("MULTIPLIER TABLES")
    print("=" * 80)
    
    base_risk = 2.0
    
    print(f"\nCONFIDENCE MULTIPLIER (Base Risk: {base_risk}%):")
    print(f"{'Confidence':<15} {'Multiplier':<12} {'Adjusted Risk':<15}")
    print("-" * 45)
    
    confidence_levels = [60, 65, 70, 75, 80, 85, 90, 92, 95, 98]
    for conf in confidence_levels:
        adjusted = TradingImprovements.calculate_dynamic_position_size(
            base_risk_pct=base_risk,
            confidence=float(conf),
            volatility_pct=1.0,  # Normal volatility
            max_multiplier=2.0
        )
        multiplier = adjusted / base_risk
        print(f"{conf}%{'':<10} {multiplier:.2f}x{'':<8} {adjusted:.2f}%")
    
    print(f"\nVOLATILITY MULTIPLIER (Base Risk: {base_risk}%, Confidence: 85%):")
    print(f"{'Volatility':<15} {'Multiplier':<12} {'Adjusted Risk':<15}")
    print("-" * 45)
    
    volatility_levels = [0.1, 0.2, 0.3, 0.5, 1.0, 1.5, 2.0, 2.5, 3.0]
    for vol in volatility_levels:
        adjusted = TradingImprovements.calculate_dynamic_position_size(
            base_risk_pct=base_risk,
            confidence=85.0,
            volatility_pct=vol,
            max_multiplier=2.0
        )
        multiplier = adjusted / base_risk
        print(f"{vol}%{'':<11} {multiplier:.2f}x{'':<8} {adjusted:.2f}%")


if __name__ == "__main__":
    test_dynamic_sizing_scenarios()
    test_position_size_calculation()
    test_multiplier_table()
    
    print("\n" + "=" * 80)
    print("✅ DYNAMIC POSITION SIZING TEST COMPLETE")
    print("=" * 80)
    print("\nKey Features:")
    print("  ✅ Confidence-based adjustment (0.5x - 2.0x)")
    print("  ✅ Volatility-based adjustment (0.5x - 1.0x)")
    print("  ✅ Max multiplier cap (default 2.0x)")
    print("  ✅ Tối ưu risk/reward ratio")

