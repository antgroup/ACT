import assert from "node:assert/strict";
import test from "node:test";

import { decodePaymentNeeded, sanitizedSummary } from "./inspect-402.mjs";

const bill = {
  protocol: {
    out_trade_no: "ORDER_REDACTED",
    amount: "0.01",
    currency: "CNY",
    resource_id: "resource-1",
    pay_before: "2026-07-22T12:00:00+08:00",
    seller_signature: "secret-looking-signature",
    seller_sign_type: "RSA2",
    seller_unique_id: "2088secret",
  },
  method: {
    seller_name: "Test merchant",
    seller_id: "2088secret",
    seller_app_id: "app-secret",
    goods_name: "ACT resource",
    seller_unique_id_key: "seller_id",
    service_id: "service-secret",
  },
};

test("decodes Base64URL and validates required fields", () => {
  const encoded = Buffer.from(JSON.stringify(bill), "utf8").toString("base64url");
  assert.deepEqual(decodePaymentNeeded(encoded), bill);
});

test("summary excludes merchant identifiers and signature", () => {
  const summary = sanitizedSummary(bill);
  assert.equal(summary.amount, "0.01");
  assert.equal(summary.goods_name, "ACT resource");
  assert.equal("seller_signature" in summary, false);
  assert.equal("seller_id" in summary, false);
  assert.equal("out_trade_no" in summary, false);
});
