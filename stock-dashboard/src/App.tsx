import { useState, useEffect } from 'react'

const COLORS = {
  up: '#3b82f6',
  down: '#ef4444',
  neutral: '#eab308',
  bg: '#121214',
  card: '#1e1e24',
  text: '#e5e7e3',
  textSecondary: '#8b949a',
  border: 'rgba(255,255,255,0.08)',
}

type Indicator = {
  id: string
  name: string
  value: number
  signal: 'up' | 'down' | 'neutral'
  country: string
  type: string
  yahooSymbol: string | null
  unit: string
  description: string
  date?: string
  source?: string
  yahoo?: ApiIndicator | null
}

interface ApiIndicator {
  symbol: string
  value: number
  change: number
  changePct: number
  signal: string
  nameKo: string
  country: string
  type: string
}

function getSignal(ind: Indicator, current: number, changePct: number): 'up' | 'down' | 'neutral' {
  if (ind.type === 'index') {
    if (changePct > 0.1) return 'up'
    if (changePct < -0.1) return 'down'
    return 'neutral'
  }
  if (ind.type === 'unemployment') {
    if (changePct < 0) return 'up'
    if (Math.abs(changePct) <= 0.5) return 'neutral'
    return 'down'
  }
  if (ind.type === 'inflation') {
    if (current < 2.5) return 'up'
    if (current <= 3.5) return 'neutral'
    return 'down'
  }
  if (ind.type === 'interest_rate') {
    if (changePct < 0) return 'up'
    if (Math.abs(changePct) <= 0.5) return 'neutral'
    return 'down'
  }
  if (ind.type === 'money_stock') {
    if (changePct > 0) return 'up'
    if (changePct < 0) return 'down'
    return 'neutral'
  }
  if (ind.type === 'us_trade') {
    if (changePct > 0) return 'up' // 적자축소/흑자확대 = 긍정
    return 'down'
  }
  return 'neutral'
}

const US_INDICATORS: Indicator[] = [
  { id: 'usp500', name: 'S&P 500 지수', value: 7580.06, signal: 'up', country: 'US', type: 'index', yahooSymbol: '^GSPC', unit: 'pt', description: '미국 대형주 500개 종목을 담은 종합 지수 (시장 지배력 70% 대)' },
  { id: 'usdjwr', name: '다우 존스 지수', value: 51032.46, signal: 'up', country: 'US', type: 'index', yahooSymbol: '^DJI', unit: 'pt', description: '도이체은행 주관 미국 우수 대기업 30개 종목 중심 지수' },
  { id: 'usnx', name: '나스닥 종합지수', value: 26972.61, signal: 'up', country: 'US', type: 'index', yahooSymbol: '^IXIC', unit: 'pt', description: '비즈니스 기업 중심의 종합 지수, 정보기술 기업 위주' },
  { id: 'uscpi', name: '소비자물가지수', value: 315.7, signal: 'neutral', country: 'US', type: 'inflation', yahooSymbol: null, unit: '지수', description: '전반적 물가 수준을 나타내는 지표, 연준의 인플레이션 타겟 2% 상회' },
  { id: 'unemployment', name: '실업률', value: 4.3, signal: 'up', country: 'US', type: 'unemployment', yahooSymbol: null, unit: '%', description: '고용시장 상황, 4%대 초중반으로 완만한 고용 유지' },
   { id: 'usfedrate', name: '미 연방기준금리', value: 4.5, signal: 'neutral', country: 'US', type: 'interest_rate', yahooSymbol: null, unit: '%', description: '미 연준(Fed) 기준금리, 고금리 장기화(3~4%) 추세' },
   { id: 'us_m2', name: '미국 M2 통화량', value: 20.9, signal: 'up', country: 'US', type: 'money_stock', yahooSymbol: null, unit: '조$', description: '미국 M2 통화 공급량, M1+저축예금+소액시간예금+.MMF (FRED: M2SL)' },
   { id: 'us_trade_bal', name: '미국 무역수지', value: -750, signal: 'down', country: 'US', type: 'us_trade', yahooSymbol: null, unit: 'B$', description: '미국 월간 무역수지 (수출−수입), 2025.06 기준 약 750B$ 적자 (FRED: BOPGSTB)' },
]

