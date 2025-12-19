import React, { useState, useEffect } from 'react'
import { dnseAPI } from '../services/api'
import { useOptimizerStore } from '../store/optimizerStore'
import { OHLCV } from '../types'

export const DNSEDataFetcher: React.FC = () => {
  const { setCsvData, setProgress } = useOptimizerStore()
  
  const [symbols, setSymbols] = useState<string[]>([])
  const [timeframes, setTimeframes] = useState<Record<string, string>>({})
  
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

  // Initialize default dates: 1 year ago to now
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
  const fallbackSymbols = ['VCB', 'VIC', 'VHM', 'VRE', 'VNM', 'HPG', 'MSN', 'TCB', 'BID', 'CTG', 'VPB', 'SSI', 'FPT', 'VJC', 'MWG', 'PNJ', 'GAS', 'PLX', 'POW', 'GVR']
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

  // Set default dates when useDateRange is enabled
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
        dnseAPI.getSymbols(),
        dnseAPI.getTimeframes()
      ])
      
      if (symbolsRes.status === 'warning' || timeframesRes.status === 'warning') {
        const warningMsg = symbolsRes.message || timeframesRes.message || 'DNSE/yfinance API tạm thời không khả dụng'
        setWarning(warningMsg)
      } else if (symbolsRes.status === 'success' || !symbolsRes.status) {
        setWarning('')
      }
      
      setSymbols(symbolsRes.symbols || fallbackSymbols)
      setTimeframes(timeframesRes.timeframes || fallbackTimeframes)
    } catch (err: any) {
      const errorMsg = err.message || String(err)
      setSymbols(fallbackSymbols)
      setTimeframes(fallbackTimeframes)
      
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
      let formattedStartDate = ''
      let formattedEndDate = ''
      
      if (useDateRange) {
        if (!startDate || !endDate) {
          throw new Error('Vui lòng chọn cả ngày bắt đầu và ngày kết thúc')
        }
        if (new Date(startDate) >= new Date(endDate)) {
          throw new Error('Ngày bắt đầu phải trước ngày kết thúc')
        }
        
        formattedStartDate = startDate.replace('T', ' ')
        if (formattedStartDate.split(':').length === 2) {
          formattedStartDate += ':00'
        }
        
        formattedEndDate = endDate.replace('T', ' ')
        if (formattedEndDate.split(':').length === 2) {
          formattedEndDate += ':00'
        }
      }

      setProgress({ isRunning: true, percent: 10, tested: 0, withTrades: 0 })

      const response = useDateRange
        ? await dnseAPI.fetchData(selectedSymbol, selectedTimeframe, undefined, formattedStartDate, formattedEndDate)
        : await dnseAPI.fetchData(selectedSymbol, selectedTimeframe, limit)

      if (response.status !== 'success') {
        const errorMsg = response.message || response.detail || 'Fetch failed'
        throw new Error(errorMsg)
      }

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
      const errMsg = (err as Error).message
      setError('❌ Lỗi: ' + errMsg)
      setProgress({ isRunning: false, percent: 0, tested: 0, withTrades: 0 })
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="p-6 bg-white rounded-lg shadow-md border border-gray-200">
      <h2 className="text-2xl font-bold mb-4 text-gray-800">📈 Lấy Data từ DNSE/YFinance</h2>

      <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-4">
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-2">
            Mã Cổ Phiếu
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

      <div className="mb-4">
        <button
          onClick={handleFetchData}
          disabled={loading || !selectedSymbol || !selectedTimeframe || (useDateRange && (!startDate || !endDate))}
          className="w-full px-6 py-3 bg-purple-600 text-white rounded-lg font-semibold hover:bg-purple-700 disabled:bg-gray-400 disabled:cursor-not-allowed transition shadow-md hover:shadow-lg"
        >
          {loading ? '⏳ Đang tải...' : '📥 Tải Data từ DNSE/YFinance'}
        </button>
      </div>

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

      <div className="text-sm text-gray-600 bg-purple-50 p-4 rounded-lg border border-purple-100">
        <p>💡 <strong>Tip:</strong> DNSE/YFinance hỗ trợ một số mã cổ phiếu VN (với .VN suffix)</p>
        <ul className="list-disc list-inside mt-1 ml-2">
          <li>Số lượng candles (50-10000), hoặc</li>
          <li>Khoảng thời gian (từ ngày đến ngày)</li>
        </ul>
        <p className="mt-2">🔗 <strong>Mã cổ phiếu phổ biến:</strong> VCB, VIC, VHM, HPG, MSN, TCB, BID, CTG, VPB, SSI, FPT, VJC, v.v...</p>
        <p>⏱️ <strong>Timeframes:</strong> 1 phút, 5 phút, 15 phút, 30 phút, 1 giờ, 1 ngày, 1 tuần, 1 tháng</p>
        <p className="mt-2">📅 <strong>Date Range:</strong> Chọn checkbox để tải data theo khoảng thời gian cụ thể</p>
        <p className="mt-2 text-orange-600">⚠️ <strong>Lưu ý:</strong></p>
        <ul className="list-disc list-inside mt-1 ml-2 text-orange-600">
          <li>YFinance có thể không hỗ trợ đầy đủ mã VN</li>
          <li>Một số mã có thể cần thêm .VN suffix (VD: VCB.VN)</li>
          <li>Nếu không tìm thấy data, thử mã khác hoặc dùng vnstock</li>
        </ul>
      </div>
    </div>
  )
}

