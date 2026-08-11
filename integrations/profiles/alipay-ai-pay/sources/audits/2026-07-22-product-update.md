# Alipay AI Pay 官网更新核对（2026-07-22）

> 状态：Completed source audit / Sandbox validation pending  
> 核对时间：2026-07-22  
> 用途：记录官网当日更新对 Profile、Quickstart 和大会验证的影响

## 1. 结论

官网更新强化了“一条机器支付闭环、两侧产品能力”的接入路线，未改变本项目主架构：

- 买方仍通过 `@alipay/agent-payment` 获得 Agent 支付能力；
- 卖方 AI 按量付费仍使用 HTTP 402、`Payment-Needed`、`Payment-Proof`、`payment.verify` 和 `fulfillment.confirm`；
- 卖方新增明确的 Agent 自动集成推荐入口 `@alipay/alipay-aipay`；
- 一站式接入页已经提供完整沙箱接入与联调路径，ACT 仓库只需引用。

因此大会 Quickstart 应保留“官方 Skill/CLI + 可审查的手动服务端实现”两条互补路径：官方工具降低产品接入成本，本仓库代码用于解释 ACT/Profile 映射、控制流和安全门槛。

## 2. 新确认的公开事实

| 事实 | 官网状态 | 仓库动作 |
|---|---|---|
| 买方安装命令为 `npx -y @alipay/agent-payment@latest install` | Agent 支付产品页公开 | 保持买方 Quickstart |
| 卖方推荐安装命令为 `npx -y @alipay/alipay-aipay@latest install` | AI 按量付费接入指南和接入页公开 | 在卖方 Quickstart 引用，不复制工具实现 |
| 沙箱向导同时展示应用公钥和支付宝公钥 | 接入页公开 | 将验签变量改名为 `ALIPAY_ALIPAY_PUBLIC_KEY_FILE`，保留旧名兼容 |
| 当前服务类型显示 Restful 接口、回调接口，Skill 为后续扩展 | 接入页公开 | 大会卖方技术基线保持 HTTP 402 |

## 3. 尚未关闭的差异

| ID | 差异 | 当前处理 |
|---|---|---|
| AP-001 | 字段表称 `amount` 为“最小货币单位”，账单示例和服务注册页面使用 `0.01 CNY` / `0.01 元` | 不做单位换算；按控制台注册价格原字符串执行并记录沙箱结果 |
| AP-002 | `Payment-Needed` 明确为 Base64URL，`Payment-Proof` 文案仍写 Base64 | 用真实官方 Skill 产生的数据验证，协议草案不得提前冻结 |
| AP-003 | `client_session` 出现在 Proof 和验款入参，但必填条件仍不清晰 | Runbook 设置停止条件并记录真实错误码 |
| AP-009 | 买方 fulfillment ack 与卖方 fulfillment confirm 的关系未在卖方指南中解释 | 沙箱记录双侧实际调用，不自行删除任一侧 |

## 4. 对大会执行的影响

- `ACT-OSR-020` 的产品操作直接引用官网；仓库只维护 ACT/Profile 验收补充，真实验证仍未完成。
- Profile 的公开产品快照更新到 2026-07-22。
- Quickstart 不存储官网显示的测试账号、密钥或二维码。
- Demo Replay 只能来自真实沙箱通过后的脱敏事件，不能根据官网示例手工制作。
