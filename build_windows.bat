@echo off
REM Windows용 빌드 스크립트

echo ========================================
echo Img2WebP Windows 빌드 스크립트
echo ========================================
echo.

REM Python 환경 확인
python --version >nul 2>&1
if errorlevel 1 (
    echo 오류: Python이 설치되어 있지 않거나 PATH에 없습니다.
    pause
    exit /b 1
)

REM 가상환경 활성화 (있는 경우)
if exist "venv\Scripts\activate.bat" (
    echo 가상환경 활성화 중...
    call venv\Scripts\activate.bat
)

REM 의존성 확인
echo 의존성 확인 중...
pip show pyinstaller >nul 2>&1
if errorlevel 1 (
    echo PyInstaller가 설치되어 있지 않습니다. 설치 중...
    pip install pyinstaller
)

REM 아이콘 파일 생성
echo.
echo Windows용 아이콘 파일 생성 중...
python create_ico.py
if errorlevel 1 (
    echo 경고: 아이콘 파일 생성에 실패했습니다. 아이콘 없이 빌드를 진행합니다.
)

REM 빌드 실행
echo.
echo 빌드 시작...
pyinstaller Img2WebP_windows.spec

if errorlevel 1 (
    echo.
    echo 오류: 빌드에 실패했습니다.
    pause
    exit /b 1
)

echo.
echo ========================================
echo 빌드 완료!
echo ========================================
echo 실행 파일 위치: dist\Img2WebP.exe
echo.
pause

