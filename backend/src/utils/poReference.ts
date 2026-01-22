export interface ParsedPoReference {
  base: string;
  suffix?: 'A' | 'B' | 'C';
  normalized: string;
  original: string;
}

/**
 * Normalize and parse PO reference with backorder suffix detection
 *
 * Rules:
 * - Trim spaces
 * - Uppercase
 * - If ends with A/B/C immediately preceded by alphanumeric, treat as suffix
 *
 * Examples:
 * - "PO-12345A" -> { base: "PO-12345", suffix: "A", normalized: "PO-12345A" }
 * - "PO-12345" -> { base: "PO-12345", suffix: undefined, normalized: "PO-12345" }
 * - "ABC123B" -> { base: "ABC123", suffix: "B", normalized: "ABC123B" }
 * - "TESTA" -> { base: "TESTA", suffix: undefined, normalized: "TESTA" } (no preceding char)
 */
export function normalizePoRef(input: string): ParsedPoReference {
  if (!input) {
    throw new Error('PO reference cannot be empty');
  }

  // Trim and uppercase
  const trimmed = input.trim().toUpperCase();

  // Check if ends with A, B, or C
  const lastChar = trimmed.slice(-1);
  const isValidSuffix = ['A', 'B', 'C'].includes(lastChar);

  if (!isValidSuffix || trimmed.length < 2) {
    // No suffix
    return {
      base: trimmed,
      suffix: undefined,
      normalized: trimmed,
      original: input
    };
  }

  // Check if character before suffix is alphanumeric
  const beforeSuffix = trimmed.slice(-2, -1);
  const isAlphanumeric = /[A-Z0-9]/.test(beforeSuffix);

  if (!isAlphanumeric) {
    // Suffix not preceded by alphanumeric, treat whole string as base
    return {
      base: trimmed,
      suffix: undefined,
      normalized: trimmed,
      original: input
    };
  }

  // Valid suffix detected
  const base = trimmed.slice(0, -1);
  const suffix = lastChar as 'A' | 'B' | 'C';

  return {
    base,
    suffix,
    normalized: trimmed,
    original: input
  };
}

/**
 * Generate search variants for PO reference matching
 * Returns array of references to try in order of preference
 */
export function generateSearchVariants(parsed: ParsedPoReference): string[] {
  const variants: string[] = [parsed.normalized];

  // If has suffix, also try base reference
  if (parsed.suffix) {
    variants.push(parsed.base);
  }

  return variants;
}

/**
 * Calculate similarity score between two strings (0-1)
 * Uses Levenshtein distance normalized by max length
 */
export function calculateSimilarity(str1: string, str2: string): number {
  if (!str1 || !str2) return 0;
  if (str1 === str2) return 1;

  const s1 = str1.toLowerCase();
  const s2 = str2.toLowerCase();

  const distance = levenshteinDistance(s1, s2);
  const maxLen = Math.max(s1.length, s2.length);

  return 1 - (distance / maxLen);
}

/**
 * Levenshtein distance algorithm
 */
function levenshteinDistance(str1: string, str2: string): number {
  const m = str1.length;
  const n = str2.length;
  const dp: number[][] = Array(m + 1).fill(null).map(() => Array(n + 1).fill(0));

  for (let i = 0; i <= m; i++) dp[i][0] = i;
  for (let j = 0; j <= n; j++) dp[0][j] = j;

  for (let i = 1; i <= m; i++) {
    for (let j = 1; j <= n; j++) {
      if (str1[i - 1] === str2[j - 1]) {
        dp[i][j] = dp[i - 1][j - 1];
      } else {
        dp[i][j] = Math.min(
          dp[i - 1][j] + 1,    // deletion
          dp[i][j - 1] + 1,    // insertion
          dp[i - 1][j - 1] + 1 // substitution
        );
      }
    }
  }

  return dp[m][n];
}

/**
 * Fuzzy match string against array of candidates
 * Returns matches with similarity score >= threshold, sorted by score
 */
export function fuzzyMatch(
  query: string,
  candidates: string[],
  threshold = 0.6
): Array<{ value: string; score: number }> {
  return candidates
    .map(candidate => ({
      value: candidate,
      score: calculateSimilarity(query, candidate)
    }))
    .filter(result => result.score >= threshold)
    .sort((a, b) => b.score - a.score);
}
