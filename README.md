# Cin7 Docket Receiver

Production-ready web application for streamlining stock receiving into Cin7 Omni by scanning delivery docket photos.

## Features

- **Mobile-first UI** - Optimized for smartphone camera capture
- **OCR Processing** - Automated text extraction from docket photos/PDFs with preprocessing
- **Smart PO Matching** - Handles backorder suffixes (A/B/C) and fuzzy matching
- **Line Item Matching** - Automatic SKU matching with fuzzy fallback
- **Duplicate Detection** - Prevents accidental double-receipting
- **Receipt History** - Full audit trail of all receipts
- **Cin7 Integration** - Direct API integration with retry logic and rate limiting

## Tech Stack

**Backend:**
- Node.js 20 + TypeScript
- Express.js
- PostgreSQL
- Tesseract.js (OCR)
- Sharp + Jimp (image preprocessing)

**Frontend:**
- React 18 + TypeScript
- React Router
- Axios

**Infrastructure:**
- Docker + Docker Compose
- Nginx (production)

## Quick Start

### Prerequisites

- Docker and Docker Compose
- Cin7 Omni API credentials

### Setup

1. **Clone and configure**

```bash
cd cin7-docket-receiver
cp .env.example .env
```

2. **Edit `.env` with your Cin7 credentials**

```env
CIN7_API_KEY=your-api-key
CIN7_API_SECRET=your-api-secret
JWT_SECRET=generate-a-random-secret
```

3. **Start with Docker**

```bash
docker-compose up -d
```

4. **Access the application**

- Frontend: http://localhost:3000
- Backend API: http://localhost:3001

5. **Create an account**

Navigate to http://localhost:3000/register and create your first user account.

## Development Setup

### Backend

```bash
cd backend
npm install
cp ../.env.example .env
# Edit .env with your configuration
npm run dev
```

### Frontend

```bash
cd frontend
npm install
echo "REACT_APP_API_URL=http://localhost:3001" > .env
npm start
```

### Database Migration

```bash
cd backend
npm run migrate
```

## Project Structure

```
cin7-docket-receiver/
├── backend/
│   ├── src/
│   │   ├── cin7/              # Cin7 API client
│   │   │   ├── cin7Client.ts   # Main API client with retry & pagination
│   │   │   ├── rateLimiter.ts  # Rate limit enforcement
│   │   │   └── types.ts        # TypeScript interfaces
│   │   ├── database/           # Database layer
│   │   │   ├── db.ts           # Connection pool
│   │   │   ├── schema.sql      # Database schema
│   │   │   └── migrate.ts      # Migration runner
│   │   ├── middleware/         # Express middleware
│   │   │   └── auth.ts         # JWT authentication
│   │   ├── routes/             # API endpoints
│   │   │   ├── auth.routes.ts  # Login/register
│   │   │   └── docket.routes.ts # Docket processing
│   │   ├── services/           # Business logic
│   │   │   ├── ocrService.ts   # OCR processing
│   │   │   ├── imagePreprocessor.ts # Image enhancement
│   │   │   └── poMatcher.ts    # PO matching algorithm
│   │   ├── utils/              # Utilities
│   │   │   └── poReference.ts  # PO reference parser
│   │   └── server.ts           # Express app
│   ├── Dockerfile
│   └── package.json
├── frontend/
│   ├── src/
│   │   ├── context/            # React context
│   │   │   └── AuthContext.tsx # Auth state management
│   │   ├── pages/              # Page components
│   │   │   ├── Login.tsx
│   │   │   ├── Dashboard.tsx
│   │   │   ├── CaptureScreen.tsx
│   │   │   ├── ReviewExtraction.tsx
│   │   │   ├── MatchPo.tsx
│   │   │   ├── MatchLines.tsx
│   │   │   ├── ConfirmReceipt.tsx
│   │   │   ├── ReceiptResult.tsx
│   │   │   └── ReceiptHistory.tsx
│   │   ├── services/           # API client
│   │   │   └── api.ts
│   │   ├── App.tsx
│   │   └── index.tsx
│   ├── Dockerfile
│   ├── nginx.conf
│   └── package.json
├── docker-compose.yml
├── .env.example
└── README.md
```

