"""
Mock JWT 工具库
用于模拟 JWT 的编码和解码，便于在测试环境中使用
"""

import base64
import json
import hmac
import hashlib
import time
import uuid
from typing import Dict, Any, Optional, Tuple
from datetime import datetime, timezone


class MockJWT:
    """
    模拟 JWT 操作
    在真实环境中，应使用 PyJWT 库: pip install PyJWT
    """

    # 模拟密钥（真实环境应使用安全的密钥管理）
    _SECRET_KEY = "act-protocol-mock-secret-key-2024"
    _ALGORITHM = "HS256"

    @classmethod
    def encode(cls, payload: Dict[str, Any], headers: Optional[Dict[str, str]] = None) -> str:
        """
        编码 JWT

        Args:
            payload: JWT 载荷
            headers: JWT 头部

        Returns:
            编码后的 JWT 字符串
        """
        if headers is None:
            headers = {
                "typ": "JWT",
                "alg": cls._ALGORITHM
            }

        # 编码头部和载荷
        header_encoded = cls._base64url_encode(json.dumps(headers).encode())
        payload_encoded = cls._base64url_encode(json.dumps(payload).encode())

        # 创建签名
        message = f"{header_encoded}.{payload_encoded}"
        signature = cls._sign(message)
        signature_encoded = cls._base64url_encode(signature)

        return f"{message}.{signature_encoded}"

    @classmethod
    def decode(cls, token: str, verify: bool = True) -> Dict[str, Any]:
        """
        解码 JWT

        Args:
            token: JWT 字符串
            verify: 是否验证签名（mock 模式下总是验证通过）

        Returns:
            解码后的载荷

        Raises:
            ValueError: 当 token 格式无效或签名验证失败时
        """
        try:
            parts = token.split(".")
            if len(parts) != 3:
                raise ValueError("Invalid JWT format")

            header_encoded, payload_encoded, signature_encoded = parts

            # 解码头部
            try:
                header = json.loads(cls._base64url_decode(header_encoded))
            except Exception as e:
                raise ValueError(f"Invalid JWT header: {e}")

            # 解码载荷
            try:
                payload = json.loads(cls._base64url_decode(payload_encoded))
            except Exception as e:
                raise ValueError(f"Invalid JWT payload: {e}")

            # 验证签名
            if verify:
                message = f"{header_encoded}.{payload_encoded}"
                expected_signature = cls._sign(message)
                actual_signature = cls._base64url_decode(signature_encoded)

                if not hmac.compare_digest(expected_signature, actual_signature):
                    raise ValueError("Invalid JWT signature")

            return payload

        except ValueError:
            raise
        except Exception as e:
            raise ValueError(f"JWT decode error: {e}")

    @classmethod
    def decode_unsafe(cls, token: str) -> Tuple[Dict[str, Any], Dict[str, Any]]:
        """
        不安全地解码 JWT（不验证签名，用于调试）

        Args:
            token: JWT 字符串

        Returns:
            (header, payload)
        """
        parts = token.split(".")
        if len(parts) != 3:
            raise ValueError("Invalid JWT format")

        header = json.loads(cls._base64url_decode(parts[0]))
        payload = json.loads(cls._base64url_decode(parts[1]))

        return header, payload

    @classmethod
    def create_iac_token(
        cls,
        delegation_id: str,
        principal_id: str,
        agent_id: str,
        validity_start: Optional[str] = None,
        validity_end: Optional[str] = None,
        max_total_amount: float = 10000.0,
        max_single_amount: Optional[float] = None,
        allowed_payment_methods: Optional[list] = None,
        allowed_merchants: Optional[list] = None,
        allowed_items: Optional[list] = None,  # 场景特定：允许购买的商品
        delegation_mode: str = "SPECIFIED",
        agent_type: str = "PLATFORM_AGENT",  # PLATFORM_AGENT / DEDICATED_AGENT
        subaccount_id: Optional[str] = None,  # 场景三：专属子账户
        delegation_purpose: Optional[str] = None  # 委托目的说明
    ) -> str:
        """
        创建 IAC（意图授权凭证）

        支持两种委托支付场景：
        1. 场景二（平台型智能体）：agent_type=PLATFORM_AGENT，需验证平台 + 委托人双重绑定
        2. 场景三（专属型智能体）：agent_type=DEDICATED_AGENT，可设置 subaccount_id 进行风险隔离

        Args:
            delegation_id: 委托标识
            principal_id: 委托人 ID
            agent_id: 智能体 ID
            validity_start: 有效期开始（可选，默认当前时间）
            validity_end: 有效期结束（可选，默认 1 年后）
            max_total_amount: 授权总金额上限
            max_single_amount: 单笔金额上限（可选）
            allowed_payment_methods: 允许的支付方式列表（可选）
            allowed_merchants: 允许的商户列表（可选）
            allowed_items: 允许购买的商品列表（场景特定约束）
            delegation_mode: 委托模式（SPECIFIED/UNSPECIFIED）
            agent_type: 智能体类型（PLATFORM_AGENT/DEDICATED_AGENT）
            subaccount_id: 专属子账户 ID（场景三可选）
            delegation_purpose: 委托目的说明（明确购买标的）

        Returns:
            IAC JWT 字符串
        """
        now = datetime.now(timezone.utc)

        # 如果没有指定时间，使用当前时间和 1 年后
        if validity_start is None:
            validity_start = now.isoformat()
        if validity_end is None:
            validity_end = (now.replace(year=now.year + 1)).isoformat()

        payload = {
            "iss": principal_id,  # Issuer
            "sub": agent_id,  # Subject
            "iat": now.isoformat(),  # Issued at
            "jti": delegation_id,  # JWT ID
            "exp": cls._parse_datetime_to_epoch(validity_end),  # Expiration
            "nbf": cls._parse_datetime_to_epoch(validity_start),  # Not before

            # VC+JWT declaration
            "typ": "vc+jwt",

            # VC data
            "vc": {
                "type": ["VCValidationCredential", "ActIntentAuthorization"],
                "credential_subject": {
                    # 核心授权意图
                    "user_intent_raw": delegation_purpose or "委托智能体代为支付",
                    "delegation_id": delegation_id,
                    "delegation_mode": delegation_mode,

                    # 时效约束
                    "validity_start_time": validity_start,
                    "validity_end_time": validity_end,

                    # 金额约束
                    "max_total_amount": max_total_amount,
                    "amount_currency": "CNY",

                    # 支付约束
                    "allowed_payment_methods": allowed_payment_methods or [],
                    "allowed_merchants": allowed_merchants or [],

                    # 身份绑定（场景二：平台型智能体的关键）
                    "signer_identity": principal_id,
                    "agent_id": agent_id,
                    "agent_type": agent_type,  # PLATFORM_AGENT / DEDICATED_AGENT

                    # 场景特定字段
                    "delegation_purpose": delegation_purpose,  # 明确购买标的
                    "allowed_items": allowed_items or [],  # 允许购买的商品
                    "subaccount_id": subaccount_id,  # 场景三专属子账户（可选）
                }
            }
        }

        if max_single_amount:
            payload["max_single_amount"] = max_single_amount
            payload["vc"]["credential_subject"]["max_single_amount"] = max_single_amount

        if allowed_merchants:
            payload["vc"]["credential_subject"]["allowed_merchants"] = allowed_merchants

        if allowed_items:
            payload["vc"]["credential_subject"]["allowed_items"] = allowed_items

        if subaccount_id:
            payload["vc"]["credential_subject"]["subaccount_id"] = subaccount_id

        return cls.encode(payload)

    @classmethod
    def _base64url_encode(cls, data: bytes) -> str:
        """Base64URL 编码"""
        return base64.urlsafe_b64encode(data).rstrip(b"=").decode()

    @classmethod
    def _base64url_decode(cls, data: str) -> bytes:
        """Base64URL 解码"""
        # 添加 padding
        padding = 4 - len(data) % 4
        if padding != 4:
            data += "=" * padding
        return base64.urlsafe_b64decode(data)

    @classmethod
    def _sign(cls, message: str) -> bytes:
        """使用 HMAC-SHA256 签名"""
        return hmac.new(
            cls._SECRET_KEY.encode(),
            message.encode(),
            hashlib.sha256
        ).digest()

    @classmethod
    def verify_signature(cls, token: str) -> bool:
        """验证 JWT 签名（简化的验证方法）"""
        try:
            cls.decode(token, verify=True)
            return True
        except ValueError:
            return False

    @staticmethod
    def _parse_datetime_to_epoch(dt_string: str) -> int:
        """将 ISO8601 日期字符串转换为 Unix 时间戳"""
        try:
            # 处理 Z 后缀
            if dt_string.endswith("Z"):
                dt_string = dt_string[:-1] + "+00:00"

            dt = datetime.fromisoformat(dt_string)

            # 如果有显式时区信息，直接转换
            if dt.tzinfo is not None:
                return int(dt.timestamp() * 1000)

            # 如果没有时区信息，假设为本地时间并转换为 UTC
            # 这是为了确保与 Python datetime.now() 的兼容性
            import time
            # 将本地时间作为 UTC 解读，然后转换 - 这样 datetime.now() 的结果会被正确解释
            local_utc = time.mktime(dt.timetuple()) * 1000
            return int(local_utc)
        except Exception:
            # 如果解析失败，返回当前时间
            return int(time.time() * 1000)