# HDL PO Receipt Tool - Architecture Documentation

Visual architecture diagrams and technical specifications.

## System Architecture

### High-Level Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                     USER INTERFACE                          │
│                                                             │
│  ┌─────────┐  ┌─────────┐  ┌──────┐  ┌───────┐  ┌────────┐│
│  │ Upload  │→ │ Review  │→ │ Match│→ │ Lines │→ │ Submit ││
│  │ Docket  │  │ Extract │  │  PO  │  │ Match │  │Receipt ││
│  └─────────┘  └─────────┘  └──────┘  └───────┘  └────────┘│
│                     Streamlit Frontend                      │
└───────────────────────────┬─────────────────────────────────┘
                            │
┌───────────────────────────▼─────────────────────────────────┐
│                   APPLICATION LAYER                         │
│                                                             │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐    │
│  │ OCR Service  │  │  PO Matcher  │  │ Cin7 Client  │    │
│  │              │  │              │  │              │    │
│  │ • Tesseract  │  │ • Normalize  │  │ • Auth       │    │
│  │ • Extract    │  │ • Match      │  │ • Retry      │    │
│  │ • Parse      │  │ • Rank       │  │ • Rate Limit │    │
│  └──────────────┘  └──────────────┘  └──────────────┘    │
│                                                             │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐    │
│  │Image Processor│  │Rate Limiter │  │  Validation  │    │
│  │              │  │              │  │              │    │
│  │ • Deskew     │  │ • 3/sec      │  │ • Input      │    │
│  │ • Denoise    │  │ • 60/min     │  │ • Business   │    │
│  │ • Threshold  │  │ • 5000/day   │  │ • Duplicate  │    │
│  └──────────────┘  └──────────────┘  └──────────────┘    │
└─────────────┬───────────────────────────┬─────────────────┘
              │                           │
┌─────────────▼────────┐    ┌────────────▼───────────────────┐
│   PostgreSQL DB      │    │   Cin7 Omni API                │
│                      │    │                                │
│ • uploads            │    │ • Purchase Orders              │
│ • extractions        │    │ • Suppliers                    │
│ • receipts           │    │ • Products                     │
│ • audit_log          │    │                                │
└──────────────────────┘    └────────────────────────────────┘
```

---

## Data Flow Diagram

### Receipt Processing Flow

```
┌──────────┐
│  Start   │
└────┬─────┘
     │
     ▼
┌──────────────────────┐
│ 1. Capture Docket    │
│  • Camera photo      │
│  • File upload       │
└────┬─────────────────┘
     │
     ▼
┌──────────────────────┐
│ 2. Save to Database  │
│  uploads table       │
└────┬─────────────────┘
     │
     ▼
┌──────────────────────┐
│ 3. Preprocess Image  │
│  • Deskew            │
│  • Denoise           │
│  • Threshold         │
└────┬─────────────────┘
     │
     ▼
┌──────────────────────┐
│ 4. Run OCR           │
│  • Extract text      │
│  • Parse fields      │
│  • Extract lines     │
└────┬─────────────────┘
     │
     ▼
┌──────────────────────┐
│ 5. User Review       │
│  • Edit fields       │
│  • Confirm data      │
└────┬─────────────────┘
     │
     ▼
┌──────────────────────┐
│ 6. Save Extraction   │
│  extractions table   │
│  extraction_lines    │
└────┬─────────────────┘
     │
     ▼
┌──────────────────────┐
│ 7. Search Cin7 PO    │
│  • Normalize ref     │
│  • Query API         │
│  • Rank results      │
└────┬─────────────────┘
     │
     ▼
┌──────────────────────┐
│ 8. User Selects PO   │
│  • Review matches    │
│  • Confirm PO        │
└────┬─────────────────┘
     │
     ▼
┌──────────────────────┐
│ 9. Match Lines       │
│  • SKU match         │
│  • Fuzzy match       │
│  • Flag issues       │
└────┬─────────────────┘
     │
     ▼
┌──────────────────────┐
│ 10. User Review      │
│  • Adjust qtys       │
│  • Confirm matches   │
└────┬─────────────────┘
     │
     ▼
┌──────────────────────┐
│ 11. Check Duplicate  │
│  • Query receipts    │
│  • Warn if exists    │
└────┬─────────────────┘
     │
     ▼
