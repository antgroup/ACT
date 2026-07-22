# 支付宝 AI 付公开接入基线

> 状态：Draft / Non-normative  
> 资料快照：2026-07-15  
> 用途：记录公开产品事实，为后续 Alipay AI Pay Profile 提供输入

本文不定义 ACT 正式消息。文中的支付宝字段、API 和命令来自公开官网、支付宝开放平台或官方开源仓库，后续仍需要产品和技术复核。

## 1. 官网产品结构

[支付宝 AI 付概览](https://aipay.alipay.com/docs/overview.html)将能力分为 Agent 支付、AI 按量付费、AI 订阅付费及移动端/网页收款等产品。首期 ACT Profile 聚焦：

- [Agent 支付](https://aipay.alipay.com/agentpay)：为 Agent 提供 AI 钱包和支付能力。
- [AI 按量付费](https://aipay.alipay.com/callpay)：允许 API、MCP Tool 或 Skill 按调用收费。

在 HTTP 402 场景中，两者不是孤立产品流程，而是同一机器支付闭环的两侧能力：Agent 支付赋予买方 Agent 授权、付款和取得凭证的能力；AI 按量付费赋予卖方服务机器可读出账、验款、交付和确认履约的能力。

协议结构上，v2.1 修订方向把授权场景与支付接入方式分开：首期是 L1 `PSD-PAY-INS` 场景引用候选 `PSD-PAY-A402`，再由官方 Skill/CLI Binding 和 Alipay AI Pay Profile 落到支付宝产品。该方向用于组织开源框架，正式组件仍等待公开规范发布。

两侧能力都不是 ACT 的独立域或单域实现。它们作为 Alipay AI Pay Product Profile 跨 ADD、CID、PSD、TSD 协作，具体见[双侧能力与 ACT 四域映射](../../profiles/alipay-ai-pay/domain-mapping.md)。

## 2. Agent 支付公开接入路径

### 2.1 当前公开载体

官网公开推荐的安装命令为：

```bash
npx -y @alipay/agent-payment@latest install
```

公开实现来自 [alipay/payment-skills](https://github.com/alipay/payment-skills)，主要包含：

| Skill | 公开职责 |
|---|---|
| `alipay-authenticate-wallet` | 钱包状态检查、申请、授权绑定和解绑 |
| `alipay-payment-skill` | 收银台链接支付、HTTP 402 支付和支付结果查询 |

钱包开通和绑定流程见[支付宝 AI 钱包使用指南](https://aipay.alipay.com/wallet-guide)。每个 Agent 需要独立获得用户授权；授权过程中用户通过支付宝完成身份确认并向 Agent 提交短时有效的绑定口令。

### 2.2 Agent 最小接入旅程

```text
安装官方 Skill
  → 检查钱包状态
  → 未开通时申请钱包
  → 用户在支付宝授权
  → Agent 提交绑定口令
  → 识别收银台链接或 HTTP 402
  → 展示支付意图并取得用户确认
  → 提交支付
  → 查询支付结果
  → 恢复原 Agent 任务
```

### 2.3 当前公开边界

Agent 支付产品页当前主要指向 Skill 安装和钱包使用路径。面向 Agent 平台或智能硬件的独立 SDK 尚不能作为开源项目的可用接入前提。因此首期 Alipay Agent Payment Profile 应以公开 Skill/CLI 行为为产品事实，未来 SDK/API 公开后再增加 Binding。

当前官方 Skill/CLI 是工作流级 Binding：在 402 场景中可以保存账单和原始请求、发起或查询支付、携带 Proof 恢复请求并返回资源。ACT 接入不应假设宿主 Agent 必须直接获得完整 Proof。详细核对见[官方 Skill/CLI 行为审计](../../profiles/alipay-ai-pay/skill-cli-behavior-audit-2026-07-21.md)。

## 3. AI 按量付费公开接入路径

完整卖方流程见[AI 按量付费接入指南](https://aipay.alipay.com/docs/ai-receive/MACHINE_PAY.html)。服务提供方需要实现：

1. 未支付时返回 HTTP 402 及 `Payment-Needed`。
2. Agent 完成支付后，接收其携带 `Payment-Proof` 的原请求重试。
3. 调用支付宝支付验证 API。
4. 校验支付结果和原账单的一致性，并阻止凭证重复履约。
5. 返回付费资源。
6. 调用支付宝履约确认 API。

### 3.1 `Payment-Needed`

公开文档将支付要求作为 Base64URL 编码的 JSON 放入 HTTP Header，示意结构为：

```json
{
  "protocol": {
    "out_trade_no": "merchant-order-id",
    "amount": "0.01",
    "currency": "CNY",
    "resource_id": "resource-id",
    "pay_before": "2026-07-15T10:00:00+08:00",
    "seller_signature": "signature",
    "seller_sign_type": "RSA2",
    "seller_unique_id": "2088..."
  },
  "method": {
    "seller_name": "merchant-name",
    "seller_id": "merchant-id",
    "seller_app_id": "app-id",
    "goods_name": "resource-name",
    "seller_unique_id_key": "seller_id",
    "service_id": "registered-service-id"
  }
}
```

官网还规定了参与签名的字段集合、字典序拼接方式和 RSA2 本地签名要求。该结构应进入支付宝 Profile，而不是原样成为支付渠道中立的 ACT Core 对象。

### 3.2 `Payment-Proof`

公开文档给出的支付凭证示意为：

```json
{
  "protocol": {
    "payment_proof": "64-character-proof",
    "trade_no": "32-digit-trade-number"
  },
  "method": {
    "client_session": "session-data"
  }
}
```

卖方使用以下公开 API 完成闭环：

- 支付验证：[alipay.aipay.agent.payment.verify](https://ideservice.alipay.com/cms/site/0j7uot)
- 履约确认：[alipay.aipay.agent.fulfillment.confirm](https://ideservice.alipay.com/cms/site/0j7sw0)

验证成功不能只依据接口调用成功。卖方还需要检查：

- 支付状态有效。
- 金额与原账单一致。
- `out_trade_no` 与原账单一致。
- `resource_id` 与请求资源一致。
- `trade_no` 未被重复用于资源交付。

官方公开示例位于 [alipay/ai 的 aipay-402-example](https://github.com/alipay/ai/tree/main/code_example/aipay-402-example)。

## 4. ACT 四域到双侧机器支付能力的工作映射

| ACT 域 | 买方 Agent 支付能力 | 卖方机器支付能力 |
|---|---|---|
| ADD | 当前支付意图与用户确认；未来委托授权 | 消费买方授权上下文，不替买方签发授权 |
| CID | 保留商品、商户、订单和支付能力上下文 | 描述收费资源、交易条件和支付宝支付能力 |
| PSD | L1 `PSD-PAY-INS`、支付工具引用、用户确认支付和结果查询 | 候选 `PSD-PAY-A402`、支付凭证、服务端验款和履约确认 |
| TSD | 关联意图、订单、支付和履约证据 | 提供支付完成和资源履约证据 |

组件级映射以[四域映射文档](../../profiles/alipay-ai-pay/domain-mapping.md)为准。以下工作语义表保留用于字段和 Profile 讨论。

以下名称仅用于框架讨论，等待 ACT 修订后替换：

| ACT 工作语义 | 支付宝公开实现 | 归属层 | 修订状态 |
|---|---|---|---|
| Wallet Authorization | AI 钱包申请、授权和绑定 | Alipay Profile | 产品事实待复核 |
| Payment Intent | Payment Skill 支付意图和用户确认 | Core + Profile | Core 待修订 |
| Payment Requirement | `Payment-Needed` | Core + HTTP Binding + Profile | Core 待修订 |
| Payment Proof | `Payment-Proof` | Core + HTTP Binding + Profile | Core 待修订 |
| Proof Verification | `alipay.aipay.agent.payment.verify` | Alipay Profile | 产品事实待复核 |
| Fulfillment Receipt | `alipay.aipay.agent.fulfillment.confirm` | Core + Profile | Core 待修订 |
| Recovery Action | 支付宝错误码、重试或重新支付 | Core + Profile | 待设计 |

建议字段映射的工作底稿为：

| ACT 工作字段 | 支付宝字段 |
|---|---|
| `payment_request.id` | `out_trade_no` |
| `payment_request.amount` | `amount` |
| `payment_request.currency` | `currency` |
| `resource.id` | `resource_id` |
| `expires_at` | `pay_before` |
| `payee.id` | `seller_id` / `seller_unique_id` |
| `payee.display_name` | `seller_name` |
| `product.service_id` | `service_id` |
| `integrity.signature` | `seller_signature` |
| `integrity.algorithm` | `seller_sign_type` |

工作字段不是正式 ACT Schema，不能用于实现兼容性声明。

## 5. 官网文档需要由开源项目补齐的导航

当前公开资料能够支持产品接入，但信息分散。ACT 项目需要提供一个公开、可追溯的解释层：

1. 解释 Agent 支付和 AI 按量付费在 402 闭环中的关系。
2. 把钱包 Skill、支付 Skill、402 卖方接入、验证 API 和履约 API 串成开发者旅程。
3. 明确 Agent 支付当前以 Skill 接入为公开基线，不把未来 SDK 描述成现有能力。
4. 说明 API、MCP Tool 和 Skill 是收费资源形态；当前卖方技术基线主要是 HTTP 402。
5. 区分产品开户签约、协议消息、Transport 和业务履约。
6. 提供从沙箱到上线的检查清单，而不是只给孤立代码片段。

## 6. 待支付宝产品复核的问题

| 编号 | 问题 | 风险 |
|---|---|---|
| AP-001 | `amount` 是以元表示的小数字符串，还是“最小货币单位” | 金额误解可能导致错误支付 |
| AP-002 | `Payment-Proof` 的编码是否严格要求 Base64URL | 不同实现可能无法互操作 |
| AP-003 | `client_session` 在什么条件下必填 | API 参数描述与错误码存在理解差异 |
| AP-004 | 第三方代调用时 `app_auth_token` 与 `seller_app_id` 的准确关系 | ISV/平台商户接入可能失败 |
| AP-005 | `trade_no` 防重复履约的存储周期和并发要求 | 可能产生重复交付或重放风险 |
| AP-006 | 履约失败、部分交付和履约确认重试如何表达 | 资源交付状态可能不一致 |
| AP-007 | Agent 平台未来 SDK/API 与当前 Skill/CLI 的兼容关系 | Profile 演进和版本兼容风险 |
| AP-008 | 是否存在原生 MCP/Skill 卖方支付 Binding 的公开计划 | 产品表述与技术接入边界可能不一致 |
| AP-009 | 买方 `402-buyer-fulfillment-ack` 与卖方 `fulfillment.confirm` 是否是同一接口、能否重复调用及最终责任方 | 双侧都调用可能产生重复或错误履约状态 |
| AP-010 | npm `latest` 安装器、实际安装后的 Skill 与 `alipay/payment-skills` main 如何建立可验证版本关系 | 大会证据可能引用了错误或不可复现的 Skill 版本 |

这些问题在确认前进入[修订追踪](05-revision-tracker.md)，不能由示例代码自行假设答案。

## 7. 公开资料索引

- [支付宝 AI 付产品概览](https://aipay.alipay.com/docs/overview.html)
- [Agent 支付产品页](https://aipay.alipay.com/agentpay)
- [AI 钱包使用指南](https://aipay.alipay.com/wallet-guide)
- [AI 按量付费产品页](https://aipay.alipay.com/callpay)
- [AI 按量付费接入指南](https://aipay.alipay.com/docs/ai-receive/MACHINE_PAY.html)
- [AI 付文档机器索引](https://aipay.alipay.com/docs/llms.txt)
- [支付验证 API](https://ideservice.alipay.com/cms/site/0j7uot)
- [履约确认 API](https://ideservice.alipay.com/cms/site/0j7sw0)
- [官方 Payment Skills](https://github.com/alipay/payment-skills)
- [官方 AI 付代码示例](https://github.com/alipay/ai/tree/main/code_example/aipay-402-example)
