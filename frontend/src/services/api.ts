import axios, { AxiosInstance, AxiosError } from 'axios';

const API_BASE_URL = process.env.REACT_APP_API_URL || 'http://localhost:3001';

class ApiClient {
  private client: AxiosInstance;

  constructor() {
    this.client = axios.create({
      baseURL: `${API_BASE_URL}/api`,
      headers: {
        'Content-Type': 'application/json'
      }
    });
  }

  // Auth endpoints
  async register(email: string, password: string, name?: string) {
    const response = await this.client.post('/auth/register', { email, password, name });
    return response.data;
  }

  async login(email: string, password: string) {
    const response = await this.client.post('/auth/login', { email, password });
    return response.data;
  }

  // Docket endpoints
  async uploadDocket(file: File) {
    const formData = new FormData();
    formData.append('docket', file);

    const response = await this.client.post('/dockets/upload', formData, {
      headers: {
        'Content-Type': 'multipart/form-data'
      }
    });
    return response.data;
  }

  async matchPo(data: {
    poReference: string;
    supplierName?: string;
    lineItems?: Array<{ sku: string; qty: number }>;
  }) {
    const response = await this.client.post('/dockets/match-po', data);
    return response.data;
  }

  async matchLines(data: { poId: string; docketLines: any[] }) {
    const response = await this.client.post('/dockets/match-lines', data);
    return response.data;
  }

  async createReceipt(data: {
    poId: string;
    poReference: string;
    docketNumber?: string;
    supplierName?: string;
    deliveryDate?: string;
    lineItems: any[];
    allowOverride?: boolean;
  }) {
    const response = await this.client.post('/dockets/receipt', data);
    return response.data;
  }

  async getReceipts(limit = 50, offset = 0) {
    const response = await this.client.get('/dockets/receipts', {
      params: { limit, offset }
    });
    return response.data;
  }

  async getReceiptById(id: number) {
    const response = await this.client.get(`/dockets/receipts/${id}`);
    return response.data;
  }
}

export const api = new ApiClient();
