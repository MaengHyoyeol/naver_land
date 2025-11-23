#!/usr/bin/env python3
"""
네이버 부동산 크롤러 - 직접 실행 스크립트
"""

import sys
import os

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from src.naver_crawler import NaverRealEstateCrawler
from src.data_parser import DataParser


def main(keyword: str = None):
    """
    메인 실행 함수
    
    Args:
        keyword (str): 검색할 단지명
    """
    
    print("\n" + "="*80)
    print("  🏠 네이버 부동산 데이터 수집")
    print("="*80 + "\n")
    
    # 단지명 설정
    if not keyword:
        if len(sys.argv) > 1:
            keyword = ' '.join(sys.argv[1:])
        else:
            keyword = input("검색할 단지명을 입력하세요: ").strip()
    
    if not keyword:
        print("❌ 단지명을 입력해주세요.")
        return
    
    # 크롤러 초기화 (브라우저 창 보이게)
    crawler = NaverRealEstateCrawler(headless=False)
    
    try:
        # 크롤링 실행
        df = crawler.crawl(keyword)
        
        if df is not None and not df.empty:
            print("\n" + "="*80)
            print("  📊 데이터 미리보기 (처음 10개)")
            print("="*80)
            print(df.head(10).to_string())
            
            # 자동 저장
            safe_name = keyword.replace(' ', '_')
            crawler.save_data(df, f"{safe_name}_매물")
            
            # 데이터 파싱 (선택사항)
            print("\n" + "="*80)
            print("  🔍 데이터 파싱 중...")
            print("="*80)
            
            parser = DataParser()
            parsed_df = parser.parse_dataframe(df)
            
            if not parsed_df.empty:
                print(f"\n파싱된 데이터 미리보기:")
                print(parsed_df.head(10).to_string())
                
                # 파싱된 데이터도 저장
                crawler.save_data(parsed_df, f"{safe_name}_파싱")
                
                # 통계 출력
                stats = parser.get_statistics(parsed_df)
                if stats:
                    print("\n" + "="*80)
                    print("  📈 통계")
                    print("="*80)
                    for key, value in stats.items():
                        print(f"  {key}: {value}")
            
            print("\n✅ 크롤링 완료!\n")
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

