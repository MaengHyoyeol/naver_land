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
import random
import os
from datetime import datetime


class NaverRealEstateCrawler:
    """네이버 부동산 크롤러 (undetected_chromedriver 사용)"""
    
    USER_AGENTS = [
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 13_5_2) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/16.5 Safari/605.1.15",
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36 Edg/119.0.0.0",
    ]
    
    def __init__(self, headless: bool = False, enable_logging: bool = True):
        """
        초기화
        
        Args:
            headless (bool): 헤드리스 모드 (False 권장, 디버깅 용이)
            enable_logging (bool): 로그 파일 저장 여부
        """
        self.headless = headless
        self.driver = None
        self.enable_logging = enable_logging
        self.log_file = None
        
        # 로그 파일 설정
        if self.enable_logging:
            self._setup_logging()
    
    def _setup_logging(self):
        """로그 파일 설정"""
        try:
            # logs 디렉토리 생성
            os.makedirs('logs', exist_ok=True)
            
            # 타임스탬프로 로그 파일명 생성
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            self.log_file = f"logs/crawler_{timestamp}.log"
            
            # 로그 파일 초기화
            with open(self.log_file, 'w', encoding='utf-8') as f:
                f.write(f"=== 크롤러 로그 시작: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')} ===\n\n")
            
            print(f"📝 로그 파일: {self.log_file}")
        except Exception as e:
            print(f"⚠️  로그 파일 생성 실패: {e}")
            self.enable_logging = False
    
    def _log(self, message: str):
        """
        로그 출력 (콘솔 + 파일)
        
        Args:
            message (str): 로그 메시지
        """
        # 콘솔 출력
        print(message)
        
        # 파일 출력
        if self.enable_logging and self.log_file:
            try:
                with open(self.log_file, 'a', encoding='utf-8') as f:
                    timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                    f.write(f"[{timestamp}] {message}\n")
            except Exception as e:
                # 로그 파일 쓰기 실패해도 계속 진행
                pass
        
    def init_driver(self):
        """WebDriver 초기화 (봇 탐지 우회)"""
        try:
            options = uc.ChromeOptions()
            
            # 봇 탐지 회피를 위한 옵션
            user_agent = random.choice(self.USER_AGENTS)
            options.add_argument(f'--user-agent={user_agent}')
            options.add_argument('--disable-blink-features=AutomationControlled')
            options.add_argument('--disable-infobars')
            options.add_argument('--lang=ko-KR')
            options.add_argument('--start-maximized')
            options.add_argument('--no-first-run')
            options.add_argument('--no-default-browser-check')
            options.add_argument('--disable-notifications')
            options.add_argument('--disable-popup-blocking')
            options.add_argument('--window-size=1920,1080')
            options.add_argument('--disable-gpu')
            options.add_argument('--no-sandbox')
            options.add_argument('--disable-dev-shm-usage')
            
            # headless 모드 개선
            if self.headless:
                options.add_argument('--headless=new')
            
            # excludeSwitches와 useAutomationExtension 옵션은 일부 Chrome 버전에서 지원하지 않으므로 제거
            # options.add_experimental_option("excludeSwitches", ["enable-automation"])
            # options.add_experimental_option("useAutomationExtension", False)
            prefs = {
                "profile.default_content_setting_values.notifications": 2,
                "credentials_enable_service": False,
                "profile.password_manager_enabled": False,
            }
            options.add_experimental_option("prefs", prefs)
            
            # 타임아웃 설정
            self.driver = uc.Chrome(options=options)
            self.driver.set_page_load_timeout(30)  # 페이지 로딩 타임아웃 30초
            self.driver.implicitly_wait(10)  # 요소 찾기 대기 시간 10초
            
            self._log("✅ WebDriver 초기화 완료 (undetected_chromedriver)")
            return True
            
        except Exception as e:
            self._log(f"❌ WebDriver 초기화 실패: {e}")
            import traceback
            traceback.print_exc()
            return False
    
    def close(self):
        """WebDriver 종료"""
        if self.driver:
            self.driver.quit()
            self._log("✅ WebDriver 종료")
    
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
            
            self._log(f"\n🔍 '{keyword}' 검색 시작...")
            
            # 1. 네이버 부동산 메인 페이지 접속
            self._log("🌐 메인 페이지 접속 중...")
            try:
                self.driver.get("https://land.naver.com/")
                # 페이지 로딩 완료 대기
                WebDriverWait(self.driver, 30).until(
                    lambda d: d.execute_script("return document.readyState") == "complete"
                )
                time.sleep(3)  # 추가 안정화 시간
                self._log("✅ 메인 페이지 접속 완료")
                self._log(f"   현재 URL: {self.driver.current_url}")
            except Exception as e:
                self._log(f"❌ 메인 페이지 접속 실패: {e}")
                # 재시도
                self._log("🔄 재시도 중...")
                time.sleep(5)
                self.driver.get("https://land.naver.com/")
                WebDriverWait(self.driver, 30).until(
                    lambda d: d.execute_script("return document.readyState") == "complete"
                )
                time.sleep(3)
                self._log("✅ 메인 페이지 접속 완료 (재시도 성공)")
            
            # 2. 검색창 찾기 및 검색
            self._log("🔍 검색창 찾는 중...")
            try:
                # 여러 선택자 시도
                search_input = None
                selectors = [
                    (By.ID, "queryInputHeader"),
                    (By.CSS_SELECTOR, "input[id*='query']"),
                    (By.CSS_SELECTOR, "input[placeholder*='검색']"),
                    (By.CSS_SELECTOR, "input[type='text']"),
                ]
                
                for by, selector in selectors:
                    try:
                        search_input = WebDriverWait(self.driver, 10).until(
                            EC.presence_of_element_located((by, selector))
                        )
                        self._log(f"✅ 검색창 발견: {selector}")
                        break
                    except:
                        continue
                
                if not search_input:
                    raise Exception("검색창을 찾을 수 없습니다")
                
                # 검색어 입력
                search_input.clear()
                search_input.send_keys(keyword)
                time.sleep(1)
                
                # 엔터 키 입력
                search_input.send_keys(Keys.RETURN)
                self._log("✅ 검색 실행")
                
                # 검색 결과 페이지 로딩 대기
                time.sleep(3)
                WebDriverWait(self.driver, 30).until(
                    lambda d: d.execute_script("return document.readyState") == "complete"
                )
                time.sleep(2)  # 추가 안정화 시간
                
                self._log(f"✅ 검색 완료")
                self._log(f"   현재 URL: {self.driver.current_url}")
                
                return True
                
            except Exception as e:
                self._log(f"❌ 검색 실행 오류: {e}")
                import traceback
                traceback.print_exc()
                return False
            
        except Exception as e:
            self._log(f"❌ 검색 오류: {e}")
            import traceback
            traceback.print_exc()
            return False
    
    def check_property_list_exists(self) -> bool:
        """
        매물 목록(articleListArea)이 존재하는지 확인
        
        Returns:
            bool: 매물 목록이 존재하면 True
        """
        try:
            # articleListArea가 있는지 확인
            article_area = WebDriverWait(self.driver, 3).until(
                EC.presence_of_element_located((By.ID, "articleListArea"))
            )
            
            # 매물 버튼이 하나라도 있는지 확인
            items = self.driver.find_elements(By.CSS_SELECTOR, "#articleListArea button")
            if len(items) > 0:
                self._log(f"✅ 매물 목록 확인: {len(items)}개 매물 발견")
                return True
            else:
                self._log(f"⚠️  매물 목록 영역은 있지만 매물이 없습니다.")
                return False
                
        except Exception as e:
            self._log(f"⚠️  매물 목록을 찾을 수 없습니다: {str(e)}")
            return False
    
    def click_complex_name(self, keyword: str) -> bool:
        """
        검색 결과에서 단지명 클릭 (매물 목록이 나타나지 않을 때)
        
        Args:
            keyword (str): 검색한 단지명
            
        Returns:
            bool: 클릭 성공 여부
        """
        try:
            self._log(f"\n🔄 단지명 클릭 시도: '{keyword}'")
            
            # 여러 선택자 시도 (단지명 링크 또는 버튼)
            selectors = [
                # 단지명 링크 (검색 결과 페이지)
                (By.XPATH, f"//a[contains(text(), '{keyword}')]"),
                (By.XPATH, f"//a[contains(@href, '/complexes/') and contains(., '{keyword}')]"),
                # 단지명이 포함된 링크
                (By.CSS_SELECTOR, f"a[href*='/complexes/']"),
                # 단지 정보 영역의 클릭 가능한 요소
                (By.CSS_SELECTOR, "div[class*='complex'] a"),
                (By.CSS_SELECTOR, "div[class*='item'] a"),
                # h1, h2, h3 등 단지명 제목
                (By.XPATH, f"//h1[contains(text(), '{keyword}')] | //h2[contains(text(), '{keyword}')] | //h3[contains(text(), '{keyword}')]"),
            ]
            
            for by, selector in selectors:
                try:
                    elements = self.driver.find_elements(by, selector)
                    for element in elements:
                        element_text = element.text.strip()
                        # 단지명이 포함되어 있는지 확인
                        if keyword.split()[0] in element_text or any(word in element_text for word in keyword.split() if len(word) > 2):
                            # 요소가 보이는지 확인
                            if element.is_displayed():
                                self._log(f"✅ 단지명 요소 발견: {element_text}")
                                # 스크롤하여 요소가 보이도록
                                self.driver.execute_script("arguments[0].scrollIntoView(true);", element)
                                time.sleep(1)
                                element.click()
                                self._log(f"✅ 단지명 클릭 완료")
                                
                                # 클릭 후 페이지 로딩 대기
                                time.sleep(3)
                                WebDriverWait(self.driver, 30).until(
                                    lambda d: d.execute_script("return document.readyState") == "complete"
                                )
                                time.sleep(2)
                                
                                self._log(f"   클릭 후 URL: {self.driver.current_url}")
                                return True
                except Exception as e:
                    continue
            
            # 대안: 검색 결과 목록에서 첫 번째 단지 클릭
            try:
                self._log("   검색 결과 목록에서 첫 번째 단지 클릭 시도...")
                # 검색 결과 리스트의 첫 번째 항목
                first_complex = WebDriverWait(self.driver, 5).until(
                    EC.element_to_be_clickable((By.CSS_SELECTOR, "div[class*='item'] a, div[class*='list'] a, a[href*='/complexes/']"))
                )
                self.driver.execute_script("arguments[0].scrollIntoView(true);", first_complex)
                time.sleep(1)
                first_complex.click()
                self._log(f"✅ 첫 번째 검색 결과 클릭 완료")
                
                # 클릭 후 페이지 로딩 대기
                time.sleep(3)
                WebDriverWait(self.driver, 30).until(
                    lambda d: d.execute_script("return document.readyState") == "complete"
                )
                time.sleep(2)
                
                self._log(f"   클릭 후 URL: {self.driver.current_url}")
                return True
            except Exception as e:
                self._log(f"⚠️  첫 번째 검색 결과 클릭 실패: {str(e)}")
            
            self._log(f"❌ 단지명 클릭 실패")
            return False
            
        except Exception as e:
            self._log(f"❌ 단지명 클릭 오류: {e}")
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
        스크롤하여 모든 매물 로드 (부모 컨테이너 스크롤)
        
        Returns:
            int: 로드된 매물 수
        """
        self._log("\n📜 스크롤로 모든 매물 로딩 중...")
        
        # articleListArea의 부모 컨테이너 찾기
        scroll_area = None
        try:
            # 먼저 articleListArea 찾기
            article_area = WebDriverWait(self.driver, 5).until(
                EC.presence_of_element_located((By.ID, "articleListArea"))
            )
            
            # 부모 요소 찾기 (실제 스크롤 가능한 컨테이너)
            scroll_area = self.driver.execute_script("return arguments[0].parentElement", article_area)
            
            if not scroll_area:
                self._log(f"⚠️  부모 요소를 찾을 수 없습니다.")
                return 0
            
            self._log(f"✅ 스크롤 영역 발견: articleListArea의 부모 요소")
            
            # 스크롤 가능 여부 확인
            scroll_height = self.driver.execute_script("return arguments[0].scrollHeight", scroll_area)
            client_height = self.driver.execute_script("return arguments[0].clientHeight", scroll_area)
            overflow_y = self.driver.execute_script("return window.getComputedStyle(arguments[0]).overflowY", scroll_area)
            
            self._log(f"📏 스크롤 정보: scrollHeight={scroll_height}, clientHeight={client_height}, overflowY={overflow_y}")
            
            if scroll_height <= client_height:
                self._log(f"⚠️  스크롤이 필요 없는 영역입니다.")
                # 그래도 매물은 세어서 반환
                items = self.driver.find_elements(By.CSS_SELECTOR, "#articleListArea button")
                self._log(f"📋 매물 수: {len(items)}개")
                return len(items)
                
        except Exception as e:
            self._log(f"⚠️  스크롤 영역을 찾을 수 없습니다: {str(e)}")
            return 0
        
        prev_count = 0
        no_change_count = 0
        i = 0
        max_iterations = 100
        
        self._log("📜 스크롤 시작...")
        
        # 스크롤 실행
        while i < max_iterations:
            i += 1
            
            # 스크롤 전 위치
            try:
                scroll_before = self.driver.execute_script("return arguments[0].scrollTop", scroll_area)
                scroll_height_before = self.driver.execute_script("return arguments[0].scrollHeight", scroll_area)
            except:
                self._log(f"⚠️  스크롤 위치 읽기 실패")
                break
            
            # 스크롤 끝까지 내리기
            self.driver.execute_script("arguments[0].scrollTop = arguments[0].scrollHeight;", scroll_area)
            time.sleep(2)
            
            # 스크롤 후 위치
            try:
                scroll_after = self.driver.execute_script("return arguments[0].scrollTop", scroll_area)
                scroll_height_after = self.driver.execute_script("return arguments[0].scrollHeight", scroll_area)
            except:
                scroll_after = scroll_before
                scroll_height_after = scroll_height_before
            
            # 매물 수 확인
            try:
                items = self.driver.find_elements(By.CSS_SELECTOR, "#articleListArea button")
                current_count = len(items)
            except:
                current_count = prev_count
            
            # 로그 출력
            if i == 1:
                self._log(f"  스크롤 {i:3d}회 | 매물: {current_count:3d}개 | 위치: {scroll_before}→{scroll_after} | 높이: {scroll_height_before}→{scroll_height_after}")
            else:
                self._log(f"  스크롤 {i:3d}회 | 매물: {current_count:3d}개 | 위치: {scroll_before}→{scroll_after}")
            
            # 종료 조건
            scroll_changed = (scroll_after > scroll_before) or (scroll_height_after > scroll_height_before)
            data_changed = (current_count > prev_count)
            
            if not scroll_changed and not data_changed:
                no_change_count += 1
                if no_change_count >= 3:
                    self._log("\n✅ 스크롤 완료!")
                    break
            else:
                no_change_count = 0
                if data_changed:
                    self._log(f"    → +{current_count - prev_count}개 추가됨")
            
            prev_count = current_count
        
        # 최종 매물 수 확인
        try:
            items = self.driver.find_elements(By.CSS_SELECTOR, "#articleListArea button")
            final_count = len(items)
            self._log(f"\n📋 최종 매물 수: {final_count}개")
            return final_count
        except:
            self._log(f"\n📋 최종 매물 수: {prev_count}개")
            return prev_count


    
    def extract_data(self) -> pd.DataFrame:
        """
        매물 데이터 추출
        
        Returns:
            pd.DataFrame: 추출된 매물 데이터
        """
        self._log("\n📊 데이터 추출 시작...\n")
        
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
                        self._log(f"  {idx}/{len(items)} 추출 완료...")
            except:
                continue
        
        df = pd.DataFrame(data_list)
        self._log(f"\n✅ {len(df)}개 매물 추출 완료!")
        
        return df
    
    def crawl(self, keyword: str) -> Optional[pd.DataFrame]:
        """
        전체 크롤링 프로세스 실행
        
        Args:
            keyword (str): 검색할 단지명
            
        Returns:
            pd.DataFrame: 크롤링된 데이터
        """
        self._log(f"\n{'='*80}")
        self._log(f"  🏠 '{keyword}' 크롤링 시작")
        self._log(f"{'='*80}")
        
        try:
            # 1. 검색
            if not self.search_complex(keyword):
                return None
            
            # 2. 매물 목록 확인 및 단지명 클릭
            time.sleep(2)  # 검색 후 페이지 로딩 대기
            if not self.check_property_list_exists():
                self._log("\n⚠️  매물 목록이 나타나지 않았습니다. 단지명을 클릭합니다...")
                if self.click_complex_name(keyword):
                    # 클릭 후 다시 확인
                    time.sleep(3)
                    if not self.check_property_list_exists():
                        self._log("⚠️  단지명 클릭 후에도 매물 목록이 나타나지 않습니다.")
                        self._log("   1초 후 다시 확인합니다...")
                        time.sleep(1)
                else:
                    self._log("⚠️  단지명 클릭 실패. 계속 진행합니다...")
            
            # 3. 동일매물 묶기
            #self.click_merge_checkbox()
            
            # 4. 모든 매물 로드
            total_items = self.load_all_items()
            
            # 매물이 0개이고, 아직 매물 목록이 없으면 다시 단지명 클릭 시도
            if total_items == 0:
                self._log("\n⚠️  매물이 0개입니다. 단지명을 다시 클릭합니다...")
                if self.click_complex_name(keyword):
                    time.sleep(3)
                    total_items = self.load_all_items()  # 다시 시도
            
            self._log(f"\n📋 최종 매물 수: {total_items}개\n")
            
            # 5. 데이터 추출
            df = self.extract_data()
            
            return df
            
        except Exception as e:
            self._log(f"\n❌ 크롤링 오류: {e}")
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
            self._log("⚠️  저장할 데이터가 없습니다.")
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
        self._log(f"✅ CSV 저장: {csv_file}")
        
        # Excel 저장
        try:
            excel_file = f"data/{filename_prefix}_{timestamp}.xlsx"
            df.to_excel(excel_file, index=False, engine='openpyxl')
            self._log(f"✅ Excel 저장: {excel_file}")
        except Exception as e:
            self._log(f"⚠️  Excel 저장 실패: {e}")


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

