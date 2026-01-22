"""
PO reference normalization and matching logic
Handles backorder suffixes (A/B/C) and fuzzy matching
"""

import re
from typing import Dict, List, Optional
from fuzzywuzzy import fuzz
import logging
import config

logger = logging.getLogger(__name__)


def normalize_po_ref(ref: str) -> Dict[str, Optional[str]]:
    """
    Normalize PO reference and extract backorder suffix

    Args:
        ref: Raw PO reference string

    Returns:
        {
            'normalized': str,      # Full normalized reference
            'base': str,            # Base reference without suffix
            'suffix': Optional[str] # Suffix (A/B/C) if present
        }

    Examples:
        'PO-12345A' -> {'normalized': 'PO-12345A', 'base': 'PO-12345', 'suffix': 'A'}
        'po 12345' -> {'normalized': 'PO-12345', 'base': 'PO-12345', 'suffix': None}
    """
    if not ref:
        return {'normalized': '', 'base': '', 'suffix': None}

    # Trim whitespace and uppercase
    ref = ref.strip().upper()

    # Remove multiple spaces/dashes
    ref = re.sub(r'[\s\-]+', '-', ref)

    # Ensure it starts with PO prefix
    if not ref.startswith('PO'):
        ref = 'PO-' + ref

    # Check if last character is a valid suffix
    suffix = None
    base = ref

    if ref and ref[-1] in config.VALID_PO_SUFFIXES:
        suffix = ref[-1]
        base = ref[:-1]

    result = {
        'normalized': ref,
        'base': base,
        'suffix': suffix
    }

    logger.debug(f"Normalized '{ref}' -> {result}")
    return result


class POMatchResult:
    """Represents a PO match with scoring"""

    def __init__(self, po_data: Dict, score: int, match_type: str, reason: str):
        self.po_data = po_data
        self.score = score
        self.match_type = match_type  # 'exact', 'base', 'fuzzy'
        self.reason = reason
        self.po_id = po_data.get('Id')
        self.reference = po_data.get('Reference')
        self.supplier = po_data.get('Supplier', {}).get('Name', '')

    def __repr__(self):
        return f"<POMatch {self.reference} score={self.score} type={self.match_type}>"


