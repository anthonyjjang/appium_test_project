#!/bin/bash
# start_appium_server.sh
# Appium 서버 시작 스크립트 (Chromedriver 자동 다운로드 지원)

echo "🚀 Appium 서버 시작 중..."

# 기존 Appium 프로세스 종료
echo "🔄 기존 Appium 프로세스 정리 중..."
pkill -f appium 2>/dev/null

# 잠시 대기
sleep 2

echo "📋 Appium 서버 시작 옵션:"
echo "1. 기본 모드 (자동 다운로드 없음)"
echo "2. Chromedriver 자동 다운로드 모드 (권장)"
echo "3. 디버그 모드"

read -p "선택하세요 (1-3): " choice

case $choice in
    1)
        echo "🟢 기본 모드로 시작..."
        appium server --port 4723 --log-level info
        ;;
    2)
        echo "🟢 Chromedriver 자동 다운로드 모드로 시작... (권장)"
        appium server --allow-insecure uiautomator2:chromedriver_autodownload --port 4723 --log-level info
        ;;
    3)
        echo "🟢 디버그 모드로 시작..."
        appium server --allow-insecure uiautomator2:chromedriver_autodownload --port 4723 --log-level debug
        ;;
    *)
        echo "🟡 기본값: Chromedriver 자동 다운로드 모드"
        appium server --allow-insecure uiautomator2:chromedriver_autodownload --port 4723 --log-level info
        ;;
esac
