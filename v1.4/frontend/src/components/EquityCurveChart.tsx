import React, { useMemo } from 'react'

interface Props {
  equityCurve: number[]
  initialCapital: number
}

export const EquityCurveChart: React.FC<Props> = ({ equityCurve, initialCapital }) => {
  const stats = useMemo(() => {
    if (!equityCurve || equityCurve.length === 0) {
      return {
        final: initialCapital,
        max: initialCapital,
        min: initialCapital,
        totalReturn: 0,
        maxDrawdown: 0
      }
    }

    const final = equityCurve[equityCurve.length - 1]
    const max = Math.max(...equityCurve)
    const min = Math.min(...equityCurve)
    const totalReturn = ((final - initialCapital) / initialCapital) * 100
    
    // Calculate max drawdown
    let maxDrawdown = 0
    let peak = equityCurve[0]
    
    for (const value of equityCurve) {
      if (value > peak) {
        peak = value
      }
      const drawdown = ((peak - value) / peak) * 100
      if (drawdown > maxDrawdown) {
        maxDrawdown = drawdown
      }
    }

    return { final, max, min, totalReturn, maxDrawdown }
  }, [equityCurve, initialCapital])

  // Calculate chart dimensions and scaling
  const chartWidth = 800
  const chartHeight = 400
  const padding = { top: 40, right: 60, bottom: 60, left: 80 }
  const innerWidth = chartWidth - padding.left - padding.right
  const innerHeight = chartHeight - padding.top - padding.bottom

  // Scale functions
  const scaleY = (value: number) => {
    const range = stats.max - stats.min
    const buffer = range * 0.1 // 10% buffer
    const min = stats.min - buffer
    const max = stats.max + buffer
    return innerHeight - ((value - min) / (max - min)) * innerHeight
  }

  const scaleX = (index: number) => {
    return (index / Math.max(equityCurve.length - 1, 1)) * innerWidth
  }

  // Generate path for equity curve
  const pathData = useMemo(() => {
    if (!equityCurve || equityCurve.length === 0) return ''
    
    return equityCurve
      .map((value, index) => {
        const x = scaleX(index)
        const y = scaleY(value)
        return `${index === 0 ? 'M' : 'L'} ${x},${y}`
      })
      .join(' ')
  }, [equityCurve])

  // Generate area path (filled under curve)
  const areaPathData = useMemo(() => {
    if (!equityCurve || equityCurve.length === 0) return ''
    
    const points = equityCurve
      .map((value, index) => `${scaleX(index)},${scaleY(value)}`)
      .join(' L ')
    
    const lastX = scaleX(equityCurve.length - 1)
    const baseY = scaleY(Math.min(initialCapital, stats.min - (stats.max - stats.min) * 0.1))
    
    return `M 0,${baseY} L ${points} L ${lastX},${baseY} Z`
  }, [equityCurve])

  // Y-axis ticks
  const yTicks = useMemo(() => {
    const range = stats.max - stats.min
    const buffer = range * 0.1
    const min = stats.min - buffer
    const max = stats.max + buffer
    const step = (max - min) / 5
    
    return Array.from({ length: 6 }, (_, i) => {
      const value = min + step * i
      return {
        value: Math.round(value),
        y: scaleY(value)
      }
    })
  }, [stats])

  // X-axis ticks
  const xTicks = useMemo(() => {
    const numTicks = 5
    return Array.from({ length: numTicks }, (_, i) => {
      const index = Math.floor((i / (numTicks - 1)) * (equityCurve.length - 1))
      return {
        label: index === 0 ? 'Start' : index === equityCurve.length - 1 ? 'End' : `${index}`,
        x: scaleX(index)
      }
    })
  }, [equityCurve])

  const formatCurrency = (value: number) => {
    return new Intl.NumberFormat('en-US', {
      style: 'currency',
      currency: 'USD',
      minimumFractionDigits: 0,
      maximumFractionDigits: 0
    }).format(value)
  }

  if (!equityCurve || equityCurve.length === 0) {
    return (
      <div className="bg-white dark:bg-gray-800 rounded-xl p-6 shadow-lg">
        <h3 className="text-2xl font-bold mb-4">📈 Equity Curve</h3>
        <div className="text-center text-gray-600 py-12">
          No equity data available
        </div>
      </div>
    )
  }

  return (
    <div className="bg-white dark:bg-gray-800 rounded-xl p-6 shadow-lg">
      <h3 className="text-2xl font-bold mb-6">📈 Equity Curve - Portfolio Growth</h3>
      
      {/* Stats Summary */}
      <div className="grid grid-cols-2 md:grid-cols-5 gap-4 mb-6">
        <div className="p-3 bg-blue-50 dark:bg-blue-900/20 rounded-lg">
          <div className="text-xs text-gray-600">Initial Capital</div>
          <div className="text-lg font-bold">{formatCurrency(initialCapital)}</div>
        </div>
        <div className="p-3 bg-green-50 dark:bg-green-900/20 rounded-lg">
          <div className="text-xs text-gray-600">Final Balance</div>
          <div className={`text-lg font-bold ${stats.final >= initialCapital ? 'text-green-600' : 'text-red-600'}`}>
            {formatCurrency(stats.final)}
          </div>
        </div>
        <div className="p-3 bg-purple-50 dark:bg-purple-900/20 rounded-lg">
          <div className="text-xs text-gray-600">Total Return</div>
          <div className={`text-lg font-bold ${stats.totalReturn >= 0 ? 'text-green-600' : 'text-red-600'}`}>
            {stats.totalReturn >= 0 ? '+' : ''}{stats.totalReturn.toFixed(2)}%
          </div>
        </div>
        <div className="p-3 bg-orange-50 dark:bg-orange-900/20 rounded-lg">
          <div className="text-xs text-gray-600">Peak Balance</div>
          <div className="text-lg font-bold text-orange-600">{formatCurrency(stats.max)}</div>
        </div>
        <div className="p-3 bg-red-50 dark:bg-red-900/20 rounded-lg">
          <div className="text-xs text-gray-600">Max Drawdown</div>
          <div className="text-lg font-bold text-red-600">{stats.maxDrawdown.toFixed(2)}%</div>
        </div>
      </div>

      {/* Chart */}
      <div className="overflow-x-auto">
        <svg 
          width={chartWidth} 
          height={chartHeight} 
          className="mx-auto"
          style={{ maxWidth: '100%', height: 'auto' }}
        >
          {/* Grid lines */}
          <g transform={`translate(${padding.left}, ${padding.top})`}>
            {yTicks.map((tick, i) => (
              <line
                key={i}
                x1={0}
                y1={tick.y}
                x2={innerWidth}
                y2={tick.y}
                stroke="#e5e7eb"
                strokeWidth={1}
                strokeDasharray="4 4"
              />
            ))}
          </g>

          {/* Area under curve */}
          <g transform={`translate(${padding.left}, ${padding.top})`}>
            <path
              d={areaPathData}
              fill="url(#gradient)"
              opacity={0.3}
            />
            <defs>
              <linearGradient id="gradient" x1="0%" y1="0%" x2="0%" y2="100%">
                <stop offset="0%" stopColor={stats.totalReturn >= 0 ? '#10b981' : '#ef4444'} stopOpacity={0.8} />
                <stop offset="100%" stopColor={stats.totalReturn >= 0 ? '#10b981' : '#ef4444'} stopOpacity={0.1} />
              </linearGradient>
            </defs>
          </g>

          {/* Equity curve line */}
          <g transform={`translate(${padding.left}, ${padding.top})`}>
            <path
              d={pathData}
              fill="none"
              stroke={stats.totalReturn >= 0 ? '#10b981' : '#ef4444'}
              strokeWidth={3}
              strokeLinecap="round"
              strokeLinejoin="round"
            />
          </g>

          {/* Initial capital reference line */}
          <g transform={`translate(${padding.left}, ${padding.top})`}>
            <line
              x1={0}
              y1={scaleY(initialCapital)}
              x2={innerWidth}
              y2={scaleY(initialCapital)}
              stroke="#6b7280"
              strokeWidth={2}
              strokeDasharray="8 4"
            />
            <text
              x={innerWidth + 5}
              y={scaleY(initialCapital)}
              fill="#6b7280"
              fontSize={12}
              dominantBaseline="middle"
            >
              Initial
            </text>
          </g>

          {/* Y-axis */}
          <g transform={`translate(${padding.left}, ${padding.top})`}>
            <line
              x1={0}
              y1={0}
              x2={0}
              y2={innerHeight}
              stroke="#374151"
              strokeWidth={2}
            />
            {yTicks.map((tick, i) => (
              <g key={i}>
                <line
                  x1={-5}
                  y1={tick.y}
                  x2={0}
                  y2={tick.y}
                  stroke="#374151"
                  strokeWidth={2}
                />
                <text
                  x={-10}
                  y={tick.y}
                  textAnchor="end"
                  dominantBaseline="middle"
                  fontSize={12}
                  fill="#6b7280"
                >
                  {formatCurrency(tick.value)}
                </text>
              </g>
            ))}
          </g>

          {/* X-axis */}
          <g transform={`translate(${padding.left}, ${padding.top + innerHeight})`}>
            <line
              x1={0}
              y1={0}
              x2={innerWidth}
              y2={0}
              stroke="#374151"
              strokeWidth={2}
            />
            {xTicks.map((tick, i) => (
              <g key={i}>
                <line
                  x1={tick.x}
                  y1={0}
                  x2={tick.x}
                  y2={5}
                  stroke="#374151"
                  strokeWidth={2}
                />
                <text
                  x={tick.x}
                  y={20}
                  textAnchor="middle"
                  fontSize={12}
                  fill="#6b7280"
                >
                  {tick.label}
                </text>
              </g>
            ))}
          </g>

          {/* Axis labels */}
          <text
            x={padding.left / 2}
            y={chartHeight / 2}
            textAnchor="middle"
            fontSize={14}
            fontWeight="bold"
            fill="#374151"
            transform={`rotate(-90, ${padding.left / 2}, ${chartHeight / 2})`}
          >
            Balance ($)
          </text>
          <text
            x={chartWidth / 2}
            y={chartHeight - 10}
            textAnchor="middle"
            fontSize={14}
            fontWeight="bold"
            fill="#374151"
          >
            Trade Number
          </text>
        </svg>
      </div>

      {/* Legend */}
      <div className="mt-6 flex justify-center gap-6 text-sm">
        <div className="flex items-center gap-2">
          <div className="w-4 h-4 rounded" style={{ backgroundColor: stats.totalReturn >= 0 ? '#10b981' : '#ef4444' }}></div>
          <span>Equity Curve</span>
        </div>
        <div className="flex items-center gap-2">
          <div className="w-4 h-1 bg-gray-600"></div>
          <span>Initial Capital</span>
        </div>
      </div>
    </div>
  )
}
