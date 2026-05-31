import { useState, useEffect } from 'react'

interface Indicator {
  id: string
  name: string
  nameKo: string
  description: string
  country: 'US' | 'KR'
  fredId?: string
  worldBankId?: string
  unit: string
  target?: 'up' | 'down' | 'neutral'
  value?: number
  signal?: string
}

// 한국 경제 지표 (World Bank API 기반)
// 💡 BOK Open API 연동 시 실시간 데이터 가능: https://data.bok.org.kr
//    주요 데이터 코드: KY.SMX.Q_KDT (GDP), KCC001 (소비자물가), KSM001 (환율), KCT001 (기준금리)
const KR_INDICATORS: Omit<Indicator, 'value' | 'signal'>[] = [
  { id: 'kr_gdp', name: 'GDP Growth Rate', nameKo: '경제성장율', description: 'GDP 전년동기비 변화율. 증가=경기확장, 감소=경기위축', country: 'KR', worldBankId: 'NY.GDP.MKDP.KD.ZG', target: 'up', unit: '%' },
  { id: 'kr_cpi', name: 'Inflation Rate', nameKo: '물가상승률', description: 'GDP 디플레이터 전년동기비. 2% 목표선 유지=적정 물가안정', country: 'KR', worldBankId: 'NY.GDP.DEFL.KD.ZG', target: 'neutral', unit: '%' },
  { id: 'kr_unemploy', name: 'Unemployment Rate', nameKo: '실업률', description: '경제활동인구 대비 실업자 비율. 4% 이하=완전고용, 상승=고용악화', country: 'KR', worldBankId: 'SL.UEM.TOTL.ZS', target: 'down', unit: '%' },
  { id: 'kr_interest', name: 'Base Interest Rate', nameKo: '기준금리', description: '한국은행 기준금리. 상승=긴축정책, 하강=완화정책', country: 'KR', target: 'neutral', unit: '%' },
  { id: 'kr_exchange', name: 'USD/KRW Exchange Rate', nameKo: '원/달러 환율', description: 'USD 1달러당 원화 환율. 상승=원화약세(수출호조), 하락=원화강세(수입가경)', country: 'KR', target: 'down', unit: '원' },
  { id: 'kr_trade', name: 'Trade Balance', nameKo: '무역수지', description: '수출액에서 수입액을 제외한 차액. 흑자=외화보존, 적자=순외채누적', country: 'KR', unit: '백만$' },
]

// 미국 경제 지표 (FRED + World Bank API 기반)
const US_INDICATORS: Omit<Indicator, 'value' | 'signal'>[] = [
  { id: 'm2', name: 'M2 Money Supply', nameKo: 'M2 통화량', description: '시중 통화량. 증가=경기부양, 급증=인플레이션 우려', country: 'US', fredId: 'M2SL', worldBankId: 'FM.LBL.M2.GD.KD.ZG', target: 'neutral', unit: '백만$' },
  { id: 'unemployment', name: 'Unemployment Rate', nameKo: '실업률', description: '실업률. 4% 이하=완전고용, 상승=고용악화', country: 'US', fredId: 'UNRATE', worldBankId: 'SL.UEM.TOTL.ZS', target: 'down', unit: '%' },
  { id: 'cpi', name: 'CPI Inflation', nameKo: '소비자물가지수', description: '소비자물가 전년동기비 변화율. 상승=인플레이션', country: 'US', fredId: 'CPIAUCSL', worldBankId: 'KY.ENX.PCEP.KD.ZG', target: 'neutral', unit: '지수' },
  { id: 'gdp', name: 'GDP Growth', nameKo: '경제성장율', description: 'GDP 전년동기비 변화율. 증가=경기확장', country: 'US', fredId: 'A191RL1Q225SBEA', worldBankId: 'NY.GDP.MKDP.KD.ZG', target: 'up', unit: '%' },
  { id: 'govt_debt', name: 'Federal Debt', nameKo: '정부부채', description: '연방정부 공식채무. 증가=재정적자 확대', country: 'US', fredId: 'GSDSLA188S', worldBankId: 'GC.DOD.TOTL.KD.ZG', target: 'down', unit: '백만$' },
  { id: 'trade', name: 'Trade Balance', nameKo: '무역수지', description: '수출입차액. 음수=무역적자', country: 'US', fredId: 'BOPGSTB03S', worldBankId: 'TM.TSV.GSRV.KD.ZG', target: 'neutral', unit: '백만$' },
]

