# Setup Checklist

Use this checklist to verify your installation and configuration.

## ☐ Prerequisites

- [ ] Docker Desktop installed and running
- [ ] Cin7 Omni account with API access
- [ ] Cin7 API credentials obtained (Key + Secret)
- [ ] Text editor for editing `.env` file

## ☐ Initial Setup

- [ ] Project files extracted to a directory
- [ ] `.env.example` copied to `.env`
- [ ] Cin7 API Key added to `.env`
- [ ] Cin7 API Secret added to `.env`
- [ ] JWT Secret generated and added to `.env`
- [ ] Database password changed from default (recommended)

## ☐ Docker Deployment

- [ ] Run `docker-compose up -d`
- [ ] Wait 60 seconds for services to start
- [ ] Verify all 3 containers are running: `docker-compose ps`
  - [ ] cin7-receiver-db (postgres)
  - [ ] cin7-receiver-backend (backend)
  - [ ] cin7-receiver-frontend (frontend)

## ☐ Health Checks

- [ ] Backend health check: http://localhost:3001/health
  - Should return: `{"status":"ok","database":"connected"}`
- [ ] Frontend loads: http://localhost:3000
  - Should show login/register page

## ☐ First User Setup

- [ ] Navigate to http://localhost:3000/register
- [ ] Create account with:
  - [ ] Valid email address
  - [ ] Password (min 6 characters)
  - [ ] Name (optional)
- [ ] Successfully logged in to dashboard

## ☐ Functional Tests

### Test 1: Docket Upload
- [ ] Click "Scan New Docket" from dashboard
- [ ] Upload a test image or PDF
- [ ] Wait for OCR processing
- [ ] Extracted data appears on review screen

### Test 2: PO Matching
- [ ] Edit PO reference if needed
- [ ] Click "Continue to PO Matching"
- [ ] System searches Cin7 for matching PO
- [ ] Best match or error message displayed

### Test 3: Line Matching (requires valid PO)
- [ ] Line items matched to PO lines
- [ ] Match types shown (exact/fuzzy/unmatched)
- [ ] Any issues flagged

### Test 4: Receipt Creation (requires valid PO)
- [ ] Review receipt summary
- [ ] Click "Submit Receipt to Cin7"
- [ ] Success message with receipt ID
- [ ] Receipt appears in history

### Test 5: Receipt History
- [ ] Click "Receipt History" from dashboard
- [ ] Previous receipts displayed
- [ ] Status badges shown
- [ ] Can click to view details

## ☐ Database Verification

- [ ] Connect to database:
  ```bash
  docker exec -it cin7-receiver-db psql -U postgres -d cin7_receiver
  ```
- [ ] Verify tables exist:
  ```sql
  \dt
  ```
  Should show: users, uploads, extractions, receipts, receipt_lines, audit_log
- [ ] Check user count:
  ```sql
  SELECT COUNT(*) FROM users;
  ```

## ☐ Logs Review

- [ ] Check backend logs for errors:
  ```bash
  docker-compose logs backend | grep -i error
  ```
- [ ] Check database logs:
  ```bash
  docker-compose logs postgres | grep -i error
  ```

## ☐ Configuration Validation

- [ ] Verify environment variables loaded:
  ```bash
  docker exec cin7-receiver-backend env | grep CIN7
  ```
- [ ] Should show CIN7_API_KEY and CIN7_API_SECRET (values hidden)

## ☐ Security Check

- [ ] JWT_SECRET is not the default value
- [ ] Database password changed from "postgres"
- [ ] `.env` file not committed to git
- [ ] No API credentials in source code

## ☐ Performance Check

- [ ] OCR processing completes within 5 seconds
- [ ] PO search completes within 2 seconds
- [ ] Frontend loads within 1 second
- [ ] No memory leaks (containers stable over 1 hour)

## ☐ Documentation Review

- [ ] Read README.md
- [ ] Review QUICK_START.md
- [ ] Bookmark ADMIN_GUIDE.md for troubleshooting
- [ ] Check API_DOCUMENTATION.md for integration

## ☐ Production Readiness (If Deploying to Production)

- [ ] HTTPS/SSL certificate configured
- [ ] Firewall rules configured (only expose 80/443)
- [ ] Automated backups scheduled
- [ ] Monitoring set up
- [ ] Log aggregation configured
- [ ] Disaster recovery plan documented
- [ ] Team trained on usage
- [ ] Support contact information updated

## ☐ Optional Enhancements

- [ ] Configure reverse proxy (nginx/traefik)
- [ ] Set up log rotation
- [ ] Enable fail2ban for brute force protection
- [ ] Configure CDN for frontend assets
- [ ] Set up staging environment
- [ ] Create automated tests for CI/CD

## Troubleshooting

If any check fails, refer to:

1. **ADMIN_GUIDE.md** - Troubleshooting section
2. **Logs** - `docker-compose logs -f`
3. **Health endpoint** - http://localhost:3001/health

### Common Issues

**❌ Database connection failed**
- Check: `docker-compose ps postgres`
- Fix: `docker-compose restart postgres`

**❌ Frontend blank page**
- Check: Browser console for errors
- Fix: Hard refresh (Ctrl+Shift+R)

**❌ OCR not working**
- Check: Image quality (clear, well-lit)
- Try: Upload PDF instead of image

**❌ Cin7 API errors**
- Check: API credentials in `.env`
- Verify: Credentials work via curl test

**❌ Duplicate docket error**
- Expected: This is intentional protection
- Option: Use "Allow Override" if needed

## Success Criteria

Your installation is successful when:

✅ All containers running (green status)
✅ Health check returns OK
✅ Can create user account
✅ Can upload and process docket
✅ Can search for PO in Cin7
✅ Receipt history shows entries
✅ No errors in logs

## Next Steps

Once all checks pass:

1. **Train users** - Share QUICK_START.md
2. **Test with real data** - Process actual delivery dockets
3. **Monitor usage** - Check logs and database
4. **Plan backups** - Schedule automated backups
5. **Document processes** - Create internal procedures

## Support

Need help?
- 📖 Read ADMIN_GUIDE.md
- 🔍 Check logs: `docker-compose logs -f`
- 🏥 Health check: http://localhost:3001/health
- 📊 Database: `docker exec -it cin7-receiver-db psql -U postgres -d cin7_receiver`

---

**Last Updated:** January 2026
**Version:** 1.0.0

**Installation Time:** ~5 minutes
**Checklist Items:** 50+
**Success Rate:** Should be 100% with proper setup
