# 🔧 Hardware Direct - PO Receipt Tool

**Streamline stock receiving by scanning delivery dockets**

Powered by Cin7 Omni | Built for Hardware Direct Limited

---

## 🚀 What Does This Do?

This app lets you:
1. **📷 Take a photo** of a delivery docket with your phone
2. **🤖 Automatically extract** supplier, PO number, and line items
3. **✅ Match to Cin7** Purchase Orders automatically
4. **📦 Receipt stock** directly into Cin7 Omni

**No more manual data entry!**

---

## ⚡ Quick Start (5 Minutes)

### 1️⃣ Put Your Cin7 Credentials in the .env File

**READ THIS FIRST:** [WHERE_TO_PUT_CIN7_CREDENTIALS.md](WHERE_TO_PUT_CIN7_CREDENTIALS.md)

**Quick version:**
1. Copy `.env.example` to `.env`
2. Open `.env` in Notepad
3. Replace `your-cin7-api-key-paste-here` with your actual API key
4. Replace `your-cin7-api-secret-paste-here` with your actual API secret
5. Save the file

### 2️⃣ Start the App

Open PowerShell in this folder and run:

```powershell
docker-compose up -d
```

Wait 60 seconds for everything to start.

### 3️⃣ Open the App

Open your web browser and go to:

**http://localhost:3000**

### 4️⃣ Create Your Account

1. Click "Register"
2. Enter your email and password
3. Start scanning dockets!

---

## 📱 How to Use

### On Your Phone (Recommended)

1. Open **http://[your-computer-ip]:3000** on your phone
2. Login with your account
3. Click "📦 Scan New Delivery Docket"
4. Take a photo of the docket
5. Review the extracted information
6. Confirm and submit to Cin7

### On Your Computer

1. Open **http://localhost:3000**
2. Upload a photo or PDF of the docket
3. Follow the same steps as above

---

## 🎯 Features

✅ **Mobile camera capture** - Use your phone to scan dockets
✅ **OCR text extraction** - Automatically reads supplier, PO, items
✅ **Smart PO matching** - Handles backorders (PO-12345A, PO-12345B, etc.)
✅ **Fuzzy matching** - Finds items even if SKU is slightly different
✅ **Duplicate prevention** - Won't accidentally receipt twice
✅ **Receipt history** - See all past receipts
✅ **Cin7 integration** - Updates stock levels in real-time

---

## 🔧 Troubleshooting

### App Won't Start

```bash
# Check if Docker is running
docker --version

# Check what's wrong
docker-compose logs
```

### Can't Connect to Cin7

1. Check your credentials in `.env` file
2. Make sure you have internet connection
3. Verify Cin7 is accessible: https://inventory.cin7.com

### OCR Not Reading Docket Clearly

- Make sure photo is clear and well-lit
- Try uploading the PDF instead of a photo
- You can manually edit the extracted information

### "Duplicate Docket" Error

- This means you already receipted this docket
- Check receipt history to confirm
- Use "Allow Override" if you need to receipt again

---

## 📊 System Requirements

**To Run the App:**
- Windows 10/11 with Docker Desktop
- 4 GB RAM minimum
- Internet connection (for Cin7 API)

**To Use the App:**
- Any modern web browser
- Smartphone with camera (optional, for mobile scanning)

---

## 🔒 Security

- All passwords are encrypted
- Cin7 credentials stored securely in `.env` file
- Never share your `.env` file
- Each user has their own login

---

## 📁 Important Files

| File | What It Does |
|------|--------------|
| `.env` | **⚠️ YOUR CIN7 CREDENTIALS GO HERE** |
| `WHERE_TO_PUT_CIN7_CREDENTIALS.md` | Step-by-step credential setup |
| `docker-compose.yml` | App configuration |
| `QUICK_START.md` | Detailed setup guide |
| `ADMIN_GUIDE.md` | Advanced admin features |

---

## 🆘 Getting Help

### Check the Logs

```bash
docker-compose logs -f backend
```

### Restart Everything

```bash
docker-compose down
docker-compose up -d
```

### Check if Services are Running

```bash
docker-compose ps
```

Should show:
- ✅ hdl-po-receipt-db (postgres)
- ✅ hdl-po-receipt-backend (backend)
- ✅ hdl-po-receipt-frontend (frontend)

### Test Health

Open in browser: http://localhost:3001/health

Should show: `{"status":"ok","database":"connected"}`

---

## 💼 For Hardware Direct Team

### Daily Use

1. Open http://localhost:3000 (or phone browser)
2. Login with your account
3. Scan dockets as they arrive
4. Check receipt history at end of day

### Adding New Users

1. Share the app URL: http://localhost:3000
2. They click "Register"
3. They create their own account
4. No admin approval needed

### Viewing All Receipts

Currently each user sees only their receipts. To see all receipts, access the database:

```bash
docker exec -it hdl-po-receipt-db psql -U postgres -d cin7_hdl_receipt
```

Then run:
```sql
SELECT * FROM receipts ORDER BY created_at DESC LIMIT 20;
```

---

## 📞 Support Contacts

**Cin7 API Issues:**
- Cin7 Support: https://support.cin7.com
- Check API Status: https://status.cin7.com

**App Technical Issues:**
- Check documentation in this folder
- Review logs: `docker-compose logs`

**Database Backup:**
```bash
docker exec hdl-po-receipt-db pg_dump -U postgres cin7_hdl_receipt > backup.sql
```

---

## 🎨 Hardware Direct Branding

The app uses Hardware Direct's orange/amber color scheme:
- Primary: Orange (#d97706)
- Secondary: Charcoal (#1f2937)
- Accent: Amber (#f59e0b)

---

## ⚙️ Advanced Options

For advanced configuration, backup, monitoring, and troubleshooting, see:
- **[ADMIN_GUIDE.md](ADMIN_GUIDE.md)** - Complete admin documentation
- **[API_DOCUMENTATION.md](API_DOCUMENTATION.md)** - API reference
- **[SETUP_CHECKLIST.md](SETUP_CHECKLIST.md)** - Verification checklist

---

**Version:** 1.0.0
**Built for:** Hardware Direct Limited
**Powered by:** Cin7 Omni API
**Last Updated:** January 2026

---

## 🚦 Status Indicators

When everything is working:
- ✅ Health check returns OK
- ✅ Can login to app
- ✅ Can scan/upload dockets
- ✅ Can search for POs in Cin7
- ✅ Can create receipts

If you see ❌ for any of these, check the troubleshooting section above.

---

**Made with 🔧 for Hardware Direct**
