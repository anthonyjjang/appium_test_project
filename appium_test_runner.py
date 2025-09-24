# appium_test_runner.py
import unittest
import time
import os
import json
import csv
from datetime import datetime
from dotenv import load_dotenv
from appium import webdriver
from appium.webdriver.common.appiumby import AppiumBy
from appium.options.android import UiAutomator2Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

# Load environment variables
load_dotenv()

start_time = datetime.now().strftime('%Y%m%d_%H%M%S')

# Load configuration from environment variables
SCREENSHOT_DIR = os.path.join('screenshots', f'test_{start_time}')
os.makedirs(SCREENSHOT_DIR, exist_ok=True)
TEST_DEFINITION_FILE = os.getenv('TEST_DEFINITION_FILE', 'test_cases_navi.json')
RESULT_CSV_FILE = 'test_results.csv'
BASE_URL = os.getenv('BASE_URL', 'http://localhost/')
LOGIN_PATH = os.getenv('LOGIN_PATH', 'LOG1000')
LANGUAGES = os.getenv('VI_LANGUAGES', 'vi,ko,en').split(',')
SLEEP_TIME = int(os.getenv('SLEEP_TIME', '4'))
WEBVIEW_NAME = os.getenv('VI_WEBVIEW_NAME', 'WEBVIEW_com.cesco.oversea.srs.viet')
APP_PACKAGE = os.getenv('VI_APP_PACKAGE', 'com.cesco.oversea.srs.viet')
APP_ACTIVITY = os.getenv('DEFAULT_APP_ACTIVITY', 'com.mcnc.bizmob.cesco.SlideFragmentActivity')
UDID = os.getenv('DEFAULT_UDID', 'RFCM902ZM9K')

USER_ID = os.getenv('USER_ID', 'c89109')
USER_PW = os.getenv('USER_PW', 'mcnc1234!!')
# Appium 드라이버 초기화 ([개선]다수의 디바이스 병력 실행 필요)
def get_driver():
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

