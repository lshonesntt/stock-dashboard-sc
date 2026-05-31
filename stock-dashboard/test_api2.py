import requests
import json
from datetime import datetime, timedelta

# IMF API - KOSPI / GDP / inflation / exchange rate / trade balance
print("=== IMF API 테스트 ===\n")

# IMF S&P500 / KOSPI / exchange rate / trade balance
# IMF Data API: https://data.imf.org/quick/QuickStarts.jsp

# 1. KOSPI index - KFISYMT00748487 (or similar)
try:
    # IMF Quoted Exchange Rates - KRW
    url = "https://data.imf.org/quick/QuickRest.svc/GetQuotedFXRate"
    params = {
        "key": "",  # free tier
        "source": "DFEXR_USD_KRW",  # USD/KRW
        "freq": "D"
    }
    res = requests.get(url, params=params, timeout=10)
    print(f"IMF FX Rate: status={res.status_code}, text={res.text[:200]}")
except Exception as e:
    print(f"IMF FX Error: {e}")

# 2. World Bank Global indicators for KR
print("\n=== World Bank Global API for KR ===")
wb_indicators = [
    "NY.GDP.MKDP.KD.ZG",   # GDP growth
    "NY.GDP.DEFL.KD.ZG",   # Inflation
    "SL.UEM.TOTL.ZS",      # Unemployment
    "FR.INR.RINR",         # Interest rate
]

for ind_id in wb_indicators:
    try:
        url = f"https://api.worldbank.org/v2/indicator/{ind_id}"
        params = {"date": "2023:2025", "format": "json", "per_page": 5}
        res = requests.get(url, params=params, timeout=10)
        if res.status_code == 200:
            data = res.json()
            if len(data) > 1 and data[1]:
                for item in data[1]:
                    country = item.get("country", "")
                    val = item.get("value")
                    if country == "Korea, Rep." and val is not None:
                        print(f"  {ind_id} ({country}): {val} (date: {item.get('date')})")
    except Exception as e:
        print(f"  {ind_id} Error: {e}")

# 3. Try FRED API with Fred API Key (if available)
print("\n=== FRED API test ===")
fred_api_key = ""  # Need user's FRED API key

# 4. Try alternative: Korean Stats API (통계청 Open API)
print("\n=== 통계청 Open API ===")
try:
    import os
    stats_url = "http://statistik.kostat.go.kr:8080/openapi/ndl"
    print(f"Stats API available: {stats_url}")
except Exception as e:
    print(f"Stats API Error: {e}")

print("\n=== FRED alternative: Yahoo Finance ===")
try:
    import yfinance as yf
    # KOSPI: ^KS11, Samsung: 005930.KS
    kospi = yf.Ticker("^KS11")
    hist = kospi.history(period="5d")
    if not hist.empty:
        last = hist.iloc[-1]
        print(f"KOSPI: {last['Close']:.2f}")
    else:
        print("KOSPI: No data")
    
    samsung = yf.Ticker("005930.KS")
    s_hist = samsung.history(period="5d")
    if not s_hist.empty:
        sl = s_hist.iloc[-1]
        print(f"Samsung: {sl['Close']:.0f} KRW")
    else:
        print("Samsung: No data")
except ImportError:
    print("yfinance not installed")
except Exception as e:
    print(f"Yahoo Finance Error: {e}")
