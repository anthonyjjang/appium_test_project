import unittest
import time
import os
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
TEST_CASES_FILE = os.getenv('TEST_CASES_FILE', 'test_cases.csv')
TEST_STEPS_FILE = os.getenv('TEST_STEPS_FILE', 'test_steps.csv')

# App settings from environment (Excel runner specific - Vietnam focused)
BASE_URL = os.getenv('BASE_URL', 'http://localhost/')
LOGIN_PATH = os.getenv('LOGIN_PATH', 'LOG1000')
LANGUAGES = os.getenv('EXCEL_LANGUAGES', 'vi,ko,en').split(',')
SLEEP_TIME = int(os.getenv('SLEEP_TIME', '3'))
WEBVIEW_NAME = os.getenv('EXCEL_WEBVIEW_NAME', 'WEBVIEW_com.cesco.oversea.srs.viet')
APP_PACKAGE = os.getenv('EXCEL_APP_PACKAGE', 'com.cesco.oversea.srs.viet')
APP_ACTIVITY = os.getenv('DEFAULT_APP_ACTIVITY', 'com.mcnc.bizmob.cesco.SlideFragmentActivity')
UDID = os.getenv('EXCEL_UDID', 'RFCM902ZM9K')

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
    """Initialize Appium driver with required capabilities"""
    capabilities = dict(
        platformName='Android',
        automationName='uiautomator2',
        udid=UDID,
        appPackage=APP_PACKAGE,
        appActivity=APP_ACTIVITY,
        noReset=True,
        fullReset=False,
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
    appium_host = os.getenv('APPIUM_HOST', 'localhost')
    appium_port = os.getenv('APPIUM_PORT', '4723')
    driver = webdriver.Remote(f'http://{appium_host}:{appium_port}', options=options)
    driver.implicitly_wait(int(os.getenv('IMPLICIT_WAIT', '10')))
    return driver

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
    """Read test scenarios from CSV files"""
    try:
        # Read test cases CSV
        test_cases = []
        with open(TEST_CASES_FILE, 'r', encoding='utf-8') as f:
            cases_reader = csv.DictReader(f)
            cases_data = list(cases_reader)
        
        # Read test steps CSV
        with open(TEST_STEPS_FILE, 'r', encoding='utf-8') as f:
            steps_reader = csv.DictReader(f)
            steps_data = list(steps_reader)
        
        # Group steps by test_id
        steps_by_test = {}
        for step in steps_data:
            test_id = step['test_id']
            if test_id not in steps_by_test:
                steps_by_test[test_id] = []
            steps_by_test[test_id].append(step)
        
        # Create test cases
        for case_data in cases_data:
            test_id = case_data['test_id']
            
            # Get steps for this test case and sort by step_order
            case_steps = steps_by_test.get(test_id, [])
            case_steps.sort(key=lambda x: int(x['step_order']))
            
            steps = []
            for step_data in case_steps:
                test_step = TestStep(
                    action=step_data['action'],
                    selector_type=step_data['selector_type'],
                    selector_value=step_data['selector_value'],
                    input_value=step_data['input_value'] if step_data['input_value'] else None,
                    description=step_data['description'] if step_data['description'] else None
                )
                steps.append(test_step)
            
            test_case = TestCase(
                test_id=case_data['test_id'],
                screen_id=case_data['screen_id'],
                url=case_data['url'],
                description=case_data['description'],
                steps=steps,
                expected_result=case_data['expected_result'] if case_data['expected_result'] else None
            )
            test_cases.append(test_case)
            
        return test_cases
    except Exception as e:
        print(f"Error loading test cases from CSV: {str(e)}")
        return []

def change_language(driver, wait, lang):
    """Change application language"""
    try:
        lang_btn = wait.until(EC.element_to_be_clickable((AppiumBy.XPATH, "//button[contains(.,'select language')]")))
        lang_btn.click()
        
        index = {'vi': 1, 'ko': 2, 'en': 3}.get(lang, 1)
        selector = f"(//input[@name='select'])[{index}]"
        lang_input = wait.until(EC.element_to_be_clickable((AppiumBy.XPATH, selector)))
        lang_input.click()
        return True
    except Exception as e:
        print(f"Language change failed for {lang}: {str(e)}")
        return False

def login(driver, wait):
    """Perform login"""
    try:
        user_id = wait.until(EC.presence_of_element_located((AppiumBy.CSS_SELECTOR, ".log_id input")))
        user_id.clear()
        user_id.send_keys(USER_ID)

        user_pw = wait.until(EC.presence_of_element_located((AppiumBy.XPATH, "//input[@type='password']")))
        user_pw.clear()
        user_pw.send_keys(USER_PW)

        login_btn = wait.until(EC.element_to_be_clickable((AppiumBy.CSS_SELECTOR, ".btn01")))
        login_btn.click()
        time.sleep(SLEEP_TIME)
        return True
    except Exception as e:
        print(f"Login failed: {str(e)}")
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
    def test_all_scenarios(self):
        # Load test cases from CSV
        test_cases = load_test_cases_from_csv()
        if not test_cases:
            self.fail("No test cases loaded from CSV files")

        # Initialize driver
        driver = get_driver()
        wait = WebDriverWait(driver, int(os.getenv('EXPLICIT_WAIT', '20')))
        
        try:
            # Switch to WebView context
            driver.switch_to.context(WEBVIEW_NAME)
            
            # Execute test cases for each language
            for lang in LANGUAGES:
                # Change language
                if not change_language(driver, wait, lang):
                    continue
                
                # Perform login
                if not login(driver, wait):
                    continue
                
                # Execute each test case
                for test_case in test_cases:
                    run_test_case(driver, wait, lang, test_case)
                
                # Return to login page for next language
                driver.get(BASE_URL + LOGIN_PATH)
                time.sleep(SLEEP_TIME)
                
        finally:
            driver.quit()

if __name__ == '__main__':
    print("🚀 CSV 기반 Appium 테스트 실행기 (베트남 패키지)")
    print("=" * 60)
    print(f"📁 테스트 케이스 파일: {TEST_CASES_FILE}")
    print(f"📁 테스트 스텝 파일: {TEST_STEPS_FILE}")
    print(f"📱 디바이스: {UDID}")
    print(f"📦 앱 패키지: {APP_PACKAGE}")
    print(f"🌐 웹뷰 컨텍스트: {WEBVIEW_NAME}")
    print(f"🌐 베이스 URL: {BASE_URL}")
    print(f"🔑 로그인 경로: {LOGIN_PATH}")
    print(f"🌍 지원 언어: {', '.join(LANGUAGES)}")
    print(f"📁 스크린샷 저장: {SCREENSHOT_DIR}")
    print(f"📊 결과 파일: {RESULT_CSV_FILE}")
    print("=" * 60)
    unittest.main() 