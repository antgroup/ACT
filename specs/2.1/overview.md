# ACT 2.1 支付服务域公开候选概览

> **状态：Candidate Working Draft / Non-normative**  
> **不是正式发布版本，不得用于声明 ACT 2.1 Conformance。**  
> 候选基线：2026-08-03；协议来源最后核对：2026-08-03（UTC+8）

本目录以支付服务域（Payment Services Domain，PSD）为当前开源主轴。公开包不包含 ACT 2.0 目录。2026-08-03 更新的《支付服务域》已经整合本轮修订，因此 2.1 Candidate 直接对齐该完整协议事实源，不再把它解释为“旧基线 + 另一份增量稿”。

## 1. 事实来源与优先级

1. PSD 2.1 的范围、组件、对象、流程、Header、载荷、状态和错误语义，以观岳维护并于 2026-08-03 完成修订的[《支付服务域》](https://yuque.antfin.com/hknzlf/fvle20/dve0b9g2u1t3cs33)为协议事实来源。
2. [《ACT v2.1 协议修订需求点分析》](https://yuque.antfin.com/hknzlf/fvle20/dh5iwcigwa65hkds)只保留为修订背景和差异追溯资料；当它与完成版《支付服务域》不一致时，以完成版为准。
3. 支付宝产品字段、接口、签名、编码、沙箱和当前产品流程，以[支付宝 AI 按量付费](https://aipay.alipay.com/callpay)及其[官方接入指南](https://aipay.alipay.com/docs/ai-receive/MACHINE_PAY.html)为事实来源。
4. 产品事实只进入 Product Profile，不反向覆盖 ACT Core；完成版协议没有规定的 wire 细节继续记录为 Pending Decision。

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

`CID-PCA-NEG` 是支付能力协商的跨域依赖，不是 PSD 的第七个组件。当前开源主路径只维护支付闭环需要的 CID/ADD/TSD 引用边界，不以补齐其他域作为 PSD 发布前置条件。

## 3. 开源接入主路径

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
| Local smoke | 一条命令理解 402，并确认假 Proof 不会交付 | [端到端本地 Golden Path](../../quickstarts/alipay/end-to-end-402/README.md) |
| Buyer install | 使用支付宝官方安装器获得买方支付能力 | [Agent 支付 Quickstart](../../quickstarts/alipay/agent-payment/README.md) |
| Seller bootstrap | 配置凭证后，以一个启动命令运行卖方 402 服务 | [按量付费服务端 Quickstart](../../quickstarts/alipay/metered-rest-provider/README.md) |
| Sandbox E2E | 连接官方 Skill/CLI、沙箱验凭和履约 API，记录脱敏证据 | [端到端 402 Quickstart](../../quickstarts/alipay/end-to-end-402/README.md) |

产品开通、钱包授权、密钥和沙箱由支付宝官方能力负责，不能由仓库静默代办；仓库负责把代码初始化、启动、验证和责任边界压缩到最短路径。

## 4. 分层边界

| 层次 | 负责 | 不负责 |
|---|---|---|
| ACT PSD Core 候选 | 支付工具、账户隔离、L1/L2/L3 场景、通用对象、状态和恢复语义 | 支付宝专有字段、API 名称和开户流程 |
| HTTP A402 Binding | Header 承载、原请求关联、HTTP 重试行为 | 决定用户授权级别 |
| Alipay AI Pay Profile | 支付宝字段、RSA2、验凭和履约接口映射 | 将产品行为改写为通用 Core 规则 |
| Quickstart / Demo | 展示和验证已声明的 Core、Binding、Profile 组合 | 创造协议结论或实现独立支付沙箱 |

支付宝官网沙箱只作为外部产品能力引用；本仓库不重复实现。

## 5. 当前候选文件

- [支付服务域完整候选](payment-services-domain-spec.md)
- [A402 接入协议候选](a402-binding.md)
- [商业支付能力协商候选](commerce-payment-negotiation.md)
- [A402 候选可测试断言](assertions/README.md)
- [协议源修订状态与待决定事项](revision-status.md)

当前未建立 ACT 2.1 通用消息 Schema。基线中的字段清单、状态转移和错误类别可以作为 Candidate 语义被继承，但字段是否必填、线上编码、错误对象、版本和标准错误码仍需治理决定。候选断言不能用于正式兼容声明。

返回[规范导航](../README.md)。
