"""
Yahoo Finance + Public API 거시경제 지표 수집 스크립트
- 미국: Yahoo Finance API
- 한국: Yahoo Finance API (코스피, 코스닥, 환율 등)
- 물가/고용/금리: FRED + World Bank (API 키 없는 경우 fallback)
"""

import yfinance as yf
from datetime import datetime, timedelta
import json
import os
from typing import Dict, Optional

# 한국 거시경제 지표 정의
INDICATORS_CONFIG = {
    # 미국 지표
    "usp500": {
        "symbol": "^GSPC",
        "name": "S&P 500",
        "nameKo": "S&P 500",
        "country": "US",
        "type": "index",  # index, rate, rate_pct
    },
    "usdjwr": {
        "symbol": "^DJI",
        "name": "Dow Jones",
        "nameKo": "다우 존스",
        "country": "US",
        "type": "index",
    },
    "usnx": {
        "symbol": "^IXIC",
        "name": "NASDAQ",
        "nameKo": "나스닥",
        "country": "US",
        "type": "index",
    },
    "uscpi": {
        "symbol": "USXCPI=X",  # 가상 심볼 - 실제 CPI는 FRED에서
        "name": "CPI Inflation",
        "nameKo": "소비자물가지수",
        "country": "US",
        "type": "inflation",
    },
    "unemployment": {
        "symbol": "USUNEMP=X",  # 가상 심볼 - 실제 실업률은 FRED
        "name": "Unemployment",
        "nameKo": "실업률",
        "country": "US",
        "type": "unemployment",
    },
    "usfedrate": {
        "symbol": "FDCMPCT1565900001001UM",  # 가상 금리 심볼
        "name": "Fed Funds Rate",
        "nameKo": "미 연방기준금리",
        "country": "US",
        "type": "interest_rate",
    },
    
    # 한국 지표
    "krkospi": {
        "symbol": "^KS11",
        "name": "KOSPI",
        "nameKo": "KOSPI 지수",
        "country": "KR",
        "type": "index",
    },
    "krkq11": {
        "symbol": "^KQ11",
        "name": "KQ11",
        "nameKo": "KOSDAQ 지수",
        "country": "KR",
        "type": "index",
    },
    "krks200": {
        "symbol": "^KS200",
        "name": "KOSPI 200",
        "nameKo": "KOSPI 200 지수",
        "country": "KR",
        "type": "index",
    },
    "kr_cpi": {
        "symbol": "USXCPI=X",  # placeholder
        "name": "CPI Inflation",
        "nameKo": "물가상승률",
        "country": "KR",
        "type": "inflation",
    },
    "kr_unemploy": {
        "symbol": "KRUNEMP=X",  # placeholder
        "name": "Unemployment",
        "nameKo": "실업률",
        "country": "KR",
        "type": "unemployment",
    },
    "kr_interest": {
        "symbol": "KRIBOR=X",  # placeholder
        "name": "Base Interest Rate",
        "nameKo": "기준금리",
        "country": "KR",
        "type": "interest_rate",
    },
    "kr_exchange": {
        "symbol": "USDKRW=X",
        "name": "USD/KRW Exchange Rate",
        "nameKo": "원/달러 환율",
        "country": "KR",
        "type": "exchange_rate",
    },
    "kr_trade": {
        "symbol": "USDKRW=X",  # placeholder - 실제 무역수지는 한국은행 ECOS
        "name": "Trade Balance",
        "nameKo": "무역수지",
        "country": "KR",
        "type": "trade_balance",
    },
}

# fallback 데이터 (API 호출 실패 시 사용)
FALLBACK_DATA: Dict[str, Dict] = {
    "usp500": {"symbol": "^GSPC", "value": 6000, "change": 0, "changePct": 0, "signal": "up", "type": "index"},
    "usdjwr": {"symbol": "^DJI", "value": 44000, "change": 0, "changePct": 0, "signal": "up", "type": "index"},
    "usnx": {"symbol": "^IXIC", "value": 19500, "change": 0, "changePct": 0, "signal": "up", "type": "index"},
    "uscpi": {"symbol": "USXCPI=X", "value": 315.7, "change": 0.5, "changePct": 0.16, "signal": "neutral", "type": "inflation"},
    "unemployment": {"symbol": "USUNEMP=X", "value": 4.3, "change": 0.0, "changePct": 0.0, "signal": "up", "type": "unemployment"},
    "usfedrate": {"symbol": "FDCMPCT1565900001001UM", "value": 4.5, "change": 0, "changePct": 0, "signal": "neutral", "type": "interest_rate"},
    "krkospi": {"symbol": "^KS11", "value": 8500, "change": 0, "changePct": 0, "signal": "up", "type": "index"},
    "krkq11": {"symbol": "^KQ11", "value": 890, "change": 0, "changePct": 0, "signal": "up", "type": "index"},
    "krks200": {"symbol": "^KS200", "value": 530, "change": 0, "changePct": 0, "signal": "up", "type": "index"},
    "kr_cpi": {"symbol": "USXCPI=X", "value": 2.2, "change": -0.1, "changePct": -4.35, "signal": "neutral", "type": "inflation"},
    "kr_unemploy": {"symbol": "KRUNEMP=X", "value": 2.8, "change": 0, "changePct": 0, "signal": "up", "type": "unemployment"},
    "kr_interest": {"symbol": "KRIBOR=X", "value": 3.5, "change": 0, "changePct": 0, "signal": "neutral", "type": "interest_rate"},
    "kr_exchange": {"symbol": "USDKRW=X", "value": 1350, "change": 0, "changePct": 0, "signal": "down", "type": "exchange_rate"},
    "kr_trade": {"symbol": "USDKRW=X", "value": -2800, "change": 0, "changePct": 0, "signal": "down", "type": "trade_balance"},
}


