import type { SecurityProvider } from '../crypto/security-provider';

/**
 * PSD-PMT-BND：支付方式绑定
 *
 * 规范委托人向 PSP 完成智能体支付能力开通、并为智能体建立支付标记关联的操作流程。
 */

export interface TokenConstraints {
  /** 单笔金额上限 */
  max_amount_per_transaction?: number;
  /** 标记有效期 */
  validity_period?: {
    start_time: string;
    end_time: string;
  };
  /** 允许使用的商户范围 */
  allowed_merchants?: string[];
}

export interface BindingRequest {
  /** 本次请求的全局唯一标识 */
  request_id: string;
  /** 委托人身份标识 */
  principal_id: string;
  /** 受托智能体身份标识 */
  agent_id: string;
  /** 委托人支付账户引用 */
  payment_account_ref: string;
  /** 支付标记约束参数 */
  token_constraints?: TokenConstraints;
  /** 委托人核身方式 */
  authentication_method?: 'FACE_RECOGNITION' | 'FINGERPRINT' | 'PASSWORD' | 'OTP';
  /** 请求时间戳 */
  timestamp: string;
}

export type BindingStatus = 'SUCCESS' | 'FAILED';

export type BindingErrorCode =
  | 'AUTH_FAILED'
  | 'AGENT_NOT_REGISTERED'
  | 'ACCOUNT_LIMIT_EXCEEDED'
  | 'ACCOUNT_INVALID'
  | 'SYSTEM_ERROR';

export interface BindingResponse {
  /** 回传本次请求的全局唯一标识 */
  request_id: string;
  /** 绑定结果状态 */
  status: BindingStatus;
  /** PSP 生成的支付标记（绑定成功时返回） */
  payment_token?: string;
  /** 支付标记过期时间（绑定成功时返回） */
  token_expiry?: string;
  /** 支付标记绑定的智能体身份标识（绑定成功时返回） */
  bound_agent_id?: string;
  /** 响应时间戳 */
  timestamp: string;
  /** 错误详情，仅在绑定失败时返回 */
  error?: {
    error_code: BindingErrorCode;
    error_message: string;
  };
}

export class PaymentMethodBinding {
  constructor(private securityProvider: SecurityProvider) {}

  /**
   * 构造支付方式绑定请求
   *
   * @param params - 绑定请求参数
   * @returns 完整的绑定请求对象
   */
  async constructRequest(params: {
    principalId: string;
    agentId: string;
    paymentAccountRef: string;
    tokenConstraints?: TokenConstraints;
  }): Promise<BindingRequest> {
    const timestamp = await this.securityProvider.getSecureTime();

    const authResult = await this.securityProvider.authenticateUser(params.principalId);
    if (!authResult.success) {
      throw new Error(`用户核身失败: ${params.principalId}`);
    }

    return {
      request_id: `urn:uuid:${crypto.randomUUID()}`,
      principal_id: params.principalId,
      agent_id: params.agentId,
      payment_account_ref: params.paymentAccountRef,
      token_constraints: params.tokenConstraints,
      authentication_method: authResult.method,
      timestamp,
    };
  }

  /**
   * 向 PSP 发送支付方式绑定请求
   */
  async sendBindingRequest(endpoint: string, request: BindingRequest): Promise<BindingResponse> {
    const response = await fetch(endpoint, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(request),
    });
    return response.json() as Promise<BindingResponse>;
  }
}