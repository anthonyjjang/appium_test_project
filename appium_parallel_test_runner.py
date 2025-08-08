import unittest
import time
import os
import csv
import threading
import subprocess
from datetime import datetime
from concurrent.futures import ThreadPoolExecutor
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

# Configuration files from environment
DEVICES_CSV = os.getenv('DEVICES_CSV', 'devices.csv')
USERS_CSV = os.getenv('USERS_CSV', 'users.csv')
TEST_CASES_CSV = os.getenv('TEST_CASES_CSV', 'test_cases.csv')
TEST_STEPS_CSV = os.getenv('TEST_STEPS_CSV', 'test_steps.csv')
TEST_PAIRS_CSV = os.getenv('TEST_PAIRS_CSV', 'test_pairs.csv')

# App settings from environment
BASE_URL = os.getenv('BASE_URL', 'http://localhost/')
LOGIN_PATH = os.getenv('LOGIN_PATH', 'LOG1000')
SLEEP_TIME = int(os.getenv('SLEEP_TIME', '3'))

# Country specific settings
COUNTRY_SETTINGS = {
    'VN': {'languages': ['vi', 'ko', 'en'], 'default_lang': 'vi'},
    'CN': {'languages': ['zh', 'ko', 'en'], 'default_lang': 'zh'},
    'KR': {'languages': ['ko', 'en'], 'default_lang': 'ko'}
}

# Thread-safe logging
csv_lock = threading.Lock()

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

class DeviceConfig:
    def __init__(self, device_id, udid, platform_name, platform_version):
        self.device_id = device_id
        self.udid = udid
        self.platform_name = platform_name
        self.platform_version = platform_version

class UserConfig:
    def __init__(self, user_id, user_pw, country_code, app_package, webview_name, description):
        self.user_id = user_id
        self.user_pw = user_pw
        self.country_code = country_code
        self.app_package = app_package
        self.webview_name = webview_name
        self.description = description
        self.languages = COUNTRY_SETTINGS[country_code]['languages']
        self.default_lang = COUNTRY_SETTINGS[country_code]['default_lang']

class TestPair:
    def __init__(self, pair_id, device_config, user_configs, languages, description):
        self.pair_id = pair_id
        self.device_config = device_config
        self.user_configs = user_configs  # 여러 사용자 설정 목록
        self.languages = languages.split(';')  # 세미콜론으로 구분된 언어 목록
        self.description = description

def read_csv_file(file_path):
    """Read CSV file and return list of dictionaries"""
    with open(file_path, 'r', encoding='utf-8') as f:
        return list(csv.DictReader(f))

def get_connected_devices():
    """Get list of connected Android devices"""
    try:
        # Run adb devices command
        result = subprocess.run(['adb', 'devices'], capture_output=True, text=True)
        
        if result.returncode != 0:
            print("Error running adb devices command")
            return []
        
        # Parse the output
        lines = result.stdout.strip().split('\n')[1:]  # Skip the first line (header)
        devices = []
        
        for line in lines:
            if line.strip():
                parts = line.split()
                if len(parts) >= 2 and parts[1] == 'device':
                    device_info = get_device_info(parts[0])
                    if device_info:
                        devices.append(device_info)
        
        return devices
    except Exception as e:
        print(f"Error detecting devices: {str(e)}")
        return []

def get_device_info(udid):
    """Get detailed information about a specific device"""
    try:
        # Get device properties
        result = subprocess.run(['adb', '-s', udid, 'shell', 'getprop'], 
                              capture_output=True, text=True)
        
        if result.returncode != 0:
            return None
            
        # Parse properties
        props = {}
        for line in result.stdout.split('\n'):
            if ': ' in line:
                key, value = line.split(': ', 1)
                key = key.strip('[]')
                value = value.strip('[]')
                props[key] = value
        
        return {
            'udid': udid,
            'platform_name': 'Android',
            'platform_version': props.get('ro.build.version.release', ''),
            'device_name': props.get('ro.product.model', '')
        }
    except Exception as e:
        print(f"Error getting device info for {udid}: {str(e)}")
        return None

