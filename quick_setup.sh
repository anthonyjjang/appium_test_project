#!/bin/bash

# Appium 테스트 환경 빠른 설정 스크립트 (Mac/Linux)
# Usage: chmod +x quick_setup.sh && ./quick_setup.sh

echo "🚀 Appium Test Environment Quick Setup"
echo "======================================"

# 색상 정의
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# 함수 정의
print_status() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

check_command() {
    if command -v $1 &> /dev/null; then
        print_success "$1 is installed"
        return 0
    else
        print_error "$1 is not installed"
        return 1
    fi
}

# OS 확인
OS="$(uname -s)"
case "${OS}" in
    Linux*)     MACHINE=Linux;;
    Darwin*)    MACHINE=Mac;;
    *)          MACHINE="UNKNOWN:${OS}"
esac

print_status "Detected OS: ${MACHINE}"

# 1. 기본 도구 확인
print_status "Checking basic tools..."

if [[ "$MACHINE" == "Mac" ]]; then
    # Homebrew 설치 확인
    if ! command -v brew &> /dev/null; then
        print_warning "Homebrew not found. Installing..."
        /bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
    else
        print_success "Homebrew is installed"
    fi
elif [[ "$MACHINE" == "Linux" ]]; then
    # 패키지 관리자 업데이트
    print_status "Updating package manager..."
    sudo apt update
fi

# 2. Java 설치
print_status "Checking Java installation..."
if ! check_command java; then
    print_status "Installing Java..."
    if [[ "$MACHINE" == "Mac" ]]; then
        brew install openjdk@11
        # Java 경로 설정
        echo 'export JAVA_HOME=/opt/homebrew/opt/openjdk@11/libexec/openjdk.jdk/Contents/Home' >> ~/.zshrc
        echo 'export PATH=$JAVA_HOME/bin:$PATH' >> ~/.zshrc
        source ~/.zshrc
    elif [[ "$MACHINE" == "Linux" ]]; then
        sudo apt install -y openjdk-11-jdk
        echo 'export JAVA_HOME=/usr/lib/jvm/java-11-openjdk-amd64' >> ~/.bashrc
        echo 'export PATH=$JAVA_HOME/bin:$PATH' >> ~/.bashrc
        source ~/.bashrc
    fi
fi

# 3. Node.js 설치
print_status "Checking Node.js installation..."
if ! check_command node; then
    print_status "Installing Node.js..."
    if [[ "$MACHINE" == "Mac" ]]; then
        brew install node
    elif [[ "$MACHINE" == "Linux" ]]; then
        curl -fsSL https://deb.nodesource.com/setup_lts.x | sudo -E bash -
        sudo apt-get install -y nodejs
    fi
fi

# 4. Android SDK 설치 안내
print_status "Checking Android SDK..."
if [[ -z "$ANDROID_HOME" ]]; then
    print_warning "ANDROID_HOME not set"
    print_status "Please install Android Studio and set ANDROID_HOME:"
    print_status "1. Download from https://developer.android.com/studio"
    print_status "2. Install Android SDK Platform-Tools"
    print_status "3. Set environment variables:"
    if [[ "$MACHINE" == "Mac" ]]; then
        print_status "   echo 'export ANDROID_HOME=\$HOME/Library/Android/sdk' >> ~/.zshrc"
        print_status "   echo 'export PATH=\$ANDROID_HOME/platform-tools:\$PATH' >> ~/.zshrc"
    elif [[ "$MACHINE" == "Linux" ]]; then
        print_status "   echo 'export ANDROID_HOME=\$HOME/Android/Sdk' >> ~/.bashrc"
        print_status "   echo 'export PATH=\$ANDROID_HOME/platform-tools:\$PATH' >> ~/.bashrc"
    fi
else
    print_success "ANDROID_HOME is set: $ANDROID_HOME"
fi

# 5. Appium 설치
print_status "Checking Appium installation..."
if ! check_command appium; then
    print_status "Installing Appium..."
    npm install -g appium
    appium driver install uiautomator2
else
    print_success "Appium is installed"
    # uiautomator2 드라이버 확인 및 설치
    print_status "Checking uiautomator2 driver..."
    if ! appium driver list | grep -q "uiautomator2"; then
        print_status "Installing uiautomator2 driver..."
        appium driver install uiautomator2
    fi
fi

# 6. Python 환경 설정
print_status "Setting up Python environment..."

# Python 3 확인
if ! check_command python3; then
    print_error "Python 3 is required but not found"
    if [[ "$MACHINE" == "Mac" ]]; then
        print_status "Installing Python 3..."
        brew install python3
    elif [[ "$MACHINE" == "Linux" ]]; then
        print_status "Installing Python 3..."
        sudo apt install -y python3 python3-pip python3-venv
    fi
fi

# 가상환경 생성
if [[ ! -d "appium_test_env" ]]; then
    print_status "Creating Python virtual environment..."
    python3 -m venv appium_test_env
fi

# 가상환경 활성화 및 패키지 설치
print_status "Installing Python packages..."
source appium_test_env/bin/activate

# pip 업그레이드
pip install --upgrade pip

# requirements.txt가 있으면 설치
if [[ -f "requirements.txt" ]]; then
    pip install -r requirements.txt
else
    # 기본 패키지 설치
    pip install Appium-Python-Client>=3.1.0 selenium>=4.15.0 pandas>=2.1.0 python-dotenv>=1.0.0 openpyxl>=3.1.0
fi

# 7. 프로젝트 설정 파일 생성
print_status "Setting up project configuration..."

# .env 파일 생성
if [[ ! -f ".env" ]] && [[ -f ".env.template" ]]; then
    print_status "Creating .env file from template..."
    cp .env.template .env
    print_warning "Please edit .env file with your specific configuration"
fi

# 디렉터리 생성
mkdir -p screenshots

# 8. 권한 설정 (실행 가능하도록)
chmod +x verify_environment.py

print_success "Setup completed!"
print_status "Next steps:"
print_status "1. Connect your Android device via USB"
print_status "2. Enable USB debugging on your device"
print_status "3. Edit .env file with your configuration"
print_status "4. Run: python verify_environment.py"
print_status "5. Start Appium server: appium"
print_status "6. Run tests: python enhanced_test_runner.py"

echo ""
print_status "To activate Python virtual environment:"
print_status "source appium_test_env/bin/activate"

echo ""
print_status "Setup script completed!"