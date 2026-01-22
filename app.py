"""
HDL PO Receipt Tool - Main Streamlit Application
Multi-page app for receiving purchase orders via delivery docket OCR
"""

import streamlit as st
from pathlib import Path
import logging
import sys

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler('app.log')
    ]
)

logger = logging.getLogger(__name__)

# Page configuration
st.set_page_config(
    page_title="HDL PO Receipt Tool",
    page_icon="📦",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Initialize session state
def init_session_state():
    """Initialize all session state variables"""
    defaults = {
        'current_step': 1,
        'upload_id': None,
        'extraction_id': None,
        'uploaded_file_path': None,
        'extracted_data': None,
        'selected_po': None,
        'po_details': None,
        'matched_lines': None,
        'receipt_result': None,
        'user_id': 'warehouse_user',  # In production, use actual auth
    }

    for key, value in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = value

init_session_state()

# Sidebar navigation
with st.sidebar:
    st.title("📦 HDL PO Receipt Tool")
    st.markdown("---")

    # Step indicator
    steps = [
        "1️⃣ Upload Docket",
        "2️⃣ Review Extraction",
        "3️⃣ Match PO",
        "4️⃣ Match Lines",
        "5️⃣ Submit Receipt"
    ]

    current_step = st.session_state.current_step

    for i, step in enumerate(steps, 1):
        if i == current_step:
            st.markdown(f"**{step}** ⬅️")
        elif i < current_step:
            st.markdown(f"~~{step}~~ ✅")
        else:
            st.markdown(f"{step}")

    st.markdown("---")

    # Navigation buttons
    col1, col2 = st.columns(2)

    with col1:
        if current_step > 1:
            if st.button("⬅️ Back", use_container_width=True):
                st.session_state.current_step -= 1
                st.rerun()

    with col2:
        if current_step < 5:
            # Next button logic handled in individual pages
            pass

    st.markdown("---")

    # Status info
    if st.session_state.upload_id:
        st.success("✅ Docket uploaded")
    if st.session_state.extracted_data:
        st.success("✅ Data extracted")
    if st.session_state.selected_po:
        st.success("✅ PO matched")
    if st.session_state.matched_lines:
        st.success("✅ Lines matched")

    # Reset button
    st.markdown("---")
    if st.button("🔄 Start New Receipt", type="secondary", use_container_width=True):
        for key in list(st.session_state.keys()):
            if key not in ['current_step', 'user_id']:
                del st.session_state[key]
        st.session_state.current_step = 1
        st.rerun()

# Main content area - route to appropriate page
if current_step == 1:
    from pages import page1_upload
    page1_upload.render()
elif current_step == 2:
    from pages import page2_review
    page2_review.render()
elif current_step == 3:
    from pages import page3_match_po
    page3_match_po.render()
elif current_step == 4:
    from pages import page4_match_lines
    page4_match_lines.render()
elif current_step == 5:
    from pages import page5_submit
    page5_submit.render()
