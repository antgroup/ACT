export interface PaymentMethod {
  method_id: string;
  psps: {
    psp_id: string;
    endpoint: string;
    method_schema_url: string;
  }[];
}

export interface PaymentCapability {
  version: string;
  role: 'payee' | 'payer';
  agent_id: string;
  supported_methods: PaymentMethod[];
}

export interface NegotiationResult {
  matched: boolean;
  method_id?: string;
  psp_id?: string;
  endpoint?: string;
  method_schema_url?: string;
}

export class PaymentCapabilityNegotiation {
  negotiateOneWay(buyerMethods: string[], sellerCapability: PaymentCapability): NegotiationResult {
    for (const method of sellerCapability.supported_methods) {
      if (buyerMethods.includes(method.method_id)) {
        const psp = method.psps[0];
        return {
          matched: true,
          method_id: method.method_id,
          psp_id: psp.psp_id,
          endpoint: psp.endpoint,
          method_schema_url: psp.method_schema_url,
        };
      }
    }
    return { matched: false };
  }

  async negotiateTwoWay(
    endpoint: string,
    agentId: string,
    supportedMethods: string[],
    currency: string,
    estimatedAmount: number
  ): Promise<NegotiationResult> {
    const response = await fetch(endpoint, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        agent_id: agentId,
        supported_methods: supportedMethods,
        currency: currency,
        estimated_amount: estimatedAmount,
      }),
    });
    const data = await response.json() as { matched_methods: PaymentMethod[] };
    if (data.matched_methods && data.matched_methods.length > 0) {
      const method = data.matched_methods[0];
      return {
        matched: true,
        method_id: method.method_id,
        psp_id: method.psps[0].psp_id,
        endpoint: method.psps[0].endpoint,
        method_schema_url: method.psps[0].method_schema_url,
      };
    }
    return { matched: false };
  }
}