def update_devices_csv(connected_devices):
    """Update devices.csv with currently connected devices"""
    try:
        # Read existing device configurations
        existing_configs = {}
        if os.path.exists(DEVICES_CSV):
            with open(DEVICES_CSV, 'r', encoding='utf-8') as f:
                reader = csv.DictReader(f)
                for row in reader:
                    existing_configs[row['udid']] = row
        
        # Update configurations with connected devices
        updated_configs = []
        for device in connected_devices:
            config = existing_configs.get(device['udid'], {})
            updated_config = {
                'device_id': config.get('device_id', f"DEVICE_{device['udid'][:8]}"),
                'udid': device['udid'],
                'platform_name': device['platform_name'],
                'platform_version': device['platform_version']
            }
            updated_configs.append(updated_config)
        
        # Write updated configurations back to CSV
        if updated_configs:
            with open(DEVICES_CSV, 'w', newline='', encoding='utf-8') as f:
                writer = csv.DictWriter(f, fieldnames=updated_configs[0].keys())
                writer.writeheader()
                writer.writerows(updated_configs)
            
        return len(updated_configs) > 0
    except Exception as e:
        print(f"Error updating devices.csv: {str(e)}")
        return False

def load_configurations():
    """Load device and user configurations from CSV files"""
    try:
        # Get connected devices first
        connected_devices = get_connected_devices()
        if not connected_devices:
            print("No devices connected!")
            return [], []
            
        # Update devices.csv with connected devices
        if not update_devices_csv(connected_devices):
            print("Failed to update devices configuration!")
            return [], []
        
        # Now read the updated devices.csv
        devices_data = read_csv_file(DEVICES_CSV)
        users_data = read_csv_file(USERS_CSV)
        
        devices = []
        for row in devices_data:
            device = DeviceConfig(
                device_id=row['device_id'],
                udid=row['udid'],
                platform_name=row['platform_name'],
                platform_version=row['platform_version']
            )
            devices.append(device)
            
        users = []
        for row in users_data:
            user = UserConfig(
                user_id=row['user_id'],
                user_pw=row['user_pw'],
                country_code=row['country_code'],
                app_package=row['app_package'],
                webview_name=row['webview_name'],
                description=row['description']
            )
            users.append(user)
            
        return devices, users
    except Exception as e:
        print(f"Error loading configurations: {str(e)}")
        return [], []

def load_test_cases_from_csv():
    """Read test scenarios from CSV files"""
    try:
        cases_data = read_csv_file(TEST_CASES_CSV)
        steps_data = read_csv_file(TEST_STEPS_CSV)
        
        test_cases = []
        for case in cases_data:
            # Get all steps for current test case
            case_steps = [step for step in steps_data if step['test_id'] == case['test_id']]
            # Sort steps by order
            case_steps.sort(key=lambda x: int(x['step_order']))
            
            steps = []
            for step in case_steps:
                test_step = TestStep(
                    action=step['action'],
                    selector_type=step['selector_type'],
                    selector_value=step['selector_value'],
                    input_value=step['input_value'] if step['input_value'] else None,
                    description=step['description'] if step['description'] else None
                )
                steps.append(test_step)
            
            test_case = TestCase(
                test_id=case['test_id'],
                screen_id=case['screen_id'],
                url=case['url'],
                description=case['description'],
                steps=steps,
                expected_result=case['expected_result']
            )
            test_cases.append(test_case)
            
        return test_cases
    except Exception as e:
        print(f"Error loading test cases: {str(e)}")
        return []

