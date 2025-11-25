#!/bin/bash
# Amazon Linux 2023 배포 스크립트
# EC2 인스턴스에서 실행하세요

set -e

echo "🚀 네이버 부동산 크롤러 EC2 배포 시작..."

# 1. 시스템 업데이트 및 필수 패키지 설치
echo "📦 시스템 패키지 업데이트 중..."
sudo dnf update -y
sudo dnf install -y git python3 python3-pip python3-devel gcc gcc-c++ make wget curl unzip

# 2. Chrome 의존성 먼저 설치 (Chrome 설치 전 필수)
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

# 3. Chrome 설치 (Amazon Linux 2023)
echo "🌐 Chrome 설치 중..."
if ! command -v google-chrome &> /dev/null && ! command -v /usr/bin/google-chrome &> /dev/null; then
    cd /tmp
    CHROME_RPM="google-chrome-stable_current_x86_64.rpm"
    
    # 기존 파일 제거
    rm -f $CHROME_RPM
    
    # Chrome 다운로드
    echo "📥 Chrome 다운로드 중..."
    wget -q https://dl.google.com/linux/direct/$CHROME_RPM || {
        echo "❌ Chrome 다운로드 실패"
        exit 1
    }
    
    # Chrome 설치 시도 (여러 방법)
    echo "📦 Chrome 설치 중..."
    if sudo dnf localinstall -y $CHROME_RPM 2>/dev/null; then
        echo "✅ Chrome 설치 완료 (dnf localinstall)"
    elif sudo rpm -i --nodeps $CHROME_RPM 2>/dev/null; then
        echo "✅ Chrome 설치 완료 (rpm --nodeps)"
        # 의존성 해결
        sudo dnf install -y --skip-broken || true
    else
        echo "⚠️  기본 설치 실패, 수동 설치 시도..."
        sudo rpm -ivh --force $CHROME_RPM || {
            echo "❌ Chrome 설치 실패"
            echo "수동 설치를 시도하세요:"
            echo "  cd /tmp"
            echo "  wget https://dl.google.com/linux/direct/$CHROME_RPM"
            echo "  sudo rpm -ivh --force $CHROME_RPM"
            exit 1
        }
    fi
    
    rm -f $CHROME_RPM
    
    # Chrome 경로 확인
    if command -v google-chrome &> /dev/null; then
        echo "✅ Chrome 설치 확인: $(which google-chrome)"
    elif [ -f /usr/bin/google-chrome ]; then
        echo "✅ Chrome 설치 확인: /usr/bin/google-chrome"
        # 심볼릭 링크 생성 (필요시)
        if [ ! -f /usr/local/bin/google-chrome ]; then
            sudo ln -sf /usr/bin/google-chrome /usr/local/bin/google-chrome 2>/dev/null || true
        fi
    else
        echo "⚠️  Chrome 경로를 찾을 수 없습니다"
    fi
else
    CHROME_PATH=$(which google-chrome 2>/dev/null || echo "/usr/bin/google-chrome")
    echo "✅ Chrome이 이미 설치되어 있습니다: $CHROME_PATH"
fi

# Chrome 버전 확인
echo "🔍 Chrome 버전 확인..."
if command -v google-chrome &> /dev/null; then
    google-chrome --version || /usr/bin/google-chrome --version || echo "⚠️  Chrome 버전 확인 실패"
else
    /usr/bin/google-chrome --version 2>/dev/null || echo "⚠️  Chrome을 찾을 수 없습니다"
fi

# 4. 한글 폰트 설치 (선택사항)
echo "🔤 한글 폰트 설치 중..."
sudo dnf install -y google-noto-cjk-fonts || echo "⚠️  폰트 설치 실패 (선택사항)"

# 5. 프로젝트 디렉토리 확인
PROJECT_DIR="$HOME/naver_real_estate"
if [ ! -d "$PROJECT_DIR" ]; then
    echo "❌ 프로젝트 디렉토리를 찾을 수 없습니다: $PROJECT_DIR"
    echo "📝 GitHub에서 클론하거나 프로젝트를 배포하세요:"
    echo "   git clone <your-repo-url> $PROJECT_DIR"
    exit 1
fi

cd "$PROJECT_DIR"

# 6. Python 가상환경 생성
echo "🐍 Python 가상환경 생성 중..."
if [ ! -d "venv" ]; then
    python3 -m venv venv
fi
source venv/bin/activate

# 7. pip 업그레이드 및 패키지 설치
echo "📦 Python 패키지 설치 중..."
pip install --upgrade pip
pip install -r requirements.txt

# 8. Chrome 버전 확인
echo "🔍 Chrome 버전 확인..."
google-chrome --version || echo "⚠️  Chrome 실행 확인 필요"

# 9. systemd 서비스 파일 생성
echo "⚙️  systemd 서비스 설정 중..."
sudo tee /etc/systemd/system/naver-streamlit.service > /dev/null <<EOF
[Unit]
Description=Naver Real Estate Streamlit App
After=network.target

[Service]
Type=simple
User=$USER
WorkingDirectory=$PROJECT_DIR
Environment="PATH=$PROJECT_DIR/venv/bin"
ExecStart=$PROJECT_DIR/venv/bin/streamlit run app.py --server.headless true --server.address 0.0.0.0 --server.port 8501
Restart=always
RestartSec=10
StandardOutput=journal
StandardError=journal

[Install]
WantedBy=multi-user.target
EOF

# 10. 방화벽 설정 (필요시)
echo "🔥 방화벽 설정 확인 중..."
if command -v firewall-cmd &> /dev/null; then
    sudo firewall-cmd --permanent --add-port=8501/tcp
    sudo firewall-cmd --reload
    echo "✅ 방화벽 포트 8501 열림"
fi

# 11. systemd 서비스 활성화
echo "🔄 systemd 서비스 활성화 중..."
sudo systemctl daemon-reload
sudo systemctl enable naver-streamlit
sudo systemctl start naver-streamlit

# 12. 서비스 상태 확인
echo "📊 서비스 상태 확인 중..."
sleep 3
sudo systemctl status naver-streamlit --no-pager || true

echo ""
echo "✅ 배포 완료!"
echo ""
echo "📋 다음 명령어로 관리하세요:"
echo "   서비스 시작:   sudo systemctl start naver-streamlit"
echo "   서비스 중지:   sudo systemctl stop naver-streamlit"
echo "   서비스 재시작: sudo systemctl restart naver-streamlit"
echo "   로그 확인:     sudo journalctl -u naver-streamlit -f"
echo "   상태 확인:     sudo systemctl status naver-streamlit"
echo ""
echo "🌐 접속 주소: http://$(curl -s ifconfig.me):8501"
echo "   또는: http://$(hostname -I | awk '{print $1}'):8501"

