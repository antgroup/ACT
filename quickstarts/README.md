# Quickstart

Quickstart 是连接官方产品或沙箱的最短路径，不等同于 Demo 中用于讲解流程的 Guided Preview。

支付宝 AI 付的产品级说明、接入顺序和官网边界见 [支付宝 AI 付 Quickstart](alipay/README.md)。

| 目标 | 从这里开始 | 真实外部依赖 |
|---|---|---|
| 本地理解 402 挑战与拒绝假凭证 | [端到端 402 本地 Golden Path](alipay/end-to-end-402/README.md#0-先跑本地非支付闭环) | 无；不支付、不交付付费内容 |
| 赋予买方 Agent 支付宝支付能力 | [Agent 支付](alipay/agent-payment/README.md) | 官方 `@alipay/agent-payment` 安装器和用户授权 |
| 让 REST 资源接受 Agent 支付 | [AI 按量付费服务端](alipay/metered-rest-provider/README.md)；凭证配置后 `./run.sh` | 支付宝沙箱应用、服务注册和开放 API |
| 验证买卖两侧完整链路 | [端到端 402](alipay/end-to-end-402/README.md) | 上述两条路径和一次用户授权的沙箱支付 |

本地单元测试通过只证明本地协议处理逻辑可运行。真实接入声明还需要官方 Skill/CLI、支付宝沙箱验凭证、履约确认和脱敏证据。
