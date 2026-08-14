import test from "node:test";
import assert from "node:assert/strict";
import { createReplay } from "./prepare-replay.mjs";
import { SCENARIO_STATES, validateEvents } from "./validate-evidence.mjs";

function liveEvents() {
  return SCENARIO_STATES.SUCCESS.map((state, index) => ({
    sequence: index + 1,
    state,
    scenario: "SUCCESS",
    mode: "LIVE_SANDBOX",
    environment: "SANDBOX",
    source: index < 2 ? "buyer-agent-runtime" : "official-sandbox-workflow",
    occurred_at: `2026-07-27T12:00:${String(index).padStart(2, "0")}Z`,
    evidence_ref: `E2E-20260727-001#step-${index + 1}`,
    correlation_ref: "corr-sha256-a1b2",
    method_id: "example:a402/alipay-ai-pay",
    method_version: "1.0.0",
    psp_id: "alipay",
    endpoint_ref: "endpoint-sha256-a1b2",
    method_schema_ref: "schema-sha256-a1b2",
    capability_source_ref: "capability-sha256-a1b2",
    capability_source_validated: true,
    commerce_confirmation_ref: "commerce-sha256-a1b2",
    request_ref: "req-sha256-41bd",
    request_fingerprint: "sha-256:AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA",
    http_method: "GET",
    order_ref: "order-sha256-92ae",
    resource_id: "resource-demo",
    amount: "0.01",
    currency: "CNY",
    profile_mapping: "ALIPAY_PRODUCT_PAYLOAD_TO_ACT_2_1_EVIDENCE",
    transaction_ref: "trade-sha256-8c11",
    proof_ref: "proof-sha256-8c11",
    delivery_ref: "delivery-sha256-8c11",
    fulfillment_ref: "fulfillment-sha256-8c11",
    product_fulfillment_status: "CONFIRMED",
    ...(state === "PAYMENT_VERIFIED" ? { validation_mapping: "ACT 2.1 evidence ← Alipay payment.verify result" } : {}),
  }));
}

test("creates a validator-compatible replay after explicit review", () => {
  const replay = createReplay(liveEvents(), {
    validationId: "E2E-20260727-001",
    reviewedBy: "review-20260727-a",
    ackSanitized: true,
  });
  assert.equal(validateEvents(replay).mode, "SANITIZED_REPLAY");
  assert.equal(replay[0].origin_validation_id, "E2E-20260727-001");
  assert.equal(replay[0].sanitization_review_ref, "review-20260727-a");
});

test("refuses unreviewed or sensitive evidence", () => {
  assert.throws(() => createReplay(liveEvents(), {
    validationId: "E2E-20260727-001",
    reviewedBy: "review-20260727-a",
    ackSanitized: false,
  }), /ack-sanitized/);

  const unsafe = liveEvents();
  unsafe[1].result_summary = "app_auth_token must-not-leak";
  assert.throws(() => createReplay(unsafe, {
    validationId: "E2E-20260727-001",
    reviewedBy: "review-20260727-a",
    ackSanitized: true,
  }), /forbidden sensitive text/);
});
