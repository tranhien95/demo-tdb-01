"""
Script to validate backtest data structure
Checks if the data format matches expected structure
"""

import json
import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from strategy_models_simple import SignalDetail


def validate_entry_signals(entry_signals):
    """Validate entry_signals structure"""
    if not isinstance(entry_signals, list):
        return False, f"entry_signals should be a list, got {type(entry_signals)}"
    
    required_fields = [
        'indicator_type', 'indicator_id', 'bullish', 'bearish', 
        'value', 'weight', 'contribution_percent', 'enabled'
    ]
    
    for i, signal in enumerate(entry_signals):
        if not isinstance(signal, dict):
            return False, f"entry_signals[{i}] should be a dict, got {type(signal)}"
        
        for field in required_fields:
            if field not in signal:
                return False, f"entry_signals[{i}] missing required field: {field}"
    
    return True, "entry_signals structure is valid"


def validate_trade(trade):
    """Validate a single trade structure"""
    required_fields = [
        'entry', 'exit', 'sl', 'tp', 'profit', 'profit_pct',
        'position_size', 'position_percent', 'type', 'time',
        'exit_time', 'entry_signals'
    ]
    
    for field in required_fields:
        if field not in trade:
            return False, f"Trade missing required field: {field}"
    
    # Validate entry_signals
    is_valid, message = validate_entry_signals(trade.get('entry_signals', []))
    if not is_valid:
        return False, f"Trade entry_signals validation failed: {message}"
    
    return True, "Trade structure is valid"


def validate_backtest_result(result):
    """Validate backtest result structure"""
    required_fields = [
        'status', 'total_trades', 'winning_trades', 'losing_trades',
        'win_rate', 'profit_factor', 'total_profit', 'total_profit_pct',
        'max_drawdown', 'sharpe_ratio', 'trades', 'long_trades',
        'short_trades', 'signals_found', 'long_signals', 'short_signals',
        'equity_curve'
    ]
    
    for field in required_fields:
        if field not in result:
            return False, f"Result missing required field: {field}"
    
    # Validate trades
    if not isinstance(result['trades'], list):
        return False, "trades should be a list"
    
    for i, trade in enumerate(result['trades'][:5]):  # Check first 5 trades
        is_valid, message = validate_trade(trade)
        if not is_valid:
            return False, f"Trade[{i}] validation failed: {message}"
    
    return True, "Backtest result structure is valid"


def check_data_from_file(file_path):
    """Check data from a JSON file"""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        print(f"Checking data from: {file_path}")
        print(f"Data type: {type(data)}")
        
        if isinstance(data, dict):
            # Check if it's a backtest result
            if 'status' in data and 'trades' in data:
                is_valid, message = validate_backtest_result(data)
                print(f"\nValidation Result: {message}")
                if is_valid:
                    print("\n✓ Data structure is valid!")
                    print(f"\nSummary:")
                    print(f"  - Status: {data.get('status')}")
                    print(f"  - Total Trades: {data.get('total_trades')}")
                    print(f"  - Win Rate: {data.get('win_rate')}%")
                    print(f"  - Total Profit: ${data.get('total_profit')}")
                    if data.get('trades'):
                        first_trade = data['trades'][0]
                        print(f"  - First Trade Entry Signals: {len(first_trade.get('entry_signals', []))} signals")
                else:
                    print(f"\n✗ Validation failed: {message}")
            else:
                print("Data appears to be a request or other structure")
                print(f"Keys: {list(data.keys())}")
        elif isinstance(data, list):
            print(f"Data is a list with {len(data)} items")
            if data and isinstance(data[0], dict):
                print(f"First item keys: {list(data[0].keys())}")
        
    except Exception as e:
        print(f"Error reading file: {e}")


def check_data_from_stdin():
    """Check data from stdin (pasted JSON)"""
    try:
        print("Paste your JSON data (press Ctrl+D or Ctrl+Z when done):")
        content = sys.stdin.read()
        data = json.loads(content)
        
        if isinstance(data, dict):
            if 'status' in data and 'trades' in data:
                is_valid, message = validate_backtest_result(data)
                print(f"\nValidation Result: {message}")
                if is_valid:
                    print("\n✓ Data structure is valid!")
                    print(f"\nSummary:")
                    print(f"  - Status: {data.get('status')}")
                    print(f"  - Total Trades: {data.get('total_trades')}")
                    print(f"  - Win Rate: {data.get('win_rate')}%")
                    print(f"  - Total Profit: ${data.get('total_profit')}")
                    if data.get('trades'):
                        first_trade = data['trades'][0]
                        print(f"  - First Trade Entry Signals: {len(first_trade.get('entry_signals', []))} signals")
                        if first_trade.get('entry_signals'):
                            print(f"\n  First Entry Signal Details:")
                            sig = first_trade['entry_signals'][0]
                            for key, value in sig.items():
                                print(f"    {key}: {value}")
                else:
                    print(f"\n✗ Validation failed: {message}")
    except Exception as e:
        print(f"Error parsing JSON: {e}")


if __name__ == "__main__":
    if len(sys.argv) > 1:
        # Check from file
        file_path = sys.argv[1]
        check_data_from_file(file_path)
    else:
        # Check from stdin
        check_data_from_stdin()

