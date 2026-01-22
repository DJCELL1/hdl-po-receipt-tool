# 🚂 Deploy to Railway - Step by Step Guide

Your Hardware Direct PO Receipt Tool is ready to deploy to Railway!

---

## 🎯 What is Railway?

Railway is a cloud platform that makes it easy to deploy apps. They have:
- ✅ Free tier (perfect for getting started)
- ✅ PostgreSQL database included
- ✅ Automatic HTTPS
- ✅ Easy environment variable management

---

## ⚡ Quick Deploy (5 Minutes)

### Step 1: Create Railway Account

1. **Go to:** https://railway.app
2. **Click:** "Start a New Project"
3. **Sign up with GitHub** (easiest option)
4. **Authorize Railway** to access your GitHub

---

### Step 2: Deploy from GitHub

#### Option A: Use Railway Web Interface (Easiest)

1. **In Railway Dashboard:**
   - Click "New Project"
   - Select "Deploy from GitHub repo"
   - Choose: `DJCELL1/hdl-po-receipt-tool`

2. **Railway will automatically:**
   - Detect it's a Node.js app
   - Build frontend and backend
   - Deploy everything

3. **Add PostgreSQL Database:**
   - Click "New" in your project
   - Select "Database"
   - Choose "PostgreSQL"
   - Railway will automatically create and link it

---

### Step 3: Set Environment Variables

Railway needs your Cin7 credentials. Here's how:

1. **Click on your backend service** (in Railway dashboard)
2. **Go to "Variables" tab**
3. **Add these variables:**

```
CIN7_API_KEY=your-actual-cin7-api-key
CIN7_API_SECRET=your-actual-cin7-api-secret
JWT_SECRET=your-secure-random-string-change-this
DATABASE_URL=${{Postgres.DATABASE_URL}}
NODE_ENV=production
PORT=3001
```

