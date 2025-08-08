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
from enhanced_test_engine import EnhancedTestEngine

# Load environment variables
load_dotenv()

start_time = datetime.now().strftime('%Y%m%d_%H%M%S')

# Configuration from environment
SCREENSHOT_DIR = os.path.join('screenshots', f'test_{start_time}')
os.makedirs(SCREENSHOT_DIR, exist_ok=True)
RESULT_CSV_FILE = f'test_results_enhanced_{start_time}.csv'
TEST_STEPS_FILE = os.getenv('TEST_STEPS_ENHANCED_CSV', 'test_steps_enhanced.csv')
TEST_CASES_FILE = os.getenv('TEST_CASES_CSV', 'test_cases.csv')

# App settings from environment
BASE_URL = os.getenv('BASE_URL', 'http://localhost/')
LOGIN_PATH = os.getenv('LOGIN_PATH', 'LOG1000')
LANGUAGES = os.getenv('CN_LANGUAGES', 'zh,ko,en').split(',')
SLEEP_TIME = int(os.getenv('SLEEP_TIME', '3'))
WEBVIEW_NAME = os.getenv('CN_WEBVIEW_NAME', 'WEBVIEW_com.cesco.oversea.srs.cn')
APP_PACKAGE = os.getenv('CN_APP_PACKAGE', 'com.cesco.oversea.srs.cn')
APP_ACTIVITY = os.getenv('DEFAULT_APP_ACTIVITY', 'com.mcnc.bizmob.cesco.SlideFragmentActivity')
UDID = os.getenv('DEFAULT_UDID', 'RFCX715QHAL')

class EnhancedTestCase:
    """향상된 테스트 케이스 클래스"""
    def __init__(self, test_id, description, url, steps):
        self.test_id = test_id
        self.description = description
        self.url = url
        self.steps = steps

class EnhancedTestStep:
    """향상된 테스트 스텝 클래스"""
    def __init__(self, step_order, action, selector_type, selector_value, 
                 input_value=None, expected_value=None, wait_time=3, 
                 description=None, validation_type='basic', retry_count=1):
        self.step_order = int(step_order)
        self.action = action
        self.selector_type = selector_type
        self.selector_value = selector_value
        self.input_value = input_value
        self.expected_value = expected_value
        self.wait_time = int(wait_time)
        self.description = description
        self.validation_type = validation_type
        self.retry_count = int(retry_count)

def get_driver():
    """Appium 드라이버 초기화"""
    capabilities = dict(
        platformName='Android',
        automationName='uiautomator2',
        udid=UDID,
        appPackage=APP_PACKAGE,
        appActivity=APP_ACTIVITY,
        noReset=True,
        fullReset=False
    )
    options = UiAutomator2Options().load_capabilities(capabilities)
    appium_host = os.getenv('APPIUM_HOST', 'localhost')
    appium_port = os.getenv('APPIUM_PORT', '4723')
    driver = webdriver.Remote(f'http://{appium_host}:{appium_port}', options=options)
    driver.implicitly_wait(int(os.getenv('IMPLICIT_WAIT', '10')))
    return driver

