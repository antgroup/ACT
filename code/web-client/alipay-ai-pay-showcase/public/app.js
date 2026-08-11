const stateCatalog = {
  PAYMENT_TOOL_STATUS_CHECKED: {
    label: "检查支付宝支付能力", phase: "BINDING", domain: "PSD", component: "PSD-PMT-BND",
    binding: "支付宝官方钱包状态检查", profile: "钱包聚合生命周期只映射为支付工具就绪状态",
    product: "Agent 支付 · 检查开通与绑定状态", code: "PMT · CHECK",
    explanation: "首次使用时，Agent 检查支付宝支付能力是否已经开通并完成账户授权绑定；已绑定用户可以跳过后续绑定步骤。",
    agent: "我正在检查当前 Agent 是否已经获得可用的支付宝支付能力。",
  },
  WALLET_BINDING_REQUIRED: {
    label: "申请开通支付能力", phase: "BINDING", domain: "PSD", component: "PSD-PMT-BND",
    binding: "官方开通申请 + 授权绑定链接", profile: "产品开通申请不等同于绑定成功",
    product: "Agent 支付 · 开通申请", code: "PMT · APPLY",
    explanation: "当前演示采用首次使用路径：开通申请提交后仍必须进入支付宝官方页面完成授权绑定。",
    agent: "支付宝支付能力尚未绑定。我已经提交开通申请，下一步需要你在官方页面完成授权。",
  },
  WALLET_BINDING_QR_PRESENTED: {
    label: "扫码授权绑定", phase: "BINDING", domain: "PSD", component: "PSD-PMT-BND",
    binding: "官方绑定链接 / 二维码", profile: "二维码仅指向支付宝可信授权界面",
    product: "Agent 支付 · 开启支付宝支付功能", code: "PMT · QR",
    explanation: "用户扫码或打开官方绑定链接，在支付宝页面点击开启并完成身份核验；Demo 二维码不可扫码。",
    agent: "请使用支付宝扫描绑定二维码，在官方页面点击“开启”并完成身份核验。",
  },
  WALLET_BOUND: {
    label: "支付能力绑定完成", phase: "BINDING", domain: "PSD", component: "PSD-PMT-BND",
    binding: "短时 6 位绑定指令 → 官方绑定确认", profile: "绑定指令不得进入日志、夹具或 Replay",
    product: "Agent 支付 · 授权成功", code: "PMT · READY",
    explanation: "授权后用户将短时绑定指令返回 Agent，官方能力确认绑定成功；后续每笔支付仍需按 L1 逐笔授权。",
    agent: "支付宝支付功能已经绑定。短时绑定指令未被记录，现在可以继续本次购买。",
  },
  PAYMENT_QR_PRESENTED: {
    label: "核身后生成付款码", phase: "INS / L1", domain: "PSD", component: "PSD-PAY-INS · L1",
    binding: "支付宝官方支付卡片", profile: "用户逐笔确认后生成本笔支付二维码",
    product: "Agent 支付 · 扫码支付", code: "INS · QR",
    explanation: "本笔交易生成支付宝支付卡片和二维码。二维码由官方产品生成；Demo 仅展示不可扫码占位图。",
    agent: "本笔 0.01 元支付卡片已经生成，请使用支付宝扫码完成付款。",
  },
  SPECIFIED_INTENT_CAPTURED: {
    label: "明确自动支付意图", phase: "ADD / L2", domain: "ADD", component: "ADD-INT-ICS · SPECIFIED",
    binding: "指定商品、商户、金额与受托 Agent", profile: "L2 产品映射 Validation-pending",
    product: "未来委托支付 Profile · 未声明已上线", code: "ADD · SPECIFIED",
    explanation: "用户预先明确商品、商户、金额和次数，生成 SPECIFIED 意图；完全匹配后自动支付，执行时用户可以不在场。",
    agent: "我已取得明确的委托目标：只允许向指定数据服务购买一次 0.01 元资源。",
  },
  SPECIFIED_IAC_ISSUED: {
    label: "签发 SPECIFIED IAC", phase: "ADD / L2", domain: "ADD", component: "ADD-IAC-ISS",
    binding: "完整 IAC + delegation_id", profile: "IAC wire Schema 尚未冻结",
    product: "未来委托支付 Profile · Validation-pending", code: "IAC · SPECIFIED",
    explanation: "授权服务签发绑定委托人、受托 Agent、商户、商品、金额和有效期的 SPECIFIED IAC。",
    agent: "定向委托凭证已经签发；后续支付必须严格匹配指定商户、资源和金额。",
  },
  SPECIFIED_IAC_VERIFIED: {
    label: "本地核对定向授权", phase: "DEL / L2", domain: "ADD + PSD", component: "PSD-PAY-DEL · local precheck",
    binding: "检查 IAC 状态、范围和 Agent 绑定", profile: "本地检查不能替代 PSP 权威核验",
    product: "未来委托支付 Profile · Validation-pending", code: "DEL · PRECHECK",
    explanation: "Agent 在付款前检查 IAC 有效状态、指定商户、资源、金额和当前运行身份。",
    agent: "本笔交易与 SPECIFIED IAC 完全匹配，可以在用户不在场时提交支付。",
  },
  DEL_PSP_AUTHORIZED: {
    label: "授权通过并自动支付", phase: "DEL / L2", domain: "PSD", component: "PSD-PAY-DEL · L2",
    binding: "PSP 验证签名、防重放、IAC 与绑定关系", profile: "支付宝 L2 产品能力尚未公开验证",
    product: "Future / Validation-pending", code: "DEL · VERIFY",
    explanation: "PSP 权威验证完整 IAC、签名、状态、受托人绑定、订单和金额；执行时不要求逐笔用户核身。",
    agent: "支付受理方已验证定向委托边界，现在可以执行本笔支付。",
  },
  BOUNDED_INTENT_CAPTURED: {
    label: "定义自主任务边界", phase: "ADD / L3", domain: "ADD", component: "ADD-INT-ICS · BOUNDED",
    binding: "任务目标、总预算、商户/类目与有效期", profile: "L3 产品映射 Validation-pending",
    product: "未来自主支付 Profile · 未声明已上线", code: "ADD · BOUNDED",
    explanation: "用户授权任务目标和可执行边界，具体服务选择由 Agent 在边界内自主决定。",
    agent: "我获得了一个 BOUNDED 任务：在 1 元总预算内购买完成报告所需的数据服务。",
  },
  BOUNDED_IAC_ISSUED: {
    label: "签发 BOUNDED IAC", phase: "ADD / L3", domain: "ADD", component: "ADD-IAC-ISS",
    binding: "BOUNDED IAC + delegation_id", profile: "IAC wire Schema 与状态查询仍待治理",
    product: "未来自主支付 Profile · Validation-pending", code: "IAC · BOUNDED",
    explanation: "授权服务签发任务级凭证，约束总预算、单笔上限、类目、商户范围、有效期和受托 Agent。",
    agent: "自主任务凭证已经签发；每一笔子支付都必须重新检查剩余预算和交易边界。",
  },
  AUP_BOUNDARY_CHECKED: {
    label: "检查自主支付边界", phase: "AUP / L3", domain: "ADD + PSD", component: "PSD-PAY-AUP · boundary check",
    binding: "检查 BOUNDED IAC、单笔/累计额度和目标范围", profile: "不依赖用户逐笔确认",
    product: "未来自主支付 Profile · Validation-pending", code: "AUP · CHECK",
    explanation: "Agent 检查本笔 0.01 元交易是否落在任务、类目、商户、单笔和累计预算边界内。",
    agent: "本笔数据服务调用符合 BOUNDED IAC，支付后剩余任务预算为 0.99 元。",
  },
  AUP_PSP_AUTHORIZED: {
    label: "PSP 验证自主授权", phase: "AUP / L3", domain: "PSD", component: "PSD-PAY-AUP · L3",
    binding: "PSP 权威验证 IAC、Agent、额度和防重放", profile: "支付宝 L3 产品能力尚未公开验证",
    product: "Future / Validation-pending", code: "AUP · VERIFY",
    explanation: "PSP 对本笔子支付执行权威边界核验；AUP 可在任务周期内循环，但每笔仍需独立校验。",
    agent: "支付受理方已确认本笔子支付处于授权边界内，可以自主执行。",
  },
  CAPABILITY_NEGOTIATED: {
    label: "确认服务支持支付",
    phase: "CID",
    domain: "CID",
    component: "CID-PCA-NEG",
    binding: "能力协商：选择 method_id 与接入端点",
    profile: "演示证据映射，不是支付宝线上字段",
    product: "支付宝 AI 付 Profile",
    code: "CID · NEG",
    explanation: "Buyer 与 Seller 在支付前确认 method_id、PSP 和接入端点。A402 不隐含某个支付场景。",
    agent: "已确认该服务支持支付宝 AI 付，并选择双方共同支持的支付方法。",
  },
  ORDER_CONFIRMED: {
    label: "确认购买内容",
    phase: "CID",
    domain: "CID",
    component: "CID-CART-CFM",
    binding: "CID 商业确认引用",
    profile: "商业确认与 A402 请求指纹相互独立",
    product: "交易摘要与商户订单",
    code: "CID · CFM",
    explanation: "确认商品、金额、币种和履约条件，形成独立商业确认引用；A402 请求指纹将在 Payment-Needed 阶段生成。",
    agent: "已锁定交易条件，并保存独立的商业确认引用。",
  },
  RESOURCE_REQUESTED: {
    label: "调用付费数据",
    phase: "A402",
    domain: "CID + PSD",
    component: "Paid resource request",
    binding: "HTTP 原始资源请求",
    profile: "卖方仅收到请求，此时还没有付款事实",
    product: "AI 按量付费 · 收费资源",
    code: "A402 · REQ",
    explanation: "Agent 发起原始 GET/POST 资源请求；方法、目标与请求摘要必须能在支付后恢复。",
    agent: "正在访问完成报告所需的专业数据服务。",
  },
  PAYMENT_REQUIRED: {
    label: "服务返回报价",
    phase: "A402",
    domain: "PSD",
    component: "PSD-PAY-A402 · Payment-Needed",
    binding: "HTTP 402 + Payment-Needed",
    profile: "ACT Candidate 索款要求 ↔ 支付宝产品账单",
    product: "AI 按量付费 · 机器账单",
    code: "A402 · 402",
    explanation: "Seller 返回机器可读 Payment-Needed，并回显已协商的 method_id；资源继续锁定。",
    agent: "服务返回了一张机器账单。我正在核对商品、金额、支付方法和有效期。",
  },
  USER_AUTHORIZATION_REQUIRED: {
    label: "用户对本笔核身确认",
    phase: "INS / L1",
    domain: "PSD",
    component: "PSD-PAY-INS · L1",
    binding: "支付宝官方 Skill / CLI",
    profile: "INS/L1 场景 ↔ 用户逐笔确认",
    product: "Agent 支付 · 用户在场",
    code: "INS · L1",
    explanation: "当前场景预先采用 L1。PSP 完成基础校验，并在资金处理前取得用户对本笔金额、商户与支付方式的确认和身份验证。",
    agent: "L1 不允许自动扣款：请你对这一笔核身，并确认收款方、商品、金额和支付方式。",
  },
  PAYMENT_PROCESSING: {
    label: "支付宝处理中",
    phase: "INS / L1",
    domain: "PSD",
    component: "Payment execution / status",
    binding: "支付宝官方 Skill / CLI",
    profile: "ACT 支付执行 ↔ 支付宝官方支付流程",
    product: "Agent 支付 · 支付与查询",
    code: "INS · PAY",
    explanation: "支付宝官方能力处理本次支付；结果未知时查询原交易，不能创建第二笔支付。",
    agent: "支付宝正在处理本次支付。结果确认前不会重复付款。",
  },
  PAYMENT_RESULT_RECEIVED: {
    label: "付款结果确认",
    phase: "INS / L1",
    domain: "PSD",
    component: "Payment result / Proof reference",
    binding: "支付宝官方 Skill / CLI",
    profile: "官方支付结果提供脱敏 Proof 引用",
    product: "Agent 支付 · 支付结果",
    code: "INS · RESULT",
    explanation: "Buyer 收到支付结果和可提交给 Seller 的 Proof。Demo 只记录脱敏引用，不记录完整 Proof。",
    agent: "支付结果已确认。我将用支付凭据恢复原来的资源请求。",
  },
  RESOURCE_REQUEST_RETRIED: {
    label: "重新请求数据",
    phase: "A402",
    domain: "PSD",
    component: "PSD-PAY-A402 · Payment-Proof",
    binding: "原请求 + Payment-Proof",
    profile: "适配产品 Proof，不修改官方载荷",
    product: "AI 按量付费 · 二次资源请求",
    code: "A402 · PROOF",
    explanation: "Buyer 以相同方法和目标重试原请求，并携带 Payment-Proof；Seller 仍将 Proof 视为不可信输入。",
    agent: "正在携带支付凭据重试同一个资源请求。",
  },
  PAYMENT_VERIFIED: {
    label: "服务方验款",
    phase: "A402",
    domain: "PSD",
    component: "Proof verification / Validation mapping",
    binding: "支付宝 payment.verify",
    profile: "候选 Payment-Validation ↔ 支付宝验款结果",
    product: "AI 按量付费 · payment.verify",
    code: "A402 · VERIFY",
    explanation: "Seller 通过支付宝官方接口核验状态、金额、订单、资源和防重。候选 Payment-Validation 映射到验款结果，不冒充已上线 Header。",
    agent: "卖方已通过支付宝官方接口完成验款，正在准备交付资源。",
  },
  RESOURCE_DELIVERED: {
    label: "资源交付",
    phase: "FULFILLMENT",
    domain: "BUSINESS FULFILLMENT",
    component: "Resource delivery",
    binding: "HTTP 成功响应",
    profile: "资源交付是独立业务事实，不等同于支付成功",
    product: "AI 按量付费 · 服务交付",
    code: "DELIVERY",
    explanation: "验款通过后，Seller 对同一请求返回对应资源；重复请求只返回幂等结果。",
    agent: "专业数据已经交付，我正在把它整理成最终报告。",
  },
  FULFILLMENT_CONFIRMED: {
    label: "履约确认",
    phase: "FULFILLMENT",
    domain: "PSD / PRODUCT PROFILE",
    component: "Method fulfillment confirmation",
    binding: "支付宝 fulfillment.confirm · 卖方观察",
    profile: "产品履约确认与可选 TSD 证据相互独立",
    product: "AI 按量付费 · 履约确认",
    code: "RECEIPT",
    explanation: "卖方已完成支付宝产品履约确认。本 Demo 不把该调用冒充 TSD 事件；买方 ack 与卖方 confirm 的正式关系仍是 Profile 待确认项。",
    agent: "资源已交付，卖方产品履约确认已完成；可选 TSD 证据仍独立异步处理。",
  },
  PAYMENT_PENDING: {
    label: "结果待确认",
    phase: "RECOVERY",
    domain: "PSD",
    component: "Transaction state recovery",
    binding: "查询原交易，不重新付款",
    profile: "支付宝官方交易状态是权威结果",
    product: "Agent 支付 · 结果查询",
    code: "PENDING",
    explanation: "支付结果暂时未知。必须查询原交易，禁止再次付款，资源保持锁定。",
    agent: "支付结果仍在确认中。我不会重复付款，也不会把资源标记为已交付。",
    failure: true,
  },
  PROOF_REJECTED: {
    label: "Proof 被拒绝",
    phase: "RECOVERY",
    domain: "PSD",
    component: "Proof consistency / replay checks",
    binding: "payment.verify 拒绝",
    profile: "必须同时通过产品验款与本地账单一致性检查",
    product: "AI 按量付费 · 验款失败",
    code: "REJECTED",
    explanation: "Proof 与订单、金额、资源或 method_id 不一致，或触发重放检查。Seller 不得交付资源。",
    agent: "支付凭据未通过一致性检查，资源不会交付。",
    failure: true,
  },
  VERIFICATION_UNAVAILABLE: {
    label: "验款暂不可用",
    phase: "RECOVERY",
    domain: "PSD",
    component: "Verification availability",
    binding: "503 + Retry-After",
    profile: "示例恢复响应，不代表支付宝线上报文承诺",
    product: "AI 按量付费 · payment.verify",
    code: "RETRY",
    explanation: "官方验款暂不可用。Seller 返回可重试错误，不能猜测支付成功或提前交付。",
    agent: "验款服务暂不可用。稍后会重试同一交易，不会重复扣款。",
    failure: true,
  },
};

