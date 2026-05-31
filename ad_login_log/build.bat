@echo off
echo ========================================
echo   IP분류도구 Windows 빌드 스크립트
echo ========================================
echo.

cd /d "%~dp0"

echo [1/3] 가상 환경 생성 중...
python -m venv venv
if errorlevel 1 (
    echo ✖ 가상 환경 생성 실패
    pause
    exit /b 1
)

echo [2/3] 의존성 설치 중...
call venv\Scripts\activate.bat
pip install --upgrade pip
pip install PyQt5 openpyxl xlrd PyInstaller
if errorlevel 1 (
    echo ✖ 의존성 설치 실패
    pause
    exit /b 1
)

echo [3/3] PyInstaller 실행 중...
pyinstaller --clean --name "IP분류도구" ^
    --windowed ^
    --noconfirm ^
    app.py
if errorlevel 1 (
    echo ✖ 빌드 실패
    pause
    exit /b 1
)

echo.
echo ========================================
echo   빌드 완료!
echo   위치: dist/IP분류도구/IP분류도구.exe
echo ========================================
echo.
pause
