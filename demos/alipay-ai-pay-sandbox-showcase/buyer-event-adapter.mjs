import { readFile } from "node:fs/promises";
import { pathToFileURL } from "node:url";
import { assertNoSensitiveFields } from "./validate-evidence.mjs";

const SIGNALS = Object.freeze({
  CAPABILITY_SELECTED: {
    state: "CAPABILITY_NEGOTIATED",
    observedFrom: "HOST_AGENT",
    required: ["method_id", "psp_id"],
  },
  ORDER_CONFIRMED: {
    state: "ORDER_CONFIRMED",
    observedFrom: "HOST_AGENT",
    required: ["request_ref", "order_ref"],
  },
  AUTHORIZATION_REQUIRED: {
    state: "USER_AUTHORIZATION_REQUIRED",
    observedFrom: "OFFICIAL_ALIPAY_PAYMENT_SKILL",
    required: [],
  },
  PAYMENT_STARTED: {
    state: "PAYMENT_PROCESSING",
    observedFrom: "OFFICIAL_ALIPAY_PAYMENT_SKILL",
    required: [],
  },
  PAYMENT_SUCCEEDED: {
    state: "PAYMENT_RESULT_RECEIVED",
    observedFrom: "OFFICIAL_ALIPAY_PAYMENT_SKILL",
    required: ["transaction_ref"],
  },
  PAYMENT_PENDING: {
    state: "PAYMENT_PENDING",
    observedFrom: "OFFICIAL_ALIPAY_PAYMENT_SKILL",
    required: ["recovery_action"],
  },
});

const COMMON_REQUIRED = ["source", "evidence_ref", "correlation_ref", "observed_from"];
const FORWARDED_FIELDS = new Set([
  "source",
  "evidence_ref",
  "correlation_ref",
  "method_id",
  "psp_id",
  "request_ref",
  "request_digest",
  "http_method",
  "order_ref",
  "transaction_ref",
  "amount",
  "currency",
  "resource_id",
  "goods_name",
  "seller_name",
  "result_summary",
  "recovery_action",
]);
const INPUT_FIELDS = new Set(["signal", "observed_from", ...FORWARDED_FIELDS]);

export function toDemoEvent(input) {
  if (!input || typeof input !== "object" || Array.isArray(input)) {
    throw new Error("buyer adapter input must be a JSON object");
  }
  assertNoSensitiveFields(input, "buyer adapter input");
  for (const key of Object.keys(input)) {
    if (!INPUT_FIELDS.has(key)) throw new Error(`unsupported buyer adapter field: ${key}`);
  }

  const definition = SIGNALS[input.signal];
  if (!definition) {
    throw new Error(`signal must be one of: ${Object.keys(SIGNALS).join(", ")}`);
  }
  if (input.observed_from !== definition.observedFrom) {
    throw new Error(
      `${input.signal} must be observed from ${definition.observedFrom}, not ${input.observed_from || "missing"}`,
    );
  }
  for (const field of [...COMMON_REQUIRED, ...definition.required]) {
    if (typeof input[field] !== "string" || input[field].trim() === "") {
      throw new Error(`${input.signal} requires ${field}`);
    }
  }
  if (/mock/i.test(input.source)) throw new Error("source must identify a non-Mock runtime");

  const event = { state: definition.state };
  for (const field of FORWARDED_FIELDS) {
    if (input[field] !== undefined) event[field] = input[field];
  }
  return event;
}

export async function postBuyerSignal(input, {
  bridge = process.env.ACT_DEMO_BRIDGE_URL || "http://127.0.0.1:4173/events",
  fetchImpl = fetch,
} = {}) {
  const event = toDemoEvent(input);
  const response = await fetchImpl(bridge, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(event),
  });
  const result = await response.json();
  if (!response.ok) {
    throw new Error(`${result.error || "event rejected"}: ${result.message || response.status}`);
  }
  return result;
}

async function readInput(path) {
  if (!path) throw new Error("usage: node buyer-event-adapter.mjs <signal.json|->");
  if (path !== "-") return JSON.parse(await readFile(path, "utf8"));
  const chunks = [];
  for await (const chunk of process.stdin) chunks.push(chunk);
  return JSON.parse(Buffer.concat(chunks).toString("utf8"));
}

async function main() {
  const result = await postBuyerSignal(await readInput(process.argv[2]));
  process.stdout.write(`accepted ${result.sequence} ${result.state}\n`);
}

if (process.argv[1] && import.meta.url === pathToFileURL(process.argv[1]).href) {
  main().catch((error) => {
    process.stderr.write(`[FAIL] ${error.message}\n`);
    process.exitCode = 1;
  });
}