const authorizationFlows = {
  L1: [
    "PAYMENT_TOOL_STATUS_CHECKED", "WALLET_BINDING_REQUIRED", "WALLET_BINDING_QR_PRESENTED", "WALLET_BOUND",
    "CAPABILITY_NEGOTIATED", "ORDER_CONFIRMED", "RESOURCE_REQUESTED", "PAYMENT_REQUIRED",
    "USER_AUTHORIZATION_REQUIRED", "PAYMENT_QR_PRESENTED", "PAYMENT_PROCESSING", "PAYMENT_RESULT_RECEIVED",
    "RESOURCE_REQUEST_RETRIED", "PAYMENT_VERIFIED", "RESOURCE_DELIVERED", "FULFILLMENT_CONFIRMED",
  ],
  L2: [
    "SPECIFIED_INTENT_CAPTURED", "SPECIFIED_IAC_ISSUED", "CAPABILITY_NEGOTIATED", "ORDER_CONFIRMED",
    "RESOURCE_REQUESTED", "PAYMENT_REQUIRED", "SPECIFIED_IAC_VERIFIED", "DEL_PSP_AUTHORIZED",
    "PAYMENT_PROCESSING", "PAYMENT_RESULT_RECEIVED", "RESOURCE_REQUEST_RETRIED", "PAYMENT_VERIFIED",
    "RESOURCE_DELIVERED", "FULFILLMENT_CONFIRMED",
  ],
  L3: [
    "BOUNDED_INTENT_CAPTURED", "BOUNDED_IAC_ISSUED", "CAPABILITY_NEGOTIATED", "ORDER_CONFIRMED",
    "RESOURCE_REQUESTED", "PAYMENT_REQUIRED", "AUP_BOUNDARY_CHECKED", "AUP_PSP_AUTHORIZED",
    "PAYMENT_PROCESSING", "PAYMENT_RESULT_RECEIVED", "RESOURCE_REQUEST_RETRIED", "PAYMENT_VERIFIED",
    "RESOURCE_DELIVERED", "FULFILLMENT_CONFIRMED",
  ],
};

const exchangeCatalog = {
  PAYMENT_TOOL_STATUS_CHECKED: { from: "buyer", to: "psp", message: "检查支付宝支付能力是否已开通并绑定" },
  WALLET_BINDING_REQUIRED: { from: "psp", to: "buyer", message: "返回官方开通与授权绑定指引" },
  WALLET_BINDING_QR_PRESENTED: { from: "buyer", to: "principal", message: "展示支付宝官方绑定链接 / 二维码" },
  WALLET_BOUND: { from: "principal", to: "psp", message: "提交短时绑定指令并确认支付能力就绪" },
  PAYMENT_QR_PRESENTED: { from: "psp", to: "principal", message: "生成本笔交易的支付宝扫码支付卡片" },
  SPECIFIED_INTENT_CAPTURED: { from: "principal", to: "auth", message: "明确指定商户、资源、金额和受托 Agent" },
  SPECIFIED_IAC_ISSUED: { from: "auth", to: "buyer", message: "签发 SPECIFIED IAC 与 delegation_id" },
  SPECIFIED_IAC_VERIFIED: { from: "buyer", to: "buyer", message: "本地检查 IAC 状态、范围与 Agent 绑定" },
  DEL_PSP_AUTHORIZED: { from: "buyer", to: "psp", message: "提交完整 IAC，由 PSP 权威验证定向委托" },
  BOUNDED_INTENT_CAPTURED: { from: "principal", to: "auth", message: "定义任务目标、1 元总预算和交易边界" },
  BOUNDED_IAC_ISSUED: { from: "auth", to: "buyer", message: "签发 BOUNDED IAC 与任务授权边界" },
  AUP_BOUNDARY_CHECKED: { from: "buyer", to: "buyer", message: "检查本笔交易与剩余预算是否处于授权边界" },
  AUP_PSP_AUTHORIZED: { from: "buyer", to: "psp", message: "PSP 权威验证 BOUNDED IAC 与本笔子支付" },
  CAPABILITY_NEGOTIATED: { from: "buyer", to: "seller", message: "确认该数据服务支持支付宝 AI 付" },
  ORDER_CONFIRMED: { from: "buyer", to: "seller", message: "确认商品：趋势数据 API · 单价 0.01 元 · 调用 1 次" },
  RESOURCE_REQUESTED: { from: "buyer", to: "seller", message: "Agent 请求调用 AI 支付行业趋势数据 API" },
  PAYMENT_REQUIRED: { from: "seller", to: "buyer", message: "服务返回报价：0.01 CNY，并保持数据锁定" },
  USER_AUTHORIZATION_REQUIRED: { from: "buyer", to: "principal", message: "请确认：向示例专业数据服务支付 0.01 元" },
  PAYMENT_PROCESSING: { from: "principal", to: "psp", message: "支付宝处理本次 0.01 元支付" },
  PAYMENT_RESULT_RECEIVED: { from: "psp", to: "buyer", message: "付款结果已确认，Agent 获得脱敏支付凭据" },
  RESOURCE_REQUEST_RETRIED: { from: "buyer", to: "seller", message: "Agent 携付款凭据重新请求同一份趋势数据" },
  PAYMENT_VERIFIED: { from: "seller", to: "psp", message: "核对交易、金额、订单和目标数据资源" },
  RESOURCE_DELIVERED: { from: "seller", to: "buyer", message: "验款通过，返回结构化趋势数据" },
  FULFILLMENT_CONFIRMED: { from: "seller", to: "psp", message: "服务方确认本次数据交付已完成" },
  PAYMENT_PENDING: { from: "buyer", to: "psp", message: "查询原支付结果；不会再次发起付款" },
  PROOF_REJECTED: { from: "seller", to: "buyer", message: "付款凭据不匹配，数据保持锁定" },
  VERIFICATION_UNAVAILABLE: { from: "psp", to: "seller", message: "验款暂不可用，稍后重试且不提前交付" },
};

