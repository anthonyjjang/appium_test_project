# 🔧 WEBVIEW 컨텍스트 전환 문제 해결 가이드

## 📋 문제 상황
- **오류**: `No Chromedriver found that can automate Chrome '139.0.7258'`
- **원인**: 디바이스의 Chrome 버전과 호환되는 Chromedriver 부재
- **결과**: WEBVIEW 컨텍스트 전환 실패 → 웹 요소 탐지 불가

## 🛠️ 해결 방법

### ⚡ 빠른 해결 (권장)

1. **Chromedriver 자동 설치 스크립트 실행**
   ```bash
   cd /Users/loveauden/개발환경/appiumTestProject
   source venv/bin/activate
   python fix_chromedriver.py
   ```

2. **Appium 서버 재시작**
   ```bash
   # 기존 Appium 프로세스 종료
   pkill -f appium
   
   # 새 Appium 서버 시작
   appium server --port 4723 --log-level info &
   ```

3. **앱 재시작 및 테스트**
   ```bash
   # 앱 완전 종료
   adb shell am force-stop com.cesco.oversea.srs.viet
   
   # 테스트 재실행
   python appium_webview_element_logger.py
   ```

### 🔧 수동 해결

1. **Chrome 버전 확인**
   ```bash
   adb shell dumpsys package com.android.chrome | grep versionName
   ```

2. **호환 Chromedriver 다운로드**
   - 사이트: https://chromedriver.chromium.org/downloads
   - 버전: Chrome 139와 호환되는 버전 선택
   - 플랫폼: macOS (arm64 또는 x64)

3. **Chromedriver 설치**
   ```bash
   # 다운로드한 파일 압축 해제
   unzip chromedriver_mac64.zip
   
   # 실행 권한 부여
   chmod +x chromedriver
   
   # 시스템 경로로 이동
   sudo mv chromedriver /usr/local/bin/
   
   # 설치 확인
   chromedriver --version
   ```

### 🎯 Appium 설정 최적화

`appium_webview_element_logger.py`의 capabilities 확인:
```python
capabilities = dict(
    # ... 기존 설정 ...
    chromedriverAutodownload=True,  # ✅ 활성화됨
    chromedriverChromeMappingFile=None,  # ✅ 자동 매핑
    recreateChromeDriverSessions=True,  # ✅ 세션 재생성
    # ...
)
```

## 🔍 문제 진단

### 현재 상태 확인
```bash
# Appium 서버 상태
ps aux | grep appium

# 디바이스 연결 상태
adb devices

# Chrome 버전
adb shell dumpsys package com.android.chrome | grep version

# Chromedriver 버전
chromedriver --version
```

### 로그 분석
- **성공 로그**: `✅ 웹뷰 컨텍스트 전환 성공`
- **실패 로그**: `❌ 웹뷰 컨텍스트 전환 중 오류: No Chromedriver found`

## 🎯 대안 방법

### 1. Chrome 버전 다운그레이드
```bash
# 디바이스에서 Chrome 업데이트 비활성화
adb shell pm disable-user com.android.vending
```

### 2. 다른 브라우저 사용
- Samsung Internet
- Firefox
- Edge

### 3. 네이티브 요소 활용
현재 프로그램은 WEBVIEW 전환 실패 시 자동으로 네이티브 컨텍스트로 폴백하여 계속 진행합니다.

## 📞 추가 지원

문제가 계속 발생할 경우:
1. `logs/webview_test_*/detailed_test.log` 확인
2. Appium 서버 로그 확인
3. 디바이스별 특수 설정 필요 여부 검토

---
**마지막 업데이트**: 2025-09-15
**테스트 환경**: macOS, Android, Appium 3.0.2
