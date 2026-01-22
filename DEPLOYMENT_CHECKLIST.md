# ✅ Railway Deployment Checklist

Use this checklist to ensure a smooth deployment to Railway.

---

## 📋 Pre-Deployment Checklist

### 1. Cin7 Credentials Ready

- [ ] I have my Cin7 API username (goes in `CIN7_API_KEY`)
- [ ] I have my Cin7 API key (goes in `CIN7_API_SECRET`)
- [ ] I've tested these credentials work (logged into Cin7)

**Where to get them:**
1. Login to Cin7: https://inventory.cin7.com
2. Go to Settings → API
3. Click "Generate API Key"
4. Copy both values

---

### 2. Railway Account

- [ ] I have a Railway account
- [ ] I've connected my GitHub account to Railway
- [ ] I can access: https://railway.app/dashboard

**Don't have an account yet?**
1. Go to https://railway.app
2. Click "Login with GitHub"
3. Authorize Railway

---

### 3. GitHub Repository

- [ ] Code is pushed to: https://github.com/DJCELL1/hdl-po-receipt-tool
- [ ] I can see all files on GitHub
- [ ] Latest commits are visible

**Verify:**
```powershell
cd "C:\Users\selwy\OneDrive\Desktop\PROJECTS HDL\Receipt"
git status
git log -1
```

---

## 🚀 Deployment Steps Checklist

### Step 1: Create Railway Project

- [ ] Logged into Railway
- [ ] Clicked "New Project"
- [ ] Selected "Deploy from GitHub repo"
- [ ] Chose `DJCELL1/hdl-po-receipt-tool`
- [ ] Railway started building

---

### Step 2: Add PostgreSQL Database

- [ ] Clicked "+ New" in project
- [ ] Selected "Database"
- [ ] Chose "PostgreSQL"
- [ ] PostgreSQL service is running
- [ ] I can see `DATABASE_URL` in PostgreSQL variables

---

### Step 3: Configure Backend Service

- [ ] Clicked on backend service
- [ ] Went to "Variables" tab
- [ ] Added all required variables:

**Backend Variables:**
```
- [ ] CIN7_API_KEY=(my actual Cin7 api_username)
- [ ] CIN7_API_SECRET=(my actual Cin7 api_key)
- [ ] JWT_SECRET=(random string, changed from default)
- [ ] DATABASE_URL=${{Postgres.DATABASE_URL}}
- [ ] NODE_ENV=production
- [ ] PORT=3001
```

**How to add variables:**
1. Click "New Variable"
2. Type name (e.g., `CIN7_API_KEY`)
3. Type value (e.g., your actual key)
4. Click "Add"
5. Repeat for each variable

---

### Step 4: Configure Frontend Service

- [ ] Clicked on frontend service
- [ ] Went to "Variables" tab
- [ ] Added frontend variables:

**Frontend Variables:**
```
- [ ] REACT_APP_API_URL=(my backend URL from Railway)
- [ ] NODE_ENV=production
```

**To find backend URL:**
1. Click on backend service
2. Go to "Settings" tab
3. Scroll to "Domains"
4. Copy the URL (e.g., `https://hdl-po-receipt-backend-production-abc123.up.railway.app`)
5. Paste into `REACT_APP_API_URL`

---

### Step 5: Deploy and Verify

- [ ] Both services show "Deployed" status
- [ ] No build errors in logs
- [ ] Backend health check passes
- [ ] Frontend loads in browser

**Verify backend health:**
1. Get backend URL from Railway
2. Open: `https://your-backend-url/health`
3. Should see: `{"status":"ok","database":"connected"}`

**Verify frontend:**
1. Get frontend URL from Railway
2. Open in browser
3. Should see Hardware Direct dashboard

---

## 🧪 Testing Checklist

### Test 1: Frontend Loads

- [ ] Frontend URL opens
- [ ] No console errors (press F12)
- [ ] Orange Hardware Direct theme visible
- [ ] "Scan New Delivery Docket" button visible

---

### Test 2: Upload Works

- [ ] Click "Scan New Delivery Docket"
- [ ] Upload a test image
- [ ] OCR extraction completes
- [ ] Data appears on Review screen

---

### Test 3: Cin7 Connection

- [ ] Enter a real PO number
- [ ] Click "Match PO"
- [ ] Cin7 search executes
- [ ] Results returned (or "not found" if invalid PO)

**This confirms:**
- ✅ Backend can reach Cin7 API
- ✅ Credentials are correct
- ✅ Network connectivity works

---

### Test 4: Database Works

- [ ] Complete a test receipt
- [ ] Go to "Receipt History"
- [ ] Your test receipt appears
- [ ] Can click to view details

**This confirms:**
- ✅ PostgreSQL connected
- ✅ Migrations ran successfully
- ✅ Data persists

---

## 🔧 Troubleshooting Checklist

### Issue: Build Failed

- [ ] Check deployment logs in Railway
- [ ] Look for "error" or "failed" messages
- [ ] Verify all config files are in GitHub
- [ ] Try redeploying

**How to check logs:**
1. Click on service
2. Go to "Deployments" tab
3. Click latest deployment
4. Click "View Logs"

---

### Issue: Backend Won't Start

