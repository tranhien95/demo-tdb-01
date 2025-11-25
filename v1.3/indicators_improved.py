"""
Trading Indicators Library - IMPROVED VERSION
20 Technical Indicators with Strength Score & Convergence Detection
Designed for high-accuracy signal filtering
"""

from typing import List, Dict, Optional, Tuple
import math


class IndicatorCalculator:
    """Calculate 20 technical indicators with strength validation"""

    # ======================== HELPER METHODS ========================
    
    @staticmethod
    def sma(data: List[float], period: int) -> List[Optional[float]]:
        """Simple Moving Average"""
        sma = []
        for i in range(len(data)):
            if i < period - 1:
                sma.append(None)
            else:
                avg = sum(data[i - period + 1:i + 1]) / period
                sma.append(avg)
        return sma

    @staticmethod
    def ema(data: List[float], period: int) -> List[Optional[float]]:
        """Exponential Moving Average"""
        ema = []
        multiplier = 2 / (period + 1)
        
        for i in range(len(data)):
            if i < period - 1:
                ema.append(None)
            elif i == period - 1:
                ema.append(sum(data[:period]) / period)
            else:
                prev_ema = ema[i - 1]
                new_ema = data[i] * multiplier + prev_ema * (1 - multiplier)
                ema.append(new_ema)
        
        return ema

    # ======================== IMPROVED INDICATORS ========================
    
    @staticmethod
    def rsi(data: List[Dict], index: int, period: int = 14) -> Dict:
        """RSI with Strength Score"""
        if index < period:
            return {
                "bullish": False,
                "bearish": False,
                "value": 50,
                "strength": 0  # NEW: 0-100
            }
        
        gains, losses = 0, 0
        for i in range(index - period + 1, index + 1):
            change = data[i]["close"] - data[i - 1]["close"]
            if change > 0:
                gains += change
            else:
                losses -= change
        
        avg_gain = gains / period
        avg_loss = losses / period
        rs = avg_gain / avg_loss if avg_loss != 0 else 100
        rsi_val = 100 - (100 / (1 + rs))
        
        # Strength Score: 0-100
        # Extreme levels = higher confidence
        strength = 0
        if rsi_val < 10:
            strength = 100  # EXTREME OVERSOLD
        elif rsi_val < 20:
            strength = 90   # VERY OVERSOLD
        elif rsi_val < 30:
            strength = 70   # OVERSOLD
        elif rsi_val < 40:
            strength = 40   # WEAKLY OVERSOLD
        elif rsi_val > 90:
            strength = 100  # EXTREME OVERBOUGHT
        elif rsi_val > 80:
            strength = 90   # VERY OVERBOUGHT
        elif rsi_val > 70:
            strength = 70   # OVERBOUGHT
        elif rsi_val > 60:
            strength = 40   # WEAKLY OVERBOUGHT
        else:
            strength = 20   # NEUTRAL
        
        return {
            "bullish": rsi_val < 30,
            "bearish": rsi_val > 70,
            "value": rsi_val,
            "strength": strength
        }

    @staticmethod
    def macd(data: List[Dict], index: int, fast: int = 12, slow: int = 26, signal: int = 9) -> Dict:
        """MACD with Strength Score"""
        if index < slow:
            return {
                "bullish": False,
                "bearish": False,
                "value": 0,
                "strength": 0,
                "histogram": 0
            }
        
        closes = [d["close"] for d in data[:index + 1]]
        ema_fast = IndicatorCalculator.ema(closes, fast)
        ema_slow = IndicatorCalculator.ema(closes, slow)
        
        macd_line = (ema_fast[index] or 0) - (ema_slow[index] or 0)
        
        # Calculate signal line
        macd_vals = []
        for i in range(len(closes)):
            if ema_fast[i] and ema_slow[i]:
                macd_vals.append(ema_fast[i] - ema_slow[i])
            else:
                macd_vals.append(None)
        
        signal_line_vals = IndicatorCalculator.ema([v for v in macd_vals if v is not None], signal)
        signal_val = signal_line_vals[-1] if signal_line_vals and signal_line_vals[-1] is not None else 0
        histogram = macd_line - signal_val
        
        # Strength Score: based on histogram magnitude
        abs_hist = abs(histogram)
        if abs_hist > 0.5:
            strength = 100  # STRONG
        elif abs_hist > 0.3:
            strength = 80
        elif abs_hist > 0.1:
            strength = 60
        else:
            strength = 30  # WEAK
        
        return {
            "bullish": macd_line > signal_val and histogram > 0,
            "bearish": macd_line < signal_val and histogram < 0,
            "value": macd_line,
            "strength": strength,
            "histogram": histogram
        }

    @staticmethod
    def stochastic(data: List[Dict], index: int, period: int = 14) -> Dict:
        """Stochastic Oscillator with Strength Score"""
        if index < period:
            return {
                "bullish": False,
                "bearish": False,
                "value": 50,
                "strength": 0
            }
        
        high = max(d["high"] for d in data[index - period + 1:index + 1])
        low = min(d["low"] for d in data[index - period + 1:index + 1])
        k = ((data[index]["close"] - low) / (high - low) * 100) if (high - low) != 0 else 50
        
        # Strength Score
        strength = 0
        if k < 10:
            strength = 100  # EXTREME OVERSOLD
        elif k < 20:
            strength = 80
        elif k < 30:
            strength = 60
        elif k > 90:
            strength = 100  # EXTREME OVERBOUGHT
        elif k > 80:
            strength = 80
        elif k > 70:
            strength = 60
        else:
            strength = 30
        
        return {
            "bullish": k < 20,
            "bearish": k > 80,
            "value": k,
            "strength": strength
        }

    @staticmethod
    def bollinger_bands(data: List[Dict], index: int, period: int = 20, std_dev: int = 2) -> Dict:
        """Bollinger Bands with Strength Score"""
        if index < period:
            return {
                "bullish": False,
                "bearish": False,
                "value": 0,
                "strength": 0
            }
        
        closes = [d["close"] for d in data[index - period + 1:index + 1]]
        mean = sum(closes) / period
        variance = sum((x - mean) ** 2 for x in closes) / period
        std = math.sqrt(variance)
        
        upper = mean + std_dev * std
        lower = mean - std_dev * std
        
        # Strength: How far price is from bands
        distance_to_upper = (upper - data[index]["close"]) / (upper - lower) if (upper - lower) > 0 else 0.5
        distance_to_lower = (data[index]["close"] - lower) / (upper - lower) if (upper - lower) > 0 else 0.5
        
        strength = 0
        if distance_to_lower < 0.1:  # Very close to lower band
            strength = 90  # STRONG BULLISH
        elif distance_to_lower < 0.2:
            strength = 70
        elif distance_to_upper < 0.1:  # Very close to upper band
            strength = 90  # STRONG BEARISH
        elif distance_to_upper < 0.2:
            strength = 70
        else:
            strength = 30
        
        return {
            "bullish": data[index]["close"] < lower,
            "bearish": data[index]["close"] > upper,
            "value": mean,
            "strength": strength
        }

    @staticmethod
    def volume_ma(data: List[Dict], index: int, period: int = 20) -> Dict:
        """Volume Moving Average with Strength Score"""
        if index < period:
            return {
                "bullish": False,
                "bearish": False,
                "value": 0,
                "strength": 0
            }
        
        vol_ma = sum(d["volume"] for d in data[index - period + 1:index + 1]) / period
        current_vol = data[index]["volume"]
        
        # Strength: How much volume exceeds MA
        vol_ratio = current_vol / vol_ma if vol_ma > 0 else 1
        
        strength = 0
        if vol_ratio > 1.5:
            strength = 90  # VERY HIGH VOLUME
        elif vol_ratio > 1.3:
            strength = 75
        elif vol_ratio > 1.1:
            strength = 60
        elif vol_ratio < 0.7:
            strength = 75  # LOW VOLUME (caution)
        else:
            strength = 40
        
        return {
            "bullish": current_vol > vol_ma * 1.2,
            "bearish": current_vol < vol_ma * 0.8,
            "value": vol_ma,
            "strength": strength
        }

    @staticmethod
    def ema_50(data: List[Dict], index: int) -> Dict:
        """EMA 50 with Strength Score"""
        closes = [d["close"] for d in data[:index + 1]]
        ema_vals = IndicatorCalculator.ema(closes, 50)
        ema_val = ema_vals[index] if ema_vals[index] is not None else data[index]["close"]
        
        # Strength: Distance from EMA
        distance = abs(data[index]["close"] - ema_val) / ema_val if ema_val > 0 else 0
        
        strength = 0
        if distance > 0.05:  # 5% away
            strength = 80
        elif distance > 0.03:  # 3% away
            strength = 60
        else:
            strength = 30
        
        return {
            "bullish": data[index]["close"] > ema_val,
            "bearish": data[index]["close"] < ema_val,
            "value": ema_val,
            "strength": strength
        }

    @staticmethod
    def ema_200(data: List[Dict], index: int) -> Dict:
        """EMA 200 with Strength Score"""
        closes = [d["close"] for d in data[:index + 1]]
        ema_vals = IndicatorCalculator.ema(closes, 200)
        ema_val = ema_vals[index] if ema_vals[index] is not None else data[index]["close"]
        
        # Strength: Distance from EMA
        distance = abs(data[index]["close"] - ema_val) / ema_val if ema_val > 0 else 0
        
        strength = 0
        if distance > 0.10:  # 10% away
            strength = 80
        elif distance > 0.05:  # 5% away
            strength = 60
        else:
            strength = 30
        
        return {
            "bullish": data[index]["close"] > ema_val,
            "bearish": data[index]["close"] < ema_val,
            "value": ema_val,
            "strength": strength
        }

    @staticmethod
    def adx(data: List[Dict], index: int, period: int = 14) -> Dict:
        """Average Directional Index - CRITICAL FILTER"""
        if index < period * 2:
            return {
                "bullish": False,
                "bearish": False,
                "value": 0,
                "strength": 0
            }
        
        plus_dm, minus_dm = 0, 0
        for i in range(index - period + 1, index + 1):
            up_move = data[i]["high"] - data[i - 1]["high"]
            down_move = data[i - 1]["low"] - data[i]["low"]
            
            if up_move > down_move and up_move > 0:
                plus_dm += up_move
            if down_move > up_move and down_move > 0:
                minus_dm += down_move
        
        atr_val = IndicatorCalculator.atr(data, index, period)
        plus_di = (plus_dm / atr_val * 100) if atr_val > 0 else 0
        minus_di = (minus_dm / atr_val * 100) if atr_val > 0 else 0
        adx_val = abs(plus_di - minus_di) / (plus_di + minus_di) * 100 if (plus_di + minus_di) > 0 else 0
        
        # Strength: Based on ADX level
        # ADX < 20 = No trend (avoid trading)
        # ADX 20-40 = Normal trend (good to trade)
        # ADX > 40 = Strong trend (best to trade)
        strength = 0
        if adx_val > 50:
            strength = 100  # EXTREMELY STRONG TREND
        elif adx_val > 40:
            strength = 90
        elif adx_val > 30:
            strength = 80
        elif adx_val > 25:
            strength = 60
        elif adx_val > 20:
            strength = 40
        else:
            strength = 0  # NO TREND - DON'T TRADE
        
        return {
            "bullish": plus_di > minus_di and adx_val > 25,
            "bearish": minus_di > plus_di and adx_val > 25,
            "value": adx_val,
            "strength": strength,
            "plus_di": plus_di,
            "minus_di": minus_di
        }

    @staticmethod
    def cci(data: List[Dict], index: int, period: int = 20) -> Dict:
        """Commodity Channel Index with Strength Score"""
        if index < period:
            return {
                "bullish": False,
                "bearish": False,
                "value": 0,
                "strength": 0
            }
        
        tp_list = [(d["high"] + d["low"] + d["close"]) / 3 for d in data[index - period + 1:index + 1]]
        sma_tp = sum(tp_list) / period
        tp = (data[index]["high"] + data[index]["low"] + data[index]["close"]) / 3
        
        mad = sum(abs(tp - sma_tp) for tp in tp_list) / period
        cci_val = (tp - sma_tp) / (0.015 * mad) if mad > 0 else 0
        
        # Strength: Based on CCI magnitude
        abs_cci = abs(cci_val)
        strength = 0
        if abs_cci > 200:
            strength = 100  # EXTREME
        elif abs_cci > 150:
            strength = 85
        elif abs_cci > 100:
            strength = 70
        else:
            strength = 30
        
        return {
            "bullish": cci_val > 100,
            "bearish": cci_val < -100,
            "value": cci_val,
            "strength": strength
        }

    @staticmethod
    def mfi(data: List[Dict], index: int, period: int = 14) -> Dict:
        """Money Flow Index with Strength Score"""
        if index < period:
            return {
                "bullish": False,
                "bearish": False,
                "value": 50,
                "strength": 0
            }
        
        pos_flow, neg_flow = 0, 0
        for i in range(index - period + 1, index + 1):
            tp = (data[i]["high"] + data[i]["low"] + data[i]["close"]) / 3
            prev_tp = (data[i - 1]["high"] + data[i - 1]["low"] + data[i - 1]["close"]) / 3
            mf = tp * data[i]["volume"]
            
            if tp > prev_tp:
                pos_flow += mf
            else:
                neg_flow += mf
        
        ratio = pos_flow / neg_flow if neg_flow > 0 else 100
        mfi_val = 100 - (100 / (1 + ratio))
        
        # Strength: Similar to RSI
        strength = 0
        if mfi_val < 20:
            strength = 90
        elif mfi_val < 30:
            strength = 70
        elif mfi_val > 80:
            strength = 90
        elif mfi_val > 70:
            strength = 70
        else:
            strength = 30
        
        return {
            "bullish": mfi_val < 30,
            "bearish": mfi_val > 70,
            "value": mfi_val,
            "strength": strength
        }

    @staticmethod
    def roc(data: List[Dict], index: int, period: int = 12) -> Dict:
        """Rate of Change with Strength Score"""
        if index < period:
            return {
                "bullish": False,
                "bearish": False,
                "value": 0,
                "strength": 0
            }
        
        prev_close = data[index - period]["close"]
        if prev_close == 0:
            return {
                "bullish": False,
                "bearish": False,
                "value": 0,
                "strength": 0
            }
        
        roc_val = ((data[index]["close"] - prev_close) / prev_close) * 100
        
        # Strength: Based on ROC magnitude
        abs_roc = abs(roc_val)
        strength = 0
        if abs_roc > 5:
            strength = 90  # STRONG MOMENTUM
        elif abs_roc > 3:
            strength = 70
        elif abs_roc > 1:
            strength = 50
        else:
            strength = 20
        
        return {
            "bullish": roc_val > 0,
            "bearish": roc_val < 0,
            "value": roc_val,
            "strength": strength
        }

    @staticmethod
    def vroc(data: List[Dict], index: int, period: int = 14) -> Dict:
        """Volume Rate of Change with Strength Score"""
        if index < period:
            return {
                "bullish": False,
                "bearish": False,
                "value": 0,
                "strength": 0
            }
        
        vroc_val = ((data[index]["volume"] - data[index - period]["volume"]) / data[index - period]["volume"]) * 100 if data[index - period]["volume"] > 0 else 0
        
        # Strength: Based on VROC
        abs_vroc = abs(vroc_val)
        strength = 0
        if abs_vroc > 50:
            strength = 90
        elif abs_vroc > 30:
            strength = 70
        else:
            strength = 30
        
        return {
            "bullish": vroc_val > 0,
            "bearish": vroc_val < 0,
            "value": vroc_val,
            "strength": strength
        }

    @staticmethod
    def rvi(data: List[Dict], index: int, period: int = 10) -> Dict:
        """Relative Vigor Index with Strength Score"""
        if index < period:
            return {
                "bullish": False,
                "bearish": False,
                "value": 50,
                "strength": 0
            }
        
        numerator, denominator = 0, 0
        for i in range(index - period + 1, index + 1):
            numerator += data[i]["close"] - data[i]["open"]
            denominator += data[i]["high"] - data[i]["low"]
        
        rvi_val = (numerator / denominator * 100) if denominator > 0 else 50
        
        # Strength
        strength = 0
        if rvi_val > 70:
            strength = 80
        elif rvi_val > 60:
            strength = 60
        elif rvi_val < 40:
            strength = 80
        elif rvi_val < 30:
            strength = 60
        else:
            strength = 30
        
        return {
            "bullish": rvi_val > 50,
            "bearish": rvi_val < 50,
            "value": rvi_val,
            "strength": strength
        }

    @staticmethod
    def donchian(data: List[Dict], index: int, period: int = 20) -> Dict:
        """Donchian Channel with Strength Score"""
        if index < period:
            return {
                "bullish": False,
                "bearish": False,
                "value": 0,
                "strength": 0
            }
        
        high = max(d["high"] for d in data[index - period + 1:index + 1])
        low = min(d["low"] for d in data[index - period + 1:index + 1])
        mid = (high + low) / 2
        
        # Strength: How far from middle
        distance = abs(data[index]["close"] - mid) / (high - low) if (high - low) > 0 else 0
        
        strength = 0
        if distance > 0.4:
            strength = 80  # Far from middle
        elif distance > 0.2:
            strength = 60
        else:
            strength = 30
        
        return {
            "bullish": data[index]["close"] > mid,
            "bearish": data[index]["close"] < mid,
            "value": mid,
            "strength": strength
        }

    @staticmethod
    def awesome_oscillator(data: List[Dict], index: int, fast: int = 5, slow: int = 34) -> Dict:
        """Awesome Oscillator with Strength Score"""
        if index < slow:
            return {
                "bullish": False,
                "bearish": False,
                "value": 0,
                "strength": 0
            }
        
        medians = [(d["high"] + d["low"]) / 2 for d in data[:index + 1]]
        fast_ma = sum(medians[index - fast + 1:index + 1]) / fast if index >= fast - 1 else 0
        slow_ma = sum(medians[index - slow + 1:index + 1]) / slow if index >= slow - 1 else 0
        
        ao_val = fast_ma - slow_ma
        prev_ao = 0
        if index > slow:
            prev_fast = sum(medians[index - fast:index]) / fast
            prev_slow = sum(medians[index - slow:index]) / slow
            prev_ao = prev_fast - prev_slow
        
        # Strength: AO momentum
        abs_ao = abs(ao_val)
        strength = 0
        if abs_ao > 0.5:
            strength = 90
        elif abs_ao > 0.2:
            strength = 70
        else:
            strength = 30
        
        return {
            "bullish": ao_val > 0 and ao_val > prev_ao,
            "bearish": ao_val < 0 and ao_val < prev_ao,
            "value": ao_val,
            "strength": strength
        }

    @staticmethod
    def momentum(data: List[Dict], index: int, period: int = 10) -> Dict:
        """Momentum with Strength Score"""
        if index < period:
            return {
                "bullish": False,
                "bearish": False,
                "value": 0,
                "strength": 0
            }
        
        momentum_val = data[index]["close"] - data[index - period]["close"]
        prev_momentum = data[index - 1]["close"] - data[index - 1 - period]["close"] if index > period else momentum_val
        
        # Strength: Momentum magnitude
        abs_mom = abs(momentum_val)
        strength = 0
        if abs_mom > 10:
            strength = 90
        elif abs_mom > 5:
            strength = 70
        else:
            strength = 30
        
        return {
            "bullish": momentum_val > 0 and momentum_val > prev_momentum,
            "bearish": momentum_val < 0 and momentum_val < prev_momentum,
            "value": momentum_val,
            "strength": strength
        }

    @staticmethod
    def atr(data: List[Dict], index: int, period: int = 14) -> float:
        """Average True Range"""
        if index < period:
            return 0
        
        tr_sum = 0
        for i in range(index - period + 1, index + 1):
            prev_close = data[i - 1]["close"] if i > 0 else data[i]["close"]
            tr = max(
                data[i]["high"] - data[i]["low"],
                abs(data[i]["high"] - prev_close),
                abs(data[i]["low"] - prev_close)
            )
            tr_sum += tr
        
        return tr_sum / period

    @staticmethod
    def pivot_points(data: List[Dict], index: int) -> Dict:
        """Pivot Points with Strength Score"""
        h = data[index]["high"]
        l = data[index]["low"]
        c = data[index]["close"]
        
        pivot = (h + l + c) / 3
        r1 = (2 * pivot) - l
        s1 = (2 * pivot) - h
        
        # Strength: Distance from pivot
        distance_to_r1 = abs(data[index]["close"] - r1) / pivot if pivot > 0 else 0
        distance_to_s1 = abs(data[index]["close"] - s1) / pivot if pivot > 0 else 0
        
        strength = 0
        if distance_to_r1 < 0.01 or distance_to_s1 < 0.01:
            strength = 90  # Close to R1 or S1
        else:
            strength = 50
        
        return {
            "bullish": data[index]["close"] > pivot,
            "bearish": data[index]["close"] < pivot,
            "value": pivot,
            "strength": strength
        }

    @staticmethod
    def obv(data: List[Dict], index: int) -> Dict:
        """On Balance Volume with Strength Score"""
        obv_val = 0
        for i in range(1, index + 1):
            if data[i]["close"] > data[i - 1]["close"]:
                obv_val += data[i]["volume"]
            elif data[i]["close"] < data[i - 1]["close"]:
                obv_val -= data[i]["volume"]
        
        prev_obv = 0
        if index > 1:
            for i in range(1, index):
                if data[i]["close"] > data[i - 1]["close"]:
                    prev_obv += data[i]["volume"]
                elif data[i]["close"] < data[i - 1]["close"]:
                    prev_obv -= data[i]["volume"]
        
        # Strength: OBV momentum
        obv_change = abs(obv_val - prev_obv)
        strength = 0
        if obv_change > 100000:
            strength = 90
        elif obv_change > 50000:
            strength = 70
        else:
            strength = 30
        
        return {
            "bullish": obv_val > prev_obv,
            "bearish": obv_val < prev_obv,
            "value": obv_val,
            "strength": strength
        }

    @staticmethod
    def supertrend(data: List[Dict], index: int, period: int = 10, multiplier: float = 3) -> Dict:
        """SuperTrend with Strength Score"""
        if index < period:
            return {
                "bullish": False,
                "bearish": False,
                "value": 0,
                "strength": 0
            }
        
        hl2 = (data[index]["high"] + data[index]["low"]) / 2
        atr_val = IndicatorCalculator.atr(data, index, period)
        
        basic_ub = hl2 + multiplier * atr_val
        basic_lb = hl2 - multiplier * atr_val
        
        final_ub = basic_ub
        final_lb = basic_lb
        
        if index > 0:
            prev_close = data[index - 1]["close"]
            if basic_ub < final_ub or prev_close > final_ub:
                final_ub = basic_ub
            if basic_lb > final_lb or prev_close < final_lb:
                final_lb = basic_lb
        
        supertrend_val = final_ub if data[index]["close"] <= final_ub else final_lb
        
        # Strength: Distance from SuperTrend
        distance = abs(data[index]["close"] - supertrend_val) / supertrend_val if supertrend_val > 0 else 0
        
        strength = 0
        if distance > 0.05:
            strength = 80
        elif distance > 0.02:
            strength = 60
        else:
            strength = 30
        
        return {
            "bullish": data[index]["close"] > supertrend_val,
            "bearish": data[index]["close"] < supertrend_val,
            "value": supertrend_val,
            "strength": strength
        }

    # ======================== CONVERGENCE DETECTION ========================
    
    @staticmethod
    def get_convergence_score(all_signals: Dict) -> Dict:
        """
        Calculate convergence score based on indicator agreements
        Groups indicators into categories and checks agreement
        
        Returns:
        {
            'bullish_score': 0-100,
            'bearish_score': 0-100,
            'confidence': 'STRONG' | 'MEDIUM' | 'WEAK',
            'category_details': {...}
        }
        """
        
        # Category 1: MOMENTUM (RSI, Stochastic, ROC, RVI, MFI)
        momentum_bullish = 0
        momentum_strength = 0
        momentum_count = 0
        
        for ind in ['RSI', 'Stochastic', 'ROC', 'RVI', 'MFI']:
            if ind in all_signals and all_signals[ind].get('bullish'):
                momentum_bullish += 1
                momentum_strength += all_signals[ind].get('strength', 50)
                momentum_count += 1
        
        momentum_bullish_pct = (momentum_bullish / momentum_count * 100) if momentum_count > 0 else 0
        momentum_strength_avg = momentum_strength / momentum_count if momentum_count > 0 else 0
        
        # Category 2: TREND (ADX, Supertrend, EMA_50, EMA_200, Donchian)
        trend_bullish = 0
        trend_strength = 0
        trend_count = 0
        
        for ind in ['ADX', 'SuperTrend', 'EMA_50', 'EMA_200', 'Donchian']:
            if ind in all_signals and all_signals[ind].get('bullish'):
                trend_bullish += 1
                trend_strength += all_signals[ind].get('strength', 50)
                trend_count += 1
        
        trend_bullish_pct = (trend_bullish / trend_count * 100) if trend_count > 0 else 0
        trend_strength_avg = trend_strength / trend_count if trend_count > 0 else 0
        
        # Category 3: VOLUME (Volume_MA, OBV, VROC)
        volume_bullish = 0
        volume_strength = 0
        volume_count = 0
        
        for ind in ['Volume_MA', 'OBV', 'VROC']:
            if ind in all_signals and all_signals[ind].get('bullish'):
                volume_bullish += 1
                volume_strength += all_signals[ind].get('strength', 50)
                volume_count += 1
        
        volume_bullish_pct = (volume_bullish / volume_count * 100) if volume_count > 0 else 0
        volume_strength_avg = volume_strength / volume_count if volume_count > 0 else 0
        
        # ==================== CONVERGENCE SCORE CALCULATION ====================
        
        # For BULLISH: All 3 categories agree = HIGH CONFIDENCE
        bullish_convergence = 0
        
        if momentum_bullish_pct >= 60:  # Momentum mostly bullish
            bullish_convergence += 30
        
        if trend_bullish_pct >= 60:  # Trend mostly bullish
            bullish_convergence += 30
        
        if volume_bullish_pct >= 60:  # Volume mostly bullish
            bullish_convergence += 20
        
        # Factor in strength
        avg_strength = (momentum_strength_avg + trend_strength_avg + volume_strength_avg) / 3
        strength_multiplier = avg_strength / 100
        bullish_score = bullish_convergence * strength_multiplier
        
        # ==================== BEARISH CONVERGENCE ====================
        
        bearish_convergence = 0
        momentum_bearish = momentum_count - momentum_bullish
        trend_bearish = trend_count - trend_bullish
        volume_bearish = volume_count - volume_bullish
        
        momentum_bearish_pct = (momentum_bearish / momentum_count * 100) if momentum_count > 0 else 0
        trend_bearish_pct = (trend_bearish / trend_count * 100) if trend_count > 0 else 0
        volume_bearish_pct = (volume_bearish / volume_count * 100) if volume_count > 0 else 0
        
        if momentum_bearish_pct >= 60:
            bearish_convergence += 30
        
        if trend_bearish_pct >= 60:
            bearish_convergence += 30
        
        if volume_bearish_pct >= 60:
            bearish_convergence += 20
        
        bearish_score = bearish_convergence * strength_multiplier
        
        # ==================== DETERMINE CONFIDENCE ====================
        
        max_score = max(bullish_score, bearish_score)
        confidence = 'WEAK'
        if max_score >= 75:
            confidence = 'STRONG'
        elif max_score >= 50:
            confidence = 'MEDIUM'
        
        return {
            'bullish_score': round(bullish_score, 1),
            'bearish_score': round(bearish_score, 1),
            'confidence': confidence,
            'category_details': {
                'momentum': {
                    'bullish_pct': round(momentum_bullish_pct, 1),
                    'strength': round(momentum_strength_avg, 1)
                },
                'trend': {
                    'bullish_pct': round(trend_bullish_pct, 1),
                    'strength': round(trend_strength_avg, 1)
                },
                'volume': {
                    'bullish_pct': round(volume_bullish_pct, 1),
                    'strength': round(volume_strength_avg, 1)
                }
            }
        }

    @staticmethod
    def get_all_signals(data: List[Dict], index: int) -> Dict[str, Dict]:
        """Get all indicator signals with Strength Scores"""
        return {
            "RSI": IndicatorCalculator.rsi(data, index),
            "MACD": IndicatorCalculator.macd(data, index),
            "Stochastic": IndicatorCalculator.stochastic(data, index),
            "Bollinger_Bands": IndicatorCalculator.bollinger_bands(data, index),
            "Volume_MA": IndicatorCalculator.volume_ma(data, index),
            "EMA_50": IndicatorCalculator.ema_50(data, index),
            "EMA_200": IndicatorCalculator.ema_200(data, index),
            "ADX": IndicatorCalculator.adx(data, index),
            "CCI": IndicatorCalculator.cci(data, index),
            "MFI": IndicatorCalculator.mfi(data, index),
            "ROC": IndicatorCalculator.roc(data, index),
            "VROC": IndicatorCalculator.vroc(data, index),
            "RVI": IndicatorCalculator.rvi(data, index),
            "Donchian": IndicatorCalculator.donchian(data, index),
            "Awesome_Oscillator": IndicatorCalculator.awesome_oscillator(data, index),
            "Momentum": IndicatorCalculator.momentum(data, index),
            "ATR": {
                "bullish": IndicatorCalculator.atr(data, index) > 0.5,
                "bearish": False,
                "value": IndicatorCalculator.atr(data, index),
                "strength": 50
            },
            "Pivot_Points": IndicatorCalculator.pivot_points(data, index),
            "OBV": IndicatorCalculator.obv(data, index),
            "SuperTrend": IndicatorCalculator.supertrend(data, index)
        }


