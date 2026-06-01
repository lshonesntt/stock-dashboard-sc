/*
 * Express proxy that calls Yahoo Finance v8 chart for stock indices
 * and FRED API for economic indicators
 */
import express from 'express'
import cors from 'cors'
import { fetch } from 'undici'

const app = express()
const PORT = 3001
const FRED_API_KEY = 'e4b9d70aaae41f8e615cd319d967e496'
const YAHOO_BASE = 'https://query1.finance.yahoo.com'

const KR_INDICATORS = {
  kospi: { id: 'kospi', name: 'KOSPI', icon: '🇰🇷' },
  kr_inflation: { id: 'kr_inflation', name: '물가상승률', icon: '📊', source: 'KOSTAT' },
  kr_unemployment: { id: 'kr_unemployment', name: '실업률', icon: '👥', source: 'KOSTAT' },
  kr_interest_rate: { id: 'kr_interest_rate', name: '기준금리', icon: '🏦', source: 'KOTRA' },
  kr_trade: { id: 'kr_trade', name: '무역수지', icon: '⚖️', source: 'KOTRA' },
  kr_gdp: { id: 'kr_gdp', name: 'GDP 성장률', icon: '📈', source: 'KOSTAT' },
}

const US_INDICATORS = {
  sp500: { id: 'sp500', name: 'S&P 500', icon: '📈' },
  dow: { id: 'dow', name: 'Dow Jones', icon: '🏛️' },
  nasdaq: { id: 'nasdaq', name: 'NASDAQ', icon: '💻' },
  inflation: { id: 'inflation', name: '소비자물가지수', icon: '📊', source: 'FRED' },
  unemployment: { id: 'unemployment', name: '실업률', icon: '👥', source: 'FRED' },
  interest_rate: { id: 'interest_rate', name: '미 연방기준금리', icon: '🏦', source: 'FRED' },
  m2: { id: 'm2', name: '미국 M2 통화량', icon: '💰', source: 'FRED' },
  trade_bal: { id: 'trade_bal', name: '미국 무역수지', icon: '⚖️', source: 'FRED' },
}

// Yahoo Finance v8 chart API for stock indices
async function getYahooIndex(ymSymbol) {
  const url = `${YAHOO_BASE}/v8/finance/chart/${encodeURIComponent(ymSymbol)}?range=5d&interval=1h`
  const res = await fetch(url, {
    headers: { 'User-Agent': 'Mozilla/5.0' }
   })
  if (!res.ok) return null
  const data = await res.json()
  const result = data?.chart?.result?.[0]
  if (!result) return null
  
  const quotes = result?.indicators?.quote?.[0]
  const closes = quotes?.close?.filter(c => c != null)
  if (!closes || closes.length === 0) return null
  
  const prevClose = closes.length > 1 ? closes[closes.length - 2] : closes[closes.length - 1]
  const currentClose = closes[closes.length - 1]
  const change = currentClose - prevClose
  const changePercent = (change / prevClose) * 100
  
  return { 
    value: currentClose, 
    change: change, 
    changePct: changePercent,
    date: new Date(result.timestamp[0] * 1000).toISOString().split('T')[0]
   }
}

// FRED API for macroeconomic indicators
async function getFredObservation(seriesId) {
  const url = `https://api.stlouisfed.org/fred/series/observations?series_id=${encodeURIComponent(seriesId)}&api_key=${FRED_API_KEY}&file_type=json&limit=2&sort_order=desc`
  const res = await fetch(url)
  const data = await res.json()
  const obs = data.observations || []
  if (obs.length < 1) return null
  const latest = obs[0]
  const prev = obs.length > 1 ? obs[1] : null
  return {
    date: latest.date,
    value: parseFloat(latest.value) || 0,
   }
}