const actorLabels = {
  principal: "用户",
  buyer: "Buyer Agent",
  seller: "收费服务",
  psp: "支付宝",
  auth: "授权服务",
};

const phaseCatalogs = {
  L1: [
    { eyebrow: "PMT-BND", label: "开通并绑定", states: ["PAYMENT_TOOL_STATUS_CHECKED", "WALLET_BINDING_REQUIRED", "WALLET_BINDING_QR_PRESENTED", "WALLET_BOUND"] },
    { eyebrow: "CID + A402", label: "选服务与报价", states: ["CAPABILITY_NEGOTIATED", "ORDER_CONFIRMED", "RESOURCE_REQUESTED", "PAYMENT_REQUIRED"] },
    { eyebrow: "INS / L1", label: "逐笔核身确认", states: ["USER_AUTHORIZATION_REQUIRED", "PAYMENT_QR_PRESENTED", "PAYMENT_PROCESSING", "PAYMENT_RESULT_RECEIVED", "PAYMENT_PENDING"] },
    { eyebrow: "A402", label: "凭据与验款", states: ["RESOURCE_REQUEST_RETRIED", "PAYMENT_VERIFIED", "PROOF_REJECTED", "VERIFICATION_UNAVAILABLE"] },
    { eyebrow: "FULFILLMENT", label: "获取数据", states: ["RESOURCE_DELIVERED", "FULFILLMENT_CONFIRMED"] },
  ],
  L2: [
    { eyebrow: "ADD", label: "明确委托", states: ["SPECIFIED_INTENT_CAPTURED"] },
    { eyebrow: "SPECIFIED IAC", label: "签发授权", states: ["SPECIFIED_IAC_ISSUED"] },
    { eyebrow: "CID + A402", label: "选服务与报价", states: ["CAPABILITY_NEGOTIATED", "ORDER_CONFIRMED", "RESOURCE_REQUESTED", "PAYMENT_REQUIRED"] },
    { eyebrow: "DEL / L2", label: "意图匹配自动付", states: ["SPECIFIED_IAC_VERIFIED", "DEL_PSP_AUTHORIZED", "PAYMENT_PROCESSING", "PAYMENT_RESULT_RECEIVED", "PAYMENT_PENDING"] },
    { eyebrow: "A402", label: "验款与交付", states: ["RESOURCE_REQUEST_RETRIED", "PAYMENT_VERIFIED", "PROOF_REJECTED", "VERIFICATION_UNAVAILABLE", "RESOURCE_DELIVERED", "FULFILLMENT_CONFIRMED"] },
  ],
  L3: [
    { eyebrow: "ADD", label: "定义任务边界", states: ["BOUNDED_INTENT_CAPTURED"] },
    { eyebrow: "BOUNDED IAC", label: "签发授权", states: ["BOUNDED_IAC_ISSUED"] },
    { eyebrow: "CID + A402", label: "自主选服务", states: ["CAPABILITY_NEGOTIATED", "ORDER_CONFIRMED", "RESOURCE_REQUESTED", "PAYMENT_REQUIRED"] },
    { eyebrow: "AUP / L3", label: "边界内自主付", states: ["AUP_BOUNDARY_CHECKED", "AUP_PSP_AUTHORIZED", "PAYMENT_PROCESSING", "PAYMENT_RESULT_RECEIVED", "PAYMENT_PENDING"] },
    { eyebrow: "A402", label: "验款与交付", states: ["RESOURCE_REQUEST_RETRIED", "PAYMENT_VERIFIED", "PROOF_REJECTED", "VERIFICATION_UNAVAILABLE", "RESOURCE_DELIVERED", "FULFILLMENT_CONFIRMED"] },
  ],
};

const forbiddenKeys = /(^|_)(secret|private_key|access_token|app_auth_token|payment_proof|client_session|binding_code|password)($|_)/i;
const detailKeys = [
  "authorization_level", "delegation_mode", "delegation_id", "method_id", "method_version", "psp_id", "http_method", "commerce_confirmation_ref",
  "request_ref", "request_fingerprint", "order_ref", "proof_ref", "transaction_ref",
  "resource_id", "amount", "currency", "validation_mapping", "delivery_ref", "fulfillment_ref",
  "idempotent_replay", "recovery_action",
];
const previewBase = {
  mode: "GUIDED_PREVIEW",
  source: "illustrative-ui-preview",
  environment: "NOT_APPLICABLE",
  evidence_ref: "UI-PREVIEW-NOT-PAYMENT-EVIDENCE",
  correlation_ref: "corr-preview-7f3a",
};

const authorizationCopy = {
  L1: {
    eyebrow: "USER PRESENT · PER PAYMENT",
    title: "每一笔都由用户核身确认",
    description: "Agent 可以准备订单，但每笔扣款前都必须回到用户确认金额、商户与支付方式。",
    facts: ["用户逐笔在场", "逐笔核身确认", "Agent 不可自动扣款"],
    prompt: "帮我生成《2026 AI 支付趋势报告》，需要付款时每一笔都让我核身确认。",
    intro: "L1 中 Agent 可以寻找并报价，但每一笔支付都必须由用户在场核身确认。本页演示首次绑定、逐笔确认、扫码付款和数据交付。",
    idle: "我会先寻找专业数据；收到报价后必须请你对本笔支付核身确认。",
  },
  L2: {
    eyebrow: "SPECIFIED INTENT · AUTOMATIC PAYMENT",
    title: "明确商品、商户和金额后自动支付",
    description: "用户预先把这一笔交易说清楚并签发 SPECIFIED IAC；执行时 Agent 不再逐笔打断用户。",
    facts: ["指定商品", "指定商户与金额", "单笔自动执行"],
    prompt: "授权你自动向“示例专业数据服务”购买一次“AI 支付行业趋势数据 API”，金额必须是 0.01 元。",
    intro: "L2 中用户提前明确商品、商户、金额和次数。Agent 只能自动执行这笔指定交易，不能换商品、换商户或提高金额。",
    idle: "我会严格匹配你指定的商品、商户和 0.01 元金额，匹配成功后自动执行，不再逐笔询问。",
  },
  L3: {
    eyebrow: "BOUNDED TASK · AUTONOMOUS PAYMENT",
    title: "Agent 在任务边界内自主决策和支付",
    description: "用户授权任务目标和预算边界；Agent 可以自主选服务并执行多笔子支付，但每笔都必须重新校验边界。",
    facts: ["Agent 自主选服务", "总预算 1.00 元", "每笔不超过 0.20 元"],
    prompt: "在 1 元总预算内自主购买完成《2026 AI 支付趋势报告》所需的数据，每笔不得超过 0.20 元。",
    intro: "L3 中用户不指定某一笔交易，而是给出任务、总预算和单笔边界。Agent 自主选择服务并支付，每一笔都重新检查授权范围。",
    idle: "我会在任务和预算边界内自主选择数据服务，并对每笔子支付重新检查范围和剩余预算。",
  },
};

const elements = Object.fromEntries(
  [
    "actBinding", "actComponent", "actDomain", "agentMessage", "alipayProduct", "controlStatus",
    "correlationChain", "currentState", "eventCounter", "eventStreamUrl", "evidenceDetails", "baselineValue", "footerScenarioValue",
    "evidenceRef", "exchangeCard", "fromActor", "directionArrow", "layerCode", "liveForm",
    "liveTab", "methodId", "modeBadge", "phaseRail", "playReplay",
    "replayControls", "replayFile", "replayTab", "playPreview", "previewControls", "previewTab",
    "resetPreview", "resourceCard", "resourceDescription", "resourceId", "resourcePrice",
    "resourceState", "resourceTitle", "scenarioSelect", "stateExplanation", "stepPreview",
    "stepReplay", "taskResult", "taskStatusDot", "timeline", "toActor", "wireBadge", "wireMessage",
    "principalActor", "buyerActor", "sellerActor", "pspActor", "authActor", "profileMapping", "tsdStatus",
    "businessJourney", "purchaseStatus", "businessActionTitle", "agentThinkingLabel",
    "paymentCard", "paymentCardKind", "paymentCardTitle", "paymentCardStatus", "paymentCardHint", "paymentQr", "resultArtifact",
    "authorizationSelect", "authorizationCard", "authorizationCardKind", "authorizationCardTitle",
    "authorizationCardStatus", "authorizationCardDescription", "authorizationFacts", "bindingQr", "bindingCommand", "protocolLayerValue",
    "productLayerValue", "footerProfileValue", "pspActorIcon", "pspActorName", "pspActorDescription", "layerExplanation",
    "authorizationSummary", "authorizationSummaryLevel", "authorizationSummaryEyebrow", "authorizationSummaryTitle",
    "authorizationSummaryDescription", "authorizationSummaryFacts", "userPrompt", "introScenarioCopy",
  ].map((id) => [id, document.getElementById(id)]),
);

let mode = "GUIDED_PREVIEW";
let scenario = "SUCCESS";
let authorizationLevel = "L1";
let events = [];
let replayEvents = [];
let replayIndex = 0;
let replayTimer = null;
let eventSource = null;
let previewEvents = [];
let previewIndex = 0;
let previewTimer = null;

const operationalL1Flow = [
  "CAPABILITY_NEGOTIATED", "ORDER_CONFIRMED", "RESOURCE_REQUESTED", "PAYMENT_REQUIRED",
  "USER_AUTHORIZATION_REQUIRED", "PAYMENT_PROCESSING", "PAYMENT_RESULT_RECEIVED",
  "RESOURCE_REQUEST_RETRIED", "PAYMENT_VERIFIED", "RESOURCE_DELIVERED", "FULFILLMENT_CONFIRMED",
];

function successFlow() {
  if (mode !== "GUIDED_PREVIEW") return operationalL1Flow;
  return authorizationFlows[authorizationLevel] || authorizationFlows.L1;
}

