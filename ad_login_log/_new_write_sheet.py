    def _write_sheet(self, ws, rows, has_bigo=False):
        """시트에 헤더와 데이터 쓰기.
        has_bigo=True: 신규IP 시트 (비고 열 포함)
        has_bigo=False: IP삭제 시트 (비고 열 없음)
        """
        # 비고 열 유무에 따라 헤더 결정
        if has_bigo:
            headers = ["No", "발생일시", "이벤트 종류", "엔포서명", "IP", "관리자", "비고"]
        else:
            headers = ["No", "발생일시", "이벤트 종류", "엔포서명", "IP", "관리자"]
        
        bold_font = Font(bold=True)
        thin_border = Border(
            left=Side(style='thin'),
            right=Side(style='thin'),
            top=Side(style='thin'),
            bottom=Side(style='thin')
        )

        # 헤더
        for col, h in enumerate(headers, 1):
            cell = ws.cell(row=1, column=col, value=h)
            cell.font = bold_font
            cell.border = thin_border
            cell.alignment = Alignment(horizontal='center', vertical='center')

        # 데이터
        for idx, row_data in enumerate(rows, 1):
            ws.cell(row=idx + 1, column=1, value=idx).border = thin_border
            ws.cell(row=idx + 1, column=1).alignment = Alignment(horizontal='center')

            # 발생일시
            ts = row_data.get("발생일시", "")
            ts_str = self._format_timestamp(ts)
            ws.cell(row=idx + 1, column=2, value=ts_str).border = thin_border

            # 이벤트 종류
            event_val = row_data.get("이벤트 종류", "") or ""
            ws.cell(row=idx + 1, column=3, value=str(event_val)).border = thin_border

            # 엔포서명
            enforcer = row_data.get("엔포서명", "") or ""
            ws.cell(row=idx + 1, column=4, value=enforcer).border = thin_border

            # IP - 숫자일 수 있으니 문자열로
            ip_val = row_data.get("IP", "") or ""
            ws.cell(row=idx + 1, column=5, value=str(ip_val)).border = thin_border

            # 관리자
            admin_val = row_data.get("관리자", "") or ""
            ws.cell(row=idx + 1, column=6, value=admin_val).border = thin_border

            # 비고 (신규IP 시트만)
            if has_bigo:
                bigo_val = row_data.get("비고", "") or ""
                ws.cell(row=idx + 1, column=7, value=str(bigo_val)).border = thin_border

        # 셀 너비 자동 조정
        max_widths = [10] * len(headers)     # 기본 너비
        for row_data in rows:
            vals = [
                str(rows.index(row_data) + 1),     # No
                self._format_timestamp(row_data.get("발생일시", "")),     # 발생일시
                str(row_data.get("이벤트 종류", "") or ""),     # 이벤트 종류
                str(row_data.get("엔포서명", "") or ""),     # 엔포서명
                str(row_data.get("IP", "") or ""),     # IP
                str(row_data.get("관리자", "") or ""),     # 관리자
            ]
            if has_bigo:
                vals.append(str(row_data.get("비고", "") or ""))     # 비고
            for col_idx, val in enumerate(vals):
                w = len(val.encode('utf-8'))    # 한글은 3바이트
                if w > max_widths[col_idx]:
                    max_widths[col_idx] = min(w, 60)    # 최대 60

        for col_idx, max_w in enumerate(max_widths):
            col_letter = ws.cell(row=1, column=col_idx + 1).column_letter
            ws.column_dimensions[col_letter].width = max_w + 4

    def _format_timestamp(self, val):
        """timestamp를 YYYY-MM-DD HH:mm:ss 형식으로 변환."""
        if not val:
            return ""
        if isinstance(val, str):
            return val   # 이미 문자열
        if isinstance(val, datetime):
            return val.strftime("%Y-%m-%d %H:%M:%S")
         # openpyxl/xlrd 날짜 객체
        if hasattr(val, 'strftime'):
            return val.strftime("%Y-%m-%d %H:%M:%S")
        return str(val)
