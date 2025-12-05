#!/usr/bin/env python3
"""
네이버 부동산 크롤러 웹 GUI
Streamlit 기반 웹 인터페이스
"""

import streamlit as st
import pandas as pd
import sys
import os
from datetime import datetime
import time
import re

# 프로젝트 경로 추가
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from src.naver_crawler import NaverRealEstateCrawler
from src.data_parser import DataParser
from src.display import DataDisplay


# 페이지 설정
st.set_page_config(
    page_title="네이버 부동산 크롤러",
    page_icon="🏠",
    layout="wide",
    initial_sidebar_state="expanded"
)

# CSS 스타일
st.markdown("""
<style>
    /* 텍스트 선택 허용 */
    * {
        -webkit-user-select: text !important;
        -moz-user-select: text !important;
        -ms-user-select: text !important;
        user-select: text !important;
    }
    
    .main-header {
        font-size: 2.5rem;
        font-weight: bold;
        color: #1f77b4;
        text-align: center;
        margin-bottom: 2rem;
    }
    .stButton>button {
        width: 100%;
        background-color: #1f77b4;
        color: white;
        font-weight: bold;
    }
    .success-box {
        padding: 1rem;
        border-radius: 0.5rem;
        background-color: #d4edda;
        border: 1px solid #c3e6cb;
        margin: 1rem 0;
    }
</style>
""", unsafe_allow_html=True)


def log_app(message: str) -> None:
    """앱 레벨 로그 출력 (타임스탬프 포함)"""
    ts = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    print(f"[APP][{ts}] {message}", flush=True)


