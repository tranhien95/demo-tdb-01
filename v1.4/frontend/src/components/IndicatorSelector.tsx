import React, { useState } from 'react'
import { AvailableIndicator } from '../types'

interface Props {
  availableIndicators: AvailableIndicator[]
  onAddIndicator: (type: string) => void
}

export const IndicatorSelector: React.FC<Props> = ({ availableIndicators, onAddIndicator }) => {
  const [searchTerm, setSearchTerm] = useState('')

  const filteredIndicators = availableIndicators.filter(ind =>
    ind.type.toLowerCase().includes(searchTerm.toLowerCase()) ||
    ind.description.toLowerCase().includes(searchTerm.toLowerCase())
  )

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

  return (
    <div className="bg-white dark:bg-gray-800 rounded-xl p-6 shadow-lg">
      <h3 className="text-xl font-bold mb-4">🔍 Available Indicators ({availableIndicators.length})</h3>
      
      <input
        type="text"
        placeholder="Search indicators..."
        value={searchTerm}
        onChange={(e) => setSearchTerm(e.target.value)}
        className="w-full px-4 py-2 border rounded-lg mb-4"
      />

      <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-4 gap-3 max-h-[400px] overflow-y-auto">
        {filteredIndicators.map((indicator) => (
          <button
            key={indicator.type}
            onClick={() => onAddIndicator(indicator.type)}
            className="p-4 border-2 border-gray-300 rounded-lg hover:border-blue-500 hover:bg-blue-50 dark:hover:bg-blue-900/20 transition-all text-left"
          >
            <div className="text-2xl mb-2">{getIndicatorIcon(indicator.type)}</div>
            <div className="font-bold text-sm mb-1">{indicator.type}</div>
            <div className="text-xs text-gray-600 dark:text-gray-400 line-clamp-2">
              {indicator.description}
            </div>
          </button>
        ))}
      </div>
    </div>
  )
}
