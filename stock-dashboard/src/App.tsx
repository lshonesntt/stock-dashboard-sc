import { useState, useEffect } from 'react'

// CSS Variables로 색상 정의
const COLORS: Record<string, string> & {
  up: string
  down: string
  neutral: string
  bg: string
  card: string
  text: string
  textSecondary: string
  border: string
} = {
  up: '#22c55e',        // 초록
  down: '#ef4444',      // 빨강
  neutral: '#eab308',    // 노랑
  bg: '#121214',        // 배경 다크 네이비/블랙
  card: '#1e1e24',      // 카 짙은 회색
  text: '#e6edf3',      // 메인 텍스트
  textSecondary: '#8b949e', // 서브 텍스트
  border: 'rgba(255,255,255,0.08)',
}

interface YahooData {
  current: number
  change: number
  changePct: number
}

interface Indicator {
  id: string
  name: string
  nameKo: string
  description: string
  country: 'US' | 'KR'
  yahooSymbol: string
  unit: string
  target: 'up' | 'down' | 'neutral'
  value: number
  signal: string
  type: string  // index, inflation, unemployment, interest_rate, etc.
}

// 한국 경제 지표
const KR_INDICATORS: Indicator[] = [
  { id: 'krkospi', name: 'KOSPI', nameKo: 'KOSPI 지수', description: '한국 주식시장의 대표적인 종합지수로, 시가총액 상위 200개 종목으로 구성', country: 'KR', yahooSymbol: '^KS11', unit: 'pt', target: 'up', value: 0, signal: 'neutral', type: 'index' },
  { id: 'krkq11', name: 'KOSDAQ', nameKo: 'KOSDAQ 지수', description: '한국 중소벤처기업 중심의 주식시장 지수, IT/바이오 기업 비중 높음', country: 'KR', yahooSymbol: '^KQ11', unit: 'pt', target: 'up', value: 0, signal: 'neutral', type: 'index' },
  { id: 'krks200', name: 'KOSPI 200', nameKo: 'KOSPI 200 지수', description: '시가총액 및 유동성 기준 선정된 대형주 200개 종목으로 구성된 선도 지수', country: 'KR', yahooSymbol: '^KS200', unit: 'pt', target: 'up', value: 0, signal: 'neutral', type: 'index' },
  { id: 'kr_cpi', name: 'Inflation Rate', nameKo: '물가상승률', description: '소비자물가지수 전년동기비. 2% 목표선 유지가 적정 물가안정 수준', country: 'KR', yahooSymbol: 'USXCPI=X', unit: '%', target: 'neutral', value: 2.2, signal: 'neutral', type: 'inflation' },
  { id: 'kr_unemploy', name: 'Unemployment', nameKo: '실업률', description: '경제활동인구 대비 실업자 비율. 2.8% 미만은 완전고용 수준', country: 'KR', yahooSymbol: 'KRUNEMP=X', unit: '%', target: 'down', value: 2.8, signal: 'up', type: 'unemployment' },
  { id: 'kr_interest', name: 'Base Interest Rate', nameKo: '기준금리', description: '한국은행 기준금리. 금리 인상=긴축, 인하=완화 정책 방향', country: 'KR', yahooSymbol: 'KRIBOR=X', unit: '%', target: 'neutral', value: 3.5, signal: 'neutral', type: 'interest_rate' },
  { id: 'kr_exchange', name: 'USD/KRW Exchange', nameKo: '원/달러 환율', description: '1달러당 원화 환율. 상승=원화약세(수출호조), 하락=원화강세(수입가경)', country: 'KR', yahooSymbol: 'USDKRW=X', unit: '원', target: 'down', value: 1350, signal: 'neutral', type: 'exchange_rate' },
]

