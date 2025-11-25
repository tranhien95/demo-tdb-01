/**
 * Trading Indicators Library
 * 20 Real Indicators with Bullish/Bearish Signals
 * Used by Combo Optimizer for backtesting
 */

class IndicatorCalculator {
    // RSI (Relative Strength Index)
    static RSI(data, index, period = 14) {
        if (index < period) return { bullish: false, bearish: false, value: 50 };
        
        let gains = 0, losses = 0;
        for (let i = index - period + 1; i <= index; i++) {
            const change = data[i].close - data[i - 1].close;
            if (change > 0) gains += change;
            else losses -= change;
        }
        
        const avgGain = gains / period;
        const avgLoss = losses / period;
        const rs = avgLoss === 0 ? 100 : avgGain / avgLoss;
        const rsi = 100 - (100 / (1 + rs));
        
        return {
            bullish: rsi < 30,  // Oversold
            bearish: rsi > 70,  // Overbought
            value: rsi
        };
    }

    // MACD (Moving Average Convergence Divergence)
    static MACD(data, index, fast = 12, slow = 26, signal = 9) {
        if (index < slow) return { bullish: false, bearish: false, value: 0 };
        
        const emaFast = this.EMA(data, index, fast);
        const emaSlow = this.EMA(data, index, slow);
        const macdLine = emaFast - emaSlow;
        
        const signalLine = this.EMAValue(data, index, signal, macdLine);
        const histogram = macdLine - signalLine;
        
        return {
            bullish: macdLine > signalLine && histogram > 0,
            bearish: macdLine < signalLine && histogram < 0,
            value: macdLine
        };
    }

    // Stochastic Oscillator
    static Stochastic(data, index, period = 14, smoothK = 3, smoothD = 3) {
        if (index < period) return { bullish: false, bearish: false, value: 50 };
        
        let high = -Infinity, low = Infinity;
        for (let i = index - period + 1; i <= index; i++) {
            high = Math.max(high, data[i].high);
            low = Math.min(low, data[i].low);
        }
        
        const k = (data[index].close - low) / (high - low) * 100;
        
        return {
            bullish: k < 20,    // Oversold
            bearish: k > 80,    // Overbought
            value: k
        };
    }

    // Bollinger Bands
    static BollingerBands(data, index, period = 20, stdDev = 2) {
        if (index < period) return { bullish: false, bearish: false, value: 0 };
        
        const sma = this.SMA(data, index, period);
        let variance = 0;
        
        for (let i = index - period + 1; i <= index; i++) {
            variance += Math.pow(data[i].close - sma, 2);
        }
        variance /= period;
        
        const std = Math.sqrt(variance);
        const upper = sma + (std * stdDev);
        const lower = sma - (std * stdDev);
        
        return {
            bullish: data[index].close < lower,   // Touched lower band
            bearish: data[index].close > upper,   // Touched upper band
            value: sma
        };
    }

    // Volume Moving Average
    static VolumeMA(data, index, period = 20) {
        if (index < period) return { bullish: false, bearish: false, value: 0 };
        
        const volMA = this.SMA(data, index, period, 'volume');
        const bullish = data[index].volume > volMA * 1.2;
        const bearish = data[index].volume < volMA * 0.8;
        
        return {
            bullish: bullish,
            bearish: bearish,
            value: volMA
        };
    }

    // EMA 50
    static EMA_50(data, index) {
        const ema = this.EMA(data, index, 50);
        return {
            bullish: data[index].close > ema,
            bearish: data[index].close < ema,
            value: ema
        };
    }

    // EMA 200
    static EMA_200(data, index) {
        const ema = this.EMA(data, index, 200);
        return {
            bullish: data[index].close > ema,
            bearish: data[index].close < ema,
            value: ema
        };
    }

    // ADX (Average Directional Index)
    static ADX(data, index, period = 14) {
        if (index < period * 2) return { bullish: false, bearish: false, value: 0 };
        
        let plusDM = 0, minusDM = 0;
        for (let i = index - period + 1; i <= index; i++) {
            const upMove = data[i].high - data[i - 1].high;
            const downMove = data[i - 1].low - data[i].low;
            
            if (upMove > downMove && upMove > 0) plusDM += upMove;
            if (downMove > upMove && downMove > 0) minusDM += downMove;
        }
        
        const plusDI = (plusDM / this.ATR(data, index, period)) * 100;
        const minusDI = (minusDM / this.ATR(data, index, period)) * 100;
        const adx = Math.abs(plusDI - minusDI) / (plusDI + minusDI) * 100 || 0;
        
        return {
            bullish: plusDI > minusDI && adx > 25,
            bearish: minusDI > plusDI && adx > 25,
            value: adx
        };
    }

