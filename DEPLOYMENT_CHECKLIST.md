# HDL PO Receipt Tool - Deployment Checklist

Complete checklist for deploying the HDL PO Receipt Tool to production.

## Pre-Deployment

### 1. Environment Setup

- [ ] Server/VM provisioned (minimum 2GB RAM, 5GB disk)
- [ ] Docker and Docker Compose installed
- [ ] Firewall rules configured (ports 80, 443, 8501)
- [ ] Domain name configured (if applicable)
- [ ] SSL certificate obtained (Let's Encrypt recommended)

### 2. Cin7 API Access

- [ ] Cin7 Omni API key obtained
- [ ] API secret obtained
- [ ] API permissions verified:
  - [ ] Purchase Orders (Read & Write)
  - [ ] Suppliers (Read)
  - [ ] Products (Read)
- [ ] API rate limits understood (3/sec, 60/min, 5000/day)
- [ ] Test API connection successful

### 3. Database Preparation

- [ ] PostgreSQL credentials generated
- [ ] Strong database password set
- [ ] Backup strategy planned
- [ ] Retention policy defined (recommend 30 days)

### 4. Application Configuration

- [ ] `.env` file created from `.env.example`
- [ ] All required variables populated:
  - [ ] `DATABASE_URL`
  - [ ] `CIN7_API_KEY`
  - [ ] `CIN7_API_SECRET`
  - [ ] `TESSERACT_CMD`
  - [ ] `POSTGRES_USER`
  - [ ] `POSTGRES_PASSWORD`
  - [ ] `POSTGRES_DB`
- [ ] Passwords are strong and secure
- [ ] `.env` file NOT committed to git

### 5. Code Review

- [ ] Latest code pulled from repository
- [ ] Dependencies up to date
- [ ] No debug code in production
- [ ] Logging level set appropriately (INFO or WARNING)
- [ ] Error handling verified
- [ ] Unit tests passing

## Deployment Steps

### 6. Initial Deployment

```bash
# Navigate to project directory
cd Receipt

# Build containers
- [ ] docker-compose build

# Start services
- [ ] docker-compose up -d

# Verify services running
- [ ] docker-compose ps
```

### 7. Database Initialization

```bash
# Run database migration
- [ ] docker-compose exec app python database/migrate.py

# Verify tables created
- [ ] docker-compose exec db psql -U hdl_user -d hdl_receipts -c "\dt"
```

### 8. Application Testing

#### Health Checks
- [ ] Application accessible at http://localhost:8501
- [ ] Health endpoint responds: http://localhost:8501/_stcore/health
- [ ] Database connection successful

#### Functional Testing
- [ ] Upload test docket image
- [ ] OCR extraction works
- [ ] PO search connects to Cin7
- [ ] Test PO found successfully
- [ ] Line matching works
- [ ] Receipt submission successful
- [ ] Data logged to database

#### End-to-End Test
- [ ] Create test PO in Cin7 (TEST-0001)
- [ ] Prepare test docket for TEST-0001
- [ ] Complete full receipt workflow
- [ ] Verify receipt in Cin7
- [ ] Verify data in database
- [ ] Check audit log

### 9. Security Configuration

- [ ] Firewall rules active
- [ ] Only necessary ports exposed
- [ ] Strong passwords used everywhere
- [ ] API credentials stored securely
- [ ] Database accessible only from localhost
- [ ] HTTPS enabled (production)
- [ ] Security headers configured (if using reverse proxy)

### 10. Monitoring Setup

- [ ] Log rotation configured
- [ ] Disk space monitoring active
- [ ] Database backup script installed
- [ ] Backup cron job scheduled
- [ ] Health check monitoring (optional)
- [ ] Alert notifications configured (optional)

## Post-Deployment

### 11. Documentation

- [ ] README.md updated with production URLs
- [ ] Admin credentials documented (securely)
- [ ] Support contacts updated
- [ ] Backup/restore procedures documented
- [ ] Troubleshooting guide accessible

### 12. User Training

- [ ] Training session scheduled
- [ ] User guide provided
- [ ] Test accounts created
- [ ] Practice session completed
- [ ] Feedback collected

### 13. Go-Live Preparation

- [ ] Maintenance window scheduled (if needed)
- [ ] Users notified of launch
- [ ] Support team on standby
- [ ] Rollback plan documented
- [ ] Success criteria defined

### 14. Go-Live

- [ ] Application accessible to users
- [ ] First real receipt completed successfully
- [ ] Users can access application
- [ ] No critical errors in logs
- [ ] Performance acceptable
- [ ] Cin7 integration working

### 15. Post Go-Live Monitoring

**First 24 Hours:**
- [ ] Monitor logs hourly
- [ ] Check error rates
- [ ] Verify receipts in Cin7
- [ ] User feedback collected
- [ ] Performance metrics recorded

**First Week:**
- [ ] Daily log review
- [ ] Performance monitoring
- [ ] User satisfaction survey
- [ ] Issue tracking
- [ ] Optimization opportunities identified

**First Month:**
- [ ] Weekly performance review
- [ ] Database maintenance
- [ ] Backup verification
- [ ] Usage statistics analysis
- [ ] Feature requests collected

## Verification Checklist

### Critical Functionality

- [ ] ✅ Users can upload dockets (camera & file)
- [ ] ✅ OCR extracts text accurately
- [ ] ✅ PO matching finds correct POs
- [ ] ✅ Backorder suffixes (A/B/C) handled
- [ ] ✅ Line items matched correctly
- [ ] ✅ Duplicate detection works
- [ ] ✅ Receipts submit to Cin7
- [ ] ✅ Audit log captures all actions

### Performance

- [ ] ✅ Page load < 3 seconds
- [ ] ✅ OCR processing < 10 seconds
- [ ] ✅ PO search < 2 seconds
- [ ] ✅ Receipt submission < 5 seconds
- [ ] ✅ No timeout errors
- [ ] ✅ Rate limits respected

### Security

- [ ] ✅ No credentials in code
- [ ] ✅ No credentials in logs
- [ ] ✅ Database password strong
- [ ] ✅ API keys not exposed
- [ ] ✅ HTTPS enabled (production)
- [ ] ✅ Firewall active

### Reliability

- [ ] ✅ Error handling works
- [ ] ✅ Retry logic functional
- [ ] ✅ Database transactions atomic
- [ ] ✅ No data loss on errors
- [ ] ✅ Backups working
- [ ] ✅ Recovery tested

## Rollback Plan

If critical issues occur:

### Immediate Actions
1. Stop accepting new receipts
2. Identify issue from logs
3. Assess impact

### Rollback Steps
```bash
# Stop application
docker-compose down

# Restore previous version (if needed)
git checkout <previous-commit>
docker-compose up -d

# Restore database (if needed)
docker-compose exec -T db psql -U hdl_user hdl_receipts < backup.sql
```

### Communication
- Notify users of downtime
- Provide status updates
- Communicate resolution timeline

## Success Criteria

Deployment is successful when:

- [ ] ✅ Application is accessible
- [ ] ✅ 10+ successful receipts completed
- [ ] ✅ Zero critical errors
- [ ] ✅ User feedback positive
- [ ] ✅ Performance meets requirements
- [ ] ✅ Cin7 integration stable
- [ ] ✅ Backups operational
- [ ] ✅ Support team trained

## Sign-Off

### Technical Sign-Off

| Role | Name | Signature | Date |
|------|------|-----------|------|
| Developer | | | |
| System Admin | | | |
| Database Admin | | | |
| Security | | | |

### Business Sign-Off

| Role | Name | Signature | Date |
|------|------|-----------|------|
| Warehouse Manager | | | |
| IT Manager | | | |
| Operations Manager | | | |

## Support Plan

### Support Contacts

| Issue Type | Contact | Method |
|------------|---------|--------|
| User questions | IT Help Desk | support@hdl.com |
| Technical issues | System Admin | admin@hdl.com |
| Critical outages | On-call | [Emergency #] |

### Escalation Path

1. **Level 1**: Help desk (user issues, training)
2. **Level 2**: System admin (technical issues)
3. **Level 3**: Developer (critical bugs)

### SLA Targets

| Priority | Response Time | Resolution Time |
|----------|---------------|-----------------|
| Critical | 1 hour | 4 hours |
| High | 4 hours | 24 hours |
| Medium | 1 day | 3 days |
| Low | 3 days | 1 week |

## Maintenance Schedule

### Daily
- [ ] Log review
- [ ] Error monitoring
- [ ] Disk space check

### Weekly
- [ ] Performance review
- [ ] Database maintenance
- [ ] Backup verification

### Monthly
- [ ] Dependency updates
- [ ] Security patches
- [ ] Usage analysis
- [ ] User feedback review

### Quarterly
- [ ] Full security audit
- [ ] Disaster recovery test
- [ ] Performance optimization
- [ ] Feature roadmap review

## Notes

Add any deployment-specific notes here:

```
Date: _______________
Deployed by: _______________
Environment: _______________
Version: _______________

Notes:
_________________________________
_________________________________
_________________________________
```

---

## Quick Command Reference

```bash
# Start application
docker-compose up -d

# Stop application
docker-compose down

# View logs
docker-compose logs -f app

# Restart services
docker-compose restart

# Check status
docker-compose ps

# Backup database
docker-compose exec -T db pg_dump -U hdl_user hdl_receipts > backup_$(date +%Y%m%d).sql

# Restore database
docker-compose exec -T db psql -U hdl_user hdl_receipts < backup.sql

# View database
docker-compose exec db psql -U hdl_user hdl_receipts

# Clean old uploads (90+ days)
find uploads/ -mtime +90 -type f -delete
```

---

**Deployment Version**: 1.0.0
**Last Updated**: 2024
**Status**: Ready for Production ✅
