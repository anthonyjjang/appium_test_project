#!/usr/bin/env python3
# appium_login_test.py
# 로그인 전용 테스트 프로그램

import os
import time
import unittest
from datetime import datetime
from appium import webdriver
from appium.options.android import UiAutomator2Options
from appium.webdriver.common.appiumby import AppiumBy

# 설정 상수
DEVICE_UDID = "RFCM902ZM9K"
APP_PACKAGE = "com.cesco.oversea.srs.viet"
APP_ACTIVITY = "com.mcnc.bizmob.cesco.SlideFragmentActivity"
WEBVIEW_CONTEXT = "WEBVIEW_com.cesco.oversea.srs.viet"

# 로그인 정보
LOGIN_ID = "c89109"
LOGIN_PASSWORD = "mcnc1234!!"

# 디렉토리 설정
timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
SCREENSHOT_DIR = f"screenshots/login_test_{timestamp}"
os.makedirs(SCREENSHOT_DIR, exist_ok=True)

print("🔑 WEBVIEW 로그인 테스트 프로그램")
print("=" * 60)
print(f"📱 디바이스: {DEVICE_UDID}")
print(f"📦 앱 패키지: {APP_PACKAGE}")
print(f"👤 로그인 ID: {LOGIN_ID}")
print(f"📁 스크린샷 저장: {SCREENSHOT_DIR}")
print("=" * 60)

