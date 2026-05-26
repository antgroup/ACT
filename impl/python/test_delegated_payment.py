"""
委托支付示例脚本
展示如何使用 ACT 协议 Python 实现完成委托支付流程

支持的两种场景：
1. 场景二：平台型智能体定向委托
   - 多租户共享平台智能体身份
   - 需验证平台 + 委托人双重绑定

2. 场景三：专属型智能体定向委托
   - 智能体与委托人设备/账号强绑定
   - 支持子账户风险隔离
"""

import sys
import os

# 添加项目路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from psd.delegated_payment import (
    DelegatedPaymentHandler,
    DelegationApplyRequest,
    DelegationQueryRequest,
    DelegationCancelRequest,
    DelegationPayRequest,
    DelegationScenario
)
from psd.delegated_payment.payload import PaymentTokenInfo


def main():
    """演示完整委托支付流程 - 场景三：专属型智能体定向委托"""

    print("=" * 70)
    print("ACT 协议委托支付 (PSD-PAY-DEL) 演示")
    print("=" * 70)

    # 场景说明
    print("""

    📌 演示场景：场景三 - 专属型智能体定向委托

    本场景适用于：
    • 委托人不在场
    • 购买标的已在初始交互中明确
    • 智能体与委托人设备/账号强绑定

    核心特征：
    • 独立唯一智能体身份
    • 支持子账户风险隔离
    • 直接锚定专属智能体验证

    典型示例：帮我买《人工智能：现代方法》这本书，不超过 150 元

    """ + "=" * 70)

    # ============================================
    # 初始化服务
    # ============================================
    print("\n【初始化】创建委托支付服务...")

    handler = DelegatedPaymentHandler()
    print("委托支付服务已就绪\n")

    # ============================================
    # 步骤 1：委托协议签约（签发 IAC）
    # ============================================
    print("=" * 70)
    print("步骤 1：委托协议签约（签发 IAC）")
    print("=" * 70)

    # 场景三：专属型智能体定向委托
    apply_request = DelegationApplyRequest(
        principal_id="did:act:example.com/user-alice",
        agent_id="did:act:example.com/alice-dedicated-agent",  # 专属智能体
        delegation_id="urn:uuid:7f3e9a12-b4c8-4d56-a321-8b7c6d5e4f30",
        delegation_mode="SPECIFIED",
        agent_type=DelegationScenario.DEDICATED_AGENT.value,  # 专属型智能体
        subaccount_id="SA-ALICE-001",  # 场景三：专属子账户
        delegation_purpose="帮我买《人工智能：现代方法》这本书，不超过 150 元，准备买 3 本",
        allowed_items=["BOOK-9787111XXX"],  # 允许购买的商品
        validity_start=None,
        validity_end=None,
        max_total_amount=5000.0,  # 5 本 * 1000 元 = 5000 元
        max_single_amount=1500.0,  # 单本最高 1500 元
        allowed_payment_methods=None,
        allowed_merchants=None
    )

    apply_response = handler.apply_delegation(apply_request)

    print(f"\n✓ 委托协议已签发（场景三：专属型智能体）")
    print(f"  委托 ID: {apply_response.delegation_id}")
    print(f"  签发时间：{apply_response.issued_at}")
    print(f"  协议状态：{apply_response.status}")
    print(f"  IAC 凭证：{apply_response.iac[:60]}...")

    # 场景三特有信息
    print(f"\n  智能体类型：{apply_response.agent_type}")
    print(f"  专属子账户：{apply_response.subaccount_id}")
    print(f"  委托目的：{apply_response.delegation_purpose}")
    print(f"  允许商品：{apply_response.max_single_amount}")

    iac = apply_response.iac
    delegation_id = apply_response.delegation_id
    max_total = apply_response.max_total_amount
    print()

    # ============================================
    # 步骤 2：查询委托状态
    # ============================================
    print("=" * 70)
    print("步骤 2：查询委托协议状态")
    print("=" * 70)

    query_request = DelegationQueryRequest(
        delegation_id=delegation_id,
        principal_id="did:act:example.com/user-alice"
    )

    query_response = handler.query_delegation(query_request)

    print(f"\n✓ 委托协议状态查询结果:")
    print(f"  委托 ID: {query_response.delegation_id}")
    print(f"  状态：{query_response.status}")
    print(f"  委托人：{query_response.principal_id}")
    print(f"  累计已扣款：¥{query_response.cumulative_amount:.2f}")
    print()

    # ============================================
    # 步骤 3：构造购物车快照
    # ============================================
    print("=" * 70)
    print("步骤 3：构造购物车确认")
    print("=" * 70)

    # 场景三：购买 3 本书，总金额 450 元（在授权范围内）
    cart_items = [
        {
            "item_id": "BOOK-9787111XXX",  # 符合 allowed_items 中的商品
            "name": "《人工智能：现代方法》",
            "quantity": 3,
            "unit_price": 150.0,
            "total_price": 450.0
        }
    ]

    from psd.delegated_payment.payload import DelegatedPaymentPayload
    cart_snapshot_hash = DelegatedPaymentPayload.calculate_cart_snapshot_hash(cart_items)

    pay_amount = 450.0  # 3 本 * 150 元 = 450 元，在 max_single_amount=1500 限制内

    print(f"\n✓ 购物车确认:")
    for item in cart_items:
        print(f"  - {item['name']}: ¥{item['total_price']:.2f} x {item['quantity']}")
    print(f"  订单总额：¥{pay_amount:.2f}")
    print(f"  购物车快照哈希：{cart_snapshot_hash}")
    print()

    # ============================================
    # 步骤 4：执行委托支付
    # ============================================
    print("=" * 70)
    print("步骤 4：执行委托支付")
    print("=" * 70)

    # Create payment token info
    payment_token_info = PaymentTokenInfo(
        token="t_mock_token_12345",
        token_type="CARD_TOKEN",
        token_scheme="EMV_PAIT"
    )

    # Create subaccount info (optional)
    # subaccount_info = SubAccountInfo(
    #     subaccount_id="SA-20240514-001",
    #     signature="mock_signature_abc123"
    # )

    pay_request = DelegationPayRequest(
        request_id=f"req-deleg-{delegation_id.split('-')[-1]}",
        buyer_agent_id="did:act:example.com/alice-dedicated-agent",  # 与 IAC 中的 agent_id 一致
        delegation_id=delegation_id,
        iac=iac,
        merchant_id="did:act:example.com/merchant-bookstore",
        merchant_order_id="MCH20240514123456789",
        cart_snapshot_hash=cart_snapshot_hash,
        amount=pay_amount,
        currency="CNY",
        payment_method="urn:act:payment:example-wallet",
        payment_token=payment_token_info
    )

    pay_response = handler.pay(pay_request)

    print(f"\n{'='*40}")
    print("支付结果:")
    print(f"{'='*40}")

    if pay_response.success:
        print(f"  ✓ 支付成功!")
        print(f"\n  支付详情:")
        print(f"    支付流水号：{pay_response.payment_id}")
        print(f"    交易流水号：{pay_response.transaction_id}")
        print(f"    订单号：{pay_request.merchant_order_id}")
        print(f"    支付金额：¥{pay_response.amount:.2f}")
        print(f"    币种：{pay_response.currency}")
        print(f"    状态：{pay_response.status}")
    else:
        print(f"  ✗ 支付失败!")
        print(f"\n  错误信息:")
        print(f"    错误代码：{pay_response.error_code}")
        print(f"    错误消息：{pay_response.error_message}")

    print()

    # ============================================
    # 步骤 5：查询累计扣款金额
    # ============================================
    print("=" * 70)
    print("步骤 5：查询累计扣款确认额")
    print("=" * 70)

    renewed_cumulative = handler.payment_service.get_cumulative_amount(delegation_id)

    print(f"\n✓ 累计扣款确认额：¥{renewed_cumulative:.2f}")
    print(f"  剩余授权额度：¥{max_total - renewed_cumulative:.2f}")
    print()

    # ============================================
    # 步骤 6：吊销委托授权（可选）
    # ============================================
    print("=" * 70)
    print("步骤 6：吊销委托授权（测试）")
    print("=" * 70)

    cancel_request = DelegationCancelRequest(
        delegation_id=delegation_id,
        principal_id="did:act:example.com/user-alice",
        reason="任务完成，取消委托"
    )

    cancel_response = handler.cancel_delegation(cancel_request)

    print(f"\n✓ 委托状态变更:")
    print(f"  委托 ID: {cancel_response.delegation_id}")
    print(f"  原状态：{cancel_response.old_status}")
    print(f"  新状态：{cancel_response.new_status}")
    print(f"  说明：{cancel_response.message}")
    print()

    # ============================================
    # 总结
    # ============================================
    print("=" * 70)
    print("委托支付流程演示完成")
    print("=" * 70)

    print(f"""

【ACT 协议 PSD-PAY-DEL 流程总结】

1. 签约 (APPLY)    → 用户签发 IAC，授权智能体支付
2. 查询 (QUERY)    → 查询协议状态和剩余额度
3. 购物车确认      → 商户返回商品和价格
4. 支付 (PAY)      → 智能体发起委托支付
5. 累计扣款        → PSP 更新授权额度
6. 吊销 (CANCEL)   → 任务完成后取消授权

【核心特性】
  ✓ 用户意图可信授权 (IAC)
  ✓ 授权范围可验证 (金额/商户/时间)
  ✓ 支付标记化保护 (token)
  ✓ 子账户资金隔离 (可选)
  ✓ 累计额度控制
  ✓ 全链路存证 (待扩展)

    """)


if __name__ == "__main__":
    main()