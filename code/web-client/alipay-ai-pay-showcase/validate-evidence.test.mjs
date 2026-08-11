import test from "node:test";
import assert from "node:assert/strict";
import { REQUIRED_STATES, SCENARIO_STATES, validateEvents } from "./validate-evidence.mjs";

function liveEvents() {
  return REQUIRED_STATES.map((state, index) => ({
    sequence: index + 1,
    state,
    mode: "LIVE_SANDBOX",
    source: index < 3 ? "buyer-agent-quickstart" : "alipay-sandbox-workflow",
    environment: "SANDBOX",
    occurred_at: new Date(Date.UTC(2026, 6, 22, 12, 0, index)).toISOString(),
    evidence_ref: `E2E-20260722-001#step-${index + 1}`,
    scenario: "SUCCESS",
    correlation_ref: "corr-sha256-a1b2",
    method_id: "example:a402/alipay-ai-pay",
    method_version: "0.1.0-preview.1",
    psp_id: "alipay",
    endpoint_ref: "endpoint-sha256-a1b2",
    method_schema_ref: "schema-sha256-a1b2",
    capability_source_ref: "capability-sha256-a1b2",
    capability_source_validated: true,
    commerce_confirmation_ref: "commerce-sha256-a1b2",
    request_ref: "req-sha256-a1b2",
    request_fingerprint: "sha-256:AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA",
    order_ref: "order-sha256-c3d4",
    resource_id: "resource-demo",
    amount: "0.01",
    currency: "CNY",
    profile_mapping: "ALIPAY_PRODUCT_PAYLOAD_TO_ACT_CANDIDATE_EVIDENCE",
    transaction_ref: "trade-sha256-e5f6",
    proof_ref: "proof-sha256-e5f6",
    delivery_ref: "delivery-sha256-e5f6",
    fulfillment_ref: "fulfillment-sha256-e5f6",
    product_fulfillment_status: "CONFIRMED",
    ...(state === "PAYMENT_VERIFIED" ? { validation_mapping: "ACT candidate evidence ← Alipay payment.verify result" } : {}),
  }));
}

test("accepts a complete ordered sandbox evidence chain", () => {
  assert.deepEqual(validateEvents(liveEvents()), {
    mode: "LIVE_SANDBOX",
    scenario: "SUCCESS",
    event_count: 11,
    first_state: "CAPABILITY_NEGOTIATED",
    final_state: "FULFILLMENT_CONFIRMED",
  });
});

test("accepts a terminal failure scenario without claiming delivery", () => {
  const states = [
    "CAPABILITY_NEGOTIATED", "ORDER_CONFIRMED", "RESOURCE_REQUESTED", "PAYMENT_REQUIRED",
    "USER_AUTHORIZATION_REQUIRED", "PAYMENT_PROCESSING", "PAYMENT_PENDING",
  ];
  const events = states.map((state, index) => ({
    sequence: index + 1,
    state,
    scenario: "PAYMENT_PENDING",
    mode: "LIVE_SANDBOX",
    source: "official-sandbox-adapter",
    environment: "SANDBOX",
    occurred_at: new Date(Date.UTC(2026, 6, 22, 13, 0, index)).toISOString(),
    evidence_ref: `E2E-PENDING#step-${index + 1}`,
    correlation_ref: "corr-sha256-pending",
    method_id: "example:a402/alipay-ai-pay",
    method_version: "0.1.0-preview.1",
    psp_id: "alipay",
    endpoint_ref: "endpoint-sha256-p1",
    method_schema_ref: "schema-sha256-p1",
    capability_source_ref: "capability-sha256-p1",
    capability_source_validated: true,
    commerce_confirmation_ref: "commerce-sha256-p1",
    request_ref: "req-sha256-p1",
    request_fingerprint: "sha-256:BBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBB",
    order_ref: "order-sha256-p1",
    resource_id: "resource-pending",
    amount: "0.01",
    currency: "CNY",
    profile_mapping: "ALIPAY_PRODUCT_PAYLOAD_TO_ACT_CANDIDATE_EVIDENCE",
    transaction_ref: "trade-sha256-p1",
    proof_ref: "proof-sha256-p1",
  }));
  assert.equal(validateEvents(events).final_state, "PAYMENT_PENDING");
});

test("rejects a manufactured source", () => {
  const events = liveEvents();
  events[4].source = "local-mock-payment";
  assert.throws(() => validateEvents(events), /non-Mock source/);
});

test("rejects sensitive payment material", () => {
  const events = liveEvents();
  events[4].payment_proof = "must-not-be-recorded";
  assert.throws(() => validateEvents(events), /forbidden sensitive field/);
});

test("requires replay provenance on every replay event", () => {
  const events = liveEvents().map((event) => ({ ...event, mode: "SANITIZED_REPLAY", sanitized: true }));
  assert.throws(() => validateEvents(events), /sanitized source validation/);
});

test("rejects invalid method identifiers and cross-step fingerprint drift", () => {
  const invalidMethod = liveEvents();
  invalidMethod.forEach((event) => { event.method_id = "alipay-ai-pay"; });
  assert.throws(() => validateEvents(invalidMethod), /Candidate namespace syntax/);

  const changedFingerprint = liveEvents();
  changedFingerprint[8].request_fingerprint = "sha-256:BBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBB";
  assert.throws(() => validateEvents(changedFingerprint), /request_fingerprint changes/);
});

test("requires a real second submission for idempotent replay evidence", () => {
  const base = liveEvents()[0];
  const events = SCENARIO_STATES.IDEMPOTENT_REPLAY.map((state, index) => ({
    ...base,
    sequence: index + 1,
    state,
    scenario: "IDEMPOTENT_REPLAY",
    occurred_at: new Date(Date.UTC(2026, 6, 22, 14, 0, index)).toISOString(),
    evidence_ref: `E2E-REPLAY#step-${index + 1}`,
    validation_mapping: state === "PAYMENT_VERIFIED"
      ? "ACT candidate evidence ← Alipay payment.verify result"
      : undefined,
  }));
  assert.throws(() => validateEvents(events), /must prove no repeated payment/);
  Object.assign(events.at(-1), {
    idempotent_replay: true,
    payment_action: "NO_NEW_PAYMENT",
    delivery_action: "RETURN_PRIOR_RESULT",
    fulfillment_action: "NOT_REPEATED",
  });
  assert.equal(validateEvents(events).event_count, 14);
});
