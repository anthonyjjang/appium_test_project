# install_dependencies.py
# WEBVIEW 요소 로깅 프로그램 의존성 설치 스크립트

import subprocess
import sys
import os

def run_command(command, description):
    """명령어 실행 및 결과 출력"""
    print(f"🔄 {description}...")
    try:
        result = subprocess.run(command, shell=True, capture_output=True, text=True)
        if result.returncode == 0:
            print(f"✅ {description} 완료")
            return True
        else:
            print(f"❌ {description} 실패:")
            print(result.stderr)
            return False
    except Exception as e:
        print(f"❌ {description} 중 오류: {e}")
        return False

def check_python_version():
    """Python 버전 확인"""
    version = sys.version_info
    print(f"🐍 Python 버전: {version.major}.{version.minor}.{version.micro}")
    
    if version.major < 3 or (version.major == 3 and version.minor < 8):
        print("❌ Python 3.8 이상이 필요합니다.")
        return False
    
    print("✅ Python 버전 호환성 확인 완료")
    return True

def install_requirements():
    """requirements.txt 패키지 설치"""
    print("📦 의존성 패키지 설치 시작")
    
    # 기본 요구사항 설치
    success = run_command(
        "pip install -r requirements.txt",
        "기본 패키지 설치"
    )
    
    if not success:
        print("⚠️ 일부 패키지 개별 설치 시도")
        
        # 핵심 패키지들 개별 설치
        core_packages = [
            "Appium-Python-Client>=3.1.0",
            "selenium>=4.15.0",
            "beautifulsoup4>=4.12.0",
            "lxml>=4.9.0",
            "jsonschema>=4.17.0",
            "rich>=13.5.0",
            "colorlog>=6.7.0"
        ]
        
        for package in core_packages:
            run_command(f"pip install '{package}'", f"{package} 설치")
    
    return True

def verify_installation():
    """설치 확인"""
    print("🔍 설치 확인 중...")
    
    required_packages = [
        'appium',
        'selenium', 
        'bs4',
        'lxml',
        'jsonschema',
        'rich',
        'colorlog'
    ]
    
    failed_imports = []
    
    for package in required_packages:
        try:
            __import__(package)
            print(f"✅ {package} 가져오기 성공")
        except ImportError:
            print(f"❌ {package} 가져오기 실패")
            failed_imports.append(package)
    
    if failed_imports:
        print(f"⚠️ 설치 실패한 패키지: {failed_imports}")
        print("수동으로 설치해주세요:")
        for package in failed_imports:
            print(f"  pip install {package}")
        return False
    
    print("✅ 모든 필수 패키지 설치 확인 완료")
    return True

def create_test_directories():
    """테스트 디렉토리 생성"""
    print("📁 테스트 디렉토리 생성")
    
    directories = [
        'screenshots',
        'logs',
        'reports',
        'exports'
    ]
    
    for directory in directories:
        try:
            os.makedirs(directory, exist_ok=True)
            print(f"✅ {directory} 디렉토리 생성")
        except Exception as e:
            print(f"❌ {directory} 디렉토리 생성 실패: {e}")
    
    return True

def main():
    """메인 설치 함수"""
    print("🚀 WEBVIEW 요소 로깅 프로그램 설치 시작")
    print("=" * 60)
    
    # 1. Python 버전 확인
    if not check_python_version():
        return False
    
    print()
    
    # 2. 의존성 설치
    if not install_requirements():
        return False
    
    print()
    
    # 3. 설치 확인
    if not verify_installation():
        return False
    
    print()
    
    # 4. 디렉토리 생성
    if not create_test_directories():
        return False
    
    print()
    print("🎉 설치 완료!")
    print("=" * 60)
    print("📋 다음 단계:")
    print("1. Appium 서버 실행: appium")
    print("2. 디바이스 연결 확인: adb devices")
    print("3. 테스트 실행: python appium_webview_element_logger.py")
    print("=" * 60)
    
    return True

if __name__ == '__main__':
    success = main()
    if not success:
        sys.exit(1)
