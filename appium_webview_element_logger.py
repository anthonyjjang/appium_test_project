# appium_webview_element_logger.py
# 하이브리드 앱 WEBVIEW 요소 로깅 전용 Appium 테스트 프로그램

import unittest
import time
import os
import json
import logging
from datetime import datetime
from appium import webdriver
from appium.webdriver.common.appiumby import AppiumBy
from appium.options.android import UiAutomator2Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

# 테스트 시작 시간
start_time = datetime.now().strftime('%Y%m%d_%H%M%S')

# 디렉토리 설정
SCREENSHOT_DIR = os.path.join('screenshots', f'webview_test_{start_time}')
LOG_DIR = os.path.join('logs', f'webview_test_{start_time}')
ELEMENT_LOG_FILE = os.path.join(LOG_DIR, 'webview_elements.json')
DETAILED_LOG_FILE = os.path.join(LOG_DIR, 'detailed_test.log')

# 디렉토리 생성
os.makedirs(SCREENSHOT_DIR, exist_ok=True)
os.makedirs(LOG_DIR, exist_ok=True)

# 앱 설정
APP_PACKAGE = 'com.cesco.oversea.srs.viet'
APP_ACTIVITY = 'com.mcnc.bizmob.cesco.SlideFragmentActivity'
DEVICE_UDID = 'RFCM902ZM9K'
WEBVIEW_CONTEXT = 'WEBVIEW_com.cesco.oversea.srs.viet'

# 로깅 설정
def setup_logging():
    """상세 로깅 설정"""
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler(DETAILED_LOG_FILE, encoding='utf-8'),
            logging.StreamHandler()
        ]
    )
    return logging.getLogger(__name__)

logger = setup_logging()

