# 支付宝 AI 付 Quickstart

> 状态：Preview / Non-normative  
> 接入基线：支付宝官方 Skill/CLI、HTTP 402、支付宝沙箱/OpenAPI  
> 产品资料核对：2026-08-08  
> ACT 兼容性：映射 ACT Core `2.1-candidate.1`；真实 Sandbox 兼容性尚未声明

这里是支付宝 AI 付在 ACT 开源项目中的产品级接入入口。仓库不重复实现支付宝钱包、收银台、沙箱或开放平台；Quickstart 只负责把 ACT 的机器支付语义连接到支付宝官网已经公开的产品能力。

## 一个闭环，两侧能力

| 接入方 | 获得的能力 | 公开接入方式 | 从这里开始 |
|---|---|---|---|
| 买方 Agent | 在用户授权下识别支付要求、执行支付并恢复原请求 | 支付宝官方 Payment Skill/CLI | [Agent 支付](agent-payment/README.md) |
| 卖方服务 | 机器可读地出账、验凭证、交付资源并确认履约 | HTTP 402 + 支付宝沙箱/OpenAPI | [AI 按量付费服务端](metered-rest-provider/README.md) |
| 双侧联调 | 验证从资源请求到履约确认的完整链路 | 官方 Skill/CLI + 真实 402 服务端 | [端到端 402](end-to-end-402/README.md) |

Agent 支付和 AI 按量付费不是两套孤立协议：前者赋予 Agent 支付能力，后者赋予卖方服务接受机器支付的能力。二者通过候选 A402 接入协议形成同一条机器支付链路。

## 推荐路径

1. 如果你开发 Agent，先完成 [Agent 支付 Quickstart](agent-payment/README.md)。
2. 如果你提供收费 API、MCP Tool 或 Skill，先完成 [AI 按量付费服务端 Quickstart](metered-rest-provider/README.md)。
3. 当买卖两侧分别就绪后，使用[端到端 402 Quickstart](end-to-end-402/README.md)完成沙箱验证和脱敏证据记录。

## “一键”具体指什么

| 级别 | 单命令入口 | 边界 |
|---|---|---|
| 本地 smoke | `npm --prefix code/examples/alipay/end-to-end-402 run local` | 不支付、不交付付费资源 |
| 买方安装 | `npx -y @alipay/agent-payment@latest install` | 官方安装器继续处理钱包与用户授权 |
| 卖方启动 | `./code/examples/alipay/metered-rest-provider/run.sh` | 需先完成官网开通并填写 `.env`；脚本测试、构建并启动 |
| 沙箱 E2E | 按[端到端步骤](end-to-end-402/README.md)执行 | 包含真实用户授权，不能设计为无人值守自动扣款 |

仓库把代码路径压缩为单命令，但不会把账号开通、用户授权、密钥管理或人工验证伪装成可静默自动化的步骤。

## 仓库与官网的责任边界

| 本仓库负责 | 支付宝官网与官方能力负责 |
|---|---|
| ACT 分层、产品映射、Binding 说明、最短接入代码和本地检查 | 产品开通、钱包授权、密钥管理、沙箱、支付执行、验凭证和履约 API |
| 明确本地测试与真实验证的边界 | 提供当前有效的产品流程、接口参数和运营规则 |

产品操作始终以公开官网为准：

- [支付宝 AI 付官网](https://aipay.alipay.com/callpay)
- [AI 钱包使用指南](https://aipay.alipay.com/wallet-guide)
- [AI 按量付费接入指南](https://aipay.alipay.com/docs/ai-receive/MACHINE_PAY.html)
- [支付宝 Payment Skills](https://github.com/alipay/payment-skills)

## 成功标准

本地测试通过只说明示例的解析、校验和控制流可运行，不代表已经接入支付宝产品。真实接入至少需要：

- 使用支付宝官方 Skill/CLI 或公开 OpenAPI，而不是复制 Mock；
- 完成官方授权或沙箱支付；
- 卖方通过官方接口验证支付凭证并确认履约；
- 对待处理中、失败、过期和重复请求有明确处理；
- 留存不可重放、无密钥和完整凭证的脱敏证据。

发布 Profile Preview 不要求本仓库复制或完成支付宝沙箱；开户、密钥、测试账号、沙箱 App 和支付操作统一引用官网。只有声明 `Alipay AI Pay Sandbox Verified` 时，才要求完成上述真实链路并提交脱敏证据。

协议与产品关系见 [Alipay AI Pay Profile](../../../integrations/profiles/alipay-ai-pay/README.md)，分层边界见 [ACT 项目框架](../../../docs/architecture/README.md)。
