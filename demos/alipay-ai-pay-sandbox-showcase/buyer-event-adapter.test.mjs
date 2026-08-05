import test from "node:test";
import assert from "node:assert/strict";
import { postBuyerSignal, toDemoEvent } from "./buyer-event-adapter.mjs";

const common = {
  source: "codex-with-official-alipay-payment-skill",
  evidence_ref: "E2E-20260727-001#buyer",
  correlation_ref: "corr-sha256-a1b2",
};

test("maps host and official payment signals to demo states", () => {
  assert.deepEqual(toDemoEvent({
    ...common,
    signal: "CAPABILITY_SELECTED",
    observed_from: "HOST_AGENT",
    method_id: "alipay-ai-pay",
    psp_id: "alipay",
  }), {
    state: "CAPABILITY_NEGOTIATED",
    source: common.source,
    evidence_ref: common.evidence_ref,
    correlation_ref: common.correlation_ref,
    method_id: "alipay-ai-pay",
    psp_id: "alipay",
  });

  assert.equal(toDemoEvent({
    ...common,
    signal: "PAYMENT_SUCCEEDED",
    observed_from: "OFFICIAL_ALIPAY_PAYMENT_SKILL",
    transaction_ref: "trade-sha256-8c11",
  }).state, "PAYMENT_RESULT_RECEIVED");
});

test("rejects wrong provenance, sensitive material, and incomplete success", () => {
  assert.throws(() => toDemoEvent({
    ...common,
    signal: "PAYMENT_STARTED",
    observed_from: "HOST_AGENT",
  }), /must be observed from OFFICIAL_ALIPAY_PAYMENT_SKILL/);

  assert.throws(() => toDemoEvent({
    ...common,
    signal: "PAYMENT_SUCCEEDED",
    observed_from: "OFFICIAL_ALIPAY_PAYMENT_SKILL",
    payment_proof: "must-not-enter-demo",
  }), /forbidden sensitive field/);

  assert.throws(() => toDemoEvent({
    ...common,
    signal: "PAYMENT_SUCCEEDED",
    observed_from: "OFFICIAL_ALIPAY_PAYMENT_SKILL",
  }), /requires transaction_ref/);
});

test("posts only the mapped, allow-listed event", async () => {
  let submitted;
  const result = await postBuyerSignal({
    ...common,
    signal: "PAYMENT_PENDING",
    observed_from: "OFFICIAL_ALIPAY_PAYMENT_SKILL",
    recovery_action: "QUERY_ORIGINAL_PAYMENT",
  }, {
    bridge: "http://bridge.invalid/events",
    fetchImpl: async (url, init) => {
      submitted = { url, init, body: JSON.parse(init.body) };
      return new Response(JSON.stringify({ sequence: 7, state: "PAYMENT_PENDING" }), {
        status: 202,
        headers: { "Content-Type": "application/json" },
      });
    },
  });

  assert.equal(result.state, "PAYMENT_PENDING");
  assert.equal(submitted.url, "http://bridge.invalid/events");
  assert.equal(submitted.body.state, "PAYMENT_PENDING");
  assert.equal(submitted.body.observed_from, undefined);
});
