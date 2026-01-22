"""
OCR service for extracting text and structured data from delivery dockets
Uses Tesseract OCR with preprocessing
"""

import pytesseract
import re
from typing import Dict, List, Optional
from datetime import datetime
import logging
from pathlib import Path
import config
from services.image_processor import ImageProcessor

logger = logging.getLogger(__name__)

# Configure Tesseract path
if config.TESSERACT_CMD:
    pytesseract.pytesseract.tesseract_cmd = config.TESSERACT_CMD


class OCRService:
    """Extract text and structured data from delivery dockets"""

    @staticmethod
    def extract_text(image_path: str, preprocess: bool = True) -> Dict:
        """
        Extract raw text from image using OCR
        Returns: {
            'text': str,
            'confidence': float
        }
        """
        try:
            if preprocess:
                # Preprocess image
                processed_img = ImageProcessor.preprocess_for_ocr(image_path)
            else:
                processed_img = ImageProcessor.load_image(image_path)

            # Run OCR with detailed output
            ocr_data = pytesseract.image_to_data(
                processed_img,
                output_type=pytesseract.Output.DICT,
                config='--psm 6'  # Assume uniform text block
            )

            # Extract text
            text = pytesseract.image_to_string(processed_img, config='--psm 6')

            # Calculate average confidence
            confidences = [int(conf) for conf in ocr_data['conf'] if int(conf) > 0]
            avg_confidence = sum(confidences) / len(confidences) if confidences else 0

            logger.info(f"OCR complete. Confidence: {avg_confidence:.1f}%")

            return {
                'text': text.strip(),
                'confidence': round(avg_confidence, 2),
                'word_count': len(text.split())
            }

        except Exception as e:
            logger.error(f"OCR error: {e}")
            raise

    @staticmethod
    def extract_docket_data(image_path: str) -> Dict:
        """
        Extract structured data from delivery docket
        Returns: {
            'supplier_name': str,
            'docket_number': str,
            'po_reference': str,
            'delivery_date': date,
            'line_items': List[Dict],
            'raw_text': str,
            'confidence': float
        }
        """
        # Get raw OCR text
        ocr_result = OCRService.extract_text(image_path)
        text = ocr_result['text']
        lines = text.split('\n')

        # Initialize extraction result
        result = {
            'supplier_name': None,
            'docket_number': None,
            'po_reference': None,
            'delivery_date': None,
            'line_items': [],
            'raw_text': text,
            'confidence': ocr_result['confidence']
        }

        # Extract supplier name (usually near top)
        result['supplier_name'] = OCRService._extract_supplier(lines)

        # Extract docket number
        result['docket_number'] = OCRService._extract_docket_number(text)

        # Extract PO reference
        result['po_reference'] = OCRService._extract_po_reference(text)

        # Extract delivery date
        result['delivery_date'] = OCRService._extract_date(text)

        # Extract line items
        result['line_items'] = OCRService._extract_line_items(lines)

        logger.info(f"Extracted: PO={result['po_reference']}, Docket={result['docket_number']}, Lines={len(result['line_items'])}")

        return result

    @staticmethod
    def _extract_supplier(lines: List[str]) -> Optional[str]:
        """Extract supplier name from top of document"""
        # Look in first 10 lines for company name indicators
        for line in lines[:10]:
            line = line.strip()
            # Skip empty lines and lines with common header words
            if not line or line.lower() in ['tax invoice', 'delivery docket', 'invoice', 'receipt']:
                continue
            # First substantial line is often company name
            if len(line) > 5 and not re.match(r'^[\d\s\-/]+$', line):
                return line
        return None

    @staticmethod
    def _extract_docket_number(text: str) -> Optional[str]:
        """Extract delivery docket number"""
        patterns = [
            r'(?:docket|delivery)\s*(?:no|number|#)[\s:]*([A-Z0-9\-]+)',
            r'(?:doc|dkt)\s*(?:no|#)[\s:]*([A-Z0-9\-]+)',
            r'delivery\s+([A-Z0-9]{5,})',
        ]

        for pattern in patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                return match.group(1).strip()

        return None

    @staticmethod
    def _extract_po_reference(text: str) -> Optional[str]:
        """Extract PO reference number"""
        patterns = [
            r'(?:PO|P\.O\.|Purchase Order)[\s#:]*([A-Z0-9\-]+[ABC]?)',
            r'(?:Order|Ref|Reference)[\s#:]*([A-Z0-9\-]{5,}[ABC]?)',
            r'\b(PO[-\s]?\d{4,}[ABC]?)\b',
        ]

        for pattern in patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                po_ref = match.group(1).strip().upper()
                # Clean up common OCR errors
                po_ref = po_ref.replace(' ', '').replace('.', '-')
                return po_ref

        return None

    @staticmethod
    def _extract_date(text: str) -> Optional[datetime]:
        """Extract delivery date"""
        date_patterns = [
            r'\b(\d{1,2}[/-]\d{1,2}[/-]\d{2,4})\b',
            r'\b(\d{4}[/-]\d{1,2}[/-]\d{1,2})\b',
            r'\b(\d{1,2}\s+(?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)[a-z]*\s+\d{2,4})\b',
        ]

        for pattern in date_patterns:
            matches = re.findall(pattern, text, re.IGNORECASE)
            for date_str in matches:
                try:
                    # Try various date formats
                    for fmt in ['%d/%m/%Y', '%d-%m-%Y', '%Y/%m/%d', '%Y-%m-%d', '%d/%m/%y', '%d %b %Y', '%d %B %Y']:
                        try:
                            return datetime.strptime(date_str, fmt).date()
                        except ValueError:
                            continue
                except Exception:
                    continue

        return None

    @staticmethod
    def _extract_line_items(lines: List[str]) -> List[Dict]:
        """
        Extract line items from docket
        Each line item contains: SKU, description, quantity
        """
        line_items = []
        in_items_section = False

        # Patterns for line items
        qty_pattern = r'\b(\d+(?:\.\d+)?)\b'
        sku_pattern = r'\b([A-Z0-9]{3,}[-_]?[A-Z0-9]*)\b'

        for i, line in enumerate(lines):
            line = line.strip()
            if not line:
                continue

            # Detect start of items section
            if re.search(r'(?:item|product|description|qty|quantity)', line, re.IGNORECASE):
                in_items_section = True
                continue

            # Detect end of items section
            if re.search(r'(?:total|subtotal|tax|gst|notes|signature)', line, re.IGNORECASE):
                break

            if in_items_section:
                # Extract quantity (usually a number)
                qty_matches = re.findall(qty_pattern, line)

                # Extract SKU (alphanumeric code)
                sku_matches = re.findall(sku_pattern, line)

                # Extract description (remaining text)
                desc = line

                if qty_matches:
                    line_items.append({
                        'line_number': len(line_items) + 1,
                        'sku': sku_matches[0] if sku_matches else None,
                        'description': desc,
                        'quantity': float(qty_matches[-1]),  # Last number is usually qty
                        'confidence': 70  # Default confidence
                    })

        logger.info(f"Extracted {len(line_items)} line items")
        return line_items
