# ACT 2.1 Candidate 当前发布说明

> 状态：Active / Non-normative；快照日期：2026-08-03

本页定义当前仓库可发布内容和允许主张。机器可读判定以 [`release-readiness.json`](release-readiness.json) 为准。

## 分级发布目标

| 目标 | 内容就绪 | 允许主张 | 独立阻塞 |
|---|---|---|---|
| ACT Candidate Publication | 支付服务域、A402 Candidate 文本、Schema、Fixture、错误目录和校验器 | `ACT 2.1 Candidate Working Draft / Non-normative` | 法务、安全渠道、公开仓库和干净发布快照 |
| Alipay Profile Preview | 产品映射、Preview Schema、Binding 和 Quickstart | `Alipay AI Pay Profile Preview / Sandbox validation pending` | 与 Candidate 相同的公开发布治理项 |
| Alipay Sandbox Verified | 以上内容加官方沙箱端到端证据 | 仅限证据记录版本和范围的 `Sandbox Verified` | 官方产品配置、密钥、真实测试和脱敏证据 |
| ACT SEP Candidate | Candidate 内容加正式治理及独立实现验证 | `ACT SEP Candidate` | 正式表决和 clean-room / 独立实现 |

官方沙箱不是 ACT Candidate 或 Alipay Profile Preview 的前置条件。仓库不实现或复制支付宝沙箱；开户、凭证、测试账号和产品操作始终引用 [AIPay 官网](https://aipay.alipay.com/callpay)。只有声称支付宝真实互操作或 Sandbox Verified 时，才必须提供官网沙箱证据。

## 当前完成范围

- `specs/2.1/` 已形成支付服务域优先的 Candidate 文本，所有内容保持 Candidate / Non-normative。
- A402 已有最小机器契约、有效与无效 Fixture、错误目录和本地校验器。
- Alipay AI Pay Profile 已有 `0.9-preview.1` 字段、生命周期、错误、Binding 和三份产品 Preview Schema。
- Quickstart、Demo 和本地测试严格区分协议、产品和演示层；本地 Preview 不产生真实支付成功主张。
- 产品待复核项已按影响范围记录在 `profiles/alipay-ai-pay/profile-review-status.json`，不再整体阻塞 Profile Preview。

## 尚未满足的发布条件

以下事项不能由仓库代码自行决定：

- 法务确认版权主体、双许可证分配以及 CLA 或 DCO 策略；
- 确认真实的私密安全报告渠道和责任人；
- 确认公开代码仓库目标与发布权限；
- 形成干净、经评审且通过公开 CI 的发布提交。

真实 Sandbox Verified 还需要有效的支付宝应用、商户及服务配置、应用私钥、支付宝公钥，以及真实闭环的脱敏证据。SEP Candidate 另需正式治理表决和独立实现验证。

在上述条件完成前，不得使用 `Stable`、`Recommendation`、`ACT 2.1 Conformance` 或 `Production Certified`。

## 验证命令

```bash
python3 scripts/check_repository.py
python3 scripts/validate_a402_contract.py
python3 scripts/release_readiness.py --target act-candidate-publication
python3 scripts/release_readiness.py --target alipay-profile-preview
./scripts/verify.sh
```

发布门禁返回 blocked 时，应读取具体 gate；不能把 Sandbox Verified 的外部阻塞扩大成 Candidate 或 Profile Preview 的内容阻塞。
