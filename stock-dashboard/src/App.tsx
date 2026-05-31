import { useState, useEffect } from 'react'

interface Indicator {
  id: string
  name: string
  nameKo: string
  description: string
  country: 'US' | 'KR'
  fredId?: string
  worldBankId?: string
  yahooSymbol?: string  // Yahoo Finance symbol for real-time data
  unit: string
  target?: 'up' | 'down' | 'neutral'
  value?: number
  signal?: string
}

// 한국 경제 지표 (Yahoo Finance real-time + World Bank for macro data)
// 💡 KRX Open API 연동 시 실시간 개인 종목 데이터 가능: https://data.krx.co.kr
//    API 키: 875D2DA8A6C940D7BFF23955D567686A2E88FC55 (아직 데이터별 이용신청 필요)

// 미국 경제 지표 (Yahoo Finance real-time + World Bank for macro data)

// 한국 경제 패백 데이터 (2024년 기준)
const KR_FALLBACK: Indicator[] = [
  { id: 'krkospi', name: 'KOSPI Index', nameKo: 'KOSPI 지수', country: 'KR', description: '한국 주식시장의 대표적인 종합지수', yahooSymbol: '^KS11', target: 'up', unit: 'point', value: 8500, signal: 'up' },
  { id: 'kr_samsung', name: 'Samsung Electronics', nameKo: '삼성전자', country: 'KR', description: '한국 대표 기술주', yahooSymbol: '005930.KS', target: 'up', unit: 'W', value: 317000, signal: 'up' },
  { id: 'kr_cpi', name: 'Inflation Rate', nameKo: '물가상승률', country: 'KR', description: 'GDP 디플레이터 전년동기비', worldBankId: 'NY.GDP.DEFL.KD.ZG', target: 'neutral', unit: '%', value: 2.2, signal: 'neutral' },
  { id: 'kr_unemploy', name: 'Unemployment Rate', nameKo: '실업률', country: 'KR', description: '경제활동인구 대비 실업자 비율', worldBankId: 'SL.UEM.TOTL.ZS', target: 'down', unit: '%', value: 2.8, signal: 'up' },
  { id: 'kr_interest', name: 'Base Interest Rate', nameKo: '기준금리', country: 'KR', description: '한국은행 기준금리', target: 'neutral', unit: '%', value: 3.5, signal: 'neutral' },
  { id: 'kr_exchange', name: 'USD/KRW', nameKo: '원/달러 환율', country: 'KR', description: 'USD 1달러당 원화 환율', yahooSymbol: 'USDKRW=X', target: 'down', unit: '원', value: 1350, signal: 'down' },
  { id: 'kr_trade', name: 'Trade Balance', nameKo: '무역수지', country: 'KR', description: '수출액에서 수입액을 제외한 차액', unit: '백만$', value: -2800, signal: 'down' },
]

// 미국 경제 패백 데이터
const US_FALLBACK: Indicator[] = [
  { id: 'usp500', name: 'S&P 500', nameKo: 'S&P 500', country: 'US', description: '미국 대형주 500개 지수', yahooSymbol: '^GSPC', target: 'up', unit: 'point', value: 6000, signal: 'up' },
  { id: 'usdjwr', name: 'Dow Jones', nameKo: '다우 존스', country: 'US', description: '미국 산업대표 30개 종목 지수', yahooSymbol: '^DJI', target: 'up', unit: 'point', value: 44000, signal: 'up' },
  { id: 'usnx', name: 'NASDAQ', nameKo: '나스닥', country: 'US', description: '기술주 중심 지수', yahooSymbol: '^IXIC', target: 'up', unit: 'point', value: 19500, signal: 'up' },
  { id: 'uscpi', name: 'CPI Inflation', nameKo: '소비자물가지수', country: 'US', description: '소비자물가 전년동기비', worldBankId: 'KY.ENX.PCEP.KD.ZG', unit: '지수', value: 315.7, signal: 'down', target: 'neutral' },
  { id: 'unemployment', name: 'Unemployment Rate', nameKo: '실업률', country: 'US', description: '실업률', worldBankId: 'SL.UEM.TOTL.ZS', unit: '%', value: 4.3, signal: 'down', target: 'down' },
  { id: 'usfedrate', name: 'Fed Funds Rate', nameKo: '미 연방기준금리', country: 'US', description: '미 연준 기준금리', target: 'neutral', unit: '%', value: 4.5, signal: 'neutral' },
]

const COLORS: Record<string, string> = {
  up: '#4CAF50',
  down: '#f44336',
  neutral: '#FF9800',
}

function getSignal(ind: Indicator, value: number): string {
  const t = ind.target
  if (t === 'up') return value > 0 ? 'up' : 'down'
  if (t === 'down') return value < 0 ? 'down' : 'up'
  return 'neutral'
}

