import React, { useState } from 'react'
import { IndicatorConfig } from '../types'

interface Props {
  indicator: IndicatorConfig
  onSave: (config: IndicatorConfig) => void
  onCancel: () => void
}

export const IndicatorConfigModal: React.FC<Props> = ({ indicator, onSave, onCancel }) => {
  const [config, setConfig] = useState<IndicatorConfig>(indicator)

  const updateConfigValue = (key: string, value: any) => {
    setConfig(prev => ({
      ...prev,
      config: {
        ...prev.config,
        [key]: value
      }
    }))
  }

  const renderConfigInput = (key: string, value: any) => {
    const inputType = typeof value === 'number' ? 'number' : 'text'
    
    return (
      <div key={key} className="mb-4">
        <label className="block text-sm font-bold mb-2 capitalize">
          {key.replace(/_/g, ' ')}
        </label>
        {typeof value === 'boolean' ? (
          <input
            type="checkbox"
            checked={value}
            onChange={(e) => updateConfigValue(key, e.target.checked)}
            className="w-5 h-5"
          />
        ) : Array.isArray(value) ? (
          <input
            type="text"
            value={value.join(', ')}
            onChange={(e) => {
              const arr = e.target.value.split(',').map(v => parseFloat(v.trim())).filter(v => !isNaN(v))
              updateConfigValue(key, arr)
            }}
            placeholder="Comma-separated values (e.g., 0.236, 0.382, 0.5)"
            className="w-full px-4 py-2 border rounded-lg"
          />
        ) : (
          <input
            type={inputType}
            value={value}
            onChange={(e) => updateConfigValue(
              key,
              inputType === 'number' ? parseFloat(e.target.value) : e.target.value
            )}
            className="w-full px-4 py-2 border rounded-lg"
            step={inputType === 'number' ? '0.1' : undefined}
          />
        )}
      </div>
    )
  }

  return (
    <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50">
      <div className="bg-white dark:bg-gray-800 rounded-xl p-6 w-[500px] max-h-[80vh] overflow-auto shadow-2xl">
        <h3 className="text-xl font-bold mb-4">⚙️ Configure {config.type}</h3>
        
        <div className="mb-4">
          <label className="block text-sm font-bold mb-2">Weight</label>
          <input
            type="number"
            value={config.weight}
            onChange={(e) => setConfig(prev => ({ ...prev, weight: parseFloat(e.target.value) || 1 }))}
            className="w-full px-4 py-2 border rounded-lg"
            min="0.1"
            step="0.1"
          />
        </div>

        <div className="mb-4">
          <label className="flex items-center gap-2">
            <input
              type="checkbox"
              checked={config.enabled}
              onChange={(e) => setConfig(prev => ({ ...prev, enabled: e.target.checked }))}
              className="w-5 h-5"
            />
            <span className="font-bold">Enabled</span>
          </label>
        </div>

        <hr className="my-4" />

        <h4 className="font-bold mb-4">Indicator Parameters</h4>
        {Object.entries(config.config).map(([key, value]) => renderConfigInput(key, value))}

        <div className="flex gap-2 mt-6">
          <button className="btn-primary flex-1" onClick={() => onSave(config)}>
            ✅ Save
          </button>
          <button className="btn-secondary flex-1" onClick={onCancel}>
            Cancel
          </button>
        </div>
      </div>
    </div>
  )
}