def load_enhanced_test_cases():
    """향상된 테스트 케이스 로딩"""
    try:
        # 테스트 케이스 기본 정보 로딩
        test_cases_data = {}
        with open(TEST_CASES_FILE, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                test_cases_data[row['test_id']] = {
                    'description': row['description'],
                    'url': row['url']
                }
        
        # 테스트 스텝 로딩
        test_steps_data = {}
        with open(TEST_STEPS_FILE, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                # 주석 행 스킵
                if row['test_id'].startswith('#'):
                    continue
                    
                test_id = row['test_id']
                if test_id not in test_steps_data:
                    test_steps_data[test_id] = []
                
                step = EnhancedTestStep(
                    step_order=row['step_order'],
                    action=row['action'],
                    selector_type=row['selector_type'],
                    selector_value=row['selector_value'],
                    input_value=row.get('input_value'),
                    expected_value=row.get('expected_value'),
                    wait_time=row.get('wait_time', 3),
                    description=row.get('description'),
                    validation_type=row.get('validation_type', 'basic'),
                    retry_count=row.get('retry_count', 1)
                )
                test_steps_data[test_id].append(step)
        
        # 테스트 케이스 생성
        test_cases = []
        for test_id, case_info in test_cases_data.items():
            if test_id in test_steps_data:
                # 스텝을 순서대로 정렬
                steps = sorted(test_steps_data[test_id], key=lambda x: x.step_order)
                test_case = EnhancedTestCase(
                    test_id=test_id,
                    description=case_info['description'],
                    url=case_info['url'],
                    steps=steps
                )
                test_cases.append(test_case)
            else:
                print(f"Warning: No steps found for test case {test_id}")
        
        return test_cases
    except Exception as e:
        print(f"Error loading enhanced test cases: {str(e)}")
        return []

def log_enhanced_result(lang, test_id, step_order, step_description, status, 
                       message, execution_time=None, screenshot_path=None):
    """향상된 테스트 결과 로깅"""
    file_exists = os.path.isfile(RESULT_CSV_FILE)
    with open(RESULT_CSV_FILE, mode='a', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        if not file_exists:
            writer.writerow([
                'timestamp', 'language', 'test_id', 'step_order', 'step_description',
                'status', 'message', 'execution_time_ms', 'screenshot_path'
            ])
        writer.writerow([
            datetime.now().isoformat(),
            lang,
            test_id,
            step_order,
            step_description,
            status,
            message,
            execution_time,
            screenshot_path
        ])

def execute_enhanced_test_case(engine, test_case, lang):
    """향상된 테스트 케이스 실행"""
    test_start_time = time.time()
    
    print(f"\n🚀 Starting test case: {test_case.test_id} - {test_case.description}")
    
    # URL 이동 (필요한 경우)
    if test_case.url:
        full_url = BASE_URL + test_case.url
        engine.driver.get(full_url)
        time.sleep(SLEEP_TIME)
        print(f"📍 Navigated to: {full_url}")
    
    total_steps = len(test_case.steps)
    passed_steps = 0
    failed_steps = []
    
    for step in test_case.steps:
        step_start_time = time.time()
        step_description = step.description or f"{step.action} on {step.selector_value}"
        
        try:
            print(f"  ⏳ Step {step.step_order}/{total_steps}: {step_description}")
            
            # 스텝을 딕셔너리로 변환하여 엔진에 전달
            step_dict = {
                'action': step.action,
                'selector_type': step.selector_type,
                'selector_value': step.selector_value,
                'input_value': step.input_value,
                'expected_value': step.expected_value,
                'wait_time': step.wait_time,
                'validation_type': step.validation_type,
                'retry_count': step.retry_count
            }
            
            success = engine.execute_step(step_dict, test_case.test_id, lang)
            
            step_execution_time = int((time.time() - step_start_time) * 1000)
            
            if success:
                print(f"  ✅ Step {step.step_order} passed ({step_execution_time}ms)")
                passed_steps += 1
                log_enhanced_result(
                    lang, test_case.test_id, step.step_order, step_description,
                    'PASS', '', step_execution_time
                )
            else:
                print(f"  ❌ Step {step.step_order} failed ({step_execution_time}ms)")
                failed_steps.append(step.step_order)
                log_enhanced_result(
                    lang, test_case.test_id, step.step_order, step_description,
                    'FAIL', 'Step execution returned False', step_execution_time
                )
                
        except Exception as e:
            step_execution_time = int((time.time() - step_start_time) * 1000)
            error_message = str(e)
            print(f"  💥 Step {step.step_order} error: {error_message} ({step_execution_time}ms)")
            failed_steps.append(step.step_order)
            
            # 에러 발생 시 스크린샷 촬영
            screenshot_filename = f"{lang}_{test_case.test_id}_step{step.step_order}_error.png"
            screenshot_path = os.path.join(SCREENSHOT_DIR, screenshot_filename)
            try:
                engine.driver.save_screenshot(screenshot_path)
            except:
                screenshot_path = None
            
            log_enhanced_result(
                lang, test_case.test_id, step.step_order, step_description,
                'ERROR', error_message, step_execution_time, screenshot_path
            )
    
    # 테스트 케이스 완료 후 최종 스크린샷
    final_screenshot = f"{lang}_{test_case.test_id}_final.png"
    final_screenshot_path = os.path.join(SCREENSHOT_DIR, final_screenshot)
    try:
        engine.driver.save_screenshot(final_screenshot_path)
    except:
        final_screenshot_path = None
    
    total_execution_time = int((time.time() - test_start_time) * 1000)
    success_rate = (passed_steps / total_steps) * 100 if total_steps > 0 else 0
    
    print(f"🎯 Test case completed: {passed_steps}/{total_steps} steps passed ({success_rate:.1f}%)")
    if failed_steps:
        print(f"❌ Failed steps: {failed_steps}")
    print(f"⏱️  Total execution time: {total_execution_time}ms")
    
    # 테스트 케이스 전체 결과 로깅
    case_status = 'PASS' if len(failed_steps) == 0 else 'PARTIAL' if passed_steps > 0 else 'FAIL'
    log_enhanced_result(
        lang, test_case.test_id, 'SUMMARY', f"Test Case Summary - {success_rate:.1f}% success",
        case_status, f"Passed: {passed_steps}, Failed: {len(failed_steps)}", 
        total_execution_time, final_screenshot_path
    )
    
    return len(failed_steps) == 0

class TestEnhancedScenarios(unittest.TestCase):
    """향상된 테스트 시나리오 실행"""
    
    def test_enhanced_scenarios(self):
        print("🎬 Starting Enhanced Test Scenarios")
        print(f"📊 Target languages: {LANGUAGES}")
        print(f"📱 Target device: {UDID}")
        print(f"📦 Target app: {APP_PACKAGE}")
        
        # 테스트 케이스 로딩
        test_cases = load_enhanced_test_cases()
        if not test_cases:
            self.fail("No enhanced test cases loaded")
        
        print(f"📋 Loaded {len(test_cases)} test cases:")
        for case in test_cases:
            print(f"  - {case.test_id}: {case.description} ({len(case.steps)} steps)")
        
        # 드라이버 초기화
        driver = get_driver()
        wait = WebDriverWait(driver, int(os.getenv('EXPLICIT_WAIT', '20')))
        engine = EnhancedTestEngine(driver, int(os.getenv('EXPLICIT_WAIT', '20')))
        
        try:
            # WebView 컨텍스트 전환
            print(f"🔄 Switching to WebView context: {WEBVIEW_NAME}")
            available_contexts = driver.contexts
            print(f"Available contexts: {available_contexts}")
            driver.switch_to.context(WEBVIEW_NAME)
            
            total_tests = len(LANGUAGES) * len(test_cases)
            completed_tests = 0
            passed_tests = 0
            
            print(f"\n🎯 Total tests to execute: {total_tests}")
            
            # 언어별 테스트 실행
            for lang_index, lang in enumerate(LANGUAGES):
                print(f"\n🌐 Testing language {lang_index + 1}/{len(LANGUAGES)}: {lang.upper()}")
                
                # 언어 변경 (첫 번째 언어가 아닌 경우)
                if lang_index > 0:
                    try:
                        self._change_language(driver, wait, lang)
                        print(f"✅ Language changed to: {lang}")
                    except Exception as e:
                        print(f"⚠️  Language change failed: {e}")
                
                # 로그인
                try:
                    self._perform_login(driver, wait)
                    print("✅ Login successful")
                except Exception as e:
                    print(f"❌ Login failed: {e}")
                    continue
                
                # 각 테스트 케이스 실행
                for case_index, test_case in enumerate(test_cases):
                    print(f"\n📝 Test {case_index + 1}/{len(test_cases)} in {lang.upper()}")
                    
                    try:
                        result = execute_enhanced_test_case(engine, test_case, lang)
                        completed_tests += 1
                        if result:
                            passed_tests += 1
                    except Exception as e:
                        print(f"💥 Test case execution failed: {e}")
                        completed_tests += 1
                
                # 다음 언어를 위해 로그인 페이지로 이동
                if lang_index < len(LANGUAGES) - 1:
                    try:
                        driver.get(BASE_URL + LOGIN_PATH)
                        time.sleep(SLEEP_TIME)
                    except Exception as e:
                        print(f"⚠️  Failed to return to login page: {e}")
            
            # 최종 결과 리포트
            success_rate = (passed_tests / completed_tests) * 100 if completed_tests > 0 else 0
            print(f"\n🎉 Test Execution Complete!")
            print(f"📊 Final Results:")
            print(f"   - Total Tests: {completed_tests}/{total_tests}")
            print(f"   - Passed Tests: {passed_tests}")
            print(f"   - Failed Tests: {completed_tests - passed_tests}")
            print(f"   - Success Rate: {success_rate:.1f}%")
            print(f"📁 Results saved to: {RESULT_CSV_FILE}")
            print(f"📸 Screenshots saved to: {SCREENSHOT_DIR}")
            
        finally:
            driver.quit()
            print("🔚 Driver closed")
    
    def _change_language(self, driver, wait, lang):
        """언어 변경"""
        try:
            lang_btn = wait.until(EC.element_to_be_clickable(
                (AppiumBy.XPATH, "//button[contains(.,'select language')]")))
            lang_btn.click()
            
            # 언어 인덱스 매핑 (중국 앱 기준)
            index = {'zh': 1, 'ko': 2, 'en': 3}.get(lang, 1)
            selector = f"(//input[@name='select'])[{index}]"
            lang_input = wait.until(EC.element_to_be_clickable((AppiumBy.XPATH, selector)))
            lang_input.click()
            time.sleep(SLEEP_TIME)
        except Exception as e:
            print(f"Language change failed for {lang}: {e}")
            raise
    
    def _perform_login(self, driver, wait):
        """로그인 수행"""
        try:
            user_id_input = wait.until(EC.presence_of_element_located(
                (AppiumBy.CSS_SELECTOR, ".log_id input")))
            user_id_input.clear()
            user_id_input.send_keys(os.getenv('USER_ID', 'c89109'))
            
            user_pw_input = wait.until(EC.presence_of_element_located(
                (AppiumBy.XPATH, "//input[@type='password']")))
            user_pw_input.clear()
            user_pw_input.send_keys(os.getenv('USER_PW', 'mcnc1234!!'))
            
            login_btn = wait.until(EC.element_to_be_clickable(
                (AppiumBy.CSS_SELECTOR, ".btn01")))
            login_btn.click()
            time.sleep(SLEEP_TIME)
        except Exception as e:
            print(f"Login failed: {e}")
            raise

if __name__ == '__main__':
    unittest.main(verbosity=2)