# Pine Script code templates for indicators
PINE_CODES = {
    "RSI": """rsi_value = ta.rsi(close, 14)
rsi_bullish = rsi_value < 30
rsi_bearish = rsi_value > 70""",
    
    "MACD": """macd_line = ta.ema(close, 12) - ta.ema(close, 26)
macd_signal = ta.ema(macd_line, 9)
macd_bullish = macd_line > macd_signal
macd_bearish = macd_line < macd_signal""",
    
    "Stochastic": """k_value = ta.stoch(close, high, low, 14)
d_value = ta.sma(k_value, 3)
stoch_bullish = k_value < 20
stoch_bearish = k_value > 80""",
    
    "Bollinger_Bands": """basis = ta.sma(close, 20)
dev = ta.stdev(close, 20)
bb_upper = basis + dev * 2
bb_lower = basis - dev * 2
bb_bullish = close < bb_lower
bb_bearish = close > bb_upper""",
    
    "Volume_MA": """vol_ma = ta.sma(volume, 20)
vol_bullish = volume > vol_ma * 1.2
vol_bearish = volume < vol_ma * 0.8""",
    
    "EMA_50": """ema_50 = ta.ema(close, 50)
ema50_bullish = close > ema_50
ema50_bearish = close < ema_50""",
    
    "EMA_200": """ema_200 = ta.ema(close, 200)
ema200_bullish = close > ema_200
ema200_bearish = close < ema_200""",
    
    "ADX": """adx_value = ta.adx(14)
adx_bullish = adx_value > 25
adx_bearish = adx_value < 25""",
    
    "CCI": """cci_value = ta.cci(close, 20)
cci_bullish = cci_value < -100
cci_bearish = cci_value > 100""",
    
    "MFI": """mfi_value = ta.mfi(close, 14)
mfi_bullish = mfi_value < 20
mfi_bearish = mfi_value > 80""",
    
    "ROC": """roc_value = ta.roc(close, 12)
roc_bullish = roc_value > 0
roc_bearish = roc_value < 0""",
    
    "VROC": """vroc_value = ta.roc(volume, 12)
vroc_bullish = vroc_value > 0
vroc_bearish = vroc_value < 0""",
    
    "RVI": """rvi_value = ta.ema((close - close[1]).abs(), 10) / ta.ema((close - close[1]).abs(), 100)
rvi_bullish = rvi_value > 0.5
rvi_bearish = rvi_value < -0.5""",
    
    "Donchian": """donchian_high = ta.highest(high, 20)
donchian_low = ta.lowest(low, 20)
donchian_bullish = close > donchian_high * 0.95
donchian_bearish = close < donchian_low * 1.05""",
    
    "Awesome_Oscillator": """ao = ta.sma(hl2, 5) - ta.sma(hl2, 34)
ao_bullish = ao > 0
ao_bearish = ao < 0""",
    
    "Momentum": """momentum_value = close - close[10]
momentum_bullish = momentum_value > 0
momentum_bearish = momentum_value < 0""",
    
    "ATR": """atr_value = ta.atr(14)
atr_bullish = atr_value > 0.5
atr_bearish = atr_value < 0.5""",
    
    "Pivot_Points": """pivot = (high + low + close) / 3
r1 = pivot * 2 - low
s1 = pivot * 2 - high
pivot_bullish = close > pivot
pivot_bearish = close < pivot""",
    
    "OBV": """obv = ta.cum(ta.change(close) > 0 ? volume : -volume)
obv_bullish = obv > ta.sma(obv, 10)
obv_bearish = obv < ta.sma(obv, 10)""",
    
    "SuperTrend": """[supertrend, direction] = ta.supertrend(3, 10)
supertrend_bullish = direction > 0
supertrend_bearish = direction < 0"""
}


def get_pine_script_code(indicators: List[str]) -> str:
    """Generate Pine Script code from indicator list"""
    code = "// ======================== INDICATORS ========================\n"
    for ind in indicators:
        if ind in PINE_CODES:
            code += PINE_CODES[ind] + "\n\n"
    return code
