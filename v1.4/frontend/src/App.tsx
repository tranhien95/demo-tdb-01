import React, { useState } from 'react'
import { useOptimizerStore } from './store/optimizerStore'
import { DataManager } from './components/DataManager'
import { StrategyBuilder } from './components/StrategyBuilder'
import { ComboOptimizer } from './components/ComboOptimizer'
import LiveTradingDashboard from './components/LiveTradingDashboard'
import { AdminPanel } from './components/AdminPanel'
import { PineScriptTester } from './components/PineScriptTester'

type ScreenMode = 'data' | 'strategy' | 'combo-optimizer' | 'live-trading' | 'admin' | 'pine-tester'

function App() {
  const { csvData } = useOptimizerStore()
  const [activeMode, setActiveMode] = useState<ScreenMode>('data')

  const navigationItems: Array<{ mode: ScreenMode; label: string; icon: string; description: string }> = [
    { mode: 'data', label: 'Data Manager', icon: '📊', description: 'Upload/Fetch data' },
    { mode: 'strategy', label: 'Strategy Builder', icon: '🎯', description: 'Build custom strategy' },
    { mode: 'combo-optimizer', label: 'Combo Optimizer', icon: '⚙️', description: 'Optimize indicator combos with advanced settings' },
    { mode: 'pine-tester', label: 'Pine Script Tester', icon: '📝', description: 'Test Pine Script code directly' },
    { mode: 'live-trading', label: 'Live Trading', icon: '📈', description: 'Real-time trading' },
    { mode: 'admin', label: 'Admin', icon: '🔧', description: 'System management' },
  ]

  return (
    <div className="min-h-screen bg-gray-50 dark:bg-gray-900">
      <div className="max-w-7xl mx-auto p-6">
        {/* Main Header */}
        <header className="gradient-header rounded-2xl p-6 mb-6 shadow-2xl">
          <div className="flex items-center justify-between">
            <div>
              <h1 className="text-3xl font-bold">🎯 Trading Strategy Platform v1.4</h1>
              <p className="text-sm opacity-90 mt-1">Build, Optimize & Trade with Advanced Indicators</p>
            </div>
            {csvData && (
              <div className="text-right">
                <div className="text-sm opacity-90">Data Loaded</div>
                <div className="text-lg font-bold">{csvData.length} candles</div>
              </div>
            )}
          </div>
        </header>

        {/* Navigation */}
        <nav className="bg-white dark:bg-gray-800 rounded-xl p-4 mb-6 shadow-lg">
          <div className="flex flex-wrap gap-2">
            {navigationItems.map((item) => (
              <button
                key={item.mode}
                className={`px-4 py-2 rounded-lg text-sm font-bold transition-all ${
                  activeMode === item.mode
                    ? 'bg-blue-600 text-white shadow-lg'
                    : 'bg-gray-100 dark:bg-gray-700 text-gray-700 dark:text-gray-300 hover:bg-gray-200 dark:hover:bg-gray-600'
                }`}
                onClick={() => setActiveMode(item.mode)}
                title={item.description}
              >
                <span className="mr-2">{item.icon}</span>
                {item.label}
              </button>
            ))}
          </div>
        </nav>

        {/* Screen Content */}
        <main>
          {activeMode === 'data' && <DataManager />}
          {activeMode === 'strategy' && <StrategyBuilder />}
          {activeMode === 'combo-optimizer' && <ComboOptimizer />}
          {activeMode === 'pine-tester' && <PineScriptTester />}
          {activeMode === 'live-trading' && <LiveTradingDashboard />}
          {activeMode === 'admin' && <AdminPanel />}
        </main>
      </div>
    </div>
  )
}

export default App
