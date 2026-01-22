# 🔧 Hardware Direct - PO Receipt Tool Setup Instructions

## ⚡ Quick Setup (For Hardware Direct Team)

### What You Need

1. **Docker Desktop** installed on your Windows computer
2. **Your Cin7 Omni API credentials** (API Key + API Secret)

---

## 📝 Step-by-Step Setup

### Step 1: Get Your Cin7 API Credentials

1. **Login to Cin7 Omni**
   - Go to: https://inventory.cin7.com
   - Use your Hardware Direct Cin7 account

2. **Generate API Credentials**
   - Click **Settings** (⚙️ gear icon)
   - Click **API** in the sidebar
   - Click **"Generate API Key"** button
   - **COPY BOTH VALUES:**
     - API Key (long string of letters/numbers)
     - API Secret (another long string)
   - **⚠️ IMPORTANT:** The secret is only shown once! Save it somewhere safe.

### Step 2: Configure the Application

1. **Find the `.env.example` file** in this folder:
   ```
   C:\Users\selwy\OneDrive\Desktop\PROJECTS HDL\Receipt\.env.example
   ```

2. **Make a copy** and rename it to `.env` (just `.env`, no `.example`)

3. **Open `.env` in Notepad**

4. **Find these two lines** (near the top):
   ```env
   CIN7_API_KEY=your-cin7-api-key-paste-here
   CIN7_API_SECRET=your-cin7-api-secret-paste-here
   ```

5. **Replace with your actual credentials**:
   ```env
   CIN7_API_KEY=paste-your-actual-api-key-here
   CIN7_API_SECRET=paste-your-actual-api-secret-here
   ```

6. **Also change the JWT_SECRET** (scroll down to find it):
   ```env
   JWT_SECRET=hardware-direct-2024-secret-key-change-this-to-anything-random
   ```

7. **Save the file**

**👉 For detailed instructions, see:** [WHERE_TO_PUT_CIN7_CREDENTIALS.md](WHERE_TO_PUT_CIN7_CREDENTIALS.md)

### Step 3: Start the Application

1. **Open PowerShell** in this folder
   - Right-click in the folder
   - Choose "Open in Terminal" or "Open PowerShell window here"

2. **Run this command:**
   ```powershell
   docker-compose up -d
   ```

3. **Wait 60 seconds** for everything to start

### Step 4: Access the Application

1. **On your computer:**
   - Open web browser
   - Go to: **http://localhost:3000**

2. **On your phone (optional):**
   - Find your computer's IP address (run `ipconfig` in PowerShell)
   - On your phone's browser, go to: **http://[your-computer-ip]:3000**
   - Example: http://192.168.1.100:3000

### Step 5: Create Your Account

1. Click **"Register"**
2. Enter your email and password
3. Enter your name (optional)
4. Click **"Register"**
5. You're in! 🎉

---

## 📱 Daily Use

### To Scan a Delivery Docket:

1. **Login** to http://localhost:3000
2. Click **"📦 Scan New Delivery Docket"**
3. **Take a photo** of the docket (or upload an image/PDF)
4. **Review** the extracted information (supplier, PO, items)
5. **Confirm** the PO match
6. **Verify** line items
7. **Submit** to receipt into Cin7

The whole process takes 30-60 seconds!

### To View Receipt History:

1. **Login** to the app
2. Click **"📋 View Receipt History"**
3. See all your past receipts with status

---

## ✅ How to Know It's Working

### Health Check

Open in browser: **http://localhost:3001/health**

Should show:
```json
{"status":"ok","database":"connected"}
```

### Check Running Services

In PowerShell, run:
```powershell
docker-compose ps
```

Should show 3 services running:
- ✅ hdl-po-receipt-db
- ✅ hdl-po-receipt-backend
- ✅ hdl-po-receipt-frontend

### Test the Full Flow

1. Login to the app
2. Upload a test docket
3. Try to match a PO
4. If it finds the PO in Cin7 = **Everything is working!** ✅

---

## 🔧 Troubleshooting

### "Can't connect to app" / Page won't load

```powershell
# Restart everything
docker-compose down
docker-compose up -d

# Wait 60 seconds, then try again
```

### "Invalid Cin7 credentials" error

1. Check your `.env` file
2. Make sure API Key and Secret are correct
3. No spaces before/after the values
4. Restart: `docker-compose down` then `docker-compose up -d`

### "Duplicate docket" warning

