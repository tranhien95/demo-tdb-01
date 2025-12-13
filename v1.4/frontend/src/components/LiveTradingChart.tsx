import React, { useEffect, useRef } from 'react';
import { createChart, ColorType, CrosshairMode, SeriesMarkerPosition } from 'lightweight-charts';

interface ChartCandle {
  time: string | number;
  open: number;
  high: number;
  low: number;
  close: number;
  volume: number;
}

interface LiveTradingChartProps {
  candles: ChartCandle[];
  trades: Array<{
    entryTime: string;
    entryPrice: number;
    side: string;
    exitTime?: string;
    exitPrice?: number;
  }>;
  symbol: string;
  timeframe: string;
}

const LiveTradingChart: React.FC<LiveTradingChartProps> = ({
  candles,
  trades,
}) => {
  const chartContainerRef = useRef<HTMLDivElement>(null);
  const chartRef = useRef<any>(null);
  const candleSeriesRef = useRef<any>(null);

  useEffect(() => {
    if (!chartContainerRef.current || !candles.length) return;

    // Create chart
    const chart = createChart(chartContainerRef.current, {
      layout: {
        background: { type: ColorType.Solid, color: '#1e293b' },
        textColor: '#d1d5db',
      },
      width: chartContainerRef.current.clientWidth,
      height: 500,
      timeScale: {
        timeVisible: true,
        secondsVisible: false,
      },
      crosshair: {
        mode: CrosshairMode.Normal,
      },
    });

    chartRef.current = chart;

    // Create candlestick series
    const candleSeries = chart.addCandlestickSeries({
      upColor: '#10b981',
      downColor: '#ef4444',
      borderUpColor: '#10b981',
      borderDownColor: '#ef4444',
      wickUpColor: '#10b981',
      wickDownColor: '#ef4444',
    });

    candleSeriesRef.current = candleSeries;

    // Add candles
    const chartData = candles.map((c) => {
      let timeValue: number;
      if (typeof c.time === 'number') {
        timeValue = c.time;
      } else {
        timeValue = Math.floor(new Date(c.time).getTime() / 1000);
      }
      return {
        time: timeValue as any,
        open: c.open,
        high: c.high,
        low: c.low,
        close: c.close,
      };
    });

    candleSeries.setData(chartData);

    // Add trade markers
    const markers: any[] = [];
    trades.forEach((trade) => {
      const entryTime = Math.floor(new Date(trade.entryTime).getTime() / 1000) as any;
      
      // Entry marker
      markers.push({
        time: entryTime,
        position: (trade.side === 'LONG' ? 'belowBar' : 'aboveBar') as SeriesMarkerPosition,
        color: trade.side === 'LONG' ? '#10b981' : '#ef4444',
        shape: trade.side === 'LONG' ? 'arrowUp' : 'arrowDown',
        text: `${trade.side} @${trade.entryPrice.toFixed(2)}`,
      });

      // Exit marker if exists
      if (trade.exitTime && trade.exitPrice) {
        const exitTime = Math.floor(new Date(trade.exitTime).getTime() / 1000) as any;
        markers.push({
          time: exitTime,
          position: (trade.side === 'LONG' ? 'aboveBar' : 'belowBar') as SeriesMarkerPosition,
          color: '#fbbf24',
          shape: 'circle',
          text: `EXIT @${trade.exitPrice.toFixed(2)}`,
        });
      }
    });

    candleSeries.setMarkers(markers);

    // Fit content
    chart.timeScale().fitContent();

    // Handle resize
    const handleResize = () => {
      if (chartContainerRef.current) {
        chart.applyOptions({
          width: chartContainerRef.current.clientWidth,
        });
      }
    };

    window.addEventListener('resize', handleResize);

    return () => {
      window.removeEventListener('resize', handleResize);
      chart.remove();
    };
  }, [candles, trades]);

  return (
    <div
      ref={chartContainerRef}
      className="w-full bg-slate-900 rounded"
      style={{ height: '500px' }}
    />
  );
};

export default LiveTradingChart;
