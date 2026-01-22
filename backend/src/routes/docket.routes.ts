import { Router, Response, Request } from 'express';
import multer from 'multer';
import { join } from 'path';
import { mkdirSync, existsSync } from 'fs';
import { ocrService } from '../services/ocrService';
import { PoMatcher } from '../services/poMatcher';
import { createCin7Client } from '../cin7/cin7Client';
import { db } from '../database/db';

const router = Router();

// Mock user ID for no-auth mode
const MOCK_USER_ID = 1;

// Setup file upload
const uploadDir = process.env.UPLOAD_DIR || join(__dirname, '../../uploads');
if (!existsSync(uploadDir)) {
  mkdirSync(uploadDir, { recursive: true });
}

const storage = multer.diskStorage({
  destination: (_req, _file, cb) => {
    cb(null, uploadDir);
  },
  filename: (_req, file, cb) => {
    const uniqueSuffix = Date.now() + '-' + Math.round(Math.random() * 1E9);
    cb(null, file.fieldname + '-' + uniqueSuffix + '-' + file.originalname);
  }
});

const upload = multer({
  storage,
  limits: {
    fileSize: 10 * 1024 * 1024 // 10MB
  },
  fileFilter: (req, file, cb) => {
    const allowedTypes = /jpeg|jpg|png|pdf/;
    const extname = allowedTypes.test(file.originalname.toLowerCase());
    const mimetype = allowedTypes.test(file.mimetype);

    if (extname && mimetype) {
      cb(null, true);
    } else {
      cb(new Error('Only images (JPEG, PNG) and PDF files are allowed'));
    }
  }
});

/**
 * POST /api/dockets/upload
 * Upload and process a docket image/PDF
 */
router.post(
  '/upload',
  upload.single('docket'),
  async (req: Request, res: Response) => {
    try {
      if (!req.file) {
        return res.status(400).json({ error: 'No file uploaded' });
      }

      const userId = MOCK_USER_ID;
      const filePath = req.file.path;

      // Save upload record
      const uploadResult = await db.query(
        `INSERT INTO uploads (user_id, file_path, file_type, file_size)
         VALUES ($1, $2, $3, $4)
         RETURNING id`,
        [userId, filePath, req.file.mimetype, req.file.size]
      );

      const uploadId = uploadResult.rows[0].id;

      // Process with OCR
      const startTime = Date.now();
      const extractedData = await ocrService.processDocket(filePath);
      const processingTime = Date.now() - startTime;

      // Save extraction record
      await db.query(
        `INSERT INTO extractions (upload_id, raw_text, parsed_json, confidence, processing_time_ms)
         VALUES ($1, $2, $3, $4, $5)`,
        [uploadId, extractedData.rawText, JSON.stringify(extractedData), extractedData.confidence, processingTime]
      );

      res.json({
        uploadId,
        extractedData,
        processingTime
      });
    } catch (error) {
      console.error('Upload processing error:', error);
      return res.status(500).json({ error: 'Failed to process docket' });
    }
  }
);

/**
 * POST /api/dockets/match-po
 * Match extracted docket data to Purchase Orders
 */
router.post(
  '/match-po',
  async (req: Request, res: Response) => {
    try {
      const { poReference, supplierName, lineItems } = req.body;

      if (!poReference) {
        return res.status(400).json({ error: 'PO reference is required' });
      }

      const cin7Client = createCin7Client();
      const poMatcher = new PoMatcher(cin7Client);

      const matchResult = await poMatcher.findMatches(
        poReference,
        supplierName,
        lineItems
      );

      res.json(matchResult);
    } catch (error) {
      console.error('PO matching error:', error);
      return res.status(500).json({ error: 'Failed to match Purchase Order' });
    }
  }
);

/**
 * POST /api/dockets/match-lines
 * Match docket line items to PO line items
 */
router.post(
  '/match-lines',
  async (req: Request, res: Response) => {
    try {
      const { poId, docketLines } = req.body;

      if (!poId || !docketLines) {
        return res.status(400).json({ error: 'PO ID and docket lines are required' });
      }

      const cin7Client = createCin7Client();
      const po = await cin7Client.getPurchaseOrderById(poId);
      const poMatcher = new PoMatcher(cin7Client);

      const lineMatches = poMatcher.matchLineItems(docketLines, po.OrderLines);

      res.json({
        po,
        lineMatches
      });
    } catch (error) {
      console.error('Line matching error:', error);
      return res.status(500).json({ error: 'Failed to match line items' });
    }
  }
);

/**
 * POST /api/dockets/receipt
 * Create receipt in Cin7
 */
