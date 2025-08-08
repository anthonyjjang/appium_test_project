# 🚀 Appium 테스트 프레임워크

**다국가/다언어 모바일 앱 자동화 테스트 프레임워크**

[![Python](https://img.shields.io/badge/Python-3.8%2B-blue.svg)](https://www.python.org/)
[![Appium](https://img.shields.io/badge/Appium-2.x-green.svg)](https://appium.io/)
[![License](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

> CESCO 해외 SRS 앱(베트남/중국/한국 버전)을 위한 포괄적인 자동화 테스트 솔루션

## 📋 목차

- [주요 기능](#-주요-기능)
- [빠른 시작](#-빠른-시작)
- [상세 설치](#-상세-설치)
- [테스트 러너](#-테스트-러너)
- [설정 파일](#-설정-파일)
- [사용 방법](#-사용-방법)
- [문제 해결](#-문제-해결)
- [기여 방법](#-기여-방법)

## 🌟 주요 기능

### ✨ 핵심 기능
- 🌐 **다국가 지원**: 베트남(VN), 중국(CN), 한국(KR) 버전
- 🗣️ **다언어 테스트**: 자동 언어 전환 및 언어별 검증
- 🔄 **병렬 실행**: 다중 디바이스 동시 테스트
- 📊 **Excel 연동**: Excel 파일 기반 테스트 시나리오
- 🔍 **향상된 검증**: 25개 전문화된 테스트 액션
- 📸 **자동 스크린샷**: 실패/성공 시점별 자동 캡처
- 📈 **상세 리포트**: 단계별 실행 시간 및 성공률 분석

### 🛠️ 기술적 특징
- **환경변수 기반 설정**: `.env` 파일로 중앙집중식 관리
- **재시도 로직**: 네트워크/UI 불안정성 대응
- **동적 대기**: 스마트한 요소 대기 및 로딩 감지
- **테스트 데이터 분리**: CSV 기반 데이터 관리
- **에러 처리**: 상세한 에러 로깅 및 복구 로직

## ⚡ 빠른 시작

### 1️⃣ 자동 설치 (권장)

```bash
# Mac/Linux
chmod +x quick_setup.sh
./quick_setup.sh

# Windows (관리자 권한으로 실행)
quick_setup.bat
```

### 2️⃣ 환경 검증

```bash
# 설치 환경 자동 검증
python verify_environment.py
```

### 3️⃣ 기본 설정

```bash
# 설정 파일 생성
cp .env.template .env
# .env 파일을 편집하여 본인 환경에 맞게 수정
```

### 4️⃣ 테스트 실행

```bash
# Appium 서버 시작 (별도 터미널)
appium

# 기본 테스트 실행
python appium_test_runner.py

# 향상된 테스트 실행 (권장)
python enhanced_test_runner.py
```

## 🔧 상세 설치

### 시스템 요구사항

**PC 환경:**
- 🖥️ **OS**: Windows 10+, macOS 10.15+, Ubuntu 18.04+
- ☕ **Java**: OpenJDK 11+ 
- 🟢 **Node.js**: LTS 버전 (18.x+)
- 🐍 **Python**: 3.8+
- 📱 **Android SDK**: API Level 28+

**모바일 디바이스:**
- 📲 **OS**: Android 8.0+ (API Level 26+)
- 🔌 **연결**: USB 디버깅 활성화
- 📦 **앱**: CESCO SRS 앱 설치 필요

### 수동 설치

자세한 수동 설치 가이드는 [`INSTALLATION_GUIDE.md`](INSTALLATION_GUIDE.md)를 참조하세요.

## ⚙️ 설정 파일

### 환경 설정 (.env)

| 설정 항목 | 설명 | 예시 |
|-----------|------|------|
| `BASE_URL` | 테스트 대상 앱 기본 URL | `http://localhost/` |
| `USER_ID`, `USER_PW` | 테스트용 로그인 계정 | `testuser`, `password123` |
| `DEFAULT_UDID` | 기본 디바이스 UDID | `RFCX715QHAL` |
| `SLEEP_TIME` | 단계 간 대기 시간(초) | `3` |
| `APPIUM_HOST`, `APPIUM_PORT` | Appium 서버 설정 | `localhost`, `4723` |

### 국가별 설정

```bash
# 베트남 버전
VN_APP_PACKAGE=com.cesco.oversea.srs.viet
VN_WEBVIEW_NAME=WEBVIEW_com.cesco.oversea.srs.viet
VN_LANGUAGES=vi,ko,en

# 중국 버전 
CN_APP_PACKAGE=com.cesco.oversea.srs.cn
CN_WEBVIEW_NAME=WEBVIEW_com.cesco.oversea.srs.cn
CN_LANGUAGES=zh,ko,en

# 한국 버전
KR_APP_PACKAGE=com.cesco.oversea.srs.dev  
KR_WEBVIEW_NAME=WEBVIEW_com.cesco.oversea.srs.dev
KR_LANGUAGES=ko,en
```

### CSV 설정 파일

#### `devices.csv` - 디바이스 설정
```csv
device_id,udid,platform_name,platform_version
DEVICE_SAMSUNG01,RFCX715QHAL,Android,14
```

#### `users.csv` - 사용자 계정
```csv
user_id,user_pw,country_code,app_package,webview_name,description
testuser01,pass123,VN,com.cesco.oversea.srs.viet,WEBVIEW_com.cesco.oversea.srs.viet,베트남 테스트 계정
```

#### `test_data.csv` - 테스트 데이터
```csv
test_id,data_type,key,value,description,locale
TC001,credential,user_id,testuser,테스트 계정 ID,all
TC001,validation,page_title,홈,메인 페이지 제목,ko
```

## 🏃‍♂️ 테스트 러너

### 1. 🔰 기본 테스트 러너 (`appium_test_runner.py`)
- **용도**: 단순한 네비게이션 테스트
- **특징**: 단일 디바이스, 순차 실행
- **설정**: 환경변수 기반 (중국 버전 기본)

```bash
python appium_test_runner.py
```

### 2. ⚡ 병렬 테스트 러너 (`appium_parallel_test_runner.py`)
- **용도**: 다중 디바이스 동시 테스트
- **특징**: ThreadPoolExecutor 기반 병렬 처리
- **설정**: CSV 파일 기반 디바이스/사용자 관리

```bash
python appium_parallel_test_runner.py
```

### 3. 📊 Excel 테스트 러너 (`appium_excel_test_runner.py`) 
- **용도**: Excel 기반 테스트 시나리오
- **특징**: pandas 활용, 베트남 버전 특화
- **설정**: `test_scenarios.xlsx` 파일 기반

```bash
python appium_excel_test_runner.py
```

### 4. 🚀 향상된 테스트 러너 (`enhanced_test_runner.py`) ⭐
- **용도**: 완전한 검증 로직이 포함된 테스트
- **특징**: 25개 전문화 액션, 재시도 로직, 상세 리포트
- **설정**: `test_steps_enhanced.csv` + `test_data.csv`

```bash
python enhanced_test_runner.py
```

## 🎯 테스트 시나리오

### 기본 테스트 (47개 화면)
- 로그인/로그아웃
- 네비게이션 메뉴  
- 고객관리 (검색, 상세정보, 계약정보 등)
- 서비스 관리 (방역, 설치, 회수 등)
- 루트플랜 (조회, 배정, 변경)
- 리포트 및 통계

### 향상된 테스트 (6개 핵심 시나리오)
1. **로그인 테스트** (9단계) - 완전한 검증 플로우
2. **고객 검색** (9단계) - 검색어 입력부터 결과 검증까지  
3. **고객 상세보기** (8단계) - 탭 네비게이션 포함
4. **루트플랜 조회** (9단계) - 달력 네비게이션 테스트
5. **설치/회수 관리** (10단계) - 상태 업데이트 포함
6. **수금 등록** (10단계) - 폼 입력 및 검증

## 🚀 사용 방법

### 기본 실행 플로우

```bash
# 1. Python 가상환경 활성화 (선택사항)
source appium_test_env/bin/activate  # Mac/Linux
appium_test_env\Scripts\activate     # Windows

# 2. 환경 검증
python verify_environment.py

# 3. Android 디바이스 연결 확인
adb devices

# 4. Appium 서버 시작 (별도 터미널)
appium

# 5. 테스트 실행
python enhanced_test_runner.py
```

### 고급 사용법

#### 특정 언어만 테스트
```bash
# .env 파일에서 언어 설정
CN_LANGUAGES=ko  # 한국어만 테스트
```

#### 디버그 모드 실행
```bash
# Appium 서버 디버그 모드
appium --log-level debug

# Python 로깅 활성화
export PYTHONPATH=.
python -c "import logging; logging.basicConfig(level=logging.DEBUG)" enhanced_test_runner.py
```

#### 병렬 테스트 (다중 디바이스)
```bash
# devices.csv와 users.csv 설정 후
python appium_parallel_test_runner.py
```

## 📊 결과 파일

### 스크린샷
```
screenshots/
└── test_20250108_143022/
    ├── login_success.png
    ├── ko_TC001_step1_error.png
    └── zh_TC002_final.png
```

### 테스트 결과 로그
```csv
# test_results_enhanced_20250108_143022.csv
timestamp,language,test_id,step_order,step_description,status,execution_time_ms
2025-01-08T14:30:22,ko,TC001,1,로그인 페이지 로딩 대기,PASS,2341
2025-01-08T14:30:24,ko,TC001,2,아이디 입력,PASS,892
```

### 실행 결과 예시
```
🎯 Test case completed: 8/9 steps passed (88.9%)
⏱️  Total execution time: 15432ms
📊 Final Results:
   - Total Tests: 18/18
   - Passed Tests: 16  
   - Failed Tests: 2
   - Success Rate: 88.9%
```

## 📁 프로젝트 구조

```
appiumTestProject/
├── 📋 README.md                    # 프로젝트 개요
├── 🔧 INSTALLATION_GUIDE.md        # 상세 설치 가이드  
├── 📝 migration_guide.md           # 기존→향상된 테스트 마이그레이션
├── 📖 test_step_templates.md       # 테스트 스텝 작성 가이드
├── ⚙️ .env                        # 환경 설정 (사용자 생성)
├── 📄 .env.template               # 환경 설정 템플릿
├── 📦 requirements.txt            # Python 패키지 목록
├── 🔍 verify_environment.py       # 환경 검증 스크립트
├── 🚀 quick_setup.sh/.bat         # 자동 설치 스크립트
│
├── 🧪 테스트 러너
│   ├── appium_test_runner.py      # 기본 테스트 러너
│   ├── appium_parallel_test_runner.py  # 병렬 실행 러너
│   ├── appium_excel_test_runner.py     # Excel 기반 러너
│   └── enhanced_test_runner.py    # 향상된 러너 ⭐
│
├── ⚡ 테스트 엔진
│   └── enhanced_test_engine.py    # 향상된 테스트 엔진
│
├── 📊 설정 및 데이터 파일
│   ├── devices.csv                # 디바이스 설정
│   ├── users.csv                  # 사용자 계정
│   ├── test_cases.csv             # 기본 테스트 케이스
│   ├── test_steps.csv             # 기본 테스트 스텝
│   ├── test_steps_enhanced.csv    # 향상된 테스트 스텝 ⭐
│   ├── test_data.csv              # 테스트 데이터 ⭐
│   ├── test_pairs.csv             # 테스트 페어 설정
│   └── *.json                     # JSON 기반 테스트 케이스
│
└── 📸 screenshots/                # 실행 결과 스크린샷
    └── test_YYYYMMDD_HHMMSS/
```

## 🔧 문제 해결

### 일반적인 문제

#### ❌ 디바이스 연결 안됨
```bash
# USB 드라이버 재설치 후
adb kill-server
adb start-server
adb devices
```

#### ❌ Appium 연결 실패
```bash
# 포트 충돌 확인
netstat -ano | findstr :4723  # Windows
lsof -i :4723                 # Mac/Linux

# 다른 포트 사용
appium -p 4724
```

#### ❌ WebView 컨텍스트 전환 실패
- Chrome 브라우저에서 `chrome://inspect/#devices` 접속
- WebView 디버깅 활성화 확인
- 앱에서 WebView 디버깅 허용 설정

#### ❌ 테스트 스텝 실패
```bash
# 상세 로그 확인
appium --log-level debug --log ./appium.log

# 스크린샷으로 현재 화면 상태 확인
# screenshots/ 디렉터리의 에러 시점 이미지 분석
```

### 성능 최적화

```bash
# .env 파일에서 대기 시간 조정
SLEEP_TIME=1          # 빠른 실행 (불안정할 수 있음)
SLEEP_TIME=5          # 안정적 실행 (느림)
IMPLICIT_WAIT=5       # 요소 대기 시간
EXPLICIT_WAIT=15      # 페이지 로딩 대기
```

## 📞 지원 및 문의

### 유용한 링크
- 📚 [Appium 공식 문서](https://appium.io/docs/en/2.1/)
- 🤖 [Android SDK 다운로드](https://developer.android.com/studio)
- 🐍 [Python Appium Client](https://pypi.org/project/Appium-Python-Client/)
- 💬 [Appium 커뮤니티](https://discuss.appium.io/)

### 로그 및 디버깅
```bash
# 상세 로그 수집
appium --log-level debug --log ./appium_debug.log

# adb 로그 실시간 확인
adb logcat | grep -i appium

# Python 상세 로깅
import logging
logging.basicConfig(level=logging.DEBUG)
```

### 버그 리포트

이슈 발생 시 다음 정보와 함께 문의해주세요:
- 운영체제 및 버전
- Python, Java, Node.js 버전
- Appium 버전
- Android 디바이스 모델 및 OS 버전
- 에러 로그 및 스크린샷

## 🤝 기여 방법

1. 프로젝트 포크
2. 기능 브랜치 생성 (`git checkout -b feature/amazing-feature`)
3. 변경사항 커밋 (`git commit -m 'Add amazing feature'`)
4. 브랜치에 푸시 (`git push origin feature/amazing-feature`) 
5. Pull Request 생성

### 개발 가이드라인
- Python PEP 8 스타일 가이드 준수
- 새로운 테스트 스텝 추가 시 `test_step_templates.md` 참고
- 환경변수 추가 시 `.env.template` 업데이트
- 문서 업데이트 필수

---

## 📄 라이선스

MIT License - 자세한 내용은 [LICENSE](LICENSE) 파일 참고

---

**Made with ❤️ for CESCO SRS Mobile Testing**