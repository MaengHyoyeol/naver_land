# Amazon Linux 2023 배포 가이드

이 가이드는 네이버 부동산 크롤러를 Amazon Linux 2023 EC2 인스턴스에 배포하는 방법을 설명합니다.

## 📋 사전 준비

### 1. EC2 인스턴스 생성
- **AMI**: Amazon Linux 2023
- **인스턴스 타입**: 최소 `t3.medium` (2 vCPU, 4GB RAM) 권장
  - Chrome + Selenium + Streamlit 동시 실행을 위해 충분한 메모리 필요
  - 권장: `t3.large` (2 vCPU, 8GB RAM) 이상
- **스토리지**: 최소 30GB (Chrome 캐시 및 데이터 저장용)
- **보안 그룹**: 
  - SSH (22/tcp) - 본인 IP만 허용
  - Streamlit (8501/tcp) - 접근할 IP만 허용 (또는 0.0.0.0/0)

### 2. Elastic IP 할당 (선택사항)
- EC2 콘솔에서 Elastic IP 생성 및 인스턴스에 연결
- IP 주소가 변경되지 않도록 고정

## 🚀 배포 방법

### 방법 1: 자동 배포 스크립트 사용 (권장)

#### 1-1. 프로젝트를 EC2에 배포

**옵션 A: GitHub에서 클론**
```bash
# EC2에 SSH 접속
ssh -i your-key.pem ec2-user@your-ec2-ip

# 프로젝트 클론
cd ~
git clone https://github.com/your-username/naver_real_estate.git
cd naver_real_estate
```

**옵션 B: 로컬에서 직접 업로드**
```bash
# 로컬에서 실행
cd /Users/maenghyoyeol/cursor/naver_real_estate
tar czf naver_real_estate.tar.gz --exclude='venv' --exclude='data' --exclude='__pycache__' .
scp -i your-key.pem naver_real_estate.tar.gz ec2-user@your-ec2-ip:~/

# EC2에서 실행
ssh -i your-key.pem ec2-user@your-ec2-ip
cd ~
tar xzf naver_real_estate.tar.gz -C naver_real_estate
cd naver_real_estate
```

#### 1-2. 배포 스크립트 실행
```bash
# EC2에서 실행
chmod +x deploy_ec2.sh
./deploy_ec2.sh
```

스크립트가 자동으로:
- 시스템 패키지 업데이트
- Chrome 및 의존성 설치
- Python 가상환경 생성
- 패키지 설치
- systemd 서비스 설정 및 시작

### 방법 2: 수동 배포

#### 2-1. 시스템 패키지 설치
```bash
sudo dnf update -y
sudo dnf install -y git python3 python3-pip python3-devel gcc gcc-c++ make wget curl unzip
```

#### 2-2. Chrome 설치
```bash
cd /tmp
wget https://dl.google.com/linux/direct/google-chrome-stable_current_x86_64.rpm
sudo dnf localinstall -y google-chrome-stable_current_x86_64.rpm
rm google-chrome-stable_current_x86_64.rpm
```

#### 2-3. Chrome 의존성 설치
```bash
sudo dnf install -y \
    alsa-lib atk cups-libs gtk3 ipa-gothic-fonts \
    libXcomposite libXcursor libXdamage libXext libXi \
    libXrandr libXScrnSaver libXtst pango \
    xorg-x11-fonts-100dpi xorg-x11-fonts-75dpi \
    xorg-x11-fonts-cyrillic xorg-x11-fonts-misc \
    xorg-x11-fonts-Type1 xorg-x11-utils
```

#### 2-4. 프로젝트 설정
```bash
cd ~/naver_real_estate
python3 -m venv venv
source venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt
```

#### 2-5. systemd 서비스 생성
```bash
sudo nano /etc/systemd/system/naver-streamlit.service
```

다음 내용 입력:
```ini
[Unit]
Description=Naver Real Estate Streamlit App
After=network.target

[Service]
Type=simple
User=ec2-user
WorkingDirectory=/home/ec2-user/naver_real_estate
Environment="PATH=/home/ec2-user/naver_real_estate/venv/bin"
ExecStart=/home/ec2-user/naver_real_estate/venv/bin/streamlit run app.py --server.headless true --server.address 0.0.0.0 --server.port 8501
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

#### 2-6. 서비스 시작
```bash
sudo systemctl daemon-reload
sudo systemctl enable naver-streamlit
sudo systemctl start naver-streamlit
sudo systemctl status naver-streamlit
```

## 🔧 관리 명령어

### 서비스 제어
```bash
# 시작
sudo systemctl start naver-streamlit