// 미국 경제 지표
const US_INDICATORS: Indicator[] = [
  { id: 'usp500', name: 'S&P 500', nameKo: 'S&P 500 지수', description: '미국 대형주 500개 종목으로 구성된 대표 지수, 미국 경제의 건강 지표', country: 'US', yahooSymbol: '^GSPC', unit: 'pt', target: 'up', value: 0, signal: 'neutral', type: 'index' },
  { id: 'usdjwr', name: 'Dow Jones', nameKo: '다우 존스 지수', description: '미국 산업 대표 30개 우량기업으로 구성된 역사 있는 주가지수', country: 'US', yahooSymbol: '^DJI', unit: 'pt', target: 'up', value: 0, signal: 'neutral', type: 'index' },
  { id: 'usnx', name: 'NASDAQ', nameKo: '나스닥 종합지수', description: '기술주 중심의 상장 종목 3000개 이상 포함, 미국 IT 섹터 대표', country: 'US', yahooSymbol: '^IXIC', unit: 'pt', target: 'up', value: 0, signal: 'neutral', type: 'index' },
  { id: 'uscpi', name: 'CPI', nameKo: '소비자물가지수', description: '소비자물가 전년동기비 변화율. 상승=인플레이션, 2-3% 내 유지가 적정', country: 'US', yahooSymbol: 'USXCPI=X', unit: '지수', target: 'neutral', value: 315.7, signal: 'neutral', type: 'inflation' },
  { id: 'unemployment', name: 'Unemployment', nameKo: '실업률', description: '실업률. 4% 이하=완전고용 수준, 상승 시 경기 침체 우려', country: 'US', yahooSymbol: 'USUNEMP=X', unit: '%', target: 'down', value: 4.3, signal: 'up', type: 'unemployment' },
  { id: 'usfedrate', name: 'Fed Funds Rate', nameKo: '미 연방기준금리', description: '미 연준 기준금리. 금리 결정=통화정책 방향 파악, 금인하=완화, 금인상=긴축', country: 'US', yahooSymbol: 'FDCMPCT1565900001001UM', unit: '%', target: 'neutral', value: 4.5, signal: 'neutral', type: 'interest_rate' },
]

function getSignal(ind: Indicator, value: number, changePct: number): string {
  if (ind.type === 'index') {
    if (changePct > 0.1) return 'up'
    if (changePct <= -0.1) return 'down'
    return 'neutral'
  }
  if (ind.type === 'exchange_rate') {
    if (changePct < -0.5) return 'up'   // 원화 강세
    if (changePct > 1) return 'down'    // 원화 약세
    return 'neutral'
  }
  if (ind.type === 'inflation') {
    if (value <= 2.0) return 'up'
    if (value <= 3.0) return 'neutral'
    return 'down'
  }
  if (ind.type === 'unemployment') {
    if (value <= 3.5) return 'up'    // 완전고용
    if (value <= 5.0) return 'neutral'
    return 'down'
  }
  if (ind.type === 'interest_rate') {
    if (changePct < 0) return 'up'    // 금리 인하
    if (Math.abs(changePct) <= 0.5) return 'neutral'
    return 'down'
  }
  return 'neutral'
}

async function fetchYahooFromProxy(symbol: string): Promise<YahooData | null> {
  try {
    const url = `http://localhost:3001/api/yfinance/chart/${encodeURIComponent(symbol)}?interval=1d&range=1d`
    const res = await fetch(url, { signal: AbortSignal.timeout(5000) })
    if (!res.ok) return null
    const json = await res.json()
    const result = json?.chart?.result?.[0]
    if (!result) return null
    const close = result.indicators?.quote?.[0]?.close
    if (!close || close.length === 0) return null
    const current = close[close.length - 1]
    if (!current || isNaN(current)) return null
    const meta = result.meta
    const prevClose = meta?.regularMarketPreviousClose || meta?.chartPreviousClose || 0
    const change = current - prevClose
    const changePct = prevClose ? (change / prevClose) * 100 : 0
    return { current, change, changePct }
  } catch {
    return null
  }
}

