export interface OHLCV {
  time: string
  open: number
  high: number
  low: number
  close: number
  volume: number
}

export interface OptimizationParams {
  minComboSize: number
  maxComboSize: number
  threshold: number
  riskPercent: number
  rrRatio: number
  slPercent: number
  candleConfirmation: number
  minWinRate: number
  minProfit: number
  minTrades: number
  capital: number
  enableADXFilter: boolean
  adxThreshold: number
  enableVolumeFilter: boolean
  volumeThreshold: number
  enableMAFilter: boolean
  maValue: number
  enableTrendFilter: boolean
  trendMA: number
  enableVolatilityFilter: boolean
  minATR: number
  minSignalStrength: number
  maxCombos: number
  // Advanced Exit Settings
  enableTrailingStop: boolean
  trailingActivationR: number
  trailingMultiplier: number
  enablePartialTPClose: boolean
  tpClosePct: number
}

export interface Trade {
  entry: number
  exit: number | null
  sl: number
  tp: number
  profit: number | null
  profit_pct: number | null
  position_size: number | null  // Amount of money in trade
  position_percent: number | null  // Percent of capital used
  type: 'LONG' | 'SHORT'
  time: string
  exit_time: string | null
  exit_reason?: string
  balance_before?: number  // Balance before trade entry
  balance_after?: number   // Balance after trade exit
}

export interface ComboResult {
  combo: string
  trades: number
  wins: number
  losses: number
  win_rate: number
  profit_pct: number
  profit_factor: number
  draw_down: number
  sharpe: number
  trades_list: Trade[]
}

export interface ProgressUpdate {
  progress: number
  tested: number
  with_trades: number
}

export interface OptimizerState {
  csvData: OHLCV[] | null
  setCsvData: (data: OHLCV[] | null) => void
  
  params: OptimizationParams
  setParams: (params: Partial<OptimizationParams>) => void
  
  progress: {
    isRunning: boolean
    percent: number
    tested: number
    withTrades: number
    timeElapsed: number
  }
  setProgress: (progress: Partial<OptimizerState['progress']>) => void
  
  results: ComboResult[]
  setResults: (results: ComboResult[]) => void
  
  selectedCombo: ComboResult | null
  setSelectedCombo: (combo: ComboResult | null) => void
  
  showChart: boolean
  setShowChart: (show: boolean) => void
}

// ======================== STRATEGY BUILDER TYPES ========================

export interface IndicatorConfig {
  type: string
  config: Record<string, any>
  weight: number
  enabled: boolean
}

export interface SignalLogic {
  threshold_percent: number
  enable_partial_tp_close?: boolean
  tp_close_pct?: number
  enable_trailing_stop?: boolean
  trailing_activation_r?: number
  trailing_multiplier?: number
}

export interface FilterConfig {
  enable_adx: boolean
  adx_threshold: number
  enable_volume: boolean
  volume_threshold: number
  enable_ma_filter: boolean
  ma_period: number
  enable_atr_filter: boolean
  min_atr: number
  enable_trend_filter: boolean
  trend_ma: number
}

export interface RiskManagement {
  risk_percent: number
  reward_ratio: number
  stop_loss_percent: number
  capital: number  // Initial capital
  margin?: number  // Margin/leverage (optional)
}

export interface Strategy {
  name: string
  description: string
  indicators: IndicatorConfig[]
  signal_logic: SignalLogic
  filters: FilterConfig
  risk_management: RiskManagement
}

export interface AvailableIndicator {
  type: string
  description: string
  default_config: Record<string, any>
}

export interface SignalDetail {
  index: number
  time: string
  bullish_percent: number
  bearish_percent: number
  contributing_indicators: Record<string, string>
}

export interface BacktestResult {
  status?: string
  total_trades: number
  winning_trades: number
  losing_trades: number
  win_rate: number
  profit_pct?: number  // Old field name for backwards compatibility
  total_profit_pct?: number  // New field name
  total_profit_usd?: number  // Old field name
  total_profit?: number  // New field name
  profit_factor: number
  max_drawdown: number
  sharpe_ratio: number
  long_trades: number
  short_trades: number
  trades: Trade[]
  signals?: SignalDetail[]
  equity_curve?: number[]
  signals_found?: number
  long_signals?: number
  short_signals?: number
}

export interface StrategyListItem {
  name: string
  description: string
  created_at: string
  indicator_count: number
}

export interface PineScriptExport {
  code: string
  strategy_name: string
  indicators_used?: string[]
  version?: string
  backtest_info?: any
}
