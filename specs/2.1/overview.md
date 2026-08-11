# ACT 2.1 公开候选概览

> **状态：Candidate Working Draft / Non-normative**  
> **不是正式发布版本，不得用于声明 ACT 2.1 Conformance。**  
> 候选基线：2026-08-06；官方发布入口最后核对：2026-08-10（UTC+8）

本目录保存委托授权域（ADD）、商业交互域（CID）、支付服务域（PSD）和信任服务域（TSD）的公开 Candidate 快照，并以 PSD 的一键式接入作为当前可执行主轴。公开包不包含 ACT 2.0 目录。[ACT Protocol 官网](https://www.act-protocol.com/)是协议事实源；仓库内容始终以 Candidate / Non-normative 形式提供，不替代官网发布。

## 1. 事实来源与优先级

1. [ACT 协议概览](https://www.act-protocol.com/documentation/overview)是四域结构、参与方和跨域术语的上位公开来源。
2. ADD、CID、PSD 与 TSD 分别以官网[委托授权域](https://www.act-protocol.com/documentation/delegation)、[商业交互域](https://www.act-protocol.com/documentation/commerce)、[支付服务域](https://www.act-protocol.com/documentation/payment)和[信任服务域](https://www.act-protocol.com/documentation/trust)为事实来源。
3. 官网[典型场景与业务流程](https://www.act-protocol.com/documentation/scenarios)用于解释四域组合；与域正文冲突时，以对应域正文为准。
4. 历史维护文档、更新时间和正文指纹只用于证明本仓库 Candidate 的演进过程，不再是外部开发者核对协议的前置条件。
5. 官网更新会触发自动漂移检查；维护者必须先评审结构、正文和语义差异，再更新 Candidate 与来源快照。
6. 当前官网支付页尚未完整呈现仓库已接受的独立 A402 Candidate 等最新细节；在官网更新并完成差异评审前，不得宣称二者已经完全同步，也不得因此回退 Candidate。
7. 支付宝产品字段、接口、签名、编码、沙箱和当前产品流程，以[支付宝 AI 按量付费](https://aipay.alipay.com/callpay)及其[官方接入指南](https://aipay.alipay.com/docs/ai-receive/MACHINE_PAY.html)为产品事实来源。
8. 产品事实只进入 Product Profile，不反向覆盖 ACT Core；官网协议没有规定的 wire 细节继续记录为 Pending Decision。

来源版本、正文指纹和逐项同步状态见[修订状态](revision-status.md)。

## 2. PSD 候选组件

完成版《支付服务域》定义以下六个组件：

| 类型 | 候选组件 | 当前候选含义 |
|---|---|---|
| 支付工具 | `PSD-PMT-BND` | 建立受限的支付工具引用，避免 Agent 直接接触原始账户信息 |
| 账户隔离 | `PSD-AGT-SUB` | 为特定 Agent 提供可选的专属子账户、密钥绑定和生命周期管理 |
| 支付场景 | `PSD-PAY-INS` / L1 | 用户实时在场，资金处理前逐笔确认 |
| 支付场景 | `PSD-PAY-DEL` / L2 | 人预先决定明确标的，Agent 在有效 IAC 边界内执行 |
| 支付场景 | `PSD-PAY-AUP` / L3 | 人预先授权目标与边界，Agent 在 `BOUNDED` IAC 内自主决策和执行 |
| 支付接入 | `PSD-PAY-A402` | 独立的 HTTP 402 支付要求、证明、验证和资源履约接入协议 |

`PSD-PAY-INS`、`PSD-PAY-DEL`、`PSD-PAY-AUP` 都可以引用 A402，或使用相应 MCP/API 接口。A402 不替代支付工具准备、用户确认、IAC、额度、商户范围、支付方式或子账户约束。

`CID-PCA-NEG` 是支付能力协商的跨域依赖，不是 PSD 的第七个组件。ADD、CID 和 TSD 已作为独立 Candidate 域公开，但完成 PSD 一键接入不等于实现全部 ADD/TSD 组件；开发者应按场景选择所需域能力。

## 3. CID 候选组件

| 候选组件 | 当前候选含义 |
|---|---|
| `CID-MER-CAT` | 商品和服务发现结果的最低机器可读信息，不统一目录传输协议 |
| `CID-INT-XFR` | 意图上下文、请求关联、候选返回、动态更新和错误语义 |
| `CID-PCA-NEG` | 单向声明或双向协商支付方式、PSP、端点和方法 Schema |
| `CID-CART-CFM` | 规则前置检验、订单级锁定和交易确认结果 |

完整范围见[商业交互域公开候选](domains/commerce-interaction.md)。来源没有提供正式 JSON Schema 的部分不得由示例代码补造。

## 4. ADD 与 TSD 候选组件

| 域/子篇 | 候选组件 | 当前边界 |
|---|---|---|
| ADD | `ADD-INT-ICS`、`ADD-IAC-ISS`、`ADD-IAC-LCM` | 完整语义 Candidate；暂无正式 ISR/IAC Schema、封装或状态查询协议 |
| TSD / 可信存证 | `TSD-ATT-EVT`、`TSD-ATT-OFF`、`TSD-ATT-OCA`、`TSD-ATT-SVF`、`TSD-ATT-DSP` | 完整语义 Candidate；仓库不实现 ACT Trust Chain |
| TSD / 信用关联 | `TSD-CRD-ASC`、`TSD-CRD-MAP`、`TSD-CRD-LCM`、`TSD-CRD-VER`、`TSD-CRD-AUTH` | 新增子篇 Candidate；不实现信用评分、授信或产品风控 |

完整范围见[委托授权域公开候选](domains/authorization-delegation.md)、[信任服务域公开候选](domains/trust-services.md)和[典型场景与业务流程](scenarios.md)。

## 5. 开源接入主路径

首期一键式接入以支付宝当前可验证的 L1 路径为主：

```text
PSD-PMT-BND + PSD-PAY-INS + PSD-PAY-A402
    + HTTP A402 Binding
    + Alipay AI Pay Profile
    + 官方 Skill/CLI 与 OpenAPI
```

开发者入口分四级，避免把本地预览误称为真实支付接入：

| 级别 | 目标 | 入口 |
|---|---|---|
| Local smoke | 一条命令理解 402，并确认假 Proof 不会交付 | [端到端本地 Golden Path](../../code/examples/alipay/end-to-end-402/README.md) |
| Buyer install | 使用支付宝官方安装器获得买方支付能力 | [Agent 支付 Quickstart](../../code/examples/alipay/agent-payment/README.md) |
| Seller bootstrap | 配置凭证后，以一个启动命令运行卖方 402 服务 | [按量付费服务端 Quickstart](../../code/examples/alipay/metered-rest-provider/README.md) |
| Sandbox E2E | 连接官方 Skill/CLI、沙箱验凭和履约 API，记录脱敏证据 | [端到端 402 Quickstart](../../code/examples/alipay/end-to-end-402/README.md) |

产品开通、钱包授权、密钥和沙箱由支付宝官方能力负责，不能由仓库静默代办；仓库负责把代码初始化、启动、验证和责任边界压缩到最短路径。

## 6. 分层边界

| 层次 | 负责 | 不负责 |
|---|---|---|
| ACT 2.1 Core 候选 | ADD/CID/PSD/TSD 的跨产品语义；PSD 提供当前可执行主路径 | 支付宝专有字段、API 名称和开户流程 |
| HTTP A402 Binding | Header 承载、原请求关联、HTTP 重试行为 | 决定用户授权级别 |
| Alipay AI Pay Profile | 支付宝字段、RSA2、验凭和履约接口映射 | 将产品行为改写为通用 Core 规则 |
| Quickstart / Demo | 展示和验证已声明的 Core、Binding、Profile 组合 | 创造协议结论或实现独立支付沙箱 |

支付宝官网沙箱只作为外部产品能力引用；本仓库不重复实现。

## 7. 当前候选文件

- [委托授权域完整候选](domains/authorization-delegation.md)
- [支付服务域完整候选](domains/payment-services.md)
- [商业交互域公开候选](domains/commerce-interaction.md)
- [信任服务域完整候选](domains/trust-services.md)
- [典型场景与业务流程](scenarios.md)
- [A402 接入协议候选](a402/specification.md)
- [商业交互到支付的连接规则](domains/commerce-payment-negotiation.md)
- [A402 候选可测试断言](a402/assertions/README.md)
- [协议源修订状态与待决定事项](revision-status.md)

当前未建立 ACT 2.1 通用消息 Schema。基线中的字段清单、状态转移和错误类别可以作为 Candidate 语义被继承，但字段是否必填、线上编码、错误对象、版本和标准错误码仍需治理决定。候选断言不能用于正式兼容声明。

返回[规范导航](../README.md)。
