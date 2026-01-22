# Cin7 Docket Receiver - API Documentation

Base URL: `http://localhost:3001/api`

## Authentication

All endpoints except `/auth/login` and `/auth/register` require authentication.

Include the JWT token in the Authorization header:
```
Authorization: Bearer <token>
```

---

## Auth Endpoints

### Register User

**POST** `/auth/register`

Create a new user account.

**Request Body:**
```json
{
  "email": "user@example.com",
  "password": "securepassword",
  "name": "John Doe" // optional
}
```

**Response:** `201 Created`
```json
{
  "user": {
    "id": 1,
    "email": "user@example.com",
    "name": "John Doe"
  },
  "token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
}
```

**Errors:**
- `400` - Validation error (invalid email, password too short)
- `409` - Email already exists

---

### Login

**POST** `/auth/login`

Authenticate and receive JWT token.

**Request Body:**
```json
{
  "email": "user@example.com",
  "password": "securepassword"
}
```

**Response:** `200 OK`
```json
{
  "user": {
    "id": 1,
    "email": "user@example.com",
    "name": "John Doe"
  },
  "token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
}
```

**Errors:**
- `401` - Invalid email or password

---

## Docket Endpoints

### Upload Docket

**POST** `/dockets/upload`

Upload and process a docket image/PDF using OCR.

**Request:** `multipart/form-data`
- `docket`: File (image/jpeg, image/png, application/pdf, max 10MB)

**Response:** `200 OK`
```json
{
  "uploadId": 123,
  "extractedData": {
    "supplierName": "Acme Corp",
    "docketNumber": "DOC-12345",
    "poReference": "PO-67890A",
    "deliveryDate": "2024-01-15",
    "lineItems": [
      {
        "sku": "WIDGET-001",
        "description": "Blue Widget",
        "quantity": 50,
        "unit": "EA"
      }
    ],
    "rawText": "...",
    "confidence": 87.5
  },
  "processingTime": 3450
}
```

**Errors:**
- `400` - No file uploaded or invalid file type
- `413` - File too large
- `500` - OCR processing failed

---

### Match Purchase Order

**POST** `/dockets/match-po`

Find matching Purchase Order(s) in Cin7 for the extracted docket data.

**Request Body:**
```json
{
  "poReference": "PO-67890A",
  "supplierName": "Acme Corp", // optional
  "lineItems": [ // optional
    { "sku": "WIDGET-001", "qty": 50 }
  ]
}
```

**Response:** `200 OK`
```json
{
  "bestMatch": {
    "po": {
      "Id": "abc123",
      "Reference": "PO-67890A",
      "Supplier": "Acme Corporation",
      "OrderDate": "2024-01-10",
      "OrderStatus": "Approved",
      "OrderLines": [
        {
          "Id": "line1",
          "ProductId": "prod1",
          "ProductCode": "WIDGET-001",
          "ProductDescription": "Blue Widget",
          "OrderedQty": 100,
          "ReceivedQty": 0,
          "UnitPrice": 25.00,
          "Total": 2500.00
        }
      ],
      "Total": 2500.00,
      "Currency": "USD"
    },
    "matchType": "exact",
    "confidence": 1.0,
    "reason": "Exact match on reference PO-67890A"
  },
  "alternativeMatches": [],
  "searchedReferences": ["PO-67890A"]
}
```

**Match Types:**
- `exact` - Exact reference match
- `base` - Base reference match (suffix stripped)
- `wildcard` - Wildcard match on base reference
- `supplier` - Matched by supplier only

**Errors:**
- `400` - Missing PO reference
- `500` - Cin7 API error

---

### Match Line Items

**POST** `/dockets/match-lines`

Match docket line items to PO line items.

**Request Body:**
```json
{
  "poId": "abc123",
  "docketLines": [
    {
      "sku": "WIDGET-001",
      "description": "Blue Widget",
      "qty": 50
    }
  ]
}
```

**Response:** `200 OK`
```json
{
  "po": { /* Full PO object */ },
  "lineMatches": [
    {
      "docketLine": {
        "sku": "WIDGET-001",
        "description": "Blue Widget",
        "qty": 50
      },
      "poLine": {
        "Id": "line1",
        "ProductCode": "WIDGET-001",
        "ProductDescription": "Blue Widget",
        "OrderedQty": 100,
        "ReceivedQty": 0
      },
      "matchType": "exact",
      "confidence": 1.0,
      "issues": []
    }
  ]
}
```

**Match Types:**
- `exact` - SKU exact match
- `fuzzy` - Description similarity match
- `unmatched` - No match found

**Possible Issues:**
- "Over-delivery: received X, remaining Y"
- "Quantity exceeds order: received X, ordered Y"
- "No matching line found in PO"
- "Fuzzy matched by description (XX% confidence)"

**Errors:**
- `400` - Missing poId or docketLines
- `500` - Cin7 API error

---

### Create Receipt

**POST** `/dockets/receipt`

Create a receipt in Cin7 and update PO received quantities.

