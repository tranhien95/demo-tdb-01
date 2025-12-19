const API_BASE = 'http://localhost:4000'

// Optimizer API
export const optimizerAPI = {
  async runOptimization(csvData: any[], params: any) {
    const response = await fetch(`${API_BASE}/optimize-stream`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        ohlcv_data: csvData,
        ...params
      })
    })
    if (!response.ok) {
      const errorText = await response.text()
      throw new Error(`Failed to run optimization: ${response.status} ${errorText}`)
    }
    return response  // Return full response, not just body
  },

  async generatePineScript(indicators: string[], filters: any) {
    const response = await fetch(`${API_BASE}/generate-pine-script`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ indicators, filters })
    })
    if (!response.ok) throw new Error('Failed to generate Pine Script')
    return response.json()
  }
}

// Strategy API
export const strategyAPI = {
  async listIndicators() {
    const response = await fetch(`${API_BASE}/api/strategy/indicators/list`)
    if (!response.ok) throw new Error('Failed to fetch indicators')
    return response.json()
  },

  async listStrategies() {
    const response = await fetch(`${API_BASE}/api/strategy/list`)
    if (!response.ok) throw new Error('Failed to fetch strategies')
    return response.json()
  },

  async previewSignals(request: { strategy: any; ohlcv_data: any[] }) {
    const response = await fetch(`${API_BASE}/api/strategy/preview`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(request)
    })
    if (!response.ok) throw new Error('Failed to preview signals')
    return response.json()
  },

  async backtestStrategy(request: { strategy: any; ohlcv_data: any[] }) {
    const response = await fetch(`${API_BASE}/api/strategy/backtest`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(request)
    })
    if (!response.ok) throw new Error('Failed to backtest strategy')
    return response.json()
  },

  async saveStrategy(strategy: any) {
    const response = await fetch(`${API_BASE}/api/strategy/save`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(strategy)
    })
    if (!response.ok) throw new Error('Failed to save strategy')
    return response.json()
  },

  async loadStrategy(name: string) {
    const response = await fetch(`${API_BASE}/api/strategy/load/${encodeURIComponent(name)}`)
    if (!response.ok) throw new Error('Failed to load strategy')
    return response.json()
  },

  async deleteStrategy(name: string) {
    const response = await fetch(`${API_BASE}/api/strategy/delete/${encodeURIComponent(name)}`, {
      method: 'DELETE'
    })
    if (!response.ok) throw new Error('Failed to delete strategy')
    return response.json()
  },

  async exportPineScript(request: { strategy: any; ohlcv_data?: any[] }) {
    const response = await fetch(`${API_BASE}/api/strategy/export-pine`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(request)
    })
    if (!response.ok) throw new Error('Failed to export Pine Script')
    return response.json()
  },

  async backtestPineScript(pineCode: string, ohlcvData: any[]) {
    const response = await fetch(`${API_BASE}/api/strategy/backtest-pine`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        pine_code: pineCode,
        ohlcv_data: ohlcvData
      })
    })
    if (!response.ok) throw new Error('Failed to backtest Pine Script')
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

  async fetchData(
    symbol: string, 
    timeframe: string, 
    limit?: number,
    startDate?: string,
    endDate?: string
  ) {
    const body: any = { symbol, timeframe }
    if (startDate && endDate) {
      body.start_date = startDate
      body.end_date = endDate
    } else if (limit) {
      body.limit = limit
    } else {
      body.limit = 200 // Default
    }
    
    const response = await fetch(`${API_BASE}/api/binance/fetch`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(body)
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

// VNStock API (Vietnam Stock Market)
export const vnstockAPI = {
  async getSymbols(assetType: 'stock' | 'derivative' = 'stock'): Promise<{ status?: string; symbols: string[]; message?: string; asset_type?: string }> {
    const response = await fetch(`${API_BASE}/api/vnstock/symbols?asset_type=${assetType}`)
    // Don't throw on 200 OK even if status is 'warning'
    if (!response.ok) {
      const errorData = await response.json().catch(() => ({ detail: response.statusText }))
      throw new Error(errorData.detail || errorData.message || 'Failed to fetch symbols')
    }
    return response.json()
  },

  async getTimeframes(): Promise<{ status?: string; timeframes: Record<string, string>; message?: string }> {
    const response = await fetch(`${API_BASE}/api/vnstock/timeframes`)
    // Don't throw on 200 OK even if status is 'warning'
    if (!response.ok) {
      const errorData = await response.json().catch(() => ({ detail: response.statusText }))
      throw new Error(errorData.detail || errorData.message || 'Failed to fetch timeframes')
    }
    return response.json()
  },

  async fetchData(
    symbol: string, 
    timeframe: string, 
    limit?: number,
    startDate?: string,
    endDate?: string
  ) {
    const body: any = { symbol, timeframe }
    if (startDate && endDate) {
      body.start_date = startDate
      body.end_date = endDate
    } else if (limit) {
      body.limit = limit
    } else {
      body.limit = 200 // Default
    }
    
    const response = await fetch(`${API_BASE}/api/vnstock/fetch`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(body)
    })
    if (!response.ok) {
      // Try to get error detail from response
      const errorData = await response.json().catch(() => ({ detail: response.statusText }))
      const errorMsg = errorData.detail || errorData.message || `Failed to fetch ${symbol} data`
      throw new Error(errorMsg)
    }
    return response.json()
  },

  async getSymbolInfo(symbol: string) {
    const response = await fetch(`${API_BASE}/api/vnstock/symbol-info/${encodeURIComponent(symbol)}`)
    if (!response.ok) throw new Error('Failed to fetch symbol info')
    return response.json()
  },

  async getDerivativesSymbols(): Promise<{ status?: string; symbols: string[]; message?: string }> {
    const response = await fetch(`${API_BASE}/api/vnstock/derivatives/symbols`)
    if (!response.ok) {
      const errorData = await response.json().catch(() => ({ detail: response.statusText }))
      throw new Error(errorData.detail || errorData.message || 'Failed to fetch derivatives symbols')
    }
    return response.json()
  }
}

// DNSE/YFinance API (Alternative Vietnam Stock Market Data Source)
export const dnseAPI = {
  async getSymbols(): Promise<{ status?: string; symbols: string[]; message?: string }> {
    const response = await fetch(`${API_BASE}/api/dnse/symbols`)
    if (!response.ok) {
      const errorData = await response.json().catch(() => ({ detail: response.statusText }))
      throw new Error(errorData.detail || errorData.message || 'Failed to fetch symbols')
    }
    return response.json()
  },

  async getTimeframes(): Promise<{ status?: string; timeframes: Record<string, string>; message?: string }> {
    const response = await fetch(`${API_BASE}/api/dnse/timeframes`)
    if (!response.ok) {
      const errorData = await response.json().catch(() => ({ detail: response.statusText }))
      throw new Error(errorData.detail || errorData.message || 'Failed to fetch timeframes')
    }
    return response.json()
  },

  async fetchData(
    symbol: string, 
    timeframe: string, 
    limit?: number,
    startDate?: string,
    endDate?: string
  ) {
    const body: any = { symbol, timeframe }
    if (startDate && endDate) {
      body.start_date = startDate
      body.end_date = endDate
    } else if (limit) {
      body.limit = limit
    } else {
      body.limit = 200 // Default
    }
    
    const response = await fetch(`${API_BASE}/api/dnse/fetch`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(body)
    })
    if (!response.ok) {
      const errorData = await response.json().catch(() => ({ detail: response.statusText }))
      const errorMsg = errorData.detail || errorData.message || `Failed to fetch ${symbol} data`
      throw new Error(errorMsg)
    }
    return response.json()
  },

  async getSymbolInfo(symbol: string) {
    const response = await fetch(`${API_BASE}/api/dnse/symbol-info/${encodeURIComponent(symbol)}`)
    if (!response.ok) throw new Error('Failed to fetch symbol info')
    return response.json()
  }
}

