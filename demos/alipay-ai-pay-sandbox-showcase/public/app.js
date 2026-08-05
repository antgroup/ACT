const stateCatalog = {
  CAPABILITY_NEGOTIATED: {
    label: "能力协商",
    phase: "CID",
    domain: "CID",
    component: "CID-PCA-NEG",
    binding: "Capability negotiation",
    product: "支付宝 AI 付 Profile",
    code: "CID · NEG",
    explanation: "Buyer 与 Seller 在支付前确认 method_id、PSP 和接入端点。A402 不隐含某个支付场景。",
    agent: "已确认该服务支持支付宝 AI 付，并选择双方共同支持的支付方法。",
  },
  ORDER_CONFIRMED: {
    label: "订单确认",
    phase: "CID",
    domain: "CID",
    component: "CID-CART-CFM",
    binding: "Request / order binding",
    product: "交易摘要与商户订单",
    code: "CID · CFM",
    explanation: "确认商品、金额、币种、资源和原请求摘要，建立后续 Needed、Proof 与交付的关联链。",
    agent: "已锁定商品和订单，并保存原始资源请求摘要。",
  },
  RESOURCE_REQUESTED: {
    label: "资源请求",
    phase: "A402",
    domain: "CID + PSD",
    component: "Paid resource request",
    binding: "Original HTTP request",
    product: "AI 按量付费 · 收费资源",
    code: "A402 · REQ",
    explanation: "Agent 发起原始 GET/POST 资源请求；方法、目标与请求摘要必须能在支付后恢复。",
    agent: "正在访问完成报告所需的专业数据服务。",
  },
  PAYMENT_REQUIRED: {
    label: "机器出账",
    phase: "A402",
    domain: "PSD",
    component: "PSD-PAY-A402 · Payment-Needed",
    binding: "HTTP 402 + Base64URL JSON",
    product: "AI 按量付费 · 机器账单",
    code: "A402 · 402",
    explanation: "Seller 返回机器可读 Payment-Needed，并回显已协商的 method_id；资源继续锁定。",
    agent: "服务返回了一张机器账单。我正在核对商品、金额、支付方法和有效期。",
  },
  USER_AUTHORIZATION_REQUIRED: {
    label: "逐笔授权",
    phase: "INS / L1",
    domain: "PSD",
    component: "PSD-PAY-INS · L1",
    binding: "Official Skill / CLI",
    product: "Agent 支付 · 用户在场",
    code: "INS · L1",
    explanation: "PSP 产品运行时选择 L1。用户看到金额、商户与支付方式，并对本笔支付完成确认和身份验证。",
    agent: "需要购买这份专业数据。请确认收款方、商品、金额和支付方式。",
  },
  PAYMENT_PROCESSING: {
    label: "支付处理中",
    phase: "INS / L1",
    domain: "PSD",
    component: "Payment execution / status",
    binding: "Official Skill / CLI",
    product: "Agent 支付 · 支付与查询",
    code: "INS · PAY",
    explanation: "支付宝官方能力处理本次支付；结果未知时查询原交易，不能创建第二笔支付。",
    agent: "支付宝正在处理本次支付。结果确认前不会重复付款。",
  },
  PAYMENT_RESULT_RECEIVED: {
    label: "支付结果",
    phase: "INS / L1",
    domain: "PSD",
    component: "Payment result / Proof reference",
    binding: "Official Skill / CLI",
    product: "Agent 支付 · 支付结果",
    code: "INS · RESULT",
    explanation: "Buyer 收到支付结果和可提交给 Seller 的 Proof。Demo 只记录脱敏引用，不记录完整 Proof。",
    agent: "支付结果已确认。我将用支付凭据恢复原来的资源请求。",
  },
  RESOURCE_REQUEST_RETRIED: {
    label: "携 Proof 重试",
    phase: "A402",
    domain: "PSD",
    component: "PSD-PAY-A402 · Payment-Proof",
    binding: "Original request + Payment-Proof",
    product: "AI 按量付费 · 二次资源请求",
    code: "A402 · PROOF",
    explanation: "Buyer 以相同方法和目标重试原请求，并携带 Payment-Proof；Seller 仍将 Proof 视为不可信输入。",
    agent: "正在携带支付凭据重试同一个资源请求。",
  },
  PAYMENT_VERIFIED: {
    label: "卖方验款",
    phase: "A402",
    domain: "PSD",
    component: "Proof verification / Validation mapping",
    binding: "Alipay payment.verify",
    product: "AI 按量付费 · payment.verify",
    code: "A402 · VERIFY",
    explanation: "Seller 通过支付宝官方接口核验状态、金额、订单、资源和防重。候选 Payment-Validation 映射到验款结果，不冒充已上线 Header。",
    agent: "卖方已通过支付宝官方接口完成验款，正在准备交付资源。",
  },
  RESOURCE_DELIVERED: {
    label: "资源交付",
    phase: "FULFILLMENT",
    domain: "CID + PSD",
    component: "Resource delivery",
    binding: "HTTP success response",
    product: "AI 按量付费 · 服务交付",
    code: "DELIVERY",
    explanation: "验款通过后，Seller 对同一请求返回对应资源；重复请求只返回幂等结果。",
    agent: "专业数据已经交付，我正在把它整理成最终报告。",
  },
  FULFILLMENT_CONFIRMED: {
    label: "履约确认",
    phase: "FULFILLMENT",
    domain: "PSD + TSD",
    component: "Fulfillment receipt / optional evidence",
    binding: "Alipay fulfillment.confirm",
    product: "AI 按量付费 · 履约确认",
    code: "RECEIPT",
    explanation: "资源交付后形成履约回执。可向 TSD 发布脱敏事件，但 TSD 不执行支付。",
    agent: "数据购买与履约均已完成，报告已生成。",
  },
  PAYMENT_PENDING: {
    label: "结果待确认",
    phase: "RECOVERY",
    domain: "PSD",
    component: "Transaction state recovery",
    binding: "Query original transaction",
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
    binding: "payment.verify rejection",
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
    product: "AI 按量付费 · payment.verify",
    code: "RETRY",
    explanation: "官方验款暂不可用。Seller 返回可重试错误，不能猜测支付成功或提前交付。",
    agent: "验款服务暂不可用。稍后会重试同一交易，不会重复扣款。",
    failure: true,
  },
};

