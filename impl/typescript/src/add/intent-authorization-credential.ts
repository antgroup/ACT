import type { IAC, ISR } from '../types/common';
import type { SecurityProvider } from '../crypto/security-provider';

export class IntentAuthorizationCredential {
  constructor(private securityProvider: SecurityProvider) {}

  async issueISR(isr: ISR, signerIdentity: string): Promise<IAC> {
    const canonicalPayload = this.securityProvider.canonicalizeJson(isr);
    const signResult = await this.securityProvider.sign(
      signerIdentity,
      canonicalPayload,
      'IAC'
    );

    return {
      iss: signerIdentity,
      sub: isr.agent_id,
      jti: isr.delegation_id ?? isr.intent_id,
      iat: Math.floor(Date.now() / 1000),
      exp: Math.floor(new Date(isr.validity_end_time).getTime() / 1000),
      vc: {
        type: ['VerifiableCredential', 'ACTIntentAuthorization'],
        credentialSubject: isr,
      },
    };
  }

  async verifyIAC(iac: IAC): Promise<boolean> {
    const canonicalPayload = this.securityProvider.canonicalizeJson(iac.vc.credentialSubject);
    // Extract signature from the IAC (in a real implementation, this would be the JWS signature)
    return this.securityProvider.verify(iac.iss, canonicalPayload, '');
  }
}