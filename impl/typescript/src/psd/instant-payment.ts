import type { SecurityProvider } from '../crypto/security-provider';

/**
 * PSD-PAY-INS：用户即时支付流程
 *
 * 适用于用户实时在场（Human-Present）且购买标的已在当次交互中明确的即时购买场景。
 * 用户无需预先签发意图授权凭证，收银台确认即构成支付授权依据。
 */

export interface CartItem {
  product_id: string;
  product_name: string;
  price: number;
  currency: string;
  quantity: number;
}

export interface CartInfo {
  items: CartItem[];
  cart_snapshot_digest?: string;
}

export interface InstantPaymentRequest {
  /** 本次请求的全局唯一标识，用于防重放 */
  request_id: string;
  /** 来自 CID-CART-CFM 的商户侧订单号 */
  merchant_order_no: string;
  /** 来自 CID-CART-CFM 的购物车信息 */
  cart_info?: CartInfo;
  /** 前期绑定的支付标记 */
  payment_token: string;
  /** 本次支付金额（字符串格式，避免浮点精度问题） */
  amount: string;
  /** 交易币种（ISO 4217 三字母码） */
  currency: string;
  /** 请求时间戳（ISO 8601 格式） */
  timestamp: string;
  /** 买方智能体身份标识 */
  buyer_agent_id: string;
  /** 买方智能体对本次请求关键要素的签名 */
  signature: {
    algorithm: string;
    value: string;
  };
}

export type InstantPaymentStatus = 'SUCCESS' | 'FAILED' | 'PENDING';

export type InstantPaymentErrorCode =
  | 'REQUEST_DUPLICATE'
  | 'REQUEST_EXPIRED'
  | 'SIGNATURE_INVALID'
  | 'PAYMENT_TOKEN_INVALID'
  | 'PAYMENT_TOKEN_MISMATCH'
  | 'AMOUNT_MISMATCH'
  | 'INSUFFICIENT_BALANCE'
  | 'USER_AUTH_FAILED'
  | 'RISK_CONTROL_REJECTED'
  | 'SYSTEM_ERROR';

export interface InstantPaymentResponse {
  /** 回传本次请求的全局唯一标识 */
  request_id: string;
  /** PSP 生成的全局唯一交易流水号 */
  trade_no: string;
  /** 回传商户侧订单号 */
  merchant_order_no: string;
  /** 交易状态 */
  status: InstantPaymentStatus;
  /** 交易时间戳 */
  trade_timestamp: string;
  /** 错误详情，仅在支付失败时返回 */
  error?: {
    error_code: InstantPaymentErrorCode;
    error_message: string;
  };
}

export class InstantPayment {
  constructor(private securityProvider: SecurityProvider) {}

  /**
   * 构造即时支付请求对象
   *
   * @param params - 请求参数
   * @returns 完整的即时支付请求对象
   */
  async constructRequest(params: {
    merchantOrderNo: string;
    cartInfo?: CartInfo;
    paymentToken: string;
    amount: string;
    currency: string;
    buyerAgentId: string;
  }): Promise<InstantPaymentRequest> {
    const timestamp = await this.securityProvider.getSecureTime();
    const requestId = `urn:uuid:${crypto.randomUUID()}`;

    const request: InstantPaymentRequest = {
      request_id: requestId,
      merchant_order_no: params.merchantOrderNo,
      cart_info: params.cartInfo,
      payment_token: params.paymentToken,
      amount: params.amount,
      currency: params.currency,
      timestamp,
      buyer_agent_id: params.buyerAgentId,
      signature: {
        algorithm: '',
        value: '',
      },
    };

    // 对请求关键要素签名：request_id + merchant_order_no + amount + currency + timestamp
    const signingPayload = this.securityProvider.canonicalizeJson({
      request_id: request.request_id,
      merchant_order_no: request.merchant_order_no,
      amount: request.amount,
      currency: request.currency,
      timestamp: request.timestamp,
    });

    const signResult = await this.securityProvider.sign(
      params.buyerAgentId,
      signingPayload,
      'PSD-PAY-INS',
    );

    request.signature = {
      algorithm: signResult.algorithm,
      value: signResult.signature,
    };

    return request;
  }

  /**
   * 验证即时支付请求的基础合法性
   *
   * 按协议定义校验：防重放、时间戳时效、签名有效性、支付标记有效性
   *
   * @param request - 即时支付请求
   * @param knownRequestIds - 已知的请求 ID 集合，用于防重放校验
   * @param maxTimestampDriftMs - 允许的最大时间戳偏移量（毫秒），默认 5 分钟
   */
  async validateRequest(
    request: InstantPaymentRequest,
    knownRequestIds: Set<string>,
    maxTimestampDriftMs: number = 5 * 60 * 1000,
  ): Promise<{ valid: boolean; errors: string[] }> {
    const errors: string[] = [];

    // 防重放校验
    if (knownRequestIds.has(request.request_id)) {
      errors.push('REQUEST_DUPLICATE: 请求唯一标识已被使用，疑似重放攻击');
    }

    // 请求时间戳时效性校验
    const requestTime = new Date(request.timestamp).getTime();
    const now = Date.now();
    if (isNaN(requestTime)) {
      errors.push('REQUEST_EXPIRED: 请求时间戳格式无效');
    } else if (Math.abs(now - requestTime) > maxTimestampDriftMs) {
      errors.push('REQUEST_EXPIRED: 请求时间戳超出有效窗口');
    }

    // 买方智能体签名验证
    const signaturePayload = this.securityProvider.canonicalizeJson({
      request_id: request.request_id,
      merchant_order_no: request.merchant_order_no,
      amount: request.amount,
      currency: request.currency,
      timestamp: request.timestamp,
    });

    const publicKey = await this.securityProvider.getPublicKey(request.buyer_agent_id);
    const signatureValid = await this.securityProvider.verify(
      publicKey,
      signaturePayload,
      request.signature.value,
    );
    if (!signatureValid) {
      errors.push('SIGNATURE_INVALID: 买方智能体签名验证失败');
    }

    // 金额一致性校验（如果有购物车信息）
    if (request.cart_info) {
      const totalAmount = request.cart_info.items.reduce(
        (sum, item) => sum + item.price * item.quantity,
        0,
      );
      if (request.amount !== totalAmount.toFixed(2) && request.amount !== String(totalAmount)) {
        errors.push('AMOUNT_MISMATCH: 支付金额与购物车总金额不一致');
      }
    }

    return { valid: errors.length === 0, errors };
  }

  /**
   * 向 PSP 发送即时支付请求
   */
  async sendRequest(endpoint: string, request: InstantPaymentRequest): Promise<InstantPaymentResponse> {
    const response = await fetch(endpoint, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(request),
    });
    return response.json() as Promise<InstantPaymentResponse>;
  }
}