function flow() {
  const success = successFlow();
  if (scenario === "SUCCESS") return success;
  if (scenario === "PAYMENT_PENDING") {
    const index = success.indexOf("PAYMENT_PROCESSING");
    return [...success.slice(0, index + 1), "PAYMENT_PENDING"];
  }
  if (["PROOF_MISMATCH", "VERIFICATION_UNAVAILABLE"].includes(scenario)) {
    const index = success.indexOf("RESOURCE_REQUEST_RETRIED");
    return [...success.slice(0, index + 1), scenario === "PROOF_MISMATCH" ? "PROOF_REJECTED" : "VERIFICATION_UNAVAILABLE"];
  }
  if (scenario === "IDEMPOTENT_REPLAY") {
    return [...success, "RESOURCE_REQUEST_RETRIED", "PAYMENT_VERIFIED", "RESOURCE_DELIVERED"];
  }
  return success;
}

function renderTimeline() {
  elements.timeline.innerHTML = flow().map((id, index) => {
    const state = displayState(id, index);
    return `<li class="timeline-item ${state.failure ? "failure" : ""}" data-index="${index}">
      <span class="timeline-index">${String(index + 1).padStart(2, "0")}</span>
      <span><span class="timeline-name">${state.label}</span><small>${id}</small></span>
      <span class="timeline-domain">${state.phase}</span>
    </li>`;
  }).join("");
}

function displayState(id, index) {
  let state = stateCatalog[id];
  if (["PAYMENT_PROCESSING", "PAYMENT_RESULT_RECEIVED", "PAYMENT_PENDING"].includes(id) && authorizationLevel !== "L1") {
    const delegated = authorizationLevel === "L2";
    state = {
      ...state,
      phase: delegated ? "DEL / L2" : "AUP / L3",
      component: delegated ? "PSD-PAY-DEL · L2" : "PSD-PAY-AUP · L3",
      binding: delegated ? "SPECIFIED IAC 授权下的支付执行" : "BOUNDED IAC 边界内的子支付执行",
      profile: "协议语义演示；支付宝产品映射 Validation-pending",
      product: "Future / Validation-pending · 不代表支付宝已上线能力",
      label: id === "PAYMENT_PROCESSING" ? (delegated ? "委托支付处理中" : "自主子支付处理中") : state.label,
      code: delegated ? `DEL · ${id === "PAYMENT_RESULT_RECEIVED" ? "RESULT" : id === "PAYMENT_PENDING" ? "PENDING" : "PAY"}`
        : `AUP · ${id === "PAYMENT_RESULT_RECEIVED" ? "RESULT" : id === "PAYMENT_PENDING" ? "PENDING" : "PAY"}`,
      explanation: id === "PAYMENT_RESULT_RECEIVED"
        ? `${delegated ? "定向委托" : "自主支付"}结果已确认，并产生可供 A402 重试使用的脱敏 Proof 引用；该页面只演示 ACT 语义。`
        : id === "PAYMENT_PENDING"
          ? "授权范围内的原交易结果仍未知；只能查询原交易，不能生成第二笔支付。"
          : `${delegated ? "DEL" : "AUP"} 在 IAC 约束下执行本笔支付；支付宝侧产品映射尚待验证。`,
      agent: id === "PAYMENT_PROCESSING"
        ? `正在演示 ${delegated ? "DEL 定向委托" : "AUP 自主"}支付；这不是支付宝产品上线声明。`
        : state.agent,
    };
  }
  const replayStart = successFlow().length;
  if (scenario !== "IDEMPOTENT_REPLAY" || index < replayStart) return state;
  return {
    ...state,
    label: {
      RESOURCE_REQUEST_RETRIED: "再次提交同一请求",
      PAYMENT_VERIFIED: "重放再次验款",
      RESOURCE_DELIVERED: "返回既有结果",
    }[id] || state.label,
    code: {
      RESOURCE_REQUEST_RETRIED: "A402 · REPLAY",
      PAYMENT_VERIFIED: "A402 · REVERIFY",
      RESOURCE_DELIVERED: "IDEMPOTENT RESULT",
    }[id] || state.code,
    explanation: {
      RESOURCE_REQUEST_RETRIED: "Buyer 再次提交相同 Proof 与同一请求指纹；不会创建第二笔支付。",
      PAYMENT_VERIFIED: "Seller 仍执行权威验款与一致性检查，并命中既有防重占用记录。",
      RESOURCE_DELIVERED: "Seller 返回已保存的交付结果，不重复非幂等交付，也不再次触发履约确认。",
    }[id] || state.explanation,
  };
}

function renderPhaseRail(currentStateId = null) {
  const phases = phaseCatalogs[authorizationLevel] || phaseCatalogs.L1;
  const activeIndex = phases.findIndex((phase) => phase.states.includes(currentStateId));
  elements.phaseRail.innerHTML = phases.map((phase, index) => `
    <div class="phase-item ${index < activeIndex ? "done" : ""} ${index === activeIndex ? "active" : ""}">
      <small>${index + 1} · ${phase.eyebrow}</small>
      <strong>${phase.label}</strong>
    </div>
  `).join("");
}

const businessJourneys = {
  L1: [
    { title: "检查支付能力", detail: "首次使用确认开通状态", states: ["PAYMENT_TOOL_STATUS_CHECKED", "WALLET_BINDING_REQUIRED"] },
    { title: "完成钱包绑定", detail: "扫码授权并返回短时指令", states: ["WALLET_BINDING_QR_PRESENTED", "WALLET_BOUND"] },
    { title: "获取服务报价", detail: "选择 API 并收到 0.01 元账单", states: ["CAPABILITY_NEGOTIATED", "ORDER_CONFIRMED", "RESOURCE_REQUESTED", "PAYMENT_REQUIRED"] },
    { title: "本笔核身确认", detail: "每笔都回到用户确认后付款", states: ["USER_AUTHORIZATION_REQUIRED", "PAYMENT_QR_PRESENTED", "PAYMENT_PROCESSING", "PAYMENT_RESULT_RECEIVED", "PAYMENT_PENDING"] },
    { title: "验款并交付", detail: "携 Proof 重试并生成报告", states: ["RESOURCE_REQUEST_RETRIED", "PAYMENT_VERIFIED", "PROOF_REJECTED", "VERIFICATION_UNAVAILABLE", "RESOURCE_DELIVERED", "FULFILLMENT_CONFIRMED"] },
  ],
  L2: [
    { title: "明确委托目标", detail: "限定商户、资源和金额", states: ["SPECIFIED_INTENT_CAPTURED"] },
    { title: "签发定向授权", detail: "生成 SPECIFIED IAC", states: ["SPECIFIED_IAC_ISSUED"] },
    { title: "调用目标服务", detail: "命中指定 API 并收到报价", states: ["CAPABILITY_NEGOTIATED", "ORDER_CONFIRMED", "RESOURCE_REQUESTED", "PAYMENT_REQUIRED"] },
    { title: "自动执行指定支付", detail: "完全匹配意图，不再询问用户", states: ["SPECIFIED_IAC_VERIFIED", "DEL_PSP_AUTHORIZED", "PAYMENT_PROCESSING", "PAYMENT_RESULT_RECEIVED", "PAYMENT_PENDING"] },
    { title: "验款并交付", detail: "A402 恢复原请求", states: ["RESOURCE_REQUEST_RETRIED", "PAYMENT_VERIFIED", "PROOF_REJECTED", "VERIFICATION_UNAVAILABLE", "RESOURCE_DELIVERED", "FULFILLMENT_CONFIRMED"] },
  ],
  L3: [
    { title: "定义任务边界", detail: "设置目标与 1 元总预算", states: ["BOUNDED_INTENT_CAPTURED"] },
    { title: "签发任务授权", detail: "生成 BOUNDED IAC", states: ["BOUNDED_IAC_ISSUED"] },
    { title: "自主选择服务", detail: "Agent 在边界内比较并调用", states: ["CAPABILITY_NEGOTIATED", "ORDER_CONFIRMED", "RESOURCE_REQUESTED", "PAYMENT_REQUIRED"] },
    { title: "自主选择并支付", detail: "AUP 每笔检查预算与范围", states: ["AUP_BOUNDARY_CHECKED", "AUP_PSP_AUTHORIZED", "PAYMENT_PROCESSING", "PAYMENT_RESULT_RECEIVED", "PAYMENT_PENDING"] },
    { title: "验款并交付", detail: "更新预算并完成报告", states: ["RESOURCE_REQUEST_RETRIED", "PAYMENT_VERIFIED", "PROOF_REJECTED", "VERIFICATION_UNAVAILABLE", "RESOURCE_DELIVERED", "FULFILLMENT_CONFIRMED"] },
  ],
};

function businessStageFor(stateId) {
  return (businessJourneys[authorizationLevel] || businessJourneys.L1)
    .findIndex((stage) => stage.states.includes(stateId));
}

function renderBusinessJourney(stateId = null, failure = false) {
  const journey = businessJourneys[authorizationLevel] || businessJourneys.L1;
  elements.businessJourney.innerHTML = journey.map((stage, index) =>
    `<div data-stage="${index}"><span>${index + 1}</span><strong>${stage.title}</strong><small>${stage.detail}</small></div>`).join("");
  const activeIndex = businessStageFor(stateId);
  [...elements.businessJourney.children].forEach((item, index) => {
    item.classList.toggle("done", index < activeIndex || (index === 4 && stateId === "FULFILLMENT_CONFIRMED"));
    item.classList.toggle("active", index === activeIndex && !failure);
    item.classList.toggle("failure", index === activeIndex && failure);
  });
  elements.purchaseStatus.textContent = failure
    ? "流程已暂停 · 数据未交付"
    : {
        "PAYMENT_TOOL_STATUS_CHECKED": "正在检查支付能力",
        "WALLET_BINDING_REQUIRED": "需要开通并绑定",
        "WALLET_BINDING_QR_PRESENTED": "等待扫码授权绑定",
        "WALLET_BOUND": "支付宝支付能力已绑定",
        "SPECIFIED_INTENT_CAPTURED": "定向委托目标已明确",
        "SPECIFIED_IAC_ISSUED": "SPECIFIED IAC 已签发",
        "SPECIFIED_IAC_VERIFIED": "定向授权本地校验通过",
        "DEL_PSP_AUTHORIZED": "定向授权权威校验通过",
        "BOUNDED_INTENT_CAPTURED": "自主任务边界已明确",
        "BOUNDED_IAC_ISSUED": "BOUNDED IAC 已签发",
        "AUP_BOUNDARY_CHECKED": "本笔交易在任务边界内",
        "AUP_PSP_AUTHORIZED": "自主支付授权校验通过",
        "CAPABILITY_NEGOTIATED": "正在选择服务",
        "ORDER_CONFIRMED": "购买内容已确认",
        "RESOURCE_REQUESTED": "正在调用数据服务",
        "PAYMENT_REQUIRED": "已报价 · 等待确认",
        "USER_AUTHORIZATION_REQUIRED": "等待用户确认 0.01 元",
        "PAYMENT_QR_PRESENTED": "等待支付宝扫码付款",
        "PAYMENT_PROCESSING": authorizationLevel === "L1" ? "支付宝处理中" : "授权范围内支付处理中",
        "PAYMENT_RESULT_RECEIVED": "付款结果已确认",
        "RESOURCE_REQUEST_RETRIED": "正在请求交付数据",
        "PAYMENT_VERIFIED": "验款通过",
        "RESOURCE_DELIVERED": "数据已交付",
        "FULFILLMENT_CONFIRMED": "报告可以生成",
      }[stateId] || "等待开始";
}

