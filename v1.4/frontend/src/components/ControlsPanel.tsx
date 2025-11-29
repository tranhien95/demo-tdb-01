import React from 'react'
import { useOptimizerStore } from '../store/optimizerStore'

export const ControlsPanel: React.FC = () => {
  const { params, setParams } = useOptimizerStore()

  const handleChange = (key: keyof typeof params, value: number | boolean) => {
    setParams({ [key]: value })
  }

  return (
    <div className="card">
      <h2 className="text-2xl font-bold text-primary mb-6">⚙️ Cấu Hình Tham Số</h2>
      
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
        <div>
          <label className="block text-secondary font-bold mb-2">💰 Vốn Hiện Có (USDT)</label>
          <input
            type="number"
            className="input-field"
            value={params.capital}
            onChange={(e) => handleChange('capital', parseFloat(e.target.value))}
          />
        </div>

        <div>
          <label className="block text-secondary font-bold mb-2">📈 Min Win Rate (%)</label>
          <input
            type="number"
            className="input-field"
            value={params.minWinRate}
            onChange={(e) => handleChange('minWinRate', parseFloat(e.target.value))}
          />
        </div>

        <div>
          <label className="block text-secondary font-bold mb-2">💹 Min Profit (%)</label>
          <input
            type="number"
            className="input-field"
            value={params.minProfit}
            onChange={(e) => handleChange('minProfit', parseFloat(e.target.value))}
          />
        </div>

        <div>
          <label className="block text-secondary font-bold mb-2">🔢 Min Trades</label>
          <input
            type="number"
            className="input-field"
            value={params.minTrades}
            onChange={(e) => handleChange('minTrades', parseInt(e.target.value))}
          />
        </div>

        <div>
          <label className="block text-secondary font-bold mb-2">📏 Min Combo Size</label>
          <input
            type="number"
            className="input-field"
            min="2"
            max="5"
            value={params.minComboSize}
            onChange={(e) => handleChange('minComboSize', parseInt(e.target.value))}
          />
        </div>

        <div>
          <label className="block text-secondary font-bold mb-2">📏 Max Combo Size</label>
          <input
            type="number"
            className="input-field"
            min="2"
            max="5"
            value={params.maxComboSize}
            onChange={(e) => handleChange('maxComboSize', parseInt(e.target.value))}
          />
        </div>

        <div>
          <label className="block text-secondary font-bold mb-2">📊 Threshold %</label>
          <input
            type="number"
            className="input-field"
            min="50"
            max="100"
            value={params.threshold}
            onChange={(e) => handleChange('threshold', parseInt(e.target.value))}
          />
        </div>

        <div>
          <label className="block text-secondary font-bold mb-2">💰 Risk Per Trade (%)</label>
          <input
            type="number"
            className="input-field"
            step="0.5"
            value={params.riskPercent}
            onChange={(e) => handleChange('riskPercent', parseFloat(e.target.value))}
          />
        </div>

        <div>
          <label className="block text-secondary font-bold mb-2">📈 Risk/Reward Ratio</label>
          <input
            type="number"
            className="input-field"
            step="0.5"
            value={params.rrRatio}
            onChange={(e) => handleChange('rrRatio', parseFloat(e.target.value))}
          />
        </div>

        <div>
          <label className="block text-secondary font-bold mb-2">🛑 Stop Loss (%)</label>
          <input
            type="number"
            className="input-field"
            step="0.1"
            value={params.slPercent}
            onChange={(e) => handleChange('slPercent', parseFloat(e.target.value))}
          />
        </div>

        <div>
          <label className="block text-secondary font-bold mb-2">📍 Candle Confirmation</label>
          <select
            className="input-field"
            value={params.candleConfirmation}
            onChange={(e) => handleChange('candleConfirmation', parseInt(e.target.value))}
          >
            <option value="1">1 Candle (Nhạy)</option>
            <option value="2">2 Candles (Bình thường)</option>
            <option value="3">3 Candles (An toàn)</option>
            <option value="4">4 Candles (Rất an toàn)</option>
          </select>
        </div>

        <div>
          <label className="block text-secondary font-bold mb-2">🎯 Min Signal Strength (%)</label>
          <input
            type="number"
            className="input-field"
            min="50"
            max="100"
            value={params.minSignalStrength}
            onChange={(e) => handleChange('minSignalStrength', parseInt(e.target.value))}
          />
        </div>
      </div>

      <div className="mt-6 p-4 bg-primary/10 rounded-lg border-l-4 border-primary">
        <div className="font-bold text-secondary mb-2">💎 Recommended Quick Test:</div>
        <div className="text-sm text-gray-300">
          Set Combo Size: 2-2 | Threshold: 70 | SL: 0.75% | RR: 2.0 | Disable Filters
        </div>
        <div className="text-xs text-gray-400 mt-1">
          Expected: 10 trades, 60% WR, +6.00% profit
        </div>
      </div>

      <div className="mt-6">
        <h3 className="text-lg font-bold text-secondary mb-3">🔧 Advanced Filters</h3>
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          <div className="flex items-center space-x-3">
            <input
              type="checkbox"
              className="w-5 h-5"
              checked={params.enableADXFilter}
              onChange={(e) => handleChange('enableADXFilter', e.target.checked)}
            />
            <label className="text-gray-300">ADX Filter (Trend Strength)</label>
          </div>

          <div className="flex items-center space-x-3">
            <input
              type="checkbox"
              className="w-5 h-5"
              checked={params.enableMAFilter}
              onChange={(e) => handleChange('enableMAFilter', e.target.checked)}
            />
            <label className="text-gray-300">MA Filter (Price above MA50)</label>
          </div>

          <div className="flex items-center space-x-3">
            <input
              type="checkbox"
              className="w-5 h-5"
              checked={params.enableVolumeFilter}
              onChange={(e) => handleChange('enableVolumeFilter', e.target.checked)}
            />
            <label className="text-gray-300">Volume Filter</label>
          </div>

          <div className="flex items-center space-x-3">
            <input
              type="checkbox"
              className="w-5 h-5"
              checked={params.enableTrendFilter}
              onChange={(e) => handleChange('enableTrendFilter', e.target.checked)}
            />
            <label className="text-gray-300">Trend Filter (MA200)</label>
          </div>
        </div>
      </div>
    </div>
  )
}
