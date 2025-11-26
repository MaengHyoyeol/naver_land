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
        **버전**: v2.0.0  
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
                if st.button("🔍 데이터 파싱", use_container_width=True, type="primary"):
                    with st.spinner("데이터 파싱 중..."):
                        parser = DataParser()
                        df_parsed = parser.parse_dataframe(df_raw)
                        
                        if not df_parsed.empty:
                            st.session_state.df_parsed = df_parsed
                            st.success(f"✅ {len(df_parsed)}개 매물 파싱 완료!")
                            st.rerun()  # 페이지 새로고침하여 분석 탭에 표시
                        else:
                            st.warning("⚠️ 파싱된 데이터가 없습니다.")
            else:
                st.warning("⚠️ 수집된 데이터가 비어있습니다.")
    
    with tab2:
        st.header("데이터 분석")
        
        if 'df_parsed' in st.session_state and st.session_state.df_parsed is not None:
            df = st.session_state.df_parsed
            
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
            st.subheader("🔍 필터")
            col1, col2, col3, col4, col5 = st.columns(5)
            
            with col1:
                if '거래유형' in df.columns:
                    trade_types = ['전체'] + list(df['거래유형'].dropna().unique())
                    selected_type = st.selectbox("거래유형", trade_types)
                else:
                    selected_type = '전체'
            
            with col2:
                if '동' in df.columns:
                    dongs = ['전체'] + list(df['동'].dropna().unique())
                    selected_dong = st.selectbox("동", dongs)
                else:
                    selected_dong = '전체'
            
            with col3:
                if '방향' in df.columns:
                    directions = ['전체'] + list(df['방향'].dropna().unique())
                    selected_direction = st.selectbox("방향", directions)
                else:
                    selected_direction = '전체'
            
            with col4:
                if '확인일' in df.columns:
                    dates = ['전체'] + sorted(df['확인일'].dropna().unique())
                    selected_date = st.selectbox("확인일", dates)
                else:
                    selected_date = '전체'
            
            with col5:
                if '공인중개사무소' in df.columns:
                    agents = ['전체'] + list(df['공인중개사무소'].dropna().unique())
                    selected_agent = st.selectbox("공인중개사무소", agents)
                else:
                    selected_agent = '전체'
            
            # 필터링
            df_filtered = df.copy()
            original_count = len(df_filtered)
            
            if selected_type != '전체':
                df_filtered = df_filtered[df_filtered['거래유형'] == selected_type]
            if selected_dong != '전체':
                df_filtered = df_filtered[df_filtered['동'] == selected_dong]
            if selected_direction != '전체':
                df_filtered = df_filtered[df_filtered['방향'] == selected_direction]
            if selected_date != '전체':
                df_filtered = df_filtered[df_filtered['확인일'] == selected_date]
            if selected_agent != '전체':
                df_filtered = df_filtered[df_filtered['공인중개사무소'] == selected_agent]
            
            filtered_count = len(df_filtered)

            # 동일 매물 중 최신 확인일만 유지
            # 같은 매물 제거 기준: 가격, 공급면적, 전용면적, 층, 총층수, 방향, 공인중개사무소가 모두 같은 경우
            dedup_key = ['가격', '공급면적', '전용면적', '층', '총층수', '방향', '공인중개사무소', '확인일']
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
            
            st.markdown("---")
            st.subheader("📊 필터링된 데이터")
            
            # 필터링 정보 표시
            filter_info = []
            if selected_type != '전체':
                filter_info.append(f"거래유형: {selected_type}")
            if selected_dong != '전체':
                filter_info.append(f"동: {selected_dong}")
            if selected_direction != '전체':
                filter_info.append(f"방향: {selected_direction}")
            if selected_date != '전체':
                filter_info.append(f"확인일: {selected_date}")
            if selected_agent != '전체':
                filter_info.append(f"공인중개사무소: {selected_agent}")
            
            if filter_info:
                st.info(f"🔍 적용된 필터: {', '.join(filter_info)} | 필터링 후: {filtered_count}개 → 중복 제거 후: {after_dedup_count}개 (전체: {original_count}개)")
            else:
                st.info(f"📊 전체 데이터: {original_count}개 → 중복 제거 후: {after_dedup_count}개")
            preferred_order = [
                '순번', '단지명', '동', '거래유형', '가격', '구분',
                '공급면적', '전용면적', '층', '총층수', '방향',
                '확인일', '중개사수', '공인중개사무소', '원문'
            ]
            display_cols = [col for col in preferred_order if col in df_filtered.columns]
            if display_cols:
                st.dataframe(df_filtered[display_cols], use_container_width=True)
            else:
                st.dataframe(df_filtered, use_container_width=True)
            
            st.markdown("---")
            st.subheader("🏅 내 공인중개사 순위")
            agent_input = st.text_input(
                "내 공인중개사무소 이름을 입력하세요",
                placeholder="예: 영등포아트자이공인중개사사무소",
                key="agent_name_input"
            )
            rank_button = st.button("순위 계산", use_container_width=True)
            
            if rank_button:
                if not agent_input:
                    st.warning("공인중개사무소 이름을 입력해주세요.")
                else:
                    with st.spinner("순위 계산 중..."):
                        rankings = DataParser.calculate_agent_rankings(df_filtered, agent_input)
                        if rankings is None or rankings.empty:
                            st.info("해당 공인중개사무소의 순위 데이터를 찾을 수 없습니다.")
                        else:
                            st.success(f"{agent_input} 순위 결과")
                            
                            if '같은매물내순위' in rankings.columns:
                                def highlight_rank(row):
                                    rank_value = row.get('같은매물내순위')
                                    if pd.notna(rank_value) and rank_value >= 3:
                                        return ['background-color: #ffe5e5'] * len(row)
                                    return [''] * len(row)
                                
                                styled_rankings = rankings.style.apply(highlight_rank, axis=1)
                                st.dataframe(styled_rankings, use_container_width=True)
                            else:
                                st.dataframe(rankings, use_container_width=True)
                            
                            csv_rank = rankings.to_csv(index=False, encoding='utf-8-sig')
                            st.download_button(
                                "📥 순위 CSV 다운로드",
                                csv_rank,
                                file_name=f"{agent_input}_순위.csv",
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