def main():
    """메인 앱"""
    
    # 헤더
    st.markdown('<div class="main-header">🏠 네이버 부동산 데이터 수집</div>', unsafe_allow_html=True)
    
    # 사이드바
    with st.sidebar:
        st.header("⚙️ 설정")
        
        headless_mode = st.checkbox("헤드리스 모드 (브라우저 숨김)", value=True)
        
        st.markdown("---")
        st.markdown("### 📊 기능")
        st.markdown("""
        - 단지명 검색
        - 자동 매물 수집
        - 데이터 파싱
        - 결과 다운로드
        """)
        
        st.markdown("---")
        st.markdown("### ℹ️ 정보")
        st.markdown("""
        **버전**: v2.1.3  
        **브랜치**: develop
        """)
    
    # 메인 영역
    tab1, tab2, tab3 = st.tabs(["🔍 크롤링", "📊 데이터 분석", "📁 파일 관리"])
    
    with tab1:
        st.header("단지 검색 및 크롤링")
        
        # 검색 입력
        col1, col2 = st.columns([3, 1])
        
        with col1:
            keyword = st.text_input(
                "검색할 단지명을 입력하세요",
                placeholder="예: 영등포 아트자이",
                key="search_keyword"
            )
        
        with col2:
            st.write("")  # 공간 맞추기
            search_button = st.button("🔍 검색 및 크롤링", type="primary", use_container_width=True)
        
        # 크롤링 실행
        if search_button:
            if not keyword:
                st.error("❌ 단지명을 입력해주세요.")
            else:
                # 이전 크롤러가 있으면 닫기
                if 'crawler' in st.session_state and st.session_state.crawler:
                    try:
                        st.session_state.crawler.close()
                    except:
                        pass
                
                with st.spinner(f"'{keyword}' 크롤링 중... (1~3분 소요)"):
                    # 진행 상황 표시
                    progress_bar = st.progress(0)
                    status_text = st.empty()
                    
                    # 크롤러 초기화
                    crawler = NaverRealEstateCrawler(headless=headless_mode)
                    st.session_state.crawler = crawler
                    
                    try:
                        status_text.text("🔍 검색 중...")
                        progress_bar.progress(10)
                        
                        # crawl() 메서드 사용 (전체 프로세스)
                        df_raw = crawler.crawl(keyword)
                        
                        progress_bar.progress(100)
                        status_text.text("✅ 완료!")
                        
                        if df_raw is not None and not df_raw.empty:
                            # 세션에 데이터 저장
                            st.session_state.df_raw = df_raw
                            st.session_state.keyword = keyword
                            
                            # 성공 메시지
                            st.success(f"✅ {len(df_raw)}개 매물 수집 완료!")
                        else:
                            st.warning("⚠️ 수집된 데이터가 없습니다. 다시 시도해주세요.")
                            # 세션 데이터 초기화
                            if 'df_raw' in st.session_state:
                                del st.session_state.df_raw
                        
                    except Exception as e:
                        st.error(f"❌ 오류 발생: {e}")
                        import traceback
                        with st.expander("상세 오류 정보"):
                            st.code(traceback.format_exc())
                        
                        # 세션 데이터 초기화
                        if 'df_raw' in st.session_state:
                            del st.session_state.df_raw
                    finally:
                        # 크롤러는 세션에 유지 (나중에 닫기)
                        pass
        
        # 수집된 데이터 표시
        if 'df_raw' in st.session_state and st.session_state.df_raw is not None:
            st.markdown("---")
            st.subheader("📋 수집된 데이터")
            
            df_raw = st.session_state.df_raw
            
            if not df_raw.empty:
                # 데이터 미리보기
                st.markdown("#### 🏠 매물 데이터")
                st.dataframe(df_raw.head(20), use_container_width=True)
                st.info(f"📊 총 {len(df_raw)}개 매물이 수집되었습니다.")
                
                # 파싱 버튼
                # 이미 파싱된 데이터가 있으면 파싱 버튼을 표시하지 않음
                if 'df_parsed' not in st.session_state or st.session_state.df_parsed is None:
                    if st.button("🔍 데이터 파싱", use_container_width=True, type="primary"):
                        start_time = time.time()
                        log_app(f"데이터 파싱 시작 - 원본 행 수: {len(df_raw)}")
                        with st.spinner("데이터 파싱 중..."):
                            parser = DataParser()
                            try:
                                df_parsed = parser.parse_dataframe(df_raw)
                            except Exception as e:
                                elapsed = time.time() - start_time
                                log_app(f"데이터 파싱 중 예외 발생 (경과 {elapsed:.2f}s): {e}")
                                raise
                        
                        elapsed = time.time() - start_time
                        if df_parsed is not None and not df_parsed.empty:
                            st.session_state.df_parsed = df_parsed
                            log_app(
                                f"데이터 파싱 완료 - 파싱된 행 수: {len(df_parsed)}, 경과 시간: {elapsed:.2f}s"
                            )
                            st.success(f"✅ {len(df_parsed)}개 매물 파싱 완료! (소요 시간: {elapsed:.1f}초)")
                            log_app("페이지 새로고침 시작 (st.rerun 호출)")
                            st.rerun()  # 페이지 새로고침하여 분석 탭에 표시
                        else:
                            log_app(f"데이터 파싱 결과 없음 - 경과 시간: {elapsed:.2f}s")
                            st.warning("⚠️ 파싱된 데이터가 없습니다.")
                else:
                    st.info("✅ 데이터가 이미 파싱되었습니다. '📊 데이터 분석' 탭에서 확인하세요.")
                
                # 단지 추가검색 섹션
                st.markdown("---")
                st.subheader("➕ 단지 추가검색")
                st.info("현재 데이터에 다른 단지의 매물을 추가로 수집할 수 있습니다.")
                
                col1, col2 = st.columns([3, 1])
                
                with col1:
                    additional_keyword = st.text_input(
                        "추가 검색할 단지명을 입력하세요",
                        placeholder="예: 래미안 아파트",
                        key="additional_search_keyword"
                    )
                
                with col2:
                    st.write("")  # 공간 맞추기
                    additional_search_button = st.button("➕ 추가 검색", type="primary", use_container_width=True)
                
                if additional_search_button:
                    if not additional_keyword:
                        st.error("❌ 추가 검색할 단지명을 입력해주세요.")
                    else:
                        with st.spinner(f"'{additional_keyword}' 추가 크롤링 중... (1~3분 소요)"):
                            # 진행 상황 표시
                            additional_progress_bar = st.progress(0)
                            additional_status_text = st.empty()
                            
                            # 기존 크롤러가 있으면 사용, 없으면 새로 생성
                            if 'crawler' not in st.session_state or st.session_state.crawler is None:
                                crawler = NaverRealEstateCrawler(headless=headless_mode)
                                st.session_state.crawler = crawler
                            else:
                                crawler = st.session_state.crawler
                            
                            try:
                                additional_status_text.text(f"🔍 '{additional_keyword}' 검색 중...")
                                additional_progress_bar.progress(10)
                                
                                # 추가 크롤링 실행
                                df_additional = crawler.crawl(additional_keyword)
                                
                                additional_progress_bar.progress(70)
                                additional_status_text.text("📊 데이터 처리 중...")
                                
                                if df_additional is not None and not df_additional.empty:
                                    # 기존 데이터와 병합
                                    # 순번 재설정
                                    existing_count = len(df_raw)
                                    df_additional = df_additional.copy()
                                    df_additional['순번'] = range(existing_count + 1, existing_count + 1 + len(df_additional))
                                    
                                    # 원본 데이터 병합
                                    df_merged = pd.concat([df_raw, df_additional], ignore_index=True)
                                    
                                    # 세션에 업데이트된 원본 데이터 저장
                                    st.session_state.df_raw = df_merged
                                    if 'keyword' in st.session_state:
                                        existing_keywords = st.session_state.keyword.split(', ') if ', ' in st.session_state.keyword else [st.session_state.keyword]
                                        if additional_keyword not in existing_keywords:
                                            st.session_state.keyword = ', '.join(existing_keywords + [additional_keyword])
                                    else:
                                        st.session_state.keyword = additional_keyword
                                    
                                    # 추가 데이터 자동 파싱
                                    additional_status_text.text("🔍 추가 데이터 파싱 중...")
                                    additional_progress_bar.progress(85)
                                    
                                    parser = DataParser()
                                    df_additional_parsed = parser.parse_dataframe(df_additional)
                                    
                                    if not df_additional_parsed.empty:
                                        # 기존 파싱 데이터와 병합
                                        if 'df_parsed' in st.session_state and st.session_state.df_parsed is not None:
                                            df_parsed_merged = pd.concat([st.session_state.df_parsed, df_additional_parsed], ignore_index=True)
                                            st.session_state.df_parsed = df_parsed_merged
                                        else:
                                            # 기존 파싱 데이터가 없으면 새로 생성
                                            st.session_state.df_parsed = df_additional_parsed
                                        
                                        additional_progress_bar.progress(100)
                                        additional_status_text.text("✅ 모든 작업 완료!")
                                        
                                        # 성공 메시지
                                        st.success(f"✅ '{additional_keyword}' 추가 검색 완료! ({len(df_additional)}개 매물 추가, 총 {len(df_merged)}개, 파싱 완료: {len(df_additional_parsed)}개)")
                                    else:
                                        additional_progress_bar.progress(100)
                                        additional_status_text.text("⚠️ 파싱 경고")
                                        st.warning(f"⚠️ '{additional_keyword}' 추가 검색 완료! ({len(df_additional)}개 매물 추가, 총 {len(df_merged)}개) 단, 파싱된 데이터가 없습니다.")
                                        # 파싱 실패해도 원본 데이터는 병합됨
                                    
                                    # 추가 검색 결과를 기존 데이터 아래에 표시
                                    st.markdown("---")
                                    st.markdown(f"#### ➕ '{additional_keyword}' 추가 검색 결과")
                                    st.dataframe(df_additional.head(20), use_container_width=True)
                                    st.info(f"📊 추가된 매물: {len(df_additional)}개")
                                else:
                                    additional_progress_bar.progress(100)
                                    additional_status_text.text("⚠️ 데이터 없음")
                                    st.error(f"❌ **'{additional_keyword}' 추가 검색 실패**\n\n"
                                            f"⚠️ 추가 검색된 데이터가 없습니다.\n"
                                            f"단지명을 확인하거나 다시 시도해주세요.")
                                    
                            except Exception as e:
                                additional_progress_bar.progress(100)
                                additional_status_text.text("❌ 오류 발생")
                                st.error(f"❌ **'{additional_keyword}' 추가 검색 오류 발생**\n\n"
                                        f"오류 내용: {e}")
                                import traceback
                                with st.expander("상세 오류 정보"):
                                    st.code(traceback.format_exc())
            else:
                st.warning("⚠️ 수집된 데이터가 비어있습니다.")
    
    with tab2:
        st.header("데이터 분석")
        
        if 'df_parsed' in st.session_state and st.session_state.df_parsed is not None:
            log_app("데이터 분석 탭 렌더링 시작")
            tab2_start = time.time()
            df = st.session_state.df_parsed
            log_app(f"데이터프레임 로드 완료 - 행 수: {len(df)}, 경과: {time.time() - tab2_start:.2f}s")
            
            # 통계
            col1, col2, col3, col4 = st.columns(4)
            
            with col1:
                st.metric("총 매물수", len(df))
            
            with col2:
                if '거래유형' in df.columns:
                    sale_count = len(df[df['거래유형'] == '매매']) if '매매' in df['거래유형'].values else 0
                    st.metric("매매", sale_count)
            
            with col3:
                if '거래유형' in df.columns:
                    rent_count = len(df[df['거래유형'] == '전세']) if '전세' in df['거래유형'].values else 0
                    st.metric("전세", rent_count)
            
            with col4:
                if '거래유형' in df.columns:
                    monthly_count = len(df[df['거래유형'] == '월세']) if '월세' in df['거래유형'].values else 0
                    st.metric("월세", monthly_count)
            
            st.markdown("---")
            
            # 필터
            log_app("필터 섹션 렌더링 시작")
            filter_start = time.time()
            st.subheader("🔍 필터")
            col1, col2, col3, col4, col5, col6 = st.columns(6)
            
            with col1:
                if '거래유형' in df.columns:
                    trade_types = ['전체'] + list(df['거래유형'].dropna().unique())
                    selected_type = st.selectbox("거래유형", trade_types)
                else:
                    selected_type = '전체'
            
            with col2:
                if '동' in df.columns:
                    # 동 숫자 정렬 함수
                    def extract_dong_num(x):
                        try:
                            if isinstance(x, str):
                                num_match = re.findall(r'\d+', x)
                                return int(num_match[0]) if num_match else 999
                            else:
                                return 999
                        except:
                            return 999
                    
                    unique_dongs = df['동'].dropna().unique()
                    sorted_dongs = sorted(unique_dongs, key=extract_dong_num)
                    dongs = ['전체'] + list(sorted_dongs)
                    selected_dong = st.selectbox("동", dongs)
                else:
                    selected_dong = '전체'
            
            with col3:
                if '층' in df.columns:
                    # 층 숫자 정렬 함수
                    def extract_floor_num(x):
                        try:
                            if isinstance(x, str):
                                # "저층", "중층", "고층" 처리
                                if '저층' in x or x == '저':
                                    return 0
                                elif '중층' in x or x == '중':
                                    return 500
                                elif '고층' in x or x == '고':
                                    return 1000
                                # 숫자 추출
                                num_match = re.findall(r'\d+', x)
                                return int(num_match[0]) if num_match else 999
                            else:
                                return 999
                        except:
                            return 999
                    
                    unique_floors = df['층'].dropna().unique()
                    sorted_floors = sorted(unique_floors, key=extract_floor_num)
                    floors = ['전체'] + list(sorted_floors)
                    selected_floor = st.selectbox("층", floors)
                else:
                    selected_floor = '전체'
            
            with col4:
                if '전용면적' in df.columns:
                    # 전용면적 정렬을 위한 함수
                    def extract_area_num(x):
                        try:
                            if isinstance(x, str):
                                num_str = x.replace('㎡', '').replace('m²', '').strip()
                                return float(num_str)
                            elif isinstance(x, (int, float)):
                                return float(x)
                            else:
                                return 999.0
                        except:
                            return 999.0
                    
                    unique_areas = df['전용면적'].dropna().unique()
                    sorted_areas = sorted(unique_areas, key=extract_area_num)
                    areas = ['전체'] + list(sorted_areas)
                    selected_area = st.selectbox("전용면적", areas)
                else:
                    selected_area = '전체'
            
            with col5:
                if '확인일' in df.columns:
                    dates = ['전체'] + sorted(df['확인일'].dropna().unique())
                    selected_date = st.selectbox("확인일", dates)
                else:
                    selected_date = '전체'
            
            with col6:
                if '공인중개사무소' in df.columns:
                    agents = ['전체'] + list(df['공인중개사무소'].dropna().unique())
                    selected_agent = st.selectbox("공인중개사무소", agents)
                else:
                    selected_agent = '전체'
            
            # 필터링
            log_app(f"필터 UI 생성 완료 - 경과: {time.time() - filter_start:.2f}s")
            filter_process_start = time.time()
            df_filtered = df.copy()
            original_count = len(df_filtered)
            
            if selected_type != '전체':
                df_filtered = df_filtered[df_filtered['거래유형'] == selected_type]
            if selected_dong != '전체':
                df_filtered = df_filtered[df_filtered['동'] == selected_dong]
            if selected_floor != '전체':
                df_filtered = df_filtered[df_filtered['층'] == selected_floor]
            if selected_area != '전체':
                df_filtered = df_filtered[df_filtered['전용면적'] == selected_area]
            if selected_date != '전체':
                df_filtered = df_filtered[df_filtered['확인일'] == selected_date]
            if selected_agent != '전체':
                df_filtered = df_filtered[df_filtered['공인중개사무소'] == selected_agent]
            
            filtered_count = len(df_filtered)
            log_app(f"필터링 완료 - 필터링 후: {filtered_count}개, 경과: {time.time() - filter_process_start:.2f}s")

            # 동일 매물 중 최신 확인일만 유지
            # 같은 매물 제거 기준: 동, 층, 총층수, 거래유형, 전용면적, 공급면적이 모두 같은 경우
            dedup_start = time.time()
            dedup_key = ['동', '층', '총층수', '거래유형', '전용면적', '공급면적', '공인중개사무소', '광고사']
            if all(col in df_filtered.columns for col in dedup_key) and '확인일' in df_filtered.columns:
                before_dedup_count = len(df_filtered)
                df_dedup = df_filtered.copy()
                parsed_dates = pd.to_datetime(
                    df_dedup['확인일'].astype(str).str.replace('.', '-', regex=False),
                    format='%y-%m-%d',
                    errors='coerce'
                )
                df_dedup['_확인일_dt'] = parsed_dates
                df_dedup = df_dedup.sort_values('_확인일_dt', ascending=False)
                df_dedup = df_dedup.drop_duplicates(subset=dedup_key, keep='first')
                df_dedup = df_dedup.drop(columns=['_확인일_dt'])
                df_filtered = df_dedup.reset_index(drop=True)
                after_dedup_count = len(df_filtered)
            else:
                before_dedup_count = filtered_count
                after_dedup_count = filtered_count
            
            log_app(f"중복 제거 완료 - 제거 후: {after_dedup_count}개, 경과: {time.time() - dedup_start:.2f}s")
            log_app(f"데이터 분석 탭 전체 렌더링 완료 - 총 경과: {time.time() - tab2_start:.2f}s")
            
            st.markdown("---")
            st.subheader("📊 필터링된 데이터")
            
            # 필터링 정보 표시
            filter_info = []
            if selected_type != '전체':
                filter_info.append(f"거래유형: {selected_type}")
            if selected_dong != '전체':
                filter_info.append(f"동: {selected_dong}")
            if selected_floor != '전체':
                filter_info.append(f"층: {selected_floor}")
            if selected_area != '전체':
                filter_info.append(f"전용면적: {selected_area}")
            if selected_date != '전체':
                filter_info.append(f"확인일: {selected_date}")
            if selected_agent != '전체':
                filter_info.append(f"공인중개사무소: {selected_agent}")
            
            if filter_info:
                st.info(f"🔍 적용된 필터: {', '.join(filter_info)} | 필터링 후: {filtered_count}개 → 중복 제거 후: {after_dedup_count}개 (전체: {original_count}개)")
            else:
                st.info(f"📊 전체 데이터: {original_count}개 → 중복 제거 후: {after_dedup_count}개")
            # 순번 컬럼 제거
            if '순번' in df_filtered.columns:
                df_filtered = df_filtered.drop(columns=['순번'])
            
            # 필터링된 데이터 정렬: 거래유형, 동, 층, 총층수, 전용면적 순서
            sort_columns = []
            temp_sort_cols = []
            
            if '거래유형' in df_filtered.columns:
                sort_columns.append('거래유형')
            
            if '동' in df_filtered.columns:
                df_filtered['_sort_dong'] = df_filtered['동'].astype(str).apply(
                    lambda x: int(re.findall(r'\d+', x)[0]) if re.findall(r'\d+', x) else 999
                )
                sort_columns.append('_sort_dong')
                temp_sort_cols.append('_sort_dong')
            
            if '층' in df_filtered.columns:
                df_filtered['_sort_floor'] = df_filtered['층'].astype(str).apply(
                    lambda x: int(re.findall(r'\d+', x)[0]) if re.findall(r'\d+', x) else 999
                )
                sort_columns.append('_sort_floor')
                temp_sort_cols.append('_sort_floor')
            
            if '총층수' in df_filtered.columns:
                df_filtered['_sort_total_floor'] = df_filtered['총층수'].astype(str).apply(
                    lambda x: int(re.findall(r'\d+', x)[0]) if re.findall(r'\d+', x) else 999
                )
                sort_columns.append('_sort_total_floor')
                temp_sort_cols.append('_sort_total_floor')
            
            if '전용면적' in df_filtered.columns:
                df_filtered['_sort_area'] = df_filtered['전용면적'].astype(str).apply(
                    lambda x: float(re.findall(r'\d+\.?\d*', x)[0]) if re.findall(r'\d+\.?\d*', x) else 0
                )
                sort_columns.append('_sort_area')
                temp_sort_cols.append('_sort_area')
            
            # 정렬 실행
            if sort_columns:
                df_filtered = df_filtered.sort_values(sort_columns, ascending=[True] * len(sort_columns))
                # 정렬용 임시 컬럼 제거
                df_filtered = df_filtered.drop(columns=[col for col in temp_sort_cols if col in df_filtered.columns])
            
            preferred_order = [
                '거래유형', '동', '층', '층구분', '전용면적',
                '단지명', '총층수', '가격', '공급면적',
                '확인일', '공인중개사무소', '광고사', '원문', '구분'
            ]
            display_cols = [col for col in preferred_order if col in df_filtered.columns]
            if display_cols:
                st.dataframe(df_filtered[display_cols], use_container_width=True)
            else:
                st.dataframe(df_filtered, use_container_width=True)
            
            st.markdown("---")
            st.subheader("🏅 내 공인중개사 순위")
            agent_input = st.text_area(
                "내 공인중개사무소 이름을 입력하세요 (여러 개 입력 가능, 한 줄에 하나씩 또는 쉼표로 구분)",
                value="국민공인중개사사무소\n중동역래미안어반비스타공인중개사사무소",
                placeholder="예:\n영등포아트자이공인중개사사무소\n래미안탑부동산공인중개사사무소",
                key="agent_name_input",
                height=100
            )
            rank_button = st.button("순위 계산", use_container_width=True)
            
            if rank_button:
                if not agent_input:
                    st.warning("공인중개사무소 이름을 입력해주세요.")
                else:
                    # 여러 개의 공인중개사무소 이름 파싱 (줄바꿈 또는 쉼표로 구분)
                    agent_names = []
                    for line in agent_input.split('\n'):
                        line = line.strip()
                        if line:
                            # 쉼표로 구분된 경우도 처리
                            for name in line.split(','):
                                name = name.strip()
                                if name:
                                    agent_names.append(name)
                    
                    if not agent_names:
                        st.warning("공인중개사무소 이름을 입력해주세요.")
                    else:
                        with st.spinner(f"{len(agent_names)}개 공인중개사무소 순위 계산 중..."):
                            all_rankings = []
                            
                            for agent_name in agent_names:
                                rankings = DataParser.calculate_agent_rankings(df_filtered, agent_name)
                                if rankings is not None and not rankings.empty:
                                    all_rankings.append(rankings)
                            
                            if not all_rankings:
                                st.info("입력하신 공인중개사무소의 순위 데이터를 찾을 수 없습니다.")
                            else:
                                # 모든 결과 합치기
                                combined_rankings = pd.concat(all_rankings, ignore_index=True)
                                # 컬럼 중복 제거 (같은 이름의 컬럼이 여러 개 있을 경우 첫 번째만 유지)
                                combined_rankings = combined_rankings.loc[:, ~combined_rankings.columns.duplicated()]
                                # 인덱스를 재설정하여 중복 제거 (스타일링 호환성)
                                combined_rankings = combined_rankings.reset_index(drop=True)
                                st.success(f"{len(agent_names)}개 공인중개사무소 순위 결과 (총 {len(combined_rankings)}건)")
                                
                                # 순위 결과 컬럼 순서 지정
                                rank_preferred_order = [
                                    '단지명', '거래유형', '동', '층', '총층수',
                                    '전용면적', '공급면적', '공인중개사무소', '광고사', '확인일',
                                    '같은매물내순위', '동일매물건수', '원문'
                                ]
                                # 중복 제거된 컬럼 리스트 생성
                                rank_display_cols = []
                                seen_cols = set()
                                for col in rank_preferred_order:
                                    if col in combined_rankings.columns and col not in seen_cols:
                                        rank_display_cols.append(col)
                                        seen_cols.add(col)
                                # 순서에 없는 컬럼도 추가 (중복 제거)
                                for col in combined_rankings.columns:
                                    if col not in seen_cols:
                                        rank_display_cols.append(col)
                                        seen_cols.add(col)
                                
                                # 완전히 새로운 DataFrame 생성 (인덱스와 컬럼 모두 고유하게)
                                rankings_display = pd.DataFrame(combined_rankings[rank_display_cols].values, columns=rank_display_cols)
                                rankings_display = rankings_display.reset_index(drop=True)
                                
                                # 정렬: 동, 층, 같은매물내순위 순서
                                rankings_display_sorted = rankings_display.copy()
                                
                                # 동 정렬 (숫자 추출)
                                if '동' in rankings_display_sorted.columns:
                                    rankings_display_sorted['_sort_dong'] = rankings_display_sorted['동'].astype(str).apply(
                                        lambda x: int(re.findall(r'\d+', x)[0]) if re.findall(r'\d+', x) else 999
                                    )
                                else:
                                    rankings_display_sorted['_sort_dong'] = 999
                                
                                # 층 정렬 (숫자 추출)
                                if '층' in rankings_display_sorted.columns:
                                    rankings_display_sorted['_sort_floor'] = rankings_display_sorted['층'].astype(str).apply(
                                        lambda x: int(re.findall(r'\d+', x)[0]) if re.findall(r'\d+', x) else 999
                                    )
                                else:
                                    rankings_display_sorted['_sort_floor'] = 999
                                
                                # 같은매물내순위 정렬
                                if '같은매물내순위' in rankings_display_sorted.columns:
                                    rankings_display_sorted['_sort_rank'] = pd.to_numeric(rankings_display_sorted['같은매물내순위'], errors='coerce').fillna(999)
                                else:
                                    rankings_display_sorted['_sort_rank'] = 999
                                
                                # 정렬 실행: 동, 층, 순위
                                rankings_display_sorted = rankings_display_sorted.sort_values(
                                    ['_sort_dong', '_sort_floor', '_sort_rank'],
                                    ascending=[True, True, True]
                                )
                                
                                # 정렬용 임시 컬럼 제거
                                rankings_display_sorted = rankings_display_sorted.drop(
                                    columns=[col for col in ['_sort_dong', '_sort_floor', '_sort_rank'] if col in rankings_display_sorted.columns]
                                )
                                rankings_display = rankings_display_sorted.reset_index(drop=True)
                                
                                # 같은 매물 찾기 기준
                                same_property_key = ['동', '층', '총층수', '거래유형', '전용면적', '공급면적', '광고사']
                                
                                if '같은매물내순위' in rankings_display.columns:
                                    # 여러 공인중개사무소가 입력된 경우, 같은 매물 내 최소 순위 계산
                                    if len(agent_names) > 1:
                                        # 같은 매물 그룹별로 내가 정한 모든 공인중개사무소의 순위 저장
                                        # 동일매물 그룹 키: 광고사 제외
                                        property_ranks_by_agents = {}  # {property_key: {agent_name: rank}}
                                        
                                        for idx, row in combined_rankings.iterrows():
                                            # 같은 매물 그룹 키 생성 (광고사 제외 - 광고사가 다른 것도 동일 매물로 간주)
                                            property_key_parts = []
                                            for key_col in same_property_key:
                                                if key_col == '광고사':  # 광고사는 제외
                                                    continue
                                                if key_col in row.index:
                                                    val = row[key_col]
                                                    property_key_parts.append(str(val) if pd.notna(val) else 'None')
                                            
                                            property_key = tuple(property_key_parts)
                                            rank_value = row.get('같은매물내순위')
                                            agent_name = row.get('공인중개사무소')
                                            
                                            if pd.notna(rank_value) and agent_name in agent_names:
                                                if property_key not in property_ranks_by_agents:
                                                    property_ranks_by_agents[property_key] = {}
                                                property_ranks_by_agents[property_key][agent_name] = rank_value
                                        
                                        # 순위에 따른 색상 판단 함수
                                        def get_rank_color(row):
                                            property_key_parts = []
                                            for key_col in same_property_key:
                                                if key_col == '광고사':  # 광고사는 제외
                                                    continue
                                                if key_col in row.index:
                                                    val = row[key_col]
                                                    property_key_parts.append(str(val) if pd.notna(val) else 'None')
                                            
                                            property_key = tuple(property_key_parts)
                                            agent_ranks = property_ranks_by_agents.get(property_key, {})
                                            
                                            # 내가 정한 모든 공인중개사무소의 순위 확인
                                            if len(agent_ranks) < len(agent_names):
                                                # 일부 공인중개사무소만 해당 매물에 있는 경우
                                                return 'white'
                                            
                                            # 모든 공인중개사무소의 순위 리스트
                                            all_ranks = list(agent_ranks.values())
                                            
                                            # 빨간색: 모든 공인중개사무소가 3위 이상
                                            if all(rank >= 3 for rank in all_ranks):
                                                return 'red'
                                            # 노란색: 모든 공인중개사무소가 4~5위
                                            elif all(rank >= 4 and rank <= 5 for rank in all_ranks):
                                                return 'yellow'
                                            else:
                                                return 'white'  # 그 외: 하얀색
                                        
                                        # 하이라이트 함수
                                        def highlight_rank(row):
                                            color = get_rank_color(row)
                                            if color == 'red':
                                                return ['background-color: #ffe5e5'] * len(row)
                                            elif color == 'yellow':
                                                return ['background-color: #fff4cd'] * len(row)
                                            else:
                                                return [''] * len(row)
                                        
                                        # 정렬: 하이라이트(색상) 우선 → 거래유형 → 동 → 층 → 같은매물내순위 순서
                                        rankings_display['_highlight_sort'] = rankings_display.apply(
                                            lambda row: 0 if get_rank_color(row) == 'red' else (1 if get_rank_color(row) == 'yellow' else 2), 
                                            axis=1
                                        )
                                        
                                        # 거래유형 정렬
                                        if '거래유형' in rankings_display.columns:
                                            # 매매=1, 전세=2, 월세=3 순서
                                            rankings_display['_sort_type'] = rankings_display['거래유형'].map({'매매': 1, '전세': 2, '월세': 3}).fillna(999)
                                        else:
                                            rankings_display['_sort_type'] = 999
                                        
                                        # 동 정렬 (숫자 추출)
                                        if '동' in rankings_display.columns:
                                            rankings_display['_sort_dong'] = rankings_display['동'].astype(str).apply(
                                                lambda x: int(re.findall(r'\d+', x)[0]) if re.findall(r'\d+', x) else 999
                                            )
                                        else:
                                            rankings_display['_sort_dong'] = 999
                                        
                                        # 층 정렬 (숫자 추출)
                                        if '층' in rankings_display.columns:
                                            rankings_display['_sort_floor'] = rankings_display['층'].astype(str).apply(
                                                lambda x: int(re.findall(r'\d+', x)[0]) if re.findall(r'\d+', x) else 999
                                            )
                                        else:
                                            rankings_display['_sort_floor'] = 999
                                        
                                        # 같은매물내순위 정렬
                                        if '같은매물내순위' in rankings_display.columns:
                                            rankings_display['_sort_rank'] = pd.to_numeric(rankings_display['같은매물내순위'], errors='coerce').fillna(999)
                                        else:
                                            rankings_display['_sort_rank'] = 999
                                        
                                        rankings_display = rankings_display.sort_values(
                                            ['_highlight_sort', '_sort_type', '_sort_dong', '_sort_floor', '_sort_rank'],
                                            ascending=[True, True, True, True, True]
                                        ).drop(columns=[col for col in ['_highlight_sort', '_sort_type', '_sort_dong', '_sort_floor', '_sort_rank'] if col in rankings_display.columns]).reset_index(drop=True)
                                        
                                    else:
                                        # 단일 공인중개사무소인 경우
                                        # 같은 매물 그룹별로 해당 공인중개사무소의 순위 저장 (광고사 제외)
                                        property_rank_by_agent = {}  # {property_key: rank}
                                        
                                        agent_name = agent_names[0]  # 단일 공인중개사무소
                                        
                                        for idx, row in combined_rankings.iterrows():
                                            # 같은 매물 그룹 키 생성 (광고사 제외)
                                            property_key_parts = []
                                            for key_col in same_property_key:
                                                if key_col == '광고사':  # 광고사는 제외
                                                    continue
                                                if key_col in row.index:
                                                    val = row[key_col]
                                                    property_key_parts.append(str(val) if pd.notna(val) else 'None')
                                            
                                            property_key = tuple(property_key_parts)
                                            rank_value = row.get('같은매물내순위')
                                            
                                            if pd.notna(rank_value):
                                                # 같은 매물 그룹에서 해당 공인중개사무소의 순위 저장
                                                if property_key not in property_rank_by_agent:
                                                    property_rank_by_agent[property_key] = rank_value
                                                else:
                                                    # 같은 매물에 여러 개가 있으면 최소 순위 사용
                                                    property_rank_by_agent[property_key] = min(
                                                        property_rank_by_agent[property_key],
                                                        rank_value
                                                    )
                                        
                                        def get_rank_color(row):
                                            property_key_parts = []
                                            for key_col in same_property_key:
                                                if key_col == '광고사':  # 광고사는 제외
                                                    continue
                                                if key_col in row.index:
                                                    val = row[key_col]
                                                    property_key_parts.append(str(val) if pd.notna(val) else 'None')
                                            
                                            property_key = tuple(property_key_parts)
                                            rank = property_rank_by_agent.get(property_key, 0)
                                            
                                            # 빨간색: 3위 이상
                                            if rank >= 3:
                                                return 'red'
                                            # 노란색: 4~5위
                                            elif rank >= 4 and rank <= 5:
                                                return 'yellow'
                                            else:
                                                return 'white'  # 그 외: 하얀색
                                        
                                        # 하이라이트 함수
                                        def highlight_rank(row):
                                            color = get_rank_color(row)
                                            if color == 'red':
                                                return ['background-color: #ffe5e5'] * len(row)
                                            elif color == 'yellow':
                                                return ['background-color: #fff4cd'] * len(row)
                                            else:
                                                return [''] * len(row)
                                        
                                        # 정렬: 하이라이트(색상) 우선 → 거래유형 → 동 → 층 → 같은매물내순위 순서
                                        rankings_display['_highlight_sort'] = rankings_display.apply(
                                            lambda row: 0 if get_rank_color(row) == 'red' else (1 if get_rank_color(row) == 'yellow' else 2), 
                                            axis=1
                                        )
                                        
                                        # 거래유형 정렬
                                        if '거래유형' in rankings_display.columns:
                                            # 매매=1, 전세=2, 월세=3 순서
                                            rankings_display['_sort_type'] = rankings_display['거래유형'].map({'매매': 1, '전세': 2, '월세': 3}).fillna(999)
                                        else:
                                            rankings_display['_sort_type'] = 999
                                        
                                        # 동 정렬 (숫자 추출)
                                        if '동' in rankings_display.columns:
                                            rankings_display['_sort_dong'] = rankings_display['동'].astype(str).apply(
                                                lambda x: int(re.findall(r'\d+', x)[0]) if re.findall(r'\d+', x) else 999
                                            )
                                        else:
                                            rankings_display['_sort_dong'] = 999
                                        
                                        # 층 정렬 (숫자 추출)
                                        if '층' in rankings_display.columns:
                                            rankings_display['_sort_floor'] = rankings_display['층'].astype(str).apply(
                                                lambda x: int(re.findall(r'\d+', x)[0]) if re.findall(r'\d+', x) else 999
                                            )
                                        else:
                                            rankings_display['_sort_floor'] = 999
                                        
                                        # 같은매물내순위 정렬
                                        if '같은매물내순위' in rankings_display.columns:
                                            rankings_display['_sort_rank'] = pd.to_numeric(rankings_display['같은매물내순위'], errors='coerce').fillna(999)
                                        else:
                                            rankings_display['_sort_rank'] = 999
                                        
                                        rankings_display = rankings_display.sort_values(
                                            ['_highlight_sort', '_sort_type', '_sort_dong', '_sort_floor', '_sort_rank'],
                                            ascending=[True, True, True, True, True]
                                        ).drop(columns=[col for col in ['_highlight_sort', '_sort_type', '_sort_dong', '_sort_floor', '_sort_rank'] if col in rankings_display.columns]).reset_index(drop=True)
                                    
                                    styled_rankings = rankings_display.style.apply(highlight_rank, axis=1)
                                    st.dataframe(styled_rankings, use_container_width=True)
                                else:
                                    st.dataframe(rankings_display, use_container_width=True)
                                
                                # 각 행에 대한 같은 매물 보기 기능
                                st.markdown("---")
                                st.subheader("🔍 각 매물의 같은 매물 목록")
                                st.info("아래에서 인덱스를 클릭하여 같은 매물들을 확인할 수 있습니다.")
                                
                                # expander 항목들을 동, 층, 순위로 정렬
                                combined_rankings_sorted = combined_rankings.copy()
                                
                                # 동 정렬 (숫자 추출)
                                if '동' in combined_rankings_sorted.columns:
                                    combined_rankings_sorted['_sort_dong'] = combined_rankings_sorted['동'].astype(str).apply(
                                        lambda x: int(re.findall(r'\d+', x)[0]) if re.findall(r'\d+', x) else 999
                                    )
                                else:
                                    combined_rankings_sorted['_sort_dong'] = 999
                                
                                # 층 정렬 (숫자 추출)
                                if '층' in combined_rankings_sorted.columns:
                                    combined_rankings_sorted['_sort_floor'] = combined_rankings_sorted['층'].astype(str).apply(
                                        lambda x: int(re.findall(r'\d+', x)[0]) if re.findall(r'\d+', x) else 999
                                    )
                                else:
                                    combined_rankings_sorted['_sort_floor'] = 999
                                
                                # 같은매물내순위 정렬
                                if '같은매물내순위' in combined_rankings_sorted.columns:
                                    combined_rankings_sorted['_sort_rank'] = pd.to_numeric(combined_rankings_sorted['같은매물내순위'], errors='coerce').fillna(999)
                                else:
                                    combined_rankings_sorted['_sort_rank'] = 999
                                
                                # 정렬 실행: 동, 층, 순위
                                combined_rankings_sorted = combined_rankings_sorted.sort_values(
                                    ['_sort_dong', '_sort_floor', '_sort_rank'],
                                    ascending=[True, True, True]
                                )
                                
                                # 정렬용 임시 컬럼 제거
                                combined_rankings_sorted = combined_rankings_sorted.drop(
                                    columns=[col for col in ['_sort_dong', '_sort_floor', '_sort_rank'] if col in combined_rankings_sorted.columns]
                                )
                                combined_rankings_sorted = combined_rankings_sorted.reset_index(drop=True)
                                
                                # 이미 표시한 같은 매물 그룹 추적
                                shown_property_groups = set()
                                
                                # 각 행을 반복하면서 expander 추가 (정렬된 순서로)
                                for idx, row in combined_rankings_sorted.iterrows():
                                    # 같은 매물 그룹 키 생성 (중복 체크용)
                                    property_group_key_parts = []
                                    for key in same_property_key:
                                        if key in row.index:
                                            val = row[key]
                                            property_group_key_parts.append(str(val) if pd.notna(val) else 'None')
                                    property_group_key = tuple(property_group_key_parts)
                                    
                                    # 이미 표시한 같은 매물 그룹이면 건너뛰기
                                    if property_group_key in shown_property_groups:
                                        continue
                                    
                                    # 같은 매물 찾기 (필터링된 데이터에서 찾기)
                                    same_property_mask = pd.Series(True, index=df_filtered.index)
                                    
                                    for key in same_property_key:
                                        if key in row.index and key in df_filtered.columns:
                                            row_value = row[key]
                                            # NaN 값 처리
                                            if pd.isna(row_value):
                                                same_property_mask = same_property_mask & df_filtered[key].isna()
                                            else:
                                                same_property_mask = same_property_mask & (df_filtered[key] == row_value)
                                    
                                    same_properties = df_filtered[same_property_mask].copy()
                                    
                                    # 현재 매물의 공인중개사무소 (강조용)
                                    current_agent = row.get('공인중개사무소', '') if '공인중개사무소' in row.index else ''
                                    
                                    # Expander 제목 생성
                                    property_info = []
                                    for col in ['단지명', '동', '층', '거래유형']:
                                        if col in row.index and pd.notna(row.get(col)):
                                            property_info.append(str(row[col]))
                                    
                                    expander_title = f"📌 {' | '.join(property_info[:3])}"
                                    if '같은매물내순위' in row.index and pd.notna(row.get('같은매물내순위')):
                                        expander_title += f" (동일 매물: {len(same_properties)}개)"
                                    
                                    # 같은 매물 그룹을 표시했다고 표시
                                    shown_property_groups.add(property_group_key)
                                    
                                    with st.expander(expander_title, expanded=False):
                                        if len(same_properties) > 0:
                                            # 같은 매물 목록에 순위 계산 (없으면 계산)
                                            if '같은매물내순위' not in same_properties.columns or '동일매물건수' not in same_properties.columns:
                                                same_properties_with_rank = same_properties.copy()
                                                
                                                # 그룹 기준 컬럼 결측치 처리
                                                for key_col in same_property_key:
                                                    if key_col in same_properties_with_rank.columns:
                                                        same_properties_with_rank[key_col] = same_properties_with_rank[key_col].fillna('정보없음')
                                                
                                                # 같은 매물 그룹 내 순위 계산
                                                if all(col in same_properties_with_rank.columns for col in same_property_key):
                                                    # 동일매물건수 계산
                                                    group_obj = same_properties_with_rank.groupby(same_property_key, dropna=False)
                                                    size_target = '순번' if '순번' in same_properties_with_rank.columns else same_property_key[0]
                                                    same_properties_with_rank['동일매물건수'] = group_obj[size_target].transform('size')
                                                    
                                                    # 동, 층, 확인일 기준으로 정렬 후 순위 계산
                                                    sort_columns = []
                                                    sort_ascending = []
                                                    
                                                    # 동 정렬
                                                    if '동' in same_properties_with_rank.columns:
                                                        same_properties_with_rank['_sort_dong'] = same_properties_with_rank['동'].astype(str).apply(
                                                            lambda x: int(re.findall(r'\d+', x)[0]) if re.findall(r'\d+', x) else 999
                                                        )
                                                        sort_columns.append('_sort_dong')
                                                        sort_ascending.append(True)
                                                    
                                                    # 층 정렬
                                                    if '층' in same_properties_with_rank.columns:
                                                        same_properties_with_rank['_sort_floor'] = same_properties_with_rank['층'].astype(str).apply(
                                                            lambda x: int(re.findall(r'\d+', x)[0]) if re.findall(r'\d+', x) else 999
                                                        )
                                                        sort_columns.append('_sort_floor')
                                                        sort_ascending.append(True)
                                                    
                                                    # 확인일 기준으로 정렬 (최신순)
                                                    if '확인일' in same_properties_with_rank.columns:
                                                        try:
                                                            parsed_dates = pd.to_datetime(
                                                                same_properties_with_rank['확인일'].astype(str).str.replace('.', '-', regex=False),
                                                                format='%y-%m-%d',
                                                                errors='coerce'
                                                            )
                                                            same_properties_with_rank['_sort_date'] = parsed_dates
                                                            sort_columns.append('_sort_date')
                                                            sort_ascending.append(False)  # 최신순
                                                        except:
                                                            pass
                                                    
                                                    # 정렬 실행
                                                    if sort_columns:
                                                        same_properties_with_rank = same_properties_with_rank.sort_values(sort_columns, ascending=sort_ascending, na_position='last')
                                                    
                                                    # 정렬 후 다시 그룹화하여 순위 계산
                                                    group_obj_sorted = same_properties_with_rank.groupby(same_property_key, dropna=False)
                                                    same_properties_with_rank['같은매물내순위'] = group_obj_sorted.cumcount() + 1
                                                    
                                                    # 정렬용 임시 컬럼 제거
                                                    same_properties_with_rank = same_properties_with_rank.drop(
                                                        columns=[col for col in ['_sort_dong', '_sort_floor', '_sort_date'] if col in same_properties_with_rank.columns]
                                                    )
                                                    
                                                    same_properties = same_properties_with_rank
                                            
                                            # 표시할 컬럼 선택
                                            display_cols_for_same = [
                                                '거래유형', '동', '층', '층구분', '전용면적',
                                                '단지명', '총층수', '가격', '공급면적',
                                                '확인일', '공인중개사무소', '광고사', 
                                                '같은매물내순위', '동일매물건수', '원문'
                                            ]
                                            existing_display_cols = [col for col in display_cols_for_same if col in same_properties.columns]
                                            
                                            # 정렬: 동, 층, 같은매물내순위 순서
                                            same_properties_sorted = same_properties.copy()
                                            
                                            # 동 정렬 (숫자 추출)
                                            if '동' in same_properties_sorted.columns:
                                                same_properties_sorted['_sort_dong'] = same_properties_sorted['동'].astype(str).apply(
                                                    lambda x: int(re.findall(r'\d+', x)[0]) if re.findall(r'\d+', x) else 999
                                                )
                                            else:
                                                same_properties_sorted['_sort_dong'] = 999
                                            
                                            # 층 정렬 (숫자 추출)
                                            if '층' in same_properties_sorted.columns:
                                                same_properties_sorted['_sort_floor'] = same_properties_sorted['층'].astype(str).apply(
                                                    lambda x: int(re.findall(r'\d+', x)[0]) if re.findall(r'\d+', x) else 999
                                                )
                                            else:
                                                same_properties_sorted['_sort_floor'] = 999
                                            
                                            # 같은매물내순위 정렬
                                            if '같은매물내순위' in same_properties_sorted.columns:
                                                same_properties_sorted['_sort_rank'] = pd.to_numeric(same_properties_sorted['같은매물내순위'], errors='coerce').fillna(999)
                                            else:
                                                same_properties_sorted['_sort_rank'] = 999
                                            
                                            # 정렬 실행: 동, 층, 순위
                                            same_properties_sorted = same_properties_sorted.sort_values(
                                                ['_sort_dong', '_sort_floor', '_sort_rank'],
                                                ascending=[True, True, True]
                                            )
                                            
                                            # 정렬용 임시 컬럼 제거
                                            same_properties_sorted = same_properties_sorted.drop(
                                                columns=[col for col in ['_sort_dong', '_sort_floor', '_sort_rank'] if col in same_properties_sorted.columns]
                                            )
                                            same_properties = same_properties_sorted
                                            
                                            # 현재 매물 강조 표시 함수
                                            def highlight_current_property(compare_row):
                                                styles = [''] * len(compare_row)
                                                
                                                # 현재 행의 공인중개사무소와 같은 매물 강조
                                                if '공인중개사무소' in compare_row.index and current_agent:
                                                    compare_agent = str(compare_row.get('공인중개사무소', ''))
                                                    if compare_agent and current_agent in compare_agent:
                                                        return ['background-color: #fff4cd; font-weight: bold'] * len(compare_row)
                                                
                                                return styles
                                            
                                            styled_same = same_properties[existing_display_cols].style.apply(
                                                highlight_current_property, axis=1
                                            )
                                            st.dataframe(styled_same, use_container_width=True)
                                            st.caption(f"✅ 총 {len(same_properties)}개의 같은 매물 | 노란색 강조: 현재 공인중개사무소 ({current_agent})")
                                        else:
                                            st.info("⚠️ 같은 매물을 찾을 수 없습니다.")
                                
                                csv_rank = combined_rankings.to_csv(index=False, encoding='utf-8-sig')
                                agent_names_str = "_".join([name[:10] for name in agent_names[:3]])  # 파일명용
                                st.download_button(
                                    "📥 순위 CSV 다운로드",
                                    csv_rank,
                                    file_name=f"공인중개사순위_{agent_names_str}.csv",
                                    mime="text/csv",
                                    use_container_width=True
                                )
            
            # 다운로드 버튼
            col1, col2 = st.columns(2)
            
            with col1:
                csv = df_filtered.to_csv(index=False, encoding='utf-8-sig')
                st.download_button(
                    label="📥 CSV 다운로드",
                    data=csv,
                    file_name=f"{st.session_state.get('keyword', '매물')}_필터링.csv",
                    mime="text/csv"
                )
            
            with col2:
                # Excel 다운로드를 위한 임시 파일 생성
                import tempfile
                with tempfile.NamedTemporaryFile(delete=False, suffix='.xlsx') as tmp:
                    df_filtered.to_excel(tmp.name, index=False, engine='openpyxl')
                    with open(tmp.name, 'rb') as f:
                        st.download_button(
                            label="📥 Excel 다운로드",
                            data=f.read(),
                            file_name=f"{st.session_state.get('keyword', '매물')}_필터링.xlsx",
                            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                        )
        
        else:
            st.info("👈 먼저 크롤링을 실행해주세요!")
    
    with tab3:
        st.header("파일 관리")
        
        # data 디렉토리 파일 목록
        data_dir = "data"
        if os.path.exists(data_dir):
            files = [f for f in os.listdir(data_dir) if f.endswith(('.csv', '.xlsx'))]
            
            if files:
                st.subheader("📁 저장된 파일")
                
                for file in sorted(files, reverse=True):
                    file_path = os.path.join(data_dir, file)
                    file_size = os.path.getsize(file_path) / 1024  # KB
                    file_time = datetime.fromtimestamp(os.path.getmtime(file_path))
                    
                    col1, col2, col3 = st.columns([3, 1, 1])
                    
                    with col1:
                        st.write(f"📄 {file}")
                    
                    with col2:
                        st.write(f"{file_size:.1f} KB")
                    
                    with col3:
                        with open(file_path, 'rb') as f:
                            if file.endswith('.csv'):
                                st.download_button(
                                    "다운로드",
                                    f.read(),
                                    file,
                                    key=f"dl_{file}",
                                    use_container_width=True
                                )
                            else:
                                st.download_button(
                                    "다운로드",
                                    f.read(),
                                    file,
                                    key=f"dl_{file}",
                                    use_container_width=True
                                )
            else:
                st.info("저장된 파일이 없습니다.")
        else:
            st.info("data 디렉토리가 없습니다.")


if __name__ == "__main__":
    main()

