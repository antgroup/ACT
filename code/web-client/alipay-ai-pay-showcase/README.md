# ACT × Alipay AI Pay Guided Showcase

[English](README.en.md) | 简体中文

本 Demo 说明“Agent 在调研过程中如何购买专业数据”，以左右对照方式展示业务执行、参与方、ACT 2.1 组件和支付宝产品映射。

> **范围：Guided Demo / Non-normative / No real payment**
> 本 Demo 不连接支付宝沙箱、钱包、支付接口或验款接口，不接收真实事件，也不执行支付。

## 演示内容

| 场景 | 核心区别 | 支付宝实现边界 |
|---|---|---|
| L1 / `PSD-PAY-INS` | 用户对每一笔支付核身确认 | 展示支付宝绑定二维码占位图和付款确认卡片；二维码不可扫码 |
| L2 / `PSD-PAY-DEL` | 用户预先明确商品、商户、金额和次数，匹配后自动支付 | 仅演示 ACT 2.1 语义，本仓库不声明支付宝 L2 实现 |
| L3 / `PSD-PAY-AUP` | 用户给出任务与预算边界，Agent 在边界内自主选择和支付 | 仅演示 ACT 2.1 语义，本仓库不声明支付宝 L3 实现 |

每个场景均展示 `CID-PCA-NEG`、商业确认、资源请求、HTTP 402、`Payment-Needed`、支付处理、携 `Payment-Proof` 重试原请求、验款、资源交付和履约确认。异常选项覆盖支付结果未知、Proof 不匹配、验款不可用和幂等重试。

## 运行要求

- Node.js 18 或更高版本；
- 无需执行 `npm install`；
- 以下命令从仓库根目录运行。

## 启动

在仓库根目录执行：

```bash
npm --prefix code/web-client/alipay-ai-pay-showcase run demo
```

启动成功后，终端会显示：

```text
ACT showcase: http://127.0.0.1:4173/
```

服务不会自动打开浏览器。访问 `http://127.0.0.1:4173/` 后：

1. 选择 L1、L2 或 L3，比较三种授权等级的核心区别；
2. 使用单步播放逐项查看业务动作、参与方和协议组件；
3. 使用自动播放观察完整流程；
4. 切换异常场景，查看支付结果未知、Proof 不匹配、验款不可用和幂等重试。

服务在当前终端前台运行；按 `Ctrl+C` 停止。

## 更换端口

默认端口为 `4173`。端口已被占用时，可以通过 `PORT` 指定其他端口。

macOS 或 Linux：

```bash
PORT=4174 npm --prefix code/web-client/alipay-ai-pay-showcase run demo
```

Windows PowerShell：

```powershell
$env:PORT=4174; npm --prefix code/web-client/alipay-ai-pay-showcase run demo
```

然后打开终端输出的新地址。如果出现 `EADDRINUSE`，说明指定端口仍被占用；请换一个端口重试。

## 边界

- 页面中的订单、金额、交易引用、二维码和结果均为说明性演示数据。
- Demo 不验证真实 `Payment-Proof`，不提供支付成功证据，也不构成一致性认证。
- ACT 语义以 [`docs/specification/`](../../../docs/specification/README.md) 中的正式规范为准。
- 支付宝产品接入以 [AIPay 官网](https://aipay.alipay.com/callpay)及其官方接入文档为准；本仓库只在 [`integrations/alipay/`](../../../integrations/alipay/README.md) 提供参考接入。
- 官网沙箱由支付宝提供和运行，本 Demo 不复制、不代理，也不提供“连接沙箱”功能。

## 检查

```bash
npm --prefix code/web-client/alipay-ai-pay-showcase test
npm --prefix code/web-client/alipay-ai-pay-showcase run build
```
