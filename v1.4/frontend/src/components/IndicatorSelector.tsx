import React, { useState } from 'react'
import { AvailableIndicator } from '../types'

interface Props {
  availableIndicators: AvailableIndicator[]
  onAddIndicator: (type: string) => void
}

export const IndicatorSelector: React.FC<Props> = ({ availableIndicators, onAddIndicator }) => {
  const [searchTerm, setSearchTerm] = useState('')
  const [selectedCategory, setSelectedCategory] = useState<string>('all')

  const getIndicatorLag = (type: string): 'leading' | 'lagging' | 'hybrid' => {
    const typeLower = type.toLowerCase()
    // Leading indicators (predict future price movements)
    if (typeLower.includes('rsi') || typeLower.includes('stochastic') || typeLower.includes('cci') || 
        typeLower.includes('mfi') || typeLower.includes('volume') || typeLower.includes('obv') ||
        typeLower.includes('candlestick') || typeLower.includes('candle') || typeLower.includes('ict')) {
      return 'leading'
    }
    // Lagging indicators (confirm trends)
    if (typeLower.includes('ema') || typeLower.includes('sma') || typeLower.includes('triple') ||
        typeLower.includes('adx') || typeLower.includes('supertrend') || typeLower.includes('ichimoku')) {
      return 'lagging'
    }
    // Hybrid indicators (both leading and lagging properties)
    if (typeLower.includes('macd') || typeLower.includes('bollinger') || typeLower.includes('donchian') ||
        typeLower.includes('atr') || typeLower.includes('momentum') || typeLower.includes('roc') || 
        typeLower.includes('awesome') || typeLower.includes('pivot') || typeLower.includes('fibonacci') || 
        typeLower.includes('fib') || typeLower.includes('rvi')) {
      return 'hybrid'
    }
    return 'hybrid'
  }

  const getIndicatorCategory = (type: string): string => {
    const typeLower = type.toLowerCase()
    
    // Trend Indicators - Xác định hướng xu hướng
    if (typeLower.includes('ema') || typeLower.includes('sma') || typeLower.includes('triple') ||
        typeLower.includes('adx') || typeLower.includes('supertrend') || typeLower.includes('ichimoku')) {
      return 'trend'
    }
    
    // Momentum Indicators - Đo tốc độ và sức mạnh thay đổi giá
    if (typeLower.includes('rsi') || typeLower.includes('macd') || typeLower.includes('stochastic') || 
        typeLower.includes('cci') || typeLower.includes('momentum') || typeLower.includes('roc') || 
        typeLower.includes('awesome') || typeLower.includes('rvi')) {
      return 'momentum'
    }
    
    // Volume Indicators - Phân tích khối lượng giao dịch
    if (typeLower.includes('volume') || typeLower.includes('obv') || typeLower.includes('vroc') || 
        typeLower.includes('mfi')) {
      return 'volume'
    }
    
    // Volatility Indicators - Đo biến động giá
    if (typeLower.includes('bollinger') || typeLower.includes('donchian') || typeLower.includes('atr')) {
      return 'volatility'
    }
    
    // Support/Resistance - Xác định vùng giá quan trọng
    if (typeLower.includes('pivot') || typeLower.includes('fibonacci') || typeLower.includes('fib')) {
      return 'support_resistance'
    }
    
    // Pattern Recognition
    if (typeLower.includes('candlestick') || typeLower.includes('candle')) {
      return 'patterns'
    }
    
    // ICT Concepts
    if (typeLower.includes('ict')) {
      return 'ict'
    }
    
    return 'other'
  }

  const getIndicatorIcon = (type: string) => {
    const typeLower = type.toLowerCase()
    if (typeLower.includes('rsi')) return '📊'
    if (typeLower.includes('macd')) return '📈'
    if (typeLower.includes('ema') || typeLower.includes('sma')) return '〰️'
    if (typeLower.includes('triple')) return '〰️〰️〰️'
    if (typeLower.includes('bollinger')) return '🎯'
    if (typeLower.includes('stochastic')) return '⚡'
    if (typeLower.includes('adx')) return '💪'
    if (typeLower.includes('volume')) return '📦'
    if (typeLower.includes('atr')) return '📏'
    if (typeLower.includes('supertrend')) return '🚀'
    if (typeLower.includes('pivot')) return '🎲'
    if (typeLower.includes('fibonacci') || typeLower.includes('fib')) return '🔢'
    if (typeLower.includes('ichimoku')) return '☁️'
    if (typeLower.includes('candlestick') || typeLower.includes('candle')) return '🕯️'
    if (typeLower.includes('ict')) return '💎'
    return '📉'
  }

  const categories = [
    { id: 'all', label: 'Tất cả', labelEn: 'All', icon: '📋', desc: 'Tất cả chỉ báo' },
    { id: 'leading', label: 'Dự đoán', labelEn: 'Leading', icon: '🔮', type: 'lag', desc: 'Dự đoán xu hướng trước khi xảy ra' },
    { id: 'lagging', label: 'Xác nhận', labelEn: 'Lagging', icon: '🔄', type: 'lag', desc: 'Xác nhận xu hướng đã xảy ra' },
    { id: 'hybrid', label: 'Kết hợp', labelEn: 'Hybrid', icon: '⚖️', type: 'lag', desc: 'Kết hợp cả dự đoán và xác nhận' },
    { id: 'trend', label: 'Xu hướng', labelEn: 'Trend', icon: '📈', desc: 'Xác định hướng xu hướng thị trường (MA, ADX, Supertrend)' },
    { id: 'momentum', label: 'Động lượng', labelEn: 'Momentum', icon: '⚡', desc: 'Đo tốc độ & sức mạnh thay đổi giá (RSI, MACD, Stochastic)' },
    { id: 'volume', label: 'Khối lượng', labelEn: 'Volume', icon: '📦', desc: 'Phân tích khối lượng giao dịch (MFI, OBV, VROC)' },
    { id: 'volatility', label: 'Biến động', labelEn: 'Volatility', icon: '📏', desc: 'Đo biến động giá (Bollinger, ATR)' },
    { id: 'support_resistance', label: 'Hỗ trợ/Kháng cự', labelEn: 'S/R', icon: '🎲', desc: 'Vùng giá quan trọng có thể đảo chiều (Pivot, Fibonacci)' },
    { id: 'patterns', label: 'Mô hình nến', labelEn: 'Patterns', icon: '🕯️', desc: 'Nhận diện mô hình nến Nhật' },
    { id: 'ict', label: 'ICT', labelEn: 'ICT', icon: '💎', desc: 'Inner Circle Trader Concepts' },
  ]

  const filteredIndicators = availableIndicators.filter(ind => {
    const matchesSearch = ind.type.toLowerCase().includes(searchTerm.toLowerCase()) ||
      ind.description.toLowerCase().includes(searchTerm.toLowerCase())
    
    // Check if filtering by lag type
    if (selectedCategory === 'leading' || selectedCategory === 'lagging' || selectedCategory === 'hybrid') {
      return matchesSearch && getIndicatorLag(ind.type) === selectedCategory
    }
    
    const matchesCategory = selectedCategory === 'all' || getIndicatorCategory(ind.type) === selectedCategory
    return matchesSearch && matchesCategory
  })

  return (
    <div className="bg-white dark:bg-gray-800 rounded-xl p-4 shadow-lg">
      <h3 className="text-lg font-bold mb-2">🔍 Available Indicators ({availableIndicators.length})</h3>
      
      {/* Category Filter */}
      <div className="flex flex-wrap gap-1 mb-3">
        {categories.map(cat => (
          <button
            key={cat.id}
            onClick={() => setSelectedCategory(cat.id)}
            className={`px-2 py-1 text-xs rounded transition-all ${
              selectedCategory === cat.id
                ? cat.type === 'lag' 
                  ? 'bg-purple-500 text-white font-bold'
                  : 'bg-blue-500 text-white font-bold'
                : 'bg-gray-200 dark:bg-gray-700 hover:bg-gray-300 dark:hover:bg-gray-600'
            }`}
            title={cat.desc}
          >
            {cat.icon} {cat.label} <span className="opacity-60">({cat.labelEn})</span>
          </button>
        ))}
      </div>

      {/* Search */}
      <input
        type="text"
        placeholder="Search..."
        value={searchTerm}
        onChange={(e) => setSearchTerm(e.target.value)}
        className="w-full px-3 py-1.5 text-sm border rounded-lg mb-3"
      />

      {/* Indicators Grid */}
      <div className="grid grid-cols-2 md:grid-cols-4 lg:grid-cols-8 gap-2 max-h-[250px] overflow-y-auto">
        {filteredIndicators.map((indicator) => {
          const lag = getIndicatorLag(indicator.type)
          const lagColor = lag === 'leading' ? 'border-l-4 border-l-green-500' : 
                          lag === 'lagging' ? 'border-l-4 border-l-orange-500' : 
                          'border-l-4 border-l-purple-500'
          return (
            <button
              key={indicator.type}
              onClick={() => onAddIndicator(indicator.type)}
              className={`p-2 border-2 border-gray-300 rounded-lg hover:border-blue-500 hover:bg-blue-50 dark:hover:bg-blue-900/20 transition-all text-left ${lagColor}`}
              title={`${lag.charAt(0).toUpperCase() + lag.slice(1)} indicator`}
            >
              <div className="text-xl mb-1">{getIndicatorIcon(indicator.type)}</div>
              <div className="font-bold text-xs mb-0.5">{indicator.type}</div>
              <div className="text-[10px] text-gray-600 dark:text-gray-400 line-clamp-1">
                {indicator.description}
              </div>
            </button>
          )
        })}
      </div>

      {filteredIndicators.length === 0 && (
        <div className="text-center py-8 text-gray-500">
          No indicators found
        </div>
      )}
    </div>
  )
}
