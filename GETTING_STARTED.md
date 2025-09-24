# 🚀 빠른 시작 가이드 (Getting Started)

> **5분만에 Appium 테스트 환경 구축하기!**

## 📋 사전 준비사항

### ✅ 체크리스트
- [ ] Android 디바이스 (Android 8.0+)
- [ ] USB 케이블  
- [ ] PC (Windows 10+, macOS 10.15+, Ubuntu 18.04+)
- [ ] 인터넷 연결
- [ ] 관리자 권한 (Windows의 경우)

### 📱 모바일 디바이스 설정

1. **개발자 옵션 활성화**
   ```
   설정 > 휴대전화 정보 > 빌드번호를 7번 연속 탭
   "개발자가 되었습니다" 메시지 확인
   ```

2. **USB 디버깅 활성화**
   ```
   설정 > 개발자 옵션 > USB 디버깅 ON
   설정 > 개발자 옵션 > USB로 설치 ON (선택)
   ```

3. **디바이스 연결 확인**
   ```bash
   # PC와 USB 연결 후
   # 처음 연결 시 "USB 디버깅을 허용하시겠습니까?" 팝업에서 "허용" 선택
   ```

## ⚡ 1분 설치 (자동)

### Mac/Linux 사용자
```bash
# 1. 프로젝트 다운로드
git clone <repository-url>
cd appiumTestProject

# 2. 자동 설치 실행
chmod +x quick_setup.sh
./quick_setup.sh

# 3. 환경 검증
python verify_environment.py
```

### Windows 사용자
```bash
# 1. 관리자 권한으로 Command Prompt 또는 PowerShell 실행

# 2. 프로젝트 디렉터리로 이동
cd appiumTestProject

# 3. 자동 설치 실행
quick_setup.bat

# 4. 환경 검증
python verify_environment.py
```

## 🎯 첫 번째 테스트 실행

### 1️⃣ 설정 파일 준비
```bash
# 설정 템플릿 복사
cp .env.template .env

# .env 파일 편집 (필수 설정만)
# - USER_ID: 테스트 계정 ID
# - USER_PW: 테스트 계정 비밀번호  
# - DEFAULT_UDID: 연결된 디바이스 UDID
```

### 2️⃣ 디바이스 UDID 확인
```bash
# 연결된 디바이스 목록 확인
adb devices

# 예시 출력:
# List of devices attached
# RFCX715QHAL    device  ← 이것이 UDID

# .env 파일의 DEFAULT_UDID를 위 값으로 설정
```

### 3️⃣ 테스트 앱 설치 (필요한 경우)
```bash
# APK 파일이 있는 경우
adb install your_app.apk

# 또는 Play Store에서 CESCO SRS 앱 설치
```

### 4️⃣ Appium 서버 시작
```bash
# 터미널 1 (Appium 서버용)
appium

# 성공 메시지 확인:
# [Appium] Welcome to Appium v2.x.x
# [Appium] Appium REST http interface listener started on 0.0.0.0:4723
```

### 5️⃣ 테스트 실행
```bash
# 터미널 2 (테스트 실행용)
# 기본 테스트 (빠른 확인용)
python appium_test_runner.py

# 또는 향상된 테스트 (상세 검증)
python enhanced_test_runner.py
```

## 🎉 성공 확인

### 예상되는 출력 결과
```
🚀 Starting Enhanced Test Scenarios
📊 Target languages: ['zh', 'ko', 'en']
📱 Target device: RFCX715QHAL
📦 Target app: com.cesco.oversea.srs.cn

📋 Loaded 6 test cases:
  - TC001: 로그인 테스트 (9 steps)
  - TC002: 고객 검색 테스트 (9 steps)
  ...

🌐 Testing language 1/3: ZH
✅ Language changed to: zh
✅ Login successful

📝 Test 1/6 in ZH
🚀 Starting test case: TC001 - 로그인 테스트
  ✅ Step 1/9: 로그인 페이지 로딩 대기 (2341ms)
  ✅ Step 2/9: 아이디 입력 (892ms)
  ...

🎯 Test case completed: 9/9 steps passed (100.0%)
⏱️  Total execution time: 15432ms

🎉 Test Execution Complete!
📊 Final Results:
   - Total Tests: 18/18
   - Passed Tests: 18
   - Success Rate: 100.0%
```

### 결과 파일 확인
```bash
# 스크린샷 확인
ls screenshots/test_*/

# 테스트 결과 로그 확인
ls test_results_enhanced_*.csv
```

## 🔧 문제 발생 시 빠른 해결

