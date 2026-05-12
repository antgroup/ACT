import type { SecurityProvider } from '../crypto/security-provider';

export class IntentExpression {
  constructor(private securityProvider: SecurityProvider) {}

  async expressAndConfirm(
    userId: string,
    rawIntent: string
  ): Promise<{ confirmed: boolean; confirmationMethod?: string; confirmedAt?: string }> {
    const authResult = await this.securityProvider.authenticateUser(userId);
    if (!authResult.success) {
      return { confirmed: false };
    }
    return {
      confirmed: true,
      confirmationMethod: authResult.method,
      confirmedAt: authResult.authenticatedAt,
    };
  }
}