# 테스트 결과 로그 저장
def log_result(lang, test_id, screen_id, status, message):
    file_exists = os.path.isfile(RESULT_CSV_FILE)
    with open(RESULT_CSV_FILE, mode='a', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        if not file_exists:
            writer.writerow(['timestamp', 'language', 'test_id', 'screen_id', 'status', 'message'])
        writer.writerow([datetime.now().isoformat(), lang, test_id, screen_id, status, message])
    
# 테스트 케이스 로딩
def load_test_cases():
    with open(TEST_DEFINITION_FILE, encoding='utf-8') as f:
        return json.load(f)

# 언어 변경 함수
def change_language(driver, wait, lang):
    try:
        # 언어 선택 버튼 클릭
        lang_btn = wait.until(EC.element_to_be_clickable((AppiumBy.XPATH, "//button[contains(.,'select language')]")))
        lang_btn.click()
        
        index = {'vi': 1, 'ko': 2, 'en': 3}.get(lang, 1)
        selector = f"(//input[@name='select'])[{index}]"
        lang_input = wait.until(EC.element_to_be_clickable((AppiumBy.XPATH, selector)))
        lang_input.click()
    except Exception as e:
        print(f"[언어 변경 실패] {lang}: {e}")
    
# 로그인 페이지 이동
def go_login_page(driver, wait):
    try:
        url = BASE_URL + LOGIN_PATH
        print(f"[로그페이지 이동 ]: {url}")
        if url:
            driver.get(url)
            time.sleep(SLEEP_TIME)
        print(f"[로그페이지 이동 성공]: {url}")
    except Exception as e:
        print(f"[로그페이지 이동 실패]: {e}")

# 로그인 테스트 ([개선]권한 별 계정 목록에 따른 실행 및 캡쳐, 계정별 처리리)
def login(driver, wait):
    try:
        user_id = wait.until(EC.presence_of_element_located((AppiumBy.CSS_SELECTOR, ".log_id input")))
        user_id.clear()
        user_id.send_keys(USER_ID)

        user_pw = wait.until(EC.presence_of_element_located((AppiumBy.XPATH, "//input[@type='password']")))
        user_pw.clear()
        user_pw.send_keys(USER_PW)

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

# 네비게이션 메뉴 테스트
def test_navigation(driver, wait):
    try:
        menu_btn = wait.until(EC.element_to_be_clickable((AppiumBy.XPATH, "//nav//button[contains(.,'Menu')]")))
        menu_btn.click()
        print("[네비게이션 메뉴] 열림")
    except Exception as e:
        print(f"[네비게이션 실패]: {e}")

# 단일 테스트 실행
def run_test_case(driver, wait, lang, case):
    test_id = case.get("test_id")
    screen_id = case.get("screen_id")
    try:
        url = case.get("url")
        if url:
            driver.get(url)
            time.sleep(SLEEP_TIME)

        for step in case.get("steps", []):
            action = step.get("action")
            selector = step.get("selector")
            value = step.get("value")
            if action == "click":
                el = wait.until(EC.element_to_be_clickable((AppiumBy.XPATH, selector)))
                el.click()
            elif action == "input":
                el = wait.until(EC.presence_of_element_located((AppiumBy.XPATH, selector)))
                el.clear()
                el.send_keys(value)

        expected = case.get("assert_text")
        if expected:
            body = driver.page_source
            assert expected in body, f"'{expected}' not found"

        screenshot_path = os.path.join(SCREENSHOT_DIR, f"{lang}_{test_id}_{screen_id}_pass.png")
        driver.save_screenshot(screenshot_path)
        log_result(lang, test_id, screen_id, "PASS", "")
    except Exception as e:
        screenshot_path = os.path.join(SCREENSHOT_DIR, f"{lang}_{test_id}_{screen_id}_fail.png")
        driver.save_screenshot(screenshot_path)
        log_result(lang, test_id, screen_id, "FAIL", str(e))
# 서치 테스트 실행
def search_test_case(driver, wait, lang, case):
    test_id = case.get("test_id")
    screen_id = case.get("screen_id") 

    try:
        #if(screen_id=="CUS1000" and lang=="ko"):
        url = BASE_URL+case.get("url")
        if url:
            driver.get(url)
            time.sleep(SLEEP_TIME)

        for step in case.get("steps", []):
            action = step.get("action")
            selector_css = step.get("selector_css")
            selector_xpath = step.get("selector_xpath")
            selector_id = step.get("selector_id")
            value = step.get("value")
            if action == "click":
                #el = wait.until(EC.element_to_be_clickable((AppiumBy.XPATH, selector_css)))
                #el = wait.until(EC.element_to_be_clickable((AppiumBy.CSS_SELECTOR, selector_css)))
                el = wait.until(EC.element_to_be_clickable((AppiumBy.ID, selector_id)))
                el.click()
            elif action == "input":
                #el = wait.until(EC.presence_of_element_located((AppiumBy.XPATH, selector_css)))
                #el = wait.until(EC.presence_of_element_located((AppiumBy.CSS_SELECTOR, selector_css)))
                #el = wait.until(EC.presence_of_element_located((AppiumBy.CSS_SELECTOR, ".active > input")))
                #el = wait.until(EC.presence_of_element_located((AppiumBy.XPATH, "//input[@placeholder='검색어 입력']")))
                el = wait.until(EC.element_to_be_clickable((AppiumBy.ID, selector_id)))
                try:
                    el.clear()
                    el.send_keys(value)
                except Exception as e:
                    print(f"[입력 실패]: {e}")

        expected = case.get("assert_text")
        if expected:
            body = driver.page_source
            assert expected in body, f"'{expected}' not found"

        screenshot_path = os.path.join(SCREENSHOT_DIR, f"{lang}_{test_id}_{screen_id}_pass.png")
        driver.save_screenshot(screenshot_path)
        log_result(lang, test_id, screen_id, "PASS", "")
    except Exception as e:
        screenshot_path = os.path.join(SCREENSHOT_DIR, f"{lang}_{test_id}_{screen_id}_fail.png")
        driver.save_screenshot(screenshot_path)
        log_result(lang, test_id, screen_id, "FAIL", str(e))
# 서치 테스트 실행
def search_test(driver, wait, lang):
    
    try:
        url = BASE_URL+"CUS1000"
        if url:
            driver.get(url)
            time.sleep(SLEEP_TIME)
            el = wait.until(EC.presence_of_element_located((AppiumBy.XPATH, "//input[@placeholder='검색어 입력']")))
            el.clear()
            el.send_keys("12")
            el = wait.until(EC.element_to_be_clickable((AppiumBy.CSS_SELECTOR, ".active .btn_search")))
            el.click()
        time.sleep(SLEEP_TIME)
        screenshot_path = os.path.join(SCREENSHOT_DIR, f"{lang}_search_pass.png")
        driver.save_screenshot(screenshot_path)
        #log_result(lang, test_id, screen_id, "PASS", "")
    except Exception as e:
        screenshot_path = os.path.join(SCREENSHOT_DIR, f"{lang}_search_fail.png")
        driver.save_screenshot(screenshot_path)
        #log_result(lang, test_id, screen_id, "FAIL", str(e))
# 네비게이션션 테스트 실행
def navi_test_case(driver, wait, lang, case):
    test_id = case.get("test_id")
    screen_id = case.get("screen_id")
    url = case.get("url")
    assert_text = case.get("assert_text")
    try:
        go_url = BASE_URL + url
        if go_url:
            driver.get(go_url)
            time.sleep(SLEEP_TIME)
        print(f"[페이지 이동 ]: {go_url}")
        screenshot_path = os.path.join(SCREENSHOT_DIR, f"{lang}_{test_id}_{assert_text}_pass.png")
        driver.save_screenshot(screenshot_path)
        log_result(lang, test_id, screen_id, "PASS", "")
    except Exception as e:
        screenshot_path = os.path.join(SCREENSHOT_DIR, f"{lang}_{test_id}_{assert_text}_fail.png")
        driver.save_screenshot(screenshot_path)
        log_result(lang, test_id, screen_id, "FAIL", str(e))

# unittest 실행
class TestAllLanguages(unittest.TestCase):
    def test_01_login(self):
        cases = load_test_cases()
        driver = get_driver()
        wait = WebDriverWait(driver, int(os.getenv('EXPLICIT_WAIT', '20')))
        # WebView 컨텍스트 전환 (대기 로직 포함)
        print(f"🔄 Waiting for WebView context: {WEBVIEW_NAME}")
        
        # WebView가 로드될 때까지 최대 30초 대기
        max_wait_time = 30
        wait_interval = 2
        waited_time = 0
        
        while waited_time < max_wait_time:
            available_contexts = driver.contexts
            print(f"Available contexts: {available_contexts}")
            
            if WEBVIEW_NAME in available_contexts:
                print(f"✅ WebView context found: {WEBVIEW_NAME}")
                driver.switch_to.context(WEBVIEW_NAME)
                break
            else:
                print(f"⏳ WebView not ready, waiting... ({waited_time}s/{max_wait_time}s)")
                time.sleep(wait_interval)
                waited_time += wait_interval
        
        if waited_time >= max_wait_time:
            print(f"⚠️  WebView context not found after {max_wait_time}s, using NATIVE_APP")
            print(f"Available contexts: {driver.contexts}")
        else:
            print(f"✅ Successfully switched to WebView context: {WEBVIEW_NAME}")
        for lang in LANGUAGES:
            #화면 로딩 후후
            change_language(driver, wait, lang)
            login(driver, wait)
            #화면 로딩 후 
            # test_navigation(driver, wait)
            for case in cases:
                # run_test_case(driver, wait, lang, case)
                # 고객 검색 테스트
                # search_test_case(driver, wait, lang, case)
                navi_test_case(driver, wait, lang, case)
            #로그인 페이지로 이동
            # search_test(driver, wait, lang)
            go_login_page(driver, wait)
        driver.quit()

if __name__ == '__main__':
    unittest.main()