function renderAgentExecution(stateId = null, current = null) {
  const failure = current?.failure === true;
  const delivered = events.some((item) => item.state === "RESOURCE_DELIVERED");
  const toolVisible = events.some((item) => item.state === "CAPABILITY_NEGOTIATED");
  const paymentVisible = events.some((item) => [
    "PAYMENT_REQUIRED", "USER_AUTHORIZATION_REQUIRED", "PAYMENT_QR_PRESENTED", "SPECIFIED_IAC_VERIFIED",
    "DEL_PSP_AUTHORIZED", "AUP_BOUNDARY_CHECKED", "AUP_PSP_AUTHORIZED", "PAYMENT_PROCESSING", "PAYMENT_RESULT_RECEIVED",
    "PAYMENT_PENDING", "RESOURCE_REQUEST_RETRIED", "PAYMENT_VERIFIED", "PROOF_REJECTED",
    "VERIFICATION_UNAVAILABLE", "RESOURCE_DELIVERED", "FULFILLMENT_CONFIRMED",
  ].includes(item.state));
  const paymentKnown = events.some((item) => [
    "PAYMENT_RESULT_RECEIVED", "RESOURCE_REQUEST_RETRIED", "PAYMENT_VERIFIED", "PROOF_REJECTED",
    "VERIFICATION_UNAVAILABLE", "RESOURCE_DELIVERED", "FULFILLMENT_CONFIRMED",
  ].includes(item.state));

  elements.agentThinkingLabel.className = `agent-session-status ${failure ? "failure" : delivered ? "success" : stateId ? "active" : ""}`;
  elements.agentThinkingLabel.textContent = failure ? "需要处理" : delivered ? "任务继续" : stateId ? "正在执行" : "等待任务";
  elements.resourceCard.classList.toggle("hidden", !toolVisible);
  elements.resourceCard.classList.toggle("active", toolVisible && !delivered && !failure);
  elements.resourceCard.classList.toggle("failure", failure);
  elements.resultArtifact.classList.toggle("hidden", !delivered);
  elements.resultArtifact.classList.toggle("delivered", delivered);
  renderAuthorizationCard(stateId, failure);

  if (!stateId) {
    elements.paymentCard.className = "agent-payment-card hidden";
    elements.paymentQr.classList.add("hidden");
    elements.paymentCardStatus.textContent = "待确认";
    elements.paymentCardHint.textContent = "等待服务返回机器账单。";
    return;
  }

  elements.resourceState.textContent = failure ? "调用暂停" : {
    CAPABILITY_NEGOTIATED: "选择服务",
    ORDER_CONFIRMED: "参数已确认",
    RESOURCE_REQUESTED: "调用中",
    PAYMENT_REQUIRED: "等待付款",
    USER_AUTHORIZATION_REQUIRED: "等待确认",
    PAYMENT_QR_PRESENTED: "等待扫码",
    SPECIFIED_IAC_VERIFIED: "授权已校验",
    DEL_PSP_AUTHORIZED: "委托已核准",
    AUP_BOUNDARY_CHECKED: "边界已检查",
    AUP_PSP_AUTHORIZED: "授权已核准",
    PAYMENT_PROCESSING: "付款中",
    PAYMENT_RESULT_RECEIVED: "付款成功",
    RESOURCE_REQUEST_RETRIED: "重新调用",
    PAYMENT_VERIFIED: "验款通过",
    RESOURCE_DELIVERED: "已返回数据",
    FULFILLMENT_CONFIRMED: "调用完成",
  }[stateId] || elements.resourceState.textContent;

  if (!paymentVisible) {
    elements.paymentCard.className = "agent-payment-card hidden";
    elements.paymentQr.classList.add("hidden");
    return;
  }

  const pending = ["PAYMENT_PENDING", "VERIFICATION_UNAVAILABLE"].includes(stateId);
  elements.paymentCard.className = `agent-payment-card ${failure ? "failure" : pending ? "pending" : paymentKnown ? "paid" : "processing"}`;
  elements.paymentCardKind.textContent = authorizationLevel === "L1"
    ? "ALIPAY · 付款确认"
    : authorizationLevel === "L2"
      ? "DEL / L2 · 委托支付语义预览"
      : "AUP / L3 · 自主支付语义预览";
  elements.paymentCardTitle.textContent = authorizationLevel === "L1"
    ? "专业数据服务调用"
    : "产品映射 Validation-pending";
  elements.paymentQr.classList.toggle("hidden", authorizationLevel !== "L1"
    || !["PAYMENT_QR_PRESENTED", "PAYMENT_PROCESSING"].includes(stateId));
  elements.paymentCardStatus.textContent = {
    PAYMENT_REQUIRED: "待确认",
    USER_AUTHORIZATION_REQUIRED: "等待用户",
    PAYMENT_QR_PRESENTED: "等待扫码",
    SPECIFIED_IAC_VERIFIED: "授权已校验",
    DEL_PSP_AUTHORIZED: "委托已核准",
    AUP_BOUNDARY_CHECKED: "边界已检查",
    AUP_PSP_AUTHORIZED: "授权已核准",
    PAYMENT_PROCESSING: "支付处理中",
    PAYMENT_PENDING: "结果待确认",
    PAYMENT_RESULT_RECEIVED: "支付已确认",
    RESOURCE_REQUEST_RETRIED: "支付已确认",
    PAYMENT_VERIFIED: "支付已确认",
    PROOF_REJECTED: "凭据未通过验款",
    VERIFICATION_UNAVAILABLE: "等待验款",
    RESOURCE_DELIVERED: "支付已确认",
    FULFILLMENT_CONFIRMED: "支付已确认",
  }[stateId] || "支付已确认";
  const l1Hint = {
    PAYMENT_REQUIRED: "Agent 已收到 0.01 元报价，准备请求用户逐笔确认。",
    USER_AUTHORIZATION_REQUIRED: "请核对收款方、商品与金额；本页面不会发起真实支付。",
    PAYMENT_QR_PRESENTED: "支付卡片已生成。真实二维码由支付宝官方页面提供；这里是不可扫码的演示占位图。",
    PAYMENT_PROCESSING: "支付宝正在处理本笔交易，Agent 不会重复付款。",
    PAYMENT_PENDING: "结果未知，Agent 只查询原交易，不会再次付款。",
    PAYMENT_RESULT_RECEIVED: "支付结果已确认，Agent 将携脱敏凭据恢复原工具调用。",
    RESOURCE_REQUEST_RETRIED: "Agent 正在使用同一付款结果重新请求数据。",
    PAYMENT_VERIFIED: "服务方已完成验款，等待工具返回数据。",
    PROOF_REJECTED: "付款凭据与订单或资源不一致，工具不会返回数据。",
    VERIFICATION_UNAVAILABLE: "官方验款暂不可用，工具调用暂停并等待重试。",
    RESOURCE_DELIVERED: "支付与验款完成，专业数据已经返回给 Agent。",
    FULFILLMENT_CONFIRMED: "本次服务交付确认完成。",
  };
  const delegatedHint = {
    PAYMENT_REQUIRED: `Agent 已收到 0.01 元报价，准备按 ${authorizationLevel === "L2" ? "SPECIFIED" : "BOUNDED"} IAC 校验授权。`,
    SPECIFIED_IAC_VERIFIED: "Agent 已检查凭证状态、指定目标、金额和受托方绑定。",
    DEL_PSP_AUTHORIZED: "指定商品、商户、金额和次数完全匹配，授权通过后自动执行；这里不声称支付宝已提供对应产品能力。",
    AUP_BOUNDARY_CHECKED: "Agent 已检查本笔金额、目标和累计预算均处于任务边界内。",
    AUP_PSP_AUTHORIZED: "PSP 权威校验自主授权；这里不声称支付宝已提供对应产品能力。",
    PAYMENT_PROCESSING: "正在演示授权范围内的协议支付执行；产品映射仍待验证。",
    PAYMENT_PENDING: "结果未知，只查询原交易，不得再次支付。",
    PAYMENT_RESULT_RECEIVED: "支付结果已确认，Agent 将携脱敏凭据恢复原工具调用。",
    RESOURCE_REQUEST_RETRIED: "Agent 正在使用同一付款结果重新请求数据。",
    PAYMENT_VERIFIED: "服务方已完成验款，等待工具返回数据。",
    PROOF_REJECTED: "付款凭据与订单或资源不一致，工具不会返回数据。",
    VERIFICATION_UNAVAILABLE: "权威验款暂不可用，工具调用暂停并等待重试。",
    RESOURCE_DELIVERED: "支付与验款完成，专业数据已经返回给 Agent。",
    FULFILLMENT_CONFIRMED: "本次服务交付确认完成。",
  };
  elements.paymentCardHint.textContent = (authorizationLevel === "L1" ? l1Hint : delegatedHint)[stateId]
    || "等待本次支付继续处理。";
}

function renderAuthorizationCard(stateId = null, failure = false) {
  if (!stateId) {
    elements.authorizationCard.className = "agent-authorization-card hidden";
    elements.bindingQr.classList.add("hidden");
    elements.bindingCommand.classList.add("hidden");
    return;
  }
  const reached = (candidate) => events.some((event) => event.state === candidate);
  const l1Bound = reached("WALLET_BOUND");
  const l2Issued = reached("SPECIFIED_IAC_ISSUED");
  const l3Issued = reached("BOUNDED_IAC_ISSUED");
  const ready = authorizationLevel === "L1" ? l1Bound : authorizationLevel === "L2" ? l2Issued : l3Issued;
  elements.authorizationCard.className = `agent-authorization-card ${failure ? "failure" : ready ? "ready" : "active"}`;
  elements.bindingQr.classList.toggle("hidden", stateId !== "WALLET_BINDING_QR_PRESENTED");
  elements.bindingCommand.classList.toggle("hidden", stateId !== "WALLET_BOUND");

  if (authorizationLevel === "L1") {
    elements.authorizationCardKind.textContent = "ALIPAY · 首次开通与绑定";
    elements.authorizationCardTitle.textContent = l1Bound ? "支付宝支付能力已就绪" : "绑定支付宝支付能力";
    elements.authorizationCardStatus.textContent = l1Bound ? "已绑定" : stateId === "WALLET_BINDING_QR_PRESENTED" ? "等待扫码" : "处理中";
    elements.authorizationCardDescription.textContent = l1Bound
      ? "账户授权绑定已完成；L1 不授予自动扣款权，后续每一笔仍需用户核身确认。"
      : "首次使用需要在支付宝官方页面完成授权。Demo 二维码不可扫码，也不会保存真实绑定指令。";
    elements.authorizationFacts.innerHTML = ["每笔用户在场", "每笔核身确认", "不可自动扣款"]
      .map((fact) => `<span>${fact}</span>`).join("");
    return;
  }

  const specified = authorizationLevel === "L2";
  elements.authorizationCardKind.textContent = `${specified ? "DEL / L2" : "AUP / L3"} · ACT CANDIDATE`;
  elements.authorizationCardTitle.textContent = specified ? "SPECIFIED 定向委托" : "BOUNDED 自主任务授权";
  elements.authorizationCardStatus.textContent = ready ? "IAC 已签发" : "定义边界";
  elements.authorizationCardDescription.textContent = specified
    ? "商品、商户、金额和次数已明确；完全匹配后自动支付，不再逐笔询问用户。支付宝产品映射仍待验证。"
    : "允许 Agent 在任务、预算、类目、商户和有效期边界内执行多笔子支付；支付宝产品映射仍待验证。";
  const facts = specified
    ? ["资源：market-signal-demo", "金额：0.01 CNY", "次数：1 次"]
    : ["总预算：1.00 CNY", "单笔：≤ 0.20 CNY", "每笔重新校验"];
  elements.authorizationFacts.innerHTML = facts.map((fact) => `<span>${fact}</span>`).join("");
}

