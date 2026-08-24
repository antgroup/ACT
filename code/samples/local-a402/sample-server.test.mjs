import assert from "node:assert/strict";
import test from "node:test";

import { decodePaymentNeeded } from "./inspect-402.mjs";
import { SAMPLE_SIGNATURE, startSampleServer } from "./sample-server.mjs";

function closeServer(server) {
  return new Promise((resolve, reject) => {
    server.close((error) => (error ? reject(error) : resolve()));
  });
}

test("[A402-TEST-002] local sample returns a decodable non-payable 402 challenge", async () => {
  const { server, baseUrl } = await startSampleServer();
  try {
    const response = await fetch(baseUrl + "/paid-resource");
    assert.equal(response.status, 402);
    assert.equal(response.headers.get("X-ACT-Sample-Mode"), "non-payable");
    const decoded = decodePaymentNeeded(response.headers.get("Payment-Needed"));
    assert.equal(decoded.protocol.signature_content, SAMPLE_SIGNATURE);
    assert.equal(decoded.protocol.currency, "CNY");
    const body = await response.json();
    assert.equal(body.payment_performed, false);
    assert.equal(body.resource_delivered, false);
  } finally {
    await closeServer(server);
  }
});

test("[A402-TEST-003] local sample rejects unverified Payment-Proof", async () => {
  const { server, baseUrl } = await startSampleServer();
  try {
    const response = await fetch(baseUrl + "/paid-resource", {
      headers: { "Payment-Proof": "NON_PAYABLE_FAKE_PROOF" },
    });
    const body = await response.json();
    assert.equal(response.status, 402);
    assert.equal(body.error, "LOCAL_SAMPLE_NO_PAYMENT");
    assert.equal(body.resource_delivered, false);
  } finally {
    await closeServer(server);
  }
});

test("local sample exposes a health endpoint", async () => {
  const { server, baseUrl } = await startSampleServer();
  try {
    const response = await fetch(baseUrl + "/health");
    assert.equal(response.status, 200);
    assert.deepEqual(await response.json(), {
      status: "ok",
      mode: "non-payable-local-sample",
    });
  } finally {
    await closeServer(server);
  }
});