    // CCI (Commodity Channel Index)
    static CCI(data, index, period = 20) {
        if (index < period) return { bullish: false, bearish: false, value: 0 };
        
        let typicalPrice = 0, sumTP = 0;
        for (let i = index - period + 1; i <= index; i++) {
            const tp = (data[i].high + data[i].low + data[i].close) / 3;
            sumTP += tp;
        }
        
        const smaTP = sumTP / period;
        typicalPrice = (data[index].high + data[index].low + data[index].close) / 3;
        
        let meanDev = 0;
        for (let i = index - period + 1; i <= index; i++) {
            const tp = (data[i].high + data[i].low + data[i].close) / 3;
            meanDev += Math.abs(tp - smaTP);
        }
        meanDev /= period;
        
        const cci = meanDev === 0 ? 0 : (typicalPrice - smaTP) / (0.015 * meanDev);
        
        return {
            bullish: cci > 100,
            bearish: cci < -100,
            value: cci
        };
    }

    // MFI (Money Flow Index)
    static MFI(data, index, period = 14) {
        if (index < period) return { bullish: false, bearish: false, value: 50 };
        
        let posMoneyFlow = 0, negMoneyFlow = 0;
        
        for (let i = index - period + 1; i <= index; i++) {
            const typicalPrice = (data[i].high + data[i].low + data[i].close) / 3;
            const prevTP = (data[i - 1].high + data[i - 1].low + data[i - 1].close) / 3;
            const moneyFlow = typicalPrice * data[i].volume;
            
            if (typicalPrice > prevTP) {
                posMoneyFlow += moneyFlow;
            } else {
                negMoneyFlow += moneyFlow;
            }
        }
        
        const moneyRatio = negMoneyFlow === 0 ? 100 : posMoneyFlow / negMoneyFlow;
        const mfi = 100 - (100 / (1 + moneyRatio));
        
        return {
            bullish: mfi < 30,
            bearish: mfi > 70,
            value: mfi
        };
    }

    // ROC (Rate of Change)
    static ROC(data, index, period = 12) {
        if (index < period) return { bullish: false, bearish: false, value: 0 };
        
        const roc = ((data[index].close - data[index - period].close) / data[index - period].close) * 100;
        
        return {
            bullish: roc > 0,
            bearish: roc < 0,
            value: roc
        };
    }

    // VROC (Volume Rate of Change)
    static VROC(data, index, period = 14) {
        if (index < period) return { bullish: false, bearish: false, value: 0 };
        
        const vroc = ((data[index].volume - data[index - period].volume) / data[index - period].volume) * 100;
        
        return {
            bullish: vroc > 0,
            bearish: vroc < 0,
            value: vroc
        };
    }

    // RVI (Relative Vigor Index)
    static RVI(data, index, period = 10) {
        if (index < period) return { bullish: false, bearish: false, value: 50 };
        
        let numerator = 0, denominator = 0;
        
        for (let i = index - period + 1; i <= index; i++) {
            const num = (data[i].close - data[i].open);
            const den = (data[i].high - data[i].low);
            numerator += num;
            denominator += den;
        }
        
        const rvi = denominator === 0 ? 50 : 100 * (numerator / denominator);
        
        return {
            bullish: rvi > 50,
            bearish: rvi < 50,
            value: rvi
        };
    }

    // Donchian Channel
    static Donchian(data, index, period = 20) {
        if (index < period) return { bullish: false, bearish: false, value: 0 };
        
        let high = -Infinity, low = Infinity;
        for (let i = index - period + 1; i <= index; i++) {
            high = Math.max(high, data[i].high);
            low = Math.min(low, data[i].low);
        }
        
        const mid = (high + low) / 2;
        
        return {
            bullish: data[index].close > mid,
            bearish: data[index].close < mid,
            value: mid
        };
    }

    // Awesome Oscillator
    static AwesomeOscillator(data, index, fast = 5, slow = 34) {
        if (index < slow) return { bullish: false, bearish: false, value: 0 };
        
        const fastMA = this.SMA(data, index, fast, 'medianPrice');
        const slowMA = this.SMA(data, index, slow, 'medianPrice');
        const ao = fastMA - slowMA;
        const prevAO = index > slow ? this.SMA(data, index - 1, fast, 'medianPrice') - this.SMA(data, index - 1, slow, 'medianPrice') : ao;
        
        return {
            bullish: ao > 0 && ao > prevAO,
            bearish: ao < 0 && ao < prevAO,
            value: ao
        };
    }

    // Momentum
    static Momentum(data, index, period = 10) {
        if (index < period) return { bullish: false, bearish: false, value: 0 };
        
        const momentum = data[index].close - data[index - period].close;
        const prevMomentum = index > period ? data[index - 1].close - data[index - 1 - period].close : momentum;
        
        return {
            bullish: momentum > 0 && momentum > prevMomentum,
            bearish: momentum < 0 && momentum < prevMomentum,
            value: momentum
        };
    }

    // ATR (Average True Range)
    static ATR(data, index, period = 14) {
        if (index < period) return 0;
        
        let trSum = 0;
        for (let i = index - period + 1; i <= index; i++) {
            const prevClose = i > 0 ? data[i - 1].close : data[i].close;
            const tr = Math.max(
                data[i].high - data[i].low,
                Math.abs(data[i].high - prevClose),
                Math.abs(data[i].low - prevClose)
            );
            trSum += tr;
        }
        
        return trSum / period;
    }

