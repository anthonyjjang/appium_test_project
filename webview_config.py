# webview_config.py
# WEBVIEW 요소 로깅 테스트 설정 파일

# 디바이스 및 앱 설정
DEVICE_CONFIG = {
    'udid': 'RFCM902ZM9K',
    'platform_name': 'Android',
    'automation_name': 'uiautomator2'
}

APP_CONFIG = {
    'app_package': 'com.cesco.oversea.srs.viet',
    'app_activity': 'com.mcnc.bizmob.cesco.SlideFragmentActivity',
    'webview_context': 'WEBVIEW_com.cesco.oversea.srs.viet'
}

# 로그인 테스트 설정
LOGIN_CONFIG = {
    'username': 'c89109',
    'password': 'mcnc1234!!',
    'login_url': 'http://localhost/LOG1000',
    'success_indicators': [
        '.main_content',
        '.dashboard',
        '.home',
        'url_change'
    ]
}

# Appium 서버 설정
APPIUM_CONFIG = {
    'server_url': 'http://localhost:4723',
    'implicit_wait': 10,
    'explicit_wait': 30
}

# 로깅 설정
LOGGING_CONFIG = {
    'log_level': 'INFO',
    'save_screenshots': True,
    'save_element_data': True,
    'max_elements_per_type': 10,
    'max_clickable_elements_to_test': 2
}

# 스캔할 요소 타입 설정
ELEMENT_TYPES_TO_SCAN = {
    'inputs': {
        'selectors': [
            "input[type='text']",
            "input[type='email']", 
            "input[type='password']",
            "input[type='number']",
            "input[type='tel']",
            "input[type='search']",
            "input[type='url']",
            "input:not([type])",
            "input"
        ],
        'priority': 1
    },
    'buttons': {
        'selectors': [
            "button",
            "input[type='button']",
            "input[type='submit']",
            "[role='button']",
            ".btn",
            ".button"
        ],
        'priority': 1
    },
    'links': {
        'selectors': [
            "a[href]",
            "[role='link']"
        ],
        'priority': 2
    },
    'forms': {
        'selectors': [
            "form"
        ],
        'priority': 2
    },
    'selects': {
        'selectors': [
            "select",
            "[role='combobox']",
            "[role='listbox']"
        ],
        'priority': 2
    },
    'textareas': {
        'selectors': [
            "textarea"
        ],
        'priority': 2
    },
    'images': {
        'selectors': [
            "img",
            "[role='img']"
        ],
        'priority': 3
    }
}

# 추출할 요소 속성 목록
ELEMENT_ATTRIBUTES_TO_EXTRACT = [
    'id', 'class', 'name', 'type', 'value', 'placeholder',
    'href', 'src', 'alt', 'title', 'role', 'aria-label',
    'data-test', 'data-id', 'data-name'
]

# 페이지 탐색 설정
EXPLORATION_CONFIG = {
    'wait_between_scans': 5,  # 페이지 스캔 간 대기 시간 (초)
    'wait_after_click': 3,    # 클릭 후 대기 시간 (초)
    'max_pages_to_explore': 3, # 탐색할 최대 페이지 수
    'click_timeout': 10       # 클릭 요소 대기 시간 (초)
}
