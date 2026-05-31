/**
 * 거시경제 대시보드 API сервер
 * - dashboard_data.json 파일을 serving
 * - 5분마다 데이터 자동 갱신 (Python 데이터 수집 스크립트 실행)
 * - CORS 활성화
 */
import express from 'express'
import cors from 'cors'
import { readFileSync, writeFileSync } from 'fs'
import { join, dirname } from 'path'
import { fileURLToPath } from 'url'
import { spawn } from 'child_process'

const __filename = fileURLToPath(import.meta.url)
const __dirname = dirname(__filename)

const app = express()
const PORT = 3001

app.use(cors())
app.use(express.json())

// dashboard_data.json 파일 경로
const DATA_PATH = join(__dirname, 'dashboard_data.json')

/**
 * Python 데이터 수집 스크립트 실행
 */
function runDataFetcher() {
     return new Promise((resolve, reject) => {
          const python = spawn('python3', [join(__dirname, 'data_fetcher.py')])
          let output = ''
          let errorOutput = ''

          python.stdout.on('data', (data) => {
               output += data.toString()
               console.log(`[DATA FETCHER] ${data.toString()}`)
          })

          python.stderr.on('data', (data) => {
               errorOutput += data.toString()
               console.error(`[DATA FETCHER ERROR] ${data.toString()}`)
          })

          python.on('close', (code) => {
               if (code === 0) {
                    console.log('✅ Python 데이터 수집 완료')
                     // JSON 파일 다시 읽어서 저장
                    try {
                         const freshData = JSON.parse(readFileSync(DATA_PATH, 'utf-8'))
                         resolve(freshData)
                     } catch (e) {
                          console.error('❌ JSON 읽기 실패:', e)
                          reject(e)
                     }
               } else {
                    console.error('❌ Python 데이터 수집 실패:', errorOutput)
                    reject(new Error(`Python 데이터 수집 실패: ${errorOutput}`))
               }
          })
     })
}

/**
 * GET /api/dashboard - 대시보드 데이터 반환
 */
app.get('/api/dashboard', async (req, res) => {
    try {
         // 데이터 수집 실행
         const freshData = await runDataFetcher()
         res.json(freshData)
    } catch (error) {
        console.error('데이터 수집 실패, fallback 사용:', error)
         // fallback: 기존 파일 읽기
        try {
             const fallbackData = JSON.parse(readFileSync(DATA_PATH, 'utf-8'))
             res.json(fallbackData)
        } catch (e) {
             console.error('fallback 데이터 읽기 실패:', e)
             res.status(500).json({ error: '데이터를 불러올 수 없습니다' })
        }
   }
})

/**
 * GET /api/health - 헬스 체크
 */
app.get('/api/health', (req, res) => {
    res.json({
         status: 'ok',
         timestamp: new Date().toISOString(),
         dataPath: DATA_PATH,
     })
})

// 서버 시작
app.listen(PORT, () => {
    console.log(`📊 거시경제 대시보드 API 서버 시작`)
    console.log(`   포트: http://localhost:${PORT}`)
    console.log(`   Dashboard API: http://localhost:${PORT}/api/dashboard`)
    console.log(`   Health Check: http://localhost:${PORT}/api/health`)
    console.log(`   자동 갱신: 5분마다 Python 데이터 수집 실행`)

     // 초기 데이터 수집
     setTimeout(() => {
          runDataFetcher().catch(e => console.error('초기 데이터 수집 실패:', e))
     }, 1000)
})
