# 开源就绪度评审（Open-Source Readiness Review）

> 状态：Active / Non-normative（指导后续修订，不改变协议语义、组件编号与 Schema）

> **2026-08-03 收敛说明：** 完成版[《支付服务域》](https://yuque.antfin.com/hknzlf/fvle20/dve0b9g2u1t3cs33)是单一协议事实源。A402 Candidate 决策、三类 Header Schema、fixtures、validator、十一类错误和状态转移已经完成；本文后续未逐段改写的“Core Schema 缺失”“九项决策待定”等内容仅保留为历史发现，不代表当前状态。当前状态以[分级发布门禁](../releases/release-readiness.json)和[项目修订状态](../revision-status.md)为准。
> 评审日期：2026-07-28；支付域基线纠偏与实施更新：2026-07-30；July Preview 发布门禁更新：2026-07-31
> 评审范围：协议规范清晰度、开发者接入体验、Agent 机器可消费性、开源治理与架构、与标杆协议对比
> 对照标杆：Google A2A、IBM BeeAI ACP、Anthropic MCP、x402、Stripe Agent Toolkit
> 关联回溯：本文是 [`repository-audit.md`](repository-audit.md) 的延续；前者校正工程事实，本文评估「能否作为合格开源协议被采纳」

---

## 0. 摘要（TL;DR）

**结论：Core / Binding / Product Profile / Quickstart 的分层架构合理。2026-08-03 起，正确主轴是“完成版支付服务域协议 + 支付宝产品事实”，修订分析只作历史追溯；开源目标是让开发者快速接入支付服务域。**

纠偏后的三项核心结论：

1. **PSD 内容基线曾不完整，现已纠偏** —— 2.1 Candidate 已对齐完成版协议，包含 `PSD-PMT-BND`、`PSD-AGT-SUB`、INS/L1、DEL/L2、AUP/L3 和独立 A402；公开 2.0 已删除。
2. **A402 Candidate 机器契约已经冻结** —— JSON Schema、字段分布、`method_id`、请求指纹、幂等/防重放、六态触发、错误对象和恢复动作均已形成 Non-normative Candidate；正式 DWG/SEP ratification 仍未完成。
3. **开源接入路径已完成，产品验证分层处理** —— 仓库负责本地 smoke、买方/卖方入口、preflight 和证据规则；支付宝沙箱、账号、密钥及支付执行统一引用官网。真实闭环只阻塞 `Sandbox Verified` 声明，不阻塞 ACT Candidate 或 Profile Preview。

治理、法务、第二 Product Profile 和正式 Conformance 仍是发布成熟度问题，但不应取代“PSD 完整性 + L1/A402 一键接入”的近期主任务。

> 修订原则：本文档不指定协议语义的最终形态，只提出「修订必须解决的问题」与「可验证的验收准则」。语义冻结由 `specs/2.1` 修订议题推进。

### 0.1 复核结论

本评审对问题发现的方向基本合理，尤其是 A402 缺少 Core 机器契约、真实接入断层、顶层状态不透明、仓库卫生和法务未决。但原修订建议不能原样执行，需做以下校正：

1. **以完成版协议为单一语义事实源。** [《支付服务域》](https://yuque.antfin.com/hknzlf/fvle20/dve0b9g2u1t3cs33)已经整合本轮修订；[v2.1 修订方案](https://yuque.antfin.com/hknzlf/fvle20/dh5iwcigwa65hkds)只保留为演进背景和差异追溯。
2. **删除公开旧版，不删除有效语义。** 旧版目录、Schema、示例和迁移草案继续退出公开包；仍有效的 PSD 组件、对象、流程、状态和错误语义在 2.1 中显式重述。
3. **不能用工程修订替代完成版协议没有规定的决定。** A402 Candidate 已通过显式 Candidate 决策固定 `method_id`、字段必填性、幂等键和错误对象；CID discovery、`endpoint` 信任、`method_schema_url` 缓存/完整性和 L2/L3 扩展仍保持 Pending，不由 Quickstart 或支付宝产品事实反向决定。
4. **测试层级不等于规范强度。** `documentation` / `integration` / `end-to-end` 描述验证环境，不能机械映射为 RFC 2119 的 MAY / SHOULD / MUST。
5. **法务、基金会托管、npm 发布和第二 Product Profile 需要新授权或外部协调。** 仓库可以准备材料和验收门槛，但不能由一次文档修订自行宣布完成。

因此，本文的正确定位是：**发现清单有效，但执行计划必须拆成“立即工程修复 / 协议决策门槛 / 外部授权阻塞”三类。**

### 0.2 经复核的修订计划与本轮状态

| Workstream | 本轮动作 | 状态 | 退出条件 |
|---|---|---|---|
| R-PSD 支付域协议同步 | 登记完成版协议源；同步六组件、对象、INS/DEL/AUP 流程和 A402 Header/字段/状态/错误语义 | **Completed as Candidate** | 自动检查阻止组件或来源再次丢失 |
| R-ONBOARD L1/A402 接入 | 以 L1 + A402 为首期主路径；区分 smoke、buyer、seller、sandbox E2E；产品沙箱统一引用官网 | **Completed for open-source Preview；Sandbox Verified pending** | ACT/Profile 可独立发布；真实兼容声明必须有脱敏闭环证据 |
| R0 仓库卫生与公开入口 | 忽略构建产物；角色化公开证据审批；收敛 README；暴露 Normative / Production certified | **Completed** | 仓库检查可阻止回归 |
| R1 可执行追踪 | 修复断言锚点和 ID 扩展性；增加前置条件、输入、预期输出、Feature 与测试追踪 | **Completed for current candidate scope** | 所有断言来源锚点可解析；已有测试有稳定 ID |
| R2 产品契约去硬编码 | 把当前支付宝 `Payment-Needed` 字段集合迁到明确的 Product Profile Preview Schema，Quickstart 读取该单一来源 | **Completed as Preview** | Schema 自身、消费关系和状态标签受检查 |
| R3 非 Node 首次体验 | 增加 curl 三联块和 `.http` 文件 | **Completed for local non-payment path** | 请求、402 解码、假 Proof 拒绝可复制 |
| R4 A402 Core 机器契约 | Candidate 决策 Register、三类载荷 Schema、fixtures、validator、错误词典和状态机 | **Completed for Candidate；formal ratification pending** | 正式 DWG/SEP 评审和版本批准 |
| R5 法务和中立治理 | 确认版权主体、CLA 入口、委员会和可能的基金会路径 | **Blocked on maintainer/legal authority** | 可执行 CLA、明确版权声明和公开治理决定 |
| R6 SDK / Discovery / TCK | 错误词典已完成；SDK、Discovery 和独立实现 TCK 不阻塞 Working Draft 发布 | **Post-publication / SEP Candidate scope** | 至少两个独立实现共享同一 Core 契约 |
| R-RELEASE 分级收口 | ACT Candidate、Profile Preview、Sandbox Verified、SEP Candidate 使用独立门禁 | **Implemented；public publication governance blocked** | 法务、安全渠道、公开远端和干净发布 Commit 均通过 |

---

## 1. 评审方法与维度

本次评审从两个用户视角与一个外部对标维度展开：

| 视角 | 回答的核心问题 |
|---|---|
| **Agent 视角** | 一个 LLM/Agent 拿到 402 响应，能否自洽地解析出「付多少 / 付给谁 / 用什么 proof / 如何重试」并执行？ |
| **开发者视角** | 想接入支付能力的 API/Agent 开发者，能否 5 分钟跑通、能否快速建立 normative/illustrative 心智模型？ |
| **外部对比** | 相对 A2A / MCP / x402 / Stripe，在「开源架构与治理 / 开发者接入 / Agent 可消费性」上处于什么位置？可借鉴什么？ |

每个维度的发现分为 **严重问题（S）** 与 **改进建议（W）**，最终汇入第 5 节的分级修订项。

---

## 2. Agent 视角发现（机器可读性 & 可执行性）

### 严重问题

**A1. 缺少规范化的 402 Core Challenge Schema**
完成版协议已明确三个 Header 的 Base64URL UTF-8 JSON 编码、两层结构和可选 `Payment-Validation`，因此原先将其整体排除出 Core 的结论已失效。仍缺的是 Header 字段分布/必填、版本化 Core Schema、类型/格式约束及跨方法扩展规则；当前可消费 Schema 仍只有 Alipay Product Profile Preview，不能冒充 Core。
*影响：Agent 无法依据 ACT 规范推断未知卖方的账单结构，只能依赖产品文档硬编码字段。*

> 2026-08-03 状态：**已解决为 Candidate**。Core Schema 位于 `specs/2.1/schemas/a402/`；支付宝产品字段继续由独立 Profile Preview Schema 管理。

**A2. 「用什么 proof、如何重试」曾未冻结**
A402 Candidate 现已固定 `method_id` 与独立版本、Proof/request fingerprint 关联、非安全方法幂等键、原请求恢复和重复履约处理。产品支付授权、验凭证及查询仍由 Product Profile 指向官方实现。

> 2026-08-03 状态：**已解决为 Candidate**。正式规范强度与 SEP ratification 仍由治理决定。

**A3. Assertion catalog 不可被 Agent 直接消费做自检**
`specs/2.1/assertions/a402-core-assertions.json` 的 `statement` 是自然语言句子，无 JSONPath、无 schema 引用、无输入输出契约；`source` 锚点全部失真（指向 `#a402-的独立性`，实际标题是 `## 1. 独立性`）。`assertion-catalog.schema.json:41` 把 ID 锁死在 `^A402-CAND-[0-9]{3}$`，无法扩展到 CID/INS/DEL/AUP。
*影响：Agent 按锚点回查规范会定位失败；断言无法编译为可执行检查。*

> 2026-08-03 状态：**已完成当前 Candidate 可执行追踪**。8 条 A402 Candidate 断言均链接检查或测试，PSD 组件库存断言也已接入仓库检查；独立跨实现 TCK 属 SEP Candidate 范围。

**A4. 错误码映射曾不可机器读**
Core Candidate 现有 11 类机器错误、retryability 和 `valid_next_actions`；Alipay Profile 另有机器可读产品错误映射，并由仓库检查保证只引用现存 Core 错误 ID。官方 Skill/CLI 的精确运行时错误仍需沙箱证据，不阻塞 Profile Preview。

**A5. Capability Discovery 缺失 —— Agent 无法服务发现**
历史能力声明 Schema 没有规定 Agent 如何获取它；该 Schema 已退出公开包，但 `method_schema_url` 的拉取、缓存、校验语义和 `endpoint` 的安全约束仍未在 2.1 Candidate 中定义。
*影响：Agent 无法在浏览阶段机读发现卖方支付能力，也无法判断可信方。*

**A6. JSON Schema 内部不一致、约束不足**
- 金额格式不一致：`instant-payment.schema.json` 任意小数位 vs `delegated-payment-payload.schema.json` 最多 2 位；
- `error_message` 无长度/字符集约束（提示注入风险）；
- `payment_token` 与 `subaccount_info` 互斥关系未用 `oneOf` 表达；
- 所有 schema 缺 `$comment`，`description` 多是产品黑话叙述；
- `payment-capability.schema.json:5` 出现零宽字符乱码 `定﻿义`。

> 2026-07-30 状态：这些旧版 Schema 已退出公开包，不再是当前实现基线。对应的渠道中立约束仍需在 2.1 canonical source 决策后重新设计。

### Agent 视角一句话
**当前 2.1 已同时具有人类候选文本和 A402 Candidate 机器契约；它仍是 Non-normative Working Draft，不是 SEP Candidate 或正式 Conformance。**

---

## 3. 开发者视角发现（清晰度 & 接入体验）

### 做得好、应保留

- **本地 Golden Path 定位清晰**：`README.md:8-14` 一条 `npm run local` 零凭证跑通，`quickstarts/alipay/end-to-end-402/README.md:7-17` 讲清「只验证假 Proof 不交付」安全边界。
- **仓库/官网责任边界表**（`quickstarts/alipay/README.md:26-39`）把「本仓库负责 / 官网负责」二分干净，是新人最友好的资产。
- **资产五分类定义**（Scenario / Demo / Quickstart / Reference Implementation / Conformance Suite，`README.md:109-121`）有效区分「能跑」与「能声明合规」。
- **Profile 状态标签自检表**（`profiles/alipay-ai-pay/README.md:42-51`：PUBLIC-FACT / PRODUCT-REVIEW / PROTOCOL-PENDING / VALIDATION-PENDING）。

### 严重问题

**D1. Golden Path 之后是断崖。**
跑通后下一步「真实接入」全部跳出仓库（买方交给 `npx @alipay/agent-payment install`，卖方要求「已开通产品/已注册 service_id/已配沙箱/已备私钥」）。顶层 README 在分流页前没显式提示「跑通 Golden Path ≠ 接入支付」。

> 本轮状态：顶层和 Quickstart 已明确本地路径不支付、不交付，也不构成真实接入；真实产品路径仍天然依赖官方账号、授权和沙箱。

**D2. 入口爆炸。** 仅「我在开发 Agent」栏抛 7 条链接，首屏「下一步」总数超 15 条，Getting Started 文档互相 cross-link。新人迷路。

> 本轮状态：**已解决顶层首屏问题**。README 每个角色只保留主路径和官方资料，其余进入延伸阅读；Getting Started 与 Quickstart 保留“角色选择”和“可运行资产”两种不同职责。

**D3. normative 维度未在顶层暴露。** `release-manifest.json` 已有 `normative` / `production_certified` 字段，但 README「当前文档状态」表曾未呈现这两列。新人看见「Candidate / Preview」无法判断「能否据此声称合规」。

> 本轮状态：**已解决**。README 已增加两列及“当前建议实现基线”。

**D4. 缺关键接入资产：**
- 无可直接复制粘贴的 `curl` 三联块（请求 → 402 响应样例 → 带 Proof 重试）；
- 无 `.http` / Postman / Bruno collection（非 Node 开发者被排除）；
- **无 SDK** —— 想在自己 Agent 框架嵌入 402 解码，得自己实现 Payment-Needed 解码、Proof 构造；
- 无交互式 API 文档 / OpenAPI 在线浏览；
- 无工程化错误排查表（「看到 X 报错 → 检查 Y」）；
- 无版本兼容矩阵（`release-manifest.json:81-96` 的 `resolved_version: null` 等于「版本不固定自己 lock」）。

> 2026-08-03 状态：**当前 Candidate/Preview 接入范围已解决**。本地路径已有 curl 三联块、`.http` 文件、Core Schema/错误词典和 Profile Preview Schema/错误映射；provider-neutral SDK、OpenAPI 在线浏览和公开包供应链属于后续采用率增强，不阻塞本次源码发布。

**D5. 仓库卫生事故级问题：**
- `.gitignore` 漏了 `.tmp/`、`output/`、`target/`（Maven 构建产物）。当前虽未追踪，但下一次 `git add .` 极易误提交 `.tmp/aipay-two-slide-ppt/`、`output/AIPay_AI付_AI收_两页介绍初稿.pptx`、`quickstarts/.../target/*.jar`。
- **疑似内部花名泄漏**：`docs/getting-started/end-to-end-402.md:136-137` 与 `end-to-end-evidence-template.md:136-137` 出现「观岳确认 / 念箴确认」「Alipay Profile owner: 念箴 / ACT protocol owner: 观岳」，与社区/DWG 治理路径冲突，传递「需找内部人确认」信号。
- Quickstart 残留「大会 Demo」措辞（`quickstarts/alipay/agent-payment/README.md:70-74`），属内部演示脚本改写的场景化残留。

> 本轮状态：`.gitignore` 和自动检查已覆盖 `.tmp/`、`output/`、`target/`；公开接入与证据文档已改用角色和公开评审记录。修订来源、历史决策和发布项目文档仍保留事实性责任人。

**D6. 法务卡点：** `README.md:159-161` 许可证「计划采用 CC BY 4.0 / Apache 2.0，版权主体仍需维护者确认」；`CONTRIBUTING.md:135,255` CLA「仍待维护者确认」。两者使外部企业无法声明 `SPDX-License-Identifier`、无法走合规放行 —— 属「尚未准备好被外部依赖」的硬阻塞。

---

## 4. 外部对比发现（A2A / MCP / x402 / Stripe）

### 4.1 对比矩阵

| 维度 | A2A | MCP | x402 | Stripe Agent Toolkit | **ACT（当前）** |
|---|---|---|---|---|---|
| 仓库结构 | spec+docs monorepo，SDK/samples 兄弟 repo | 多仓：spec + 10 SDK + servers + inspector + conformance | polyglot monorepo（TS/Py/Go/Java + specs + contracts） | monorepo 多语言 + 内嵌 MCP server | 单仓混合 specs/bindings/profiles/quickstarts |
| machine-readable schema | **Protobuf canonical**（`a2a.proto`，JSON Schema 为生成产物且不 commit） | 106 KB JSON Schema（TypeScript `schema.ts` 为 normative 源） | v2 每扩展含 JSON Schema + EIP-712 typed-data | OpenAPI 自带 | A402 Candidate 采用 JSON Schema 2020-12，覆盖三类 Header、错误、状态和 Workflow manifest；仍为 Non-normative |
| 5-min quickstart | `uv run` 启 demo agent + CLI client | `@mcp.tool()` 装饰器，5 分钟建 server | **「加一行 `paymentMiddleware()`」** | `pip install` 设 key | Java/Maven 偏重；无 provider-neutral 极简路径 |
| normative / 版本化 | Protobuf 唯一 normative + 协议 semver（评审时公开版本 **1.0.0**）+ ADR | BCP 14 / RFC 2119 大写关键字 + dated revisions + SEP | semver + 版本字段 | 日期版本 | 自定义 stage（working-preview/candidate），**未用 RFC 2119** |
| SDK/conformance | 多语言官方 SDK；Proto 生成派生模型 | 多语言 SDK + **独立可执行 conformance（scenario + CI）** | 多语言 `@x402/*` + facilitator | Python / TypeScript、多 agent 框架 SDK | Java quickstart + JS/Python 校验；A402 8/8 Candidate 断言可追踪，尚非独立跨实现 TCK |
| 治理 | **Linux Foundation**，8 席多公司 TSC | **LF AAIF** | **x402 Foundation（40 家成员，含 Visa/Stripe）** | Stripe 单家（反例） | 单家（蚂蚁/支付宝），**无基金会托管计划** |

### 4.2 三条成熟路径（ACT 尚未完成）

1. **中立基金会托管** —— A2A / MCP / x402 都已进入 Linux Foundation；Stripe 单家是反例（因 API 标准化强仍被采纳）。ACT 需明确「蚂蚁孵化 → 中立基金会」路径与毕业标准。
2. **可执行 conformance TCK** —— MCP 已有 scenario + CI 形式的独立 conformance；A2A 和 x402 也通过权威模型、SDK 与测试资产降低漂移。**ACT 当前只有候选断言与少量追踪测试，尚不能称为 TCK**。
3. **x402 facilitator 独立验证角色** —— `/verify` 链下校验（亚秒）+ `/settle` 链上结算解耦。ACT 把 Proof 验证耦合在「卖方 → PSP」里，不利于跨 PSP 复用与建立 TCK。

### 4.3 x402 是最直接的差距参照
x402 v2 使用 `PAYMENT-REQUIRED` / `PAYMENT-SIGNATURE` / `PAYMENT-RESPONSE` 三个 Header（Base64 JSON），并通过 SDK 自动完成“首次 402 → 构造支付载荷 → 重试”的两次 HTTP 请求流程。它通常不要求传统服务账户/API Key，但客户端仍需要可签名钱包或等价支付能力。这套「Agent 原生」体验是 ACT A402 Binding 值得参考的实现基准，但两者支付模型和信任假设不同，不能直接复制字段。

外部事实来源（评审快照 2026-07-28）：

- [A2A Protocol Specification](https://github.com/a2aproject/A2A/blob/main/docs/specification.md)
- [MCP specification repository](https://github.com/modelcontextprotocol/modelcontextprotocol)
- [MCP Conformance Test Framework](https://github.com/modelcontextprotocol/conformance)
- [x402 HTTP 402](https://docs.x402.org/core-concepts/http-402) 与 [Facilitator](https://docs.x402.org/core-concepts/facilitator)
- [Linux Foundation：A2A](https://www.linuxfoundation.org/press/linux-foundation-launches-the-agent2agent-protocol-project-to-enable-secure-intelligent-communication-between-ai-agents)、[MCP/AAIF](https://www.linuxfoundation.org/press/linux-foundation-announces-the-formation-of-the-agentic-ai-foundation)、[x402 Foundation](https://www.linuxfoundation.org/press/linux-foundation-announces-operational-launch-of-x402-foundation-to-standardize-internet-native-payments-for-ai-agents-and-applications)

---

## 5. 分级修订项（按优先级）

> 验收准则统一要求：每项修订须能被 `scripts/verify.sh` 或一个独立检查脚本客观验证，避免问题静默回归。

### P0 — 开源发布前必须解决（阻断合规与卫生）

> 2026-08-03 状态：P0-0、P0-1、P0-2、P0-4 已完成到 Candidate；P0-3 仍受版权主体和贡献机制确认阻塞。公开发布继续受私密安全渠道、公开远端和干净发布快照阻塞；支付宝沙箱不再阻塞 ACT Candidate/Profile Preview。

| ID | 修订项 | 问题来源 | 验收准则 |
|---|---|---|---|
| **P0-0** | **对齐完成版 PSD 协议源**：追踪完成版《支付服务域》的元数据与哈希；2.1 显式包含 PMT-BND、AGT-SUB、INS、DEL、AUP、A402，以及协议对象/流程/Header/状态/错误语义 | 基线纠偏 | (a) 单一协议事实源可追踪；(b) 六组件在 Core 与 Profile 一致；(c) 删除公开 2.0 后无隐式旧目录依赖；(d) 自动检查阻止回归 |
| **P0-1** | **完成 A402 剩余机器契约决策**：保留完成版协议已明确的 Header 编码/形态、基础字段语义、六状态和错误语义；关闭 `method_id`、字段分布、重试和幂等 Pending 后，再选择 JSON Schema 或 Protobuf 等 canonical source。决定前只允许 Product Profile Preview Schema，不得冒充 Core | A1, A2, A6, §4.3 | (a) 决策记录可追踪；(b) canonical source 选择明确；(c) 三类载荷候选 Schema、fixtures 和 validator 同步生成或校验；(d) Candidate 语义与 wire-level Pending Decision 明确分开 |
| **P0-2** | **修仓库卫生**：`.gitignore` 补 `.tmp/` `output/` `target/`；公开 onboarding/evidence 使用 `ACT Core spec owner` / `Alipay Profile maintainer` + 公开评审；去 Quickstart 的「大会 Demo」措辞 | D5 | (a) 构建产物不进入 `git status`；(b) 公开 onboarding 无内部姓名；(c) 检查脚本防止关键字回归 |
| **P0-3** | **落地法务**：确认版权主体并补 `SPDX-License-Identifier`；落实 CLA 流程 | D6 | (a) 每个 schema/代码文件有 `SPDX` 标头或仓库级 LICENSE 明确 copyright line；(b) CONTRIBUTING 指向可执行的 CLA 签署入口（哪怕是「待基金会托管后切换」的明确声明） |
| **P0-4** | **README 暴露 normative 维度**：把 `release-manifest.json` 的 `normative` / `production_certified` 两列搬进「当前文档状态」表；并加一行明确「当前建议实现基线」 | D3, A1 旁证 | (a) README 状态表含 normative/production_certified 列；(b) 有一行明确对外「现在该实现哪个版本」 |

### P1 — 接入体验与 Agent 可消费性（决定采用率）

| ID | 修订项 | 当前状态 | 验收准则 |
|---|---|---|---|
| **P1-1** | curl 三联块、`.http` 文件和可复制本地路径；provider-neutral SDK 作为后续独立发布物 | **Completed for source Preview；SDK deferred** | 本地路径有「请求 → 402 解码 → 带假 Proof 重试」；公开 SDK 另过供应链和版本授权 |
| **P1-2** | capability discovery 决策提案：比较 `.well-known`、A2A Agent Card 与 CID；不发布未经治理的发现约定 | **Decision proposal complete；protocol decision deferred** | `protocol-decision-brief.md` 和 `commerce-payment-negotiation.md` 明确选择面、安全问题和 Pending 范围 |
| **P1-3** | Core 错误词典与 Alipay Product Preview 错误映射机器可读化 | **Completed for Candidate/Preview** | Core error schema/catalog 可校验；产品映射只引用有效 Core error ID；运行时标识只阻塞 Sandbox Verified |
| **P1-4** | 精简角色入口并拆分主路径与延伸阅读 | **Completed** | README 每个角色保留一条主路径和一条官方资料，仓库检查阻止入口回归 |
| **P1-5** | assertion catalog 增加有效锚点、通用 ID、输入输出和可执行追踪 | **Completed for A402 Candidate** | 8/8 A402 断言链接检查或测试；完整独立 TCK 留到 SEP Candidate |

### P2 — 协议清晰度与治理（决定能否成为标准）

| ID | 修订项 | 问题来源 | 验收准则 |
|---|---|---|---|
| **P2-1** | **统一术语与组件命名**：固定 `PSD-PAY-AUP` 权威名（消除 A2A / AUP / Autonomous Delegated Payment 三译名）；同步 overview 框图与 PSD 域规范的组件清单，补定义 `BOUNDED IAC` / `ASL` | 第 2 轮规范review S2/S3/I2/I6 | (a) 术语表有单一权威名 + 别名；(b) overview 与域规范组件数一致；(c) 未定义术语全部补定义或标注 Pending |
| **P2-2** | **给 2.1「最小可实现子集」**：标出 6 条不变量与「安全下限」5 条为「可原型化基线」，区分「可原型」vs「需治理决策」 | 第 2 轮规范review S1/I3 | overview 有「可原型化」标注区，列出可作基线的不变量 |
| **P2-3** | **在进入规范候选阶段时引入 RFC 2119/BCP 14**，由治理决定哪些安全不变量成为 MUST；Non-normative 工作草案继续使用“候选安全下限”避免伪装成已发布规范 | 第 2 轮规范review S5/I5/S2 | (a) 规范阶段与要求语言一致；(b) 每个 MUST 有可执行测试；(c) 向后兼容影响有明确记录 |
| **P2-4** | **引入 ADR 机制**：先提供模板；只有真实决定被接受后，才把 A402 编码、版本和兼容选择记录为 `docs/project/decisions/adr-00x`，不得用占位 ADR 冒充决定 | §4.2 A2A 借鉴 | 模板、编号规则和索引存在；每份 ADR 都链接实际讨论与批准记录 |
| **P2-5** | **形成中立治理提案**：由维护者/TSC 讨论基金会托管、多供应商委员会和仓库拆分；未获批准前不得在 GOVERNANCE 中写虚假时间表。独立验证者作为协议议题评估，而非照搬 x402 | §4.2, §4.3 | 公开提案、决策人、里程碑和毕业标准经治理接受 |
| **P2-6** | **引入第二个真实 Product Profile 或独立实现**：不使用虚构 mock PSP 证明跨产品；测试用 provider-neutral fixture 只能证明结构可测试 | §4.3 | 第二个公开产品/实现由独立维护方提供，且通过相同 Core 测试 |

---

## 6. 修订路线图（建议三阶段）

### 阶段一：可被外部安全引用（完成 P0）
**目标**：外部企业 clone 仓库后，能获得完整 PSD Candidate、法务能判断适用范围、仓库卫生无事故，并能判断「现在该实现哪个版本」。
**退出条件**：P0-0、P0-2、P0-4 完成；P0-1 有决策记录和 canonical-source 方案；P0-3 获法务确认。
**产出**：内容可作为 `ACT 2.1 Candidate Working Draft / Non-normative`；完成法务、安全渠道、公开远端和发布快照后方可实际公开发布，且不可声称正式合规。Product Profile Preview Schema 不能替代 Core Schema。

### 阶段二：有竞争力的接入体验（完成 P1）
**目标**：开发者能运行 provider-neutral 的安全本地路径；Agent 能消费经决定的错误词典与 capability discovery；assertion catalog 开始向 TCK 演进。
**退出条件**：本次源码 Candidate/Preview 的 P1-1、P1-3、P1-4、P1-5 已通过；P1-2 已形成可治理提案且保持 Pending。provider-neutral SDK 和独立实现不作为源码 Preview 阻塞，公开包发布仍需另过供应链与版本审批。
**产出**：可发布为开发者 Preview；只有满足 CONTRIBUTING/GOVERNANCE 的正式治理与独立实现门槛后，才能称 SEP Candidate。

### 阶段三：真正的开放标准（完成 P2）
**目标**：术语统一、normative 关键字到位、ADR 治理、中立基金会路径明确、第二个 profile 证明跨产品。
**退出条件**：P2-1 ~ P2-6 的治理项被正式接受；至少一份可运行 TCK 覆盖全部规范 MUST；独立实现和发布投票达到治理门槛。
**产出**：是否发布 ACT 2.1 Stable、是否启动基金会托管，由正式治理决定，本文不预先宣布。

---

## 7. 应保留的既有资产（修订时勿删）

1. 诚实的状态标注（Non-normative / Pending Decision / 修订中）—— 早期开源协议里少见，应保留。
2. `specs/2.1/revision-status.md` 的完成版协议源、PSD 同步状态、Pending Decision 和仓库一致性结论 —— 清晰划清「协议事实 / 修订历史 / 产品事实」三者关系。
3. 仓库/官网责任边界表、资产五分类、Profile 状态标签表 —— 三张优秀发明，建议在 README 更高位置复用。
4. `release-manifest.json` 的机器可读状态、依赖和兼容关系—— 应继续与公开包实际内容保持一致。

---

## 8. 评审回顾点

每完成一个修订项后，按以下问题自查是否真正解决根因（非仅补丁）：

- 该修订是否让 Agent **按规范**（而非读代码）就能完成消费？
- 该修订是否让外部企业**法务可放行**且能判断**版本兼容性**？
- 该修订是否降低了「此协议 = 支付宝内部协议开源镜像」的感知？
- 该修订是否能在 `scripts/verify.sh` 中被**客观验证**，防止静默回归？

如对某项根因存疑，回到 §2/§3 对应「严重问题」条目复核，避免修订偏离发现。
