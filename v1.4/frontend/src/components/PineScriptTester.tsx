import React, { useState } from 'react'
import { strategyAPI } from '../services/api'
import { useOptimizerStore } from '../store/optimizerStore'
import { StrategyResults } from './StrategyResults'
import { StrategyChart } from './StrategyChart'
import { Layout } from './Layout'
import { BacktestResult } from '../types'

export const PineScriptTester: React.FC = () => {
  const { csvData } = useOptimizerStore()
  const [pineCode, setPineCode] = useState('')
  const [backtestResult, setBacktestResult] = useState<BacktestResult | null>(null)
  const [isRunning, setIsRunning] = useState(false)
  const [error, setError] = useState<string | null>(null)
  const [parsedInfo, setParsedInfo] = useState<{
    strategy_name: string
    parsed_indicators: string[]
  } | null>(null)

  const handleBacktest = async () => {
    if (!pineCode.trim()) {
      setError('Vui lòng nhập Pine Script code')
      return
    }

    if (!csvData || csvData.length === 0) {
      setError('Vui lòng load dữ liệu OHLCV trước')
      return
    }

    setIsRunning(true)
    setError(null)
    setBacktestResult(null)
    setParsedInfo(null)

    try {
      const result = await strategyAPI.backtestPineScript(pineCode, csvData)
      
      setParsedInfo({
        strategy_name: result.strategy_name,
        parsed_indicators: result.parsed_indicators
      })
      setBacktestResult(result.backtest_result)
    } catch (err: any) {
      setError(err.message || 'Lỗi khi backtest Pine Script')
      console.error('Backtest error:', err)
    } finally {
      setIsRunning(false)
    }
  }

  const handleClear = () => {
    setPineCode('')
    setBacktestResult(null)
    setError(null)
    setParsedInfo(null)
  }

  const handleLoadExample = () => {
    setPineCode(`//@version=5
strategy("Optimized Combo", overlay=true, 
         default_qty_type=strategy.fixed,
         default_qty_value=0,
         initial_capital=1000.0,
         currency=currency.USD,
         commission_type=strategy.commission.percent,
         commission_value=0.0,
         slippage=0,
         pyramiding=0)

// Example indicators
rsi_val = ta.rsi(close, 14)
rsi_bull = rsi_val < 30
rsi_bear = rsi_val > 70

macd_line = ta.ema(close, 12) - ta.ema(close, 26)
signal_line = ta.ema(macd_line, 9)
macd_bull = macd_line > signal_line
macd_bear = macd_line < signal_line

// Signal calculation
total_indicators = 2.0
bullish_count = (rsi_bull ? 1 : 0) + (macd_bull ? 1 : 0)
bearish_count = (rsi_bear ? 1 : 0) + (macd_bear ? 1 : 0)

bullish_percent = (bullish_count / total_indicators) * 100
bearish_percent = (bearish_count / total_indicators) * 100

// Entry signals
long_signal = bullish_percent >= 70.0
short_signal = bearish_percent >= 70.0

// Risk management
risk_percent = 10.0
sl_percent = 5.0
rr_ratio = 1.0
initial_capital = 1000.0

// Entry/Exit
if long_signal and strategy.position_size == 0
    strategy.entry("Long", strategy.long)
    
if short_signal and strategy.position_size == 0
    strategy.entry("Short", strategy.short)`)
  }

  return (
    <Layout
      title="📝 Pine Script Tester"
      description="Paste Pine Script code và backtest ngay trên client"
    >
      <div className="space-y-6">
        {/* Input Section */}
        <div className="bg-white dark:bg-gray-800 rounded-xl p-6 shadow-lg">
          <div className="flex items-center justify-between mb-4">
            <h2 className="text-xl font-bold text-gray-800 dark:text-white">
              Pine Script Code
            </h2>
            <div className="flex gap-2">
              <button
                onClick={handleLoadExample}
                className="px-3 py-1.5 bg-gray-600 hover:bg-gray-700 text-white rounded text-sm transition"
                disabled={isRunning}
              >
                📋 Load Example
              </button>
              <button
                onClick={handleClear}
                className="px-3 py-1.5 bg-gray-600 hover:bg-gray-700 text-white rounded text-sm transition"
                disabled={isRunning}
              >
                🗑️ Clear
              </button>
            </div>
          </div>

          <textarea
            value={pineCode}
            onChange={(e) => setPineCode(e.target.value)}
            placeholder="Paste Pine Script code here...&#10;&#10;//@version=5&#10;strategy(&quot;My Strategy&quot;, overlay=true)&#10;// ..."
            className="w-full h-96 p-4 bg-slate-900 text-green-400 font-mono text-sm rounded-lg border border-gray-600 focus:border-blue-500 focus:ring-2 focus:ring-blue-500/20 resize-none"
            disabled={isRunning}
          />

          {!csvData || csvData.length === 0 && (
            <div className="mt-4 p-3 bg-yellow-500/20 border border-yellow-500/50 rounded text-yellow-600 dark:text-yellow-400 text-sm">
              ⚠️ Vui lòng load dữ liệu OHLCV từ <strong>Data Manager</strong> trước khi backtest
            </div>
          )}

          {error && (
            <div className="mt-4 p-3 bg-red-500/20 border border-red-500/50 rounded text-red-600 dark:text-red-400 text-sm">
              ❌ {error}
            </div>
          )}

          {parsedInfo && (
            <div className="mt-4 p-3 bg-blue-500/20 border border-blue-500/50 rounded text-blue-600 dark:text-blue-400 text-sm">
              <div className="font-bold mb-1">✅ Parsed Strategy:</div>
              <div>Name: <strong>{parsedInfo.strategy_name}</strong></div>
              <div>Indicators: <strong>{parsedInfo.parsed_indicators.join(', ') || 'None detected'}</strong></div>
              <div className="mt-2 text-xs opacity-75">
                ⚠️ Note: Parser có thể không extract đầy đủ parameters. Vui lòng verify kết quả.
              </div>
            </div>
          )}

          <button
            onClick={handleBacktest}
            disabled={isRunning || !pineCode.trim() || !csvData || csvData.length === 0}
            className={`mt-4 w-full py-3 rounded-lg font-bold text-white transition ${
              isRunning || !pineCode.trim() || !csvData || csvData.length === 0
                ? 'bg-gray-400 cursor-not-allowed'
                : 'bg-blue-600 hover:bg-blue-700'
            }`}
          >
            {isRunning ? '⏳ Đang backtest...' : '🚀 Run Backtest'}
          </button>
        </div>

        {/* Results Section */}
        {backtestResult && (
          <>
            <StrategyResults result={backtestResult} />
            {csvData && csvData.length > 0 && (
              <StrategyChart
                ohlcvData={csvData}
                result={backtestResult}
              />
            )}
          </>
        )}
      </div>
    </Layout>
  )
}