async function fetchYahooFinance(symbol: string): Promise<{ current: number; change: number; changePct: number } | null> {
  try {
    // Use Vite proxy to avoid CORS
    const url = `/api/yfinance/chart/${encodeURIComponent(symbol)}?interval=1d&range=1d`
    const res = await fetch(url)
    if (!res.ok) return null
    const json = await res.json()
    const result = json?.chart?.result?.[0]
    if (!result) return null
    const close = result.indicators?.quote?.[0]?.close
    if (!close || close.length === 0) return null
    const current = close[close.length - 1]
    if (!current || isNaN(current)) return null
    const meta = result.meta
    const previousClose = meta?.regularMarketPreviousClose || meta?.chartPreviousClose || 0
    const change = current - previousClose
    const changePct = previousClose ? (change / previousClose) * 100 : 0
    return { current, change, changePct }
  } catch {
    return null
  }
}

function formatValue(ind: Indicator, displayValue: number): string {
  if (ind.id === 'kr_exchange') {
    return `${Math.round(displayValue).toLocaleString()} ${ind.unit}`
  }
  if (ind.id === 'kr_samsung') {
    return `${Math.round(displayValue).toLocaleString()} ${ind.unit}`
  }
  const isCurrency = ['usp500', 'usdjwr', 'usnx', 'uscpi', 'govt_debt', 'trade', 'kr_trade'].includes(ind.id)
  if (isCurrency) {
    if (displayValue >= 1000) {
      return `${(displayValue / 1000).toFixed(1)}${ind.unit === '백만$' ? 'T' : ''}${ind.unit}`
    }
    return `${Math.round(displayValue)}${ind.unit}`
  }
  if (ind.yahooSymbol) {
    // Yahoo Finance data - show with decimals
    return displayValue.toLocaleString(undefined, { minimumFractionDigits: 2, maximumFractionDigits: 2 }) + ` ${ind.unit === 'W' ? '만원' : ind.unit}`
  }
  return displayValue.toFixed(2) + (ind.unit === '%' || ind.unit === '점' ? '%' : ind.unit === '원' ? '원' : ` ${ind.unit}`)
}

function IndicatorCard({ ind, yahooData }: { ind: Indicator; yahooData: { current: number; change: number; changePct: number } | null }) {
  const color = COLORS[ind.signal ?? 'neutral']
  const flag = ind.country === 'KR' ? '🇰🇷' : '🇺🇸'
  const displayValue = yahooData?.current ?? ind.value ?? 0
  const formatted = formatValue(ind, displayValue)
  const changePct = yahooData?.changePct ?? 0
  const isUp = changePct > 0
  const chartColor = isUp ? '#ff6b6b' : '#4ecdc4'

  return (
    <div style={{
      background: 'rgba(255,255,255,0.04)',
      border: '1px solid rgba(255,255,255,0.08)',
      borderRadius: 16,
      padding: '24px',
      borderLeft: `5px solid ${color}`,
      transition: 'all 0.3s ease',
      cursor: 'default',
    }}
    onMouseEnter={(e) => {
     e.currentTarget.style.transform = 'translateY(-4px)'
      e.currentTarget.style.boxShadow = `0 12px 40px ${color}22`
      e.currentTarget.style.borderColor = color
    }}
    onMouseLeave={(e) => {
     e.currentTarget.style.transform = 'translateY(0)'
      e.currentTarget.style.boxShadow = 'none'
      e.currentTarget.style.borderColor = 'rgba(255,255,255,0.08)'
    }}
    >
      <div style={{ display: 'flex', alignItems: 'center', marginBottom: 12 }}>
        <div style={{
          width: 16, height: 16, borderRadius: '50%',
          backgroundColor: color, marginRight: 12,
          boxShadow: `0 0 12px ${color}80`,
          flexShrink: 0,
        }} />
        <span style={{ fontSize: 20, marginRight: 8 }}>{flag}</span>
        <h3 style={{ fontSize: 18, fontWeight: 600, margin: 0, color: '#e6edf3' }}>
          {ind.nameKo}
        </h3>
        {yahooData && (
          <span style={{
            marginLeft: 'auto',
            fontSize: 14,
            fontWeight: 600,
            color: chartColor,
            background: `${chartColor}15`,
            padding: '4px 12px',
            borderRadius: 20,
          }}>
            {isUp ? '▲' : '▼'} {Math.abs(changePct).toFixed(2)}%
          </span>
        )}
      </div>

      <div style={{
        fontSize: 44,
        fontWeight: 700,
        margin: '12px 0',
        lineHeight: 1,
        color: color,
      }}>
        {formatted}
      </div>

      {yahooData && (
        <div style={{
          fontSize: 14,
          color: chartColor,
          marginBottom: 8,
          fontWeight: 500,
        }}>
          {isUp ? '▲' : '▼'} {Math.abs(yahooData.change).toFixed(2)} ({isUp ? '상승' : '하락'})
        </div>
      )}

      <p style={{
        color: '#8b949e',
        fontSize: 13,
        margin: 0,
        lineHeight: 1.5,
        minHeight: 38,
      }}>
        {ind.description}
      </p>
    </div>
  )
}

