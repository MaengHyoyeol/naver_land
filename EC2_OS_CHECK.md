# EC2 OS 확인 및 패키지 매니저 가이드

## OS 확인 방법

EC2에 SSH 접속 후 다음 명령어로 OS를 확인하세요:

```bash
# OS 확인
cat /etc/os-release

# 또는
hostnamectl
```

## 패키지 매니저별 명령어

### Amazon Linux 2023 (dnf 사용)
```bash
# 패키지 업데이트
sudo dnf update -y

# 패키지 설치
sudo dnf install -y <패키지명>

# 예시
sudo dnf install -y git python3 python3-pip
```

### Amazon Linux 2 (yum 사용)
```bash
# 패키지 업데이트
sudo yum update -y

# 패키지 설치
sudo yum install -y <패키지명>

# 예시
sudo yum install -y git python3 python3-pip
```

### Ubuntu/Debian (apt 사용)
```bash
# 패키지 업데이트
sudo apt update && sudo apt upgrade -y

# 패키지 설치
sudo apt install -y <패키지명>

# 예시
sudo apt install -y git python3 python3-pip
```

## 빠른 해결 방법

### 방법 1: 자동 배포 스크립트 사용 (권장)
```bash
cd ~/naver_real_estate
chmod +x deploy_ec2.sh
./deploy_ec2.sh
```

이 스크립트는 Amazon Linux 2023용으로 작성되어 있으며, 자동으로 OS를 감지하고 적절한 패키지 매니저를 사용합니다.

### 방법 2: 수동 설치 (OS별)

**Amazon Linux 2023인 경우:**
```bash
sudo dnf update -y
sudo dnf install -y git python3 python3-pip python3-devel gcc gcc-c++ make wget curl unzip
```

**Amazon Linux 2인 경우:**
```bash
sudo yum update -y
sudo yum install -y git python3 python3-pip python3-devel gcc gcc-c++ make wget curl unzip
```

**Ubuntu인 경우:**
```bash
sudo apt update && sudo apt upgrade -y
sudo apt install -y git python3 python3-pip python3-dev build-essential wget curl unzip
```

## 현재 프로젝트의 배포 스크립트

`deploy_ec2.sh`는 **Amazon Linux 2023**용으로 작성되어 있습니다.
- `dnf` 사용
- Chrome 설치 포함
- systemd 서비스 설정 포함

Ubuntu를 사용하는 경우, `deploy_ec2.sh`를 수정하거나 Ubuntu용 스크립트를 별도로 만들어야 합니다.

