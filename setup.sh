#!/bin/bash

echo "================================"
echo "네이버 부동산 프로젝트 설정"
echo "================================"
echo ""

# 가상환경 생성
echo "1. 가상환경 생성 중..."
python3 -m venv venv

if [ $? -ne 0 ]; then
    echo "❌ 가상환경 생성 실패"
    exit 1
fi

echo "✅ 가상환경 생성 완료"
echo ""

# 가상환경 활성화
echo "2. 가상환경 활성화 중..."
source venv/bin/activate

if [ $? -ne 0 ]; then
    echo "❌ 가상환경 활성화 실패"
    exit 1
fi

echo "✅ 가상환경 활성화 완료"
echo ""

# pip 업그레이드
echo "3. pip 업그레이드 중..."
pip install --upgrade pip

echo "✅ pip 업그레이드 완료"
echo ""

# 패키지 설치
echo "4. 필요한 패키지 설치 중..."
pip install -r requirements.txt

if [ $? -ne 0 ]; then
    echo "❌ 패키지 설치 실패"
    exit 1
fi

echo "✅ 패키지 설치 완료"
echo ""

# data 디렉토리 생성
echo "5. 데이터 디렉토리 생성 중..."
mkdir -p data

echo "✅ 데이터 디렉토리 생성 완료"
echo ""

echo "================================"
echo "✅ 설정 완료!"
echo "================================"
echo ""
echo "다음 명령어로 프로그램을 실행하세요:"
echo "  python main.py"
echo ""
echo "또는 가상환경을 먼저 활성화하세요:"
echo "  source venv/bin/activate"
echo "  python main.py"
echo ""


