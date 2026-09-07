# 支付宝 AI 按量付费卖方 Java 接入

> 范围：卖方 HTTP 402 + 支付宝沙箱/OpenAPI 验凭证与履约确认

这是一个可运行的最小服务端，不是 Mock 支付服务。只有 `alipay.aipay.agent.payment.verify` 调用成功，且验得金额、商户订单、资源和交易号与已存账单一致时，服务端才会交付资源。

实现依据当前公开的 [AI 按量付费接入指南](https://aipay.alipay.com/docs/ai-receive/MACHINE_PAY.html)。官网要求支付宝 Java SDK `4.38.0.ALL` 或更高版本；本示例固定使用 `4.40.720.ALL`，其中包含这里使用的 AI 付请求和响应类型。产品字段属于支付宝实现层；`PSD-PAY-A402` 描述其协议位置。

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
cd integrations/alipay/seller-java
./run.sh init
```

替换全部占位值，并使用密钥文件的绝对路径。`.env` 和 `*.pem` 已被 Git 忽略。启动脚本会在当前进程内加载配置，不需要手工 `source`。

本示例接受 `ALIPAY_PRIVATE_KEY_FILE` 和 `ALIPAY_ALIPAY_PUBLIC_KEY_FILE`，比直接把密钥写入环境变量更安全。`ALIPAY_APP_AUTH_TOKEN` 是可选项，只适用于官网说明的第三方应用模式。

支付宝向导会同时展示“应用公钥”和“支付宝公钥”。本服务端验签必须配置后者，因此当前变量名为 `ALIPAY_ALIPAY_PUBLIC_KEY_FILE`。旧的 `ALIPAY_PUBLIC_KEY_FILE` 只保留兼容并会输出弃用提示，避免开发者误填应用公钥。

`ALIPAY_AMOUNT` 会按原字符串传递，不会静默转换单位。按照当前官网服务注册约束，启动时仅接受 `0.01` 至 `50.00` CNY、最多两位小数，并要求 `ALIPAY_CURRENCY=CNY`。该金额还必须与 `service_id` 在 AIPay 控制台登记的服务单价完全一致；后者只能由官方控制台确认，本地代码不会假装完成核验。

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

使用[端到端验证清单](../validation/README.md)和官方 Agent Payment Skill/CLI 完成授权支付与重试。

## 4. 已实现的安全门槛

- RSA2 按排序后的 Key 顺序签署官网公开字段集合。
- 将 `Payment-Proof` 作为不可信 Base64 JSON 解析。
- 交付资源前调用官方验凭证 API。
- 在 `biz_content` 中传递官网要求的 `client_session`；当前固定 SDK 的生成式 Model 尚无该字段 setter，测试会锁定实际发送的三个字段，避免升级时丢失。
- 校验 `active`、金额、商户订单、资源 ID 和交易号。
- 同一交易不能用于不同资源。
- 相同未支付请求复用仍有效的账单，避免刷新请求时制造多个可支付订单。
- 官方验款明确返回 inactive 时才返回新的 402；关联事实不一致时只返回机器可读冲突，调用方必须先查询或对账，服务端不会自动诱导第二次付款。已经验为有效且关联一致的 Proof 不会仅因原支付截止时间已经过去而被拒绝交付。
- 在卖方可信上下文计算并保存非规范性 A402 产物请求指纹；支付宝官网产品报文保持不变。
- 使用 `(method_id, trade_no, out_trade_no, resource_id)` 占用键和 `(method_id, trade_no, request_fingerprint)` 交付键处理重放。
- 幂等重试返回同一资源，不会创建新支付或重复安排履约确认。
- 资源交付后异步执行履约确认。
- 日志和资源响应只输出脱敏 `transaction_ref`，不输出完整交易号、密钥或完整凭证。

`ACT_A402_METHOD_ID` 和 `ACT_A402_METHOD_VERSION` 只用于非规范性实现产物的可信本地上下文及防重键，不会写入支付宝产品报文，也不是支付宝产品字段。仓库为这份映射固定使用集成层标识 `act-integration:a402/alipay-ai-pay` 和版本 `1.0.0`；它由本仓库维护，不声称由支付宝产品返回，也不是 ACT 2.1 的全局注册项。官方沙箱联调证据应同时记录该映射版本、仓库 Commit 和支付宝官方产品来源。

## 5. 距离生产使用仍有差距

本示例有意使用内存账单和履约记录。生产使用前必须替换为持久化、原子化存储，并补充：

- 持久化履约任务，以及有界重试和退避；
- 多实例幂等和防重放锁；
- 根据反向代理和公开服务地址安全解析 artifact `normalized_target_uri`；当前示例以直接收到的 HTTP Host/URI 计算请求指纹；
- 账单过期清理和数据保留策略；
- 边缘层鉴权、限流和请求大小限制；
- 结构化、脱敏的可观测性与告警；
- 使用密钥管理系统，而不是进程环境变量；
- 产品要求的容灾和对账。

在补齐上述能力并通过沙箱证据验证前，这些代码只能称为接入示例，不能称为生产参考实现。
