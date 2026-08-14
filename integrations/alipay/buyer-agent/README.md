# 支付宝买方 Agent 接入

> 范围：买方 Agent，通过支付宝官方 Skill/CLI 组合 L1 `PSD-PAY-INS` 与 `PSD-PAY-A402`

本接入示例不安装 ACT 私有支付实现。它只检查本地前置条件，实际钱包授权和支付交给支付宝公开软件包完成。

## 1. 运行本地预检

需要 Node.js 18 或更高版本。

```bash
cd integrations/alipay/buyer-agent
npm run preflight
```

预检不会下载软件，也不会索取凭证。它会输出下一条官方安装命令，并报告当前环境是否已经存在 `alipay-bot`。

## 2. 安装官方支付能力

执行 [alipay/payment-skills](https://github.com/alipay/payment-skills) 当前公开的安装命令：

```bash
npx -y @alipay/agent-payment@latest install
```

如果只需要 CLI，官方仓库当前提供：

```bash
npx -y @alipay/agent-payment@latest install-cli
```

软件包内容和命令可能独立于 ACT 变化。制作发布快照前，应重新核对官方仓库。

为使验证结果可复现，应在安装时记录实际解析到的精确版本和完整性信息；仓库只保留官方 `@latest` 入口，不猜测或锁定一个未经本次验证的版本：

```bash
npm view @alipay/agent-payment@latest version dist.integrity
```

把结果连同仓库 Commit 写入[端到端证据模板](../validation/evidence-template.md)，不要把令牌或本地凭证写入仓库。

## 3. 在 Agent 中启用支付流程

让 Agent 加载已安装的支付宝钱包和支付 Skill。访问收费 HTTP 资源时，向 Agent 提供资源 URL 和原始请求上下文。官方工作流应当：

1. 保留原始请求的 Method、URL、Body 和必要 Header；
2. 识别 `402` 和 `Payment-Needed`；
3. 向用户展示可理解的支付意图；
4. 获得所需的支付宝授权；
5. 支付结果未知时查询结果，避免重复支付；
6. 提交 `Payment-Proof`，并在内部恢复原始资源请求；
7. 返回资源或结构化的非成功结果。

不要在每次支付前固定增加 `check-wallet` 调用。钱包就绪状态由官方支付命令在真实支付流程中负责。

## 4. 如何判断接入成功

本地预检通过只证明主机可以运行官方安装器或 CLI。买方接入成功还要求：

- 使用官方 Skill/CLI，而不是复制的 Mock；
- 完成真实的支付宝授权路径；
- 完成一次真实收银台或 402 测试支付；
- 分别处理待处理中、成功、失败和需要授权；
- 留存不包含绑定码、密码或完整凭证的脱敏证据。

然后按[端到端验证清单](../validation/README.md)与收费资源完成联调。

## 5. 接入 Sandbox Showcase（可选）

真实联调需要可视化时，宿主 Agent 可在官方支付工作流产生真实状态后，调用 [Buyer Event Adapter](../../../code/web-client/alipay-ai-pay-showcase/buyer-event-adapter.mjs)。Adapter 只接收脱敏的结构化状态与关联引用，不执行支付、不解析 CLI 对客文本，也不能接收完整 `Payment-Proof`。

运行时接线和信号格式见 [Demo 的买方 Adapter 说明](../../../code/web-client/alipay-ai-pay-showcase/README.md#买方-agent-adapter)。没有官方 Skill/CLI 的真实结果时不得提交成功信号。