class POMatcher:
    """Matches extracted PO references to Cin7 purchase orders"""

    def __init__(self, cin7_client):
        self.cin7 = cin7_client

    def find_matching_pos(self, extracted_ref: str, supplier_name: Optional[str] = None) -> List[POMatchResult]:
        """
        Find matching POs using multi-strategy approach

        Strategy:
        1. Exact match on full reference
        2. If suffix exists, try base reference
        3. Try LIKE query with base%
        4. Rank by supplier similarity and recency

        Args:
            extracted_ref: PO reference from docket
            supplier_name: Supplier name for ranking (optional)

        Returns:
            List of POMatchResult ordered by score (best first)
        """
        if not extracted_ref:
            logger.warning("No PO reference provided")
            return []

        # Normalize reference
        norm = normalize_po_ref(extracted_ref)
        normalized_ref = norm['normalized']
        base_ref = norm['base']
        has_suffix = norm['suffix'] is not None

        logger.info(f"Searching for PO: {normalized_ref} (base: {base_ref}, suffix: {norm['suffix']})")

        matches = []

        # Strategy 1: Exact match on normalized reference
        try:
            exact_matches = self.cin7.find_purchase_orders(normalized_ref)
            for po in exact_matches:
                matches.append(POMatchResult(
                    po_data=po,
                    score=100,
                    match_type='exact',
                    reason=f"Exact match: {po.get('Reference')}"
                ))
            logger.info(f"Found {len(exact_matches)} exact matches")
        except Exception as e:
            logger.error(f"Error in exact match search: {e}")

        # Strategy 2: If suffix exists and no exact match, try base reference
        if has_suffix and not matches:
            try:
                base_matches = self.cin7.find_purchase_orders(base_ref)
                for po in base_matches:
                    po_ref = po.get('Reference', '')
                    # Only include if it's exactly the base (no suffix on the PO)
                    if po_ref == base_ref:
                        matches.append(POMatchResult(
                            po_data=po,
                            score=90,
                            match_type='base',
                            reason=f"Base reference match (no suffix): {po_ref}"
                        ))
                logger.info(f"Found {len([m for m in matches if m.match_type == 'base'])} base matches")
            except Exception as e:
                logger.error(f"Error in base match search: {e}")

        # Strategy 3: Wildcard search with base%
        if has_suffix:
            try:
                wildcard_matches = self.cin7.find_purchase_orders_by_base_ref(base_ref)
                for po in wildcard_matches:
                    po_ref = po.get('Reference', '')
                    # Skip if already matched
                    if any(m.reference == po_ref for m in matches):
                        continue
                    # Check if it has a valid suffix
                    if po_ref.startswith(base_ref) and len(po_ref) == len(base_ref) + 1:
                        suffix_char = po_ref[-1]
                        if suffix_char in config.VALID_PO_SUFFIXES:
                            matches.append(POMatchResult(
                                po_data=po,
                                score=85,
                                match_type='wildcard',
                                reason=f"Wildcard match: {po_ref}"
                            ))
                logger.info(f"Found {len([m for m in matches if m.match_type == 'wildcard'])} wildcard matches")
            except Exception as e:
                logger.error(f"Error in wildcard search: {e}")

        # Rank matches
        matches = self._rank_matches(matches, supplier_name)

        logger.info(f"Total matches found: {len(matches)}")
        return matches

    def _rank_matches(self, matches: List[POMatchResult], supplier_name: Optional[str] = None) -> List[POMatchResult]:
        """
        Rank matches by:
        1. Base score (exact > base > wildcard)
        2. Supplier name similarity
        3. Most recent PO date
        """
        if not matches:
            return []

        # Add supplier similarity bonus
        if supplier_name:
            for match in matches:
                po_supplier = match.supplier
                if po_supplier:
                    similarity = fuzz.ratio(supplier_name.lower(), po_supplier.lower())
                    # Add up to 10 points for supplier match
                    match.score += int(similarity / 10)

        # Add recency bonus (newer POs score higher)
        # Assume POs have a CreatedDate or similar field
        for match in matches:
            created_date = match.po_data.get('CreatedDate') or match.po_data.get('Date')
            if created_date:
                # Add small bonus for recent POs (up to 5 points)
                # This is simplified - in production, calculate days difference
                match.score += 2

        # Sort by score descending
        matches.sort(key=lambda m: m.score, reverse=True)

        return matches

    def match_line_items(
        self,
        docket_lines: List[Dict],
        po_lines: List[Dict],
        fuzzy_threshold: int = None
    ) -> List[Dict]:
        """
        Match docket line items to PO line items

        Matching rules:
        1. Exact SKU match (preferred)
        2. Fuzzy description match (requires manual confirmation)
        3. Flag mismatches

        Args:
            docket_lines: Lines from extracted docket
            po_lines: Lines from Cin7 PO
            fuzzy_threshold: Minimum fuzzy match score (default from config)

        Returns:
            List of matched line items with flags
        """
        if fuzzy_threshold is None:
            fuzzy_threshold = config.FUZZY_MATCH_THRESHOLD

        matched_lines = []

        for docket_line in docket_lines:
            docket_sku = docket_line.get('sku', '').strip().upper()
            docket_desc = docket_line.get('description', '').strip().lower()
            docket_qty = float(docket_line.get('quantity', 0))

            best_match = None
            best_score = 0
            match_method = None

            # Try to match with PO lines
            for po_line in po_lines:
                po_sku = po_line.get('Code', '').strip().upper()
                po_desc = po_line.get('Description', '').strip().lower()
                po_qty_ordered = float(po_line.get('Qty', 0))
                po_qty_received = float(po_line.get('ReceivedQty', 0))
                po_qty_remaining = po_qty_ordered - po_qty_received

                # Exact SKU match (100 score)
                if docket_sku and po_sku and docket_sku == po_sku:
                    best_match = po_line
                    best_score = 100
                    match_method = 'sku_exact'
                    break

                # Fuzzy description match
                if docket_desc and po_desc:
                    desc_score = fuzz.ratio(docket_desc, po_desc)
                    if desc_score > best_score and desc_score >= fuzzy_threshold:
                        best_match = po_line
                        best_score = desc_score
                        match_method = 'description_fuzzy'

            # Build matched line result
            flags = []

            if best_match:
                po_qty_ordered = float(best_match.get('Qty', 0))
                po_qty_received = float(best_match.get('ReceivedQty', 0))
                po_qty_remaining = po_qty_ordered - po_qty_received

                # Flag over-delivery
                if docket_qty > po_qty_remaining:
                    flags.append('over_delivery')

                # Flag fuzzy matches for manual review
                if match_method == 'description_fuzzy':
                    flags.append('fuzzy_match_requires_confirmation')

                matched_lines.append({
                    'docket_line': docket_line,
                    'po_line': best_match,
                    'match_score': best_score,
                    'match_method': match_method,
                    'quantity_to_receive': min(docket_qty, po_qty_remaining),
                    'quantity_ordered': po_qty_ordered,
                    'quantity_remaining': po_qty_remaining,
                    'flags': flags
                })
            else:
                # No match found
                flags.append('sku_not_found')
                matched_lines.append({
                    'docket_line': docket_line,
                    'po_line': None,
                    'match_score': 0,
                    'match_method': 'none',
                    'quantity_to_receive': docket_qty,
                    'flags': flags
                })

        logger.info(f"Matched {len([m for m in matched_lines if m['po_line']])} of {len(docket_lines)} lines")
        return matched_lines
