import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

export default defineConfig({
  base: '/stock-dashboard-sc/',
  plugins: [react()],
  server: {
    port: 5174,
    proxy: {
       '/api': {
        target: 'https://query1.finance.yahoo.com',
        changeOrigin: true,
        rewrite: (path) => path.replace(/^\/api/, '/v8/finance'),
        headers: {
           'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7)',
         },
       },
     },
   },
})
