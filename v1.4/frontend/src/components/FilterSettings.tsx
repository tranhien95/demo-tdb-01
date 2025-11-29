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
    <div className="bg-white dark:bg-gray-800 rounded-xl p-4 shadow-lg">
      <h3 className="text-lg font-bold mb-2">🔧 Optional Filters</h3>
      <p className="text-xs text-gray-600 mb-3">
        Các filter này sẽ loại bỏ tín hiệu không đạt điều kiện
      </p>

      <div className="grid grid-cols-3 md:grid-cols-5 gap-3">
        {/* ADX Filter */}
        <div className="p-3 border rounded-lg">
          <label className="flex items-center gap-1.5 mb-2">
            <input
              type="checkbox"
              checked={filters.enable_adx}
              onChange={(e) => updateFilter('enable_adx', e.target.checked)}
              className="w-4 h-4"
            />
            <span className="font-bold text-xs">💪 ADX</span>
          </label>
          {filters.enable_adx && (
            <div>
              <label className="block text-[10px] mb-0.5">Threshold</label>
              <input
                type="number"
                value={filters.adx_threshold}
                onChange={(e) => updateFilter('adx_threshold', parseFloat(e.target.value))}
                className="w-full px-2 py-1 text-xs border rounded"
                step="1"
              />
            </div>
          )}
        </div>

        {/* Volume Filter */}
        <div className="p-3 border rounded-lg">
          <label className="flex items-center gap-1.5 mb-2">
            <input
              type="checkbox"
              checked={filters.enable_volume}
              onChange={(e) => updateFilter('enable_volume', e.target.checked)}
              className="w-4 h-4"
            />
            <span className="font-bold text-xs">📦 Volume</span>
          </label>
          {filters.enable_volume && (
            <div>
              <label className="block text-[10px] mb-0.5">Multiplier</label>
              <input
                type="number"
                value={filters.volume_threshold}
                onChange={(e) => updateFilter('volume_threshold', parseFloat(e.target.value))}
                className="w-full px-2 py-1 text-xs border rounded"
                step="0.1"
              />
            </div>
          )}
        </div>

        {/* MA Filter */}
        <div className="p-3 border rounded-lg">
          <label className="flex items-center gap-1.5 mb-2">
            <input
              type="checkbox"
              checked={filters.enable_ma_filter}
              onChange={(e) => updateFilter('enable_ma_filter', e.target.checked)}
              className="w-4 h-4"
            />
            <span className="font-bold text-xs">〰️ MA</span>
          </label>
          {filters.enable_ma_filter && (
            <div>
              <label className="block text-[10px] mb-0.5">Period</label>
              <input
                type="number"
                value={filters.ma_period}
                onChange={(e) => updateFilter('ma_period', parseInt(e.target.value))}
                className="w-full px-2 py-1 text-xs border rounded"
                step="1"
              />
            </div>
          )}
        </div>

        {/* ATR Filter */}
        <div className="p-3 border rounded-lg">
          <label className="flex items-center gap-1.5 mb-2">
            <input
              type="checkbox"
              checked={filters.enable_atr_filter}
              onChange={(e) => updateFilter('enable_atr_filter', e.target.checked)}
              className="w-4 h-4"
            />
            <span className="font-bold text-xs">📏 ATR</span>
          </label>
          {filters.enable_atr_filter && (
            <div>
              <label className="block text-[10px] mb-0.5">Min ATR</label>
              <input
                type="number"
                value={filters.min_atr}
                onChange={(e) => updateFilter('min_atr', parseFloat(e.target.value))}
                className="w-full px-2 py-1 text-xs border rounded"
                step="0.0001"
              />
            </div>
          )}
        </div>

        {/* Trend Filter */}
        <div className="p-3 border rounded-lg">
          <label className="flex items-center gap-1.5 mb-2">
            <input
              type="checkbox"
              checked={filters.enable_trend_filter}
              onChange={(e) => updateFilter('enable_trend_filter', e.target.checked)}
              className="w-4 h-4"
            />
            <span className="font-bold text-xs">📈 Trend</span>
          </label>
          {filters.enable_trend_filter && (
            <div>
              <label className="block text-[10px] mb-0.5">MA Period</label>
              <input
                type="number"
                value={filters.trend_ma}
                onChange={(e) => updateFilter('trend_ma', parseInt(e.target.value))}
                className="w-full px-2 py-1 text-xs border rounded"
                step="1"
              />
            </div>
          )}
        </div>
      </div>
    </div>
  )
}
