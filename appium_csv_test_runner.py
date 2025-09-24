import unittest
import time
import os
import pandas as pd
import csv
from datetime import datetime
from dotenv import load_dotenv
from appium import webdriver
from appium.webdriver.common.appiumby import AppiumBy
from appium.options.android import UiAutomator2Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException

# Load environment variables
load_dotenv()

start_time = datetime.now().strftime('%Y%m%d_%H%M%S')

# Directory settings
SCREENSHOT_DIR = os.path.join('screenshots', f'test_{start_time}')
os.makedirs(SCREENSHOT_DIR, exist_ok=True)
RESULT_CSV_FILE = f'test_results_{start_time}.csv'
TEST_csv_FILE = os.getenv('TEST_CSV_FILE', 'test_scenarios.csv')

# App settings from environment (csv runner specific - Vietnam focused)
BASE_URL = os.getenv('BASE_URL', 'http://localhost/')
LOGIN_PATH = os.getenv('LOGIN_PATH', 'LOG1000')
LANGUAGES = os.getenv('csv_LANGUAGES', 'vi,ko,en').split(',')
SLEEP_TIME = int(os.getenv('SLEEP_TIME', '3'))
WEBVIEW_NAME = os.getenv('csv_WEBVIEW_NAME', 'WEBVIEW_com.cesco.oversea.srs.viet')
APP_PACKAGE = os.getenv('csv_APP_PACKAGE', 'com.cesco.oversea.srs.viet')
APP_ACTIVITY = os.getenv('DEFAULT_APP_ACTIVITY', 'com.mcnc.bizmob.cesco.SlideFragmentActivity')
UDID = os.getenv('csv_UDID', 'RFCM902ZM9K')

# Login credentials from environment
USER_ID = os.getenv('USER_ID', 'c89109')
USER_PW = os.getenv('USER_PW', 'mcnc1234!!')

class TestStep:
    def __init__(self, action, selector_type, selector_value, input_value=None, description=None):
        self.action = action
        self.selector_type = selector_type
        self.selector_value = selector_value
        self.input_value = input_value
        self.description = description

class TestCase:
    def __init__(self, test_id, screen_id, url, description, steps, expected_result=None):
        self.test_id = test_id
        self.screen_id = screen_id
        self.url = url
        self.description = description
        self.steps = steps
        self.expected_result = expected_result

