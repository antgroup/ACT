# ACT 2.1 A402 接入协议候选

> **状态：Candidate Working Draft / Non-normative**  
> 候选组件名：`PSD-PAY-A402`。本文对齐 2026-08-03 完成修订的《支付服务域》，不是已发布的 HTTP Binding 或产品 Profile，也不覆盖支付宝官网当前格式。

文件名沿用维护任务约定的 `a402-binding.md`。在候选架构中，`PSD-PAY-A402` 是与支付场景解耦的接入协议组件；具体 HTTP 序列化实现同时受跨产品的[HTTP A402 Binding](../../bindings/http-a402/README.md)和所选 Product Profile 约束。

## 1. 独立性

A402 不等同于 AUP/L3。它可以被以下任一场景引用：

- `PSD-PAY-INS` / L1；
- `PSD-PAY-DEL` / L2；
- `PSD-PAY-AUP` / L3。

场景组件决定用户是否在场、IAC 类型、额度和支付授权；A402 决定 HTTP 402 支付要求、支付证明、验证和资源履约如何衔接。

## 2. 参与方与前置条件

候选参与方包括买方智能体、卖方服务方、PSP、委托人，以及可能与卖方服务方分离的商户或资源提供方。

进入 A402 前，候选文本要求：

- 卖方能稳定标识收费资源/服务和商户订单；
- 卖方能生成、签名、编码并保存 `Payment-Needed`；
- 买方能识别 HTTP 402、解析 Header、选择受支持的 `method_id` 并执行场景授权检查；
- 各方通过 `CID-PCA-NEG` 或等价机制获得 `method_id`、`psp_id`、`endpoint`、`method_schema_url`；
- DEL/AUP 仍满足相应 IAC、金额、累计额度、商户范围、支付方式和子账户约束。

## 3. 候选交互

1. 买方向卖方请求收费资源、工具、API、数字内容或服务。
2. 没有可用 Proof 或 Proof 验证失败时，卖方返回 `402 Payment Required` 和 `Payment-Needed`。
3. 买方按 INS、DEL 或 AUP 的场景要求完成授权检查，并依 `method_id` 调用 PSP 或指定端点支付。
4. 支付成功后，买方对原资源或服务发起新的请求，并携带 `Payment-Proof`。
5. 卖方把 Proof 作为不可信输入，调用 PSP 或受信验证服务，检查凭证有效性、防重放和当前请求一致性。
6. 验证通过后卖方交付资源，并按支付方法规范确认履约；成功响应可以携带 `Payment-Validation`。

## 4. Header 与编码

| Header | 协议用途 | 当前支付宝产品事实 |
|---|---|---|
| `Payment-Needed` | 传递支付要求和方法相关载荷 | 官方指南定义为 Base64URL 编码账单 |
| `Payment-Proof` | 传递支付证明、交易关联和方法相关载荷 | 官方指南定义该 Header，并在正文中称其为 Base64 编码 |
| `Payment-Validation` | 卖方在验凭后返回机器可读验证及履约状态；成功响应中可选 | 官方指南没有定义同名 Header；仅公开服务端验凭结果 |

完成版协议明确：三个 Header 的值均采用 **Base64URL 编码的 UTF-8 JSON**，编码前使用 `protocol` + `method` 两层结构。`Payment-Validation` 是卖方验凭后的可选响应 Header，不是每次成功响应都必须发送。

这是一项 ACT 候选协议事实，不等于支付宝产品当前已经实现同名 Header。支付宝官网对 `Payment-Proof` 的文字表述及 `Payment-Validation` 的缺失继续由 Alipay Profile 记录为产品映射差异，不能反向把已明确的 ACT 编码规则重新标为 Core Pending。

支付宝的具体 `out_trade_no`、`resource_id`、`seller_signature`、`seller_id`、`service_id`、`payment_proof`、`trade_no`、`client_session` 等字段属于[Alipay AI Pay Profile](../../profiles/alipay-ai-pay/README.md)，不直接冻结为渠道中立 Core Schema。

## 5. `method_id` 与能力协商

`method_id` 标识本次交易采用的具体支付方法。每个支付方法由独立方法规范定义请求构造、扩展字段、签名算法、PSP 核验、支付授权结果凭证及方法错误码。进入 A402 前，买卖双方可通过 `CID-PCA-NEG` 或等价机制协商 `method_id`、`psp_id`、`endpoint` 和 `method_schema_url`。

Candidate 机器契约采用以下工程决定：

