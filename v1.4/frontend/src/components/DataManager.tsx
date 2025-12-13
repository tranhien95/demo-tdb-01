import React from 'react'
import { FileUpload } from './FileUpload'
import { BinanceDataFetcher } from './BinanceDataFetcher'
import { Layout } from './Layout'

export const DataManager: React.FC = () => {
  return (
    <Layout
      title="📊 Data Manager"
      description="Upload CSV hoặc tải data từ Binance để sử dụng cho backtesting và optimization"
    >
      <div className="space-y-6">
        <div className="bg-white dark:bg-gray-800 rounded-xl p-4 shadow-lg">
          <h3 className="text-lg font-bold mb-3">📁 Upload CSV File</h3>
          <FileUpload />
        </div>

        <div className="bg-white dark:bg-gray-800 rounded-xl p-4 shadow-lg">
          <h3 className="text-lg font-bold mb-3">🌐 Fetch from Binance</h3>
          <BinanceDataFetcher />
        </div>
      </div>
    </Layout>
  )
}

