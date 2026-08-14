# Alipay AI Pay 端到端验证证据模板

> 状态：Template / Non-normative  
> 使用范围：官方 Skill/CLI + AI 按量付费 Sandbox  
> 安全要求：只记录脱敏摘要、哈希和结果，不记录完整 Proof、密钥、令牌、绑定码或可重放请求

## 1. 验证元数据

| 项目 | 记录值 |
|---|---|
| 验证编号 | `E2E-YYYYMMDD-NNN` |
| 执行时间 |  |
| 执行人 |  |
| 代码分支/提交 |  |
| ACT Core 版本 |  |
| 支付宝接入示例版本 |  |
| A402 机器产物版本 |  |
| 官方 Skill/CLI 版本 |  |
| 支付宝环境 | Sandbox / 其他公开测试环境 |
| 产品资料快照 |  |

## 2. 制品版本

| 制品 | 精确版本或哈希 | 获取来源 | 验证方式 |
|---|---|---|---|
| Agent Runtime |  |  |  |
| npm 安装器 | 不得只写 `latest` | npm official | version + integrity |
| `alipay-bot` CLI |  | official installer | version output / file hash |
| 安装后的 Payment Skill |  | official installer | content hash / metadata |
| 安装后的 Wallet Skill |  | official installer | content hash / metadata |
| 公开 Skill 源码 | commit SHA | `alipay/payment-skills` | Git commit |
| 卖方示例/实现 | commit SHA | 当前项目/官方示例 | Git commit |

## 3. 声明范围

只勾选本次实际通过的范围：

- [ ] `AGENT_PAYMENT_CAPABLE`
- [ ] `MACHINE_PAYMENT_ACCEPTING`
- [ ] `ALIPAY_AI_PAY_END_TO_END_COMPATIBLE`

限制说明：

```text

```

## 4. 脱敏关联链

不要记录完整真实值。建议记录不可逆哈希的前 8—12 位和字段来源。

| 标识 | 脱敏值/哈希前缀 | 生成方 | 首次出现步骤 | 已验证的关联 |
|---|---|---|---|---|
| `intent_id` |  | Agent/ACT |  |  |
| `delegation_id` | N/A /  | ADD |  |  |
| `out_trade_no` |  | Seller |  |  |
| `resource_id` |  | Seller |  |  |
| `service_id` |  | Alipay product registration |  |  |
| `trade_no` |  | Alipay |  |  |
| `payment_proof` | 仅记录“present/absent”和安全哈希前缀 | Alipay |  |  |

## 5. 主链路证据

| 步骤 | 预期行为 | 实际结果 | 证据位置/摘要 | 结论 |
|---|---|---|---|---|
| 1 | 用户请求收费资源并形成意图 |  |  | Pass/Fail |
| 2 | Agent 发起原始资源请求 |  |  | Pass/Fail |
| 3 | 卖方返回 402 + `Payment-Needed` |  |  | Pass/Fail |
| 4 | Agent 展示交易信息并取得确认 |  |  | Pass/Fail |
| 5 | 官方 CLI 发起支付或待确认流程 |  |  | Pass/Fail |
| 6 | CLI 返回本轮支付状态 |  |  | Pass/Fail |
| 7 | CLI 恢复同一资源请求 |  |  | Pass/Fail |
| 8 | 卖方调用官方验款 API |  |  | Pass/Fail |
| 9 | 卖方核对 active、金额、订单、资源和防重 |  |  | Pass/Fail |
| 10 | 卖方返回对应资源 |  |  | Pass/Fail |
| 11A | 卖方调用 fulfillment confirm |  |  | Pass/Fail/N/A |
| 11B | 买方 CLI 调用 fulfillment ack |  |  | Pass/Fail/N/A |
| 12 | 四域证据可以关联 |  |  | Pass/Fail |

## 6. 原请求恢复检查

| 项目 | 原请求摘要/哈希 | 支付后请求摘要/哈希 | 一致性 |
|---|---|---|---|
| URL |  |  |  |
| HTTP Method |  |  |  |
| Body |  |  |  |
| 必要 Header |  |  |  |
| Resource |  |  |  |

不得在证据中记录授权 Header、Cookie 或可重放的完整请求。

## 7. 必测异常

| 用例 | 实际恢复动作 | 是否重复支付 | 是否未付款交付 | 是否重复交付 | 结论 |
|---|---|---|---|---|---|
| 账单过期 |  | No/Yes | No/Yes | No/Yes |  |
| 用户拒绝 |  | No/Yes | No/Yes | No/Yes |  |
| pending 后查询 |  | No/Yes | No/Yes | No/Yes |  |
| Proof 无效 |  | No/Yes | No/Yes | No/Yes |  |
| 金额不一致 |  | No/Yes | No/Yes | No/Yes |  |
| 订单不一致 |  | No/Yes | No/Yes | No/Yes |  |
| 资源不一致 |  | No/Yes | No/Yes | No/Yes |  |
| Proof 重放 |  | No/Yes | No/Yes | No/Yes |  |
| 验款 API 暂时失败 |  | No/Yes | No/Yes | No/Yes |  |
| 卖方履约确认失败 |  | No/Yes | No/Yes | No/Yes |  |
| 买方履约 ack 重复/失败 |  | No/Yes | No/Yes | No/Yes |  |

## 8. 已知差异

| ID | 预期 | 实际 | 分类 | 后续动作 | 负责人 |
|---|---|---|---|---|---|
|  |  |  | Product / Protocol / Binding / Implementation |  |  |

重点记录：

- `amount` 单位解释。
- `Payment-Proof` 的 Base64/Base64URL 实际编码。
- `client_session` 是否出现及何时必填。
- Proof 是否对宿主 Agent 可见。
- `tradeNo` 与 `outShakeNo` 的实际用途。
- 买方 fulfillment ack 与卖方 fulfillment confirm 的调用关系。

## 9. 安全检查

- [ ] 没有私钥、访问令牌、绑定码、支付密码或完整 Proof。
- [ ] 没有完整支付链接或可重放的完整 HTTP 请求。
- [ ] 订单、交易、资源和用户标识已脱敏。
- [ ] CLI 原始日志保存在安全环境，公开证据只使用摘要。
- [ ] 所有截图已检查二维码、账号和链接泄露。

## 10. 结论与签字

| 角色 | 结论 | 姓名 | 日期 |
|---|---|---|---|
| 执行人 | Pass / Fail / Partial |  |  |
| 支付宝接入维护者 | Accepted / Changes required；附公开评审链接 |  |  |
| ACT Core spec owner / DWG reviewer | Accepted semantics / Changes required；附公开评审链接 |  |  |

最终说明：

```text
本次验证通过的能力范围：
未通过或未验证的范围：
禁止对外扩大的声明：
下一次验证条件：
```