- [ ] Verify `PORT=3001` is set
- [ ] Check `DATABASE_URL` is set
- [ ] Check Cin7 credentials are correct
- [ ] Look at backend logs for errors

**Common fixes:**
```
- Missing environment variable → Add it
- Typo in variable → Fix spelling
- Wrong port → Set PORT=3001
```

---

### Issue: Frontend Can't Connect to Backend

- [ ] Check `REACT_APP_API_URL` matches backend URL
- [ ] Verify backend is running (green status)
- [ ] Check CORS errors in browser console (F12)
- [ ] Redeploy frontend after changing variables

**Fix:**
1. Get correct backend URL from Railway
2. Update `REACT_APP_API_URL` in frontend variables
3. Redeploy frontend (Railway → frontend service → "Deploy")

---

### Issue: Database Connection Failed

- [ ] PostgreSQL service is running
- [ ] `DATABASE_URL` is set in backend
- [ ] Format is: `${{Postgres.DATABASE_URL}}`
- [ ] Check backend logs for connection errors

**Fix:**
```
DATABASE_URL should be:
${{Postgres.DATABASE_URL}}

NOT:
- Empty
- A real URL (Railway fills it automatically)
- Anything else
```

---

### Issue: Cin7 API Errors

- [ ] Credentials are correct (check Cin7 dashboard)
- [ ] No typos in `CIN7_API_KEY` or `CIN7_API_SECRET`
- [ ] Backend logs show what error Cin7 returned
- [ ] Try testing credentials in Cin7 web interface

**Common errors:**
```
401 Unauthorized → Wrong credentials
429 Too Many Requests → Rate limited (wait)
404 Not Found → PO doesn't exist in Cin7
```

---

## 📱 Mobile Testing Checklist

- [ ] Open frontend URL on phone
- [ ] Layout looks good on mobile
- [ ] Can access camera
- [ ] Can take photo of docket
- [ ] Upload works
- [ ] Buttons are easy to tap

---

## 🎯 Production Readiness Checklist

### Security

- [ ] `JWT_SECRET` is changed from default
- [ ] `.env` file not in GitHub (check .gitignore)
- [ ] Cin7 credentials only in Railway (not in code)
- [ ] HTTPS enabled (Railway does this automatically)

---

### Performance

- [ ] Health check endpoint responds quickly
- [ ] Upload/OCR completes in <10 seconds
- [ ] PO matching completes in <5 seconds
- [ ] Database queries are fast

---

### Monitoring

- [ ] Can access Railway deployment logs
- [ ] Can see backend logs
- [ ] Can see frontend logs
- [ ] Health check endpoint monitored

**Bookmark these:**
```
Railway Dashboard: https://railway.app/dashboard
Backend Logs: Railway → backend service → Logs
Frontend Logs: Railway → frontend service → Logs
Health Check: https://your-backend-url/health
```

---

### Documentation

- [ ] Team knows the frontend URL
- [ ] Team knows how to use the app
- [ ] Instructions saved for future reference
- [ ] Know how to check logs if issues occur

---

## ✅ Final Verification

### All Green?

- [ ] Frontend status: Deployed ✅
- [ ] Backend status: Deployed ✅
- [ ] PostgreSQL status: Running ✅
- [ ] Health check: OK ✅
- [ ] Test upload: Works ✅
- [ ] Cin7 connection: Works ✅
- [ ] Mobile access: Works ✅

---

### Share with Team

- [ ] Frontend URL shared
- [ ] Instructions provided
- [ ] Demo completed
- [ ] Questions answered

**Example message:**
```
🎉 Our new PO Receipt Tool is live!

📱 Access it here:
https://your-frontend-url.railway.app

How to use:
1. Open URL on your phone
2. Click "Scan New Delivery Docket"
3. Take photo of docket
4. Review extracted data
5. Confirm and submit

The app will automatically:
- Extract supplier, PO, items
- Find matching PO in Cin7
- Create the receipt
- Update Cin7

Questions? Check the guides or ask me!
```

---

## 🎉 Deployment Complete!

If all items are checked above, you're done! 🚀

Your Hardware Direct PO Receipt Tool is:
- ✅ Deployed to Railway
- ✅ Accessible from anywhere
- ✅ Connected to Cin7
- ✅ Storing data in PostgreSQL
- ✅ Ready for production use

---

## 🔄 Future Updates

When you want to update the app:

1. Make changes locally
2. Test locally: `docker-compose up -d`
3. Commit: `git add . && git commit -m "Update"`
4. Push: `git push origin main`
5. Railway auto-deploys in 2-3 minutes

- [ ] I know how to update the app
- [ ] I know Railway auto-deploys on git push
- [ ] I know how to check deployment status

---

## 📚 Reference Documents

Keep these handy:

| Document | When to Use |
|----------|-------------|
| **RAILWAY_QUICK_START.md** | Quick 5-minute deploy |
| **DEPLOY_TO_RAILWAY.md** | Detailed deployment guide |
| **RAILWAY_ARCHITECTURE.md** | How everything works |
| **DEPLOYMENT_SUMMARY.md** | Overview and links |
| **START_HERE.md** | Local development |
| **NO_AUTH_MODE.md** | Authentication info |

---

**Need help?** Re-check this list or review the deployment guides!

**All done?** Congratulations! 🎉 Your app is live!
