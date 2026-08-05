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
    ...(state === "CAPABILITY_NEGOTIATED"
      ? { method_id: "alipay-ai-pay", psp_id: "alipay" }
      : {}),
    ...(state === "ORDER_CONFIRMED"
      ? { request_ref: "req-sha256-41bd", order_ref: "order-sha256-92ae" }
      : {}),
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
