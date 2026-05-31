"""
Express API 서버 - dashboard_data.json 파일을 serving
"""
import express from 'express'
import cors from 'cors'
import { readFileSync } from 'fs'
import { join, dirname } from 'path'
import { fileURLToPath } from 'url'

const __filename = fileURLToPath(import.meta.url)
const __dirname = dirname(__filename)

const app = express()
const PORT = 3001

app.use(cors())

// dashboard_data.json 파일 serving
app.get('/api/dashboard', (req, res) => {
    try {
        const dataPath = join(__dirname, 'dashboard_data.json')
        const data = JSON.parse(readFileSync(dataPath, 'utf-8'))
        res.json(data)
    } catch (error) {
        console.error('Error reading data file:', error)
        res.status(500).json({ error: 'Failed to read data file' })
    }
})

app.listen(PORT, () => {
    console.log(`📊 API Server running on http://localhost:${PORT}`)
    console.log(`🔗 Dashboard API: http://localhost:${PORT}/api/dashboard`)
})
