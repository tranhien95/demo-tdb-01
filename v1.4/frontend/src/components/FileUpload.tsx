import React, { useRef } from 'react'
import Papa from 'papaparse'
import { useOptimizerStore } from '../store/optimizerStore'
import { OHLCV } from '../types'

export const FileUpload: React.FC = () => {
  const fileInputRef = useRef<HTMLInputElement>(null)
  const { setCsvData, csvData } = useOptimizerStore()

  const handleFileUpload = (event: React.ChangeEvent<HTMLInputElement>) => {
    const file = event.target.files?.[0]
    if (!file) return

    Papa.parse(file, {
      header: true,
      dynamicTyping: true,
      skipEmptyLines: true,
      complete: (results) => {
        const data = results.data as any[]
        const filtered = data.filter((d: any) => {
          const keys = Object.keys(d)
          const hasOHLC = keys.some(k => k.toLowerCase().includes('open')) &&
                         keys.some(k => k.toLowerCase().includes('high')) &&
                         keys.some(k => k.toLowerCase().includes('low')) &&
                         keys.some(k => k.toLowerCase().includes('close'))
          return hasOHLC && d[keys[1]] && d[keys[2]] && d[keys[3]] && d[keys[4]]
        })

        const normalized: OHLCV[] = filtered.map((d: any) => {
          const keys = Object.keys(d)
          const timeKey = keys.find(k => k.toLowerCase().includes('time'))
          let timeValue = d[timeKey!]
          
          if (timeValue && typeof timeValue === 'number' && timeValue > 1000000000) {
            const date = new Date(timeValue * 1000)
            timeValue = date.toISOString()
          }
          
          return {
            time: timeValue || '',
            open: parseFloat(d[keys.find(k => k.toLowerCase().includes('open'))!]),
            high: parseFloat(d[keys.find(k => k.toLowerCase().includes('high'))!]),
            low: parseFloat(d[keys.find(k => k.toLowerCase().includes('low'))!]),
            close: parseFloat(d[keys.find(k => k.toLowerCase().includes('close'))!]),
            volume: parseFloat(d[keys.find(k => k.toLowerCase().includes('volume'))!]) || Math.random() * 5000 + 1000
          }
        })

        setCsvData(normalized)
      },
      error: (error) => {
        alert('❌ Lỗi: ' + error.message)
      }
    })
  }

  return (
    <div className="card">
      <div 
        className="border-2 border-dashed border-primary rounded-lg p-2 text-center cursor-pointer hover:bg-primary/5 transition-all"
        onClick={() => fileInputRef.current?.click()}
      >
        <div className="text-secondary text-xl mb-3">📊 Kéo file CSV vào đây hoặc click để chọn</div>
        <div className="text-gray-400 text-sm">Hỗ trợ: CSV (OHLCV format)</div>
      </div>
      <input
        ref={fileInputRef}
        type="file"
        accept=".csv"
        className="hidden"
        onChange={handleFileUpload}
      />
      {csvData && (
        <div className="mt-4 text-center text-gray-300">
          ✅ Tải thành công: <strong>{csvData.length}</strong> candles
        </div>
      )}
    </div>
  )
}
