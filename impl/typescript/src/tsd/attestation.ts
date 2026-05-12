import type { AttestationEvent } from '../types/common';

export interface AttestationRecord {
  record_id: string;
  event_id: string;
  event_digest: string;
  attestation_time: string;
  attestation_provider_id: string;
  anchor_id?: string;
  merkle_proof?: { position: 'left' | 'right'; hash: string }[];
  provider_signature: string;
}

export class AttestationService {
  async submitEvent(endpoint: string, event: AttestationEvent): Promise<AttestationRecord> {
    const response = await fetch(endpoint, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(event),
    });
    return response.json() as Promise<AttestationRecord>;
  }

  async verifyRecord(endpoint: string, recordId: string): Promise<boolean> {
    // TODO: 实现存证记录验证（含 Merkle 证明与链上锚验证）
    return false;
  }
}