┌──────────────────────┐
│ 12. Update Cin7 PO   │
│  • Update quantities │
│  • PUT request       │
└────┬─────────────────┘
     │
     ▼
┌──────────────────────┐
│ 13. Save Receipt     │
│  receipts table      │
│  receipt_lines       │
│  audit_log           │
└────┬─────────────────┘
     │
     ▼
┌──────────┐
│ Success! │
└──────────┘
```

---

## Component Diagram

### Core Components

```
┌─────────────────────────────────────────────────────────┐
│                    STREAMLIT APP                        │
│                                                         │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐   │
│  │   app.py    │  │  config.py  │  │   .env      │   │
│  │             │  │             │  │             │   │
│  │ • Main      │→ │ • Settings  │→ │ • API Keys  │   │
│  │ • Routing   │  │ • Validation│  │ • DB URL    │   │
│  │ • Session   │  │ • Paths     │  │ • Limits    │   │
│  └─────────────┘  └─────────────┘  └─────────────┘   │
│                                                         │
│  ┌─────────────────────────────────────────────────┐  │
│  │               PAGE COMPONENTS                   │  │
│  │                                                 │  │
│  │  page1_upload.py     → Capture & upload        │  │
│  │  page2_review.py     → OCR review & edit       │  │
│  │  page3_match_po.py   → PO matching             │  │
│  │  page4_match_lines.py→ Line matching           │  │
│  │  page5_submit.py     → Submit receipt          │  │
│  └─────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────┘
                            │
                            ▼
┌─────────────────────────────────────────────────────────┐
│                   SERVICE LAYER                         │
│                                                         │
│  ┌──────────────────┐  ┌──────────────────┐           │
│  │  OCR Service     │  │ Image Processor  │           │
│  ├──────────────────┤  ├──────────────────┤           │
│  │ extract_text()   │  │ preprocess()     │           │
│  │ extract_docket() │  │ deskew()         │           │
│  │ _extract_po()    │  │ denoise()        │           │
│  │ _extract_date()  │  │ threshold()      │           │
│  │ _extract_lines() │  │ enhance()        │           │
│  └──────────────────┘  └──────────────────┘           │
│                                                         │
│  ┌──────────────────┐  ┌──────────────────┐           │
│  │   PO Matcher     │  │  Cin7 Client     │           │
│  ├──────────────────┤  ├──────────────────┤           │
│  │ normalize_po()   │  │ find_pos()       │           │
│  │ find_matching()  │  │ get_po()         │           │
│  │ match_lines()    │  │ update_po()      │           │
│  │ rank_matches()   │  │ _make_request()  │           │
│  └──────────────────┘  │ _paginate()      │           │
│                        └──────────────────┘           │
│                                                         │
│  ┌──────────────────┐                                  │
│  │  Rate Limiter    │                                  │
│  ├──────────────────┤                                  │
│  │ acquire()        │                                  │
│  │ get_status()     │                                  │
│  │ _clean_windows() │                                  │
│  │ _calc_wait()     │                                  │
│  └──────────────────┘                                  │
└─────────────────────────────────────────────────────────┘
                            │
                            ▼
┌─────────────────────────────────────────────────────────┐
│                     DATA LAYER                          │
│                                                         │
│  ┌──────────────────┐  ┌──────────────────┐           │
│  │    db.py         │  │   schema.sql     │           │
│  ├──────────────────┤  ├──────────────────┤           │
│  │ SQLAlchemy ORM   │  │ CREATE TABLE     │           │
│  │ • Upload         │  │ • uploads        │           │
│  │ • Extraction     │  │ • extractions    │           │
│  │ • Receipt        │  │ • receipts       │           │
│  │ • AuditLog       │  │ • audit_log      │           │
│  └──────────────────┘  └──────────────────┘           │
│                                                         │
│  ┌──────────────────┐                                  │
│  │   migrate.py     │                                  │
│  ├──────────────────┤                                  │
│  │ run_migration()  │                                  │
│  └──────────────────┘                                  │
└─────────────────────────────────────────────────────────┘
```

---

## Database Schema

### Entity Relationship Diagram

```
┌─────────────────┐
│    uploads      │
│─────────────────│
│ id (PK)        │
│ filename       │
│ file_path      │
│ uploaded_at    │
│ uploaded_by    │
│ status         │
└────────┬────────┘
         │ 1
         │
         │ N
