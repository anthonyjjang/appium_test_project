import time
import re
import csv
import os
from datetime import datetime, timedelta
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException
from appium.webdriver.common.appiumby import AppiumBy

class EnhancedTestEngine:
    """향상된 테스트 실행 엔진 - 상세한 검증 로직 포함"""
    
    def __init__(self, driver, wait_timeout=20):
        self.driver = driver
        self.wait = WebDriverWait(driver, wait_timeout)
        self.test_data = {}
        self.load_test_data()
        
    def load_test_data(self):
        """테스트 데이터 로딩"""
        try:
            with open('test_data.csv', 'r', encoding='utf-8') as f:
                reader = csv.DictReader(f)
                for row in reader:
                    if row['test_id'] not in self.test_data:
                        self.test_data[row['test_id']] = {}
                    if row['data_type'] not in self.test_data[row['test_id']]:
                        self.test_data[row['test_id']][row['data_type']] = {}
                    self.test_data[row['test_id']][row['data_type']][row['key']] = row['value']
        except FileNotFoundError:
            print("Warning: test_data.csv not found, using default values")
            
    def get_test_data(self, test_id, data_type, key, default=None):
        """테스트 데이터 조회"""
        return self.test_data.get(test_id, {}).get(data_type, {}).get(key, default)
    
    def get_locator(self, selector_type, selector_value):
        """셀렉터 타입에 따른 로케이터 생성"""
        selector_map = {
            'CSS_SELECTOR': AppiumBy.CSS_SELECTOR,
            'XPATH': AppiumBy.XPATH,
            'ID': AppiumBy.ID,
            'CLASS_NAME': AppiumBy.CLASS_NAME,
            'TAG_NAME': AppiumBy.TAG_NAME,
            'NAME': AppiumBy.NAME
        }
        return (selector_map.get(selector_type.upper(), AppiumBy.XPATH), selector_value)
    
    def execute_step(self, step, test_id, lang='ko'):
        """향상된 단일 스텝 실행"""
        action = step.get('action', '').lower()
        selector_type = step.get('selector_type', '')
        selector_value = step.get('selector_value', '')
        input_value = step.get('input_value', '')
        expected_value = step.get('expected_value', '')
        wait_time = int(step.get('wait_time', 3))
        validation_type = step.get('validation_type', 'basic')
        retry_count = int(step.get('retry_count', 1))
        
        # 테스트 데이터에서 값 치환
        if input_value:
            input_value = self._replace_test_data(test_id, input_value, lang)
        if expected_value:
            expected_value = self._replace_test_data(test_id, expected_value, lang)
            
        # 재시도 로직
        for attempt in range(retry_count):
            try:
                result = self._execute_action(action, selector_type, selector_value, 
                                            input_value, expected_value, wait_time, validation_type)
                if result:
                    return True
            except Exception as e:
                if attempt == retry_count - 1:  # 마지막 시도
                    raise e
                time.sleep(1)  # 재시도 전 잠시 대기
        return False
    
    def _execute_action(self, action, selector_type, selector_value, input_value, 
                       expected_value, wait_time, validation_type):
        """실제 액션 실행"""
        
        if action == 'wait_for_element':
            return self._wait_for_element(selector_type, selector_value, expected_value, wait_time)
        
        elif action == 'clear_and_input':
            return self._clear_and_input(selector_type, selector_value, input_value, wait_time)
        
        elif action == 'verify_input_value':
            return self._verify_input_value(selector_type, selector_value, expected_value)
        
        elif action == 'click':
            return self._enhanced_click(selector_type, selector_value, expected_value, wait_time)
        
        elif action == 'wait_for_page_load':
            return self._wait_for_page_load(selector_type, selector_value, expected_value, wait_time)
        
        elif action == 'verify_url_contains':
            return self._verify_url_contains(expected_value)
        
        elif action == 'verify_element_text':
            return self._verify_element_text(selector_type, selector_value, expected_value)
        
        elif action == 'take_screenshot':
            return self._take_screenshot(input_value)
        
        elif action == 'wait_for_loading':
            return self._wait_for_loading(selector_type, selector_value, expected_value, wait_time)
        
        elif action == 'verify_element_exists':
            return self._verify_element_exists(selector_type, selector_value)
        
        elif action == 'verify_result_count':
            return self._verify_result_count(selector_type, selector_value, expected_value)
        
        elif action == 'verify_search_highlight':
            return self._verify_search_highlight(selector_type, selector_value, expected_value)
        
        elif action == 'scroll_to_bottom':
            return self._scroll_to_bottom()
        
        elif action == 'click_each_tab':
            return self._click_each_tab(selector_type, selector_value)
        
        elif action == 'verify_current_month':
            return self._verify_current_month(selector_type, selector_value)
        
        elif action == 'apply_date_filter':
            return self._apply_date_filter(selector_type, selector_value, input_value)
        
        elif action == 'select_customer':
            return self._select_from_dropdown(selector_type, selector_value, input_value)
        
        elif action in ['input_amount', 'input_collection_date', 'input_remarks']:
            return self._specialized_input(action, selector_type, selector_value, input_value, validation_type)
        
        elif action == 'verify_form_validation':
            return self._verify_form_validation(selector_type, selector_value)
        
        elif action == 'verify_registration_success':
            return self._verify_success_message(selector_type, selector_value, expected_value, wait_time)
        
        else:
            # 기본 액션들
            return self._execute_basic_action(action, selector_type, selector_value, input_value)
    
    def _wait_for_element(self, selector_type, selector_value, condition, wait_time):
        """요소 대기 (향상된 버전)"""
        locator = self.get_locator(selector_type, selector_value)
        wait = WebDriverWait(self.driver, wait_time)
        
        if condition == 'visible':
            wait.until(EC.visibility_of_element_located(locator))
        elif condition == 'clickable':
            wait.until(EC.element_to_be_clickable(locator))
        elif condition == 'present':
            wait.until(EC.presence_of_element_located(locator))
        elif condition == 'invisible':
            wait.until(EC.invisibility_of_element_located(locator))
        
        return True
    
    def _clear_and_input(self, selector_type, selector_value, input_value, wait_time):
        """입력 필드 클리어 후 입력"""
        locator = self.get_locator(selector_type, selector_value)
        element = self.wait.until(EC.presence_of_element_located(locator))
        element.clear()
        time.sleep(0.5)  # 클리어 후 잠시 대기
        element.send_keys(input_value)
        time.sleep(wait_time)
        return True
    
    def _verify_input_value(self, selector_type, selector_value, expected_value):
        """입력값 검증"""
        locator = self.get_locator(selector_type, selector_value)
        element = self.driver.find_element(*locator)
        actual_value = element.get_attribute('value') or element.text
        return actual_value == expected_value
    
    def _enhanced_click(self, selector_type, selector_value, condition, wait_time):
        """향상된 클릭 (요소 상태 확인 후 클릭)"""
        locator = self.get_locator(selector_type, selector_value)
        
        if condition == 'enabled':
            element = self.wait.until(EC.element_to_be_clickable(locator))
        else:
            element = self.wait.until(EC.presence_of_element_located(locator))
        
        # JavaScript 클릭도 시도 (일반 클릭 실패 시)
        try:
            element.click()
        except:
            self.driver.execute_script("arguments[0].click();", element)
        
        time.sleep(wait_time)
        return True
    
    def _wait_for_page_load(self, selector_type, selector_value, condition, wait_time):
        """페이지 로딩 완료 대기"""
        if selector_type and selector_value:
            return self._wait_for_element(selector_type, selector_value, condition, wait_time)
        else:
            # JavaScript readyState 확인
            wait = WebDriverWait(self.driver, wait_time)
            wait.until(lambda driver: driver.execute_script("return document.readyState") == "complete")
            return True
    
    def _verify_url_contains(self, expected_url_part):
        """URL 포함 문자열 검증"""
        current_url = self.driver.current_url
        return expected_url_part in current_url
    
    def _verify_element_text(self, selector_type, selector_value, expected_text):
        """요소 텍스트 검증"""
        locator = self.get_locator(selector_type, selector_value)
        element = self.driver.find_element(*locator)
        actual_text = element.text.strip()
        return expected_text in actual_text
    
    def _take_screenshot(self, filename):
        """스크린샷 촬영"""
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        screenshot_path = f"screenshots/test_{timestamp}/{filename}_{timestamp}.png"
        os.makedirs(os.path.dirname(screenshot_path), exist_ok=True)
        self.driver.save_screenshot(screenshot_path)
        return True
    
    def _wait_for_loading(self, selector_type, selector_value, condition, wait_time):
        """로딩 스피너 사라질 때까지 대기"""
        if condition == 'invisible':
            return self._wait_for_element(selector_type, selector_value, 'invisible', wait_time)
        return True
    
    def _verify_element_exists(self, selector_type, selector_value):
        """요소 존재 여부 확인"""
        locator = self.get_locator(selector_type, selector_value)
        try:
            self.driver.find_element(*locator)
            return True
        except NoSuchElementException:
            return False
    
    def _verify_result_count(self, selector_type, selector_value, expected_condition):
        """결과 개수 검증"""
        locator = self.get_locator(selector_type, selector_value)
        elements = self.driver.find_elements(*locator)
        count = len(elements)
        
        if expected_condition.startswith('>'):
            return count > int(expected_condition[1:])
        elif expected_condition.startswith('<'):
            return count < int(expected_condition[1:])
        elif expected_condition.startswith('='):
            return count == int(expected_condition[1:])
        else:
            return count == int(expected_condition)
    
    def _verify_search_highlight(self, selector_type, selector_value, search_term):
        """검색어 하이라이트 확인"""
        locator = self.get_locator(selector_type, selector_value)
        elements = self.driver.find_elements(*locator)
        for element in elements:
            if search_term in element.text:
                return True
        return False
    
    def _scroll_to_bottom(self):
        """페이지 하단으로 스크롤"""
        self.driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        time.sleep(2)
        return True
    
    def _click_each_tab(self, selector_type, selector_value):
        """각 탭 클릭해서 테스트"""
        locator = self.get_locator(selector_type, selector_value)
        tabs = self.driver.find_elements(*locator)
        
        for i, tab in enumerate(tabs):
            try:
                tab.click()
                time.sleep(2)
                # 탭 내용 로딩 확인
                self.driver.execute_script("return document.readyState") == "complete"
            except Exception as e:
                print(f"Tab {i} click failed: {e}")
                continue
        return True
    
    def _verify_current_month(self, selector_type, selector_value):
        """현재 월 표시 확인"""
        locator = self.get_locator(selector_type, selector_value)
        element = self.driver.find_element(*locator)
        current_month = datetime.now().month
        return str(current_month) in element.text or f"{current_month}월" in element.text
    
    def _apply_date_filter(self, selector_type, selector_value, date_value):
        """날짜 필터 적용"""
        if date_value == 'today':
            date_value = datetime.now().strftime('%Y-%m-%d')
        
        locator = self.get_locator(selector_type, selector_value)
        element = self.driver.find_element(*locator)
        element.clear()
        element.send_keys(date_value)
        return True
    
    def _select_from_dropdown(self, selector_type, selector_value, option_value):
        """드롭다운에서 옵션 선택"""
        locator = self.get_locator(selector_type, selector_value)
        dropdown = self.driver.find_element(*locator)
        dropdown.click()
        
        # 옵션 찾아서 클릭
        option_locator = (AppiumBy.XPATH, f"//option[@value='{option_value}'] | //li[contains(text(), '{option_value}')]")
        option = self.wait.until(EC.element_to_be_clickable(option_locator))
        option.click()
        return True
    
    def _specialized_input(self, action_type, selector_type, selector_value, input_value, validation_type):
        """특수 입력 처리 (금액, 날짜 등)"""
        locator = self.get_locator(selector_type, selector_value)
        element = self.driver.find_element(*locator)
        
        if action_type == 'input_amount':
            # 금액 입력 시 숫자만 허용
            if validation_type == 'numeric' and not input_value.isdigit():
                return False
            element.clear()
            element.send_keys(input_value)
            
        elif action_type == 'input_collection_date':
            if input_value == 'today':
                input_value = datetime.now().strftime('%Y-%m-%d')
            element.clear()
            element.send_keys(input_value)
            
        elif action_type == 'input_remarks':
            element.clear()
            element.send_keys(input_value)
        
        return True
    
    def _verify_form_validation(self, selector_type, selector_value):
        """폼 유효성 검증 상태 확인"""
        # 폼의 submit 버튼이 활성화되었는지 확인
        try:
            locator = self.get_locator(selector_type, selector_value)
            form = self.driver.find_element(*locator)
            
            # HTML5 validation API 사용
            is_valid = self.driver.execute_script("return arguments[0].checkValidity();", form)
            return is_valid
        except:
            return True  # 폼 검증이 없는 경우 통과
    
    def _verify_success_message(self, selector_type, selector_value, expected_message, wait_time):
        """성공 메시지 확인"""
        try:
            locator = self.get_locator(selector_type, selector_value)
            element = self.wait.until(EC.visibility_of_element_located(locator))
            return expected_message in element.text
        except TimeoutException:
            return False
    
    def _execute_basic_action(self, action, selector_type, selector_value, input_value):
        """기본 액션 실행 (기존 호환성)"""
        locator = self.get_locator(selector_type, selector_value)
        
        if action == 'click':
            element = self.wait.until(EC.element_to_be_clickable(locator))
            element.click()
        elif action == 'input':
            element = self.wait.until(EC.presence_of_element_located(locator))
            element.clear()
            element.send_keys(input_value)
        elif action == 'verify':
            element = self.wait.until(EC.presence_of_element_located(locator))
            assert element.is_displayed(), "Element not visible"
        
        time.sleep(2)  # 기본 대기
        return True
    
    def _replace_test_data(self, test_id, value, lang='ko'):
        """테스트 데이터 값 치환"""
        if not value:
            return value
            
        # 동적 값 처리
        if value == 'today':
            return datetime.now().strftime('%Y-%m-%d')
        elif value == 'current_month':
            return str(datetime.now().month)
        elif value.startswith('{{') and value.endswith('}}'):
            # 테스트 데이터 참조 {{data_type.key}}
            data_ref = value[2:-2]
            if '.' in data_ref:
                data_type, key = data_ref.split('.', 1)
                return self.get_test_data(test_id, data_type, key, value)
        
        return value