const scenarioFlows = {
  SUCCESS: [
    "CAPABILITY_NEGOTIATED", "ORDER_CONFIRMED", "RESOURCE_REQUESTED", "PAYMENT_REQUIRED",
    "USER_AUTHORIZATION_REQUIRED", "PAYMENT_PROCESSING", "PAYMENT_RESULT_RECEIVED",
    "RESOURCE_REQUEST_RETRIED", "PAYMENT_VERIFIED", "RESOURCE_DELIVERED", "FULFILLMENT_CONFIRMED",
  ],
  PAYMENT_PENDING: [
    "CAPABILITY_NEGOTIATED", "ORDER_CONFIRMED", "RESOURCE_REQUESTED", "PAYMENT_REQUIRED",
    "USER_AUTHORIZATION_REQUIRED", "PAYMENT_PROCESSING", "PAYMENT_PENDING",
  ],
  PROOF_MISMATCH: [
    "CAPABILITY_NEGOTIATED", "ORDER_CONFIRMED", "RESOURCE_REQUESTED", "PAYMENT_REQUIRED",
    "USER_AUTHORIZATION_REQUIRED", "PAYMENT_PROCESSING", "PAYMENT_RESULT_RECEIVED",
    "RESOURCE_REQUEST_RETRIED", "PROOF_REJECTED",
  ],
  VERIFICATION_UNAVAILABLE: [
    "CAPABILITY_NEGOTIATED", "ORDER_CONFIRMED", "RESOURCE_REQUESTED", "PAYMENT_REQUIRED",
    "USER_AUTHORIZATION_REQUIRED", "PAYMENT_PROCESSING", "PAYMENT_RESULT_RECEIVED",
    "RESOURCE_REQUEST_RETRIED", "VERIFICATION_UNAVAILABLE",
  ],
  IDEMPOTENT_REPLAY: [
    "CAPABILITY_NEGOTIATED", "ORDER_CONFIRMED", "RESOURCE_REQUESTED", "PAYMENT_REQUIRED",
    "USER_AUTHORIZATION_REQUIRED", "PAYMENT_PROCESSING", "PAYMENT_RESULT_RECEIVED",
    "RESOURCE_REQUEST_RETRIED", "PAYMENT_VERIFIED", "RESOURCE_DELIVERED", "FULFILLMENT_CONFIRMED",
  ],
};

