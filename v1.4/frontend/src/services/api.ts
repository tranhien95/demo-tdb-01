import { 
  OHLCV, 
  OptimizationParams, 
  ComboResult,
  Strategy,
  BacktestResult,
  AvailableIndicator,
  StrategyListItem,
  PineScriptExport
} from '../types'

const API_BASE = 'http://localhost:4000'

export const optimizerAPI = {
  async runOptimization(ohlcvData: OHLCV[], params: OptimizationParams): Promise<Response> {
    const response = await fetch(`${API_BASE}/optimize-stream`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        ohlcv_data: ohlcvData.map(d => ({
          ...d,
          volume: Math.floor(d.volume)
        })),
        min_combo_size: params.minComboSize,
        max_combo_size: params.maxComboSize,
        threshold: params.threshold,
        risk_percent: params.riskPercent,
        rr_ratio: params.rrRatio,
        sl_percent: params.slPercent,
        candle_confirmation: params.candleConfirmation,
        enable_adx_filter: params.enableADXFilter,
        adx_threshold: params.adxThreshold,
        enable_volume_filter: params.enableVolumeFilter,
        volume_ma_period: 20,
        enable_ma_filter: params.enableMAFilter,
        ma_period: params.maValue,
        min_signal_ratio: params.minSignalStrength,
        max_combos: params.maxCombos || 0,
        filters: {}
      })
    })

    if (!response.ok) {
      throw new Error(`Backend error: ${response.status}`)
    }

    return response
  },

  async generatePineScript(indicators: string[]): Promise<{ status: string; code: string; indicators: string[] }> {
    const response = await fetch(`${API_BASE}/generate-pine-script`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(indicators)
    })

    if (!response.ok) {
      throw new Error('Failed to generate Pine Script')
    }

    return response.json()
  },

  async healthCheck(): Promise<{ status: string; version: string; port: number; frontend: string }> {
    const response = await fetch(`${API_BASE}/health`)
    return response.json()
  }
}

// ======================== STRATEGY BUILDER API ========================

export const strategyAPI = {
  async listIndicators(): Promise<{ indicators: AvailableIndicator[] }> {
    const response = await fetch(`${API_BASE}/api/indicators/list`)
    if (!response.ok) throw new Error('Failed to fetch indicators')
    return response.json()
  },

  async validateStrategy(strategy: Strategy): Promise<{ valid: boolean; message: string }> {
    const response = await fetch(`${API_BASE}/api/strategy/validate`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(strategy)
    })
    if (!response.ok) throw new Error('Validation request failed')
    return response.json()
  },

  async previewSignals(request: { strategy: Strategy; ohlcv_data: OHLCV[] }): Promise<{
    total_signals: number
    long_signals: number
    short_signals: number
    total_candles: number
  }> {
    const response = await fetch(`${API_BASE}/api/strategy/preview`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(request)
    })
    if (!response.ok) throw new Error('Preview failed')
    return response.json()
  },

  async backtestStrategy(request: { strategy: Strategy; ohlcv_data: OHLCV[] }): Promise<BacktestResult> {
    const response = await fetch(`${API_BASE}/api/strategy/backtest`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(request)
    })
    if (!response.ok) throw new Error('Backtest failed')
    return response.json()
  },

  async saveStrategy(strategy: Strategy): Promise<{ status: string; message: string }> {
    const response = await fetch(`${API_BASE}/api/strategy/save`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(strategy)
    })
    if (!response.ok) throw new Error('Save failed')
    return response.json()
  },

  async listStrategies(): Promise<{ strategies: StrategyListItem[] }> {
    const response = await fetch(`${API_BASE}/api/strategy/list`)
    if (!response.ok) throw new Error('Failed to list strategies')
    return response.json()
  },

  async loadStrategy(name: string): Promise<Strategy> {
    const response = await fetch(`${API_BASE}/api/strategy/load/${encodeURIComponent(name)}`)
    if (!response.ok) throw new Error('Load failed')
    return response.json()
  },

  async deleteStrategy(name: string): Promise<{ status: string; message: string }> {
    const response = await fetch(`${API_BASE}/api/strategy/delete/${encodeURIComponent(name)}`, {
      method: 'DELETE'
    })
    if (!response.ok) throw new Error('Delete failed')
    return response.json()
  },

  async exportPineScript(strategy: Strategy): Promise<PineScriptExport> {
    const response = await fetch(`${API_BASE}/api/strategy/export-pine`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(strategy)
    })
    if (!response.ok) throw new Error('Export failed')
    return response.json()
  },

  async optimizeStrategy(request: {
    ohlcv_data: any[]
    combo_size: number
    max_combos?: number
    filters: any
    risk_management: any
  }): Promise<{
    total_results: number
    total_tested: number
    top_combos: any[]
  }> {
    const response = await fetch(`${API_BASE}/api/strategy/optimize`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(request)
    })
    if (!response.ok) throw new Error('Optimization failed')
    return response.json()
  }
}

// Binance API
export const binanceAPI = {
  async getSymbols(): Promise<{ symbols: string[] }> {
    const response = await fetch(`${API_BASE}/api/binance/symbols`)
    if (!response.ok) throw new Error('Failed to fetch symbols')
    return response.json()
  },

  async getTimeframes(): Promise<{ timeframes: Record<string, string> }> {
    const response = await fetch(`${API_BASE}/api/binance/timeframes`)
    if (!response.ok) throw new Error('Failed to fetch timeframes')
    return response.json()
  },

  async fetchData(symbol: string, timeframe: string, limit: number = 200) {
    const response = await fetch(`${API_BASE}/api/binance/fetch`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ symbol, timeframe, limit })
    })
    if (!response.ok) throw new Error(`Failed to fetch ${symbol} data`)
    return response.json()
  },

  async getSymbolInfo(symbol: string) {
    const response = await fetch(`${API_BASE}/api/binance/symbol-info/${encodeURIComponent(symbol)}`)
    if (!response.ok) throw new Error('Failed to fetch symbol info')
    return response.json()
  }
}


