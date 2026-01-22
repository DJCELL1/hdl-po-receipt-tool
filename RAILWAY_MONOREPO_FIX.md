# 🔧 Railway Monorepo Build Fix

**Issue:** Railway build failed because it tried to build both services from the root.

**Solution:** Configure Railway to deploy backend and frontend as separate services.

---

## ✅ What's Been Fixed

- ✅ Removed root-level `nixpacks.toml` and `Procfile`
- ✅ Added `backend/nixpacks.toml` - Backend build config
- ✅ Added `frontend/nixpacks.toml` - Frontend build config
- ✅ Added `backend/railway.json` - Backend Railway config
- ✅ Added `frontend/railway.json` - Frontend Railway config
- ✅ Added `serve` to frontend dependencies for production serving

---

## 🚀 How to Deploy (Updated Instructions)

### Step 1: Delete Existing Railway Project (if you created one)

1. Go to https://railway.app/dashboard
2. Click on your project (if exists)
3. Go to Settings → Danger Zone → Delete Project

### Step 2: Create New Railway Project

1. Click "New Project"
2. Select "Empty Project" (not "Deploy from GitHub" yet!)

### Step 3: Add Services One by One

#### Add Backend Service:

1. In your empty project, click "+ New"
2. Select "GitHub Repo"
3. Choose: `DJCELL1/hdl-po-receipt-tool`
4. **IMPORTANT:** Set "Root Directory" to `backend`
5. Click "Deploy"

**Set Backend Variables:**
- Click on the backend service
- Go to "Variables" tab
- Add:
  ```
  CIN7_API_KEY=your-actual-cin7-api-key
  CIN7_API_SECRET=your-actual-cin7-api-secret
  JWT_SECRET=change-this-random-string
  NODE_ENV=production
  PORT=3001
  ```

#### Add PostgreSQL:

1. Click "+ New" in project
2. Select "Database"
3. Choose "PostgreSQL"
4. It automatically links to backend

**Add DATABASE_URL to backend:**
- Go to backend service → Variables
- Add: `DATABASE_URL` = `${{Postgres.DATABASE_URL}}`

#### Add Frontend Service:

1. Click "+ New"
2. Select "GitHub Repo"
3. Choose: `DJCELL1/hdl-po-receipt-tool`
4. **IMPORTANT:** Set "Root Directory" to `frontend`
5. Click "Deploy"

**Set Frontend Variables:**
- Click on the frontend service
- Go to "Variables" tab
- Add:
  ```
  REACT_APP_API_URL=https://your-backend-url.railway.app
  NODE_ENV=production
  ```

**To get backend URL:**
1. Click on backend service
2. Go to "Settings" tab
3. Scroll to "Domains"
4. Copy the public domain
5. Use it in `REACT_APP_API_URL`

---

## 🔄 Alternative: Railway CLI (Easier)

If you have Railway CLI installed:

```powershell
cd "C:\Users\selwy\OneDrive\Desktop\PROJECTS HDL\Receipt"

# Login
railway login

# Create project
railway init

# Link backend
cd backend
railway link
railway up

# Link frontend (in new terminal)
cd ../frontend
railway link
railway up

# Add PostgreSQL
railway add --database postgres

# Set variables via Railway dashboard
```

---

## ✅ How to Verify It's Working

### Backend Deployed:
1. Get backend URL from Railway
2. Open: `https://your-backend-url/health`
3. Should see: `{"status":"ok","database":"connected"}`

### Frontend Deployed:
1. Get frontend URL from Railway
2. Open in browser
3. Should see Hardware Direct dashboard

### Everything Connected:
1. Open frontend URL
2. Click "Scan New Delivery Docket"
3. Upload a test image
4. If OCR works = ✅ Backend connected!

---

## 🐛 Common Issues

### "Root directory not found"
**Fix:** Make sure you set "Root Directory" when adding each service:
- Backend service → Root Directory: `backend`
- Frontend service → Root Directory: `frontend`

### "Module not found" errors
**Fix:** Railway is trying to build from wrong directory. Delete service and recreate with correct Root Directory.

### Frontend can't reach backend
**Fix:**
1. Check `REACT_APP_API_URL` in frontend variables
2. Must match backend public URL exactly
3. Redeploy frontend after changing variables

### Database connection failed
**Fix:**
1. Make sure PostgreSQL service is added
2. Check `DATABASE_URL` is set in backend variables
3. Format: `${{Postgres.DATABASE_URL}}` (Railway fills this)

---

## 📋 Quick Checklist

Before deploying:
- [ ] Delete old Railway project (if exists)
- [ ] Create new empty project
- [ ] Add backend service (Root Directory: `backend`)
- [ ] Set all backend variables
- [ ] Add PostgreSQL
- [ ] Link `DATABASE_URL` to backend
- [ ] Add frontend service (Root Directory: `frontend`)
- [ ] Set frontend `REACT_APP_API_URL`
- [ ] Verify backend health endpoint
- [ ] Verify frontend loads
- [ ] Test upload/OCR

---

## 🎯 Environment Variables Summary

### Backend Service
```
CIN7_API_KEY=your-cin7-username
CIN7_API_SECRET=your-cin7-key
JWT_SECRET=random-string
DATABASE_URL=${{Postgres.DATABASE_URL}}
NODE_ENV=production
PORT=3001
```

### Frontend Service
```
REACT_APP_API_URL=https://backend-service-name.railway.app
NODE_ENV=production
```

### PostgreSQL
```
(Railway manages this automatically)
```

---

## 🔧 What Changed in the Code

**Files Removed:**
- `/nixpacks.toml` (was causing conflicts)
- `/Procfile` (not needed with nixpacks)
- `/railway.json` (moved to service directories)

**Files Added:**
- `backend/nixpacks.toml` - Backend build config
- `backend/railway.json` - Backend Railway config
- `frontend/nixpacks.toml` - Frontend build config
- `frontend/railway.json` - Frontend Railway config

**Files Modified:**
- `frontend/package.json` - Added `serve` dependency

---

## 📖 Railway Monorepo Documentation

Railway automatically detects monorepos when you:
1. Set the "Root Directory" for each service
2. Have package.json in each service directory
3. Configure build commands in nixpacks.toml

Our structure:
```
hdl-po-receipt-tool/
├── backend/           ← Deploy this as one service
│   ├── nixpacks.toml
│   ├── railway.json
│   └── package.json
└── frontend/          ← Deploy this as another service
    ├── nixpacks.toml
    ├── railway.json
    └── package.json
```

---

## ✅ After Successful Deployment

Your project should have:
- ✅ 1 backend service (Node.js)
- ✅ 1 frontend service (React)
- ✅ 1 PostgreSQL database
- ✅ All 3 services showing "Deployed" status
- ✅ Backend health check passes
- ✅ Frontend loads in browser

---

## 🎉 Ready to Try Again?

1. Delete old Railway project
2. Follow "How to Deploy (Updated Instructions)" above
3. Deploy backend first, then PostgreSQL, then frontend
4. Set all environment variables
5. Verify everything works

**This should fix the build failure!** 🚀

---

**Still having issues?** Check Railway deployment logs for specific error messages.