// Live Trading API
export const liveTradingAPI = {
  async startTrading(config: {
    symbol: string
    timeframe: string
    strategy_name: string
    initial_balance: number
    risk_percent: number
    margin?: number
    stoploss_percent?: number
    reversal_strength_threshold?: number
    max_positions?: number
  }) {
    const response = await fetch(`${API_BASE}/api/live-trading/start`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(config)
    })
    if (!response.ok) throw new Error('Failed to start trading')
    return response.json()
  },

  async getStatus() {
    const response = await fetch(`${API_BASE}/api/live-trading/status`)
    if (!response.ok) throw new Error('Failed to get status')
    return response.json()
  },

  async update() {
    const response = await fetch(`${API_BASE}/api/live-trading/update`, {
      method: 'POST'
    })
    if (!response.ok) throw new Error('Failed to update')
    return response.json()
  },

  async pause() {
    const response = await fetch(`${API_BASE}/api/live-trading/pause`, {
      method: 'POST'
    })
    if (!response.ok) throw new Error('Failed to pause')
    return response.json()
  },

  async resume() {
    const response = await fetch(`${API_BASE}/api/live-trading/resume`, {
      method: 'POST'
    })
    if (!response.ok) throw new Error('Failed to resume')
    return response.json()
  },

  async stop() {
    const response = await fetch(`${API_BASE}/api/live-trading/stop`, {
      method: 'POST'
    })
    if (!response.ok) throw new Error('Failed to stop')
    return response.json()
  },

  async closeAll() {
    const response = await fetch(`${API_BASE}/api/live-trading/close-all`, {
      method: 'POST'
    })
    if (!response.ok) throw new Error('Failed to close all')
    return response.json()
  }
}