const exchangeCatalog = {
  CAPABILITY_NEGOTIATED: { from: "buyer", to: "seller", message: "Capability Offer → method_id selected" },
  ORDER_CONFIRMED: { from: "buyer", to: "seller", message: "Order Context + Original Request Digest" },
  RESOURCE_REQUESTED: { from: "buyer", to: "seller", message: "GET /paid-resource" },
  PAYMENT_REQUIRED: { from: "seller", to: "buyer", message: "HTTP 402 · Payment-Needed" },
  USER_AUTHORIZATION_REQUIRED: { from: "buyer", to: "principal", message: "L1 · Confirm merchant, goods and amount" },
  PAYMENT_PROCESSING: { from: "principal", to: "psp", message: "Official Skill / CLI · Execute Payment" },
  PAYMENT_RESULT_RECEIVED: { from: "psp", to: "buyer", message: "Payment Result + Proof Reference" },
  RESOURCE_REQUEST_RETRIED: { from: "buyer", to: "seller", message: "GET /paid-resource + Payment-Proof" },
  PAYMENT_VERIFIED: { from: "seller", to: "psp", message: "payment.verify(trade, order, amount, resource)" },
  RESOURCE_DELIVERED: { from: "seller", to: "buyer", message: "HTTP 200 · Paid Resource" },
  FULFILLMENT_CONFIRMED: { from: "seller", to: "psp", message: "fulfillment.confirm" },
  PAYMENT_PENDING: { from: "buyer", to: "psp", message: "Query Original Transaction · DO NOT REPAY" },
  PROOF_REJECTED: { from: "seller", to: "buyer", message: "Proof Rejected · DO NOT DELIVER" },
  VERIFICATION_UNAVAILABLE: { from: "psp", to: "seller", message: "503 Retry-After · DO NOT DELIVER" },
};

const actorLabels = {
  principal: "用户",
  buyer: "Buyer Agent",
  seller: "收费服务",
  psp: "支付宝",
};

const phaseCatalog = [
  { id: "CONTEXT", eyebrow: "CID", label: "协商与订单", states: ["CAPABILITY_NEGOTIATED", "ORDER_CONFIRMED"] },
  { id: "NEEDED", eyebrow: "A402", label: "请求与出账", states: ["RESOURCE_REQUESTED", "PAYMENT_REQUIRED"] },
  {
    id: "PAY",
    eyebrow: "INS / L1",
    label: "确认与支付",
    states: ["USER_AUTHORIZATION_REQUIRED", "PAYMENT_PROCESSING", "PAYMENT_RESULT_RECEIVED", "PAYMENT_PENDING"],
  },
  {
    id: "PROOF",
    eyebrow: "A402",
    label: "Proof 与验款",
    states: ["RESOURCE_REQUEST_RETRIED", "PAYMENT_VERIFIED", "PROOF_REJECTED", "VERIFICATION_UNAVAILABLE"],
  },
  { id: "DELIVERY", eyebrow: "FULFILLMENT", label: "交付与履约", states: ["RESOURCE_DELIVERED", "FULFILLMENT_CONFIRMED"] },
];

const forbiddenKeys = /(^|_)(secret|private_key|access_token|app_auth_token|payment_proof|client_session|binding_code|password)($|_)/i;
const detailKeys = [
  "method_id", "psp_id", "http_method", "request_ref", "order_ref", "transaction_ref",
  "resource_id", "amount", "currency", "validation_mapping", "fulfillment_ref", "recovery_action",
];
const previewBase = {
  mode: "GUIDED_PREVIEW",
  source: "illustrative-ui-preview",
  environment: "NOT_APPLICABLE",
  evidence_ref: "UI-PREVIEW-NOT-PAYMENT-EVIDENCE",
  correlation_ref: "corr-preview-7f3a",
};

const elements = Object.fromEntries(
  [
    "actBinding", "actComponent", "actDomain", "agentMessage", "alipayProduct", "controlStatus",
    "correlationChain", "currentState", "eventCounter", "eventStreamUrl", "evidenceDetails",
    "evidenceRef", "exchangeCard", "fromActor", "directionArrow", "layerCode", "liveForm",
    "liveTab", "methodId", "modeBadge", "phaseRail", "playReplay",
    "replayControls", "replayFile", "replayTab", "playPreview", "previewControls", "previewTab",
    "resetPreview", "resourceCard", "resourceDescription", "resourceId", "resourcePrice",
    "resourceState", "resourceTitle", "scenarioSelect", "stateExplanation", "stepPreview",
    "stepReplay", "taskResult", "taskStatusDot", "timeline", "toActor", "wireBadge", "wireMessage",
    "principalActor", "buyerActor", "sellerActor", "pspActor",
  ].map((id) => [id, document.getElementById(id)]),
);

