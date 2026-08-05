# ACT 2.1 候选修订状态

> **状态：Active Candidate Working Draft Tracker / Non-normative**  
> 最后核对：2026-08-03（UTC+8）  
> 本页记录协议来源、同步结果和剩余 Pending Decision，不是正式发布声明。

## 1. 当前协议事实源

### 1.1 完成版支付服务域

| 项目 | 本次核对 |
|---|---|
| 来源 | [支付服务域](https://yuque.antfin.com/hknzlf/fvle20/dve0b9g2u1t3cs33) |
| 文档 ID / slug | `545380168` / `dve0b9g2u1t3cs33` |
| 维护人 | 观岳 |
| `updated_at` | `2026-08-03T07:05:44.000Z` |
| `content_updated_at` | `2026-08-03T07:05:43.000Z` |
| `published_at` | `2026-08-03T07:05:43.000Z` |
| 字数 / 正文行数 | 16,197 / 661 |
| 正文 SHA-256 | `8d39bbafe0bd5c344a78355c4a68371e07b927cc97bb394b3fdbfb0bfb776d06` |
| 与上次核对比较 | 已变化：原记录更新时间为 2026-05-19、字数 11,890、哈希 `34123c…`；本次为完成版修订 |

该文档现在完整定义 PSD 六组件，并直接包含 A402、INS/L1、DEL/L2、AUP/L3、三类 Header、基础载荷、六态状态机和十一类错误语义。它是当前 PSD 2.1 协议修订事实源。

### 1.2 修订背景资料

[《ACT v2.1 协议修订需求点分析》](https://yuque.antfin.com/hknzlf/fvle20/dh5iwcigwa65hkds)继续用于解释改名、拆分和演进背景，不再作为覆盖《支付服务域》的独立语义增量。两者不一致时，以完成版《支付服务域》为准。

后续同步只在完成版协议的更新时间、正文哈希、章节结构或正文内容实际变化时修改候选文本，不因每日任务制造无意义改动。

## 2. 本次协议变化与同步

| 完成版协议事实 | 公开候选处理 | 状态 |
|---|---|---|
| PSD 六组件 | `PSD-PMT-BND`、`PSD-AGT-SUB`、INS/L1、DEL/L2、AUP/L3、独立 A402 均保留 | Synced as Candidate |
| A402 独立性 | INS、DEL、AUP 均可引用 A402，也可使用传统商户平台下单流程及 MCP/API 实现 | Synced as Candidate |
| `Payment-Needed` / `Payment-Proof` / `Payment-Validation` | 三者均为 Base64URL UTF-8 JSON；编码前采用 `protocol` + `method`；`Payment-Validation` 为成功响应中的可选 Header | Synced as Candidate |
| `method_id` | 标识具体支付方法；方法规范独立维护；可由 `CID-PCA-NEG` 协商 `method_id`、`psp_id`、`endpoint`、`method_schema_url` | Synced; Candidate naming/version contract implemented |
| 基础载荷 | 14 个共享字段语义保留；方法扩展不得改变基础字段语义 | Synced; Candidate field placement/requiredness implemented |
| 原请求重试 | 支付成功后对原资源或服务发起新请求并携带 Proof | Synced; Candidate fingerprint/idempotency rules implemented |
| Proof 验证 | 验证有效性、防重复履约以及 `trade_no` / `resource_id` 与当前请求一致性 | Synced as Candidate |
| 状态机 | 六个状态和允许转移已明确 | Synced; Candidate triggers and transition fixtures implemented |
| 错误恢复 | 十一类错误语义及重试方向已明确 | Synced; Candidate error schema/catalog implemented |
| INS/L1 | 五步支付流程；用户资金处理前逐笔核身；A402 履约是支付后接入流程 | Synced as Candidate |
| DEL/L2 | 四步支付流程；完整 IAC、本地预检和 PSP 权威核验；无需用户笔笔核身 | Synced as Candidate |
| AUP/L3 | 五步单次支付流程，可在任务周期内循环；使用 `BOUNDED` IAC；A402 接入细节不在 AUP 重复定义 | Synced as Candidate |
| 购物车与订单 | 商业交互可先做购物车确认，但支付请求以商户侧订单号及必要支付要素关联；A402 可由 `Payment-Needed` 返回订单/资源标识 | Synced; no full-cart wire requirement |

## 3. 支付宝产品事实边界

| 来源 | 当前处理 |
|---|---|
| [AI 按量付费产品页](https://aipay.alipay.com/callpay) | 支付宝产品事实主入口 |
| [AI 按量付费接入指南](https://aipay.alipay.com/docs/ai-receive/MACHINE_PAY.html) | 当前仓库最后产品核对为 2026-08-03；页面更新时间 `2026-07-31 11:54:36` |

完成版 ACT 协议与当前产品文档存在两项需要分层表达的差异：

- ACT 候选规定三类 Header 均使用 Base64URL；支付宝指南对 `Payment-Proof` 的文字写作 Base64。支付宝实现必须继续服从官网，差异记录为 Product Review，不把 ACT 事实降级为协议 Pending。
- ACT 候选定义可选 `Payment-Validation` Header；支付宝官网只公开服务端验凭结果，未定义同名 Header。Alipay Profile 只映射验证语义，不声称产品发送该 Header。

产品事实明细由[Alipay AI Pay 官方资料表](../../profiles/alipay-ai-pay/sources/README.md)维护；Core 不复制产品开户、沙箱和 API 操作手册。

## 4. 已由完成版协议关闭的旧 Pending

| 原 ID | 关闭结论 | 下游处理 |
|---|---|---|
| PD-2.1-001 | `Payment-Validation` 是验凭后的可选 HTTP Header | 产品是否暴露同名 Header由 Profile 映射 |
| PD-2.1-002 | 三类 Header 统一采用 Base64URL 编码的 UTF-8 JSON，并使用 `protocol` + `method` 两层结构 | HTTP Binding 同步；支付宝差异留 Product Review |
| PD-2.1-008 | 完成版协议不要求支付请求传完整购物车；传统流程使用商户侧订单号，A402 返回订单/资源标识 | 删除“完整购物车是否上送”的协议待决表述 |

## 5. Candidate 工程决议与剩余 Pending

2026-08-03 为完成当日开源 Candidate，仓库接受了[A402 Candidate 机器契约决议](../../docs/project/decisions/candidate-machine-contract-resolution-2026-08-03.md)。它关闭实现悬空，不冒充公开 DWG 治理：

| 原 ID | Candidate 处理 | 状态 |
|---|---|---|
| PD-2.1-003 | 稳定命名空间 `method_id` + 独立 SemVer `method_version`，三类载荷回显 | Candidate closed |
| PD-2.1-004 | 六状态公共投影 + 七个转移触发 + 结构化阶段结果 | Candidate closed |
| PD-2.1-005 | 规范化请求指纹；非安全方法另需业务幂等键；敏感 Header 不进入重放材料 | Candidate closed |
| PD-2.1-006 | 权威防重键、交付幂等键、原子占用和 Profile 声明保存截止时间 | Candidate closed |
| PD-2.1-007 | 最小订单/资源关联 + 可选 `commerce_confirmation`，不传完整购物车 | Candidate closed |
| PD-2.1-009 | 验凭、交付、履约确认和 TSD 证据保持四个独立事实 | Candidate closed |
| PD-2.1-010 | INS/L1 为可执行发布基线；DEL/L2、AUP/L3 保持 Validation-pending | Candidate closed |

正式 DWG 评审仍可接受、修订或替代上述选择；替代时必须发布新决议和新 Schema 版本，不得静默改写。

以下两项不属于最小 A402 机器包，继续保持 Pending：

| ID | 待决定事项 | 完成版协议已知边界与剩余问题 | 影响范围 | 需要确认 |
|---|---|---|---|---|
| PD-2.1-011 | `PSD-PMT-BND` 与支付宝钱包生命周期的准确映射 | 协议绑定语义明确；产品聚合生命周期不能整体等同于组件 | PSD、Profile、买方接入 | Profile |
| PD-2.1-012 | AUP 自主场景错误的标准机器表达 | AUP 复用 DEL 和 A402 错误语义；完成版未定义 AUP 专属错误对象/代码 | AUP、A402、错误词典 | ACT Core |

上述剩余事项映射到[A402 决策 Register](../../docs/project/decisions/a402-decision-register.json)。完成版协议已经明确的事项不得继续以“等待治理”为由阻塞候选同步；源文档没有规定的机器契约细节也不得凭空补全。

## 6. 仓库一致性结论

| 区域 | 本次结论 |
|---|---|
| `specs/2.1/` | 已切换为完成版《支付服务域》单一协议事实源；保持 Candidate / Non-normative |
| `bindings/http-a402/` | 同步三类 Header、Base64URL、两层载荷和可选 Validation；仍为 Preview |
| `profiles/alipay-ai-pay/` | ACT 语义与支付宝产品事实继续分层；不虚构产品 `Payment-Validation` Header |
| `quickstarts/` / `demos/` | 当前产品路径未因协议文本更新而改写；继续只按官网产品格式运行 |
| 决策与审计资料 | 关闭旧 PD-001/002/008，缩小剩余决策范围 |
| Schema / Conformance | Candidate JSON Schema、fixtures、validator、十一类错误和状态转移已实现；仍不冒充正式 Conformance |

项目级重构与发布追踪继续位于[项目修订状态](../../docs/project/revision-status.md)；本页只追踪 2.1 候选规范事实。
