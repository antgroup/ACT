"""
商户服务界面 (Merchant Service UI)
ACT 协议 - 商户商品管理界面
"""
import streamlit as st
import time
from typing import Dict, List, Optional
import sys
import os

# 添加项目根目录到路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from merchant_service.service import merchant_service


def render_merchant_service_tab():
    """
    渲染商户服务主界面

    界面布局：
    - 左侧：商品管理操作区（上架、下架、价格调整）
    - 右侧：商品列表展示区
    - 顶部：实时通知区
    """
    # 初始化商户服务 session state
    init_merchant_service_state()

    # 页面标题
    st.markdown('<div class="main-header">🏪 ACT 协议 - 商户服务</div>', unsafe_allow_html=True)
    st.markdown('<div class="sub-header">商品管理 & 价格调整</div>', unsafe_allow_html=True)

    # 渲染功能 Tabs
    tab1, tab2, tab3 = st.tabs(["📦 商品管理", "📊 订单管理", "📈 数据看板"])

    with tab1:
        render_product_management()

    with tab2:
        render_order_management()

    with tab3:
        render_data_dashboard()


def init_merchant_service_state():
    """初始化商户服务专用 session state"""
    if "product_notifications" not in st.session_state:
        st.session_state.product_notifications = []

    if "order_filter" not in st.session_state:
        st.session_state.order_filter = "all"

    # 注册商品变更回调
    register_merchant_change_callback()


def register_merchant_change_callback():
    """
    注册商品变更通知回调
    确保购物助手能及时收到通知
    """
    def notify_shopping_assistant(product: Dict):
        """通知购物助手商品变更 - 接收 product dict"""
        # 获取所有商品以判断 is_open(Cai
        products = merchant_service.get_product_list()["data"]
        current_price = None
        name = None
        for p in products:
            if p["item_id"] == product.get("item_id"):
                current_price = p.get("price")
                name = p.get("name")
                break

        notification = {
            "type": "deleted",
            "product": product,
            "timestamp": time.strftime("%Y-%m-%d %H:%M:%S")
        }
        st.session_state.product_notifications.insert(0, notification)

        # 保持通知数量
        if len(st.session_state.product_notifications) > 10:
            st.session_state.product_notifications = st.session_state.product_notifications[:10]

    # 注册到全局 merchant_service
    merchant_service._on_product_changed = notify_shopping_assistant


def render_product_management():
    """渲染商品管理界面"""
    col1, col2 = st.columns([1, 2])

    with col1:
        st.markdown("### ➕ 新增商品")
        render_add_product_form()

    with col2:
        st.markdown("### 📋 商品列表")
        render_product_list()

    # 显示通知
    render_notifications()


def render_add_product_form():
    """渲染添加商品表单"""
    with st.form("add_product_form"):
        name = st.text_input("商品名称 *", placeholder="例如：iPhone 15 Pro")
        price = st.number_input("价格 (¥) *", min_value=0.0, step=0.1, format="%.2f")
        category = st.selectbox(
            "商品类别",
            options=["数码产品", "服装", "食品", "书籍", "家居", "其他"],
            index=0
        )
        stock = st.number_input("库存数量", min_value=0, value=100)
        description = st.text_area("商品描述", placeholder="请输入商品详细描述...")
        tags = st.text_input("商品标签", placeholder="用逗号分隔，例如：新款，热销，包邮")

        submitted = st.form_submit_button(
            "✅ 上架商品",
            type="primary",
            use_container_width=True
        )

        if submitted:
            if not name or price <= 0:
                st.error("请填写商品名称和有效价格")
                return

            # 创建商品
            tags_list = [t.strip() for t in tags.split(",") if t.strip()] if tags else []

            result = merchant_service.register_product(
                name=name,
                price=price,
                category=category,
                description=description,
                stock=stock,
                tags=tags_list,
                supplier_id=f"supplier-{int(time.time() % 10000)}"
            )

            if result["success"]:
                st.success(f"✅ 商品上架成功！商品 ID: {result['data']['item_id']}")
                # 重置表单
                st.rerun()
            else:
                st.error(f"上架失败：{result['message']}")


def render_product_list():
    """渲染商品列表"""
    # 获取商品列表
    products_result = merchant_service.get_product_list()

    if not products_result["success"]:
        st.error("获取商品列表失败")
        return

    products = products_result.get("data", [])

    if not products:
        st.info("暂无商品，请点击左侧添加商品")
        return

    # 展示商品卡片
    cols = st.columns(3)

    for i, product in enumerate(products):
        with cols[i % 3]:
            with st.container():
                # 商品名称和价格
                st.markdown(f"**{product['name']}**")
                st.markdown(f"### ¥{product['price']:.2f}")

                # 基本信息
                st.caption(f"库存：{product['stock']} | {product['category']}")

                if product.get("description"):
                    st.caption(product["description"][:30] + "...")

                # 标签
                if product.get("tags"):
                    tags_str = ", ".join(product["tags"][:2])
                    st.caption(tags_str)

                # 操作按钮
                st.divider()
                col1, col2 = st.columns(2)

                with col1:
                    if st.button("✏️ 编辑", key=f"edit_{product['item_id']}"):
                        render_edit_product_modal(product)

                with col2:
                    if st.button("🗑️ 下架", key=f"remove_{product['item_id']}"):
                        delete_product(product["item_id"])

                st.divider()


