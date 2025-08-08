"""
다국가/다언어 지원 통합 관리 모듈
CESCO SRS 모바일 앱 테스트의 언어별 설정과 데이터 관리
"""

import os
import csv
import json
from typing import Dict, List, Optional, Any
from dataclasses import dataclass
from enum import Enum

class SupportedCountry(Enum):
    """지원 국가 코드"""
    VIETNAM = "VN"
    CHINA = "CN" 
    KOREA = "KR"
    THAILAND = "TH"  # 새로 추가
    INDONESIA = "ID"  # 새로 추가

class SupportedLanguage(Enum):
    """지원 언어 코드"""
    VIETNAMESE = "vi"
    CHINESE = "zh"
    KOREAN = "ko"
    ENGLISH = "en"
    THAI = "th"      # 새로 추가
    INDONESIAN = "id" # 새로 추가

@dataclass
class CountryConfig:
    """국가별 설정 정보"""
    country_code: str
    country_name: str
    primary_language: str
    supported_languages: List[str]
    app_package: str
    webview_name: str
    currency: str
    date_format: str
    phone_format: str
    timezone: str

@dataclass
class LocalizedData:
    """언어별 로컬라이즈 데이터"""
    test_id: str
    data_type: str
    key: str
    language: str
    value: str
    description: str