function setMode(nextMode) {
  stopInputs();
  mode = nextMode;
  authorizationLevel = mode === "GUIDED_PREVIEW" ? elements.authorizationSelect.value : "L1";
  scenario = mode === "GUIDED_PREVIEW" ? elements.scenarioSelect.value : "SUCCESS";
  events = [];
  replayEvents = [];
  replayIndex = 0;
  previewEvents = createPreviewEvents();
  previewIndex = 0;
  elements.previewTab.classList.toggle("active", mode === "GUIDED_PREVIEW");
  elements.liveTab.classList.toggle("active", mode === "LIVE_SANDBOX");
  elements.replayTab.classList.toggle("active", mode === "SANITIZED_REPLAY");
  elements.previewControls.classList.toggle("hidden", mode !== "GUIDED_PREVIEW");
  elements.authorizationSummary.classList.toggle("hidden", mode !== "GUIDED_PREVIEW");
  elements.liveForm.classList.toggle("hidden", mode !== "LIVE_SANDBOX");
  elements.replayControls.classList.toggle("hidden", mode !== "SANITIZED_REPLAY");
  const baseline = authorizationLevel === "L1" ? "PMT-BND + INS / L1 + A402"
    : authorizationLevel === "L2" ? "ADD + DEL / L2 + A402" : "ADD + AUP / L3 + A402";
  elements.baselineValue.textContent = baseline;
  elements.protocolLayerValue.textContent = baseline;
  elements.footerScenarioValue.textContent = authorizationLevel === "L1" ? "PSD-PAY-INS (L1)" : authorizationLevel === "L2" ? "PSD-PAY-DEL (L2)" : "PSD-PAY-AUP (L3)";
  elements.productLayerValue.textContent = authorizationLevel === "L1" ? "Agent 支付 + AI 按量付费" : "产品映射待验证 · 不声明已上线";
  elements.footerProfileValue.textContent = authorizationLevel === "L1" ? "ALIPAY AI PAY PROFILE" : "ALIPAY PROFILE · VALIDATION-PENDING";
  const copy = authorizationCopy[authorizationLevel];
  elements.authorizationSummary.dataset.level = authorizationLevel;
  elements.authorizationSummaryLevel.textContent = authorizationLevel;
  elements.authorizationSummaryEyebrow.textContent = copy.eyebrow;
  elements.authorizationSummaryTitle.textContent = copy.title;
  elements.authorizationSummaryDescription.textContent = copy.description;
  elements.authorizationSummaryFacts.innerHTML = copy.facts.map((fact) => `<span>${fact}</span>`).join("");
  elements.userPrompt.textContent = copy.prompt;
  elements.introScenarioCopy.textContent = copy.intro;
  elements.pspActorIcon.textContent = authorizationLevel === "L1" ? "支" : "P";
  elements.pspActorName.textContent = authorizationLevel === "L1" ? "支付宝" : "PSP（待验证）";
  elements.pspActorDescription.textContent = authorizationLevel === "L1" ? "支付、查询、验款" : "协议角色，非产品声明";
  elements.layerExplanation.textContent = authorizationLevel === "L1"
    ? "先看懂上面的购买故事，再用这里核对协议边界：ACT 描述协商、授权和支付服务消息；支付宝产品完成支付与验款；示例服务负责真正的数据交付。"
    : "本档只对照 ACT Candidate 的授权与支付语义；PSP 是协议角色，支付宝侧 L2/L3 产品能力仍待验证；示例服务只负责资源交付。";
  if (mode === "GUIDED_PREVIEW") {
    elements.modeBadge.textContent = authorizationLevel === "L1"
      ? "UI PREVIEW · NOT PAYMENT EVIDENCE"
      : `CANDIDATE ${authorizationLevel} · PRODUCT PENDING`;
    elements.modeBadge.className = "mode-badge preview";
    setStatus(authorizationLevel === "L1"
      ? "说明性数据展示首次绑定、笔笔核身确认和 A402 恢复，不代表真实支付或兼容性证据。"
      : `${authorizationLevel} 仅演示 ACT Candidate 协议语义；支付宝产品映射 Validation-pending。`);
  } else if (mode === "LIVE_SANDBOX") {
    elements.eventStreamUrl.value = `${window.location.origin}/events`;
    elements.modeBadge.textContent = "LIVE · NOT CONNECTED";
    elements.modeBadge.className = "mode-badge live";
    setStatus("Demo 不生成支付结果。请连接真实脱敏事件流。");
  } else {
    elements.modeBadge.textContent = "REPLAY · NO FILE";
    elements.modeBadge.className = "mode-badge replay";
    setStatus("请选择由官网沙箱链路生成的脱敏 NDJSON。");
  }
  renderTimeline();
  renderPhaseRail();
  render();
}

function stopInputs() {
  if (eventSource) eventSource.close();
  eventSource = null;
  if (replayTimer) clearInterval(replayTimer);
  if (previewTimer) clearInterval(previewTimer);
  replayTimer = null;
  previewTimer = null;
  elements.playReplay.textContent = "播放";
  elements.playPreview.textContent = "播放当前场景";
}

function createPreviewEvents() {
  const startedAt = Date.now();
  const shared = {
    ...previewBase,
    scenario,
    authorization_level: authorizationLevel,
    goods_name: "AI 支付行业趋势专业数据",
    seller_name: "示例专业数据服务",
  };
  const capability = {
    method_id: "example:a402/alipay-ai-pay",
    method_version: "0.1.0-preview.1",
    psp_id: "alipay",
    endpoint_ref: "endpoint-sha256-6cc2",
    method_schema_ref: "schema-sha256-3bd1",
    capability_source_ref: "capability-sha256-59e4",
    capability_source_validated: true,
  };
  const commerce = { commerce_confirmation_ref: "commerce-sha256-0f21" };
  const request = { http_method: "GET", request_ref: "req-sha256-41bd" };
  const bill = {
    amount: "0.01",
    currency: "CNY",
    resource_id: "market-signal-demo",
    order_ref: "order-sha256-92ae",
    request_fingerprint: "sha-256:AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA",
    profile_mapping: "ALIPAY_PRODUCT_PAYLOAD_TO_ACT_CANDIDATE_EVIDENCE",
  };
  const payment = { transaction_ref: "trade-sha256-8c11", proof_ref: "proof-sha256-a831" };
  const delivery = { delivery_ref: "delivery-sha256-42bd" };
  const fulfillment = {
    fulfillment_ref: "fulfill-sha256-6d2a",
    product_fulfillment_status: "CONFIRMED",
  };
  const delegation = authorizationLevel === "L1" ? {} : {
    delegation_mode: authorizationLevel === "L2" ? "SPECIFIED" : "BOUNDED",
    delegation_id: authorizationLevel === "L2" ? "delegation-sha256-l2a1" : "delegation-sha256-l3b1",
    ...(authorizationLevel === "L3" ? { task_budget: "1.00", per_payment_limit: "0.20" } : {}),
  };
  const currentFlow = flow();
  const successLength = successFlow().length;
  return currentFlow.map((id, index) => {
    const seen = (stateId) => currentFlow.slice(0, index + 1).includes(stateId);
    const replayStep = scenario === "IDEMPOTENT_REPLAY" && index >= successLength;
    const paymentStarted = seen("PAYMENT_PROCESSING") || id === "PAYMENT_PENDING";
    const paymentCompleted = seen("PAYMENT_RESULT_RECEIVED");
    return {
      ...shared,
      ...(authorizationLevel !== "L1" ? delegation : {}),
      ...(seen("CAPABILITY_NEGOTIATED") ? capability : {}),
      ...(seen("ORDER_CONFIRMED") ? commerce : {}),
      ...(seen("RESOURCE_REQUESTED") ? request : {}),
      ...(seen("PAYMENT_REQUIRED") ? bill : {}),
      ...(paymentStarted ? { transaction_ref: payment.transaction_ref } : {}),
      ...(paymentCompleted ? { proof_ref: payment.proof_ref } : {}),
      ...(seen("RESOURCE_DELIVERED") ? delivery : {}),
      ...(seen("FULFILLMENT_CONFIRMED") ? fulfillment : {}),
      sequence: index + 1,
      state: id,
      occurred_at: new Date(startedAt + index * 1000).toISOString(),
      validation_mapping: id === "PAYMENT_VERIFIED" ? "ACT candidate evidence ← Alipay payment.verify result" : undefined,
      idempotent_replay: replayStep && id === "RESOURCE_DELIVERED" ? true : undefined,
      payment_action: replayStep ? "NO_NEW_PAYMENT" : undefined,
      delivery_action: replayStep && id === "RESOURCE_DELIVERED" ? "RETURN_PRIOR_RESULT" : undefined,
      fulfillment_action: replayStep && id === "RESOURCE_DELIVERED" ? "NOT_REPEATED" : undefined,
      recovery_action: {
        PAYMENT_PENDING: "QUERY_ORIGINAL_TRANSACTION · DO_NOT_REPAY",
        PROOF_REJECTED: "DO_NOT_DELIVER · REISSUE_OR_RECONCILE",
        VERIFICATION_UNAVAILABLE: "RETRY_SAME_VERIFICATION · DO_NOT_DELIVER",
      }[id],
      result_summary: replayStep && id === "RESOURCE_DELIVERED"
        ? "返回既有交付结果；未重复支付、交付或履约确认"
        : {
            RESOURCE_DELIVERED: "专业数据已交付给 Agent",
            FULFILLMENT_CONFIRMED: "卖方产品履约确认完成；TSD 证据未自动生成",
          }[id],
    };
  });
}

function validateSensitiveKeys(value, path = "event") {
  if (!value || typeof value !== "object") return;
  for (const [key, child] of Object.entries(value)) {
    if (forbiddenKeys.test(key)) throw new Error(`${path} 包含禁止展示的敏感字段：${key}`);
    validateSensitiveKeys(child, `${path}.${key}`);
  }
}

