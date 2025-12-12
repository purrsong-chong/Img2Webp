#!/bin/bash
# Windows용 빌드 스크립트 (WSL/Linux에서 Windows 빌드용)

set -e

echo "========================================"
echo "Img2WebP Windows 빌드 스크립트"
echo "========================================"
echo ""

# Python 환경 확인
if ! command -v python &> /dev/null; then
    echo "오류: Python이 설치되어 있지 않거나 PATH에 없습니다."
    exit 1
fi

# 가상환경 활성화 (있는 경우)
if [ -f "venv/bin/activate" ]; then
    echo "가상환경 활성화 중..."
    source venv/bin/activate
fi

# 의존성 확인
echo "의존성 확인 중..."
if ! pip show pyinstaller &> /dev/null; then
    echo "PyInstaller가 설치되어 있지 않습니다. 설치 중..."
    pip install pyinstaller
fi

# 아이콘 파일 생성
echo ""
echo "Windows용 아이콘 파일 생성 중..."
python create_ico.py || echo "경고: 아이콘 파일 생성에 실패했습니다. 아이콘 없이 빌드를 진행합니다."

# 빌드 실행
echo ""
echo "빌드 시작..."
pyinstaller Img2WebP_windows.spec

if [ $? -eq 0 ]; then
    echo ""
    echo "========================================"
    echo "빌드 완료!"
    echo "========================================"
    echo "실행 파일 위치: dist/Img2WebP.exe"
    echo ""
else
    echo ""
    echo "오류: 빌드에 실패했습니다."
    exit 1
fi

