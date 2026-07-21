# Alipay Agent Payment Skill/CLI 行为核对（2026-07-21）

> 状态：Completed source audit / Runtime validation pending  
> 核对对象：`alipay/payment-skills` 默认分支公开内容  
> 用途：确定买方公开 Binding 的真实接入形态，不把仓库 Demo 当成产品接口

## 1. 核心结论

当前官方 `alipay-payment-skill` 不是一个只返回 `Payment-Proof` 的薄 API。它通过 `alipay-bot` CLI 编排完整 402 买方工作流：保存本轮账单和原始请求、传入支付意图摘要、发起支付、查询状态、恢复原请求、透传资源，并在符合条件时发送买方履约确认。

因此，July Preview 的买方公开基线应建模为**工作流级 Skill/CLI Binding**：

- ACT/Profile 仍解释账单、授权、支付、凭证、验款和履约语义。
- Skill/CLI Binding 可以封装多个协议步骤，不要求宿主 Agent 直接读写完整 Proof。
- 验收不能只检查某个 CLI 命令是否成功，必须检查其保存和恢复的交易上下文是否对应同一笔请求。
- 如果未来提供更细粒度 SDK/API，应作为新的 Binding，不改变 Core 语义。

## 2. 公开行为映射

| 官方 Skill/CLI 行为 | 对接入契约的影响 | 状态 |
|---|---|---|
| `alipay-payment-skill` 同时覆盖收银台与 HTTP 402 | Agent 支付不是只针对某一种卖方资源形态 | `PUBLIC-FACT` |
| 402 第一条支付命令为 `402-buyer-pay`，禁止预先执行 `check-wallet` | 支付命令内部处理钱包就绪；独立钱包检查不能成为每笔支付前置步骤 | `PUBLIC-FACT` |
| `402-buyer-pay` 必须携带本轮 `--intent-summary` | ADD/CID 的用户意图与资源请求摘要必须进入 Binding | `PUBLIC-FACT` |
| 必须完整保存本轮 `Payment-Needed`，禁止解码、改写或复用旧文件 | Binding 必须保持产品账单完整性和本轮作用域 | `PUBLIC-FACT` |
| 必须保存触发 402 的 URL、方法、Body 和自定义 Header | Binding 负责恢复原始资源请求 | `PUBLIC-FACT` |
| POST 的支付和查询必须使用相同 `-m/-d/-H` | 支付状态查询与资源恢复共享原请求上下文 | `PUBLIC-FACT` |
| CLI 的用户可见状态和资源输出需要原样传递 | 宿主 Agent 不能自行追加“支付成功”等结论 | `PUBLIC-FACT` |
| 待确认路径可能使用 `tradeNo` 或 `outShakeNo` 查询 | 两者用途不同；`outShakeNo` 不是履约交易号 | `PUBLIC-FACT` |
| 查询成功后 CLI 可直接返回资源 | Skill/CLI Binding 可能封装 Proof 提交、卖方验款和资源重试 | `PUBLIC-FACT` |
| 资源返回且本次输出包含 `tradeNo` 时执行 `402-buyer-fulfillment-ack` | 与卖方指南的履约确认责任可能重叠 | `PRODUCT-REVIEW` |
| 支付命令和查询输出必须来自实际 CLI，禁止模拟或使用用户粘贴结果 | 本地 Demo、历史输出或伪造结果不能作为验收证据 | `PUBLIC-FACT` |

## 3. 版本与制品核对

2026-07-21 的只读 npm 元数据与 tarball 静态检查结果：

| 对象 | 观察结果 | 结论 |
|---|---|---|
| 官网安装命令 | 使用 `@alipay/agent-payment@latest` | 每次验证必须记录解析出的实际版本 |
| npm `latest` | `1.0.18`，integrity 为该版本独立 SHA-512 值 | 当前真实安装入口不是仓库 Skill 中声明的 `1.0.12` |
| GitHub main 的 Skill metadata | 声明安装 `@alipay/agent-payment@1.0.12` 及对应 integrity | 与 npm latest 存在版本漂移，不能用 main 代替 installed artifact |
| npm 1.0.18 tarball | 仅包含 `dist/cli.js`、`bin/install-payguard.js`、`package.json` | 安装包是安装器/CLI，不是完整 Skill 内容快照 |
| npm package repository 字段 | 指向发布仓库，不是 `alipay/payment-skills` | npm 制品、公开 Skill 源码和实际安装结果需要分别追踪 |

