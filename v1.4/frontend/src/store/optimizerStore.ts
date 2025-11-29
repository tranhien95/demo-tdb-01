import { create } from 'zustand'
import { OptimizerState, OptimizationParams } from '../types'

const defaultParams: OptimizationParams = {
  minComboSize: 2,
  maxComboSize: 3,
  threshold: 70,
  riskPercent: 10,
  rrRatio: 2.0,
  slPercent: 0.75,
  candleConfirmation: 2,
  minWinRate: 50,
  minProfit: 0,
  minTrades: 10,
  capital: 10000,
  enableADXFilter: false,
  adxThreshold: 25,
  enableVolumeFilter: false,
  volumeThreshold: 120,
  enableMAFilter: false,
  maValue: 50,
  enableTrendFilter: false,
  trendMA: 200,
  enableVolatilityFilter: false,
  minATR: 0.5,
  minSignalStrength: 70,
  maxCombos: 0
}

export const useOptimizerStore = create<OptimizerState>((set) => ({
  csvData: null,
  setCsvData: (data) => set({ csvData: data }),
  
  params: defaultParams,
  setParams: (newParams) => set((state) => ({ 
    params: { ...state.params, ...newParams } 
  })),
  
  progress: {
    isRunning: false,
    percent: 0,
    tested: 0,
    withTrades: 0,
    timeElapsed: 0
  },
  setProgress: (progress) => set((state) => ({
    progress: { ...state.progress, ...progress }
  })),
  
  results: [],
  setResults: (results) => set({ results }),
  
  selectedCombo: null,
  setSelectedCombo: (combo) => set({ selectedCombo: combo }),
  
  showChart: false,
  setShowChart: (show) => set({ showChart: show })
}))
