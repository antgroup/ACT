"""
ACT 协议支付演示界面 (Payment Demo UI)
展示三种支付模式的差异：即时支付、委托支付、自主支付
"""
import streamlit as st
import time
import uuid
from typing import Dict, Any

from merchant_service.service import merchant_service
from payment_service.instant_payment import InstantPaymentService, InstantPayRequest
from payment_service.delegated_payment import DelegatedPaymentService, DelegationApplyRequest, DelegationPayRequest

# Global service singleton (persists across reruns in demo mode)
_delegated_service_singleton = None


def get_delegated_service() -> DelegatedPaymentService:
    """获取或创建委托支付服务单例，用于演示状态管理"""
    global _delegated_service_singleton
    if _delegated_service_singleton is None:
        _delegated_service_singleton = DelegatedPaymentService()
    return _delegated_service_singleton
from payment_service.delegated_payment import DelegatedPaymentService, DelegationApplyRequest
from psd.delegated_payment import DelegationPayRequest
from payment_service.autonomous_payment import AutonomousPaymentService, PaymentStrategy


def render_payment_demo_tab():
    """渲染支付演示标签页"""
    st.markdown('<div class="main-header">💳 ACT 协议 - 支付模式演示</div>', unsafe_allow_html=True)
    st.markdown('<div class="sub-header">即时支付 | 委托支付 | 自主支付</div>', unsafe_allow_html=True)

    # 显示三种支付模式对比
    st.markdown("### 📊 支付模式对比")

    col1, col2, col3 = st.columns(3)

    with col1:
        card_style = "border: 2px solid #1f77b4; border-radius: 0.5rem; padding: 1rem; background-color: #e3f2fd;"
        st.markdown(f"""
        <div style="{card_style}">
            <h4 style="margin-top: 0; color: #1f77b4;">💸 即时支付</h4>
            <p><strong>特点：</strong></p>
            <ul style="padding-left: 1rem;">
                <li>用户全程在场</li>
                <li>实时确认支付</li>
                <li>无需 IAC 委托</li>
                <li>单笔即时交易</li>
            </ul>
            <p><strong>流程：</strong></p>
            <ol style="padding-left: 1rem;">
                <li>选择商品</li>
                <li>请求支付</li>
                <li>唤起收银台</li>
                <li>用户确认并扣款</li>
            </ol>
            <p><strong>适用场景：</strong></p>
            <p style="font-size: 0.9rem; color: #666;">传统电商、实物商品购买</p>
        </div>
        """, unsafe_allow_html=True)

    with col2:
        card_style = "border: 2px solid #f57c00; border-radius: 0.5rem; padding: 1rem; background-color: #fef3e2;"
        st.markdown(f"""
        <div style="{card_style}">
            <h4 style="margin-top: 0; color: #f57c00;">💼 委托支付</h4>
            <p><strong>特点：</strong></p>
            <ul style="padding-left: 1rem;">
                <li>用户预先授权</li>
                <li>智能体代为支付</li>
                <li>基于 IAC 凭证</li>
                <li>额度限制可控</li>
            </ul>
            <p><strong>流程：</strong></p>
            <ol style="padding-left: 1rem;">
                <li>签发 IAC 凭证</li>
                <li>设定额度上限</li>
                <li>智能体下单</li>
                <li>PSP 核验 IAC 扣款</li>
            </ol>
            <p><strong>适用场景：</strong></p>
            <p style="font-size: 0.9rem; color: #666;">自动续费、代买任务</p>
        </div>
        """, unsafe_allow_html=True)

    with col3:
        card_style = "border: 2px solid #388e3c; border-radius: 0.5rem; padding: 1rem; background-color: #e8f5e9;"
        st.markdown(f"""
        <div style="{card_style}">
            <h4 style="margin-top: 0; color: #388e3c;">🤖 自主支付 (A2A)</h4>
            <p><strong>特点：</strong></p>
            <ul style="padding-left: 1rem;">
                <li>高度自主决策</li>
                <li>智能体间交易</li>
                <li>A2A 支付协议</li>
                <li>HTTP 402 语义</li>
            </ul>
            <p><strong>流程：</strong></p>
            <ol style="padding-left: 1rem;">
                <li>设定任务边界</li>
                <li>智能体拆解任务</li>
                <li>服务发现与协商</li>
                <li>A2A 支付完成交易</li>
            </ol>
            <p><strong>适用场景：</strong></p>
            <p style="font-size: 0.9rem; color: #666;">智能旅游规划、复杂任务外包</p>
        </div>
        """, unsafe_allow_html=True)

    # 分隔线
    st.markdown("---")

    # 支付模式选择
    st.markdown("### 🎯 选择演示模式")

    payment_mode = st.radio(
        "选择支付模式进行演示：",
        options=["即时支付演示", "委托支付演示", "自主支付演示"],
        index=0,
        label_visibility="collapsed"
    )

    # 根据选择渲染不同界面
    if "即时支付演示" in payment_mode:
        render_instant_payment_demo()
    elif "委托支付演示" in payment_mode:
        render_delegated_payment_demo()
    else:
        render_autonomous_payment_demo()