- This is normal! It prevents accidental double-receipting
- Check receipt history to see if you already processed this docket
- If you need to receipt again, use the "Allow Override" checkbox

### OCR not reading docket clearly

- Make sure photo is clear, well-lit, not blurry
- Try uploading the PDF version if available
- You can manually edit any fields after extraction

### How to see logs (if something's wrong)

```powershell
docker-compose logs -f backend
```

Press `Ctrl+C` to exit logs

---

## 🔒 Security Tips

**DO:**
- ✅ Keep your `.env` file secure
- ✅ Use strong passwords for user accounts
- ✅ Change the JWT_SECRET to something random

**DON'T:**
- ❌ Share your `.env` file
- ❌ Email API credentials in plain text
- ❌ Commit `.env` to Git (it's already ignored)

---

## 👥 Multiple Users

### Adding More Users

1. Share the app URL with them
2. They go to http://localhost:3000
3. They click "Register" and create their account
4. No admin approval needed!

### Each User Gets:

- Their own login
- Their own receipt history
- Access to all Cin7 POs (shared Cin7 account)

---

## 📊 What Happens When You Receipt a Docket

1. **Photo captured** → OCR extracts text
2. **PO matched** → Searches Cin7 for matching Purchase Order
3. **Lines matched** → Maps docket items to PO line items
4. **Quantities updated** → Updates ReceivedQty in Cin7
5. **Receipt saved** → Stored in local database for history
6. **Cin7 updated** → Stock levels updated in Cin7 Omni

All in real-time!

---

## 🎨 Hardware Direct Branding

The app features Hardware Direct's orange/charcoal color scheme:
- Orange buttons and accents
- Professional industrial look
- Mobile-optimized for warehouse use

---

## 📞 Need More Help?

### Documentation Files

| File | What's In It |
|------|--------------|
| **HDL_README.md** | This file - Quick start for HDL team |
| **WHERE_TO_PUT_CIN7_CREDENTIALS.md** | Detailed credential setup |
| **QUICK_START.md** | Full setup guide |
| **ADMIN_GUIDE.md** | Advanced admin features & troubleshooting |

### Commands Reference

| Command | What It Does |
|---------|--------------|
| `docker-compose up -d` | Start the app |
| `docker-compose down` | Stop the app |
| `docker-compose ps` | Check if running |
| `docker-compose logs backend` | View backend logs |
| `docker-compose logs -f backend` | Watch logs live |

### URLs to Bookmark

- **App:** http://localhost:3000
- **Health Check:** http://localhost:3001/health
- **Cin7 Omni:** https://inventory.cin7.com

---

## 🔄 Updating the App

If you receive an updated version:

```powershell
# Stop current version
docker-compose down

# Rebuild with new code
docker-compose build

# Start new version
docker-compose up -d
```

Your data (receipts, users) will be preserved!

---

## 💾 Backup & Data

### Where Data is Stored

- **Receipts:** PostgreSQL database (in Docker)
- **Uploaded dockets:** `backend/uploads/` folder
- **User accounts:** PostgreSQL database

### How to Backup

```powershell
# Backup database
docker exec hdl-po-receipt-db pg_dump -U postgres cin7_hdl_receipt > backup_$(Get-Date -Format "yyyy-MM-dd").sql

# Backup uploaded files
Copy-Item -Path "backend\uploads" -Destination "backup_uploads_$(Get-Date -Format "yyyy-MM-dd")" -Recurse
```

---

## ✨ Features Summary

**For Warehouse Team:**
- 📷 Camera capture on phone
- 🔍 Automatic text extraction
- ⚡ Instant PO matching
- ✅ Simple confirmation flow
- 📋 Receipt history

**Smart Features:**
- 🧠 Handles backorder suffixes (PO-12345A, PO-12345B, etc.)
- 🎯 Fuzzy matching (finds items even if SKU slightly wrong)
- 🛡️ Duplicate prevention
- 📊 Over/under delivery warnings

**Integration:**
- 🔄 Real-time Cin7 updates
- 🔒 Secure API communication
- ⚡ Rate limiting (respects Cin7 limits)
- 🔁 Automatic retry on errors

---

**Built for:** Hardware Direct Limited
**Powered by:** Cin7 Omni API
**Version:** 1.0.0
**Last Updated:** January 2026

**Questions?** Check the documentation files or contact your IT administrator.

---

**🎉 You're all set! Start scanning dockets and save hours of manual data entry.**
