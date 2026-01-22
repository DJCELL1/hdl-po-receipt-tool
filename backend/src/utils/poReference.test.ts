import {
  normalizePoRef,
  generateSearchVariants,
  calculateSimilarity,
  fuzzyMatch
} from './poReference';

describe('PO Reference Parsing', () => {
  describe('normalizePoRef', () => {
    it('should parse PO reference with suffix A', () => {
      const result = normalizePoRef('PO-12345A');
      expect(result.base).toBe('PO-12345');
      expect(result.suffix).toBe('A');
      expect(result.normalized).toBe('PO-12345A');
    });

    it('should parse PO reference with suffix B', () => {
      const result = normalizePoRef('ABC123B');
      expect(result.base).toBe('ABC123');
      expect(result.suffix).toBe('B');
      expect(result.normalized).toBe('ABC123B');
    });

    it('should parse PO reference with suffix C', () => {
      const result = normalizePoRef('ORDER-999C');
      expect(result.base).toBe('ORDER-999');
      expect(result.suffix).toBe('C');
      expect(result.normalized).toBe('ORDER-999C');
    });

    it('should handle PO reference without suffix', () => {
      const result = normalizePoRef('PO-12345');
      expect(result.base).toBe('PO-12345');
      expect(result.suffix).toBeUndefined();
      expect(result.normalized).toBe('PO-12345');
    });

    it('should uppercase and trim input', () => {
      const result = normalizePoRef('  po-12345a  ');
      expect(result.base).toBe('PO-12345');
      expect(result.suffix).toBe('A');
      expect(result.normalized).toBe('PO-12345A');
    });

    it('should not treat standalone A as suffix', () => {
      const result = normalizePoRef('A');
      expect(result.base).toBe('A');
      expect(result.suffix).toBeUndefined();
    });

    it('should not treat A after non-alphanumeric as suffix', () => {
      const result = normalizePoRef('PO-A');
      expect(result.base).toBe('PO-A');
      expect(result.suffix).toBeUndefined();
    });

    it('should handle complex reference with suffix', () => {
      const result = normalizePoRef('PO-2024-001-A');
      expect(result.base).toBe('PO-2024-001-');
      expect(result.suffix).toBe('A');
    });
  });

  describe('generateSearchVariants', () => {
    it('should generate variants for reference with suffix', () => {
      const parsed = normalizePoRef('PO-12345A');
      const variants = generateSearchVariants(parsed);
      expect(variants).toEqual(['PO-12345A', 'PO-12345']);
    });

    it('should generate single variant for reference without suffix', () => {
      const parsed = normalizePoRef('PO-12345');
      const variants = generateSearchVariants(parsed);
      expect(variants).toEqual(['PO-12345']);
    });
  });

  describe('calculateSimilarity', () => {
    it('should return 1 for identical strings', () => {
      expect(calculateSimilarity('hello', 'hello')).toBe(1);
    });

    it('should return 0 for completely different strings', () => {
      const similarity = calculateSimilarity('abc', 'xyz');
      expect(similarity).toBeLessThan(0.5);
    });

    it('should return high similarity for similar strings', () => {
      const similarity = calculateSimilarity('Acme Corp', 'Acme Corporation');
      expect(similarity).toBeGreaterThan(0.5);
    });

    it('should be case insensitive', () => {
      expect(calculateSimilarity('HELLO', 'hello')).toBe(1);
    });

    it('should handle empty strings', () => {
      expect(calculateSimilarity('', '')).toBe(0);
      expect(calculateSimilarity('hello', '')).toBe(0);
    });
  });

  describe('fuzzyMatch', () => {
    it('should find exact matches', () => {
      const candidates = ['Apple Inc', 'Microsoft Corp', 'Google LLC'];
      const results = fuzzyMatch('Apple Inc', candidates);
      expect(results[0].value).toBe('Apple Inc');
      expect(results[0].score).toBe(1);
    });

    it('should find close matches above threshold', () => {
      const candidates = ['Acme Corporation', 'Acme Corp', 'Smith & Co'];
      const results = fuzzyMatch('Acme Corp', candidates, 0.7);
      expect(results.length).toBeGreaterThanOrEqual(2);
      expect(results[0].score).toBeGreaterThanOrEqual(0.7);
    });

    it('should filter out matches below threshold', () => {
      const candidates = ['Apple Inc', 'Microsoft Corp', 'Google LLC'];
      const results = fuzzyMatch('Zebra Company', candidates, 0.7);
      expect(results.length).toBe(0);
    });

    it('should sort results by score descending', () => {
      const candidates = ['Acme', 'Acme Corp', 'Acme Corporation'];
      const results = fuzzyMatch('Acme Corp', candidates, 0.5);
      for (let i = 0; i < results.length - 1; i++) {
        expect(results[i].score).toBeGreaterThanOrEqual(results[i + 1].score);
      }
    });
  });
});