let mode = "GUIDED_PREVIEW";
let scenario = "SUCCESS";
let events = [];
let replayEvents = [];
let replayIndex = 0;
let replayTimer = null;
let eventSource = null;
let previewEvents = [];
let previewIndex = 0;
let previewTimer = null;

function flow() {
  return scenarioFlows[scenario] || scenarioFlows.SUCCESS;
}

function renderTimeline() {
  elements.timeline.innerHTML = flow().map((id, index) => {
    const state = stateCatalog[id];
    return `<li class="timeline-item ${state.failure ? "failure" : ""}" data-index="${index}">
      <span class="timeline-index">${String(index + 1).padStart(2, "0")}</span>
      <span><span class="timeline-name">${state.label}</span><small>${id}</small></span>
      <span class="timeline-domain">${state.phase}</span>
    </li>`;
  }).join("");
}

function renderPhaseRail(currentStateId = null) {
  const activeIndex = phaseCatalog.findIndex((phase) => phase.states.includes(currentStateId));
  elements.phaseRail.innerHTML = phaseCatalog.map((phase, index) => `
    <div class="phase-item ${index < activeIndex ? "done" : ""} ${index === activeIndex ? "active" : ""}">
      <small>${index + 1} · ${phase.eyebrow}</small>
      <strong>${phase.label}</strong>
    </div>
  `).join("");
}

function setMode(nextMode) {
  stopInputs();
  mode = nextMode;
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
  elements.liveForm.classList.toggle("hidden", mode !== "LIVE_SANDBOX");
  elements.replayControls.classList.toggle("hidden", mode !== "SANITIZED_REPLAY");
  if (mode === "GUIDED_PREVIEW") {
    elements.modeBadge.textContent = "UI PREVIEW · NOT PAYMENT EVIDENCE";
    elements.modeBadge.className = "mode-badge preview";
    setStatus("说明性数据展示协议映射和恢复行为，不代表真实支付或兼容性证据。");
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
    amount: "0.01",
    currency: "CNY",
    resource_id: "market-signal-demo",
    goods_name: "AI 支付行业趋势专业数据",
    seller_name: "示例专业数据服务",
    method_id: "alipay-ai-pay",
    psp_id: "alipay",
    http_method: "GET",
    request_ref: "req-sha256-41bd",
    order_ref: "order-sha256-92ae",
    transaction_ref: "trade-sha256-8c11",
  };
  return flow().map((id, index) => ({
    ...shared,
    sequence: index + 1,
    state: id,
    occurred_at: new Date(startedAt + index * 1000).toISOString(),
    request_digest: id === "ORDER_CONFIRMED" ? "sha256:41bd…9a20" : undefined,
    validation_mapping: id === "PAYMENT_VERIFIED" ? "ACT candidate → Alipay payment.verify" : undefined,
    fulfillment_ref: id === "FULFILLMENT_CONFIRMED" ? "fulfill-sha256-6d2a" : undefined,
    recovery_action: {
      PAYMENT_PENDING: "QUERY_ORIGINAL_TRANSACTION · DO_NOT_REPAY",
      PROOF_REJECTED: "DO_NOT_DELIVER · REISSUE_OR_RECONCILE",
      VERIFICATION_UNAVAILABLE: "RETRY_SAME_VERIFICATION · DO_NOT_DELIVER",
    }[id],
    result_summary: {
      RESOURCE_DELIVERED: scenario === "IDEMPOTENT_REPLAY" ? "幂等返回已交付资源，未重复扣款" : "专业数据已交付给 Agent",
      FULFILLMENT_CONFIRMED: "交付闭环完成，Agent 已生成报告",
    }[id],
  }));
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
  if (!event.source || /mock/i.test(event.source)) throw new Error("事件必须标明非 Mock 来源");
  if (!event.evidence_ref || !event.correlation_ref) throw new Error("事件缺少证据或关联引用");
  if (!Number.isFinite(Date.parse(event.occurred_at))) throw new Error("事件时间格式无效");
  if (event.state === "CAPABILITY_NEGOTIATED" && !event.method_id) throw new Error("能力协商缺少 method_id");
  if (event.state === "ORDER_CONFIRMED" && (!event.request_ref || !event.order_ref)) {
    throw new Error("订单确认缺少请求或订单引用");
  }
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
  const prior = events.at(-1);
  if (prior && Date.parse(event.occurred_at) < Date.parse(prior.occurred_at)) {
    throw new Error("事件时间不能倒序");
  }
  events.push(event);
  render();
}