router.post(
  '/receipt',
  async (req: Request, res: Response) => {
    try {
      const {
        poId,
        poReference,
        docketNumber,
        supplierName,
        deliveryDate,
        lineItems,
        allowOverride
      } = req.body;

      if (!poId || !lineItems || lineItems.length === 0) {
        return res.status(400).json({ error: 'PO ID and line items are required' });
      }

      const userId = MOCK_USER_ID;

      // Check for duplicate docket
      if (supplierName && docketNumber) {
        const duplicateCheck = await db.query(
          `SELECT id FROM receipts
           WHERE supplier_name = $1 AND docket_number = $2 AND status = 'completed'`,
          [supplierName, docketNumber]
        );

        if (duplicateCheck.rows.length > 0 && !allowOverride) {
          return res.status(409).json({
            error: 'Duplicate docket',
            message: `Docket ${docketNumber} from ${supplierName} has already been receipted`,
            receiptId: duplicateCheck.rows[0].id
          });
        }
      }

      const cin7Client = createCin7Client();

      // Get current PO state
      const po = await cin7Client.getPurchaseOrderById(poId);

      // Update received quantities
      const updatedOrderLines = po.OrderLines.map(orderLine => {
        const matchingLine = lineItems.find((item: any) => item.cin7LineId === orderLine.Id);

        if (matchingLine) {
          return {
            ...orderLine,
            ReceivedQty: orderLine.ReceivedQty + matchingLine.qtyReceipted
          };
        }

        return orderLine;
      });

      // Update PO in Cin7
      const updatedPo = await cin7Client.receiptPurchaseOrder(poId, {
        ...po,
        OrderLines: updatedOrderLines
      });

      // Save receipt record
      const receiptResult = await db.transaction(async (client) => {
        const receiptInsert = await client.query(
          `INSERT INTO receipts (
            user_id, cin7_po_id, cin7_po_reference, docket_number,
            supplier_name, delivery_date, receipt_payload_json, status
          ) VALUES ($1, $2, $3, $4, $5, $6, $7, $8)
          RETURNING id`,
          [
            userId,
            poId,
            poReference,
            docketNumber,
            supplierName,
            deliveryDate,
            JSON.stringify({ lineItems }),
            'completed'
          ]
        );

        const receiptId = receiptInsert.rows[0].id;

        // Save receipt lines
        for (const item of lineItems) {
          await client.query(
            `INSERT INTO receipt_lines (
              receipt_id, sku, description, qty_delivered, qty_receipted,
              unit, match_type, cin7_line_id, cin7_product_id
            ) VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9)`,
            [
              receiptId,
              item.sku,
              item.description,
              item.qtyDelivered,
              item.qtyReceipted,
              item.unit,
              item.matchType,
              item.cin7LineId,
              item.cin7ProductId
            ]
          );
        }

        // Audit log
        await client.query(
          `INSERT INTO audit_log (user_id, action, entity_type, entity_id, details)
           VALUES ($1, $2, $3, $4, $5)`,
          [
            userId,
            'receipt_created',
            'receipt',
            receiptId,
            JSON.stringify({ poId, poReference, docketNumber })
          ]
        );

        return receiptId;
      });

      res.json({
        success: true,
        receiptId: receiptResult,
        updatedPo
      });
    } catch (error: any) {
      console.error('Receipt creation error:', error);

      // Save failed receipt
      try {
        await db.query(
          `INSERT INTO receipts (
            user_id, cin7_po_id, cin7_po_reference, docket_number,
            supplier_name, status, error_message
          ) VALUES ($1, $2, $3, $4, $5, $6, $7)`,
          [
            MOCK_USER_ID,
            req.body.poId,
            req.body.poReference,
            req.body.docketNumber,
            req.body.supplierName,
            'failed',
            error.message
          ]
        );
      } catch (dbError) {
        console.error('Failed to log error receipt:', dbError);
      }

      return res.status(500).json({ error: 'Failed to create receipt', details: error.message });
    }
  }
);

/**
 * GET /api/dockets/receipts
 * Get receipt history
 */
router.get(
  '/receipts',
  async (req: Request, res: Response) => {
    try {
      const userId = MOCK_USER_ID;
      const limit = parseInt(req.query.limit as string) || 50;
      const offset = parseInt(req.query.offset as string) || 0;

      const result = await db.query(
        `SELECT r.*,
                COUNT(rl.id) as line_count
         FROM receipts r
         LEFT JOIN receipt_lines rl ON rl.receipt_id = r.id
         WHERE r.user_id = $1
         GROUP BY r.id
         ORDER BY r.created_at DESC
         LIMIT $2 OFFSET $3`,
        [userId, limit, offset]
      );

      res.json({
        receipts: result.rows,
        limit,
        offset
      });
    } catch (error) {
      console.error('Receipt history error:', error);
      return res.status(500).json({ error: 'Failed to fetch receipt history' });
    }
  }
);

/**
 * GET /api/dockets/receipts/:id
 * Get receipt details
 */
router.get(
  '/receipts/:id',
  async (req: Request, res: Response) => {
    try {
      const receiptId = parseInt(req.params.id);
      const userId = MOCK_USER_ID;

      const receiptResult = await db.query(
        'SELECT * FROM receipts WHERE id = $1 AND user_id = $2',
        [receiptId, userId]
      );

      if (receiptResult.rows.length === 0) {
        return res.status(404).json({ error: 'Receipt not found' });
      }

      const linesResult = await db.query(
        'SELECT * FROM receipt_lines WHERE receipt_id = $1 ORDER BY id',
        [receiptId]
      );

      res.json({
        receipt: receiptResult.rows[0],
        lines: linesResult.rows
      });
    } catch (error) {
      console.error('Receipt detail error:', error);
      return res.status(500).json({ error: 'Failed to fetch receipt details' });
    }
  }
);

export default router;
