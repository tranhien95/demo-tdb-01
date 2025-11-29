import React from 'react'
import { FilterConfig } from '../types'

interface Props {
  filters: FilterConfig
  onChange: (filters: FilterConfig) => void
}

export const FilterSettings: React.FC<Props> = ({ filters, onChange }) => {
  const updateFilter = (key: keyof FilterConfig, value: any) => {
    onChange({ ...filters, [key]: value })
  }

  return (
    <div className="bg-white dark:bg-gray-800 rounded-xl p-6 shadow-lg">
      <h3 className="text-xl font-bold mb-4">🔧 Optional Filters</h3>
      <p className="text-sm text-gray-600 mb-4">
        Các filter này sẽ loại bỏ tín hiệu không đạt điều kiện
      </p>

      <div className="space-y-4">
        {/* ADX Filter */}
        <div className="p-4 border rounded-lg">
          <label className="flex items-center gap-2 mb-3">
            <input
              type="checkbox"
              checked={filters.enable_adx}
              onChange={(e) => updateFilter('enable_adx', e.target.checked)}
              className="w-5 h-5"
            />
            <span className="font-bold">💪 ADX Filter (Trend Strength)</span>
          </label>
          {filters.enable_adx && (
            <div className="ml-7">
              <label className="block text-sm mb-1">ADX Threshold</label>
              <input
                type="number"
                value={filters.adx_threshold}
                onChange={(e) => updateFilter('adx_threshold', parseFloat(e.target.value))}
                className="w-full px-3 py-2 border rounded"
                step="1"
              />
            </div>
          )}
        </div>

        {/* Volume Filter */}
        <div className="p-4 border rounded-lg">
          <label className="flex items-center gap-2 mb-3">
            <input
              type="checkbox"
              checked={filters.enable_volume}
              onChange={(e) => updateFilter('enable_volume', e.target.checked)}
              className="w-5 h-5"
            />
            <span className="font-bold">📦 Volume Filter</span>
          </label>
          {filters.enable_volume && (
            <div className="ml-7">
              <label className="block text-sm mb-1">Volume Threshold (multiplier)</label>
              <input
                type="number"
                value={filters.volume_threshold}
                onChange={(e) => updateFilter('volume_threshold', parseFloat(e.target.value))}
                className="w-full px-3 py-2 border rounded"
                step="0.1"
              />
            </div>
          )}
        </div>

        {/* MA Filter */}
        <div className="p-4 border rounded-lg">
          <label className="flex items-center gap-2 mb-3">
            <input
              type="checkbox"
              checked={filters.enable_ma_filter}
              onChange={(e) => updateFilter('enable_ma_filter', e.target.checked)}
              className="w-5 h-5"
            />
            <span className="font-bold">〰️ MA Filter (Price vs MA)</span>
          </label>
          {filters.enable_ma_filter && (
            <div className="ml-7">
              <label className="block text-sm mb-1">MA Period</label>
              <input
                type="number"
                value={filters.ma_period}
                onChange={(e) => updateFilter('ma_period', parseInt(e.target.value))}
                className="w-full px-3 py-2 border rounded"
                step="1"
              />
            </div>
          )}
        </div>

        {/* ATR Filter */}
        <div className="p-4 border rounded-lg">
          <label className="flex items-center gap-2 mb-3">
            <input
              type="checkbox"
              checked={filters.enable_atr_filter}
              onChange={(e) => updateFilter('enable_atr_filter', e.target.checked)}
              className="w-5 h-5"
            />
            <span className="font-bold">📏 ATR Filter (Volatility)</span>
          </label>
          {filters.enable_atr_filter && (
            <div className="ml-7">
              <label className="block text-sm mb-1">Min ATR</label>
              <input
                type="number"
                value={filters.min_atr}
                onChange={(e) => updateFilter('min_atr', parseFloat(e.target.value))}
                className="w-full px-3 py-2 border rounded"
                step="0.0001"
              />
            </div>
          )}
        </div>

        {/* Trend Filter */}
        <div className="p-4 border rounded-lg">
          <label className="flex items-center gap-2 mb-3">
            <input
              type="checkbox"
              checked={filters.enable_trend_filter}
              onChange={(e) => updateFilter('enable_trend_filter', e.target.checked)}
              className="w-5 h-5"
            />
            <span className="font-bold">📈 Trend Filter (Long-term MA)</span>
          </label>
          {filters.enable_trend_filter && (
            <div className="ml-7">
              <label className="block text-sm mb-1">Trend MA Period</label>
              <input
                type="number"
                value={filters.trend_ma}
                onChange={(e) => updateFilter('trend_ma', parseInt(e.target.value))}
                className="w-full px-3 py-2 border rounded"
                step="1"
              />
            </div>
          )}
        </div>
      </div>
    </div>
  )
}