def render_instant_payment_demo():
    """渲染即时支付演示界面"""
    st.markdown('<div class="sub-header">💳 场景：用户实时在场，明确表达购买意图</div>', unsafe_allow_html=True)

    # 左右分栏
    left_col, right_col = st.columns([3, 1])

    with left_col:
        st.subheader("🛒 购物体验")

        # 显示商品列表
        products_result = merchant_service.get_product_list()

        if products_result["success"] and products_result["data"]:
            cols = st.columns(3)
            for i, product in enumerate(products_result["data"]):
                with cols[i % 3]:
                    st.metric(
                        label=product["name"],
                        value=f"¥{product['price']:.2f}",
                        delta=f"库存：{product['stock']}" if product["stock"] > 0 else "缺货"
                    )

                    if st.button(
                        "加入购物车",
                        key=f"add_{product['item_id']}",
                        use_container_width=True
                    ):
                        if "cart" not in st.session_state:
                            st.session_state.cart = []

                        st.session_state.cart.append({
                            "item_id": product["item_id"],
                            "name": product["name"],
                            "price": product["price"]
                        })
                        st.success(f"✅ 已添加 {product['name']} 到购物车")
                        st.rerun()
        else:
            st.info("暂无商品，请 Go 商户服务添加商品")

        # 购物车预览
        if "cart" in st.session_state and st.session_state.cart:
            st.markdown("---")
            st.subheader("🛍️ 购物车")

            total = 0
            for item in st.session_state.cart:
                st.markdown(f"• {item['name']} - ¥{item['price']:.2f}")
                total += item["price"]

            st.metric("订单总额", f"¥{total:.2f}")

            # 结算按钮
            if st.button("💳 立即结算", type="primary", use_container_width=True):
                with st.spinner("处理支付中..."):
                    # 创建订单
                    order_result = merchant_service.create_order(
                        item_id=st.session_state.cart[0]["item_id"],
                        quantity=1
                    )

                    if order_result["success"]:
                        # 发起即时支付
                        payment_service = InstantPaymentService(merchant_service)
                        pay_request = InstantPayRequest(
                            order_id=order_result["data"]["order_id"],
                            amount=order_result["data"]["total_amount"],
                            payment_method="credit_card"
                        )

                        pay_result = payment_service.pay(pay_request)

                        if pay_result.success:
                            st.success("✅ **支付成功**!")
                            st.info("""
                            **即时支付完成**：
                            - 用户全程在场
                            - 实时确认支付
                            - 使用已绑定的支付标记
                            - 唤起收银台，用户确认扣款
                            """)
                            st.session_state.cart = []
                            st.rerun()
                        else:
                            st.error(f"❌ 支付失败：{pay_result.message}")
        else:
            st.info("请先添加商品到购物车")

    with right_col:
        st.subheader("📖 流程图解")

        st.markdown("""
        ```
        用户 -> 智能体：帮我买 iPhone
         |
         v
        智能体 -> 商户：搜索商品目录
         |
         v
        智能体 -> 用户：确认商品 -> 实时选择
         |
         v
        用户 -> PSP：唤起收银台 -> 确认支付
         |
         v
        PSP -> 用户：扣款成功
        ```
        """)

        st.markdown("---")

        st.subheader("🔐 协议组件")

        st.markdown("""
        - `ADD-INT-EAC`：获取购买意图
        - `ADD-INT-ISR`：结构化意图表达
        - `CID-MER-CAT`：获取商品目录
        - `CID-CART-CFM`：购物车确认
        - `PSD-PAY-INS`：即时支付流程
        """)