function render() {
  const currentIndex = events.length - 1;
  const event = events[currentIndex];
  const current = event ? stateCatalog[event.state] : null;
  [...elements.timeline.children].forEach((item, index) => {
    item.classList.toggle("done", index < currentIndex);
    item.classList.toggle("current", index === currentIndex);
  });
  elements.eventCounter.textContent = `${events.length} / ${flow().length}`;
  elements.taskStatusDot.classList.toggle("active", events.length > 0);
  if (!current) {
    elements.currentState.textContent = "等待开始";
    elements.stateExplanation.textContent = "这里会解释同一个动作在 ACT 场景组件、A402 Binding 与支付宝产品中的位置。";
    ["actDomain", "actComponent", "actBinding", "alipayProduct"].forEach((id) => { elements[id].textContent = "—"; });
    elements.layerCode.textContent = "READY";
    elements.fromActor.textContent = "—";
    elements.toActor.textContent = "—";
    elements.directionArrow.textContent = "→";
    elements.wireBadge.textContent = "WAITING";
    elements.wireMessage.textContent = "选择一个场景，然后逐步播放协议消息";
    elements.exchangeCard.className = "exchange-card idle";
    setActorFocus(null, null);
    renderPhaseRail();
    elements.agentMessage.textContent = "等待连接真实事件流或加载脱敏证据。";
    elements.evidenceRef.textContent = "NO EVIDENCE";
    elements.methodId.textContent = "—";
    elements.correlationChain.textContent = "等待建立关联链";
    renderEvidence(null);
    lockResource();
    return;
  }
  elements.currentState.textContent = current.label;
  elements.stateExplanation.textContent = current.explanation;
  elements.actDomain.textContent = current.domain;
  elements.actComponent.textContent = current.component;
  elements.actBinding.textContent = current.binding;
  elements.alipayProduct.textContent = current.product;
  elements.layerCode.textContent = current.code;
  renderExchange(event.state, current);
  elements.agentMessage.textContent = current.agent;
  elements.evidenceRef.textContent = event.evidence_ref;
  elements.methodId.textContent = event.method_id || findLatest("method_id") || "—";
  elements.correlationChain.textContent = correlationText();
  renderEvidence(event);
  applyResource(event, current);
  if (events.length === flow().length) {
    elements.taskResult.textContent = current.failure
      ? `场景终止于 ${current.label}：${event.recovery_action || "资源保持锁定，不推断成功。"}`
      : mode === "GUIDED_PREVIEW"
        ? "演示完成：支付、验款与履约形成关联闭环。本结果仅为界面预览。"
        : event.result_summary || "付费数据已进入任务上下文，Agent 可以完成最终报告。";
  }
}

function renderExchange(stateId, current) {
  const exchange = exchangeCatalog[stateId] || { from: "buyer", to: "seller", message: stateId };
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
  for (const actor of ["principal", "buyer", "seller", "psp"]) {
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
    ["REQ", findLatest("request_ref")],
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
    amount: "金额", currency: "币种", fulfillment_ref: "履约", http_method: "原请求",
    method_id: "支付方法", order_ref: "订单", psp_id: "PSP", request_ref: "请求",
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
  elements.resourceState.textContent = delivered ? "DELIVERED" : current.failure ? "NOT DELIVERED" : events.length >= 4 ? "PAYMENT REQUIRED" : "LOCKED";
  elements.resourceDescription.textContent = delivered
    ? event.result_summary || "卖方已在官方验款通过后交付对应资源。"
    : current.failure ? "当前路径未满足交付条件，资源保持锁定。" : "专业数据尚未交付。支付验证通过后，由卖方服务返回资源。";
}

function lockResource() {
  elements.resourceCard.className = "resource-card locked";
  elements.resourceState.textContent = "LOCKED";
  elements.resourceTitle.textContent = "AI Payment Market Signal API";
  elements.resourceDescription.textContent = "专业数据尚未交付。支付验证通过后，由卖方服务返回资源。";
  elements.resourcePrice.textContent = "— CNY";
  elements.resourceId.textContent = "resource —";
  elements.taskResult.textContent = "等待付费数据，尚未生成最终报告。";
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
        if (!scenarioFlows[scenario]) throw new Error(`不支持场景 ${scenario}`);
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
    if (!scenarioFlows[scenario]) throw new Error(`不支持场景 ${scenario}`);
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