const KR_INDICATORS: Indicator[] = [
  { id: 'krkospi', name: 'KOSPI 지수', value: 8476.15, signal: 'up', country: 'KR', type: 'index', yahooSymbol: '^KS11', unit: 'pt', description: '한국증권거래소 시장가치Weight 종합지수, 300개 종목' },
  { id: 'krkq11', name: 'KOSDAQ 지수', value: 1074.8, signal: 'down', country: 'KR', type: 'index', yahooSymbol: '^KQ11', unit: 'pt', description: '중소기업·신산업 중심의 종합지수, 변동성 높음' },
  { id: 'krks200', name: 'KOSPI 200 지수', value: 1342.82, signal: 'up', country: 'KR', type: 'index', yahooSymbol: '^KS200', unit: 'pt', description: '대장주 200개로 구성된 지수로 선물·옵션 선물지수 기반 지수' },
  { id: 'kr_cpi', name: '물가상승률', value: 2.2, signal: 'neutral', country: 'KR', type: 'inflation', yahooSymbol: null, unit: '%', description: '전년동월대비 물가상승률, 2%대 중반으로 안정세 유지' },
  { id: 'kr_unemploy', name: '실업률', value: 2.8, signal: 'up', country: 'KR', type: 'unemployment', yahooSymbol: null, unit: '%', description: '15세이상 경제활동인구 중 실업체 비율, 2.8%로 매우 낮음' },
  { id: 'kr_interest', name: '기준금리', value: 3.5, signal: 'neutral', country: 'KR', type: 'interest_rate', yahooSymbol: null, unit: '%', description: '한국은행 기준금리, 3%대 중반으로 고금리 기조 유지' },
  { id: 'kr_exchange', name: '원/달러 환율', value: 1507.13, signal: 'neutral', country: 'KR', type: 'exchange_rate', yahooSymbol: 'USDKRW=X', unit: '원', description: '1달러당 원화 환율, 1,500원대 후반으로 원화 약세' },
    { id: 'kr_trade', name: '무역수지', value: -2800, signal: 'down', country: 'KR', type: 'trade_balance', yahooSymbol: null, unit: '백만$ ', description: '수출−수입 격차, 2,800억 달러 무역적자 발생' },
    { id: 'kr_m2', name: '한국 M2 통화량', value: 4303, signal: 'up', country: 'KR', type: 'money_stock', yahooSymbol: null, unit: '조원', description: '한국 M2 통화 공급량, 금융기관 통화예금 합계 (IMF/한국은행, MYAGM2KRM189S)' },
]

function getDisplayValue(ind: Indicator, yahoo: ApiIndicator | null): string {
  const displayValue = yahoo ? yahoo.value : ind.value
  if (ind.id === 'kr_exchange') return `${Math.round(displayValue).toLocaleString()}${ind.unit}`
  if (ind.type === 'index') return `${Math.round(displayValue).toLocaleString()}${ind.unit}`
  if (ind.unit === '%') return `${displayValue.toFixed(2)}${ind.unit}`
  if (ind.unit === '지수' || ind.unit === 'pt') return `${displayValue.toFixed(2)}${ind.unit}`
  if (ind.unit === '조$') return `$${displayValue.toFixed(2)}조`
  if (ind.unit === '조원') return `₩${displayValue.toFixed(2)}조`
  if (ind.unit === 'B$') return `$${displayValue.toFixed(1)}B`
  return `${displayValue} ${ind.unit}`
}

function getChangeText(_yahoo: ApiIndicator | null, changePct: number): string {
  const isUp = changePct > 0.001
  const isNeutral = Math.abs(changePct) <= 0.001
  if (changePct === 0) return '0.00%'
  if (isUp) return `▲ +${changePct.toFixed(2)}%`
  if (!isNeutral) return `▼ ${changePct.toFixed(2)}%`
  return `${changePct.toFixed(2)}%`
}