function validateEvent(event, expectedIndex, expectedMode) {
  validateSensitiveKeys(event);
  const expectedId = flow()[expectedIndex];
  if (!expectedId) throw new Error("事件数量超过当前场景状态数");
  if (event.sequence !== expectedIndex + 1) throw new Error(`事件序号应为 ${expectedIndex + 1}`);
  if (event.state !== expectedId) throw new Error(`下一状态必须是 ${expectedId}`);
  if (event.mode !== expectedMode) throw new Error(`事件模式必须为 ${expectedMode}`);
  if ((event.scenario || "SUCCESS") !== scenario) throw new Error(`事件场景必须为 ${scenario}`);
  if ((event.authorization_level || "L1") !== authorizationLevel) throw new Error(`事件授权级别必须为 ${authorizationLevel}`);
  if (!event.source || /mock/i.test(event.source)) throw new Error("事件必须标明非 Mock 来源");
  if (!event.evidence_ref || !event.correlation_ref) throw new Error("事件缺少证据或关联引用");
  if (!Number.isFinite(Date.parse(event.occurred_at))) throw new Error("事件时间格式无效");
  validateCandidateEvidence(event, expectedIndex);
  if (expectedMode === "LIVE_SANDBOX" && event.environment !== "SANDBOX") {
    throw new Error("Live 事件必须声明 SANDBOX 环境");
  }
  if (expectedMode === "SANITIZED_REPLAY" && (event.sanitized !== true || !event.origin_validation_id)) {
    throw new Error("Replay 事件必须包含脱敏标记和原验证编号");
  }
  if (expectedMode === "GUIDED_PREVIEW"
      && (event.source !== previewBase.source || event.evidence_ref !== previewBase.evidence_ref)) {
    throw new Error("演示预览不能冒充支付证据");
  }
}

const methodIdPattern = /^[a-z][a-z0-9+.-]*:[a-z0-9][a-z0-9._/-]*$/;
const methodVersionPattern = /^(0|[1-9][0-9]*)\.(0|[1-9][0-9]*)\.(0|[1-9][0-9]*)(?:-[0-9A-Za-z.-]+)?$/;
const fingerprintPattern = /^sha-256:[A-Za-z0-9_-]{43}$/;

function validateCandidateEvidence(event, expectedIndex) {
  const capabilityIndex = flow().indexOf("CAPABILITY_NEGOTIATED");
  if (expectedIndex >= capabilityIndex) {
    if (!methodIdPattern.test(event.method_id || "")) throw new Error("method_id 不符合 Candidate 命名空间格式");
    if (!methodVersionPattern.test(event.method_version || "")) throw new Error("method_version 必须使用 SemVer");
  }
  if (authorizationLevel !== "L1") {
    const expectedMode = authorizationLevel === "L2" ? "SPECIFIED" : "BOUNDED";
    if (event.delegation_mode !== expectedMode || !event.delegation_id) {
      throw new Error(`${authorizationLevel} 事件缺少 ${expectedMode} IAC 关联`);
    }
  }
  if (event.state === "CAPABILITY_NEGOTIATED") {
    for (const field of ["psp_id", "endpoint_ref", "method_schema_ref", "capability_source_ref"]) {
      if (!event[field]) throw new Error(`能力协商缺少 ${field}`);
    }
    if (event.capability_source_validated !== true) throw new Error("能力声明来源尚未验证");
  }
  if (event.state === "ORDER_CONFIRMED" && !event.commerce_confirmation_ref) {
    throw new Error("订单确认缺少独立 commerce_confirmation_ref");
  }
  if (["PAYMENT_REQUIRED", "RESOURCE_REQUEST_RETRIED", "PAYMENT_VERIFIED", "RESOURCE_DELIVERED"].includes(event.state)) {
    if (!fingerprintPattern.test(event.request_fingerprint || "")) throw new Error("事件缺少合法 request_fingerprint");
    for (const field of ["order_ref", "resource_id"]) {
      if (!event[field]) throw new Error(`${event.state} 缺少 ${field}`);
    }
  }
  if (event.state === "PAYMENT_REQUIRED") {
    for (const field of ["amount", "currency", "profile_mapping"]) {
      if (!event[field]) throw new Error(`Payment-Needed 证据缺少 ${field}`);
    }
  }
  if (event.state === "PAYMENT_RESULT_RECEIVED" && (!event.transaction_ref || !event.proof_ref)) {
    throw new Error("支付结果缺少交易或 Proof 脱敏引用");
  }
  if (event.state === "PAYMENT_VERIFIED" && (!event.transaction_ref || !event.validation_mapping)) {
    throw new Error("验款事件缺少权威交易或映射引用");
  }
  if (event.state === "RESOURCE_DELIVERED" && (!event.transaction_ref || !event.delivery_ref)) {
    throw new Error("资源交付缺少独立交付引用");
  }
  if (event.state === "FULFILLMENT_CONFIRMED"
      && (!event.transaction_ref || !event.fulfillment_ref || event.product_fulfillment_status !== "CONFIRMED")) {
    throw new Error("履约确认缺少独立产品确认事实");
  }
  if (scenario === "IDEMPOTENT_REPLAY" && expectedIndex === flow().length - 1) {
    if (event.idempotent_replay !== true
        || event.payment_action !== "NO_NEW_PAYMENT"
        || event.delivery_action !== "RETURN_PRIOR_RESULT"
        || event.fulfillment_action !== "NOT_REPEATED") {
      throw new Error("幂等重放缺少不重复支付、交付和履约确认的证据");
    }
  }
}

function parseNdjson(text) {
  return text.split(/\r?\n/).filter((line) => line.trim()).map((line, index) => {
    try {
      return JSON.parse(line);
    } catch {
      throw new Error(`第 ${index + 1} 行不是有效 JSON`);
    }
  });
}

function addEvent(event) {
  validateEvent(event, events.length, mode);
  validateChainInvariants(event);
  const prior = events.at(-1);
  if (prior && Date.parse(event.occurred_at) < Date.parse(prior.occurred_at)) {
    throw new Error("事件时间不能倒序");
  }
  events.push(event);
  render();
}

function validateChainInvariants(event) {
  const invariantFields = [
    "correlation_ref", "authorization_level", "delegation_mode", "delegation_id", "method_id", "method_version", "psp_id", "commerce_confirmation_ref",
    "order_ref", "resource_id", "request_fingerprint", "amount", "currency", "transaction_ref",
  ];
  for (const field of invariantFields) {
    const priorValue = findLatest(field);
    if (priorValue !== undefined && event[field] !== undefined && event[field] !== priorValue) {
      throw new Error(`${field} 与当前链路既有事实不一致`);
    }
  }
}

function render() {
  const currentIndex = events.length - 1;
  const event = events[currentIndex];
  const current = event ? displayState(event.state, currentIndex) : null;
  [...elements.timeline.children].forEach((item, index) => {
    item.classList.toggle("done", index < currentIndex);
    item.classList.toggle("current", index === currentIndex);
  });
  elements.eventCounter.textContent = `${events.length} / ${flow().length}`;
  elements.taskStatusDot.classList.toggle("active", events.length > 0);
  if (!current) {
    elements.currentState.textContent = "等待开始";
    elements.stateExplanation.textContent = "这里会解释同一个动作在 ACT 场景组件、A402 Binding 与支付宝产品中的位置。";
    ["actDomain", "actComponent", "actBinding", "alipayProduct", "profileMapping"].forEach((id) => { elements[id].textContent = "—"; });
    elements.layerCode.textContent = "READY";
    elements.fromActor.textContent = "—";
    elements.toActor.textContent = "—";
    elements.directionArrow.textContent = "→";
    elements.wireBadge.textContent = "WAITING";
    elements.wireMessage.textContent = "选择一个场景，然后逐步播放协议消息";
    elements.exchangeCard.className = "exchange-card idle";
    setActorFocus(null, null);
    renderPhaseRail();
    elements.agentMessage.textContent = authorizationCopy[authorizationLevel].idle;
    elements.businessActionTitle.textContent = "等待 Agent 开始任务";
    elements.evidenceRef.textContent = "NO EVIDENCE";
    elements.methodId.textContent = "—";
    elements.tsdStatus.textContent = "NOT EMITTED · OPTIONAL";
    elements.correlationChain.textContent = "等待建立关联链";
    renderBusinessJourney();
    renderAgentExecution();
    renderEvidence(null);
    lockResource();
    return;
  }
  elements.currentState.textContent = current.label;
  elements.stateExplanation.textContent = current.explanation;
  elements.actDomain.textContent = current.domain;
  elements.actComponent.textContent = current.component;
  elements.actBinding.textContent = current.binding;
  elements.profileMapping.textContent = current.profile || "Demo evidence observation";
  elements.alipayProduct.textContent = current.product;
  elements.layerCode.textContent = current.code;
  renderExchange(event.state, current);
  renderBusinessJourney(event.state, current.failure === true);
  elements.businessActionTitle.textContent = current.label;
  elements.agentMessage.textContent = current.agent;
  elements.evidenceRef.textContent = event.evidence_ref;
  elements.methodId.textContent = event.method_id || findLatest("method_id") || "—";
  elements.tsdStatus.textContent = event.tsd_evidence_ref || findLatest("tsd_evidence_ref") || "NOT EMITTED · OPTIONAL";
  elements.correlationChain.textContent = correlationText();
  renderEvidence(event);
  applyResource(event, current);
  renderAgentExecution(event.state, current);
  if (events.length === flow().length) {
    elements.taskResult.textContent = current.failure
      ? `报告暂停：${current.label}，专业数据没有交付，也不会把付款或交付状态猜成成功。`
      : "专业数据已经进入 Agent 上下文，《2026 AI 支付趋势报告》可以生成。";
  }
}

function renderExchange(stateId, current) {
  let exchange = exchangeCatalog[stateId] || { from: "buyer", to: "seller", message: stateId };
  if (stateId === "PAYMENT_PROCESSING" && authorizationLevel !== "L1") {
    exchange = {
      from: "buyer",
      to: "psp",
      message: authorizationLevel === "L2"
        ? "依据已验证的 SPECIFIED IAC 执行本笔定向委托支付"
        : "依据 BOUNDED IAC 在剩余预算内执行本笔子支付",
    };
  }
  elements.fromActor.textContent = actorLabels[exchange.from];
  elements.toActor.textContent = actorLabels[exchange.to];
  elements.directionArrow.textContent = exchange.from === exchange.to ? "↻" : "→";
  elements.wireBadge.textContent = current.phase;
  elements.wireMessage.textContent = exchange.message;
  elements.exchangeCard.className = `exchange-card ${current.failure ? "failure" : ""}`;
  setActorFocus(exchange.from, exchange.to);
  renderPhaseRail(stateId);
}

