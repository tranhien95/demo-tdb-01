import React, { useState } from 'react'
import { BacktestResult } from '../types'
import { TradeTable } from './TradeTable'
import { EquityCurveChart } from './EquityCurveChart'

interface Props {
  result: BacktestResult
  initialCapital: number
}

const formatCurrency = (value: number) => {
  return new Intl.NumberFormat('en-US', {
    style: 'currency',
    currency: 'USD',
    minimumFractionDigits: 2,
    maximumFractionDigits: 2
  }).format(value)
}

export const StrategyResults: React.FC<Props> = ({ result, initialCapital }) => {
  const [activeTab, setActiveTab] = useState<'overview' | 'trades' | 'signals' | 'equity'>('overview')

  if (!result) {
    return null
  }

  const tradesCount = result.trades?.length || 0
  const signalsCount = result.signals?.length || 0
  const totalProfitUsd = result.total_profit || result.total_profit_usd || 0
  const totalProfitPct = result.total_profit_pct || result.profit_pct || 0
  const longTrades = result.long_trades || 0
  const shortTrades = result.short_trades || 0

  return (
    <div className="space-y-6">
      {/* Tabs */}
      <div className="bg-white dark:bg-gray-800 rounded-xl p-6 shadow-lg">
        <div className="flex gap-2 border-b">
          <button
            className={`px-4 py-2 font-bold ${activeTab === 'overview' ? 'border-b-2 border-blue-500 text-blue-600' : 'text-gray-600'}`}
            onClick={() => setActiveTab('overview')}
          >
            📊 Overview
          </button>
          <button
            className={`px-4 py-2 font-bold ${activeTab === 'equity' ? 'border-b-2 border-blue-500 text-blue-600' : 'text-gray-600'}`}
            onClick={() => setActiveTab('equity')}
          >
            📈 Equity Curve
          </button>
          <button
            className={`px-4 py-2 font-bold ${activeTab === 'trades' ? 'border-b-2 border-blue-500 text-blue-600' : 'text-gray-600'}`}
            onClick={() => setActiveTab('trades')}
          >
            📋 Trades ({tradesCount})
          </button>
          <button
            className={`px-4 py-2 font-bold ${activeTab === 'signals' ? 'border-b-2 border-blue-500 text-blue-600' : 'text-gray-600'}`}
            onClick={() => setActiveTab('signals')}
          >
            🔔 Signals ({signalsCount})
          </button>
        </div>
      </div>

      {/* Equity Curve Tab */}
      {activeTab === 'equity' && (
        <EquityCurveChart 
          equityCurve={result.equity_curve || []} 
          initialCapital={initialCapital}
        />
      )}

      {/* Overview Tab */}
      {activeTab === 'overview' && (
        <div className="bg-white dark:bg-gray-800 rounded-xl p-6 shadow-lg">
          <h3 className="text-2xl font-bold mb-6">📊 Backtest Results</h3>
          <div className="grid grid-cols-2 md:grid-cols-5 gap-4">
            <div className="p-4 bg-blue-50 dark:bg-blue-900/20 rounded-lg">
              <div className="text-sm text-gray-600">Total Trades</div>
              <div className="text-2xl font-bold">{result.total_trades}</div>
            </div>
            <div className="p-4 bg-blue-50 dark:bg-blue-900/20 rounded-lg">
              <div className="text-sm text-gray-600">Long / Short</div>
              <div className="text-xl font-bold text-blue-600">{longTrades} / {shortTrades}</div>
            </div>
            <div className="p-4 bg-green-50 dark:bg-green-900/20 rounded-lg">
              <div className="text-sm text-gray-600">Win Rate</div>
              <div className="text-2xl font-bold text-green-600">{(result.win_rate || 0).toFixed(2)}%</div>
            </div>
            <div className="p-4 bg-purple-50 dark:bg-purple-900/20 rounded-lg">
              <div className="text-sm text-gray-600">Total Profit %</div>
              <div className={`text-2xl font-bold ${totalProfitPct >= 0 ? 'text-green-600' : 'text-red-600'}`}>
                {totalProfitPct >= 0 ? '+' : ''}{totalProfitPct.toFixed(2)}%
              </div>
            </div>
            <div className="p-4 bg-purple-50 dark:bg-purple-900/20 rounded-lg">
              <div className="text-sm text-gray-600">Total Profit USD</div>
              <div className={`text-2xl font-bold ${totalProfitUsd >= 0 ? 'text-green-600' : 'text-red-600'}`}>
                {totalProfitUsd >= 0 ? '+' : ''}{formatCurrency(totalProfitUsd)}
              </div>
            </div>
            <div className="p-4 bg-orange-50 dark:bg-orange-900/20 rounded-lg">
              <div className="text-sm text-gray-600">Profit Factor</div>
              <div className="text-2xl font-bold">{(result.profit_factor || 0).toFixed(2)}</div>
            </div>
            <div className="p-4 bg-red-50 dark:bg-red-900/20 rounded-lg">
              <div className="text-sm text-gray-600">Max Drawdown</div>
              <div className="text-2xl font-bold text-red-600">{(result.max_drawdown || 0).toFixed(2)}%</div>
            </div>
            <div className="p-4 bg-yellow-50 dark:bg-yellow-900/20 rounded-lg">
              <div className="text-sm text-gray-600">Sharpe Ratio</div>
              <div className="text-2xl font-bold">{(result.sharpe_ratio || 0).toFixed(2)}</div>
            </div>
            <div className="p-4 bg-green-50 dark:bg-green-900/20 rounded-lg">
              <div className="text-sm text-gray-600">Winning Trades</div>
              <div className="text-2xl font-bold text-green-600">{result.winning_trades}</div>
            </div>
            <div className="p-4 bg-red-50 dark:bg-red-900/20 rounded-lg">
              <div className="text-sm text-gray-600">Losing Trades</div>
              <div className="text-2xl font-bold text-red-600">{result.losing_trades}</div>
            </div>
          </div>
        </div>
      )}

      {/* Trades Tab */}
      {activeTab === 'trades' && (
        <>
          {tradesCount === 0 ? (
            <div className="bg-white dark:bg-gray-800 rounded-xl p-6 shadow-lg text-center text-gray-600">
              No trades found
            </div>
          ) : (
            <TradeTable trades={result.trades} totalProfit={totalProfitUsd} totalProfitPct={totalProfitPct} />
          )}
        </>
      )}

      {/* Signals Tab */}
      {activeTab === 'signals' && (
        <div className="bg-white dark:bg-gray-800 rounded-xl p-6 shadow-lg">
          <h3 className="text-2xl font-bold mb-6">🔔 Trading Signals</h3>
          <div className="space-y-4 max-h-[600px] overflow-y-auto">
            {signalsCount === 0 ? (
              <div className="text-center text-gray-600 py-8">No signals found</div>
            ) : (
              result.signals.map((signal, index) => {
                const indicators = Object.entries(signal.contributing_indicators)
                const bullishCount = indicators.filter(([_, sig]) => sig === 'BULLISH').length
                const bearishCount = indicators.filter(([_, sig]) => sig === 'BEARISH').length
                const totalCount = indicators.length
                const agreementPercent = Math.max(bullishCount, bearishCount) / totalCount * 100
                
                return (
              <div key={index} className="p-4 border-2 rounded-lg hover:shadow-lg transition-shadow">
                <div className="flex justify-between items-start mb-3">
                  <div>
                    <span className="font-bold text-lg">Signal #{signal.index}</span>
                    <span className="text-sm text-gray-600 ml-2">{signal.time}</span>
                  </div>
                  <div className="text-right">
                    <div className="text-sm mb-1">
                      <span className="text-green-600 font-bold">🟢 Bullish: {signal.bullish_percent.toFixed(1)}%</span>
                      <span className="mx-2">|</span>
                      <span className="text-red-600 font-bold">🔴 Bearish: {signal.bearish_percent.toFixed(1)}%</span>
                    </div>
                    <div className="text-xs text-gray-600">
                      Agreement: {bullishCount > bearishCount ? `${bullishCount}/${totalCount} Bullish` : `${bearishCount}/${totalCount} Bearish`}
                      ({agreementPercent.toFixed(0)}%)
                    </div>
                  </div>
                </div>

                {/* Indicator Agreement Visual */}
                <div className="mb-3">
                  <div className="flex gap-1 mb-2">
                    {indicators.map(([ind, sig], i) => (
                      <div
                        key={i}
                        className={`h-2 flex-1 rounded ${
                          sig === 'BULLISH' ? 'bg-green-500' : 'bg-red-500'
                        }`}
                        title={`${ind}: ${sig}`}
                      />
                    ))}
                  </div>
                </div>

                <div className="text-sm">
                  <div className="font-bold mb-2">📊 Indicator Breakdown:</div>
                  <div className="grid grid-cols-2 gap-2">
                    {indicators.map(([ind, sig]) => (
                      <div key={ind} className="flex items-center gap-2 p-2 rounded bg-gray-50 dark:bg-gray-700">
                        <span className={`w-3 h-3 rounded-full flex-shrink-0 ${
                          sig === 'BULLISH' ? 'bg-green-500' : 'bg-red-500'
                        }`} />
                        <span className="text-xs font-medium truncate">{ind}</span>
                        <span className={`text-xs font-bold ml-auto ${
                          sig === 'BULLISH' ? 'text-green-600' : 'text-red-600'
                        }`}>
                          {sig === 'BULLISH' ? '↑' : '↓'}
                        </span>
                      </div>
                    ))}
                  </div>
                </div>

                {/* Signal Strength Badge */}
                <div className="mt-3 flex justify-end">
                  <span className={`px-3 py-1 rounded-full text-xs font-bold ${
                    agreementPercent >= 80 ? 'bg-green-100 text-green-700' :
                    agreementPercent >= 60 ? 'bg-yellow-100 text-yellow-700' :
                    'bg-orange-100 text-orange-700'
                  }`}>
                    {agreementPercent >= 80 ? '💪 Strong Agreement' :
                     agreementPercent >= 60 ? '⚠️ Moderate Agreement' :
                     '🔸 Weak Agreement'}
                  </span>
                </div>
              </div>
                )
              })
            )}
          </div>
        </div>
      )}
    </div>
  )
}