function IndicatorCard({ ind, yahoo }: { ind: Indicator; yahoo: ApiIndicator | null }) {
  const color = COLORS[ind.signal || 'neutral']
  const flag = ind.country === 'KR' ? '🇰🇷' : '🇺🇸'
  const changePct = yahoo ? yahoo.changePct : 0
  const formattedValue = getDisplayValue(ind, yahoo)
  const changeText = getChangeText(yahoo, changePct)

  return (
    <div style={{
      backgroundColor: COLORS.card,
      borderRadius: 16,
      padding: '24px 20px',
      border: `1px solid ${COLORS.border}`,
      boxShadow: '0 4px 12px rgba(0,0,0,0.4)',
      transition: 'transform 0.2s, box-shadow 0.2s',
    }}
    onMouseEnter={(e) => {
      e.currentTarget.style.transform = 'translateY(-2px)'
      e.currentTarget.style.boxShadow = '0 6px 24px rgba(0,0,0,0.6)'
    }}
    onMouseLeave={(e) => {
      e.currentTarget.style.transform = 'translateY(0)'
      e.currentTarget.style.boxShadow = '0 4px 12px rgba(0,0,0,0.4)'
    }}>
      <div style={{
        display: 'flex',
        justifyContent: 'space-between',
        alignItems: 'center',
        marginBottom: 16,
        paddingBottom: 12,
        borderBottom: `1px solid ${COLORS.border}`,
      }}>
        <div style={{
          display: 'flex',
          alignItems: 'center',
          gap: 12,
        }}>
          <div style={{
            width: 14,
            height: 14,
            borderRadius: '50%',
            backgroundColor: color,
            boxShadow: `${color}5e 0px 0px 12px`,
          }} />
          <span style={{ fontSize: 24 }}>{flag}</span>
          <span style={{
            fontSize: 14,
            color: COLORS.textSecondary,
          }}>{ind.name}</span>
        </div>
        <span style={{
          fontSize: 16,
          fontWeight: 600,
          color: changePct > 0.001 ? COLORS.up : COLORS.down,
        }}>{changeText}</span>
      </div>

      <div style={{
        fontSize: 36,
        fontWeight: 800,
        marginBottom: 12,
        fontFamily: 'monospace',
        color: COLORS.text,
      }}>{formattedValue}</div>

      <div style={{
        display: 'flex',
        justifyContent: 'space-between',
        alignItems: 'flex-start',
      }}>
        <span style={{
          fontSize: 13,
          fontWeight: 500,
          color: changePct > 0.001 ? COLORS.up : COLORS.down,
        }}>포인트: {yahoo ? (yahoo.change > 0 ? '+' : '') + yahoo.change.toFixed(2) : changePct.toFixed(2)}</span>

        <p style={{
          fontSize: 12,
          color: COLORS.textSecondary,
          maxWidth: '50%',
          margin: 0,
          lineHeight: 1.4,
        }}>{ind.description}</p>
      </div>
    </div>
  )
}

function SummaryBar({ up: upCount, neutral: neutralCount, down: downCount }: {
  up: number
  neutral: number
  down: number
}) {
  return (
    <div style={{
      display: 'inline-flex',
      alignItems: 'center',
      gap: 12,
      padding: '12px 24px',
      background: 'rgba(255,255,255,0.05)',
      border: `1px solid ${COLORS.border}`,
      borderRadius: 24,
    }}>
      <div style={{
        width: 14,
        height: 14,
        borderRadius: '50%',
        backgroundColor: COLORS.up,
        boxShadow: `${COLORS.up}5e 0px 0px 12px`,
      }} />
      <span style={{ fontSize: 13, fontWeight: 500, color: COLORS.up }}>긍정 {upCount}</span>
      <div style={{
        width: 10,
        height: 10,
        borderRadius: '50%',
        backgroundColor: COLORS.neutral,
        boxShadow: `${COLORS.neutral}5e 0px 0px 8px`,
      }} />
      <span style={{ fontSize: 13, fontWeight: 500, color: COLORS.neutral }}>중립 {neutralCount}</span>
      <div style={{
        width: 10,
        height: 10,
        borderRadius: '50%',
        backgroundColor: COLORS.down,
        boxShadow: `${COLORS.down}5e 0px 0px 8px`,
      }} />
      <span style={{ fontSize: 13, fontWeight: 500, color: COLORS.down }}>부정 {downCount}</span>
    </div>
  )
}