class LoginTest(unittest.TestCase):
    """로그인 테스트 클래스"""
    
    def setUp(self):
        """테스트 전 설정"""
        self.driver = None
        self.initialize_driver()
    
    def tearDown(self):
        """테스트 후 정리"""
        print("\n🔄 테스트 종료 처리 중...")
        
        # 앱 종료
        self.stop_app()
        
        # 드라이버 종료
        if self.driver:
            try:
                self.driver.quit()
                print("✅ Appium 드라이버 종료 완료")
            except Exception as e:
                print(f"⚠️ 드라이버 종료 중 오류: {e}")
        
        print("🔚 테스트 정리 완료")
    
    def initialize_driver(self):
        """Appium 드라이버 초기화"""
        print("\n🚀 Appium 드라이버 초기화 중...")
        
        capabilities = dict(
            platformName='Android',
            automationName='uiautomator2',
            udid=DEVICE_UDID,
            appPackage=APP_PACKAGE,
            appActivity=APP_ACTIVITY,
            noReset=True,
            fullReset=False,
            # WEBVIEW 관련 설정
            chromedriverAutodownload=True,  # 자동 다운로드 활성화
            chromedriverExecutable='/Users/loveauden/.appium/chromedriver/chromedriver-mac-arm64/chromedriver',
            chromedriverChromeMappingFile=None,  # 자동 매핑 사용
            chromedriverUseSystemExecutable=False,  # 시스템 chromedriver 사용 안함
            skipLogCapture=True,  # 로그 캡처 건너뛰기
            autoWebview=False,  # 수동 웹뷰 전환
            recreateChromeDriverSessions=True,  # 세션 재생성
            ensureWebviewsHavePages=True,  # 웹뷰 페이지 확인
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
        
        try:
            options = UiAutomator2Options().load_capabilities(capabilities)
            self.driver = webdriver.Remote('http://localhost:4723', options=options)
            self.driver.implicitly_wait(10)
            print("✅ 드라이버 초기화 완료")
            return True
        except Exception as e:
            print(f"❌ 드라이버 초기화 실패: {e}")
            return False
    
    def stop_app(self):
        """테스트 완료 후 앱 종료"""
        import subprocess
        print("🔄 앱 종료 중...")
        
        try:
            # 방법 1: Appium을 통한 앱 종료 (권장)
            if self.driver:
                try:
                    # 앱 백그라운드로 보내기 (완전 종료)
                    self.driver.background_app(-1)
                    print("✅ 앱 백그라운드 처리 완료")
                    
                    # 잠시 대기
                    import time
                    time.sleep(1)
                    
                    # 앱 완전 종료
                    self.driver.terminate_app(APP_PACKAGE)
                    print("✅ 앱 완전 종료 완료")
                    
                except Exception as appium_error:
                    print(f"⚠️ Appium을 통한 앱 종료 실패: {appium_error}")
                    print("🔄 adb 명령어로 강제 종료 시도...")
                    
                    # 방법 2: adb를 통한 강제 종료 (백업)
                    result = subprocess.run(
                        ['adb', '-s', DEVICE_UDID, 'shell', 'am', 'force-stop', APP_PACKAGE],
                        capture_output=True, text=True, timeout=10
                    )
                    
                    if result.returncode == 0:
                        print("✅ adb를 통한 앱 강제 종료 완료")
                    else:
                        print(f"❌ adb 앱 종료 실패: {result.stderr}")
            else:
                print("⚠️ 드라이버가 없어 adb로 직접 종료")
                
                # adb를 통한 직접 종료
                result = subprocess.run(
                    ['adb', '-s', DEVICE_UDID, 'shell', 'am', 'force-stop', APP_PACKAGE],
                    capture_output=True, text=True, timeout=10
                )
                
                if result.returncode == 0:
                    print("✅ adb를 통한 앱 종료 완료")
                else:
                    print(f"❌ adb 앱 종료 실패: {result.stderr}")
            
            # 앱 종료 확인
            import time
            time.sleep(1)
            
            # 프로세스 확인
            try:
                check_result = subprocess.run(
                    ['adb', '-s', DEVICE_UDID, 'shell', 'ps | grep', APP_PACKAGE],
                    capture_output=True, text=True, timeout=5
                )
                
                if APP_PACKAGE not in check_result.stdout:
                    print("✅ 앱 종료 확인됨")
                else:
                    print("⚠️ 앱이 여전히 실행 중일 수 있음")
                    
            except Exception:
                print("⚠️ 앱 종료 상태 확인 실패")
                
        except subprocess.TimeoutExpired:
            print("⚠️ 앱 종료 명령 타임아웃")
        except Exception as e:
            print(f"⚠️ 앱 종료 중 오류: {e}")
    
    def safe_screenshot(self, filename):
        """안전한 스크린샷 저장"""
        try:
            filepath = os.path.join(SCREENSHOT_DIR, filename)
            self.driver.save_screenshot(filepath)
            print(f"📸 스크린샷 저장: {filename}")
            return True
        except Exception as e:
            print(f"⚠️ 스크린샷 저장 실패: {e}")
            return False
    
    def switch_to_webview(self):
        """WEBVIEW 컨텍스트로 전환"""
        print("\n🔄 WEBVIEW 컨텍스트 전환 중...")
        
        try:
            # 사용 가능한 컨텍스트 확인
            contexts = self.driver.contexts
            print(f"📋 사용 가능한 컨텍스트: {contexts}")
            
            # WEBVIEW 컨텍스트 찾기
            webview_context = None
            for context in contexts:
                if 'WEBVIEW' in context and APP_PACKAGE in context:
                    webview_context = context
                    break
            
            if not webview_context:
                print("❌ WEBVIEW 컨텍스트를 찾을 수 없음")
                return False
            
            # WEBVIEW로 전환
            print(f"🔄 {webview_context}로 전환 중...")
            self.driver.switch_to.context(webview_context)
            time.sleep(3)
            
            # 전환 확인
            current_context = self.driver.current_context
            if current_context == webview_context:
                print(f"✅ WEBVIEW 전환 성공: {current_context}")
                
                # URL 확인
                try:
                    current_url = self.driver.current_url
                    print(f"🌐 현재 URL: {current_url}")
                except:
                    print("⚠️ URL 정보 없음")
                
                return True
            else:
                print(f"❌ WEBVIEW 전환 실패")
                return False
                
        except Exception as e:
            print(f"❌ WEBVIEW 전환 중 오류: {e}")
            return False
    
    def perform_login(self):
        """로그인 수행"""
        print(f"\n🔑 로그인 시작 - ID: {LOGIN_ID}")
        
        try:
            # 초기 스크린샷
            self.safe_screenshot("01_initial_screen.png")
            
            # 1. 사번 입력 필드 찾기
            print("👤 사번 입력 필드 찾는 중...")
            username_field = None
            
            selectors = [
                "input[placeholder*='사번']",
                "input[type='text']:first-of-type",
                "input[type='text']"
            ]
            
            for selector in selectors:
                try:
                    elements = self.driver.find_elements(AppiumBy.CSS_SELECTOR, selector)
                    for element in elements:
                        if element.is_displayed() and element.is_enabled():
                            username_field = element
                            print(f"✅ 사번 입력 필드 발견: {selector}")
                            break
                    if username_field:
                        break
                except:
                    continue
            
            if not username_field:
                print("❌ 사번 입력 필드를 찾을 수 없음")
                return False
            
            # 사번 입력
            username_field.clear()
            username_field.send_keys(LOGIN_ID)
            print(f"✅ 사번 입력 완료: {LOGIN_ID}")
            time.sleep(1)
            
            # 2. 비밀번호 입력 필드 찾기
            print("🔒 비밀번호 입력 필드 찾는 중...")
            password_field = None
            
            password_selectors = [
                "input[type='password']",
                "input[placeholder*='비밀번호']"
            ]
            
            for selector in password_selectors:
                try:
                    elements = self.driver.find_elements(AppiumBy.CSS_SELECTOR, selector)
                    for element in elements:
                        if element.is_displayed() and element.is_enabled():
                            password_field = element
                            print(f"✅ 비밀번호 입력 필드 발견: {selector}")
                            break
                    if password_field:
                        break
                except:
                    continue
            
            if not password_field:
                print("❌ 비밀번호 입력 필드를 찾을 수 없음")
                return False
            
            # 비밀번호 입력
            password_field.clear()
            password_field.send_keys(LOGIN_PASSWORD)
            print("✅ 비밀번호 입력 완료")
            time.sleep(1)
            
            # 입력 완료 후 스크린샷
            self.safe_screenshot("02_credentials_entered.png")
            
            # 3. 로그인 버튼 찾기 및 클릭
            print("🔘 로그인 버튼 찾는 중...")
            login_button = None
            
            # XPath로 '로그인' 텍스트가 있는 버튼 찾기
            try:
                buttons = self.driver.find_elements(AppiumBy.XPATH, "//button[contains(text(), '로그인')]")
                if buttons:
                    for button in buttons:
                        if button.is_displayed() and button.is_enabled():
                            login_button = button
                            print("✅ 로그인 버튼 발견 (텍스트 기준)")
                            break
            except:
                pass
            
            # CSS 선택자로 로그인 버튼 찾기
            if not login_button:
                button_selectors = [
                    ".btn01",
                    "button[class*='btn']",
                    "button[type='button']"
                ]
                
                for selector in button_selectors:
                    try:
                        elements = self.driver.find_elements(AppiumBy.CSS_SELECTOR, selector)
                        for element in elements:
                            if element.is_displayed() and element.is_enabled():
                                try:
                                    # 버튼 텍스트 확인
                                    if '로그인' in element.text or 'btn01' in element.get_attribute('class'):
                                        login_button = element
                                        print(f"✅ 로그인 버튼 발견: {selector}")
                                        break
                                except:
                                    pass
                        if login_button:
                            break
                    except:
                        continue
            
            if not login_button:
                print("❌ 로그인 버튼을 찾을 수 없음")
                return False
            
            # 로그인 버튼 클릭
            print("🔘 로그인 버튼 클릭 중...")
            login_button.click()
            print("✅ 로그인 버튼 클릭 완료")
            
            # 로그인 처리 대기
            print("⏳ 로그인 처리 대기 중...")
            time.sleep(5)
            
            # 로그인 후 스크린샷
            self.safe_screenshot("03_after_login.png")
            
            # 4. 로그인 결과 확인
            print("🔍 로그인 결과 확인 중...")
            
            try:
                current_url = self.driver.current_url
                print(f"📍 로그인 후 URL: {current_url}")
                
                # URL 변화로 로그인 성공 판단
                if current_url and current_url != "http://localhost/LOG1000":
                    print("✅ 로그인 성공! (URL 변화 감지)")
                    return True
                
                # 메인 화면 요소 확인
                main_indicators = [
                    ".main_content", 
                    ".dashboard", 
                    ".home",
                    ".main-container",
                    "[class*='main']"
                ]
                
                for indicator in main_indicators:
                    try:
                        elements = self.driver.find_elements(AppiumBy.CSS_SELECTOR, indicator)
                        if elements and elements[0].is_displayed():
                            print(f"✅ 로그인 성공! (메인 화면 요소 발견: {indicator})")
                            return True
                    except:
                        continue
                
                # 로그인 실패 요소 확인
                error_indicators = [
                    ".error", 
                    ".alert", 
                    "[class*='error']",
                    "[class*='alert']"
                ]
                
                for indicator in error_indicators:
                    try:
                        elements = self.driver.find_elements(AppiumBy.CSS_SELECTOR, indicator)
                        if elements and elements[0].is_displayed():
                            error_text = elements[0].text
                            print(f"❌ 로그인 실패: {error_text}")
                            return False
                    except:
                        continue
                
                print("⚠️ 로그인 결과 불명확 - 추가 확인 필요")
                return False
                
            except Exception as e:
                print(f"⚠️ 로그인 결과 확인 중 오류: {e}")
                return False
                
        except Exception as e:
            print(f"❌ 로그인 실패: {e}")
            return False
    
    def test_login(self):
        """로그인 테스트 메인 함수"""
        print("\n🚀 로그인 테스트 시작")
        
        # Step 1: WEBVIEW 전환
        webview_success = self.switch_to_webview()
        self.assertTrue(webview_success, "WEBVIEW 전환 실패")
        
        # Step 2: 로그인 수행
        login_success = self.perform_login()
        self.assertTrue(login_success, "로그인 실패")
        
        print("\n🎉 로그인 테스트 완료!")
        print(f"📁 스크린샷 저장 위치: {SCREENSHOT_DIR}")
        print("📝 테스트 요약:")
        print("   ✅ WEBVIEW 컨텍스트 전환")
        print("   ✅ 자동 로그인 수행")
        print("   ✅ 로그인 성공 확인")
        print("   🔄 테스트 종료 후 앱 자동 종료")

def main():
    """메인 함수"""
    unittest.main(verbosity=2)

if __name__ == "__main__":
    main()
