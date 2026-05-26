"""
委托支付验证器
负责验证委托支付请求的各个要素
"""

import json
import time
from dataclasses import dataclass
from typing import Dict, Any, Optional, List
from datetime import datetime, timezone
from enum import Enum

from .mock_jwt import MockJWT


class PaymentErrorCode(Enum):
    """
    支付错误代码
    按照 ACT 协议规范定义
    """
    # 请求相关错误
    INVALID_REQUEST = "INVALID_REQUEST"
    REQUEST_DUPLICATE = "REQUEST_DUPLICATE"
    REQUEST_EXPIRED = "REQUEST_EXPIRED"

    # 智能体签名错误
    AGENT_SIGNATURE_INVALID = "AGENT_SIGNATURE_INVALID"
    AGENT_SIGNATURE_ALGORITHM_UNSUPPORTED = "AGENT_SIGNATURE_ALGORITHM_UNSUPPORTED"
    AGENT_ID_MISMATCH = "AGENT_ID_MISMATCH"

    # IAC 相关错误
    IAC_EXPIRED = "IAC_EXPIRED"
    IAC_REVOKED = "IAC_REVOKED"
    IAC_SUSPENDED = "IAC_SUSPENDED"
    IAC_INVALID = "IAC_INVALID"
    IAC_SIGNATURE_INVALID = "IAC_SIGNATURE_INVALID"

    # 智能体身份校验
    AGENT_NOT_AUTHORIZED = "AGENT_NOT_AUTHORIZED"
    DELEGATION_MODE_MISMATCH = "DELEGATION_MODE_MISMATCH"

    # 金融约束错误
    SINGLE_AMOUNT_LIMIT = "SINGLE_AMOUNT_LIMIT"
    TOTAL_AMOUNT_LIMIT = "TOTAL_AMOUNT_LIMIT"
    BALANCE_INSUFFICIENT = "BALANCE_INSUFFICIENT"

    # 支付方式错误
    PAYMENT_METHOD_INVALID = "PAYMENT_METHOD_INVALID"
    PAYMENT_METHOD_NOT_ALLOWED = "PAYMENT_METHOD_NOT_ALLOWED"

    # 商户相关错误
    MERCHANT_NOT_ALLOWED = "MERCHANT_NOT_ALLOWED"
    MERCHANT_NOT_FOUND = "MERCHANT_NOT_FOUND"

    # 金额相关错误
    AMOUNT_SNAPSHOT_MISMATCH = "AMOUNT_SNAPSHOT_MISMATCH"
    AMOUNT_INVALID = "AMOUNT_INVALID"

    # 子账户相关错误
    SUBACCOUNT_INVALID = "SUBACCOUNT_INVALID"
    SUBACCOUNT_SIGNATURE_INVALID = "SUBACCOUNT_SIGNATURE_INVALID"
    SUBACCOUNT_FROZEN = "SUBACCOUNT_FROZEN"

    # 支付标记错误
    TOKEN_INVALID = "TOKEN_INVALID"
    TOKEN_EXPIRED = "TOKEN_EXPIRED"
    TOKEN_MISMATCH = "TOKEN_MISMATCH"

    # 系统错误
    SYSTEM_ERROR = "SYSTEM_ERROR"
    INTERNAL_ERROR = "INTERNAL_ERROR"


@dataclass
class PaymentError:
    """
    支付错误信息
    """
    code: PaymentErrorCode
    message: str
    details: Optional[Dict[str, Any]] = None

    def to_dict(self) -> Dict[str, Any]:
        result = {
            "error": {
                "code": self.code.value,
                "message": self.message
            }
        }
        if self.details:
            result["error"]["details"] = self.details
        return result


