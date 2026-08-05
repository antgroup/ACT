# ACT Bindings

本目录只保存跨产品的 ACT 公共 Binding。Binding 定义协议语义如何由具体传输方式承载，不重定义支付授权、产品字段或商户开户。

| Binding | 当前 Preview 基线 | 责任 |
|---|---|---|
| [HTTP A402](http-a402/README.md) | 卖方公共基线 | 承载 `Payment-Needed` 和 `Payment-Proof`，并保留原始资源请求 |

候选 `PSD-PAY-A402` 是支付接入协议层；INS、DEL、AUP 是支付场景组件。支付宝官方 Skill/CLI 是产品特定工作流，位于 [Alipay AI Pay Profile Binding](../profiles/alipay-ai-pay/bindings/skill-cli/README.md)，不作为跨产品 ACT Binding 发布。