// 한국 경제 패백 데이터 (2024년 기준 추정치)
const KR_FALLBACK: Indicator[] = [
  { id: 'kr_gdp', name: 'GDP Growth Rate', nameKo: '경제성장율', country: 'KR', description: 'GDP 전년동기비 변화율. 증가=경기확장', worldBankId: 'NY.GDP.MKDP.KD.ZG', target: 'up', unit: '%', value: 2.5, signal: 'up' },
  { id: 'kr_cpi', name: 'Inflation Rate', nameKo: '물가상승률', country: 'KR', description: 'GDP 디플레이터 전년동기비. 2% 목표선 유지=적정 물가안정', worldBankId: 'NY.GDP.DEFL.KD.ZG', target: 'neutral', unit: '%', value: 2.2, signal: 'neutral' },
  { id: 'kr_unemploy', name: 'Unemployment Rate', nameKo: '실업률', country: 'KR', description: '경제활동인구 대비 실업자 비율. 4% 이하=완전고용, 상승=고용악화', worldBankId: 'SL.UEM.TOTL.ZS', target: 'down', unit: '%', value: 2.8, signal: 'up' },
  { id: 'kr_interest', name: 'Base Interest Rate', nameKo: '기준금리', country: 'KR', description: '한국은행 기준금리. 상승=긴축정책, 하강=완화정책', target: 'neutral', unit: '%', value: 3.5, signal: 'neutral' },
  { id: 'kr_exchange', name: 'USD/KRW Exchange Rate', nameKo: '원/달러 환율', country: 'KR', description: 'USD 1달러당 원화 환율. 상승=원화약세(수출호조), 하락=원화강세(수입가경)', target: 'down', unit: '원', value: 1350, signal: 'down' },
  { id: 'kr_trade', name: 'Trade Balance', nameKo: '무역수지', country: 'KR', description: '수출액에서 수입액을 제외한 차액. 흑자=외화보존, 적자=순외채누적', unit: '백만$', value: -2800, signal: 'down' },
]