def render_delegated_payment_demo():
    """渲染委托支付演示界面"""
    st.markdown('<div class="sub-header">💼 场景：用户预先签发 IAC，授权智能体代为支付</div>', unsafe_allow_html=True)

    # 左侧：委托管理
    left_col, right_col = st.columns([2, 1])

    with left_col:
        st.subheader("📝 委托管理")

        # 检查是否有活跃委托
        if "active_delegation" not in st.session_state or not st.session_state.active_delegation:
            st.info("💡 请创建新的委托协议")

            # 创建委托表单
            with st.form("create_delegation"):
                st.markdown("### 🔐 签发 IAC 凭证")

                principal_id = st.text_input(
                    "委托人 ID",
                    value="did:act:user-001",
                    help="用户的去中心化身份"
                )

                agent_id = st.text_input(
                    "智能体 ID",
                    value="did:act:assistant-001",
                    help="负责代买的智能体身份"
                )

                delegation_id = st.text_input(
                    "委托 ID",
                    value=f"urn:act:delegation:{int(time.time() * 1000)}",
                    help="委托唯一标识"
                )

                max_total = st.number_input(
                    "总额度上限",
                    min_value=0.0,
                    value=1000.0,
                    step=100.0,
                    format="%.2f"
                )

                max_single = st.number_input(
                    "单笔额度上限",
                    min_value=0.0,
                    value=200.0,
                    step=50.0,
                    format="%.2f"
                )

                delegation_purpose = st.text_input(
                    "委托目的",
                    value="智能助手代购授权",
                    help="委托用途说明"
                )

                submitted = st.form_submit_button("签发 IAC", type="primary", use_container_width=True)

                if submitted:
                    delegated_service = get_delegated_service()
                    result = delegated_service.apply(
                        DelegationApplyRequest(
                            principal_id=principal_id,
                            agent_id=agent_id,
                            delegation_id=delegation_id,
                            max_total_amount=max_total,
                            max_single_amount=max_single,
                            delegation_purpose=delegation_purpose
                        )
                    )

                    if result.delegation_id:
                        st.session_state.active_delegation = {
                            "delegation_id": result.delegation_id,
                            "iac": result.iac,
                            "max_total": result.max_total_amount,
                            "max_single": result.max_single_amount or 0,
                            "principal_id": principal_id,
                            "agent_id": agent_id
                        }
                        st.success("✅ 委托协议已签发!")
                        st.rerun()
                    else:
                        st.error(f"❌ 签发失败：{result.message}")
        else:
            # 显示当前委托状态
            delegation = st.session_state.active_delegation
            delegated_service = DelegatedPaymentService()

            cumulative = delegated_service.get_cumulative_amount(delegation["delegation_id"])
            remaining = delegation["max_total"] - cumulative

            st.markdown(f"""
            ### 📊 委托状态
            - **委托 ID**: `{delegation['delegation_id'][:40]}...`
            - **总额度**: ¥{delegation['max_total']:.2f}
            - **累计使用**: ¥{cumulative:.2f}
            - **剩余额度**: ¥{remaining:.2f}
            """
            )

            if remaining <= 0:
                st.warning("⚠️ 额度已用完，请创建新的委托协议")
            else:
                st.success("✅ 委托协议有效中")

        st.markdown("---")

        # 执行委托支付
        st.subheader("💰 使用委托支付")

        if st.session_state.active_delegation:
            # 显示商品列表
            products_result = merchant_service.get_product_list()

            if products_result["success"] and products_result["data"]:
                selected_product = st.selectbox(
                    "选择要购买的商品:",
                    options=products_result["data"],
                    format_func=lambda x: f"{x['name']} - ¥{x['price']:.2f}",
                    help="选择使用委托支付的商品"
                )

                remaining = st.session_state.active_delegation["max_total"] - \
                            delegated_service.get_cumulative_amount(st.session_state.active_delegation["delegation_id"])

                if selected_product["price"] > remaining:
                    st.error(f"❌ 商品价格 ¥{selected_product['price']:.2f} 超过剩余额度 ¥{remaining:.2f}")
                elif selected_product["price"] > st.session_state.active_delegation["max_single"]:
                    st.warning(f"⚠️ 商品价格 ¥{selected_product['price']:.2f} 超过单笔上限 ¥{st.session_state.active_delegation['max_single']:.2f}")
                elif st.button("使用委托购买", type="primary", use_container_width=True):
                    with st.spinner("执行委托支付中..."):
                        # 创建订单
                        order_result = merchant_service.create_order(
                            item_id=selected_product["item_id"],
                            quantity=1
                        )

                        if order_result["success"]:
                            # 使用委托支付
                            delegated_service = DelegatedPaymentService()
                            pay_result = delegated_service.pay(
                                DelegationPayRequest(
                                    request_id=str(uuid.uuid4()),
                                    buyer_agent_id=st.session_state.active_delegation.get("agent_id", "did:act:assistant-001"),
                                    delegation_id=st.session_state.active_delegation["delegation_id"],
                                    iac=st.session_state.active_delegation["iac"],
                                    merchant_id="did:act:merchant-example",
                                    merchant_order_id=order_result["data"]["order_id"],
                                    cart_snapshot_hash="hash_snapshot_001",
                                    amount=order_result["data"]["total_amount"]
                                )
                            )
                            result = pay_result

                            if result.status == "COMPLETED":
                                st.success("✅ **委托支付成功**!")
                                st.info("""
                                **委托支付完成**：
                                - 智能体基于 IAC 发起支付
                                - PSP 核验 IAC 有效性
                                - 执行扣款
                                - 无需用户实时介入
                                """)
                                st.rerun()
                            else:
                                st.error(f"❌ 支付失败：{result.message}")
        else:
            st.warning("请先创建委托协议")

    with right_col:
        st.markdown("### 🔄 流程图")

        st.markdown("""
        ```
        用户 -> 智能体：授权代买
         |
         v
        智能体 -> PSP：签发 IAC -> 设定额度
         |
         v
        [IAC 签发完成]
         |
         v
        智能体 -> 商户：自主下单
         |
         v
        智能体 -> PSP：基于 IAC 发起支付
         |
         v
        PSP -> 智能体：核验 IAC -> 扣款成功
        ```
        """)

        st.markdown("---")

        st.markdown("### 🔐 协议组件")

        st.markdown("""
        - `ADD-INT-EAC`：获取委托意图
        - `ADD-INT-ISR`：结构化表达 (delegation_mode)
        - `ADD-IAC-ISS`：签发 IAC 凭证
        - `ADD-IAC-LCM`：IAC 生命周期管理
        - `PSD-PAY-DEL`：委托支付流程
        """)


