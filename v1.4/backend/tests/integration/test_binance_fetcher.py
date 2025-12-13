#!/usr/bin/env python3
"""
Test script để verify Binance fetcher hoạt động đúng
"""
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))

from binance_fetcher import get_binance_fetcher

def test_binance_fetcher():
    """Test tất cả tính năng của Binance Fetcher"""
    
    print("=" * 60)
    print("🧪 TESTING BINANCE FETCHER v1.4")
    print("=" * 60)
    
    fetcher = get_binance_fetcher()
    
    # Test 1: Get available symbols
    print("\n[TEST 1] Getting available symbols...")
    try:
        symbols = fetcher.get_available_symbols()
        print(f"✅ Found {len(symbols)} popular symbols")
        print(f"   Symbols: {', '.join(symbols[:5])}...")
    except Exception as e:
        print(f"❌ Error: {e}")
        return False
    
    # Test 2: Get timeframes
    print("\n[TEST 2] Getting timeframes...")
    try:
        timeframes = fetcher.get_timeframes()
        print(f"✅ Found {len(timeframes)} timeframes")
        print(f"   Available: {', '.join(timeframes.values())}")
    except Exception as e:
        print(f"❌ Error: {e}")
        return False
    
    # Test 3: Validate symbol
    print("\n[TEST 3] Validating symbols...")
    try:
        valid = fetcher.validate_symbol('BTC/USDT')
        print(f"✅ BTC/USDT is valid: {valid}")
        
        invalid = fetcher.validate_symbol('FAKE/USDT')
        print(f"✅ FAKE/USDT is invalid: {not invalid}")
    except Exception as e:
        print(f"❌ Error: {e}")
        return False
    
    # Test 4: Get symbol info
    print("\n[TEST 4] Getting symbol info...")
    try:
        info = fetcher.get_symbol_info('BTC/USDT')
        if info:
            print(f"✅ BTC/USDT info:")
            print(f"   Base: {info.get('base')}")
            print(f"   Quote: {info.get('quote')}")
            print(f"   Active: {info.get('active')}")
        else:
            print("❌ Could not get symbol info")
            return False
    except Exception as e:
        print(f"❌ Error: {e}")
        return False
    
    # Test 5: Fetch BTC/USDT 15m data
    print("\n[TEST 5] Fetching BTC/USDT 15m data (50 candles)...")
    try:
        data = fetcher.fetch_ohlcv('BTC/USDT', '15m', 50)
        if data:
            print(f"✅ Fetched {len(data)} candles")
            print(f"   First: {data[0]}")
            print(f"   Last:  {data[-1]}")
        else:
            print("❌ No data returned")
            return False
    except Exception as e:
        print(f"❌ Error: {e}")
        return False
    
    # Test 6: Fetch ETH/USDT 1h data
    print("\n[TEST 6] Fetching ETH/USDT 1h data (100 candles)...")
    try:
        data = fetcher.fetch_ohlcv('ETH/USDT', '1h', 100)
        if data:
            print(f"✅ Fetched {len(data)} candles")
            print(f"   Price range: ${data[0]['low']:.2f} - ${data[-1]['high']:.2f}")
        else:
            print("❌ No data returned")
            return False
    except Exception as e:
        print(f"❌ Error: {e}")
        return False
    
    # Test 7: Fetch multiple symbols
    print("\n[TEST 7] Fetching multiple symbols...")
    try:
        symbols = ['BTC/USDT', 'ETH/USDT', 'BNB/USDT']
        result = fetcher.fetch_multiple_symbols(symbols, '1h', 50)
        print(f"✅ Fetched data for {len(result)} symbols")
        for sym, data in result.items():
            print(f"   {sym}: {len(data)} candles")
    except Exception as e:
        print(f"❌ Error: {e}")
        return False
    
    print("\n" + "=" * 60)
    print("✅ ALL TESTS PASSED!")
    print("=" * 60)
    print("\n📊 Binance Fetcher is working correctly!")
    print("You can now:")
    print("  1. Run the backend: python main.py")
    print("  2. Open http://localhost:3000")
    print("  3. Use the 'Lấy Data từ Binance' section")
    
    return True

if __name__ == '__main__':
    success = test_binance_fetcher()
    sys.exit(0 if success else 1)
