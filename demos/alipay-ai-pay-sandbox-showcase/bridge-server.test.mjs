import test from "node:test";
import assert from "node:assert/strict";
import { dirname, join } from "node:path";
import { fileURLToPath } from "node:url";
import { createDemoServer } from "./bridge-server.mjs";

const root = join(dirname(fileURLToPath(import.meta.url)), "public");

async function withServer(run) {
  const demo = createDemoServer({ root, port: 0 });
  await demo.start();
  try {
    await run(`http://127.0.0.1:${demo.port()}`);
  } finally {
    await demo.close();
  }
}

test("accepts the next sanitized live event and reports state", async () => {
  await withServer(async (base) => {
    const accepted = await fetch(`${base}/events`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        state: "CAPABILITY_NEGOTIATED",
        source: "buyer-agent-adapter",
        evidence_ref: "E2E-20260725-001#step-1",
        correlation_ref: "corr-sha256-a1b2",
        method_id: "alipay-ai-pay",
      }),
    });
    assert.equal(accepted.status, 202);
    const event = await accepted.json();
    assert.equal(event.sequence, 1);
    assert.equal(event.mode, "LIVE_SANDBOX");
    assert.equal(event.environment, "SANDBOX");

    const state = await fetch(`${base}/events/state`).then((response) => response.json());
    assert.deepEqual(state, {
      scenario: "SUCCESS",
      event_count: 1,
      next_state: "ORDER_CONFIRMED",
      complete: false,
    });
  });
});

test("rejects out-of-order and sensitive events", async () => {
  await withServer(async (base) => {
    const outOfOrder = await fetch(`${base}/events`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        state: "PAYMENT_VERIFIED",
        source: "seller-provider",
        evidence_ref: "E2E-20260725-002#step-5",
        correlation_ref: "corr-sha256-a1b2",
      }),
    });
    assert.equal(outOfOrder.status, 400);

    const sensitive = await fetch(`${base}/events`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        state: "CAPABILITY_NEGOTIATED",
        source: "buyer-agent-adapter",
        evidence_ref: "E2E-20260725-002#step-1",
        correlation_ref: "corr-sha256-a1b2",
        method_id: "alipay-ai-pay",
        payment_proof: "must-not-enter-demo",
      }),
    });
    assert.equal(sensitive.status, 400);
    assert.match((await sensitive.json()).message, /forbidden sensitive field/);
  });
});

test("reset clears the live sequence", async () => {
  await withServer(async (base) => {
    await fetch(`${base}/events`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        state: "CAPABILITY_NEGOTIATED",
        source: "buyer-agent-adapter",
        evidence_ref: "E2E-20260725-003#step-1",
        correlation_ref: "corr-sha256-a1b2",
        method_id: "alipay-ai-pay",
      }),
    });
    const reset = await fetch(`${base}/events/reset`, { method: "POST" });
    assert.equal(reset.status, 200);
    assert.deepEqual(await reset.json(), {
      scenario: "SUCCESS",
      event_count: 0,
      next_state: "CAPABILITY_NEGOTIATED",
    });
  });
});

test("accepts a complete correlated success chain", async () => {
  await withServer(async (base) => {
    const states = [
      "CAPABILITY_NEGOTIATED", "ORDER_CONFIRMED", "RESOURCE_REQUESTED", "PAYMENT_REQUIRED",
      "USER_AUTHORIZATION_REQUIRED", "PAYMENT_PROCESSING", "PAYMENT_RESULT_RECEIVED",
      "RESOURCE_REQUEST_RETRIED", "PAYMENT_VERIFIED", "RESOURCE_DELIVERED",
      "FULFILLMENT_CONFIRMED",
    ];
    for (const [index, state] of states.entries()) {
      const response = await fetch(`${base}/events`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          state,
          source: index < 2 ? "buyer-agent-adapter" : "official-sandbox-workflow",
          evidence_ref: `E2E-20260725-004#step-${index + 1}`,
          correlation_ref: "corr-sha256-complete",
          ...(state === "CAPABILITY_NEGOTIATED" ? { method_id: "alipay-ai-pay" } : {}),
          ...(state === "ORDER_CONFIRMED"
            ? { request_ref: "req-sha256-complete", order_ref: "order-sha256-complete" }
            : {}),
        }),
      });
      assert.equal(response.status, 202, `expected ${state} to be accepted`);
    }
    assert.deepEqual(await fetch(`${base}/events/state`).then((response) => response.json()), {
      scenario: "SUCCESS",
      event_count: 11,
      next_state: null,
      complete: true,
    });
    const evidence = await fetch(`${base}/events/export`);
    assert.equal(evidence.status, 200);
    const lines = (await evidence.text()).trim().split("\n").map(JSON.parse);
    assert.equal(lines.length, 11);
    assert.equal(lines[0].mode, "LIVE_SANDBOX");
  });
});

test("refuses to export an incomplete live chain", async () => {
  await withServer(async (base) => {
    const response = await fetch(`${base}/events/export`);
    assert.equal(response.status, 409);
    const body = await response.json();
    assert.equal(body.error, "evidence_incomplete");
    assert.equal(body.next_state, "CAPABILITY_NEGOTIATED");
  });
});

test("supports an explicit failure scenario and rejects invalid reset scenarios", async () => {
  await withServer(async (base) => {
    const reset = await fetch(`${base}/events/reset`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ scenario: "PROOF_MISMATCH" }),
    });
    assert.equal(reset.status, 200);
    assert.equal((await reset.json()).scenario, "PROOF_MISMATCH");

    const rejected = await fetch(`${base}/events/reset`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ scenario: "UNKNOWN" }),
    });
    assert.equal(rejected.status, 400);
  });
});