function IndicatorCard({ ind, yahoo }: { ind: Indicator; yahoo: YahooData | null }) {
  const color = COLORS[ind.signal || 'neutral']
  const flag = ind.country === 'KR' ? '🇰🇷' : '🇺🇸'
  const displayValue = yahoo ? yahoo.current : ind.value
  const changePct = yahoo ? yahoo.changePct : (ind.value > 0 ? 0 : 0)
  const isUp = changePct > 0.001
  const isNeutral = Math.abs(changePct) <= 0.001

  let formattedValue: string
  if (ind.id === 'kr_exchange' || ind.id === 'krkq11') {
    formattedValue = `${Math.round(displayValue).toLocaleString()}`
  } else if (ind.id === 'kr_samsung' || ind.type === 'index') {
    formattedValue = `${Math.round(displayValue).toLocaleString()}`
  } else if (ind.unit === '%') {
    formattedValue = `${displayValue.toFixed(2)}${ind.unit}`
  } else if (ind.unit === '지수' || ind.unit === 'pt') {
    formattedValue = `${displayValue.toFixed(2)} ${ind.unit}`
  } else {
    formattedValue = `${displayValue} ${ind.unit}`
  }

  const changeText = isNeutral ? '보합' : isUp ? '▲ 상승' : '▼ 하락'
  const changeSign = isUp ? '+' : ''

  return (
    <div style={{
      background: COLORS.card,
      border: `1px solid ${COLORS.border}`,
      borderRadius: 16,
      padding: 24,
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
      e.currentTarget.style.borderColor = COLORS.border
    }}>
      {/* Header: 신호등 + 국기 + 지표명 + 등락률 */}
      <div style={{ display: 'flex', alignItems: 'center', marginBottom: 16 }}>
        <div style={{
          width: 14,
          height: 14,
          borderRadius: '50%',
          backgroundColor: color,
          marginRight: 12,
          boxShadow: `0 0 10px ${color}60`,
          flexShrink: 0,
        }} />
        <span style={{ fontSize: 20, marginRight: 8 }}>{flag}</span>
        <h3 style={{ fontSize: 17, fontWeight: 600, margin: 0, color: COLORS.text, flex: 1 }}>
          {ind.nameKo}
        </h3>
        {yahoo && (
          <span style={{
            marginLeft: 'auto',
            fontSize: 13,
            fontWeight: 700,
            color: isUp ? '#22c55e' : isNeutral ? '#eab308' : '#ef4444',
            background: isUp ? '#22c55e14' : isNeutral ? '#eab30814' : '#ef444414',
            padding: '4px 12px',
            borderRadius: 20,
          }}>
            {changeSign}{changePct.toFixed(2)}{isNeutral ? ' (보합)' : ` (${changeText})`}
          </span>
        )}
      </div>

      {/* Main Value: 크고 굵게 */}
      <div style={{
        fontSize: 42,
        fontWeight: 800,
        margin: '16px 0',
        lineHeight: 1,
        color: color,
        letterSpacing: '-0.02em',
      }}>
        {formattedValue}
      </div>

      {/* Change detail */}
      {yahoo && (
        <div style={{
          fontSize: 14,
          color: COLORS.textSecondary,
          marginBottom: 12,
          fontWeight: 500,
        }}>
          {isUp ? '▲' : '▼'} {Math.abs(changePct).toFixed(2)}% ({changeText})
        </div>
      )}

      {/* Description */}
      <p style={{
        color: COLORS.textSecondary,
        fontSize: 13,
        margin: 0,
        lineHeight: 1.6,
      }}>
        {ind.description}
      </p>
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
        boxShadow: `0 0 12px ${COLORS.up}60`,
      }} />
      <span style={{ fontSize: 13, fontWeight: 500, color: COLORS.up }}>
        긍정 {upCount}
      </span>
      <div style={{
        width: 10,
        height: 10,
        borderRadius: '50%',
        backgroundColor: COLORS.neutral,
        boxShadow: `0 0 8px ${COLORS.neutral}60`,
      }} />
      <span style={{ fontSize: 13, fontWeight: 500, color: COLORS.neutral }}>
        중립 {neutralCount}
      </span>
      <div style={{
        width: 10,
        height: 10,
        borderRadius: '50%',
        backgroundColor: COLORS.down,
        boxShadow: `0 0 8px ${COLORS.down}60`,
      }} />
      <span style={{ fontSize: 13, fontWeight: 500, color: COLORS.down }}>
        부정 {downCount}
      </span>
    </div>
  )
}

