# appium_test_runner.py
import unittest
import time
import os
import json
import csv
from datetime import datetime
from appium import webdriver
from appium.webdriver.common.appiumby import AppiumBy
from appium.options.android import UiAutomator2Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

start_time = datetime.now().strftime('%Y%m%d_%H%M%S')

# SCREENSHOT_DIR 경로에 테스트 시작 시간을 포함
SCREENSHOT_DIR = os.path.join('screenshots', f'test_{start_time}')
os.makedirs(SCREENSHOT_DIR, exist_ok=True)
#TEST_DEFINITION_FILE = 'test_cases.json'
#TEST_DEFINITION_FILE = 'test_cases_navi.json'
TEST_DEFINITION_FILE = 'test_cases_search.json'
RESULT_CSV_FILE = 'test_results.csv'
#BASE_URL = "../"  # 접속할 기본 URL
#BASE_URL = "http://localhost/"  # 접속할 기본 URL
BASE_URL = "http://10.200.11.143:8080/"  # 접속할 기본 URL
LOGIN_PATH = 'LOG1000'
LANGUAGES = ['vi','ko','en']  # 지원 언어 목록
SLEEP_TIME = 3

# Appium 드라이버 초기화 ([개선]다수의 디바이스 병력 실행 필요)
def get_driver():
    capabilities = dict(
        platformName='Android',
        automationName='uiautomator2',
        udid='R3CW509J2RE',
        appPackage='com.cesco.oversea.srs.dev',
        appActivity='com.mcnc.bizmob.cesco.SlideFragmentActivity',
        noReset=True,
        fullReset=False
    )
    options = UiAutomator2Options().load_capabilities(capabilities)
    driver = webdriver.Remote('http://localhost:4723', options=options)
    driver.implicitly_wait(10)
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
        user_id.send_keys("c20700")

        user_pw = wait.until(EC.presence_of_element_located((AppiumBy.XPATH, "//input[@type='password']")))
        user_pw.clear()
        user_pw.send_keys("20700")

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
                el = wait.until(EC.presence_of_element_located((AppiumBy.XPATH, "//input[@placeholder='검색어 입력']")))
                #el = wait.until(EC.presence_of_element_located((AppiumBy.ID, selector_id)))
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
        wait = WebDriverWait(driver, 20)
        #for context in contexts:
            #    print("INIT Available context: " + context)
        driver.switch_to.context('WEBVIEW_com.cesco.oversea.srs.dev')
        for lang in LANGUAGES:
            #화면 로딩 후후
            change_language(driver, wait, lang)
            login(driver, wait)
            #화면 로딩 후 
            # test_navigation(driver, wait)
            for case in cases:
                # run_test_case(driver, wait, lang, case)
                # 고객 검색 테스트
                search_test_case(driver, wait, lang, case)
                # navi_test_case(driver, wait, lang, case)
            #로그인 페이지로 이동
            # search_test(driver, wait, lang)
            go_login_page(driver, wait)
        driver.quit()

if __name__ == '__main__':
    unittest.main()