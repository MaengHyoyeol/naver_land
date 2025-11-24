"""
네이버 부동산 크롤러 (실제 작동 검증됨)
undetected_chromedriver를 사용하여 봇 탐지를 우회합니다.
"""

import undetected_chromedriver as uc
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.keys import Keys
import time
import pandas as pd
from typing import Dict, List, Optional
import re


class NaverRealEstateCrawler:
    """네이버 부동산 크롤러 (undetected_chromedriver 사용)"""
    
    def __init__(self, headless: bool = False):
        """
        초기화
        
        Args:
            headless (bool): 헤드리스 모드 (False 권장, 디버깅 용이)
        """
        self.headless = headless
        self.driver = None
        
    def init_driver(self):
        """WebDriver 초기화 (봇 탐지 우회)"""
        try:
            options = uc.ChromeOptions()
            if self.headless:
                options.add_argument('--headless')
            
            self.driver = uc.Chrome(options=options)
            print("✅ WebDriver 초기화 완료 (undetected_chromedriver)")
            return True
            
        except Exception as e:
            print(f"❌ WebDriver 초기화 실패: {e}")
            return False
    
    def close(self):
        """WebDriver 종료"""
        if self.driver:
            self.driver.quit()
            print("✅ WebDriver 종료")
    
    def search_complex(self, keyword: str) -> bool:
        """
        단지 검색
        
        Args:
            keyword (str): 검색할 단지명
            
        Returns:
            bool: 검색 성공 여부
        """
        try:
            if not self.driver:
                if not self.init_driver():
                    return False
            
            print(f"\n🔍 '{keyword}' 검색 시작...")
            
            # 1. 네이버 부동산 메인 페이지 접속
            self.driver.get("https://land.naver.com/")
            time.sleep(3)
            print("✅ 메인 페이지 접속 완료")
            
            # 2. 검색창 찾기 및 검색
            search_input = self.driver.find_element(By.ID, "queryInputHeader")
            search_input.send_keys(keyword)
            time.sleep(1)
            search_input.send_keys(Keys.RETURN)
            time.sleep(5)
            
            print(f"✅ 검색 완료")
            print(f"현재 URL: {self.driver.current_url}")
            
            return True
            
        except Exception as e:
            print(f"❌ 검색 오류: {e}")
            import traceback
            traceback.print_exc()
            return False
    
    def click_merge_checkbox(self) -> bool:
        """
        동일매물 묶기 체크박스 클릭
        
        Returns:
            bool: 성공 여부
        """
        selectors = [
            "//input[@id='sameAddressGroup']",
            "//label[contains(text(), '동일매물')]",
            "//span[contains(text(), '동일매물')]",
            "input[id*='same']",
            "input[id*='merge']",
            "label[for*='same']",
            "#sameAddressGroup",
            "input[type='checkbox'][id*='Address']",
        ]
        
        for selector in selectors:
            try:
                if selector.startswith("//"):
                    element = self.driver.find_element(By.XPATH, selector)
                else:
                    element = self.driver.find_element(By.CSS_SELECTOR, selector)
                
                # 체크박스가 이미 체크되어 있는지 확인
                if element.tag_name == 'input':
                    if not element.is_selected():
                        element.click()
                        print(f"✅ 동일매물 묶기 활성화")
                    else:
                        print(f"✅ 동일매물 묶기 이미 활성화됨")
                else:
                    # label인 경우 클릭
                    element.click()
                    print(f"✅ 동일매물 묶기 클릭")
                
                time.sleep(2)
                return True
                
            except Exception as e:
                continue
        
        print("⚠️  동일매물 묶기 버튼을 찾을 수 없습니다.")
        print("   수동으로 클릭하거나 10초 대기 중...")
        time.sleep(10)
        return False
    
    def load_all_items(self) -> int:
        """
        스크롤하여 모든 매물 로드
        
        Returns:
            int: 로드된 매물 수
        """
        print("\n📜 스크롤로 모든 매물 로딩 중...")
        
        # 왼쪽 리스트 영역 찾기
        try:
            list_area = self.driver.find_element(By.CSS_SELECTOR, "div.list_contents, div[class*='list']")
            is_container_scroll = True
            print("✅ 리스트 컨테이너 발견")
        except:
            list_area = None
            is_container_scroll = False
            print("⚠️  리스트 컨테이너 미발견 - 전체 페이지 스크롤 사용")
        
        prev_count = 0
        stable_count = 0
        
        for i in range(100):  # 최대 100회
            # 스크롤
            if is_container_scroll and list_area:
                self.driver.execute_script("arguments[0].scrollTop = arguments[0].scrollHeight", list_area)
            else:
                self.driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            
            time.sleep(1.5)
            
            # 현재 매물 수 확인
            try:
                items = self.driver.find_elements(By.CSS_SELECTOR, "div[class*='item']")
                current_count = len(items)
                
                print(f"  스크롤 {i+1:3d}회 | 매물 수: {current_count:3d}개", end='')
                
                if current_count == prev_count:
                    stable_count += 1
                    print(f" (변화없음 {stable_count}/5)")
                    if stable_count >= 5:
                        print("\n✅ 로딩 완료!")
                        break
                else:
                    stable_count = 0
                    print(f" (+{current_count - prev_count})")
                
                prev_count = current_count
                
            except Exception as e:
                print(f"\r  스크롤 {i+1}회 완료")
        
        time.sleep(2)
        return prev_count
    
    def extract_data(self) -> pd.DataFrame:
        """
        매물 데이터 추출
        
        Returns:
            pd.DataFrame: 추출된 매물 데이터
        """
        print("\n📊 데이터 추출 시작...\n")
        
        items = self.driver.find_elements(By.CSS_SELECTOR, "div[class*='item']")
        data_list = []
        
        for idx, item in enumerate(items, 1):
            try:
                text = item.text.strip()
                if text:
                    data_list.append({
                        '순번': idx,
                        '매물정보': text
                    })
                    if idx % 20 == 0:
                        print(f"  {idx}/{len(items)} 추출 완료...")
            except:
                continue
        
        df = pd.DataFrame(data_list)
        print(f"\n✅ {len(df)}개 매물 추출 완료!")
        
        return df
    
    def crawl(self, keyword: str) -> Optional[pd.DataFrame]:
        """
        전체 크롤링 프로세스 실행
        
        Args:
            keyword (str): 검색할 단지명
            
        Returns:
            pd.DataFrame: 크롤링된 데이터
        """
        print(f"\n{'='*80}")
        print(f"  🏠 '{keyword}' 크롤링 시작")
        print(f"{'='*80}")
        
        try:
            # 1. 검색
            if not self.search_complex(keyword):
                return None
            
            # 2. 동일매물 묶기
            #self.click_merge_checkbox()
            
            # 3. 모든 매물 로드
            total_items = self.load_all_items()
            print(f"\n📋 최종 매물 수: {total_items}개\n")
            
            # 4. 데이터 추출
            df = self.extract_data()
            
            return df
            
        except Exception as e:
            print(f"\n❌ 크롤링 오류: {e}")
            import traceback
            traceback.print_exc()
            return None
    
    def save_data(self, df: pd.DataFrame, filename_prefix: str = "매물데이터"):
        """
        데이터 저장 (CSV, Excel)
        
        Args:
            df (pd.DataFrame): 저장할 데이터
            filename_prefix (str): 파일명 접두사
        """
        if df is None or df.empty:
            print("⚠️  저장할 데이터가 없습니다.")
            return
        
        import os
        from datetime import datetime
        
        # data 디렉토리 생성
        os.makedirs('data', exist_ok=True)
        
        # 타임스탬프 추가
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        # CSV 저장
        csv_file = f"data/{filename_prefix}_{timestamp}.csv"
        df.to_csv(csv_file, index=False, encoding='utf-8-sig')
        print(f"✅ CSV 저장: {csv_file}")
        
        # Excel 저장
        try:
            excel_file = f"data/{filename_prefix}_{timestamp}.xlsx"
            df.to_excel(excel_file, index=False, engine='openpyxl')
            print(f"✅ Excel 저장: {excel_file}")
        except Exception as e:
            print(f"⚠️  Excel 저장 실패: {e}")


if __name__ == "__main__":
    # 테스트 코드
    crawler = NaverRealEstateCrawler(headless=False)
    
    try:
        # 영등포 아트자이 크롤링
        df = crawler.crawl("영등포 아트자이")
        
        if df is not None and not df.empty:
            print("\n" + "="*80)
            print("  데이터 미리보기")
            print("="*80)
            print(df.head(10))
            
            # 저장
            crawler.save_data(df, "영등포아트자이_매물")
    
    finally:
        crawler.close()

