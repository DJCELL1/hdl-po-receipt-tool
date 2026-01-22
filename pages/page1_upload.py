"""
Page 1: Capture / Upload Delivery Docket
"""

import streamlit as st
from pathlib import Path
from datetime import datetime
import uuid
import config
from database.db import SessionLocal, Upload


def render():
    """Render the upload page"""
    st.title("📸 Step 1: Upload Delivery Docket")
    st.markdown("Take a photo or upload an image of the delivery docket")

    # Create tabs for different input methods
    tab1, tab2 = st.tabs(["📷 Camera", "📁 File Upload"])

    with tab1:
        st.markdown("### Take Photo")
        st.markdown("📱 **Mobile users:** This will use your device camera")

        camera_photo = st.camera_input("Capture delivery docket")

        if camera_photo:
            st.image(camera_photo, caption="Captured Image", use_container_width=True)

            if st.button("✅ Use This Photo", type="primary", use_container_width=True):
                success = save_upload(camera_photo, "camera_capture.jpg")
                if success:
                    st.success("✅ Photo saved successfully!")
                    st.session_state.current_step = 2
                    st.rerun()

    with tab2:
        st.markdown("### Upload File")
        st.markdown("📄 **Supported formats:** JPG, PNG, PDF")

        uploaded_file = st.file_uploader(
            "Choose a file",
            type=['jpg', 'jpeg', 'png', 'pdf'],
            help=f"Max file size: {config.MAX_UPLOAD_SIZE_MB}MB"
        )

        if uploaded_file:
            # Show preview
            if uploaded_file.type.startswith('image'):
                st.image(uploaded_file, caption=f"Preview: {uploaded_file.name}", use_container_width=True)
            else:
                st.info(f"📄 PDF file: {uploaded_file.name}")

            # File info
            file_size_mb = uploaded_file.size / (1024 * 1024)
            st.caption(f"File size: {file_size_mb:.2f} MB")

            if file_size_mb > config.MAX_UPLOAD_SIZE_MB:
                st.error(f"❌ File too large. Maximum size is {config.MAX_UPLOAD_SIZE_MB}MB")
            else:
                if st.button("✅ Upload and Continue", type="primary", use_container_width=True):
                    success = save_upload(uploaded_file, uploaded_file.name)
                    if success:
                        st.success("✅ File uploaded successfully!")
                        st.session_state.current_step = 2
                        st.rerun()

    # Instructions
    with st.expander("📋 Tips for Best Results"):
        st.markdown("""
        **For optimal OCR accuracy:**
        - Ensure the document is well-lit
        - Avoid shadows and glare
        - Keep the camera/document steady
        - Capture the entire document
        - Ensure text is in focus and readable
        - Place the document on a flat surface
        """)


def save_upload(file_data, filename: str) -> bool:
    """
    Save uploaded file and create database record

    Args:
        file_data: Streamlit UploadedFile or camera input
        filename: Original filename

    Returns:
        bool: Success status
    """
    try:
        # Generate unique filename
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        file_id = str(uuid.uuid4())[:8]
        ext = Path(filename).suffix
        unique_filename = f"{timestamp}_{file_id}{ext}"

        # Save to uploads directory
        file_path = config.UPLOAD_DIR / unique_filename
        with open(file_path, 'wb') as f:
            f.write(file_data.getvalue())

        # Create database record
        db = SessionLocal()
        try:
            upload = Upload(
                filename=filename,
                file_path=str(file_path),
                file_size_bytes=file_data.size,
                mime_type=file_data.type if hasattr(file_data, 'type') else 'image/jpeg',
                uploaded_by=st.session_state.user_id,
                status='completed'
            )
            db.add(upload)
            db.commit()
            db.refresh(upload)

            # Store in session state
            st.session_state.upload_id = str(upload.id)
            st.session_state.uploaded_file_path = str(file_path)

            return True

        finally:
            db.close()

    except Exception as e:
        st.error(f"❌ Error saving file: {str(e)}")
        return False
