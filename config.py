"""
Configuration module for HDL PO Receipt Tool
Loads environment variables and provides application settings
"""

import os
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Base paths
BASE_DIR = Path(__file__).parent
UPLOAD_DIR = Path(os.getenv("UPLOAD_DIR", "./uploads"))
UPLOAD_DIR.mkdir(exist_ok=True)

# Database Configuration
DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://hdl_user:changeme@localhost:5432/hdl_receipts")

# Cin7 API Configuration
CIN7_API_BASE_URL = os.getenv("CIN7_API_BASE_URL", "https://api.cin7.com/api").rstrip("/")
CIN7_API_KEY = os.getenv("CIN7_API_KEY", "")
CIN7_API_SECRET = os.getenv("CIN7_API_SECRET", "")

# Rate Limiting
CIN7_RATE_LIMIT_PER_SECOND = int(os.getenv("CIN7_RATE_LIMIT_PER_SECOND", "3"))
CIN7_RATE_LIMIT_PER_MINUTE = int(os.getenv("CIN7_RATE_LIMIT_PER_MINUTE", "60"))
CIN7_RATE_LIMIT_PER_DAY = int(os.getenv("CIN7_RATE_LIMIT_PER_DAY", "5000"))

# Application Settings
APP_ENV = os.getenv("APP_ENV", "development")
LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")
MAX_UPLOAD_SIZE_MB = int(os.getenv("MAX_UPLOAD_SIZE_MB", "10"))

# OCR Configuration
TESSERACT_CMD = os.getenv("TESSERACT_CMD", "/usr/bin/tesseract")

# Fuzzy Matching
FUZZY_MATCH_THRESHOLD = int(os.getenv("FUZZY_MATCH_THRESHOLD", "85"))

# PO Reference Backorder Suffixes
VALID_PO_SUFFIXES = ["A", "B", "C"]

def validate_config():
    """Validate critical configuration values"""
    errors = []

    if not CIN7_API_KEY:
        errors.append("CIN7_API_KEY is not set")

    if not CIN7_API_SECRET:
        errors.append("CIN7_API_SECRET is not set")

    if not DATABASE_URL:
        errors.append("DATABASE_URL is not set")

    if errors:
        raise ValueError(f"Configuration errors: {', '.join(errors)}")

    return True
