export interface ISR {
  user_intent_raw: string;
  intent_id: string;
  delegation_id?: string;
  delegation_mode: 'SPECIFIED' | 'BOUNDED';
  validity_start_time: string;
  validity_end_time: string;
  max_total_amount: number;
  amount_currency: string;
  allowed_payment_methods: string[];
  signer_identity: string;
  agent_id: string;
  user_confirmation_method?: 'FACE_RECOGNITION' | 'FINGERPRINT' | 'PASSWORD' | 'OTP';
  user_confirmation_timestamp?: string;
  ext?: {
    commerce?: {
      max_single_amount?: number;
      min_single_amount?: number;
      allowed_categories?: string[];
      forbidden_categories?: string[];
      allowed_merchants?: string[];
      forbidden_merchants?: string[];
    };
    agent_behavior?: {
      price_change_tolerance?: number;
      price_change_action?: 'PAUSE_AND_NOTIFY' | 'AUTO_CANCEL';
      on_payment_failure?: 'AUTO_RETRY' | 'CANCEL';
      max_retry_count?: number;
    };
    fulfillment?: {
      delivery_time_requirement?: string;
      delivery_address?: string;
    };
  };
}

export interface IAC {
  iss: string;
  sub: string;
  jti: string;
  iat: number;
  exp: number;
  vc: {
    type: string[];
    credentialSubject: ISR;
  };
}

export type IACStatus = 'Active' | 'Suspended' | 'Expired' | 'Revoked';

export interface AttestationEvent {
  event_id: string;
  event_type: string;
  event_time: string;
  event_source: string;
  domain: 'ADD' | 'CID' | 'PSD' | 'TSD';
  payload: Record<string, unknown>;
  payload_digest: string;
  related_ids?: string[];
  signature: string;
}