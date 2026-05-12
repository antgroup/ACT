import type { ISR } from '../types/common';

export class IntentStructuredRule {
  constructISR(params: Partial<ISR> & Pick<ISR, 'user_intent_raw' | 'intent_id' | 'delegation_mode'>): ISR {
    return {
      ...params,
      validity_start_time: params.validity_start_time ?? new Date().toISOString(),
      validity_end_time: params.validity_end_time ?? '',
      max_total_amount: params.max_total_amount ?? 0,
      amount_currency: params.amount_currency ?? 'CNY',
      allowed_payment_methods: params.allowed_payment_methods ?? [],
      signer_identity: params.signer_identity ?? '',
      agent_id: params.agent_id ?? '',
    };
  }

  validateISR(isr: ISR): { valid: boolean; errors: string[] } {
    const errors: string[] = [];
    if (!isr.user_intent_raw) errors.push('user_intent_raw is required');
    if (!isr.intent_id) errors.push('intent_id is required');
    if (!isr.delegation_mode) errors.push('delegation_mode is required');
    if (isr.max_total_amount < 0) errors.push('max_total_amount must be >= 0');
    if (new Date(isr.validity_end_time) <= new Date(isr.validity_start_time)) {
      errors.push('validity_end_time must be after validity_start_time');
    }
    if (isr.ext?.commerce?.max_single_amount && isr.ext.commerce.max_single_amount > isr.max_total_amount) {
      errors.push('max_single_amount must not exceed max_total_amount');
    }
    return { valid: errors.length === 0, errors };
  }
}