class WebViewElementLogger:
    """WEBVIEW 요소 로깅 클래스"""
    
    def __init__(self):
        self.driver = None
        self.wait = None
        self.element_data = {
            'session_info': {
                'start_time': start_time,
                'app_package': APP_PACKAGE,
                'app_activity': APP_ACTIVITY,
                'device_udid': DEVICE_UDID,
                'webview_context': WEBVIEW_CONTEXT
            },
            'context_switches': [],
            'scanned_pages': [],
            'all_elements': []
        }
    
    def safe_screenshot(self, filepath):
        """안전한 스크린샷 저장"""
        try:
            self.driver.save_screenshot(filepath)
            logger.info(f"📸 스크린샷 저장: {filepath}")
            return True
        except Exception as e:
            logger.warning(f"⚠️ 스크린샷 저장 실패: {e}")
            logger.info(f"💡 스크린샷 파일: {filepath}")
            return False
    
    def force_stop_app(self):
        """기존 앱 강제 종료 (데이터 유지)"""
        import subprocess
        logger.info("🔄 기존 앱 강제 종료 중 (데이터 보존)...")
        
        try:
            # adb를 사용하여 앱 강제 종료 (데이터 유지)
            result = subprocess.run(
                ['adb', '-s', DEVICE_UDID, 'shell', 'am', 'force-stop', APP_PACKAGE],
                capture_output=True, text=True, timeout=10
            )
            
            if result.returncode == 0:
                logger.info(f"✅ 앱 강제 종료 완료: {APP_PACKAGE}")
                logger.info("💾 앱 데이터 유지됨 (로그인 상태, 설정 등 보존)")
                
                # 잠시 대기 (앱 완전 종료 대기)
                import time
                time.sleep(2)
                
                # 앱 프로세스 확인
                check_result = subprocess.run(
                    ['adb', '-s', DEVICE_UDID, 'shell', 'ps | grep', APP_PACKAGE],
                    capture_output=True, text=True, timeout=5
                )
                
                if APP_PACKAGE in check_result.stdout:
                    logger.warning("⚠️ 앱이 여전히 실행 중일 수 있음")
                else:
                    logger.info("✅ 앱 완전 종료 확인")
            else:
                logger.warning(f"⚠️ 앱 강제 종료 실패: {result.stderr}")
                
        except subprocess.TimeoutExpired:
            logger.warning("⚠️ 앱 종료 명령 타임아웃")
        except Exception as e:
            logger.warning(f"⚠️ 앱 종료 중 오류: {e}")
        
        logger.info("🔄 2초 대기 후 앱 재시작 (데이터 유지)...")
        import time
        time.sleep(2)
    
    def wait_for_app_launch(self):
        """앱 시작 대기"""
        logger.info("⏳ 앱 시작 대기 중...")
        import time
        
        # 앱 시작 대기 (최대 15초)
        start_time = time.time()
        timeout = 15
        
        while time.time() - start_time < timeout:
            try:
                # 현재 액티비티 확인
                current_activity = self.driver.current_activity
                logger.info(f"📱 현재 액티비티: {current_activity}")
                
                # 목표 액티비티 또는 관련 액티비티 확인
                if APP_ACTIVITY in current_activity or 'cesco' in current_activity.lower():
                    logger.info("✅ 앱 시작 완료")
                    time.sleep(2)  # 추가 안정화 대기
                    return True
                    
            except Exception as e:
                logger.info(f"🔄 앱 시작 확인 중... ({int(time.time() - start_time)}초)")
            
            time.sleep(1)
        
        logger.warning("⚠️ 앱 시작 대기 타임아웃")
        return False
        
    def initialize_driver(self):
        """Appium 드라이버 초기화"""
        logger.info("🚀 Appium 드라이버 초기화 시작")
        
        capabilities = dict(
            platformName='Android',
            automationName='uiautomator2',
            udid=DEVICE_UDID,
            appPackage=APP_PACKAGE,
            appActivity=APP_ACTIVITY,
            noReset=True,  # 앱 데이터 유지 (초기화하지 않음)
            fullReset=False,  # 전체 초기화하지 않음
            forceAppLaunch=True,  # 앱 강제 재시작
            shouldTerminateApp=True,  # 기존 앱 종료
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
        
        try:
            options = UiAutomator2Options().load_capabilities(capabilities)
            self.driver = webdriver.Remote('http://localhost:4723', options=options)
            self.driver.implicitly_wait(10)
            self.wait = WebDriverWait(self.driver, 30)
            
            logger.info("✅ Appium 드라이버 초기화 완료")
            logger.info(f"📱 연결된 디바이스: {DEVICE_UDID}")
            logger.info(f"📦 앱 패키지: {APP_PACKAGE}")
            logger.info(f"🎯 앱 액티비티: {APP_ACTIVITY}")
            
            # 앱 시작 대기
            self.wait_for_app_launch()
            
            return True
            
        except Exception as e:
            logger.error(f"❌ Appium 드라이버 초기화 실패: {e}")
            return False
    
    def scan_contexts(self):
        """컨텍스트 스캔 및 로깅"""
        logger.info("🔍 Step 1: 컨텍스트 스캔 시작")
        
        try:
            # 현재 컨텍스트 확인
            current_context = self.driver.current_context
            available_contexts = self.driver.contexts
            
            context_info = {
                'timestamp': datetime.now().isoformat(),
                'current_context': current_context,
                'available_contexts': available_contexts,
                'webview_contexts': [ctx for ctx in available_contexts if 'WEBVIEW' in ctx],
                'native_contexts': [ctx for ctx in available_contexts if 'NATIVE' in ctx]
            }
            
            self.element_data['context_switches'].append(context_info)
            
            logger.info(f"📱 현재 컨텍스트: {current_context}")
            logger.info(f"📋 사용 가능한 컨텍스트: {available_contexts}")
            logger.info(f"🌐 웹뷰 컨텍스트 개수: {len(context_info['webview_contexts'])}")
            logger.info(f"📲 네이티브 컨텍스트 개수: {len(context_info['native_contexts'])}")
            
            # 스크린샷 저장 (안전하게)
            screenshot_path = os.path.join(SCREENSHOT_DIR, "01_initial_context.png")
            self.safe_screenshot(screenshot_path)
            
            return context_info
            
        except Exception as e:
            logger.error(f"❌ 컨텍스트 스캔 실패: {e}")
            return None
    
    def switch_to_webview(self, max_retries=3):
        """WEBVIEW 컨텍스트로 전환 (강화된 재시도 로직)"""
        logger.info("🔄 Step 2: WEBVIEW 컨텍스트 전환 시작")
        
        for retry in range(max_retries):
            try:
                logger.info(f"🔄 웹뷰 전환 시도 {retry + 1}/{max_retries}")
                
                contexts = self.driver.contexts
                webview_contexts = [ctx for ctx in contexts if 'WEBVIEW' in ctx]
                
                if not webview_contexts:
                    logger.warning("⚠️ 사용 가능한 WEBVIEW 컨텍스트가 없음")
                    if retry < max_retries - 1:
                        logger.info("⏳ 3초 후 재시도...")
                        time.sleep(3)
                        continue
                    return False
                
                # 첫 번째 웹뷰 컨텍스트 선택 (또는 지정된 컨텍스트 찾기)
                target_webview = None
                for ctx in webview_contexts:
                    if WEBVIEW_CONTEXT in ctx or APP_PACKAGE in ctx:
                        target_webview = ctx
                        break
                
                if not target_webview:
                    target_webview = webview_contexts[0]
                    logger.info(f"🎯 지정된 웹뷰를 찾을 수 없어 첫 번째 웹뷰 사용: {target_webview}")
                
                logger.info(f"🔄 웹뷰 컨텍스트로 전환 시도: {target_webview}")
                
                # 웹뷰로 전환
                self.driver.switch_to.context(target_webview)
                time.sleep(3)  # 웹뷰 로딩 대기 (증가)
                
                # 전환 확인
                current_context = self.driver.current_context
                if current_context == target_webview:
                    logger.info(f"✅ 웹뷰 컨텍스트 전환 성공: {current_context}")
                    
                    # 웹뷰 접근 테스트
                    try:
                        # 간단한 웹 요소 접근 테스트
                        body_elements = self.driver.find_elements(AppiumBy.TAG_NAME, "body")
                        logger.info(f"✅ 웹뷰 접근 테스트 성공: {len(body_elements)}개 body 요소 발견")
                    except Exception as web_e:
                        logger.warning(f"⚠️ 웹뷰 접근 테스트 실패: {web_e}")
                        logger.info("💡 웹뷰로 전환되었지만 웹 요소에 즉시 접근할 수 없음")
                    
                    # 웹뷰 컨텍스트 정보 저장
                    switch_info = {
                        'timestamp': datetime.now().isoformat(),
                        'action': 'switch_to_webview',
                        'target_context': target_webview,
                        'success': True,
                        'current_context': current_context,
                        'retry_count': retry + 1
                    }
                    self.element_data['context_switches'].append(switch_info)
                    
                    # 스크린샷 저장 (안전하게)
                    screenshot_path = os.path.join(SCREENSHOT_DIR, "02_webview_context.png")
                    self.safe_screenshot(screenshot_path)
                    
                    return True
                else:
                    logger.error(f"❌ 웹뷰 컨텍스트 전환 실패: 요청={target_webview}, 실제={current_context}")
                    if retry < max_retries - 1:
                        logger.info("⏳ 2초 후 재시도...")
                        time.sleep(2)
                        continue
                    
            except Exception as e:
                error_msg = str(e)
                logger.error(f"❌ 웹뷰 컨텍스트 전환 중 오류: {error_msg}")
                
                # Chromedriver 관련 오류 감지
                if 'chromedriver' in error_msg.lower() or 'chrome' in error_msg.lower():
                    logger.error("🔧 Chromedriver 관련 오류 감지")
                    logger.error("💡 해결 방법:")
                    logger.error("   1. 앱을 완전히 종료하고 다시 실행")
                    logger.error("   2. Appium 서버 재시작")
                    logger.error("   3. 호환되는 Chromedriver 수동 설치")
                    
                    # Chromedriver 오류는 재시도해도 해결되지 않으므로 중단
                    break
                
                # 오류 정보 저장
                error_info = {
                    'timestamp': datetime.now().isoformat(),
                    'action': 'switch_to_webview',
                    'success': False,
                    'error': error_msg,
                    'retry_count': retry + 1
                }
                self.element_data['context_switches'].append(error_info)
                
                if retry < max_retries - 1:
                    logger.info(f"⏳ {3}초 후 재시도...")
                    time.sleep(3)
                    continue
        
        logger.warning("❌ 모든 웹뷰 컨텍스트 전환 시도 실패")
        logger.info("🔄 네이티브 컨텍스트로 폴백하여 테스트 계속")
        
        # 네이티브 컨텍스트로 명시적 전환
        try:
            self.driver.switch_to.context('NATIVE_APP')
            logger.info("✅ 네이티브 컨텍스트로 폴백 완료")
        except Exception as native_e:
            logger.error(f"❌ 네이티브 컨텍스트 전환도 실패: {native_e}")
        
        return False
    
    def perform_login(self, user_id="c89109", password="mcnc1234!!"):
        """실제 로그인 수행"""
        logger.info("🔑 Step 2.5: 로그인 테스트 시작")
        
        try:
            # 1. 사번 입력 필드 찾기
            logger.info(f"👤 사번 입력: {user_id}")
            
            # 사번 입력 필드 선택자들 시도
            username_selectors = [
                "input[placeholder='사번 입력']",
                "input[type='text']",
                "input:first-of-type"
            ]
            
            username_field = None
            for selector in username_selectors:
                try:
                    elements = self.driver.find_elements(AppiumBy.CSS_SELECTOR, selector)
                    if elements:
                        # 보이는 요소 중 첫 번째 선택
                        for element in elements:
                            if element.is_displayed() and element.is_enabled():
                                username_field = element
                                logger.info(f"✅ 사번 입력 필드 발견: {selector}")
                                break
                        if username_field:
                            break
                except Exception:
                    continue
            
            if not username_field:
                logger.error("❌ 사번 입력 필드를 찾을 수 없음")
                return False
            
            # 사번 입력
            username_field.clear()
            username_field.send_keys(user_id)
            logger.info(f"✅ 사번 입력 완료: {user_id}")
            
            # 2. 비밀번호 입력 필드 찾기
            logger.info(f"🔒 비밀번호 입력")
            
            password_selectors = [
                "input[type='password']",
                "input[placeholder='비밀번호 입력']"
            ]
            
            password_field = None
            for selector in password_selectors:
                try:
                    elements = self.driver.find_elements(AppiumBy.CSS_SELECTOR, selector)
                    if elements:
                        for element in elements:
                            if element.is_displayed() and element.is_enabled():
                                password_field = element
                                logger.info(f"✅ 비밀번호 입력 필드 발견: {selector}")
                                break
                        if password_field:
                            break
                except Exception:
                    continue
            
            if not password_field:
                logger.error("❌ 비밀번호 입력 필드를 찾을 수 없음")
                return False
            
            # 비밀번호 입력
            password_field.clear()
            password_field.send_keys(password)
            logger.info("✅ 비밀번호 입력 완료")
            
            # 3. 로그인 버튼 찾기 및 클릭
            logger.info("🔘 로그인 버튼 클릭")
            
            login_selectors = [
                "button:contains('로그인')",
                ".btn01",
                "button[class*='btn']",
                "button[type='button']"
            ]
            
            login_button = None
            for selector in login_selectors:
                try:
                    if "contains" in selector:
                        # text 내용으로 찾기
                        elements = self.driver.find_elements(AppiumBy.XPATH, "//button[contains(text(), '로그인')]")
                    else:
                        elements = self.driver.find_elements(AppiumBy.CSS_SELECTOR, selector)
                    
                    if elements:
                        for element in elements:
                            if element.is_displayed() and element.is_enabled():
                                # '로그인' 텍스트가 있는 버튼 우선 선택
                                try:
                                    if '로그인' in element.text or 'btn01' in element.get_attribute('class'):
                                        login_button = element
                                        logger.info(f"✅ 로그인 버튼 발견: {selector}")
                                        break
                                except:
                                    pass
                        if login_button:
                            break
                except Exception:
                    continue
            
            if not login_button:
                logger.error("❌ 로그인 버튼을 찾을 수 없음")
                return False
            
            # 로그인 전 스크린샷
            screenshot_path = os.path.join(SCREENSHOT_DIR, "login_before.png")
            self.safe_screenshot(screenshot_path)
            
            # 로그인 버튼 클릭
            login_button.click()
            logger.info("✅ 로그인 버튼 클릭 완료")
            
            # 로그인 처리 대기
            time.sleep(5)
            
            # 로그인 후 스크린샷
            screenshot_path = os.path.join(SCREENSHOT_DIR, "login_after.png")
            self.safe_screenshot(screenshot_path)
            
            # 4. 로그인 결과 확인
            logger.info("🔍 로그인 결과 확인")
            
            # 현재 URL 확인
            try:
                current_url = self.driver.current_url
                logger.info(f"📍 로그인 후 URL: {current_url}")
                
                # 로그인 성공 판단 (URL 변화 또는 특정 요소 존재)
                if current_url and current_url != "http://localhost/LOG1000":
                    logger.info("✅ 로그인 성공 (URL 변화 감지)")
                    login_success = True
                else:
                    # 메인 화면 요소 확인
                    main_elements = self.driver.find_elements(AppiumBy.CSS_SELECTOR, ".main_content, .dashboard, .home")
                    if main_elements:
                        logger.info("✅ 로그인 성공 (메인 화면 요소 발견)")
                        login_success = True
                    else:
                        logger.warning("⚠️ 로그인 상태 불명확")
                        login_success = False
                        
            except Exception as e:
                logger.warning(f"⚠️ 로그인 결과 확인 중 오류: {e}")
                login_success = False
            
            # 로그인 정보 기록
            login_info = {
                'timestamp': datetime.now().isoformat(),
                'action': 'login_attempt',
                'user_id': user_id,
                'success': login_success,
                'url_after_login': current_url if 'current_url' in locals() else 'unknown'
            }
            self.element_data['context_switches'].append(login_info)
            
            if login_success:
                logger.info("🎉 로그인 테스트 성공!")
            else:
                logger.warning("⚠️ 로그인 테스트 결과 확인 필요")
                
            return login_success
            
        except Exception as e:
            logger.error(f"❌ 로그인 테스트 실패: {e}")
            
            # 오류 정보 기록
            error_info = {
                'timestamp': datetime.now().isoformat(),
                'action': 'login_attempt',
                'user_id': user_id,
                'success': False,
                'error': str(e)
            }
            self.element_data['context_switches'].append(error_info)
            
            return False
    
    def scan_page_elements(self, page_name="unknown"):
        """현재 페이지의 모든 웹 요소 스캔"""
        logger.info(f"🔍 Step 3: 페이지 요소 스캔 시작 - {page_name}")
        
        page_data = {
            'page_name': page_name,
            'timestamp': datetime.now().isoformat(),
            'url': None,
            'title': None,
            'elements': {
                'inputs': [],
                'buttons': [],
                'links': [],
                'forms': [],
                'selects': [],
                'textareas': [],
                'images': [],
                'other_elements': []
            },
            'total_elements': 0
        }
        
        try:
            # 페이지 기본 정보 수집
            try:
                page_data['url'] = self.driver.current_url
                logger.info(f"🌐 현재 URL: {page_data['url']}")
            except:
                logger.warning("⚠️ URL 정보를 가져올 수 없음")
            
            try:
                page_data['title'] = self.driver.title
                logger.info(f"📄 페이지 제목: {page_data['title']}")
            except:
                logger.warning("⚠️ 페이지 제목을 가져올 수 없음")
            
            # 다양한 타입의 요소들 스캔
            element_selectors = {
                'inputs': [
                    "input[type='text']",
                    "input[type='email']", 
                    "input[type='password']",
                    "input[type='number']",
                    "input[type='tel']",
                    "input[type='search']",
                    "input[type='url']",
                    "input:not([type])",
                    "input"
                ],
                'buttons': [
                    "button",
                    "input[type='button']",
                    "input[type='submit']",
                    "[role='button']",
                    ".btn",
                    ".button"
                ],
                'links': [
                    "a[href]",
                    "[role='link']"
                ],
                'forms': [
                    "form"
                ],
                'selects': [
                    "select",
                    "[role='combobox']",
                    "[role='listbox']"
                ],
                'textareas': [
                    "textarea"
                ],
                'images': [
                    "img",
                    "[role='img']"
                ]
            }
            
            # 각 요소 타입별로 스캔
            for element_type, selectors in element_selectors.items():
                logger.info(f"🔍 {element_type.upper()} 요소 스캔 중...")
                
                for selector in selectors:
                    try:
                        elements = self.driver.find_elements(AppiumBy.CSS_SELECTOR, selector)
                        logger.info(f"   📍 '{selector}' 선택자로 {len(elements)}개 요소 발견")
                        
                        for i, element in enumerate(elements):
                            element_info = self.extract_element_info(element, element_type, selector, i)
                            if element_info and element_info not in page_data['elements'][element_type]:
                                page_data['elements'][element_type].append(element_info)
                                
                    except Exception as e:
                        logger.debug(f"   ⚠️ 선택자 '{selector}' 스캔 실패: {e}")
                
                logger.info(f"✅ {element_type.upper()} 요소 스캔 완료: {len(page_data['elements'][element_type])}개")
            
            # 기타 요소들 스캔
            logger.info("🔍 기타 요소 스캔 중...")
            other_selectors = ['div', 'span', 'p', 'h1', 'h2', 'h3', 'h4', 'h5', 'h6', 'label']
            
            for selector in other_selectors:
                try:
                    elements = self.driver.find_elements(AppiumBy.TAG_NAME, selector)
                    # 텍스트가 있거나 특별한 속성이 있는 요소만 수집
                    for i, element in enumerate(elements[:5]):  # 최대 5개만
                        element_info = self.extract_element_info(element, 'other', selector, i)
                        if element_info and (element_info.get('text') or element_info.get('id') or element_info.get('class')):
                            page_data['elements']['other_elements'].append(element_info)
                except:
                    continue
            
            # 전체 요소 개수 계산
            page_data['total_elements'] = sum(len(elements) for elements in page_data['elements'].values())
            
            logger.info(f"📊 페이지 요소 스캔 완료:")
            logger.info(f"   📝 Input 요소: {len(page_data['elements']['inputs'])}개")
            logger.info(f"   🔘 Button 요소: {len(page_data['elements']['buttons'])}개")
            logger.info(f"   🔗 Link 요소: {len(page_data['elements']['links'])}개")
            logger.info(f"   📋 Form 요소: {len(page_data['elements']['forms'])}개")
            logger.info(f"   📝 Select 요소: {len(page_data['elements']['selects'])}개")
            logger.info(f"   📄 Textarea 요소: {len(page_data['elements']['textareas'])}개")
            logger.info(f"   🖼️ Image 요소: {len(page_data['elements']['images'])}개")
            logger.info(f"   📦 기타 요소: {len(page_data['elements']['other_elements'])}개")
            logger.info(f"   🔢 총 요소 개수: {page_data['total_elements']}개")
            
            # 페이지 데이터 저장
            self.element_data['scanned_pages'].append(page_data)
            
            # 모든 요소를 전체 요소 리스트에도 추가
            for element_type, elements in page_data['elements'].items():
                for element in elements:
                    element['page_name'] = page_name
                    element['element_type_category'] = element_type
                    self.element_data['all_elements'].append(element)
            
            # 페이지별 스크린샷 저장 (안전하게)
            screenshot_path = os.path.join(SCREENSHOT_DIR, f"03_{page_name}_elements.png")
            self.safe_screenshot(screenshot_path)
            
            return page_data
            
        except Exception as e:
            logger.error(f"❌ 페이지 요소 스캔 실패: {e}")
            return None
    
    def extract_element_info(self, element, element_type, selector, index):
        """개별 요소의 상세 정보 추출"""
        try:
            element_info = {
                'index': index,
                'selector_used': selector,
                'element_type': element_type,
                'tag_name': None,
                'id': None,
                'class': None,
                'name': None,
                'type': None,
                'value': None,
                'text': None,
                'placeholder': None,
                'href': None,
                'src': None,
                'alt': None,
                'title': None,
                'role': None,
                'is_displayed': False,
                'is_enabled': False,
                'location': None,
                'size': None,
                'attributes': {}
            }
            
            # 기본 정보
            element_info['tag_name'] = element.tag_name
            element_info['is_displayed'] = element.is_displayed()
            element_info['is_enabled'] = element.is_enabled()
            
            # 위치 및 크기 정보
            try:
                element_info['location'] = element.location
                element_info['size'] = element.size
            except:
                pass
            
            # 주요 속성들 추출
            attributes_to_check = [
                'id', 'class', 'name', 'type', 'value', 'placeholder', 
                'href', 'src', 'alt', 'title', 'role', 'data-*'
            ]
            
            for attr in attributes_to_check:
                try:
                    attr_value = element.get_attribute(attr)
                    if attr_value:
                        element_info[attr] = attr_value
                        element_info['attributes'][attr] = attr_value
                except:
                    pass
            
            # 텍스트 내용
            try:
                text = element.text
                if text and text.strip():
                    element_info['text'] = text.strip()
            except:
                pass
            
            # innerHTML 내용 (일부만)
            try:
                inner_html = element.get_attribute('innerHTML')
                if inner_html and len(inner_html) < 200:
                    element_info['innerHTML'] = inner_html
            except:
                pass
            
            return element_info
            
        except Exception as e:
            logger.debug(f"요소 정보 추출 실패 (인덱스 {index}): {e}")
            return None
    
    def log_element_summary(self):
        """요소 스캔 결과 요약 로깅"""
        logger.info("📊 Step 4: 요소 스캔 결과 요약")
        
        if not self.element_data['all_elements']:
            logger.warning("⚠️ 스캔된 요소가 없습니다")
            return
        
        # 요소 타입별 통계
        type_stats = {}
        for element in self.element_data['all_elements']:
            element_type = element.get('element_type', 'unknown')
            type_stats[element_type] = type_stats.get(element_type, 0) + 1
        
        logger.info("📈 요소 타입별 통계:")
        for element_type, count in sorted(type_stats.items()):
            logger.info(f"   {element_type}: {count}개")
        
        # 중요한 요소들 상세 로깅
        logger.info("📝 주요 Input 요소들:")
        inputs = [e for e in self.element_data['all_elements'] if e.get('element_type') == 'inputs']
        for i, input_elem in enumerate(inputs[:10]):  # 최대 10개
            logger.info(f"   Input {i+1}: type='{input_elem.get('type', 'text')}', "
                       f"id='{input_elem.get('id', 'N/A')}', "
                       f"name='{input_elem.get('name', 'N/A')}', "
                       f"placeholder='{input_elem.get('placeholder', 'N/A')}'")
        
        logger.info("🔘 주요 Button 요소들:")
        buttons = [e for e in self.element_data['all_elements'] if e.get('element_type') == 'buttons']
        for i, button_elem in enumerate(buttons[:10]):  # 최대 10개
            logger.info(f"   Button {i+1}: text='{button_elem.get('text', 'N/A')}', "
                       f"type='{button_elem.get('type', 'N/A')}', "
                       f"id='{button_elem.get('id', 'N/A')}', "
                       f"class='{button_elem.get('class', 'N/A')}'")
    
    def save_element_data(self):
        """요소 데이터를 JSON 파일로 저장"""
        logger.info("💾 Step 5: 요소 데이터 저장")
        
        try:
            # 세션 완료 정보 추가
            self.element_data['session_info']['end_time'] = datetime.now().isoformat()
            self.element_data['session_info']['total_elements_found'] = len(self.element_data['all_elements'])
            self.element_data['session_info']['total_pages_scanned'] = len(self.element_data['scanned_pages'])
            
            # JSON 파일로 저장
            with open(ELEMENT_LOG_FILE, 'w', encoding='utf-8') as f:
                json.dump(self.element_data, f, ensure_ascii=False, indent=2)
            
            logger.info(f"✅ 요소 데이터 저장 완료: {ELEMENT_LOG_FILE}")
            logger.info(f"📊 저장된 데이터:")
            logger.info(f"   총 페이지 수: {len(self.element_data['scanned_pages'])}")
            logger.info(f"   총 요소 수: {len(self.element_data['all_elements'])}")
            logger.info(f"   컨텍스트 전환 기록: {len(self.element_data['context_switches'])}")
            
            return ELEMENT_LOG_FILE
            
        except Exception as e:
            logger.error(f"❌ 요소 데이터 저장 실패: {e}")
            return None
    
    def wait_and_scan_multiple_pages(self, wait_seconds_between_scans=5):
        """여러 페이지를 대기하면서 스캔"""
        logger.info("🔄 Step 6: 다중 페이지 스캔 시작")
        
        try:
            # 초기 페이지 스캔
            self.scan_page_elements("initial_page")
            
            # 일정 시간 대기 후 다시 스캔 (페이지 변화 감지)
            logger.info(f"⏳ {wait_seconds_between_scans}초 대기 후 재스캔...")
            time.sleep(wait_seconds_between_scans)
            
            # 두 번째 스캔
            self.scan_page_elements("after_wait")
            
            # 페이지 내에서 클릭 가능한 요소들을 찾아서 탐색
            self.explore_clickable_elements()
            
        except Exception as e:
            logger.error(f"❌ 다중 페이지 스캔 실패: {e}")
    
    def explore_clickable_elements(self):
        """클릭 가능한 요소들을 탐색하여 새로운 페이지 발견"""
        logger.info("🔍 클릭 가능한 요소 탐색 시작")
        
        try:
            # 버튼과 링크 찾기
            clickable_selectors = [
                "button:not([disabled])",
                "a[href]",
                "input[type='button']",
                "input[type='submit']",
                "[role='button']"
            ]
            
            clickable_elements = []
            for selector in clickable_selectors:
                try:
                    elements = self.driver.find_elements(AppiumBy.CSS_SELECTOR, selector)
                    for element in elements[:3]:  # 최대 3개씩만
                        if element.is_displayed() and element.is_enabled():
                            clickable_elements.append({
                                'element': element,
                                'selector': selector,
                                'text': element.text or 'No text',
                                'id': element.get_attribute('id') or 'No ID'
                            })
                except:
                    continue
            
            logger.info(f"🔘 발견된 클릭 가능한 요소: {len(clickable_elements)}개")
            
            # 몇 개의 요소를 클릭해보기 (최대 2개)
            for i, elem_info in enumerate(clickable_elements[:2]):
                try:
                    logger.info(f"🔄 요소 클릭 시도 {i+1}: '{elem_info['text']}' (ID: {elem_info['id']})")
                    
                    # 클릭 전 스크린샷 (안전하게)
                    screenshot_path = os.path.join(SCREENSHOT_DIR, f"04_before_click_{i+1}.png")
                    self.safe_screenshot(screenshot_path)
                    
                    # 요소 클릭
                    elem_info['element'].click()
                    time.sleep(3)  # 페이지 로딩 대기
                    
                    # 클릭 후 스크린샷 (안전하게)
                    screenshot_path = os.path.join(SCREENSHOT_DIR, f"05_after_click_{i+1}.png")
                    self.safe_screenshot(screenshot_path)
                    
                    # 새 페이지 스캔
                    self.scan_page_elements(f"clicked_page_{i+1}")
                    
                    logger.info(f"✅ 요소 클릭 및 스캔 완료: {elem_info['text']}")
                    
                except Exception as e:
                    logger.warning(f"⚠️ 요소 클릭 실패: {e}")
                    continue
                    
        except Exception as e:
            logger.error(f"❌ 클릭 가능한 요소 탐색 실패: {e}")
    
    def close(self):
        """드라이버 종료"""
        logger.info("🔚 테스트 세션 종료")
        if self.driver:
            try:
                self.driver.quit()
                logger.info("✅ 드라이버 종료 완료")
            except Exception as e:
                logger.error(f"❌ 드라이버 종료 실패: {e}")


class TestWebViewElementLogger(unittest.TestCase):
    """WEBVIEW 요소 로깅 테스트 클래스"""
    
    def setUp(self):
        """테스트 시작 전 설정"""
        logger.info("=" * 80)
        logger.info("🚀 WEBVIEW 요소 로깅 테스트 시작")
        logger.info("=" * 80)
        
        self.logger_instance = WebViewElementLogger()
        
        # 기존 앱 강제 종료
        self.logger_instance.force_stop_app()
    
    def tearDown(self):
        """테스트 종료 후 정리"""
        logger.info("\n🔄 테스트 종료 처리 중...")
        
        # 앱 종료
        if self.logger_instance.driver:
            try:
                # Appium을 통한 앱 종료 시도
                self.logger_instance.driver.terminate_app(APP_PACKAGE)
                logger.info("✅ 앱 종료 완료")
            except Exception as e:
                logger.warning(f"⚠️ Appium을 통한 앱 종료 실패: {e}")
                # adb를 통한 강제 종료 시도
                try:
                    import subprocess
                    result = subprocess.run(
                        ['adb', '-s', DEVICE_UDID, 'shell', 'am', 'force-stop', APP_PACKAGE],
                        capture_output=True, text=True, timeout=10
                    )
                    if result.returncode == 0:
                        logger.info("✅ adb를 통한 앱 강제 종료 완료")
                    else:
                        logger.warning(f"⚠️ adb 앱 종료 실패: {result.stderr}")
                except Exception as adb_e:
                    logger.warning(f"⚠️ adb 앱 종료 중 오류: {adb_e}")
        
        # 드라이버 종료
        self.logger_instance.close()
        
        logger.info("=" * 80)
        logger.info("✅ WEBVIEW 요소 로깅 테스트 완료")
        logger.info("=" * 80)
    
    def test_webview_element_logging(self):
        """WEBVIEW 요소 로깅 메인 테스트"""
        
        # Step 1: 드라이버 초기화
        self.assertTrue(
            self.logger_instance.initialize_driver(),
            "드라이버 초기화 실패"
        )
        
        # Step 2: 컨텍스트 스캔
        context_info = self.logger_instance.scan_contexts()
        self.assertIsNotNone(context_info, "컨텍스트 스캔 실패")
        
        # Step 3: WEBVIEW로 전환
        webview_success = self.logger_instance.switch_to_webview()
        if not webview_success:
            logger.warning("⚠️ WEBVIEW 전환 실패, 네이티브 컨텍스트로 계속 진행")
            # WEBVIEW 전환 실패해도 테스트는 계속 진행
        
        # Step 3: 로그인 테스트 (WEBVIEW 전환 성공 시에만)
        if webview_success:
            login_success = self.logger_instance.perform_login("c89109", "mcnc1234!!")
            if login_success:
                logger.info("🎉 로그인 후 추가 페이지 스캔 시작")
                # 로그인 후 페이지 스캔
                self.logger_instance.scan_page_elements("after_login")
        
        # Step 4: 페이지 요소 스캔
        self.logger_instance.wait_and_scan_multiple_pages()
        
        # Step 5: 결과 요약
        self.logger_instance.log_element_summary()
        
        # Step 6: 데이터 저장
        saved_file = self.logger_instance.save_element_data()
        self.assertIsNotNone(saved_file, "요소 데이터 저장 실패")
        
        logger.info("🎉 모든 테스트 단계 완료!")
        logger.info(f"📁 결과 파일:")
        logger.info(f"   📊 요소 데이터: {ELEMENT_LOG_FILE}")
        logger.info(f"   📝 상세 로그: {DETAILED_LOG_FILE}")
        logger.info(f"   📸 스크린샷: {SCREENSHOT_DIR}")


def main():
    """메인 실행 함수"""
    print("🚀 WEBVIEW 요소 로깅 테스트 프로그램 (앱 재시작, 데이터 유지)")
    print("=" * 75)
    print(f"📱 디바이스: {DEVICE_UDID}")
    print(f"📦 앱 패키지: {APP_PACKAGE}")
    print(f"🎯 앱 액티비티: {APP_ACTIVITY}")
    print(f"🌐 웹뷰 컨텍스트: {WEBVIEW_CONTEXT}")
    print(f"📁 스크린샷 저장: {SCREENSHOT_DIR}")
    print(f"📁 로그 저장: {LOG_DIR}")
    print("🔄 테스트 시작 시 앱 강제 종료 및 재시작")
    print("💾 앱 데이터 유지 (로그인 상태, 설정 등 보존)")
    print("🔚 테스트 종료 시 앱 자동 종료")
    print("=" * 75)
    
    # unittest 실행
    unittest.main(verbosity=2)


if __name__ == '__main__':
    main()
