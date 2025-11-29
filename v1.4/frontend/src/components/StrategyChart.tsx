import React, { useEffect, useRef } from 'react'
import { createChart, ColorType, IChartApi, ISeriesApi } from 'lightweight-charts'
import { BacktestResult, OHLCV } from '../types'

interface Props {
  ohlcvData: OHLCV[]
  result: BacktestResult
}

export const StrategyChart: React.FC<Props> = ({ ohlcvData, result }) => {
  const chartContainerRef = useRef<HTMLDivElement>(null)
  const chartRef = useRef<IChartApi | null>(null)

  useEffect(() => {
    if (!chartContainerRef.current || !ohlcvData.length) return

    const chart = createChart(chartContainerRef.current, {
      layout: {
        background: { type: ColorType.Solid, color: '#ffffff' },
        textColor: '#333',
      },
      width: chartContainerRef.current.clientWidth,
      height: 500,
      grid: {
        vertLines: { color: '#e1e1e1' },
        horzLines: { color: '#e1e1e1' },
      },
      crosshair: {
        mode: 1,
      },
      timeScale: {
        borderColor: '#cccccc',
      },
    })

    chartRef.current = chart

    // Add candlestick series
    const candlestickSeries = chart.addCandlestickSeries({
      upColor: '#26a69a',
      downColor: '#ef5350',
      borderVisible: false,
      wickUpColor: '#26a69a',
      wickDownColor: '#ef5350',
    })

    // Format OHLCV data and convert to Unix timestamps
    const candleData = ohlcvData.map((d) => {
      // Always convert to Unix timestamp for consistency
      let timeValue: number
      if (typeof d.time === 'string') {
        if (d.time.includes('T')) {
          // ISO format - convert to Unix timestamp (seconds)
          timeValue = Math.floor(new Date(d.time).getTime() / 1000)
        } else {
          // YYYY-MM-DD format - parse and convert
          timeValue = Math.floor(new Date(d.time).getTime() / 1000)
        }
      } else {
        // Already a number, assume it's Unix timestamp
        timeValue = d.time
      }
      
      return {
        time: timeValue,
        open: d.open,
        high: d.high,
        low: d.low,
        close: d.close,
      }
    })

    // Sort by time ascending FIRST
    candleData.sort((a, b) => a.time - b.time)

    // Then remove duplicates, keeping the first occurrence
    const uniqueCandleData = candleData.reduce((acc, candle) => {
      const existing = acc.find(c => c.time === candle.time)
      if (!existing) {
        acc.push(candle)
      }
      return acc
    }, [] as typeof candleData)

    candlestickSeries.setData(uniqueCandleData)

    // Add entry markers
    const entryMarkers = result.trades.map((trade) => {
      let tradeTime: number
      if (typeof trade.time === 'string') {
        tradeTime = Math.floor(new Date(trade.time).getTime() / 1000)
      } else {
        tradeTime = trade.time
      }
      
      return {
        time: tradeTime,
        position: trade.type === 'LONG' ? 'belowBar' : 'aboveBar',
        color: trade.type === 'LONG' ? '#26a69a' : '#ef5350',
        shape: trade.type === 'LONG' ? 'arrowUp' : 'arrowDown',
        text: `${trade.type} @ ${trade.entry.toFixed(5)}`,
      }
    })

    // Add exit markers
    const exitMarkers = result.trades
      .filter((trade) => trade.exit_time)
      .map((trade) => {
        let exitTime: number
        if (typeof trade.exit_time === 'string') {
          exitTime = Math.floor(new Date(trade.exit_time).getTime() / 1000)
        } else {
          exitTime = trade.exit_time!
        }
        
        const isProfit = (trade.profit_pct || 0) > 0
        return {
          time: exitTime,
          position: trade.type === 'LONG' ? 'aboveBar' : 'belowBar',
          color: isProfit ? '#4caf50' : '#f44336',
          shape: 'circle',
          text: `Exit: ${(trade.profit_pct || 0).toFixed(2)}%`,
        }
      })

    // Sort all markers by time ascending
    const allMarkers = [...entryMarkers, ...exitMarkers].sort((a, b) => a.time - b.time)

    candlestickSeries.setMarkers(allMarkers as any)

    // Handle resize
    const handleResize = () => {
      if (chartContainerRef.current) {
        chart.applyOptions({ width: chartContainerRef.current.clientWidth })
      }
    }

    window.addEventListener('resize', handleResize)

    return () => {
      window.removeEventListener('resize', handleResize)
      chart.remove()
    }
  }, [ohlcvData, result])

  return (
    <div className="bg-white dark:bg-gray-800 rounded-xl p-6 shadow-lg mt-6">
      <h3 className="text-xl font-bold mb-4">📈 Trade Visualization</h3>
      <div ref={chartContainerRef} />
      <div className="mt-4 flex gap-4 text-sm">
        <div className="flex items-center gap-2">
          <div className="w-4 h-4 bg-green-500 rounded"></div>
          <span>Long Entry</span>
        </div>
        <div className="flex items-center gap-2">
          <div className="w-4 h-4 bg-red-500 rounded"></div>
          <span>Short Entry</span>
        </div>
        <div className="flex items-center gap-2">
          <div className="w-4 h-4 bg-green-600 rounded-full"></div>
          <span>Profitable Exit</span>
        </div>
        <div className="flex items-center gap-2">
          <div className="w-4 h-4 bg-red-600 rounded-full"></div>
          <span>Loss Exit</span>
        </div>
      </div>
    </div>
  )
}
