# HDL PO Receipt Tool - Quick Start Guide

Get up and running in 5 minutes!

## 🚀 Fastest Setup (Docker)

### Step 1: Prerequisites

- Docker & Docker Compose installed
- Cin7 Omni API credentials

### Step 2: Clone & Configure

```bash
# Clone repository
git clone <repository-url>
cd Receipt

# Create environment file
cp .env.example .env

# Edit with your credentials
nano .env
```

**Minimum Required Configuration:**

```bash
CIN7_API_KEY=your_api_key_here
CIN7_API_SECRET=your_api_secret_here
```

### Step 3: Start Application

```bash
# Start all services
docker-compose up -d

# Initialize database
docker-compose exec app python database/migrate.py

# View logs
docker-compose logs -f
```

### Step 4: Access Application

Open your browser: **http://localhost:8501**

---

## 📱 Using the App

### Workflow Overview

```
📸 Upload Docket → 🔍 Review Data → 🔗 Match PO → 📋 Match Lines → ✅ Submit
```

### Step-by-Step

1. **Upload Docket**
   - Take photo or upload image
   - Supports JPG, PNG, PDF

2. **Review Extraction**
   - Check extracted fields
   - Edit if needed
   - Verify line items

3. **Match PO**
   - App finds matching PO in Cin7
   - Handles backorders (A/B/C suffix)
   - Manual search if needed

4. **Match Lines**
   - Review line-by-line matching
   - Adjust quantities
   - Resolve flags

5. **Submit Receipt**
   - Final review
   - Submit to Cin7
   - Done!

---

## 🎯 Quick Examples

### Example 1: Standard Receipt

**Docket Shows:**
```
PO-12345
Supplier: ACME Supplies
Item: Widget-A, Qty: 10
```

**Steps:**
1. Upload docket photo
2. Verify PO-12345 extracted correctly
3. App finds PO in Cin7
4. Match Widget-A to PO line
5. Submit → ✅ Done!

### Example 2: Backorder Receipt

**Docket Shows:**
```
PO-12345A (Backorder A)
```

**Steps:**
1. Upload docket
2. App finds PO-12345A
3. Matches backorder PO
4. Receipt against correct PO
5. Submit → ✅ Done!

### Example 3: Partial Delivery

**PO Line:**
- Ordered: 100 units
- Remaining: 100 units

**Docket Shows:**
- Delivered: 50 units

**Steps:**
1. Upload docket (50 units)
2. App matches line
3. Receipts 50 units
4. PO shows 50 remaining
5. Submit → ✅ Done!

---

## 🔧 Quick Troubleshooting

### OCR Not Working?

```bash
# Check Tesseract
docker-compose exec app tesseract --version

# Ensure good image quality:
# - Well-lit
# - In focus
# - Flat surface
```

### Can't Connect to Cin7?

```bash
# Test API
docker-compose exec app python -c "
from cin7.cin7_client import Cin7Client
client = Cin7Client()
print(client.get_rate_limit_status())
"
```

### Database Error?

```bash
# Restart database
docker-compose restart db

# Re-run migration
docker-compose exec app python database/migrate.py
```

### View Logs

```bash
# All logs
docker-compose logs -f

# App only
docker-compose logs -f app

# Errors only
docker-compose logs app | grep -i error
```

---

## 📊 Quick Status Check

```bash
# Check all services
docker-compose ps

# Expected output:
# hdl_receipts_app   Up   0.0.0.0:8501->8501/tcp
# hdl_receipts_db    Up   0.0.0.0:5432->5432/tcp
```

---

## 🎓 Tips for Best Results

### For OCR Accuracy

✅ **DO:**
- Use good lighting
- Keep camera steady
- Capture entire document
- Ensure text is in focus

❌ **DON'T:**
- Use flash (causes glare)
- Photograph at angles
- Use blurry images
- Crop important info

### For Efficient Processing

✅ **DO:**
- Review extracted data carefully
- Use manual search if auto-match fails
- Confirm fuzzy matches
- Check quantities before submitting

❌ **DON'T:**
- Rush through without reviewing
- Ignore warning flags
- Skip duplicate checks
- Submit without verifying PO

---

## 📚 Full Documentation

- **Setup Guide**: [`SETUP_INSTRUCTIONS.md`](SETUP_INSTRUCTIONS.md)
- **Admin Guide**: [`ADMIN_GUIDE.md`](ADMIN_GUIDE.md)
- **README**: [`README.md`](README.md)

---

## 🆘 Getting Help

### Common Issues

| Issue | Solution |
|-------|----------|
| OCR not extracting text | Check image quality, verify Tesseract installed |
| PO not found | Verify PO exists in Cin7, try manual search |
| Duplicate warning | Check if already receipted, use override if needed |
| Rate limit error | Wait 1 minute, reduce concurrent operations |

### Support Contacts

- **IT Support**: support@hdl.com
- **Documentation**: See guides in repo
- **Logs**: `docker-compose logs app`

---

## ⚡ Quick Commands Reference

```bash
# Start application
docker-compose up -d

# Stop application
docker-compose down

# View logs
docker-compose logs -f app

# Restart
docker-compose restart

# Database backup
docker-compose exec -T db pg_dump -U hdl_user hdl_receipts > backup.sql

# Check status
docker-compose ps

# View stats
docker stats
```

---

## ✅ Ready to Go!

You're all set! Start receipting POs at **http://localhost:8501**

**First Time Users:**
1. Test with a sample docket
2. Verify extraction accuracy
3. Confirm Cin7 integration works
4. Train warehouse team

**Questions?** Check the full documentation or contact IT support.

---

**Happy Receipting! 📦✨**
