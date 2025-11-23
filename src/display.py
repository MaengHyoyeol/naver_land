"""
데이터 출력 모듈
"""

import pandas as pd
from typing import Dict, List
from tabulate import tabulate


class DataDisplay:
    """데이터를 테이블 형태로 출력하는 클래스"""
    
    @staticmethod
    def print_dataframe(df: pd.DataFrame, title: str = "", tablefmt: str = "grid"):
        """
        DataFrame을 보기 좋게 출력
        
        Args:
            df (pd.DataFrame): 출력할 DataFrame
            title (str): 테이블 제목
            tablefmt (str): 테이블 포맷 (grid, simple, pretty, etc.)
        """
        if df.empty:
            print(f"\n{title}")
            print("  데이터가 없습니다.")
            return
        
        print(f"\n{'='*80}")
        print(f"  {title}")
        print(f"{'='*80}")
        
        # tabulate를 사용하여 테이블 출력
        print(tabulate(df, headers='keys', tablefmt=tablefmt, showindex=False))
        print(f"{'='*80}\n")
    
    @staticmethod
    def print_dict(data: Dict, title: str = ""):
        """
        딕셔너리를 보기 좋게 출력
        
        Args:
            data (Dict): 출력할 딕셔너리
            title (str): 제목
        """
        if not data:
            print(f"\n{title}")
            print("  데이터가 없습니다.")
            return
        
        print(f"\n{'='*80}")
        print(f"  {title}")
        print(f"{'='*80}")
        
        for key, value in data.items():
            print(f"  {key:15s}: {value}")
        
        print(f"{'='*80}\n")
    
    @staticmethod
    def print_all_dataframes(dataframes: Dict[str, pd.DataFrame]):
        """
        여러 DataFrame을 순서대로 출력
        
        Args:
            dataframes (Dict[str, pd.DataFrame]): 테이블명: DataFrame 딕셔너리
        """
        if not dataframes:
            print("\n출력할 데이터가 없습니다.")
            return
        
        print("\n" + "="*80)
        print("  네이버 부동산 데이터 조회 결과")
        print("="*80)
        
        for table_name, df in dataframes.items():
            DataDisplay.print_dataframe(df, title=table_name)
    
    @staticmethod
    def print_statistics(stats: Dict, title: str = "통계"):
        """
        통계 정보 출력
        
        Args:
            stats (Dict): 통계 딕셔너리
            title (str): 제목
        """
        DataDisplay.print_dict(stats, title=title)
    
    @staticmethod
    def save_to_excel(dataframes: Dict[str, pd.DataFrame], filename: str):
        """
        여러 DataFrame을 Excel 파일의 각 시트로 저장
        
        Args:
            dataframes (Dict[str, pd.DataFrame]): 시트명: DataFrame 딕셔너리
            filename (str): 저장할 파일명
        """
        try:
            with pd.ExcelWriter(filename, engine='openpyxl') as writer:
                for sheet_name, df in dataframes.items():
                    if not df.empty:
                        df.to_excel(writer, sheet_name=sheet_name, index=False)
            
            print(f"✅ 데이터가 '{filename}' 파일로 저장되었습니다.")
            
        except Exception as e:
            print(f"❌ 파일 저장 실패: {e}")
    
    @staticmethod
    def save_to_csv(df: pd.DataFrame, filename: str):
        """
        DataFrame을 CSV 파일로 저장
        
        Args:
            df (pd.DataFrame): 저장할 DataFrame
            filename (str): 저장할 파일명
        """
        try:
            df.to_csv(filename, index=False, encoding='utf-8-sig')
            print(f"✅ 데이터가 '{filename}' 파일로 저장되었습니다.")
            
        except Exception as e:
            print(f"❌ 파일 저장 실패: {e}")
    
    @staticmethod
    def print_summary(dataframes: Dict[str, pd.DataFrame]):
        """
        데이터 요약 정보 출력
        
        Args:
            dataframes (Dict[str, pd.DataFrame]): 테이블 딕셔너리
        """
        print("\n" + "="*80)
        print("  📊 데이터 요약")
        print("="*80)
        
        for table_name, df in dataframes.items():
            if not df.empty:
                print(f"  {table_name}: {len(df)}개 레코드")
        
        print("="*80 + "\n")


if __name__ == "__main__":
    # 테스트 코드
    print("DataDisplay 모듈 테스트")
    
    # 샘플 데이터
    sample_df = pd.DataFrame({
        '단지명': ['영등포 아트자이'],
        '주소': ['서울시 영등포구'],
        '세대수': [1200],
        '준공년도': [2020]
    })
    
    display = DataDisplay()
    display.print_dataframe(sample_df, title="테스트 테이블")
    
    sample_dict = {
        '최고가': '15억',
        '최저가': '10억',
        '평균가': '12.5억'
    }
    display.print_dict(sample_dict, title="가격 통계")


