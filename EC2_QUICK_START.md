# EC2 빠른 시작 가이드

EC2에서 네이버 부동산 크롤러를 실행하는 방법입니다.

## 🚀 빠른 실행 (3단계)

### 1단계: 프로젝트를 EC2에 배포

**옵션 A: GitHub에서 클론 (권장)**
```bash
# EC2에 SSH 접속
ssh -i your-key.pem ec2-user@your-ec2-ip

# 프로젝트 클론
cd ~
git clone https://github.com/your-username/naver_real_estate.git
cd naver_real_estate
```

**옵션 B: 로컬에서 업로드**
```bash
# 로컬에서 실행
cd /Users/maenghyoyeol/cursor/naver_real_estate
tar czf naver_real_estate.tar.gz --exclude='venv' --exclude='data' --exclude='__pycache__' --exclude='*.csv' --exclude='*.xlsx' .
scp -i your-key.pem naver_real_estate.tar.gz ec2-user@your-ec2-ip:~/

# EC2에서 실행
ssh -i your-key.pem ec2-user@your-ec2-ip
cd ~
mkdir -p naver_real_estate
tar xzf naver_real_estate.tar.gz -C naver_real_estate
cd naver_real_estate
```

### 2단계: 자동 배포 스크립트 실행
```bash
cd ~/naver_real_estate
chmod +x deploy_ec2.sh
./deploy_ec2.sh
```

이 스크립트가 자동으로:
- ✅ 시스템 패키지 설치
- ✅ Chrome 설치
- ✅ Python 가상환경 생성
- ✅ 패키지 설치
- ✅ systemd 서비스 설정 및 시작

### 3단계: 접속 확인
```bash
# 공인 IP 확인
curl ifconfig.me

# 브라우저에서 접속
http://<공인-IP>:8501
```

## 📋 실행 방법

### 방법 1: systemd 서비스 (자동 실행, 권장)

배포 스크립트가 자동으로 설정합니다.

```bash
# 서비스 시작
sudo systemctl start naver-streamlit

# 서비스 중지
sudo systemctl stop naver-streamlit

# 서비스 재시작
sudo systemctl restart naver-streamlit

# 서비스 상태 확인
sudo systemctl status naver-streamlit

# 자동 시작 활성화 (재부팅 시 자동 실행)
sudo systemctl enable naver-streamlit

# 로그 확인
sudo journalctl -u naver-streamlit -f
```

### 방법 2: 수동 실행 (테스트용)

```bash
cd ~/naver_real_estate
source venv/bin/activate
streamlit run app.py --server.headless true --server.address 0.0.0.0 --server.port 8501
```

**백그라운드 실행 (SSH 종료 후에도 유지)**
```bash
cd ~/naver_real_estate
source venv/bin/activate
nohup streamlit run app.py --server.headless true --server.address 0.0.0.0 --server.port 8501 > streamlit.log 2>&1 &

# 프로세스 확인
ps aux | grep streamlit

# 종료
pkill -f streamlit
```

### 방법 3: tmux 사용 (권장 - SSH 종료 후에도 유지)

```bash
# tmux 설치 (없는 경우)
sudo dnf install -y tmux

# tmux 세션 시작
tmux new -s streamlit

# 가상환경 활성화 및 실행
cd ~/naver_real_estate
source venv/bin/activate
streamlit run app.py --server.headless true --server.address 0.0.0.0 --server.port 8501

# 세션에서 나가기 (Ctrl+B, D)
# 세션 다시 접속
tmux attach -t streamlit

# 세션 종료
tmux kill-session -t streamlit
```

## 🔧 문제 해결

### 1. 포트가 열리지 않음

**보안 그룹 확인 (AWS 콘솔)**
- EC2 > 보안 그룹 > 인바운드 규칙
- 포트 8501/tcp 추가 (소스: 0.0.0.0/0 또는 특정 IP)

