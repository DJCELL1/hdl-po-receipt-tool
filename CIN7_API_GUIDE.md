# Cin7 Omni API Integration Guide

Complete guide for working with the Cin7 Omni API in the HDL PO Receipt Tool.

## Table of Contents

1. [API Overview](#api-overview)
2. [Authentication](#authentication)
3. [Rate Limiting](#rate-limiting)
4. [Endpoints Used](#endpoints-used)
5. [Error Handling](#error-handling)
6. [Testing](#testing)
7. [Troubleshooting](#troubleshooting)

---

## API Overview

### Base Information

- **Base URL**: `https://api.cin7.com/api`
- **Authentication**: HTTP Basic Auth
- **Content-Type**: `application/json`
- **API Version**: v1

### Getting API Credentials

1. Log in to Cin7 Omni
2. Navigate to **Settings** → **API** → **API Keys**
3. Click **Create New API Key**
4. Name: "HDL PO Receipt Tool"
5. Save **API Key** and **API Secret**
6. Add to `.env` file:
   ```bash
   CIN7_API_KEY=your_api_key_here
   CIN7_API_SECRET=your_api_secret_here
   ```

### Required Permissions

Your API key must have these permissions:

- ✅ **Purchase Orders** - Read & Write
- ✅ **Suppliers** - Read
- ✅ **Products** - Read (for SKU validation)

---

## Authentication

### Basic Auth

The API uses HTTP Basic Authentication:

```python
import requests
from requests.auth import HTTPBasicAuth

auth = HTTPBasicAuth(api_key, api_secret)
response = requests.get(
    'https://api.cin7.com/api/v1/PurchaseOrders',
    auth=auth
)
```

### In Our Client

```python
from cin7.cin7_client import Cin7Client

# Initialize with credentials
client = Cin7Client(
    api_key="your_key",
    api_secret="your_secret"
)

# Or use environment variables (recommended)
client = Cin7Client()  # Reads from .env
```

---

## Rate Limiting

### Official Limits

Cin7 enforces these rate limits:

| Period | Limit | Enforced By |
|--------|-------|-------------|
| Per Second | 3 requests | Application |
| Per Minute | 60 requests | Application |
| Per Day | 5,000 requests | Cin7 API |

### Our Rate Limiter

```python
from cin7.rate_limiter import RateLimiter

limiter = RateLimiter(
    per_second=3,
    per_minute=60,
    per_day=5000
)

# Acquire permission before making request
limiter.acquire()  # Blocks until allowed
make_api_request()

# Check current status
status = limiter.get_status()
print(status)
# {
#     'per_second': {'used': 2, 'limit': 3, 'remaining': 1},
#     'per_minute': {'used': 45, 'limit': 60, 'remaining': 15},
#     'per_day': {'used': 1230, 'limit': 5000, 'remaining': 3770}
# }
```

### How It Works

1. **Sliding Windows**: Tracks requests in 1-second, 1-minute, and 1-day windows
2. **Automatic Waiting**: Blocks when limit reached until window clears
3. **Thread-Safe**: Uses locks for concurrent access
4. **Transparent**: Caller doesn't need to handle timing

### Rate Limit Responses

**429 Too Many Requests:**
```json
{
    "error": "Rate limit exceeded",
    "retry_after": 60
}
```

**Our Handling:**
- Wait for `retry_after` seconds
- Retry automatically
- Log warning

---

## Endpoints Used

### 1. Find Purchase Orders

**Search by reference:**

```http
GET /v1/PurchaseOrders?where=Reference='PO-12345'
```

**Parameters:**
- `where`: Filter expression (URL encoded)
- `page`: Page number (default: 1)
- `rows`: Results per page (default: 250, max: 250)

**Example:**

```python
client = Cin7Client()

# Exact match
results = client.find_purchase_orders("PO-12345")

# Returns list of POs
for po in results:
    print(po['Id'], po['Reference'])
```

**Response:**

```json
[
    {
        "Id": "123456",
        "Reference": "PO-12345",
        "Supplier": {
            "Id": "789",
            "Name": "ACME Supplies"
        },
        "Status": "Open",
        "Date": "2024-01-15",
        "Total": 1250.50,
        "Lines": [
            {
                "Id": "line-1",
                "Code": "WIDGET-A",
                "Description": "Widget Type A",
                "Qty": 100,
                "ReceivedQty": 0,
                "UnitPrice": 10.50
            }
        ]
    }
]
```

### 2. Find POs with LIKE (Wildcard)

**Search for backorders:**

```http
GET /v1/PurchaseOrders?where=Reference LIKE 'PO-12345%'
```

**Example:**

```python
# Find all backorders for PO-12345
results = client.find_purchase_orders_by_base_ref("PO-12345")

# Returns: PO-12345, PO-12345A, PO-12345B, PO-12345C
```

**Note**: The `%` must be URL encoded as `%25` in the actual request.

### 3. Get Purchase Order Details

**Get full PO by ID:**

```http
GET /v1/PurchaseOrders/{id}
```

**Example:**

```python
po_details = client.get_purchase_order("123456")

print(po_details['Reference'])
print(f"Lines: {len(po_details['Lines'])}")
```

### 4. Update Purchase Order (Receipt)

**Update received quantities:**

```http
PUT /v1/PurchaseOrders/{id}
Content-Type: application/json
```

**Example:**

```python
# Get current PO
po = client.get_purchase_order("123456")

# Update received quantity on a line
for line in po['Lines']:
    if line['Code'] == 'WIDGET-A':
        line['ReceivedQty'] = float(line['ReceivedQty']) + 50

# Submit update
response = client.update_purchase_order("123456", po)
```

**Request Body:**

```json
{
    "Id": "123456",
    "Reference": "PO-12345",
    "Supplier": { ... },
    "Lines": [
        {
            "Id": "line-1",
            "Code": "WIDGET-A",
            "Description": "Widget Type A",
            "Qty": 100,
            "ReceivedQty": 50,  // ← Updated
            "UnitPrice": 10.50
        }
    ]
}
```

**Response:**

```json
{
    "Id": "123456",
    "Reference": "PO-12345",
    "Status": "Open",
    ...
}
```

### 5. Get Suppliers (Optional)

**Search suppliers:**

```http
GET /v1/Suppliers?where=Name LIKE '%ACME%'
```

**Example:**

```python
suppliers = client.get_suppliers(name_filter="ACME")

for supplier in suppliers:
    print(supplier['Id'], supplier['Name'])
```

---

## Error Handling

### HTTP Status Codes

| Code | Meaning | Our Response |
|------|---------|--------------|
| 200 | Success | Return data |
| 400 | Bad Request | Raise Cin7APIError |
| 401 | Unauthorized | Check credentials |
| 404 | Not Found | Return empty list |
| 429 | Rate Limit | Wait and retry |
| 500 | Server Error | Retry with backoff |
| 503 | Service Unavailable | Retry with backoff |

### Retry Logic

```python
def _make_request(method, endpoint, params, data, max_retries=3):
    for attempt in range(max_retries):
        try:
            # Wait for rate limiter
            rate_limiter.acquire()

            # Make request
            response = session.request(method, url, params, json=data)

            # Handle 429
            if response.status_code == 429:
                retry_after = int(response.headers.get('Retry-After', 60))
                time.sleep(retry_after)
                continue

            # Handle 503
            if response.status_code == 503:
                wait_time = (2 ** attempt) * 2  # Exponential backoff
                time.sleep(wait_time)
                continue

            # Success
            response.raise_for_status()
            return response.json()

        except RequestException as e:
            if attempt == max_retries - 1:
                raise Cin7APIError(f"Max retries exceeded: {e}")

            # Exponential backoff
            time.sleep((2 ** attempt) * 2)

    raise Cin7APIError("Request failed after all retries")
```

### Error Examples

**Invalid Credentials:**

```python
try:
    client = Cin7Client(api_key="wrong", api_secret="wrong")
    client.find_purchase_orders("PO-12345")
except Cin7APIError as e:
    print(f"Authentication failed: {e}")
    # Check CIN7_API_KEY and CIN7_API_SECRET in .env
```

**PO Not Found:**

```python
results = client.find_purchase_orders("PO-NONEXISTENT")
if not results:
    print("PO not found")
# Returns empty list, not an error
```

**Rate Limit Exceeded:**

```python
# Automatically handled by rate limiter
# Will wait and retry automatically
results = client.find_purchase_orders("PO-12345")
# No action needed from caller
```

---

## Testing

### Test API Connection

```python
from cin7.cin7_client import Cin7Client

try:
    client = Cin7Client()
    status = client.get_rate_limit_status()
    print("✅ API Connected")
    print(f"Rate limit remaining: {status['per_day']['remaining']}/5000")
except Exception as e:
    print(f"❌ API Error: {e}")
    print("Check your credentials in .env")
```

### Test PO Search

```python
client = Cin7Client()

# Search for a known PO
results = client.find_purchase_orders("PO-12345")

if results:
    print(f"✅ Found {len(results)} PO(s)")
    for po in results:
        print(f"  - {po['Reference']}: {po['Supplier']['Name']}")
else:
    print("⚠️  No POs found")
```

### Mock API for Testing

```python
import responses
from cin7.cin7_client import Cin7Client

@responses.activate
def test_find_po():
    # Mock API response
    responses.add(
        responses.GET,
        'https://api.cin7.com/api/v1/PurchaseOrders',
        json=[{
            'Id': '12345',
            'Reference': 'PO-12345',
            'Supplier': {'Name': 'Test Supplier'}
        }],
        status=200
    )

    # Test
    client = Cin7Client(api_key="test", api_secret="test")
    results = client.find_purchase_orders("PO-12345")

    assert len(results) == 1
    assert results[0]['Reference'] == 'PO-12345'
```

---

## Troubleshooting

### Common Issues

#### 1. "Cin7 API credentials not configured"

**Problem**: Missing or empty API credentials

**Solution**:
```bash
# Check .env file
cat .env | grep CIN7

# Should show:
# CIN7_API_KEY=your_key_here
# CIN7_API_SECRET=your_secret_here

# If missing, add them to .env
nano .env
```

#### 2. "401 Unauthorized"

**Problem**: Invalid API credentials

**Solution**:
1. Verify credentials in Cin7 portal
2. Check for extra spaces in .env
3. Ensure API key is active
4. Verify permissions are correct

```python
# Test auth
import requests
from requests.auth import HTTPBasicAuth

response = requests.get(
    'https://api.cin7.com/api/v1/PurchaseOrders',
    auth=HTTPBasicAuth('your_key', 'your_secret')
)
print(response.status_code)  # Should be 200
```

#### 3. "Rate limit exceeded"

**Problem**: Too many requests

**Solution**:
- Application automatically handles this
- If persistent, check for multiple instances
- Review daily usage in logs

```python
# Check current usage
client = Cin7Client()
status = client.get_rate_limit_status()
print(f"Daily usage: {status['per_day']['used']}/5000")
```

#### 4. "No POs found" (but PO exists in Cin7)

**Problem**: Search criteria not matching

**Solution**:
```python
# Try different searches
results = client.find_purchase_orders("PO-12345")  # Exact
results = client.find_purchase_orders("12345")      # Without prefix
results = client.find_purchase_orders_by_base_ref("PO-12345")  # Wildcard

# Check actual reference in Cin7
# Verify there are no extra spaces or characters
```

#### 5. "Connection timeout"

**Problem**: Network issues or Cin7 API down

**Solution**:
```bash
# Check network connectivity
curl -I https://api.cin7.com

# Check Cin7 status
# Visit: https://status.cin7.com

# Increase timeout (in cin7_client.py)
response = session.request(..., timeout=60)  # Default is 30
```

### Debug Mode

Enable detailed logging:

```python
import logging

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger('cin7')

# Now all API calls will be logged
client = Cin7Client()
results = client.find_purchase_orders("PO-12345")
```

### API Response Logging

All API responses are logged to the database:

```sql
-- View recent API responses
SELECT
    po_reference,
    cin7_response,
    posted_at
FROM receipts
ORDER BY posted_at DESC
LIMIT 10;
```

---

## Best Practices

### 1. Always Use Rate Limiter

```python
# ✅ Good - Rate limiter built into client
client = Cin7Client()
results = client.find_purchase_orders("PO-12345")

# ❌ Bad - Direct requests bypass rate limiting
import requests
requests.get('https://api.cin7.com/api/v1/PurchaseOrders')
```

### 2. Handle Errors Gracefully

```python
try:
    results = client.find_purchase_orders("PO-12345")
except Cin7APIError as e:
    logger.error(f"Cin7 API error: {e}")
    # Show user-friendly message
    st.error("Unable to connect to Cin7. Please try again.")
```

### 3. Use Pagination for Large Results

```python
# Client automatically handles pagination
results = client._paginate('v1/PurchaseOrders', params={'where': "Status='Open'"})
# Returns ALL results across all pages
```

### 4. Cache Frequently Used Data

```python
# Cache supplier list (changes infrequently)
@st.cache_data(ttl=3600)  # Cache for 1 hour
def get_suppliers():
    client = Cin7Client()
    return client.get_suppliers()
```

### 5. Monitor Daily Usage

```python
# Check at startup or periodically
client = Cin7Client()
status = client.get_rate_limit_status()

if status['per_day']['remaining'] < 100:
    logger.warning("Low daily API quota remaining!")
```

---

## API Reference Summary

| Method | Endpoint | Purpose |
|--------|----------|---------|
| `find_purchase_orders(ref)` | GET /v1/PurchaseOrders | Search by reference |
| `find_purchase_orders_by_base_ref(base)` | GET /v1/PurchaseOrders | Wildcard search |
| `get_purchase_order(id)` | GET /v1/PurchaseOrders/{id} | Get PO details |
| `update_purchase_order(id, data)` | PUT /v1/PurchaseOrders/{id} | Update PO (receipt) |
| `get_suppliers(filter)` | GET /v1/Suppliers | Search suppliers |
| `get_rate_limit_status()` | N/A | Check rate limits |

---

## Additional Resources

- **Cin7 API Documentation**: https://developers.cin7.com/
- **Cin7 Support**: support@cin7.com
- **API Status**: https://status.cin7.com
- **Our Implementation**: [cin7/cin7_client.py](cin7/cin7_client.py)

---

**Last Updated**: 2024
**Version**: 1.0.0
