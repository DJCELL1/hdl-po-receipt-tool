# HDL PO Receipt Tool - Setup Instructions

Complete guide for setting up and deploying the HDL PO Receipt Tool.

## Table of Contents

1. [System Requirements](#system-requirements)
2. [Local Development Setup](#local-development-setup)
3. [Docker Deployment](#docker-deployment)
4. [Cin7 API Setup](#cin7-api-setup)
5. [Database Setup](#database-setup)
6. [Testing](#testing)
7. [Production Deployment](#production-deployment)

---

## System Requirements

### Minimum Requirements

- **OS**: Linux (Ubuntu 20.04+), macOS 11+, or Windows 10+
- **Python**: 3.9 or higher
- **RAM**: 2GB minimum, 4GB recommended
- **Disk**: 5GB free space
- **Database**: PostgreSQL 12+

### For Docker Deployment

- **Docker**: 20.10+
- **Docker Compose**: 1.29+

---

## Local Development Setup

### Step 1: Install System Dependencies

#### Ubuntu/Debian

```bash
# Update package list
sudo apt-get update

# Install Tesseract OCR
sudo apt-get install -y tesseract-ocr tesseract-ocr-eng

# Install OpenCV dependencies
sudo apt-get install -y libgl1-mesa-glx libglib2.0-0

# Install PostgreSQL
sudo apt-get install -y postgresql postgresql-contrib

# Start PostgreSQL
sudo systemctl start postgresql
sudo systemctl enable postgresql
```

#### macOS

```bash
# Install Homebrew (if not installed)
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"

# Install dependencies
brew install tesseract
brew install opencv
brew install postgresql

# Start PostgreSQL
brew services start postgresql
```

#### Windows

1. **Install Tesseract OCR**
   - Download: https://github.com/UB-Mannheim/tesseract/wiki
   - Install to: `C:\Program Files\Tesseract-OCR`
   - Add to PATH or note installation path

2. **Install PostgreSQL**
   - Download: https://www.postgresql.org/download/windows/
   - Run installer and remember your password

3. **Install Python**
   - Download: https://www.python.org/downloads/
   - Check "Add Python to PATH" during installation

### Step 2: Clone Repository

```bash
git clone <repository-url>
cd Receipt
```

### Step 3: Create Virtual Environment

```bash
# Create virtual environment
python -m venv venv

# Activate (Linux/Mac)
source venv/bin/activate

# Activate (Windows)
venv\Scripts\activate
```

### Step 4: Install Python Dependencies

```bash
pip install --upgrade pip
pip install -r requirements.txt
```

### Step 5: Configure Environment

```bash
# Copy example env file
cp .env.example .env

# Edit .env with your settings
nano .env  # or use your preferred editor
```

**Required Configuration:**

```bash
# Database
DATABASE_URL=postgresql://hdl_user:your_password@localhost:5432/hdl_receipts

# Cin7 API (get from Cin7 portal)
CIN7_API_KEY=your_api_key_here
CIN7_API_SECRET=your_api_secret_here

# Tesseract path (adjust for your system)
# Linux: /usr/bin/tesseract
# Mac: /usr/local/bin/tesseract
# Windows: C:\Program Files\Tesseract-OCR\tesseract.exe
TESSERACT_CMD=/usr/bin/tesseract
```

### Step 6: Set Up Database

```bash
# Create PostgreSQL user and database
sudo -u postgres psql

# In psql:
CREATE USER hdl_user WITH PASSWORD 'your_password';
CREATE DATABASE hdl_receipts OWNER hdl_user;
GRANT ALL PRIVILEGES ON DATABASE hdl_receipts TO hdl_user;
\q

# Run migration
python database/migrate.py
```

### Step 7: Verify Installation

```bash
# Test Tesseract
tesseract --version

# Test database connection
python -c "from database.db import engine; print('DB Connected:', engine.connect())"

# Test imports
python -c "import cv2, pytesseract, streamlit; print('All imports successful')"
```

### Step 8: Run Application

```bash
streamlit run app.py
```

Access at: http://localhost:8501

---

## Docker Deployment

### Step 1: Install Docker

#### Ubuntu

```bash
# Install Docker
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh

# Install Docker Compose
sudo curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
sudo chmod +x /usr/local/bin/docker-compose

# Add user to docker group
sudo usermod -aG docker $USER
newgrp docker
```

#### macOS

```bash
# Install Docker Desktop
brew install --cask docker
```

#### Windows

Download and install Docker Desktop: https://www.docker.com/products/docker-desktop

### Step 2: Configure Environment

```bash
cp .env.example .env
# Edit .env with your Cin7 API credentials
```

### Step 3: Build and Start

```bash
# Build and start all services
docker-compose up -d

# View logs
docker-compose logs -f

# Check status
docker-compose ps
```

### Step 4: Initialize Database

```bash
# Run migration
docker-compose exec app python database/migrate.py
```

### Step 5: Access Application

Open browser: http://localhost:8501

### Docker Management Commands

```bash
# Stop services
docker-compose down

# Restart services
docker-compose restart

# View logs
docker-compose logs app
docker-compose logs db

# Rebuild after code changes
docker-compose up -d --build

# Clean up (removes volumes - data will be lost!)
docker-compose down -v
```

---

## Cin7 API Setup

### Step 1: Get API Credentials

1. Log in to Cin7 Omni
2. Go to **Settings** → **API** → **API Keys**
3. Click **Create New API Key**
4. Name: "HDL PO Receipt Tool"
5. Copy **API Key** and **API Secret**
6. Save these to your `.env` file

### Step 2: Set Permissions

Ensure your API key has these permissions:
- ✅ **Purchase Orders** - Read & Write
- ✅ **Suppliers** - Read
- ✅ **Products** - Read

### Step 3: Test Connection

```bash
# Test API connection
python -c "
from cin7.cin7_client import Cin7Client
client = Cin7Client()
print('API Connected:', client.get_rate_limit_status())
"
```

### Step 4: API Rate Limits

Cin7 enforces these limits:
- **3 requests/second**
- **60 requests/minute**
- **5000 requests/day**

The app automatically handles these limits with:
- Rate limiting queue
- Automatic retries
- Exponential backoff

---

## Database Setup

### Manual PostgreSQL Setup

```bash
# Install PostgreSQL
sudo apt-get install postgresql

# Create user
sudo -u postgres createuser hdl_user -P

# Create database
sudo -u postgres createdb hdl_receipts -O hdl_user

# Run schema
psql -U hdl_user -d hdl_receipts -f database/schema.sql
```

### Verify Database

```bash
# Connect to database
psql -U hdl_user -d hdl_receipts

# List tables
\dt

# Expected tables:
# - uploads
# - extractions
# - extraction_lines
# - receipts
# - receipt_lines
# - audit_log
```

### Database Backup

```bash
# Backup
pg_dump -U hdl_user hdl_receipts > backup.sql

# Restore
psql -U hdl_user hdl_receipts < backup.sql
```

---

## Testing

### Run Unit Tests

```bash
# Activate virtual environment
source venv/bin/activate

# Run all tests
pytest

# Run specific test file
pytest tests/test_po_matcher.py

# Run with coverage
pytest --cov=. --cov-report=html

# View coverage report
open htmlcov/index.html
```

### Test PO Reference Normalization

```bash
pytest tests/test_po_matcher.py -v
```

### Test Rate Limiter

```bash
pytest tests/test_rate_limiter.py -v
```

### Test Cin7 Client (with mocks)

```bash
pytest tests/test_cin7_client.py -v
```

---

## Production Deployment

### Prerequisites

- Ubuntu 20.04+ server
- Docker installed
- Domain name (optional)
- SSL certificate (recommended)

### Step 1: Server Setup

```bash
# Update system
sudo apt-get update && sudo apt-get upgrade -y

# Install Docker
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh

# Install Docker Compose
sudo curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
sudo chmod +x /usr/local/bin/docker-compose
```

### Step 2: Deploy Application

```bash
# Clone repository
git clone <repository-url>
cd Receipt

# Configure environment
cp .env.example .env
nano .env  # Add production credentials

# Important: Set secure passwords!
# - Change POSTGRES_PASSWORD
# - Add real Cin7 credentials
# - Set APP_ENV=production

# Start services
docker-compose up -d

# Run migration
docker-compose exec app python database/migrate.py
```

### Step 3: Configure Firewall

```bash
# Allow SSH
sudo ufw allow 22

# Allow HTTP/HTTPS
sudo ufw allow 80
sudo ufw allow 443

# Enable firewall
sudo ufw enable
```

### Step 4: Set Up Nginx Reverse Proxy (Optional)

```bash
# Install Nginx
sudo apt-get install nginx

# Create config
sudo nano /etc/nginx/sites-available/hdl-receipt

# Add:
server {
    listen 80;
    server_name your-domain.com;

    location / {
        proxy_pass http://localhost:8501;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
        proxy_set_header Host $host;
    }
}

# Enable site
sudo ln -s /etc/nginx/sites-available/hdl-receipt /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl restart nginx
```

### Step 5: SSL Certificate (Let's Encrypt)

```bash
# Install Certbot
sudo apt-get install certbot python3-certbot-nginx

# Get certificate
sudo certbot --nginx -d your-domain.com

# Auto-renewal
sudo certbot renew --dry-run
```

### Step 6: Monitoring

```bash
# View logs
docker-compose logs -f app

# Check resource usage
docker stats

# Database connection count
docker-compose exec db psql -U hdl_user -d hdl_receipts -c "SELECT count(*) FROM pg_stat_activity;"
```

### Step 7: Backups

```bash
# Create backup script
cat > backup.sh << 'EOF'
#!/bin/bash
DATE=$(date +%Y%m%d_%H%M%S)
docker-compose exec -T db pg_dump -U hdl_user hdl_receipts > backups/backup_$DATE.sql
find backups/ -mtime +7 -delete
EOF

chmod +x backup.sh

# Add to cron (daily at 2 AM)
crontab -e
# Add: 0 2 * * * /path/to/backup.sh
```

---

## Troubleshooting

### Tesseract Not Found

```bash
# Find Tesseract location
which tesseract

# Update TESSERACT_CMD in .env with the path
```

### Database Connection Failed

```bash
# Check PostgreSQL is running
sudo systemctl status postgresql

# Check connection string in .env
# Format: postgresql://user:password@host:port/database
```

### Cin7 API Errors

```bash
# Test API credentials
python -c "
from cin7.cin7_client import Cin7Client
try:
    client = Cin7Client()
    print('Success:', client.get_rate_limit_status())
except Exception as e:
    print('Error:', e)
"
```

### Docker Container Won't Start

```bash
# Check logs
docker-compose logs app

# Rebuild
docker-compose down
docker-compose up -d --build

# Check resource usage
docker stats
```

### Port Already in Use

```bash
# Check what's using port 8501
sudo lsof -i :8501

# Kill process or change port in docker-compose.yml
```

---

## Next Steps

After successful setup:

1. ✅ Test OCR with a sample docket
2. ✅ Create a test PO in Cin7
3. ✅ Perform end-to-end receipt test
4. ✅ Train warehouse staff
5. ✅ Set up monitoring & alerts

## Support

For issues:
- Check application logs: `docker-compose logs app`
- Check database logs: `docker-compose logs db`
- Review troubleshooting section
- Contact: IT Support

---

**Last Updated:** 2024
**Version:** 1.0.0