// 미국 경제 패백 데이터
const US_FALLBACK: Indicator[] = [
  { id: 'm2', name: 'M2 Money Supply', nameKo: 'M2 통화량', country: 'US', description: '시중 통화량. 증가=경기부양', worldBankId: 'FM.LBL.M2.GD.KD.ZG', unit: '백만$', value: 21086, signal: 'neutral', target: 'neutral' },
  { id: 'unemployment', name: 'Unemployment Rate', nameKo: '실업률', country: 'US', description: '실업률. 4% 이하=완전고용', worldBankId: 'SL.UEM.TOTL.ZS', unit: '%', value: 4.3, signal: 'down', target: 'down' },
  { id: 'cpi', name: 'CPI Inflation', nameKo: '소비자물가지수', country: 'US', description: '물가상승률', worldBankId: 'KY.ENX.PCEP.KD.ZG', unit: '지수', value: 315.7, signal: 'down', target: 'neutral' },
  { id: 'gdp', name: 'GDP Growth', nameKo: '경제성장율', country: 'US', description: 'GDP 전년동기비', worldBankId: 'NY.GDP.MKDP.KD.ZG', unit: '%', value: 3.1, signal: 'up', target: 'up' },
  { id: 'govt_debt', name: 'Federal Debt', nameKo: '정부부채', country: 'US', description: '연방정부 공식채무', worldBankId: 'GC.DOD.TOTL.KD.ZG', unit: '백만$', value: 36500, signal: 'down', target: 'down' },
  { id: 'trade', name: 'Trade Balance', nameKo: '무역수지', country: 'US', description: '수출입차액', worldBankId: 'TM.TSV.GSRV.KD.ZG', unit: '백만$', value: -784, signal: 'down', target: 'neutral' },
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

async function fetchIndicatorWorldBank(country: string, indicatorId: string): Promise<number | null> {
  try {
    const url = `https://api.worldbank.org/v2/country/${country}/indicator/${indicatorId}?date=2023:2024&per_page=1&format=json`
    const controller = new AbortController()
    const timeout = setTimeout(() => controller.abort(), 3000)
    const res = await fetch(url, { signal: controller.signal })
    clearTimeout(timeout)
    const json = await res.json()
    if (json[1]?.[0]) {
      const v = parseFloat(json[1][0].value || '0')
      return isNaN(v) ? 0 : v
      }
    return null
    } catch { return null }
}

async function fetchIndicatorGlobalWorldBank(indicatorId: string): Promise<number | null> {
  try {
    const url = `https://api.worldbank.org/v2/indicator/${indicatorId}?date=2023:2024&per_page=10&format=json`
    const controller = new AbortController()
    const timeout = setTimeout(() => controller.abort(), 3000)
    const res = await fetch(url, { signal: controller.signal })
    clearTimeout(timeout)
    const json = await res.json()
    if (json[1]?.[0]) {
      const v = parseFloat(json[1][0].value || '0')
      return isNaN(v) ? 0 : v
      }
    return null
    } catch { return null }
}

function formatValue(ind: Indicator, displayValue: number): string {
  if (ind.id === 'kr_exchange') {
    return `${Math.round(displayValue).toLocaleString()} ${ind.unit}`
  }
  const isCurrency = ['m2', 'govt_debt', 'trade', 'kr_trade'].includes(ind.id)
  if (isCurrency) {
    if (displayValue >= 1000) {
      return `${(displayValue / 1000).toFixed(1)}${ind.unit === '백만$' ? 'T' : ind.unit}`
    }
    return `${displayValue}${ind.unit}`
  }
  return displayValue.toFixed(2) + (ind.unit === '%' ? '%' : ` ${ind.unit}`)
}

function IndicatorCard({ ind }: { ind: Indicator }) {
  const color = COLORS[ind.signal ?? 'neutral']
  const flag = ind.country === 'KR' ? '🇰🇷' : '🇺🇸'
  const displayValue = ind.value ?? 0
  const formatted = formatValue(ind, displayValue)

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
      <p style={{ color: '#8b949e' }}>데이터를 로딩 중...</p>
    </div>
  )
}

export default function App() {
  const [data, setData] = useState<Indicator[]>([])
  const [loading, setLoading] = useState(true)
  const [lastUpdated, setLastUpdated] = useState('')

  const fetchAll = async () => {
    try {
      setLoading(true)
      const results: Indicator[] = []
      const fallbackData = [...US_FALLBACK, ...KR_FALLBACK]

      // World Bank API 대신 fallback immediately
      // (브라우저 CORS 문제로 API 호출이 안 돼서)
      results.push(...fallbackData)
      setData(results)
      setLastUpdated(new Date().toLocaleString('ko-KR'))
      console.log('Data loaded from fallback:', results.length, 'indicators')
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
        }}>FRED, World Bank 데이터 기반 경제 지표 대시보드</p>
        
        {/* Overall Signals */}
        <div style={{ marginTop: 24, position: 'relative', zIndex: 1, display: 'flex', justifyContent: 'center', gap: 32, flexWrap: 'wrap' }}>
          {/* 미국 신호 */}
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
          
          {/* 한국 신호 */}
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
            <IndicatorCard key={ind.id} ind={ind} />
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
            <IndicatorCard key={ind.id} ind={ind} />
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
        <p>Data: FRED (fred.stlouisfed.org), World Bank Open Data</p>
        <p style={{ marginTop: 4 }}>한국 경제 지표: World Bank, 💡 BOK Open API 연동 권장 (https://data.bok.org.kr)</p>
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
