# 🏗️ Railway Deployment Architecture

Visual guide to how your app works on Railway.

---

## 📊 System Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                        RAILWAY PLATFORM                      │
│                                                              │
│  ┌────────────────────────────────────────────────────────┐ │
│  │              YOUR PROJECT                              │ │
│  │                                                        │ │
│  │  ┌──────────────────┐      ┌──────────────────┐      │ │
│  │  │  Frontend        │      │  Backend         │      │ │
│  │  │  Service         │◄────►│  Service         │      │ │
│  │  │                  │      │                  │      │ │
│  │  │  React App       │      │  Node.js API     │      │ │
│  │  │  Port: 3000      │      │  Port: 3001      │      │ │
│  │  │                  │      │                  │      │ │
│  │  │  Public URL:     │      │  Public URL:     │      │ │
│  │  │  *.railway.app   │      │  *.railway.app   │      │ │
│  │  └──────────────────┘      └─────────┬────────┘      │ │
│  │                                      │               │ │
│  │                                      │               │ │
│  │                                      ▼               │ │
│  │                           ┌──────────────────┐       │ │
│  │                           │  PostgreSQL      │       │ │
│  │                           │  Database        │       │ │
│  │                           │                  │       │ │
│  │                           │  Private Network │       │ │
│  │                           │  Auto-backup     │       │ │
│  │                           └──────────────────┘       │ │
│  │                                      │               │ │
│  │                                      │               │ │
│  │                                      ▼               │ │
│  │                           ┌──────────────────┐       │ │
│  │                           │  Tables:         │       │ │
│  │                           │  - users         │       │ │
│  │                           │  - uploads       │       │ │
│  │                           │  - extractions   │       │ │
│  │                           │  - receipts      │       │ │
│  │                           │  - receipt_lines │       │ │
│  │                           │  - audit_log     │       │ │
│  │                           └──────────────────┘       │ │
│  └────────────────────────────────────────────────────┘ │
│                                                          │
│                           │                              │
│                           ▼                              │
│                  ┌────────────────┐                      │
│                  │  External API  │                      │
│                  │  Cin7 Omni     │                      │
│                  │                │                      │
│                  │  api.cin7.com  │                      │
│                  └────────────────┘                      │
└──────────────────────────────────────────────────────────┘
                           │
                           ▼
                  ┌────────────────┐
                  │  Users         │
                  │  📱 Mobile     │
                  │  💻 Desktop    │
                  │  📷 Camera     │
                  └────────────────┘
```

---

## 🔄 Request Flow

### 1. User Scans Docket

```
User's Phone 📱
    │
    │ Take photo of delivery docket
    │
    ▼
Frontend (Railway)
https://*.railway.app
    │
    │ POST /api/dockets/upload
    │
    ▼
Backend (Railway)
https://*.railway.app/api
    │
    ├─► OCR Service (Tesseract.js)
    │   │
    │   └─► Extract: Supplier, PO#, Items
    │
    ├─► Save to PostgreSQL
    │
    └─► Return extracted data
```

### 2. Match Purchase Order

```
Frontend
    │
    │ POST /api/dockets/match-po
    │ { poReference: "PO-12345A" }
    │
    ▼
Backend
    │
    ├─► Parse PO Reference
    │   │ Normalize: "PO-12345A"
    │   │ Base: "PO-12345"
    │   │ Suffix: "A"
    │
    ├─► Query Cin7 API
    │   │ https://api.cin7.com/api/v1/PurchaseOrders
    │   │ Rate limiting: 3/sec, 60/min
    │   │ Retry on failure
    │
    ├─► Rank matches by:
    │   │ - Exact PO match
    │   │ - Supplier match
    │   │ - Line item similarity
    │
    └─► Return best matches
```

### 3. Create Receipt

```
Frontend
    │
    │ POST /api/dockets/receipt
    │ { poId, lineItems, quantities }
    │
    ▼
Backend
    │
    ├─► Validate quantities
    │   │ Check over-delivery
    │   │ Check duplicate docket
    │
    ├─► Update Cin7 PO
    │   │ PUT /v1/PurchaseOrders/{id}
    │   │ Update ReceivedQty
    │
    ├─► Save receipt to PostgreSQL
    │   │ INSERT INTO receipts
    │   │ INSERT INTO receipt_lines
    │   │ INSERT INTO audit_log
    │
    └─► Return success
```

---

## 🌐 Network Flow

```
┌──────────────┐
│  User Device │
│  (Anywhere)  │
└──────┬───────┘
       │
       │ HTTPS (443)
       │
       ▼
┌──────────────────────┐
│  Railway CDN         │
│  (Global)            │
└──────┬───────────────┘
       │
       │ Load Balancer
       │
       ▼
┌──────────────────────┐
│  Frontend Container  │
│  nginx + React       │
│  PORT: 3000          │
└──────┬───────────────┘
       │
       │ API Calls
       │
       ▼
┌──────────────────────┐
│  Backend Container   │
│  Node.js + Express   │
│  PORT: 3001          │
└──────┬───────────────┘
       │
       ├─────────────────┐
       │                 │
       ▼                 ▼
┌──────────────┐  ┌──────────────┐
│  PostgreSQL  │  │  Cin7 API    │
│  (Railway)   │  │  (External)  │
└──────────────┘  └──────────────┘
```

---

## 📦 Deployment Process

```
GitHub Push
    │
    │ git push origin main
    │
    ▼
