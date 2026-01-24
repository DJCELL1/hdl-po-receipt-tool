"""
Configuration module for HDL PO Receipt Tool
Loads environment variables and provides application settings
Supports both local .env files and Streamlit Cloud secrets
"""

import os
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Try to import streamlit for cloud deployment
try:
    import streamlit as st
    # Check if we're in Streamlit Cloud by attempting to access secrets
    try:
        IN_STREAMLIT_CLOUD = hasattr(st, 'secrets') and len(st.secrets) > 0
    except (FileNotFoundError, RuntimeError):
        # No secrets file means we're running locally
        IN_STREAMLIT_CLOUD = False
except ImportError:
    IN_STREAMLIT_CLOUD = False


def get_env(key: str, default: str = "") -> str:
    """
    Get environment variable, checking Streamlit secrets first if available

    Args:
        key: Environment variable name
        default: Default value if not found

    Returns:
        Environment variable value or default
    """
    if IN_STREAMLIT_CLOUD:
        try:
            return st.secrets.get(key, os.getenv(key, default))
        except Exception:
            pass
    return os.getenv(key, default)


# Base paths
BASE_DIR = Path(__file__).parent
UPLOAD_DIR = Path(get_env("UPLOAD_DIR", "./uploads"))
UPLOAD_DIR.mkdir(exist_ok=True, parents=True)

# Database Configuration
DATABASE_URL = get_env("DATABASE_URL", "postgresql://hdl_user:changeme@localhost:5432/hdl_receipts")

# Cin7 API Configuration
CIN7_API_BASE_URL = get_env("CIN7_API_BASE_URL", "https://api.cin7.com/api").rstrip("/")
CIN7_API_KEY = get_env("CIN7_API_KEY", "")
CIN7_API_SECRET = get_env("CIN7_API_SECRET", "")

# Rate Limiting
CIN7_RATE_LIMIT_PER_SECOND = int(get_env("CIN7_RATE_LIMIT_PER_SECOND", "3"))
CIN7_RATE_LIMIT_PER_MINUTE = int(get_env("CIN7_RATE_LIMIT_PER_MINUTE", "60"))
CIN7_RATE_LIMIT_PER_DAY = int(get_env("CIN7_RATE_LIMIT_PER_DAY", "5000"))

# Application Settings
APP_ENV = get_env("APP_ENV", "development")
LOG_LEVEL = get_env("LOG_LEVEL", "INFO")
MAX_UPLOAD_SIZE_MB = int(get_env("MAX_UPLOAD_SIZE_MB", "10"))

# OCR Configuration
TESSERACT_CMD = get_env("TESSERACT_CMD", "/usr/bin/tesseract")

# Fuzzy Matching
FUZZY_MATCH_THRESHOLD = int(get_env("FUZZY_MATCH_THRESHOLD", "85"))

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
