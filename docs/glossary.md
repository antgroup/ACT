# ACT 2.1 术语表 / Glossary

本表解释 ACT 2.1 中最常见的角色、对象和缩写。各域正文对具体字段给出更精确约束；本表不新增规范要求。

| Term | 中文含义 | Meaning |
|---|---|---|
| ACT | 智能体商业信任协议 | Agentic Commerce Trust Protocol |
| ADD | 委托授权域 | Authorization & Delegation Domain |
| CID | 商业交互域 | Commerce Interaction Domain |
| PSD | 支付服务域 | Payment Services Domain |
| TSD | 信任服务域 | Trust Services Domain |
| TSD-CRD | 信用关联子篇 | Credit Association subprotocol within the ACT 2.1 Trust Services Domain |
| `ASSOCIATED_CREDIT` | 关联信用来源标记 | Marks credit information mapped from a verified associated subject; it is not the Agent's independent credit or reputation |
| Principal / Delegator | 委托人 | The user or principal whose intent and authority the Agent acts upon |
| Buyer Agent | 买方智能体 | The Agent that acts for the principal to discover, negotiate and purchase |
| Seller Service | 卖方服务方 | The merchant, service, Agent or endpoint that protects and delivers a paid resource |
| PSP | 支付服务方 | Payment service provider |
| ISR | 意图结构化结果 | Intent Structured Result: the structured expression of the user's goals and constraints |
| IAC | 意图授权凭证 | Intent Authorization Credential: a verifiable representation of an Agent's delegated authority |
| `intent_id` | 意图标识 | Identifier that links intent capture, ISR and downstream processing |
| `delegation_id` | 委托标识 | Identifier of an IAC and its lifecycle |
| `SPECIFIED` | 定向委托 | Delegation whose transaction, merchant, goods, amount or equivalent boundaries are explicitly specified |
| `BOUNDED` | 有界委托 | Delegation that lets an Agent choose actions within task, budget and policy boundaries |
| L1 / INS | 即时支付 | User-present, per-payment identity and authorization confirmation |
| L2 / DEL | 委托支付 | Automatic payment for a transaction whose goods, merchant, amount and limits are explicitly specified |
| L3 / AUP | 自主支付 | Autonomous payment within a bounded task, budget and policy |
| A402 | 402 支付接入 | ACT payment-access component using an HTTP 402 challenge and proof retry |
| `method_id` | 支付方法标识 | Identifier of the selected payment-method specification or integration mapping |
| Payment-Needed | 支付诉求 | Payment requirement returned with an HTTP 402 response |
| Payment-Proof | 支付证明 | Payment evidence submitted when retrying the original request |
| Payment-Validation | 支付验证结果 | Optional validation result returned after proof verification |
| Original request retry | 原请求重试 | Repeating the protected resource request with its method, target and semantics preserved, plus Payment-Proof |
| Request fingerprint | 请求指纹 | Implementation-derived digest used to correlate a proof with the protected request |
| Idempotency | 幂等 | Repeating the same operation without creating duplicate payment, delivery or fulfillment side effects |
| Replay protection | 防重放 | Preventing a valid proof or request from being reused outside its authorized transaction and resource context |
| Binding | 协议绑定 | Rules that map ACT semantics to a transport, workflow or external protocol |
| Product profile | 产品映射 | Non-normative mapping between ACT semantics and a provider's product behavior |
| Conformance | 一致性证明 | Evidence that an implementation satisfies a defined, published conformance contract |