function App() {
  const [loading, setLoading] = useState(true)
  const [data, setData] = useState<Indicator[]>([])
  const [apiData, _setApiData] = useState<Record<string, ApiIndicator>>({})
  const [lastUpdated, setLastUpdated] = useState('')

  const fetchAll = async () => {
    console.log('🔄 fetchAll() started')
    try {
      setLoading(true)
      console.log('📡 Fetching from localhost:3001...')
      const res = await fetch('http://localhost:3001/api/dashboard', {
        signal: AbortSignal.timeout(15000)
        })
      console.log('📡 Response received:', res.ok, res.status)
      const apiDataResponse = res.ok ? await res.json() : {}
      console.log('📦 API data loaded:', Object.keys(apiDataResponse).length, 'indicators')

      const allData = [
          ...KR_INDICATORS.map(ind => {
          const api = apiDataResponse[ind.id]
          const realValue = api ? api.value : ind.value
          const realSignal = api
              ? getSignal(ind, api.value, api.changePct)
              : ind.signal
          return { ...ind, value: realValue, signal: realSignal, date: api?.date || ind.date, source: api?.source || '예상', yahoo: api || null }
          }),
          ...US_INDICATORS.map(ind => {
          const api = apiDataResponse[ind.id]
          const realValue = api ? api.value : ind.value
          const realSignal = api
              ? getSignal(ind, api.value, api.changePct)
              : ind.signal
          return { ...ind, value: realValue, signal: realSignal, date: api?.date || ind.date, source: api?.source || '예상', yahoo: api || null }
          }),
        ]

      setData(allData)
      setLastUpdated(new Date().toLocaleString('ko-KR'))
      console.log('✅ Data loaded:', allData.length, 'indicators')
      } catch (err) {
      console.error('❌ Fetch error:', err)
      setData([...KR_INDICATORS, ...US_INDICATORS])
      setLastUpdated(new Date().toLocaleString('ko-KR'))
     } finally {
      setLoading(false)
      console.log('🔄 loading -> false')
     }
  }

  useEffect(() => {
    fetchAll()
    const interval = setInterval(fetchAll, 5 * 60 * 1000)
    return () => clearInterval(interval)
  }, [])

  if (loading) {
    return (
      <div style={{
        minHeight: '100vh',
        backgroundColor: COLORS.bg,
        color: COLORS.text,
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'center',
        flexDirection: 'column',
      }}>
        <div style={{ fontSize: 48, marginBottom: 16, animation: 'spin 1s linear infinite' }}>⏳</div>
        <h2>🇺🇸🇰🇷 한미 경제 신호등 로딩 중...</h2>
        <p style={{ color: COLORS.textSecondary }}>실시간 데이터를 가져오는 중입니다</p>
      </div>
    )
  }

  const usData = data.filter(i => i.country === 'US')
  const krData = data.filter(i => i.country === 'KR')

  const calcSummary = (items: Indicator[]) => ({
    up: items.filter(i => i.signal === 'up').length,
    neutral: items.filter(i => i.signal === 'neutral').length,
    down: items.filter(i => i.signal === 'down').length,
  })

  const usSummary = calcSummary(usData)
  const krSummary = calcSummary(krData)

  return (
    <div style={{
      minHeight: '100vh',
      backgroundColor: COLORS.bg,
      color: COLORS.text,
      fontFamily: '-apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif',
    }}>
      <header style={{
        background: 'linear-gradient(135deg, #1a1a2e 0%, #16213e 50%, #0f3460 100%)',
        padding: '40px 20px',
        textAlign: 'center',
        borderBottom: `1px solid ${COLORS.border}`,
      }}>
        <h1 style={{ fontSize: 32, margin: 0, fontWeight: 800, letterSpacing: '-0.02em' }}>
          🇺🇸🇰🇷 한·미 경제 신호등
        </h1>
        <p style={{ margin: '8px 0px 24px', color: COLORS.textSecondary, fontSize: 14 }}>
          Yahoo Finance + 세계은행 기반 실시간 경제 지표 대시보드
        </p>
        <div style={{
          display: 'flex',
          justifyContent: 'center',
          gap: 32,
          flexWrap: 'wrap',
        }}>
          <SummaryBar {...usSummary} />
          <SummaryBar {...krSummary} />
        </div>
      </header>

      <main style={{
        maxWidth: 1400,
        margin: '0 auto',
        padding: '32px 20px',
        display: 'grid',
        gridTemplateColumns: '1fr 1fr',
        gap: 32,
      }}>
        <section>
          <div style={{
            display: 'flex',
            alignItems: 'center',
            gap: 12,
            marginBottom: 24,
            paddingBottom: 16,
            borderBottom: `2px solid ${COLORS.up}30`,
          }}>
            <span style={{ fontSize: 32 }}>🇺🇸</span>
            <h2 style={{ fontSize: 24, fontWeight: 700, margin: 0 }}>
              미국 경제 신호등
            </h2>
          </div>
          <div style={{
            display: 'grid',
            gridTemplateColumns: 'repeat(auto-fill, minmax(320px, 1fr))',
            gap: 20,
          }}>
             {usData.map(ind => (
                <IndicatorCard
                key={ind.id}
                ind={ind}
                yahoo={apiData[ind.id] || null}
                />
              ))}
          </div>
        </section>

        <section>
          <div style={{
            display: 'flex',
            alignItems: 'center',
            gap: 12,
            marginBottom: 24,
            paddingBottom: 16,
            borderBottom: `2px solid ${COLORS.up}30`,
          }}>
            <span style={{ fontSize: 32 }}>🇰🇷</span>
            <h2 style={{ fontSize: 24, fontWeight: 700, margin: 0 }}>
              한국 경제 신호등
            </h2>
          </div>
          <div style={{
            display: 'grid',
            gridTemplateColumns: 'repeat(auto-fill, minmax(320px, 1fr))',
            gap: 20,
          }}>
              {krData.map(ind => (
                 <IndicatorCard
                key={ind.id}
                ind={ind}
                yahoo={apiData[ind.id] || null}
                 />
               ))}
          </div>
        </section>
      </main>

      <footer style={{
        textAlign: 'center',
        padding: '32px 20px 24px',
        borderTop: `1px solid ${COLORS.border}`,
        color: COLORS.textSecondary,
        fontSize: 13,
        lineHeight: 1.6,
      }}>
        <p>데이터 출처: Yahoo Finance (실시간), 세계은행 (거시경제)</p>
        <p>마지막 업데이트: {lastUpdated}</p>
      </footer>
    </div>
  )
}

export default App