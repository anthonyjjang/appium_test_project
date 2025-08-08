# Appium 테스트 프레임워크 설치 가이드

## 🖥️ PC 환경 설정 (Windows/Mac/Linux)

### 1. Java 환경 설치

#### Windows
```bash
# Java 8 이상 설치 (OpenJDK 또는 Oracle JDK)
# https://adoptium.net/ 에서 다운로드

# 환경변수 설정
JAVA_HOME=C:\Program Files\Eclipse Adoptium\jdk-11.0.x
PATH=%JAVA_HOME%\bin;%PATH%

# 확인
java -version
```

#### Mac
```bash
# Homebrew로 설치
brew install openjdk@11

# 환경변수 설정 (~/.zshrc 또는 ~/.bash_profile)
export JAVA_HOME=/opt/homebrew/opt/openjdk@11/libexec/openjdk.jdk/Contents/Home
export PATH=$JAVA_HOME/bin:$PATH

# 확인
java -version
```

#### Linux (Ubuntu/Debian)
```bash
# OpenJDK 설치
sudo apt update
sudo apt install openjdk-11-jdk

# 환경변수 설정 (~/.bashrc)
export JAVA_HOME=/usr/lib/jvm/java-11-openjdk-amd64
export PATH=$JAVA_HOME/bin:$PATH

# 확인
java -version
```

### 2. Node.js 및 npm 설치

#### Windows
```bash
# https://nodejs.org 에서 LTS 버전 다운로드
# 또는 Chocolatey 사용
choco install nodejs

# 확인
node --version
npm --version
```

#### Mac
```bash
# Homebrew로 설치
brew install node

# 확인
node --version
npm --version
```

#### Linux
```bash
# NodeSource 저장소 사용
curl -fsSL https://deb.nodesource.com/setup_lts.x | sudo -E bash -
sudo apt-get install -y nodejs

# 확인
node --version
npm --version
```

### 3. Android SDK 설치

#### Android Studio 설치
```bash
# https://developer.android.com/studio 에서 다운로드
# 설치 후 SDK Manager에서 다음 컴포넌트 설치:
# - Android SDK Platform-Tools
# - Android SDK Build-Tools (최신 버전)
# - Android API Level 28 이상
```

#### 환경변수 설정

**Windows**
```bash
ANDROID_HOME=C:\Users\{username}\AppData\Local\Android\Sdk
PATH=%ANDROID_HOME%\platform-tools;%ANDROID_HOME%\tools;%PATH%
```

**Mac/Linux**
```bash
# ~/.zshrc 또는 ~/.bashrc에 추가
export ANDROID_HOME=$HOME/Library/Android/sdk  # Mac
# export ANDROID_HOME=$HOME/Android/Sdk        # Linux
export PATH=$ANDROID_HOME/platform-tools:$PATH
export PATH=$ANDROID_HOME/tools:$PATH
```

#### SDK 설치 확인
```bash
adb --version
# Android Debug Bridge version 1.0.41
```

### 4. Appium 설치

#### Appium 서버 설치
```bash
# 전역 설치
npm install -g appium

# Appium 2.0 사용 시 (권장)
npm install -g appium@next

# 드라이버 설치
appium driver install uiautomator2

# 확인
appium --version
appium driver list
```

#### Appium Inspector 설치 (선택사항)
```bash
# GUI 테스트 도구
# https://github.com/appium/appium-inspector/releases
# 플랫폼별 설치 파일 다운로드
```

### 5. Python 환경 설정

#### Python 설치
```bash
# Windows: https://python.org 에서 3.8+ 다운로드
# Mac: brew install python3
# Linux: sudo apt install python3 python3-pip

# 확인
python --version  # 또는 python3 --version
pip --version     # 또는 pip3 --version
```

#### 가상환경 생성 (권장)
```bash
# 프로젝트 디렉터리에서
python -m venv appium_test_env

# 활성화
# Windows
appium_test_env\Scripts\activate
# Mac/Linux  
source appium_test_env/bin/activate

# 비활성화
deactivate
```

#### Python 패키지 설치
```bash
# 프로젝트 디렉터리에서
pip install -r requirements.txt

# 또는 개별 설치
pip install Appium-Python-Client>=3.1.0
pip install selenium>=4.15.0
pip install pandas>=2.1.0
pip install python-dotenv>=1.0.0
pip install openpyxl>=3.1.0
```

## 📱 스마트폰 설정 (Android)

### 1. 개발자 옵션 활성화
```
1. 설정 > 휴대전화 정보 (또는 디바이스 정보)
2. 빌드번호를 7번 연속 탭
3. "개발자가 되었습니다" 메시지 확인
```

### 2. USB 디버깅 활성화
```
1. 설정 > 개발자 옵션
2. USB 디버깅 활성화
3. USB로 설치 활성화 (선택사항)
4. USB 검증 앱 비활성화 (선택사항)
```

