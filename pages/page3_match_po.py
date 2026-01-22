"""
Page 3: PO Matching (Cin7)
"""

import streamlit as st
from cin7.cin7_client import Cin7Client
from services.po_matcher import POMatcher
import config


def render():
    """Render the PO matching page"""
    st.title("🔗 Step 3: Match Purchase Order")

    extracted = st.session_state.extracted_data
    if not extracted:
        st.error("❌ No extraction data found. Please go back.")
        return

    po_reference = extracted.get('po_reference')
    supplier_name = extracted.get('supplier_name')

    st.markdown(f"**Looking for PO:** `{po_reference}`")
    if supplier_name:
        st.markdown(f"**Supplier:** {supplier_name}")

    # Initialize Cin7 client
    try:
        cin7 = Cin7Client()
    except Exception as e:
        st.error(f"❌ Cin7 API Error: {str(e)}")
        st.info("💡 Check your Cin7 API credentials in .env file")
        return

    # Search for matching POs
    if 'po_matches' not in st.session_state or st.button("🔄 Refresh Search"):
        with st.spinner("🔍 Searching Cin7 for matching POs..."):
            try:
                matcher = POMatcher(cin7)
                matches = matcher.find_matching_pos(po_reference, supplier_name)
                st.session_state.po_matches = matches
            except Exception as e:
                st.error(f"❌ Search Error: {str(e)}")
                return

    matches = st.session_state.get('po_matches', [])

    if not matches:
        st.warning("⚠️ No matching POs found in Cin7")

        # Manual search option
        st.markdown("---")
        st.markdown("### 🔍 Manual Search")

        manual_ref = st.text_input("Enter PO Reference manually", value=po_reference)

        if st.button("Search", type="primary"):
            with st.spinner("Searching..."):
                try:
                    matcher = POMatcher(cin7)
                    matches = matcher.find_matching_pos(manual_ref, supplier_name)
                    st.session_state.po_matches = matches
                    st.rerun()
                except Exception as e:
                    st.error(f"❌ Error: {str(e)}")

    else:
        # Display matches
        st.success(f"✅ Found {len(matches)} potential match(es)")

        # Best match (highlighted)
        if matches:
            best_match = matches[0]

            st.markdown("### 🎯 Best Match")
            display_po_card(best_match, is_best=True)

            if st.button("✅ Use This PO", type="primary", key="use_best"):
                select_po(cin7, best_match)
                st.session_state.current_step = 4
                st.rerun()

        # Alternate matches
        if len(matches) > 1:
            st.markdown("---")
            st.markdown("### 📋 Alternate Matches")

            for i, match in enumerate(matches[1:], 1):
                with st.expander(f"Alternative {i}: {match.reference} (Score: {match.score})"):
                    display_po_card(match, is_best=False)

                    if st.button(f"Use This PO", key=f"use_alt_{i}"):
                        select_po(cin7, match)
                        st.session_state.current_step = 4
                        st.rerun()

    # Manual override option
    st.markdown("---")
    with st.expander("🛠️ Advanced: Manual PO ID Override"):
        st.warning("⚠️ Use this only if you know the exact Cin7 PO ID")

        manual_po_id = st.text_input("Cin7 PO ID")

        if manual_po_id and st.button("Fetch PO by ID"):
            with st.spinner("Fetching PO details..."):
                try:
                    po_details = cin7.get_purchase_order(manual_po_id)
                    st.session_state.selected_po = {
                        'id': po_details.get('Id'),
                        'reference': po_details.get('Reference'),
                        'supplier': po_details.get('Supplier', {}).get('Name')
                    }
                    st.session_state.po_details = po_details
                    st.success("✅ PO fetched successfully!")
                    st.session_state.current_step = 4
                    st.rerun()
                except Exception as e:
                    st.error(f"❌ Error: {str(e)}")

    # Navigation
    st.markdown("---")
    if st.button("⬅️ Back to Review", use_container_width=True):
        st.session_state.current_step = 2
        st.rerun()


def display_po_card(match, is_best: bool = False):
    """Display PO match details in a card"""
    po = match.po_data

    if is_best:
        st.success(f"**Match Score:** {match.score}/100 ({match.match_type.upper()})")
    else:
        st.info(f"**Match Score:** {match.score}/100 ({match.match_type.upper()})")

    col1, col2 = st.columns(2)

    with col1:
        st.markdown(f"**PO Reference:** {po.get('Reference', 'N/A')}")
        st.markdown(f"**Cin7 PO ID:** {po.get('Id', 'N/A')}")
        st.markdown(f"**Supplier:** {po.get('Supplier', {}).get('Name', 'N/A')}")

    with col2:
        st.markdown(f"**Status:** {po.get('Status', 'N/A')}")
        st.markdown(f"**Date:** {po.get('Date', 'N/A')}")
        st.markdown(f"**Total:** {po.get('Total', 'N/A')}")

    # Show reason
    st.caption(f"💡 {match.reason}")


def select_po(cin7: Cin7Client, match):
    """Select a PO and fetch full details"""
    try:
        po_details = cin7.get_purchase_order(match.po_id)

        st.session_state.selected_po = {
            'id': match.po_id,
            'reference': match.reference,
            'supplier': match.supplier
        }
        st.session_state.po_details = po_details

    except Exception as e:
        st.error(f"❌ Error fetching PO details: {str(e)}")
        raise
