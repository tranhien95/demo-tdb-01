import React, { useState } from 'react'
import { useOptimizerStore } from './store/optimizerStore'
import { optimizerAPI } from './services/api'
import { FileUpload } from './components/FileUpload'
import { ControlsPanel } from './components/ControlsPanel'
import { ProgressBar } from './components/ProgressBar'
import { ResultsTable } from './components/ResultsTable'
import { ChartView } from './components/ChartView'
import { StrategyBuilder } from './components/StrategyBuilder'

function App() {
  const { csvData, params, setProgress, setResults, progress, results, showChart } = useOptimizerStore()
  const [startTime, setStartTime] = useState(0)
  const [activeMode, setActiveMode] = useState<'optimizer' | 'strategy'>('strategy')

  const runOptimization = async () => {
    if (!csvData || csvData.length < 100) {
      alert('⚠️ Cần ít nhất 100 candles!')
      return
    }

    setStartTime(Date.now())
    setProgress({ isRunning: true, percent: 0, tested: 0, withTrades: 0 })

    try {
      const response = await optimizerAPI.runOptimization(csvData, params)
      const reader = response.body?.getReader()
      const decoder = new TextDecoder()
      
      if (!reader) {
        throw new Error('No reader available')
      }

      let buffer = ''
      let finalData = null

      while (true) {
        const { done, value } = await reader.read()
        if (done) break

        buffer += decoder.decode(value, { stream: true })
        const lines = buffer.split('\n')

        for (let i = 0; i < lines.length - 1; i++) {
          const line = lines[i].trim()
          if (line.startsWith('data: ')) {
            try {
              const jsonStr = line.substring(6)
              const event = JSON.parse(jsonStr)

              if (event.final) {
                finalData = event.data
              } else if (event.error) {
                throw new Error(event.error)
              } else if (event.progress !== undefined) {
                setProgress({
                  percent: event.progress,
                  tested: event.tested,
                  withTrades: event.with_trades,
                  timeElapsed: Math.round((Date.now() - startTime) / 1000)
                })
              }
            } catch (e) {
              console.error('Parse error:', e)
            }
          }
        }

        buffer = lines[lines.length - 1]
      }

      if (finalData) {
        setResults(finalData.results)
        setProgress({ isRunning: false })
      }
    } catch (error) {
      console.error('❌ Backend error:', error)
      alert('⚠️ Lỗi kết nối backend:\n' + (error as Error).message)
      setProgress({ isRunning: false })
    }
  }

  return (
    <div className="min-h-screen p-6">
      <div className="max-w-7xl mx-auto">
        <header className="gradient-header rounded-2xl p-4 text-center mb-6 shadow-2xl">
          <div className="flex items-center justify-between">
            <div className="flex-1">
              <h1 className="text-2xl font-bold">🎯 Combo Optimizer v1.4</h1>
              <p className="text-xs opacity-90 mt-1">Strategy Builder + Combo Optimizer</p>
            </div>

            {/* Mode Switcher */}
            <div className="flex gap-3">
            <button
              className={`px-4 py-2 rounded-lg text-sm font-bold transition-all ${
                activeMode === 'strategy'
                  ? 'bg-white text-blue-600 shadow-lg'
                  : 'bg-white/20 text-white hover:bg-white/30'
              }`}
              onClick={() => setActiveMode('strategy')}
            >
              🎯 Strategy Builder
            </button>
            <button
              className={`px-4 py-2 rounded-lg text-sm font-bold transition-all ${
                activeMode === 'optimizer'
                  ? 'bg-white text-blue-600 shadow-lg'
                  : 'bg-white/20 text-white hover:bg-white/30'
              }`}
              onClick={() => setActiveMode('optimizer')}
            >
              🔍 Combo Optimizer
            </button>
          </div>
          </div>
        </header>

        <FileUpload />

        {activeMode === 'optimizer' ? (
          <>
            <div className="mt-6">
              <ControlsPanel />
            </div>

            <div className="mt-6 flex gap-4">
              <button
                className="btn-primary flex-1"
                onClick={runOptimization}
                disabled={!csvData || progress.isRunning}
              >
                {progress.isRunning ? '⏳ Đang xử lý...' : '▶️ Chạy Optimization'}
              </button>
              <button className="btn-secondary">🔄 Reset</button>
            </div>

            {progress.isRunning && <ProgressBar />}

            {results.length > 0 && !progress.isRunning && <ResultsTable />}

            {showChart && <ChartView />}
          </>
        ) : (
          <div className="mt-6">
            <StrategyBuilder />
          </div>
        )}
      </div>
    </div>
  )
}

export default App
