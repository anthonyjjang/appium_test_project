#!/usr/bin/env python3
"""
Appium 테스트 환경 검증 스크립트
이 스크립트는 테스트 실행에 필요한 모든 환경을 자동으로 검증합니다.
"""

import os
import sys
import subprocess
import json
from pathlib import Path

class EnvironmentVerifier:
    def __init__(self):
        self.results = []
        self.errors = []
        self.warnings = []
    
    def run_command(self, cmd, shell=True):
        """명령어 실행 및 결과 반환"""
        try:
            result = subprocess.run(cmd, shell=shell, capture_output=True, text=True, timeout=30)
            return result.returncode == 0, result.stdout.strip(), result.stderr.strip()
        except subprocess.TimeoutExpired:
            return False, "", "Command timeout"
        except Exception as e:
            return False, "", str(e)
    
    def check_java(self):
        """Java 환경 확인"""
        print("🔍 Checking Java environment...")
        
        success, output, error = self.run_command("java -version")
        if success:
            java_version = output.split('\n')[0] if output else error.split('\n')[0]
            self.results.append(f"✅ Java: {java_version}")
            
            # JAVA_HOME 확인
            java_home = os.environ.get('JAVA_HOME')
            if java_home:
                self.results.append(f"✅ JAVA_HOME: {java_home}")
            else:
                self.warnings.append("⚠️  JAVA_HOME environment variable not set")
        else:
            self.errors.append("❌ Java not found or not properly installed")
    
    def check_nodejs(self):
        """Node.js 환경 확인"""
        print("🔍 Checking Node.js environment...")
        
        success, output, _ = self.run_command("node --version")
        if success:
            self.results.append(f"✅ Node.js: {output}")
        else:
            self.errors.append("❌ Node.js not found")
        
        success, output, _ = self.run_command("npm --version")
        if success:
            self.results.append(f"✅ npm: {output}")
        else:
            self.errors.append("❌ npm not found")
    
    def check_python(self):
        """Python 환경 확인"""
        print("🔍 Checking Python environment...")
        
        python_version = f"{sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}"
        self.results.append(f"✅ Python: {python_version}")
        
        # 필수 패키지 확인
        required_packages = [
            'appium',
            'selenium', 
            'pandas',
            'python-dotenv',
            'openpyxl'
        ]
        
        for package in required_packages:
            try:
                __import__(package.replace('-', '_'))
                self.results.append(f"✅ Python package: {package}")
            except ImportError:
                self.errors.append(f"❌ Python package missing: {package}")
    
    def check_android_sdk(self):
        """Android SDK 환경 확인"""
        print("🔍 Checking Android SDK...")
        
        # ANDROID_HOME 확인
        android_home = os.environ.get('ANDROID_HOME') or os.environ.get('ANDROID_SDK_ROOT')
        if android_home:
            self.results.append(f"✅ ANDROID_HOME: {android_home}")
            
            # platform-tools 확인
            platform_tools = Path(android_home) / 'platform-tools'
            if platform_tools.exists():
                self.results.append(f"✅ Platform-tools found: {platform_tools}")
            else:
                self.errors.append(f"❌ Platform-tools not found in {android_home}")
        else:
            self.errors.append("❌ ANDROID_HOME environment variable not set")
        
        # adb 명령어 확인
        success, output, _ = self.run_command("adb version")
        if success:
            adb_version = output.split('\n')[0]
            self.results.append(f"✅ ADB: {adb_version}")
        else:
            self.errors.append("❌ ADB command not found")
    
    def check_appium(self):
        """Appium 환경 확인"""
        print("🔍 Checking Appium...")
        
        # Appium 버전 확인
        success, output, _ = self.run_command("appium --version")
        if success:
            self.results.append(f"✅ Appium: {output}")
        else:
            self.errors.append("❌ Appium not found")
            return
        
        # Appium 드라이버 확인
        success, output, _ = self.run_command("appium driver list")
        if success:
            if 'uiautomator2' in output:
                self.results.append("✅ Appium driver: uiautomator2 installed")
            else:
                self.errors.append("❌ uiautomator2 driver not installed")
        else:
            self.warnings.append("⚠️  Could not check Appium drivers")
    
    def check_devices(self):
        """연결된 디바이스 확인"""
        print("🔍 Checking connected devices...")
        
        success, output, _ = self.run_command("adb devices")
        if success:
            lines = output.split('\n')[1:]  # 첫 번째 헤더 라인 제외
            devices = [line.split()[0] for line in lines if line.strip() and 'device' in line]
            
            if devices:
                self.results.append(f"✅ Connected devices: {len(devices)}")
                for device in devices:
                    # 디바이스 정보 가져오기
                    model_success, model, _ = self.run_command(f"adb -s {device} shell getprop ro.product.model")
                    android_success, android_ver, _ = self.run_command(f"adb -s {device} shell getprop ro.build.version.release")
                    
                    device_info = f"{device}"
                    if model_success and model:
                        device_info += f" ({model})"
                    if android_success and android_ver:
                        device_info += f" Android {android_ver}"
                    
                    self.results.append(f"  📱 {device_info}")
            else:
                self.warnings.append("⚠️  No devices connected")
        else:
            self.errors.append("❌ Could not check connected devices")
    
    def check_project_files(self):
        """프로젝트 파일 확인"""
        print("🔍 Checking project files...")
        
        required_files = [
            '.env.template',
            'requirements.txt',
            'enhanced_test_engine.py',
            'enhanced_test_runner.py',
            'test_data.csv',
            'test_steps_enhanced.csv'
        ]
        
        for file in required_files:
            if Path(file).exists():
                self.results.append(f"✅ Project file: {file}")
            else:
                self.warnings.append(f"⚠️  Project file missing: {file}")
        
        # .env 파일 확인
        if Path('.env').exists():
            self.results.append("✅ .env configuration file exists")
        else:
            self.warnings.append("⚠️  .env file not found - copy from .env.template and configure")
    
    def check_appium_server(self):
        """Appium 서버 연결 테스트"""
        print("🔍 Testing Appium server connectivity...")
        
        try:
            import requests
            response = requests.get('http://localhost:4723/status', timeout=5)
            if response.status_code == 200:
                self.results.append("✅ Appium server is running on port 4723")
            else:
                self.warnings.append("⚠️  Appium server responded with non-200 status")
        except ImportError:
            self.warnings.append("⚠️  requests package not available for server test")
        except Exception:
            self.warnings.append("⚠️  Appium server not running on port 4723")
    
    def check_permissions(self):
        """권한 및 디렉터리 확인"""
        print("🔍 Checking permissions...")
        
        # 스크린샷 디렉터리 생성 권한 확인
        try:
            test_dir = Path('screenshots/test_permission_check')
            test_dir.mkdir(parents=True, exist_ok=True)
            test_file = test_dir / 'test.txt'
            test_file.write_text('permission test')
            test_file.unlink()
            test_dir.rmdir()
            Path('screenshots').rmdir()
            self.results.append("✅ File system permissions OK")
        except Exception as e:
            self.errors.append(f"❌ File system permission error: {e}")
    
    def run_all_checks(self):
        """모든 검증 실행"""
        print("🚀 Starting environment verification...\n")
        
        self.check_java()
        self.check_nodejs()
        self.check_python()
        self.check_android_sdk()
        self.check_appium()
        self.check_devices()
        self.check_project_files()
        self.check_appium_server()
        self.check_permissions()
        
        self.print_results()
    
    def print_results(self):
        """결과 출력"""
        print("\n" + "="*60)
        print("📋 ENVIRONMENT VERIFICATION RESULTS")
        print("="*60)
        
        if self.results:
            print("\n✅ PASSED CHECKS:")
            for result in self.results:
                print(f"  {result}")
        
        if self.warnings:
            print("\n⚠️  WARNINGS:")
            for warning in self.warnings:
                print(f"  {warning}")
        
        if self.errors:
            print("\n❌ ERRORS:")
            for error in self.errors:
                print(f"  {error}")
        
        print("\n" + "="*60)
        
        total_checks = len(self.results) + len(self.warnings) + len(self.errors)
        success_rate = (len(self.results) / total_checks * 100) if total_checks > 0 else 0
        
        print(f"📊 SUMMARY:")
        print(f"  Total Checks: {total_checks}")
        print(f"  Passed: {len(self.results)}")
        print(f"  Warnings: {len(self.warnings)}")
        print(f"  Errors: {len(self.errors)}")
        print(f"  Success Rate: {success_rate:.1f}%")
        
        if len(self.errors) == 0:
            if len(self.warnings) == 0:
                print("\n🎉 Environment is fully ready for testing!")
            else:
                print("\n✅ Environment is ready for testing with minor warnings.")
        else:
            print(f"\n❌ Environment has {len(self.errors)} critical error(s) that need to be fixed.")
            print("\n📝 Next Steps:")
            print("  1. Fix the errors listed above")
            print("  2. Run this script again to verify")
            print("  3. Check INSTALLATION_GUIDE.md for detailed setup instructions")
        
        print("="*60)

def main():
    """메인 실행 함수"""
    verifier = EnvironmentVerifier()
    verifier.run_all_checks()
    
    # 에러가 있으면 비정상 종료
    if verifier.errors:
        sys.exit(1)
    else:
        sys.exit(0)

if __name__ == '__main__':
    main()