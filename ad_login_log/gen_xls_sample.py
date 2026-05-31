#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
.xls 파일 샘플 생성 (구버전 Excel)
"""

import xlwt
import os

def create_xls_sample():
    wb = xlwt.Workbook(encoding='utf-8')
    ws = wb.add_sheet('원본')
    
    # 헤더
    headers = ['No', '발생일시', '엔포서명', 'IP', '관리자', '이벤트 종류']
    bold = xlwt.easyxf('font: bold on')
    for col, h in enumerate(headers):
        ws.write(0, col, h, bold)
    
    rows = [
        [1, '2026-05-20 09:15:30', 'firewall01', '192.168.1.10', 'admin01', 'IP 등록'],
        [2, '2026-05-20 10:22:45', 'firewall01', '10.0.0.55', 'admin02', 'IP 삭제'],
        [3, '2026-05-20 11:05:12', 'firewall01', '172.16.0.3', 'admin01', '로그인'],
        [4, '2026-05-21 08:30:00', 'firewall02', '192.168.2.50', 'admin03', '인증허가'],
        [5, '2026-05-21 14:17:33', 'firewall01', '10.0.0.100', 'admin02', 'IP 삭제'],
        [6, '2026-05-21 16:45:22', 'web01', '192.168.5.80', 'admin01', '파일 업로드'],
        [7, '2026-05-22 07:00:10', 'firewall02', '172.16.1.200', 'admin01', 'IP 등록'],
        [8, '2026-05-22 09:33:41', 'firewall01', '10.10.0.15', 'admin04', 'IP 등록'],
        [9, '2026-05-22 12:00:00', 'monitor01', '192.168.0.1', 'admin01', '시스템 경고'],
        [10, '2026-05-23 02:00:15', 'firewall01', '10.0.0.200', 'admin02', '일정기간 미사용 IP삭제'],
    ]
    
    for row_num, row_data in enumerate(rows):
        for col_num, val in enumerate(row_data):
            if col_num == 1:  # 날짜
                ws.write(row_num + 1, col_num, str(val))
            else:
                ws.write(row_num + 1, col_num, val)
    
    # 컬럼 너비
    for col in range(len(headers)):
        ws.col(col).width = 4000
    
    output_path = '/Users/scott/hermes room/ip_classifier/samples_1.xls'
    wb.save(output_path)
    print(f"✓ {output_path} 생성 완료")
    
    # 분류 예측
    new_ip = [r for r in rows if 'IP 등록' in r[5] or '인증허가' in r[5]]
    del_ip = [r for r in rows if 'IP 삭제' in r[5] or '일정기간 미사용 IP삭제' in r[5]]
    other = [r for r in rows if not ('IP 등록' in r[5] or '인증허가' in r[5] or 'IP 삭제' in r[5] or '일정기간 미사용 IP삭제' in r[5])]
    print(f"  신규IP: {len(new_ip)}행, IP삭제: {len(del_ip)}행, 기타: {len(other)}행")

if __name__ == '__main__':
    create_xls_sample()
