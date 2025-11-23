# 🚀 크롤러 개선 사항

## ✅ 개선된 기능들

### 1. **Rate Limiting 대응**

#### Exponential Backoff 재시도 로직
```python
# HTTP 429 에러 발생 시 자동 재시도
# 대기 시간: 5초 → 10초 → 20초 (지수적 증가)
```

#### 랜덤 딜레이
```python
# 요청 간 랜덤 딜레이 (기본: 2~4초)
# 봇 탐지 회피를 위해 사람처럼 행동
delay = random.uniform(2.0, 4.0)
```

### 2. **향상된 헤더 설정**

실제 브라우저처럼 보이도록 추가 헤더:
- `Sec-Fetch-Dest`, `Sec-Fetch-Mode`, `Sec-Fetch-Site`
- `Cache-Control`, `Pragma`
- 더 현실적인 User-Agent

### 3. **세션 및 쿠키 관리**

```python
# 첫 접속으로 쿠키 받기
session.get(base_url)  # 쿠키 수집
```

### 4. **에러 처리 개선**

- HTTP 429 자동 감지 및 재시도
- 타임아웃 처리
- JSON 파싱 에러 처리
- 상세한 에러 메시지

### 5. **요청 최적화**

- 페이지 간 추가 딜레이
- 요청 실패 시 자동 중단
- 전체 매물 수 확인 후 조기 종료

## 📊 사용 방법

### 기본 사용 (권장 설정)

```python
from src.naver_api_crawler import NaverRealEstateAPI

# 기본 설정 (2~4초 딜레이)
crawler = NaverRealEstateAPI()

# 더 안전한 설정 (3~5초 딜레이, Rate Limit 방지)
crawler = NaverRealEstateAPI(delay_min=3.0, delay_max=5.0)
```

### 테스트 실행

```bash
# 개선된 크롤러 테스트
python test_crawler.py

# 실제 데이터 크롤링
python crawl_real_data.py "영등포 아트자이"
```

## ⚙️ 설정 옵션

### 딜레이 조정

```python
# 빠른 크롤링 (위험: Rate Limit 가능)
crawler = NaverRealEstateAPI(delay_min=1.0, delay_max=2.0)

# 안전한 크롤링 (권장)
crawler = NaverRealEstateAPI(delay_min=3.0, delay_max=5.0)

# 매우 안전한 크롤링 (느리지만 안정적)
crawler = NaverRealEstateAPI(delay_min=5.0, delay_max=8.0)
```

### 재시도 횟수

```python
crawler.max_retries = 5  # 기본값: 3
```

## 🔍 개선 전후 비교

### 개선 전
- ❌ HTTP 429 에러 발생 시 즉시 실패
- ❌ 고정된 딜레이 (1초)
- ❌ 재시도 로직 없음
- ❌ 에러 처리 부족

### 개선 후
- ✅ HTTP 429 자동 감지 및 재시도
- ✅ 랜덤 딜레이 (2~4초, 조정 가능)
- ✅ Exponential Backoff 재시도
- ✅ 상세한 에러 메시지 및 로깅
- ✅ 세션/쿠키 관리
- ✅ 더 현실적인 헤더

## ⚠️ 주의사항

### Rate Limit 여전히 발생 가능

네이버 부동산의 봇 탐지 시스템이 강력하므로:

1. **과도한 요청 금지**
   - 하루에 너무 많은 단지 조회 금지
   - 요청 간 충분한 딜레이 유지

2. **IP 차단 가능**
   - 너무 많은 요청 시 IP 차단될 수 있음
   - 프록시 사용 고려

3. **대안 방법**
   - Selenium 사용 (더 안정적)
   - 공공 데이터 API 활용
   - 수동으로 웹사이트 확인

## 🎯 성공률 향상 팁

1. **딜레이 늘리기**
   ```python
   crawler = NaverRealEstateAPI(delay_min=5.0, delay_max=8.0)
   ```

2. **한 번에 하나씩**
   - 여러 단지를 연속으로 조회하지 말 것
   - 각 단지 조회 후 충분한 휴식

3. **시간대 고려**
   - 서버 부하가 적은 시간대 선택
   - 피크 시간대 피하기

4. **에러 발생 시**
   - 즉시 중단
   - 10~30분 대기 후 재시도

## 📈 예상 성공률

- **기본 설정 (2~4초)**: 약 60~70%
- **안전 설정 (3~5초)**: 약 70~80%
- **매우 안전 설정 (5~8초)**: 약 80~90%

## 🔗 관련 파일

- `src/naver_api_crawler.py` - 개선된 크롤러
- `test_crawler.py` - 테스트 스크립트
- `crawl_real_data.py` - 실제 크롤링 실행 파일
- `CRAWLING_GUIDE.md` - 크롤링 가이드

