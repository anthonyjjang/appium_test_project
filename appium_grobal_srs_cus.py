import unittest
import json
import time
import os
# Import Appium UiAutomator2 driver for Android platforms (AppiumOptions)
from appium import webdriver
from appium.webdriver.common.appiumby import AppiumBy
from appium.options.android import UiAutomator2Options
# Import Selenium webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
capabilities = dict(
    platformName='Android',
    automationName='uiautomator2',
    udid = 'RFCM902ZM9K', #테스트 단말기 목록, 계정정보 외 시나리오 기반으로 진행행, 'ce0916097236850f05'(A90 이창건 매니저 테스트폰)
    #deviceName='Samsung 11',
    appPackage='com.cesco.oversea.srs.viet',
    appActivity='com.mcnc.bizmob.cesco.SlideFragmentActivity',
    #language='en',
    #locale='US',
    noReset=True,  # 앱 데이터 유지
    fullReset=False,  # 앱을 다시 설치하지 않음
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

appium_server_url = 'http://localhost:4723' #앱티업 서버 정보보

# Converts capabilities to AppiumOptions instance
capabilities_options = UiAutomator2Options().load_capabilities(capabilities)

# 캡처 저장 경로
screenshot_dir = os.path.join(os.getcwd(), "screenshots_cn")
os.makedirs(screenshot_dir, exist_ok=True)

# 프로그램 목록
program_list = ["GNB2000", "CUS1000", "CUS1121", "RTP1000", "RTP1200", "RTP2000", "RTP2200"]  # 필요한 만큼 추가 가능
#program_list = ["CUS1000"]  # 필요한 만큼 추가 가능
language_list = ["ko","vi","zh"]
#language_list = ["vi"]
base_url = "http://localhost/"  # 접속할 기본 URL

class TestAppium(unittest.TestCase):
    def setUp(self) -> None:
        self.driver = webdriver.Remote(command_executor=appium_server_url,options=capabilities_options)
        self.driver.implicitly_wait(10)  # 암시적 대기 시간 추가
    def tearDown(self) -> None:
        if self.driver:
            self.driver.quit()
    def get_current_url(self, message):
        current_url = self.driver.execute_script("return window.location.href;")
        print(f"{message}Current page URL: {current_url}")
        return current_url
    def save_configuration_values(self):
         # configuration 객체의 모든 하위 값 확인
        configuration_values = self.driver.execute_script("""
            var configValues = {};
            for (var key in configuration) {
                if (configuration.hasOwnProperty(key)) {
                    configValues[key] = configuration[key];
                }
            }
            return configValues;
        """)
        with open('configuration_values.json', 'w', encoding='utf-8') as f:
            json.dump(configuration_values, f, ensure_ascii=False, indent=4)
        print("Configuration values saved to configuration_values.json")
    def get_current_context(self):
        current_context = self.driver.context
        print(f"Current context: {current_context}")
        return current_context
    def test_login_srs(self) -> None:
        print("Starting test_login_srs")
    
        try:
            
            contexts = self.driver.contexts
            for context in contexts:
                print("INIT Available context: " + context)
            # 웹뷰 컨텍스트로 전환
            self.driver.switch_to.context('WEBVIEW_com.cesco.oversea.srs.viet')
            # 명시적 대기: 비밀번호 필드가 표시될 때까지 기다립니다.
            wait = WebDriverWait(self.driver, 30)  # 최대 30초 대기
  
            # 언어선택 클릭  //button[contains(.,'select language')] 
            select_language = wait.until(
                EC.element_to_be_clickable((AppiumBy.XPATH, "//button[contains(.,'select language')]"))
                #EC.presence_of_element_located((AppiumBy.XPATH, "//button[contains(.,'select language')]"))
            )
            select_language.click() 

            # 현재 언어선택 값을 확인, 해당 언어값이면 유지, 아니면 언어변경(선택 클릭)
            # 언어 선택 후 현재 선택된 언어 값 확인
            selected_language_value = wait.until(
                EC.presence_of_element_located((AppiumBy.XPATH, "//input[@name='select' and @checked]"))
            )

            # 또는: class나 텍스트 기준으로 선택된 언어 항목을 추적하는 경우
            # selected_language_value = wait.until(
            #     EC.presence_of_element_located((AppiumBy.XPATH, "//div[contains(@class, 'selected')]"))
            # )

            language_value = selected_language_value.get_attribute("value")
            print(f"[선택된 언어] 현재 선택된 언어 value: {language_value}")

            for target_lang in language_list:

                # 언어선택 xpath=(//input[@name='select'])[2] , 1-한글 ko, 2-베트남 vi, 3-중국어 zh
                select_language_field = wait.until(
                    #EC.presence_of_element_located((AppiumBy.XPATH, "//input[@name='select'])[3]"))
                    #EC.element_to_be_clickable((AppiumBy.XPATH, "(//input[@name='select'])[3]"))
                    EC.element_to_be_clickable((AppiumBy.XPATH, f"//input[@name='select' and @value='{target_lang}']"))
                    #EC.element_to_be_clickable((AppiumBy.XPATH, f"//input[@name='select' and @value='vi']"))
                )
                select_language_field.click()
                # 같은 값으로 선택하는 경우 레이어가 유지됨
                print(f"[변경된 언어] 현재 선택된 언어 value:{target_lang}->{language_value}")
            #  
                if(target_lang!=language_value):
                    print(f"[변경된 언어] 같은 언어 선택!! 닫기 버튼 클릭:{target_lang}->{language_value}")
                    btn_pop_close = wait.until(
                        EC.element_to_be_clickable((AppiumBy.CSS_SELECTOR, ".slide_up .btn_pop_close"))
                        
                    )
                    btn_pop_close.click()
                print(f"[변경된 언어] 현재 선택된 언어 value:{target_lang}->{language_value}")
            #  
            user_id_field = wait.until(
                EC.presence_of_element_located((AppiumBy.CSS_SELECTOR, ".log_id input"))
                #EC.presence_of_element_located((AppiumBy.XPATH, "//input"))
            )
            #user_id_field.click() 
            
            user_id_field.send_keys("c89109")  # userID 값 설정
            
            
            user_pw_field = wait.until(
                EC.presence_of_element_located((AppiumBy.XPATH, "//input[@id='ion-input-0']"))
            )
            
            user_pw_field.send_keys("mcnc1234!!")  # userID 값 설정
            login_button = wait.until(
                #EC.element_to_be_clickable((AppiumBy.XPATH, "//button[contains(.,'로그인')]"))
                EC.element_to_be_clickable((AppiumBy.CSS_SELECTOR, ".btn01"))
                
            )
            login_button.click()  # 로그인 버튼 클릭
            print("로그페이지 완료")



        except Exception as e:
            print(f"Exception occurred: {e}")

        finally:
            # 다시 네이티브 앱 컨텍스트로 전환
            self.driver.switch_to.context('NATIVE_APP')  # 네이티브 컨텍스트로 전환
            print(f"Finally occurred:switch_to NATIVE_APP")

        try:
            contexts = self.driver.contexts
            for context in contexts:
                print("GO MAIN Available context: " + context)
            # 웹뷰 컨텍스트로 전환
            self.driver.switch_to.context('WEBVIEW_com.cesco.oversea.srs.viet')

            # 명시적 대기: 메인 UI가 표시 될 때 까지 
            wait = WebDriverWait(self.driver, 30)  # 최대 30초 대기
            self.get_current_url('STEP 2')
            
            for program in program_list:
                url = f"{base_url}{program}"
                self.driver.get(url)
                time.sleep(5)  # 페이지 로딩 대기
                # 캡처 파일 저장
                screenshot_path = os.path.join(screenshot_dir, f"{target_lang}{program}.png")
                self.driver.save_screenshot(screenshot_path)
                print(f"[캡처 완료] {program} → {screenshot_path}")
        except Exception as e:
            print(f"Exception occurred: {e}")

        finally:
            # 다시 네이티브 앱 컨텍스트로 전환
            self.driver.switch_to.context('NATIVE_APP')  # 네이티브 컨텍스트로 전환

if __name__ == '__main__':
    unittest.main()