### 3. 테스트 앱 설치
```bash
# APK 파일이 있는 경우
adb install your_app.apk

# 또는 Play Store에서 설치 후 패키지명 확인
adb shell pm list packages | grep cesco
# com.cesco.oversea.srs.viet
# com.cesco.oversea.srs.cn
# com.cesco.oversea.srs.dev
```

### 4. 디바이스 연결 확인
```bash
# USB 케이블로 PC와 연결 후
adb devices
# List of devices attached
# RFCX715QHAL	device

# 디바이스 정보 확인
adb shell getprop ro.product.model
adb shell getprop ro.build.version.release
```

## 🔧 환경 설정 파일

### 1. .env 파일 설정
```bash
# 프로젝트 디렉터리에서
cp .env.template .env

# .env 파일 편집하여 본인 환경에 맞게 수정
# - USER_ID, USER_PW: 테스트 계정
# - DEFAULT_UDID: 연결된 디바이스 UDID
# - APP_PACKAGE: 테스트할 앱 패키지명
```

### 2. CSV 설정 파일 준비

#### devices.csv
```csv
device_id,udid,platform_name,platform_version
DEVICE_RFCX715Q,RFCX715QHAL,Android,14
```

#### users.csv  
```csv
user_id,user_pw,country_code,app_package,webview_name,description
testuser01,testpass123,CN,com.cesco.oversea.srs.cn,WEBVIEW_com.cesco.oversea.srs.cn,중국 테스트 계정
```

## 🚀 설치 검증

### 자동 환경 검증 스크립트
```bash
# 환경 검증 스크립트 실행
python verify_environment.py
```

### 수동 검증 단계

#### 1. Java 환경
```bash
java -version
# openjdk version "11.0.x" 이상 출력 확인
```

#### 2. Android SDK
```bash
adb version
# Android Debug Bridge version 1.0.x 출력 확인

adb devices
# 연결된 디바이스 목록 출력 확인
```

#### 3. Appium 서버
```bash
appium --version
# 2.x.x 또는 1.22.x 이상 출력 확인

appium driver list
# uiautomator2 드라이버 설치 확인
```

#### 4. Python 패키지
```bash
pip list | grep -i appium
# Appium-Python-Client 3.1.x 이상 확인

python -c "from appium import webdriver; print('Appium client OK')"
# "Appium client OK" 출력 확인
```

#### 5. 테스트 실행
```bash
# Appium 서버 시작 (별도 터미널)
appium

# 테스트 실행 (다른 터미널)
python appium_test_runner.py
```

## 📝 환경 검증 체크리스트

### PC 환경
- [ ] Java 11+ 설치 및 JAVA_HOME 설정
- [ ] Node.js 및 npm 설치
- [ ] Android SDK 설치 및 ANDROID_HOME 설정
- [ ] adb 명령어 실행 가능
- [ ] Appium 서버 설치 및 uiautomator2 드라이버 설치
- [ ] Python 3.8+ 및 필수 패키지 설치

### 모바일 디바이스
- [ ] 개발자 옵션 활성화
- [ ] USB 디버깅 활성화  
- [ ] 테스트 앱 설치
- [ ] adb devices에서 디바이스 인식 확인

### 프로젝트 설정
- [ ] .env 파일 설정 완료
- [ ] CSV 설정 파일 준비
- [ ] 테스트 데이터 파일 존재 확인
- [ ] 스크린샷 디렉터리 생성 권한 확인

## 🔧 문제 해결

### 일반적인 이슈

#### 1. adb 디바이스 인식 안됨
```bash
# USB 드라이버 재설치
# 다른 USB 포트 사용
# USB 케이블 교체

# adb 서버 재시작
adb kill-server
adb start-server
adb devices
```

#### 2. Appium 연결 실패
```bash
# Appium 서버 로그 확인
appium --log-level debug

# 포트 충돌 확인
netstat -ano | findstr :4723  # Windows
lsof -i :4723                 # Mac/Linux

# 다른 포트 사용
appium -p 4724
```

#### 3. WebView 컨텍스트 전환 실패
```bash
# Chrome 개발자 도구에서 WebView 디버깅 활성화
# chrome://inspect/#devices

# 앱에서 WebView 디버깅 허용 설정 확인
```

#### 4. 권한 오류
```bash
# Android 앱 권한 수동 허용
adb shell pm grant com.your.app android.permission.CAMERA
adb shell pm grant com.your.app android.permission.WRITE_EXTERNAL_STORAGE
```

## 📞 지원 및 문의

### 유용한 링크
- [Appium 공식 문서](https://appium.io/docs/en/2.1/)
- [Android SDK 다운로드](https://developer.android.com/studio)
- [Python Appium Client](https://pypi.org/project/Appium-Python-Client/)

### 로그 및 디버깅
```bash
# 상세 로그 활성화
appium --log-level debug --log ./appium.log

# adb 로그 모니터링
adb logcat | grep -i appium

# Python 로그 레벨 설정
import logging
logging.basicConfig(level=logging.DEBUG)
```