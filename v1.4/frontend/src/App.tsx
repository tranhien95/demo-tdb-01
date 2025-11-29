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
  const [activeMode, setActiveMode] = useState<'optimizer' | 'strategy'>('optimizer')

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
        <header className="gradient-header rounded-2xl p-8 text-center mb-8 shadow-2xl">
          <h1 className="text-4xl font-bold mb-3">🎯 Combo Optimizer v1.4</h1>
          <p className="text-lg opacity-90">
            Tìm Tổ Hợp Chỉ Báo Tối Ưu + Strategy Builder
          </p>
          <div className="mt-3 inline-block bg-green-500 text-white px-6 py-2 rounded-full text-sm font-bold">
            ✅ React + TypeScript + FastAPI + Weighted Indicators
          </div>

          {/* Mode Switcher */}
          <div className="mt-6 flex justify-center gap-4">
            <button
              className={`px-6 py-3 rounded-lg font-bold transition-all ${
                activeMode === 'optimizer'
                  ? 'bg-white text-blue-600 shadow-lg'
                  : 'bg-white/20 text-white hover:bg-white/30'
              }`}
              onClick={() => setActiveMode('optimizer')}
            >
              🔍 Combo Optimizer
            </button>
            <button
              className={`px-6 py-3 rounded-lg font-bold transition-all ${
                activeMode === 'strategy'
                  ? 'bg-white text-blue-600 shadow-lg'
                  : 'bg-white/20 text-white hover:bg-white/30'
              }`}
              onClick={() => setActiveMode('strategy')}
            >
              🎯 Strategy Builder
            </button>
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