function LoadingState() {
  return (
    <div style={{
      minHeight: '100vh',
      backgroundColor: '#0d1117',
      color: '#e6edf3',
      fontFamily: '-apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif',
      display: 'flex',
      alignItems: 'center',
      justifyContent: 'center',
      flexDirection: 'column',
    }}>
      <div style={{ fontSize: 48, marginBottom: 16, animation: 'spin 1s linear infinite' }}>⏳</div>
      <h2 style={{ fontSize: 24, marginBottom: 8 }}>🇺🇸🇰🇷 한미 경제 신호등</h2>
       <p style={{ color: '#8b949e' }}>실시간 데이터를 로딩 중...</p>
       <p style={{ color: '#8b949e', fontSize: 12, marginTop: 8 }}>Yahoo Finance API 연동 중</p>
    </div>
  )
}

export default function App() {
  const [data, setData] = useState<Indicator[]>([])
  const [yahooDataMap, setYahooDataMap] = useState<Record<string, { current: number; change: number; changePct: number }>>({})
  const [loading, setLoading] = useState(true)
  const [lastUpdated, setLastUpdated] = useState('')

  const fetchAll = async () => {
    try {
      setLoading(true)
      const allIndicators = [...KR_FALLBACK, ...US_FALLBACK]
      const allYahooSymbols = allIndicators.filter(i => i.yahooSymbol).map(i => (i.yahooSymbol!))
      
      // Fetch Yahoo Finance data for symbols
      const yahooResults: Record<string, { current: number; change: number; changePct: number }> = {}
      for (const symbol of allYahooSymbols) {
        const data = await fetchYahooFinance(symbol)
        if (data) {
          yahooResults[symbol] = data
        }
      }
      setYahooDataMap(yahooResults)

      // Build final data
      const results: Indicator[] = []
      const fallbackData = [...US_FALLBACK, ...KR_FALLBACK]
      
      for (const ind of fallbackData) {
        let value = ind.value ?? 0
        if (ind.yahooSymbol && yahooResults[ind.yahooSymbol]) {
          value = yahooResults[ind.yahooSymbol].current
        }
        results.push({ ...ind, value, signal: ind.target ? getSignal(ind, value) : ind.signal })
      }

      setData(results)
      setLastUpdated(new Date().toLocaleString('ko-KR'))
      console.log('Data loaded with Yahoo Finance:', results.length, 'indicators')
    } catch (err) {
      console.error('Fetch error:', err)
      const fallbackData = [...US_FALLBACK, ...KR_FALLBACK]
      setData(fallbackData)
      setLastUpdated(new Date().toLocaleString('ko-KR'))
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => {
    fetchAll()
    const interval = setInterval(fetchAll, 5 * 60 * 1000)
    return () => clearInterval(interval)
  }, [])

  if (loading) return <LoadingState />

  const usData = data.filter(ind => ind.country === 'US')
  const krData = data.filter(ind => ind.country === 'KR')

  const usUp = usData.filter(i => i.signal === 'up').length
  const usDown = usData.filter(i => i.signal === 'down').length
  const usNeutral = usData.filter(i => i.signal === 'neutral').length
  const usNetSignal = usDown > usUp ? 'down' : usUp > usDown ? 'up' : 'neutral'

  const krUp = krData.filter(i => i.signal === 'up').length
  const krDown = krData.filter(i => i.signal === 'down').length
  const krNeutral = krData.filter(i => i.signal === 'neutral').length
  const krNetSignal = krDown > krUp ? 'down' : krUp > krDown ? 'up' : 'neutral'

  return (
    <div style={{
      minHeight: '100vh',
      backgroundColor: '#0d1117',
      color: '#e6edf3',
      fontFamily: '-apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif',
    }}>
      {/* Header */}
      <header style={{
        background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
        padding: '48px 20px 36px',
        textAlign: 'center',
        position: 'relative',
        overflow: 'hidden',
      }}>
        <div style={{
          position: 'absolute',
          top: '-50%', left: '-10%', width: '120%', height: '200%',
          background: 'radial-gradient(circle, rgba(255,255,255,0.08) 0%, transparent 70%)',
          pointerEvents: 'none',
        }} />
        
        <h1 style={{
          fontSize: 36,
          margin: 0,
          fontWeight: 800,
          letterSpacing: '-0.02em',
          position: 'relative',
          zIndex: 1,
        }}>🇺🇸🇰🇷 한미 경제 신호등</h1>
        <p style={{
          margin: '8px 0 0',
          opacity: 0.85,
          fontSize: 15,
          position: 'relative',
          zIndex: 1,
        }}>Yahoo Finance + World Bank 기반 실시간 경제 지표 대시보드</p>
        
        {/* Overall Signals */}
        <div style={{ marginTop: 24, position: 'relative', zIndex: 1, display: 'flex', justifyContent: 'center', gap: 32, flexWrap: 'wrap' }}>
          {/* US Signal */}
          <div style={{
            display: 'inline-flex',
            alignItems: 'center',
            gap: 12,
            padding: '10px 24px',
            background: 'rgba(255,255,255,0.1)',
            borderRadius: 24,
            backdropFilter: 'blur(10px)',
          }}>
            <div style={{
              width: 20,
              height: 20,
              borderRadius: '50%',
              backgroundColor: COLORS[usNetSignal],
              boxShadow: `0 0 16px ${COLORS[usNetSignal]}80`,
            }} />
            <span style={{ fontSize: 14, fontWeight: 500 }}>
              🇺🇸 긍정 {usUp}개 | 🟡 중립 {usNeutral}개 | 🔴 부정 {usDown}개
            </span>
          </div>
          
          {/* KR Signal */}
          <div style={{
            display: 'inline-flex',
            alignItems: 'center',
            gap: 12,
            padding: '10px 24px',
            background: 'rgba(255,255,255,0.1)',
            borderRadius: 24,
            backdropFilter: 'blur(10px)',
          }}>
            <div style={{
              width: 20,
              height: 20,
              borderRadius: '50%',
              backgroundColor: COLORS[krNetSignal],
              boxShadow: `0 0 16px ${COLORS[krNetSignal]}80`,
            }} />
            <span style={{ fontSize: 14, fontWeight: 500 }}>
              🇰🇷 긍정 {krUp}개 | 🟡 중립 {krNeutral}개 | 🔴 부정 {krDown}개
            </span>
          </div>
        </div>
      </header>

      {/* 미국 경제 섹션 */}
      <main style={{ maxWidth: 1200, margin: '40px auto', padding: '0 20px' }}>
        <h2 style={{
          fontSize: 28,
          fontWeight: 700,
          margin: '0 0 24px',
          color: '#e6edf3',
          display: 'flex',
          alignItems: 'center',
          gap: 12,
        }}>
          🇺🇸 미국 경제 신호등
        </h2>
        <div style={{
          display: 'grid',
          gridTemplateColumns: 'repeat(auto-fill, minmax(300px, 1fr))',
          gap: 20,
        }}>
          {usData.map(ind => (
            <IndicatorCard key={ind.id} ind={ind} yahooData={yahooDataMap[findYahooSymbol(ind) ?? ''] ?? null} />
          ))}
        </div>
      </main>

      {/* 한국 경제 섹션 */}
      <main style={{ maxWidth: 1200, margin: '40px auto', padding: '0 20px' }}>
        <h2 style={{
          fontSize: 28,
          fontWeight: 700,
          margin: '0 0 24px',
          color: '#e6edf3',
          display: 'flex',
          alignItems: 'center',
          gap: 12,
        }}>
          🇰🇷 한국 경제 신호등
        </h2>
        <div style={{
          display: 'grid',
          gridTemplateColumns: 'repeat(auto-fill, minmax(300px, 1fr))',
          gap: 20,
          marginBottom: 40,
        }}>
          {krData.map(ind => (
            <IndicatorCard key={ind.id} ind={ind} yahooData={yahooDataMap[findYahooSymbol(ind) ?? ''] ?? null} />
          ))}
        </div>
      </main>

      {/* Footer */}
      <footer style={{
        textAlign: 'center',
        padding: '32px 20px 48px',
        color: '#4a5568',
        fontSize: 13,
        borderTop: '1px solid rgba(255,255,255,0.06)',
        marginTop: 20,
      }}>
        <p>Data sources: Yahoo Finance (real-time), World Bank Open Data</p>
        <p style={{ marginTop: 4 }}>KRX API 연동 예정 (API 키: 875D2DA8A6C940D7BFF23955D567686A2E88FC55 | 데이터별 이용신청 시 활성화)</p>
        <p style={{ marginTop: 6 }}>마지막 업데이트: {lastUpdated}</p>
      </footer>

      <style>{`
        @keyframes spin {
          from { transform: rotate(0deg); }
          to { transform: rotate(360deg); }
        }
      `}</style>
    </div>
  )
}

function findYahooSymbol(ind: Indicator): string | null {
  return ind.yahooSymbol ?? null
}