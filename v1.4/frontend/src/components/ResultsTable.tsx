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
    // Parse combo string to get indicators
    const indicators = combo.combo.split(' + ').map(indName => ({
      type: indName.trim(),
      config: {},
      weight: 1.0,
      enabled: true
    }))

    // Save to localStorage for Strategy Builder to load
    localStorage.setItem('optimizedCombo', JSON.stringify({
      indicators: indicators,
      threshold: 70 // Default threshold
    }))

    alert(`✅ Đã lưu combo "${combo.combo}"! Vào Strategy Builder để load và test chi tiết.`)
  }

  const handleGenerateScript = async (combo: ComboResult) => {
    const indicators = combo.combo.split(' + ')
    try {
      const result = await optimizerAPI.generatePineScript(indicators)
      
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
                  <td className="p-4 font-mono text-secondary font-bold">{result.combo}</td>
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
                    <div className="flex gap-2 justify-center">
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
