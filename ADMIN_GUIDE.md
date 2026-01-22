# HDL PO Receipt Tool - Administrator Guide

Complete guide for administering and maintaining the HDL PO Receipt Tool.

## Table of Contents

1. [System Administration](#system-administration)
2. [User Management](#user-management)
3. [Database Management](#database-management)
4. [Monitoring & Logs](#monitoring--logs)
5. [Troubleshooting](#troubleshooting)
6. [Backup & Recovery](#backup--recovery)
7. [Performance Tuning](#performance-tuning)
8. [Security](#security)

---

## System Administration

### Starting/Stopping the Application

**Docker Deployment:**

```bash
# Start all services
docker-compose up -d

# Stop all services
docker-compose down

# Restart a specific service
docker-compose restart app
docker-compose restart db

# View service status
docker-compose ps

# View resource usage
docker stats
```

**Manual Deployment:**

```bash
# Start application
streamlit run app.py

# With custom port
streamlit run app.py --server.port 8502

# Start PostgreSQL
sudo systemctl start postgresql

# Stop PostgreSQL
sudo systemctl stop postgresql
```

### Application Configuration

Configuration is managed via `.env` file:

```bash
# Edit configuration
nano .env

# Restart application to apply changes
docker-compose restart app
```

**Key Configuration Parameters:**

| Parameter | Description | Default |
|-----------|-------------|---------|
| `DATABASE_URL` | PostgreSQL connection string | Required |
| `CIN7_API_KEY` | Cin7 API key | Required |
| `CIN7_API_SECRET` | Cin7 API secret | Required |
| `TESSERACT_CMD` | Path to Tesseract binary | System-dependent |
| `FUZZY_MATCH_THRESHOLD` | Fuzzy matching sensitivity (0-100) | 85 |
| `MAX_UPLOAD_SIZE_MB` | Maximum file upload size | 10 |
| `LOG_LEVEL` | Logging verbosity | INFO |

### System Health Checks

```bash
# Check application health
curl http://localhost:8501/_stcore/health

# Check database connectivity
docker-compose exec db pg_isready -U hdl_user

# Check disk space
df -h

# Check Docker resources
docker system df
```

---

## User Management

> **Note:** Current version uses basic user tracking via `st.session_state.user_id`. Production deployment should implement proper authentication.

### Current User Tracking

Users are tracked in database fields:
- `uploaded_by`
- `reviewed_by`
- `posted_by`

### Future Authentication (TODO)

Recommended authentication methods:
- **Streamlit-Authenticator**: For basic auth
- **OAuth 2.0**: For enterprise SSO
- **LDAP/Active Directory**: For domain integration

### Audit Trail

All actions are logged in the `audit_log` table:

```sql
-- View recent user actions
SELECT * FROM audit_log
ORDER BY created_at DESC
LIMIT 100;

-- Actions by specific user
SELECT * FROM audit_log
WHERE user_id = 'warehouse_user'
ORDER BY created_at DESC;

-- Actions on specific date
SELECT * FROM audit_log
WHERE DATE(created_at) = '2024-12-01';
```

---

## Database Management

### Database Access

```bash
# Docker deployment
docker-compose exec db psql -U hdl_user -d hdl_receipts

# Manual deployment
psql -U hdl_user -d hdl_receipts
```

### Common Database Queries

**View Recent Receipts:**

```sql
SELECT
    po_reference,
    supplier_name,
    docket_number,
    posted_at,
    posted_by,
    status
FROM receipts
ORDER BY posted_at DESC
LIMIT 20;
```

**View Receipt Details:**

```sql
SELECT
    r.po_reference,
    r.docket_number,
    rl.sku,
    rl.description,
    rl.quantity_received
FROM receipts r
JOIN receipt_lines rl ON r.id = rl.receipt_id
WHERE r.po_reference = 'PO-12345';
```

**Check for Duplicates:**

```sql
SELECT
    supplier_name,
    docket_number,
    COUNT(*) as count
FROM receipts
WHERE status = 'success'
GROUP BY supplier_name, docket_number
HAVING COUNT(*) > 1;
```

**View Failed Receipts:**

```sql
SELECT
    po_reference,
    error_message,
    posted_at
FROM receipts
WHERE status = 'failed'
ORDER BY posted_at DESC;
```

**Upload Statistics:**

```sql
SELECT
    DATE(uploaded_at) as date,
    COUNT(*) as uploads,
    AVG(file_size_bytes / 1024.0 / 1024.0) as avg_size_mb
FROM uploads
GROUP BY DATE(uploaded_at)
ORDER BY date DESC;
```

### Database Maintenance

**Vacuum and Analyze:**

```bash
# Docker deployment
docker-compose exec db psql -U hdl_user -d hdl_receipts -c "VACUUM ANALYZE;"

# Manual deployment
psql -U hdl_user -d hdl_receipts -c "VACUUM ANALYZE;"
```

**Check Database Size:**

```sql
SELECT
    pg_size_pretty(pg_database_size('hdl_receipts')) as size;
```

**Check Table Sizes:**

```sql
SELECT
    tablename,
    pg_size_pretty(pg_total_relation_size(schemaname||'.'||tablename)) as size
FROM pg_tables
WHERE schemaname = 'public'
ORDER BY pg_total_relation_size(schemaname||'.'||tablename) DESC;
```

**Clean Old Upload Files:**

```bash
# Find files older than 90 days
find uploads/ -name "*.jpg" -mtime +90 -type f

# Delete files older than 90 days (be careful!)
find uploads/ -name "*.jpg" -mtime +90 -type f -delete
```

---

## Monitoring & Logs

### Application Logs

**Docker Deployment:**

```bash
# View all logs
docker-compose logs -f

# View app logs only
docker-compose logs -f app

# View last 100 lines
docker-compose logs --tail=100 app

# Save logs to file
docker-compose logs app > app.log
```

**Log Files (Manual Deployment):**

- Application log: `app.log`
- Error log: Check console output

### Log Analysis

**Search for errors:**

```bash
# Docker
docker-compose logs app | grep -i error

# Manual
cat app.log | grep -i error
```

**Monitor in real-time:**

```bash
# Docker
docker-compose logs -f app | grep -i "error\|warning\|failed"

# Manual
tail -f app.log | grep -i "error\|warning\|failed"
```

### Cin7 API Rate Limit Monitoring

Rate limit status is logged in the application. Check logs for:

```
INFO - Rate limit status: {per_second: {used: X, remaining: Y}}
```

**Check current rate limit:**

```python
from cin7.cin7_client import Cin7Client

client = Cin7Client()
status = client.get_rate_limit_status()
print(status)
```

### Database Monitoring

**Active Connections:**

```sql
SELECT
    count(*) as connections
FROM pg_stat_activity
WHERE datname = 'hdl_receipts';
```

**Slow Queries:**

```sql
SELECT
    pid,
    now() - query_start as duration,
    query
FROM pg_stat_activity
WHERE state = 'active'
  AND now() - query_start > interval '5 seconds';
```

**Lock Monitoring:**

```sql
SELECT
    locktype,
    relation::regclass,
    mode,
    granted
FROM pg_locks
WHERE NOT granted;
```

---

## Troubleshooting

### Common Issues

#### 1. OCR Not Extracting Text

**Symptoms:**
- No text extracted
- Low confidence scores
- Missing fields

**Solutions:**

```bash
# Check Tesseract installation
tesseract --version

# Test Tesseract directly
tesseract test_image.jpg output

# Check image quality
# - Ensure image is well-lit
# - Check focus and resolution
# - Verify no shadows or glare

# Try aggressive preprocessing
# (This is automatic if OCR confidence is low)
```

#### 2. Cin7 API Connection Failed

**Symptoms:**
- "Cin7 API Error"
- Connection timeout

**Solutions:**

```bash
# Test API credentials
python -c "
from cin7.cin7_client import Cin7Client
try:
    client = Cin7Client()
    status = client.get_rate_limit_status()
    print('API Connected:', status)
except Exception as e:
    print('API Error:', e)
"

# Check network connectivity
curl -I https://api.cin7.com

# Verify credentials in .env
cat .env | grep CIN7
```

#### 3. Database Connection Failed

**Symptoms:**
- "Database connection error"
- "Could not connect to database"

**Solutions:**

```bash
# Check PostgreSQL is running
sudo systemctl status postgresql

# Test connection
psql -U hdl_user -d hdl_receipts -c "SELECT 1;"

# Check DATABASE_URL in .env
cat .env | grep DATABASE_URL

# Check database logs
docker-compose logs db

# Restart database
docker-compose restart db
```

#### 4. Rate Limit Exceeded

**Symptoms:**
- "Rate limit exceeded"
- 429 errors in logs

**Solutions:**

- Wait for rate limit to reset (1 second/1 minute/1 day)
- Check if multiple instances are running
- Review API usage in logs
- Consider reducing concurrent operations

#### 5. Duplicate Receipt Detection

**Symptoms:**
- "Duplicate detected" warning
- Receipt blocked

**Solutions:**

```sql
-- Check for duplicate
SELECT * FROM receipts
WHERE supplier_name = 'ACME Supplies'
  AND docket_number = 'DKT-12345'
  AND status = 'success';

-- If false positive, use override checkbox in app
-- Or delete incorrect duplicate (carefully!)
DELETE FROM receipts WHERE id = 'uuid-here';
```

### Debug Mode

Enable detailed logging:

```bash
# Edit .env
LOG_LEVEL=DEBUG

# Restart application
docker-compose restart app

# View detailed logs
docker-compose logs -f app
```

---

## Backup & Recovery

### Database Backups

**Automated Backup Script:**

```bash
#!/bin/bash
# backup_db.sh

DATE=$(date +%Y%m%d_%H%M%S)
BACKUP_DIR="/backups"
BACKUP_FILE="$BACKUP_DIR/hdl_receipts_$DATE.sql"

# Create backup directory
mkdir -p $BACKUP_DIR

# Backup database
docker-compose exec -T db pg_dump -U hdl_user hdl_receipts > $BACKUP_FILE

# Compress
gzip $BACKUP_FILE

# Delete backups older than 30 days
find $BACKUP_DIR -name "*.sql.gz" -mtime +30 -delete

echo "Backup completed: $BACKUP_FILE.gz"
```

**Schedule with Cron:**

```bash
# Edit crontab
crontab -e

# Add daily backup at 2 AM
0 2 * * * /path/to/backup_db.sh >> /var/log/hdl_backup.log 2>&1
```

**Manual Backup:**

```bash
# Docker deployment
docker-compose exec -T db pg_dump -U hdl_user hdl_receipts > backup.sql

# Manual deployment
pg_dump -U hdl_user hdl_receipts > backup.sql

# Compress
gzip backup.sql
```

### Restore from Backup

```bash
# Docker deployment
gunzip backup.sql.gz
docker-compose exec -T db psql -U hdl_user -d hdl_receipts < backup.sql

# Manual deployment
gunzip backup.sql.gz
psql -U hdl_user -d hdl_receipts < backup.sql
```

### File Backups

```bash
# Backup uploaded files
tar -czf uploads_backup.tar.gz uploads/

# Restore
tar -xzf uploads_backup.tar.gz
```

---

## Performance Tuning

### Database Optimization

**Add Indexes:**

```sql
-- Already created by schema.sql, but can add more:
CREATE INDEX idx_receipts_supplier ON receipts(supplier_name);
CREATE INDEX idx_receipts_date ON receipts(receipt_date);
```

**Query Optimization:**

```sql
-- Analyze query performance
EXPLAIN ANALYZE
SELECT * FROM receipts
WHERE po_reference = 'PO-12345';
```

**Increase Connection Pool:**

Edit `.env`:
```bash
DATABASE_URL=postgresql://user:password@host:5432/db?pool_size=20&max_overflow=40
```

### Application Performance

**Streamlit Configuration:**

Create `.streamlit/config.toml`:

```toml
[server]
maxUploadSize = 10
maxMessageSize = 200

[browser]
gatherUsageStats = false

[runner]
magicEnabled = false
fastReruns = true
```

**Image Processing:**

- Reduce image resolution before OCR
- Use aggressive preprocessing only when needed
- Consider async processing for large batches

---

## Security

### Access Control

**Firewall Rules:**

```bash
# Allow only specific IPs (example)
sudo ufw allow from 192.168.1.0/24 to any port 8501

# Block all other access
sudo ufw deny 8501
```

**Nginx Basic Auth (if using reverse proxy):**

```bash
# Create password file
sudo htpasswd -c /etc/nginx/.htpasswd admin

# Add to nginx config
location / {
    auth_basic "Restricted";
    auth_basic_user_file /etc/nginx/.htpasswd;
    proxy_pass http://localhost:8501;
}
```

### Security Best Practices

1. ✅ **Keep credentials secure**
   - Never commit `.env` to git
   - Use strong passwords
   - Rotate API keys regularly

2. ✅ **Regular updates**
   ```bash
   # Update dependencies
   pip install --upgrade -r requirements.txt

   # Update Docker images
   docker-compose pull
   docker-compose up -d
   ```

3. ✅ **Monitor logs for suspicious activity**
   ```bash
   # Check for failed logins, unusual patterns
   docker-compose logs app | grep -i "error\|fail"
   ```

4. ✅ **Database security**
   - Use strong database password
   - Restrict database access to localhost
   - Enable SSL for database connections

5. ✅ **HTTPS in production**
   - Use Let's Encrypt for SSL
   - Force HTTPS redirects
   - Update CORS settings

---

## Maintenance Schedule

### Daily

- [ ] Check application logs for errors
- [ ] Monitor disk space
- [ ] Verify backups completed

### Weekly

- [ ] Review failed receipts
- [ ] Check for duplicate receipts
- [ ] Analyze OCR accuracy
- [ ] Review rate limit usage

### Monthly

- [ ] Database vacuum and analyze
- [ ] Review and archive old uploads
- [ ] Update dependencies
- [ ] Performance review
- [ ] Backup verification

### Quarterly

- [ ] Security audit
- [ ] Review user access
- [ ] Rotate API credentials
- [ ] Disaster recovery test
- [ ] Performance optimization review

---

## Support Escalation

### Level 1: Application Issues
- OCR problems
- UI bugs
- User training

### Level 2: System Issues
- Database problems
- API connection issues
- Performance problems

### Level 3: Critical Issues
- Data corruption
- Security breaches
- System outages

**Contact:**
- IT Support: support@hdl.com
- On-call: [Emergency contact]

---

**Last Updated:** 2024
**Version:** 1.0.0