**Request Body:**
```json
{
  "poId": "abc123",
  "poReference": "PO-67890A",
  "docketNumber": "DOC-12345",
  "supplierName": "Acme Corp",
  "deliveryDate": "2024-01-15",
  "lineItems": [
    {
      "sku": "WIDGET-001",
      "description": "Blue Widget",
      "qtyDelivered": 50,
      "qtyReceipted": 50,
      "unit": "EA",
      "matchType": "exact",
      "cin7LineId": "line1",
      "cin7ProductId": "prod1"
    }
  ],
  "allowOverride": false // Set true to bypass duplicate check
}
```

**Response:** `200 OK`
```json
{
  "success": true,
  "receiptId": 456,
  "updatedPo": { /* Updated PO object with new ReceivedQty */ }
}
```

**Errors:**
- `400` - Missing required fields
- `409` - Duplicate docket detected
- `500` - Receipt creation failed

**Duplicate Docket Response:**
```json
{
  "error": "Duplicate docket",
  "message": "Docket DOC-12345 from Acme Corp has already been receipted",
  "receiptId": 123
}
```

---

### Get Receipt History

**GET** `/dockets/receipts`

Get paginated list of receipts for the authenticated user.

**Query Parameters:**
- `limit` (optional, default: 50) - Number of records
- `offset` (optional, default: 0) - Offset for pagination

**Response:** `200 OK`
```json
{
  "receipts": [
    {
      "id": 456,
      "cin7_po_id": "abc123",
      "cin7_po_reference": "PO-67890A",
      "docket_number": "DOC-12345",
      "supplier_name": "Acme Corp",
      "delivery_date": "2024-01-15",
      "status": "completed",
      "created_at": "2024-01-15T14:30:00Z",
      "line_count": 1
    }
  ],
  "limit": 50,
  "offset": 0
}
```

**Status Values:**
- `pending` - Created but not submitted
- `processing` - Being submitted to Cin7
- `completed` - Successfully receipted
- `failed` - Error occurred
- `duplicate` - Detected as duplicate

---

### Get Receipt Details

**GET** `/dockets/receipts/:id`

Get detailed information for a specific receipt.

**Response:** `200 OK`
```json
{
  "receipt": {
    "id": 456,
    "cin7_po_id": "abc123",
    "cin7_po_reference": "PO-67890A",
    "docket_number": "DOC-12345",
    "supplier_name": "Acme Corp",
    "delivery_date": "2024-01-15",
    "status": "completed",
    "created_at": "2024-01-15T14:30:00Z",
    "receipt_payload_json": { /* Full receipt data */ }
  },
  "lines": [
    {
      "id": 1,
      "sku": "WIDGET-001",
      "description": "Blue Widget",
      "qty_delivered": 50,
      "qty_receipted": 50,
      "unit": "EA",
      "match_type": "exact",
      "cin7_line_id": "line1",
      "cin7_product_id": "prod1"
    }
  ]
}
```

**Errors:**
- `404` - Receipt not found or not owned by user

---

## Error Response Format

All error responses follow this format:

```json
{
  "error": "Error message",
  "details": "Additional details (in development mode)",
  "errors": [ /* Validation errors if applicable */ ]
}
```

**Common HTTP Status Codes:**
- `200` - Success
- `201` - Created
- `400` - Bad Request (validation error)
- `401` - Unauthorized (invalid/missing token)
- `403` - Forbidden (token expired)
- `404` - Not Found
- `409` - Conflict (duplicate)
- `413` - Payload Too Large
- `500` - Internal Server Error

---

## Rate Limiting

The API respects Cin7's rate limits:
- 3 requests/second
- 60 requests/minute
- 5000 requests/day

Requests are automatically queued and retried with exponential backoff when limits are hit.

---

## Example Workflow

Complete flow from docket upload to receipt:

```javascript
// 1. Login
const { token } = await POST('/auth/login', {
  email: 'user@example.com',
  password: 'password'
});

// 2. Upload docket
const formData = new FormData();
formData.append('docket', fileInput.files[0]);
const { extractedData } = await POST('/dockets/upload', formData, {
  headers: { Authorization: `Bearer ${token}` }
});

// 3. Match PO
const { bestMatch } = await POST('/dockets/match-po', {
  poReference: extractedData.poReference,
  supplierName: extractedData.supplierName,
  lineItems: extractedData.lineItems
}, {
  headers: { Authorization: `Bearer ${token}` }
});

// 4. Match lines
const { lineMatches } = await POST('/dockets/match-lines', {
  poId: bestMatch.po.Id,
  docketLines: extractedData.lineItems
}, {
  headers: { Authorization: `Bearer ${token}` }
});

// 5. Create receipt
const { receiptId } = await POST('/dockets/receipt', {
  poId: bestMatch.po.Id,
  poReference: bestMatch.po.Reference,
  docketNumber: extractedData.docketNumber,
  supplierName: extractedData.supplierName,
  deliveryDate: extractedData.deliveryDate,
  lineItems: lineMatches.map(m => ({
    sku: m.docketLine.sku,
    description: m.docketLine.description,
    qtyDelivered: m.docketLine.qty,
    qtyReceipted: m.docketLine.qty,
    matchType: m.matchType,
    cin7LineId: m.poLine?.Id,
    cin7ProductId: m.poLine?.ProductId
  }))
}, {
  headers: { Authorization: `Bearer ${token}` }
});

console.log('Receipt created:', receiptId);
```

---

**Last Updated:** January 2026
**API Version:** 1.0
