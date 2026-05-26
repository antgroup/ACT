"""
完整委托支付流程测试
演示商品服务注册商品后，委托代理自动感知并执行支付
"""

import sys
import os

# 添加项目路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from psd.delegated_payment import (
    DelegatedPaymentHandler,
    DelegationApplyRequest,
    DelegationScenario
)
from psd.delegated_payment.payload import PaymentTokenInfo, DelegatedPaymentPayload
from merchant_service.service import merchant_service
from assistant_agent.delegated_payment_agent import DelegatedPaymentAgent

# 全局回调存储
_product_callbacks = []

def register_callback(callback):
    """注册商品变更回调"""
    _product_callbacks.append(callback)

def _notify_product_added(product):
    """通知产品添加"""
    for callback in _product_callbacks:
        try:
            callback(product)
        except Exception as e:
            print(f"Error in callback: {e}")


def simple_callback_handler(product):
    """简单的事件处理器"""
    print(f"\n🔔 [助理感知] 检测到新商品：{product['name']} (ID: {product['item_id']}, ¥{product['price']:.2f})")


# 覆盖 register_product 方法来注入回调
original_register_product = merchant_service.register_product

def new_register_product(name, price, category, description="", stock=100, tags=None, supplier_id=None):
    """包装的注册产品方法，包含回调"""
    result = original_register_product(name, price, category, description, stock, tags, supplier_id)
    if result["success"] and result.get("data"):
        _notify_product_added(result["data"])
    return result

merchant_service.register_product = new_register_product


def main():
    """演示完整委托支付流程 - 包含商品服务"""

    print("=" * 70)
    print("ACT 协议完整委托支付流程演示")
    print("结合商品服务 + 委托支付 + 智能助理")
    print("=" * 70)

    # ============================================
    # 初始化
    # ============================================
    print("\n【系统初始化】")

    # 注册商品变更回调
    register_callback(simple_callback_handler)

    # 创建代理
    agent = DelegatedPaymentAgent()

    # ============================================
    # 步骤 1: 商户注册新商品
    # ============================================
    print("\n" + "=" * 70)
    print("步骤 1: 商户服务注册新商品")
    print("=" * 70)

    # 注册新商品 1
    result1 = merchant_service.register_product(
        name="无线蓝牙耳机",
        price=299.0,
        category="电子产品",
        description="主动降噪，长续航",
        stock=50,
        tags=["audio", "wireless", "bluetooth"]
    )
    print(f"\n✅ {result1['message']}")
    if result1.get("data"):
        print(f"   商品 ID: {result1['data']['item_id']}")
        print(f"   名称：{result1['data']['name']}")
        print(f"   价格：¥{result1['data']['price']:.2f}")

    # 注册新商品 2
    result2 = merchant_service.register_product(
        name="智能手环",
        price=199.0,
        category="电子产品",
        description="健康监测，运动追踪",
        stock=100,
        tags=["health", "fitness", "smart"]
    )
    print(f"\n✅ {result2['message']}")
    if result2.get("data"):
        print(f"   商品 ID: {result2['data']['item_id']}")
        print(f"   名称：{result2['data']['name']}")
        print(f"   价格：¥{result2['data']['price']:.2f}")

    # 显示当前商品列表
    print("\n--- 当前商品列表 ---")
    products = merchant_service.get_product_list()["data"]
    for p in products:
        print(f"  - {p['item_id']}: {p['name']} (¥{p['price']:.2f}) - {p['category']}")

    # ============================================
    # 步骤 2: 用户发起委托支付请求
    # ============================================
    print("\n" + "=" * 70)
    print("步骤 2: 用户发起委托支付请求")
    print("=" * 70)

    print("\n【用户】帮我购买智能手环，不超过 300 元")
    response1 = agent.process_user_message("帮我购买智能手环，不超过 300 元")
    print("\n【助理】")
    print(response1[:400] + "...")

    # ============================================
    # 步骤 3: 用户确认授权
    # ============================================
    print("\n" + "-" * 50)
    print("【用户】好的，同意授权")
    response2 = agent.process_user_message("好的，同意授权")
    print("\n【助理】")
    print(response2[:400] + "...")

    # ============================================
    # 步骤 4: 查看可用商品
    # ============================================
    print("\n" + "-" * 50)
    print("【用户】查看商品列表")
    response3 = agent.process_user_message("查看商品列表")
    print("\n【助理】")
    print(response3[:800])

    # ============================================
    # 步骤 5: 执行购买
    # ============================================
    print("\n" + "-" * 50)
    print("【用户】购买智能手环")
    response4 = agent.process_user_message("购买智能手环")
    print("\n【助理】")
    print(response4[:600])

    # ============================================
    # 步骤 6: 更多商品注册
    # ============================================
    print("\n" + "=" * 70)
    print("步骤 6: 商户继续注册新商品（助理自动感知）")
    print("=" * 70)

    result3 = merchant_service.register_product(
        name="机械键盘",
        price=599.0,
        category="电子产品",
        description="青轴，RGB 背光",
        stock=30,
        tags=["keyboard", "gaming", "rgb"]
    )
    print(f"\n✅ {result3['message']}")
    if result3.get("data"):
        print(f"   商品 ID: {result3['data']['item_id']}")
        print(f"   新商品已注册")

    # ============================================
    # 步骤 7: 查询累计扣款
    # ============================================
    print("\n" + "=" * 70)
    print("步骤 7: 查询委托状态")
    print("=" * 70)

    current_delegation_id = agent.delegation_context.get("active_delegation_id")
    if current_delegation_id:
        cumulative = agent.delegation_handler.payment_service.get_cumulative_amount(
            current_delegation_id
        )
        remaining = agent.delegation_context["max_total_amount"] - cumulative
        print(f"\n委托 ID: {current_delegation_id[:40]}...")
        print(f"总额度：¥{agent.delegation_context['max_total_amount']:.2f}")
        print(f"已用额度：¥{cumulative:.2f}")
        print(f"剩余额度：¥{remaining:.2f}")

    # ============================================
    # 总结
    # ============================================
    print("\n" + "=" * 70)
    print("【演示总结】")
    print("=" * 70)
    print("""
✅ 功能演示完成！

1. 商品服务注册 - 商户可以动态注册商品
2. 助理感知 - 委托代理自动感知新商品（通过回调）
3. 委托支付 - 用户可以授权智能体执行购买
4. 额度控制 - 严格的金额限制
5. 实时状态 - 随时查看委托状态和剩余额度

【使用方式】
- 商户：merchant_service.register_product(name, price, category, ...)
- 用户：在对话中说"帮我买 XXX，不超过 XXX 元"
- 查看商品："查看商品列表"
- 购买："购买 XXX"
    """)


if __name__ == "__main__":
    main()