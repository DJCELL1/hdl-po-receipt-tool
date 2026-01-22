import axios, { AxiosInstance, AxiosError } from 'axios';
import { Cin7Config, Cin7PurchaseOrder, Cin7Product, Cin7ProductOption, Cin7ReceiptPayload } from './types';
import { RateLimiter } from './rateLimiter';

export class Cin7Client {
  private axiosInstance: AxiosInstance;
  private rateLimiter: RateLimiter;
  private config: Cin7Config;

  constructor(config: Cin7Config) {
    this.config = config;
    this.rateLimiter = new RateLimiter(config);

    this.axiosInstance = axios.create({
      baseURL: config.baseUrl,
      auth: {
        username: config.apiKey,
        password: config.apiSecret
      },
      headers: {
        'Content-Type': 'application/json'
      },
      timeout: 30000
    });
  }

  private async retryWithBackoff<T>(
    operation: () => Promise<T>,
    attempt = 0
  ): Promise<T> {
    try {
      await this.rateLimiter.waitForAvailability();
      return await operation();
    } catch (error) {
      const axiosError = error as AxiosError;
      const status = axiosError.response?.status;

      // Retry on 429 (Too Many Requests) or 503 (Service Unavailable)
      if ((status === 429 || status === 503) && attempt < this.config.maxRetries) {
        const backoffMs = Math.min(1000 * Math.pow(2, attempt), 30000);
        console.log(`Retry attempt ${attempt + 1} after ${backoffMs}ms for status ${status}`);
        await this.sleep(backoffMs);
        return this.retryWithBackoff(operation, attempt + 1);
      }

      throw error;
    }
  }

  private sleep(ms: number): Promise<void> {
    return new Promise(resolve => setTimeout(resolve, ms));
  }

  /**
   * Find Purchase Orders by reference
   * Handles exact match and wildcard search
   */
  async findPurchaseOrders(reference: string, useWildcard = false): Promise<Cin7PurchaseOrder[]> {
    const whereClause = useWildcard
      ? `Reference LIKE '${this.escapeString(reference)}%'`
      : `Reference='${this.escapeString(reference)}'`;

    return this.retryWithBackoff(async () => {
      const response = await this.axiosInstance.get('/v1/PurchaseOrders', {
        params: {
          where: whereClause
        }
      });
      return response.data;
    });
  }

  /**
   * Get Purchase Order by ID
   */
  async getPurchaseOrderById(id: string): Promise<Cin7PurchaseOrder> {
    return this.retryWithBackoff(async () => {
      const response = await this.axiosInstance.get(`/v1/PurchaseOrders/${id}`);
      return response.data;
    });
  }

  /**
   * Find products by code or description
   */
  async findProducts(searchTerm: string, searchBy: 'code' | 'description' = 'code'): Promise<Cin7Product[]> {
    const whereClause = searchBy === 'code'
      ? `Code='${this.escapeString(searchTerm)}'`
      : `Name LIKE '%${this.escapeString(searchTerm)}%'`;

    return this.retryWithBackoff(async () => {
      const response = await this.axiosInstance.get('/v1/Products', {
        params: {
          where: whereClause,
          rows: 50
        }
      });
      return response.data;
    });
  }

  /**
   * Find product options (variants) by code
   */
  async findProductOptions(code: string): Promise<Cin7ProductOption[]> {
    return this.retryWithBackoff(async () => {
      const response = await this.axiosInstance.get('/v1/ProductOptions', {
        params: {
          where: `Code='${this.escapeString(code)}'`
        }
      });
      return response.data;
    });
  }

  /**
   * Update Purchase Order with received quantities
   * This is the primary method for receipting goods in Cin7
   */
  async receiptPurchaseOrder(poId: string, updates: Partial<Cin7PurchaseOrder>): Promise<Cin7PurchaseOrder> {
    return this.retryWithBackoff(async () => {
      const response = await this.axiosInstance.put(`/v1/PurchaseOrders/${poId}`, updates);
      return response.data;
    });
  }

  /**
   * Fetch all pages of results for a query
   */
  async fetchAllPages<T>(
    endpoint: string,
    whereClause?: string,
    pageSize = 250
  ): Promise<T[]> {
    const results: T[] = [];
    let page = 1;
    let hasMore = true;

    while (hasMore) {
      const items = await this.retryWithBackoff(async () => {
        const params: any = {
          page,
          rows: pageSize
        };
        if (whereClause) {
          params.where = whereClause;
        }

        const response = await this.axiosInstance.get(endpoint, { params });
        return response.data;
      });

      results.push(...items);

      // If we got fewer items than page size, we're done
      hasMore = items.length === pageSize;
      page++;
    }

    return results;
  }

  /**
   * Escape single quotes in strings for Cin7 where clauses
   */
  private escapeString(str: string): string {
    return str.replace(/'/g, "''");
  }

  /**
   * Health check
   */
  async healthCheck(): Promise<boolean> {
    try {
      await this.retryWithBackoff(async () => {
        const response = await this.axiosInstance.get('/v1/PurchaseOrders', {
          params: { rows: 1 }
        });
        return response.data;
      });
      return true;
    } catch (error) {
      console.error('Cin7 health check failed:', error);
      return false;
    }
  }
}

export function createCin7Client(): Cin7Client {
  const config: Cin7Config = {
    apiKey: process.env.CIN7_API_KEY || '',
    apiSecret: process.env.CIN7_API_SECRET || '',
    baseUrl: process.env.CIN7_BASE_URL || 'https://api.cin7.com/api',
    maxRetries: 3,
    rateLimits: {
      perSecond: 3,
      perMinute: 60,
      perDay: 5000
    }
  };

  if (!config.apiKey || !config.apiSecret) {
    throw new Error('CIN7_API_KEY and CIN7_API_SECRET must be set in environment variables');
  }

  return new Cin7Client(config);
}