class LocalizationManager:
    """다국가/다언어 지원 통합 관리자"""
    
    def __init__(self, config_path: str = None):
        self.config_path = config_path or os.path.join(os.path.dirname(__file__), 'localization_config.json')
        self.test_data_path = 'test_data.csv'
        
        # 국가별 설정 초기화
        self.country_configs: Dict[str, CountryConfig] = {}
        self.localized_data: Dict[str, Dict[str, Dict[str, LocalizedData]]] = {}
        
        self._initialize_default_configs()
        self._load_configurations()
        self._load_test_data()
    
    def _initialize_default_configs(self):
        """기본 국가 설정 초기화"""
        default_configs = {
            'VN': CountryConfig(
                country_code='VN',
                country_name='Vietnam',
                primary_language='vi',
                supported_languages=['vi', 'ko', 'en'],
                app_package='com.cesco.oversea.srs.viet',
                webview_name='WEBVIEW_com.cesco.oversea.srs.viet',
                currency='VND',
                date_format='DD/MM/YYYY',
                phone_format='+84-XXX-XXX-XXX',
                timezone='Asia/Ho_Chi_Minh'
            ),
            'CN': CountryConfig(
                country_code='CN',
                country_name='China',
                primary_language='zh',
                supported_languages=['zh', 'ko', 'en'],
                app_package='com.cesco.oversea.srs.cn',
                webview_name='WEBVIEW_com.cesco.oversea.srs.cn',
                currency='CNY',
                date_format='YYYY-MM-DD',
                phone_format='+86-XXX-XXXX-XXXX',
                timezone='Asia/Shanghai'
            ),
            'KR': CountryConfig(
                country_code='KR',
                country_name='Korea',
                primary_language='ko',
                supported_languages=['ko', 'en'],
                app_package='com.cesco.oversea.srs.dev',
                webview_name='WEBVIEW_com.cesco.oversea.srs.dev',
                currency='KRW',
                date_format='YYYY-MM-DD',
                phone_format='+82-XX-XXXX-XXXX',
                timezone='Asia/Seoul'
            ),
            'TH': CountryConfig(
                country_code='TH',
                country_name='Thailand',
                primary_language='th',
                supported_languages=['th', 'ko', 'en'],
                app_package='com.cesco.oversea.srs.thai',
                webview_name='WEBVIEW_com.cesco.oversea.srs.thai',
                currency='THB',
                date_format='DD/MM/YYYY',
                phone_format='+66-XX-XXX-XXXX',
                timezone='Asia/Bangkok'
            ),
            'ID': CountryConfig(
                country_code='ID',
                country_name='Indonesia',
                primary_language='id',
                supported_languages=['id', 'ko', 'en'],
                app_package='com.cesco.oversea.srs.indo',
                webview_name='WEBVIEW_com.cesco.oversea.srs.indo',
                currency='IDR',
                date_format='DD/MM/YYYY',
                phone_format='+62-XXX-XXX-XXXX',
                timezone='Asia/Jakarta'
            )
        }
        
        self.country_configs = default_configs
    
    def _load_configurations(self):
        """설정 파일에서 국가 구성 로드"""
        if os.path.exists(self.config_path):
            try:
                with open(self.config_path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    for country_code, config_data in data.items():
                        if country_code in self.country_configs:
                            # 기존 설정 업데이트
                            for key, value in config_data.items():
                                setattr(self.country_configs[country_code], key, value)
            except Exception as e:
                print(f"Warning: Failed to load localization config: {e}")
    
    def _load_test_data(self):
        """테스트 데이터 CSV에서 언어별 데이터 로드"""
        if not os.path.exists(self.test_data_path):
            print(f"Warning: {self.test_data_path} not found")
            return
        
        try:
            with open(self.test_data_path, 'r', encoding='utf-8') as f:
                reader = csv.DictReader(f)
                for row in reader:
                    if row['test_id'].startswith('#'):  # 주석 행 건너뛰기
                        continue
                    
                    test_id = row['test_id']
                    data_type = row['data_type']
                    key = row['key']
                    locale = row.get('locale', 'all')
                    
                    localized_data = LocalizedData(
                        test_id=test_id,
                        data_type=data_type,
                        key=key,
                        language=locale,
                        value=row['value'],
                        description=row.get('description', '')
                    )
                    
                    # 데이터 구조화
                    if test_id not in self.localized_data:
                        self.localized_data[test_id] = {}
                    if data_type not in self.localized_data[test_id]:
                        self.localized_data[test_id][data_type] = {}
                    
                    self.localized_data[test_id][data_type][f"{key}_{locale}"] = localized_data
                    
        except Exception as e:
            print(f"Error loading test data: {e}")
    
    def get_country_config(self, country_code: str) -> Optional[CountryConfig]:
        """국가별 설정 조회"""
        return self.country_configs.get(country_code)
    
    def get_supported_languages(self, country_code: str) -> List[str]:
        """국가별 지원 언어 목록 조회"""
        config = self.get_country_config(country_code)
        return config.supported_languages if config else []
    
    def get_primary_language(self, country_code: str) -> str:
        """국가별 기본 언어 조회"""
        config = self.get_country_config(country_code)
        return config.primary_language if config else 'en'
    
    def get_localized_value(self, test_id: str, data_type: str, key: str, 
                           language: str = 'ko', fallback: bool = True) -> Optional[str]:
        """언어별 로컬라이즈 값 조회"""
        # 1차: 특정 언어로 조회
        specific_key = f"{key}_{language}"
        if (test_id in self.localized_data and 
            data_type in self.localized_data[test_id] and
            specific_key in self.localized_data[test_id][data_type]):
            return self.localized_data[test_id][data_type][specific_key].value
        
        # 2차: 'all' 언어로 조회 (공통 데이터)
        all_key = f"{key}_all"
        if (test_id in self.localized_data and 
            data_type in self.localized_data[test_id] and
            all_key in self.localized_data[test_id][data_type]):
            return self.localized_data[test_id][data_type][all_key].value
        
        # 3차: 폴백 언어로 조회 (영어)
        if fallback and language != 'en':
            return self.get_localized_value(test_id, data_type, key, 'en', False)
        
        return None
    
    def get_error_message(self, error_type: str, language: str = 'ko') -> str:
        """언어별 에러 메시지 조회"""
        message = self.get_localized_value('ALL', 'error', error_type, language)
        return message if message else f"Error: {error_type}"
    
    def get_validation_message(self, validation_type: str, language: str = 'ko') -> str:
        """언어별 검증 메시지 조회"""
        message = self.get_localized_value('ALL', 'validation', validation_type, language)
        return message if message else f"Validation: {validation_type}"
    
    def get_app_config(self, country_code: str) -> Dict[str, str]:
        """국가별 앱 설정 정보 조회"""
        config = self.get_country_config(country_code)
        if not config:
            return {}
        
        return {
            'app_package': config.app_package,
            'webview_name': config.webview_name,
            'primary_language': config.primary_language,
            'supported_languages': config.supported_languages
        }
    
    def validate_language_support(self, country_code: str, language: str) -> bool:
        """국가에서 해당 언어를 지원하는지 확인"""
        supported_langs = self.get_supported_languages(country_code)
        return language in supported_langs
    
    def get_language_selector_index(self, country_code: str, language: str) -> int:
        """언어 선택기에서의 인덱스 조회 (1-based)"""
        supported_langs = self.get_supported_languages(country_code)
        if language in supported_langs:
            return supported_langs.index(language) + 1
        return 1  # 기본값
    
    def format_currency(self, amount: float, country_code: str) -> str:
        """국가별 통화 형식 적용"""
        config = self.get_country_config(country_code)
        if not config:
            return f"{amount}"
        
        currency_formats = {
            'VND': f"{amount:,.0f} ₫",
            'CNY': f"¥{amount:,.2f}",
            'KRW': f"₩{amount:,.0f}",
            'THB': f"฿{amount:,.2f}",
            'IDR': f"Rp {amount:,.0f}"
        }
        
        return currency_formats.get(config.currency, f"{amount:,.2f}")
    
    def format_phone_number(self, phone: str, country_code: str) -> str:
        """국가별 전화번호 형식 적용"""
        config = self.get_country_config(country_code)
        if not config:
            return phone
        
        # 간단한 전화번호 형식 적용 (실제 구현에서는 더 정교한 로직 필요)
        return phone  # 현재는 원본 반환
    
    def get_all_countries(self) -> List[str]:
        """지원하는 모든 국가 코드 반환"""
        return list(self.country_configs.keys())
    
    def get_all_languages(self) -> List[str]:
        """지원하는 모든 언어 코드 반환"""
        all_languages = set()
        for config in self.country_configs.values():
            all_languages.update(config.supported_languages)
        return list(all_languages)
    
    def save_configuration(self):
        """현재 설정을 파일로 저장"""
        config_data = {}
        for country_code, config in self.country_configs.items():
            config_data[country_code] = {
                'country_name': config.country_name,
                'primary_language': config.primary_language,
                'supported_languages': config.supported_languages,
                'app_package': config.app_package,
                'webview_name': config.webview_name,
                'currency': config.currency,
                'date_format': config.date_format,
                'phone_format': config.phone_format,
                'timezone': config.timezone
            }
        
        try:
            os.makedirs(os.path.dirname(self.config_path), exist_ok=True)
            with open(self.config_path, 'w', encoding='utf-8') as f:
                json.dump(config_data, f, indent=2, ensure_ascii=False)
            print(f"Configuration saved to {self.config_path}")
        except Exception as e:
            print(f"Failed to save configuration: {e}")
    
    def generate_test_report(self) -> Dict[str, Any]:
        """다국가 지원 현황 리포트 생성"""
        report = {
            'total_countries': len(self.country_configs),
            'total_languages': len(self.get_all_languages()),
            'countries': {},
            'language_coverage': {},
            'test_data_stats': {
                'total_test_cases': len(self.localized_data),
                'localized_items': 0,
                'missing_translations': []
            }
        }
        
        # 국가별 정보
        for country_code, config in self.country_configs.items():
            report['countries'][country_code] = {
                'name': config.country_name,
                'primary_language': config.primary_language,
                'supported_languages': config.supported_languages,
                'app_package': config.app_package
            }
        
        # 언어별 커버리지
        for language in self.get_all_languages():
            countries_supporting = [
                cc for cc, config in self.country_configs.items()
                if language in config.supported_languages
            ]
            report['language_coverage'][language] = countries_supporting
        
        # 테스트 데이터 통계
        localized_count = 0
        for test_id, test_data in self.localized_data.items():
            for data_type, type_data in test_data.items():
                localized_count += len(type_data)
        
        report['test_data_stats']['localized_items'] = localized_count
        
        return report

# 글로벌 인스턴스
localization_manager = LocalizationManager()

def get_localization_manager() -> LocalizationManager:
    """글로벌 LocalizationManager 인스턴스 반환"""
    return localization_manager

# 편의 함수들
def get_localized_text(test_id: str, data_type: str, key: str, language: str = 'ko') -> str:
    """간편한 로컬라이즈 텍스트 조회"""
    return localization_manager.get_localized_value(test_id, data_type, key, language) or key

def is_language_supported(country: str, language: str) -> bool:
    """언어 지원 여부 확인"""
    return localization_manager.validate_language_support(country, language)

def get_app_package(country: str) -> str:
    """국가별 앱 패키지명 조회"""
    config = localization_manager.get_country_config(country)
    return config.app_package if config else ""

if __name__ == "__main__":
    # 테스트 및 데모
    lm = LocalizationManager()
    
    print("=== CESCO SRS 다국가/다언어 지원 현황 ===")
    report = lm.generate_test_report()
    
    print(f"지원 국가: {report['total_countries']}개")
    print(f"지원 언어: {report['total_languages']}개")
    
    for country, info in report['countries'].items():
        print(f"\n📍 {country} ({info['name']})")
        print(f"  기본 언어: {info['primary_language']}")
        print(f"  지원 언어: {', '.join(info['supported_languages'])}")
        print(f"  앱 패키지: {info['app_package']}")
    
    print(f"\n📊 테스트 데이터: {report['test_data_stats']['total_test_cases']}개 케이스")
    print(f"로컬라이즈 항목: {report['test_data_stats']['localized_items']}개")