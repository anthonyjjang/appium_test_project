"""
향상된 언어 전환 모듈
다국가 CESCO SRS 앱의 스마트 언어 전환 및 상태 관리
"""

import time
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass
from enum import Enum

from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException
from appium.webdriver.common.appiumby import AppiumBy

from localization_manager import get_localization_manager

class LanguageSwitchStrategy(Enum):
    """언어 전환 전략"""
    XPATH_BASED = "xpath"           # XPath 기반 선택
    INDEX_BASED = "index"           # 인덱스 기반 선택
    TEXT_BASED = "text"             # 텍스트 매칭 기반 선택
    ATTRIBUTE_BASED = "attribute"   # 속성 기반 선택

@dataclass
class LanguageState:
    """현재 언어 상태 정보"""
    current_language: str
    target_language: str
    country_code: str
    switch_successful: bool
    switch_time: float
    error_message: Optional[str] = None

class EnhancedLanguageSwitcher:
    """향상된 언어 전환기"""
    
    def __init__(self, driver, country_code: str = 'KR', wait_timeout: int = 20):
        self.driver = driver
        self.wait = WebDriverWait(driver, wait_timeout)
        self.country_code = country_code
        self.localization_manager = get_localization_manager()
        
        # 언어 전환 셀렉터 설정 (국가별로 다를 수 있음)
        self.language_selectors = {
            'button': "//button[contains(.,'select language')]",
            'dropdown': "//select[@id='language-select']",
            'menu': "//div[@class='language-menu']",
            'options': "//div[@class='language-option']",
            'close_button': "//button[contains(@class,'close') or contains(text(),'닫기')]"
        }
        
        # 국가별 언어 선택 전략
        self.country_strategies = {
            'VN': LanguageSwitchStrategy.INDEX_BASED,
            'CN': LanguageSwitchStrategy.INDEX_BASED,
            'KR': LanguageSwitchStrategy.INDEX_BASED,
            'TH': LanguageSwitchStrategy.TEXT_BASED,
            'ID': LanguageSwitchStrategy.TEXT_BASED
        }
        
        # 언어별 표시명 매핑
        self.language_display_names = {
            'ko': {'ko': '한국어', 'en': 'Korean', 'zh': '韩语', 'vi': 'Tiếng Hàn', 'th': 'ภาษาเกาหลี', 'id': 'Bahasa Korea'},
            'en': {'ko': '영어', 'en': 'English', 'zh': '英语', 'vi': 'Tiếng Anh', 'th': 'ภาษาอังกฤษ', 'id': 'Bahasa Inggris'},
            'zh': {'ko': '중국어', 'en': 'Chinese', 'zh': '中文', 'vi': 'Tiếng Trung', 'th': 'ภาษาจีน', 'id': 'Bahasa Cina'},
            'vi': {'ko': '베트남어', 'en': 'Vietnamese', 'zh': '越南语', 'vi': 'Tiếng Việt', 'th': 'ภาษาเวียดนาม', 'id': 'Bahasa Vietnam'},
            'th': {'ko': '태국어', 'en': 'Thai', 'zh': '泰语', 'vi': 'Tiếng Thái', 'th': 'ภาษาไทย', 'id': 'Bahasa Thailand'},
            'id': {'ko': '인도네시아어', 'en': 'Indonesian', 'zh': '印尼语', 'vi': 'Tiếng Indonesia', 'th': 'ภาษาอินโดนีเซีย', 'id': 'Bahasa Indonesia'}
        }
    
    def get_current_language(self) -> Optional[str]:
        """현재 설정된 언어 감지"""
        try:
            # 언어 선택 버튼에서 현재 언어 추출
            lang_button = self.wait.until(
                EC.presence_of_element_located((AppiumBy.XPATH, self.language_selectors['button']))
            )
            
            # value 속성에서 언어 코드 추출
            current_value = lang_button.get_attribute('value')
            if current_value and len(current_value) == 2:
                return current_value.lower()
            
            # 텍스트에서 언어 추론
            button_text = lang_button.text
            for lang_code, display_names in self.language_display_names.items():
                if any(display_name in button_text for display_name in display_names.values()):
                    return lang_code
            
            # 기본값 반환
            return self.localization_manager.get_primary_language(self.country_code)
            
        except Exception as e:
            print(f"Failed to detect current language: {e}")
            return self.localization_manager.get_primary_language(self.country_code)
    
    def validate_language_support(self, target_language: str) -> bool:
        """대상 언어가 현재 국가에서 지원되는지 확인"""
        supported_languages = self.localization_manager.get_supported_languages(self.country_code)
        return target_language in supported_languages
    
    def switch_language(self, target_language: str, retry_count: int = 3, 
                       verify_switch: bool = True) -> LanguageState:
        """
        언어 전환 실행
        
        Args:
            target_language: 전환할 언어 코드 (예: 'ko', 'en', 'zh')
            retry_count: 재시도 횟수
            verify_switch: 전환 후 검증 여부
            
        Returns:
            LanguageState: 언어 전환 결과 상태
        """
        start_time = time.time()
        current_language = self.get_current_language()
        
        # 언어 지원 여부 확인
        if not self.validate_language_support(target_language):
            return LanguageState(
                current_language=current_language,
                target_language=target_language,
                country_code=self.country_code,
                switch_successful=False,
                switch_time=0,
                error_message=f"Language '{target_language}' not supported in {self.country_code}"
            )
        
        # 이미 같은 언어인 경우
        if current_language == target_language:
            return LanguageState(
                current_language=current_language,
                target_language=target_language,
                country_code=self.country_code,
                switch_successful=True,
                switch_time=time.time() - start_time,
                error_message=None
            )
        
        # 전환 시도
        for attempt in range(retry_count):
            try:
                print(f"Language switch attempt {attempt + 1}/{retry_count}: {current_language} -> {target_language}")\n                \n                # 전환 전략 선택\n                strategy = self.country_strategies.get(self.country_code, LanguageSwitchStrategy.INDEX_BASED)\n                \n                success = self._execute_language_switch(target_language, strategy)\n                \n                if success:\n                    # 전환 후 검증\n                    if verify_switch:\n                        time.sleep(2)  # 언어 전환 반영 대기\n                        actual_language = self.get_current_language()\n                        \n                        if actual_language == target_language:\n                            return LanguageState(\n                                current_language=actual_language,\n                                target_language=target_language,\n                                country_code=self.country_code,\n                                switch_successful=True,\n                                switch_time=time.time() - start_time\n                            )\n                        else:\n                            print(f"Verification failed: expected {target_language}, got {actual_language}")\n                    else:\n                        return LanguageState(\n                            current_language=target_language,  # 검증하지 않으므로 대상 언어로 가정\n                            target_language=target_language,\n                            country_code=self.country_code,\n                            switch_successful=True,\n                            switch_time=time.time() - start_time\n                        )\n                        \n            except Exception as e:\n                print(f"Language switch attempt {attempt + 1} failed: {e}")\n                if attempt < retry_count - 1:\n                    time.sleep(1)  # 재시도 전 대기\n        \n        # 모든 시도 실패\n        return LanguageState(\n            current_language=current_language,\n            target_language=target_language,\n            country_code=self.country_code,\n            switch_successful=False,\n            switch_time=time.time() - start_time,\n            error_message=f"Failed to switch language after {retry_count} attempts"\n        )\n    \n    def _execute_language_switch(self, target_language: str, strategy: LanguageSwitchStrategy) -> bool:\n        """실제 언어 전환 실행"""\n        try:\n            # 1. 언어 선택 버튼 클릭\n            lang_button = self.wait.until(\n                EC.element_to_be_clickable((AppiumBy.XPATH, self.language_selectors['button']))\n            )\n            lang_button.click()\n            time.sleep(1)\n            \n            # 2. 전략별 언어 선택\n            if strategy == LanguageSwitchStrategy.INDEX_BASED:\n                return self._select_by_index(target_language)\n            elif strategy == LanguageSwitchStrategy.TEXT_BASED:\n                return self._select_by_text(target_language)\n            elif strategy == LanguageSwitchStrategy.ATTRIBUTE_BASED:\n                return self._select_by_attribute(target_language)\n            else:\n                return self._select_by_xpath(target_language)\n                \n        except Exception as e:\n            print(f"Language switch execution failed: {e}")\n            return False\n    \n    def _select_by_index(self, target_language: str) -> bool:\n        """인덱스 기반 언어 선택"""\n        try:\n            supported_languages = self.localization_manager.get_supported_languages(self.country_code)\n            if target_language not in supported_languages:\n                return False\n            \n            # 언어 인덱스 계산 (1-based)\n            language_index = supported_languages.index(target_language) + 1\n            \n            # XPath로 인덱스 기반 선택\n            language_option_xpath = f"//select/option[{language_index}] | //div[@class='language-option'][{language_index}]"\n            \n            language_option = self.wait.until(\n                EC.element_to_be_clickable((AppiumBy.XPATH, language_option_xpath))\n            )\n            language_option.click()\n            \n            # 선택 완료 대기\n            time.sleep(1)\n            \n            # 메뉴 닫기 (필요한 경우)\n            self._close_language_menu()\n            \n            return True\n            \n        except Exception as e:\n            print(f"Index-based selection failed: {e}")\n            return False\n    \n    def _select_by_text(self, target_language: str) -> bool:\n        """텍스트 매칭 기반 언어 선택"""\n        try:\n            # 현재 앱 언어에서 대상 언어의 표시명 가져오기\n            current_lang = self.get_current_language()\n            display_name = self.language_display_names.get(target_language, {}).get(current_lang, target_language)\n            \n            # 텍스트로 언어 옵션 찾기\n            language_option_xpath = f"//option[contains(text(),'{display_name}')] | //div[contains(text(),'{display_name}')]"\n            \n            language_option = self.wait.until(\n                EC.element_to_be_clickable((AppiumBy.XPATH, language_option_xpath))\n            )\n            language_option.click()\n            \n            time.sleep(1)\n            self._close_language_menu()\n            \n            return True\n            \n        except Exception as e:\n            print(f"Text-based selection failed: {e}")\n            return False\n    \n    def _select_by_attribute(self, target_language: str) -> bool:\n        """속성 기반 언어 선택"""\n        try:\n            # value 속성으로 언어 옵션 찾기\n            language_option_xpath = f"//option[@value='{target_language}'] | //div[@data-lang='{target_language}']"\n            \n            language_option = self.wait.until(\n                EC.element_to_be_clickable((AppiumBy.XPATH, language_option_xpath))\n            )\n            language_option.click()\n            \n            time.sleep(1)\n            self._close_language_menu()\n            \n            return True\n            \n        except Exception as e:\n            print(f"Attribute-based selection failed: {e}")\n            return False\n    \n    def _select_by_xpath(self, target_language: str) -> bool:\n        """XPath 기반 언어 선택 (기본 방식)"""\n        try:\n            # 언어별 XPath 패턴\n            language_xpaths = {\n                'ko': "//option[contains(text(),'한국어') or contains(text(),'Korean') or @value='ko']",\n                'en': "//option[contains(text(),'English') or contains(text(),'영어') or @value='en']",\n                'zh': "//option[contains(text(),'中文') or contains(text(),'Chinese') or @value='zh']",\n                'vi': "//option[contains(text(),'Tiếng Việt') or contains(text(),'Vietnamese') or @value='vi']",\n                'th': "//option[contains(text(),'ภาษาไทย') or contains(text(),'Thai') or @value='th']",\n                'id': "//option[contains(text(),'Bahasa Indonesia') or contains(text(),'Indonesian') or @value='id']"\n            }\n            \n            xpath = language_xpaths.get(target_language)\n            if not xpath:\n                return False\n            \n            language_option = self.wait.until(\n                EC.element_to_be_clickable((AppiumBy.XPATH, xpath))\n            )\n            language_option.click()\n            \n            time.sleep(1)\n            self._close_language_menu()\n            \n            return True\n            \n        except Exception as e:\n            print(f"XPath-based selection failed: {e}")\n            return False\n    \n    def _close_language_menu(self):\n        """언어 선택 메뉴 닫기"""\n        try:\n            # 닫기 버튼이나 배경 클릭으로 메뉴 닫기\n            close_selectors = [\n                self.language_selectors['close_button'],\n                "//button[contains(@class,'modal-close')]",\n                "//div[@class='modal-backdrop']"\n            ]\n            \n            for selector in close_selectors:\n                try:\n                    close_element = self.driver.find_element(AppiumBy.XPATH, selector)\n                    if close_element.is_displayed():\n                        close_element.click()\n                        break\n                except:\n                    continue\n                    \n        except Exception as e:\n            print(f"Failed to close language menu: {e}")\n    \n    def get_language_switch_report(self, language_states: List[LanguageState]) -> Dict:\n        """언어 전환 리포트 생성"""\n        if not language_states:\n            return {}\n        \n        successful_switches = [state for state in language_states if state.switch_successful]\n        failed_switches = [state for state in language_states if not state.switch_successful]\n        \n        avg_switch_time = sum(state.switch_time for state in successful_switches) / len(successful_switches) if successful_switches else 0\n        \n        return {\n            'total_attempts': len(language_states),\n            'successful_switches': len(successful_switches),\n            'failed_switches': len(failed_switches),\n            'success_rate': len(successful_switches) / len(language_states) * 100,\n            'average_switch_time': round(avg_switch_time, 2),\n            'country_code': self.country_code,\n            'failed_languages': [state.target_language for state in failed_switches],\n            'error_messages': [state.error_message for state in failed_switches if state.error_message]\n        }\n    \n    def test_all_supported_languages(self) -> List[LanguageState]:\n        """지원하는 모든 언어로 전환 테스트"""\n        supported_languages = self.localization_manager.get_supported_languages(self.country_code)\n        results = []\n        \n        print(f"Testing language switching for {self.country_code}: {supported_languages}")\n        \n        for language in supported_languages:\n            print(f"\\nTesting switch to: {language}")\n            state = self.switch_language(language)\n            results.append(state)\n            \n            if state.switch_successful:\n                print(f"✅ Successfully switched to {language} in {state.switch_time:.2f}s")\n            else:\n                print(f"❌ Failed to switch to {language}: {state.error_message}")\n                \n            time.sleep(1)  # 테스트 간 대기\n        \n        # 리포트 출력\n        report = self.get_language_switch_report(results)\n        print(f"\\n📊 Language Switch Test Report for {self.country_code}:")\n        print(f"Success Rate: {report['success_rate']:.1f}% ({report['successful_switches']}/{report['total_attempts']})")\n        print(f"Average Switch Time: {report['average_switch_time']}s")\n        \n        if report['failed_languages']:\n            print(f"Failed Languages: {', '.join(report['failed_languages'])}")\n        \n        return results\n\n# 편의 함수\ndef create_language_switcher(driver, country_code: str = 'KR') -> EnhancedLanguageSwitcher:\n    \"\"\"언어 전환기 생성\"\"\"\n    return EnhancedLanguageSwitcher(driver, country_code)\n\ndef quick_language_switch(driver, target_language: str, country_code: str = 'KR') -> bool:\n    \"\"\"빠른 언어 전환\"\"\"\n    switcher = EnhancedLanguageSwitcher(driver, country_code)\n    state = switcher.switch_language(target_language)\n    return state.switch_successful\n\nif __name__ == "__main__":\n    # 테스트 코드 (실제 드라이버 필요)\n    print("Enhanced Language Switcher - Test Mode")\n    print("Supported countries:", ['VN', 'CN', 'KR', 'TH', 'ID'])\n    \n    lm = get_localization_manager()\n    for country in ['VN', 'CN', 'KR', 'TH', 'ID']:\n        languages = lm.get_supported_languages(country)\n        primary = lm.get_primary_language(country)\n        print(f"{country}: {languages} (primary: {primary})")