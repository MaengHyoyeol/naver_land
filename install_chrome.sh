#!/bin/bash
# Amazon Linux 2023 Chrome 설치 스크립트
# EC2에서 직접 실행하세요

set -e

echo "🌐 Chrome 설치 시작..."

# 1. 의존성 설치
echo "📚 Chrome 의존성 설치 중..."
sudo dnf install -y \
    alsa-lib \
    atk \
    cups-libs \
    gtk3 \
    ipa-gothic-fonts \
    libXcomposite \
    libXcursor \
    libXdamage \
    libXext \
    libXi \
    libXrandr \
    libXScrnSaver \
    libXtst \
    pango \
    xorg-x11-fonts-100dpi \
    xorg-x11-fonts-75dpi \
    xorg-x11-fonts-cyrillic \
    xorg-x11-fonts-misc \
    xorg-x11-fonts-Type1 \
    xorg-x11-utils \
    liberation-fonts

# 2. Chrome 다운로드 및 설치
cd /tmp
CHROME_RPM="google-chrome-stable_current_x86_64.rpm"

# 기존 파일 제거
rm -f $CHROME_RPM

echo "📥 Chrome 다운로드 중..."
wget https://dl.google.com/linux/direct/$CHROME_RPM

echo "📦 Chrome 설치 중..."
# 방법 1: dnf localinstall
if sudo dnf localinstall -y $CHROME_RPM 2>/dev/null; then
    echo "✅ Chrome 설치 완료 (dnf localinstall)"
# 방법 2: rpm --nodeps
elif sudo rpm -i --nodeps $CHROME_RPM 2>/dev/null; then
    echo "✅ Chrome 설치 완료 (rpm --nodeps)"
    sudo dnf install -y --skip-broken || true
# 방법 3: rpm --force
elif sudo rpm -ivh --force $CHROME_RPM 2>/dev/null; then
    echo "✅ Chrome 설치 완료 (rpm --force)"
else
    echo "❌ Chrome 설치 실패"
    echo "수동으로 시도해보세요:"
    echo "  sudo rpm -ivh --force $CHROME_RPM"
    exit 1
fi

# 정리
rm -f $CHROME_RPM

# 3. Chrome 경로 확인 및 설정
echo "🔍 Chrome 경로 확인..."
if command -v google-chrome &> /dev/null; then
    CHROME_PATH=$(which google-chrome)
    echo "✅ Chrome 경로: $CHROME_PATH"
elif [ -f /usr/bin/google-chrome ]; then
    echo "✅ Chrome 경로: /usr/bin/google-chrome"
    # PATH에 추가 (현재 세션)
    export PATH="/usr/bin:$PATH"
    # .bashrc에 추가 (영구)
    if ! grep -q "/usr/bin" ~/.bashrc 2>/dev/null; then
        echo 'export PATH="/usr/bin:$PATH"' >> ~/.bashrc
    fi
else
    echo "⚠️  Chrome을 찾을 수 없습니다"
    exit 1
fi

# 4. Chrome 버전 확인
echo "🔍 Chrome 버전 확인..."
if command -v google-chrome &> /dev/null; then
    google-chrome --version
elif [ -f /usr/bin/google-chrome ]; then
    /usr/bin/google-chrome --version
else
    echo "❌ Chrome 실행 실패"
    exit 1
fi

echo ""
echo "✅ Chrome 설치 완료!"
echo "다음 명령어로 테스트하세요:"
echo "  google-chrome --version"
echo "  또는"
echo "  /usr/bin/google-chrome --version"


