"""
Page 2: OCR + Extraction Review
"""

import streamlit as st
from datetime import datetime
import uuid
from database.db import SessionLocal, Extraction, ExtractionLine
from services.ocr_service import OCRService


def render():
    """Render the extraction review page"""
    st.title("🔍 Step 2: Review Extracted Data")

    if not st.session_state.uploaded_file_path:
        st.error("❌ No file uploaded. Please go back to Step 1.")
        return

    # Run OCR if not already done
    if not st.session_state.extracted_data:
        with st.spinner("🔄 Extracting data from docket... This may take a moment."):
            try:
                extracted = OCRService.extract_docket_data(st.session_state.uploaded_file_path)
                st.session_state.extracted_data = extracted
            except Exception as e:
                st.error(f"❌ OCR Error: {str(e)}")
                return

    extracted = st.session_state.extracted_data

    # Show extracted data with edit capability
    st.markdown("### 📄 Extracted Information")
    st.markdown("Review and edit any fields as needed")

    col1, col2 = st.columns(2)

    with col1:
        # Supplier name
        confidence_icon = "🟢" if extracted.get('confidence', 0) > 80 else "🟡" if extracted.get('confidence', 0) > 60 else "🔴"
        st.markdown(f"**Overall Confidence:** {confidence_icon} {extracted.get('confidence', 0):.1f}%")

        supplier_name = st.text_input(
            "Supplier Name",
            value=extracted.get('supplier_name', ''),
            help="Company delivering the goods"
        )

        docket_number = st.text_input(
            "Docket Number",
            value=extracted.get('docket_number', ''),
            help="Delivery docket reference number"
        )

    with col2:
        po_reference = st.text_input(
            "PO Reference",
            value=extracted.get('po_reference', ''),
            help="Purchase Order number (may include A/B/C suffix for backorders)"
        )

        delivery_date = st.date_input(
            "Delivery Date",
            value=extracted.get('delivery_date') or datetime.now().date()
        )

    # Line items
    st.markdown("---")
    st.markdown("### 📦 Line Items")
    st.markdown("Review delivered quantities for each item")

    line_items = extracted.get('line_items', [])

    if line_items:
        # Editable dataframe for line items
        edited_lines = []

        for i, line in enumerate(line_items):
            with st.expander(f"Line {i + 1}: {line.get('description', 'No description')[:50]}", expanded=True):
                col1, col2, col3 = st.columns([2, 2, 1])

                with col1:
                    sku = st.text_input(
                        "SKU / Code",
                        value=line.get('sku', ''),
                        key=f"sku_{i}"
                    )

                with col2:
                    description = st.text_input(
                        "Description",
                        value=line.get('description', ''),
                        key=f"desc_{i}"
                    )

                with col3:
                    quantity = st.number_input(
                        "Quantity",
                        min_value=0.0,
                        value=float(line.get('quantity', 0)),
                        step=1.0,
                        key=f"qty_{i}"
                    )

                # Show confidence if low
                line_conf = line.get('confidence', 100)
                if line_conf < 80:
                    st.warning(f"⚠️ Low confidence: {line_conf}%")

                edited_lines.append({
                    'line_number': i + 1,
                    'sku': sku,
                    'description': description,
                    'quantity': quantity,
                    'confidence': line_conf
                })

        # Update extracted data with edits
        extracted['line_items'] = edited_lines
        extracted['supplier_name'] = supplier_name
        extracted['docket_number'] = docket_number
        extracted['po_reference'] = po_reference
        extracted['delivery_date'] = delivery_date

    else:
        st.warning("⚠️ No line items detected. You may need to add them manually.")

        # Add line item manually
        if st.button("➕ Add Line Item"):
            if 'line_items' not in extracted:
                extracted['line_items'] = []
            extracted['line_items'].append({
                'line_number': len(extracted['line_items']) + 1,
                'sku': '',
                'description': '',
                'quantity': 0,
                'confidence': 100
            })
            st.rerun()

    # Raw OCR text (collapsed)
    with st.expander("📝 View Raw OCR Text"):
        st.text(extracted.get('raw_text', 'No text extracted'))

    # Validation
    st.markdown("---")
    validation_errors = []

    if not po_reference:
        validation_errors.append("❌ PO Reference is required")
    if not docket_number:
        validation_errors.append("❌ Docket Number is required")
    if not line_items or len(line_items) == 0:
        validation_errors.append("❌ At least one line item is required")

    if validation_errors:
        for error in validation_errors:
            st.error(error)

    # Navigation
    col1, col2 = st.columns([1, 1])

    with col1:
        if st.button("⬅️ Back to Upload", use_container_width=True):
            st.session_state.current_step = 1
            st.rerun()

    with col2:
        if not validation_errors:
            if st.button("✅ Confirm and Continue", type="primary", use_container_width=True):
                # Save to database
                if save_extraction(extracted):
                    st.session_state.current_step = 3
                    st.rerun()


def save_extraction(extracted: dict) -> bool:
    """Save extraction to database"""
    try:
        db = SessionLocal()
        try:
            extraction = Extraction(
                upload_id=st.session_state.upload_id,
                supplier_name=extracted.get('supplier_name'),
                docket_number=extracted.get('docket_number'),
                po_reference=extracted.get('po_reference'),
                delivery_date=extracted.get('delivery_date'),
                raw_ocr_text=extracted.get('raw_text'),
                confidence_score=extracted.get('confidence'),
                reviewed=True,
                reviewed_by=st.session_state.user_id,
                reviewed_at=datetime.now()
            )
            db.add(extraction)
            db.flush()

            # Save line items
            for line in extracted.get('line_items', []):
                extraction_line = ExtractionLine(
                    extraction_id=extraction.id,
                    line_number=line['line_number'],
                    sku=line.get('sku'),
                    description=line.get('description'),
                    quantity_delivered=line.get('quantity'),
                    confidence_score=line.get('confidence')
                )
                db.add(extraction_line)

            db.commit()
            db.refresh(extraction)

            st.session_state.extraction_id = str(extraction.id)
            return True

        finally:
            db.close()

    except Exception as e:
        st.error(f"❌ Error saving extraction: {str(e)}")
        return False
