/**
 * SecurityProvider — 外部安全服务接口声明
 *
 * ACT 协议规范中涉及的安全操作（签名、核身、哈希等）均通过本接口抽象。
 * 实现方可依据自身安全架构选择适配的安全组件。
 */

export interface SignatureResult {
  signature: string;
  algorithm: string;
  authenticatedAt?: string;
}

export interface KeyPairResult {
  keyId: string;
  publicKey: string;
}

export interface AuthenticationResult {
  success: boolean;
  method: 'FACE_RECOGNITION' | 'FINGERPRINT' | 'PASSWORD' | 'OTP';
  authenticatedAt: string;
}

export interface SecurityProvider {
  /** 生成密钥对，私钥不可导出 */
  generateKeyPair(algorithm: string, purpose: string): Promise<KeyPairResult>;

  /** 使用指定密钥对已规范化的载荷进行签名 */
  sign(keyId: string, payload: Buffer, payloadType: string): Promise<SignatureResult>;

  /** 验证签名有效性 */
  verify(publicKey: string, payload: Buffer, signature: string): Promise<boolean>;

  /** 获取指定密钥的公钥 */
  getPublicKey(keyId: string): Promise<string>;

  /** 唤起用户核身流程 */
  authenticateUser(userId: string, preferredMethods?: string[]): Promise<AuthenticationResult>;

  /** 计算密码学安全摘要 */
  hash(algorithm: string, data: Buffer): Promise<string>;

  /** 按 RFC 8785 JCS 规范执行 JSON 规范化 */
  canonicalizeJson(data: unknown): Buffer;

  /** 获取受保护时间戳 */
  getSecureTime(): Promise<string>;
}