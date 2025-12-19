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
        
        # Extract indicators (from comments or variable names)
        # Look for indicator variable patterns
        indicator_patterns = [
            r'(\w+)_\d+_(val|bull|bear)',  # momentum_0_bull, rsi_1_val, etc.
            r'//\s*([A-Z_]+)\s+contributes',  # // RSI contributes
            r'(\w+)\s*=\s*ta\.',  # rsi = ta.rsi(...)
        ]
        
        found_indicators = set()
        for pattern in indicator_patterns:
            matches = re.findall(pattern, pine_code)
            for match in matches:
                if isinstance(match, tuple):
                    match = match[0]
                # Clean indicator name
                ind_name = match.split('_')[0].title().replace('_', ' ')
                if ind_name and len(ind_name) > 2:
                    found_indicators.add(ind_name)
        
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
        }
        
        mapped_indicators = []
        for ind in found_indicators:
            if ind in indicator_mappings:
                mapped_indicators.append(indicator_mappings[ind])
            else:
                mapped_indicators.append(ind)
        
        params['indicators'] = mapped_indicators if mapped_indicators else ['RSI', 'MACD']  # Default
        
        # Extract filters
        if 'adx_filter' in pine_code.lower():
            adx_threshold_match = re.search(r'adx_val\s*>\s*(\d+)', pine_code)
            if adx_threshold_match:
                params['filters']['enable_adx_filter'] = True
                params['filters']['adx_threshold'] = float(adx_threshold_match.group(1))
        
        if 'volume_filter' in pine_code.lower() or 'vol_ma' in pine_code.lower():
            params['filters']['enable_volume_filter'] = True
        
        if 'ma_trend' in pine_code.lower() or 'ma_filter' in pine_code.lower():
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
        indicator_configs = []
        for ind_name in params['indicators']:
            indicator_configs.append(IndicatorConfig(
                type=ind_name,
                enabled=True,
                weight=1.0
            ))
        
        # Build filters
        filters = FilterConfig(
            enable_adx_filter=params['filters'].get('enable_adx_filter', False),
            adx_threshold=params['filters'].get('adx_threshold', 25.0),
            enable_volume_filter=params['filters'].get('enable_volume_filter', False),
            volume_threshold=1.5,
            volume_ma_period=params['filters'].get('volume_ma_period', 20),
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

