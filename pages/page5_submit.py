"""
Page 5: Submit Receipt to Cin7
"""

import streamlit as st
from datetime import datetime
import json
from cin7.cin7_client import Cin7Client
from database.db import SessionLocal, Receipt, ReceiptLine, check_duplicate_receipt


def render():
    """Render the submit receipt page"""
    st.title("✅ Step 5: Submit Receipt")

    # Validate prerequisites
    if not st.session_state.final_receipt_lines or not st.session_state.po_details:
        st.error("❌ Missing data. Please go back.")
        return

    po_details = st.session_state.po_details
    extracted = st.session_state.extracted_data
    final_lines = st.session_state.final_receipt_lines

    # Display summary
    st.markdown("### 📋 Receipt Summary")

    col1, col2 = st.columns(2)

    with col1:
        st.markdown(f"**PO Reference:** {po_details.get('Reference')}")
        st.markdown(f"**Cin7 PO ID:** {po_details.get('Id')}")
        st.markdown(f"**Supplier:** {extracted.get('supplier_name')}")

    with col2:
        st.markdown(f"**Docket Number:** {extracted.get('docket_number')}")
        st.markdown(f"**Delivery Date:** {extracted.get('delivery_date')}")
        st.markdown(f"**Line Items:** {len(final_lines)}")

    # Check for duplicate
    st.markdown("---")
    db = SessionLocal()
    is_duplicate = check_duplicate_receipt(
        db,
        extracted.get('supplier_name'),
        extracted.get('docket_number')
    )
    db.close()

    if is_duplicate:
        st.error("⚠️ **DUPLICATE DETECTED**")
        st.error(f"A receipt for docket **{extracted.get('docket_number')}** from **{extracted.get('supplier_name')}** already exists!")

        allow_override = st.checkbox("⚠️ Override and submit anyway (use with caution)")

        if not allow_override:
            st.markdown("---")
            if st.button("⬅️ Go Back", use_container_width=True):
                st.session_state.current_step = 4
                st.rerun()
            return

    # Show receipt details
    st.markdown("### 📦 Items to Receipt")

    for i, line in enumerate(final_lines, 1):
        po_line = line['po_line']
        qty = line['quantity_to_receive']

        st.markdown(
            f"{i}. **{po_line.get('Code')}** - {po_line.get('Description', '')[:50]} | "
            f"Qty: **{qty}**"
        )

    total_qty = sum(line['quantity_to_receive'] for line in final_lines)
    st.metric("Total Quantity", int(total_qty))

    # Final confirmation
    st.markdown("---")
    st.warning("⚠️ **This action will update Cin7 Omni. Please review carefully before submitting.**")

    confirm_checkbox = st.checkbox("✅ I confirm all details are correct and ready to receipt", key="final_confirm")

    # Submit button
    if confirm_checkbox:
        if st.button("🚀 Submit Receipt to Cin7", type="primary", use_container_width=True):
            submit_receipt()
    else:
        st.button("Submit (Disabled)", disabled=True, use_container_width=True)

    # Navigation
    st.markdown("---")
    if st.button("⬅️ Back to Line Matching", use_container_width=True):
        st.session_state.current_step = 4
        st.rerun()


def submit_receipt():
    """Submit receipt to Cin7 and save to database"""
    po_details = st.session_state.po_details
    extracted = st.session_state.extracted_data
    final_lines = st.session_state.final_receipt_lines

    with st.spinner("🚀 Submitting receipt to Cin7..."):
        try:
            cin7 = Cin7Client()

            # Build receipt payload
            # Update PO with received quantities
            po_id = po_details.get('Id')

            # Clone PO data and update line quantities
            updated_po = po_details.copy()

            for receipt_line in final_lines:
                cin7_line_id = receipt_line['cin7_line_id']
                qty_to_receive = receipt_line['quantity_to_receive']

                # Find the corresponding line in the PO
                for po_line in updated_po.get('Lines', []):
                    if po_line.get('Id') == cin7_line_id:
                        current_received = float(po_line.get('ReceivedQty', 0))
                        new_received = current_received + qty_to_receive
                        po_line['ReceivedQty'] = new_received
                        break

            # Submit to Cin7
            response = cin7.update_purchase_order(po_id, updated_po)

            # Save to database
            db = SessionLocal()
            try:
                receipt = Receipt(
                    extraction_id=st.session_state.extraction_id,
                    cin7_po_id=po_id,
                    po_reference=po_details.get('Reference'),
                    supplier_name=extracted.get('supplier_name'),
                    docket_number=extracted.get('docket_number'),
                    receipt_date=extracted.get('delivery_date'),
                    cin7_response=response,
                    cin7_receipt_id=response.get('Id') if response else None,
                    posted_by=st.session_state.user_id,
                    status='success'
                )
                db.add(receipt)
                db.flush()

                # Save receipt lines
                for receipt_line in final_lines:
                    po_line = receipt_line['po_line']

                    db_line = ReceiptLine(
                        receipt_id=receipt.id,
                        cin7_line_id=receipt_line['cin7_line_id'],
                        sku=po_line.get('Code'),
                        description=po_line.get('Description'),
                        quantity_ordered=po_line.get('Qty'),
                        quantity_received=receipt_line['quantity_to_receive'],
                        quantity_remaining=float(po_line.get('Qty', 0)) - float(po_line.get('ReceivedQty', 0)) - receipt_line['quantity_to_receive'],
                        flags=receipt_line['flags']
                    )
                    db.add(db_line)

                db.commit()
                db.refresh(receipt)

                st.session_state.receipt_result = {
                    'receipt_id': str(receipt.id),
                    'cin7_receipt_id': receipt.cin7_receipt_id,
                    'success': True
                }

            finally:
                db.close()

            # Show success
            st.success("✅ **Receipt submitted successfully!**")
            st.balloons()

            st.markdown(f"**Receipt ID:** {st.session_state.receipt_result['receipt_id']}")
            st.markdown(f"**Cin7 Response:** {response.get('Reference', 'Updated')}")

            # Show next steps
            st.markdown("---")
            st.markdown("### 🎉 What's Next?")

            col1, col2 = st.columns(2)

            with col1:
                if st.button("📦 Receipt Another Docket", use_container_width=True):
                    # Reset session
                    for key in list(st.session_state.keys()):
                        if key not in ['user_id']:
                            del st.session_state[key]
                    st.session_state.current_step = 1
                    st.rerun()

            with col2:
                if st.button("📊 View Receipt History", use_container_width=True):
                    st.info("Receipt history feature coming soon!")

        except Exception as e:
            st.error(f"❌ **Submission Failed**")
            st.error(f"Error: {str(e)}")

            # Save failed receipt to DB
            db = SessionLocal()
            try:
                receipt = Receipt(
                    extraction_id=st.session_state.extraction_id,
                    cin7_po_id=po_details.get('Id'),
                    po_reference=po_details.get('Reference'),
                    supplier_name=extracted.get('supplier_name'),
                    docket_number=extracted.get('docket_number'),
                    receipt_date=extracted.get('delivery_date'),
                    posted_by=st.session_state.user_id,
                    status='failed',
                    error_message=str(e)
                )
                db.add(receipt)
                db.commit()
            finally:
                db.close()

            st.markdown("---")
            st.markdown("### 🔧 Troubleshooting")
            st.markdown("- Check your Cin7 API credentials")
            st.markdown("- Verify the PO is still open in Cin7")
            st.markdown("- Check network connectivity")
            st.markdown("- Review error details above")
