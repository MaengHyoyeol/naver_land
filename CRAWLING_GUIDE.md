# 네이버 부동산 실제 크롤링 가이드

## 📋 현재 상태

네이버 부동산은 봇 탐지 시스템으로 보호되고 있어, 직접적인 API 호출이 제한됩니다 (HTTP 429 에러).

## 🔍 실제 크롤링 구현 방법

### 1. Selenium을 사용한 크롤링 (권장)

Selenium을 사용하면 실제 브라우저를 제어하여 데이터를 수집할 수 있습니다.

#### 준비 사항

```bash
# ChromeDriver 설치 (macOS)
brew install chromedriver

# 또는 수동 다운로드
# https://chromedriver.chromium.org/downloads
```

#### 사용 방법

```python
from src.selenium_crawler import SeleniumNaverCrawler

crawler = SeleniumNaverCrawler(headless=True)
try:
    data = crawler.get_full_data("영등포 아트자이")
    if data:
        print("데이터 수집 성공!")
finally:
    crawler.close()
```

### 2. 개발자 도구를 사용한 API 분석

실제 네이버 부동산의 API 엔드포인트를 파악하는 방법:

#### Step 1: 개발자 도구 열기
1. Chrome 브라우저에서 네이버 부동산 접속
2. F12 또는 Cmd+Option+I (Mac) 눌러 개발자 도구 열기
3. "Network" 탭 선택

#### Step 2: API 요청 분석
1. 네이버 부동산에서 단지 검색 (예: "영등포 아트자이")
2. Network 탭에서 XHR 필터 선택
3. API 요청 확인:
   - `/api/search/complexes` - 단지 검색
   - `/api/complexes/{complexNo}` - 단지 상세 정보
   - `/api/complexes/{complexNo}/articles` - 현재 매물
   - `/api/complexes/{complexNo}/prices` - 실거래가

#### Step 3: 요청 헤더 복사
필요한 헤더들:
```
User-Agent: Mozilla/5.0 ...
Accept: application/json
Referer: https://new.land.naver.com/
Cookie: [실제 쿠키 값]
```

### 3. 실제 API 엔드포인트 (참고)

```python
# 단지 검색
GET https://new.land.naver.com/api/search/complexes?keyword={단지명}

# 단지 상세 정보
GET https://new.land.naver.com/api/complexes/{complexNo}

# 현재 매물 목록
GET https://new.land.naver.com/api/complexes/{complexNo}/articles
Parameters:
  - realEstateType: APT
  - tradeType: A1 (매매), B1 (전세), B2 (월세)
  - page: 1
  - size: 20

# 실거래가 정보
GET https://new.land.naver.com/api/complexes/{complexNo}/prices
```

## ⚠️ 주의사항

### 법적 고려사항
1. **이용 약관 준수**: 네이버 부동산의 이용 약관을 반드시 확인하세요
2. **개인적 용도**: 상업적 목적이 아닌 개인 학습/분석용으로만 사용하세요
3. **저작권**: 수집한 데이터의 저작권은 네이버에 있습니다

### 기술적 고려사항
1. **요청 제한**: 과도한 요청은 IP 차단으로 이어질 수 있습니다
2. **딜레이 설정**: 각 요청 사이에 1~2초 딜레이를 두세요
3. **User-Agent**: 실제 브라우저의 User-Agent를 사용하세요
4. **세션 관리**: 쿠키와 세션을 적절히 관리하세요

### Rate Limiting 회피 방법
```python
import time
import random

# 요청 사이에 랜덤 딜레이
time.sleep(random.uniform(1.0, 2.0))

# 요청 실패 시 재시도
max_retries = 3
for i in range(max_retries):
    try:
        response = session.get(url)
        if response.status_code == 200:
            break
        elif response.status_code == 429:
            # Too Many Requests
            wait_time = (2 ** i) * 5  # Exponential backoff
            print(f"Rate limited. Waiting {wait_time} seconds...")
            time.sleep(wait_time)
    except Exception as e:
        print(f"Error: {e}")
        time.sleep(5)
```

## 🛠️ 대안 방법

### 1. 공식 API 사용 (있는 경우)
- 네이버 부동산 공식 API가 제공된다면 사용하세요
- 현재는 공개 API가 없는 것으로 보입니다

### 2. 크롤링 서비스 활용
- Bright Data, Oxylabs 등의 프록시 서비스 활용
- 합법적인 데이터 수집 서비스 이용

### 3. 공공 데이터 활용
- 국토교통부 실거래가 공개시스템 활용
- 공공데이터포털의 부동산 관련 API 사용

## 📚 참고 자료

### 공공 데이터 API
- **국토교통부 실거래가 공개시스템**: http://rtdown.molit.go.kr/
- **공공데이터포털**: https://www.data.go.kr/
  - 아파트매매 실거래가 API
  - 아파트 전월세 자료 API

### 추천 라이브러리
```bash
pip install selenium
pip install beautifulsoup4
pip install requests
pip install pandas
```

## 🔗 유용한 링크

- **영등포아트자이 단지 정보**: https://new.land.naver.com/complexes/116459
- **네이버 부동산 메인**: https://land.naver.com/
- **Selenium 공식 문서**: https://www.selenium.dev/documentation/

## 💡 현재 프로젝트의 데이터

현재 프로젝트에서는 **실제 시세를 반영한 샘플 데이터**를 제공하고 있습니다.

실제 최신 데이터가 필요한 경우:
1. 네이버 부동산 웹사이트에서 직접 확인
2. Selenium을 사용한 자동화 구현
3. 공공 데이터 API 활용

```bash
# 샘플 데이터 생성
python create_realistic_data.py

# Selenium 크롤러 (ChromeDriver 필요)
# python -c "from src.selenium_crawler import SeleniumNaverCrawler; ..."
```

## ⚖️ 면책 조항

본 프로젝트는 교육 목적으로 제작되었습니다. 
- 크롤링으로 인한 법적 문제는 사용자 책임입니다
- 웹사이트의 이용 약관을 반드시 확인하고 준수하세요
- 과도한 크롤링으로 서버에 부담을 주지 마세요