# 중지
sudo systemctl stop naver-streamlit

# 재시작
sudo systemctl restart naver-streamlit

# 상태 확인
sudo systemctl status naver-streamlit

# 자동 시작 활성화/비활성화
sudo systemctl enable naver-streamlit
sudo systemctl disable naver-streamlit
```

### 로그 확인
```bash
# 실시간 로그
sudo journalctl -u naver-streamlit -f

# 최근 로그 (100줄)
sudo journalctl -u naver-streamlit -n 100

# 오늘 로그
sudo journalctl -u naver-streamlit --since today
```

## 🌐 접속 확인

### 내부 IP로 접속
```bash
# EC2 내부 IP 확인
hostname -I

# 브라우저에서 접속
http://<내부-IP>:8501
```

### 공인 IP로 접속
```bash
# 공인 IP 확인
curl ifconfig.me

# 브라우저에서 접속
http://<공인-IP>:8501
```

## 🔄 업데이트 방법

### 코드 업데이트 (Git 사용 시)
```bash
cd ~/naver_real_estate
git pull
source venv/bin/activate
pip install -r requirements.txt
sudo systemctl restart naver-streamlit
```

### 수동 업데이트
```bash
# 새 파일 업로드 후
cd ~/naver_real_estate
source venv/bin/activate
pip install -r requirements.txt
sudo systemctl restart naver-streamlit
```

## 🐛 문제 해결

### 1. Chrome이 실행되지 않음
```bash
# Chrome 버전 확인
google-chrome --version

# 의존성 재설치
sudo dnf install -y alsa-lib atk cups-libs gtk3 libXcomposite libXcursor libXdamage libXext libXi libXrandr libXScrnSaver libXtst pango
```

### 2. 포트가 열리지 않음
```bash
# 방화벽 확인 (firewalld 사용 시)
sudo firewall-cmd --list-ports
sudo firewall-cmd --permanent --add-port=8501/tcp
sudo firewall-cmd --reload

# 보안 그룹 확인 (AWS 콘솔)
# EC2 > 보안 그룹 > 인바운드 규칙에 8501/tcp 추가
```

### 3. 서비스가 시작되지 않음
```bash
# 로그 확인
sudo journalctl -u naver-streamlit -n 50

# 수동 실행 테스트
cd ~/naver_real_estate
source venv/bin/activate
streamlit run app.py --server.headless true --server.address 0.0.0.0 --server.port 8501
```

### 4. 메모리 부족
```bash
# 메모리 사용량 확인
free -h
ps aux | grep streamlit
ps aux | grep chrome

# 인스턴스 타입 업그레이드 고려 (t3.medium -> t3.large)
```

### 5. Python 패키지 설치 실패
```bash
# 컴파일러 재설치
sudo dnf install -y python3-devel gcc gcc-c++ make

# 가상환경 재생성
cd ~/naver_real_estate
rm -rf venv
python3 -m venv venv
source venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt
```

## 📝 주의사항

1. **headless 모드 필수**: EC2는 GUI가 없으므로 반드시 `headless=True`로 실행
2. **메모리 관리**: Chrome + Selenium은 메모리를 많이 사용하므로 인스턴스 타입 선택 주의
3. **보안**: 프로덕션 환경에서는 Nginx reverse proxy + HTTPS 사용 권장
4. **백업**: 정기적으로 데이터 백업 (`data/` 디렉토리)
5. **비용**: EC2 인스턴스는 사용 시간에 따라 과금되므로 사용하지 않을 때는 중지

## 🔒 보안 강화 (선택사항)

### Nginx Reverse Proxy 설정
```bash
# Nginx 설치
sudo dnf install -y nginx

# 설정 파일 생성
sudo nano /etc/nginx/conf.d/streamlit.conf
```

```nginx
server {
    listen 80;
    server_name your-domain.com;

    location / {
        proxy_pass http://127.0.0.1:8501;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_read_timeout 86400;
    }
}
```

```bash
sudo systemctl enable nginx
sudo systemctl start nginx
```

### SSL 인증서 (Let's Encrypt)
```bash
sudo dnf install -y certbot python3-certbot-nginx
sudo certbot --nginx -d your-domain.com
```

## 📞 지원

문제가 발생하면 다음을 확인하세요:
1. `sudo journalctl -u naver-streamlit -n 100` - 서비스 로그
2. `sudo systemctl status naver-streamlit` - 서비스 상태
3. `google-chrome --version` - Chrome 설치 확인
4. AWS 콘솔의 보안 그룹 설정