**Important Notes:**
- `DATABASE_URL` will auto-fill from your PostgreSQL service
- Use your REAL Cin7 credentials (same as in local .env)
- Change `JWT_SECRET` to a random string (even though we don't use auth)

4. **Click on your frontend service**
5. **Add these variables:**

```
REACT_APP_API_URL=https://hdl-po-receipt-backend.railway.app
NODE_ENV=production
```

**Note:** Replace `hdl-po-receipt-backend` with your actual backend URL from Railway

---

### Step 4: Deploy!

1. **Railway will automatically deploy** when you push to GitHub
2. **First deployment takes 3-5 minutes**
3. **Watch the logs** to see progress

---

## 🌐 Access Your App

Once deployed, Railway gives you URLs:

**Frontend URL:**
```
https://hdl-po-receipt-tool.railway.app
```

**Backend URL:**
```
https://hdl-po-receipt-backend.railway.app
```

**Your app will be live at the frontend URL!**

---

## 🔧 Advanced: Railway CLI Deploy

If you prefer command line:

### Install Railway CLI

```powershell
npm install -g @railway/cli
```

### Login

```powershell
railway login
```

### Initialize Project

```powershell
cd "C:\Users\selwy\OneDrive\Desktop\PROJECTS HDL\Receipt"
railway init
```

### Link to Your Project

```powershell
railway link
```

### Add PostgreSQL

```powershell
railway add --database postgres
```

### Set Environment Variables

```powershell
railway variables set CIN7_API_KEY=your-actual-key
railway variables set CIN7_API_SECRET=your-actual-secret
railway variables set JWT_SECRET=your-random-string
```

### Deploy

```powershell
railway up
```

---

## 📊 Railway Project Structure

Railway will create 3 services:

1. **Frontend Service** (React app)
   - Serves the web interface
   - Public URL for users to access

2. **Backend Service** (Node.js API)
   - Handles API requests
   - Connects to Cin7
   - Processes OCR

3. **PostgreSQL Database**
   - Stores receipts, uploads, audit logs
   - Automatically backed up by Railway

---

## 🔒 Environment Variables Checklist

Make sure you set ALL of these:

### Backend Variables:
- ✅ `CIN7_API_KEY` - Your Cin7 API username
- ✅ `CIN7_API_SECRET` - Your Cin7 API key
- ✅ `JWT_SECRET` - Random string for sessions
- ✅ `DATABASE_URL` - Auto-set by Railway PostgreSQL
- ✅ `NODE_ENV` - Set to "production"
- ✅ `PORT` - Set to "3001"

### Frontend Variables:
- ✅ `REACT_APP_API_URL` - Your backend Railway URL
- ✅ `NODE_ENV` - Set to "production"

---

## 🆘 Troubleshooting

### Build Failed?

**Check the logs:**
- Click on your service in Railway
- Go to "Deployments" tab
- Click on the failed deployment
- Read the error logs

**Common issues:**
- Missing environment variables
- Incorrect `REACT_APP_API_URL` (must match backend URL)
- Node version mismatch (Railway uses Node 20)

### Can't Connect to Cin7?

1. **Check environment variables** in Railway
2. **Verify credentials** are correct
3. **Check backend logs** for API errors

### Frontend Shows "Cannot connect to backend"?

1. **Check `REACT_APP_API_URL`** in frontend variables
2. **Make sure backend is deployed** and running
3. **Check CORS settings** in backend (should allow Railway URLs)

### Database Connection Failed?

1. **Make sure PostgreSQL service is added**
2. **Check `DATABASE_URL` is set** in backend variables
3. **Railway auto-links databases** - it should just work

---

## 💰 Pricing

**Railway Free Tier:**
- $5 free credit per month
- Enough for development/testing
- No credit card required to start

**If you need more:**
- Upgrade to Hobby plan ($5/month)
- Includes more resources
- Production-ready

**Your app will likely use:**
- ~$3-4/month for small usage
- PostgreSQL included in that price

---

## 🔄 Automatic Deployments

Railway automatically redeploys when you push to GitHub!

**To update your app:**
1. Make changes locally
2. Commit to git
3. Push to GitHub
4. Railway auto-deploys in 2-3 minutes

```powershell
git add .
git commit -m "Update feature"
git push origin main
```

Railway will automatically build and deploy the new version!

---

## 📱 Mobile Access

Once deployed on Railway:

**Desktop:** `https://hdl-po-receipt-tool.railway.app`

**Mobile/Tablet:** Same URL!
- Works from anywhere with internet
- No need for local network
- HTTPS secure by default

---

## 🎯 Health Check

After deployment, check if everything works:

1. **Backend Health:**
   ```
   https://your-backend-url.railway.app/health
   ```
   Should return: `{"status":"ok","database":"connected"}`

2. **Frontend Loads:**
   ```
   https://your-frontend-url.railway.app
   ```
   Should show the dashboard

3. **Test Upload:**
   - Upload a test docket
   - Check if OCR works
   - Try matching a PO

---

## 📚 Railway Documentation

**Need more help?**
- Railway Docs: https://docs.railway.app
- Railway Discord: https://discord.gg/railway
- Your project dashboard: https://railway.app/dashboard

---

## ✅ Deployment Checklist

Before you deploy, make sure:

- ✅ Code is pushed to GitHub
- ✅ Railway account created
- ✅ Project linked to GitHub repo
- ✅ PostgreSQL database added
- ✅ All environment variables set
- ✅ Cin7 credentials are correct
- ✅ Frontend URL points to backend

**Then just click Deploy and wait!**

---

## 🎉 You're Live!

Once deployed:

1. **Share the URL** with your team
2. **Test on your phone** - scan a docket
3. **Monitor the logs** in Railway dashboard
4. **Check the receipts** in Cin7

**Your PO receipt tool is now available 24/7 from anywhere!**

---

## 🔐 Security Notes

Railway deployment is secure:
- ✅ HTTPS encryption by default
- ✅ Environment variables are encrypted
- ✅ Database credentials never exposed
- ✅ No .env file in git (protected by .gitignore)

**Your Cin7 credentials stay safe!**

---

## 🚀 Next Steps After Deployment

1. **Test thoroughly** with real dockets
2. **Train your team** on how to use it
3. **Monitor usage** in Railway dashboard
4. **Set up custom domain** (optional)
5. **Enable Railway backups** (in settings)

---

**Questions?** Check the Railway documentation or deployment logs.

**Ready to deploy?** Go to https://railway.app and follow Step 1 above!

---

**Built with 🔧 for Hardware Direct Limited**
**Deployed on Railway 🚂**
**Version 1.0.0**
