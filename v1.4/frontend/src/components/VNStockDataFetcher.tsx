import React, { useState, useEffect } from 'react'
import { vnstockAPI } from '../services/api'
import { useOptimizerStore } from '../store/optimizerStore'
import { OHLCV } from '../types'

export const VNStockDataFetcher: React.FC = () => {
  const { setCsvData, setProgress } = useOptimizerStore()
  
  const [symbols, setSymbols] = useState<string[]>([])
  const [timeframes, setTimeframes] = useState<Record<string, string>>({})
  
  const [assetType, setAssetType] = useState<'stock' | 'derivative'>('stock')
  const [selectedSymbol, setSelectedSymbol] = useState('VCB')
  const [selectedTimeframe, setSelectedTimeframe] = useState('1d')
  const [limit, setLimit] = useState(1000)
  const [useDateRange, setUseDateRange] = useState(false)
  const [startDate, setStartDate] = useState('')
  const [endDate, setEndDate] = useState('')
  
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState('')
  const [success, setSuccess] = useState('')
  const [warning, setWarning] = useState('')

  // Helper function to format date for datetime-local input
  const formatDateForInput = (date: Date): string => {
    const year = date.getFullYear()
    const month = String(date.getMonth() + 1).padStart(2, '0')
    const day = String(date.getDate()).padStart(2, '0')
    const hours = String(date.getHours()).padStart(2, '0')
    const minutes = String(date.getMinutes()).padStart(2, '0')
    return `${year}-${month}-${day}T${hours}:${minutes}`
  }

  // Initialize default dates: 1 year ago to now (for stocks)
  const getDefaultDates = () => {
    const now = new Date()
    const oneYearAgo = new Date(now)
    oneYearAgo.setFullYear(now.getFullYear() - 1)
    return {
      start: formatDateForInput(oneYearAgo),
      end: formatDateForInput(now)
    }
  }

  // Load symbols and timeframes on mount
  useEffect(() => {
    loadAvailableOptions()
  }, [])

  // Fallback symbols if API fails
  const fallbackStocks = ['VCB', 'VIC', 'VHM', 'VRE', 'VNM', 'HPG', 'MSN', 'TCB', 'BID', 'CTG', 'VPB', 'SSI', 'FPT', 'VJC', 'MWG', 'PNJ', 'GAS', 'PLX', 'POW', 'GVR']
  const fallbackDerivatives = ['VN30F1M', 'VN30F2M', 'VN30F3M', 'HNX30F1M', 'HNX30F2M', 'HNX30F3M']
  
  // Load symbols when asset type changes
  useEffect(() => {
    loadAvailableOptions()
  }, [assetType])
  const fallbackTimeframes: Record<string, string> = {
    '1': '1 phút',
    '5': '5 phút',
    '15': '15 phút',
    '30': '30 phút',
    '1h': '1 giờ',
    '1d': '1 ngày',
    '1w': '1 tuần',
    '1M': '1 tháng'
  }

  // Set default dates (1 year ago to now) when useDateRange is enabled
  useEffect(() => {
    if (useDateRange) {
      const defaults = getDefaultDates()
      setStartDate(defaults.start)
      setEndDate(defaults.end)
    }
  }, [useDateRange])

  const loadAvailableOptions = async () => {
    try {
      setError('')
      setWarning('')
      
      const [symbolsRes, timeframesRes] = await Promise.all([
        vnstockAPI.getSymbols(assetType),
        vnstockAPI.getTimeframes()
      ])
      
      // Handle warning status (vnstock not installed, API error, outside trading hours, etc.)
      if (symbolsRes.status === 'warning' || timeframesRes.status === 'warning') {
        const warningMsg = symbolsRes.message || timeframesRes.message || 'vnstock API tạm thời không khả dụng'
        setWarning(warningMsg)
        // Don't set error, just show warning
      } else if (symbolsRes.status === 'success' || !symbolsRes.status) {
        // Success - clear warnings
        setWarning('')
      }
      
      const fallbackSymbols = assetType === 'derivative' ? fallbackDerivatives : fallbackStocks
      setSymbols(symbolsRes.symbols || fallbackSymbols)
      setTimeframes(timeframesRes.timeframes || fallbackTimeframes)
      
      // Reset selected symbol when asset type changes
      if (symbolsRes.symbols && symbolsRes.symbols.length > 0) {
        setSelectedSymbol(symbolsRes.symbols[0])
      }
    } catch (err: any) {
      const errorMsg = err.message || String(err)
      // Use fallback data on errors
      const fallbackSymbols = assetType === 'derivative' ? fallbackDerivatives : fallbackStocks
      setSymbols(fallbackSymbols)
      setTimeframes(fallbackTimeframes)
      
      if (fallbackSymbols.length > 0) {
        setSelectedSymbol(fallbackSymbols[0])
      }
      
      // Check if it's a network error or server error
      if (errorMsg.includes('Failed to fetch') || errorMsg.includes('NetworkError')) {
        setWarning('⚠️ Không thể kết nối đến server. Đang dùng danh sách mã mặc định. Vui lòng kiểm tra backend server.')
      } else {
        setWarning('⚠️ ' + errorMsg + '. Đang dùng danh sách mã mặc định.')
      }
    }
  }

  const handleFetchData = async () => {
    setError('')
    setSuccess('')
    setWarning('')
    setLoading(true)

    try {
      // Validate date range if using it
      let formattedStartDate = ''
      let formattedEndDate = ''
      
      if (useDateRange) {
        if (!startDate || !endDate) {
          throw new Error('Vui lòng chọn cả ngày bắt đầu và ngày kết thúc')
        }
        if (new Date(startDate) >= new Date(endDate)) {
          throw new Error('Ngày bắt đầu phải trước ngày kết thúc')
        }
        
        // Convert datetime-local format (YYYY-MM-DDTHH:mm) to backend format (YYYY-MM-DD HH:MM:SS)
        formattedStartDate = startDate.replace('T', ' ')
        if (formattedStartDate.split(':').length === 2) {
          formattedStartDate += ':00' // Add seconds if missing
        }
        
        formattedEndDate = endDate.replace('T', ' ')
        if (formattedEndDate.split(':').length === 2) {
          formattedEndDate += ':00' // Add seconds if missing
        }
      }

      setProgress({ isRunning: true, percent: 10, tested: 0, withTrades: 0 })

      const response = useDateRange
        ? await vnstockAPI.fetchData(selectedSymbol, selectedTimeframe, undefined, formattedStartDate, formattedEndDate)
        : await vnstockAPI.fetchData(selectedSymbol, selectedTimeframe, limit)

      if (response.status !== 'success') {
        const errorMsg = response.message || response.detail || 'Fetch failed'
        if (errorMsg.includes('vnstock') || errorMsg.includes('503') || errorMsg.includes('Service Unavailable')) {
          throw new Error('⚠️ vnstock library chưa được cài đặt hoặc API không khả dụng.\n\nVui lòng:\n1. Chạy: pip install vnstock trong thư mục backend\n2. Restart backend server\n3. Refresh browser và thử lại\n\nHoặc có thể do:\n- Không trong giờ giao dịch (9:00-15:00 giờ VN)\n- Lỗi mạng hoặc API tạm thời không khả dụng')
        }
        throw new Error(errorMsg)
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
      const dateInfo = useDateRange 
        ? `từ ${startDate} đến ${endDate}`
        : `(${limit} candles)`
      setSuccess(`✅ Tải thành công ${ohlcvData.length} candles từ ${selectedSymbol} ${dateInfo}`)
      
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
      <h2 className="text-2xl font-bold mb-4 text-gray-800">🇻🇳 Lấy Data từ Chứng Khoán Việt Nam</h2>

      {/* Asset Type Selection */}
      <div className="mb-4 p-4 bg-blue-50 rounded-lg border border-blue-200">
        <label className="block text-sm font-medium text-gray-700 mb-2">
          Loại Tài Sản
        </label>
        <div className="flex gap-4">
          <label className="flex items-center gap-2 cursor-pointer">
            <input
              type="radio"
              name="assetType"
              value="stock"
              checked={assetType === 'stock'}
              onChange={(e) => setAssetType(e.target.value as 'stock' | 'derivative')}
              disabled={loading}
              className="w-4 h-4 text-blue-600 border-gray-300 focus:ring-blue-500"
            />
            <span className="text-sm font-medium text-gray-700">📈 Cổ Phiếu</span>
          </label>
          <label className="flex items-center gap-2 cursor-pointer">
            <input
              type="radio"
              name="assetType"
              value="derivative"
              checked={assetType === 'derivative'}
              onChange={(e) => setAssetType(e.target.value as 'stock' | 'derivative')}
              disabled={loading}
              className="w-4 h-4 text-blue-600 border-gray-300 focus:ring-blue-500"
            />
            <span className="text-sm font-medium text-gray-700">📊 Phái Sinh (Futures)</span>
          </label>
        </div>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-4">
        {/* Symbol Selection */}
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-2">
            {assetType === 'derivative' ? 'Mã Phái Sinh' : 'Mã Cổ Phiếu'}
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
          <input
            type="number"
            min="50"
            max="10000"
            value={limit}
            onChange={(e) => setLimit(parseInt(e.target.value) || 1000)}
            disabled={loading || useDateRange}
            className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:border-blue-500 focus:outline-none disabled:bg-gray-100"
          />
        </div>
      </div>

      {/* Date Range Toggle */}
      <div className="mb-4 p-4 bg-gray-50 rounded-lg border border-gray-200">
        <label className="flex items-center gap-2 cursor-pointer mb-3">
          <input
            type="checkbox"
            checked={useDateRange}
            onChange={(e) => setUseDateRange(e.target.checked)}
            disabled={loading}
            className="w-4 h-4 text-blue-600 border-gray-300 rounded focus:ring-blue-500"
          />
          <span className="text-sm font-medium text-gray-700">Sử dụng khoảng thời gian (từ ngày đến ngày)</span>
        </label>

        {/* Date Range Inputs */}
        {useDateRange && (
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4 mt-3">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Từ ngày (Start Date)
              </label>
              <input
                type="datetime-local"
                value={startDate}
                onChange={(e) => setStartDate(e.target.value)}
                disabled={loading}
                className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:border-blue-500 focus:outline-none disabled:bg-gray-100"
              />
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Đến ngày (End Date)
              </label>
              <input
                type="datetime-local"
                value={endDate}
                onChange={(e) => setEndDate(e.target.value)}
                disabled={loading}
                className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:border-blue-500 focus:outline-none disabled:bg-gray-100"
              />
            </div>
          </div>
        )}
      </div>

      {/* Fetch Button */}
      <div className="mb-4">
        <button
          onClick={handleFetchData}
          disabled={loading || !selectedSymbol || !selectedTimeframe || (useDateRange && (!startDate || !endDate))}
          className="w-full px-6 py-3 bg-green-600 text-white rounded-lg font-semibold hover:bg-green-700 disabled:bg-gray-400 disabled:cursor-not-allowed transition shadow-md hover:shadow-lg"
        >
          {loading ? '⏳ Đang tải...' : '📥 Tải Data từ Chứng Khoán VN'}
        </button>
      </div>

      {/* Status Messages */}
      {warning && (
        <div className="mb-4 p-4 bg-yellow-50 border border-yellow-200 rounded-lg text-yellow-800">
          <div className="flex items-start gap-2">
            <span className="text-xl">⚠️</span>
            <div className="flex-1">
              <p className="font-semibold mb-1">Cảnh báo:</p>
              <p className="whitespace-pre-line text-sm">{warning}</p>
            </div>
          </div>
        </div>
      )}
      {error && (
        <div className="mb-4 p-4 bg-red-50 border border-red-200 rounded-lg text-red-700">
          <div className="flex items-start gap-2">
            <span className="text-xl">❌</span>
            <div className="flex-1">
              <p className="font-semibold mb-1">Lỗi:</p>
              <p className="whitespace-pre-line text-sm">{error}</p>
            </div>
          </div>
        </div>
      )}
      {success && (
        <div className="mb-4 p-4 bg-green-50 border border-green-200 rounded-lg text-green-700">
          <div className="flex items-start gap-2">
            <span className="text-xl">✅</span>
            <div className="flex-1">
              <p className="font-semibold mb-1">Thành công:</p>
              <p className="text-sm">{success}</p>
            </div>
          </div>
        </div>
      )}

      {/* Info */}
      <div className="text-sm text-gray-600 bg-green-50 p-4 rounded-lg border border-green-100">
        <p>💡 <strong>Tip:</strong> Chọn mã cổ phiếu, timeframe, và:</p>
        <ul className="list-disc list-inside mt-1 ml-2">
          <li>Số lượng candles (50-10000), hoặc</li>
          <li>Khoảng thời gian (từ ngày đến ngày)</li>
        </ul>
        <p className="mt-2">🔗 <strong>Mã cổ phiếu phổ biến:</strong> VCB, VIC, VHM, HPG, MSN, TCB, BID, CTG, VPB, SSI, FPT, VJC, v.v...</p>
        <p>⏱️ <strong>Timeframes:</strong> 1 phút, 5 phút, 15 phút, 30 phút, 1 giờ, 1 ngày, 1 tuần, 1 tháng</p>
        <p className="mt-2">📅 <strong>Date Range:</strong> Chọn checkbox để tải data theo khoảng thời gian cụ thể</p>
        <p className="mt-2 text-orange-600">⚠️ <strong>Lưu ý:</strong></p>
        <ul className="list-disc list-inside mt-1 ml-2 text-orange-600">
          <li>Cần cài đặt vnstock library: <code className="bg-gray-200 px-1 rounded">pip install vnstock</code></li>
          <li>Giờ giao dịch VN: 9:00 - 15:00 (giờ VN). Ngoài giờ giao dịch, API có thể không trả về data.</li>
          <li>Nếu gặp lỗi, hệ thống sẽ tự động dùng danh sách mã mặc định để UI vẫn hoạt động.</li>
        </ul>
      </div>
    </div>
  )
}