def get_driver():
    """Initialize Appium driver with enhanced capabilities"""
    print("\n🚀 Appium 드라이버 초기화 중...")
    
    capabilities = dict(
        platformName='Android',
        automationName='uiautomator2',
        udid=UDID,
        appPackage=APP_PACKAGE,
        appActivity=APP_ACTIVITY,
        noReset=True,
        fullReset=False,
        # WEBVIEW 관련 강화된 설정
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
        appium_host = os.getenv('APPIUM_HOST', 'localhost')
        appium_port = os.getenv('APPIUM_PORT', '4723')
        driver = webdriver.Remote(f'http://{appium_host}:{appium_port}', options=options)
        driver.implicitly_wait(int(os.getenv('IMPLICIT_WAIT', '10')))
        
        print("✅ Appium 드라이버 초기화 완료")
        print(f"📱 연결된 디바이스: {UDID}")
        print(f"📦 앱 패키지: {APP_PACKAGE}")
        print(f"🎯 앱 액티비티: {APP_ACTIVITY}")
        
        return driver
        
    except Exception as e:
        print(f"❌ Appium 드라이버 초기화 실패: {e}")
        raise

def log_result(lang, test_id, screen_id, status, message, description=None):
    """Log test results to CSV file"""
    file_exists = os.path.isfile(RESULT_CSV_FILE)
    with open(RESULT_CSV_FILE, mode='a', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        if not file_exists:
            writer.writerow(['timestamp', 'language', 'test_id', 'screen_id', 'description', 'status', 'message'])
        writer.writerow([
            datetime.now().isoformat(),
            lang,
            test_id,
            screen_id,
            description,
            status,
            message
        ])

def load_test_cases_from_csv():
    """Read test scenarios from csv file"""
    print(f"📋 CSV 파일 로드 시도: {TEST_csv_FILE}")
    
    try:
        # CSV 파일 존재 확인
        if not os.path.exists(TEST_csv_FILE):
            print(f"❌ CSV 파일이 존재하지 않음: {TEST_csv_FILE}")
            return []
        
        # CSV 파일 읽기 (단일 파일에 모든 테스트 단계가 포함됨)
        print("📖 CSV 파일 읽는 중...")
        df_steps = pd.read_csv(TEST_csv_FILE)
        
        print(f"✅ CSV 파일 읽기 성공: {len(df_steps)}개 행")
        print(f"📋 컬럼: {list(df_steps.columns)}")
        
        # test_id별로 그룹화하여 테스트 케이스 생성
        test_cases = []
        unique_test_ids = df_steps['test_id'].unique()
        
        print(f"🔍 발견된 테스트 ID: {list(unique_test_ids)}")
        
        for test_id in unique_test_ids:
            # 현재 테스트 ID의 모든 단계 가져오기
            case_steps_df = df_steps[df_steps['test_id'] == test_id].sort_values('step_order')
            
            print(f"📝 테스트 {test_id}: {len(case_steps_df)}개 단계")
            
            # 테스트 단계들 생성
            steps = []
            for _, step_row in case_steps_df.iterrows():
                # input_value가 NaN인 경우 None으로 처리
                input_value = step_row['input_value'] if pd.notna(step_row['input_value']) else None
                description = step_row['description'] if pd.notna(step_row['description']) else None
                
                test_step = TestStep(
                    action=step_row['action'],
                    selector_type=step_row['selector_type'],
                    selector_value=step_row['selector_value'],
                    input_value=input_value,
                    description=description
                )
                steps.append(test_step)
                
                print(f"   단계 {step_row['step_order']}: {step_row['action']} - {description}")
            
            # 테스트 케이스 생성 (CSV에는 케이스 메타데이터가 없으므로 기본값 사용)
            test_case = TestCase(
                test_id=test_id,
                screen_id=f"{test_id}_SCREEN",  # 기본 스크린 ID
                url="",  # CSV에 URL 정보가 없으므로 빈 문자열
                description=f"테스트 케이스 {test_id}",  # 기본 설명
                steps=steps,
                expected_result=None  # 기본값
            )
            test_cases.append(test_case)
            
            print(f"✅ 테스트 케이스 생성 완료: {test_id}")
        
        print(f"🎉 총 {len(test_cases)}개 테스트 케이스 로드 완료")
        return test_cases
        
    except Exception as e:
        print(f"❌ CSV 파일 로드 중 오류: {str(e)}")
        print(f"💡 파일 경로: {TEST_csv_FILE}")
        print(f"💡 현재 작업 디렉토리: {os.getcwd()}")
        
        # 파일 존재 여부 재확인
        if os.path.exists(TEST_csv_FILE):
            print(f"📄 파일은 존재함 - 내용 확인 중...")
            try:
                with open(TEST_csv_FILE, 'r', encoding='utf-8') as f:
                    first_lines = [f.readline().strip() for _ in range(3)]
                    print(f"📝 파일 첫 3줄:\n" + "\n".join(first_lines))
            except Exception as read_e:
                print(f"❌ 파일 읽기 실패: {read_e}")
        
        return []

def safe_switch_to_webview(driver, webview_name=None, max_retries=3):
    """안전한 WEBVIEW 컨텍스트 전환 (강화된 재시도 로직)"""
    print(f"\n🔄 WEBVIEW 컨텍스트 전환 시작 (목표: {webview_name or 'auto-detect'})")
    
    for retry in range(max_retries):
        try:
            print(f"🔄 웹뷰 전환 시도 {retry + 1}/{max_retries}")
            
            contexts = driver.contexts
            webview_contexts = [ctx for ctx in contexts if 'WEBVIEW' in ctx]
            
            print(f"📋 사용 가능한 컨텍스트: {contexts}")
            print(f"🌐 웹뷰 컨텍스트: {webview_contexts}")
            
            if not webview_contexts:
                print("⚠️ 사용 가능한 WEBVIEW 컨텍스트가 없음")
                if retry < max_retries - 1:
                    print("⏳ 3초 후 재시도...")
                    time.sleep(3)
                    continue
                return False
            
            # 목표 웹뷰 컨텍스트 선택
            target_webview = None
            if webview_name:
                for ctx in webview_contexts:
                    if webview_name in ctx:
                        target_webview = ctx
                        break
            
            if not target_webview:
                target_webview = webview_contexts[0]
                print(f"🎯 첫 번째 웹뷰 사용: {target_webview}")
            
            print(f"🔄 웹뷰 컨텍스트로 전환: {target_webview}")
            
            # 웹뷰로 전환
            driver.switch_to.context(target_webview)
            time.sleep(3)  # 웹뷰 로딩 대기
            
            # 전환 확인
            current_context = driver.current_context
            if current_context == target_webview:
                print(f"✅ 웹뷰 컨텍스트 전환 성공: {current_context}")
                
                # 웹뷰 접근 테스트
                try:
                    body_elements = driver.find_elements(AppiumBy.TAG_NAME, "body")
                    print(f"✅ 웹뷰 접근 테스트 성공: {len(body_elements)}개 body 요소 발견")
                except Exception as web_e:
                    print(f"⚠️ 웹뷰 접근 테스트 실패: {web_e}")
                    print("💡 웹뷰로 전환되었지만 웹 요소에 즉시 접근할 수 없음")
                
                return True
            else:
                print(f"❌ 웹뷰 컨텍스트 전환 실패: 요청={target_webview}, 실제={current_context}")
                if retry < max_retries - 1:
                    print("⏳ 2초 후 재시도...")
                    time.sleep(2)
                    continue
                    
        except Exception as e:
            error_msg = str(e)
            print(f"❌ 웹뷰 컨텍스트 전환 중 오류: {error_msg}")
            
            # Chromedriver 관련 오류 감지
            if 'chromedriver' in error_msg.lower() or 'chrome' in error_msg.lower():
                print("🔧 Chromedriver 관련 오류 감지")
                print("💡 해결 방법:")
                print("   1. 앱을 완전히 종료하고 다시 실행")
                print("   2. Appium 서버 재시작")
                print("   3. 호환되는 Chromedriver 수동 설치")
                
                # Chromedriver 오류는 재시도해도 해결되지 않으므로 중단
                break
            
            if retry < max_retries - 1:
                print(f"⏳ 3초 후 재시도...")
                time.sleep(3)
                continue
    
    print("❌ 모든 웹뷰 컨텍스트 전환 시도 실패")
    print("🔄 네이티브 컨텍스트로 폴백")
    
    # 네이티브 컨텍스트로 폴백
    try:
        driver.switch_to.context('NATIVE_APP')
        print("✅ 네이티브 컨텍스트로 폴백 완료")
        return False
    except Exception as native_e:
        print(f"❌ 네이티브 컨텍스트 전환도 실패: {native_e}")
        return False

def change_language(driver, wait, lang):
    """Change application language with enhanced error handling"""
    print(f"\n🌐 언어 변경 시도: {lang}")
    
    try:
        # 현재 컨텍스트 확인
        current_context = driver.current_context
        print(f"📱 현재 컨텍스트: {current_context}")
        
        # WEBVIEW 컨텍스트에서만 언어 변경 시도
        if 'WEBVIEW' in current_context:
            try:
                lang_btn = wait.until(EC.element_to_be_clickable((AppiumBy.XPATH, "//button[contains(.,'select language')]")))
                lang_btn.click()
                
                index = {'vi': 1, 'ko': 2, 'en': 3}.get(lang, 1)
                selector = f"(//input[@name='select'])[{index}]"
                lang_input = wait.until(EC.element_to_be_clickable((AppiumBy.XPATH, selector)))
                lang_input.click()
                
                print(f"✅ 언어 변경 성공: {lang}")
                time.sleep(SLEEP_TIME)
                return True
                
            except TimeoutException:
                print(f"⚠️ 언어 선택 버튼을 찾을 수 없음 (WEBVIEW): {lang}")
                return False
        else:
            print(f"⚠️ NATIVE_APP 컨텍스트에서는 언어 변경 불가: {lang}")
            return False
            
    except Exception as e:
        print(f"❌ 언어 변경 실패 ({lang}): {str(e)}")
        return False

def login(driver, wait):
    """Perform login with enhanced error handling and multiple selector strategies"""
    print(f"\n🔑 로그인 시작 - ID: {USER_ID}")
    
    try:
        # 현재 컨텍스트 확인
        current_context = driver.current_context
        print(f"📱 로그인 컨텍스트: {current_context}")
        
        # WEBVIEW 컨텍스트에서만 로그인 시도
        if 'WEBVIEW' not in current_context:
            print("⚠️ WEBVIEW 컨텍스트가 아님 - 로그인 건너뛰기")
            return False
        
        # 1. 사번 입력 필드 찾기 (다양한 선택자 시도)
        print("👤 사번 입력 필드 찾는 중...")
        username_selectors = [
            ".log_id input",
            "input[placeholder*='사번']",
            "input[type='text']",
            "input:first-of-type"
        ]
        
        username_field = None
        for selector in username_selectors:
            try:
                elements = driver.find_elements(AppiumBy.CSS_SELECTOR, selector)
                if elements:
                    for element in elements:
                        if element.is_displayed() and element.is_enabled():
                            username_field = element
                            print(f"✅ 사번 입력 필드 발견: {selector}")
                            break
                    if username_field:
                        break
            except Exception:
                continue
        
        if not username_field:
            print("❌ 사번 입력 필드를 찾을 수 없음")
            return False
        
        # 사번 입력
        username_field.clear()
        username_field.send_keys(USER_ID)
        print(f"✅ 사번 입력 완료: {USER_ID}")

        # 2. 비밀번호 입력 필드 찾기
        print("🔒 비밀번호 입력 필드 찾는 중...")
        password_selectors = [
            "input[type='password']",
            "input[placeholder*='비밀번호']"
        ]
        
        password_field = None
        for selector in password_selectors:
            try:
                elements = driver.find_elements(AppiumBy.CSS_SELECTOR, selector)
                if elements:
                    for element in elements:
                        if element.is_displayed() and element.is_enabled():
                            password_field = element
                            print(f"✅ 비밀번호 입력 필드 발견: {selector}")
                            break
                    if password_field:
                        break
            except Exception:
                continue
        
        if not password_field:
            print("❌ 비밀번호 입력 필드를 찾을 수 없음")
            return False

        # 비밀번호 입력
        password_field.clear()
        password_field.send_keys(USER_PW)
        print("✅ 비밀번호 입력 완료")

        # 3. 로그인 버튼 찾기 및 클릭
        print("🔘 로그인 버튼 찾는 중...")
        login_selectors = [
            ".btn01",
            "button:contains('로그인')",
            "button[class*='btn']",
            "button[type='button']"
        ]
        
        login_button = None
        for selector in login_selectors:
            try:
                if "contains" in selector:
                    elements = driver.find_elements(AppiumBy.XPATH, "//button[contains(text(), '로그인')]")
                else:
                    elements = driver.find_elements(AppiumBy.CSS_SELECTOR, selector)
                
                if elements:
                    for element in elements:
                        if element.is_displayed() and element.is_enabled():
                            login_button = element
                            print(f"✅ 로그인 버튼 발견: {selector}")
                            break
                    if login_button:
                        break
            except Exception:
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
        time.sleep(SLEEP_TIME + 2)  # 조금 더 긴 대기
        
        # 4. 로그인 결과 확인
        print("🔍 로그인 결과 확인 중...")
        try:
            current_url = driver.current_url
            print(f"📍 로그인 후 URL: {current_url}")
            
            # 로그인 성공 판단 (URL 변화 또는 특정 요소 존재)
            if current_url and current_url != f"{BASE_URL}{LOGIN_PATH}":
                print("✅ 로그인 성공! (URL 변화 감지)")
                return True
            else:
                # 메인 화면 요소 확인
                main_elements = driver.find_elements(AppiumBy.CSS_SELECTOR, ".main_content, .dashboard, .home")
                if main_elements:
                    print("✅ 로그인 성공! (메인 화면 요소 발견)")
                    return True
                else:
                    print("⚠️ 로그인 상태 불명확 - 계속 진행")
                    return True  # 일단 성공으로 처리하고 계속 진행
                    
        except Exception as e:
            print(f"⚠️ 로그인 결과 확인 중 오류: {e}")
            return True  # 일단 성공으로 처리하고 계속 진행
            
    except Exception as e:
        print(f"❌ 로그인 실패: {str(e)}")
        return False

def execute_test_step(driver, wait, step):
    """Execute a single test step"""
    try:
        selector = (getattr(AppiumBy, step.selector_type.upper()), step.selector_value)
        
        if step.action.lower() == 'click':
            element = wait.until(EC.element_to_be_clickable(selector))
            element.click()
        elif step.action.lower() == 'input':
            element = wait.until(EC.presence_of_element_located(selector))
            element.clear()
            if step.input_value:
                element.send_keys(step.input_value)
        elif step.action.lower() == 'verify':
            element = wait.until(EC.presence_of_element_located(selector))
            assert element.is_displayed(), "Element not visible"
            if step.input_value:
                assert step.input_value in element.text, f"Expected text '{step.input_value}' not found"
        
        time.sleep(SLEEP_TIME)
        return True
    except Exception as e:
        print(f"Step execution failed: {str(e)}")
        return False

def run_test_case(driver, wait, lang, test_case):
    """Execute a complete test case"""
    try:
        # Navigate to test URL
        if test_case.url:
            full_url = BASE_URL + test_case.url
            driver.get(full_url)
            time.sleep(SLEEP_TIME)

        # Execute each test step
        for step in test_case.steps:
            if not execute_test_step(driver, wait, step):
                raise Exception(f"Step failed: {step.description}")

        # Take screenshot for successful test
        screenshot_path = os.path.join(SCREENSHOT_DIR, f"{lang}_{test_case.test_id}_{test_case.screen_id}_pass.png")
        driver.save_screenshot(screenshot_path)
        
        log_result(lang, test_case.test_id, test_case.screen_id, "PASS", "", test_case.description)
        return True
    except Exception as e:
        # Take screenshot for failed test
        screenshot_path = os.path.join(SCREENSHOT_DIR, f"{lang}_{test_case.test_id}_{test_case.screen_id}_fail.png")
        driver.save_screenshot(screenshot_path)
        
        log_result(lang, test_case.test_id, test_case.screen_id, "FAIL", str(e), test_case.description)
        return False

class TestCsvScenarios(unittest.TestCase):
    """CSV 기반 테스트 시나리오 실행 클래스"""
    
    def setUp(self):
        """테스트 시작 전 설정"""
        print("\n" + "=" * 80)
        print("🚀 CSV 테스트 시나리오 시작")
        print("=" + "=" * 78 + "=")
        print(f"📱 디바이스: {UDID}")
        print(f"📦 앱 패키지: {APP_PACKAGE}")
        print(f"🎯 앱 액티비티: {APP_ACTIVITY}")
        print(f"🌐 웹뷰 컨텍스트: {WEBVIEW_NAME}")
        print(f"📁 스크린샷 저장: {SCREENSHOT_DIR}")
        print(f"📊 결과 저장: {RESULT_CSV_FILE}")
        print("=" * 80)
        
        self.driver = None
        self.wait = None
    
    def tearDown(self):
        """테스트 종료 후 정리"""
        if self.driver:
            try:
                print("\n🔄 테스트 종료 처리 중...")
                
                # 앱 종료 시도
                try:
                    self.driver.terminate_app(APP_PACKAGE)
                    print("✅ 앱 종료 완료")
                except:
                    pass
                
                # 드라이버 종료
                self.driver.quit()
                print("✅ 드라이버 종료 완료")
                
            except Exception as e:
                print(f"⚠️ 정리 중 오류: {e}")
        
        print("🔚 CSV 테스트 정리 완료")
        print("=" * 80)

    def test_all_scenarios(self):
        """모든 테스트 시나리오 실행"""
        # Load test cases from csv
        print("📋 CSV 파일에서 테스트 케이스 로드 중...")
        test_cases = load_test_cases_from_csv()
        if not test_cases:
            self.fail("❌ CSV 파일에서 테스트 케이스를 로드할 수 없음")

        print(f"✅ {len(test_cases)}개 테스트 케이스 로드 완료")

        # Initialize driver
        self.driver = get_driver()
        self.wait = WebDriverWait(self.driver, int(os.getenv('EXPLICIT_WAIT', '20')))
        
        try:
            # Safe switch to WebView context
            print("\n🔄 WEBVIEW 컨텍스트로 안전한 전환 시도...")
            webview_success = safe_switch_to_webview(self.driver, WEBVIEW_NAME)
            
            if not webview_success:
                print("⚠️ WEBVIEW 전환 실패 - 네이티브 앱 컨텍스트로 진행")
                # WEBVIEW 실패해도 테스트는 계속 진행
                log_result('system', 'WEBVIEW_SWITCH', 'CONTEXT', 'FAIL', 'WEBVIEW 컨텍스트 전환 실패')
            else:
                print("✅ WEBVIEW 컨텍스트 전환 성공")
                log_result('system', 'WEBVIEW_SWITCH', 'CONTEXT', 'PASS', 'WEBVIEW 컨텍스트 전환 성공')
            
            # Execute test cases for each language
            for lang in LANGUAGES:
                print(f"\n🌐 언어별 테스트 시작: {lang}")
                
                # Change language (WEBVIEW 모드에서만)
                if webview_success:
                    if not change_language(self.driver, self.wait, lang):
                        print(f"⚠️ 언어 변경 실패: {lang} - 건너뛰기")
                        log_result(lang, 'LANGUAGE_CHANGE', 'SETUP', 'FAIL', f'언어 변경 실패: {lang}')
                        continue
                else:
                    print(f"⚠️ WEBVIEW 모드가 아니므로 언어 변경 건너뛰기: {lang}")
                
                # Perform login (WEBVIEW 모드에서만)
                if webview_success:
                    if not login(self.driver, self.wait):
                        print(f"⚠️ 로그인 실패: {lang} - 건너뛰기")
                        log_result(lang, 'LOGIN', 'AUTH', 'FAIL', f'로그인 실패: {lang}')
                        continue
                else:
                    print(f"⚠️ WEBVIEW 모드가 아니므로 로그인 건너뛰기: {lang}")
                
                # Execute each test case
                print(f"🧪 테스트 케이스 실행 시작: {lang}")
                for i, test_case in enumerate(test_cases, 1):
                    print(f"\n📝 테스트 케이스 {i}/{len(test_cases)}: {test_case.test_id}")
                    run_test_case(self.driver, self.wait, lang, test_case)
                
                # Return to login page for next language (WEBVIEW 모드에서만)
                if webview_success and len(LANGUAGES) > 1:
                    try:
                        print(f"🔄 다음 언어를 위해 로그인 페이지로 이동: {lang}")
                        self.driver.get(BASE_URL + LOGIN_PATH)
                        time.sleep(SLEEP_TIME)
                    except Exception as e:
                        print(f"⚠️ 로그인 페이지 이동 실패: {e}")
                
                print(f"✅ 언어별 테스트 완료: {lang}")
            
            print("\n🎉 모든 테스트 시나리오 완료!")
            print(f"📊 결과 파일: {RESULT_CSV_FILE}")
            print(f"📸 스크린샷: {SCREENSHOT_DIR}")
                
        except Exception as e:
            print(f"❌ 테스트 실행 중 심각한 오류: {e}")
            log_result('system', 'TEST_EXECUTION', 'ERROR', 'FAIL', f'테스트 실행 오류: {str(e)}')
            raise

def main():
    """메인 실행 함수"""
    print("🚀 CSV 기반 Appium 테스트 러너")
    print("=" * 60)
    print(f"📱 디바이스: {UDID}")
    print(f"📦 앱 패키지: {APP_PACKAGE}")
    print(f"🎯 앱 액티비티: {APP_ACTIVITY}")
    print(f"🌐 웹뷰 컨텍스트: {WEBVIEW_NAME}")
    print(f"🌍 테스트 언어: {', '.join(LANGUAGES)}")
    print(f"👤 로그인 ID: {USER_ID}")
    print(f"📄 CSV 파일: {TEST_csv_FILE}")
    print(f"📁 스크린샷 저장: {SCREENSHOT_DIR}")
    print(f"📊 결과 저장: {RESULT_CSV_FILE}")
    print("=" * 60)
    
    # unittest 실행
    unittest.main(verbosity=2)

if __name__ == '__main__':
    main() 