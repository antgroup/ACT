import test from "node:test";
import assert from "node:assert/strict";
import { REQUIRED_STATES, validateEvents } from "./validate-evidence.mjs";

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
    ...(state === "CAPABILITY_NEGOTIATED" ? { method_id: "alipay-ai-pay" } : {}),
    ...(state === "ORDER_CONFIRMED" ? { request_ref: "req-sha256-a1b2", order_ref: "order-sha256-c3d4" } : {}),
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
    ...(state === "CAPABILITY_NEGOTIATED" ? { method_id: "alipay-ai-pay" } : {}),
    ...(state === "ORDER_CONFIRMED" ? { request_ref: "req-sha256-p1", order_ref: "order-sha256-p1" } : {}),
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
