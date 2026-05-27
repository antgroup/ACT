"""
ACT 协议 - GPT对话式支付演示
Chat-based Demo for ACT Protocol Payment Methods

核心设计理念：
1. 所有交互通过自然语言对话完成
2. 智能体根据用户意图自动判断使用哪种支付模式
3. 三种支付模式的流程和差异通过对话清晰展示
4. 用户和商户角色切换时，商品和订单数据保持同步
"""

import streamlit as st
import json
import os
import time
import uuid
from typing import Dict, Any, List, Optional
from datetime import datetime
from dataclasses import dataclass, asdict

# 数据持久化 - 使用JSON文件存储，确保用户和商户数据同步
DATA_FILE = os.path.join(os.path.dirname(__file__), "demo_data.json")


def load_demo_data() -> Dict[str, Any]:
    """加载演示数据"""
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    return {
        "products": [
            {"id": "p1", "name": "iPhone 15 Pro", "price": 8999.0, "stock": 10, "merchant_id": "m1"},
            {"id": "p2", "name": "MacBook Pro M3", "price": 14999.0, "stock": 5, "merchant_id": "m1"},
            {"id": "p3", "name": "AirPods Pro 2", "price": 1899.0, "stock": 20, "merchant_id": "m1"},
            {"id": "p4", "name": "星巴克大杯拿铁", "price": 38.0, "stock": 100, "merchant_id": "m2"},
            {"id": "p5", "name": "奈雪的茶", "price": 32.0, "stock": 50, "merchant_id": "m2"},
        ],
        "orders": [],
        "delegations": [],
        "sub_accounts": {},
        "notifications": []
    }


