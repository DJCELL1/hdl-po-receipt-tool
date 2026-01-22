# HDL PO Receipt Tool

Production-ready Streamlit application for receiving Purchase Orders in Cin7 Omni by capturing delivery dockets, extracting data via OCR, and receipting quantities accurately.

## Features

- 📸 **Mobile-friendly capture** - Take photos directly from your device
- 🔍 **OCR extraction** - Automatic text extraction with Tesseract
- 🎯 **Smart PO matching** - Handles backorder suffixes (A/B/C)
- ✅ **Line-by-line matching** - Fuzzy matching with manual override
- 🔒 **Duplicate prevention** - Prevents double receipting
- 📊 **Audit trail** - Full database logging
- 🔄 **Rate limit compliance** - Cin7 API rate limiting (3/sec, 60/min, 5000/day)
- ⚡ **Retry logic** - Automatic exponential backoff

## Tech Stack

- **Frontend/Backend**: Streamlit (Python)
- **Database**: PostgreSQL
- **OCR**: Tesseract + OpenCV
- **API**: Cin7 Omni REST API
- **Deployment**: Docker + Docker Compose

## Quick Start

### Prerequisites

- Docker & Docker Compose
- Cin7 Omni API credentials
- (Optional) Tesseract OCR for local development

### Installation

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd Receipt
   ```

2. **Configure environment variables**
   ```bash
   cp .env.example .env
   # Edit .env with your Cin7 API credentials
   ```

3. **Start with Docker Compose**
   ```bash
   docker-compose up -d
   ```

4. **Run database migration**
   ```bash
   docker-compose exec app python database/migrate.py
   ```

5. **Access the application**
   ```
   http://localhost:8501
   ```

## Manual Setup (Without Docker)

### 1. Install System Dependencies

**Ubuntu/Debian:**
```bash
sudo apt-get update
sudo apt-get install tesseract-ocr python3-opencv postgresql
```

**macOS:**
```bash
brew install tesseract opencv postgresql
```

**Windows:**
- Download Tesseract: https://github.com/UB-Mannheim/tesseract/wiki
- Install PostgreSQL: https://www.postgresql.org/download/windows/

### 2. Install Python Dependencies

```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
```

### 3. Set up Database

```bash
# Create PostgreSQL database
createdb hdl_receipts

# Run migration
python database/migrate.py
```

### 4. Configure Environment

Edit `.env` file with your settings (see `.env.example`)

### 5. Run Application

```bash
streamlit run app.py
```

## Configuration

### Environment Variables

Key configuration options in `.env`:

```bash
# Database
DATABASE_URL=postgresql://user:password@localhost:5432/hdl_receipts

# Cin7 API
CIN7_API_KEY=your_api_key
CIN7_API_SECRET=your_api_secret

# OCR (adjust path for your system)
TESSERACT_CMD=/usr/bin/tesseract

# Fuzzy matching threshold (0-100)
FUZZY_MATCH_THRESHOLD=85
```

## Application Flow

### Page 1: Upload Docket
- 📷 Capture via camera (mobile-friendly)
- 📁 Upload JPG/PNG/PDF

### Page 2: Review Extraction
- Review OCR results
- Edit supplier, docket number, PO reference
- Verify line items
- All fields are editable

### Page 3: Match PO
- Automatic search in Cin7
- Handles backorder suffixes (PO-12345A/B/C)
- Best match highlighted
- Manual search override available

### Page 4: Match Lines
- Side-by-side docket vs PO comparison
- Exact SKU matching
- Fuzzy description matching
- Flags: over-delivery, SKU not found
- Manual quantity adjustment

### Page 5: Submit Receipt
- Final review
- Duplicate detection
- Submit to Cin7 Omni
- Full audit logging

## PO Reference Handling

The app intelligently handles backorder PO references:

```python
PO-12345   → Base reference
PO-12345A  → Backorder A
PO-12345B  → Backorder B
PO-12345C  → Backorder C
```

**Matching Logic:**
1. Exact match on full reference
2. If suffix present, try base reference
3. Wildcard search for related POs
4. Rank by supplier similarity & recency

## Business Rules

- ✅ Partial deliveries supported
- ⚠️ Over-delivery requires explicit confirmation
- 🚫 Duplicate docket detection with override option
- ⚠️ Missing SKU allowed but flagged
- ⚠️ Fuzzy matches always require confirmation

## API Rate Limiting

Cin7 API limits:
- 3 requests per second
- 60 requests per minute
- 5000 requests per day

The app automatically:
- Enforces rate limits
- Retries on 429 (rate limit)
- Exponential backoff on 503
- Handles pagination

## Testing

Run unit tests:

```bash
# All tests
pytest

# Specific test file
pytest tests/test_po_matcher.py

# With coverage
pytest --cov=. --cov-report=html

# Exclude slow tests
pytest -m "not slow"
```

## Troubleshooting

### OCR Not Working
- Verify Tesseract is installed: `tesseract --version`
- Check TESSERACT_CMD path in `.env`
- Ensure image quality is good (well-lit, in focus)

### Cin7 API Errors
- Verify API credentials in `.env`
- Check API key has correct permissions
- Review rate limit status in logs

### Database Connection Errors
- Verify PostgreSQL is running
- Check DATABASE_URL in `.env`
- Run migration: `python database/migrate.py`

### Docker Issues
- Check logs: `docker-compose logs app`
- Verify .env file is in place
- Restart: `docker-compose restart`

## Project Structure

```
Receipt/
├── app.py                  # Main Streamlit app
├── config.py               # Configuration loader
├── requirements.txt        # Python dependencies
├── Dockerfile             # Docker container config
├── docker-compose.yml     # Multi-container setup
├── cin7/
│   ├── cin7_client.py     # Cin7 API client
│   └── rate_limiter.py    # Rate limiting logic
├── database/
│   ├── db.py              # SQLAlchemy models
│   ├── schema.sql         # Database schema
│   └── migrate.py         # Migration script
├── services/
│   ├── ocr_service.py     # OCR extraction
│   ├── image_processor.py # Image preprocessing
│   └── po_matcher.py      # PO matching logic
├── pages/
│   ├── page1_upload.py    # Upload page
│   ├── page2_review.py    # Review extraction
│   ├── page3_match_po.py  # PO matching
│   ├── page4_match_lines.py # Line matching
│   └── page5_submit.py    # Submit receipt
└── tests/
    ├── test_po_matcher.py
    ├── test_rate_limiter.py
    ├── test_cin7_client.py
    └── test_ocr_service.py
```

## Security Considerations

- 🔐 Store API credentials in environment variables
- 🔐 Use HTTPS in production
- 🔐 Implement user authentication (TODO)
- 🔐 Validate all user inputs
- 🔐 Audit all database operations

## Future Enhancements

- [ ] User authentication & authorization
- [ ] Receipt history dashboard
- [ ] Email notifications
- [ ] Barcode scanning support
- [ ] Multi-language OCR
- [ ] Bulk receipt upload
- [ ] Advanced analytics

## Support

For issues or questions:
- Check logs: `docker-compose logs app`
- Review documentation
- Contact: support@hdl.com (adjust as needed)

## License

Proprietary - HDL Internal Use Only

## Authors

Built for HDL Warehouse Operations