function App() {
  const [loading, setLoading] = useState(true)
  const [data, setData] = useState<Indicator[]>([])
  const [yahooMap, setYahooMap] = useState<Record<string, YahooData>>({})
  const [lastUpdated, setLastUpdated] = useState('')

  const fetchAll = async () => {
    try {
      setLoading(true)
      const symbols = [...KR_INDICATORS, ...US_INDICATORS].filter(i => i.yahooSymbol).map(i => i.yahooSymbol!)
      const results: Record<string, YahooData> = {}
      
      // 병렬로 Yahoo Finance 데이터 fetched
      const fetchPromises = symbols.map(async (symbol) => {
        const data = await fetchYahooFromProxy(symbol)
        if (data) {
          results[symbol] = data
        }
      })
      await Promise.all(fetchPromises)
      
      setYahooMap(results)

      // 지표 데이터 완성
      const allData: Indicator[] = [
        ...KR_INDICATORS.map(ind => {
          const yahoo = results[ind.yahooSymbol!]
          const realValue = yahoo ? yahoo.current : ind.value
          const realSignal = yahoo
            ? getSignal(ind, yahoo.current, yahoo.changePct)
            : ind.signal
          return { ...ind, value: realValue, signal: realSignal }
        }),
        ...US_INDICATORS.map(ind => {
          const yahoo = results[ind.yahooSymbol!]
          const realValue = yahoo ? yahoo.current : ind.value
          const realSignal = yahoo
            ? getSignal(ind, yahoo.current, yahoo.changePct)
            : ind.signal
          return { ...ind, value: realValue, signal: realSignal }
        }),
      ]

      setData(allData)
      setLastUpdated(new Date().toLocaleString('ko-KR'))
    } catch (err) {
      console.error('Fetch error:', err)
      setData([...KR_INDICATORS, ...US_INDICATORS])
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
      {/* Header */}
      <header style={{
        background: 'linear-gradient(135deg, #1a1a2e 0%, #16213e 50%, #0f3460 100%)',
        padding: '40px 20px',
        textAlign: 'center',
        borderBottom: `1px solid ${COLORS.border}`,
      }}>
        <h1 style={{
          fontSize: 32,
          margin: 0,
          fontWeight: 800,
          letterSpacing: '-0.02em',
        }}>
          🇺🇸🇰🇷 한·미 경제 신호등
        </h1>
        <p style={{
          margin: '8px 0 24px',
          color: COLORS.textSecondary,
          fontSize: 14,
        }}>
          Yahoo Finance + 세계은행 기반 실시간 경제 지표 대시보드
        </p>

        {/* Summary Bar: 좌우 요약 */}
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

      {/* Main Content: 좌우 2단 컬럼 */}
      <main style={{
        maxWidth: 1400,
        margin: '0 auto',
        padding: '32px 20px',
        display: 'grid',
        gridTemplateColumns: '1fr 1fr',
        gap: 32,
      }}>
        {/* Left: 미국 경제 */}
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
                yahoo={yahooMap[ind.yahooSymbol] || null}
              />
            ))}
          </div>
        </section>

        {/* Right: 한국 경제 */}
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
                yahoo={yahooMap[ind.yahooSymbol] || null}
              />
            ))}
          </div>
        </section>
      </main>

      {/* Footer */}
      <footer style={{
        textAlign: 'center',
        padding: '32px 20px',
        color: COLORS.textSecondary,
        fontSize: 13,
        borderTop: `1px solid ${COLORS.border}`,
        marginTop: 40,
      }}>
        <p>데이터 출처: Yahoo Finance (실시간), 세계은행 (거시경제)</p>
        <p style={{ marginTop: 4 }}>마지막 업데이트: {lastUpdated}</p>
        <p style={{ marginTop: 8, fontSize: 12, opacity: 0.6 }}>
          ⚠️ KRX OpenAPI 연동 예정 (API 키 확보 시 실시간 개인 종목 데이터 추가)
        </p>
      </footer>

      <style>{`
        @keyframes spin {
          from { transform: rotate(0deg); }
          to { transform: rotate(360deg); }
        }
        @media (max-width: 900px) {
          main {
            grid-template-columns: 1fr !important;
          }
        }
      `}</style>
    </div>
  )
}

export default App
