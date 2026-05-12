export interface IntentRequest {
  request_id: string;
  intent_id: string;
  delegation_id?: string;
  buyer_agent_id: string;
  intent_context: {
    explicit_intent: string;
    implicit_intent?: string[];
    preferences?: string[];
  };
  constraints: {
    max_amount?: number;
    currency?: string;
    allowed_categories?: string[];
    allowed_merchants?: string[];
  };
  timestamp?: string;
}

export interface CandidateItem {
  product_id: string;
  product_name: string;
  category?: string;
  price: number;
  currency: string;
  availability: 'in_stock' | 'out_of_stock' | 'limited';
}

export interface IntentResponse {
  request_id: string;
  merchant_id: string;
  candidates: CandidateItem[];
  error?: {
    error_type: string;
    error_message: string;
  };
}

export class IntentRouting {
  async sendRequest(endpoint: string, request: IntentRequest): Promise<IntentResponse> {
    const response = await fetch(endpoint, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(request),
    });
    return response.json() as Promise<IntentResponse>;
  }
}