class IACValidator:
    """
    IAC（意图授权凭证）验证器
    """

    def __init__(self, revocation_list: Optional[List[str]] = None):
        """
        初始化验证器

        Args:
            revocation_list: 已吊销的 IAC delegation_id 列表
        """
        self.revocation_list = set(revocation_list or [])

    def validate(
        self,
        iac_token: str,
        expected_agent_id: str,
        current_time: Optional[datetime] = None
    ) -> tuple[bool, Optional[PaymentError]]:
        """
        验证 IAC

        Args:
            iac_token: IAC JWT 字符串
            expected_agent_id: 期望的受托智能体 ID
            current_time: 当前时间（用于测试）

        Returns:
            (是否有效，错误信息)
        """
        # 1. 解码 JWT
        try:
            iac_payload = MockJWT.decode(iac_token, verify=True)
        except ValueError as e:
            return False, PaymentError(
                code=PaymentErrorCode.IAC_INVALID,
                message=f"IAC 格式无效：{str(e)}"
            )

        # 2. 验证 IAC 签名
        if not MockJWT.verify_signature(iac_token):
            return False, PaymentError(
                code=PaymentErrorCode.IAC_SIGNATURE_INVALID,
                message="IAC 签名验证失败"
            )

        # 3. 检查是否被吊销
        delegation_id = iac_payload.get("jti", "")
        if delegation_id in self.revocation_list:
            return False, PaymentError(
                code=PaymentErrorCode.IAC_REVOKED,
                message="IAC 已被吊销",
                details={"delegation_id": delegation_id}
            )

        # 4. 验证有效期
        nbf = iac_payload.get("nbf", 0)  # Not Before (milliseconds)
        exp = iac_payload.get("exp", 0)  # Expiration (milliseconds)

        # 使用 UTC 时间进行比较
        current = current_time or datetime.now(timezone.utc)
        current_timestamp = int(current.timestamp() * 1000)  # Convert to milliseconds

        # 添加 30 秒容差以处理时间戳精度问题
        tolerance_ms = 30 * 1000  # 30 seconds in milliseconds

        if current_timestamp < (nbf - tolerance_ms):
            nbf_dt = datetime.fromtimestamp(nbf / 1000, tz=timezone.utc)
            return False, PaymentError(
                code=PaymentErrorCode.IAC_EXPIRED,
                message="IAC 尚未生效",
                details={"nbf": nbf_dt.isoformat(), "current": datetime.fromtimestamp(current_timestamp / 1000, tz=timezone.utc).isoformat()}
            )

        if current_timestamp > (exp + tolerance_ms):
            return False, PaymentError(
                code=PaymentErrorCode.IAC_EXPIRED,
                message="IAC 已过期",
                details={"exp": datetime.fromtimestamp(exp / 1000).isoformat()}
            )

        # 5. 验证智能体身份
        sub = iac_payload.get("sub", "")
        if sub != expected_agent_id:
            return False, PaymentError(
                code=PaymentErrorCode.AGENT_ID_MISMATCH,
                message="IAC 中的智能体 ID 与请求中的 ID 不匹配",
                details={
                    "iac_agent_id": sub,
                    "request_agent_id": expected_agent_id
                }
            )

        return True, None

    def extract_delegation_info(
        self,
        iac_token: str
    ) -> tuple[Optional[Any], Optional[PaymentError]]:
        """
        从 IAC 中提取委托信息

        Args:
            iac_token: IAC JWT 字符串

        Returns:
            (委托信息，错误信息)
        """
        try:
            iac_payload = MockJWT.decode(iac_token, verify=False)
            return MockJWT.create_iac_token(**{}), None  # Simplified
        except Exception as e:
            return None, PaymentError(
                code=PaymentErrorCode.IAC_INVALID,
                message=f"解析 IAC 失败：{str(e)}"
            )