    // Pivot Points
    static PivotPoints(data, index) {
        const h = data[index].high;
        const l = data[index].low;
        const c = data[index].close;
        
        const pivot = (h + l + c) / 3;
        const r1 = (2 * pivot) - l;
        const s1 = (2 * pivot) - h;
        
        return {
            bullish: data[index].close > pivot,
            bearish: data[index].close < pivot,
            value: pivot
        };
    }

    // OBV (On Balance Volume)
    static OBV(data, index) {
        let obv = 0;
        
        for (let i = 1; i <= index; i++) {
            if (data[i].close > data[i - 1].close) {
                obv += data[i].volume;
            } else if (data[i].close < data[i - 1].close) {
                obv -= data[i].volume;
            }
        }
        
        const prevOBV = index > 1 ? (() => {
            let prev = 0;
            for (let i = 1; i < index; i++) {
                if (data[i].close > data[i - 1].close) {
                    prev += data[i].volume;
                } else if (data[i].close < data[i - 1].close) {
                    prev -= data[i].volume;
                }
            }
            return prev;
        })() : obv;
        
        return {
            bullish: obv > prevOBV,
            bearish: obv < prevOBV,
            value: obv
        };
    }

    // SuperTrend
    static SuperTrend(data, index, period = 10, multiplier = 3) {
        if (index < period) return { bullish: false, bearish: false, value: 0 };
        
        const atr = this.ATR(data, index, period);
        const hl2 = (data[index].high + data[index].low) / 2;
        
        const basic_ub = hl2 + multiplier * atr;
        const basic_lb = hl2 - multiplier * atr;
        
        let final_ub = basic_ub;
        let final_lb = basic_lb;
        
        if (index > 0) {
            const prevData = data[index - 1];
            const prevHl2 = (prevData.high + prevData.low) / 2;
            const prevAtr = this.ATR(data, index - 1, period);
            const prevBasicUb = prevHl2 + multiplier * prevAtr;
            const prevBasicLb = prevHl2 - multiplier * prevAtr;
            
            final_ub = (basic_ub < final_ub || prevData.close > final_ub) ? basic_ub : final_ub;
            final_lb = (basic_lb > final_lb || prevData.close < final_lb) ? basic_lb : final_lb;
        }
        
        const supertrend = data[index].close <= final_ub ? final_ub : final_lb;
        
        return {
            bullish: data[index].close > supertrend,
            bearish: data[index].close < supertrend,
            value: supertrend
        };
    }

    // Helper: SMA (Simple Moving Average)
    static SMA(data, index, period, type = 'close') {
        if (index < period - 1) return 0;
        
        let sum = 0;
        for (let i = index - period + 1; i <= index; i++) {
            if (type === 'volume') {
                sum += data[i].volume;
            } else if (type === 'medianPrice') {
                sum += (data[i].high + data[i].low) / 2;
            } else {
                sum += data[i].close;
            }
        }
        return sum / period;
    }

    // Helper: EMA (Exponential Moving Average)
    static EMA(data, index, period) {
        if (index < period - 1) return data[index].close;
        
        const multiplier = 2 / (period + 1);
        let ema = 0;
        
        if (index === period - 1) {
            for (let i = 0; i < period; i++) {
                ema += data[i].close;
            }
            ema /= period;
        } else {
            const prevEMA = this.EMA(data, index - 1, period);
            ema = data[index].close * multiplier + prevEMA * (1 - multiplier);
        }
        
        return ema;
    }

    // Helper: Get EMA value at specific index
    static EMAValue(data, index, period, valueArray) {
        if (index < period - 1) return valueArray[0];
        
        const multiplier = 2 / (period + 1);
        let ema = valueArray[0];
        
        for (let i = 1; i <= index; i++) {
            ema = valueArray[i] * multiplier + ema * (1 - multiplier);
        }
        
        return ema;
    }

    // Get all indicator signals for a candle
    static getAllSignals(data, index) {
        return {
            RSI: this.RSI(data, index),
            Stochastic: this.Stochastic(data, index),
            MACD: this.MACD(data, index),
            Bollinger_Bands: this.BollingerBands(data, index),
            Volume_MA: this.VolumeMA(data, index),
            EMA_50: this.EMA_50(data, index),
            EMA_200: this.EMA_200(data, index),
            ADX: this.ADX(data, index),
            CCI: this.CCI(data, index),
            MFI: this.MFI(data, index),
            ROC: this.ROC(data, index),
            VROC: this.VROC(data, index),
            RVI: this.RVI(data, index),
            Donchian: this.Donchian(data, index),
            Awesome_Oscillator: this.AwesomeOscillator(data, index),
            Momentum: this.Momentum(data, index),
            ATR: { bullish: this.ATR(data, index) > 0.5, bearish: false, value: this.ATR(data, index) },
            Pivot_Points: this.PivotPoints(data, index),
            OBV: this.OBV(data, index),
            SuperTrend: this.SuperTrend(data, index)
        };
    }
}

// Export for use in HTML
if (typeof module !== 'undefined' && module.exports) {
    module.exports = IndicatorCalculator;
}
