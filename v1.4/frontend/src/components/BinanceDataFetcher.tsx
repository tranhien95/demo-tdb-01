import React, { useState, useEffect } from 'react'
import { binanceAPI } from '../services/api'
import { useOptimizerStore } from '../store/optimizerStore'
import { OHLCV } from '../types'

export const BinanceDataFetcher: React.FC = () => {
  const { setCsvData, setProgress } = useOptimizerStore()
  
  const [symbols, setSymbols] = useState<string[]>([])
  const [timeframes, setTimeframes] = useState<Record<string, string>>({})
  
  const [selectedSymbol, setSelectedSymbol] = useState('BTC/USDT')
  const [selectedTimeframe, setSelectedTimeframe] = useState('15m')
  const [limit, setLimit] = useState(2000)
  
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState('')
  const [success, setSuccess] = useState('')

  // Load symbols and timeframes on mount
  useEffect(() => {
    loadAvailableOptions()
  }, [])

  const loadAvailableOptions = async () => {
    try {
      const [symbolsRes, timeframesRes] = await Promise.all([
        binanceAPI.getSymbols(),
        binanceAPI.getTimeframes()
      ])
      setSymbols(symbolsRes.symbols)
      setTimeframes(timeframesRes.timeframes)
    } catch (err) {
      setError('Không thể tải danh sách symbol/timeframe: ' + (err as Error).message)
    }
  }

  const handleFetchData = async () => {
    setError('')
    setSuccess('')
    setLoading(true)

    try {
      setProgress({ isRunning: true, percent: 10, tested: 0, withTrades: 0 })

      const response = await binanceAPI.fetchData(selectedSymbol, selectedTimeframe, limit)

      if (response.status !== 'success') {
        throw new Error(response.message || 'Fetch failed')
      }

      // Convert to OHLCV format
      const ohlcvData: OHLCV[] = response.ohlcv_data.map((candle: any) => ({
        time: candle.time,
        open: candle.open,
        high: candle.high,
        low: candle.low,
        close: candle.close,
        volume: candle.volume
      }))

      setCsvData(ohlcvData)
      setSuccess(`✅ Tải thành công ${ohlcvData.length} candles từ ${selectedSymbol}`)
      
      setProgress({ isRunning: false, percent: 100, tested: 0, withTrades: 0 })
    } catch (err) {
      setError('❌ Lỗi: ' + (err as Error).message)
      setProgress({ isRunning: false, percent: 0, tested: 0, withTrades: 0 })
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="p-6 bg-white rounded-lg shadow-md border border-gray-200">
      <h2 className="text-2xl font-bold mb-4 text-gray-800">📊 Lấy Data từ Binance</h2>

      <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-4">
        {/* Symbol Selection */}
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-2">
            Symbol
          </label>
          <select
            value={selectedSymbol}
            onChange={(e) => setSelectedSymbol(e.target.value)}
            disabled={loading}
            className="w-full px-4 py-2 border border-gray-300 rounded-lg bg-white hover:border-blue-400 focus:border-blue-500 focus:outline-none disabled:bg-gray-100"
          >
            {symbols.map((sym) => (
              <option key={sym} value={sym}>
                {sym}
              </option>
            ))}
          </select>
        </div>

        {/* Timeframe Selection */}
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-2">
            Timeframe
          </label>
          <select
            value={selectedTimeframe}
            onChange={(e) => setSelectedTimeframe(e.target.value)}
            disabled={loading}
            className="w-full px-4 py-2 border border-gray-300 rounded-lg bg-white hover:border-blue-400 focus:border-blue-500 focus:outline-none disabled:bg-gray-100"
          >
            {Object.entries(timeframes).map(([key, label]) => (
              <option key={key} value={key}>
                {label}
              </option>
            ))}
          </select>
        </div>

        {/* Limit Selection */}
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-2">
            Số Candles
          </label>
          <div className="flex gap-2">
            <input
              type="number"
              min="50"
              max="10000"
              value={limit}
              onChange={(e) => setLimit(parseInt(e.target.value) || 1000)}
              disabled={loading}
              className="flex-1 px-4 py-2 border border-gray-300 rounded-lg focus:border-blue-500 focus:outline-none disabled:bg-gray-100"
            />
            <button
              onClick={handleFetchData}
              disabled={loading || !selectedSymbol || !selectedTimeframe}
              className="px-6 py-2 bg-blue-600 text-white rounded-lg font-semibold hover:bg-blue-700 disabled:bg-gray-400 disabled:cursor-not-allowed transition"
            >
              {loading ? 'Đang tải...' : 'Tải Data'}
            </button>
          </div>
        </div>
      </div>

      {/* Status Messages */}
      {error && (
        <div className="mb-4 p-4 bg-red-50 border border-red-200 rounded-lg text-red-700">
          {error}
        </div>
      )}
      {success && (
        <div className="mb-4 p-4 bg-green-50 border border-green-200 rounded-lg text-green-700">
          {success}
        </div>
      )}

      {/* Info */}
      <div className="text-sm text-gray-600 bg-blue-50 p-4 rounded-lg border border-blue-100">
        <p>💡 <strong>Tip:</strong> Chọn symbol, timeframe, và số lượng candles (50-10000), sau đó nhấn "Tải Data"</p>
        <p className="mt-2">🔗 <strong>Symbols:</strong> BTC, ETH, BNB, XRP, SOL, ADA, DOGE, v.v...</p>
        <p>⏱️ <strong>Timeframes:</strong> 1m, 5m, 15m, 30m, 1h, 4h, 1d, 1w</p>
      </div>
    </div>
  )
}
