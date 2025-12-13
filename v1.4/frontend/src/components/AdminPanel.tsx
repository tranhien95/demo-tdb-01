import React, { useState, useEffect } from 'react'

const API_BASE = 'http://localhost:4000'

interface DashboardStats {
  statistics: {
    total_strategies: number
    total_sessions: number
    active_sessions: number
    total_trades: number
    win_rate: number
    total_profit: number
    recent_trades_7d: number
  }
  timestamp: string
}

interface Strategy {
  id: number
  name: string
  description: string
  indicator_count: number
  session_count: number
  created_at: string
  updated_at: string
}

interface Trade {
  id: number
  symbol: string
  direction: string
  entry_price: number
  exit_price: number
  profit: number
  profit_pct: number
  exit_reason: string
  entry_time: string
  exit_time: string
}

interface DBInfo {
  database_type: string
  file_size_mb: number
  table_counts: {
    strategies: number
    sessions: number
    positions: number
    closed_trades: number
    backtest_results: number
  }
}

export const AdminPanel: React.FC = () => {
  const [activeTab, setActiveTab] = useState<'dashboard' | 'strategies' | 'trades' | 'db-info'>('dashboard')
  const [dashboard, setDashboard] = useState<DashboardStats | null>(null)
  const [strategies, setStrategies] = useState<Strategy[]>([])
  const [trades, setTrades] = useState<Trade[]>([])
  const [dbInfo, setDbInfo] = useState<DBInfo | null>(null)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)

  const fetchDashboard = async () => {
    try {
      setLoading(true)
      const response = await fetch(`${API_BASE}/admin/dashboard`)
      if (!response.ok) throw new Error('Failed to fetch dashboard')
      const data = await response.json()
      setDashboard(data)
      setError(null)
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Unknown error')
    } finally {
      setLoading(false)
    }
  }

  const fetchStrategies = async () => {
    try {
      setLoading(true)
      const response = await fetch(`${API_BASE}/admin/strategies`)
      if (!response.ok) throw new Error('Failed to fetch strategies')
      const data = await response.json()
      setStrategies(data.strategies || [])
      setError(null)
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Unknown error')
    } finally {
      setLoading(false)
    }
  }

  const fetchTrades = async () => {
    try {
      setLoading(true)
      const response = await fetch(`${API_BASE}/admin/trades?limit=50`)
      if (!response.ok) throw new Error('Failed to fetch trades')
      const data = await response.json()
      setTrades(data.trades || [])
      setError(null)
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Unknown error')
    } finally {
      setLoading(false)
    }
  }

  const fetchDBInfo = async () => {
    try {
      setLoading(true)
      const response = await fetch(`${API_BASE}/admin/db-info`)
      if (!response.ok) throw new Error('Failed to fetch DB info')
      const data = await response.json()
      setDbInfo(data)
      setError(null)
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Unknown error')
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => {
    if (activeTab === 'dashboard') {
      fetchDashboard()
    } else if (activeTab === 'strategies') {
      fetchStrategies()
    } else if (activeTab === 'trades') {
      fetchTrades()
    } else if (activeTab === 'db-info') {
      fetchDBInfo()
    }
  }, [activeTab])

  return (
    <div className="bg-white rounded-2xl shadow-xl p-6">
      <h2 className="text-2xl font-bold mb-6 text-gray-800">🔧 Admin Panel</h2>

      {/* Tabs */}
      <div className="flex gap-2 mb-6 border-b">
        <button
          onClick={() => setActiveTab('dashboard')}
          className={`px-4 py-2 font-semibold transition-colors ${
            activeTab === 'dashboard'
              ? 'border-b-2 border-blue-600 text-blue-600'
              : 'text-gray-600 hover:text-gray-800'
          }`}
        >
          Dashboard
        </button>
        <button
          onClick={() => setActiveTab('strategies')}
          className={`px-4 py-2 font-semibold transition-colors ${
            activeTab === 'strategies'
              ? 'border-b-2 border-blue-600 text-blue-600'
              : 'text-gray-600 hover:text-gray-800'
          }`}
        >
          Strategies
        </button>
        <button
          onClick={() => setActiveTab('trades')}
          className={`px-4 py-2 font-semibold transition-colors ${
            activeTab === 'trades'
              ? 'border-b-2 border-blue-600 text-blue-600'
              : 'text-gray-600 hover:text-gray-800'
          }`}
        >
          Trades
        </button>
        <button
          onClick={() => setActiveTab('db-info')}
          className={`px-4 py-2 font-semibold transition-colors ${
            activeTab === 'db-info'
              ? 'border-b-2 border-blue-600 text-blue-600'
              : 'text-gray-600 hover:text-gray-800'
          }`}
        >
          Database Info
        </button>
      </div>

      {error && (
        <div className="bg-red-50 border border-red-200 text-red-700 px-4 py-3 rounded mb-4">
          ⚠️ Error: {error}
        </div>
      )}

      {loading && (
        <div className="text-center py-8">
          <div className="inline-block animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600"></div>
          <p className="mt-2 text-gray-600">Loading...</p>
        </div>
      )}

      {/* Dashboard Tab */}
      {activeTab === 'dashboard' && dashboard && (
        <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
          <div className="bg-gradient-to-br from-blue-500 to-blue-600 rounded-lg p-4 text-white">
            <div className="text-sm opacity-90">Total Strategies</div>
            <div className="text-3xl font-bold mt-2">{dashboard.statistics.total_strategies}</div>
          </div>
          <div className="bg-gradient-to-br from-green-500 to-green-600 rounded-lg p-4 text-white">
            <div className="text-sm opacity-90">Total Sessions</div>
            <div className="text-3xl font-bold mt-2">{dashboard.statistics.total_sessions}</div>
          </div>
          <div className="bg-gradient-to-br from-purple-500 to-purple-600 rounded-lg p-4 text-white">
            <div className="text-sm opacity-90">Total Trades</div>
            <div className="text-3xl font-bold mt-2">{dashboard.statistics.total_trades}</div>
          </div>
          <div className="bg-gradient-to-br from-orange-500 to-orange-600 rounded-lg p-4 text-white">
            <div className="text-sm opacity-90">Win Rate</div>
            <div className="text-3xl font-bold mt-2">{dashboard.statistics.win_rate.toFixed(1)}%</div>
          </div>
          <div className="bg-gradient-to-br from-teal-500 to-teal-600 rounded-lg p-4 text-white">
            <div className="text-sm opacity-90">Total Profit</div>
            <div className="text-3xl font-bold mt-2">${dashboard.statistics.total_profit.toFixed(2)}</div>
          </div>
          <div className="bg-gradient-to-br from-pink-500 to-pink-600 rounded-lg p-4 text-white">
            <div className="text-sm opacity-90">Active Sessions</div>
            <div className="text-3xl font-bold mt-2">{dashboard.statistics.active_sessions}</div>
          </div>
          <div className="bg-gradient-to-br from-indigo-500 to-indigo-600 rounded-lg p-4 text-white">
            <div className="text-sm opacity-90">Recent Trades (7d)</div>
            <div className="text-3xl font-bold mt-2">{dashboard.statistics.recent_trades_7d}</div>
          </div>
        </div>
      )}

      {/* Strategies Tab */}
      {activeTab === 'strategies' && (
        <div className="overflow-x-auto">
          <table className="min-w-full divide-y divide-gray-200">
            <thead className="bg-gray-50">
              <tr>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">ID</th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Name</th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Indicators</th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Sessions</th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Updated</th>
              </tr>
            </thead>
            <tbody className="bg-white divide-y divide-gray-200">
              {strategies.map((strategy) => (
                <tr key={strategy.id} className="hover:bg-gray-50">
                  <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">{strategy.id}</td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm font-medium text-gray-900">{strategy.name}</td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">{strategy.indicator_count}</td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">{strategy.session_count}</td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                    {new Date(strategy.updated_at).toLocaleDateString()}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
          {strategies.length === 0 && !loading && (
            <div className="text-center py-8 text-gray-500">No strategies found</div>
          )}
        </div>
      )}

      {/* Trades Tab */}
      {activeTab === 'trades' && (
        <div className="overflow-x-auto">
          <table className="min-w-full divide-y divide-gray-200">
            <thead className="bg-gray-50">
              <tr>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Symbol</th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Direction</th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Entry</th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Exit</th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Profit</th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Profit %</th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Exit Reason</th>
              </tr>
            </thead>
            <tbody className="bg-white divide-y divide-gray-200">
              {trades.map((trade) => (
                <tr key={trade.id} className="hover:bg-gray-50">
                  <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">{trade.symbol}</td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm">
                    <span className={`px-2 py-1 rounded text-xs font-semibold ${
                      trade.direction === 'LONG' ? 'bg-green-100 text-green-800' : 'bg-red-100 text-red-800'
                    }`}>
                      {trade.direction}
                    </span>
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">${trade.entry_price.toFixed(2)}</td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">${trade.exit_price.toFixed(2)}</td>
                  <td className={`px-6 py-4 whitespace-nowrap text-sm font-semibold ${
                    trade.profit >= 0 ? 'text-green-600' : 'text-red-600'
                  }`}>
                    ${trade.profit.toFixed(2)}
                  </td>
                  <td className={`px-6 py-4 whitespace-nowrap text-sm font-semibold ${
                    trade.profit_pct >= 0 ? 'text-green-600' : 'text-red-600'
                  }`}>
                    {trade.profit_pct.toFixed(2)}%
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">{trade.exit_reason}</td>
                </tr>
              ))}
            </tbody>
          </table>
          {trades.length === 0 && !loading && (
            <div className="text-center py-8 text-gray-500">No trades found</div>
          )}
        </div>
      )}

      {/* Database Info Tab */}
      {activeTab === 'db-info' && dbInfo && (
        <div className="space-y-6">
          <div className="bg-gray-50 rounded-lg p-6">
            <h3 className="text-lg font-semibold mb-4 text-gray-800">Database Information</h3>
            <div className="grid grid-cols-2 gap-4">
              <div>
                <div className="text-sm text-gray-600">Database Type</div>
                <div className="text-xl font-bold text-gray-900">{dbInfo.database_type}</div>
              </div>
              <div>
                <div className="text-sm text-gray-600">File Size</div>
                <div className="text-xl font-bold text-gray-900">{dbInfo.file_size_mb} MB</div>
              </div>
            </div>
          </div>

          <div className="bg-gray-50 rounded-lg p-6">
            <h3 className="text-lg font-semibold mb-4 text-gray-800">Table Counts</h3>
            <div className="grid grid-cols-2 md:grid-cols-5 gap-4">
              <div>
                <div className="text-sm text-gray-600">Strategies</div>
                <div className="text-2xl font-bold text-blue-600">{dbInfo.table_counts.strategies}</div>
              </div>
              <div>
                <div className="text-sm text-gray-600">Sessions</div>
                <div className="text-2xl font-bold text-green-600">{dbInfo.table_counts.sessions}</div>
              </div>
              <div>
                <div className="text-sm text-gray-600">Positions</div>
                <div className="text-2xl font-bold text-purple-600">{dbInfo.table_counts.positions}</div>
              </div>
              <div>
                <div className="text-sm text-gray-600">Trades</div>
                <div className="text-2xl font-bold text-orange-600">{dbInfo.table_counts.closed_trades}</div>
              </div>
              <div>
                <div className="text-sm text-gray-600">Backtests</div>
                <div className="text-2xl font-bold text-teal-600">{dbInfo.table_counts.backtest_results}</div>
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  )
}

