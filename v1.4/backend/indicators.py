"""
Trading Indicators Library v1.4
Technical Indicators with Bullish/Bearish Signals
"""

from typing import List, Dict, Optional
import math


class IndicatorCalculator:
    """Calculate technical indicators for trading strategy backtesting"""

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

    @staticmethod
    def rsi(data: List[Dict], index: int, period: int = 14) -> Dict:
        """Relative Strength Index"""
        if index < period:
            return {"bullish": False, "bearish": False, "value": 50, "strength": 0}
        
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
        
        return {
            "bullish": rsi_val < 30,
            "bearish": rsi_val > 70,
            "value": rsi_val,
            "strength": abs(50 - rsi_val) / 50 * 100
        }

    @staticmethod
    def macd(data: List[Dict], index: int, fast: int = 12, slow: int = 26, signal: int = 9) -> Dict:
        """MACD - Moving Average Convergence Divergence"""
        if index < slow:
            return {"bullish": False, "bearish": False, "value": 0, "strength": 0}
        
        closes = [d["close"] for d in data[:index + 1]]
        ema_fast = IndicatorCalculator.ema(closes, fast)
        ema_slow = IndicatorCalculator.ema(closes, slow)
        
        macd_line = (ema_fast[index] or 0) - (ema_slow[index] or 0)
        
        macd_vals = []
        for i in range(len(closes)):
            if ema_fast[i] and ema_slow[i]:
                macd_vals.append(ema_fast[i] - ema_slow[i])
            else:
                macd_vals.append(None)
        
        signal_line_vals = IndicatorCalculator.ema([v for v in macd_vals if v is not None], signal)
        signal_val = signal_line_vals[-1] if signal_line_vals and signal_line_vals[-1] is not None else 0
        histogram = macd_line - signal_val
        
        return {
            "bullish": macd_line > signal_val and histogram > 0,
            "bearish": macd_line < signal_val and histogram < 0,
            "value": macd_line,
            "strength": abs(histogram) * 10
        }

    @staticmethod
    def stochastic(data: List[Dict], index: int, period: int = 14) -> Dict:
        """Stochastic Oscillator"""
        if index < period:
            return {"bullish": False, "bearish": False, "value": 50, "strength": 0}
        
        high = max(d["high"] for d in data[index - period + 1:index + 1])
        low = min(d["low"] for d in data[index - period + 1:index + 1])
        k = ((data[index]["close"] - low) / (high - low) * 100) if (high - low) != 0 else 50
        
        return {
            "bullish": k < 20,
            "bearish": k > 80,
            "value": k,
            "strength": abs(50 - k) / 50 * 100
        }

    @staticmethod
    def bollinger_bands(data: List[Dict], index: int, period: int = 20, std_dev: int = 2) -> Dict:
        """Bollinger Bands"""
        if index < period:
            return {"bullish": False, "bearish": False, "value": 0, "strength": 0}
        
        closes = [d["close"] for d in data[index - period + 1:index + 1]]
        mean = sum(closes) / period
        variance = sum((x - mean) ** 2 for x in closes) / period
        std = math.sqrt(variance)
        
        upper = mean + std_dev * std
        lower = mean - std_dev * std
        
        return {
            "bullish": data[index]["close"] < lower,
            "bearish": data[index]["close"] > upper,
            "value": mean,
            "strength": 50
        }

    @staticmethod
    def volume_ma(data: List[Dict], index: int, period: int = 20) -> Dict:
        """Volume Moving Average"""
        if index < period:
            return {"bullish": False, "bearish": False, "value": 0, "strength": 0}
        
        vol_ma = sum(d["volume"] for d in data[index - period + 1:index + 1]) / period
        
        return {
            "bullish": data[index]["volume"] > vol_ma * 1.2,
            "bearish": data[index]["volume"] < vol_ma * 0.8,
            "value": vol_ma,
            "strength": abs(data[index]["volume"] - vol_ma) / vol_ma * 100
        }

    @staticmethod
    def ema_signal(data: List[Dict], index: int, period: int) -> Dict:
        """Generic EMA Signal"""
        closes = [d["close"] for d in data[:index + 1]]
        ema_vals = IndicatorCalculator.ema(closes, period)
        ema_val = ema_vals[index] if ema_vals[index] is not None else data[index]["close"]
        
        return {
            "bullish": data[index]["close"] > ema_val,
            "bearish": data[index]["close"] < ema_val,
            "value": ema_val,
            "strength": abs(data[index]["close"] - ema_val) / ema_val * 100
        }

    @staticmethod
    def ema_50(data: List[Dict], index: int) -> Dict:
        return IndicatorCalculator.ema_signal(data, index, 50)

    @staticmethod
    def ema_200(data: List[Dict], index: int) -> Dict:
        return IndicatorCalculator.ema_signal(data, index, 200)

    @staticmethod
    def ema_12(data: List[Dict], index: int) -> Dict:
        return IndicatorCalculator.ema_signal(data, index, 12)

    @staticmethod
    def ema_26(data: List[Dict], index: int) -> Dict:
        return IndicatorCalculator.ema_signal(data, index, 26)

    @staticmethod
    def adx(data: List[Dict], index: int, period: int = 14) -> Dict:
        """Average Directional Index"""
        if index < period * 2:
            return {"bullish": False, "bearish": False, "value": 0, "strength": 0}
        
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
        
        return {
            "bullish": plus_di > minus_di and adx_val > 25,
            "bearish": minus_di > plus_di and adx_val > 25,
            "value": adx_val,
            "strength": adx_val
        }

    @staticmethod
    def cci(data: List[Dict], index: int, period: int = 20) -> Dict:
        """Commodity Channel Index"""
        if index < period:
            return {"bullish": False, "bearish": False, "value": 0, "strength": 0}
        
        tp_list = [(d["high"] + d["low"] + d["close"]) / 3 for d in data[index - period + 1:index + 1]]
        sma_tp = sum(tp_list) / period
        tp = (data[index]["high"] + data[index]["low"] + data[index]["close"]) / 3
        
        mad = sum(abs(tp - sma_tp) for tp in tp_list) / period
        cci_val = (tp - sma_tp) / (0.015 * mad) if mad > 0 else 0
        
        return {
            "bullish": cci_val > 100,
            "bearish": cci_val < -100,
            "value": cci_val,
            "strength": abs(cci_val) / 200 * 100
        }

    @staticmethod
    def mfi(data: List[Dict], index: int, period: int = 14) -> Dict:
        """Money Flow Index"""
        if index < period:
            return {"bullish": False, "bearish": False, "value": 50, "strength": 0}
        
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
        
        return {
            "bullish": mfi_val < 30,
            "bearish": mfi_val > 70,
            "value": mfi_val,
            "strength": abs(50 - mfi_val) / 50 * 100
        }

    @staticmethod
    def roc(data: List[Dict], index: int, period: int = 12) -> Dict:
        """Rate of Change"""
        if index < period:
            return {"bullish": False, "bearish": False, "value": 0, "strength": 0}
        
        prev_close = data[index - period]["close"]
        if prev_close == 0:
            return {"bullish": False, "bearish": False, "value": 0, "strength": 0}
        
        roc_val = ((data[index]["close"] - prev_close) / prev_close) * 100
        
        return {
            "bullish": roc_val > 0,
            "bearish": roc_val < 0,
            "value": roc_val,
            "strength": abs(roc_val)
        }

    @staticmethod
    def vroc(data: List[Dict], index: int, period: int = 14) -> Dict:
        """Volume Rate of Change"""
        if index < period:
            return {"bullish": False, "bearish": False, "value": 0, "strength": 0}
        
        vroc_val = ((data[index]["volume"] - data[index - period]["volume"]) / data[index - period]["volume"]) * 100 if data[index - period]["volume"] > 0 else 0
        
        return {
            "bullish": vroc_val > 0,
            "bearish": vroc_val < 0,
            "value": vroc_val,
            "strength": abs(vroc_val)
        }

    @staticmethod
    def rvi(data: List[Dict], index: int, period: int = 10) -> Dict:
        """Relative Vigor Index"""
        if index < period:
            return {"bullish": False, "bearish": False, "value": 50, "strength": 0}
        
        numerator, denominator = 0, 0
        for i in range(index - period + 1, index + 1):
            numerator += data[i]["close"] - data[i]["open"]
            denominator += data[i]["high"] - data[i]["low"]
        
        rvi_val = (numerator / denominator * 100) if denominator > 0 else 50
        
        return {
            "bullish": rvi_val > 50,
            "bearish": rvi_val < 50,
            "value": rvi_val,
            "strength": abs(50 - rvi_val) / 50 * 100
        }

    @staticmethod
    def donchian(data: List[Dict], index: int, period: int = 20) -> Dict:
        """Donchian Channel"""
        if index < period:
            return {"bullish": False, "bearish": False, "value": 0, "strength": 0}
        
        high = max(d["high"] for d in data[index - period + 1:index + 1])
        low = min(d["low"] for d in data[index - period + 1:index + 1])
        mid = (high + low) / 2
        
        return {
            "bullish": data[index]["close"] > mid,
            "bearish": data[index]["close"] < mid,
            "value": mid,
            "strength": 50
        }

    @staticmethod
    def awesome_oscillator(data: List[Dict], index: int, fast: int = 5, slow: int = 34) -> Dict:
        """Awesome Oscillator"""
        if index < slow:
            return {"bullish": False, "bearish": False, "value": 0, "strength": 0}
        
        medians = [(d["high"] + d["low"]) / 2 for d in data[:index + 1]]
        fast_ma = sum(medians[index - fast + 1:index + 1]) / fast if index >= fast - 1 else 0
        slow_ma = sum(medians[index - slow + 1:index + 1]) / slow if index >= slow - 1 else 0
        
        ao_val = fast_ma - slow_ma
        prev_ao = 0
        if index > slow:
            prev_fast = sum(medians[index - fast:index]) / fast
            prev_slow = sum(medians[index - slow:index]) / slow
            prev_ao = prev_fast - prev_slow
        
        return {
            "bullish": ao_val > 0 and ao_val > prev_ao,
            "bearish": ao_val < 0 and ao_val < prev_ao,
            "value": ao_val,
            "strength": abs(ao_val) * 10
        }

    @staticmethod
    def momentum(data: List[Dict], index: int, period: int = 10) -> Dict:
        """Momentum"""
        if index < period:
            return {"bullish": False, "bearish": False, "value": 0, "strength": 0}
        
        momentum_val = data[index]["close"] - data[index - period]["close"]
        prev_momentum = data[index - 1]["close"] - data[index - 1 - period]["close"] if index > period else momentum_val
        
        return {
            "bullish": momentum_val > 0 and momentum_val > prev_momentum,
            "bearish": momentum_val < 0 and momentum_val < prev_momentum,
            "value": momentum_val,
            "strength": abs(momentum_val) / data[index]["close"] * 100
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
        """Pivot Points"""
        h = data[index]["high"]
        l = data[index]["low"]
        c = data[index]["close"]
        
        pivot = (h + l + c) / 3
        
        return {
            "bullish": data[index]["close"] > pivot,
            "bearish": data[index]["close"] < pivot,
            "value": pivot,
            "strength": 50
        }

    @staticmethod
    def obv(data: List[Dict], index: int) -> Dict:
        """On Balance Volume"""
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
        
        return {
            "bullish": obv_val > prev_obv,
            "bearish": obv_val < prev_obv,
            "value": obv_val,
            "strength": 50
        }

    @staticmethod
    def supertrend(data: List[Dict], index: int, period: int = 10, multiplier: float = 3) -> Dict:
        """SuperTrend"""
        if index < period:
            return {"bullish": False, "bearish": False, "value": 0, "strength": 0}
        
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
        
        return {
            "bullish": data[index]["close"] > supertrend_val,
            "bearish": data[index]["close"] < supertrend_val,
            "value": supertrend_val,
            "strength": 50
        }

    @staticmethod
    def get_all_signals(data: List[Dict], index: int) -> Dict[str, Dict]:
        """Get all indicator signals for a candle"""
        return {
            "RSI": IndicatorCalculator.rsi(data, index),
            "MACD": IndicatorCalculator.macd(data, index),
            "Stochastic": IndicatorCalculator.stochastic(data, index),
            "Bollinger_Bands": IndicatorCalculator.bollinger_bands(data, index),
            "Volume_MA": IndicatorCalculator.volume_ma(data, index),
            "EMA_50": IndicatorCalculator.ema_50(data, index),
            "EMA_200": IndicatorCalculator.ema_200(data, index),
            "EMA_12": IndicatorCalculator.ema_12(data, index),
            "EMA_26": IndicatorCalculator.ema_26(data, index),
            "ADX": IndicatorCalculator.adx(data, index),
            "CCI": IndicatorCalculator.cci(data, index),
            "MFI": IndicatorCalculator.mfi(data, index),
            "ROC": IndicatorCalculator.roc(data, index),
            "VROC": IndicatorCalculator.vroc(data, index),
            "RVI": IndicatorCalculator.rvi(data, index),
            "Donchian": IndicatorCalculator.donchian(data, index),
            "Awesome_Oscillator": IndicatorCalculator.awesome_oscillator(data, index),
            "Momentum": IndicatorCalculator.momentum(data, index),
            "ATR": {"bullish": IndicatorCalculator.atr(data, index) > 0.5, "bearish": False, "value": IndicatorCalculator.atr(data, index), "strength": 0},
            "Pivot_Points": IndicatorCalculator.pivot_points(data, index),
            "OBV": IndicatorCalculator.obv(data, index),
            "SuperTrend": IndicatorCalculator.supertrend(data, index)
        }


PINE_CODES = {
    "RSI": """rsi_value = ta.rsi(close, 14)
rsi_bullish = rsi_value < 30
rsi_bearish = rsi_value > 70""",
    
    "MACD": """[macd_line, signal_line, _] = ta.macd(close, 12, 26, 9)
macd_bullish = macd_line > signal_line
macd_bearish = macd_line < signal_line""",
    
    "Stochastic": """k_value = ta.stoch(close, high, low, 14)
stoch_bullish = k_value < 20
stoch_bearish = k_value > 80""",
    
    "EMA_50": """ema_50 = ta.ema(close, 50)
ema50_bullish = close > ema_50
ema50_bearish = close < ema_50""",
    
    "EMA_200": """ema_200 = ta.ema(close, 200)
ema200_bullish = close > ema_200
ema200_bearish = close < ema_200""",
    
    "EMA_12": """ema_12 = ta.ema(close, 12)
ema12_bullish = close > ema_12
ema12_bearish = close < ema_12""",
    
    "EMA_26": """ema_26 = ta.ema(close, 26)
ema26_bullish = close > ema_26
ema26_bearish = close < ema_26""",
}


def get_pine_script_code(indicators: List[str]) -> str:
    """Generate Pine Script code from indicator list"""
    code = "// ======================== INDICATORS ========================\n"
    for ind in indicators:
        if ind in PINE_CODES:
            code += PINE_CODES[ind] + "\n\n"
        else:
            code += f"// {ind} indicator\n\n"
    return code
