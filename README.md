# ACT Protocol

[English](README.en.md) | 简体中文

ACT（Agentic Commerce Trust Protocol）是面向智能体商业交互的开放协议。ACT 2.1 定义委托授权、商业交互、支付服务和信任服务四个协作域。本仓库以“Agent 发现并购买付费数字资源”为贯穿场景，分别提供协议正文、产品无关的安全样例、交互演示和支付宝参考接入；这些层次不互相替代。

## 从这里开始

| 目标 | 入口 |
|---|---|
| 阅读 ACT 2.1 | [协议概览](docs/specification/overview.md) |
| 理解完整业务流程 | [典型场景与业务流程](docs/specification/scenarios.md) |
| 运行 TSD-CRD 信用关联参考链路 | [TSD-CRD Reference Implementation](code/samples/tsd-crd-reference/README.md) |
| 本地运行安全的 A402 样例 | [Local A402 Sample](code/samples/local-a402/README.md) |
| 查看交互演示 | [Web Showcase](code/web-client/alipay-ai-pay-showcase/README.md) |
| 接入支付宝 | [Alipay Reference Integration](integrations/alipay/README.md) |

第一次进入仓库，建议按以下顺序阅读：

1. 用 2 分钟阅读[协议概览](docs/specification/overview.md)，先区分 ADD、CID、PSD、TSD 与 A402；
2. 遇到缩写时查看[中英术语表](docs/glossary.md)；
3. 需要理解信用关联时，运行 TSD-CRD Reference Implementation，观察关联、映射、生命周期、查询授权和验证；
4. 运行 Local A402 Sample，观察 `402 → Payment-Needed → 伪 Proof 被拒绝` 的安全路径；
5. 需要真实支付成功链路时，选择[支付宝买方](integrations/alipay/buyer-agent/README.md)或[卖方 Java](integrations/alipay/seller-java/README.md)，并在官网沙箱完成授权和支付。

Local A402 Sample 有意不伪造支付成功。真实资源交付必须来自已经验真的支付证明，因此“本地安全失败路径”和“官网沙箱成功路径”是两个不同的接入阶段。TSD-CRD Reference Implementation 同样只使用 Mock 能力和测试密钥，不是生产信用服务。

ACT 2.1 的五份规范正文和非规范性场景指南位于 `docs/specification/`。A402 与 Commerce–Payment 接入指南随支付宝参考接入放在 `integrations/alipay/`。JSON Schema、fixtures 和测试位于 `code/schemas/`，用于帮助实现与验证，不增加协议正文未规定的要求。

本仓库发布版本中，`docs/specification/` 下的协议概览和四份域规范共同构成 ACT 2.1 唯一的版本化规范正文；场景指南明确为非规范性材料。[act-protocol.com](https://www.act-protocol.com/) 是项目信息入口；未明确标注 ACT 2.1 版本的网页内容属于信息性材料，不是本 Release 的规范来源。网页如果遗漏本 Release 的组件、采用不同结构或与正文冲突，只能按网页自身标明的版本理解，不得用于覆盖或解释本仓库的 ACT 2.1 要求。

## 仓库结构

```text
act-protocol/
├── docs/                         # ACT 2.1 规范、场景与附加文档
│   └── specification/           # 五份规范正文 + 非规范性场景指南
├── code/                         # Schema、样例和演示
│   ├── schemas/
│   ├── samples/
│   └── web-client/
├── integrations/
│   ├── tsd-crd/                  # TSD-CRD 参考实现指南
│   └── alipay/                   # 接入指南、支付宝参考代码与验证
└── tools/                        # 仓库质量与发布工具
```

依赖方向是单向的：

```text
ACT 2.1 specification
        ↓
machine-readable artifacts
        ↓
product integration
        ↓
sample / demo
```

产品实现、演示和 `tools/` 下的验证程序不得反向定义协议语义。

## 运行本地样例

下载或 clone 本仓库后，在仓库根目录执行以下命令，需要 Node.js 18 或更高版本：

```bash
npm --prefix code/samples/local-a402 run local
```

这个样例返回 `402 Payment Required`、解码 `Payment-Needed`，并验证伪造的 `Payment-Proof` 不会导致资源交付。它不连接支付产品，也不会执行支付。

运行 TSD-CRD 测试、基础一致性检查和本地 Demo 需要 Node.js 22.18 或更高版本：

```bash
npm --prefix code/samples/tsd-crd-reference run check
npm --prefix code/samples/tsd-crd-reference run demo
```

该套件采用非规范性的 `reference-v1` 机器 Profile。测试通过只证明仓库内参考路径，不等于 ACT 2.1 全量 Conformance 或生产就绪。

运行交互演示：

```bash
npm --prefix code/web-client/alipay-ai-pay-showcase run demo
```

打开 `http://127.0.0.1:4173/`。Showcase 是协议流程演示，不是支付实现或一致性认证。

## 支付宝参考接入

`integrations/alipay/` 展示两侧能力：

- `buyer-agent/`：检查环境并引导安装支付宝官方 Agent Payment Skill/CLI；
- `seller-java/`：使用支付宝 Java SDK 验证支付凭证并确认履约；
- `validation/`：沙箱前置检查和脱敏证据格式。

支付宝开户、授权、密钥、沙箱和最新产品操作始终以 [AIPay 官网](https://aipay.alipay.com/callpay)及其[官方接入指南](https://aipay.alipay.com/docs/ai-receive/MACHINE_PAY.html)为准。本仓库不复制或实现官网沙箱。

## 质量检查

完整检查需要 Python 3、Node.js 22.18+、JDK 8+ 和 Maven 3.8+：

```bash
./tools/verify.sh
```

## 项目政策

- [贡献指南](CONTRIBUTING.md)
- [安全政策](SECURITY.md)
- [行为准则](CODE_OF_CONDUCT.md)
- [版本记录](CHANGELOG.md)

协议文档采用 CC BY 4.0，代码采用 Apache License 2.0。版权主体为 Ant Group Co., Ltd。