- `method_id` 是稳定的命名空间标识，语法为 URI-scheme 风格前缀加方法路径，例如 `example:a402/test-pay`；
- `method_version` 独立使用 SemVer，兼容升级不得改变 `method_id`；
- 三类 Header 解码载荷均在 `protocol` 中回显 `method_id` 与 `method_version`；
- 不可识别、已弃用或方法 Schema 不可达时使用错误类别 `PROTOCOL_METHOD`，合法下一动作包含重新协商方法；
- 支付宝当前 `protocol` / `method` 产品结构由 Profile 做适配，不要求官网产品凭空增加 Core 字段。

上述内容是[Candidate 工程决议](../../docs/project/decisions/candidate-machine-contract-resolution-2026-08-03.md)，不是已完成公开 DWG 治理的 Stable 结论。

### 5.1 基础载荷字段清单

完成版支付服务域给出以下跨方法字段语义。Candidate 工程层已经在[机器契约](schemas/a402/README.md)中冻结三类 Header 的字段分布、必填性和格式，供开源实现与测试互操作；正式治理仍可通过新版本替代，不能把当前 Schema 宣称为 Stable。

| 字段 | 协议候选语义 |
|---|---|
| `method_id` | 本次交易采用的支付方法 |
| `out_trade_no` | 外部订单号，用于幂等和交易关联 |
| `amount` | 支付金额；协议建议使用字符串避免浮点误差 |
| `currency` | 交易币种 |
| `resource_id` | 与支付绑定的资源标识，防止 Proof 挪用 |
| `pay_before` | 支付截止时间 |
| `seller_unique_id` | 卖方服务方唯一标识 |
| `buyer_unique_id` | 买方 Agent 唯一标识 |
| `payment_proof` | PSP 生成或确认的支付授权结果凭证 |
| `trade_no` | PSP 交易流水或唯一交易标识 |
| `expires_at` | Proof 的有效截止时间 |
| `signer_id` | 报文签名主体 |
| `signature_content` | 报文签名值 |
| `signature_type` | 签名算法标识 |

支付方法可以定义扩展字段，但不得改变基础字段的候选语义。支付宝 `seller_id`、`service_id`、`seller_signature`、`client_session` 等当前字段继续由 Alipay Profile 定义，不能因为名称相近而直接等同于上述通用字段。

## 6. 原请求重试

源文档明确：支付成功后应对“原资源或服务”发起新的请求并携带 Proof。候选 Binding 必须保持本次支付要求、原请求和重试请求的关联，不能把 Proof 用于其他资源或订单。

Candidate Binding 使用 `request_fingerprint` 关联原请求：对大写 HTTP Method、规范化目标 URI、小写 Content-Type 和 Body SHA-256 摘要按固定顺序计算 SHA-256，并以 `sha-256:<base64url-no-padding>` 表示。`Payment-Needed` 生成该值，`Payment-Proof` 必须回显。

- GET/HEAD/OPTIONS 之外的方法必须另带业务 `idempotency_key`；
- Authorization、Cookie、Proxy-Authorization、Proof、签名密钥和逐跳 Header 不得保存进重试材料或公开证据；
- 指纹证明业务请求关联，不要求保存或重放字节完全相同的敏感 Header；
- 最大重试次数由 Binding/Profile 声明，但支付结果未知时必须先查权威状态，不得自动创建第二笔支付。

