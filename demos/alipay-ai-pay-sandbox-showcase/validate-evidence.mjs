import { readFile } from "node:fs/promises";
import { pathToFileURL } from "node:url";

export const SCENARIO_STATES = Object.freeze({
  SUCCESS: [
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
  ],
  PAYMENT_PENDING: [
    "CAPABILITY_NEGOTIATED",
    "ORDER_CONFIRMED",
    "RESOURCE_REQUESTED",
    "PAYMENT_REQUIRED",
    "USER_AUTHORIZATION_REQUIRED",
    "PAYMENT_PROCESSING",
    "PAYMENT_PENDING",
  ],
  PROOF_MISMATCH: [
    "CAPABILITY_NEGOTIATED",
    "ORDER_CONFIRMED",
    "RESOURCE_REQUESTED",
    "PAYMENT_REQUIRED",
    "USER_AUTHORIZATION_REQUIRED",
    "PAYMENT_PROCESSING",
    "PAYMENT_RESULT_RECEIVED",
    "RESOURCE_REQUEST_RETRIED",
    "PROOF_REJECTED",
  ],
  VERIFICATION_UNAVAILABLE: [
    "CAPABILITY_NEGOTIATED",
    "ORDER_CONFIRMED",
    "RESOURCE_REQUESTED",
    "PAYMENT_REQUIRED",
    "USER_AUTHORIZATION_REQUIRED",
    "PAYMENT_PROCESSING",
    "PAYMENT_RESULT_RECEIVED",
    "RESOURCE_REQUEST_RETRIED",
    "VERIFICATION_UNAVAILABLE",
  ],
  IDEMPOTENT_REPLAY: [
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
  ],
});

export const REQUIRED_STATES = SCENARIO_STATES.SUCCESS;

const MODES = new Set(["LIVE_SANDBOX", "SANITIZED_REPLAY"]);
const FORBIDDEN_KEYS = /(^|_)(secret|private_key|access_token|app_auth_token|payment_proof|client_session|binding_code|password)($|_)/i;

export function parseEvents(input) {
  const lines = input.split(/\r?\n/).filter((line) => line.trim() !== "");
  return lines.map((line, index) => {
    try {
      return JSON.parse(line);
    } catch (error) {
      throw new Error(`line ${index + 1} is not valid JSON: ${error.message}`);
    }
  });
}

export function assertNoSensitiveFields(value, location = "event") {
  if (!value || typeof value !== "object") return;
  for (const [key, child] of Object.entries(value)) {
    if (FORBIDDEN_KEYS.test(key)) throw new Error(`${location} contains forbidden sensitive field: ${key}`);
    assertNoSensitiveFields(child, `${location}.${key}`);
  }
}

export function statesForScenario(scenario) {
  const states = SCENARIO_STATES[scenario];
  if (!states) throw new Error(`unsupported scenario: ${scenario ?? "missing"}`);
  return states;
}

export function validateEvidenceEvent(event, index, mode, scenario = "SUCCESS") {
  const requiredStates = statesForScenario(scenario);
  if (!MODES.has(mode)) throw new Error(`unsupported demo mode: ${mode ?? "missing"}`);
  assertNoSensitiveFields(event, `event ${index + 1}`);
  if (event.sequence !== index + 1) throw new Error(`event ${index + 1} has a non-contiguous sequence`);
  if (event.state !== requiredStates[index]) throw new Error(`event ${index + 1} must be ${requiredStates[index]}`);
  if (event.mode !== mode) throw new Error("all events must use the same mode");
  if ((event.scenario || "SUCCESS") !== scenario) throw new Error("all events must use the same scenario");
  if (typeof event.source !== "string" || event.source.trim() === "" || /mock/i.test(event.source)) {
    throw new Error(`event ${index + 1} must identify a non-Mock source`);
  }
  if (typeof event.evidence_ref !== "string" || event.evidence_ref.trim() === "") {
    throw new Error(`event ${index + 1} is missing evidence_ref`);
  }
  const time = Date.parse(event.occurred_at);
  if (!Number.isFinite(time)) throw new Error(`event ${index + 1} has an invalid occurred_at`);
  if (typeof event.correlation_ref !== "string" || event.correlation_ref.trim() === "") {
    throw new Error(`event ${index + 1} is missing correlation_ref`);
  }
  if (event.state === "CAPABILITY_NEGOTIATED" && !event.method_id) {
    throw new Error("capability negotiation must identify method_id");
  }
  if (event.state === "ORDER_CONFIRMED" && (!event.request_ref || !event.order_ref)) {
    throw new Error("order confirmation must bind request_ref and order_ref");
  }
  if (mode === "LIVE_SANDBOX" && event.environment !== "SANDBOX") {
    throw new Error(`event ${index + 1} must declare the SANDBOX environment`);
  }
  if (mode === "SANITIZED_REPLAY" && (event.sanitized !== true || !event.origin_validation_id)) {
    throw new Error(`event ${index + 1} must identify a sanitized source validation`);
  }
}

export function validateEvents(events) {
  const mode = events[0]?.mode;
  const scenario = events[0]?.scenario || "SUCCESS";
  const requiredStates = statesForScenario(scenario);
  if (events.length !== requiredStates.length) {
    throw new Error(`expected ${requiredStates.length} events for ${scenario}, received ${events.length}`);
  }
  let previousTime = 0;
  events.forEach((event, index) => {
    validateEvidenceEvent(event, index, mode, scenario);
    const time = Date.parse(event.occurred_at);
    if (time < previousTime) throw new Error("event timestamps must not move backwards");
    previousTime = time;
  });

  return {
    mode,
    scenario,
    event_count: events.length,
    first_state: events[0].state,
    final_state: events.at(-1).state,
  };
}

async function main() {
  const path = process.argv[2];
  if (!path) throw new Error("usage: node validate-evidence.mjs /absolute/path/to/events.ndjson");
  const result = validateEvents(parseEvents(await readFile(path, "utf8")));
  process.stdout.write(`${JSON.stringify(result, null, 2)}\n`);
}

if (process.argv[1] && import.meta.url === pathToFileURL(process.argv[1]).href) {
  main().catch((error) => {
    process.stderr.write(`[FAIL] ${error.message}\n`);
    process.exitCode = 1;
  });
}
