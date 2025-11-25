/**
 * Indicators Library - 20 Technical Indicators
 * Used by Combo Optimizer for backtesting and Pine Script generation
 */

const IndicatorsLibrary = {
    // RSI - Relative Strength Index
    RSI: {
        calculate: (data, period = 14) => {
            const rsi = [];
            for (let i = 0; i < data.length; i++) {
                if (i < period) {
                    rsi.push(null);
                    continue;
                }
                let gains = 0, losses = 0;
                for (let j = i - period + 1; j <= i; j++) {
                    const diff = data[j].close - data[j - 1].close;
                    if (diff > 0) gains += diff;
                    else losses -= diff;
                }
                const rs = (gains / period) / (losses / period);
                rsi.push(100 - (100 / (1 + rs)));
            }
            return rsi;
        },
        pineCode: `rsi_value = ta.rsi(close, 14)
rsi_bullish = rsi_value < 70
rsi_bearish = rsi_value > 30`
    },

    // MACD - Moving Average Convergence Divergence
    MACD: {
        calculate: (data, fast = 12, slow = 26) => {
            const ema12 = IndicatorsLibrary._ema(data.map(d => d.close), fast);
            const ema26 = IndicatorsLibrary._ema(data.map(d => d.close), slow);
            return ema12.map((v, i) => v && ema26[i] ? v - ema26[i] : null);
        },
        pineCode: `macd_line = ta.ema(close, 12) - ta.ema(close, 26)
macd_signal = ta.ema(macd_line, 9)
macd_bullish = macd_line > macd_signal
macd_bearish = macd_line < macd_signal`
    },

    // Stochastic Oscillator
    Stochastic: {
        calculate: (data, period = 14) => {
            const stoch = [];
            for (let i = 0; i < data.length; i++) {
                if (i < period - 1) {
                    stoch.push(null);
                    continue;
                }
                const high = Math.max(...data.slice(i - period + 1, i + 1).map(d => d.high));
                const low = Math.min(...data.slice(i - period + 1, i + 1).map(d => d.low));
                stoch.push(((data[i].close - low) / (high - low)) * 100);
            }
            return stoch;
        },
        pineCode: `k_value = ta.stoch(close, high, low, 14)
d_value = ta.sma(k_value, 3)
stoch_bullish = k_value < 20
stoch_bearish = k_value > 80`
    },

    // Bollinger Bands
    Bollinger_Bands: {
        calculate: (data, period = 20, stdDev = 2) => {
            const closes = data.map(d => d.close);
            const sma = IndicatorsLibrary._sma(closes, period);
            const bb = [];
            for (let i = 0; i < data.length; i++) {
                if (i < period - 1) {
                    bb.push(null);
                    continue;
                }
                const slice = closes.slice(i - period + 1, i + 1);
                const mean = sma[i];
                const variance = slice.reduce((sum, v) => sum + Math.pow(v - mean, 2), 0) / period;
                const std = Math.sqrt(variance);
                bb.push({ upper: mean + stdDev * std, lower: mean - stdDev * std, mid: mean });
            }
            return bb;
        },
        pineCode: `basis = ta.sma(close, 20)
dev = ta.stdev(close, 20)
bb_upper = basis + dev * 2
bb_lower = basis - dev * 2
bb_bullish = close < bb_lower
bb_bearish = close > bb_upper`
    },

    // Volume Moving Average
    Volume_MA: {
        calculate: (data, period = 20) => {
            return IndicatorsLibrary._sma(data.map(d => d.volume), period);
        },
        pineCode: `vol_ma = ta.sma(volume, 20)
vol_bullish = volume > vol_ma * 1.2
vol_bearish = volume < vol_ma * 0.8`
    },

    // EMA 50
    EMA_50: {
        calculate: (data) => IndicatorsLibrary._ema(data.map(d => d.close), 50),
        pineCode: `ema_50 = ta.ema(close, 50)
ema50_bullish = close > ema_50
ema50_bearish = close < ema_50`
    },

    // EMA 200
    EMA_200: {
        calculate: (data) => IndicatorsLibrary._ema(data.map(d => d.close), 200),
        pineCode: `ema_200 = ta.ema(close, 200)
ema200_bullish = close > ema_200
ema200_bearish = close < ema_200`
    },

    // ADX - Average Directional Index
    ADX: {
        calculate: (data, period = 14) => {
            const adx = [];
            for (let i = 0; i < data.length; i++) {
                if (i < period) {
                    adx.push(null);
                    continue;
                }
                let plus = 0, minus = 0;
                for (let j = i - period + 1; j <= i; j++) {
                    const upMove = data[j].high - data[j - 1].high;
                    const downMove = data[j - 1].low - data[j].low;
                    if (upMove > downMove && upMove > 0) plus += upMove;
                    if (downMove > upMove && downMove > 0) minus += downMove;
                }
                adx.push(plus > minus ? 1 : -1);
            }
            return adx;
        },
        pineCode: `[plus_di, minus_di, adx_value] = ta.adx(14)
adx_bullish = plus_di > minus_di
adx_bearish = plus_di < minus_di`
    },

    // CCI - Commodity Channel Index
    CCI: {
        calculate: (data, period = 20) => {
            const cci = [];
            for (let i = 0; i < data.length; i++) {
                if (i < period - 1) {
                    cci.push(null);
                    continue;
                }
                const tp = data.slice(i - period + 1, i + 1).map(d => (d.high + d.low + d.close) / 3);
                const smaTP = tp.reduce((a, b) => a + b) / period;
                const mad = tp.reduce((sum, v) => sum + Math.abs(v - smaTP), 0) / period;
                cci.push((tp[tp.length - 1] - smaTP) / (0.015 * mad));
            }
            return cci;
        },
        pineCode: `cci_value = ta.cci(20)
cci_bullish = cci_value > 100
cci_bearish = cci_value < -100`
    },

    // MFI - Money Flow Index
    MFI: {
        calculate: (data, period = 14) => {
            const mfi = [];
            for (let i = 0; i < data.length; i++) {
                if (i < period) {
                    mfi.push(null);
                    continue;
                }
                let posFlow = 0, negFlow = 0;
                for (let j = i - period + 1; j <= i; j++) {
                    const tp = (data[j].high + data[j].low + data[j].close) / 3;
                    const prevTp = j > 0 ? (data[j - 1].high + data[j - 1].low + data[j - 1].close) / 3 : tp;
                    if (tp > prevTp) posFlow += tp * data[j].volume;
                    else negFlow += tp * data[j].volume;
                }
                const mfRatio = posFlow / negFlow;
                mfi.push(100 - (100 / (1 + mfRatio)));
            }
            return mfi;
        },
        pineCode: `mfi_value = ta.mfi(14)
mfi_bullish = mfi_value < 20
mfi_bearish = mfi_value > 80`
    },

    // ROC - Rate of Change
    ROC: {
        calculate: (data, period = 12) => {
            const roc = [];
            for (let i = 0; i < data.length; i++) {
                if (i < period) {
                    roc.push(null);
                } else {
                    roc.push(((data[i].close - data[i - period].close) / data[i - period].close) * 100);
                }
            }
            return roc;
        },
        pineCode: `roc_value = ta.roc(close, 12)
roc_bullish = roc_value > 0
roc_bearish = roc_value < 0`
    },

    // VROC - Volume Rate of Change
    VROC: {
        calculate: (data, period = 12) => {
            const vroc = [];
            for (let i = 0; i < data.length; i++) {
                if (i < period) {
                    vroc.push(null);
                } else {
                    vroc.push(((data[i].volume - data[i - period].volume) / data[i - period].volume) * 100);
                }
            }
            return vroc;
        },
        pineCode: `vroc_value = (volume - volume[12]) / volume[12] * 100
vroc_bullish = vroc_value > 0
vroc_bearish = vroc_value < 0`
    },

    // RVI - Relative Vigor Index
    RVI: {
        calculate: (data, period = 10) => {
            const rvi = [];
            for (let i = 0; i < data.length; i++) {
                if (i < period) {
                    rvi.push(null);
                    continue;
                }
                let num = 0, denom = 0;
                for (let j = i - period + 1; j <= i; j++) {
                    num += data[j].close - data[j].open;
                    denom += data[j].high - data[j].low;
                }
                rvi.push(denom !== 0 ? num / denom : 0);
            }
            return rvi;
        },
        pineCode: `rvi_value = ta.rvi(10)
rvi_bullish = rvi_value > 0
rvi_bearish = rvi_value < 0`
    },

    // Donchian Channels
    Donchian: {
        calculate: (data, period = 20) => {
            const donchian = [];
            for (let i = 0; i < data.length; i++) {
                if (i < period - 1) {
                    donchian.push(null);
                    continue;
                }
                const slice = data.slice(i - period + 1, i + 1);
                const high = Math.max(...slice.map(d => d.high));
                const low = Math.min(...slice.map(d => d.low));
                donchian.push({ high, low, mid: (high + low) / 2 });
            }
            return donchian;
        },
        pineCode: `donchian_high = ta.highest(high, 20)
donchian_low = ta.lowest(low, 20)
donchian_bullish = close > donchian_high[1]
donchian_bearish = close < donchian_low[1]`
    },

    // Awesome Oscillator
    Awesome_Oscillator: {
        calculate: (data) => {
            const ao = [];
            const sma5 = IndicatorsLibrary._sma(data.map(d => (d.high + d.low) / 2), 5);
            const sma34 = IndicatorsLibrary._sma(data.map(d => (d.high + d.low) / 2), 34);
            for (let i = 0; i < data.length; i++) {
                ao.push((sma5[i] || 0) - (sma34[i] || 0));
            }
            return ao;
        },
        pineCode: `ao = ta.sma(hl2, 5) - ta.sma(hl2, 34)
ao_bullish = ao > 0
ao_bearish = ao < 0`
    },

    // Momentum
    Momentum: {
        calculate: (data, period = 10) => {
            const momentum = [];
            for (let i = 0; i < data.length; i++) {
                if (i < period) {
                    momentum.push(null);
                } else {
                    momentum.push(data[i].close - data[i - period].close);
                }
            }
            return momentum;
        },
        pineCode: `momentum = close - close[10]
momentum_bullish = momentum > 0
momentum_bearish = momentum < 0`
    },

    // ATR - Average True Range
    ATR: {
        calculate: (data, period = 14) => {
            const atr = [];
            for (let i = 0; i < data.length; i++) {
                if (i < period) {
                    atr.push(null);
                    continue;
                }
                let trSum = 0;
                for (let j = i - period + 1; j <= i; j++) {
                    const prevClose = j > 0 ? data[j - 1].close : data[j].close;
                    const tr = Math.max(
                        data[j].high - data[j].low,
                        Math.abs(data[j].high - prevClose),
                        Math.abs(data[j].low - prevClose)
                    );
                    trSum += tr;
                }
                atr.push(trSum / period);
            }
            return atr;
        },
        pineCode: `atr_value = ta.atr(14)
atr_bullish = atr_value > ta.atr(14)[20]
atr_bearish = atr_value < ta.atr(14)[20]`
    },

    // Pivot Points
    Pivot_Points: {
        calculate: (data, period = 1) => {
            const pivots = [];
            for (let i = 0; i < data.length; i++) {
                if (i < period) {
                    pivots.push(null);
                    continue;
                }
                const h = data[i - period].high;
                const l = data[i - period].low;
                const c = data[i - period].close;
                const p = (h + l + c) / 3;
                pivots.push({
                    pivot: p,
                    r1: 2 * p - l,
                    s1: 2 * p - h,
                    r2: p + (h - l),
                    s2: p - (h - l)
                });
            }
            return pivots;
        },
        pineCode: `pivot = (high[1] + low[1] + close[1]) / 3
r1 = 2 * pivot - low[1]
s1 = 2 * pivot - high[1]
pivot_bullish = close > pivot
pivot_bearish = close < pivot`
    },

    // OBV - On Balance Volume
    OBV: {
        calculate: (data) => {
            const obv = [data[0].volume];
            for (let i = 1; i < data.length; i++) {
                if (data[i].close > data[i - 1].close) {
                    obv.push(obv[i - 1] + data[i].volume);
                } else if (data[i].close < data[i - 1].close) {
                    obv.push(obv[i - 1] - data[i].volume);
                } else {
                    obv.push(obv[i - 1]);
                }
            }
            return obv;
        },
        pineCode: `obv = ta.cum(close > close[1] ? volume : close < close[1] ? -volume : 0)
obv_bullish = obv > obv[1]
obv_bearish = obv < obv[1]`
    },

    // SuperTrend
    SuperTrend: {
        calculate: (data, period = 10, multiplier = 3) => {
            const hl2 = data.map(d => (d.high + d.low) / 2);
            const atr = IndicatorsLibrary.ATR.calculate(data, period);
            const supertrend = [];
            
            let basic_ub = hl2[0], basic_lb = hl2[0];
            let final_ub = hl2[0], final_lb = hl2[0];
            
            for (let i = 1; i < data.length; i++) {
                if (!atr[i]) {
                    supertrend.push(null);
                    continue;
                }
                basic_ub = hl2[i] + multiplier * atr[i];
                basic_lb = hl2[i] - multiplier * atr[i];
                final_ub = basic_ub < final_ub || data[i - 1].close > final_ub ? basic_ub : final_ub;
                final_lb = basic_lb > final_lb || data[i - 1].close < final_lb ? basic_lb : final_lb;
                supertrend.push(data[i].close <= final_ub ? final_ub : final_lb);
            }
            return supertrend;
        },
        pineCode: `hl2 = (high + low) / 2
atr_val = ta.atr(10)
basic_ub = hl2 + 3 * atr_val
basic_lb = hl2 - 3 * atr_val
final_ub = basic_ub < nz(final_ub[1]) or close[1] > nz(final_ub[1]) ? basic_ub : nz(final_ub[1])
final_lb = basic_lb > nz(final_lb[1]) or close[1] < nz(final_lb[1]) ? basic_lb : nz(final_lb[1])
supertrend = close <= nz(final_ub[1]) ? nz(final_ub[1]) : nz(final_lb[1])
supertrend_bullish = close > supertrend
supertrend_bearish = close < supertrend`
    },

    // Helper functions
    _sma: (data, period) => {
        const sma = [];
        for (let i = 0; i < data.length; i++) {
            if (i < period - 1) {
                sma.push(null);
            } else {
                const sum = data.slice(i - period + 1, i + 1).reduce((a, b) => a + b, 0);
                sma.push(sum / period);
            }
        }
        return sma;
    },

    _ema: (data, period) => {
        const ema = [];
        const multiplier = 2 / (period + 1);
        let smaSum = 0;
        
        for (let i = 0; i < data.length; i++) {
            if (i < period - 1) {
                ema.push(null);
                smaSum += data[i];
            } else if (i === period - 1) {
                smaSum += data[i];
                ema.push(smaSum / period);
            } else {
                const prevEma = ema[i - 1];
                const newEma = (data[i] - prevEma) * multiplier + prevEma;
                ema.push(newEma);
            }
        }
        return ema;
    },

    // Get all indicators as Pine Script code
    getPineScriptCode: (indicators) => {
        let code = '// ======================== INDICATORS ========================\n';
        indicators.forEach(ind => {
            if (IndicatorsLibrary[ind] && IndicatorsLibrary[ind].pineCode) {
                code += IndicatorsLibrary[ind].pineCode + '\n\n';
            }
        });
        return code;
    }
};
