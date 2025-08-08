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
TEST_EXCEL_FILE = os.getenv('TEST_EXCEL_FILE', 'test_scenarios.xlsx')

# App settings from environment (Excel runner specific - Vietnam focused)
BASE_URL = os.getenv('BASE_URL', 'http://localhost/')
LOGIN_PATH = os.getenv('LOGIN_PATH', 'LOG1000')
LANGUAGES = os.getenv('EXCEL_LANGUAGES', 'vi,ko,en').split(',')
SLEEP_TIME = int(os.getenv('SLEEP_TIME', '3'))
WEBVIEW_NAME = os.getenv('EXCEL_WEBVIEW_NAME', 'WEBVIEW_com.cesco.oversea.srs.viet')
APP_PACKAGE = os.getenv('EXCEL_APP_PACKAGE', 'com.cesco.oversea.srs.viet')
APP_ACTIVITY = os.getenv('DEFAULT_APP_ACTIVITY', 'com.mcnc.bizmob.cesco.SlideFragmentActivity')
UDID = os.getenv('EXCEL_UDID', 'RFCX715QHAL')

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
        fullReset=False
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

def load_test_cases_from_excel():
    """Read test scenarios from Excel file"""
    try:
        # Read main test cases sheet
        df_cases = pd.read_excel(TEST_EXCEL_FILE, sheet_name='TestCases')
        # Read test steps sheet
        df_steps = pd.read_excel(TEST_EXCEL_FILE, sheet_name='TestSteps')
        
        test_cases = []
        
        for _, case in df_cases.iterrows():
            # Get all steps for current test case
            case_steps = df_steps[df_steps['test_id'] == case['test_id']].sort_values('step_order')
            
            steps = []
            for _, step in case_steps.iterrows():
                test_step = TestStep(
                    action=step['action'],
                    selector_type=step['selector_type'],
                    selector_value=step['selector_value'],
                    input_value=step['input_value'] if 'input_value' in step else None,
                    description=step['description'] if 'description' in step else None
                )
                steps.append(test_step)
            
            test_case = TestCase(
                test_id=case['test_id'],
                screen_id=case['screen_id'],
                url=case['url'],
                description=case['description'],
                steps=steps,
                expected_result=case['expected_result'] if 'expected_result' in case else None
            )
            test_cases.append(test_case)
            
        return test_cases
    except Exception as e:
        print(f"Error loading test cases from Excel: {str(e)}")
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

class TestExcelScenarios(unittest.TestCase):
    def test_all_scenarios(self):
        # Load test cases from Excel
        test_cases = load_test_cases_from_excel()
        if not test_cases:
            self.fail("No test cases loaded from Excel file")

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
    unittest.main() 