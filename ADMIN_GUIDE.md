# Cin7 Docket Receiver - Admin Guide

## Table of Contents

1. [System Requirements](#system-requirements)
2. [Installation](#installation)
3. [Configuration](#configuration)
4. [User Management](#user-management)
5. [Monitoring](#monitoring)
6. [Backup & Recovery](#backup--recovery)
7. [Troubleshooting](#troubleshooting)
8. [Maintenance](#maintenance)

## System Requirements

### Minimum Requirements
- **CPU:** 2 cores
- **RAM:** 4 GB
- **Storage:** 20 GB
- **OS:** Linux, macOS, or Windows with Docker support

### Recommended for Production
- **CPU:** 4+ cores
- **RAM:** 8 GB
- **Storage:** 50 GB SSD
- **OS:** Ubuntu 22.04 LTS or similar

### Software Dependencies
- Docker 24.0+
- Docker Compose 2.0+
- PostgreSQL 16 (via Docker)
- Node.js 20 (via Docker)

## Installation

### Docker Installation (Recommended)

1. **Clone the repository**
```bash
git clone <repository-url>
cd cin7-docket-receiver
```

2. **Configure environment**
```bash
cp .env.example .env
nano .env  # Edit with your settings
```

3. **Start services**
```bash
docker-compose up -d
```

4. **Verify installation**
```bash
docker-compose ps
curl http://localhost:3001/health
```

Expected response:
```json
{"status":"ok","database":"connected"}
```

### Manual Installation (Development)

**Backend:**
```bash
cd backend
npm install
cp ../.env.example .env
# Edit .env
npm run migrate
npm run dev
```

**Frontend:**
```bash
cd frontend
npm install
echo "REACT_APP_API_URL=http://localhost:3001" > .env
npm start
```

## Configuration

### Environment Variables

#### Required Settings

```env
# Cin7 API Credentials (CRITICAL)
CIN7_API_KEY=your-api-key-here
CIN7_API_SECRET=your-api-secret-here

# Security (CHANGE IN PRODUCTION)
JWT_SECRET=generate-random-secret-min-32-chars
```

#### Database Configuration

```env
DB_HOST=postgres  # Use 'localhost' for manual install
DB_PORT=5432
DB_NAME=cin7_receiver
DB_USER=postgres
DB_PASSWORD=postgres  # Change in production
```

#### Application Settings

```env
# Backend
PORT=3001
NODE_ENV=production
CORS_ORIGIN=http://localhost:3000  # Update for production domain

# Frontend
REACT_APP_API_URL=http://localhost:3001  # Update for production
```

### Obtaining Cin7 API Credentials

1. Log into Cin7 Omni
2. Navigate to **Settings** > **API**
3. Click **Generate API Key**
4. Copy the API Key and API Secret
5. Add to `.env` file

**Important:** Keep API credentials secure. Never commit to version control.

### Generating JWT Secret

```bash
# Linux/macOS
openssl rand -base64 32

# Node.js
node -e "console.log(require('crypto').randomBytes(32).toString('base64'))"
```

## User Management

### Creating First Admin User

After installation, register the first user:

1. Navigate to `http://localhost:3000/register`
2. Fill in email, password, and name
3. Click Register

**Note:** All users have the same permissions. Implement role-based access control if needed.

### Resetting User Password (Database Access Required)

```sql
-- Connect to database
docker exec -it cin7-receiver-db psql -U postgres -d cin7_receiver

-- Reset password (hash for "newpassword123")
UPDATE users
SET password_hash = '$2b$10$...' -- Generate with bcrypt
WHERE email = 'user@example.com';
```

Generate bcrypt hash:
```bash
node -e "console.log(require('bcrypt').hashSync('newpassword123', 10))"
```

### Listing Users

```sql
SELECT id, email, name, created_at FROM users;
```

### Deleting User

```sql
-- This will cascade delete all user's receipts
DELETE FROM users WHERE email = 'user@example.com';
```

## Monitoring

### Health Checks

**Backend API:**
```bash
curl http://localhost:3001/health
```

**Database:**
```bash
docker exec cin7-receiver-db pg_isready -U postgres
```

### Logs

**View all logs:**
```bash
docker-compose logs -f
```

**Backend logs only:**
```bash
docker-compose logs -f backend
```

**Database logs:**
```bash
docker-compose logs -f postgres
```

### Database Statistics

```sql
-- Connect to database
docker exec -it cin7-receiver-db psql -U postgres -d cin7_receiver

-- Receipt statistics
SELECT
    status,
    COUNT(*) as count,
    DATE(created_at) as date
FROM receipts
GROUP BY status, DATE(created_at)
ORDER BY date DESC
LIMIT 30;

-- User activity
SELECT
    u.email,
    COUNT(r.id) as total_receipts,
    MAX(r.created_at) as last_receipt
FROM users u
LEFT JOIN receipts r ON r.user_id = u.id
GROUP BY u.id, u.email;

-- Failed receipts
SELECT
    cin7_po_reference,
    error_message,
    created_at
FROM receipts
WHERE status = 'failed'
ORDER BY created_at DESC
LIMIT 20;
```

## Backup & Recovery

### Database Backup

**Automated daily backup (recommended):**

Create backup script `/opt/backups/backup-cin7.sh`:
```bash
#!/bin/bash
BACKUP_DIR="/opt/backups/cin7"
TIMESTAMP=$(date +%Y%m%d_%H%M%S)
mkdir -p $BACKUP_DIR

docker exec cin7-receiver-db pg_dump -U postgres cin7_receiver > \
    $BACKUP_DIR/cin7_receiver_$TIMESTAMP.sql

# Keep last 30 days
find $BACKUP_DIR -name "*.sql" -mtime +30 -delete
```

Add to crontab:
```bash
0 2 * * * /opt/backups/backup-cin7.sh
```

**Manual backup:**
```bash
docker exec cin7-receiver-db pg_dump -U postgres cin7_receiver > backup.sql
```

### Database Restore

```bash
# Stop backend to prevent writes
docker-compose stop backend

# Restore
docker exec -i cin7-receiver-db psql -U postgres cin7_receiver < backup.sql

# Restart
docker-compose start backend
```

### Uploaded Files Backup

```bash
# Backup uploads directory
tar -czf uploads-backup-$(date +%Y%m%d).tar.gz backend/uploads/

# Restore
tar -xzf uploads-backup-YYYYMMDD.tar.gz -C backend/
```

## Troubleshooting

### Issue: Cannot connect to database

**Symptoms:** Backend logs show "database connection failed"

**Solutions:**
1. Check PostgreSQL is running:
   ```bash
   docker-compose ps postgres
   ```

2. Check database credentials in `.env`

3. Restart database:
   ```bash
   docker-compose restart postgres
   ```

4. Check logs:
   ```bash
   docker-compose logs postgres
   ```

### Issue: OCR not extracting text correctly

**Symptoms:** Extracted data is empty or garbled

**Solutions:**
1. Ensure image quality is good (not blurry, well-lit)
2. Try uploading PDF instead of image
3. Check Tesseract is installed in backend container:
   ```bash
   docker exec cin7-receiver-backend tesseract --version
   ```

4. Review raw OCR text in database:
   ```sql
   SELECT raw_text FROM extractions ORDER BY id DESC LIMIT 5;
   ```

### Issue: Cin7 API errors

**Symptoms:** "Failed to match PO" or "Failed to create receipt"

**Solutions:**
1. Verify API credentials:
   ```bash
   docker exec cin7-receiver-backend env | grep CIN7
   ```

2. Test API connection manually:
   ```bash
   curl -u "API_KEY:API_SECRET" https://api.cin7.com/api/v1/PurchaseOrders?rows=1
   ```

3. Check rate limits:
   - 3 requests/second
   - 60 requests/minute
   - 5000 requests/day

4. Review Cin7 API status: https://status.cin7.com

### Issue: Frontend not loading

**Symptoms:** Blank page or connection refused

**Solutions:**
1. Check frontend container:
   ```bash
   docker-compose ps frontend
   docker-compose logs frontend
   ```

2. Verify API URL in frontend `.env`:
   ```bash
   docker exec cin7-receiver-frontend env | grep REACT_APP
   ```

3. Clear browser cache and hard refresh (Ctrl+Shift+R)

### Issue: Duplicate docket error

**Symptoms:** "Docket XXX has already been receipted"

**Solutions:**
1. This is intentional duplicate prevention
2. Check if docket was already processed:
   ```sql
   SELECT * FROM receipts
   WHERE docket_number = 'XXX'
   AND status = 'completed';
   ```

3. If legitimate duplicate, use "Allow Override" checkbox in UI

## Maintenance

### Updating the Application

```bash
# Pull latest code
git pull

# Rebuild containers
docker-compose build

# Restart with new images
docker-compose down
docker-compose up -d

# Run any new migrations
docker exec cin7-receiver-backend npm run migrate
```

### Database Cleanup

**Remove old extractions (keep last 90 days):**
```sql
DELETE FROM extractions
WHERE created_at < NOW() - INTERVAL '90 days';
```

**Remove old audit logs (keep last 180 days):**
```sql
DELETE FROM audit_log
WHERE created_at < NOW() - INTERVAL '180 days';
```

**Vacuum database:**
```sql
VACUUM ANALYZE;
```

### Disk Space Management

**Check upload directory size:**
```bash
du -sh backend/uploads/
```

**Remove old uploads (after backing up):**
```bash
find backend/uploads/ -type f -mtime +90 -delete
```

### Performance Tuning

**PostgreSQL:**
Edit `docker-compose.yml` and add:
```yaml
command:
  - postgres
  - -c
  - max_connections=100
  - -c
  - shared_buffers=256MB
  - -c
  - effective_cache_size=1GB
```

**Backend Workers:**
For high volume, run multiple backend instances behind a load balancer.

### Security Updates

**Update Docker images:**
```bash
docker-compose pull
docker-compose up -d
```

**Update npm dependencies:**
```bash
cd backend && npm audit fix
cd frontend && npm audit fix
```

## Production Deployment Checklist

- [ ] Change `JWT_SECRET` to random 32+ character string
- [ ] Change database password
- [ ] Set `NODE_ENV=production`
- [ ] Configure HTTPS/SSL (use reverse proxy like nginx)
- [ ] Set up firewall rules (only expose 80/443)
- [ ] Configure automated backups
- [ ] Set up monitoring/alerting
- [ ] Document disaster recovery procedure
- [ ] Enable log rotation
- [ ] Review and harden CORS settings
- [ ] Set up fail2ban or similar for brute force protection
- [ ] Configure rate limiting at reverse proxy level

## Support Contacts

- **Technical Issues:** [Your IT Department]
- **Cin7 API Support:** https://support.cin7.com
- **Application Bugs:** [Your Issue Tracker]

---

**Last Updated:** January 2026
**Version:** 1.0.0