class DelegatedPaymentValidator:
    """
    委托支付请求验证器
    按照 ACT 协议 PSD-PAY-DEL 要求验证所有字段
    """

    # 为方便导出
    ErrorCodes = PaymentErrorCode

    def __init__(
        self,
        iac_validator: Optional[IACValidator] = None,
        payment_balance_store: Optional[Dict[str, float]] = None
    ):
        """
        初始化验证器

        Args:
            iac_validator: IAC 验证器
            payment_balance_store: 支付余额存储（用于模拟查询）
        """
        self.iac_validator = iac_validator or IACValidator()
        self.payment_balance_store = payment_balance_store or {}

        # 累计扣款记录（内部状态）
        self.cumulative_amounts: Dict[str, float] = {}

    def validate_request(
        self,
        request: Dict[str, Any]
    ) -> tuple[bool, Optional[PaymentError]]:
        """
        验证委托支付请求

        按照 ACT 协议 PSD-PAY-DEL 定义的步骤进行验证

        步骤一：防重放校验
        步骤二：智能体签名验证
        步骤三：IAC 有效性核验
        步骤四：金融层约束核验
        步骤五：语义层约束核验

        Args:
            request: 委托支付请求字典

        Returns:
            (是否有效，错误信息)
        """
        # ===== 步骤一：防重放校验 =====
        request_id = request.get("request_id")
        if not request_id:
            return False, PaymentError(
                code=PaymentErrorCode.INVALID_REQUEST,
                message="缺少 request_id"
            )

        # 检查是否重复请求（实际需要持久化存储）
        # if request_id in self.processed_requests:
        #     return False, PaymentError(
        #         code=PaymentErrorCode.REQUEST_DUPLICATE,
        #         message="请求已处理，疑似重放攻击"
        #     )

        # 检查时间戳有效性
        timestamp = request.get("timestamp")
        if timestamp:
            try:
                req_time = datetime.fromisoformat(timestamp.replace("Z", "+00:00"))
                current_time = datetime.now(req_time.tzinfo)
                time_diff = abs((current_time - req_time).total_seconds())

                if time_diff > 300:  # 5 分钟有效期
                    return False, PaymentError(
                        code=PaymentErrorCode.REQUEST_EXPIRED,
                        message="请求已过期",
                        details={"time_diff_seconds": time_diff}
                    )
            except ValueError:
                return False, PaymentError(
                    code=PaymentErrorCode.INVALID_REQUEST,
                    message="时间戳格式无效"
                )

        # ===== 步骤二：智能体签名验证 =====
        signature = request.get("signature")
        if signature:
            # 实际场景应从 DID Document 获取公钥验证
            # 此处为 mock 验证
            if not self._verify_agent_signature(request):
                return False, PaymentError(
                    code=PaymentErrorCode.AGENT_SIGNATURE_INVALID,
                    message="智能体签名验证失败"
                )

        # ===== 步骤三：IAC 有效性核验 =====
        iac = request.get("iac")
        if not iac:
            return False, PaymentError(
                code=PaymentErrorCode.IAC_INVALID,
                message="缺少 IAC"
            )

        buyer_agent_id = request.get("buyer_agent_id")
        iac_valid, iac_error = self.iac_validator.validate(iac, buyer_agent_id)

        if not iac_valid:
            return False, iac_error

        # ===== 步骤四：金融层约束核验 =====
        # 4.1 单笔金额校验
        amount_str = request.get("amount")
        if not amount_str:
            return False, PaymentError(
                code=PaymentErrorCode.AMOUNT_INVALID,
                message="缺少金额"
            )

        try:
            amount = float(amount_str)
        except ValueError:
            return False, PaymentError(
                code=PaymentErrorCode.AMOUNT_INVALID,
                message="金额格式无效"
            )

        # 获取 IAC 中的单笔限额
        delegation_info = self.iac_validator.extract_delegation_info(iac)[0]
        if delegation_info:
            max_single = delegation_info.allowed_amounts.get("max_single_amount")
            if max_single and amount > max_single:
                return False, PaymentError(
                    code=PaymentErrorCode.SINGLE_AMOUNT_LIMIT,
                    message="本次金额超出 IAC 单笔上限",
                    details={
                        "requested_amount": amount,
                        "max_single_amount": max_single
                    }
                )

        # 4.2 累计额度校验
        delegation_id = request.get("delegation_id")
        cumulative = self.cumulative_amounts.get(delegation_id, 0.0)

        max_total = delegation_info.allowed_amounts.get("max_total_amount") if delegation_info else None
        if max_total and (cumulative + amount) > max_total:
            return False, PaymentError(
                code=PaymentErrorCode.TOTAL_AMOUNT_LIMIT,
                message="累计金额超出 IAC 授权总额上限",
                details={
                    "cumulative_before": cumulative,
                    "requested_amount": amount,
                    "max_total_amount": max_total,
                    "cumulative_after": cumulative + amount
                }
            )

        # 4.3 支付方式匹配
        payment_method = request.get("payment_method")
        if delegation_info and delegation_info.allowed_payment_methods:
            if payment_method and payment_method not in delegation_info.allowed_payment_methods:
                return False, PaymentError(
                    code=PaymentErrorCode.PAYMENT_METHOD_NOT_ALLOWED,
                    message="支付方式不在允许的列表中",
                    details={
                        "requested_method": payment_method,
                        "allowed_methods": delegation_info.allowed_payment_methods
                    }
                )

        # ===== 步骤五：语义层约束核验（可选）=====
        # 5.1 商户白名单检查
        merchant_id = request.get("merchant_id")
        if delegation_info and delegation_info.allowed_merchants:
            if merchant_id not in delegation_info.allowed_merchants:
                return False, PaymentError(
                    code=PaymentErrorCode.MERCHANT_NOT_ALLOWED,
                    message="收款商户不在允许范围内"
                )

        # 5.2 金额一致性校验
        cart_snapshot_hash = request.get("cart_snapshot_hash")
        if cart_snapshot_hash and amount:
            # 实际需要查询购物车快照进行比对
            pass

        # 所有验证通过
        return True, None

    def _verify_agent_signature(
        self,
        request: Dict[str, Any]
    ) -> bool:
        """
        验证智能体签名（mock 实现）

        Args:
            request: 委托支付请求

        Returns:
            是否验证通过
        """
        # 模拟签名验证（真实场景应使用数字签名库）
        signature = request.get("signature", "")
        return len(signature) > 0 and signature is not None

    def update_cumulative_amount(
        self,
        delegation_id: str,
        amount: float
    ):
        """
        更新累计扣款确认额

        Args:
            delegation_id: 委托标识
            amount: 增加金额
        """
        self.cumulative_amounts[delegation_id] = \
            self.cumulative_amounts.get(delegation_id, 0.0) + amount

    def get_cumulative_amount(
        self,
        delegation_id: str
    ) -> float:
        """
        获取累计扣款确认额

        Args:
            delegation_id: 委托标识

        Returns:
            累计金额
        """
        return self.cumulative_amounts.get(delegation_id, 0.0)

    def verify_signature_covered_fields(
        self,
        request: Dict[str, Any],
        signature: str,
        covered_fields: List[str]
    ) -> bool:
        """
        验证签名覆盖的字段

        Args:
            request: 请求数据
            signature: 签名
            covered_fields: 签名覆盖的字段列表

        Returns:
            是否验证通过
        """
        # 简单验证（实际需要更复杂的签名验证逻辑）
        data_to_verify = ""
        for field in covered_fields:
            value = request.get(field, "")
            data_to_verify += f"{field}={value};"

        return len(signature) > len(data_to_verify)