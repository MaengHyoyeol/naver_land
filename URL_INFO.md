# 네이버 부동산 URL 구조

## 실제 URL 구조

### 메인 페이지
- **정식 URL**: `https://land.naver.com/` ✅
- 사용자가 지적한 대로 이것이 실제 메인 페이지입니다.

### API 및 단지 페이지
- **API 서버**: `https://new.land.naver.com/api/...`
- **단지 페이지**: `https://new.land.naver.com/complexes/{번호}`
- test.ipynb의 실제 작동 코드에서 사용하는 URL입니다.

## URL 사용 전략

1. **메인 페이지 접속**: `land.naver.com` 사용 (쿠키 수집)
2. **API 호출**: `new.land.naver.com/api/...` 사용
3. **단지 페이지**: `new.land.naver.com/complexes/{번호}` 사용

## 404 에러 해결

404 에러가 발생하는 경우:
1. 단지번호가 잘못되었을 수 있음
2. URL 형식이 변경되었을 수 있음
3. 봇 탐지로 차단되었을 수 있음

## 참고

- 실제 네이버 부동산 메인: https://land.naver.com/
- test.ipynb의 실제 작동 코드는 `new.land.naver.com` 사용

