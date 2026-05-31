import requests
import json
from datetime import datetime, timedelta

API_KEY = "875D2DA8A6C940D7BFF23955D567686A2E88FC55"

# 기준일자 계산 (2일 전)
ref_date = (datetime.now() - timedelta(days=2)).strftime("%Y%m%d")
print(f"기준일자 (2일 전): {ref_date}\n")

# 유가증권 일별 매매정보 API
print("=== 유가증권 일별 매매정보 (삼성전자 005930) ===")
try:
    url = "http://data-dbg.krx.co.kr/svc/apis/sto/stk_bydd_trd"
    headers = {"AUTH_KEY": API_KEY}
    params = {"basDd": ref_date}
    res = requests.get(url, headers=headers, params=params, timeout=10)
    print(f"Response status: {res.status_code}")
    print(f"Response text: {res.text[:500]}")
except Exception as e:
    print(f"Error: {e}")

print("\n=== 시도 2: HTTPS ===")
try:
    url = "https://data-dbg.krx.co.kr/svc/apis/sto/stk_bydd_trd"
    headers = {"AUTH_KEY": API_KEY}
    params = {"basDd": ref_date}
    res = requests.get(url, headers=headers, params=params, timeout=10, 
                       verify=False)
    print(f"Response status: {res.status_code}")
    print(f"Response text: {res.text[:500]}")
except Exception as e:
    print(f"Error: {e}")

print("\n=== 시도 3: sample 엔드포인트 ===")
try:
    url = "http://data-dbg.krx.co.kr/svc/sample/apis/sto/stk_bydd_trd"
    headers = {"AUTH_KEY": API_KEY}
    params = {"basDd": ref_date}
    res = requests.get(url, headers=headers, params=params, timeout=10)
    print(f"Response status: {res.status_code}")
    print(f"Response text: {res.text[:500]}")
except Exception as e:
    print(f"Error: {e}")

print("\n=== 시도 4: POST method ===")
try:
    url = "https://data-dbg.krx.co.kr/svc/apis/sto/stk_bydd_trd"
    headers = {"AUTH_KEY": API_KEY, "Content-Type": "application/json"}
    data = {"basDd": ref_date}
    res = requests.post(url, headers=headers, json=data, timeout=10, 
                        verify=False)
    print(f"Response status: {res.status_code}")
    print(f"Response text: {res.text[:500]}")
except Exception as e:
    print(f"Error: {e}")
