@echo off
setlocal

echo =================================
echo AD 로그인 로그 자동화 - Windows EXE 빌드
echo =================================
echo.

cd /d "%~dp0"

echo [1/3] PyInstaller 및 의존성 확인...
pip install pyinstaller "PyQt5>=5.15" openpyxl xlrd python-dateutil >nul 2>&1
if %errorlevel% neq 0 (
    echo ERROR: 의존성 설치 실패
    pause
    exit /b 1
)

echo.
echo [2/3] 빌드 시작...
echo.
pyinstaller --noconfirm --onedir --name "AD로그인로그자동화" --windowed app.py

if %errorlevel% neq 0 (
    echo.
    echo ERROR: 빌드 실패
    pause
    exit /b 1
)

echo.
echo [3/3] 빌드 완료!
echo.
echo 출력 위치: dist\AD로그인로그자동화\AD로그인로그자동화.exe
echo.

REM 불필요한 파일 정리
if exist "build" rmdir /s /q "build"
if exist "AD로그인로그자동화.spec" del /q "AD로그인로그자동화.spec"

echo ========================================
echo 완료! dist\AD로그인로그자동화 폴더 안의
echo AD로그인로그자동화.exe 파일 사용 가능
echo ========================================
pause
