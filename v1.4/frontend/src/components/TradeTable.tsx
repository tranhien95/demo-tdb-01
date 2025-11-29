import React, { useState } from 'react'
import { Trade } from '../types'

interface Props {
  trades: Trade[]
  totalProfit: number
  totalProfitPct: number
}

const ROWS_PER_PAGE = 10

export const TradeTable: React.FC<Props> = ({ trades, totalProfit, totalProfitPct }) => {
  const [currentPage, setCurrentPage] = useState(1)
  const [expandedRow, setExpandedRow] = useState<number | null>(null)

  const totalPages = Math.ceil(trades.length / ROWS_PER_PAGE)
  const startIdx = (currentPage - 1) * ROWS_PER_PAGE
  const endIdx = startIdx + ROWS_PER_PAGE
  const currentTrades = trades.slice(startIdx, endIdx)

  const handlePrevPage = () => {
    setCurrentPage(prev => Math.max(1, prev - 1))
  }

  const handleNextPage = () => {
    setCurrentPage(prev => Math.min(totalPages, prev + 1))
  }

  const formatCurrency = (value: number) => {
    return new Intl.NumberFormat('en-US', {
      style: 'currency',
      currency: 'USD',
      minimumFractionDigits: 2,
      maximumFractionDigits: 2
    }).format(value)
  }

  const formatTime = (time: string) => {
    try {
      const date = new Date(time)
      return date.toLocaleString()
    } catch {
      return time
    }
  }

  if (trades.length === 0) {
    return (
      <div className="bg-white dark:bg-gray-800 rounded-xl p-6 shadow-lg">
        <h3 className="text-xl font-bold mb-4">📋 Trade History</h3>
        <div className="text-center text-gray-600 py-8">No trades found</div>
      </div>
    )
  }

  return (
    <div className="bg-white dark:bg-gray-800 rounded-xl p-6 shadow-lg">
      <div className="flex justify-between items-center mb-4">
        <h3 className="text-xl font-bold">📋 Trade History</h3>
        <div className="flex gap-6 text-right">
          <div>
            <div className="text-sm text-gray-600">Total Profit %</div>
            <div className={`text-lg font-bold ${totalProfitPct >= 0 ? 'text-green-600' : 'text-red-600'}`}>
              {totalProfitPct.toFixed(2)}%
            </div>
          </div>
          <div>
            <div className="text-sm text-gray-600">Total Profit USD</div>
            <div className={`text-lg font-bold ${totalProfit >= 0 ? 'text-green-600' : 'text-red-600'}`}>
              {formatCurrency(totalProfit)}
            </div>
          </div>
        </div>
      </div>

      {/* Trade Table */}
      <div className="overflow-x-auto mb-6">
        <table className="w-full text-sm">
          <thead>
            <tr className="border-b-2 bg-gray-50 dark:bg-gray-700">
              <th className="text-left p-3 font-bold">Type</th>
              <th className="text-right p-3 font-bold">Entry</th>
              <th className="text-right p-3 font-bold">Exit</th>
              <th className="text-right p-3 font-bold">Position $</th>
              <th className="text-right p-3 font-bold">Capital %</th>
              <th className="text-right p-3 font-bold">Profit %</th>
              <th className="text-right p-3 font-bold">Profit USD</th>
              <th className="text-left p-3 font-bold">Entry Time</th>
              <th className="text-left p-3 font-bold">Exit Time</th>
              <th className="text-left p-3 font-bold">Exit Reason</th>
              <th className="text-center p-3 font-bold">Detail</th>
            </tr>
          </thead>
          <tbody>
            {currentTrades.map((trade, index) => {
              const globalIndex = startIdx + index
              const profitUsd = trade.profit || 0
              const profitPct = trade.profit_pct || 0
              const positionSize = trade.position_size || 0
              const positionPercent = trade.position_percent || 0
              const isExpanded = expandedRow === globalIndex

              return (
                <React.Fragment key={globalIndex}>
                  <tr className={`border-b hover:bg-gray-50 dark:hover:bg-gray-700 ${isExpanded ? 'bg-blue-50 dark:bg-blue-900/20' : ''}`}>
                    <td className="p-3">
                      <span className={`px-2 py-1 rounded text-xs font-bold ${
                        trade.type === 'LONG' ? 'bg-green-100 text-green-700' : 'bg-red-100 text-red-700'
                      }`}>
                        {trade.type}
                      </span>
                    </td>
                    <td className="p-3 text-right font-mono">{trade.entry.toFixed(5)}</td>
                    <td className="p-3 text-right font-mono">{trade.exit?.toFixed(5) || '-'}</td>
                    <td className="p-3 text-right font-bold text-blue-600">{formatCurrency(positionSize)}</td>
                    <td className="p-3 text-right font-bold text-blue-600">{positionPercent.toFixed(2)}%</td>
                    <td className={`p-3 text-right font-bold ${profitPct >= 0 ? 'text-green-600' : 'text-red-600'}`}>
                      {profitPct >= 0 ? '+' : ''}{profitPct.toFixed(2)}%
                    </td>
                    <td className={`p-3 text-right font-bold ${profitUsd >= 0 ? 'text-green-600' : 'text-red-600'}`}>
                      {profitUsd >= 0 ? '+' : ''}{formatCurrency(profitUsd)}
                    </td>
                    <td className="p-3 text-xs text-gray-600">{formatTime(trade.time)}</td>
                    <td className="p-3 text-xs text-gray-600">{trade.exit_time ? formatTime(trade.exit_time) : '-'}</td>
                    <td className="p-3 text-xs">
                      <span className={`px-2 py-1 rounded text-xs font-semibold ${
                        trade.exit_reason === 'TP' ? 'bg-green-100 text-green-700' :
                        trade.exit_reason === 'SL' ? 'bg-red-100 text-red-700' :
                        'bg-yellow-100 text-yellow-700'
                      }`}>
                        {trade.exit_reason || '-'}
                      </span>
                    </td>
                    <td className="p-3 text-center">
                      <button
                        className="text-blue-600 hover:text-blue-800 font-bold"
                        onClick={() => setExpandedRow(isExpanded ? null : globalIndex)}
                      >
                        {isExpanded ? '▼' : '▶'}
                      </button>
                    </td>
                  </tr>

                  {/* Expanded Detail Row */}
                  {isExpanded && (
                    <tr className="bg-blue-50 dark:bg-blue-900/20 border-b">
                      <td colSpan={11} className="p-4">
                        <div className="space-y-3">
                          <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
                            <div className="p-3 bg-white dark:bg-gray-700 rounded-lg">
                              <div className="text-xs text-gray-600 mb-1">Entry Price</div>
                              <div className="font-bold font-mono">{trade.entry.toFixed(8)}</div>
                            </div>
                            <div className="p-3 bg-white dark:bg-gray-700 rounded-lg">
                              <div className="text-xs text-gray-600 mb-1">Exit Price</div>
                              <div className="font-bold font-mono">{trade.exit?.toFixed(8) || '-'}</div>
                            </div>
                            <div className="p-3 bg-white dark:bg-gray-700 rounded-lg">
                              <div className="text-xs text-gray-600 mb-1">Stop Loss</div>
                              <div className="font-bold font-mono">{trade.sl.toFixed(8)}</div>
                            </div>
                            <div className="p-3 bg-white dark:bg-gray-700 rounded-lg">
                              <div className="text-xs text-gray-600 mb-1">Take Profit</div>
                              <div className="font-bold font-mono">{trade.tp.toFixed(8)}</div>
                            </div>
                          </div>

                          <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
                            <div className="p-3 bg-white dark:bg-gray-700 rounded-lg">
                              <div className="text-xs text-gray-600 mb-1">Position Size</div>
                              <div className="text-lg font-bold text-blue-600">
                                {formatCurrency(positionSize)}
                              </div>
                            </div>
                            <div className="p-3 bg-white dark:bg-gray-700 rounded-lg">
                              <div className="text-xs text-gray-600 mb-1">Capital Used %</div>
                              <div className="text-lg font-bold text-blue-600">
                                {positionPercent.toFixed(2)}%
                              </div>
                            </div>
                            <div className="p-3 bg-white dark:bg-gray-700 rounded-lg">
                              <div className="text-xs text-gray-600 mb-1">Profit %</div>
                              <div className={`text-lg font-bold ${profitPct >= 0 ? 'text-green-600' : 'text-red-600'}`}>
                                {profitPct >= 0 ? '+' : ''}{profitPct.toFixed(4)}%
                              </div>
                            </div>
                            <div className="p-3 bg-white dark:bg-gray-700 rounded-lg">
                              <div className="text-xs text-gray-600 mb-1">Profit USD</div>
                              <div className={`text-lg font-bold ${profitUsd >= 0 ? 'text-green-600' : 'text-red-600'}`}>
                                {profitUsd >= 0 ? '+' : ''}{formatCurrency(profitUsd)}
                              </div>
                            </div>
                          </div>

                          <div className="grid grid-cols-2 md:grid-cols-2 gap-4">
                            <div className="p-3 bg-white dark:bg-gray-700 rounded-lg">
                              <div className="text-xs text-gray-600 mb-1">Duration</div>
                              <div className="text-sm font-mono">
                                {trade.exit_time ? (
                                  <>
                                    {new Date(trade.exit_time).getTime() - new Date(trade.time).getTime() > 0 ?
                                      Math.round((new Date(trade.exit_time).getTime() - new Date(trade.time).getTime()) / (1000 * 60)) + ' min'
                                      : '-'
                                    }
                                  </>
                                ) : '-'}
                              </div>
                            </div>
                          </div>

                          <div className="grid grid-cols-1 gap-4">
                            {trade.exit_reason && (
                              <div className="p-3 bg-white dark:bg-gray-700 rounded-lg">
                                <div className="text-xs text-gray-600 mb-1">Exit Reason</div>
                                <span className={`px-3 py-1 rounded font-bold text-sm ${
                                  trade.exit_reason === 'TP' ? 'bg-green-100 text-green-700' :
                                  trade.exit_reason === 'SL' ? 'bg-red-100 text-red-700' :
                                  'bg-yellow-100 text-yellow-700'
                                }`}>
                                  {trade.exit_reason}
                                </span>
                              </div>
                            )}
                          </div>
                        </div>
                      </td>
                    </tr>
                  )}
                </React.Fragment>
              )
            })}
          </tbody>
        </table>
      </div>

      {/* Pagination */}
      <div className="flex items-center justify-between">
        <div className="text-sm text-gray-600">
          Showing {startIdx + 1} to {Math.min(endIdx, trades.length)} of {trades.length} trades
        </div>
        <div className="flex gap-2">
          <button
            onClick={handlePrevPage}
            disabled={currentPage === 1}
            className="px-4 py-2 rounded-lg border disabled:opacity-50 disabled:cursor-not-allowed hover:bg-gray-100 dark:hover:bg-gray-700"
          >
            ← Previous
          </button>
          <div className="flex items-center gap-2">
            {Array.from({ length: totalPages }, (_, i) => i + 1).map(page => (
              <button
                key={page}
                onClick={() => setCurrentPage(page)}
                className={`px-3 py-2 rounded-lg font-bold ${
                  currentPage === page
                    ? 'bg-blue-600 text-white'
                    : 'border hover:bg-gray-100 dark:hover:bg-gray-700'
                }`}
              >
                {page}
              </button>
            ))}
          </div>
          <button
            onClick={handleNextPage}
            disabled={currentPage === totalPages}
            className="px-4 py-2 rounded-lg border disabled:opacity-50 disabled:cursor-not-allowed hover:bg-gray-100 dark:hover:bg-gray-700"
          >
            Next →
          </button>
        </div>
      </div>
    </div>
  )
}