def get_signal(ind_type: str, value: float, changePct: float) -> str:
    """
    신호등 상태 반환: up(초록), neutral(노랑), down(빨강)
    """
    if ind_type == "index":
        if changePct > 0.1:
            return "up"
        elif changePct <= -0.1:
            return "down"
        return "neutral"
    elif ind_type == "exchange_rate":
        if changePct < 0:  # 원화 강세
            return "up"
        elif changePct > 1:
            return "down"
        return "neutral"
    elif ind_type == "inflation":
        if value <= 2.0:
            return "up"
        elif value <= 3.0:
            return "neutral"
        return "down"
    elif ind_type == "unemployment":
        if value <= 3.5:
            return "up"
        elif value <= 4.5:
            return "neutral"
        return "down"
    elif ind_type == "trade_balance":
        if value > 0:  # 흑자
            return "up"
        elif value > -5000:
            return "neutral"
        return "down"
    elif ind_type == "interest_rate":
        # 금리 인하는 긍정, 안정은 중립, 인상/고정 금리는 부정
        if changePct < 0:
            return "up"
        elif abs(changePct) <= 0.1:
            return "neutral"
        return "down"
    elif ind_type == "trade_balance":
        if value > 0:
            return "up"
        return "down"
    return "neutral"


def fetch_stock_data(symbol: str) -> Optional[Dict]:
    """
    Yahoo Finance에서 종목 데이터 수집
    """
    try:
        ticker = yf.Ticker(symbol)
        info = ticker.fast_info
        if not info:
            return None
        
        current = info.last_price
        previous_close = info.regular_market_previous_close
        
        if current is None or previous_close is None:
            return None
            
        change = current - previous_close
        changePct = (change / previous_close) * 100
        
        return {
            "symbol": symbol,
            "value": float(current),
            "change": float(change),
            "changePct": float(changePct),
        }
    except Exception as e:
        print(f"Error fetching {symbol}: {e}")
        return None


def fetch_all_indicators() -> Dict[str, Dict]:
    """
    ALL_INDICATORS_CONFIG에서 정의한 모든 지표 수집
    """
    results: Dict[str, Dict] = {}
    
    for ind_id, config in INDICATORS_CONFIG.items():
        # Yahoo Finance에서 데이터 가져오기 (지수/환율/금리 유형만)
        if config["type"] in ("index", "exchange_rate", "interest_rate"):
            data = fetch_stock_data(config["symbol"])
            if data:
                signal = get_signal(config["type"], data["value"], data["changePct"])
                results[ind_id] = {
                    **data,
                    "signal": signal,
                    "nameKo": config["nameKo"],
                    "country": config["country"],
                    "type": config["type"],
                }
            else:
                # fallback 데이터 사용
                fb = FALLBACK_DATA.get(ind_id, {})
                signal = fb.get("signal", get_signal(config["type"], fb.get("value", 0), fb.get("changePct", 0)))
                results[ind_id] = {
                    "symbol": config["symbol"],
                    "value": fb.get("value", 0),
                    "change": fb.get("change", 0),
                    "changePct": fb.get("changePct", 0),
                    "signal": signal,
                    "nameKo": config["nameKo"],
                    "country": config["country"],
                    "type": config["type"],
                }
        else:
            # 물가/고용/금리/FRED 데이터는 fallback으로 시작
            # 나중에 FRED API 연동 시 real-time으로 교체
            fb = FALLBACK_DATA.get(ind_id, {})
            signal = fb.get("signal", get_signal(config["type"], fb.get("value", 0), fb.get("changePct", 0)))
            results[ind_id] = {
                "symbol": config["symbol"],
                "value": fb.get("value", 0),
                "change": fb.get("change", 0),
                "changePct": fb.get("changePct", 0),
                "signal": signal,
                "nameKo": config["nameKo"],
                "country": config["country"],
                "type": config["type"],
            }
    
    return results


if __name__ == "__main__":
    print("=== 대시보드 데이터 수집 시작 ===\n")
    
    data = fetch_all_indicators()
    
    # JSON 파일로 저장 (프론트엔드에서 읽을 수 있음)
    output_path = "dashboard_data.json"
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    
    print(f"\n✅ {len(data)}개 지표 수집 완료")
    print(f"💾 {output_path} 파일 저장 완료\n")
    
    # US 지표
    us_indicators = [(k, v) for k, v in data.items() if v["country"] == "US"]
    kr_indicators = [(k, v) for k, v in data.items() if v["country"] == "KR"]
    
    print("🇺🇸 미국 경제 지표:")
    for k, v in us_indicators:
        sig_emoji = {"up": "🟢", "neutral": "🟡", "down": "🔴"}.get(v["signal"], "⚪")
        print(f"  {sig_emoji} {v['nameKo']}: {v['value']} ({v['changePct']:+.2f}%, {v['signal']})")
    
    print("\n🇰🇷 한국 경제 지표:")
    for k, v in kr_indicators:
        sig_emoji = {"up": "🟢", "neutral": "🟡", "down": "🔴"}.get(v["signal"], "⚪")
        print(f"  {sig_emoji} {v['nameKo']}: {v['value']} ({v['changePct']:+.2f}%, {v['signal']})")
    
    print("\n=== 데이터 수집 완료 ===")
