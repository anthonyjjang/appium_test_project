#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
베트남 패키지 로그인 테스트
devices.csv와 users.csv를 이용하여 com.cesco.oversea.srs.viet 패키지 로그인만 수행
"""

import csv
import time
import os
import unittest
from datetime import datetime
from appium import webdriver
from appium.webdriver.common.appiumby import AppiumBy
from appium.options.android import UiAutomator2Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from dotenv import load_dotenv

# 환경변수 로드
load_dotenv()

# 테스트 시작 시간
start_time = datetime.now().strftime('%Y%m%d_%H%M%S')

# 스크린샷 디렉토리 생성
SCREENSHOT_DIR = os.path.join('screenshots', f'vietnam_test_{start_time}')
os.makedirs(SCREENSHOT_DIR, exist_ok=True)

# 테스트 설정
SLEEP_TIME = 3
BASE_URL = "http://10.200.11.143:8080/"
LOGIN_PATH = 'LOG1000'

def load_device_config():
    """devices.csv에서 베트남 패키지 설정 로드"""
    with open('devices.csv', 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            if row['app_package'] == 'com.cesco.oversea.srs.viet':
                return row
    return None

def load_user_config():
    """users.csv에서 베트남 사용자 설정 로드"""
    with open('users.csv', 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            if row['country_code'] == 'VN':
                return row
    return None

def get_driver(device_config):
    """Appium 드라이버 생성"""
    capabilities = dict(
        platformName=device_config['platform_name'],
        automationName='uiautomator2',
        udid=device_config['udid'],
        appPackage=device_config['app_package'],
        appActivity=device_config['app_activity'],
        noReset=True,
        fullReset=False,
        uiautomator2ServerInstallTimeout=60000,
        uiautomator2ServerLaunchTimeout=60000,
        adbExecTimeout=60000,
        # WEBVIEW 관련 설정 (강화된 Chromedriver 지원)
        chromedriverAutodownload=True,
        chromedriverExecutable='/Users/loveauden/.appium/chromedriver/chromedriver-mac-arm64/chromedriver',  # 직접 경로 지정
        chromedriverChromeMappingFile=None,  # 자동 매핑 사용
        skipLogCapture=True,  # 로그 캡처 건너뛰기
        autoWebview=False,  # 수동 웹뷰 전환
        recreateChromeDriverSessions=True,  # 세션 재생성
        chromeOptions={
            'w3c': False,
            'args': [
                '--disable-dev-shm-usage', 
                '--no-sandbox',
                '--disable-web-security',
                '--disable-features=VizDisplayCompositor',
                '--disable-extensions',
                '--disable-plugins'
            ]
        }
    )
    
    options = UiAutomator2Options().load_capabilities(capabilities)
    driver = webdriver.Remote('http://localhost:4723', options=options)
    driver.implicitly_wait(10)
    return driver


def get_webview_contexts(driver):
    """WebView 컨텍스트 목록 조회 및 로그 출력"""
    try:
        print("🔍 WebView 컨텍스트 목록 조회 중...")
        contexts = driver.contexts
        print(f"📋 전체 컨텍스트 목록: {contexts}")
        
        # WebView 컨텍스트만 필터링
        #webview_contexts = [ctx for ctx in contexts if 'WEBVIEW' in ctx]
        print(f"🌐 WebView 컨텍스트 목록: {contexts}")
        
        # 베트남 패키지 관련 WebView 찾기
        vietnam_webviews = [ctx for ctx in webview_contexts if 'com.cesco.oversea.srs.viet' in ctx]
        if vietnam_webviews:
            print(f"🇻🇳 베트남 패키지 WebView: {vietnam_webviews}")
        else:
            print("⚠️ 베트남 패키지 WebView를 찾을 수 없습니다.")
        
        # 각 WebView 컨텍스트 상세 분석
        print("\n📊 WebView 컨텍스트 상세 분석:")
        for i, context in enumerate(webview_contexts, 1):
            print(f"  {i}. {context}")
            if 'com.cesco.oversea.srs.viet' in context:
                print(f"     ✅ 베트남 패키지 관련")
            elif 'com.cesco.oversea.srs' in context:
                print(f"     📦 SRS 패키지 관련")
            else:
                print(f"     ❓ 기타 WebView")
        
        return webview_contexts, vietnam_webviews
        
    except Exception as e:
        print(f"❌ WebView 컨텍스트 조회 실패: {e}")
        return [], []

def go_login_page(driver, wait):
    """로그인 페이지 이동"""
    try:
        url = BASE_URL + LOGIN_PATH
        print(f"[로그페이지 이동]: {url}")
        if url:
            driver.get(url)
            time.sleep(SLEEP_TIME)
        print(f"[로그페이지 이동 성공]: {url}")
    except Exception as e:
        print(f"[로그페이지 이동 실패]: {e}")

def login(driver, wait, user_config):
    """로그인 수행"""
    try:
        print("🔐 Starting login process...")
        
        # 사용자 ID 입력
        print("📝 Entering user ID...")
        user_id = wait.until(EC.presence_of_element_located((AppiumBy.CSS_SELECTOR, ".log_id input")))
        user_id.clear()
        user_id.send_keys(user_config['user_id'])

        # 비밀번호 입력
        print("🔒 Entering password...")
        user_pw = wait.until(EC.presence_of_element_located((AppiumBy.XPATH, "//input[@type='password']")))
        user_pw.clear()
        user_pw.send_keys(user_config['user_pw'])

        # 로그인 버튼 클릭 (재시도 로직 포함)
        for attempt in range(3):
            try:
                print(f"🔁 로그인 버튼 탐색 중... (시도 {attempt+1})")
                wait = WebDriverWait(driver, 10)
                login_btn = wait.until(EC.element_to_be_clickable((AppiumBy.CSS_SELECTOR, ".btn01")))
                driver.execute_script("arguments[0].scrollIntoView(true);", login_btn)
                login_btn.click()
                print("✅ 로그인 버튼 클릭 성공")
                time.sleep(SLEEP_TIME)
                screenshot_path = os.path.join(SCREENSHOT_DIR, f"LOGIN_pass.png")
                driver.save_screenshot(screenshot_path)
                print("[로그인] 완료")
                return True
            except Exception as e:
                print(f"❌ 실패: {e}")
                time.sleep(SLEEP_TIME)
                screenshot_path = os.path.join(SCREENSHOT_DIR, f"LOGIN_fail.png")
                print(f"[로그인 실패]: {e}")
    except Exception as e:
        screenshot_path = os.path.join(SCREENSHOT_DIR, f"LOGIN_fail.png")
        print(f"[로그인 실패]: {e}")
        return False

# unittest 실행
class TestVietnamLogin(unittest.TestCase):
    def test_01_login(self):
        """베트남 패키지 로그인 테스트"""
        print("🇻🇳 Vietnam Package Login Test")
        print("=" * 50)
        
        # 설정 로드
        device_config = load_device_config()
        user_config = load_user_config()
        
        if not device_config:
            print("❌ Device config not found for Vietnam package")
            return
        
        if not user_config:
            print("❌ User config not found for Vietnam")
            return
        
        print(f"📱 Device: {device_config['device_id']} ({device_config['udid']})")
        print(f"👤 User: {user_config['user_id']} ({user_config['country_code']})")
        print(f"📦 Package: {device_config['app_package']}")
        
        driver = None
        try:
            # 드라이버 생성
            print("\n🚀 Starting Appium driver...")
            driver = get_driver(device_config)
            wait = WebDriverWait(driver, 20)
            
            # 앱 로딩 대기
            print("⏳ Waiting for app to load...")
            time.sleep(10)
            
            # WebView 컨텍스트 목록 조회
            print("\n🔍 WebView 컨텍스트 확인 중...")
            webview_contexts, vietnam_webviews = get_webview_contexts(driver)
            
            # WebView 컨텍스트로 전환
            print("🔄 Switching to WebView context...")
            if vietnam_webviews:
                target_webview = vietnam_webviews[0]  # 첫 번째 베트남 WebView 사용
                print(f"🎯 Using WebView: {target_webview}")
                driver.switch_to.context(target_webview)
            else:
                print(f"⚠️ 베트남 WebView를 찾을 수 없어 기본 WebView 사용: {user_config['webview_name']}")
                driver.switch_to.context(user_config['webview_name'])
            
            # WebView 전환 후 컨텍스트 재확인
            print("🔍 WebView 전환 후 컨텍스트 재확인...")
            current_context = driver.current_context
            print(f"📍 현재 컨텍스트: {current_context}")
            
            # 전환 후 전체 컨텍스트 목록 재확인
            print("\n🔄 전환 후 전체 컨텍스트 목록:")
            final_contexts = driver.contexts
            print(f"📋 최종 컨텍스트 목록: {final_contexts}")
            
            # 로그인 페이지로 이동
            go_login_page(driver, wait)
            
            # 로그인 수행
            success = login(driver, wait, user_config)
            
            if success:
                print("\n✅ Test completed successfully!")
            else:
                print("\n❌ Test failed!")
                
        except Exception as e:
            print(f"❌ Test error: {str(e)}")
        
        finally:
            if driver:
                print("\n🔄 Closing driver...")
                driver.quit()

if __name__ == "__main__":
    unittest.main()
