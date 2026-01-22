# Complete File Structure

## Root Directory Files
```
cin7-docket-receiver/
├── .env.example                  # Environment variables template
├── .gitignore                    # Git ignore rules
├── docker-compose.yml            # Docker orchestration
├── package.json                  # Root package.json (workspaces)
├── README.md                     # Main documentation
├── QUICK_START.md                # 5-minute setup guide
├── ADMIN_GUIDE.md                # Admin & deployment guide
├── API_DOCUMENTATION.md          # Complete API reference
├── PROJECT_SUMMARY.md            # Project overview
└── FILE_STRUCTURE.md             # This file
```

## Backend Files (44 files)
```
backend/
├── Dockerfile                    # Backend Docker image
├── package.json                  # Backend dependencies
├── tsconfig.json                 # TypeScript configuration
├── jest.config.js                # Jest test configuration
├── uploads/
│   └── .gitkeep                  # Ensures uploads directory exists
└── src/
    ├── server.ts                 # Main Express application
    ├── cin7/
    │   ├── cin7Client.ts         # Cin7 API client (retry, pagination)
    │   ├── rateLimiter.ts        # Rate limit enforcement
    │   ├── rateLimiter.test.ts   # Rate limiter tests
    │   └── types.ts              # TypeScript interfaces
    ├── database/
    │   ├── db.ts                 # PostgreSQL connection pool
    │   ├── schema.sql            # Database schema
    │   └── migrate.ts            # Migration runner
    ├── middleware/
    │   └── auth.ts               # JWT authentication middleware
    ├── routes/
    │   ├── auth.routes.ts        # Auth endpoints (login/register)
    │   └── docket.routes.ts      # Docket processing endpoints
    ├── services/
    │   ├── imagePreprocessor.ts  # Image enhancement (Sharp/Jimp)
    │   ├── ocrService.ts         # OCR processing (Tesseract)
    │   └── poMatcher.ts          # PO matching algorithm
    └── utils/
        ├── poReference.ts        # PO reference parser
        └── poReference.test.ts   # Parser tests
```

## Frontend Files (19 files)
```
frontend/
├── Dockerfile                    # Frontend Docker image
├── nginx.conf                    # Nginx configuration
├── package.json                  # Frontend dependencies
├── tsconfig.json                 # TypeScript configuration
├── public/
│   └── index.html                # HTML template
└── src/
    ├── index.tsx                 # React entry point
    ├── index.css                 # Global styles
    ├── App.tsx                   # Main App component
    ├── App.css                   # App styles
    ├── context/
    │   └── AuthContext.tsx       # Authentication context
    ├── services/
    │   └── api.ts                # API client (Axios)
    └── pages/
        ├── AllPages.tsx          # Consolidated page components
        ├── Login.tsx             # Login screen
        ├── Register.tsx          # Registration screen
        ├── Dashboard.tsx         # Main dashboard
        ├── CaptureScreen.tsx     # Camera/upload screen
        ├── ReviewExtraction.tsx  # Review OCR results
        ├── MatchPo.tsx           # PO matching screen
        ├── MatchLines.tsx        # Line matching screen
        ├── ConfirmReceipt.tsx    # Confirmation screen
        ├── ReceiptResult.tsx     # Success/failure screen
        └── ReceiptHistory.tsx    # Receipt history
```

## Total File Count

| Category | Count |
|----------|-------|
| Root documentation | 9 |
| Backend source files | 14 |
| Backend config files | 4 |
| Backend test files | 2 |
| Frontend source files | 14 |
| Frontend config files | 4 |
| Docker files | 3 |
| **TOTAL** | **50 files** |

## Key Technologies by File

### Backend
- **TypeScript** - All `.ts` files
- **Express.js** - `server.ts`, routes
- **PostgreSQL** - `db.ts`, `schema.sql`
- **Tesseract.js** - `ocrService.ts`
- **Sharp/Jimp** - `imagePreprocessor.ts`
- **JWT** - `auth.ts`
- **Jest** - `.test.ts` files
- **Axios** - `cin7Client.ts`

### Frontend
- **React** - All `.tsx` files
- **TypeScript** - All `.tsx` files
- **React Router** - `App.tsx`
- **Context API** - `AuthContext.tsx`
- **Axios** - `api.ts`

### Infrastructure
- **Docker** - `Dockerfile`, `docker-compose.yml`
- **Nginx** - `nginx.conf`
- **PostgreSQL** - Via Docker

## Database Schema Files

The `schema.sql` file creates:
- 6 tables (users, uploads, extractions, receipts, receipt_lines, audit_log)
- 12 indexes
- 2 triggers
- 1 custom function

## Configuration Files

### Environment (`.env.example`)
- Database connection
- Cin7 API credentials
- JWT secret
- Server configuration

### Docker (`docker-compose.yml`)
- 3 services: postgres, backend, frontend
- 1 volume: postgres_data
- Network configuration
- Health checks

### TypeScript (`tsconfig.json`)
- 2 configs: backend, frontend
- Strict mode enabled
- ES2022 target

### Package (`package.json`)
- 3 packages: root, backend, frontend
- Workspace configuration
- Scripts for dev/build/test

## Documentation Files

1. **README.md** (335 lines) - Complete project documentation
2. **QUICK_START.md** (145 lines) - Setup in 5 minutes
3. **ADMIN_GUIDE.md** (550+ lines) - Administration & troubleshooting
4. **API_DOCUMENTATION.md** (450+ lines) - API reference
5. **PROJECT_SUMMARY.md** (400+ lines) - Project overview
6. **FILE_STRUCTURE.md** - This file

Total documentation: **~2000 lines**

## Lines of Code Estimate

| Component | Files | Estimated LOC |
|-----------|-------|---------------|
| Backend TypeScript | 14 | ~2,500 |
| Backend Tests | 2 | ~200 |
| Frontend TypeScript | 14 | ~1,800 |
| SQL | 1 | ~200 |
| Config files | 7 | ~300 |
| Documentation | 6 | ~2,000 |
| **TOTAL** | **44** | **~7,000 LOC** |

## Build Artifacts (Generated)

When built, the project generates:
```
backend/dist/           # Compiled TypeScript
frontend/build/         # Production React build
node_modules/           # Dependencies (ignored)
uploads/                # Uploaded files (ignored)
*.log                   # Log files (ignored)
```

## Git Repository Structure

### Tracked Files
- All source code
- Configuration files
- Documentation
- Dockerfiles
- Schema files

### Ignored Files (.gitignore)
- node_modules/
- dist/
- build/
- .env
- uploads/* (except .gitkeep)
- *.log

## Quick Reference

### Start Development
```bash
cd backend && npm run dev
cd frontend && npm start
```

### Run Tests
```bash
cd backend && npm test
```

### Deploy with Docker
```bash
docker-compose up -d
```

### View Logs
```bash
docker-compose logs -f
```

---

**Generated:** January 2026
**Total Files:** 50
**Total LOC:** ~7,000
