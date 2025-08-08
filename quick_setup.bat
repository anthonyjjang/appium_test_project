@echo off
REM Appium 테스트 환경 빠른 설정 스크립트 (Windows)
REM Usage: quick_setup.bat

echo ================================================
echo 🚀 Appium Test Environment Quick Setup (Windows)
echo ================================================

REM 관리자 권한 확인
net session >nul 2>&1
if %errorLevel% == 0 (
    echo [INFO] Running with administrator privileges
) else (
    echo [WARNING] Not running as administrator - some installations may fail
    echo Please run as administrator for best results
    pause
)

REM Chocolatey 설치 확인
echo [INFO] Checking Chocolatey installation...
choco --version >nul 2>&1
if %errorLevel% == 0 (
    echo [SUCCESS] Chocolatey is installed
) else (
    echo [INFO] Installing Chocolatey...
    powershell -Command "Set-ExecutionPolicy Bypass -Scope Process -Force; [System.Net.ServicePointManager]::SecurityProtocol = [System.Net.ServicePointManager]::SecurityProtocol -bor 3072; iex ((New-Object System.Net.WebClient).DownloadString('https://community.chocolatey.org/install.ps1'))"
    if %errorLevel% == 0 (
        echo [SUCCESS] Chocolatey installed successfully
    ) else (
        echo [ERROR] Failed to install Chocolatey
        goto :end
    )
)

REM Java 설치
echo [INFO] Checking Java installation...
java -version >nul 2>&1
if %errorLevel% == 0 (
    echo [SUCCESS] Java is installed
) else (
    echo [INFO] Installing Java...
    choco install -y openjdk11
    if %errorLevel% == 0 (
        echo [SUCCESS] Java installed successfully
        REM JAVA_HOME 설정
        for /f "tokens=*" %%i in ('where java') do set JAVA_PATH=%%i
        for %%i in ("%JAVA_PATH%") do set JAVA_HOME=%%~dpi..
        setx JAVA_HOME "%JAVA_HOME%" /M
        echo [INFO] JAVA_HOME set to: %JAVA_HOME%
    ) else (
        echo [ERROR] Failed to install Java
    )
)

REM Node.js 설치
echo [INFO] Checking Node.js installation...
node --version >nul 2>&1
if %errorLevel% == 0 (
    echo [SUCCESS] Node.js is installed
) else (
    echo [INFO] Installing Node.js...
    choco install -y nodejs
    if %errorLevel% == 0 (
        echo [SUCCESS] Node.js installed successfully
    ) else (
        echo [ERROR] Failed to install Node.js
    )
)

REM Python 설치
echo [INFO] Checking Python installation...
python --version >nul 2>&1
if %errorLevel% == 0 (
    echo [SUCCESS] Python is installed
) else (
    echo [INFO] Installing Python...
    choco install -y python3
    if %errorLevel% == 0 (
        echo [SUCCESS] Python installed successfully
    ) else (
        echo [ERROR] Failed to install Python
    )
)

REM Android SDK 안내
echo [INFO] Checking Android SDK...
if defined ANDROID_HOME (
    echo [SUCCESS] ANDROID_HOME is set: %ANDROID_HOME%
    if exist "%ANDROID_HOME%\platform-tools\adb.exe" (
        echo [SUCCESS] ADB found in platform-tools
    ) else (
        echo [WARNING] ADB not found in platform-tools directory
    )
) else (
    echo [WARNING] ANDROID_HOME not set
    echo [INFO] Please install Android Studio and configure:
    echo   1. Download from https://developer.android.com/studio
    echo   2. Install Android SDK Platform-Tools
    echo   3. Set ANDROID_HOME environment variable
    echo   4. Add platform-tools to PATH
)

REM PATH 새로고침
echo [INFO] Refreshing PATH environment variable...
call refreshenv

REM Appium 설치
echo [INFO] Checking Appium installation...
appium --version >nul 2>&1
if %errorLevel% == 0 (
    echo [SUCCESS] Appium is installed
) else (
    echo [INFO] Installing Appium...
    npm install -g appium
    if %errorLevel% == 0 (
        echo [SUCCESS] Appium installed successfully
        echo [INFO] Installing uiautomator2 driver...
        appium driver install uiautomator2
    ) else (
        echo [ERROR] Failed to install Appium
    )
)

REM Python 가상환경 설정
echo [INFO] Setting up Python virtual environment...
if not exist "appium_test_env" (
    echo [INFO] Creating Python virtual environment...
    python -m venv appium_test_env
    if %errorLevel% == 0 (
        echo [SUCCESS] Virtual environment created
    ) else (
        echo [ERROR] Failed to create virtual environment
        goto :python_packages
    )
)

echo [INFO] Activating virtual environment...
call appium_test_env\Scripts\activate.bat

echo [INFO] Upgrading pip...
python -m pip install --upgrade pip

:python_packages
echo [INFO] Installing Python packages...
if exist "requirements.txt" (
    echo [INFO] Installing from requirements.txt...
    pip install -r requirements.txt
) else (
    echo [INFO] Installing essential packages...
    pip install Appium-Python-Client>=3.1.0 selenium>=4.15.0 pandas>=2.1.0 python-dotenv>=1.0.0 openpyxl>=3.1.0
)

if %errorLevel% == 0 (
    echo [SUCCESS] Python packages installed successfully
) else (
    echo [WARNING] Some Python packages may not have installed correctly
)

REM 프로젝트 설정 파일
echo [INFO] Setting up project configuration...

if not exist ".env" (
    if exist ".env.template" (
        echo [INFO] Creating .env file from template...
        copy .env.template .env
        echo [WARNING] Please edit .env file with your specific configuration
    ) else (
        echo [WARNING] .env.template not found
    )
) else (
    echo [SUCCESS] .env file already exists
)

REM 디렉터리 생성
if not exist "screenshots" mkdir screenshots

echo ================================================
echo [SUCCESS] Setup completed!
echo ================================================
echo.
echo Next steps:
echo 1. Connect your Android device via USB
echo 2. Enable USB debugging on your device  
echo 3. Edit .env file with your configuration
echo 4. Run: python verify_environment.py
echo 5. Start Appium server: appium
echo 6. Run tests: python enhanced_test_runner.py
echo.
echo To activate Python virtual environment:
echo appium_test_env\Scripts\activate.bat
echo.
echo Note: You may need to restart your command prompt for environment variables to take effect.

:end
pause