def save_demo_data(data: Dict[str, Any]):
    """保存演示数据"""
    with open(DATA_FILE, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


@dataclass
class ChatMessage:
    """聊天消息"""
    role: str  # "user", "assistant", "system"
    content: str
    timestamp: str = ""
    metadata: Dict[str, Any] = None

    def __post_init__(self):
        if not self.timestamp:
            self.timestamp = datetime.now().strftime("%H:%M:%S")
        if self.metadata is None:
            self.metadata = {}


class ACTChatAgent:
    """
    ACT协议智能对话Agent
    支持三种支付模式的识别和执行
    """

    def __init__(self, user_id: str, role: str):
        self.user_id = user_id
        self.role = role  # "user" 或 "merchant"
        self.data = load_demo_data()
        self.current_mode = None  # 当前支付模式
        self.pending_action = None  # 待确认的操作

    def get_user_name(self) -> str:
        """获取用户显示名称"""
        return "用户" if self.role == "user" else "商户管理员"

    def process_message(self, message: str) -> ChatMessage:
        """
        处理用户消息，根据意图路由到不同的支付模式处理
        """
        msg_lower = message.lower().strip()

        # 帮助指令
        if any(kw in msg_lower for kw in ["帮助", "help", "怎么用", "说明"]):
            return self._handle_help()

        # 商户相关指令
        if self.role == "merchant":
            return self._handle_merchant_commands(message)

        # 用户相关指令 - 支付模式识别

        # 1. 自主支付 (A2A) - 复杂任务委托
        if any(kw in msg_lower for kw in ["帮我安排", "帮我规划", "帮我预订", "出差", "旅游", "整体方案"]):
            return self._handle_autonomous_payment_intent(message)

        # 2. 委托支付 - 定向授权（预先授权，后续自动执行）
        if any(kw in msg_lower for kw in ["授权", "委托", "自动续费", "每月帮我", "定期帮我", "设置iac", "开通委托"]):
            return self._handle_delegated_payment_intent(message)

        # 3. 即时支付 - 立即购买（用户实时在场）
        if any(kw in msg_lower for kw in ["买", "购买", "现在买", "立即买", "下单", "支付", "结算"]):
            return self._handle_instant_payment_intent(message)

        # 查询类指令
        if any(kw in msg_lower for kw in ["订单", "我的订单", "购买记录"]):
            return self._handle_view_orders()

        if any(kw in msg_lower for kw in ["商品", "有什么", "列表", "看看商品"]):
            return self._handle_view_products()

        if any(kw in msg_lower for kw in ["委托状态", "iac状态", "授权状态", "额度"]):
            return self._handle_view_delegations()

        # 默认对话
        return self._handle_default_chat(message)

    def _handle_help(self) -> ChatMessage:
        """显示帮助信息，说明三种支付模式的区别"""
        content = """
嗨！我是您的ACT协议智能购物助手 🤖

我可以帮您完成以下三种支付模式：

---

## 💸 **1. 即时支付 (Instant Payment)**
**适用场景**：您在线，想立即购买
**对话示例**：
- "帮我买一杯星巴克大杯拿铁"
- "现在购买iPhone 15 Pro"
**特点**：
- 您实时确认支付
- 无需预先授权
- 收银台确认即完成授权

---

## 💼 **2. 委托支付 (Delegated Payment)**
**适用场景**：预先授权，后续自动执行
**对话示例**：
- "帮我授权每月自动续费中国移动套餐，不超过100元"
- "设置IAC委托：每天自动购买咖啡，额度200元"
- "开通委托：帮我代购某本书，额度150元"
**特点**：
- 签发IAC授权凭证
- 智能体在额度内代您支付
- 您可以随时查询状态和剩余额度

---

## 🤖 **3. 自主支付 / A2A支付 (Autonomous Payment)**
**适用场景**：复杂任务，需要智能体自主决策
**对话示例**：
- "帮我安排下周出差上海，预算5000元"
- "帮我规划一个3天2晚的杭州旅游，预算3000元"
- "预订明天飞北京的机票和酒店，预算控制在1200元"
**特点**：
- 智能体自动拆解子任务（机票、酒店、用车等）
- A2A（智能体对智能体）直接交易
- 使用专属子账户，资金隔离
- 全程无需您逐笔确认

---

您想体验哪种支付模式呢？可以直接告诉我您的需求！
        """.strip()
        return ChatMessage(role="assistant", content=content)

    def _handle_instant_payment_intent(self, message: str) -> ChatMessage:
        """处理即时支付意图"""
        # 解析商品
        product = self._parse_product_from_message(message)

        if not product:
            products_list = "\n".join([f"- {p['name']}: ¥{p['price']}" for p in self.data["products"]])
            return ChatMessage(
                role="assistant",
                content=f"我没有找到您想要的商品。当前可购买的商品有：\n\n{products_list}\n\n请告诉我具体想买什么？"
            )

        if product["stock"] <= 0:
            return ChatMessage(
                role="assistant",
                content=f"抱歉，**{product['name']}** 暂时缺货。您可以看看其他商品，或者联系商户补货。"
            )

        self.pending_action = {
            "type": "instant_payment",
            "product_id": product["id"],
            "product_name": product["name"],
            "amount": product["price"]
        }

        content = f"""
💸 **即时支付确认**

我理解了您的购买意图：
- 商品：**{product['name']}**
- 价格：¥{product['price']}
- 模式：**即时支付** (PSD-PAY-INS)

**流程说明**：
1. ✅ 解析购买意图 (ADD-INT-EAC)
2. ✅ 获取商品信息 (CID-MER-CAT)
3. ⏳ 等待您确认支付
4. ⏳ 唤起收银台
5. ⏳ 您实时确认完成支付

**关键特征**：
- 您**全程在场**实时确认
- 无需签发IAC
- 使用已绑定的支付标记

请回复"**确认支付**"或"**取消**"：
        """.strip()

        return ChatMessage(role="assistant", content=content, metadata={"protocol": "PSD-PAY-INS"})

    def _handle_delegated_payment_intent(self, message: str) -> ChatMessage:
        """处理委托支付意图 (定向委托)"""
        # 解析额度和商品
        amount = self._parse_amount_from_message(message)

        if not amount or amount <= 0:
            amount = 500.0  # 默认额度

        delegation_id = f"did:act:delegation:{uuid.uuid4().hex[:16]}"

        self.pending_action = {
            "type": "delegated_payment_setup",
            "delegation_id": delegation_id,
            "max_total": amount,
            "max_single": amount / 5  # 单笔为总额的1/5
        }

        content = f"""
💼 **委托支付授权设置**

我理解了您的委托意图，准备为您签发IAC授权凭证。

**拟定的授权参数**：
- 委托ID：`{delegation_id}`
- 总额度上限：**¥{amount:.2f}**
- 单笔上限：**¥{amount/5:.2f}**
- 模式：**定向委托支付** (delegation_mode: SPECIFIED)

**流程说明**：
1. ⏳ 您确认签发IAC
2. ⏳ 生成IAC凭证 (ADD-IAC-ISS)
3. ⏳ 设置额度与限制
4. ✅ 后续智能体在授权内自动执行 (PSD-PAY-DEL)
5. ✅ 无需您实时介入

**关键特征**：
- 您**预先授权**，后续自动执行
- 签发IAC凭证作为授权依据
- 智能体在授权边界内程序化支付
- 支持累计额度管控

**涉及协议组件**：
- `ADD-INT-EAC` - 获取委托意图
- `ADD-IAC-ISS` - 签发IAC
- `PSD-PAY-DEL` - 委托支付流程

请回复"**签发委托**"或"**修改额度 [金额]**"或"**取消**"：
        """.strip()

        return ChatMessage(role="assistant", content=content, metadata={"protocol": "PSD-PAY-DEL"})

    def _handle_autonomous_payment_intent(self, message: str) -> ChatMessage:
        """处理自主支付/A2A支付意图"""
        # 解析预算
        budget = self._parse_amount_from_message(message)

        if not budget or budget <= 0:
            budget = 3000.0

        task_id = f"did:act:task:{uuid.uuid4().hex[:16]}"

        # 判断任务类型
        task_desc = self._parse_autonomous_task(message)

        self.pending_action = {
            "type": "autonomous_payment_setup",
            "task_id": task_id,
            "budget": budget,
            "description": task_desc
        }

        content = f"""
🤖 **自主支付 / A2A支付任务规划**

我理解了您的复杂任务需求，将为您创建A2A支付任务。

**任务规划**：
- 任务ID：`{task_id}`
- 任务描述：**{task_desc}**
- 总预算：**¥{budget:.2f}**
- 模式：**自主委托** (delegation_mode: BOUNDED + A2A支付)

**执行流程**：
1. ⏳ 您确认任务边界
2. ⏳ 为智能体开立专属子账户 (PSD-AGT-SUB)
3. ⏳ 子账户充值 ¥{budget:.2f}
4. ✅ 智能体自主拆解子任务（机票、酒店、用车等）
5. ✅ 智能体发现卖方智能体 (CID-PCA-NEG)
6. ✅ 卖方返回HTTP 402支付诉求
7. ✅ 买方智能体构造A2A支付载荷 (PSD-PAY-A2A)
8. ✅ PSP核验IAC与子账户密钥签名，完成扣款
9. ✅ 智能体携带支付凭证访问资源

**关键特征**：
- 智能体拥有**高度自主决策权**
- 智能体间**A2A直接交易**
- 使用**专属子账户**，资金隔离
- 基于HTTP 402语义扩展
- 全程**无需您逐笔确认**

**涉及协议组件**：
- `ADD-INT-EAC` - 获取任务边界
- `PSD-AGT-SUB` - 智能体子账户
- `CID-PCA-NEG` - 支付能力协商
- `PSD-PAY-A2A` - A2A支付流程

想开始模拟执行这个过程吗？回复"**确认创建任务**"或"**修改预算 [金额]**"或"**取消**"：
        """.strip()

        return ChatMessage(role="assistant", content=content, metadata={"protocol": "PSD-PAY-A2A"})

    def confirm_pending_action(self) -> ChatMessage:
        """执行待确认的操作"""
        if not self.pending_action:
            return ChatMessage(role="assistant", content="没有待确认的操作。")

        action_type = self.pending_action["type"]

        if action_type == "instant_payment":
            return self._execute_instant_payment()
        elif action_type == "delegated_payment_setup":
            return self._execute_delegated_setup()
        elif action_type == "delegated_payment_execute":
            return self._execute_delegated_payment()
        elif action_type == "autonomous_payment_setup":
            return self._execute_autonomous_setup()
        elif action_type == "autonomous_payment_execute":
            return self._execute_autonomous_payment()

        self.pending_action = None

    def _execute_instant_payment(self) -> ChatMessage:
        """执行即时支付"""
        action = self.pending_action
        self.pending_action = None

        product_id = action["product_id"]

        # 扣减库存
        for p in self.data["products"]:
            if p["id"] == product_id:
                p["stock"] -= 1
                break

        # 创建订单
        order = {
            "id": f"ORD-{uuid.uuid4().hex[:12]}",
            "user_id": self.user_id,
            "product_id": product_id,
            "product_name": action["product_name"],
            "amount": action["amount"],
            "payment_mode": "instant",
            "status": "completed",
            "timestamp": datetime.now().isoformat()
        }
        self.data["orders"].append(order)
        save_demo_data(self.data)

        return ChatMessage(
            role="assistant",
            content=f"""
✅ **即时支付成功！**

**支付详情**：
- 订单号：{order['id']}
- 商品：{action['product_name']}
- 金额：¥{action['amount']:.2f}
- 支付模式：**即时支付** (PSD-PAY-INS)
- 状态：已完成

**协议执行回顾**：
1. ✅ 获取并解析购买意图 (ADD-INT-EAC)
2. ✅ 结构化表达意图 (ADD-INT-ISR)
3. ✅ 获取商户商品目录 (CID-MER-CAT)
4. ✅ 购物车确认与规则自检 (CID-CART-CFM)
5. ✅ 使用已绑定的支付标记 (PSD-PMT-BND)
6. ✅ 即时支付流程完成 (PSD-PAY-INS)

**关键特征体现**：
✓ 用户全程在场实时确认
✓ 无需签发IAC，收银台确认即授权
✓ 单次即时交易

---
您还需要购买其他商品吗？或者想体验委托支付/自主支付模式？
            """.strip(),
            metadata={"payment_complete": True, "mode": "instant"}
        )

    def _execute_delegated_setup(self) -> ChatMessage:
        """执行委托支付设置"""
        action = self.pending_action
        self.pending_action = None

        # 保存委托
        delegation = {
            "id": action["delegation_id"],
            "user_id": self.user_id,
            "max_total": action["max_total"],
            "max_single": action["max_single"],
            "used_amount": 0.0,
            "status": "active",
            "created_at": datetime.now().isoformat(),
            "iac_jwt": self._generate_mock_iac(action)
        }
        self.data["delegations"].append(delegation)
        save_demo_data(self.data)

        return ChatMessage(
            role="assistant",
            content=f"""
✅ **IAC委托授权已签发！**

**委托凭证详情**：
- 委托ID：`{action['delegation_id']}`
- 总额度：**¥{action['max_total']:.2f}**
- 单笔上限：**¥{action['max_single']:.2f}**
- 当前已用：¥0.00
- 状态：**已激活**

**IAC凭证（模拟JWT）**：
```json
{self._generate_mock_iac(action, pretty=True)}
```

**协议执行回顾**：
1. ✅ 获取用户定向委托意图 (ADD-INT-EAC)
2. ✅ 结构化表达意图 (ADD-INT-ISR: delegation_mode=SPECIFIED)
3. ✅ 委托人核身确认
4. ✅ 签发IAC凭证 (ADD-IAC-ISS)
5. ✅ IAC生命周期管理启动 (ADD-IAC-LCM)

**接下来您可以**：
- 说"**使用委托购买 [商品名]**" - 智能体将基于IAC自动执行支付
- 说"**查询委托状态**" - 查看剩余额度和使用记录
- 说"**吊销委托**" - 取消授权

---
想试试用委托购买商品吗？例如："使用委托购买iPhone 15 Pro"
            """.strip(),
            metadata={"delegation_created": True, "mode": "delegated"}
        )

    def _execute_delegated_payment(self) -> ChatMessage:
        """使用委托执行支付"""
        action = self.pending_action
        self.pending_action = None

        delegation_id = action["delegation_id"]
        delegation = None

        for d in self.data["delegations"]:
            if d["id"] == delegation_id and d["status"] == "active":
                delegation = d
                break

        if not delegation:
            return ChatMessage(role="assistant", content="未找到有效的委托授权，请先创建委托。")

        # 检查额度
        remaining = delegation["max_total"] - delegation["used_amount"]
        if action["amount"] > remaining:
            return ChatMessage(
                role="assistant",
                content=f"❌ 委托额度不足！本次需要 ¥{action['amount']:.2f}，剩余额度 ¥{remaining:.2f}"
            )

        # 执行支付
        delegation["used_amount"] += action["amount"]

        # 创建订单
        order = {
            "id": f"ORD-{uuid.uuid4().hex[:12]}",
            "user_id": self.user_id,
            "product_id": action.get("product_id"),
            "product_name": action.get("product_name", "委托购买"),
            "amount": action["amount"],
            "payment_mode": "delegated",
            "delegation_id": delegation_id,
            "status": "completed",
            "timestamp": datetime.now().isoformat()
        }
        self.data["orders"].append(order)
        save_demo_data(self.data)

        return ChatMessage(
            role="assistant",
            content=f"""
✅ **委托支付成功！** (PSD-PAY-DEL)

**支付详情**：
- 订单号：{order['id']}
- 商品：{action.get('product_name', '委托购买')}
- 金额：¥{action['amount']:.2f}
- 支付方式：**IAC委托支付**
- 委托ID：`{delegation_id[:30]}...`
- 委托剩余额度：**¥{delegation['max_total'] - delegation['used_amount']:.2f}**

**协议执行流程**：
1. ✅ 意图上下文传递 (CID-INT-RUT)
2. ✅ 智能体完成购物车确认 (CID-CART-CFM)
3. ✅ 智能体基于IAC发起委托支付 (PSD-PAY-DEL)
4. ✅ PSP核验IAC有效性
5. ✅ 执行扣款

**关键特征体现**：
✓ 用户**无需实时在场**，智能体自主执行
✓ 基于预签发的IAC凭证授权
✓ 自动额度管控，防止超额
✓ 支持累计额度跟踪

---
委托授权仍有效，您可以说"**再帮我买 [商品]**"继续使用委托支付。
            """.strip(),
            metadata={"payment_complete": True, "mode": "delegated"}
        )

    def _execute_autonomous_setup(self) -> ChatMessage:
        """执行自主支付/A2A任务设置"""
        action = self.pending_action
        self.pending_action = None

        budget = action["budget"]
        task_id = action["task_id"]

        # 创建子账户
        sub_account_id = f"did:act:sub:{uuid.uuid4().hex[:12]}"

        # 保存任务和子账户
        task = {
            "id": task_id,
            "user_id": self.user_id,
            "description": action["description"],
            "budget": budget,
            "sub_account_id": sub_account_id,
            "sub_account_balance": budget,
            "status": "active",
            "sub_tasks": [],
            "created_at": datetime.now().isoformat()
        }

        self.data["sub_accounts"][sub_account_id] = {
            "balance": budget,
            "initial_budget": budget,
            "transactions": []
        }

        self.data["orders"].append({  # 作为任务记录
            "id": task_id,
            "type": "autonomous_task",
            "user_id": self.user_id,
            **task
        })
        save_demo_data(self.data)

        return ChatMessage(
            role="assistant",
            content=f"""
✅ **自主支付任务已创建！** (PSD-PAY-A2A)

**任务配置**：
- 任务ID：`{task_id}`
- 专属子账户：`{sub_account_id}`
- 子账户初始余额：**¥{budget:.2f}**
- 模式：**自主委托** + A2A支付

**IAC凭证（Bound模式）**：
```json
{{
  "delegation_id": "{task_id}",
  "delegation_mode": "BOUNDED",
  "max_total_amount": {budget},
  "allowed_categories": ["all"],
  "sub_account": "{sub_account_id}"
}}
```

**协议执行回顾**：
1. ✅ 获取复杂任务目标与约束边界 (ADD-INT-EAC)
2. ✅ 结构化表达意图 (ADD-INT-ISR: delegation_mode=BOUNDED)
3. ✅ 签发自主委托类型的IAC (ADD-IAC-ISS)
4. ✅ 为智能体开立专属子账户 (PSD-AGT-SUB)
5. ✅ 子账户充值完成

**接下来将自动执行**：
6. ⏳ 智能体自主拆解子任务
7. ⏳ 服务市场发现卖方智能体
8. ⏳ 与卖方智能体支付能力协商 (CID-PCA-NEG)
9. ⏳ 接收HTTP 402支付诉求
10. ⏳ A2A支付流程 (PSD-PAY-A2A)

想开始模拟执行这个过程吗？回复"**开始执行任务**"：
            """.strip(),
            metadata={"autonomous_task_created": True, "mode": "a2a"}
        )

    def simulate_autonomous_execution(self, task_id: str, step: str = "flight") -> ChatMessage:
        """模拟自主支付任务的A2A执行过程"""
        # 实际从任务记录中获取
        # 这里简化模拟

        steps = [
            ("🤖 买方智能体", "正在拆解任务为子任务：机票、酒店、用车..."),
            ("🔍 服务发现", "在A2A服务市场发现卖方智能体..."),
            ("💬 CID-PCA-NEG", "与机票服务智能体协商支付能力..."),
            ("📡 HTTP 402", "卖方智能体返回支付诉求：¥800 for 机票"),
            ("💰 A2A支付", "买方智能体提交A2A支付载荷至PSP"),
            ("🔐 PSP核验", "验证IAC有效性和子账户密钥签名..."),
            ("✅ 扣款成功", "从子账户扣款¥800，余额¥4200"),
            ("🎫 资源访问", "买方智能体携带支付凭证获取机票..."),
        ]

        progress = "\n".join([f"**{i+1}. {step[0]}**: {step[1]}" for i, step in enumerate(steps)])

        return ChatMessage(
            role="assistant",
            content=f"""
🤖 **A2A自主支付执行实录**

正在执行子任务 **机票预订**：

{progress}

**当前状态**：
- 子任务1（机票）：✅ 完成，支付¥800
- 子任务2（酒店）：⏳ 等待执行

**子账户余额**：
- 初始：¥5000.00
- 已用：¥800.00
- 剩余：**¥4200.00**

---
**A2A支付特征体现**：
✓ 智能体间直接交易 (Agent-to-Agent)
✓ HTTP 402语义扩展
✓ 专属子账户资金隔离
✓ 全程无用户逐笔介入

想继续执行酒店预订吗？回复"**继续执行**"
            """.strip(),
            metadata={"a2a_simulation": True}
        )

    def _handle_merchant_commands(self, message: str) -> ChatMessage:
        """处理商户相关指令"""
        msg_lower = message.lower()

        if any(kw in msg_lower for kw in ["上架", "添加商品", "新增商品"]):
            return ChatMessage(role="assistant", content="商户上架商品功能需要通过表单交互。请告诉我商品名称、价格和库存，格式：上架 [商品名] 价格 [金额] 库存 [数量]")

        if any(kw in msg_lower for kw in ["查看订单", "所有订单", "销售情况"]):
            return self._handle_merchant_view_orders()

        if any(kw in msg_lower for kw in ["通知用户", "推送", "公告"]):
            return ChatMessage(role="assistant", content="请输入要通知用户的内容，格式：通知 [内容]")

        return ChatMessage(role="assistant", content="商户管理功能开发中。可用指令：查看订单、上架商品、通知用户")

    def _handle_view_orders(self) -> ChatMessage:
        """查看用户订单"""
        user_orders = [o for o in self.data["orders"] if o.get("user_id") == self.user_id and o.get("type") != "autonomous_task"]

        if not user_orders:
            return ChatMessage(role="assistant", content="您还没有订单记录。")

        orders_text = "\n".join([
            f"- **{o['product_name']}** | ¥{o['amount']:.2f} | {o['payment_mode']} | {o['status']}"
            for o in user_orders[-10:]  # 最近10条
        ])

        return ChatMessage(role="assistant", content=f"**您的订单记录**（最近10条）：\n\n{orders_text}")

    def _handle_view_products(self) -> ChatMessage:
        """查看商品列表"""
        products = self.data["products"]

        product_list = "\n".join([
            f"- **{p['name']}** | ¥{p['price']:.2f} | 库存: {p['stock']}"
            for p in products
        ])

        return ChatMessage(role="assistant", content=f"**当前可购买的商品**：\n\n{product_list}\n\n想买什么直接告诉我，例如：\"买iPhone 15 Pro\"")

    def _handle_view_delegations(self) -> ChatMessage:
        """查看委托状态"""
        user_delegations = [d for d in self.data["delegations"] if d.get("user_id") == self.user_id and d.get("status") == "active"]

        if not user_delegations:
            return ChatMessage(role="assistant", content="您没有正在生效的委托授权。\n\n可以对我说：\"帮我授权每月买咖啡，额度500元\" 来创建委托。")

        delegation = user_delegations[-1]  # 最新的
        remaining = delegation["max_total"] - delegation["used_amount"]

        return ChatMessage(
            role="assistant",
            content=f"""
**您的IAC委托状态**：

- 委托ID：`{delegation['id'][:40]}...`
- 总额度：¥{delegation['max_total']:.2f}
- 已使用：¥{delegation['used_amount']:.2f}
- **剩余额度：¥{remaining:.2f}**
- 状态：{delegation['status']}

可以使用委托购买商品，智能体将自动在授权额度内完成支付。
            """.strip()
        )

    def _handle_merchant_view_orders(self) -> ChatMessage:
        """商户查看所有订单"""
        all_orders = self.data["orders"]

        if not all_orders:
            return ChatMessage(role="assistant", content="暂无订单。")

        orders_text = "\n".join([
            f"- {o.get('product_name')} | ¥{o['amount']:.2f} | {o['payment_mode']} | {o.get('timestamp', 'N/A')[:10]}"
            for o in all_orders[-10:]
        ])

        return ChatMessage(role="assistant", content=f"**所有订单**（最近10条）：\n\n{orders_text}")

    def _handle_default_chat(self, message: str) -> ChatMessage:
        """默认对话回复"""
        return ChatMessage(
            role="assistant",
            content=f"嗨！我是您的ACT协议智能助手。\n\n我可以帮您：\n\n**作为用户**：\n- 💸 即时购买商品（您在场确认支付）\n- 💼 设置委托授权（预授权后智能体自动执行）\n- 🤖 创建自动化任务（A2A支付，智能体自主决策）\n\n**作为商户**：\n- 📦 管理商品上架\n- 📋 查看订单情况\n- 📢 向用户推送通知\n\n不知道怎么做？输入\"帮助\"查看详细说明！"
        )

    # ----- 工具方法 -----

    def _parse_product_from_message(self, message: str) -> Optional[Dict]:
        """从消息中解析商品"""
        for p in self.data["products"]:
            if p["name"].lower() in message.lower():
                return p
        return None

    def _parse_amount_from_message(self, message: str) -> Optional[float]:
        """从消息中解析金额"""
        import re
        # 匹配数字+元/块/¥/￥
        match = re.search(r'(\d+(?:\.\d+)?)\s*(?:元|块|¥|￥)', message)
        if match:
            return float(match.group(1))

        # 匹配纯数字（超过10的数字才认为是金额）
        match = re.search(r'(\d{3,})', message)
        if match:
            return float(match.group(1))

        return None

    def _parse_autonomous_task(self, message: str) -> str:
        """解析自主任务描述"""
        # 简单返回描述性文本
        if "出差" in message:
            return "出差行程安排（机票+酒店+用车）"
        if "旅游" in message:
            return "旅游行程规划（交通+住宿+门票+餐饮）"
        if "订" in message and ("机票" in message or "酒店" in message):
            return "出行预订（机票+酒店）"
        return "综合性任务执行"

    def _generate_mock_iac(self, action: Dict, pretty: bool = False) -> str:
        """生成模拟的IAC JWT"""
        iac_data = {
            "header": {
                "alg": "ES256",
                "typ": "IAC",
                "kid": "did:act:psp:example#key1"
            },
            "payload": {
                "iat": int(time.time()),
                "exp": int(time.time()) + 30 * 24 * 3600,
                "iss": "did:act:psp:example",
                "sub": action.get("delegation_id"),
                "principal": "did:act:user:example",
                "agent": "did:act:agent:example",
                "max_total_amount": action.get("max_total"),
                "max_single_amount": action.get("max_single"),
                "delegation_mode": "SPECIFIED" if action.get("type") == "delegated_payment_setup" else "BOUNDED"
            }
        }

        if pretty:
            return json.dumps(iac_data, ensure_ascii=False, indent=2)

        return json.dumps(iac_data, ensure_ascii=False)


# ==================== Streamlit UI ====================

def init_session_state():
    """初始化Session State"""
    if "chat_messages" not in st.session_state:
        st.session_state.chat_messages = []

    if "current_role" not in st.session_state:
        st.session_state.current_role = None

    if "agent" not in st.session_state:
        st.session_state.agent = None

    if "user_id" not in st.session_state:
        st.session_state.user_id = f"user_{uuid.uuid4().hex[:8]}"

    # 加载持久化数据
    data = load_demo_data()
    if "products" not in st.session_state:
        st.session_state.products = data.get("products", [])
    if "orders" not in st.session_state:
        st.session_state.orders = data.get("orders", [])


def render_chat_based_demo():
    """
    渲染基于对话的ACT协议演示
    """
    init_session_state()

    st.set_page_config(
        page_title="ACT协议 - GPT对话式演示",
        page_icon="🤖",
        layout="wide",
        initial_sidebar_state="expanded"
    )

    # 自定义样式
    st.markdown("""
    <style>
    .main-header {
        font-size: 2.5rem;
        font-weight: bold;
        color: #1f77b4;
        text-align: center;
        margin-bottom: 0.5rem;
    }
    .protocol-badge {
        display: inline-block;
        padding: 0.2rem 0.6rem;
        border-radius: 1rem;
        font-size: 0.8rem;
        font-weight: 500;
        margin-left: 0.5rem;
    }
    .instant-badge { background-color: #e3f2fd; color: #1976d2; }
    .delegated-badge { background-color: #fef3e2; color: #f57c00; }
    .a2a-badge { background-color: #e8f5e9; color: #388e3c; }
    .chat-container {
        max-width: 900px;
        margin: 0 auto;
    }
    </style>
    """, unsafe_allow_html=True)

    # 顶部标题
    st.markdown('<div class="main-header">ACT协议 - GPT对话式演示</div>', unsafe_allow_html=True)
    st.markdown('<div style="text-align: center; color: #666; margin-bottom: 1rem;">三种支付模式：即时支付 <span class="protocol-badge instant-badge">PSD-PAY-INS</span> | 委托支付 <span class="protocol-badge delegated-badge">PSD-PAY-DEL</span> | 自主支付 <span class="protocol-badge a2a-badge">PSD-PAY-A2A</span></div>', unsafe_allow_html=True)

    # 角色选择
    if st.session_state.current_role is None:
        render_role_selection()
        return

    # 主界面
    col1, col2 = st.columns([4, 1])

    with col2:
        render_sidebar()

    with col1:
        render_chat_interface()


def render_role_selection():
    """渲染角色选择界面"""
    st.markdown("---")
    st.subheader("👤 请选择您的角色")

    col1, col2 = st.columns(2)

    with col1:
        st.markdown("""
        <div style="padding: 2rem; border: 2px solid #e3f2fd; border-radius: 1rem; text-align: center; background-color: #f8fbff;">
            <div style="font-size: 3rem; margin-bottom: 1rem;">🛒</div>
            <h3>我是用户</h3>
            <p style="color: #666;">体验ACT协议的三种支付模式：<br>即时支付、委托支付、自主A2A支付</p>
        </div>
        """, unsafe_allow_html=True)
        if st.button("选择用户角色", type="primary", use_container_width=True):
            st.session_state.current_role = "user"
            st.session_state.agent = ACTChatAgent(
                st.session_state.user_id,
                "user"
            )
            # 添加欢迎消息
            welcome_msg = ChatMessage(
                role="assistant",
                content="嗨！我是您的ACT协议智能购物助手 🤖\n\n我可以帮您体验三种不同的支付模式：\n\n1. 💸 **即时支付** - 您在场，实时确认购买\n2. 💼 **委托支付** - 预先授权，智能体代您支付\n3. 🤖 **自主支付** - 复杂任务，智能体A2A自主决策\n\n输入\"帮助\"查看详细说明，或直接告诉我您想做什么！"
            )
            st.session_state.chat_messages.append(welcome_msg)
            st.rerun()

    with col2:
        st.markdown("""
        <div style="padding: 2rem; border: 2px solid #f3e5f5; border-radius: 1rem; text-align: center; background-color: #fcf5ff;">
            <div style="font-size: 3rem; margin-bottom: 1rem;">🏪</div>
            <h3>我是商户</h3>
            <p style="color: #666;">管理商品和订单<br>查看各种支付模式下的交易</p>
        </div>
        """, unsafe_allow_html=True)
        if st.button("选择商户角色", type="primary", use_container_width=True):
            st.session_state.current_role = "merchant"
            st.session_state.agent = ACTChatAgent(
                st.session_state.user_id,
                "merchant"
            )
            welcome_msg = ChatMessage(
                role="assistant",
                content="您好！我是商户管理助手 🏪\n\n您可以：\n- 查看各类订单（即时支付、委托支付、A2A支付）\n- 管理商品上架\n- 向用户推送通知\n\n输入\"查看订单\"开始管理吧！"
            )
            st.session_state.chat_messages.append(welcome_msg)
            st.rerun()


def render_sidebar():
    """渲染侧边栏"""
    # 当前角色显示
    role_display = "👤 用户" if st.session_state.current_role == "user" else "🏪 商户"
    st.markdown(f"### 当前角色：{role_display}")

    # 切换角色按钮
    if st.button("⇄ 切换角色", use_container_width=True):
        new_role = "merchant" if st.session_state.current_role == "user" else "user"
        st.session_state.current_role = new_role
        st.session_state.agent = ACTChatAgent(
            st.session_state.user_id,
            new_role
        )
        st.session_state.chat_messages = []
        st.rerun()

    st.markdown("---")

    # 支付模式说明
    if st.session_state.current_role == "user":
        st.markdown("### 💡 快速提示")
        st.markdown("""
试试说：
- "买iPhone" → 即时支付
- "授权买咖啡，额度500元" → 委托支付
- "帮我安排出差，预算5000元" → A2A支付
        """)

    st.markdown("---")

    # 显示实时数据
    st.markdown("### 📊 实时数据")

    data = load_demo_data()

    st.metric("商品数量", len(data["products"]))
    st.metric("订单数量", len(data["orders"]))

    if st.session_state.current_role == "user":
        user_delegations = [d for d in data["delegations"] if d.get("user_id") == st.session_state.user_id and d.get("status") == "active"]
        st.metric("有效委托", len(user_delegations))


def render_chat_interface():
    """渲染聊天界面 - 对话框固定在底部"""

    # 添加CSS样式，使聊天区域可滚动，输入框固定在底部
    st.markdown("""
    <style>
    .chat-history {
        max-height: calc(100vh - 250px);
        overflow-y: auto;
        padding-bottom: 20px;
    }
    .chat-input-container {
        position: fixed;
        bottom: 0;
        left: 0;
        right: 0;
        background-color: white;
        padding: 10px 20px;
        border-top: 1px solid #e0e0e0;
        z-index: 100;
    }
    .main-content {
        padding-bottom: 80px;
    }
    </style>
    """, unsafe_allow_html=True)

    # 主内容区域
    st.markdown('<div class="main-content">', unsafe_allow_html=True)

    # 聊天历史容器（可滚动）
    chat_container = st.container()
    chat_container.markdown('<div class="chat-history">', unsafe_allow_html=True)

    for msg in st.session_state.chat_messages:
        with st.chat_message(msg.role):
            # 如果有协议标签，显示徽章
            if msg.metadata and msg.metadata.get("protocol"):
                protocol = msg.metadata["protocol"]
                badge_class = "instant-badge" if "INS" in protocol else ("delegated-badge" if "DEL" in protocol else "a2a-badge")
                st.markdown(f'<span class="protocol-badge {badge_class}">{protocol}</span>', unsafe_allow_html=True)

            st.markdown(msg.content)

    chat_container.markdown('</div>', unsafe_allow_html=True)

    st.markdown('</div>', unsafe_allow_html=True)

    # 输入框固定在底部
    st.markdown('<div class="chat-input-container">', unsafe_allow_html=True)
    if prompt := st.chat_input("请输入您的消息...", key="chat_input_bottom"):
        # 添加用户消息
        user_msg = ChatMessage(role="user", content=prompt)
        st.session_state.chat_messages.append(user_msg)

        # 显示用户消息
        with st.chat_message("user"):
            st.markdown(prompt)

        # 处理消息并显示回复
        handle_user_input(prompt)

        # 重新渲染以更新聊天历史
        st.rerun()

    st.markdown('</div>', unsafe_allow_html=True)


def handle_user_input(prompt: str):
    """处理用户输入"""
    agent = st.session_state.agent

    # 特殊命令处理
    prompt_lower = prompt.lower().strip()

    # 确认支付
    if prompt_lower in ["确认支付", "确认", "pay", "ok"]:
        if agent and agent.pending_action:
            with st.chat_message("assistant"):
                with st.spinner("正在处理..."):
                    response = agent.confirm_pending_action()
                    st.markdown(response.content)
                    st.session_state.chat_messages.append(response)
            return
        else:
            response = ChatMessage(role="assistant", content="没有待确认的操作。请告诉我您想做什么？")
            with st.chat_message("assistant"):
                st.markdown(response.content)
            st.session_state.chat_messages.append(response)
            return

    # 签发委托
    if prompt_lower in ["签发委托", "确认创建", "签发", "创建委托"]:
        if agent and agent.pending_action and agent.pending_action.get("type") == "delegated_payment_setup":
            with st.chat_message("assistant"):
                with st.spinner("正在签发IAC..."):
                    response = agent.confirm_pending_action()
                    st.markdown(response.content)
                    st.session_state.chat_messages.append(response)
            return

    # 创建自主任务
    if prompt_lower in ["确认创建任务", "创建任务", "开始任务"]:
        if agent and agent.pending_action and agent.pending_action.get("type") == "autonomous_payment_setup":
            with st.chat_message("assistant"):
                with st.spinner("正在创建任务..."):
                    response = agent.confirm_pending_action()
                    st.markdown(response.content)
                    st.session_state.chat_messages.append(response)
            return

    # 开始执行A2A任务（首次执行 - 机票预订）
    if prompt_lower in ["开始执行", "开始执行任务", "执行任务"]:
        task_id = st.session_state.get("last_a2a_task_id")
        if agent:
            with st.chat_message("assistant"):
                with st.spinner("正在执行A2A机票预订任务..."):
                    response = agent.simulate_autonomous_execution(task_id, step="flight")
                    st.session_state["a2a_current_step"] = "hotel"  # 标记下一步是酒店
                    st.markdown(response.content)
                    st.session_state.chat_messages.append(response)
            return

    # 继续执行A2A任务（下一步子任务）
    if prompt_lower in ["继续执行", "下一步", "继续"]:
        current_step = st.session_state.get("a2a_current_step", "flight")
        task_id = st.session_state.get("last_a2a_task_id")
        if agent:
            with st.chat_message("assistant"):
                with st.spinner(f"正在执行子任务..."):
                    if current_step == "hotel":
                        response = agent.simulate_autonomous_execution(task_id, step="hotel")
                        st.session_state["a2a_current_step"] = "car"  # 下一步是用车
                    elif current_step == "car":
                        response = agent.simulate_autonomous_execution(task_id, step="car")
                        st.session_state["a2a_current_step"] = "complete"  # 任务完成
                    else:
                        response = ChatMessage(
                            role="assistant",
                            content="""
🎉 **A2A自主支付任务全部完成！**

**执行汇总**：
- ✅ 子任务1（机票）：¥800
- ✅ 子任务2（酒店）：¥1200
- ✅ 子任务3（用车）：¥300

**总计支出：¥2300**
**子账户剩余：¥2700**

所有支付均通过A2A协议自动完成，无需您逐笔介入。
                            """.strip()
                        )
                    st.markdown(response.content)
                    st.session_state.chat_messages.append(response)
            return

    # 取消操作
    if prompt_lower in ["取消", "cancel", "不", "不要"]:
        if agent:
            agent.pending_action = None
        response = ChatMessage(role="assistant", content="已取消操作。还有什么可以帮您的？")
        with st.chat_message("assistant"):
            st.markdown(response.content)
        st.session_state.chat_messages.append(response)
        return

    # 修改额度处理
    if prompt_lower.startswith("修改额度") or prompt_lower.startswith("修改预算"):
        new_amount = agent._parse_amount_from_message(prompt) if agent else None
        if new_amount and agent and agent.pending_action:
            if "max_total" in agent.pending_action:
                agent.pending_action["max_total"] = new_amount
                agent.pending_action["max_single"] = new_amount / 5
                response = ChatMessage(
                    role="assistant",
                    content=f"已修改为总额度 ¥{new_amount:.2f}，单笔上限 ¥{new_amount/5:.2f}。请回复\"签发委托\"或\"确认创建任务\"继续。"
                )
            else:
                response = ChatMessage(role="assistant", content="无法修改，请重新创建。")
        else:
            response = ChatMessage(role="assistant", content="请输入有效的金额，例如：修改额度 1000")
        with st.chat_message("assistant"):
            st.markdown(response.content)
        st.session_state.chat_messages.append(response)
        return

    # 使用委托购买
    if "使用委托" in prompt or "用委托" in prompt:
        # 解析商品
        product = agent._parse_product_from_message(prompt) if agent else None

        if not product:
            response = ChatMessage(role="assistant", content="请告诉我具体想购买什么商品，例如：\"使用委托购买iPhone\"")
            with st.chat_message("assistant"):
                st.markdown(response.content)
            st.session_state.chat_messages.append(response)
            return

        # 查找有效委托
        data = load_demo_data()
        delegation = None
        for d in data["delegations"]:
            if d.get("user_id") == st.session_state.user_id and d.get("status") == "active":
                delegation = d
                break

        if not delegation:
            response = ChatMessage(role="assistant", content="您没有有效的委托授权。请先说\"帮我授权...\"创建委托。")
            with st.chat_message("assistant"):
                st.markdown(response.content)
            st.session_state.chat_messages.append(response)
            return

        # 设置待执行操作
        agent.pending_action = {
            "type": "delegated_payment_execute",
            "delegation_id": delegation["id"],
            "product_id": product["id"],
            "product_name": product["name"],
            "amount": product["price"]
        }

        response = ChatMessage(
            role="assistant",
            content=f"确认使用委托支付购买**{product['name']}**（¥{product['price']:.2f}）吗？请回复\"确认支付\"或\"取消\"")
        with st.chat_message("assistant"):
            st.markdown(response.content)
        st.session_state.chat_messages.append(response)
        return

    # 常规消息处理
    if agent:
        with st.chat_message("assistant"):
            with st.spinner("智能体思考中..."):
                response = agent.process_message(prompt)
                st.markdown(response.content)

                # 如果是A2A任务创建，保存任务ID
                if response.metadata and response.metadata.get("autonomous_task_created"):
                    if agent.pending_action:
                        st.session_state["last_a2a_task_id"] = agent.pending_action.get("task_id")

        st.session_state.chat_messages.append(response)


if __name__ == "__main__":
    render_chat_based_demo()
