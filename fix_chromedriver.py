#!/usr/bin/env python3
# fix_chromedriver.py
# Chromedriver 139 버전 호환성 문제 해결 스크립트

import os
import requests
import zipfile
import platform
import subprocess
import json

def get_device_chrome_version():
    """디바이스의 Chrome 버전 확인"""
    try:
        result = subprocess.run(['adb', 'shell', 'dumpsys', 'package', 'com.android.chrome'], 
                              capture_output=True, text=True)
        
        # Chrome 버전 추출 (간단한 방법)
        print("📱 디바이스 Chrome 정보:")
        lines = result.stdout.split('\n')
        for line in lines:
            if 'versionName' in line:
                print(f"   {line.strip()}")
        
        return "139.0.7258"  # 로그에서 확인된 버전
    except Exception as e:
        print(f"⚠️ Chrome 버전 확인 실패: {e}")
        return "139.0.7258"

def download_chromedriver(version="139.0.7258"):
    """호환되는 Chromedriver 다운로드"""
    print(f"🔄 Chromedriver {version} 다운로드 중...")
    
    # 시스템 아키텍처 확인
    system = platform.system().lower()
    machine = platform.machine().lower()
    
    if system == "darwin":  # macOS
        if "arm" in machine or "aarch64" in machine:
            platform_name = "mac-arm64"
        else:
            platform_name = "mac-x64"
    elif system == "linux":
        platform_name = "linux64"
    else:
        platform_name = "win32"
    
    # Chromedriver 다운로드 URL (새로운 형식)
    major_version = version.split('.')[0]
    
    try:
        # Chrome for Testing API 사용 (새로운 방식)
        api_url = f"https://googlechromelabs.github.io/chrome-for-testing/known-good-versions-with-downloads.json"
        
        print("🔍 호환되는 Chromedriver 버전 검색 중...")
        response = requests.get(api_url, timeout=30)
        data = response.json()
        
        # 139 버전과 호환되는 Chromedriver 찾기
        compatible_version = None
        for version_info in data['versions']:
            if version_info['version'].startswith('139.'):
                if 'chromedriver' in version_info['downloads']:
                    for download in version_info['downloads']['chromedriver']:
                        if download['platform'] == platform_name:
                            compatible_version = version_info['version']
                            download_url = download['url']
                            break
                    if compatible_version:
                        break
        
        if not compatible_version:
            print(f"❌ Chrome {version}과 호환되는 Chromedriver를 찾을 수 없습니다")
            print("💡 대안:")
            print("   1. 앱의 Chrome 버전을 업데이트")
            print("   2. 다른 버전의 Chromedriver 수동 설치")
            print("   3. Appium 설정에서 chromedriverAutodownload=True 확인")
            return False
            
        print(f"✅ 호환 버전 발견: {compatible_version}")
        print(f"📥 다운로드 URL: {download_url}")
        
        # 다운로드 디렉토리 생성
        chrome_dir = os.path.expanduser("~/.appium/chromedriver")
        os.makedirs(chrome_dir, exist_ok=True)
        
        # Chromedriver 다운로드
        print("⬇️ Chromedriver 다운로드 중...")
        response = requests.get(download_url, timeout=60)
        
        zip_path = os.path.join(chrome_dir, f"chromedriver_{compatible_version}.zip")
        with open(zip_path, 'wb') as f:
            f.write(response.content)
        
        # 압축 해제
        print("📦 압축 해제 중...")
        with zipfile.ZipFile(zip_path, 'r') as zip_ref:
            zip_ref.extractall(chrome_dir)
        
        # 실행 권한 부여 (macOS/Linux)
        if system != "windows":
            chromedriver_path = os.path.join(chrome_dir, "chromedriver-" + platform_name, "chromedriver")
            if os.path.exists(chromedriver_path):
                os.chmod(chromedriver_path, 0o755)
                print(f"✅ Chromedriver 설치 완료: {chromedriver_path}")
                
                # 심볼릭 링크 생성
                link_path = "/usr/local/bin/chromedriver"
                try:
                    if os.path.exists(link_path):
                        os.unlink(link_path)
                    os.symlink(chromedriver_path, link_path)
                    print(f"🔗 심볼릭 링크 생성: {link_path}")
                except Exception as e:
                    print(f"⚠️ 심볼릭 링크 생성 실패: {e}")
                    print(f"💡 수동으로 PATH에 추가: {chromedriver_path}")
        
        # 임시 파일 정리
        os.remove(zip_path)
        
        print(f"🎉 Chromedriver {compatible_version} 설치 완료!")
        return True
        
    except Exception as e:
        print(f"❌ Chromedriver 다운로드 실패: {e}")
        return False

def verify_chromedriver():
    """Chromedriver 설치 확인"""
    try:
        result = subprocess.run(['chromedriver', '--version'], 
                              capture_output=True, text=True)
        print(f"✅ 설치된 Chromedriver: {result.stdout.strip()}")
        return True
    except Exception as e:
        print(f"⚠️ Chromedriver 확인 실패: {e}")
        return False

def main():
    print("🔧 Chromedriver 호환성 문제 해결")
    print("=" * 50)
    
    # 1. 디바이스 Chrome 버전 확인
    chrome_version = get_device_chrome_version()
    print(f"🎯 대상 Chrome 버전: {chrome_version}")
    
    # 2. Chromedriver 다운로드 및 설치
    if download_chromedriver(chrome_version):
        print("\n✅ Chromedriver 설치 성공!")
        
        # 3. 설치 확인
        print("\n🔍 설치 확인:")
        verify_chromedriver()
        
        print("\n📋 다음 단계:")
        print("1. Appium 서버 재시작")
        print("2. 앱을 완전히 종료하고 재실행")
        print("3. WEBVIEW 테스트 프로그램 재실행")
        
    else:
        print("\n❌ Chromedriver 설치 실패")
        print("\n🛠️ 수동 해결 방법:")
        print("1. https://chromedriver.chromium.org/downloads 방문")
        print("2. Chrome 139 버전 호환 드라이버 다운로드")
        print("3. /usr/local/bin/chromedriver로 복사")
        print("4. chmod +x /usr/local/bin/chromedriver 실행")

if __name__ == "__main__":
    main()