┌────────▼────────┐      ┌─────────────────┐
│  extractions    │      │ extraction_lines│
│─────────────────│      │─────────────────│
│ id (PK)        │ 1  N │ id (PK)        │
│ upload_id (FK) ├──────┤ extraction_id   │
│ supplier_name  │      │ line_number     │
│ docket_number  │      │ sku             │
│ po_reference   │      │ description     │
│ delivery_date  │      │ quantity        │
│ raw_ocr_text   │      │ confidence      │
│ confidence     │      │ flags           │
│ reviewed       │      └─────────────────┘
│ reviewed_at    │
│ reviewed_by    │
└────────┬────────┘
         │ 1
         │
         │ N
┌────────▼────────┐      ┌─────────────────┐
│    receipts     │      │  receipt_lines  │
│─────────────────│      │─────────────────│
│ id (PK)        │ 1  N │ id (PK)        │
│ extraction_id  ├──────┤ receipt_id (FK) │
│ cin7_po_id     │      │ extraction_line │
│ po_reference   │      │ cin7_line_id    │
│ supplier_name  │      │ sku             │
│ docket_number  │      │ description     │
│ receipt_date   │      │ qty_ordered     │
│ cin7_response  │      │ qty_received    │
│ cin7_receipt_id│      │ qty_remaining   │
│ posted_at      │      │ flags           │
│ posted_by      │      └─────────────────┘
│ status         │
│ error_message  │
└─────────────────┘

┌─────────────────┐
│   audit_log     │
│─────────────────│
│ id (PK)        │
│ entity_type    │
│ entity_id      │
│ action         │
│ user_id        │
│ changes (JSON) │
│ created_at     │
└─────────────────┘
```

### Table Details

**uploads** (1-to-many with extractions)
- Stores uploaded docket files
- Tracks file metadata
- Links to extraction results

**extractions** (1-to-many with extraction_lines, receipts)
- Stores OCR extraction results
- Header information from docket
- Links to uploaded file and receipt

**extraction_lines** (many-to-1 with extractions)
- Individual line items from docket
- SKU, description, quantity
- Confidence scores

**receipts** (1-to-many with receipt_lines)
- Final receipts posted to Cin7
- Links to extraction
- Stores Cin7 response

**receipt_lines** (many-to-1 with receipts)
- Line-level receipt details
- Quantities and matching info

**audit_log** (standalone)
- Tracks all system actions
- JSON change history
- User attribution

---

## Deployment Architecture

### Docker Compose Stack

```
┌─────────────────────────────────────────────────┐
│              Docker Host                        │
│                                                 │
│  ┌──────────────────────────────────────────┐  │
│  │   hdl_receipts_app (Container)           │  │
│  │                                          │  │
│  │  ┌────────────────────────────────────┐ │  │
│  │  │  Streamlit App                     │ │  │
│  │  │  • Python 3.11                     │ │  │
│  │  │  • Tesseract OCR                   │ │  │
│  │  │  • OpenCV                          │ │  │
│  │  │  • All dependencies                │ │  │
│  │  └────────────────────────────────────┘ │  │
│  │                                          │  │
│  │  Exposed Ports: 8501                    │  │
│  │  Volumes: /app/uploads, /app/logs       │  │
│  │  Environment: .env variables            │  │
│  └──────────────┬───────────────────────────┘  │
│                 │                               │
│                 │ Network: hdl_network          │
│                 │                               │
│  ┌──────────────▼───────────────────────────┐  │
│  │   hdl_receipts_db (Container)            │  │
│  │                                          │  │
│  │  ┌────────────────────────────────────┐ │  │
│  │  │  PostgreSQL 15                     │ │  │
│  │  │  • Database: hdl_receipts          │ │  │
│  │  │  • User: hdl_user                  │ │  │
│  │  │  • Schema auto-init                │ │  │
│  │  └────────────────────────────────────┘ │  │
│  │                                          │  │
│  │  Exposed Ports: 5432                    │  │
│  │  Volumes: postgres_data (persistent)    │  │
│  └──────────────────────────────────────────┘  │
│                                                 │
└─────────────────────────────────────────────────┘

External:
┌────────────────┐
│  Cin7 Omni API │
│  (External)    │
└────────────────┘
       ▲
       │ HTTPS
       │