## API Endpoints

### Authentication

- `POST /api/auth/register` - Create new user
- `POST /api/auth/login` - Login

### Dockets

- `POST /api/dockets/upload` - Upload and process docket
- `POST /api/dockets/match-po` - Match to Purchase Order
- `POST /api/dockets/match-lines` - Match line items
- `POST /api/dockets/receipt` - Create receipt in Cin7
- `GET /api/dockets/receipts` - Get receipt history
- `GET /api/dockets/receipts/:id` - Get receipt details

## Cin7 API Integration

### PO Reference Parsing

The app intelligently handles backorder suffixes:

```typescript
PO-12345A -> base: PO-12345, suffix: A
PO-12345  -> base: PO-12345, suffix: null
```

**Matching Strategy:**
1. Try exact match on normalized reference
2. If no match and suffix exists, try base reference
3. If still no match, try wildcard search (base%)
4. Rank candidates by supplier match and line item similarity

### Rate Limiting

Respects Cin7 API limits:
- 3 requests/second
- 60 requests/minute
- 5000 requests/day

Implements exponential backoff for 429/503 errors.

### Receipt Process

1. Fetches current PO state
2. Updates `ReceivedQty` on matching line items
3. Submits via `PUT /v1/PurchaseOrders/{id}`

## Testing

```bash
# Backend tests
cd backend
npm test

# Frontend tests
cd frontend
npm test
```

### Test Coverage

- PO reference parsing (normalizePoRef, suffix detection)
- Rate limiter (throttling, reset)
- Matching algorithm (exact, fuzzy, wildcard)
- OCR parsing (line item extraction)

## Business Rules

### Partial Deliveries
- Allows receiving quantities less than ordered
- Tracks remaining quantity

### Over-Deliveries
- Flags when delivered qty > ordered qty
- Requires explicit override checkbox

### Duplicate Detection
- Checks supplier + docket number
- Blocks by default with override option

### Backorder Handling
- PO-12345A searches for exact match first
- Falls back to base PO-12345 if not found
- Shows all related POs for user selection

## Security

- JWT-based authentication
- Password hashing with bcrypt
- SQL injection protection (parameterized queries)
- Input validation with express-validator
- CORS protection
- Secure headers (nginx)

## Performance

- Database connection pooling
- Image preprocessing for better OCR
- Lazy loading of receipts
- Pagination on all list endpoints

## Troubleshooting

### OCR Not Working

Ensure Tesseract is installed:
```bash
# macOS
brew install tesseract

# Ubuntu/Debian
apt-get install tesseract-ocr

# Docker (already included)
```

### Database Connection Issues

Check PostgreSQL is running:
```bash
docker-compose ps
docker-compose logs postgres
```

### Cin7 API Errors

- Verify API credentials in `.env`
- Check rate limits haven't been exceeded
- Ensure PO exists and is in correct status

## Production Deployment

### Deploy to Railway (Recommended - 5 Minutes)

Railway provides the easiest cloud deployment with PostgreSQL included.

**Quick Deploy:**
1. Go to https://railway.app
2. Login with GitHub
3. Deploy from repo: `DJCELL1/hdl-po-receipt-tool`
4. Add PostgreSQL database
5. Set environment variables (see RAILWAY_QUICK_START.md)

**Full Guide:** See [RAILWAY_QUICK_START.md](RAILWAY_QUICK_START.md) or [DEPLOY_TO_RAILWAY.md](DEPLOY_TO_RAILWAY.md)

### Manual Production Deployment

1. Set strong `JWT_SECRET`
2. Use environment-specific `.env` files
3. Enable HTTPS/SSL
4. Configure backup for PostgreSQL
5. Set up monitoring and logging
6. Use production-grade secrets management

## License

Proprietary - All rights reserved

## Support

For issues and questions, contact your system administrator.