function setActorFocus(from, to) {
  for (const actor of ["principal", "buyer", "seller", "psp", "auth"]) {
    const element = elements[`${actor}Actor`];
    element.classList.toggle("sending", actor === from);
    element.classList.toggle("receiving", actor === to);
  }
}

function findLatest(key) {
  return [...events].reverse().find((item) => item[key])?.[key];
}

function correlationText() {
  const fields = [
    ["IAC", findLatest("delegation_id")],
    ["COMMERCE", findLatest("commerce_confirmation_ref")],
    ["REQ", findLatest("request_ref")],
    ["FINGERPRINT", findLatest("request_fingerprint")],
    ["ORDER", findLatest("order_ref")],
    ["RESOURCE", findLatest("resource_id")],
    ["TRADE", findLatest("transaction_ref")],
    ["FULFILL", findLatest("fulfillment_ref")],
  ].filter(([, value]) => value);
  return fields.length ? fields.map(([key, value]) => `${key} ${value}`).join("  →  ") : "等待建立关联链";
}

function renderEvidence(event) {
  const rows = event
    ? [
        ["来源", event.source],
        ["时间", new Date(event.occurred_at).toLocaleTimeString("zh-CN", { hour12: false })],
        ...detailKeys.filter((key) => event[key]).slice(0, 4).map((key) => [labelFor(key), event[key]]),
      ]
    : [["来源", "—"], ["时间", "—"], ["结果", "—"]];
  elements.evidenceDetails.innerHTML = rows.map(([label, value]) =>
    `<div><dt>${escapeHtml(label)}</dt><dd>${escapeHtml(String(value))}</dd></div>`).join("");
}

function labelFor(key) {
  return {
    amount: "金额", currency: "币种", fulfillment_ref: "产品履约", http_method: "原请求",
    authorization_level: "授权级别", delegation_mode: "委托模式", delegation_id: "IAC 关联",
    commerce_confirmation_ref: "商业确认", delivery_ref: "交付", idempotent_replay: "幂等重放",
    method_id: "支付方法", method_version: "方法版本", order_ref: "支付订单", psp_id: "PSP", proof_ref: "Proof 引用",
    request_fingerprint: "请求指纹", request_ref: "请求",
    resource_id: "资源", transaction_ref: "交易", validation_mapping: "验证映射",
    recovery_action: "恢复动作",
  }[key] || key;
}

function applyResource(event, current) {
  const amount = findLatest("amount");
  const currency = findLatest("currency") || "CNY";
  const resourceId = findLatest("resource_id");
  const goodsName = findLatest("goods_name");
  if (amount) elements.resourcePrice.textContent = `${amount} ${currency}`;
  if (resourceId) elements.resourceId.textContent = `resource ${resourceId}`;
  if (goodsName) elements.resourceTitle.textContent = goodsName;
  const delivered = events.some((item) => item.state === "RESOURCE_DELIVERED");
  elements.resourceCard.classList.toggle("locked", !delivered);
  elements.resourceCard.classList.toggle("delivered", delivered);
  const paymentResultKnown = events.some((item) => item.state === "PAYMENT_RESULT_RECEIVED");
  elements.resourceState.textContent = delivered
    ? "已交付"
    : current.failure
      ? "未交付"
      : paymentResultKnown
        ? "待验款"
        : events.some((item) => item.state === "PAYMENT_REQUIRED")
          ? "待付款"
          : "待购买";
  elements.resourceDescription.textContent = delivered
    ? "最近 30 天的结构化市场信号已返回，并进入 Agent 的报告上下文。"
    : current.failure
      ? "当前路径未满足交付条件，趋势数据保持锁定。"
      : "调用一次，返回最近 30 天的结构化市场信号；只有验款通过才会交付。";
  elements.taskResult.textContent = delivered
    ? "趋势数据已收到，Agent 正在生成包含结论、图表和来源摘要的报告。"
    : current.failure
      ? "专业数据未交付，报告不会使用不存在的付费数据。"
      : "数据尚未交付，报告暂不能完成。";
}

function lockResource() {
  elements.resourceCard.className = "resource-card tool-call-card locked hidden";
  elements.resourceState.textContent = "待调用";
  elements.resourceTitle.textContent = "AI 支付行业趋势数据 API";
  elements.resourceDescription.textContent = "调用一次，返回最近 30 天的结构化市场信号，供 Agent 生成报告。";
  elements.resourcePrice.textContent = "0.01 CNY";
  elements.resourceId.textContent = "market-signal-demo";
  elements.taskResult.textContent = "数据尚未交付，报告暂不能完成。";
  elements.tsdStatus.textContent = "NOT EMITTED · OPTIONAL";
}

function setStatus(message, error = false) {
  elements.controlStatus.textContent = message;
  elements.controlStatus.classList.toggle("error", error);
}

function escapeHtml(value) {
  return value.replace(/[&<>"']/g, (character) => ({
    "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#039;",
  })[character]);
}

function stepPreview() {
  if (previewIndex >= previewEvents.length) return;
  try {
    addEvent(previewEvents[previewIndex++]);
    if (previewIndex === previewEvents.length) {
      stopInputs();
      elements.playPreview.textContent = "重新播放";
      setStatus("当前场景演示完成。以上为说明性数据，不是支付或沙箱验证证据。");
    }
  } catch (error) {
    stopInputs();
    setStatus(`演示预览已停止：${error.message}`, true);
  }
}

elements.previewTab.addEventListener("click", () => setMode("GUIDED_PREVIEW"));
elements.liveTab.addEventListener("click", () => setMode("LIVE_SANDBOX"));
elements.replayTab.addEventListener("click", () => setMode("SANITIZED_REPLAY"));
elements.scenarioSelect.addEventListener("change", () => setMode("GUIDED_PREVIEW"));
elements.authorizationSelect.addEventListener("change", () => setMode("GUIDED_PREVIEW"));
elements.stepPreview.addEventListener("click", stepPreview);
elements.resetPreview.addEventListener("click", () => setMode("GUIDED_PREVIEW"));
elements.playPreview.addEventListener("click", () => {
  if (previewIndex >= previewEvents.length) {
    events = [];
    previewEvents = createPreviewEvents();
    previewIndex = 0;
    render();
  }
  if (previewTimer) {
    clearInterval(previewTimer);
    previewTimer = null;
    elements.playPreview.textContent = "继续";
    setStatus("演示预览已暂停。");
    return;
  }
  elements.playPreview.textContent = "暂停";
  setStatus("正在播放说明性链路，页面不会调用任何支付能力。");
  stepPreview();
  if (previewIndex < previewEvents.length) previewTimer = setInterval(stepPreview, 900);
});

elements.liveForm.addEventListener("submit", (submitEvent) => {
  submitEvent.preventDefault();
  const url = elements.eventStreamUrl.value.trim();
  if (!url) return setStatus("请输入只输出脱敏事件的 SSE 地址。", true);
  stopInputs();
  events = [];
  scenario = "SUCCESS";
  renderTimeline();
  render();
  eventSource = new EventSource(url);
  elements.modeBadge.textContent = "LIVE · CONNECTING";
  setStatus("正在连接真实沙箱事件流…");
  eventSource.onopen = () => {
    elements.modeBadge.textContent = "LIVE SANDBOX · TARGET BASELINE";
    setStatus("已连接。等待真实事件，不会自动推进状态。");
  };
  eventSource.onmessage = (message) => {
    try {
      const next = JSON.parse(message.data);
      if (events.length === 0 && next.scenario) {
        scenario = next.scenario;
        if (!["SUCCESS", "PAYMENT_PENDING", "PROOF_MISMATCH", "VERIFICATION_UNAVAILABLE", "IDEMPOTENT_REPLAY"].includes(scenario)) {
          throw new Error(`不支持场景 ${scenario}`);
        }
        renderTimeline();
      }
      addEvent(next);
      setStatus(`已接收 ${events.length} / ${flow().length} 个真实事件。`);
    } catch (error) {
      eventSource.close();
      setStatus(`事件流已停止：${error.message}`, true);
    }
  };
  eventSource.addEventListener("reset", () => {
    events = [];
    scenario = "SUCCESS";
    renderTimeline();
    render();
    setStatus("事件 Bridge 已重置，等待新的真实链路。");
  });
  eventSource.onerror = () => {
    eventSource.close();
    elements.modeBadge.textContent = "LIVE · DISCONNECTED";
    setStatus("事件流连接中断。页面不会推断后续支付结果。", true);
  };
});

elements.replayFile.addEventListener("change", async () => {
  stopInputs();
  events = [];
  replayIndex = 0;
  try {
    const file = elements.replayFile.files[0];
    if (!file) return;
    replayEvents = parseNdjson(await file.text());
    scenario = replayEvents[0]?.scenario || "SUCCESS";
    if (!["SUCCESS", "PAYMENT_PENDING", "PROOF_MISMATCH", "VERIFICATION_UNAVAILABLE", "IDEMPOTENT_REPLAY"].includes(scenario)) {
      throw new Error(`不支持场景 ${scenario}`);
    }
    renderTimeline();
    if (replayEvents.length !== flow().length) throw new Error(`Replay 必须包含当前场景的 ${flow().length} 个状态`);
    replayEvents.forEach((event, index) => validateEvent(event, index, "SANITIZED_REPLAY"));
    elements.playReplay.disabled = false;
    elements.stepReplay.disabled = false;
    elements.modeBadge.textContent = "SANITIZED REPLAY";
    setStatus(`已验证 ${file.name}。尚未播放，不代表实时支付。`);
    render();
  } catch (error) {
    replayEvents = [];
    elements.playReplay.disabled = true;
    elements.stepReplay.disabled = true;
    elements.modeBadge.textContent = "REPLAY · REJECTED";
    setStatus(`拒绝加载：${error.message}`, true);
  }
});

elements.stepReplay.addEventListener("click", () => {
  if (replayIndex >= replayEvents.length) return;
  try {
    addEvent(replayEvents[replayIndex++]);
    if (replayIndex === replayEvents.length) {
      elements.stepReplay.disabled = true;
      elements.playReplay.disabled = true;
      setStatus("Replay 播放完成。内容来自已验证链路的脱敏记录。");
    }
  } catch (error) {
    setStatus(`Replay 已停止：${error.message}`, true);
  }
});

elements.playReplay.addEventListener("click", () => {
  if (replayTimer) {
    clearInterval(replayTimer);
    replayTimer = null;
    elements.playReplay.textContent = "继续";
    return;
  }
  elements.playReplay.textContent = "暂停";
  replayTimer = setInterval(() => {
    if (replayIndex >= replayEvents.length) {
      clearInterval(replayTimer);
      replayTimer = null;
      elements.playReplay.textContent = "播放";
      elements.playReplay.disabled = true;
      elements.stepReplay.disabled = true;
      setStatus("Replay 播放完成。内容来自已验证链路的脱敏记录。");
      return;
    }
    addEvent(replayEvents[replayIndex++]);
  }, 900);
});

setMode("GUIDED_PREVIEW");
