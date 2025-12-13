import React, { useState, useEffect } from 'react';
import { Pause, Square, Settings } from 'lucide-react';
import LiveTradingChart from './LiveTradingChart';

interface LiveTradingConfig {
  symbol: string;
  timeframe: string;
  strategy_name: string;
  initial_balance: number;
  risk_percent: number;
  margin: number;
  stoploss_percent: number;
  reversal_strength_threshold: number;
  max_positions: number;
}

interface Position {
  id: string;
  symbol: string;
  entry_price: number;
  entry_time: string;
  quantity: number;
  side: string;
  stoploss: number;
  takeprofit: number;
  entry_signal: string;
  entry_confidence: number;
  current_price: number;
  current_pnl: number;
  current_pnl_percent: number;
}

interface ClosedTrade {
  id: string;
  symbol: string;
  entry_price: number;
  entry_time: string;
  exit_price: number;
  exit_time: string;
  quantity: number;
  side: string;
  pnl: number;
  pnl_percent: number;
  win: boolean;
  exit_reason: string;
  entry_signal: string;
  exit_signal?: string;
}

interface TradingState {
  status: string;
  config: LiveTradingConfig;
  balance: number;
  equity: number;
  used_margin: number;
  available_margin: number;
  open_positions: Position[];
  closed_trades: ClosedTrade[];
  candles: Array<{
    time: string | number;
    open: number;
    high: number;
    low: number;
    close: number;
    volume: number;
  }>;
  total_trades: number;
  winning_trades: number;
  losing_trades: number;
  win_rate: number;
  total_profit: number;
  total_loss: number;
  profit_factor: number;
  max_drawdown: number;
  daily_pnl: number;
  created_at: string;
  last_updated: string;
}

