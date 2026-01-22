# 🔑 Where to Put Your Cin7 API Credentials

## Step-by-Step Guide

### Step 1: Get Your Cin7 Credentials

1. **Log into Cin7 Omni**
   - Go to: https://inventory.cin7.com
   - Use your Hardware Direct Cin7 account

2. **Navigate to API Settings**
   - Click **Settings** (gear icon)
   - Click **API** in the left menu

3. **Generate API Key**
   - Click **"Generate API Key"** button
   - You'll see two values:
     - **API Key** (looks like: `abc123def456...`)
     - **API Secret** (looks like: `xyz789ghi012...`)
   - **⚠️ IMPORTANT:** Copy both values immediately - the secret is only shown once!

### Step 2: Create Your .env File

1. **Navigate to the project folder**
   ```
   C:\Users\selwy\OneDrive\Desktop\PROJECTS HDL\Receipt
   ```

2. **Copy the example file**
   - Find the file: `.env.example`
   - Copy it and rename the copy to: `.env`
   - (Just `.env` - no `.example` at the end)

### Step 3: Add Your Credentials to .env

1. **Open `.env` file** in Notepad or any text editor

2. **Find these lines** (near the top):
   ```env
   CIN7_API_KEY=your-cin7-api-key-paste-here
   CIN7_API_SECRET=your-cin7-api-secret-paste-here
   ```

3. **Replace with your actual values**:
   ```env
   CIN7_API_KEY=abc123def456...
   CIN7_API_SECRET=xyz789ghi012...
   ```

   **EXAMPLE (with fake credentials):**
   ```env
   CIN7_API_KEY=4f3a2b1c5d6e7f8g9h0i
   CIN7_API_SECRET=9z8y7x6w5v4u3t2s1r0q
   ```

4. **Also change the JWT_SECRET** (scroll down a bit):

   Find:
   ```env
   JWT_SECRET=your-secret-key-change-in-production
   ```

   Change to any random string (32+ characters):
   ```env
   JWT_SECRET=hdl-po-receipt-2024-super-secret-key-xyz123
   ```

5. **Save the file**

### Step 4: Verify Your .env File

Your `.env` file should look like this:

```env
# =================================================================
# Cin7 HDL PO Receipt Tool - Configuration
# Hardware Direct Limited
# =================================================================

# ----------------------------------------------------------------
# IMPORTANT: PUT YOUR CIN7 CREDENTIALS HERE
# ----------------------------------------------------------------
CIN7_API_KEY=4f3a2b1c5d6e7f8g9h0i
CIN7_API_SECRET=9z8y7x6w5v4u3t2s1r0q

# ----------------------------------------------------------------
# Database Configuration
# ----------------------------------------------------------------
DB_HOST=localhost
DB_PORT=5432
DB_NAME=cin7_hdl_receipt
DB_USER=postgres
DB_PASSWORD=postgres

# ----------------------------------------------------------------
# Server Configuration
# ----------------------------------------------------------------
PORT=3001
NODE_ENV=development
CORS_ORIGIN=http://localhost:3000

# ----------------------------------------------------------------
# Authentication & Security
# ----------------------------------------------------------------
JWT_SECRET=hdl-po-receipt-2024-super-secret-key-xyz123
JWT_EXPIRES_IN=24h

# ----------------------------------------------------------------
# Cin7 API Settings
# ----------------------------------------------------------------
CIN7_BASE_URL=https://api.cin7.com/api

# ... rest of file ...
```

### Step 5: Start the Application

Open PowerShell or Command Prompt in the project folder:

```bash
docker-compose up -d
```

Wait 60 seconds for everything to start.

---

## 📍 Quick Reference

**File Location:**
```
C:\Users\selwy\OneDrive\Desktop\PROJECTS HDL\Receipt\.env
```

**What to Change:**
1. `CIN7_API_KEY` - Your Cin7 API Key
2. `CIN7_API_SECRET` - Your Cin7 API Secret
3. `JWT_SECRET` - Any random string (32+ characters)

**What NOT to Change:**
- `DB_HOST`, `DB_PORT`, `DB_NAME` - Leave as default
- `CIN7_BASE_URL` - Leave as `https://api.cin7.com/api`
- `PORT` - Leave as `3001`

---

## ✅ Testing Your Credentials

After starting with `docker-compose up -d`:

1. **Check health endpoint:**
   - Open browser: http://localhost:3001/health
   - Should show: `{"status":"ok","database":"connected"}`

2. **Try the app:**
   - Open browser: http://localhost:3000
   - Register a new account
   - Try to scan a docket
   - It should connect to Cin7 when matching PO

3. **Check logs if there's an error:**
   ```bash
   docker-compose logs backend
   ```

   Look for:
   - ✅ "Cin7 health check passed" = Good!
   - ❌ "401 Unauthorized" = Bad credentials
   - ❌ "CIN7_API_KEY must be set" = Missing from .env

---

## 🚨 Troubleshooting

### Error: "CIN7_API_KEY and CIN7_API_SECRET must be set"

**Problem:** The `.env` file isn't being read

**Solution:**
1. Make sure file is named exactly `.env` (not `.env.txt` or `.env.example`)
2. Make sure it's in the root folder: `C:\Users\selwy\OneDrive\Desktop\PROJECTS HDL\Receipt\.env`
3. Restart: `docker-compose down` then `docker-compose up -d`

### Error: "401 Unauthorized" from Cin7

**Problem:** Wrong API credentials

**Solution:**
1. Double-check you copied the full key and secret
2. Make sure there are no spaces before/after the values
3. Generate new credentials in Cin7 if needed

### Error: "Rate limit exceeded"

**Problem:** Too many API requests

**Solution:**
- Wait 1 minute and try again
- The app has built-in rate limiting, this shouldn't happen often

---

## 🔒 Security Notes

**NEVER:**
- ❌ Share your `.env` file with anyone
- ❌ Commit `.env` to Git (it's already in `.gitignore`)
- ❌ Put credentials in screenshots or documentation
- ❌ Email credentials in plain text

**DO:**
- ✅ Keep `.env` file secure
- ✅ Use different credentials for production
- ✅ Rotate credentials if compromised
- ✅ Only share credentials through secure channels (password manager, encrypted email)

---

## 📞 Need Help?

1. **Check the logs:**
   ```bash
   docker-compose logs -f backend
   ```

2. **Verify the file exists:**
   ```bash
   dir .env
   ```

3. **View the configuration (credentials hidden):**
   ```bash
   docker exec hdl-po-receipt-backend env | findstr CIN7
   ```
   Should show:
   ```
   CIN7_API_KEY=abc123...
   CIN7_API_SECRET=xyz789...
   CIN7_BASE_URL=https://api.cin7.com/api
   ```

---

**Last Updated:** January 2026
**For:** Hardware Direct Limited
**App:** Cin7 HDL PO Receipt Tool
