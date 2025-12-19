import React, { useState, useEffect } from 'react'
import { Strategy, AvailableIndicator, IndicatorConfig, BacktestResult, StrategyListItem } from '../types'
import { strategyAPI } from '../services/api'
import { IndicatorSelector } from './IndicatorSelector'
import { IndicatorConfigModal } from './IndicatorConfigModal'
import { FilterSettings } from './FilterSettings'
import { StrategyResults } from './StrategyResults'
import { StrategyChart } from './StrategyChart'
import { ProgressBar } from './ProgressBar'
import { useOptimizerStore } from '../store/optimizerStore'
import { Layout } from './Layout'

export const StrategyBuilder: React.FC = () => {
  const { csvData } = useOptimizerStore()
  
  const [availableIndicators, setAvailableIndicators] = useState<AvailableIndicator[]>([])
  const [strategy, setStrategy] = useState<Strategy>({
    name: 'My Strategy',
    description: '',
    indicators: [],
    signal_logic: { 
      threshold_percent: 60,
      enable_partial_tp_close: false,
      tp_close_pct: 0.5,
      enable_trailing_stop: true,
      trailing_activation_r: 1.0,
      trailing_multiplier: 1.5
    },
    filters: {
      enable_adx: false,
      adx_threshold: 25,
      enable_volume: false,
      volume_threshold: 1.5,
      enable_ma_filter: false,
      ma_period: 50,
      enable_atr_filter: false,
      min_atr: 0.0005,
      enable_trend_filter: false,
      trend_ma: 200
    },
     risk_management: {
       risk_percent: 10.0,
       reward_ratio: 1.0,
       stop_loss_percent: 5.0,
       capital: 1000,
       margin: undefined
     }
  })
  
  const [editingIndicator, setEditingIndicator] = useState<{ index: number; config: IndicatorConfig } | null>(null)
  const [backtestResult, setBacktestResult] = useState<BacktestResult | null>(null)
  const [isRunning, setIsRunning] = useState(false)
  const [backtestProgress, setBacktestProgress] = useState({ progress: 0, tested: 0, withTrades: 0, timeElapsed: 0 })
  const [preview, setPreview] = useState<{ total: number; long: number; short: number } | null>(null)
  const [savedStrategies, setSavedStrategies] = useState<StrategyListItem[]>([])
  const [showSaveModal, setShowSaveModal] = useState(false)
  const [showLoadModal, setShowLoadModal] = useState(false)

  useEffect(() => {
    loadAvailableIndicators()
    loadSavedStrategies()
  }, [])

  const loadAvailableIndicators = async () => {
    try {
      const data = await strategyAPI.listIndicators()
      setAvailableIndicators(data.indicators)
    } catch (error) {
      console.error('Failed to load indicators:', error)
    }
  }

  const loadSavedStrategies = async () => {
    try {
      const data = await strategyAPI.listStrategies()
      setSavedStrategies(data.strategies)
    } catch (error) {
      console.error('Failed to load strategies:', error)
    }
  }

  const addIndicator = (type: string) => {
    const indicator = availableIndicators.find(ind => ind.type === type)
    if (!indicator) return

    const newIndicator: IndicatorConfig = {
      type,
      config: { ...indicator.default_config },
      weight: 1,
      enabled: true
    }

    setStrategy(prev => ({
      ...prev,
      indicators: [...prev.indicators, newIndicator]
    }))
  }

  const removeIndicator = (index: number) => {
    setStrategy(prev => ({
      ...prev,
      indicators: prev.indicators.filter((_, i) => i !== index)
    }))
  }

  const toggleIndicator = (index: number) => {
    setStrategy(prev => ({
      ...prev,
      indicators: prev.indicators.map((ind, i) =>
        i === index ? { ...ind, enabled: !ind.enabled } : ind
      )
    }))
  }

  const updateIndicatorWeight = (index: number, weight: number) => {
    setStrategy(prev => ({
      ...prev,
      indicators: prev.indicators.map((ind, i) =>
        i === index ? { ...ind, weight } : ind
      )
    }))
  }

  const openEditModal = (index: number) => {
    setEditingIndicator({ index, config: { ...strategy.indicators[index] } })
  }

  const saveIndicatorConfig = (config: IndicatorConfig) => {
    if (editingIndicator === null) return

    setStrategy(prev => ({
      ...prev,
      indicators: prev.indicators.map((ind, i) =>
        i === editingIndicator.index ? config : ind
      )
    }))
    setEditingIndicator(null)
  }

  const runPreview = async () => {
    if (!csvData || csvData.length < 100) {
      alert('⚠️ Cần upload CSV trước!')
      return
    }

    if (strategy.indicators.filter(ind => ind.enabled).length === 0) {
      alert('⚠️ Cần ít nhất 1 indicator được bật!')
      return
    }

    try {
      const data = await strategyAPI.previewSignals({
        strategy,
        ohlcv_data: csvData
      })
      setPreview(data)
    } catch (error) {
      alert('❌ Preview failed: ' + (error as Error).message)
    }
  }

  const runBacktest = async () => {
    if (!csvData || csvData.length < 100) {
      alert('⚠️ Cần upload CSV trước!')
      return
    }

    if (strategy.indicators.filter(ind => ind.enabled).length === 0) {
      alert('⚠️ Cần ít nhất 1 indicator được bật!')
      return
    }

    setIsRunning(true)
    setBacktestResult(null)
    setBacktestProgress({ progress: 0, tested: 0, withTrades: 0, timeElapsed: 0 })

    // Simulate progress
    let progress = 0
    let tested = 0
    const progressInterval = setInterval(() => {
      if (progress < 95) {
        progress += Math.random() * 30
        tested += Math.floor(Math.random() * 50)
        setBacktestProgress(prev => ({
          progress: Math.min(progress, 95),
          tested: tested,
          withTrades: Math.floor(tested * 0.3),
          timeElapsed: prev.timeElapsed + 1
        }))
      }
    }, 500)

    try {
      const result = await strategyAPI.backtestStrategy({
        strategy,
        ohlcv_data: csvData
      })
      clearInterval(progressInterval)
      setBacktestProgress({ progress: 100, tested, withTrades: Math.floor(tested * 0.3), timeElapsed: backtestProgress.timeElapsed })
      setBacktestResult(result)
    } catch (error) {
      clearInterval(progressInterval)
      alert('❌ Backtest failed: ' + (error as Error).message)
    } finally {
      setIsRunning(false)
    }
  }

  const saveStrategy = async () => {
    if (!strategy.name.trim()) {
      alert('⚠️ Nhập tên strategy!')
      return
    }

    try {
      await strategyAPI.saveStrategy(strategy)
      alert('✅ Đã lưu strategy!')
      setShowSaveModal(false)
      loadSavedStrategies()
    } catch (error) {
      alert('❌ Save failed: ' + (error as Error).message)
    }
  }

  const loadStrategy = async (name: string) => {
    try {
      const loaded = await strategyAPI.loadStrategy(name)
      setStrategy(loaded)
      setShowLoadModal(false)
      alert('✅ Đã load strategy!')
    } catch (error) {
      alert('❌ Load failed: ' + (error as Error).message)
    }
  }

  const deleteStrategy = async (name: string) => {
    if (!confirm(`Xóa strategy "${name}"?`)) return

    try {
      await strategyAPI.deleteStrategy(name)
      alert('✅ Đã xóa!')
      loadSavedStrategies()
    } catch (error) {
      alert('❌ Delete failed: ' + (error as Error).message)
    }
  }

  const exportPineScript = async () => {
    try {
      // Get version from strategy name or use default
      const version = '1.0.0' // Can be enhanced to get from strategy metadata
      
      // Include backtest result if available
      const result = await strategyAPI.exportPineScript(
        strategy, 
        backtestResult, 
        version
      )
      
      // Download as file
      const blob = new Blob([result.code], { type: 'text/plain' })
      const url = URL.createObjectURL(blob)
      const a = document.createElement('a')
      a.href = url
      a.download = `${result.strategy_name}_v${result.version || '1.0.0'}.pine`
      a.click()
      URL.revokeObjectURL(url)
      
      alert('✅ Đã export Pine Script với version và backtest results!')
    } catch (error) {
      alert('❌ Export failed: ' + (error as Error).message)
    }
  }

  // Load optimized combo from localStorage (saved by Combo Optimizer)
  useEffect(() => {
    const savedCombo = localStorage.getItem('optimizedCombo')
    if (savedCombo) {
      try {
        const combo = JSON.parse(savedCombo)
        const newIndicators: IndicatorConfig[] = combo.indicators.map((ind: any) => ({
          type: ind.type,
          config: ind.config || {},
          weight: ind.weight || 1.0,
          enabled: true
        }))

        setStrategy(prev => ({
          ...prev,
          indicators: newIndicators,
          signal_logic: {
            ...prev.signal_logic,
            threshold_percent: combo.threshold || 70
          }
        }))

        localStorage.removeItem('optimizedCombo')
        alert('✅ Đã load combo từ Combo Optimizer!')
      } catch (e) {
        console.error('Failed to load optimized combo:', e)
      }
    }
  }, [])

  const totalWeight = strategy.indicators
    .filter(ind => ind.enabled)
    .reduce((sum, ind) => sum + ind.weight, 0)

  return (
    <Layout
      title="🎯 Strategy Builder"
      description="Xây dựng chiến lược tùy chỉnh với weighted indicators"
      actions={
        <>
          <button className="btn-secondary" onClick={() => setShowLoadModal(true)}>
            📂 Load
          </button>
          <button className="btn-secondary" onClick={() => setShowSaveModal(true)}>
            💾 Save
          </button>
          <button className="btn-secondary" onClick={exportPineScript}>
            📤 Export Pine
          </button>
        </>
      }
    >

      {/* Strategy Name & Description */}
      <div className="bg-white dark:bg-gray-800 rounded-xl p-4 shadow-lg">
        <div className="grid grid-cols-2 gap-4">
          <div>
            <label className="block text-xs font-bold mb-1">Strategy Name</label>
            <input
              type="text"
              value={strategy.name}
              onChange={(e) => setStrategy(prev => ({ ...prev, name: e.target.value }))}
              className="w-full px-3 py-1.5 text-sm border rounded-lg"
              placeholder="My Strategy"
            />
          </div>
          <div>
            <label className="block text-xs font-bold mb-1">Description</label>
            <input
              type="text"
              value={strategy.description}
              onChange={(e) => setStrategy(prev => ({ ...prev, description: e.target.value }))}
              className="w-full px-3 py-1.5 text-sm border rounded-lg"
              placeholder="Strategy description..."
            />
          </div>
        </div>
      </div>

      {/* Indicator Selector */}
      <IndicatorSelector
        availableIndicators={availableIndicators}
        onAddIndicator={addIndicator}
      />

      {/* Selected Indicators */}
      {strategy.indicators.length > 0 && (
        <div className="bg-white dark:bg-gray-800 rounded-xl p-4 shadow-lg">
          <h3 className="text-lg font-bold mb-3">
            📊 Selected Indicators ({strategy.indicators.filter(ind => ind.enabled).length}/{strategy.indicators.length})
          </h3>
          <div className="grid grid-cols-3 gap-3">
            {strategy.indicators.map((ind, index) => {
              const contribution = totalWeight > 0 ? (ind.weight / totalWeight * 100).toFixed(1) : '0.0'
              return (
                <div
                  key={index}
                  className={`flex flex-col gap-2 p-3 rounded-lg border-2 ${
                    ind.enabled ? 'border-blue-500 bg-blue-50 dark:bg-blue-900/20' : 'border-gray-300 bg-gray-50 dark:bg-gray-700 opacity-50'
                  }`}
                >
                  <div className="flex items-center gap-2">
                    <input
                      type="checkbox"
                      checked={ind.enabled}
                      onChange={() => toggleIndicator(index)}
                      className="w-4 h-4"
                    />
                    <div className="flex-1">
                      <div className="font-bold text-sm">{ind.type}</div>
                      <div className="text-[10px] text-gray-600 dark:text-gray-400 truncate">
                        {JSON.stringify(ind.config)}
                      </div>
                    </div>
                  </div>
                  <div className="flex items-center justify-between gap-2">
                    <div className="flex items-center gap-1.5">
                      <label className="text-xs font-bold">Weight:</label>
                      <input
                        type="number"
                        value={ind.weight}
                        onChange={(e) => updateIndicatorWeight(index, parseFloat(e.target.value) || 1)}
                        className="w-16 px-2 py-0.5 text-xs border rounded"
                        min="0.1"
                        step="0.1"
                      />
                      <span className="text-xs font-bold text-blue-600">
                        ({contribution}%)
                      </span>
                    </div>
                    <div className="flex gap-1">
                      <button
                        className="btn-secondary text-xs px-2 py-1"
                        onClick={() => openEditModal(index)}
                      >
                        ⚙️
                      </button>
                      <button
                        className="btn-danger text-xs px-2 py-1"
                        onClick={() => removeIndicator(index)}
                      >
                        ❌
                      </button>
                    </div>
                  </div>
                </div>
              )
            })}
          </div>

          {/* Signal Threshold */}
          <div className="mt-6 p-4 bg-yellow-50 dark:bg-yellow-900/20 rounded-lg">
            <label className="block text-sm font-bold mb-2">
              📈 Signal Threshold: {strategy.signal_logic.threshold_percent}%
            </label>
            <input
              type="range"
              min="50"
              max="100"
              value={strategy.signal_logic.threshold_percent}
              onChange={(e) => setStrategy(prev => ({
                ...prev,
                signal_logic: { threshold_percent: parseInt(e.target.value) }
              }))}
              className="w-full"
            />
            <p className="text-xs text-gray-600 mt-1">
              Tín hiệu chỉ kích hoạt khi bullish hoặc bearish percent &gt;= threshold
            </p>
          </div>

          {/* Trailing Stop & Partial TP Settings */}
          <div className="mt-4 p-4 bg-blue-50 dark:bg-blue-900/20 rounded-lg">
            <h4 className="text-sm font-bold mb-3">🎯 Advanced Exit Settings</h4>
            
            {/* Trailing Stop */}
            <div className="mb-4">
              <label className="flex items-center gap-2 cursor-pointer">
                <input
                  type="checkbox"
                  checked={strategy.signal_logic.enable_trailing_stop ?? true}
                  onChange={(e) => setStrategy(prev => ({
                    ...prev,
                    signal_logic: {
                      ...prev.signal_logic,
                      enable_trailing_stop: e.target.checked
                    }
                  }))}
                  className="w-4 h-4"
                />
                <span className="text-sm font-medium">Enable Trailing Stop</span>
              </label>
              {strategy.signal_logic.enable_trailing_stop && (
                <div className="ml-6 mt-2 space-y-2">
                  <div>
                    <label className="block text-xs mb-1">
                      Activation R: {strategy.signal_logic.trailing_activation_r ?? 1.0}
                    </label>
                    <input
                      type="range"
                      min="0.5"
                      max="3.0"
                      step="0.1"
                      value={strategy.signal_logic.trailing_activation_r ?? 1.0}
                      onChange={(e) => setStrategy(prev => ({
                        ...prev,
                        signal_logic: {
                          ...prev.signal_logic,
                          trailing_activation_r: parseFloat(e.target.value)
                        }
                      }))}
                      className="w-full"
                    />
                    <p className="text-xs text-gray-600">Activate trailing when profit &gt;= this R value</p>
                  </div>
                  <div>
                    <label className="block text-xs mb-1">
                      Trailing Multiplier: {strategy.signal_logic.trailing_multiplier ?? 1.5}x ATR
                    </label>
                    <input
                      type="range"
                      min="0.5"
                      max="5.0"
                      step="0.1"
                      value={strategy.signal_logic.trailing_multiplier ?? 1.5}
                      onChange={(e) => setStrategy(prev => ({
                        ...prev,
                        signal_logic: {
                          ...prev.signal_logic,
                          trailing_multiplier: parseFloat(e.target.value)
                        }
                      }))}
                      className="w-full"
                    />
                    <p className="text-xs text-gray-600">Trailing distance = ATR × multiplier</p>
                  </div>
                </div>
              )}
            </div>

            {/* Partial TP Close */}
            <div className="mb-2">
              <label className="flex items-center gap-2 cursor-pointer">
                <input
                  type="checkbox"
                  checked={strategy.signal_logic.enable_partial_tp_close ?? false}
                  onChange={(e) => setStrategy(prev => ({
                    ...prev,
                    signal_logic: {
                      ...prev.signal_logic,
                      enable_partial_tp_close: e.target.checked
                    }
                  }))}
                  className="w-4 h-4"
                />
                <span className="text-sm font-medium">Enable Partial TP Close</span>
              </label>
              <p className="text-xs text-gray-600 ml-6 mt-1">
                Close % of position at TP, keep remainder with trailing stop
              </p>
              {strategy.signal_logic.enable_partial_tp_close && (
                <div className="ml-6 mt-2">
                  <label className="block text-xs mb-1">
                    Close % at TP: {(strategy.signal_logic.tp_close_pct ?? 0.5) * 100}%
                  </label>
                  <input
                    type="range"
                    min="0.1"
                    max="1.0"
                    step="0.1"
                    value={strategy.signal_logic.tp_close_pct ?? 0.5}
                    onChange={(e) => setStrategy(prev => ({
                      ...prev,
                      signal_logic: {
                        ...prev.signal_logic,
                        tp_close_pct: parseFloat(e.target.value)
                      }
                    }))}
                    className="w-full"
                  />
                  <p className="text-xs text-gray-600">
                    {(strategy.signal_logic.tp_close_pct ?? 0.5) * 100}% closed at TP, {((1 - (strategy.signal_logic.tp_close_pct ?? 0.5)) * 100).toFixed(0)}% kept with trailing stop
                  </p>
                </div>
              )}
            </div>
          </div>
        </div>
      )}

      {/* Filter Settings */}
      <FilterSettings
        filters={strategy.filters}
        onChange={(filters) => setStrategy(prev => ({ ...prev, filters }))}
      />

       {/* Risk Management */}
       <div className="bg-white dark:bg-gray-800 rounded-xl p-4 shadow-lg">
         <h3 className="text-lg font-bold mb-3">💰 Risk Management</h3>
        <div className="grid grid-cols-2 gap-3">
          <div>
            <label className="block text-xs font-bold mb-1">Initial Capital ($)</label>
            <input
              type="number"
              value={strategy.risk_management.capital}
              onChange={(e) => setStrategy(prev => ({
                ...prev,
                risk_management: { ...prev.risk_management, capital: parseFloat(e.target.value) || 1000 }
              }))}
              className="w-full px-3 py-1.5 text-sm border rounded-lg"
              step="100"
            />
          </div>
          <div>
            <label className="block text-xs font-bold mb-1">Risk per Trade (%)</label>
            <input
              type="number"
              value={strategy.risk_management.risk_percent}
              onChange={(e) => setStrategy(prev => ({
                ...prev,
                risk_management: { ...prev.risk_management, risk_percent: parseFloat(e.target.value) || 1.0 }
              }))}
              className={`w-full px-3 py-1.5 text-sm border rounded-lg ${
                strategy.risk_management.risk_percent > 10 
                  ? 'border-red-500 bg-red-50 dark:bg-red-900/20' 
                  : strategy.risk_management.risk_percent > 5
                  ? 'border-yellow-500 bg-yellow-50 dark:bg-yellow-900/20'
                  : ''
              }`}
              step="0.1"
              min="0.1"
              max="100"
            />
            {strategy.risk_management.risk_percent > 10 && (
              <div className="mt-1 p-2 bg-red-100 dark:bg-red-900/30 border-l-4 border-red-500 rounded text-xs">
                <div className="font-bold text-red-700 dark:text-red-300">⚠️ CẢNH BÁO: Risk quá cao!</div>
                <div className="text-red-600 dark:text-red-400 mt-1">
                  Risk {strategy.risk_management.risk_percent}% rất nguy hiểm. Chỉ cần {Math.floor(100 / strategy.risk_management.risk_percent)} trades thua là phá sản!
                </div>
                <div className="text-red-600 dark:text-red-400 mt-1">
                  Khuyến nghị: 1-2% (conservative), 2-5% (moderate), tối đa 5-10% (aggressive).
                </div>
              </div>
            )}
            {strategy.risk_management.risk_percent > 5 && strategy.risk_management.risk_percent <= 10 && (
              <div className="mt-1 p-2 bg-yellow-100 dark:bg-yellow-900/30 border-l-4 border-yellow-500 rounded text-xs">
                <div className="font-bold text-yellow-700 dark:text-yellow-300">⚠️ Risk cao</div>
                <div className="text-yellow-600 dark:text-yellow-400 mt-1">
                  Risk {strategy.risk_management.risk_percent}% là aggressive. Chỉ có thể thua {Math.floor(100 / strategy.risk_management.risk_percent)} trades trước khi phá sản.
                </div>
              </div>
            )}
          </div>
          <div>
            <label className="block text-xs font-bold mb-1">Reward Ratio</label>
            <input
              type="number"
              value={strategy.risk_management.reward_ratio}
              onChange={(e) => setStrategy(prev => ({
                ...prev,
                risk_management: { ...prev.risk_management, reward_ratio: parseFloat(e.target.value) || 1.0 }
              }))}
              className="w-full px-3 py-1.5 text-sm border rounded-lg"
              step="0.1"
            />
          </div>
          <div>
            <label className="block text-xs font-bold mb-1">Stop Loss (%)</label>
            <input
              type="number"
              value={strategy.risk_management.stop_loss_percent}
              onChange={(e) => setStrategy(prev => ({
                ...prev,
                risk_management: { ...prev.risk_management, stop_loss_percent: parseFloat(e.target.value) || 1.0 }
              }))}
              className="w-full px-3 py-1.5 text-sm border rounded-lg"
              step="0.1"
            />
          </div>
          <div>
            <label className="block text-xs font-bold mb-1">Margin/Leverage (x)</label>
            <input
              type="number"
              value={strategy.risk_management.margin || ''}
              onChange={(e) => setStrategy(prev => ({
                ...prev,
                risk_management: { 
                  ...prev.risk_management, 
                  margin: e.target.value ? parseFloat(e.target.value) : undefined 
                }
              }))}
              className="w-full px-3 py-1.5 text-sm border rounded-lg"
              step="0.5"
              min="1"
              max="125"
              placeholder="Không dùng margin (để trống)"
            />
            <div className="mt-1 text-xs text-gray-500 dark:text-gray-400">
              Để trống = không dùng margin. Ví dụ: 10x = leverage 10 lần
            </div>
          </div>
        </div>
      </div>

      {/* Action Buttons */}
      <div className="flex gap-4">
        <button
          className="btn-primary flex-1"
          onClick={runBacktest}
          disabled={isRunning || !csvData}
        >
          {isRunning ? '⏳ Running...' : '▶️ Run Backtest'}
        </button>
      </div>

      {/* Preview Result */}
      {preview && (
        <div className="bg-green-50 dark:bg-green-900/20 rounded-xl p-6 shadow-lg">
          <h3 className="text-xl font-bold mb-2">👁️ Signal Preview</h3>
          <div className="grid grid-cols-4 gap-4 text-center">
            <div>
              <div className="text-3xl font-bold">{preview.total}</div>
              <div className="text-sm">Total Signals</div>
            </div>
            <div>
              <div className="text-3xl font-bold text-green-600">{preview.long}</div>
              <div className="text-sm">Long Signals</div>
            </div>
            <div>
              <div className="text-3xl font-bold text-red-600">{preview.short}</div>
              <div className="text-sm">Short Signals</div>
            </div>
            <div>
              <div className="text-3xl font-bold text-blue-600">
                {((preview.total / (csvData?.length || 1)) * 100).toFixed(1)}%
              </div>
              <div className="text-sm">Signal Rate</div>
            </div>
          </div>
        </div>
      )}

      {/* Progress Bar */}
      {isRunning && (
        <ProgressBar
          progress={backtestProgress.progress}
          tested={backtestProgress.tested}
          withTrades={backtestProgress.withTrades}
          timeElapsed={backtestProgress.timeElapsed}
        />
      )}

      {/* Backtest Results */}
      {backtestResult && <StrategyResults result={backtestResult} initialCapital={strategy.risk_management.capital} />}

      {/* Chart Visualization */}
      {backtestResult && csvData && <StrategyChart ohlcvData={csvData} result={backtestResult} />}

      {/* Edit Indicator Modal */}
      {editingIndicator && (
        <IndicatorConfigModal
          indicator={editingIndicator.config}
          onSave={saveIndicatorConfig}
          onCancel={() => setEditingIndicator(null)}
        />
      )}

      {/* Save Modal */}
      {showSaveModal && (
        <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50">
          <div className="bg-white dark:bg-gray-800 rounded-xl p-6 w-96 shadow-2xl">
            <h3 className="text-xl font-bold mb-4">💾 Save Strategy</h3>
            <label className="block text-sm font-bold mb-2">Strategy Name</label>
            <input
              type="text"
              value={strategy.name}
              onChange={(e) => setStrategy(prev => ({ ...prev, name: e.target.value }))}
              className="w-full px-4 py-2 border rounded-lg mb-4"
            />
            <div className="flex gap-2">
              <button className="btn-primary flex-1" onClick={saveStrategy}>
                💾 Save
              </button>
              <button className="btn-secondary flex-1" onClick={() => setShowSaveModal(false)}>
                Cancel
              </button>
            </div>
          </div>
        </div>
      )}

      {/* Load Modal */}
      {showLoadModal && (
        <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50">
          <div className="bg-white dark:bg-gray-800 rounded-xl p-6 w-[600px] shadow-2xl max-h-[80vh] overflow-auto">
            <h3 className="text-xl font-bold mb-4">📂 Load Strategy</h3>
            {savedStrategies.length === 0 ? (
              <p className="text-gray-600">No saved strategies</p>
            ) : (
              <div className="space-y-2">
                {savedStrategies.map((item) => (
                  <div key={item.name} className="flex items-center justify-between p-4 border rounded-lg">
                    <div className="flex-1">
                      <div className="font-bold">{item.name}</div>
                      <div className="text-xs text-gray-600">
                        {item.description || 'No description'}
                      </div>
                      <div className="text-xs text-gray-500 mt-1">
                        {item.indicator_count} indicators • {item.created_at}
                      </div>
                    </div>
                    <div className="flex gap-2">
                      <button
                        className="btn-primary text-sm"
                        onClick={() => loadStrategy(item.name)}
                      >
                        Load
                      </button>
                      <button
                        className="btn-danger text-sm"
                        onClick={() => deleteStrategy(item.name)}
                      >
                        ❌
                      </button>
                    </div>
                  </div>
                ))}
              </div>
            )}
            <button
              className="btn-secondary w-full mt-4"
              onClick={() => setShowLoadModal(false)}
            >
              Close
            </button>
          </div>
        </div>
      )}
    </Layout>
  )
}
