import { createWorker, Worker } from 'tesseract.js';
import { imagePreprocessor } from './imagePreprocessor';
// @ts-ignore - pdf-parse doesn't have type definitions
import pdfParse from 'pdf-parse';
import { readFileSync } from 'fs';

export interface ExtractedDocketData {
  supplierName?: string;
  docketNumber?: string;
  poReference?: string;
  deliveryDate?: string;
  lineItems: Array<{
    sku?: string;
    description: string;
    quantity: number;
    unit?: string;
  }>;
  rawText: string;
  confidence: number;
}

export class OcrService {
  private worker: Worker | null = null;

  async initialize(): Promise<void> {
    if (!this.worker) {
      console.log('Initializing Tesseract worker...');
      this.worker = await createWorker('eng');
      console.log('Tesseract worker initialized');
    }
  }

  async cleanup(): Promise<void> {
    if (this.worker) {
      await this.worker.terminate();
      this.worker = null;
    }
  }

  /**
   * Extract text from image using OCR
   */
  async extractTextFromImage(imagePath: string): Promise<{ text: string; confidence: number }> {
    await this.initialize();

    try {
      // Preprocess image
      const preprocessedPath = imagePath.replace(/\.(jpg|jpeg|png)$/i, '_processed.png');
      await imagePreprocessor.preprocessImage(imagePath, preprocessedPath);

      // Perform OCR
      const { data } = await this.worker!.recognize(preprocessedPath);

      return {
        text: data.text,
        confidence: data.confidence
      };
    } catch (error) {
      console.error('OCR extraction failed:', error);
      throw new Error(`Failed to extract text from image: ${error}`);
    }
  }

  /**
   * Extract text from PDF
   */
  async extractTextFromPdf(pdfPath: string): Promise<{ text: string; confidence: number }> {
    try {
      const dataBuffer = readFileSync(pdfPath);
      const data = await pdfParse(dataBuffer);

      return {
        text: data.text,
        confidence: 95 // PDF text extraction is generally high confidence
      };
    } catch (error) {
      console.error('PDF extraction failed:', error);
      throw new Error(`Failed to extract text from PDF: ${error}`);
    }
  }

  /**
   * Parse extracted text into structured docket data
   */
  parseDocketText(text: string, confidence: number): ExtractedDocketData {
    const lines = text.split('\n').map(line => line.trim()).filter(line => line.length > 0);

    const result: ExtractedDocketData = {
      lineItems: [],
      rawText: text,
      confidence
    };

    // Pattern matching for common docket fields
    const patterns = {
      supplier: /(?:supplier|vendor|from)[\s:]+([^\n]+)/i,
      docketNumber: /(?:docket|delivery|invoice|doc)[\s#:no.]+([A-Z0-9\-]+)/i,
      poReference: /(?:po|purchase\s*order|p\.o\.|order)[\s#:no.]+([A-Z0-9\-]+[ABC]?)/i,
      deliveryDate: /(?:date|delivered|delivery\s*date)[\s:]+(\d{1,2}[\/\-]\d{1,2}[\/\-]\d{2,4})/i,
    };

    // Extract header fields
    for (const line of lines) {
      if (!result.supplierName) {
        const supplierMatch = line.match(patterns.supplier);
        if (supplierMatch) result.supplierName = supplierMatch[1].trim();
      }

      if (!result.docketNumber) {
        const docketMatch = line.match(patterns.docketNumber);
        if (docketMatch) result.docketNumber = docketMatch[1].trim();
      }

      if (!result.poReference) {
        const poMatch = line.match(patterns.poReference);
        if (poMatch) result.poReference = poMatch[1].trim();
      }

      if (!result.deliveryDate) {
        const dateMatch = line.match(patterns.deliveryDate);
        if (dateMatch) result.deliveryDate = dateMatch[1].trim();
      }
    }

    // Extract line items
    // Look for patterns like: "SKU123  Widget Description  5  EA"
    // or: "Product ABC  10  units"
    const lineItemPattern = /^([A-Z0-9\-]+)?\s+(.+?)\s+(\d+(?:\.\d+)?)\s*([A-Z]+)?$/i;

    for (const line of lines) {
      const match = line.match(lineItemPattern);
      if (match) {
        const [, sku, description, qtyStr, unit] = match;
        const quantity = parseFloat(qtyStr);

        if (quantity > 0 && description.length > 2) {
          result.lineItems.push({
            sku: sku?.trim(),
            description: description.trim(),
            quantity,
            unit: unit?.trim()
          });
        }
      }
    }

    // If no structured line items found, try alternative parsing
    if (result.lineItems.length === 0) {
      result.lineItems = this.parseLineItemsFallback(lines);
    }

    return result;
  }

  /**
   * Fallback parser for line items when main pattern fails
   */
  private parseLineItemsFallback(lines: string[]): ExtractedDocketData['lineItems'] {
    const items: ExtractedDocketData['lineItems'] = [];

    // Look for any line with a number that could be quantity
    for (let i = 0; i < lines.length; i++) {
      const line = lines[i];
      const numbers = line.match(/\b(\d+(?:\.\d+)?)\b/g);

      if (numbers && numbers.length > 0) {
        // Take last number as quantity (common in dockets)
        const qty = parseFloat(numbers[numbers.length - 1]);

        if (qty > 0 && qty < 10000) { // Reasonable quantity range
          // Use rest of line as description
          const description = line.replace(/\b\d+(?:\.\d+)?\b/g, '').trim();

          if (description.length > 3) {
            items.push({
              description,
              quantity: qty
            });
          }
        }
      }
    }

    return items;
  }

  /**
   * Full pipeline: extract and parse docket from file
   */
  async processDocket(filePath: string): Promise<ExtractedDocketData> {
    const isPdf = /\.pdf$/i.test(filePath);

    const { text, confidence } = isPdf
      ? await this.extractTextFromPdf(filePath)
      : await this.extractTextFromImage(filePath);

    return this.parseDocketText(text, confidence);
  }
}

export const ocrService = new OcrService();