const LiveTradingDashboard: React.FC = () => {
  const [config, setConfig] = useState<LiveTradingConfig>({
    symbol: 'BTCUSDT',
    timeframe: 'M5',
    strategy_name: '',
    initial_balance: 1000,
    risk_percent: 2,
    margin: 1.0,
    stoploss_percent: 2.0,
    reversal_strength_threshold: 70,
    max_positions: 1,
  });

  const [state, setState] = useState<TradingState | null>(null);
  const [isRunning, setIsRunning] = useState(false);
  const [strategies, setStrategies] = useState<string[]>([]);
  const [updateInterval, setUpdateInterval] = useState(0);
  const [showConfig, setShowConfig] = useState(true);
  const [strategyJson, setStrategyJson] = useState('');
  const [uploadedStrategyName, setUploadedStrategyName] = useState('');

  // Load strategies on mount
  useEffect(() => {
    loadStrategies();
  }, []);

  // Auto-update if trading
  useEffect(() => {
    if (!isRunning) return;

    const interval = setInterval(() => {
      updateTrading();
    }, 5000); // Update every 5 seconds

    return () => clearInterval(interval);
  }, [isRunning]);

  const loadStrategies = async () => {
    try {
      const res = await fetch('http://localhost:4000/api/strategy/list');
      const data = await res.json();
      setStrategies(data.strategies.map((s: any) => s.name));
    } catch (error) {
      console.error('Error loading strategies:', error);
      setStrategies([]); // Empty list if API fails
    }
  };

  const handleStrategyJsonUpload = async () => {
    if (!strategyJson.trim()) {
      alert('Please paste strategy JSON');
      return;
    }

    try {
      const strategyData = JSON.parse(strategyJson);
      
      const res = await fetch('http://localhost:4000/api/strategy/upload', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(strategyData),
      });

      if (res.ok) {
        const data = await res.json();
        const strategyName = data.strategy_name;
        setUploadedStrategyName(strategyName);
        setConfig(prev => ({
          ...prev,
          strategy_name: strategyName,
        }));
        setStrategyJson('');
        // Reload strategies list
        await loadStrategies();
        alert(`✅ Strategy "${strategyName}" loaded!`);
      } else {
        alert('Failed to upload strategy');
      }
    } catch (error) {
      alert('Invalid JSON or error uploading: ' + error);
    }
  };

  const startTrading = async () => {
    try {
      const res = await fetch('http://localhost:4000/api/live-trading/start', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(config),
      });
      const data = await res.json();
      setState(data.state);
      setIsRunning(true);
      setShowConfig(false);
    } catch (error) {
      alert('Error starting trading: ' + error);
    }
  };

  const stopTrading = async () => {
    try {
      const res = await fetch('http://localhost:4000/api/live-trading/stop', {
        method: 'POST',
      });
      const data = await res.json();
      setState(data.state);
      setIsRunning(false);
    } catch (error) {
      alert('Error stopping trading: ' + error);
    }
  };

  const pauseTrading = async () => {
    try {
      const res = await fetch('http://localhost:4000/api/live-trading/pause', {
        method: 'POST',
      });
      const data = await res.json();
      setState(data.state);
    } catch (error) {
      alert('Error pausing trading: ' + error);
    }
  };

  const resumeTrading = async () => {
    try {
      const res = await fetch('http://localhost:4000/api/live-trading/resume', {
        method: 'POST',
      });
      const data = await res.json();
      setState(data.state);
    } catch (error) {
      alert('Error resuming trading: ' + error);
    }
  };

  const updateTrading = async () => {
    try {
      const res = await fetch('http://localhost:4000/api/live-trading/update', {
        method: 'POST',
      });
      const data = await res.json();
      setState(data.state);
      setUpdateInterval(prev => prev + 1);
    } catch (error) {
      console.error('Error updating trading:', error);
    }
  };

  const closeAllPositions = async () => {
    if (!confirm('Close all positions?')) return;
    try {
      const res = await fetch('http://localhost:4000/api/live-trading/close-all', {
        method: 'POST',
      });
      const data = await res.json();
      setState(data.state);
    } catch (error) {
      alert('Error closing positions: ' + error);
    }
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-900 via-slate-800 to-slate-900 text-white p-6">
      <div className="max-w-7xl mx-auto">
        {/* Header */}
        <div className="flex items-center justify-between mb-8">
          <h1 className="text-4xl font-bold">📊 Live Trading Dashboard</h1>
          <div className="flex gap-3">
            {!isRunning ? (
              <button
                onClick={() => setShowConfig(!showConfig)}
                className="flex items-center gap-2 px-4 py-2 bg-blue-600 hover:bg-blue-700 rounded-lg transition"
              >
                <Settings size={20} />
                {showConfig ? 'Hide' : 'Show'} Config
              </button>
            ) : null}
          </div>
        </div>

        {/* Config Panel */}
        {showConfig && !isRunning && (
          <div className="bg-slate-800 border border-slate-700 rounded-lg p-6 mb-6">
            <h2 className="text-xl font-bold mb-4">Trading Configuration</h2>
            
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4 mb-6">
              {/* Symbol */}
              <div>
                <label className="block text-sm font-medium mb-2">Symbol</label>
                <input
                  type="text"
                  value={config.symbol}
                  onChange={(e) => setConfig({ ...config, symbol: e.target.value })}
                  placeholder="BTCUSDT"
                  className="w-full px-3 py-2 bg-slate-700 border border-slate-600 rounded text-white placeholder-gray-400"
                />
              </div>

              {/* Timeframe */}
              <div>
                <label className="block text-sm font-medium mb-2">Timeframe</label>
                <select
                  value={config.timeframe}
                  onChange={(e) => setConfig({ ...config, timeframe: e.target.value })}
                  className="w-full px-3 py-2 bg-slate-700 border border-slate-600 rounded text-white"
                >
                  <option>M1</option>
                  <option>M5</option>
                  <option>M15</option>
                  <option>H1</option>
                  <option>H4</option>
                  <option>D</option>
                </select>
              </div>

              {/* Strategy */}
              <div>
                <label className="block text-sm font-medium mb-2">Strategy</label>
                <select
                  value={config.strategy_name}
                  onChange={(e) => setConfig({ ...config, strategy_name: e.target.value })}
                  className="w-full px-3 py-2 bg-slate-700 border border-slate-600 rounded text-white"
                >
                  <option value="">Select strategy...</option>
                  {strategies.map((s) => (
                    <option key={s} value={s}>{s}</option>
                  ))}
                </select>
              </div>

              {/* Load Strategy JSON */}
              <div className="md:col-span-2 lg:col-span-3">
                <label className="block text-sm font-medium mb-2">Or Paste Strategy JSON</label>
                <textarea
                  value={strategyJson}
                  onChange={(e) => setStrategyJson(e.target.value)}
                  placeholder={'{\n  "name": "my-strategy",\n  "indicators": [...],\n  ...'}
                  className="w-full h-24 px-3 py-2 bg-slate-700 border border-slate-600 rounded text-white text-sm font-mono placeholder-gray-400"
                />
                <button
                  onClick={handleStrategyJsonUpload}
                  className="mt-2 px-4 py-2 bg-green-600 hover:bg-green-700 rounded text-white text-sm transition"
                >
                  Upload Strategy JSON
                </button>
                {uploadedStrategyName && (
                  <p className="text-sm text-green-400 mt-1">✅ Loaded: {uploadedStrategyName}</p>
                )}
              </div>

              {/* Initial Balance */}
              <div>
                <label className="block text-sm font-medium mb-2">Initial Balance (USDT)</label>
                <input
                  type="number"
                  value={config.initial_balance}
                  onChange={(e) => setConfig({ ...config, initial_balance: parseFloat(e.target.value) })}
                  className="w-full px-3 py-2 bg-slate-700 border border-slate-600 rounded text-white"
                />
              </div>

              {/* Risk % */}
              <div>
                <label className="block text-sm font-medium mb-2">Risk % per Trade</label>
                <input
                  type="number"
                  value={config.risk_percent}
                  onChange={(e) => setConfig({ ...config, risk_percent: parseFloat(e.target.value) })}
                  step="0.1"
                  className="w-full px-3 py-2 bg-slate-700 border border-slate-600 rounded text-white"
                />
              </div>

              {/* Margin */}
              <div>
                <label className="block text-sm font-medium mb-2">Margin (Leverage)</label>
                <input
                  type="number"
                  value={config.margin}
                  onChange={(e) => setConfig({ ...config, margin: parseFloat(e.target.value) })}
                  step="0.5"
                  className="w-full px-3 py-2 bg-slate-700 border border-slate-600 rounded text-white"
                />
              </div>

              {/* Stop Loss % */}
              <div>
                <label className="block text-sm font-medium mb-2">Stop Loss %</label>
                <input
                  type="number"
                  value={config.stoploss_percent}
                  onChange={(e) => setConfig({ ...config, stoploss_percent: parseFloat(e.target.value) })}
                  step="0.1"
                  className="w-full px-3 py-2 bg-slate-700 border border-slate-600 rounded text-white"
                />
              </div>

              {/* Reversal Strength */}
              <div>
                <label className="block text-sm font-medium mb-2">Reversal Strength %</label>
                <input
                  type="number"
                  value={config.reversal_strength_threshold}
                  onChange={(e) => setConfig({ ...config, reversal_strength_threshold: parseFloat(e.target.value) })}
                  step="5"
                  className="w-full px-3 py-2 bg-slate-700 border border-slate-600 rounded text-white"
                />
              </div>

              {/* Max Positions */}
              <div>
                <label className="block text-sm font-medium mb-2">Max Positions</label>
                <input
                  type="number"
                  value={config.max_positions}
                  onChange={(e) => setConfig({ ...config, max_positions: parseInt(e.target.value) })}
                  min="1"
                  className="w-full px-3 py-2 bg-slate-700 border border-slate-600 rounded text-white"
                />
              </div>
            </div>

            <button
              onClick={startTrading}
              disabled={!config.strategy_name}
              className="w-full py-3 bg-green-600 hover:bg-green-700 disabled:bg-gray-600 rounded-lg font-bold transition"
            >
              ▶️ START TRADING
            </button>
          </div>
        )}

        {/* Trading Active Panel */}
        {isRunning && state && (
          <>
            {/* Controls */}
            <div className="flex gap-3 mb-6">
              <button
                onClick={pauseTrading}
                className="flex items-center gap-2 px-4 py-2 bg-yellow-600 hover:bg-yellow-700 rounded-lg transition"
              >
                <Pause size={20} />
                Pause
              </button>
              <button
                onClick={stopTrading}
                className="flex items-center gap-2 px-4 py-2 bg-red-600 hover:bg-red-700 rounded-lg transition"
              >
                <Square size={20} />
                Stop
              </button>
              {state.open_positions.length > 0 && (
                <button
                  onClick={closeAllPositions}
                  className="flex items-center gap-2 px-4 py-2 bg-orange-600 hover:bg-orange-700 rounded-lg transition"
                >
                  Close All Positions
                </button>
              )}
            </div>

            {/* Live Trading Chart */}
            {state.candles && state.candles.length > 0 && (
              <div className="bg-slate-800 border border-slate-700 rounded-lg p-4 mb-6">
                <h3 className="text-lg font-bold mb-4">📊 Live Chart</h3>
                <LiveTradingChart
                  candles={state.candles.map((candle: any) => ({
                    time: typeof candle.time === 'string' ? candle.time : new Date(candle.time * 1000).toISOString(),
                    open: candle.open,
                    high: candle.high,
                    low: candle.low,
                    close: candle.close,
                    volume: candle.volume
                  }))}
                  trades={[
                    ...state.open_positions.map(pos => ({
                      entryTime: pos.entry_time,
                      entryPrice: pos.entry_price,
                      side: pos.side,
                      exitTime: undefined,
                      exitPrice: undefined
                    })),
                    ...state.closed_trades.map(trade => ({
                      entryTime: trade.entry_time,
                      entryPrice: trade.entry_price,
                      side: trade.side,
                      exitTime: trade.exit_time,
                      exitPrice: trade.exit_price
                    }))
                  ]}
                  symbol={config.symbol}
                  timeframe={config.timeframe}
                />
              </div>
            )}

            {/* Account Stats */}
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4 mb-6">
              <div className="bg-slate-800 border border-slate-700 rounded-lg p-4">
                <div className="text-sm text-gray-400 mb-1">Balance</div>
                <div className="text-2xl font-bold">${state.balance.toFixed(2)}</div>
              </div>

              <div className="bg-slate-800 border border-slate-700 rounded-lg p-4">
                <div className="text-sm text-gray-400 mb-1">Equity</div>
                <div className={`text-2xl font-bold ${state.equity >= state.balance ? 'text-green-400' : 'text-red-400'}`}>
                  ${state.equity.toFixed(2)}
                </div>
              </div>

              <div className="bg-slate-800 border border-slate-700 rounded-lg p-4">
                <div className="text-sm text-gray-400 mb-1">Daily P&L</div>
                <div className={`text-2xl font-bold ${state.daily_pnl >= 0 ? 'text-green-400' : 'text-red-400'}`}>
                  ${state.daily_pnl.toFixed(2)}
                </div>
              </div>

              <div className="bg-slate-800 border border-slate-700 rounded-lg p-4">
                <div className="text-sm text-gray-400 mb-1">Win Rate</div>
                <div className="text-2xl font-bold">{state.win_rate.toFixed(1)}%</div>
                <div className="text-xs text-gray-500">({state.winning_trades}W / {state.losing_trades}L)</div>
              </div>
            </div>

            {/* Performance Metrics */}
            <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-6">
              <div className="bg-slate-800 border border-slate-700 rounded-lg p-4">
                <div className="text-sm text-gray-400 mb-2">Profit Factor</div>
                <div className="text-xl font-bold text-blue-400">{state.profit_factor.toFixed(2)}</div>
                <div className="text-xs text-gray-500 mt-1">Profit: ${state.total_profit.toFixed(2)}</div>
                <div className="text-xs text-gray-500">Loss: ${state.total_loss.toFixed(2)}</div>
              </div>

              <div className="bg-slate-800 border border-slate-700 rounded-lg p-4">
                <div className="text-sm text-gray-400 mb-2">Max Drawdown</div>
                <div className={`text-xl font-bold ${state.max_drawdown <= 10 ? 'text-green-400' : state.max_drawdown <= 20 ? 'text-yellow-400' : 'text-red-400'}`}>
                  {state.max_drawdown.toFixed(2)}%
                </div>
              </div>

              <div className="bg-slate-800 border border-slate-700 rounded-lg p-4">
                <div className="text-sm text-gray-400 mb-2">Margin Usage</div>
                <div className="text-xl font-bold">
                  {((state.used_margin / (state.used_margin + state.available_margin)) * 100).toFixed(1)}%
                </div>
                <div className="text-xs text-gray-500 mt-1">Used: ${state.used_margin.toFixed(2)}</div>
              </div>
            </div>

            {/* Open Positions */}
            {state.open_positions.length > 0 && (
              <div className="bg-slate-800 border border-slate-700 rounded-lg p-6 mb-6">
                <h3 className="text-lg font-bold mb-4">📍 Open Positions ({state.open_positions.length})</h3>
                <div className="space-y-3">
                  {state.open_positions.map((pos) => (
                    <div key={pos.id} className="bg-slate-700 rounded-lg p-4">
                      <div className="flex justify-between items-start mb-3">
                        <div>
                          <div className="font-bold text-lg">
                            {pos.side} {pos.quantity.toFixed(4)} {pos.symbol}
                          </div>
                          <div className="text-sm text-gray-400">Entry: ${pos.entry_price.toFixed(2)}</div>
                        </div>
                        <div className={`text-right font-bold text-xl ${pos.current_pnl >= 0 ? 'text-green-400' : 'text-red-400'}`}>
                          ${pos.current_pnl.toFixed(2)} ({pos.current_pnl_percent.toFixed(2)}%)
                        </div>
                      </div>

                      <div className="grid grid-cols-3 gap-3 text-sm">
                        <div>
                          <div className="text-gray-400">Current</div>
                          <div className="font-bold">${pos.current_price.toFixed(2)}</div>
                        </div>
                        <div>
                          <div className="text-gray-400">SL</div>
                          <div className="font-bold text-red-400">${pos.stoploss.toFixed(2)}</div>
                        </div>
                        <div>
                          <div className="text-gray-400">TP</div>
                          <div className="font-bold text-green-400">${pos.takeprofit.toFixed(2)}</div>
                        </div>
                      </div>

                      <div className="mt-2 text-xs text-gray-500">
                        Entry Signal: {pos.entry_signal} (Confidence: {pos.entry_confidence.toFixed(1)}%)
                      </div>
                    </div>
                  ))}
                </div>
              </div>
            )}

            {/* Recent Trades */}
            {state.closed_trades && state.closed_trades.length > 0 && (
              <div className="bg-slate-800 border border-slate-700 rounded-lg p-6">
                <h3 className="text-lg font-bold mb-4">📋 Recent Trades</h3>
                <div className="overflow-x-auto">
                  <table className="w-full text-sm">
                    <thead className="border-b border-slate-600">
                      <tr>
                        <th className="text-left py-2">Entry Time</th>
                        <th>Side</th>
                        <th>Entry Price</th>
                        <th>Exit Price</th>
                        <th className="text-right">P&L</th>
                        <th>Reason</th>
                      </tr>
                    </thead>
                    <tbody>
                      {state.closed_trades.slice(-10).reverse().map((trade) => (
                        <tr key={trade.id} className="border-b border-slate-700">
                          <td className="py-2">{new Date(trade.entry_time).toLocaleTimeString()}</td>
                          <td>
                            <span className={trade.side === 'LONG' ? 'text-green-400' : 'text-red-400'}>
                              {trade.side}
                            </span>
                          </td>
                          <td>${trade.entry_price.toFixed(2)}</td>
                          <td>${trade.exit_price.toFixed(2)}</td>
                          <td className={`text-right font-bold ${trade.win ? 'text-green-400' : 'text-red-400'}`}>
                            ${trade.pnl.toFixed(2)} ({trade.pnl_percent.toFixed(2)}%)
                          </td>
                          <td className="text-gray-400">{trade.exit_reason}</td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>
              </div>
            )}
          </>
        )}

        {/* No Trading State */}
        {!isRunning && !showConfig && (
          <div className="text-center py-12">
            <div className="text-gray-400 text-lg">No trading session active</div>
            <button
              onClick={() => setShowConfig(true)}
              className="mt-4 px-6 py-2 bg-blue-600 hover:bg-blue-700 rounded-lg transition"
            >
              Start New Session
            </button>
          </div>
        )}
      </div>
    </div>
  );
};

export default LiveTradingDashboard;
