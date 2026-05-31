import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

export default defineConfig({
  plugins: [react()],
  server: {
    proxy: {
      // Yahoo Finance API proxy for real-time stock data
      '/api/yfinance': {
        target: 'https://query1.finance.yahoo.com',
        changeOrigin: true,
        rewrite: (path) => path.replace(/^\/api\/yfinance/, '/v8/finance'),
      },
      // KRX API proxy
      '/api/krx': {
        target: 'https://data-api.krx.co.kr',
        changeOrigin: true,
        headers: {
          'AUTH_KEY': '875D2DA8A6C940D7BFF23955D567686A2E88FC55',
        },
      },
    },
  },
})