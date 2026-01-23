# Deploying to Streamlit Cloud

Quick guide for deploying HDL PO Receipt Tool to Streamlit Cloud.

## ⚠️ Important: Database Dependency Issue

If you see `psycopg2-binary` build errors, use the alternative requirements file:

### Option 1: Rename Requirements File (Recommended)

In your GitHub repo, rename `requirements-streamlit-cloud.txt` to `requirements.txt`:

```bash
git mv requirements.txt requirements-local.txt
git mv requirements-streamlit-cloud.txt requirements.txt
git commit -m "Use Streamlit Cloud compatible requirements"
git push
```

### Option 2: Specify Requirements File in Streamlit Cloud

1. Go to your app settings in Streamlit Cloud
2. Click "Advanced settings"
3. Set "Python dependencies file" to: `requirements-streamlit-cloud.txt`

## System Dependencies

The `packages.txt` file tells Streamlit Cloud to install:
- `tesseract-ocr` - OCR engine
- `tesseract-ocr-eng` - English language data
- `libpq-dev` - PostgreSQL development headers
- `libgl1-mesa-glx` - OpenCV dependency
- `libglib2.0-0` - OpenCV dependency

## Deployment Steps

### 1. Prepare Your GitHub Repository

Ensure these files are in your repo:
- ✅ `app.py` - Main application
- ✅ `requirements.txt` or `requirements-streamlit-cloud.txt`
- ✅ `packages.txt` - System dependencies
- ✅ `.streamlit/config.toml` (optional)
- ✅ All other application files

### 2. Set Up Streamlit Cloud

1. Go to [share.streamlit.io](https://share.streamlit.io)
2. Sign in with GitHub
3. Click "New app"
4. Select your repository: `DJCELL1/HDL-PO-RECEIPT-TOOL`
5. Set main file path: `app.py`
6. Click "Advanced settings"

### 3. Configure Secrets

In "Advanced settings" → "Secrets", add:

```toml
# Cin7 API Configuration
CIN7_API_KEY = "your_actual_api_key_here"
CIN7_API_SECRET = "your_actual_api_secret_here"
CIN7_API_BASE_URL = "https://api.cin7.com/api"

# Database Configuration (if using external PostgreSQL)
DATABASE_URL = "postgresql://user:password@host:5432/database"

# Or for Streamlit Cloud with no external DB (optional)
# DATABASE_URL = "sqlite:///./hdl_receipts.db"

# OCR Configuration
TESSERACT_CMD = "/usr/bin/tesseract"

# Application Settings
APP_ENV = "production"
LOG_LEVEL = "INFO"
UPLOAD_DIR = "./uploads"
MAX_UPLOAD_SIZE_MB = "10"
FUZZY_MATCH_THRESHOLD = "85"
```

**Important**: Streamlit Cloud secrets are accessed differently in code:

```python
# In config.py or at the top of app.py
import streamlit as st

# Access secrets
CIN7_API_KEY = st.secrets.get("CIN7_API_KEY", os.getenv("CIN7_API_KEY"))
CIN7_API_SECRET = st.secrets.get("CIN7_API_SECRET", os.getenv("CIN7_API_SECRET"))
```

### 4. Database Considerations

**Option A: Use External PostgreSQL** (Recommended for production)

Provision a PostgreSQL database (options):
- [Neon](https://neon.tech) - Free PostgreSQL (recommended)
- [Supabase](https://supabase.com) - Free tier available
- [ElephantSQL](https://www.elephantsql.com) - Free tier available
- Any PostgreSQL hosting service

Then set `DATABASE_URL` in Streamlit secrets.

**Option B: Use SQLite** (For testing only - not recommended for production)

Streamlit Cloud has limited persistent storage, so SQLite will lose data between deploys.

To use SQLite temporarily:
```python
# In config.py
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./hdl_receipts.db")
```

### 5. Deploy

Click "Deploy!" and wait for:
1. System dependencies installation (packages.txt)
2. Python dependencies installation (requirements.txt)
3. Application startup

## Troubleshooting

### Error: `psycopg2-binary` build failed

**Solution**: Use `requirements-streamlit-cloud.txt` which uses `psycopg[binary]` instead.

### Error: `tesseract not found`

**Solution**: Ensure `packages.txt` is in the root directory and contains `tesseract-ocr`.

### Error: `opencv` import failed

**Solution**: Use `opencv-python-headless` in `requirements-streamlit-cloud.txt` (already included).

### Error: Database connection failed

**Solution**:
1. Check `DATABASE_URL` in Streamlit secrets
2. Ensure PostgreSQL is accessible from internet
3. Check firewall rules on database host

### Error: `No module named 'config'`

**Solution**: Ensure all project files are in the repository.

## Performance Notes

### Limitations on Streamlit Cloud

- **Resources**: Limited CPU/RAM (shared hosting)
- **Concurrent Users**: 3-5 maximum (free tier)
- **OCR Performance**: May be slower than local
- **File Storage**: Not persistent (uploads lost on redeploy)

### Recommendations

For production use:
- Use external PostgreSQL database
- Consider paid Streamlit Cloud tier for better performance
- Or deploy to dedicated server (see DEPLOYMENT_CHECKLIST.md)

## Alternative: Run Locally or Docker

If Streamlit Cloud limitations are too restrictive:

**Local Development:**
```bash
pip install -r requirements.txt
streamlit run app.py
```

**Docker Deployment:**
```bash
docker-compose up -d
```

See [SETUP_INSTRUCTIONS.md](SETUP_INSTRUCTIONS.md) for details.

## Configuration for Streamlit Cloud

Create `.streamlit/config.toml` in your repo:

```toml
[server]
maxUploadSize = 10
enableCORS = false
enableXsrfProtection = true

[browser]
gatherUsageStats = false

[theme]
primaryColor = "#FF4B4B"
backgroundColor = "#FFFFFF"
secondaryBackgroundColor = "#F0F2F6"
textColor = "#262730"
font = "sans serif"
```

## Update config.py for Streamlit Cloud

Add this at the top of `config.py`:

```python
import os
from pathlib import Path
from dotenv import load_dotenv

# Try to import streamlit for cloud deployment
try:
    import streamlit as st
    IN_STREAMLIT_CLOUD = True
except ImportError:
    IN_STREAMLIT_CLOUD = False

# Load environment variables
load_dotenv()

def get_env(key, default=""):
    """Get environment variable, checking Streamlit secrets first"""
    if IN_STREAMLIT_CLOUD and hasattr(st, 'secrets'):
        try:
            return st.secrets.get(key, os.getenv(key, default))
        except:
            pass
    return os.getenv(key, default)

# Then use get_env() instead of os.getenv()
CIN7_API_KEY = get_env("CIN7_API_KEY")
CIN7_API_SECRET = get_env("CIN7_API_SECRET")
# etc...
```

## Checklist

Before deploying to Streamlit Cloud:

- [ ] Repository is public or you have Streamlit Cloud Teams
- [ ] `packages.txt` is in root directory
- [ ] Using `requirements-streamlit-cloud.txt` or fixed `requirements.txt`
- [ ] All secrets configured in Streamlit Cloud
- [ ] External PostgreSQL database provisioned (recommended)
- [ ] Cin7 API credentials are valid
- [ ] Tested locally first

## Support

If deployment fails:
1. Check Streamlit Cloud logs
2. Review requirements file
3. Verify all secrets are set
4. Test locally with same dependencies
5. Open GitHub issue if needed

---

**For full deployment to production server, see [DEPLOYMENT_CHECKLIST.md](DEPLOYMENT_CHECKLIST.md)**
