import assert from "node:assert/strict";
import test from "node:test";

import { decodePaymentNeeded } from "./inspect-402.mjs";
import {
  PREVIEW_MARKER,
  startPreviewServer,
} from "./local-preview-server.mjs";

function closeServer(server) {
  return new Promise((resolve, reject) => {
    server.close((error) => (error ? reject(error) : resolve()));
  });
}

test("[A402-CAND-002] local preview returns a decodable, explicitly non-payable 402 challenge", async () => {
  const { server, baseUrl } = await startPreviewServer();

  try {
    const response = await fetch(`${baseUrl}/paid-resource`);
    assert.equal(response.status, 402);
    assert.equal(response.headers.get("X-ACT-Preview-Mode"), "non-payable");

    const decoded = decodePaymentNeeded(response.headers.get("Payment-Needed"));
    assert.equal(decoded.protocol.seller_signature, PREVIEW_MARKER);
    assert.equal(decoded.protocol.currency, "CNY");

    const body = await response.json();
    assert.equal(body.payment_performed, false);
    assert.equal(body.resource_delivered, false);
  } finally {
    await closeServer(server);
  }
});

test("[A402-CAND-003] local preview never accepts Payment-Proof or delivers paid content", async () => {
  const { server, baseUrl } = await startPreviewServer();

  try {
    const response = await fetch(`${baseUrl}/paid-resource`, {
      headers: { "Payment-Proof": "NON_PAYABLE_FAKE_PROOF" },
    });
    const body = await response.json();

    assert.equal(response.status, 402);
    assert.equal(body.error, "LOCAL_PREVIEW_NO_PAYMENT");
    assert.equal(body.payment_performed, false);
    assert.equal(body.resource_delivered, false);
  } finally {
    await closeServer(server);
  }
});

test("local preview exposes a health endpoint", async () => {
  const { server, baseUrl } = await startPreviewServer();

  try {
    const response = await fetch(`${baseUrl}/health`);
    assert.equal(response.status, 200);
    assert.deepEqual(await response.json(), {
      status: "ok",
      mode: "non-payable-local-preview",
    });
  } finally {
    await closeServer(server);
  }
});
