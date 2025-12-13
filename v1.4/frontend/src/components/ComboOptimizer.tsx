import React, { useState } from 'react'
import { useOptimizerStore } from '../store/optimizerStore'
import { optimizerAPI } from '../services/api'
import { ControlsPanel } from './ControlsPanel'
import { ProgressBar } from './ProgressBar'
import { ResultsTable } from './ResultsTable'
import { ChartView } from './ChartView'
import { Layout } from './Layout'

export const ComboOptimizer: React.FC = () => {
  const { csvData, params, setProgress, setResults, progress, results, showChart } = useOptimizerStore()
  const [startTime, setStartTime] = useState(0)

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
    <Layout
      title="🔍 Combo Optimizer"
      description="Tối ưu hóa indicator combinations với các tham số tùy chỉnh"
    >
      <div className="space-y-6">
        <div className="bg-white dark:bg-gray-800 rounded-xl p-4 shadow-lg">
          <ControlsPanel />
        </div>

        <div className="flex gap-4">
          <button
            className="btn-primary flex-1"
            onClick={runOptimization}
            disabled={!csvData || progress.isRunning}
          >
            {progress.isRunning ? '⏳ Đang xử lý...' : '▶️ Chạy Optimization'}
          </button>
          <button 
            className="btn-secondary"
            onClick={() => {
              setResults([])
              setProgress({ isRunning: false, percent: 0, tested: 0, withTrades: 0 })
            }}
          >
            🔄 Reset
          </button>
        </div>

        {progress.isRunning && (
          <ProgressBar
            progress={progress.percent || 0}
            tested={progress.tested || 0}
            withTrades={progress.withTrades || 0}
            timeElapsed={Math.floor((Date.now() - startTime) / 1000)}
          />
        )}

        {results.length > 0 && !progress.isRunning && (
          <div className="bg-white dark:bg-gray-800 rounded-xl p-6 shadow-lg">
            <ResultsTable />
          </div>
        )}

        {showChart && (
          <div className="bg-white dark:bg-gray-800 rounded-xl p-6 shadow-lg">
            <ChartView />
          </div>
        )}
      </div>
    </Layout>
  )
}

