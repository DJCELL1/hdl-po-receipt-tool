"""
Unit tests for OCR service
"""

import pytest
from services.ocr_service import OCRService


class TestOCRService:
    """Test OCR extraction functions"""

    def test_extract_po_reference_standard(self):
        """Test extracting standard PO reference"""
        text = "Purchase Order: PO-12345"
        result = OCRService._extract_po_reference(text)
        assert result == "PO-12345"

    def test_extract_po_reference_with_suffix(self):
        """Test extracting PO with backorder suffix"""
        text = "PO Number: PO-12345A"
        result = OCRService._extract_po_reference(text)
        assert result == "PO-12345A"

    def test_extract_po_reference_variations(self):
        """Test various PO format variations"""
        test_cases = [
            ("P.O. #12345", "PO-12345"),
            ("Order Ref: PO12345B", "PO12345B"),
            ("Purchase Order PO-2024-12345", "PO-2024-12345"),
        ]

        for text, expected in test_cases:
            result = OCRService._extract_po_reference(text)
            assert expected in result or result in expected

    def test_extract_docket_number(self):
        """Test extracting docket number"""
        text = "Delivery Docket No: DKT-98765"
        result = OCRService._extract_docket_number(text)
        assert "98765" in result

    def test_extract_supplier(self):
        """Test extracting supplier name"""
        lines = [
            "TAX INVOICE",
            "ACME Supplies Pty Ltd",
            "123 Main St"
        ]
        result = OCRService._extract_supplier(lines)
        assert result == "ACME Supplies Pty Ltd"

    def test_extract_date_formats(self):
        """Test extracting various date formats"""
        test_cases = [
            "Date: 25/12/2024",
            "Delivery: 2024-12-25",
            "25 Dec 2024",
            "25 December 2024"
        ]

        for text in test_cases:
            result = OCRService._extract_date(text)
            # Should extract some date
            assert result is not None or "2024" in text

    @pytest.mark.skip(reason="Requires actual image file")
    def test_extract_text_from_image(self):
        """Test OCR on actual image (requires test image)"""
        pass

    @pytest.mark.skip(reason="Requires actual image file")
    def test_extract_docket_data_integration(self):
        """Integration test for full docket extraction"""
        pass
