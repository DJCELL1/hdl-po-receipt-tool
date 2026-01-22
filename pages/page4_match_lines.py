"""
Page 4: Line Matching + Receipt Preview
"""

import streamlit as st
import pandas as pd
from services.po_matcher import POMatcher
from cin7.cin7_client import Cin7Client


def render():
    """Render the line matching page"""
    st.title("📋 Step 4: Match Line Items")

    # Validate prerequisites
    if not st.session_state.po_details or not st.session_state.extracted_data:
        st.error("❌ Missing data. Please go back.")
        return

    po_details = st.session_state.po_details
    extracted = st.session_state.extracted_data

    st.markdown(f"**PO:** {po_details.get('Reference')} | **Supplier:** {po_details.get('Supplier', {}).get('Name')}")

    # Perform line matching
    if 'matched_lines' not in st.session_state or st.button("🔄 Re-match Lines"):
        with st.spinner("🔄 Matching line items..."):
            try:
                cin7 = Cin7Client()
                matcher = POMatcher(cin7)

                docket_lines = extracted.get('line_items', [])
                po_lines = po_details.get('Lines', [])

                matched = matcher.match_line_items(docket_lines, po_lines)
                st.session_state.matched_lines = matched

            except Exception as e:
                st.error(f"❌ Matching Error: {str(e)}")
                return

    matched_lines = st.session_state.matched_lines

    # Summary stats
    total_lines = len(matched_lines)
    matched_count = len([m for m in matched_lines if m['po_line']])
    flagged_count = len([m for m in matched_lines if m['flags']])

    col1, col2, col3 = st.columns(3)
    col1.metric("Total Lines", total_lines)
    col2.metric("Matched", matched_count)
    col3.metric("Flagged", flagged_count, delta_color="off")

    st.markdown("---")

    # Display matched lines
    st.markdown("### 📦 Line Items Review")
    st.markdown("Review and adjust matches as needed")

    final_receipt_lines = []

    for i, match in enumerate(matched_lines):
        docket_line = match['docket_line']
        po_line = match['po_line']
        flags = match['flags']

        # Determine card color based on status
        if 'sku_not_found' in flags:
            card_type = "error"
        elif 'fuzzy_match_requires_confirmation' in flags or 'over_delivery' in flags:
            card_type = "warning"
        else:
            card_type = "success"

        # Display card
        with st.expander(
            f"Line {i + 1}: {docket_line.get('description', 'No description')[:50]} "
            f"{'⚠️' if flags else '✅'}",
            expanded=bool(flags)
        ):
            # Show match details
            col1, col2 = st.columns(2)

            with col1:
                st.markdown("**📄 Docket Line**")
                st.text(f"SKU: {docket_line.get('sku', 'N/A')}")
                st.text(f"Desc: {docket_line.get('description', 'N/A')[:40]}")
                st.text(f"Qty: {docket_line.get('quantity', 0)}")

            with col2:
                if po_line:
                    st.markdown("**📋 PO Line**")
                    st.text(f"Code: {po_line.get('Code', 'N/A')}")
                    st.text(f"Desc: {po_line.get('Description', 'N/A')[:40]}")
                    st.text(f"Ordered: {po_line.get('Qty', 0)}")
                    st.text(f"Received: {po_line.get('ReceivedQty', 0)}")
                    st.text(f"Remaining: {match['quantity_remaining']}")
                else:
                    st.warning("❌ No PO line matched")

            # Show match score
            if match['match_score'] > 0:
                st.info(f"Match Score: {match['match_score']}% ({match['match_method']})")

            # Display flags
            if flags:
                st.markdown("**⚠️ Flags:**")
                for flag in flags:
                    if flag == 'over_delivery':
                        st.error(f"❌ Over-delivery: Docket shows {docket_line.get('quantity')} but only {match['quantity_remaining']} remaining")
                    elif flag == 'fuzzy_match_requires_confirmation':
                        st.warning("⚠️ Fuzzy match - please confirm this is correct")
                    elif flag == 'sku_not_found':
                        st.error("❌ SKU not found in PO - manual intervention required")

            # Allow manual adjustment
            st.markdown("**Adjust Receipt Quantity:**")
            qty_to_receive = st.number_input(
                "Quantity to receive",
                min_value=0.0,
                max_value=float(match.get('quantity_remaining', docket_line.get('quantity', 0))),
                value=float(match.get('quantity_to_receive', 0)),
                step=1.0,
                key=f"qty_receive_{i}",
                help="Adjust if needed"
            )

            # Manual PO line reassignment
            if po_line is None:
                st.markdown("**Manual Assignment:**")
                all_po_lines = po_details.get('Lines', [])
                po_line_options = {f"{line.get('Code')} - {line.get('Description', '')[:40]}": line for line in all_po_lines}

                selected_po_line = st.selectbox(
                    "Assign to PO line",
                    options=["(None)"] + list(po_line_options.keys()),
                    key=f"manual_assign_{i}"
                )

                if selected_po_line != "(None)":
                    po_line = po_line_options[selected_po_line]

            # Build final receipt line
            if po_line:
                final_receipt_lines.append({
                    'docket_line': docket_line,
                    'po_line': po_line,
                    'quantity_to_receive': qty_to_receive,
                    'cin7_line_id': po_line.get('Id'),
                    'flags': flags
                })

    # Store final lines
    st.session_state.final_receipt_lines = final_receipt_lines

    # Receipt preview summary
    st.markdown("---")
    st.markdown("### 📊 Receipt Preview")

    if final_receipt_lines:
        preview_data = []
        for line in final_receipt_lines:
            preview_data.append({
                'SKU': line['po_line'].get('Code'),
                'Description': line['po_line'].get('Description', '')[:40],
                'Ordered': line['po_line'].get('Qty'),
                'Previously Received': line['po_line'].get('ReceivedQty', 0),
                'Receiving Now': line['quantity_to_receive'],
                'Flags': ', '.join(line['flags']) if line['flags'] else '✅'
            })

        df = pd.DataFrame(preview_data)
        st.dataframe(df, use_container_width=True)

        total_receiving = sum(line['quantity_to_receive'] for line in final_receipt_lines)
        st.metric("Total Units to Receipt", int(total_receiving))

    else:
        st.warning("⚠️ No lines ready to receipt")

    # Validation
    has_errors = any('sku_not_found' in line['flags'] for line in final_receipt_lines)
    needs_confirmation = any('fuzzy_match_requires_confirmation' in line['flags'] or 'over_delivery' in line['flags'] for line in final_receipt_lines)

    if has_errors:
        st.error("❌ Some lines have errors. Please resolve before continuing.")

    if needs_confirmation:
        st.warning("⚠️ Some lines require confirmation")
        confirm = st.checkbox("✅ I confirm the flagged lines are correct", key="confirm_flags")
    else:
        confirm = True

    # Navigation
    st.markdown("---")
    col1, col2 = st.columns(2)

    with col1:
        if st.button("⬅️ Back to PO Matching", use_container_width=True):
            st.session_state.current_step = 3
            st.rerun()

    with col2:
        if not has_errors and confirm and final_receipt_lines:
            if st.button("✅ Continue to Submit", type="primary", use_container_width=True):
                st.session_state.current_step = 5
                st.rerun()
        else:
            st.button("Continue (Disabled)", disabled=True, use_container_width=True)