### ❌ "adb devices"에서 디바이스가 안 보임
```bash
# 1. USB 케이블 확인 (데이터 전송 가능한 케이블 사용)
# 2. 다른 USB 포트 시도
# 3. USB 드라이버 재설치
# 4. adb 재시작
adb kill-server
adb start-server
adb devices

# 5. "unauthorized" 상태인 경우
# 디바이스에서 "USB 디버깅을 허용하시겠습니까?" 팝업에서 "허용" 선택
```

### ❌ Appium 연결 오류
```bash
# 1. 포트 충돌 확인
netstat -ano | findstr :4723  # Windows
lsof -i :4723                 # Mac/Linux

# 2. 다른 포트로 Appium 시작
appium -p 4724

# 3. .env 파일에서 포트 변경
APPIUM_PORT=4724
```

### ❌ 앱이 설치되지 않음
```bash
# 1. Unknown sources 허용 확인
# 설정 > 보안 > 알 수 없는 출처 허용

# 2. APK 파일 경로 확인
adb install -r your_app.apk  # -r 옵션으로 재설치

# 3. 패키지 이름 확인
adb shell pm list packages | grep cesco
```

### ❌ 테스트가 멈춤
```bash
# 1. 디바이스 화면 켜기 및 잠금 해제
# 2. 앱이 백그라운드에서 종료되지 않았는지 확인
# 3. 디바이스 재부팅 후 재시도
# 4. Appium 서버 재시작
```

### ❌ ANDROID_HOME 환경변수 오류
```bash
# Mac/Linux에서 환경변수 설정
export ANDROID_HOME=$HOME/Library/Android/sdk
export PATH=$ANDROID_HOME/platform-tools:$PATH

# 영구적으로 설정
echo 'export ANDROID_HOME=$HOME/Library/Android/sdk' >> ~/.zshrc
echo 'export PATH=$ANDROID_HOME/platform-tools:$PATH' >> ~/.zshrc
source ~/.zshrc
```

### ❌ python-dotenv 패키지 누락
```bash
# 패키지 설치 (환경변수 관리용)
pip install python-dotenv>=1.0.0

# 또는 전체 패키지 설치
pip install -r requirements.txt

# 설치 확인
pip list | grep python-dotenv
# python-dotenv 1.0.x 출력 확인

# 가상환경에서 설치되지 않은 경우
source appium_test_env/bin/activate  # Mac/Linux
# appium_test_env\Scripts\activate  # Windows
pip install python-dotenv
```

### ❌ uiautomator2 서버 타임아웃
```bash
# enhanced_test_runner.py에서 capabilities 설정 확인
# uiautomator2ServerInstallTimeout=60000
# uiautomator2ServerLaunchTimeout=60000
# adbExecTimeout=60000
```

## 📱 지원되는 앱 버전

| 국가 | 앱 패키지명 | 언어 |
|------|-------------|------|
| 🇻🇳 베트남 | `com.cesco.oversea.srs.viet` | vi, ko, en |
| 🇨🇳 중국 | `com.cesco.oversea.srs.cn` | zh, ko, en |
| 🇰🇷 한국 | `com.cesco.oversea.srs.dev` | ko, en |

## 🎯 다음 단계

### 기본 사용법 익히기
1. **설정 파일 이해** - [README.md의 설정 파일 섹션](README.md#설정-파일) 참조
2. **테스트 러너 종류** - 4가지 러너의 차이점 이해
3. **결과 분석** - 스크린샷과 로그 파일 해석

### 고급 기능 활용
1. **병렬 테스트** - 여러 디바이스로 동시 테스트
2. **커스텀 테스트** - 새로운 테스트 시나리오 작성
3. **CI/CD 통합** - 자동화 파이프라인 구축

### 문제 해결 및 최적화
1. **성능 튜닝** - 대기 시간 최적화
2. **안정성 향상** - 재시도 로직 커스터마이징
3. **확장성** - 더 많은 디바이스/언어 추가

## 📚 추가 리소스

- 📖 **상세 설치 가이드**: [INSTALLATION_GUIDE.md](INSTALLATION_GUIDE.md)
- 🚀 **향상된 테스트 작성**: [test_step_templates.md](test_step_templates.md)
- 🔄 **기존 테스트 마이그레이션**: [migration_guide.md](migration_guide.md)
- 📝 **변경 이력**: [CHANGELOG.md](CHANGELOG.md)

## 💬 도움말 및 지원

- **환경 검증**: `python verify_environment.py`
- **Appium 공식 문서**: https://appium.io/docs/
- **GitHub Issues**: 프로젝트 리포지토리의 Issues 탭

---

**🎊 축하합니다! 이제 Appium 자동화 테스트를 시작할 준비가 되었습니다!**