Railway Webhook
    │
    │ Detects new commit
    │
    ▼
Build Phase
    │
    ├─► Install dependencies
    │   │ npm install
    │
    ├─► Build backend
    │   │ cd backend
    │   │ npm run build (tsc)
    │
    ├─► Run migrations
    │   │ npm run migrate:prod
    │
    └─► Build frontend
        │ cd frontend
        │ npm run build
        │
        ▼
Deploy Phase
    │
    ├─► Create backend container
    │   │ Start: npm start
    │   │ Health check: /health
    │
    ├─► Create frontend container
    │   │ Start: nginx
    │   │ Serve: /build
    │
    └─► Update URLs
        │ Assign public URLs
        │
        ▼
Live! ✅
```

---

## 🔐 Environment Variables Flow

```
Railway Dashboard
    │
    │ Set variables
    │
    ▼
┌─────────────────────────────┐
│  Backend Container          │
│                             │
│  CIN7_API_KEY=***          │
│  CIN7_API_SECRET=***       │
│  JWT_SECRET=***            │
│  DATABASE_URL=postgresql://│
│  NODE_ENV=production       │
│  PORT=3001                 │
└─────────────────────────────┘
    │
    │ Used by:
    │
    ├─► Cin7 Client (API auth)
    ├─► Database connection
    └─► Express server

┌─────────────────────────────┐
│  Frontend Container         │
│                             │
│  REACT_APP_API_URL=https:// │
│  NODE_ENV=production        │
└─────────────────────────────┘
    │
    │ Baked into build
    │
    └─► API calls point to backend
```

---

## 📊 Data Flow Example

**Scenario: Scan and receipt a docket**

```
1. User Takes Photo
   📱 Camera → Upload to Frontend

2. OCR Processing
   Frontend → Backend → Tesseract
   Result: {
     supplier: "ACME Corp",
     poReference: "PO-12345A",
     items: [...]
   }

3. Save Extraction
   Backend → PostgreSQL
   INSERT INTO extractions (...)

4. Match PO
   Backend → Cin7 API
   GET /v1/PurchaseOrders?where=Reference='PO-12345A'

   If not found:
   GET /v1/PurchaseOrders?where=Reference='PO-12345'

5. Display Matches
   Backend → Frontend
   User selects correct PO

6. Match Line Items
   Frontend sends items → Backend
   Algorithm matches SKUs
   Returns matched pairs

7. User Confirms
   Review quantities → Submit

8. Create Receipt
   Backend → Cin7 API
   PUT /v1/PurchaseOrders/{id}
   Update ReceivedQty on lines

9. Save Receipt
   Backend → PostgreSQL
   INSERT INTO receipts (...)
   INSERT INTO receipt_lines (...)
   INSERT INTO audit_log (...)

10. Success!
    Display confirmation → User
```

---

## 🔄 Auto-Deployment Workflow

```
Developer Makes Change
    │
    │ Edit code locally
    │
    ▼
Git Commit
    │
    │ git commit -m "Update feature"
    │
    ▼
Git Push
    │
    │ git push origin main
    │
    ▼
GitHub Repository
    │
    │ Receives new commit
    │
    ▼
Railway Webhook
    │
    │ Triggered automatically
    │
    ▼
Build Starts
    │
    │ ~2-3 minutes
    │
    ├─► Health checks pass?
    │   │ Yes → Deploy
    │   │ No → Rollback
    │
    ▼
New Version Live! ✅
    │
    │ Zero downtime
    │
    └─► Users see new version
```

---

## 💾 Database Schema on Railway

```
PostgreSQL Container (Railway)
│
├── Database: cin7_hdl_receipt
│   │
│   ├── Table: users
│   │   └── id, email, password_hash, name
│   │
│   ├── Table: uploads
│   │   └── id, user_id, file_path, mime_type
│   │
│   ├── Table: extractions
│   │   └── id, upload_id, supplier, po_ref, items
│   │
│   ├── Table: receipts
│   │   └── id, user_id, cin7_po_id, po_reference
│   │
│   ├── Table: receipt_lines
│   │   └── id, receipt_id, sku, qty_received
│   │
│   └── Table: audit_log
│       └── id, entity_type, entity_id, action, data
│
└── Backups: Automatic (Railway)
```

---

## 🚀 Scaling on Railway

```
Traffic Increases
    │
    │ More users scanning dockets
    │
    ▼
Railway Auto-Scales
    │
    ├─► Add more backend instances
    ├─► Load balance requests
    └─► Scale database connections

    All automatic! ✅
```

---

## 📈 Monitoring

```
Railway Dashboard
    │
    ├─► Deployment logs
    ├─► Runtime logs
    ├─► Metrics (CPU, Memory)
    ├─► Network traffic
    └─► Database stats

Backend /health endpoint
    │
    └─► Database connectivity check
        Returns: {"status":"ok","database":"connected"}
```

---

## ✅ Production Ready Features

- ✅ **HTTPS**: Automatic SSL certificates
- ✅ **Auto-Scaling**: Handles traffic spikes
- ✅ **Auto-Backups**: PostgreSQL backed up daily
- ✅ **Zero-Downtime**: Rolling deployments
- ✅ **Health Checks**: Auto-restart on failure
- ✅ **Logging**: Centralized log aggregation
- ✅ **Monitoring**: Built-in metrics

---

**Ready to deploy?** See: [RAILWAY_QUICK_START.md](RAILWAY_QUICK_START.md)
