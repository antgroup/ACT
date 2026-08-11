# ACT 2.1 商业交互到支付的连接规则

> **状态：Candidate Working Draft / Non-normative**  
> 本文只记录商业交互域与支付服务域的连接关系；完整 CID 候选见[商业交互域公开候选](commerce-interaction.md)。

## 1. 候选作用

`CID-PCA-NEG` 用于在进入支付交互前确定双方可使用的支付方法和接入信息。《支付服务域》把它或等价机制作为 A402 的前置能力，并允许 INS、DEL、AUP 选择 A402、传统商户平台下单支付或相应 MCP/API 接口。

源文档给出的协商结果至少涉及：

| 字段 | 候选含义 | 定稿状态 |
|---|---|---|
| `method_id` | 所选支付方法标识 | Candidate 使用稳定命名空间 ID；版本由独立 `method_version` 表达 |
| `psp_id` | 所选支付服务方标识 | CID 语义已明确；跨组织标识体系待治理 |
| `endpoint` | 后续支付或方法端点 | CID 要求来源和一致性检查；认证、重定向和可达性规则待治理 |
| `method_schema_url` | 方法载荷结构说明 | CID 要求一致性检查；完整性、缓存和版本规则待治理 |

这些字段来自修订源的候选描述，不代表支付宝当前产品报文必须逐字段包含同名属性。

## 2. 与 A402 的关系

候选流程为：

```text
商业上下文与交易条件
→ CID-PCA-NEG（或等价机制）
→ 选择 method_id / PSP / endpoint / method schema
→ INS、DEL 或 AUP 完成场景授权检查
→ A402 或相应接口执行支付接入
```

A402 使用协商结果来解释方法相关载荷并选择 PSP/验证端点，但不负责：

- 商品或服务发现；
- 用户意图生成；
- 购物车或交易条件确认；
- INS/L1 用户确认；
- DEL/L2 或 AUP/L3 的 IAC 边界。

## 3. `Payment-Needed` 与交易确认

完成版协议已经明确两条接入路径的最小关联方式：

- 传统商户平台下单支付流程使用商户侧订单号；
- A402 流程由 `Payment-Needed` 返回 `out_trade_no`、`resource_id` 等订单或资源标识。

协议没有要求支付请求携带完整购物车，也没有把 `Payment-Needed` 定义为完整 `CID-CART-CFM` 对象。Candidate 机器契约固定 `out_trade_no`、`resource_id`、`amount`、`currency` 为最小商业关联，并允许使用 `commerce_confirmation` 引用独立确认对象。订单、资源或金额变化时必须创建新的支付要求，不得静默改写旧账单。

## 4. 不合并外部商业协议

支付服务域没有定义外部商业协议的字段。本候选不复制 UTP 等外部协议规则，也不把外部协议字段写入 ACT Core。

## 5. 本轮黄色修订：能力声明安全

历史维护稿的黄色高亮只修改 `CID-PCA-NEG` 的安全考虑；该记录用于解释 Candidate 演进：

- 使用 `act-payment-capability.json` 前，应确认它来自商户已声明的 `capability_url`；
- 解析 `supported_methods` 时，宜校验 `psp_id`、`endpoint`、`method_schema_url` 的一致性，防止声明被伪造、篡改或替换；
- 来源无法确认或关键字段校验失败时，不得继续能力匹配或支付。

黄色段落中的无下划线拼写按同文既有字段作编辑性规范化，不新增第二套字段名。

## 6. 待决定事项

- CID 来源示例中的 `currency` / `amount_currency`、`supported_methods` / `matched_methods` 等字段差异；
- 能力声明与协商请求的正式 JSON Schema、版本和签名范围；
- `method_id` 和 `psp_id` 的跨组织注册、冲突解决和长期发现服务；
- 多个 PSP/方法的排序、选择和降级；
- `endpoint`、`method_schema_url` 的认证、重定向、完整性和缓存；
- 正式 CID 确认对象的版本和签名规则；
- 协商过期或方法不可用时是否允许自动重新协商。

完整影响范围见[修订状态](../revision-status.md)。

## 7. 来源

- 当前 CID 协议事实源：[商业交互域](https://www.act-protocol.com/documentation/commerce)
- PSD 协议事实源：[支付服务域](https://www.act-protocol.com/documentation/payment)
- 跨域上位参考：[协议概览](https://www.act-protocol.com/documentation/overview)
