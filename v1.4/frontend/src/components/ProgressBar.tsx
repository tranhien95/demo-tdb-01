import React from 'react'

interface Props {
  progress: number  // 0-100
  tested: number
  withTrades: number
  timeElapsed: number
}

const formatTime = (seconds: number) => {
  const hours = Math.floor(seconds / 3600)
  const minutes = Math.floor((seconds % 3600) / 60)
  const secs = seconds % 60

  if (hours > 0) {
    return `${hours}h ${minutes}m ${secs}s`
  }
  if (minutes > 0) {
    return `${minutes}m ${secs}s`
  }
  return `${secs}s`
}

export const ProgressBar: React.FC<Props> = ({ progress, tested, withTrades, timeElapsed }) => {
  return (
    <div className="bg-white dark:bg-gray-800 rounded-xl p-6 shadow-lg border-2 border-blue-500">
      <h3 className="text-xl font-bold mb-4">⏳ Backtest Running...</h3>

      {/* Main Progress Bar */}
      <div className="space-y-2 mb-6">
        <div className="flex justify-between items-center mb-2">
          <span className="font-bold">{progress.toFixed(1)}%</span>
          <span className="text-sm text-gray-600">{progress.toFixed(1)}% complete</span>
        </div>
        <div className="w-full h-8 bg-gray-200 dark:bg-gray-700 rounded-full overflow-hidden">
          <div
            className="h-full bg-gradient-to-r from-blue-500 to-blue-600 transition-all duration-300 flex items-center justify-center"
            style={{ width: `${progress}%` }}
          >
            {progress > 10 && (
              <span className="text-white text-xs font-bold">{progress.toFixed(0)}%</span>
            )}
          </div>
        </div>
      </div>

      {/* Stats Grid */}
      <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mb-6">
        <div className="p-3 bg-blue-50 dark:bg-blue-900/20 rounded-lg">
          <div className="text-xs text-gray-600 mb-1">Progress</div>
          <div className="text-2xl font-bold text-blue-600">{progress.toFixed(1)}%</div>
        </div>
        <div className="p-3 bg-purple-50 dark:bg-purple-900/20 rounded-lg">
          <div className="text-xs text-gray-600 mb-1">Tested</div>
          <div className="text-2xl font-bold text-purple-600">{tested}</div>
        </div>
        <div className="p-3 bg-green-50 dark:bg-green-900/20 rounded-lg">
          <div className="text-xs text-gray-600 mb-1">With Trades</div>
          <div className="text-2xl font-bold text-green-600">{withTrades}</div>
        </div>
        <div className="p-3 bg-orange-50 dark:bg-orange-900/20 rounded-lg">
          <div className="text-xs text-gray-600 mb-1">Time Elapsed</div>
          <div className="text-lg font-bold text-orange-600">{formatTime(timeElapsed)}</div>
        </div>
      </div>

      {/* Info Text */}
      <div className="text-center text-sm text-gray-600">
        <p>🔄 Testing combinations... Please wait</p>
      </div>
    </div>
  )
}
