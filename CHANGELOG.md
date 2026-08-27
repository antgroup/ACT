# Changelog

本文件记录各公开发布版本的变更。版本标识、发布日期、规范定版日期和发布内容以 [`release-manifest.json`](release-manifest.json) 为准。ACT 2.1 已定版，非勘误性质的规范性变更须以新的协议版本发布。

## Repository maintenance — 2026-08-27

- 将 TSD-CRD 参考实现的实现基线、架构、快速开始、安全模型和可选扩展说明集中到 `docs/reference-implementations/tsd-crd/`，可运行代码继续保留在 `code/samples/tsd-crd-reference/`。
- 明确 TSD-CRD 是 ACT 2.1 的规范性协议子篇；`reference-v1` 机器 Profile、Reference Implementation 及其实现指南不增加或替代 ACT 2.1 协议要求。

## Repository update — 2026-08-24

- 将 TSD-CRD 作为 ACT 2.1 信任服务域的信用关联子篇集成到现有发布树。
- 在 `code/schemas/tsd-crd/reference-v1/` 发布非规范性 JSON Schema、OpenAPI、本地示例和固定测试向量，并保留既有 wire 契约与签名向量。
- 在 `code/samples/tsd-crd-reference/` 提供非生产 Reference Implementation、Sandbox、CLI、Demo、测试和基础一致性 Runner。
- 将 TSD-CRD 机器产物与参考实现接入根级导航、发布清单、仓库完整性检查和 `./tools/verify.sh`；通过不构成 ACT 2.1 全量 Conformance 或生产就绪声明。

## ACT 2.1 — 2026-08-14

- 发布协议概览及 ADD、CID、PSD、TSD 四域规范；A402 和 L1/L2/L3 均由支付服务域正文定义，提取文档仅作为非规范性便捷指南。
- 将 A402 JSON Schema、fixtures 与测试断言作为非规范性机器实现产物发布。
- 提供通用本地 A402 样例、支付宝买卖方接入示例、沙箱验证指引和机器支付 Demo。
- 采用 `docs/`、`code/`、`integrations/` 三层结构，明确协议、通用工程产物与产品实现边界。
- 公开发布树仅包含 ACT 2.1 规范、实现辅助产物、样例、产品接入和必要项目政策，不包含 ACT 2.0 或内部过程资料。
- 收口 ISR 术语、CID–PSD 机器契约边界和公共协议入口的版本权威说明。
- 支付宝买方预检对齐官网 Node.js 22+ / npm 10+ 要求，并固定仓库维护的 ACT–Alipay 集成映射标识。
- 卖方示例补充有效账单复用、Proof 拒绝后的先对账恢复规则和交易号最小披露，避免重复支付或返回过期账单。
- Demo 明确区分引导演示、官方沙箱事件与证据回放，并移除活动过程材料。
- 将仓库质量与发布程序收敛到 `tools/` 主架构，统一提供 `./tools/verify.sh` 验证入口，并明确工具不定义协议语义。
