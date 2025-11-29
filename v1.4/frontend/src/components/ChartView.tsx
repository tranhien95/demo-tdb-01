import React, { useEffect, useRef } from 'react'
import { createChart, IChartApi, ISeriesApi, CandlestickData, Time } from 'lightweight-charts'
import { useOptimizerStore } from '../store/optimizerStore'

export const ChartView: React.FC = () => {
  const { selectedCombo, csvData, setShowChart } = useOptimizerStore()
  const chartContainerRef = useRef<HTMLDivElement>(null)
  const chartRef = useRef<IChartApi | null>(null)

  useEffect(() => {
    if (!chartContainerRef.current || !selectedCombo || !csvData) return

    // Create chart
    const chart = createChart(chartContainerRef.current, {
      width: chartContainerRef.current.clientWidth,
      height: 500,
      layout: {
        background: { color: '#1a1a2e' },
        textColor: '#d1d4dc',
      },
      grid: {
        vertLines: { color: '#334158' },
        horzLines: { color: '#334158' },
      },
      timeScale: {
        borderColor: '#485c7b',
      },
    })

    chartRef.current = chart

    // Add candlestick series
    const candlestickSeries = chart.addCandlestickSeries({
      upColor: '#22c55e',
      downColor: '#ef4444',
      borderVisible: false,
      wickUpColor: '#22c55e',
      wickDownColor: '#ef4444',
    })

    const chartData: CandlestickData<Time>[] = csvData.map(d => ({
      time: (new Date(d.time).getTime() / 1000) as Time,
      open: d.open,
      high: d.high,
      low: d.low,
      close: d.close,
    }))

    candlestickSeries.setData(chartData)

    // Add markers for trades
    const markers = selectedCombo.trades_list.flatMap(trade => {
      const marks = []
      
      // Entry marker
      marks.push({
        time: (new Date(trade.time).getTime() / 1000) as Time,
        position: trade.type === 'LONG' ? 'belowBar' : 'aboveBar',
        color: trade.type === 'LONG' ? '#22c55e' : '#ef4444',
        shape: 'arrowUp' as const,
        text: `${trade.type} @ ${trade.entry}`,
      })

      // Exit marker
      if (trade.exit_time) {
        marks.push({
          time: (new Date(trade.exit_time).getTime() / 1000) as Time,
          position: (trade.profit_pct ?? 0) > 0 ? 'aboveBar' : 'belowBar',
          color: (trade.profit_pct ?? 0) > 0 ? '#10b981' : '#f59e0b',
          shape: 'circle' as const,
          text: `Exit @ ${trade.exit} (${trade.profit_pct}%)`,
        })
      }

      return marks
    })

    candlestickSeries.setMarkers(markers)

    chart.timeScale().fitContent()

    // Cleanup
    return () => {
      chart.remove()
    }
  }, [selectedCombo, csvData])

  if (!selectedCombo) return null

  return (
    <div className="card mt-6">
      <div className="flex justify-between items-center mb-4">
        <h2 className="text-2xl font-bold text-primary">📊 {selectedCombo.combo}</h2>
        <button
          className="bg-primary hover:bg-primary/80 text-white px-4 py-2 rounded font-bold"
          onClick={() => setShowChart(false)}
        >
          ✕ Đóng
        </button>
      </div>

      <div ref={chartContainerRef} className="w-full mb-4"></div>

      <div className="grid grid-cols-4 gap-4 mb-6">
        <div className="bg-primary/10 p-4 rounded-lg border-l-4 border-primary">
          <div className="text-xs text-gray-400 uppercase">Total Trades</div>
          <div className="text-2xl text-secondary font-bold">{selectedCombo.trades}</div>
        </div>
        <div className="bg-primary/10 p-4 rounded-lg border-l-4 border-primary">
          <div className="text-xs text-gray-400 uppercase">Wins / Losses</div>
          <div className="text-2xl text-secondary font-bold">{selectedCombo.wins} / {selectedCombo.losses}</div>
        </div>
        <div className="bg-primary/10 p-4 rounded-lg border-l-4 border-primary">
          <div className="text-xs text-gray-400 uppercase">Total Profit</div>
          <div className="text-2xl text-secondary font-bold">{selectedCombo.profit_pct}%</div>
        </div>
        <div className="bg-primary/10 p-4 rounded-lg border-l-4 border-primary">
          <div className="text-xs text-gray-400 uppercase">Win Rate</div>
          <div className="text-2xl text-secondary font-bold">{selectedCombo.win_rate}%</div>
        </div>
      </div>

      <h3 className="text-lg font-bold text-secondary mb-3">📋 Danh Sách Trades</h3>
      <div className="overflow-x-auto max-h-96 rounded-lg border border-primary/30">
        <table className="w-full text-sm">
          <thead className="bg-primary/20 sticky top-0">
            <tr>
              <th className="p-2">#</th>
              <th className="p-2">Entry Time</th>
              <th className="p-2">Entry Price</th>
              <th className="p-2">Exit Time</th>
              <th className="p-2">Exit Price</th>
              <th className="p-2">SL</th>
              <th className="p-2">TP</th>
              <th className="p-2">Profit %</th>
              <th className="p-2">Type</th>
            </tr>
          </thead>
          <tbody>
            {selectedCombo.trades_list.map((trade, idx) => (
              <tr key={idx} className="border-b border-primary/10">
                <td className="p-2 text-center">{idx + 1}</td>
                <td className="p-2">{trade.time.slice(11, 16)}</td>
                <td className="p-2">{trade.entry}</td>
                <td className="p-2">{trade.exit_time?.slice(11, 16) || 'N/A'}</td>
                <td className="p-2">{trade.exit}</td>
                <td className="p-2">{trade.sl}</td>
                <td className="p-2">{trade.tp}</td>
                <td className={`p-2 font-bold ${(trade.profit_pct ?? 0) > 0 ? 'text-green-400' : 'text-red-400'}`}>
                  {trade.profit_pct}%
                </td>
                <td className="p-2">{trade.type}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  )
}
