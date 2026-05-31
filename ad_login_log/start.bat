@echo off
echo ========================================
echo   IP분류도구 Windows 실행 스크립트
echo ========================================
echo.

cd /d "%~dp0"

echo [1/2] 가상 환경 확인...
if exist venv (
    echo [OK] 가상 환경이 이미 있습니다.
) else (
    echo [1/2] 가상 환경 생성 중...
    python -m venv venv
    if errorlevel 1 (
        echo ✖ 가상 환경 생성 실패 - Python 3.9+이 설치되어 있는지 확인하세요.
        pause
        exit /b 1
     )
)

echo [2/2] 의존성 설치 중...
call venv\Scripts\activate.bat
pip install --quiet --upgrade pip
pip install --quiet PyQt5 openpyxl xlrd
if errorlevel 1 (
    echo ✖ 의존성 설치 실패 - 인터넷 연결을 확인하세요.
    pause
    exit /b 1
)

echo.
echo ========================================
echo   IP분류도구 실행 중...
echo   종료하려면 창을 닫으세요.
echo ========================================
echo.

python app.py

pause
