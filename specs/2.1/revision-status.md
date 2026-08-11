# ACT 2.1 候选修订状态

> **状态：Active Candidate Working Draft Tracker / Non-normative**  
> 最后核对：2026-08-10（UTC+8）
> 本页记录协议来源、同步结果和剩余 Pending Decision，不是正式发布声明。

## 1. 协议事实源与同步证据

### 1.1 当前公开事实源

[ACT Protocol 官网](https://www.act-protocol.com/)是协议事实源。当前固定公开入口为[协议概览](https://www.act-protocol.com/documentation/overview)、[典型场景](https://www.act-protocol.com/documentation/scenarios)、[委托授权域](https://www.act-protocol.com/documentation/delegation)、[商业交互域](https://www.act-protocol.com/documentation/commerce)、[支付服务域](https://www.act-protocol.com/documentation/payment)和[信任服务域](https://www.act-protocol.com/documentation/trust)。机器可读入口、页面指纹和同步策略见 [`governance/protocol-sources.json`](../../governance/protocol-sources.json)。

本页后续列出的语雀元数据和正文哈希是 2026 年 8 月形成 Candidate 快照时的**历史维护证据**，不再是外部开发者阅读、核对或实现 ACT 的前置条件。官网页面发生变化时，必须先执行结构与语义差异评审，再更新 Candidate；不能用自动抓取结果直接覆盖规范正文。

> **Pending Publication Sync：** 2026-08-10 核对时，官网支付页尚未完整呈现仓库已接受的独立 `PSD-PAY-A402` Candidate 等最新细节。该差异等待官网后续更新；当前不回退 Candidate，也不宣称仓库与官网已经完全同步。

### 1.2 历史维护快照：支付服务域

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

该维护快照完整定义 PSD 六组件，并直接包含 A402、INS/L1、DEL/L2、AUP/L3、三类 Header、基础载荷、六态状态机和十一类错误语义。它用于说明本仓库 Candidate 的来源与演进；当前公开协议事实源已经切换为 ACT Protocol 官网。

### 1.3 历史维护快照：商业交互域

| 项目 | 本次核对 |
|---|---|
| 来源 | [商业交互域](https://yuque.antfin.com/hknzlf/fvle20/vn8s21q6cc7pmmon) |
| 文档 ID / slug | `545380139` / `vn8s21q6cc7pmmon` |
| 维护人 | 观岳 |
| `updated_at` | `2026-05-20T02:50:37.000Z` |
| `content_updated_at` | `2026-05-19T07:27:46.000Z` |
| `published_at` | `2026-05-19T09:56:04.000Z` |
| 字数 / 正文行数 | 6,701 / 361 |
| 正文 SHA-256 | `7a7259c4d2b6ea5bdd1ab3e88ad1be72b327558a0493293ed73db6e75d210113` |
| 与仓库上次状态比较 | 首次登记完整 CID 来源；仓库原先只维护 `CID-PCA-NEG` 支付连接边界 |
| 黄色修订范围 | 仅 `CID-PCA-NEG` 的“安全考虑”（语雀正文 292—297 行，标题及三段正文） |

该维护快照定义 CID 四组件、四类核心对象、目录最低信息、意图上下文传递、单/双向支付能力协商、安全校验和购物车确认。维护者于 2026-08-06 补充说明：黄色部分才是本轮修改点。因此四组件等内容按既有基线补齐，只有黄色安全段落记作协议修订增量。该记录现在只用于历史追溯；公开事实以 ACT Protocol 官网为准。

### 1.4 历史维护快照：委托授权域

| 项目 | 本次核对 |
|---|---|
| 来源 | [委托授权域](https://yuque.antfin.com/hknzlf/fvle20/fzy9k8wgpfgf6umt) |
| 文档 ID / slug | `545380123` / `fzy9k8wgpfgf6umt` |
| 维护人 | 观岳 |
| `updated_at` | `2026-05-19T09:55:55.000Z` |
| `content_updated_at` | `2026-05-19T07:27:33.000Z` |
| `published_at` | `2026-05-19T07:30:10.000Z` |
| 字数 / 正文行数 | 6,945 / 333 |
| 正文 SHA-256 | `bad030eca08f1b4b723a97fd3f53f2348922b00622f1d2a5d53c299797a6b0af` |
| 与仓库上次状态比较 | 首次登记完整 ADD 来源；仓库原先只维护 IAC 支付依赖边界 |
| 黄色修订范围 | `price_deviation_tolerance`、`price_deviation_action` 两个字段名中的 `deviation` |

该文档定义 ADD 三组件、ISR 数据字典、IAC 签发边界、封装无关规则和四态生命周期。本次补齐既有 ADD 基线，只有两个黄色字段名记作协议修订增量。

### 1.5 历史维护快照：典型场景与业务流程

| 项目 | 本次核对 |
|---|---|
| 来源 | [典型场景与业务流程](https://yuque.antfin.com/hknzlf/fvle20/yz11ev27zqtcgeeu) |
| 文档 ID / slug | `545380100` / `yz11ev27zqtcgeeu` |
| 维护人 | 观岳 |
| `updated_at` | `2026-05-20T02:49:30.000Z` |
| `content_updated_at` | `2026-05-19T07:30:00.000Z` |
| `published_at` | `2026-05-19T07:30:00.000Z` |
| 字数 / 正文行数 | 6,128 / 239 |
| 正文 SHA-256 | `41ef13fd14d2d7d87fca1237ab40912b80c387c4ff623e9e1ae6db0027159494` |
| 与仓库上次状态比较 | 首次登记并公开跨域场景指南 |
| 黄色修订范围 | 无黄色高亮；整篇按场景基线处理 |

场景文档用于解释 INS、平台/专属 Agent DEL 和 AUP 的四域组合，不凌驾于域正文。其组件表未列 `PSD-PAY-A402`，但正文使用 HTTP 402；仓库按完成版 PSD 保留独立 A402，并将该差异记录为来源版本差异而非删除组件。

### 1.6 历史维护快照：信任服务域

| 项目 | 可信存证 | 信用关联（新增子篇） |
|---|---|---|
| 来源 | [可信存证](https://yuque.antfin.com/hknzlf/fvle20/gcgkq98a1d7z63yz) | [信用关联](https://yuque.antfin.com/hknzlf/fvle20/uggov9ooo4g5tukx) |
| 文档 ID / slug | `545380294` / `gcgkq98a1d7z63yz` | `565985641` / `uggov9ooo4g5tukx` |
| 维护人 | 观岳 | 观岳 |
| `updated_at` | `2026-08-05T06:39:20.000Z` | `2026-08-05T06:39:10.000Z` |
| `content_updated_at` | `2026-08-05T06:39:20.000Z` | `2026-08-05T06:39:09.000Z` |
| `published_at` | `2026-08-05T06:39:20.000Z` | `2026-08-05T06:39:09.000Z` |
| 字数 / 正文行数 | 12,293 / 455 | 13,970 / 572 |
| 正文 SHA-256 | `d312af952b242e1d31af6a95e3dabc64ff4028686955e142a29f33c731f15282` | `1e024d74f813ff4ae41ce54e446f9f8ed5242927e0b8abb7fa722a641fcda3dd` |
| 与仓库上次状态比较 | 首次登记完整可信存证子篇；仓库原先只维护事件边界 | 首次登记新增信用关联子篇 |
| 黄色修订范围 | “可信存证是信任服务域的子篇之一” | 关联主体、核心对象/授权模式、`ASSOCIATED_CREDIT`、确认方式与责任边界等新增子篇关键语义 |

可信存证和信用关联是并列 TSD 子篇，不能再用前者代表整个信任服务域。当前来源没有提供可运行 ACT Trust Chain、信用模型或正式 wire Schema，仓库只同步语义 Candidate。

### 1.7 历史修订背景资料

[《ACT v2.1 协议修订需求点分析》](https://yuque.antfin.com/hknzlf/fvle20/dh5iwcigwa65hkds)只用于解释改名、拆分和历史演进，不是公开事实源，也不作为外部开发者的接入依赖。公开语义冲突以 ACT Protocol 官网对应域正文为准；官网尚未完成发布的差异保持 Pending Publication Sync。

后续同步只在对应域正文的更新时间、正文哈希、章节结构或正文内容实际变化时修改候选文本，不因每日任务制造无意义改动。

## 2. 本次协议变化与同步

### 2.1 支付服务域

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

### 2.2 商业交互域基线补齐

下表是因为开源仓库原先只有 `CID-PCA-NEG` 支付连接边界而进行的基线补齐，不代表这些内容都是本轮协议修改。

| CID 来源事实 | 公开候选处理 | 状态 |
|---|---|---|
| 四组件 | `CID-MER-CAT`、`CID-INT-XFR`、`CID-PCA-NEG`、`CID-CART-CFM` 均进入完整 CID 候选 | Synced as Candidate |
| 目录接口 | 固定商品/服务标识、名称、类目、价格和币种最低语义；不虚构统一调用协议 | Synced as Candidate |
| 意图传递 | 同步显式/隐式意图、约束、请求关联、动态更新、多商户和五类错误语义 | Synced as Candidate |
| 支付能力声明 | 同步 Agent Card、`act-payment-capability.json`、单向声明和双向协商语义 | Synced as Candidate; Schema pending |
| 协商结果 | 保留 `method_id`、`psp_id`、`endpoint`、`method_schema_url` 四项结果及来源校验要求 | Synced as Candidate |
| 购物车确认 | 同步规则前置检验、失败策略、订单级锁定和交易确认结果 | Synced as Candidate |
| 与 PSD 的关系 | CID 输出交易确认和支付能力协商结果；PSD 负责支付执行，不要求支付请求携完整购物车 | Synced as Candidate |
| 事件引用 | 保留 `act:commerce:decision-logged`、`act:commerce:cart-confirmed` 的跨域引用边界，不定义 TSD 事件结构 | Synced boundary only |

### 2.3 商业交互域黄色修订

| 黄色修订事实 | 公开候选处理 | 状态 |
|---|---|---|
| 能力声明来源 | 使用 `act-payment-capability.json` 前，应确认来自商户已声明的 `capability_url` | Synced as Candidate security requirement |
| 关键字段一致性 | 解析 `supported_methods` 时，宜校验 `psp_id`、`endpoint`、`method_schema_url` | Synced as Candidate security requirement |
| 失败关闭 | 来源无法确认或关键字段校验失败时，不得继续能力匹配或支付 | Synced as Candidate fail-closed requirement |
| 高亮段落字段拼写 | `capabilityurl`、`pspid`、`methodschemaurl` 回指同文既有下划线字段 | Editorially normalized; no new wire fields |

### 2.4 委托授权域基线与黄色修订

| ADD 来源事实 | 公开候选处理 | 状态 |
|---|---|---|
| 三组件 | `ADD-INT-ICS`、`ADD-IAC-ISS`、`ADD-IAC-LCM` | Synced as Candidate |
| ISR | 同步原始意图、基础字段、标准/私有扩展和 `SPECIFIED` / `BOUNDED` 语义；不虚构统一存在性或 Schema | Synced as Candidate; Schema pending |
| IAC | 同步待签名载荷、JCS、封装无关规则、推荐 VC-JWT 和状态引用 | Synced as Candidate; wire/envelope pending |
| 生命周期 | `Active`、`Suspended`、`Revoked`、`Expired` 及合法转移 | Synced as Candidate |
| 黄色字段 | 保留 `price_deviation_tolerance` 和 `price_deviation_action` | Synced as highlighted revision |

### 2.5 典型场景基线

| 场景来源事实 | 公开候选处理 | 状态 |
|---|---|---|
| 用户在场即时支付 | 无预签 IAC，使用 INS/L1 和资金处理前逐笔确认 | Synced as non-normative scenario |
| 平台/多租户定向委托 | `SPECIFIED` IAC，并验证平台 Agent 与具体委托人绑定 | Synced as non-normative scenario |
| 专属 Agent 定向委托 | `SPECIFIED` IAC 绑定唯一 Agent 身份；子账户可选 | Synced as non-normative scenario |
| 自主化委托 | `BOUNDED` IAC、任务周期多笔支付、每笔边界检查 | Synced as non-normative scenario |
| TSD | 事件异步非阻塞；支付、交付与履约完成分别形成事实 | Synced as cross-domain boundary |

### 2.6 信任服务域基线与新增子篇

| TSD 来源事实 | 公开候选处理 | 状态 |
|---|---|---|
| TSD 子篇结构 | 可信存证和信用关联并列，可信存证不再代表整个 TSD | Synced as highlighted revision |
| 可信存证五组件 | 事件、链下记录、链上锚点、签名核验、争议处理 | Synced as Candidate; machine contracts pending |
| 双层存证 | 链下完整记录 + 链上最小摘要；异步且不阻塞业务 | Synced as Candidate |
| 信用关联五组件 | 建立、映射、生命周期、验证、查询授权 | Synced as new Candidate subpart |
| 来源隔离 | 映射值必须标记 `ASSOCIATED_CREDIT`，不得冒充 Agent 独立信用或替代授权/支付风控 | Synced as Candidate |
| 状态与验证 | 五态生命周期；两级验证；最小披露与显式授权 | Synced as Candidate; wire contracts pending |

## 3. 支付宝产品事实边界

| 来源 | 当前处理 |
|---|---|
| [AI 按量付费产品页](https://aipay.alipay.com/callpay) | 支付宝产品事实主入口 |
| [AI 按量付费接入指南](https://aipay.alipay.com/docs/ai-receive/MACHINE_PAY.html) | 当前仓库最后产品核对为 2026-08-08；页面更新时间 `2026-08-07 21:51:27`；接入语义未发现变化 |

完成版 ACT 协议与当前产品文档存在两项需要分层表达的差异：

- ACT 候选规定三类 Header 均使用 Base64URL；支付宝指南对 `Payment-Proof` 的文字写作 Base64。支付宝实现必须继续服从官网，差异记录为 Product Review，不把 ACT 事实降级为协议 Pending。
- ACT 候选定义可选 `Payment-Validation` Header；支付宝官网只公开服务端验凭结果，未定义同名 Header。Alipay Profile 只映射验证语义，不声称产品发送该 Header。

产品事实明细由[Alipay AI Pay 官方资料表](../../integrations/profiles/alipay-ai-pay/sources/README.md)维护；Core 不复制产品开户、沙箱和 API 操作手册。

## 4. 已由完成版协议关闭的旧 Pending

| 原 ID | 关闭结论 | 下游处理 |
|---|---|---|
| PD-2.1-001 | `Payment-Validation` 是验凭后的可选 HTTP Header | 产品是否暴露同名 Header由 Profile 映射 |
| PD-2.1-002 | 三类 Header 统一采用 Base64URL 编码的 UTF-8 JSON，并使用 `protocol` + `method` 两层结构 | HTTP Binding 同步；支付宝差异留 Product Review |
| PD-2.1-008 | 完成版协议不要求支付请求传完整购物车；传统流程使用商户侧订单号，A402 返回订单/资源标识 | 删除“完整购物车是否上送”的协议待决表述 |

## 5. Candidate 工程决议与剩余 Pending

2026-08-03 为完成当日开源 Candidate，仓库接受了[A402 Candidate 机器契约决议](../../governance/decisions/candidate-machine-contract-resolution-2026-08-03.md)。它关闭实现悬空，不冒充公开 DWG 治理：

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

以下事项不属于最小 A402 机器包，或来源仍存在未定 wire 细节，继续保持 Pending：

| ID | 待决定事项 | 完成版协议已知边界与剩余问题 | 影响范围 | 需要确认 |
|---|---|---|---|---|
| PD-2.1-011 | `PSD-PMT-BND` 与支付宝钱包生命周期的准确映射 | 协议绑定语义明确；产品聚合生命周期不能整体等同于组件 | PSD、Profile、买方接入 | Profile |
| PD-2.1-012 | AUP 自主场景错误的标准机器表达 | AUP 复用 DEL 和 A402 错误语义；完成版未定义 AUP 专属错误对象/代码 | AUP、A402、错误词典 | ACT Core |
| PD-2.1-013 | CID 双向协商字段名 | 来源文字/示例存在 `currency` / `amount_currency`、`supported_methods` / `matched_methods` 差异 | CID Schema、Profile、实现 | 观岳 / CID 治理 |
| PD-2.1-014 | CID 能力声明机器契约 | 来源给出 Agent Card 与能力文件示例，但没有正式 Schema、版本、签名、认证、重定向和缓存规则 | CID-PCA-NEG、Binding、安全 | 观岳 / CID 治理 |
| PD-2.1-015 | CID 交易确认对象机器契约 | 来源明确结果语义，未定义对象版本、签名和完整 wire Schema | CID-CART-CFM、PSD 关联、TSD | 观岳 / CID 治理 |
| PD-2.1-016 | ADD ISR/IAC 机器契约 | 来源定义数据字典、存在性和封装边界，但未冻结 ISR/IAC Schema、版本、算法套件和状态查询协议 | ADD、DEL/AUP、TSD | 观岳 / ADD 治理 |
| PD-2.1-017 | TSD 可信存证机器契约 | 来源未冻结英文 wire 字段、事件 `event_body` Schema、JWS 载荷、节点接口、认证和隐私通道；ACT Trust Chain 公开可用性未说明 | TSD-ATT、跨域证据、实现 | 观岳 / TSD 治理 |
| PD-2.1-018 | TSD 信用关联机器契约 | 来源未冻结凭证/声明/授权/验证报文 Schema、算法套件、身份/状态解析和规则注册 | TSD-CRD、CID/PSD 风控引用 | 观岳 / TSD 治理 |

PD-2.1-011/012 继续映射到[A402 决策 Register](../../governance/decisions/a402-decision-register.json)；PD-2.1-013—018 由本页和[项目修订状态](../../governance/revision-status.md)追踪。场景组件表遗漏独立 A402 的差异已按“完成域正文优先”解决，不列为 Pending Decision。域正文已经明确的事项不得继续以“等待治理”为由阻塞候选同步；来源没有规定或存在冲突的机器契约细节也不得凭空补全。

## 6. 仓库一致性结论

| 区域 | 本次结论 |
|---|---|
| `specs/2.1/` PSD | 已切换为完成版《支付服务域》单一协议事实源；保持 Candidate / Non-normative |
| `specs/2.1/` CID | 已从支付协商边界扩充为语雀《商业交互域》四组件候选；不把来源示例升级为正式 Schema |
| `specs/2.1/` ADD | 已从 IAC 支付依赖边界扩充为语雀《委托授权域》三组件候选；不虚构 ISR/IAC Schema |
| `specs/2.1/` TSD | 已同步可信存证与新增信用关联两个子篇；不实现虚构 Trust Chain、信用模型或 wire Schema |
| 典型场景 | 已补齐四类跨域流程，并以完成域正文解决旧场景表遗漏 A402 的版本差异 |
| `integrations/bindings/http-a402/` | 同步三类 Header、Base64URL、两层载荷和可选 Validation；仍为 Preview |
| `integrations/profiles/alipay-ai-pay/` | ACT 语义与支付宝产品事实继续分层；不虚构产品 `Payment-Validation` Header |
| `code/examples/` / `code/web-client/` | 当前产品路径未因协议文本更新而改写；继续只按官网产品格式运行 |
| 决策与审计资料 | 关闭旧 PD-001/002/008，缩小剩余决策范围 |
| Schema / Conformance | Candidate JSON Schema、fixtures、validator、十一类错误和状态转移已实现；仍不冒充正式 Conformance |

项目级重构与发布追踪继续位于[项目修订状态](../../governance/revision-status.md)；本页只追踪 2.1 候选规范事实。
