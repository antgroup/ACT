import type { ISR, ConversationHistory } from '../types/common';

export class IntentStructuredRule {
  constructISR(params: Partial<ISR> & Pick<ISR, 'conversation_history' | 'intent_id' | 'delegation_mode'>): ISR {
    return {
      ...params,
      validity_start_time: params.validity_start_time ?? new Date().toISOString(),
      validity_end_time: params.validity_end_time ?? '',
      max_total_amount: params.max_total_amount ?? 0,
      currency: params.currency ?? 'CNY',
      allowed_payment_methods: params.allowed_payment_methods ?? [],
      agent_id: params.agent_id ?? '',
    };
  }

  validateISR(isr: ISR): { valid: boolean; errors: string[] } {
    const errors: string[] = [];
    const ch = isr.conversation_history;
    if (!ch?.user_intent_raw && !ch?.user_intent_raw_digest) {
      errors.push('conversation_history must contain user_intent_raw or user_intent_raw_digest');
    }
    if (ch?.user_intent_raw_digest && !ch.context_ref) {
      errors.push('context_ref is required when user_intent_raw_digest is present');
    }
    if (!isr.intent_id) errors.push('intent_id is required');
    if (!isr.delegation_mode) errors.push('delegation_mode is required');
    if (isr.max_total_amount < 0) errors.push('max_total_amount must be >= 0');
    if (new Date(isr.validity_end_time) <= new Date(isr.validity_start_time)) {
      errors.push('validity_end_time must be after validity_start_time');
    }
    if (isr.user_confirmation_method && !isr.user_confirmation_timestamp) {
      errors.push('user_confirmation_timestamp is required when user_confirmation_method is present');
    }
    if (isr.ext?.commerce?.max_single_amount && isr.ext.commerce.max_single_amount > isr.max_total_amount) {
      errors.push('max_single_amount must not exceed max_total_amount');
    }
    if (isr.ext?.commerce?.min_single_amount && isr.ext.commerce.max_single_amount &&
        isr.ext.commerce.min_single_amount > isr.ext.commerce.max_single_amount) {
      errors.push('min_single_amount must not exceed max_single_amount');
    }
    return { valid: errors.length === 0, errors };
  }
}

export function constructConversationHistory(params: {
  user_intent_raw?: string;
  user_intent_raw_digest?: string;
  input_mode?: ConversationHistory['input_mode'];
  context_ref?: string;
}): ConversationHistory {
  if (!params.user_intent_raw && !params.user_intent_raw_digest) {
    throw new Error('At least one of user_intent_raw or user_intent_raw_digest must be provided');
  }
  if (params.user_intent_raw_digest && !params.context_ref) {
    throw new Error('context_ref is required when user_intent_raw_digest is provided');
  }
  return {
    user_intent_raw: params.user_intent_raw,
    user_intent_raw_digest: params.user_intent_raw_digest,
    input_mode: params.input_mode,
    context_ref: params.context_ref,
  };
}
