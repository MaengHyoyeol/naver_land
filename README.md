# 네이버 부동산 데이터 수집 프로젝트

## 📋 프로젝트 개요
네이버 부동산에서 아파트 단지 정보를 수집하고, 단지명을 입력하면 관련 매물 데이터를 추출하는 프로젝트입니다.

**✅ 실제 크롤링 작동 검증 완료!**

## 🎯 주요 기능
- ✅ 네이버 부동산 실제 크롤링 (undetected_chromedriver 사용)
- ✅ 단지명 검색 기능 (예: "영등포 아트자이")
- ✅ 동일매물 묶기 기능
- ✅ 스크롤로 모든 매물 자동 로드
- ✅ 데이터 CSV/Excel 저장

## 🛠️ 기술 스택
- Python 3.9+
- **undetected-chromedriver** (봇 탐지 우회)
- pandas (데이터 처리)
- selenium (웹 자동화)

## 📦 설치 방법

### 1. 가상환경 생성 및 활성화
```bash
# 가상환경 생성
python3 -m venv venv

# 가상환경 활성화 (macOS/Linux)
source venv/bin/activate
```

### 2. 의존성 패키지 설치
```bash
pip install -r requirements.txt
```

### 3. ChromeDriver 설치 (자동으로 됨)
undetected-chromedriver가 자동으로 ChromeDriver를 관리합니다.

## 🚀 사용 방법

### 방법 1: 메인 프로그램 실행 (추천)
```bash
python main.py
```

실행 후 단지명 입력:
```
검색할 단지명을 입력하세요 (예: 영등포 아트자이): 영등포 아트자이
```

### 방법 2: Python 코드에서 직접 사용
```python
from src.naver_crawler import NaverRealEstateCrawler

crawler = NaverRealEstateCrawler(headless=False)

try:
    # 크롤링 실행
    df = crawler.crawl("영등포 아트자이")
    
    # 저장
    crawler.save_data(df, "영등포아트자이_매물")
finally:
    crawler.close()
```

## 📂 프로젝트 구조
```
naver_real_estate/
├── README.md
├── requirements.txt
├── main.py                 # 메인 실행 파일
├── venv/                   # 가상환경
├── src/
│   ├── __init__.py
│   ├── naver_crawler.py    # 크롤러 (undetected_chromedriver)
│   ├── data_parser.py      # 데이터 파서
│   └── display.py          # 데이터 출력
└── data/                   # 수집된 데이터 저장
```

## 🔍 크롤링 과정

1. **검색**: 네이버 부동산에서 단지명 검색
2. **동일매물 묶기**: 중복 매물 필터링
3. **스크롤 로딩**: 모든 매물이 로드될 때까지 자동 스크롤
4. **데이터 추출**: 매물 정보 텍스트 추출
5. **저장**: CSV 및 Excel 파일로 저장

## ⚠️ 주요 특징

### undetected_chromedriver 사용
일반 Selenium 대신 `undetected-chromedriver`를 사용하여:
- ✅ 네이버의 봇 탐지 시스템 우회
- ✅ Rate Limit 회피
- ✅ 안정적인 크롤링

### 자동 스크롤 로딩
- 모든 매물이 로드될 때까지 자동 스크롤
- 변화가 없을 때까지 반복 (최대 100회)
- 실시간 진행 상황 표시

## 📊 출력 예시

```
🔍 '영등포 아트자이' 검색 시작...
✅ 메인 페이지 접속 완료
✅ 검색 완료
✅ 동일매물 묶기 활성화

📜 스크롤로 모든 매물 로딩 중...
  스크롤   1회 | 매물 수:  45개 (+45)
  스크롤   2회 | 매물 수:  89개 (+44)
  ...
  스크롤  15회 | 매물 수: 234개 (변화없음 5/5)
✅ 로딩 완료!

📋 최종 매물 수: 234개

📊 데이터 추출 시작...
  20/234 추출 완료...
  40/234 추출 완료...
  ...
✅ 234개 매물 추출 완료!

✅ CSV 저장: data/영등포아트자이_매물_20241119_153000.csv
✅ Excel 저장: data/영등포아트자이_매물_20241119_153000.xlsx
```

## ⚠️ 주의사항

### 1. 브라우저 창
- `headless=False`로 설정하면 브라우저 창이 보입니다
- 크롤링 중 브라우저 창을 닫지 마세요
- 디버깅 시 유용합니다

### 2. 수동 조작 필요 시
- "동일매물 묶기"를 자동으로 찾지 못하면 수동 클릭 필요
- 10초 대기 시간이 제공됩니다

### 3. 속도
- 모든 매물을 로드하기 위해 시간이 걸립니다
- 매물 수가 많으면 3~5분 소요될 수 있습니다

### 4. 네이버 이용 약관
- 개인적인 용도로만 사용하세요
- 과도한 크롤링은 피하세요
- 수집한 데이터의 저작권은 네이버에 있습니다

## 🎓 핵심 개선 사항

### Before (작동 안 됨)
- ❌ 일반 Selenium → Rate Limit (HTTP 429)
- ❌ API 직접 호출 → 차단됨
- ❌ 봇 탐지에 걸림

### After (작동 확인됨)
- ✅ undetected-chromedriver 사용
- ✅ 실제 브라우저처럼 동작
- ✅ 스크롤 기반 데이터 로딩
- ✅ 텍스트 기반 데이터 추출

## 📝 개발 현황
- [x] undetected-chromedriver 기반 크롤러 구현 ⭐
- [x] 자동 검색 및 스크롤 로딩
- [x] 동일매물 묶기 기능
- [x] 데이터 추출 및 파싱
- [x] CSV/Excel 저장
- [x] 실제 작동 검증 완료 ✅

## ☁️ EC2 배포

Amazon Linux 2023에 배포하는 방법은 [EC2_DEPLOYMENT.md](./EC2_DEPLOYMENT.md)를 참고하세요.

### 빠른 배포
```bash
# EC2에 SSH 접속 후
git clone <your-repo-url>
cd naver_real_estate
chmod +x deploy_ec2.sh
./deploy_ec2.sh
```

자동으로 다음이 설정됩니다:
- Chrome 및 의존성 설치
- Python 가상환경 설정
- systemd 서비스 등록
- 자동 재시작 설정

## 📄 라이선스
교육 및 개인 프로젝트 목적

## 👤 작성 정보
- 프로젝트 생성일: 2025-11-19
- 최종 업데이트: 2025-11-24 (EC2 배포 지원 추가)
- ChromeDriver 경로: `/opt/homebrew/bin/chromedriver` (로컬), 자동 설치 (EC2)