def log_result(lang, test_id, screen_id, status, message, device_id, user_id, description=None):
    """Thread-safe logging of test results"""
    with csv_lock:
        file_exists = os.path.isfile(RESULT_CSV_FILE)
        with open(RESULT_CSV_FILE, mode='a', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            if not file_exists:
                writer.writerow(['timestamp', 'device_id', 'user_id', 'language', 
                               'test_id', 'screen_id', 'description', 'status', 'message'])
            writer.writerow([
                datetime.now().isoformat(),
                device_id,
                user_id,
                lang,
                test_id,
                screen_id,
                description,
                status,
                message
            ])

def get_driver(device_config, user_config, appium_port):
    """Initialize Appium driver with device-specific capabilities"""
    capabilities = dict(
        platformName=device_config.platform_name,
        platformVersion=device_config.platform_version,
        automationName='uiautomator2',
        udid=device_config.udid,
        appPackage=user_config.app_package,
        appActivity=os.getenv('DEFAULT_APP_ACTIVITY', 'com.mcnc.bizmob.cesco.SlideFragmentActivity'),
        noReset=True,
        fullReset=False
    )
    options = UiAutomator2Options().load_capabilities(capabilities)
    appium_host = os.getenv('APPIUM_HOST', 'localhost')
    driver = webdriver.Remote(f'http://{appium_host}:{appium_port}', options=options)
    driver.implicitly_wait(int(os.getenv('IMPLICIT_WAIT', '10')))
    return driver

def change_language(driver, wait, lang, country_code):
    """Change application language based on country settings"""
    try:
        lang_btn = wait.until(EC.element_to_be_clickable((AppiumBy.XPATH, "//button[contains(.,'select language')]")))
        lang_btn.click()
        
        # Get language index based on country settings
        languages = COUNTRY_SETTINGS[country_code]['languages']
        index = languages.index(lang) + 1  # 1-based index for XPath
        
        selector = f"(//input[@name='select'])[{index}]"
        lang_input = wait.until(EC.element_to_be_clickable((AppiumBy.XPATH, selector)))
        lang_input.click()
        return True
    except Exception as e:
        print(f"Language change failed for {lang}: {str(e)}")
        return False

def login(driver, wait, user_config):
    """Perform login with specific user credentials"""
    try:
        user_id = wait.until(EC.presence_of_element_located((AppiumBy.CSS_SELECTOR, ".log_id input")))
        user_id.clear()
        user_id.send_keys(user_config.user_id)

        user_pw = wait.until(EC.presence_of_element_located((AppiumBy.XPATH, "//input[@type='password']")))
        user_pw.clear()
        user_pw.send_keys(user_config.user_pw)

        login_btn = wait.until(EC.element_to_be_clickable((AppiumBy.CSS_SELECTOR, ".btn01")))
        login_btn.click()
        time.sleep(SLEEP_TIME)
        return True
    except Exception as e:
        print(f"Login failed for user {user_config.user_id}: {str(e)}")
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

def run_test_case(driver, wait, lang, test_case, device_config, user_config):
    """Execute a complete test case"""
    try:
        if test_case.url:
            full_url = BASE_URL + test_case.url
            driver.get(full_url)
            time.sleep(SLEEP_TIME)

        for step in test_case.steps:
            if not execute_test_step(driver, wait, step):
                raise Exception(f"Step failed: {step.description}")

        screenshot_path = os.path.join(SCREENSHOT_DIR, 
            f"{device_config.device_id}_{user_config.user_id}_{lang}_{test_case.test_id}_{test_case.screen_id}_pass.png")
        driver.save_screenshot(screenshot_path)
        
        log_result(lang, test_case.test_id, test_case.screen_id, "PASS", "", 
                  device_config.device_id, user_config.user_id, test_case.description)
        return True
    except Exception as e:
        screenshot_path = os.path.join(SCREENSHOT_DIR,
            f"{device_config.device_id}_{user_config.user_id}_{lang}_{test_case.test_id}_{test_case.screen_id}_fail.png")
        driver.save_screenshot(screenshot_path)
        
        log_result(lang, test_case.test_id, test_case.screen_id, "FAIL", str(e),
                  device_config.device_id, user_config.user_id, test_case.description)
        return False

def load_test_pairs(devices, users):
    """Load and validate test pairs configuration"""
    try:
        pairs_data = read_csv_file(TEST_PAIRS_CSV)
        
        # 디바이스와 사용자 맵 생성
        device_map = {d.udid: d for d in devices}
        user_map = {u.user_id: u for u in users}
        
        test_pairs = []
        for row in pairs_data:
            # 디바이스 존재 확인
            device = device_map.get(row['device_udid'])
            if not device:
                print(f"Warning: Invalid device UDID in pair {row['pair_id']}: {row['device_udid']}")
                continue
            
            # 사용자 목록 확인
            user_ids = row['user_ids'].split(';')
            user_configs = []
            invalid_users = False
            
            for user_id in user_ids:
                user = user_map.get(user_id)
                if not user:
                    print(f"Warning: Invalid user ID in pair {row['pair_id']}: {user_id}")
                    invalid_users = True
                    break
                user_configs.append(user)
            
            if invalid_users:
                continue
            
            # 언어 유효성 검증
            languages = row['languages'].split(';')
            valid_languages = set()
            
            # 모든 사용자의 국가 설정에서 지원하는 언어 확인
            for user in user_configs:
                user_languages = set(COUNTRY_SETTINGS[user.country_code]['languages'])
                if not valid_languages:
                    valid_languages = user_languages
                else:
                    valid_languages &= user_languages
            
            valid_test_languages = [lang for lang in languages if lang in valid_languages]
            
            if not valid_test_languages:
                print(f"Warning: No common valid languages for pair {row['pair_id']}")
                continue
            
            # 유효한 페어 생성
            test_pair = TestPair(
                pair_id=row['pair_id'],
                device_config=device,
                user_configs=user_configs,
                languages=row['languages'],
                description=row['description']
            )
            test_pairs.append(test_pair)
            
        return test_pairs
    except Exception as e:
        print(f"Error loading test pairs: {str(e)}")
        return []

def run_pair_tests(test_pair, test_cases, appium_port):
    """Run tests for a specific device-user pair"""
    try:
        print(f"\nStarting tests for pair {test_pair.pair_id}:")
        print(f"- Description: {test_pair.description}")
        print(f"- Device: {test_pair.device_config.device_id} ({test_pair.device_config.udid})")
        print(f"- Users: {[user.user_id for user in test_pair.user_configs]}")
        print(f"- Languages: {test_pair.languages}")
        
        for user_config in test_pair.user_configs:
            print(f"\nTesting with user: {user_config.user_id} ({user_config.country_code})")
            
            driver = get_driver(test_pair.device_config, user_config, appium_port)
            wait = WebDriverWait(driver, int(os.getenv('EXPLICIT_WAIT', '20')))
            
            try:
                print("Available contexts:", driver.contexts)
                driver.switch_to.context(user_config.webview_name)
                
                for lang in test_pair.languages:
                    print(f"\nTesting language: {lang}")
                    if not change_language(driver, wait, lang, user_config.country_code):
                        continue
                    
                    if not login(driver, wait, user_config):
                        continue
                    
                    for test_case in test_cases:
                        run_test_case(driver, wait, lang, test_case, 
                                    test_pair.device_config, user_config)
                    
                    driver.get(BASE_URL + LOGIN_PATH)
                    time.sleep(SLEEP_TIME)
                    
            finally:
                driver.quit()
                
    except Exception as e:
        print(f"Test pair execution failed for {test_pair.pair_id}: {str(e)}")

def main():
    """Main execution function"""
    # Check for connected devices first
    connected_devices = get_connected_devices()
    if not connected_devices:
        print("No devices connected. Please connect devices and try again.")
        return
        
    print(f"Found {len(connected_devices)} connected device(s):")
    for device in connected_devices:
        print(f"- {device['device_name']} ({device['udid']})")
    
    # Load configurations
    devices, users = load_configurations()
    if not devices or not users:
        print("Failed to load required configurations")
        return
    
    # Load test pairs
    test_pairs = load_test_pairs(devices, users)
    if not test_pairs:
        print("No valid test pairs found")
        return
        
    # Load test cases
    test_cases = load_test_cases_from_csv()
    if not test_cases:
        print("No test cases found")
        return
    
    print(f"\nStarting tests with {len(test_pairs)} test pair(s):")
    for pair in test_pairs:
        print(f"- {pair.pair_id}: {pair.description}")
    
    # Create a thread pool for parallel execution
    with ThreadPoolExecutor(max_workers=len(test_pairs)) as executor:
        futures = []
        for i, pair in enumerate(test_pairs):
            base_port = int(os.getenv('APPIUM_PORT', '4723'))
            appium_port = base_port + i
            
            print(f"\nInitializing test pair {pair.pair_id}:")
            print(f"- Description: {pair.description}")
            print(f"- Device: {pair.device_config.device_id} ({pair.device_config.udid})")
            print(f"- Users: {[user.user_id for user in pair.user_configs]}")
            print(f"- Languages: {pair.languages}")
            print(f"- Appium Port: {appium_port}")
            
            future = executor.submit(run_pair_tests, pair, test_cases, appium_port)
            futures.append(future)
        
        # Wait for all tests to complete
        for future in futures:
            future.result()
    
    print("\nAll tests completed. Check results in:")
    print(f"- Screenshots: {SCREENSHOT_DIR}")
    print(f"- Test Results: {RESULT_CSV_FILE}")

if __name__ == '__main__':
    main() 