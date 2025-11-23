#!/usr/bin/env python3
"""
네이버 부동산 데이터 수집 메인 프로그램
"""

import sys
import os

# 현재 디렉토리를 Python 경로에 추가
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from src.naver_crawler import NaverRealEstateCrawler


def main():
    """메인 실행 함수"""
    
    print("\n" + "="*80)
    print("  🏠 네이버 부동산 데이터 수집 프로그램")
    print("="*80 + "\n")
    
    # 사용자 입력 받기
    complex_name = input("검색할 단지명을 입력하세요 (예: 영등포 아트자이): ").strip()
    
    if not complex_name:
        print("❌ 단지명을 입력해주세요.")
        return
    
    # 크롤러 초기화
    crawler = NaverRealEstateCrawler(headless=False)
    
    try:
        # 크롤링 실행
        df = crawler.crawl(complex_name)
        
        if df is not None and not df.empty:
            print("\n" + "="*80)
            print("  📊 데이터 미리보기")
            print("="*80)
            print(df.head(10))
            
            # 저장 여부 묻기
            save_choice = input("\n💾 데이터를 파일로 저장하시겠습니까? (y/n): ").strip().lower()
            
            if save_choice == 'y':
                safe_name = complex_name.replace(' ', '_')
                crawler.save_data(df, f"{safe_name}_매물")
            
            print("\n✅ 프로그램 완료!\n")
        else:
            print("\n❌ 크롤링 실패")
    
    except KeyboardInterrupt:
        print("\n\n⚠️  사용자에 의해 중단되었습니다.")
    
    except Exception as e:
        print(f"\n❌ 오류 발생: {e}")
        import traceback
        traceback.print_exc()
    
    finally:
        crawler.close()


if __name__ == "__main__":
    main()
