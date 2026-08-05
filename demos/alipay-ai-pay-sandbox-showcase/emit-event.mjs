const allowedStates = [
  "CAPABILITY_NEGOTIATED",
  "ORDER_CONFIRMED",
  "RESOURCE_REQUESTED",
  "PAYMENT_REQUIRED",
  "USER_AUTHORIZATION_REQUIRED",
  "PAYMENT_PROCESSING",
  "PAYMENT_RESULT_RECEIVED",
  "RESOURCE_REQUEST_RETRIED",
  "PAYMENT_VERIFIED",
  "RESOURCE_DELIVERED",
  "FULFILLMENT_CONFIRMED",
  "PAYMENT_PENDING",
  "PROOF_REJECTED",
  "VERIFICATION_UNAVAILABLE",
];
const allowedOptions = new Set([
  "source",
  "evidence-ref",
  "amount",
  "currency",
  "resource-id",
  "goods-name",
  "seller-name",
  "result-summary",
  "scenario",
  "correlation-ref",
  "method-id",
  "psp-id",
  "request-ref",
  "request-digest",
  "http-method",
  "order-ref",
  "transaction-ref",
  "fulfillment-ref",
  "validation-mapping",
  "recovery-action",
  "bridge",
]);

const [state, ...args] = process.argv.slice(2);
if (!allowedStates.includes(state)) {
  fail(`state must be one of: ${allowedStates.join(", ")}`);
}

const options = parseOptions(args);
if (!options.source) fail("--source is required");
if (!options["evidence-ref"]) fail("--evidence-ref is required");
if (!options["correlation-ref"]) fail("--correlation-ref is required");
if (/mock/i.test(options.source)) fail("--source must identify a non-Mock runtime source");

const bridge = options.bridge || process.env.ACT_DEMO_BRIDGE_URL || "http://127.0.0.1:4173/events";
const event = {
  state,
  source: options.source,
  evidence_ref: options["evidence-ref"],
  scenario: options.scenario,
  correlation_ref: options["correlation-ref"],
  method_id: options["method-id"],
  psp_id: options["psp-id"],
  request_ref: options["request-ref"],
  request_digest: options["request-digest"],
  http_method: options["http-method"],
  order_ref: options["order-ref"],
  transaction_ref: options["transaction-ref"],
  fulfillment_ref: options["fulfillment-ref"],
  validation_mapping: options["validation-mapping"],
  recovery_action: options["recovery-action"],
  amount: options.amount,
  currency: options.currency,
  resource_id: options["resource-id"],
  goods_name: options["goods-name"],
  seller_name: options["seller-name"],
  result_summary: options["result-summary"],
};
Object.keys(event).forEach((key) => event[key] === undefined && delete event[key]);

const response = await fetch(bridge, {
  method: "POST",
  headers: { "Content-Type": "application/json" },
  body: JSON.stringify(event),
});
const result = await response.json();
if (!response.ok) fail(`${result.error || "event rejected"}: ${result.message || response.status}`);
process.stdout.write(`accepted ${result.sequence} ${result.state}\n`);

function parseOptions(values) {
  const result = {};
  for (let index = 0; index < values.length; index += 2) {
    const flag = values[index];
    const value = values[index + 1];
    if (!flag?.startsWith("--") || value === undefined) fail("options must use --name value pairs");
    const name = flag.slice(2);
    if (!allowedOptions.has(name)) fail(`unsupported option: --${name}`);
    result[name] = value;
  }
  return result;
}

function fail(message) {
  process.stderr.write(`[FAIL] ${message}\n`);
  process.exit(1);
}
