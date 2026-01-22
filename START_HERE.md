# 🚀 START HERE - Hardware Direct PO Receipt Tool

## Welcome to Your New PO Receipt Tool!

This tool will save you hours of manual data entry by scanning delivery dockets and automatically receipting them into Cin7 Omni.

---

## ⚡ 3-Step Setup (5 Minutes)

### ✅ Step 1: Put Your Cin7 Credentials in .env File

**📁 FIND THIS FILE:**
```
C:\Users\selwy\OneDrive\Desktop\PROJECTS HDL\Receipt\.env.example
```

**📋 COPY IT AND RENAME TO:**
```
C:\Users\selwy\OneDrive\Desktop\PROJECTS HDL\Receipt\.env
```

**📝 OPEN .env IN NOTEPAD AND CHANGE THESE LINES:**

Find:
```env
CIN7_API_KEY=your-cin7-api-key-paste-here
CIN7_API_SECRET=your-cin7-api-secret-paste-here
```

Change to:
```env
CIN7_API_KEY=your-actual-cin7-api-key
CIN7_API_SECRET=your-actual-cin7-api-secret
```

**❓ Where do I get these?**
1. Login to Cin7: https://inventory.cin7.com
2. Go to Settings → API
3. Click "Generate API Key"
4. Copy both the Key and Secret

**📖 Need more help?** Read: [WHERE_TO_PUT_CIN7_CREDENTIALS.md](WHERE_TO_PUT_CIN7_CREDENTIALS.md)

---

### ✅ Step 2: Start the App

**💻 OPEN POWERSHELL IN THIS FOLDER**
- Right-click in this folder
- Choose "Open in Terminal" or "Open PowerShell"

**⌨️ TYPE THIS COMMAND:**
```powershell
docker-compose up -d
```

**⏱️ WAIT 60 SECONDS**
(Docker is starting 3 services: database, backend, frontend)

---

### ✅ Step 3: Open the App

**🌐 OPEN YOUR WEB BROWSER**

Go to: **http://localhost:3000**

**📱 OR ON YOUR PHONE:**

Go to: **http://[your-computer-ip]:3000**

(To find your IP: Run `ipconfig` in PowerShell, look for IPv4 Address)

---

## 🎯 First Time Using the App

1. **Click "Register"**
2. **Enter your email and password**
3. **Click "Register"** again
4. **You're in!**

Now click **"📦 Scan New Delivery Docket"** to start!

---

## 📚 Documentation

| Read This | When You Need To... |
|-----------|---------------------|
| **[SETUP_INSTRUCTIONS_FOR_HDL.md](SETUP_INSTRUCTIONS_FOR_HDL.md)** | Full setup guide & daily use |
| **[WHERE_TO_PUT_CIN7_CREDENTIALS.md](WHERE_TO_PUT_CIN7_CREDENTIALS.md)** | Detailed credential setup |
| **[HDL_README.md](HDL_README.md)** | Quick reference & troubleshooting |
| **[ADMIN_GUIDE.md](ADMIN_GUIDE.md)** | Advanced features & backup |

---

## 🆘 Quick Troubleshooting

### App won't start?
```powershell
docker-compose down
docker-compose up -d
```

### Can't login to Cin7?
Check your `.env` file - make sure credentials are correct

### Page won't load?
Check if services are running:
```powershell
docker-compose ps
```

### See errors?
Check the logs:
```powershell
docker-compose logs backend
```

---

## ✅ How to Know Everything is Working

1. **Health Check:** http://localhost:3001/health
   - Should show: `{"status":"ok","database":"connected"}`

2. **Services Running:**
   ```powershell
   docker-compose ps
   ```
   - Should show 3 services with status "Up"

3. **Can Login:**
   - Go to http://localhost:3000
   - Register an account
   - Login successfully

4. **Can Connect to Cin7:**
   - Upload a test docket
   - Try to match a PO
   - If it searches Cin7 = ✅ Working!

---

## 🎨 What You'll See

**Hardware Direct Orange Theme**
- Orange buttons and highlights
- Charcoal headers
- Professional warehouse-ready design

**Mobile-Optimized**
- Works great on phones
- Large buttons for easy tapping
- Camera capture built-in

---

## 🔑 Important Files

```
Receipt/
├── .env ← PUT YOUR CIN7 CREDENTIALS HERE! ⚠️
├── .env.example ← Template (copy this to .env)
├── docker-compose.yml ← Don't change this
├── START_HERE.md ← This file
├── SETUP_INSTRUCTIONS_FOR_HDL.md ← Full guide
└── WHERE_TO_PUT_CIN7_CREDENTIALS.md ← Credential help
```

---

## 📞 Need Help?

1. **Check the documentation** (files listed above)
2. **Check the logs:** `docker-compose logs backend`
3. **Restart the app:** `docker-compose down` then `docker-compose up -d`
4. **Contact your IT administrator**

---

## 🚦 Status Colors

**Green (✅)** = Working perfectly
**Orange (⚠️)** = Warning (check it out)
**Red (❌)** = Error (needs fixing)

---

## 🎉 You're Ready!

Once you've completed the 3 steps above:

1. **Login** to http://localhost:3000
2. **Click** "📦 Scan New Delivery Docket"
3. **Take a photo** of a delivery docket
4. **Watch** the magic happen!

The app will:
- Extract supplier, PO, and items automatically
- Find the matching PO in Cin7
- Match line items
- Let you confirm and submit

**Total time: 30-60 seconds per docket!**

---

**Questions?** Read the documentation files listed above.

**Ready to go?** Open http://localhost:3000 and start scanning!

---

**Built with 🔧 for Hardware Direct Limited**
**Powered by Cin7 Omni**
**Version 1.0.0**