def render_autonomous_payment_demo():
    """渲染自主支付 (A2A) 演示界面"""
    st.markdown('<div class="sub-header">🤖 场景：用户设定任务边界，智能体自主决策执行</div>', unsafe_allow_html=True)

    left_col, right_col = st.columns([2, 1])

    with left_col:
        st.subheader("🎯 任务规划")

        if "autonomous_task" not in st.session_state:
            # 创建自主支付任务
            st.markdown("### 📋 创建新任务")

            with st.form("create_autonomous_task"):
                task_name = st.text_input(
                    "任务名称",
                    value="出差行程规划",
                    help="自主支付的任务描述"
                )

                total_budget = st.number_input(
                    "总预算",
                    min_value=0.0,
                    value=5000.0,
                    step=500.0,
                    format="%.2f"
                )

                category_scope = st.radio(
                    "品类范围",
                    options=["所有品类", "仅交通", "仅住宿", "仅餐饮"],
                    index=0
                )

                col1, col2 = st.columns(2)
                with col1:
                    agent_id = st.text_input(
                        "买方智能体 ID",
                        value="did:act:travel-agent-001",
                        help="负责任务执行的买方智能体"
                    )

                with col2:
                    sub_account = st.text_input(
                        "专属子账户",
                        value="did:act:subaccount:travel-001",
                        help="智能体独立子账户用于资金隔离"
                    )

                submitted = st.form_submit_button("创建任务", type="primary", use_container_width=True)

                if submitted:
                    st.session_state.autonomous_task = {
                        "name": task_name,
                        "budget": total_budget,
                        "category": category_scope,
                        "agent_id": agent_id,
                        "sub_account": sub_account,
                        "orders": []
                    }
                    st.success("✅ 任务创建成功!")
                    st.rerun()
        else:
            # 显示任务状态
            task = st.session_state.autonomous_task

            # 子账户充值
            if "sub_account_balance" not in st.session_state:
                st.session_state.sub_account_balance = task["budget"]

            st.markdown(f"""
            ### 📊 任务状态
            - **任务**: {task['name']}
            - **总预算**: ¥{task['budget']:.2f}
            - **子账户余额**: ¥{st.session_state.sub_account_balance:.2f}
            - **已消耗**: ¥{task['budget'] - st.session_state.sub_account_balance:.2f}
            - **状态**: `运行中`
            """
            )

            # 子账户控制面板
            st.markdown("---")
            st.subheader("💰 子账户管理")

            col1, col2 = st.columns(2)
            with col1:
                if st.button("充值", use_container_width=True):
                    recharge_amount = st.text_input("充值金额", value="1000.0")
                    if float(recharge_amount) > 0:
                        st.session_state.sub_account_balance += float(recharge_amount)
                        task["budget"] += float(recharge_amount)
                        st.success("充值成功!")
                        st.rerun()

            with col2:
                if st.button("查询余额", use_container_width=True):
                    st.write(f"**当前余额**: ¥{st.session_state.sub_account_balance:.2f}")

            # 自主执行
            st.markdown("---")
            st.subheader("🤖 自主执行")

            if st.button("▶ 开始执行", type="primary", use_container_width=True):
                with st.spinner("智能体自主执行任务中..."):
                    time.sleep(1)  # 模拟执行

                    # 模拟 A2A 交易
                    product = {
                        "name": "机票预订",
                        "price": 1500.0
                    }

                    # 创建订单并扣款
                    new_balance = st.session_state.sub_account_balance - product["price"]

                    if new_balance >= 0:
                        st.session_state.sub_account_balance = new_balance

                        task["orders"].append({
                            "name": product["name"],
                            "price": product["price"],
                            "counter_agent": "did:act:flight-service-001",
                            "payment_method": "A2A"
                        })

                        st.success(f"✅ 完成 [{product['name']}] - ¥{product['price']:.2f}")
                        st.rerun()

            # 显示订单历史
            if task["orders"]:
                st.markdown("---")
                st.subheader("📦 订单记录")

                for order in task["orders"]:
                    st.markdown(f"""
                    - **{order['name']}**
                      - 卖方智能体：`{order['counter_agent']}`
                      - 支付：`{order['payment_method']}`
                      - 金额：¥{order['price']:.2f}
                    """)

    with right_col:
        st.markdown("### 🔄 自主支付流程")

        st.markdown("""
        ```
        用户 -> 买方智能体：设定任务边界
         |
         v
        买方智能体 -> PSP：开立子账户 -> 充值
         |
         v
        [子账户就绪]
         |
         v
        买方智能体 -> 卖方智能体：服务发现
         |
         v
        卖方智能体 -> 买方智能体：HTTP 402 支付诉求
         |
         v
        买方智能体 -> PSP：A2A 支付 (子账户密钥签名)
         |
         v
        PSP -> 买方智能体：支付凭证传递
         |
         v
        买方智能体 -> 卖方智能体：资源访问授权
        ```
        """)

        st.markdown("---")

        st.markdown("### 🔐 协议组件")

        st.markdown("""
        - `ADD-INT-EAC`：获取任务边界
        - `ADD-INT-ISR`：结构化表达 (delegation_mode: BOUNDED)
        - `PSD-AGT-SUB`：智能体子账户
        - `CID-PCA-NEG`：支付能力协商
        - `PSD-PAY-A2A`：A2A 支付流程
        """)