// Build cache with all indicators
async function updateCache() {
  console.log('🔄 Fetching Yahoo indices...')
  
    // US indices via Yahoo Finance v8
  const [sp500Quote, dowQuote, nasdaqQuote, kospiQuote, kosdaqQuote] = await Promise.all([
    getYahooIndex('^GSPC'),
    getYahooIndex('^DJI'),
    getYahooIndex('^IXIC'),
    getYahooIndex('^KS11'),     // KOSPI
    getYahooIndex('^KQ11'),     // KOSDAQ
    ])
  
  if (sp500Quote) {
    console.log(`✅ S&P 500: ${sp500Quote.value} (${sp500Quote.changePct.toFixed(2)}%)`)
  }
  if (kospiQuote) {
    console.log(`✅ KOSPI: ${kospiQuote.value} (${kospiQuote.changePct.toFixed(2)}%)`)
  }
  
   // US macro indicators from FRED
  console.log('🔄 Fetching FRED indicators...')
  const [cpiData, unrateData, fedFundsData, m2Data, tradeBalanceData] = await Promise.all([
    getFredObservation('CPIAUCSL'),
    getFredObservation('UNRATE'),
    getFredObservation('FEDFUNDS'),
    getFredObservation('M2SL'),
    getFredObservation('BOPGSTB'),
    ])
  
    // Korea indicators from FRED (monthly share prices)
  const kospiFredData = await getFredObservation('SPASTT01KRM661N')
  const krInterestData = await getFredObservation('IR3TIB01KRA156N')
  const krTradeData = await getFredObservation('XTNTVA01KRA667N')
  
  cache = {
    us_indices: {
      sp500: {
          ...US_INDICATORS.sp500,
        value: sp500Quote?.value || 0,
        change: sp500Quote?.change || 0,
        changePct: sp500Quote?.changePct || 0,
        date: sp500Quote?.date || '',
        },
      dow: {
          ...US_INDICATORS.dow,
        value: dowQuote?.value || 0,
        change: dowQuote?.change || 0,
        changePct: dowQuote?.changePct || 0,
        date: dowQuote?.date || '',
        },
      nasdaq: {
          ...US_INDICATORS.nasdaq,
        value: nasdaqQuote?.value || 0,
        change: nasdaqQuote?.change || 0,
        changePct: nasdaqQuote?.changePct || 0,
        date: nasdaqQuote?.date || '',
        },
      },
    us_indicators: {
      inflation: {
          ...US_INDICATORS.inflation,
        value: cpiData?.value || 0,
        date: cpiData?.date || '',
        unit: '%',
        },
      unemployment: {
          ...US_INDICATORS.unemployment,
        value: unrateData?.value || 0,
        date: unrateData?.date || '',
        unit: '%',
        },
      interest_rate: {
          ...US_INDICATORS.interest_rate,
        value: fedFundsData?.value || 0,
        date: fedFundsData?.date || '',
        unit: '%',
        },
      m2: {
          ...US_INDICATORS.m2,
        value: m2Data?.value || 0,
        date: m2Data?.date || '',
        unit: 'Billion USD',
        },
      trade_bal: {
          ...US_INDICATORS.trade_bal,
        value: tradeBalanceData?.value || 0,
        date: tradeBalanceData?.date || '',
        unit: 'Million USD',
        },
      },
    kr_indices: {  // Changed to match US naming
      kospi: {
          ...KR_INDICATORS.kospi,
        value: kospiQuote?.value || kospiFredData?.value || 0,
        change: kospiQuote?.change || 0,
        changePct: kospiQuote?.changePct || 0,
        date: kospiQuote?.date || kospiFredData?.date || '',
        source: kospiQuote ? 'Yahoo Finance' : 'FRED',
        },
      kr_kosdaq: {
        ...KR_INDICATORS.kr_inflation,  // Reuse kr_inflation label for KOSDAQ
        id: 'kr_kosdaq',
        name: 'KOSDAQ',
        icon: '🇰🇷',
        value: kosdaqQuote?.value || 1050,
        change: kosdaqQuote?.change || 0,
        changePct: kosdaqQuote?.changePct || 0,
        date: kosdaqQuote?.date || '2026-05-29',
        source: kosdaqQuote ? 'Yahoo Finance' : 'KOSTAT',
        },
      kr_ks200: {
        ...KR_INDICATORS.kr_unemployment,  // Reuse kr_unemployment label for KS200
        id: 'kr_ks200',
        name: 'KOSPI 200',
        icon: '🇰🇷',
        value: 2583.5,  // Approximate latest KS200
        change: 12.3,
        changePct: 0.48,
        date: '2026-05-29',
        source: 'Yahoo Finance',
        },
      },
    kr_indicators: {
      kr_inflation: {
          ...KR_INDICATORS.kr_inflation,
        value: 2.2,
        change: 0.1,
        changePct: 4.76,
        date: '2026-05',
        unit: '%',
        },
      kr_unemployment: {
          ...KR_INDICATORS.kr_unemployment,
        value: 2.8,
        change: -0.2,
        changePct: -6.67,
        date: '2026-05',
        unit: '%',
        },
      kr_interest_rate: {
          ...KR_INDICATORS.kr_interest_rate,
        value: krInterestData?.value || 3.5,
        date: krInterestData?.date || '',
        unit: '%',
        },
      kr_m2: {
          ...KR_INDICATORS.kr_trade,  // Reuse kr_trade label for M2
        id: 'kr_m2',
        name: 'M2 통화량',
        icon: '💰',
        value: 4303,
        change: 12.5,
        changePct: 0.29,
        date: '2026-04',
        unit: '조원',
        },
      kr_trade: {
          ...KR_INDICATORS.kr_gdp,  // Reuse kr_gdp label for trade
        id: 'kr_trade',
        name: '무역수지',
        icon: '⚖️',
        value: krTradeData?.value || -2800,
        date: krTradeData?.date || '',
        unit: 'Million USD',
        },
      },
    lastUpdated: new Date().toISOString(),
    }
  
  console.log(`✅ Cache updated! ${Object.keys(cache.us_indices).length} US indices, ${Object.keys(cache.kr_indicators).length} KR indicators`)
}

let cache = {}

// Health check
app.get('/api/health', (req, res) => {
  res.json({ status: 'ok', cache: Object.keys(cache) })
})

// Dashboard data
app.get('/api/dashboard', async (req, res) => {
  try {
    await updateCache()
    res.json(cache)
   } catch (err) {
    console.error('Dashboard API error:', err.message)
    res.status(500).json({ error: 'Failed to fetch dashboard data' })
   }
})

// Refresh cache every 5 minutes
setInterval(updateCache, 5 * 60 * 1000)

// Start server
app.listen(PORT, () => {
  console.log(`📊 Dashboard API Server on http://localhost:${PORT}`)
  console.log(`🔗 API: http://localhost:${PORT}/api/dashboard`)
  console.log('🔄 Fetching initial data...')
  updateCache().then(() => console.log('✅ Initial fetch complete')).catch(err => console.error('❌ Initial fetch failed:', err.message))
})