完整算法和保存下限见[Candidate 工程决议](../../docs/project/decisions/candidate-machine-contract-resolution-2026-08-03.md#3-请求指纹和防重放规则)。

## 7. Proof 验证、防重放与一致性

卖方在交付前至少应检查：

- Proof 的签名或等价真实性、有效期和吊销/失效状态；
- `trade_no` 或等价交易标识未被重复用于非幂等履约；
- Proof 中的订单、资源和方法上下文与当前请求一致；
- 所选 Product Profile 要求的金额、币种、收款方及其他原账单事实一致。

支付宝官方指南当前明确要求验证 `active`，并核对金额、`out_trade_no`、`resource_id`，同时防止 `trade_no` 重复履约。该产品验证结果可以映射到候选 `Payment-Validation` 语义，但不能据此声称支付宝发送同名 Header。

## 8. 候选状态机

完成版支付服务域定义以下状态和允许转移：

| 当前状态 | 候选含义 | 允许转入 |
|---|---|---|
| `CREATE` | 交易已创建 | `WAIT_BUYER_PAY` |
| `WAIT_BUYER_PAY` | 等待买方完成支付 | `WAIT_SELLER_FULFILLMENT`、`TRADE_CLOSED` |
| `WAIT_SELLER_FULFILLMENT` | 支付已完成，等待卖方履约 | `WAIT_BUYER_RECEIPT`、`TRADE_CLOSED` |
| `WAIT_BUYER_RECEIPT` | 卖方已履约，等待买方回执 | `TRADE_FINISHED`、`TRADE_CLOSED` |
| `TRADE_FINISHED` | 交易完成终态 | 无 |
| `TRADE_CLOSED` | 取消、退款或其他关闭终态 | 无 |

实现不得创造反向转移或从终态重新进入处理中状态。Candidate 触发事件已经固定为 `PAYMENT_NEEDED_ISSUED`、`PAYMENT_VALIDATED`、`PAYMENT_TERMINATED`、`DELIVERY_COMMITTED`、`COMPENSATION_COMPLETED`、`FULFILLMENT_CONFIRMED` 和 `TRADE_TERMINATED`；允许关系由 [`transaction-state.schema.json`](schemas/a402/transaction-state.schema.json)及 fixtures 执行检查。产品状态仍由 Profile 映射，超时本身不得被当作支付失败。

## 9. 幂等与错误恢复

完成版支付服务域定义错误的通用语义类别和恢复方向。Candidate 机器层将它们固定为 `error_id`、`category`、`phase`、`retryability`、`valid_next_actions` 和 `message`；完整代码见 [`error-catalog.json`](schemas/a402/error-catalog.json)：

| 语义类别 | 候选含义 | 恢复方向 |
|---|---|---|
| 签名校验错误 | 签名无效或算法不受支持 | 修复签名者、密钥或算法配置后再发起 |
| 请求参数错误 | 参数、金额、时间格式非法或请求过期 | 修正请求；过期时重新取得支付要求 |
| 协议/方法错误 | 协议、版本或支付方法不受支持 | 重新协商方法，不盲目重试 |
| Agent/服务方身份错误 | 参与方身份或绑定关系验证失败 | 修复身份材料和绑定关系 |
| 额度与资产错误 | 余额、单笔/累计额度或账户状态不满足 | 补足资产、调整授权或更换允许的工具 |
| 限权与风控错误 | 授权边界或风控策略拒绝 | 等待解除、人工升级或重新授权 |
| 交易状态错误 | 交易不存在或当前状态不允许操作 | 查询权威状态并做幂等处理 |
| 退款错误 | 退款超限或处理失败 | 查询退款状态，必要时进入补偿/人工流程 |
| 履约回执错误 | 资源交付或履约确认失败 | 只重试幂等的履约阶段，不重新扣款 |
| Proof 验证错误 | Proof 缺失、过期、无效或与主体/订单/资源不一致 | 获取有效 Proof 或重新发起新的支付流程 |
| 系统错误 | PSP、验证方或下游临时故障 | 查询结果后有限次退避重试；保持未知态诚实 |

当前可执行的安全下限是：

- 未获得权威支付结果时，不因超时自动创建第二笔支付；
- Proof 验证暂不可用时，不猜测成功、不交付资源；
- 重复的已验凭请求只返回既有结果或拒绝，不重复非幂等交付；
- 履约确认失败只重试履约确认，不重新扣款或重复交付；
- 账单过期、金额或资源变化时，不静默改写旧账单继续支付。

防重复履约的权威占用键是 `(method_id, trade_no, out_trade_no, resource_id)`，交付幂等键是 `(method_id, trade_no, request_fingerprint)`。记录至少保存到 Proof 过期时间与方法 Profile 声明的履约/证据保留截止时间两者中较晚者；没有持久化声明的实现不得声称跨重启防重放。

支付验凭、资源交付、方法履约确认与 TSD 证据必须保持为四个独立且可关联的事实。`Payment-Validation` 不得用单一 `SUCCESS` 淹没后续阶段结果。

## 10. 来源

- 完成版协议事实源：[支付服务域](https://yuque.antfin.com/hknzlf/fvle20/dve0b9g2u1t3cs33)
- 修订背景与差异追溯：[ACT v2.1 协议修订需求点分析](https://yuque.antfin.com/hknzlf/fvle20/dh5iwcigwa65hkds)
- 支付宝产品事实：[AI 按量付费接入指南](https://aipay.alipay.com/docs/ai-receive/MACHINE_PAY.html)
