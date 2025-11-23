#!/usr/bin/env python3
"""
기존 크롤링 데이터를 개선된 파서로 다시 파싱
"""

import sys
import os
import pandas as pd

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from src.data_parser import DataParser
from src.display import DataDisplay


def main():
    """기존 데이터 다시 파싱"""
    
    print("\n" + "="*80)
    print("  🔄 기존 데이터 재파싱")
    print("="*80 + "\n")
    
    # 기존 파일 읽기
    input_file = "data/영등포_아트자이_매물_20251121_164525.csv"
    
    try:
        df_raw = pd.read_csv(input_file)
        print(f"✅ 원본 데이터 로드: {len(df_raw)}개 행")
        
        # 파싱
        parser = DataParser()
        df_parsed = parser.parse_dataframe(df_raw)
        
        print(f"✅ 파싱 완료: {len(df_parsed)}개 매물\n")
        
        # 미리보기
        print("="*80)
        print("  📊 파싱된 데이터 미리보기 (처음 10개)")
        print("="*80)
        print(df_parsed.head(10).to_string())
        
        # 통계
        stats = parser.get_statistics(df_parsed)
        if stats:
            print("\n" + "="*80)
            print("  📈 통계")
            print("="*80)
            for key, value in stats.items():
                print(f"  {key}: {value}")
        
        # 저장
        output_csv = "data/영등포아트자이_파싱완료.csv"
        output_excel = "data/영등포아트자이_파싱완료.xlsx"
        
        df_parsed.to_csv(output_csv, index=False, encoding='utf-8-sig')
        print(f"\n✅ CSV 저장: {output_csv}")
        
        df_parsed.to_excel(output_excel, index=False, engine='openpyxl')
        print(f"✅ Excel 저장: {output_excel}")
        
        # Display로 보기 좋게 출력
        print("\n" + "="*80)
        print("  🎯 거래유형별 데이터")
        print("="*80)
        
        display = DataDisplay()
        
        for trade_type in df_parsed['거래유형'].unique():
            if pd.notna(trade_type):
                df_type = df_parsed[df_parsed['거래유형'] == trade_type]
                display.print_dataframe(df_type.head(5), title=f"{trade_type} 매물 (상위 5개)")
        
        print("\n✅ 재파싱 완료!\n")
        
    except Exception as e:
        print(f"❌ 오류 발생: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()

