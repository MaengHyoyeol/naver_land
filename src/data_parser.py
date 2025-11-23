"""
크롤링한 데이터를 파싱하는 모듈
"""

import pandas as pd
import re
from typing import Dict, List, Optional


class DataParser:
    """매물 데이터 파서"""
    
    @staticmethod
    def split_articles(text: str) -> List[str]:
        """
        하나의 텍스트 블록을 개별 매물로 분리
        "집주인" 또는 중개사 이름을 기준으로 분리
        
        Args:
            text (str): 매물 정보 텍스트 블록
            
        Returns:
            List[str]: 개별 매물 리스트
        """
        # "집주인", "공인중개사" 등으로 시작하는 부분을 기준으로 분리
        articles = []
        
        # 줄바꿈으로 분리
        lines = text.split('\n')
        current_article = []
        
        for line in lines:
            line = line.strip()
            if not line:
                continue
            
            # 새 매물 시작 감지
            if '집주인' in line or '공인중개사' in line or line.endswith('동'):
                # 이전 매물이 있으면 저장
                if current_article:
                    articles.append('\n'.join(current_article))
                # 새 매물 시작
                current_article = [line]
            else:
                current_article.append(line)
        
        # 마지막 매물 저장
        if current_article:
            articles.append('\n'.join(current_article))
        
        return articles
    
    @staticmethod
    def parse_article_text(text: str) -> Dict:
        """
        매물 텍스트를 파싱하여 구조화된 데이터로 변환
        
        Args:
            text (str): 매물 정보 텍스트
            
        Returns:
            Dict: 파싱된 데이터
        """
        data = {
            '원문': text
        }
        
        # 필터링: 유효하지 않은 데이터 제외
        if any(keyword in text for keyword in ['전체거래방식', '전체면적', '전체동']):
            return None
        
        # 단지명 추출
        complex_pattern = r'(영등포\s*아트자이|[\w\s]+아파트|[\w\s]+단지)'
        complex_match = re.search(complex_pattern, text)
        if complex_match:
            data['단지명'] = complex_match.group(1).strip()
        
        # 동 정보 추출
        dong_pattern = r'(\d+동)'
        dong_match = re.search(dong_pattern, text)
        if dong_match:
            data['동'] = dong_match.group(1)
        
        # 집주인/중개사 구분
        if '집주인' in text:
            data['구분'] = '집주인 직거래'
        elif '공인중개사' in text or '중개사' in text:
            data['구분'] = '공인중개사'
        
        # 거래 유형 추출
        if '매매' in text:
            data['거래유형'] = '매매'
        elif '전세' in text:
            data['거래유형'] = '전세'
        elif '월세' in text:
            data['거래유형'] = '월세'
        else:
            return None  # 거래유형 없으면 유효하지 않은 데이터
        
        # 가격 추출 개선
        # "매매16억", "매매17억 6,000", "매매18억 5,000~20억" 등
        price_patterns = [
            r'매매\s*(\d+억[\s,0-9~]+(?:억)?)',
            r'전세\s*(\d+억[\s,0-9~]+(?:억)?)',
            r'월세\s*(\d+억[\s,0-9~/]+)',
        ]
        
        for pattern in price_patterns:
            price_match = re.search(pattern, text)
            if price_match:
                price_text = price_match.group(1).strip()
                # 줄바꿈 제거
                price_text = price_text.split('\n')[0].strip()
                data['가격'] = price_text
                break
        
        # 면적 추출 ("149/120m²" 형식 또는 "110C/84m²")
        area_patterns = [
            r'(\d+[A-Z]?)/(\d+)\s*m²',  # "149/120m²" 또는 "110C/84m²"
            r'(\d+\.?\d*)m²',
            r'(\d+\.?\d*)㎡',
        ]
        
        for pattern in area_patterns:
            area_match = re.search(pattern, text)
            if area_match:
                if len(area_match.groups()) > 1:
                    # 공급/전용 면적
                    data['공급면적'] = area_match.group(1) + 'm²'
                    data['전용면적'] = area_match.group(2) + 'm²'
                else:
                    data['전용면적'] = area_match.group(1) + 'm²'
                break
        
        # 층 추출 ("1/31층" 형식)
        floor_pattern = r'(\d+)/(\d+)\s*층'
        floor_match = re.search(floor_pattern, text)
        if floor_match:
            data['층'] = floor_match.group(1) + '층'
            data['총층수'] = floor_match.group(2) + '층'
        else:
            # 단순 "15층" 형식
            simple_floor = re.search(r'(\d+)\s*층', text)
            if simple_floor:
                data['층'] = simple_floor.group(1) + '층'
        
        # 방향 추출
        direction_keywords = ['남향', '북향', '동향', '서향', '남동향', '남서향', '북동향', '북서향']
        for direction in direction_keywords:
            if direction in text:
                data['방향'] = direction
                break
        
        # 확인 날짜 추출
        date_pattern = r'확인매물\s*([\d.]+)'
        date_match = re.search(date_pattern, text)
        if date_match:
            data['확인일'] = date_match.group(1)
        
        # 중개사 수 추출
        broker_pattern = r'중개사(\d+)곳'
        broker_match = re.search(broker_pattern, text)
        if broker_match:
            data['중개사수'] = broker_match.group(1) + '곳'
        
        return data
    
    @staticmethod
    def parse_dataframe(df: pd.DataFrame) -> pd.DataFrame:
        """
        DataFrame의 매물정보를 파싱하여 구조화
        하나의 행에 여러 매물이 있는 경우 분리
        
        Args:
            df (pd.DataFrame): 원본 데이터프레임
            
        Returns:
            pd.DataFrame: 파싱된 데이터프레임
        """
        if df is None or df.empty:
            return df
        
        parsed_data = []
        
        for idx, row in df.iterrows():
            text = row.get('매물정보', '')
            if not text:
                continue
            
            # 하나의 텍스트에서 여러 매물 분리
            articles = DataParser.split_articles(text)
            
            for article_text in articles:
                if not article_text.strip():
                    continue
                
                parsed = DataParser.parse_article_text(article_text)
                
                # 유효한 데이터만 추가 (거래유형이 있는 것만)
                if parsed and parsed.get('거래유형'):
                    parsed_data.append(parsed)
        
        if not parsed_data:
            return pd.DataFrame()
        
        parsed_df = pd.DataFrame(parsed_data)
        
        # 컬럼 순서 정리
        columns_order = [
            '단지명', '동', '거래유형', '가격', '구분',
            '공급면적', '전용면적', '층', '총층수', '방향',
            '확인일', '중개사수', '원문'
        ]
        
        # 존재하는 컬럼만 선택
        existing_columns = [col for col in columns_order if col in parsed_df.columns]
        other_columns = [col for col in parsed_df.columns if col not in existing_columns]
        
        final_columns = existing_columns + other_columns
        parsed_df = parsed_df[final_columns]
        
        # 인덱스 리셋
        parsed_df = parsed_df.reset_index(drop=True)
        parsed_df.insert(0, '순번', range(1, len(parsed_df) + 1))
        
        return parsed_df
    
    @staticmethod
    def get_statistics(df: pd.DataFrame) -> Dict:
        """
        데이터 통계 계산
        
        Args:
            df (pd.DataFrame): 데이터프레임
            
        Returns:
            Dict: 통계 정보
        """
        if df is None or df.empty:
            return {}
        
        stats = {
            '총_매물수': len(df)
        }
        
        # 거래유형별 통계
        if '거래유형' in df.columns:
            type_counts = df['거래유형'].value_counts()
            for trade_type, count in type_counts.items():
                stats[f'{trade_type}_매물수'] = count
        
        # 구분별 통계
        if '구분' in df.columns:
            gubun_counts = df['구분'].value_counts()
            for gubun, count in gubun_counts.items():
                stats[f'{gubun}'] = count
        
        # 동별 통계
        if '동' in df.columns:
            dong_counts = df['동'].value_counts()
            stats['동_개수'] = len(dong_counts)
        
        return stats


if __name__ == "__main__":
    # 테스트 코드
    sample_text = """집주인영등포아트자이 105동
매매16억
아파트149/120m², 1/31층, 남향
15년이내 1층 대형평수 방세개
확인매물 25.11.21.중개사6곳"""
    
    parser = DataParser()
    parsed = parser.parse_article_text(sample_text)
    
    print("파싱 결과:")
    for key, value in parsed.items():
        if value:
            print(f"  {key}: {value}")
