import { Cin7Client } from '../cin7/cin7Client';
import { Cin7PurchaseOrder } from '../cin7/types';
import { normalizePoRef, calculateSimilarity } from '../utils/poReference';

export interface PoMatchCandidate {
  po: Cin7PurchaseOrder;
  matchType: 'exact' | 'base' | 'wildcard' | 'supplier';
  confidence: number;
  reason: string;
}

export interface PoMatchResult {
  bestMatch?: PoMatchCandidate;
  alternativeMatches: PoMatchCandidate[];
  searchedReferences: string[];
}

export class PoMatcher {
  constructor(private cin7Client: Cin7Client) {}

  /**
   * Find and rank Purchase Order matches for a given reference
   */
  async findMatches(
    poReference: string,
    supplierName?: string,
    expectedLineItems?: Array<{ sku: string; qty: number }>
  ): Promise<PoMatchResult> {
    const searchedReferences: string[] = [];
    const candidates: PoMatchCandidate[] = [];

    // Parse the PO reference
    const parsed = normalizePoRef(poReference);
    console.log('Parsed PO reference:', parsed);

    // Step 1: Try exact match on normalized reference
    try {
      const exactMatches = await this.cin7Client.findPurchaseOrders(parsed.normalized);
      searchedReferences.push(parsed.normalized);

      for (const po of exactMatches) {
        candidates.push({
          po,
          matchType: 'exact',
          confidence: 1.0,
          reason: `Exact match on reference ${parsed.normalized}`
        });
      }
    } catch (error) {
      console.error('Error searching exact reference:', error);
    }

    // Step 2: If no exact match and suffix exists, try base reference
    if (candidates.length === 0 && parsed.suffix) {
      try {
        const baseMatches = await this.cin7Client.findPurchaseOrders(parsed.base);
        searchedReferences.push(parsed.base);

        for (const po of baseMatches) {
          const confidence = this.calculatePoConfidence(po, supplierName, expectedLineItems);
          candidates.push({
            po,
            matchType: 'base',
            confidence: confidence * 0.9, // Slightly lower confidence for base match
            reason: `Base reference match (${parsed.base}) - suffix ${parsed.suffix} not found`
          });
        }
      } catch (error) {
        console.error('Error searching base reference:', error);
      }
    }

    // Step 3: If still no match and suffix exists, try wildcard search
    if (candidates.length === 0 && parsed.suffix) {
      try {
        const wildcardMatches = await this.cin7Client.findPurchaseOrders(parsed.base, true);
        searchedReferences.push(`${parsed.base}%`);

        for (const po of wildcardMatches) {
          const confidence = this.calculatePoConfidence(po, supplierName, expectedLineItems);
          candidates.push({
            po,
            matchType: 'wildcard',
            confidence: confidence * 0.8,
            reason: `Wildcard match (${parsed.base}%) - related PO found`
          });
        }
      } catch (error) {
        console.error('Error searching wildcard reference:', error);
      }
    }

    // Step 4: Filter by supplier if provided
    if (supplierName && candidates.length > 0) {
      candidates.forEach(candidate => {
        const supplierSimilarity = calculateSimilarity(
          supplierName,
          candidate.po.Supplier || ''
        );

        if (supplierSimilarity < 0.7) {
          candidate.confidence *= 0.5; // Reduce confidence if supplier doesn't match well
          candidate.reason += ` (supplier mismatch: expected "${supplierName}", got "${candidate.po.Supplier}")`;
        }
      });
    }

    // Step 5: Rank candidates
    candidates.sort((a, b) => b.confidence - a.confidence);

    // Separate best match from alternatives
    const bestMatch = candidates.length > 0 ? candidates[0] : undefined;
    const alternativeMatches = candidates.slice(1);

    return {
      bestMatch,
      alternativeMatches,
      searchedReferences
    };
  }

  /**
   * Calculate confidence score for a PO match based on multiple factors
   */
  private calculatePoConfidence(
    po: Cin7PurchaseOrder,
    supplierName?: string,
    expectedLineItems?: Array<{ sku: string; qty: number }>
  ): number {
    let confidence = 0.6; // Base confidence

    // Factor 1: Supplier match
    if (supplierName) {
      const supplierSimilarity = calculateSimilarity(supplierName, po.Supplier || '');
      confidence += supplierSimilarity * 0.2;
    }

    // Factor 2: Line item SKU matches
    if (expectedLineItems && po.OrderLines) {
      const poSkus = new Set(po.OrderLines.map(line => line.ProductCode.toUpperCase()));
      const matchingSkus = expectedLineItems.filter(item =>
        poSkus.has(item.sku.toUpperCase())
      );
      const skuMatchRatio = matchingSkus.length / expectedLineItems.length;
      confidence += skuMatchRatio * 0.2;
    }

    return Math.min(confidence, 1.0);
  }

  /**
   * Match docket line items to PO line items
   */
  matchLineItems(
    docketLines: Array<{ sku?: string; description: string; qty: number }>,
    poLines: Cin7PurchaseOrder['OrderLines']
  ): Array<{
    docketLine: { sku?: string; description: string; qty: number };
    poLine?: Cin7PurchaseOrder['OrderLines'][0];
    matchType: 'exact' | 'fuzzy' | 'unmatched';
    confidence: number;
    issues: string[];
  }> {
    const results = [];
    const usedPoLines = new Set<string>();

    for (const docketLine of docketLines) {
      const issues: string[] = [];
      let matchedPoLine: Cin7PurchaseOrder['OrderLines'][0] | undefined;
      let matchType: 'exact' | 'fuzzy' | 'unmatched' = 'unmatched';
      let confidence = 0;

      // Try exact SKU match first
      if (docketLine.sku) {
        matchedPoLine = poLines.find(
          poLine =>
            !usedPoLines.has(poLine.Id) &&
            poLine.ProductCode.toUpperCase() === docketLine.sku!.toUpperCase()
        );

        if (matchedPoLine) {
          matchType = 'exact';
          confidence = 1.0;
          usedPoLines.add(matchedPoLine.Id);
        }
      }

      // Try fuzzy match by description if no exact match
      if (!matchedPoLine && docketLine.description) {
        const candidates = poLines
          .filter(poLine => !usedPoLines.has(poLine.Id))
          .map(poLine => ({
            poLine,
            score: calculateSimilarity(docketLine.description, poLine.ProductDescription)
          }))
          .filter(c => c.score >= 0.7)
          .sort((a, b) => b.score - a.score);

        if (candidates.length > 0) {
          matchedPoLine = candidates[0].poLine;
          matchType = 'fuzzy';
          confidence = candidates[0].score;
          usedPoLines.add(matchedPoLine.Id);
          issues.push(`Fuzzy matched by description (${(confidence * 100).toFixed(0)}% confidence)`);
        }
      }

      // Check for issues
      if (matchedPoLine) {
        const remaining = matchedPoLine.OrderedQty - matchedPoLine.ReceivedQty;

        if (docketLine.qty > remaining) {
          issues.push(
            `Over-delivery: received ${docketLine.qty}, remaining ${remaining}`
          );
        }

        if (docketLine.qty > matchedPoLine.OrderedQty) {
          issues.push(
            `Quantity exceeds order: received ${docketLine.qty}, ordered ${matchedPoLine.OrderedQty}`
          );
        }
      } else {
        issues.push('No matching line found in PO');
      }

      results.push({
        docketLine,
        poLine: matchedPoLine,
        matchType,
        confidence,
        issues
      });
    }

    return results;
  }
}
