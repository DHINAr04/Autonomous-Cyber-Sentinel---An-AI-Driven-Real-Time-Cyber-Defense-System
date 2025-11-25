# 🚀 Deployment Guide - Autonomous Cyber Sentinel

## Complete Guide for Local and Production Deployment

---

## 📋 **Table of Contents**

1. [Local Development](#local-development)
2. [Production Deployment](#production-deployment)
3. [Docker Deployment](#docker-deployment)
4. [Cloud Deployment](#cloud-deployment)
5. [Monitoring & Maintenance](#monitoring--maintenance)

---

## 🏠 **Local Development**

### **Quick Start (Windows)**

#### **Option 1: Using Batch File (Easiest)**
```powershell
.\start_server.bat
```

#### **Option 2: Manual Start**
```powershell
# Activate virtual environment
.\.venv\Scripts\Activate.ps1

# Start server
python -m uvicorn sentinel.dashboard.app:app --host 0.0.0.0 --port 8001 --reload
```

#### **Option 3: Using Dev Script**
```powershell
.\scripts\dev.ps1 run
```

### **Access Dashboard**
```
http://localhost:8001
```

### **Stop Server**
Press `Ctrl+C` in the terminal

---

## 🐳 **Docker Deployment**

### **Option 1: Docker Compose (Recommended)**

#### **Start All Services**
```powershell
docker-compose up -d
```

#### **View Logs**
```powershell
docker-compose logs -f sentinel
```

#### **Stop Services**
```powershell
docker-compose down
```

#### **Rebuild After Changes**
```powershell
docker-compose up --build -d
```

### **Option 2: Docker Only**

#### **Build Image**
```powershell
docker build -t sentinel:latest .
```

#### **Run Container**
```powershell
docker run -d `
  --name sentinel `
  -p 8001:8000 `
  -v ${PWD}/data:/app/data `
  -v ${PWD}/reports:/app/reports `
  -e BUS=memory `
  -e OFFLINE_MODE=1 `
  sentinel:latest
```

#### **View Logs**
```powershell
docker logs -f sentinel
```

#### **Stop Container**
```powershell
docker stop sentinel
docker rm sentinel
```

---

## ☁️ **Production Deployment**

### **Prerequisites**

1. **Server Requirements**
   - Ubuntu 20.04+ or Windows Server 2019+
   - 2+ CPU cores
   - 4GB+ RAM
   - 20GB+ disk space
   - Python 3.10+
   - Docker (optional)

2. **Domain & SSL**
   - Domain name (e.g., sentinel.yourcompany.com)
   - SSL certificate (Let's Encrypt recommended)

3. **Firewall**
   - Open port 80 (HTTP)
   - Open port 443 (HTTPS)
   - Open port 8001 (or your chosen port)

### **Step 1: Server Setup**

#### **Ubuntu/Linux**
```bash
# Update system
sudo apt update && sudo apt upgrade -y

# Install Python 3.10+
sudo apt install python3.10 python3.10-venv python3-pip -y

# Install system dependencies
sudo apt install libpcap-dev gcc -y

# Install Docker (optional)
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh
sudo usermod -aG docker $USER
```

#### **Windows Server**
```powershell
# Install Python 3.10+
# Download from: https://www.python.org/downloads/

# Install Docker Desktop
# Download from: https://www.docker.com/products/docker-desktop/
```

### **Step 2: Deploy Application**

#### **Clone/Upload Project**
```bash
# Clone from Git
git clone https://github.com/yourusername/sentinel.git
cd sentinel

# Or upload via SCP/FTP
scp -r ./sentinel user@server:/opt/sentinel
```

#### **Setup Environment**
```bash
# Create virtual environment
python3 -m venv .venv

# Activate
source .venv/bin/activate  # Linux
# or
.\.venv\Scripts\Activate.ps1  # Windows

# Install dependencies
pip install -r requirements.txt
```

#### **Configure Environment**
```bash
# Copy example config
cp .env.example .env

# Edit configuration
nano .env
```

**Production .env:**
```env
# Production Settings
BUS=redis
REDIS_URL=redis://localhost:6379/0
SENTINEL_DB=postgresql://user:pass@localhost/sentinel
LIVE_CAPTURE=1
CAPTURE_IFACE=eth0

# API Keys (Optional)
VT_API_KEY=your_virustotal_key
ABUSEIPDB_API_KEY=your_abuseipdb_key
OTX_API_KEY=your_otx_key

# Security
SECRET_KEY=your-secret-key-here
ALLOWED_HOSTS=sentinel.yourcompany.com

# Email Notifications
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USER=alerts@yourcompany.com
SMTP_PASSWORD=your-app-password
ALERT_EMAIL=security-team@yourcompany.com
```

### **Step 3: Setup Reverse Proxy (Nginx)**

#### **Install Nginx**
```bash
sudo apt install nginx -y
```

#### **Configure Nginx**
```bash
sudo nano /etc/nginx/sites-available/sentinel
```

**Nginx Configuration:**
```nginx
server {
    listen 80;
    server_name sentinel.yourcompany.com;
    
    # Redirect to HTTPS
    return 301 https://$server_name$request_uri;
}

server {
    listen 443 ssl http2;
    server_name sentinel.yourcompany.com;
    
    # SSL Configuration
    ssl_certificate /etc/letsencrypt/live/sentinel.yourcompany.com/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/sentinel.yourcompany.com/privkey.pem;
    
    # Security Headers
    add_header X-Frame-Options "SAMEORIGIN" always;
    add_header X-Content-Type-Options "nosniff" always;
    add_header X-XSS-Protection "1; mode=block" always;
    
    # Proxy to Sentinel
    location / {
        proxy_pass http://localhost:8001;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        
        # WebSocket support
        proxy_read_timeout 86400;
    }
    
    # Static files
    location /static/ {
        alias /opt/sentinel/sentinel/dashboard/static/;
        expires 30d;
        add_header Cache-Control "public, immutable";
    }
}
```

#### **Enable Site**
```bash
sudo ln -s /etc/nginx/sites-available/sentinel /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl restart nginx
```

### **Step 4: SSL Certificate (Let's Encrypt)**

```bash
# Install Certbot
sudo apt install certbot python3-certbot-nginx -y

# Get certificate
sudo certbot --nginx -d sentinel.yourcompany.com

# Auto-renewal (already configured)
sudo certbot renew --dry-run
```

### **Step 5: Setup Systemd Service**

```bash
sudo nano /etc/systemd/system/sentinel.service
```

**Service Configuration:**
```ini
[Unit]
Description=Autonomous Cyber Sentinel
After=network.target redis.service

[Service]
Type=simple
User=sentinel
Group=sentinel
WorkingDirectory=/opt/sentinel
Environment="PATH=/opt/sentinel/.venv/bin"
ExecStart=/opt/sentinel/.venv/bin/uvicorn sentinel.dashboard.app:app --host 127.0.0.1 --port 8001 --workers 4
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

#### **Enable and Start Service**
```bash
# Create user
sudo useradd -r -s /bin/false sentinel
sudo chown -R sentinel:sentinel /opt/sentinel

# Enable service
sudo systemctl daemon-reload
sudo systemctl enable sentinel
sudo systemctl start sentinel

# Check status
sudo systemctl status sentinel
```

---

## 🔧 **Database Setup (Production)**

### **PostgreSQL (Recommended for Production)**

#### **Install PostgreSQL**
```bash
sudo apt install postgresql postgresql-contrib -y
```

#### **Create Database**
```bash
sudo -u postgres psql

CREATE DATABASE sentinel;
CREATE USER sentinel_user WITH PASSWORD 'your_secure_password';
GRANT ALL PRIVILEGES ON DATABASE sentinel TO sentinel_user;
\q
```

#### **Update Connection String**
```env
SENTINEL_DB=postgresql://sentinel_user:your_secure_password@localhost/sentinel
```

#### **Install PostgreSQL Driver**
```bash
pip install psycopg2-binary
```

---

## 📊 **Monitoring & Maintenance**

### **Setup Prometheus Monitoring**

#### **Install Prometheus**
```bash
# Download Prometheus
wget https://github.com/prometheus/prometheus/releases/download/v2.45.0/prometheus-2.45.0.linux-amd64.tar.gz
tar xvfz prometheus-*.tar.gz
cd prometheus-*
```

#### **Configure Prometheus**
```yaml
# prometheus.yml
global:
  scrape_interval: 15s

scrape_configs:
  - job_name: 'sentinel'
    static_configs:
      - targets: ['localhost:8001']
    metrics_path: '/metrics'
```

#### **Start Prometheus**
```bash
./prometheus --config.file=prometheus.yml
```

### **Setup Grafana Dashboard**

#### **Install Grafana**
```bash
sudo apt-get install -y software-properties-common
sudo add-apt-repository "deb https://packages.grafana.com/oss/deb stable main"
wget -q -O - https://packages.grafana.com/gpg.key | sudo apt-key add -
sudo apt-get update
sudo apt-get install grafana -y
sudo systemctl start grafana-server
sudo systemctl enable grafana-server
```

#### **Access Grafana**
```
http://your-server:3000
Default: admin/admin
```

### **Log Management**

#### **Configure Logging**
```bash
# Create log directory
sudo mkdir -p /var/log/sentinel
sudo chown sentinel:sentinel /var/log/sentinel
```

#### **Logrotate Configuration**
```bash
sudo nano /etc/logrotate.d/sentinel
```

```
/var/log/sentinel/*.log {
    daily
    rotate 14
    compress
    delaycompress
    notifempty
    create 0640 sentinel sentinel
    sharedscripts
    postrotate
        systemctl reload sentinel
    endscript
}
```

---

## 🔒 **Security Hardening**

### **Firewall (UFW)**
```bash
# Enable firewall
sudo ufw enable

# Allow SSH
sudo ufw allow 22/tcp

# Allow HTTP/HTTPS
sudo ufw allow 80/tcp
sudo ufw allow 443/tcp

# Check status
sudo ufw status
```

### **Fail2Ban**
```bash
# Install
sudo apt install fail2ban -y

# Configure
sudo nano /etc/fail2ban/jail.local
```

```ini
[DEFAULT]
bantime = 3600
findtime = 600
maxretry = 5

[nginx-http-auth]
enabled = true
```

### **Regular Updates**
```bash
# Create update script
sudo nano /opt/sentinel/update.sh
```

```bash
#!/bin/bash
cd /opt/sentinel
git pull
source .venv/bin/activate
pip install -r requirements.txt --upgrade
sudo systemctl restart sentinel
```

```bash
chmod +x /opt/sentinel/update.sh
```

---

## 📦 **Backup Strategy**

### **Database Backup**
```bash
# Create backup script
sudo nano /opt/sentinel/backup.sh
```

```bash
#!/bin/bash
BACKUP_DIR="/opt/sentinel/backups"
DATE=$(date +%Y%m%d_%H%M%S)

# Create backup directory
mkdir -p $BACKUP_DIR

# Backup database
pg_dump sentinel > $BACKUP_DIR/sentinel_$DATE.sql

# Backup reports
tar -czf $BACKUP_DIR/reports_$DATE.tar.gz /opt/sentinel/reports

# Keep only last 30 days
find $BACKUP_DIR -name "*.sql" -mtime +30 -delete
find $BACKUP_DIR -name "*.tar.gz" -mtime +30 -delete
```

```bash
chmod +x /opt/sentinel/backup.sh
```

### **Schedule Backups (Cron)**
```bash
crontab -e
```

```cron
# Daily backup at 2 AM
0 2 * * * /opt/sentinel/backup.sh

# Weekly report at 9 AM Monday
0 9 * * 1 curl http://localhost:8001/report/generate
```

---

## 🌐 **Cloud Deployment**

### **AWS Deployment**

#### **EC2 Instance**
1. Launch EC2 instance (t3.medium or larger)
2. Security Group: Allow ports 80, 443, 22
3. Elastic IP for static address
4. Follow Ubuntu deployment steps above

#### **Using ECS (Docker)**
```yaml
# task-definition.json
{
  "family": "sentinel",
  "containerDefinitions": [{
    "name": "sentinel",
    "image": "your-registry/sentinel:latest",
    "memory": 2048,
    "cpu": 1024,
    "essential": true,
    "portMappings": [{
      "containerPort": 8000,
      "protocol": "tcp"
    }],
    "environment": [
      {"name": "BUS", "value": "redis"},
      {"name": "REDIS_URL", "value": "redis://redis:6379/0"}
    ]
  }]
}
```

### **Azure Deployment**

#### **App Service**
```bash
# Login
az login

# Create resource group
az group create --name sentinel-rg --location eastus

# Create App Service plan
az appservice plan create --name sentinel-plan --resource-group sentinel-rg --sku B2 --is-linux

# Deploy
az webapp up --name sentinel-app --resource-group sentinel-rg --runtime "PYTHON:3.10"
```

### **Google Cloud Deployment**

#### **Cloud Run**
```bash
# Build and push
gcloud builds submit --tag gcr.io/PROJECT_ID/sentinel

# Deploy
gcloud run deploy sentinel \
  --image gcr.io/PROJECT_ID/sentinel \
  --platform managed \
  --region us-central1 \
  --allow-unauthenticated
```

---

## ✅ **Deployment Checklist**

### **Pre-Deployment**
- [ ] All tests passing
- [ ] Environment variables configured
- [ ] SSL certificate obtained
- [ ] Database setup complete
- [ ] Backup strategy in place

### **Deployment**
- [ ] Application deployed
- [ ] Nginx configured
- [ ] Systemd service running
- [ ] Firewall configured
- [ ] Monitoring setup

### **Post-Deployment**
- [ ] Dashboard accessible
- [ ] WebSocket working
- [ ] Reports generating
- [ ] Logs rotating
- [ ] Backups running
- [ ] Monitoring active

---

## 🆘 **Troubleshooting**

### **Service Won't Start**
```bash
# Check logs
sudo journalctl -u sentinel -n 50

# Check permissions
ls -la /opt/sentinel

# Test manually
cd /opt/sentinel
source .venv/bin/activate
python -m uvicorn sentinel.dashboard.app:app --host 127.0.0.1 --port 8001
```

### **Database Connection Issues**
```bash
# Test connection
psql -h localhost -U sentinel_user -d sentinel

# Check PostgreSQL status
sudo systemctl status postgresql
```

### **Nginx Issues**
```bash
# Test configuration
sudo nginx -t

# Check logs
sudo tail -f /var/log/nginx/error.log
```

---

## 📞 **Support**

For deployment issues:
1. Check logs: `sudo journalctl -u sentinel`
2. Review documentation
3. Check GitHub issues
4. Contact support team

---

**Your Autonomous Cyber Sentinel is ready for production deployment!** 🚀🛡️