```

### Production Deployment (Optional Nginx)

```
              ┌──────────┐
              │  Users   │
              └────┬─────┘
                   │ HTTPS (443)
                   │
         ┌─────────▼──────────┐
         │   Nginx Reverse    │
         │      Proxy         │
         │  • SSL Termination │
         │  • Load Balancing  │
         │  • Static Files    │
         └─────────┬──────────┘
                   │ HTTP (8501)
                   │
         ┌─────────▼──────────┐
         │  Streamlit App     │
         │  (Docker)          │
         └─────────┬──────────┘
                   │
         ┌─────────▼──────────┐
         │  PostgreSQL        │
         │  (Docker)          │
         └────────────────────┘
```

---

## Security Architecture

### Authentication & Authorization

```
┌──────────────┐
│    User      │
└──────┬───────┘
       │
       │ (Future: OAuth/LDAP)
       │
       ▼
┌──────────────────┐
│  Session State   │
│  • user_id       │
│  • permissions   │
└──────┬───────────┘
       │
       ▼
┌──────────────────┐
│  Application     │
│  • Validates     │
│  • Logs actions  │
└──────┬───────────┘
       │
       ▼
┌──────────────────┐
│  Audit Log       │
│  • Who           │
│  • What          │
│  • When          │
└──────────────────┘
```

### Data Flow Security

```
Upload → [Validation] → [Virus Scan] → Storage
                ↓
             Log Event
                ↓
            Audit Log

Cin7 API ← [Rate Limit] ← [Retry Logic] ← [Auth]
    ↓
[Response Log] → Database
    ↓
Audit Trail
```

---

## Performance Architecture

### Caching Strategy

```
┌─────────────────────┐
│  Streamlit Cache    │
│  @st.cache_data     │
│                     │
│  • Supplier list    │
│  • Config values    │
│  • Static data      │
│  TTL: 1 hour        │
└─────────────────────┘

┌─────────────────────┐
│  Session State      │
│  st.session_state   │
│                     │
│  • Current receipt  │
│  • Extracted data   │
│  • Matched PO       │
│  • User context     │
└─────────────────────┘

┌─────────────────────┐
│  Database Indexes   │
│                     │
│  • po_reference     │
│  • docket_number    │
│  • uploaded_at      │
│  • posted_at        │
└─────────────────────┘
```

### Rate Limiting

```
Request → [Queue] → [Rate Check] → [API Call]
                         │
                    ┌────▼────┐
                    │ 3/sec   │
                    │ 60/min  │
                    │ 5000/day│
                    └─────────┘
                         │
                    [Wait if needed]
                         │
                    [Grant access]
```

---

## Error Handling Architecture

### Error Flow

```
┌──────────────┐
│  Error       │
│  Occurs      │
└──────┬───────┘
       │
       ▼
┌──────────────────┐
│  Exception       │
│  Handler         │
└──────┬───────────┘
       │
       ├──→ [Cin7APIError] → Retry logic
       │
       ├──→ [DatabaseError] → Log & alert
       │
       ├──→ [ValidationError] → User message
       │
       └──→ [Unknown] → Log & generic message
                 │
                 ▼
         ┌───────────────┐
         │  Audit Log    │
         │  Error Log    │
         │  User Message │
         └───────────────┘
```

### Retry Strategy

```
API Request
    │
    ▼
[Attempt 1] ──Fail→ Wait 2s ──→ [Attempt 2]
                                      │
                                   Fail→ Wait 4s ──→ [Attempt 3]
                                                          │
                                                       Fail→ Error
```

---

## Scalability Considerations

### Current Capacity

```
Users:       10-20 concurrent
Receipts:    100-500 per day
Database:    Millions of records
API Calls:   < 5000 per day
```

### Scale-Up Path

```
Phase 1 (Current)
    ├─ Single server
    ├─ Docker Compose
    └─ PostgreSQL

Phase 2 (Growth)
    ├─ Load balancer
    ├─ Multiple app instances
    ├─ Separate DB server
    └─ Redis cache

Phase 3 (Enterprise)
    ├─ Kubernetes cluster
    ├─ Auto-scaling
    ├─ High-availability DB
    └─ CDN for static assets
```

---

**Last Updated**: January 2024
**Version**: 1.0.0
**Status**: Production Architecture ✅
