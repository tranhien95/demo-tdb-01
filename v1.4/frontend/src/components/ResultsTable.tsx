import React, { useState } from 'react'
import { useOptimizerStore } from '../store/optimizerStore'
import { ComboResult } from '../types'
import { optimizerAPI } from '../services/api'

export const ResultsTable: React.FC = () => {
  const { results, params, setSelectedCombo, setShowChart } = useOptimizerStore()
  const [searchTerm, setSearchTerm] = useState('')

  const filteredResults = results.filter(r => {
    const matchesSearch = r.combo.toLowerCase().includes(searchTerm.toLowerCase())
    const matchesWinRate = r.win_rate >= params.minWinRate
    const matchesTrades = r.trades >= params.minTrades
    const matchesProfit = r.profit_pct >= params.minProfit
    return matchesSearch && matchesWinRate && matchesTrades && matchesProfit
  }).slice(0, 100)

  const handleRowClick = (combo: ComboResult) => {
    setSelectedCombo(combo)
    setShowChart(true)
  }

  const handleLoadToBuilder = (combo: ComboResult) => {
    // Use combo_config if available, otherwise parse from combo string
    let indicators
    if (combo.combo_config && combo.combo_config.length > 0) {
      indicators = combo.combo_config.map(ind => ({
        type: ind.indicator_name,
        config: ind.config || {},
        weight: 1.0,
        enabled: true
      }))
    } else {
      // Fallback: Parse combo string
      indicators = combo.combo.split(' + ').map(indName => ({
        type: indName.trim(),
        config: {},
        weight: 1.0,
        enabled: true
      }))
    }

    // Save to localStorage for Strategy Builder to load
    localStorage.setItem('optimizedCombo', JSON.stringify({
      indicators: indicators,
      threshold: 70 // Default threshold
    }))

    alert(`✅ Đã lưu combo "${combo.combo}" với config! Vào Strategy Builder để load và test chi tiết.`)
  }

  const handleGenerateScript = async (combo: ComboResult) => {
    const indicators = combo.combo.split(' + ')
    try {
      // Get filter settings from params
      const filterSettings = {
        indicators: indicators,
        filters: {
          enable_adx: params.enableADXFilter,
          adx_threshold: params.adxThreshold,
          enable_volume: params.enableVolumeFilter,
          volume_threshold: params.volumeThreshold >= 1 ? params.volumeThreshold / 100 : params.volumeThreshold, // Handle both % and multiplier
          enable_ma_filter: params.enableMAFilter,
          ma_period: params.maValue,
          enable_atr_filter: params.enableVolatilityFilter,
          min_atr: params.minATR,
          enable_trend_filter: params.enableTrendFilter,
          trend_ma: params.trendMA,
          threshold: params.threshold,
          candle_confirmation: params.candleConfirmation,
          risk_percent: params.riskPercent,
          rr_ratio: params.rrRatio,
          sl_percent: params.slPercent,
          capital: params.capital
        }
      }
      const result = await optimizerAPI.generatePineScript(indicators, filterSettings)
      
      // Download as file
      const blob = new Blob([result.code], { type: 'text/plain' })
      const url = URL.createObjectURL(blob)
      const a = document.createElement('a')
      a.href = url
      a.download = `${combo.combo.replace(/ \+ /g, '_')}.pine`
      a.click()
      URL.revokeObjectURL(url)
    } catch (error) {
      alert('Failed to generate Pine Script: ' + (error as Error).message)
    }
  }

  const downloadComboTrades = (combo: ComboResult) => {
    if (!combo.trades_list || combo.trades_list.length === 0) {
      alert('Không có trades để tải về cho combo này')
      return
    }

    const formatDateTime = (timeStr: string) => {
      if (!timeStr) return ''
      try {
        const date = new Date(timeStr)
        return date.toISOString().slice(0, 16).replace('T', ' ')
      } catch {
        return timeStr
      }
    }

    const formatCurrency = (value: number) => {
      return new Intl.NumberFormat('en-US', {
        style: 'currency',
        currency: 'USD',
        minimumFractionDigits: 2,
        maximumFractionDigits: 2
      }).format(value)
    }

    // TradingView format
    const headers = [
      'Giao dịch #',
      'Loại',
      'Ngày/Giờ',
      'Tín hiệu',
      'Giá USDT',
      'Quy mô vị thế (số lượng)',
      'Quy mô vị thế (giá trị)',
      'P&L ròng USD',
      'P&L ròng %',
      'Tăng lên USD',
      'Tăng lên %',
      'Mức sụt giảm tài khoản lớn nhất USD',
      'Mức sụt giảm tài khoản lớn nhất %',
      'P&L lũy kế USD',
      'P&L lũy kế %'
    ]

    const initialCapital = combo.trades_list.length > 0 && combo.trades_list[0].balance_before 
      ? combo.trades_list[0].balance_before 
      : params.capital || 1000

    let cumulativeProfit = 0
    let maxDrawdown = 0
    let maxDrawdownPct = 0
    let peakBalance = initialCapital
    let runningBalance = initialCapital

    const rows: any[] = []
    
    combo.trades_list.forEach((trade, index) => {
      const tradeNumber = index + 1
      const profitUsd = trade.profit || 0
      const profitPct = trade.profit_pct || 0
      
      // Calculate position size if not present (backward compatibility)
      let positionSize = trade.position_size || 0
      if (!positionSize && profitPct !== 0) {
        // Estimate from profit: positionSize = profitUSD / (profitPct / 100)
        positionSize = Math.abs(profitUsd / (profitPct / 100))
      } else if (!positionSize) {
        // Default calculation: risk = initialCapital * risk%, position = risk / SL%
        // Assuming 5% SL and 10% risk
        const estimatedRisk = initialCapital * 0.1
        positionSize = estimatedRisk / 0.05
      }
      
      const positionQuantity = positionSize / (trade.entry || 1)
      
      cumulativeProfit += profitUsd
      runningBalance = initialCapital + cumulativeProfit
      
      if (runningBalance > peakBalance) {
        peakBalance = runningBalance
      }
      const drawdown = peakBalance - runningBalance
      const drawdownPct = peakBalance > 0 ? (drawdown / peakBalance) * 100 : 0
      if (drawdown > maxDrawdown) {
        maxDrawdown = drawdown
      }
      if (drawdownPct > maxDrawdownPct) {
        maxDrawdownPct = drawdownPct
      }

      const entrySignal = trade.type === 'LONG' ? 'Long' : 'Short'
      const exitSignal = trade.exit_reason === 'TP' ? `${trade.type === 'LONG' ? 'Long' : 'Short'} Exit` :
                        trade.exit_reason === 'SL' ? `${trade.type === 'LONG' ? 'Long' : 'Short'} Exit` :
                        `Close entry(s) order ${trade.type === 'LONG' ? 'Long' : 'Short'}`

      // Entry row
      rows.push([
        tradeNumber,
        `Vào Lệnh ${trade.type === 'LONG' ? 'mua' : 'bán'}`,
        formatDateTime(trade.time),
        entrySignal,
        trade.entry.toFixed(2),
        positionQuantity.toFixed(5),
        positionSize.toFixed(8),
        profitUsd.toFixed(2),
        profitPct.toFixed(2),
        profitUsd >= 0 ? profitUsd.toFixed(2) : '0.00',
        profitPct >= 0 ? profitPct.toFixed(2) : '0.00',
        maxDrawdown.toFixed(2),
        maxDrawdownPct.toFixed(2),
        cumulativeProfit.toFixed(2),
        initialCapital > 0 ? ((cumulativeProfit / initialCapital) * 100).toFixed(2) : '0.00'
      ])

      // Exit row (only if trade is closed)
      if (trade.exit && trade.exit_time) {
        rows.push([
          tradeNumber,
          `Thoát Lệnh ${trade.type === 'LONG' ? 'mua' : 'bán'}`,
          formatDateTime(trade.exit_time),
          exitSignal,
          trade.exit.toFixed(2),
          positionQuantity.toFixed(5),
          positionSize.toFixed(8),
          profitUsd.toFixed(2),
          profitPct.toFixed(2),
          profitUsd >= 0 ? profitUsd.toFixed(2) : '0.00',
          profitPct >= 0 ? profitPct.toFixed(2) : '0.00',
          maxDrawdown.toFixed(2),
          maxDrawdownPct.toFixed(2),
          cumulativeProfit.toFixed(2),
          initialCapital > 0 ? ((cumulativeProfit / initialCapital) * 100).toFixed(2) : '0.00'
        ])
      }
    })

    const csvContent = [
      headers.join(','),
      ...rows.map(row => row.map((cell: any) => `"${cell}"`).join(','))
    ].join('\n')

    const blob = new Blob(['\ufeff' + csvContent], { type: 'text/csv;charset=utf-8;' })
    const url = URL.createObjectURL(blob)
    const a = document.createElement('a')
    a.href = url
    a.download = `trades-${combo.combo.replace(/ \+ /g, '_')}-${new Date().toISOString().slice(0, 10)}.csv`
    a.click()
    URL.revokeObjectURL(url)
  }

  const downloadCSV = () => {
    const csv = [
      ['Rank', 'Combo', 'Trades', 'Win Rate %', 'Profit %', 'Profit Factor', 'Draw Down %', 'Sharpe'],
      ...filteredResults.map((r, idx) => [
        idx + 1,
        r.combo,
        r.trades,
        r.win_rate,
        r.profit_pct,
        r.profit_factor,
        r.draw_down,
        r.sharpe
      ])
    ]

    const csvContent = csv.map(row => row.join(',')).join('\n')
    const blob = new Blob([csvContent], { type: 'text/csv' })
    const url = URL.createObjectURL(blob)
    const a = document.createElement('a')
    a.href = url
    a.download = 'combo-results-' + new Date().toISOString().slice(0, 10) + '.csv'
    a.click()
    URL.revokeObjectURL(url)
  }

  return (
    <div className="card mt-6">
      <div className="flex justify-between items-center mb-6 flex-wrap gap-4">
        <h2 className="text-2xl font-bold text-primary">📊 Kết Quả Top 100</h2>
        <div className="flex gap-3">
          <input
            type="text"
            className="input-field min-w-[200px]"
            placeholder="🔍 Tìm tổ hợp..."
            value={searchTerm}
            onChange={(e) => setSearchTerm(e.target.value)}
          />
          <button className="btn-secondary" onClick={downloadCSV}>
            ⬇️ Tải CSV
          </button>
        </div>
      </div>

      <div className="overflow-x-auto rounded-lg border-2 border-primary/30">
        <table className="w-full">
          <thead className="gradient-header">
            <tr>
              <th className="p-4 text-left">Rank</th>
              <th className="p-4 text-left">Tổ Hợp Chỉ Báo</th>
              <th className="p-4 text-center">Trades</th>
              <th className="p-4 text-center">Win Rate</th>
              <th className="p-4 text-center">Profit %</th>
              <th className="p-4 text-center">Profit Factor</th>
              <th className="p-4 text-center">Draw Down</th>
              <th className="p-4 text-center">Sharpe</th>
              <th className="p-4 text-center">Action</th>
            </tr>
          </thead>
          <tbody>
            {filteredResults.map((result, idx) => {
              const profitUSDT = (params.capital * result.profit_pct / 100).toFixed(2)
              return (
                <tr
                  key={idx}
                  className="border-b border-primary/10 hover:bg-primary/20 cursor-pointer transition-all"
                  onClick={() => handleRowClick(result)}
                >
                  <td className="p-4">{idx + 1}</td>
                  <td className="p-4">
                    <div className="font-mono text-secondary font-bold">{result.combo}</div>
                    {result.combo_config && result.combo_config.length > 0 && (
                      <details className="mt-2 text-xs">
                        <summary className="cursor-pointer text-blue-400 hover:text-blue-300">
                          📋 Xem config chi tiết
                        </summary>
                        <div className="mt-2 pl-4 space-y-1 bg-gray-800/50 p-2 rounded">
                          {result.combo_config.map((ind, i) => (
                            <div key={i} className="text-gray-300">
                              <span className="font-bold text-yellow-400">{ind.display_name}</span>
                              {Object.keys(ind.config).length > 0 && (
                                <span className="ml-2 text-gray-400">
                                  ({Object.entries(ind.config).map(([k, v]) => `${k}=${v}`).join(', ')})
                                </span>
                              )}
                            </div>
                          ))}
                        </div>
                      </details>
                    )}
                  </td>
                  <td className="p-4 text-center">{result.trades}</td>
                  <td className={`p-4 text-center font-bold ${result.win_rate >= 50 ? 'text-green-400' : 'text-red-400'}`}>
                    {result.win_rate}%
                  </td>
                  <td className="p-4 text-center">
                    <div>{result.profit_pct}%</div>
                    <div className="text-xs text-green-400">${profitUSDT}</div>
                  </td>
                  <td className="p-4 text-center">{result.profit_factor}</td>
                  <td className="p-4 text-center">{result.draw_down}%</td>
                  <td className="p-4 text-center">{result.sharpe}</td>
                  <td className="p-4 text-center">
                    <div className="flex gap-2 justify-center flex-wrap">
                      <button
                        className="bg-blue-500 hover:bg-blue-600 text-white px-3 py-1 rounded text-sm font-bold"
                        onClick={(e) => {
                          e.stopPropagation()
                          handleLoadToBuilder(result)
                        }}
                        title="Load vào Strategy Builder"
                      >
                        💾 Load
                      </button>
                      <button
                        className="bg-green-500 hover:bg-green-600 text-white px-3 py-1 rounded text-sm font-bold"
                        onClick={(e) => {
                          e.stopPropagation()
                          handleGenerateScript(result)
                        }}
                        title="Generate Pine Script"
                      >
                        📝 Script
                      </button>
                      <button
                        className="bg-purple-500 hover:bg-purple-600 text-white px-3 py-1 rounded text-sm font-bold"
                        onClick={(e) => {
                          e.stopPropagation()
                          downloadComboTrades(result)
                        }}
                        title="Tải danh sách trades"
                      >
                        📊 Trades
                      </button>
                    </div>
                  </td>
                </tr>
              )
            })}
          </tbody>
        </table>
      </div>
    </div>
  )
}
