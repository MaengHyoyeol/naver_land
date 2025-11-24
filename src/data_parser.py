"""
크롤링한 데이터를 파싱하는 모듈
"""

import pandas as pd
import re
from typing import Dict, List, Optional


class DataParser:
    """매물 데이터 파서"""
    
    @staticmethod
    def _is_new_article_line(line: str) -> bool:
        """
        새 매물의 시작을 나타내는 라인인지 판별
        """
        if not line:
            return False
        
        normalized = line.replace(' ', '')
        
        if normalized.startswith('집주인'):
            return True
        
        if re.search(r'\d+\s*동', line):
            return True
        
        return False
    
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
            
            if DataParser._is_new_article_line(line):
                if current_article:
                    articles.append('\n'.join(current_article))
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
            data['단지명'] = re.sub(r'^집주인\s*', '', data['단지명']).strip()
        
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
        
        # 공인중개사무소 이름 추출
        agent_name = None
        for line in text.split('\n'):
            line = line.strip()
            if not line:
                continue
            if '공인중개사' in line and '확인매물' not in line:
                agent_name = line
                break
        if agent_name:
            data['공인중개사무소'] = agent_name
        
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
            data['확인일'] = date_match.group(1).strip().rstrip('.')
        
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
            '확인일', '중개사수', '공인중개사무소', '원문'
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

    @staticmethod
    def calculate_agent_rankings(
        df: pd.DataFrame,
        agent_name: str,
        group_columns: Optional[List[str]] = None
    ) -> pd.DataFrame:
        """
        동일 매물(공급면적/전용면적/층/총층수/방향) 그룹 내에서
        지정한 공인중개사무소의 순위를 계산
        
        Args:
            df (pd.DataFrame): 파싱된 매물 데이터프레임
            agent_name (str): 관심 공인중개사무소 이름(부분 문자열 허용)
            group_columns (List[str], optional): 그룹핑에 사용할 컬럼 목록
        
        Returns:
            pd.DataFrame: 관심 공인중개사무소가 속한 매물과 순위 정보
        """
        if df is None or df.empty or not agent_name:
            return pd.DataFrame()
        
        if group_columns is None:
            group_columns = ['공급면적', '전용면적', '층', '총층수', '방향']
        
        required_columns = set(group_columns + ['공인중개사무소'])
        missing_columns = [col for col in required_columns if col not in df.columns]
        if missing_columns:
            return pd.DataFrame()
        
        # 그룹 기준 컬럼 결측치 처리 (정보없음으로 채움)
        work_df = df.copy()
        for column in group_columns:
            if column not in work_df.columns:
                return pd.DataFrame()
            work_df[column] = work_df[column].fillna('정보없음')
        
        if '공인중개사무소' not in work_df.columns:
            return pd.DataFrame()
        
        # 원본 순서를 유지하여 순위 계산
        if '순번' in work_df.columns:
            work_df = work_df.sort_values('순번')
        else:
            work_df = work_df.reset_index(drop=True)
        
        # 동일 매물 내 순위와 매물 수 계산
        group_obj = work_df.groupby(group_columns, dropna=False)
        size_target = '순번' if '순번' in work_df.columns else group_columns[0]
        work_df['동일매물건수'] = group_obj[size_target].transform('size')
        work_df['같은매물내순위'] = group_obj.cumcount() + 1
        
        # 관심 공인중개사무소 선택 (부분 문자열, 대소문자 무시)
        agent_mask = work_df['공인중개사무소'].fillna('').str.contains(agent_name, case=False)
        agent_df = work_df[agent_mask].copy()
        
        if agent_df.empty:
            return pd.DataFrame()
        
        # 출력 컬럼 구성
        output_columns = [
            '순번', '단지명', '동', '거래유형', '가격',
            *group_columns, '공인중개사무소', '확인일',
            '같은매물내순위', '동일매물건수', '원문'
        ]
        existing_output_columns = [col for col in output_columns if col in agent_df.columns]
        
        result = agent_df[existing_output_columns].reset_index(drop=True)
        return result


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