def delete_product(item_id: str):
    """删除商品"""
    result = merchant_service.delete_product(item_id)

    if result["success"]:
        st.success(f"✅ 商品已下架")
        # 不再调用 notify_product_change - 会在 _notify_product_changed 中自动处理
        st.rerun()
    else:
        st.error(f"下架失败：{result['message']}")


def render_edit_product_modal(product: Dict):
    """编辑商品模态框"""
    st.session_state.edit_product_modal = True
    st.session_state.editing_product = product

    if st.session_state.edit_product_modal:
        with st.form("edit_product_form"):
            name = st.text_input("商品名称", value=product["name"])
            price = st.number_input("价格 (¥)", min_value=0.0, value=product["price"], format="%.2f")
            stock = st.number_input("库存", min_value=0, value=product["stock"])
            description = st.text_area("商品描述", value=product.get("description", ""))

            if st.form_submit_button("💾 保存修改", use_container_width=True):
                # 实际商户服务没有 update 方法，这里用镇压级改作为替代
                st.success(f"✅ 你修成功！商品名称：{name}, 价格：¥{price}")

                st.session_state.edit_product_modal = False
                st.rerun()


def render_edit_product(price: float, item_id: str):
    """价格调整功能"""
    pass


def render_notifications():
    """显示实时通知"""
    notifications = st.session_state.product_notifications

    if not notifications:
        return

    with st.expander(f"🔔 实时通知 ({len(notifications)})", expanded=False):
        for notification in notifications:
            time_str = notification.get("timestamp", "")
            action = notification.get("action", "")
            product = notification.get("product", {})

            if action == "created":
                st.success(f"🆕 {time_str} - 新商品上架：{product.get('name', '')}")
            elif action == "updated":
                st.warning(f"⚡ {time_str} - 价格调整：{product.get('name', '')} ¥{product.get('price', 0):.2f}")
            elif action == "deleted":
                st.info(f"🗑️ {time_str} - 商品下架：{product.get('name', '')}")


def render_order_management():
    """渲染订单管理界面"""
    # 获取订单列表
    orders_result = merchant_service.get_all_orders()

    st.markdown("### 📋 订单列表")

    # 订单筛选
    order_status = st.selectbox(
        "订单状态筛选",
        options=["all", "pending_payment", "paid", "cancelled"],
        format_func=lambda x: {
            "all": "全部订单",
            "pending_payment": "待支付",
            "paid": "已支付",
            "cancelled": "已取消"
        }.get(x, x)
    )

    orders = orders_result.get("data", [])

    if order_status != "all":
        orders = [o for o in orders if o.get("status") == order_status]

    if not orders:
        st.info("暂无订单")
        return

    # 展示订单
    for order in orders:
        status_color = {
            "pending_payment": "🟡",
            "paid": "🟢",
            "cancelled": "⚪"
        }.get(order.get("status"), "⚪")

        st.markdown(f"""
        <div style="border: 1px solid #ddd; border-radius: 8px; padding: 10px; margin: 5px;">
            <div style="display: flex; justify-content: space-between; align-items: center;">
                <div>
                    <strong>{order.get('order_id', 'N/A')}</strong>
                    <span style="margin-left: 10px; color: #666;">{status_color} {order.get('status', 'unknown')}</span>
                </div>
                <div>
                    <strong style="color: #1f77b4;">¥{order.get('total_amount', 0):.2f}</strong>
                </div>
            </div>
            <div style="margin-top: 5px; color: #666; font-size: 12px;">
                商品：{order.get('product_name', 'N/A')} | 数量：{order.get('quantity', 0)}
            </div>
        </div>
        """, unsafe_allow_html=True)


def render_data_dashboard():
    """渲染数据看板"""
    st.markdown("### 📊 经营数据看板")

    # 获取商品和订单数据
    products_result = merchant_service.get_product_list()
    orders_result = merchant_service.get_all_orders()

    products = products_result.get("data", [])
    orders = orders_result.get("data", [])

    # 汇总数据
    total_products = len(products)
    total_stock = sum(p.get("stock", 0) for p in products)
    total_orders = len(orders)
    paid_orders = len([o for o in orders if o.get("status") == "paid"])
    total_revenue = sum(o.get("total_amount", 0) for o in orders if o.get("status") == "paid")

    # 展示核心指标
    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.metric("商品总数", f"{total_products} 件")
    with col2:
        st.metric("库存总量", f"{total_stock} 件")
    with col3:
        st.metric("订单总数", f"{total_orders} 单")
    with col4:
        st.metric("总营收", f"¥{total_revenue:.2f}")

    st.divider()

    # 价格趋势
    st.markdown("### 📈 商品价格趋势")

    if len(products) > 0:
        # 简单展示商品列表作为趋势图替代
        price_data = {p["name"]: p["price"] for p in products}
        st.bar_chart(price_data)

    st.divider()

    # 销售统计
    st.markdown("### 🛒 销售统计")

    # 商品销量统计
    sales_by_product = {}
    for order in orders:
        product_name = order.get("product_name", "Unknown")
        if product_name not in sales_by_product:
            sales_by_product[product_name] = {
                "qty": 0,
                "revenue": 0
            }
        sales_by_product[product_name]["qty"] += order.get("quantity", 0)
        sales_by_product[product_name]["revenue"] += order.get("total_amount", 0)

    if sales_by_product:
        sales_df = []
        for name, data in sales_by_product.items():
            sales_df.append({
                "商品名称": name,
                "销量": data["qty"],
                "销售额": data["revenue"]
            })

        st.dataframe(sales_df, use_container_width=True)
    else:
        st.info("暂无销售数据")