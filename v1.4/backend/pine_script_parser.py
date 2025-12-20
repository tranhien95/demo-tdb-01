"""
Pine Script Parser
Parse Pine Script code to extract strategy configuration and run backtest

Note: Full Pine Script execution requires a complete interpreter.
This parser extracts key parameters from Pine Script code to reconstruct
a Strategy object for Python backtesting.
"""

import re
from typing import Dict, Any, Optional, List
from strategy_models import Strategy, IndicatorConfig, SignalLogic, RiskManagement, FilterConfig


class PineScriptParser:
    """Parse Pine Script code to extract strategy parameters"""
    
    @staticmethod
    def parse(pine_code: str) -> Dict[str, Any]:
        """
        Parse Pine Script code and extract strategy parameters
        
        Returns:
            Dict with extracted parameters:
            - strategy_name: str
            - indicators: List[str]
            - threshold_percent: float
            - candle_confirmation: int
            - risk_percent: float
            - sl_percent: float
            - rr_ratio: float
            - capital: float
            - filters: Dict
        """
        params = {
            'strategy_name': 'Parsed Strategy',
            'indicators': [],
            'threshold_percent': 70.0,
            'candle_confirmation': 2,
            'risk_percent': 10.0,
            'sl_percent': 5.0,
            'rr_ratio': 1.0,
            'capital': 1000.0,
            'filters': {}
        }
        
        # Extract strategy name
        name_match = re.search(r'strategy\("([^"]+)"', pine_code)
        if name_match:
            params['strategy_name'] = name_match.group(1)
        
        # Extract initial_capital
        capital_match = re.search(r'initial_capital\s*=\s*([\d.]+)', pine_code)
        if capital_match:
            params['capital'] = float(capital_match.group(1))
        
        # Extract risk parameters
        risk_match = re.search(r'risk_percent\s*=\s*([\d.]+)', pine_code)
        if risk_match:
            params['risk_percent'] = float(risk_match.group(1))
        
        sl_match = re.search(r'sl_percent\s*=\s*([\d.]+)', pine_code)
        if sl_match:
            params['sl_percent'] = float(sl_match.group(1))
        
        rr_match = re.search(r'rr_ratio\s*=\s*([\d.]+)', pine_code)
        if rr_match:
            params['rr_ratio'] = float(rr_match.group(1))
        
        # Extract threshold
        threshold_match = re.search(r'Threshold:\s*([\d.]+)%', pine_code)
        if threshold_match:
            params['threshold_percent'] = float(threshold_match.group(1))
        
        # Extract candle confirmation
        confirmation_match = re.search(r'candle_confirmation\s*>=\s*(\d+)', pine_code)
        if confirmation_match:
            params['candle_confirmation'] = int(confirmation_match.group(1))
        
        # Extract indicators from Pine Script code
        found_indicators = set()
        
        # 1. Detect Moving Averages (SMA/EMA)
        # Look for: ta.sma(..., period) or ta.ema(..., period)
        ma_patterns = [
            (r'(\w+)\s*=\s*useEMA\s*\?\s*ta\.ema\([^,]+,\s*(\d+)\)', 'EMA'),
            (r'(\w+)\s*=\s*useEMA\s*\?\s*ta\.ema\([^,]+,\s*(\w+)\)', 'EMA'),  # Variable period
            (r'(\w+)\s*=\s*ta\.ema\([^,]+,\s*(\d+)\)', 'EMA'),
            (r'(\w+)\s*=\s*ta\.sma\([^,]+,\s*(\d+)\)', 'SMA'),
            (r'maFast\s*=\s*.*?(?:sma|ema)\([^,]+,\s*(\d+)\)', 'SMA'),  # maFast pattern
            (r'maMid\s*=\s*.*?(?:sma|ema)\([^,]+,\s*(\d+)\)', 'SMA'),   # maMid pattern
            (r'maSlow\s*=\s*.*?(?:sma|ema)\([^,]+,\s*(\d+)\)', 'SMA'),  # maSlow pattern
        ]
        
        # Detect Triple MA strategy (MA5, MA10, MA20)
        if re.search(r'lenFast|lenMid|lenSlow|maFast|maMid|maSlow', pine_code):
            # Check for Triple MA pattern
            len_fast = re.search(r'lenFast\s*=\s*input\.int\((\d+)', pine_code)
            len_mid = re.search(r'lenMid\s*=\s*input\.int\((\d+)', pine_code)
            len_slow = re.search(r'lenSlow\s*=\s*input\.int\((\d+)', pine_code)
            
            if len_fast and len_mid and len_slow:
                # Triple MA detected
                found_indicators.add('SMA')  # Add SMA indicator
                # Could also add EMA_50, EMA_200 if periods match
                fast_period = int(len_fast.group(1))
                mid_period = int(len_mid.group(1))
                slow_period = int(len_slow.group(1))
                
                # Map to appropriate indicators
                if fast_period == 5:
                    found_indicators.add('SMA')
                if mid_period in [10, 12, 13]:
                    found_indicators.add('SMA')
                if slow_period in [20, 21, 26]:
                    found_indicators.add('SMA')
                if slow_period in [50, 51]:
                    found_indicators.add('SMA50')
                if slow_period in [200, 201]:
                    found_indicators.add('SMA200')
            else:
                # Generic MA detection
                found_indicators.add('SMA')
        
        # 2. Detect ADX - Only add as indicator if not used as filter
        # If ADX is used as filter (useADXFilter), don't add it to indicators list
        uses_adx_filter = re.search(r'useADXFilter\s*=\s*input\.bool\(true', pine_code, re.IGNORECASE)
        if re.search(r'adx\s*=\s*|ta\.adx\(|ADX|adxThreshold', pine_code, re.IGNORECASE):
            # Only add ADX as indicator if it's NOT used as a filter
            # If useADXFilter is true, ADX is a filter only, not an indicator
            if not uses_adx_filter:
                found_indicators.add('ADX')
        
        # 3. Detect SuperTrend
        if re.search(r'supertrend|ta\.supertrend|useSuperTrend', pine_code, re.IGNORECASE):
            found_indicators.add('SuperTrend')
        
        # 4. Detect other common indicators
        if re.search(r'ta\.rsi\(', pine_code, re.IGNORECASE):
            found_indicators.add('RSI')
        if re.search(r'ta\.macd\(', pine_code, re.IGNORECASE):
            found_indicators.add('MACD')
        if re.search(r'ta\.stoch\(|ta\.stochastic\(', pine_code, re.IGNORECASE):
            found_indicators.add('Stochastic')
        if re.search(r'ta\.bb\(|bollinger', pine_code, re.IGNORECASE):
            found_indicators.add('Bollinger_Bands')
        if re.search(r'ta\.atr\(', pine_code, re.IGNORECASE):
            found_indicators.add('ATR')
        if re.search(r'ta\.cci\(', pine_code, re.IGNORECASE):
            found_indicators.add('CCI')
        if re.search(r'ta\.obv\(', pine_code, re.IGNORECASE):
            found_indicators.add('OBV')
        
        # Common indicator mappings
        indicator_mappings = {
            'Momentum': 'Momentum',
            'Rsi': 'RSI',
            'Macd': 'MACD',
            'Obv': 'OBV',
            'Bollinger': 'Bollinger_Bands',
            'Pivot': 'Pivot_Points',
            'Stochastic': 'Stochastic',
            'Cci': 'CCI',
            'Atr': 'ATR',
            'Adx': 'ADX',
            'Volume': 'Volume_MA',
            'Fibonacci': 'Fibonacci',
            'Ichimoku': 'Ichimoku',
            'SMA': 'SMA',
            'SuperTrend': 'SuperTrend',
        }
        
        mapped_indicators = []
        for ind in found_indicators:
            if ind in indicator_mappings:
                mapped_indicators.append(indicator_mappings[ind])
            else:
                mapped_indicators.append(ind)
        
        # Remove duplicates while preserving order
        seen = set()
        unique_indicators = []
        for ind in mapped_indicators:
            if ind not in seen:
                seen.add(ind)
                unique_indicators.append(ind)
        
        params['indicators'] = unique_indicators if unique_indicators else ['SMA']  # Default for MA strategies
        
        # Extract filters
        # ADX Filter
        if re.search(r'useADXFilter|adx_filter|adx_ok', pine_code, re.IGNORECASE):
            params['filters']['enable_adx_filter'] = True
            # Extract ADX threshold
            adx_threshold_match = re.search(r'adxThreshold\s*=\s*input\.int\((\d+)', pine_code)
            if adx_threshold_match:
                params['filters']['adx_threshold'] = float(adx_threshold_match.group(1))
            else:
                # Try to find adx > threshold pattern
                adx_val_match = re.search(r'adx\s*>\s*(\d+)', pine_code)
                if adx_val_match:
                    params['filters']['adx_threshold'] = float(adx_val_match.group(1))
                else:
                    params['filters']['adx_threshold'] = 25.0  # Default
        
        # SuperTrend Filter
        if re.search(r'useSuperTrend|st_ok', pine_code, re.IGNORECASE):
            params['filters']['enable_supertrend_filter'] = True
        
        # Volume Filter
        if re.search(r'volume_filter|vol_ma|volume.*filter', pine_code, re.IGNORECASE):
            params['filters']['enable_volume_filter'] = True
        
        # MA Trend Filter
        if re.search(r'ma_trend|ma_filter|price.*ma', pine_code, re.IGNORECASE):
            params['filters']['enable_ma_filter'] = True
            ma_period_match = re.search(r'ma_trend\s*=\s*ta\.sma\([^,]+,\s*(\d+)', pine_code)
            if ma_period_match:
                params['filters']['ma_period'] = int(ma_period_match.group(1))
        
        return params
    
    @staticmethod
    def parse_to_strategy(pine_code: str) -> Strategy:
        """
        Parse Pine Script and convert to Strategy object for backtesting
        
        Note: This is a simplified parser. For full accuracy, a complete
        Pine Script interpreter would be needed.
        """
        params = PineScriptParser.parse(pine_code)
        
        # Build indicator configs
        # Exclude ADX if it's used as a filter only (not as a signal indicator)
        indicator_configs = []
        adx_is_filter_only = params['filters'].get('enable_adx_filter', False)
        for ind_name in params['indicators']:
            # Skip ADX if it's being used as a filter only
            if ind_name == 'ADX' and adx_is_filter_only:
                continue  # ADX is a filter, not an indicator for signal calculation
            indicator_configs.append(IndicatorConfig(
                type=ind_name,
                enabled=True,
                weight=1.0
            ))
        
        # Build filters
        filters = FilterConfig(
            enable_adx=params['filters'].get('enable_adx_filter', False),
            adx_threshold=params['filters'].get('adx_threshold', 25.0),
            enable_volume=params['filters'].get('enable_volume_filter', False),
            volume_threshold=1.5,
            enable_ma_filter=params['filters'].get('enable_ma_filter', False),
            ma_period=params['filters'].get('ma_period', 50),
            enable_atr_filter=params['filters'].get('enable_atr_filter', False),
            min_atr=1.0,
            enable_trend_filter=params['filters'].get('enable_trend_filter', False),
            trend_ma=200
        )
        
        # Build strategy
        strategy = Strategy(
            name=params['strategy_name'],
            description=f"Parsed from Pine Script",
            indicators=indicator_configs,
            signal_logic=SignalLogic(
                threshold_percent=params['threshold_percent'],
                candle_confirmation=params['candle_confirmation']
            ),
            filters=filters,
            risk_management=RiskManagement(
                risk_percent=params['risk_percent'],
                reward_ratio=params['rr_ratio'],
                stop_loss_percent=params['sl_percent'],
                capital=params['capital']
            )
        )
        
        return strategy

