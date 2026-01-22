export interface Cin7Config {
  apiKey: string;
  apiSecret: string;
  baseUrl: string;
  maxRetries: number;
  rateLimits: {
    perSecond: number;
    perMinute: number;
    perDay: number;
  };
}

export interface Cin7PurchaseOrder {
  Id: string;
  Reference: string;
  Supplier: string;
  OrderDate: string;
  OrderStatus: string;
  OrderLines: Cin7OrderLine[];
  Total: number;
  Currency: string;
  Notes?: string;
}

export interface Cin7OrderLine {
  Id: string;
  ProductId: string;
  ProductCode: string;
  ProductDescription: string;
  OrderedQty: number;
  ReceivedQty: number;
  UnitPrice: number;
  Total: number;
  Unit?: string;
}

export interface Cin7Product {
  Id: string;
  Code: string;
  Name: string;
  Description?: string;
  Options?: Cin7ProductOption[];
}

export interface Cin7ProductOption {
  Id: string;
  Code: string;
  Name: string;
  ProductId: string;
}

export interface Cin7ApiResponse<T> {
  data: T;
  total?: number;
  page?: number;
  pageSize?: number;
}

export interface Cin7ReceiptPayload {
  PurchaseOrderId: string;
  ReceivedDate: string;
  Lines: Cin7ReceiptLine[];
  Notes?: string;
}

export interface Cin7ReceiptLine {
  OrderLineId: string;
  ReceivedQty: number;
}

export interface RateLimitState {
  secondRequests: number[];
  minuteRequests: number[];
  dayRequests: number[];
}
