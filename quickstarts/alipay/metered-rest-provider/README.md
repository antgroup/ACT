# 支付宝 AI 按量付费服务端 Quickstart

> 范围：卖方 HTTP 402 + 支付宝沙箱/OpenAPI 验凭证与履约确认

这是一个可运行的最小服务端，不是 Mock 支付服务。只有 `alipay.aipay.agent.payment.verify` 调用成功，且验得金额、商户订单、资源和交易号与已存账单一致时，服务端才会交付资源。

实现依据当前公开的 [AI 按量付费接入指南](https://aipay.alipay.com/docs/ai-receive/MACHINE_PAY.html)。官网要求支付宝 Java SDK `4.38.0.ALL` 或更高版本；本 Quickstart 固定使用 `4.40.720.ALL`，其中包含这里使用的 AI 付请求和响应类型。产品字段属于 Alipay Profile；候选 `PSD-PAY-A402` 描述其协议位置。

## 1. 前置条件

- JDK 8 或更高版本，Maven 3.8 或更高版本。
- 已配置官方沙箱或 OpenAPI 环境的支付宝应用。
- 已开通 AI 按量付费产品，并注册 `service_id`。
- 应用私钥和支付宝公钥保存在仓库之外。
- 卖方 ID，以及产品定义的价格和资源信息。

通过 [AIPay 官方文档](https://aipay.alipay.com/docs/ai-receive/MACHINE_PAY.html)完成产品开通和凭证配置。本仓库不重复实现控制台或沙箱。

## 2. 初始化配置

使用初始化命令创建 `.env`；已有文件不会被覆盖：

```bash
cd quickstarts/alipay/metered-rest-provider
./run.sh init
```

替换全部占位值，并使用密钥文件的绝对路径。`.env` 和 `*.pem` 已被 Git 忽略。启动脚本会在当前进程内加载配置，不需要手工 `source`。

Quickstart 接受 `ALIPAY_PRIVATE_KEY_FILE` 和 `ALIPAY_ALIPAY_PUBLIC_KEY_FILE`，比直接把密钥写入环境变量更安全。`ALIPAY_APP_AUTH_TOKEN` 是可选项，只适用于官网说明的第三方应用模式。

支付宝向导会同时展示“应用公钥”和“支付宝公钥”。本服务端验签必须配置后者，因此当前变量名为 `ALIPAY_ALIPAY_PUBLIC_KEY_FILE`。旧的 `ALIPAY_PUBLIC_KEY_FILE` 只保留兼容并会输出弃用提示，避免开发者误填应用公钥。

`ALIPAY_AMOUNT` 会按原字符串传递。应遵循当前产品控制台和 API 定义，Quickstart 不会静默转换单位。

沙箱开通、配置和联调直接使用 [AIPay 官网接入指南](https://aipay.alipay.com/docs/ai-receive/MACHINE_PAY.html)，本仓库不复述这些产品步骤。官网同时提供卖方 Agent 自动集成入口 `@alipay/alipay-aipay`；它是支付宝产品接入助手，不是买方 `@alipay/agent-payment`，本仓库只引用，不复制其实现。

## 3. 一条命令测试、构建并运行

完成官网产品开通和 `.env` 配置后：

```bash
./run.sh
```

该命令依次运行测试、构建 Jar 并启动服务；不会创建产品账号、生成密钥或绕过官方沙箱。只运行不需要凭证的单元测试可使用 `./run.sh test`，只构建可使用 `./run.sh package`。

检查未支付响应：

```bash
curl -i http://127.0.0.1:8080/paid-resource
```

预期结果：

- HTTP `402 Payment Required`；
- Base64URL 编码的 `Payment-Needed` Header；
- 不包含密钥或凭证的 JSON 诊断响应体。

使用[端到端 402 Quickstart](../end-to-end-402/README.md)和官方 Agent Payment Skill/CLI 完成授权支付与重试。

## 4. 已实现的安全门槛

- RSA2 按排序后的 Key 顺序签署官网公开字段集合。
- 将 `Payment-Proof` 作为不可信 Base64 JSON 解析。
- 交付资源前调用官方验凭证 API。
- 在 `biz_content` 中传递官网要求的 `client_session`，避免生成式 SDK 模型落后于公开 API 字段时丢失该值。
- 校验 `active`、金额、商户订单、资源 ID 和交易号。
- 同一交易不能用于不同资源。
- 幂等重试返回同一资源，不会重复安排履约确认。
- 资源交付后异步执行履约确认。
- 日志对交易号脱敏，且不输出密钥或完整凭证。

## 5. 可选 Sandbox Showcase 事件

本 Quickstart 可以向本机 [Demo Bridge](../../../demos/alipay-ai-pay-sandbox-showcase/README.md#live-sandbox)发送脱敏状态。配置 `ACT_DEMO_BRIDGE_URL` 和 `ACT_DEMO_VALIDATION_ID` 后，它会观察首次资源请求、402、携 Proof 的原请求重试、验款结论、资源交付和履约确认。Buyer Adapter 必须先输出能力协商与订单确认，并在调用官方支付能力时输出 L1 授权、处理状态和支付结果；完整顺序以 Demo 的事件格式为准。

该功能默认关闭、异步执行且失败不阻断产品链路。它不发送完整账单、Proof、交易号、订单号、`client_session`、签名或密钥。用户授权和支付处理中状态必须由实际官方 Agent Payment Adapter 提供。

## 6. 距离生产使用仍有差距

本 Quickstart 有意使用内存账单和履约记录。生产使用前必须替换为持久化、原子化存储，并补充：

- 持久化履约任务，以及有界重试和退避；
- 多实例幂等和防重放锁；
- 账单过期清理和数据保留策略；
- 边缘层鉴权、限流和请求大小限制；
- 结构化、脱敏的可观测性与告警；
- 使用密钥管理系统，而不是进程环境变量；
- 产品要求的容灾和对账。

在补齐上述能力并通过沙箱证据验证前，这些代码只能称为 Quickstart，不能称为参考实现。