从 tarball 静态内容可以观察到安装配置由 CLI 获取，但不执行安装器无法确认最终下载的 Skill 版本和内容。因此本次只得出“版本必须分层记录”的结论，不把 GitHub main 行为直接宣称为 npm latest 的运行结果。

## 4. 真实公开命令面

| 目的 | 当前公开命令 | 关键约束 |
|---|---|---|
| 发起 402 支付 | `alipay-bot 402-buyer-pay` | 必须提供 session、Payment-Needed 文件、原资源 URL 和 intent summary；POST 还需原方法/Body/Header |
| 查询并恢复 402 请求 | `alipay-bot 402-query-payment-status` | 根据本轮 `tradeNo` 或特定 `outShakeNo` 选择参数，继续携带原请求信息 |
| 买方履约确认 | `alipay-bot 402-buyer-fulfillment-ack` | 只使用本次 CLI 输出的 `tradeNo`；不得使用 `outShakeNo` |
| 普通收银台支付 | `alipay-bot submit-payment` | 与 402 命令是不同 Binding 流程 |
| 普通收银台查询 | `alipay-bot query-payment-status` | 不用于 402 查询 |

命令参数会随官方包演进，ACT 仓库只记录能力和约束，不复制完整 Skill 操作手册。执行时始终以官方仓库和安装包内的 `SKILL.md`、references 为准。

## 5. 对当前文档的校正

### 5.1 钱包检查

钱包状态检查可以用于独立的开通和诊断，但实际支付流程不得在 `submit-payment` 或 `402-buyer-pay` 前固定插入 `check-wallet`。支付命令会处理钱包就绪或支付中开通状态。

### 5.2 Proof 可见性

逻辑协议仍包含 `Payment-Proof`，但宿主 Agent 不一定直接获得或操作 Proof。官方 CLI 可以在内部提交 Proof、重试原请求并只把资源或状态返回给 Agent。

因此：

- Core/Profile 测试可以验证 Proof 语义。
- Skill/CLI Binding 测试应验证 CLI 输入、输出和卖方关联证据。
- 接入指南不应要求开发者从 CLI 输出抽取完整 Proof 再手工拼接请求。

### 5.3 履约确认

公开资料同时出现：

1. 卖方接入指南要求资源返回后由商家调用 `alipay.aipay.agent.fulfillment.confirm`。
2. 买方 Skill 在资源获取后定义 `402-buyer-fulfillment-ack`。

目前无法仅凭公开材料确认二者是否调用同一产品接口、是否允许重复调用、谁是最终责任方，以及是否存在不同用途。端到端实现不得自行删掉任意一侧；应在 Sandbox 中记录实际调用和幂等结果，并提交产品确认。

## 6. 新增验证项

| ID | 验证问题 | 所需证据 |
|---|---|---|
| CLI-001 | npm 安装器、实际安装后的 Skill 与公开仓库内容如何对应 | npm 版本/integrity、安装后 Skill 内容哈希和源码提交 |
| CLI-002 | `402-buyer-pay` 是否对宿主隐藏完整 Proof | 脱敏 CLI 结构化输出和卖方收到的 Header 特征 |
| CLI-003 | GET、POST、Body 和自定义 Header 是否原样恢复 | 卖方请求日志摘要和请求哈希 |
| CLI-004 | pending 后使用 `tradeNo` 与 `outShakeNo` 的实际分支 | 脱敏 CLI 状态与查询命令结果 |
| CLI-005 | CLI 获取资源后是否总会执行 buyer fulfillment ack | CLI 输出/调用证据 |
| CLI-006 | buyer fulfillment ack 与 seller fulfillment confirm 是否幂等或重复 | 同一 `tradeNo` 的双侧调用结果 |
| CLI-007 | CLI 原样输出是否足以形成结构化 Binding 结果 | 不同状态下的脱敏输出夹具 |

## 7. 对大会版本的约束

- 买方 Quickstart 应调用官方 Skill/CLI，不重写一套 Proof 处理库。
- 端到端 Quickstart 应把官方 CLI 作为买方驱动器，把官网 402 方案作为卖方实现基线。
- ACT Adapter 的首期工作是准备安全输入、保存关联上下文、解析允许的结果和生成证据，而不是替代官方 CLI 支付逻辑。
- 在 CLI-005、CLI-006 完成前，履约确认责任保持 `PRODUCT-REVIEW`。
- 在真实 CLI 输出夹具完成前，不冻结 Skill/CLI Binding 的结构化输出 Schema。
- 发布证据必须分别记录 npm 安装器版本、实际安装后的 CLI 版本、Skill 内容版本/哈希和公开源码提交；不得只写 `latest`。
