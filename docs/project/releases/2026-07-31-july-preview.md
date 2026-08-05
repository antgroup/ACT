# ACT 2.1 PSD July Preview 候选发布说明

> 历史快照说明：本页记录 2026-07-31 的 July Preview。2026-08-03 完成版《支付服务域》已取代当时的“双来源”假设；当前状态以 [`specs/2.1/revision-status.md`](../../../specs/2.1/revision-status.md) 为准。

> 状态：Prepared / Publication blocked  
> 候选日期：2026-07-31  
> 允许声明：ACT 2.1 PSD Candidate Working Draft / July Preview / Non-normative  
> 禁止声明：Stable、Recommendation、正式 Conformance、Production Certified

## 1. 结论

July Preview 的候选内容和本地工程验证已经准备完成，但当前不是已公开发布的版本。发布状态由[机器可读门禁](release-readiness.json)跟踪；版权与许可证确认、私密安全披露渠道、公开远端和干净发布快照完成前，不能创建正式发布声明。

## 2. 本次范围

本候选包含：

- 支付服务域六组件 Candidate Working Draft；
- 独立 `PSD-PAY-A402` 候选；
- `CID-PCA-NEG` 支付连接边界；
- HTTP A402 Binding Preview；
- Alipay AI Pay Profile Preview 和 Payment-Needed Product Preview Schema；
- Buyer Agent、Metered REST Provider、End-to-end 402 Quickstart；
- Sandbox Showcase、证据模板、候选断言和 A402 决策流程。

本候选不包含：

- ACT 2.0 公开目录、旧 Schema 或迁移草案；
- Accepted A402 Core Schema、正式错误词典或 TCK；
- 生产兼容认证；
- 真实支付宝沙箱成功证据；
- 第二个独立 Product Profile 或独立实现。

## 3. 来源快照

| 来源 | 本次结论 |
|---|---|
| 支付服务域继承基线 | 正文哈希与 `specs/2.1/revision-status.md` 登记一致 |
| ACT v2.1 修订方案 | 正文哈希与登记一致；本轮无协议源变化 |
| 支付宝 AI 按量付费接入指南 | 2026-07-31 核对；页面更新时间 `2026-07-28 20:57:32` |

支付宝产品变化见[本次产品事实审计](../../../profiles/alipay-ai-pay/sources/audits/2026-07-31-product-update.md)。

## 4. 验证结果

2026-07-31 在当前工作树运行：

```bash
./scripts/verify.sh
```

结果：

- 仓库结构、链接、JSON、PSD 双来源、Release Manifest、候选断言、Profile Preview Schema、仓库卫生、A402 决策 Register 和评审流程全部通过；
- Buyer Agent Quickstart：2 项通过；
- End-to-end 402：8 项通过；
- Java Metered REST Provider：4 项通过；
- Sandbox Showcase：16 项通过；
- Demo 静态构建通过。

以上是本地候选验证，不替代干净发布 Commit 的 CI，也不构成真实支付或产品兼容证据。

## 5. 发布前阻塞项

July Preview 公开发布仍需：

1. 确认版权主体、文档/代码许可证分配和 CLA/DCO 策略；
2. 建立并验证一个私密安全披露渠道；
3. 确认公开代码托管远端；
4. 审查当前重构变更，生成干净 Commit，并从该 Commit 重新运行 CI；
5. 只有上述条件通过后，才创建 Preview Tag 和公开 Release。

本页使用的 `july-preview` target 已退出当前工具。查看现行 ACT Candidate 发布门禁：

```bash
python3 scripts/release_readiness.py --target act-candidate-publication
```

## 6. Release Candidate 后续门槛

进入 2.1 RC 还要求：

- A402 九项决定形成 Accepted ADR；
- 生成权威 Core Schema、fixtures、validator 和标准错误契约；
- 完成至少一条官方支付宝沙箱闭环及关键异常验证；
- 形成脱敏证据包和 clean-room 开发者试用报告；
- 通过治理规定的独立实现和评审门槛。