**방화벽 확인 (EC2에서)**
```bash
# firewalld 사용 시
sudo firewall-cmd --list-ports
sudo firewall-cmd --permanent --add-port=8501/tcp
sudo firewall-cmd --reload
```

### 2. 서비스가 시작되지 않음

```bash
# 로그 확인
sudo journalctl -u naver-streamlit -n 50

# 수동 실행 테스트
cd ~/naver_real_estate
source venv/bin/activate
streamlit run app.py --server.headless true --server.address 0.0.0.0 --server.port 8501
```

### 3. Chrome이 없음

```bash
# Chrome 설치 스크립트 실행
cd ~/naver_real_estate
chmod +x install_chrome.sh
./install_chrome.sh
```

### 4. Streamlit이 없음

```bash
# 가상환경 활성화
cd ~/naver_real_estate
source venv/bin/activate

# Streamlit 설치 확인
streamlit --version

# Streamlit이 없으면 설치
pip install streamlit==1.28.0

# 또는 requirements.txt 전체 재설치
pip install -r requirements.txt
```

### 5. 메모리 부족

```bash
# 메모리 확인
free -h

# 프로세스 확인
ps aux | grep -E 'streamlit|chrome'

# 인스턴스 타입 업그레이드 고려 (t3.medium -> t3.large)
```

## 📝 일상적인 사용

### 코드 업데이트 후 재시작
```bash
cd ~/naver_real_estate
git pull  # 또는 새 파일 업로드
source venv/bin/activate
pip install -r requirements.txt
sudo systemctl restart naver-streamlit
```

### 로그 모니터링
```bash
# 실시간 로그
sudo journalctl -u naver-streamlit -f

# 최근 100줄
sudo journalctl -u naver-streamlit -n 100

# 오늘 로그
sudo journalctl -u naver-streamlit --since today
```

### 서비스 중지/시작
```bash
# 중지
sudo systemctl stop naver-streamlit

# 시작
sudo systemctl start naver-streamlit

# 상태 확인
sudo systemctl status naver-streamlit
```

## 🌐 접속 주소

### 내부 IP
```bash
hostname -I
# http://<내부-IP>:8501
```

### 공인 IP
```bash
curl ifconfig.me
# http://<공인-IP>:8501
```

### Elastic IP 사용 시
- EC2 콘솔에서 Elastic IP 확인
- `http://<Elastic-IP>:8501`

## ✅ 체크리스트

배포 전 확인:
- [ ] EC2 인스턴스 생성 (최소 t3.medium 권장)
- [ ] 보안 그룹에 8501/tcp 포트 추가
- [ ] SSH 키로 접속 가능
- [ ] 프로젝트 파일 업로드/클론 완료

배포 후 확인:
- [ ] `sudo systemctl status naver-streamlit` - 서비스 실행 중
- [ ] `curl http://localhost:8501` - 로컬 접속 가능
- [ ] 브라우저에서 공인 IP로 접속 가능
- [ ] 크롤링 기능 정상 작동

## 💡 팁

1. **Elastic IP 사용**: IP 주소가 변경되지 않도록 고정
2. **Nginx Reverse Proxy**: 프로덕션 환경에서는 Nginx 사용 권장
3. **SSL 인증서**: Let's Encrypt로 HTTPS 설정 가능
4. **모니터링**: CloudWatch로 리소스 모니터링
5. **백업**: 정기적으로 `data/` 디렉토리 백업

## 📞 빠른 참조

```bash
# 서비스 관리
sudo systemctl start/stop/restart/status naver-streamlit

# 로그 확인
sudo journalctl -u naver-streamlit -f

# 수동 실행
cd ~/naver_real_estate && source venv/bin/activate && streamlit run app.py --server.headless true --server.address 0.0.0.0 --server.port 8501

# Chrome 확인
google-chrome --version

# 포트 확인
sudo netstat -tlnp | grep 8501
```

