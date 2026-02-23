#!/usr/bin/env python3
"""
ChromeDriver 사전 캐시 스크립트 (EC2 배포 시 1회 실행)
undetected_chromedriver가 첫 실행 시 ChromeDriver를 다운로드하는데 1-2분 걸립니다.
배포 시 이 스크립트를 실행해 두면, 앱 실행 시 즉시 WebDriver를 사용할 수 있습니다.
"""

import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def main():
    print("🔥 ChromeDriver 워밍업 중... (최초 1회 1-2분 소요)")
    try:
        import undetected_chromedriver as uc
        
        options = uc.ChromeOptions()
        options.add_argument('--headless=new')
        options.add_argument('--no-sandbox')
        options.add_argument('--disable-dev-shm-usage')
        options.add_argument('--disable-gpu')
        
        # EC2 Chrome 경로
        chrome_path = "/usr/bin/google-chrome" if os.path.exists("/usr/bin/google-chrome") else None
        if chrome_path:
            options.binary_location = chrome_path
            import subprocess
            result = subprocess.run([chrome_path, '--version'], capture_output=True, text=True)
            version_main = int(result.stdout.strip().split()[2].split('.')[0])
        else:
            version_main = None
        
        driver = uc.Chrome(options=options, version_main=version_main)
        driver.quit()
        print("✅ ChromeDriver 캐시 완료!")
    except Exception as e:
        print(f"⚠️ 워밍업 실패 (앱 첫 실행 시 자동 다운로드됨): {e}")
        sys.exit(0)  # 실패해도 배포는 계속 (앱에서 직접 받음)

if __name__ == "__main__":
    main()
