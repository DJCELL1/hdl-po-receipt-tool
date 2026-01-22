# 🚂 Railway Quick Start - 5 Minute Deploy

Get your Hardware Direct PO Receipt Tool live in 5 minutes!

---

## 🎯 Step-by-Step Deployment

### 1. Create Railway Account (1 minute)

1. Go to: **https://railway.app**
2. Click **"Start a New Project"**
3. Click **"Login with GitHub"**
4. Authorize Railway to access your GitHub

---

### 2. Deploy Your App (2 minutes)

1. **In Railway Dashboard:**
   - Click **"New Project"**
   - Click **"Deploy from GitHub repo"**
   - Select: **`DJCELL1/hdl-po-receipt-tool`**

2. **Railway will automatically:**
   - ✅ Detect Node.js app
   - ✅ Build backend and frontend
   - ✅ Deploy both services

3. **Add PostgreSQL Database:**
   - Click **"+ New"** in your project
   - Select **"Database"**
   - Choose **"PostgreSQL"**
   - Railway creates and links it automatically

---

### 3. Configure Environment Variables (2 minutes)

#### Backend Service Variables:

Click on your **backend service**, go to **"Variables"** tab, and add:

```
CIN7_API_KEY=your-actual-cin7-api-key
CIN7_API_SECRET=your-actual-cin7-api-secret
JWT_SECRET=change-this-to-random-string-abc123xyz789
DATABASE_URL=${{Postgres.DATABASE_URL}}
NODE_ENV=production
PORT=3001
```

**Important:**
- Use your REAL Cin7 credentials (same as local .env)
- `DATABASE_URL` auto-fills from PostgreSQL service
- Change `JWT_SECRET` to any random string

#### Frontend Service Variables:

Click on your **frontend service**, go to **"Variables"** tab, and add:

```
REACT_APP_API_URL=https://YOUR-BACKEND-URL.railway.app
NODE_ENV=production
```

**Replace `YOUR-BACKEND-URL`** with the actual URL from your backend service!

To find backend URL:
1. Click on backend service
2. Go to "Settings" tab
3. Copy the "Public URL"

---

## ✅ You're Live!

Your app is now deployed at:

**Frontend:** `https://YOUR-FRONTEND-URL.railway.app`

Open it in your browser and start scanning dockets!

---

## 📱 Share with Your Team

Just share the frontend URL:
- Works on desktop, mobile, tablet
- HTTPS secure by default
- Available 24/7 from anywhere

---

## 🔄 Auto-Deploy Updates

Every time you push to GitHub, Railway auto-deploys:

```powershell
git add .
git commit -m "Update feature"
git push origin main
```

Railway rebuilds and deploys in 2-3 minutes!

---

## 🆘 Quick Troubleshooting

### Backend won't start?
1. Check environment variables are set
2. Check logs (click service → "Deployments" → latest → "View Logs")
3. Make sure `DATABASE_URL` is set correctly

### Frontend can't connect to backend?
1. Check `REACT_APP_API_URL` in frontend variables
2. Make sure it matches your backend URL
3. Redeploy frontend after changing variables

### Database connection failed?
1. Make sure PostgreSQL service is added
2. Check `DATABASE_URL` is in backend variables
3. Format: `${{Postgres.DATABASE_URL}}` (Railway auto-fills)

---

## 💰 Pricing

**Free Tier:**
- $5 credit per month
- Perfect for development/testing
- No credit card required

**Your app will use ~$3-4/month**

---

## 🎉 Done!

Your Hardware Direct PO Receipt Tool is now live on Railway!

- ✅ Accessible from anywhere
- ✅ Auto-deploys on git push
- ✅ PostgreSQL database included
- ✅ HTTPS secure

**Need more help?** Read: [DEPLOY_TO_RAILWAY.md](DEPLOY_TO_RAILWAY.md)

---

**Built with 🔧 for Hardware Direct Limited**
**Deployed on Railway 🚂**
