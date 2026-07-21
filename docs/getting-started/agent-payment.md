# Agent 支付 Getting Started

> 状态：July Preview / Non-normative  
> 公开接入基线：支付宝官方 Wallet + Payment Skill/CLI

本指南面向需要让 Agent 在用户授权下完成支付的开发者。它解释 ACT 与支付宝 Agent 支付的衔接，不复制支付宝钱包开通和绑定教程。

## 1. 完成后你将得到什么？

完成公开产品接入后，你的 Agent 应能够：

- 检查支付宝支付能力是否可用。
- 在未开通或未绑定时引导用户完成官方授权流程。
- 识别支付宝收银台链接或 HTTP 402 付费要求。
- 在支付前向用户展示可理解的支付意图。
- 使用官方支付能力提交支付并查询结果。
- 在获得可信支付结果后恢复原任务。

本指南不会让仓库中的 Python Mock Demo 变成真实支付实现。

## 2. 前置条件

- 一个能够安装和加载支付宝官方 Skill 的 Agent 运行环境。
- 用户可以访问支付宝官方钱包授权和绑定页面。
- 只从支付宝官网或官方开源仓库安装 Skill。
- 如果要验证 HTTP 402，需要一个遵循[官网按量付费流程](https://aipay.alipay.com/docs/ai-receive/MACHINE_PAY.html)的收费资源。

支持范围和安装方式以[支付宝 AI 钱包使用指南](https://aipay.alipay.com/wallet-guide)为准。官方源码位于 [alipay/payment-skills](https://github.com/alipay/payment-skills)。

## 3. 使用官方路径安装和绑定

支付宝当前公开的 Agent 快速接入命令为：

```bash
npx -y @alipay/agent-payment@latest install
```

如果当前任务是独立开通或绑定钱包，按照[官方钱包指南](https://aipay.alipay.com/wallet-guide)完成：

1. 加载钱包与支付 Skill。
2. 检查支付能力状态。
3. 必要时申请开通。
4. 用户在支付宝页面完成身份核验和授权。
5. 将官方生成的短时绑定指令提交给 Agent。
6. 再次检查绑定结果。

这不是每笔支付的固定前置流程。进入收银台或 402 支付时，应直接调用官方支付 Skill/CLI 的对应支付命令，由支付命令处理钱包就绪或支付中开通状态；不要在每笔支付前额外插入 `check-wallet`。

> 绑定码、支付密码和身份核验信息属于敏感信息。ACT 实现、Demo、日志和测试夹具都不应记录或提交真实值。

## 4. ACT 四域覆盖

Agent 支付不是只属于 PSD。首期公开路径横跨四域，但不同责任由宿主 Agent、商户业务、支付宝产品和 ACT 实现共同承担：

| ACT 域 | 首期关系 | 主要承担方 |
|---|---|---|
| ADD | 捕获当前支付意图并取得用户逐笔确认；不要求长期委托 IAC | 宿主 Agent + 用户 |
| CID | 保留商品/资源、商户、金额、订单和支付能力选择上下文 | 商户业务 + 宿主 Agent |
| PSD | 钱包绑定、支付能力检查、用户确认支付和结果查询 | 支付宝官方 Skill/CLI |
| TSD | 关联意图、订单、支付结果和履约证据 | ACT 实现 + 各证据提供方 |

首期即使通过 HTTP 402 收到账单，用户逐笔确认后的支付执行仍按 `PSD-PAY-INS` 建模。402 交互框架是否应从 `PSD-PAY-AUP` 抽出供不同授权级别复用，属于协议修订问题。组件级说明见[双侧能力与 ACT 四域映射](../../profiles/alipay-ai-pay/domain-mapping.md#3-买方-agent-支付能力映射)。

## 5. ACT 接入责任

安装成功只代表 Agent 获得了产品能力。为了符合大会版 ACT/Profile 方向，Agent 还需要保留以下语义：

| 阶段 | Agent 责任 | 当前归属 |
|---|---|---|
| 能力检查 | 区分可用、需授权和暂时不可用 | Alipay Profile + Skill/CLI Binding |
| 支付要求识别 | 不把普通链接或错误响应误判为付款请求 | Binding |
| 支付意图 | 展示收款方、金额、商品/资源和过期时间等必要信息 | ACT Core 候选 + Profile |
| 用户授权 | 由官方产品完成身份与授权，不在本地伪造 | Alipay Product |
| 支付执行 | 只使用官方 Skill/CLI 返回结果 | Alipay Profile + Binding |
| 状态查询 | 对 pending/未知状态进行查询，不直接再次支付 | ACT Core 候选 + Profile |
| 任务恢复 | 支付成功后恢复原请求；失败时提供安全的下一步动作 | ACT Core 候选 |

详细映射见 [Agent Payment alignment](../../profiles/alipay-ai-pay/agent-payment-alignment.md)。

## 6. 两类支付入口

### 6.1 支付宝收银台链接

如果 Agent 的业务流程生成或接收到受支持的支付宝收银台链接，交由官方 Payment Skill 处理。商户的商品、订单和履约仍属于商户业务；支付宝支付能力负责付款动作及结果查询。

传统商户 Skill 与支付 Skill 的边界见[支付宝传统供给 Skill 支付说明](https://aipay.alipay.com/docs/skillpay.html)。

### 6.2 HTTP 402

当付费资源返回 `402 Payment Required` 和 `Payment-Needed` 时：

1. Agent 保留原始请求的方法、地址、Body 和必要 Header。
2. 官方支付能力处理账单和用户支付。
3. 官方 Skill/CLI 可以在内部携带 `Payment-Proof` 重试原请求，并把状态或资源返回给 Agent；宿主不应自行从日志抽取 Proof 拼接请求。
4. 资源服务方负责验证凭证并返回资源。
5. Agent 不在本地自行宣布凭证有效。

卖方责任见[AI 按量付费 Getting Started](metered-payment.md)。

真实 Skill/CLI 命令面和封装边界见[官方 Skill/CLI 行为核对](../../profiles/alipay-ai-pay/skill-cli-behavior-audit-2026-07-21.md)。

## 7. 验收清单

以下条件全部满足，才能将该路径记录为真实产品验证：

- [ ] Skill 来自支付宝官网、官方包或官方源码仓库。
- [ ] 钱包能力状态由官方能力返回，而不是本地配置写死。
- [ ] 未绑定时实际进入支付宝官方授权流程。
- [ ] 测试未在日志中暴露绑定码、支付密码或完整凭证。
- [ ] 支付前展示了收款方、金额和交易对象。
- [ ] 支付结果来自官方能力，并能区分 pending、success 和 failure。
- [ ] HTTP 402 场景保留并恢复原始资源请求。
- [ ] 没有使用 `impl/python/` 的 Mock 成功结果作为证据。

## 8. 常见恢复路径

| 情况 | 建议处理 |
|---|---|
| 钱包未开通或未绑定 | 进入官方钱包授权流程 |
| 绑定指令过期 | 按官网指引重新获取，不重复使用旧指令 |
| 支付状态未知 | 查询权威支付状态，不立即发起第二次支付 |
| 402 账单过期 | 向资源方请求新账单 |
| Skill/CLI 临时失败 | 保留原任务上下文，按官方结果决定重试或终止 |
| 用户拒绝支付 | 终止当前支付，不伪造成功或继续交付 |

候选错误和下一步动作见 [Error mapping](../../profiles/alipay-ai-pay/error-mapping.md)。

## 9. 下一步

- 验证买方和卖方完整链路：[端到端 402 验证](end-to-end-402.md)
- 实现 Product Profile：[Alipay AI Pay Profile](../../profiles/alipay-ai-pay/README.md)
- 查看产品当前能力：[支付宝 AI 付概览](https://aipay.alipay.com/docs/overview.html)
