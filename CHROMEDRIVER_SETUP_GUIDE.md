# 🔧 Appium Chromedriver 자동 다운로드 설정 가이드

## 📋 **설정 방법 요약**

### **1. Appium 서버 시작 (올바른 방법)**

```bash
# ✅ 권장: 자동 다운로드 활성화
appium server --allow-insecure uiautomator2:chromedriver_autodownload --port 4723 --log-level info

# ❌ 잘못된 방법 (오류 발생)
appium --allow-insecure chromedriver_autodownload --port 4723

# 📝 올바른 형식: <driver_name>:<feature_name>
```

### **2. 클라이언트 코드 설정**

```python
capabilities = dict(
    platformName='Android',
    automationName='uiautomator2',
    udid='RFCM902ZM9K',
    appPackage='com.cesco.oversea.srs.viet',
    appActivity='com.mcnc.bizmob.cesco.SlideFragmentActivity',
    noReset=True,
    fullReset=False,
    
    # ✅ WEBVIEW 관련 설정 (최적화)
    chromedriverAutodownload=True,  # 자동 다운로드 활성화
    chromedriverChromeMappingFile=None,  # 자동 매핑 사용
    chromedriverUseSystemExecutable=False,  # 시스템 chromedriver 사용 안함
    skipLogCapture=True,  # 로그 캡처 건너뛰기
    autoWebview=False,  # 수동 웹뷰 전환
    recreateChromeDriverSessions=True,  # 세션 재생성
    ensureWebviewsHavePages=True,  # 웹뷰 페이지 확인
    
    chromeOptions={
        'w3c': False,
        'args': [
            '--disable-dev-shm-usage', 
            '--no-sandbox',
            '--disable-web-security',
            '--disable-features=VizDisplayCompositor',
            '--disable-extensions',
            '--disable-plugins',
            '--disable-background-timer-throttling',
            '--disable-renderer-backgrounding'
        ]
    }
)
```

## 🔍 **주요 설정 옵션 설명**

### **서버 설정**
- `--allow-insecure uiautomator2:chromedriver_autodownload`: uiautomator2 드라이버에 대해 chromedriver 자동 다운로드 허용
- `--port 4723`: Appium 서버 포트 (기본값)
- `--log-level info`: 로그 레벨 설정

### **클라이언트 설정**
- `chromedriverAutodownload=True`: Chrome 버전에 맞는 chromedriver 자동 다운로드
- `chromedriverUseSystemExecutable=False`: 시스템에 설치된 chromedriver 사용 안함
- `recreateChromeDriverSessions=True`: 각 세션마다 chromedriver 재생성
- `ensureWebviewsHavePages=True`: 웹뷰에 페이지가 로드될 때까지 대기

## 🚀 **빠른 시작**

### **1. 서버 시작**
```bash
# 간편 스크립트 사용
./start_appium_server.sh

# 또는 직접 명령어
appium server --allow-insecure uiautomator2:chromedriver_autodownload --port 4723 --log-level info
```

### **2. 테스트 실행**
```bash
# 가상환경 활성화
source venv/bin/activate

# 로그인 테스트 실행
python appium_login_test.py
```

## ⚠️ **문제 해결**

### **일반적인 오류들**

1. **`Fatal Error: The full feature name must include both the destination automation name`**
   - **원인**: 잘못된 insecure 설정 형식
   - **해결**: `uiautomator2:chromedriver_autodownload` 형식 사용

2. **`No Chromedriver found that can automate Chrome 'xxx'`**
   - **원인**: 호환되는 chromedriver 없음
   - **해결**: `chromedriverAutodownload=True` 확인

3. **`Connection refused: localhost:4723`**
   - **원인**: Appium 서버 미실행
   - **해결**: 서버 시작 후 테스트 실행

## 📁 **관련 파일들**
- `appium_login_test.py` - 로그인 테스트 (최적화된 설정 적용)
- `start_appium_server.sh` - 서버 시작 스크립트
- `fix_chromedriver.py` - 수동 chromedriver 설치 스크립트 (백업용)

---
**마지막 업데이트**: 2025-09-15  
**테스트 환경**: macOS, Android, Appium 3.0.2
